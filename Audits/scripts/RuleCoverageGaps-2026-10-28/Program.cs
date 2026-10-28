using System.Text;
using System.Text.RegularExpressions;
using WPRulesReviewer.Core.RuleDebugger;

if (args[0] == "facts")
{
    // facts <pathsFile> <outJsonl> <parallelism>
    var paths = File.ReadAllLines(args[1]).Where(l => l.Length > 0).ToList();
    var outFile = args[2];
    var parallel = int.Parse(args[3]);
    var done = File.Exists(outFile)
        ? File.ReadLines(outFile).Select(l => l.Split('\t', 2)[0]).ToHashSet(StringComparer.Ordinal)
        : new HashSet<string>(StringComparer.Ordinal);
    var todo = new System.Collections.Concurrent.ConcurrentQueue<string>(paths.Where(p => !done.Contains(p)));
    Console.WriteLine($"todo {todo.Count} (already {done.Count})");
    var writeLock = new object();
    using var writer = new StreamWriter(outFile, append: true) { AutoFlush = true };
    var sw = System.Diagnostics.Stopwatch.StartNew();
    var count = 0;
    var workers = Enumerable.Range(0, parallel).Select(async _ =>
    {
        var client = new RawMcp("http://unrealmcp.internal:8000/mcp");
        await client.InitAsync();
        while (todo.TryDequeue(out var p))
        {
            string line;
            try
            {
                var text = await client.CallAsync(UnrealRuleSource.AuditToolset, "GetActorRuleFacts", new { ActorNameOrPath = p });
                line = p + "\t" + text.Replace("\n", " ").Replace("\r", " ");
            }
            catch (Exception ex)
            {
                line = p + "\tERROR " + ex.Message.Replace("\n", " ").Replace("\r", " ");
            }
            lock (writeLock)
            {
                writer.WriteLine(line);
                if (++count % 500 == 0) Console.WriteLine($"{count} in {sw.Elapsed:hh\\:mm\\:ss} ({sw.Elapsed.TotalMilliseconds / count:0} ms/actor)");
            }
        }
    }).ToArray();
    await Task.WhenAll(workers);
    Console.WriteLine($"done {count} in {sw.Elapsed}");
    return;
}

if (args[0] == "aggregate")
{
    // aggregate <jsonl> <outDir>
    var rows = new List<(string Path, string Class, string Grid, Dictionary<string, (string Cat, string Detail)> Fam)>();
    var errors = new List<string>();
    foreach (var line in File.ReadLines(args[1]))
    {
        var parts = line.Split('\t', 2);
        if (parts.Length < 2 || parts[1].StartsWith("ERROR")) { errors.Add(line); continue; }
        using var doc = System.Text.Json.JsonDocument.Parse(parts[1]);
        var v = doc.RootElement.GetProperty("returnValue");
        var fam = new Dictionary<string, (string, string)>();
        var grid = "";
        foreach (var e in v.GetProperty("engineVerdicts").EnumerateArray())
        {
            var type = e.GetProperty("ruleType").GetString()!;
            var matched = e.GetProperty("matchedRules").EnumerateArray().Select(x => x.GetString()!).ToList();
            var cat = e.GetProperty("bIsIgnoredByRules").GetBoolean() ? "Ignored"
                : e.GetProperty("bForcedSettingsApply").GetBoolean() ? "Forced"
                : matched.Count > 0 ? "Matched" : "Unvisited";
            var detail = cat switch
            {
                "Matched" => string.Join("+", matched.Select(m => RuleNames.ShortName(Regex.Match(m, @"^\[\d+\]\s+(\S+)").Groups[1].Value))),
                _ => e.GetProperty("shortCircuitReason").GetString() ?? "",
            };
            if (type == "RuntimeGrid") grid = e.GetProperty("expectedValue").GetString() ?? "";
            fam[type] = (cat, detail);
        }
        rows.Add((parts[0], RuleNames.ShortClass(v.GetProperty("actorClass").GetString()), grid, fam));
    }

    string Pref(string p, int d) => string.Join('/', p.Split('/').Take(d));
    var sb = new StringBuilder();
    sb.AppendLine($"Actors evaluated by the engine: {rows.Count} (errors: {errors.Count})");
    foreach (var f in new[] { "DataLayer", "RuntimeGrid", "HLODLayer" })
    {
        var g = rows.GroupBy(r => r.Fam.TryGetValue(f, out var c) ? c.Cat : "?").ToDictionary(x => x.Key, x => x.Count());
        sb.AppendLine();
        sb.AppendLine($"== {f}: " + string.Join(", ", g.OrderByDescending(x => x.Value).Select(x => $"{x.Key}={x.Value} ({100.0 * x.Value / rows.Count:0.0}%)")));
        var unv = rows.Where(r => r.Fam.TryGetValue(f, out var c) && c.Cat == "Unvisited").ToList();
        sb.AppendLine("   Unvisited by class: " + string.Join(", ", unv.GroupBy(r => r.Class).OrderByDescending(x => x.Count()).Select(x => $"{x.Key}={x.Count()}")));
        sb.AppendLine("   Unvisited by grid: " + string.Join(", ", unv.GroupBy(r => r.Grid).OrderByDescending(x => x.Count()).Select(x => $"{x.Key}={x.Count()}")));
        foreach (var d in new[] { 2, 3 })
            sb.AppendLine($"   Unvisited by path depth {d}: " + string.Join(", ", unv.GroupBy(r => Pref(r.Path, d)).OrderByDescending(x => x.Count()).Take(12)
                .Select(x => $"{x.Key}={x.Count()}/{rows.Count(r => Pref(r.Path, d) == x.Key)}")));
        var forced = rows.Where(r => r.Fam.TryGetValue(f, out var c) && c.Cat == "Forced").ToList();
        if (forced.Count > 0)
            sb.AppendLine("   Forced by entry: " + string.Join(", ", forced.GroupBy(r => Regex.Match(r.Fam[f].Detail, @"contains '([^']+)'|is a[n]? (\S+)").Value).OrderByDescending(x => x.Count()).Take(15).Select(x => $"[{x.Key}]={x.Count()}")));
    }
    var none = rows.Where(r => r.Fam.Values.All(c => c.Cat is "Unvisited" or "Ignored")).ToList();
    sb.AppendLine();
    sb.AppendLine($"Actors reached by no rule in any family: {none.Count}");
    foreach (var r in none.Take(20)) sb.AppendLine($"   {r.Class}  {r.Path}");
    File.WriteAllText(Path.Combine(args[2], "engine-report.txt"), sb.ToString());

    var ecsv = new StringBuilder("OutlinerPath,Class,Grid,DataLayer,DataLayerDetail,RuntimeGrid,RuntimeGridDetail,HLODLayer,HLODLayerDetail\n");
    string Q(string s) => "\"" + s.Replace("\"", "\"\"") + "\"";
    foreach (var r in rows)
        ecsv.AppendLine(string.Join(",", new[] { Q(r.Path), r.Class, r.Grid }.Concat(new[] { "DataLayer", "RuntimeGrid", "HLODLayer" }
            .SelectMany(f => r.Fam.TryGetValue(f, out var c) ? new[] { c.Cat, Q(c.Detail) } : new[] { "?", "" }))));
    File.WriteAllText(Path.Combine(args[2], "engine-actors.csv"), ecsv.ToString());
    File.WriteAllLines(Path.Combine(args[2], "engine-errors.txt"), errors.Select(e => e.Length > 300 ? e[..300] : e));
    Console.WriteLine(sb.ToString());
    return;
}

if (args[0] == "mcp")
{
    var mcp = new RawMcp("http://unrealmcp.internal:8000/mcp");
    await mcp.InitAsync();
    System.Text.Json.JsonElement Json(string a) =>
        System.Text.Json.JsonDocument.Parse(a.StartsWith('@') ? File.ReadAllText(a[1..]) : a).RootElement;
    Console.WriteLine(args[1] == "call"
        ? await mcp.CallAsync(args[2], args[3], args.Length > 4 ? Json(args[4]) : null)
        : await mcp.ToolAsync(args[1], args.Length > 2 ? Json(args[2]) : new { }));
    return;
}

var snapshotPath = args[0];
var logPath = args[1];
var outDir = args[2];
Directory.CreateDirectory(outDir);

var snapshot = RuleSnapshotStore.Load(snapshotPath);
var families = new[] { RuleFamily.DataLayer, RuleFamily.RuntimeGrid, RuleFamily.HLODLayer };

// ------------------------------------------------------------------ rule summary
var summary = new StringBuilder();
foreach (var family in families)
{
    foreach (var r in snapshot.Registered(family))
    {
        summary.AppendLine($"{family} #{r.Index} {r.Name} enabled={r.IsEnabled} resolves={r.Resolves} -> {r.TargetDisplay}");
        foreach (var c in r.Conditions)
        {
            var parts = new List<string>();
            if (c.ActorTypes.Count > 0) parts.Add("Types=" + string.Join("|", c.ActorTypes.Select(RuleNames.ShortClass)));
            if (c.ActorTags.Count > 0) parts.Add("Tags=" + string.Join("|", c.ActorTags));
            if (c.OutlinerPathContains.Count > 0) parts.Add("Path=" + string.Join("|", c.OutlinerPathContains));
            if (c.UsesBounds) parts.Add($"Bounds(maxDim={c.MaxBoundsDimension},maxVol={c.MaxBoundsVolume},minDim={c.MinBoundsDimension},minVol={c.MinBoundsVolume})");
            if (c.RuntimeGrid is not null) parts.Add("Grid=" + c.RuntimeGrid);
            if (c.MinDepthBelowLandscape is not null) parts.Add("Depth>=" + c.MinDepthBelowLandscape);
            if (c.IsInsideLevelInstance is not null) parts.Add("InsideLI=" + c.IsInsideLevelInstance);
            summary.AppendLine($"    cond#{c.Index} {c.Operator}: {string.Join("  ", parts)}");
        }
        var e = r.Exclusion;
        var ex = new List<string>();
        if (e.OutlinerPathsToExclude.Count > 0) ex.Add("ExPath=" + string.Join("|", e.OutlinerPathsToExclude));
        if (e.TypesToExclude.Count > 0) ex.Add("ExType=" + string.Join("|", e.TypesToExclude.Select(RuleNames.ShortClass)));
        if (e.ActorTagsToExclude.Count > 0) ex.Add("ExTag=" + string.Join("|", e.ActorTagsToExclude));
        var refs = e.RuleReferences.Select(x => RuleNames.ShortName(x.Path)).ToList();
        if (refs.Count > 0) ex.Add("ExRule=" + string.Join("|", refs));
        if (e.ExcludeIfNotSpatiallyLoaded) ex.Add("ExNotSpatial");
        if (e.IsInsideLevelInstance is not null) ex.Add("ExInsideLI=" + e.IsInsideLevelInstance);
        if (ex.Count > 0) summary.AppendLine("    " + string.Join("  ", ex));
    }
}
var s = snapshot.Settings;
summary.AppendLine();
summary.AppendLine("IgnoredPaths DL: " + string.Join(" | ", s.OutlinerPathsIgnoredByDataLayerRules));
summary.AppendLine("IgnoredPaths RG: " + string.Join(" | ", s.OutlinerPathsIgnoredByRuntimeGridRules));
summary.AppendLine("IgnoredPaths HLOD: " + string.Join(" | ", s.OutlinerPathsIgnoredByHLODLayerRules));
summary.AppendLine("IgnoredTypes DL: " + string.Join(" | ", s.ActorTypesIgnoredByDataLayerRules.Select(RuleNames.ShortClass)));
summary.AppendLine("IgnoredTypes RG: " + string.Join(" | ", s.ActorTypesIgnoredByRuntimeGridRules.Select(RuleNames.ShortClass)));
summary.AppendLine("IgnoredTypes HLOD: " + string.Join(" | ", s.ActorTypesIgnoredByHLODLayerRules.Select(RuleNames.ShortClass)));
summary.AppendLine("ClearPaths DL: " + string.Join(" | ", s.OutlinerPathsToClearDataLayers));
summary.AppendLine("ClearPaths RG: " + string.Join(" | ", s.OutlinerPathsToClearRuntimeGrid));
summary.AppendLine("ForceExcludePaths HLOD: " + string.Join(" | ", s.OutlinerPathsToForceExcludeFromHLOD));
summary.AppendLine("ClearTypes DL: " + string.Join(" | ", s.ActorTypesToClearDataLayers.Select(RuleNames.ShortClass)));
summary.AppendLine("ClearTypes RG: " + string.Join(" | ", s.ActorTypesToClearRuntimeGrid.Select(RuleNames.ShortClass)));
summary.AppendLine("ForceExcludeTypes HLOD: " + string.Join(" | ", s.ActorTypesToForceExcludeFromHLOD.Select(RuleNames.ShortClass)));
File.WriteAllText(Path.Combine(outDir, "rules-summary.txt"), summary.ToString());

// ------------------------------------------------------------------ log parsing
var applying = new Regex(@"LogWorldPartitionRuleBuilder: Display: Applying rules on actor: (.+)$");
var skipping = new Regex(@"Skipping rule application for actor \[([^\]]+)\]");
var actorRule = new Regex(@"actor '([^']+)' using rule '([^']+)'");
var ruleActor = new Regex(@"Rule '([^']+)' includes actor '([^']+)'");
var multi = new Regex(@"Actor '([^']+)' matches multiple (HLODLayer|RuntimeGrid|DataLayer) rules \(\d+\): \[([^\]]*)\]");

var actors = new List<string>();
var seen = new HashSet<string>(StringComparer.Ordinal);
var skipped = new HashSet<string>(StringComparer.Ordinal);
var logMatches = new Dictionary<string, Dictionary<RuleFamily, HashSet<string>>>(StringComparer.Ordinal);

RuleFamily? FamilyOf(string ruleName) => snapshot.Find(ruleName)?.Family;

void AddMatch(string actor, string rule)
{
    if (FamilyOf(rule) is not { } family) return;
    if (!logMatches.TryGetValue(actor, out var map)) logMatches[actor] = map = new();
    if (!map.TryGetValue(family, out var set)) map[family] = set = new(StringComparer.OrdinalIgnoreCase);
    set.Add(rule);
}

foreach (var line in File.ReadLines(logPath))
{
    if (!line.Contains("LogWorldPartitionRule", StringComparison.Ordinal)) continue;
    Match m;
    if ((m = applying.Match(line)).Success)
    {
        var p = m.Groups[1].Value.Trim();
        if (seen.Add(p)) actors.Add(p);
        continue;
    }
    if ((m = skipping.Match(line)).Success) { skipped.Add(m.Groups[1].Value.Trim()); continue; }
    if ((m = actorRule.Match(line)).Success) { AddMatch(m.Groups[1].Value, m.Groups[2].Value); continue; }
    if ((m = ruleActor.Match(line)).Success) { AddMatch(m.Groups[2].Value, m.Groups[1].Value); continue; }
    if ((m = multi.Match(line)).Success)
        foreach (var r in m.Groups[3].Value.Split(',', StringSplitOptions.TrimEntries | StringSplitOptions.RemoveEmptyEntries))
            AddMatch(m.Groups[1].Value, r);
}
var skippedOnly = skipped.Where(p => !seen.Contains(p)).ToList();

// ------------------------------------------------------------------ evaluation
var evaluator = new RuleEvaluator(snapshot);
// Per actor, per family: category.
// Unvisited  = every registered rule is definitely False on the outliner path alone (no other fact can change it).
// Ignored    = IsActorIgnoredByRules definitely true (settings lists).
// Forced     = forced settings bypass the rules.
// OnPath     = at least one rule matches from the path alone.
// Possible   = at least one rule still depends on type / bounds / tags / grid.
var cats = new Dictionary<string, Dictionary<RuleFamily, string>>(StringComparer.Ordinal);
var candidateCounts = families.ToDictionary(f => f, _ => new Dictionary<string, int>(StringComparer.OrdinalIgnoreCase));
var ruleTrueCounts = new Dictionary<string, int>(StringComparer.OrdinalIgnoreCase);
var ruleUnknownCounts = new Dictionary<string, int>(StringComparer.OrdinalIgnoreCase);
var divergence = new List<string>();

foreach (var path in actors)
{
    var result = evaluator.Evaluate(new ActorFacts { OutlinerPath = path });
    var map = new Dictionary<RuleFamily, string>();
    foreach (var ft in result.Families)
    {
        string cat;
        if (ft.Ignored == Tri.True) cat = "Ignored";
        else if (ft.Forced == Tri.True && ft.Ignored == Tri.False) cat = "Forced";
        else if (ft.Rules.Any(r => r.Match == Tri.True)) cat = "OnPath";
        else if (ft.Rules.Any(r => r.Match == Tri.Unknown) || ft.Ignored == Tri.Unknown || ft.Forced == Tri.Unknown) cat = "Possible";
        else cat = "Unvisited";
        map[ft.Family] = cat;

        foreach (var r in ft.Rules)
        {
            if (r.Match == Tri.True) ruleTrueCounts[r.Rule.Name] = ruleTrueCounts.GetValueOrDefault(r.Rule.Name) + 1;
            else if (r.Match == Tri.Unknown) ruleUnknownCounts[r.Rule.Name] = ruleUnknownCounts.GetValueOrDefault(r.Rule.Name) + 1;
        }
        if (cat == "Possible")
            foreach (var r in ft.Rules.Where(r => r.Match == Tri.Unknown))
                candidateCounts[ft.Family][r.Rule.Name] = candidateCounts[ft.Family].GetValueOrDefault(r.Rule.Name) + 1;

        if (cat == "Unvisited" && logMatches.TryGetValue(path, out var lm) && lm.TryGetValue(ft.Family, out var rules))
            divergence.Add($"{ft.Family}\t{path}\t{string.Join(",", rules)}");
    }
    cats[path] = map;
}

// ------------------------------------------------------------------ rule-side: path entries that hit no actor
var pathEntries = new List<(string Owner, string Kind, string Entry)>();
foreach (var r in snapshot.Rules.Where(r => r.IsRegistered))
{
    foreach (var c in r.Conditions)
        foreach (var p in c.OutlinerPathContains) pathEntries.Add((r.Name, $"cond#{c.Index}", p));
    foreach (var p in r.Exclusion.OutlinerPathsToExclude) pathEntries.Add((r.Name, "exclude", p));
}
foreach (var (list, name) in new[]
{
    (s.OutlinerPathsIgnoredByDataLayerRules, "OutlinerPathsIgnoredByDataLayerRules"),
    (s.OutlinerPathsIgnoredByRuntimeGridRules, "OutlinerPathsIgnoredByRuntimeGridRules"),
    (s.OutlinerPathsIgnoredByHLODLayerRules, "OutlinerPathsIgnoredByHLODLayerRules"),
    (s.OutlinerPathsToClearDataLayers, "OutlinerPathsToClearDataLayers"),
    (s.OutlinerPathsToClearRuntimeGrid, "OutlinerPathsToClearRuntimeGrid"),
    (s.OutlinerPathsToForceExcludeFromHLOD, "OutlinerPathsToForceExcludeFromHLOD"),
})
    foreach (var p in list.Where(p => p.Length > 0)) pathEntries.Add(("(settings)", name, p));

var deadEntries = new StringBuilder("Owner\tKind\tEntry\tActorHits\n");
foreach (var (owner, kind, entry) in pathEntries)
{
    var hits = actors.Count(a => a.Contains(entry, StringComparison.OrdinalIgnoreCase));
    deadEntries.Append($"{owner}\t{kind}\t{entry}\t{hits}\n");
}
File.WriteAllText(Path.Combine(outDir, "rule-path-entries.tsv"), deadEntries.ToString());

// ------------------------------------------------------------------ reports
string Parent(string p) { var i = p.LastIndexOf('/'); return i > 0 ? p[..i] : p; }
string Prefix(string p, int depth) => string.Join('/', p.Split('/').Take(depth));

var report = new StringBuilder();
report.AppendLine($"Actors processed (Applying rules on actor): {actors.Count}");
report.AppendLine($"Actors only seen as skipped (checkout): {skippedOnly.Count}");
report.AppendLine();
foreach (var family in families)
{
    var g = actors.GroupBy(a => cats[a][family]).ToDictionary(x => x.Key, x => x.Count());
    report.AppendLine($"{family}: " + string.Join(", ", new[] { "Unvisited", "Ignored", "Forced", "OnPath", "Possible" }.Select(k => $"{k}={g.GetValueOrDefault(k)}")));
    var logged = actors.Count(a => logMatches.TryGetValue(a, out var m) && m.ContainsKey(family));
    report.AppendLine($"    log shows a rule of this family on {logged} actors");
    report.AppendLine("    candidate rules for 'Possible' actors: " + string.Join(", ",
        candidateCounts[family].OrderByDescending(x => x.Value).Take(8).Select(x => $"{x.Key}={x.Value}")));
}
bool NoRule(string a, RuleFamily f) => cats[a][f] is "Unvisited" or "Ignored";
var allUnvisited = actors.Where(a => families.All(f => NoRule(a, f))).ToHashSet(StringComparer.Ordinal);
var strictAll = actors.Where(a => families.All(f => cats[a][f] == "Unvisited")).ToList();
report.AppendLine();
report.AppendLine($"Actors no rule of any family can reach (Unvisited or Ignored in all 3): {allUnvisited.Count}");
report.AppendLine($"   of which Unvisited (no ignore list) in all 3: {strictAll.Count}");
report.AppendLine($"Divergences (evaluator says Unvisited but log shows a match): {divergence.Count}");
report.AppendLine();
report.AppendLine("Rules that never match on path and never stay Unknown (dead for this population):");
foreach (var family in families)
    foreach (var r in snapshot.Registered(family))
        if (ruleTrueCounts.GetValueOrDefault(r.Name) == 0 && ruleUnknownCounts.GetValueOrDefault(r.Name) == 0)
            report.AppendLine($"    {family} {r.Name}");
report.AppendLine();
report.AppendLine("Rule path entries with 0 actor hits:");
foreach (var (owner, kind, entry) in pathEntries)
    if (!actors.Any(a => a.Contains(entry, StringComparison.OrdinalIgnoreCase)))
        report.AppendLine($"    {owner} [{kind}] '{entry}'");

foreach (var family in families)
{
    report.AppendLine();
    report.AppendLine($"== {family}: top containers with Unvisited actors (container, unvisited/total) ==");
    var byContainer = actors.GroupBy(Parent)
        .Select(gp => (Container: gp.Key, Total: gp.Count(), Unv: gp.Count(a => cats[a][family] == "Unvisited")))
        .Where(x => x.Unv > 0).OrderByDescending(x => x.Unv).Take(40);
    foreach (var x in byContainer) report.AppendLine($"    {x.Unv,6}/{x.Total,-6} {x.Container}");
    report.AppendLine($"-- {family}: rollup by depth 3/4 --");
    foreach (var depth in new[] { 3, 4 })
        foreach (var x in actors.GroupBy(a => Prefix(a, depth))
                     .Select(gp => (Key: gp.Key, Total: gp.Count(), Unv: gp.Count(a => cats[a][family] == "Unvisited")))
                     .Where(x => x.Unv > 0).OrderByDescending(x => x.Unv).Take(15))
            report.AppendLine($"    d{depth} {x.Unv,6}/{x.Total,-6} {x.Key}");
}

report.AppendLine();
report.AppendLine("== All families: containers whose actors no rule can reach ==");
foreach (var x in actors.GroupBy(Parent)
             .Select(gp => (Container: gp.Key, Total: gp.Count(), Unv: gp.Count(a => allUnvisited.Contains(a))))
             .Where(x => x.Unv > 0).OrderByDescending(x => x.Unv).Take(60))
    report.AppendLine($"    {x.Unv,6}/{x.Total,-6} {x.Container}");

File.WriteAllText(Path.Combine(outDir, "report.txt"), report.ToString());

var csv = new StringBuilder("OutlinerPath,DataLayer,RuntimeGrid,HLODLayer,LogDataLayer,LogRuntimeGrid,LogHLOD\n");
foreach (var a in actors)
{
    logMatches.TryGetValue(a, out var lm);
    string L(RuleFamily f) => lm is not null && lm.TryGetValue(f, out var r) ? string.Join("|", r) : "";
    csv.Append('"').Append(a.Replace("\"", "\"\"")).Append("\",")
       .Append(string.Join(",", families.Select(f => cats[a][f]))).Append(',')
       .Append(string.Join(",", families.Select(L))).Append('\n');
}
File.WriteAllText(Path.Combine(outDir, "actors.csv"), csv.ToString());
File.WriteAllLines(Path.Combine(outDir, "divergences.tsv"), divergence);
Console.WriteLine(report.ToString());

using System.Net.Http.Headers;
using System.Text;
using System.Text.Json;

public sealed class RawMcp(string url)
{
    private static readonly HttpClient Http = new() { Timeout = TimeSpan.FromMinutes(10) };
    private string? _session;
    private string? _protocol;
    private int _id = 1;

    public async Task InitAsync()
    {
        var init = await SendAsync("initialize", new { protocolVersion = "2025-03-26", capabilities = new { }, clientInfo = new { name = "WPCoverage", version = "1.0" } });
        _protocol = init?.TryGetProperty("protocolVersion", out var v) == true ? v.GetString() : null;
        using var _ = await PostAsync(JsonSerializer.Serialize(new { jsonrpc = "2.0", method = "notifications/initialized" }));
    }

    public async Task<string> ToolAsync(string name, object args)
    {
        var result = await SendAsync("tools/call", new { name, arguments = args }) ?? throw new Exception("no result");
        var sb = new StringBuilder();
        if (result.TryGetProperty("content", out var content))
            foreach (var part in content.EnumerateArray())
                if (part.TryGetProperty("text", out var t)) sb.Append(t.GetString());
        if (result.TryGetProperty("isError", out var e) && e.ValueKind == JsonValueKind.True) throw new Exception(sb.ToString());
        return sb.ToString();
    }

    public Task<string> CallAsync(string toolset, string tool, object? args) =>
        ToolAsync("call_tool", new { toolset_name = toolset, tool_name = tool, arguments = args ?? new { } });

    private async Task<JsonElement?> SendAsync(string method, object p)
    {
        var id = _id++;
        using var resp = await PostAsync(JsonSerializer.Serialize(new { jsonrpc = "2.0", id, method, @params = p }));
        var payload = await resp.Content.ReadAsStringAsync();
        if (!resp.IsSuccessStatusCode) throw new Exception($"{(int)resp.StatusCode}: {payload}");
        if (resp.Headers.TryGetValues("Mcp-Session-Id", out var s)) _session = s.FirstOrDefault();
        var isStream = resp.Content.Headers.ContentType?.MediaType?.Contains("event-stream") == true;
        var messages = isStream
            ? payload.Split('\n').Where(l => l.StartsWith("data:")).Select(l => l[5..].Trim())
            : new[] { payload };
        foreach (var m in messages)
        {
            using var doc = JsonDocument.Parse(m);
            var root = doc.RootElement;
            if (!root.TryGetProperty("id", out var rid) || rid.ValueKind != JsonValueKind.Number || rid.GetInt32() != id) continue;
            if (root.TryGetProperty("error", out var err)) throw new Exception(err.GetRawText());
            return root.TryGetProperty("result", out var r) ? r.Clone() : null;
        }
        return null;
    }

    private Task<HttpResponseMessage> PostAsync(string body)
    {
        var req = new HttpRequestMessage(HttpMethod.Post, url) { Content = new StringContent(body, Encoding.UTF8, "application/json") };
        req.Headers.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));
        req.Headers.Accept.Add(new MediaTypeWithQualityHeaderValue("text/event-stream"));
        if (_session is not null) req.Headers.TryAddWithoutValidation("Mcp-Session-Id", _session);
        if (_protocol is not null) req.Headers.TryAddWithoutValidation("MCP-Protocol-Version", _protocol);
        return Http.SendAsync(req);
    }
}

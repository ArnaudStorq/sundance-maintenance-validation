Parent: [Custom Tools](../CustomTools.md)

# Exclude From Rules tag & Rule Exclusion column

The `ExcludeFromRules` actor tag that **freezes** an actor against the World Partition
rule system, plus a **"Rule Exclusion"** Scene Outliner column to audit which actors are
currently excluded.

Source:

- `D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionRuleSettings.h`
  — the `ActorTagExcludedFromRules` setting.
- `D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionRuleSubsystem.h/.cpp`
  — base tag check, cook-time strip, and `IsActorExcludedFromRules`.
- `D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\ExcludeFromRulesOutlinerColumn.h/.cpp`
  — the outliner column.
- `D:\Sun\Sundance\Source\WorldBuildingEditor\WorldBuildingEditorModule.cpp` — column registration.

Changelist: **1972540**.

## Why it exists

The [World Partition rule system](../WorldPartitionRules.md) reassigns `RuntimeGrid`,
DataLayers and HLOD per actor — on the headless builder and on every save. When a designer
manually aligns a value (e.g. bringing a referee onto its referencer's `RuntimeGrid` to
clear a `WorldPartitionChangelistValidator` "different runtime grid" error), the next rule
pass would silently overwrite it again. The `ExcludeFromRules` tag tells the rule system
to **skip** that actor entirely, so the manual value sticks. This is the foundation the
[Runtime Grid Reference Tools](RuntimeGridReferenceTools.md) batch fixer
relies on when it tags both sides of each couple.

## The `ExcludeFromRules` tag

- Configurable name via `UWorldPartitionRuleSettings::ActorTagExcludedFromRules`
  (Project Settings → Editor → *WorldPartition Rules* → *Ignored*), default
  `"ExcludeFromRules"`. Renamable without a recompile.
- To freeze an actor, add the tag to its **Tags** array (Details → *Actor* → *Tags*).
- It is a **global** exclusion: the check lives in the base
  `UWorldPartitionRuleSubsystem::IsActorIgnoredByRules`, so **all three** rule domains
  (RuntimeGrid, DataLayer, HLOD) honor it through their `Super::` call.
- Covered paths: the headless `WorldPartitionRuleBuilder` **and** the on-save auto-apply —
  both early-out on `IsActorIgnoredByRules`. Works for **loaded actors** and **unloaded
  actor descriptors**.

> ⚠ The tag only stops the **rule system** from reassigning values. It does **not**
> suppress the native `WorldPartitionChangelistValidator` — you must first align the values
> by hand, then tag to lock. See [Fixing map-check issues](../FixingMapCheckIssues.md).

## Cook-time stripping

The tag is editor-only metadata. A **cook-only** `PreSave` hook
(`OnStripExcludeTagsBeforeCook`, gated on `SaveContext.IsCooking()`) removes it from the
cooked actor packages, so packaged builds never ship the inert tag. The source `.uasset`
files in Perforce **keep** the tag, so editor rule exclusion keeps working.

## The "Rule Exclusion" outliner column

Because excluded actors are otherwise skipped silently, this column lets you **audit** them
directly in the Scene Outliner.

- Shows **`Excluded`** when the actor is ignored by the rule system, and an **empty** cell
  otherwise.
- Backed by the new public `UWorldPartitionRuleSubsystem::IsActorExcludedFromRules`, which
  returns true if **any** of the three rule subsystems ignores the actor — so it reflects
  the tag as well as the type / outliner-path ignore lists.
- Evaluates both **actor descriptors** (unloaded actors in a partitioned world) and
  **loaded actors**, including **inner actors of non-partitioned Level Instances** (which
  have no descriptor).
- Registered right after the **"DL Rules"** column, **hidden by default**, and toggleable
  from the outliner header's **right-click** column menu.

> **Note — `Excluded` is not always the tag.** The column shows `Excluded` for **any**
> exclusion reason, including the per-domain **type ignore lists** in `DefaultEditor.ini`:
> `ActorTypesIgnoredByDataLayerRules`, `ActorTypesIgnoredByRuntimeGridRules` and
> `ActorTypesIgnoredByHLODLayerRules`. Engine-managed singletons such as
> `WorldDataLayers` (`/Script/Engine.WorldDataLayers`) and `WorldPartitionMiniMap`
> (`/Script/Engine.WorldPartitionMiniMap`) are listed there, so they read `Excluded`
> **by type — never because they carry the `ExcludeFromRules` tag**. Don't mistake a
> type-ignored system actor for one you (or the fixup tool) tagged: to confirm a real
> tag, check the actor's **Details → Actor → Tags** for `ExcludeFromRules`.

## See also

- [Runtime Grid Reference Tools](RuntimeGridReferenceTools.md) — the scan + fix commands; the fixer applies this tag to both sides of each couple
- [World Partition rules](../WorldPartitionRules.md) — how `RuntimeGrid` / DataLayers / HLOD are normally applied
- [Runtime Grid rules](../WorldPartitionRulesAnalysis/RuntimeGridRules.md) — the RuntimeGrid domain in detail
- [Fixing map-check issues](../FixingMapCheckIssues.md) — the validator errors this unblocks
- [Perforce source control](../PerforceSourceControl.md) — checkout-before-save, changelists

---

**In this section:** [Runtime Grid Reference Tools](RuntimeGridReferenceTools.md) | [Delete World Event](DeleteWorldEvent.md) | **Exclude From Rules tag**

Back to [Custom Tools](../CustomTools.md).

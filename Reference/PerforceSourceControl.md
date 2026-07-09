# Perforce (P4) source control

How the builders and validators interact with Perforce: checkout-before-save,
diagnosing locked files, and changelist-level validation.

---

## Checkout before save

A package must be writable before it can be saved. Builders never blindly write; they
check whether a package is checkoutable and skip (or bail) otherwise.

The shared utility is `WorldPartitionRules::FPackageUtility::CanCheckoutPackage`
(`WorldPartitionRuleSubsystem.cpp:249`). It queries `ISourceControlState` and returns
`false` (with a human reason) when the file is missing, in an unknown state, or checked
out by someone else:

```249:265:D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionRuleSubsystem.cpp
bool FPackageUtility::CanCheckoutPackage(const FString& PackageName, const bool bForceUpdate, FString* OutCheckoutFailureReason)
{
	// ... GetState (with ForceUpdate retry if unknown) ...
	if (SourceControlState->IsCheckedOutOther())
	{
		*OutCheckoutFailureReason = SourceControlState->GetDisplayTooltip().ToString();
		return false;
	}
	// IsCheckedOut()/IsAdded() -> true; IsSourceControlled() && CanCheckout() -> true; else reason.
```

Actual checkout at save time goes through `FPackageSourceControlHelper::Checkout` (the
`PackageHelper` passed into every builder `RunInternal`). Patterns by builder:

| Builder | Pre-flight | Checkout |
|---------|-----------|----------|
| `UWorldPartitionRuleBuilder` | `CanCheckoutPackage` in `ShouldProcessActor` → **skip** if not checkoutable | at save via `SavePackages(PackagesToSave, PackageHelper)` |
| `UWorldPartitionFixupNonPartitionedActorsBuilder` | none (direct) | `PackageHelper.Checkout(pkg)`; on failure logs `Checkout FAILED for '...'`, increments counter, returns early |
| `ULevelInstanceTraversalBuilder` | pre-caches `GetState(..., ForceUpdate)` for all actor packages in `UpdateCanCheckoutStatus` | optional bulk checkout |
| `UWorldPartitionResaveActorsRecursiveBuilder` | `CanCheckoutPackage` → logs `STATUS=SKIP-Checkout reason=...` | at save |

> ⚠ Note: the recap mentioned `IPlatformFile::IsReadOnly()` and
> `FPerforceSourceControlState::GetHistoryItem()` / `checkedOutBy` for locked-file
> diagnostics. In the current `WorldBuildingEditor` builders, locked-file handling goes
> through `ISourceControlState::IsCheckedOutOther()` + `GetDisplayTooltip()`, **not**
> `GetHistoryItem`. A richer "checked out by <user>" dialog exists in the editor UI
> (`LandscapeProxyContextMenuExtension.cpp:422`, uses `IsCheckedOutOther(&Owner)`), but
> the builders themselves only log the tooltip reason.

---

## Diagnosing locked files

When a package can't be checked out because someone else holds it, the failure reason
comes from `GetDisplayTooltip()` (e.g. *"Checked out by jprice @ //sun/Dev"*). The
practical playbook when a batch reports locked files:

1. Read the builder log for the skipped/failed packages and their reasons.
2. Identify the owner and the depot path from the tooltip.
3. Either ask the owner to submit/revert, or scope the run to exclude those paths and
   handle them later.

---

## Changelists

- **Split a big changelist**: move the problematic actors out of a large CL into a
  small, focused one so it can be reviewed/reverted independently. This is the same
  small-reversible-steps discipline used everywhere in this project.
- **Every external actor edit is its own file** (OFPA), so a "one property change"
  can still be hundreds of files. Keep batches reviewable.

---

## Changelist-level validation

Two engine validators (in the `DataValidation` plugin) enforce changelist
completeness at submit; they are the reason a CL fails when a referenced object is
missing from it.

### `UDataValidationChangelist::IsDataValid`

Gathers dependencies for every modified package and, for each **referenced** package
not in the changelist, queries Perforce and emits:

| Referenced package state | Result | Message |
|--------------------------|--------|---------|
| Added, not in CL | **Error** | `{0} is missing from this changelist (referenced from {1}).` |
| Checked out, not in CL | **Warning** (WB tweak to match Peeves) | same text |
| Not at head | Warning | `{0} is referenced but is not at the latest revision '{1}' ...` |
| Not in depot, file missing | Error | `{0} is referenced and cannot be found in workspace ...` |
| Not in depot, file exists | Error | `{0} is referenced and must also be added to revision control ...` |

```151:165:D:\Sun\Engine\Plugins\Editor\DataValidation\Source\DataValidation\Private\DataValidationChangelist.cpp
			//@third party code - AVA BEGIN [davjones] checked out files should be a warning but added files should be an error. We want to match how we validate in Peeves.
			FText CurrentError = FText::Format(LOCTEXT("DataValidation.Changelist.Error", "{0} is missing from this changelist (referenced from {1})."), ...);
			if (ExternalDependencyFileState->IsAdded()) { bHasChangelistErrors = true; Context.AddError(CurrentError); }
			else                                        { Context.AddWarning(CurrentError); }
```

This is why, when you touch an actor that references `WorldDataLayers`, the
`WorldDataLayers` package (and referenced external actors) must be in the **same
changelist**.

### `UWorldPartitionChangelistValidator`

Runs the full World Partition error pipeline (`UWorldPartition::CheckForErrors`) but
**scoped to the changelist** — it only reports on actors/data-layers actually in the
CL (`RelevantActorGuids`, `RelevantMap`, relevant data-layer sets). Top-level failure:

> *"This changelist contains modifications that aren't valid at the world partition
> level. Please see the message log for the errors preceding this message."*

Its per-handler messages mirror the MapCheck ones (invalid runtime grid = error,
invalid HLOD layer = warning, invalid reference = error but HLOD actors downgraded to
warning). Data-layer submits are tracked so `WorldDataLayers`-related errors are only
raised when that asset is part of the CL.

There is also `UDirtyFilesChangelistValidator` → *"This changelist contains an unsaved
asset. Please save to proceed."*

---

## Related changelists

- [WorldEvent DataLayers checkout check (CL 1758012)](../WorkDoneByChangelists/P4-History/2026-03-11-09-21-worldevent-datalayers-checkout-check.md)
- [Revert last WP Rules processing (CL 1844521)](../WorkDoneByChangelists/P4-History/2026-04-22-12-33-revert-wp-rules-processing.md)

## See also

- [Peeves submit validation](PeevesSubmitValidation.md) (runs these validators at submit)
- [Transform drift](TransformDrift.md) (diff-then-revert discipline)

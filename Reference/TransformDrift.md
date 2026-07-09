# 4. Transform drift (RelativeLocation / Rotation / Scale3D)

The single most dangerous class of bug in this whole effort. A resave that was only
supposed to touch streaming properties silently changed an actor's
`RelativeLocation`, `RelativeRotation`, or `RelativeScale3D` — i.e. it **moved
content**. This is unacceptable, because it corrupts art with no visible cause.

---

## What happened

A CI (TeamCity) automated run of `UWorldPartitionRuleBuilder` resaved Level Instance
`.umap` assets and their external actors, and in doing so wrote back **drifted**
relative-transform values (in some cases on `EditorOnlySeasonsDefaultMesh` and Book
actors). The damaging changelist touched **~8,700 files**.

Key distinction: the problem was the **package saved with drifted values**, not a
transient in-memory tweak. Once the bad values were on disk, everything downstream
inherited them.

---

## Root cause

`PackagesToSave` — the builder's working list of dirty packages — was being
**serialized** into the asset instead of staying purely in memory. When a package's
transient working state leaks into what gets written, saves capture more than intended
and reference lifetime gets confused, which is how recomputed relative transforms ended
up persisted. The fix marked it transient:

```cpp
// WorldPartitionRuleBuilder.h
UPROPERTY(Transient)
TArray<TObjectPtr<UPackage>> PackagesToSave;
```

Two companion fixes hardened lifetime/behavior:

- **Release kept references** — the builder held loaded packages longer than needed,
  bloating memory and keeping objects alive across passes.
- **Keep Level Instance references during processing** — references needed while
  processing a Level Instance are retained so GC does not collect them mid-pass.
- **Skip Level Instances with non-uniform scaling** — their transforms can't be safely
  recomputed, so they are left alone.
- **Only commit real changes** — no empty/no-op commits (a no-op resave is still a risk
  surface).

---

## The immediate response: revert

When the bad run was found, the safe action was to **revert the whole changelist**
(the ~8,700-file one) rather than try to hand-patch it. Only after the builder was
hardened was rule processing trusted again. Then targeted passes restored correct
relative values on the assets the CI run had wrongly modified, and later specifically
on **Book** actors that were still off.

---

## The standing policy (how drift is handled now)

The final decision was pragmatic and is the rule to follow going forward:

> **The fixup/rule tooling stays as simple as possible. Drift verification is done
> manually by the engineer at review time**, not baked into the builder.

Concretely, the workflow after any resave that could touch transforms:

1. Run the builder / fixup.
2. `p4 diff` (or the changelist diff) the affected packages.
3. If `RelativeLocation` / `RelativeRotation` / `RelativeScale3D` changed on any actor
   that shouldn't have moved → **revert that package entirely** (do not submit).
4. Only submit changes that are purely the intended streaming-property edits.

The reason for keeping the check human rather than automated: the builder is shared and
must stay minimal/predictable; a transform-diff heuristic inside it adds risk and
false-positives. A human reviewing the diff is the reliable gate.

> "Relative" matters: an actor inside a Level Instance stores its position **relative
> to** the instance, not in world space. The original bug was in how those relative
> values were recomputed during save — which is exactly why the guard is about the
> `Relative*` fields.

---

## Related changelists

- [Revert last WP Rules processing (CL 1844521)](../Reports/P4-History/2026-04-22-12-33-revert-wp-rules-processing.md)
- [Fix WP rules `PackagesToSave` transient (CL 1841026)](../Reports/P4-History/2026-04-21-06-18-fix-wp-rules-packagestosave.md)
- [Release kept references (CL 1837219)](../Reports/P4-History/2026-04-17-14-07-release-references-wp-rules.md)
- [Fix relative transform — TeamCity (CL 1804673)](../Reports/P4-History/2026-03-27-14-28-fix-relative-transform-teamcity.md)
- [Fix relative transform — more levels (CL 1812627)](../Reports/P4-History/2026-04-02-09-49-fix-relative-transform-levels.md)
- [Fix Books relative transform (CL 1827113)](../Reports/P4-History/2026-04-13-09-27-fix-books-relative-transform.md)

## See also

- [Topic 3 — Builders & commandlets](BuildersAndCommandlets.md)
- Plain-language: [`WorkDoneByTopic/WorldPartitionRules.md`](../WorkDoneByTopic/WorldPartitionRules.md) §4–5

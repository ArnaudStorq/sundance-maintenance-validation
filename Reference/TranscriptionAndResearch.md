# 11. Transcription & research

The "keep up with what the experts said" workstream: faithfully capturing knowledge
from talks, screen-shares, and conference notes so it can be searched and acted on
later.

---

## Local transcription tooling

Small Python helpers live next to the World Partition source
(`D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\tools\`):

| Script | Purpose |
|--------|---------|
| `transcribe_video.py` | audio → timestamped transcript (`transcript.txt`, `.srt`, `segments.json[l]`, `meta.json`) |
| `extract_video_frames.py` | pull frames from a video at intervals |
| `crop_image_region.py` | crop a region of interest (e.g. a menu/columns panel) from a frame |

Outputs land under `tools/transcripts/<name>/` and `.tmp_video_summary/`
(frames + crops + `index.json` + a consolidated transcript). Example on disk:
`tools/transcripts/Phil_ExplicationTeamCity_VerificationRules/`.

---

## Phil / William videos (World Partition, HLOD, rules)

Screen-share sessions and talks by Phil (Philippe St-Jean — author of several of the
AVA engine modifications, e.g. the HLOD-relevance skip in
[Topic 1](WorldPartitionStreamingProperties.md)) and William were transcribed,
summarised, and turned into action items. Topics covered: HLOD, **Include In HLOD**,
World Partition **Rules**, **SmallGrid**.

Concrete knowledge captured from Phil's **TeamCity verification** walkthrough:

- The rule/verification builders run on a **nightly schedule** on TeamCity, split by
  day: e.g. **Tuesday/Thursday = Mission & Dungeon**, other days = other content,
  and the **weekend runs everything with no filter**.
- Some jobs are also launched **manually** ("à la mitaine") when needed.
- Results feed an **HTML reporting "hub"** (the `Report/*.html` snapshots/trends:
  `WorldStreamingHub.html`, `HLODTrend.html`, `StreamingGenerationSnapshot.html`,
  `WorldPartitionRulesSnapshot.html`, …) that **updates once per day**.
- The point of the hub: keep an eye on **what got signed/submitted automatically**,
  understand whether a run produced errors, and judge whether the auto-signed result is
  actually correct.

This is the process being **adopted and continued** — the goal was for Phil to show his
workflow so it could be taken over.

---

## Why this is a "reference" topic

The transcripts and summaries are the primary record of design intent that isn't in the
code — e.g. *why* a grid is sized a certain way, or *how often* the verification runs.
When a decision is questioned later, the transcript is the citation.

## See also

- [Topic 7 — Rules, SmallGrid & IncludeInHLOD](RulesSmallGridIncludeInHLOD.md)
- [Topic 1 — Streaming properties](WorldPartitionStreamingProperties.md) (the `[philippe.st-jean]` engine changes)

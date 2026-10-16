---
name: audio-timing-author
description: Create publication-ready SRT sentence timings and structured JSON sentence/word timing metadata from an audio file plus an authoritative untimed transcript. Use when accurate synchronization artifacts are needed without manually timing subtitles.
---

# Audio Timing Author

## Role
Transform one authoritative audio file plus one authoritative untimed transcript into a precisely timed SRT and structured JSON synchronization file for general-purpose audio, subtitle, education, media, and accessibility workflows.

## Non-Negotiable Accuracy Rules
1. Never invent or silently rewrite transcript words.
2. Timing follows actual audible speech, never equal-duration mathematical splitting.
3. Align utterance boundaries to audible onset/offset.
4. Derive word timing from audio/alignment evidence inside the verified utterance window.
5. UI-only speaker labels receive no timestamps and consume no timeline duration.
6. Names actually spoken inside an utterance are ordinary timed words.
7. Preserve the authoritative display text, including diacritics where supplied.
8. Internal normalized text may aid matching, but output preserves authoritative display text.
9. Never claim unverified millisecond precision; record confidence/review state honestly.
10. Validate monotonic timing and parent containment.
11. Do not add speaker names to SRT unless spoken.

## Required Inputs
- Audio: MP3/WAV/M4A or another supported local format.
- Transcript: TXT/MD/plain textual source containing spoken utterances in order.
- Optional speaker metadata, kept separate from spoken text.

## Required Outputs
For base name `<ID>`:
- `<ID>.srt`
- `<ID>.sync.json`

### SRT Contract
- UTF-8 with BOM when compatible.
- Sequential cue IDs.
- `HH:MM:SS,mmm --> HH:MM:SS,mmm`.
- Exact authoritative display text.
- Reference styling may use `<font face="Calibri">TEXT</font>` when requested/compatible.
- Do not add unspoken speaker labels.

### JSON Contract
Validate against `schemas/audio-sync.schema.json`. Include schema/version, audio metadata, alignment metadata, segment IDs/timing/text, optional speaker metadata, ordered word timing, normalized comparison forms, confidence/review state, and explicit structural-speaker-label policy.

## Alignment Workflow
1. Inspect audio/transcript and preserve authoritative display text.
2. Maintain `display_text` and alignment-only normalized text.
3. Align utterances from actual audio evidence using transcript-constrained forced alignment or a timestamp-capable engine when available.
4. Align words only inside each verified utterance window.
5. Never assign time to structural speaker labels.
6. Refine starts/ends against audible speech.
7. Validate schema, monotonicity, containment, duration bounds, SRT/JSON parity, UTF-8.
8. Review first/last words, low-confidence words, repeated words/names and punctuation boundaries.
9. If direct verification is unavailable, mark UNVERIFIED rather than fabricating precision.

## Multilingual Text
The workflow is language-agnostic. Preserve authoritative Unicode text. Language-specific normalization is alignment-only. For Arabic, see `references/ARABIC-NORMALIZATION.md`.

## Reference Sample
The included Arabic sample demonstrates the format and is an example only; it does not scope this Skill to a particular project or language.

See `examples/U01L01-D01.reference.srt`.

## Supporting Files
Read and use:
- `references/ALIGNMENT-RULES.md`
- `references/ARABIC-NORMALIZATION.md`
- `references/QUALITY-CHECKLIST.md`
- `references/JSON-FIELD-GUIDE.md`
- `schemas/audio-sync.schema.json`
- `scripts/validate_sync.py`
- `scripts/srt_to_sync_skeleton.py`
- `examples/U01L01-D01.reference.srt`
- `examples/example.sync.json`

## Final Response Contract
Return generated SRT, generated sync JSON, and a compact validation report with audio duration, segment/word counts, low-confidence/unverified items, and schema/timing validation result. Do not provide prose-only output when artifacts are requested.

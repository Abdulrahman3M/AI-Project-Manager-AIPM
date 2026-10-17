# Alignment Rules

## Source-of-truth hierarchy
1. Owner-supplied transcript text = authoritative words/display text.
2. Audio = authoritative timing/pronunciation evidence.
3. Generated recognition text = alignment aid only, never a replacement for the transcript.

## Sentence timing
- Locate real audible onset and offset.
- Keep inter-sentence silence outside the utterance timing.
- Never reserve time for UI-only speaker labels.

## Word timing
- Constrain word alignment to its parent sentence.
- Use acoustic/timestamp evidence.
- Preserve token order.
- Repeated tokens must map to their actual occurrence.
- Tokenization follows the authoritative transcript unless the active project defines a more granular canonical token model.

## Accuracy
- No equal mathematical splitting for final output.
- No guessed timestamps presented as verified.
- Low-confidence timing must be flagged for review.

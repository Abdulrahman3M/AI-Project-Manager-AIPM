# JSON Field Guide

`schema`: audio synchronization format identifier.
`version`: format version.
`audio`: immutable facts about referenced audio.
`alignment`: language, method, review state and source policy.
`segments[]`: sentence/utterance timing.
`segments[].speaker`: optional UI metadata; not inherently spoken.
`segments[].text`: authoritative display text.
`segments[].normalized_text`: alignment-only comparison form.
`segments[].words[]`: only words actually spoken.
`confidence`: optional meaningful engine confidence.
`review`: `verified`, `needs_review`, or `unverified`.

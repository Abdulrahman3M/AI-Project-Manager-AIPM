# Quality Checklist

- [ ] Audio duration measured.
- [ ] Transcript preserved exactly.
- [ ] Segment order matches speech order.
- [ ] Requested SRT styling preserved.
- [ ] SRT and JSON segment texts match.
- [ ] Every segment start/end derives from audio evidence.
- [ ] Every final word timing derives from alignment/audio evidence.
- [ ] No structural speaker label consumes timeline duration.
- [ ] Spoken names remain timed.
- [ ] No negative/zero intervals.
- [ ] No word escapes its parent segment.
- [ ] No timestamp exceeds audio duration.
- [ ] JSON validates against schema.
- [ ] Low-confidence items explicitly marked.
- [ ] Outputs are UTF-8 readable.

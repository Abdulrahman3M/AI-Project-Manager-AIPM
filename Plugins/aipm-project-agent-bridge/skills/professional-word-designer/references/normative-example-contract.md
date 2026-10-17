# Normative Example Contract — zero uncovered requirements

Examples are normative evidence of intended execution, not decoration.

## Mandatory rule

Every normative requirement introduced by this Skill must have a stable `REQ-...` ID and at least one mapped `EX-...` example. A release with an uncovered requirement fails the example-coverage gate.

## Example anatomy

Each example contains:
1. requirement ID;
2. scenario;
3. correct execution;
4. prohibited/incorrect execution;
5. acceptance evidence.

The existing 26 illustrated examples remain authoritative for visual component grammar. The v5 Normative Example Library adds fine-grained research, academic, Word, QA and long-document examples so agents are not expected to improvise from abstract prose alone.

Run:

```bash
python scripts/validate_example_coverage.py
```

The validator checks the requirement registry and example coverage file.

## Requirements and examples

- REQ-NE-01 — every normative rule has a stable requirement ID.
- REQ-NE-02 — every requirement maps to >=1 example.
- REQ-NE-03 — every example includes correct, incorrect and acceptance evidence.
- REQ-NE-04 — example coverage must equal 100% before release.

# Rule Source Matrix

This matrix records how the reusable governance baseline was synthesized from three different project-governance styles. It is a design trace, not a claim that the source projects used identical wording.

Legend:

- **✓** — the principle is explicit or strongly equivalent in that source.
- **~** — related principle exists but with a narrower/project-specific form.
- **—** — not a meaningful source for that rule family.
- **Generalized** — reusable form adopted by Project Governance Manager.
- **Scoped** — retained only as a conditional/project-specific pattern.

| Rule family | InfoBank | LLH | Universal AI ToolKit | Result |
|---|:---:|:---:|:---:|---|
| Owner/current instruction has highest project authority | ✓ | ✓ | ✓ | Generalized |
| Preserve existing behavior/data/knowledge outside scope | ✓ | ✓ | ✓ | Generalized |
| Do not expand scope for unrelated improvements | ✓ | ✓ | ✓ | Generalized |
| Read current governance instead of relying on memory | ✓ | ✓ | ✓ | Generalized |
| General rules vs narrow specialist authority | ✓ | ✓ | ~ | Generalized |
| One canonical source of truth | ✓ | ✓ | ✓ | Generalized |
| Avoid competing/duplicated shared logic | ✓ | ✓ | ~ | Generalized |
| Minimum sufficient inspection by default | ✓ | ~ | ✓ | Generalized with full-pre-read exception |
| Mandatory full governance pre-read | — | ✓ | — | Conditional module |
| Proportional testing focused on affected scope | ✓ | ✓ | ✓ | Generalized |
| Runtime execution stronger than syntax/type checks | ✓ | ✓ | ~ | Generalized |
| Never claim unrun verification | ✓ | ✓ | ✓ | Generalized |
| Directly affected documentation updated in same task | ✓ | ✓ | ✓ | Generalized |
| Portable/relative paths | ✓ | ✓ | ~ | Generalized |
| Security/privacy priority | ✓ | ✓ | ✓ | Generalized |
| No secrets/credentials in project files | ~ | ✓ | ✓ | Generalized |
| Evidence-based performance claims | ✓ | ✓ | ~ | Generalized |
| Central ownership for shared capabilities | ✓ | ✓ | ~ | Generalized |
| Demand-driven loading/lifecycle cleanup | ✓ | ✓ | — | Conditional frontend/runtime module |
| Evidence-based temporary cleanup | ✓ | ✓ | ~ | Generalized |
| Honest completion report: changed/tested/not tested/risks | ✓ | ✓ | ✓ | Generalized |
| Archive/historical material not current authority | ✓ | ✓ | ~ | Generalized |
| Synchronized paired/multilingual documents | ~ | ✓ | — | Conditional module |
| Content/variant family synchronization | ✓ | ✓ | — | Conditional module |
| Development-history records and canonical indexes | ✓ | ✓ | ✓ | Conditional to projects using history systems |
| Read current history-record instructions before writing | ~ | ✓ | ~ | Conditional module |
| Turn meaningful solved problems into preventive rules | ✓ | ✓ | — | Conditional learning-loop module |
| Version released artifacts; do not mutate silently | ~ | ✓ | ✓ | Conditional versioning module |
| Generated/distribution copies are not editing masters | ~ | ~ | ✓ | Generalized/conditional distribution rule |
| Integrity hash differences are evidence, not overwrite authority | ~ | ~ | ✓ | Conditional integrity module |
| Technical/platform-required names override cosmetic style | ~ | ~ | ✓ | Generalized |
| One exact human-facing naming convention | project-specific | project-specific | project-specific | **Not universal** |
| Exact folder tree | project-specific | project-specific | project-specific | **Not universal** |
| Exact language set | project-specific | project-specific | project-specific | **Not universal** |
| Exact build/record ID prefixes | project-specific | project-specific | project-specific | **Not universal** |
| Exact popup/modal/article/diagram system names | project-specific | project-specific | — | **Not universal** |
| Exact plugin manifest/package layout | — | — | project-specific | **Not universal** |

## Important synthesis decisions

### Inspection conflict

InfoBank strongly favors minimum sufficient inspection. LLH deliberately requires a broad rules pre-read before every task.

The reusable rule therefore does not choose one universally:

> Always read root governance and directly relevant specialist rules. Default to minimum sufficient inspection unless the target project explicitly mandates a broader governance pre-read.

### Naming conflict

The source projects use incompatible naming styles.

The reusable rule is:

> The target project owns its human-facing naming policy. Never import another project's naming style automatically. Always protect technical names required for execution.

### Language conflict

LLH has mandatory language-pair rules; the other projects do not share the same language contract.

The reusable rule is conditional:

> If the project declares two or more governance/content variants as synchronized equivalents, update the whole declared family in the same task.

### History/versioning conflict

The three projects use different history and version mechanisms.

The reusable rule is:

> Follow the target project's current authoritative history/version workflow. Read the current record-family instructions before writing and never invent identifiers, versions, or schemas from memory.

## Rules added as cross-project design recommendations

The following safeguards were added by the Skill because they improve governance portability, even though the source projects did not all express them identically:

- concurrency-safe final writes;
- idempotent recurring automation where practical;
- reproducibility for important generated outputs;
- explicit approval gates for external side effects;
- recovery/rollback preparation before destructive migrations;
- a permanent-rule quality test: scope, authority, exceptions, and verification method must be clear.

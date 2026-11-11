# Task Scope Contract Template

Use this as a compact task-scoped record only when authorized; it does not create a persistent state directory. Replace the labels with actual values and preserve previous evidence when a task is revised or reopened.

```yaml
task_key: existing-task-id-or-validated-context
event_type: NEW | ACTIVE | RESUME | REVISE | REOPEN | FIX | RECHECK
scope_version: observed-revision-or-content-hash
allowed_read_paths: []
allowed_edit_paths: []
excluded_paths: []
evidence: []
inspection_level: TARGETED | FOCUSED | DEPENDENCY | BROAD
quality:
  acceptance_ids: []
  required_tests: []
  pass_requires_evidence: true
read_tracking:
  path: relative-path
  revision_or_sha: observed-identity
  ranges: []
  reason: task-or-verification-relevance
  last_observed: timestamp-or-checkpoint
retry_tracking:
  operation: operation-identifier
  prior_evidence: observed-result
  new_hypothesis: reason-to-retry
  attempt: 0
  limit: bounded-limit
resource_policy_ref: resource-optimization
```

The labels are a schema example, not evidence. Replace them before treating the record as a real contract. File access and resolved-path validation are controlled by the host and project rules, not by this template.

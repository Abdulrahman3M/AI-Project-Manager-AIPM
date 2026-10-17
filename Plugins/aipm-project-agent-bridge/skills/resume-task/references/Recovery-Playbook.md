# Recovery Playbook

Resume Task applies to all agents and task domains. It does not circumvent usage limits or replace the active project's rules.

| Cause | What to inspect | Safe continuation |
|---|---|---|
| Quota / token / rate limit | Accessible original task, checkpoint and actual outputs | Continue when permitted, from verified state |
| Context loss / new model | Original instructions, approved decisions, files and logs | Reconstruct without inventing inaccessible history |
| Timeout / crash | Process status, files, logs and external state | Finish missing work without duplicating successful effects |
| Disconnected service | Remote job, transaction, publish or message ID | Check whether the operation already succeeded |
| New agent / manual pause | Portable checklist, specs and current artifacts | Verify recorded progress then resume dependencies |
| Validation failure | Failed test and related artifacts | Repair smallest cause and rerun affected checks |

A useful checkpoint records task source, all requirements, constraints, workspace references, last VERIFIED step with direct evidence, current step and acceptance criteria, possible side effects, next safe action, remaining dependencies, and final verification. Do not include secrets or sensitive data.

```sh
python scripts/validate_checkpoint.py examples/Task-Checkpoint.json
python -m unittest discover -s tests -v
```

The optional helper only validates structure; it never performs or restarts the user's task.

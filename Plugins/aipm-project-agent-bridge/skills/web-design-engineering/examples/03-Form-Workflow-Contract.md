# Example: Account Recovery Form Contract

## States

| State | User-facing behavior | Accessibility behavior |
| --- | --- | --- |
| Default | Email label, input, and “Send recovery link” action | Native label association; visible focus |
| Invalid email | Inline sentence explaining the valid format | Error text is associated with the input; focus remains predictable |
| Submitting | Action says “Sending…” and prevents duplicate submit | Busy state is exposed; no long blocking animation |
| Success | Confirms destination in masked form and explains the next step | Confirmation is announced once |
| Network error | Explains that no link was sent and provides retry | Error is not color-only; entered email remains |

The narrow layout preserves the full label and error text; it never uses a tooltip as the only explanation.

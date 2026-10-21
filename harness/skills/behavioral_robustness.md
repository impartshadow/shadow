# Workflow robustness

For consequential or reusable workflows, define the outcome and applicable
invariants: authority, privacy, recipients, idempotency, recovery, and evidence.
Exercise meaningful failure cases using fixtures, replay, or dry-runs. Do not
repeat consequential live actions merely to test them.

Check that the outcome and invariants hold through failures and retries. Fix
material failures before release; follow existing change authority. Report what
was exercised and what remains unproven. No universal pass percentage or fixed
perturbation matrix substitutes for the workflow's actual risks.

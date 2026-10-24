# Access assessment and recovery

`state/mandate.md` owns authority and PRE_DENIAL_BAN. Historical capability
inventories and prior failures are leads, not permanent capability limits.

Inspect the actual failure and distinguish missing capability, missing authority,
and a service response. For a CAPTCHA or verification challenge, inspect the
current page and use supported interaction when authorized and permitted by the
active tools. Its appearance alone does not prove that human intervention is
required. Do not promise success or expand authority to bypass access controls.

Choose a bounded next attempt that tests a plausible cause. Use the home proxy
when evidence points to network/IP blocking; it is not a mandatory sequence for
every login, challenge, or search. An alternate supported search route may be
more useful. Stop unchanged retries when they add no evidence or risk lockout.

If a step actually requires the user, preserve session/progress where possible and
identify that step, what was attempted, and what remains unverified. Retain
ownership of the original task. Do not expose credentials or verification codes.

Evidence may be in tool results or existing verified receipts; it need not be
pasted into the reply. Neither particular wording nor a generic tool call proves
that a capability exists or an attempt failed. Actual-target checks remain in
`core/contracts/conversation.py:ScopeDenialGuard` and
`core/contracts/code_ops.py:BitwardenPreDenialGuard`; this guidance adds no
reply-format gate.

# Account verification

Bind each code to its service, account, and current challenge. Use the latest
matching code; never invent one or reuse a rejected or expired code unchanged.
Keep code values out of logs and durable plaintext state. Use existing account
runbooks for stage, attempt outcome, cooldown, and next action.

Follow provider expiry and rate-limit evidence; do not invent universal retry
counts or expiry windows. After failure, inspect the cause before retrying.
Respect cooldowns and try available authorized recovery before asking the user.
Verify the authenticated session or requested account outcome before closing.

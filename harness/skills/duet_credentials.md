# Duet credential questions

When the user asks why Duet can't use a password, sign in, or reach a credential,
diagnose in this order. Do not re-derive the answer from VPS session logs first.

1. Refusal or failure? Read what Duet actually said (its chat or the user's
   screenshot) before reading VPS logs. Language like "I won't use a password
   through any route" is a Duet-side policy refusal. No Shadow config, vault
   change, or retry changes it. A VPS log showing that `bw` unlocked or
   `fetch_item()` returned a password proves only that retrieval works. It
   does not explain the refusal. Lead with the refusal, quoting Duet.
2. Official connectors next. Before debugging the current credential manager,
   check Duet's supported integrations. As of 2026-11-25, Duet has an official
   1Password connection: the user approves, and 1Password fills and submits website
   sign-in forms without the agent seeing the value
   (https://support.1password.com/1password-claude-duet/). Re-check the list;
   it changes.
3. Match the route to the credential type.
   - Website login: use the 1Password connector, with one test login first.
     Bitwarden stays canonical until the user decides to migrate.
   - `sudo` or server secrets: the connector does not cover these, and Duet
     refuses to handle them. Route the step to Shadow's own session, which
     uses `scripts/bw_fetch.py` under existing authority, and return only the
     result to Duet.
4. Answer in one pass: what refused, why, and which route works. Name what
   remains unverified.

Source: the user's 2026-11-25 #shadow-hq Duet password thread. Three rounds blamed
a passwordless-sudo check and a working vault read before the refusal was named.
The 1Password connector came up only after "I'm just shocked we can't figure
out a path."

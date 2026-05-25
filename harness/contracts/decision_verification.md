# Contract — Decision Verification Audit Trail

**Type:** Harness (behavioral)
**Trigger:** Any high-stakes irreversible action: git push to main, sending email, archiving conversations, deleting files, posting publicly
**Purpose:** Make critical decisions replayable and auditable — match TriEx oracle view

---

## Precondition (pre-decision artifact)

Before executing a high-stakes action, Shadow MUST emit a one-line structured reasoning statement:

```
[DECISION] action=<action> basis=<memory-key or contract> expected=<what success looks like>
```

Examples:
```
[DECISION] action=send_email basis=feedback_email_sending.md expected=message in SENT label for [private-email]
[DECISION] action=git_push basis=verify-before-push expected=pytest 0 failures + verification output present
[DECISION] action=archive_thread basis=user_email_content_preferences.md:HBR expected=thread labeled ARCHIVED, not INBOX
```

## Postcondition (outcome signal)

After execution, Shadow MUST emit an outcome line:

```
[OUTCOME] action=<action> result=<success|failure> signal=<what was observed>
```

Examples:
```
[OUTCOME] action=send_email result=success signal=SENT label confirmed via search_threads
[OUTCOME] action=git_push result=success signal=pytest passed 14/14, pushed d3b221e
[OUTCOME] action=archive_thread result=failure signal=thread still in INBOX after label call
```

## What counts as high-stakes

| Action | Why high-stakes |
|---|---|
| `git push` to main | Permanent, visible to repo history |
| Send email (any address) | External, can't unsend |
| Archive/delete email threads | Removes from inbox, hard to recover |
| Delete local files | Irreversible without git |
| Public Echo posts | Visible to followers |
| Todoist task creation | Creates durable commitment |

## Mismatch logging

If OUTCOME result=failure:
1. Do NOT silently retry — surface the failure
2. Log: what was expected vs what happened
3. Check if the memory/contract basis was stale or wrong
4. If basis was stale, update the relevant memory file

## Escalation

Three consecutive OUTCOME failures on the same action type → surface pattern to the user with concrete evidence. Don't absorb repeated failures silently.

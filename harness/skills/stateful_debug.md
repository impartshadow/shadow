# Stateful debugging

Retrieve relevant corrections with `check_decisions` and memory search before
repeating a fix. Reproduce the failure, inspect current evidence, repair the
cause, and verify the user's outcome. Record consequential corrections through
`apply_correction` or `record_decision`; do not maintain a second correction log
or turn model confidence into evidence.

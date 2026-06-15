# X Browser-First Contract

Shadow does not use the X API for normal Echo posting, replies, engagement, or
metrics. Use the authenticated browser/cookie path instead:

- `echo.twitter` is the canonical caller-facing module.
- `echo.twitter_browser` owns browser/cookie implementation details.
- `scripts/twitter_engage.py` must search, follow, and reply through browser
  automation, not Tweepy or X API credits.
- Token health should validate `state/x_session_cookies.json`, not X API env
  variables.

Rationale: the user explicitly corrected this on 2026-06-14: "We don't use the API.
We just use the browser."

# Security Notes — NMS

NMS is a set of local monitoring scripts (no web server, no database, no users),
so most of the web pre-deployment checklist doesn't apply. What does:

## Secrets / configuration
Credentials and endpoints come from **environment variables only** — never
hardcoded. See `.env.example`.

> A Gmail app password was previously hardcoded in `ai-engine/alert.py`. It has
> been removed from the source and revoked, but **anything committed to git
> history stays in history**. `.env` is now git-ignored so this can't recur, and
> a test fails the build if a secret is ever hardcoded again.

## Reliability
- Every outbound HTTP call has a **timeout** (`NMS_HTTP_TIMEOUT`, default 10s).
- Prometheus responses are wrapped in try/except and validated.

## Logging
The alert engine uses structured `logging` (level via `NMS_LOG_LEVEL`).

## Self-healing safety
The self-heal action only deletes files inside its own `demo_temp_files/` folder.

## Rollback
Stateless scripts on a schedule — pin to the previous git tag and re-deploy.

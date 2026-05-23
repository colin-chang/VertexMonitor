# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in Vertex Monitor, please report it responsibly:

- **Email**: Open a GitHub Issue with the `security` label, or contact the maintainer directly
- **Response time**: We aim to acknowledge reports within 48 hours and provide a fix within 7 days

## What We Take Seriously

- Credential leakage (GCP service account keys exposed in logs, responses, or Git history)
- Authentication bypass on the proxy endpoint
- Arbitrary file read/write via the API

## What Is Out of Scope

- Attacks requiring physical access to the host machine
- Denial of service via legitimate API usage
- Issues in third-party dependencies (report upstream)

## Credential Handling

Vertex Monitor processes GCP service account JSON keys. By design:

- Keys are stored **only** inside the Docker container at `/app/data/vertex-key.json`
- Keys are **never** logged, returned in API responses, or committed to Git
- The `/api/settings` endpoint returns a boolean `has_key` status — never the key content itself
- `vertex-key.json` and `config.json` are excluded via `.gitignore`

If you find that key material is being exposed in any way, please report it immediately.

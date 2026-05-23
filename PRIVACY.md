# Privacy Policy

Vertex Monitor is a **self-hosted, local-first** tool. Your data never leaves your machine.

## Data Collection

**Vertex Monitor does not collect, transmit, or store any personal data on external servers.**

All data — including GCP credentials, usage statistics, and billing records — resides entirely within your local Docker container.

## What Is Stored Locally

| Data | Location | Purpose |
|------|----------|---------|
| GCP Service Account Key | `/app/data/vertex-key.json` | Authenticate with Vertex AI API |
| Billing state | `/app/data/store.json` | Track spending and budget limits |
| Call history | `/app/data/store_history.jsonl` | Record API usage for statistics |
| Language preference | Browser `localStorage` | Remember i18n selection |

## What Is Sent Externally

The only outbound network traffic is **your own API calls** to Google Vertex AI, proxied through Vertex Monitor. No telemetry, analytics, or usage data is sent to any third party.

## Third-Party Services

- **Google Vertex AI**: API calls are forwarded to Google's endpoints. Subject to [Google's Privacy Policy](https://policies.google.com/privacy).
- **Chart.js CDN**: The dashboard loads Chart.js from `cdn.jsdelivr.net`. No data is sent to this CDN.

## Deleting Your Data

Simply stop the Docker container and delete the `data/` directory:

```bash
docker compose down
rm -rf data/
```

All local data will be permanently removed.

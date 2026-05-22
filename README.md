# Job Scraper Service

A local-first job data scraping and reporting website built as a DevOps portfolio project. Users can create scheduled job alerts, choose job sources, countries, work mode, posting age, scan frequency, and email report frequency. The app scans in the background, stores results in SQLite, and generates a mobile-friendly HTML report with direct job links.

> Portfolio positioning: this project demonstrates Python FastAPI, Docker, GitHub Actions, Jenkins, monitoring with Prometheus/Grafana, Ansible, Kubernetes manifests, and Terraform starter folders for AWS/GCP.

---

## Features

- Landing page form for job alert creation
- Main and alternate job search terms
- Posted-within filter: 2 weeks, 1 month, or 2 months
- User email field for report delivery
- Report frequency: once or twice per day
- Scraper scan frequency capped at 3 times per day
- Source selection: Remotive, Arbeitnow, RemoteOK, Mock demo provider
- Country filtering and work mode filtering
- SQLite persistence for local lightweight usage
- Mobile-friendly HTML report page
- Email preview fallback when SMTP is not configured
- Docker Compose local setup
- Prometheus metrics endpoint at `/metrics`
- GitHub Actions CI workflow
- Jenkins pipeline file
- Ansible local deployment playbook
- Kubernetes starter manifest
- Terraform starter folders for AWS and GCP

---

## Why this design?

This MVP avoids heavy browser automation such as Selenium or Playwright. That keeps the app lighter for local machines and reduces the chance of being blocked by job portals. The code uses a provider pattern so future sources can be added one file at a time.

The scraper is intentionally scheduled only a few times per day. This is better for a homelab project because it uses fewer resources, avoids noisy traffic, and behaves more responsibly toward external sites.

---

## Architecture

```text
User Browser
    |
    v
FastAPI Landing Page ---- SQLite database
    |                          |
    |                          v
    |                    Stored subscriptions
    |
    v
APScheduler background scans
    |
    v
Job Provider Plugins -> Remotive / Arbeitnow / RemoteOK / Mock
    |
    v
Deduplicated job_results table
    |
    v
HTML Report Generator -> /reports/{report_id}
    |
    v
Email Sender or local email preview
```

---

## Tech Stack

| Area | Tool |
|---|---|
| Backend | FastAPI |
| Templates | Jinja2 |
| Database | SQLite |
| Scheduler | APScheduler |
| HTTP Client | HTTPX |
| Container | Docker |
| Local orchestration | Docker Compose |
| CI | GitHub Actions |
| Alternative CI/CD | Jenkins |
| Config management | Ansible |
| Infrastructure as Code | Terraform starter folders |
| Kubernetes | Starter deployment and service YAML |
| Monitoring | Prometheus + Grafana |

---

## Quick Start: Local Python

```bash
# 1. Clone your repository
 git clone https://github.com/YOUR_USERNAME/job-scraper-service.git
 cd job-scraper-service

# 2. Create virtual environment
 python3 -m venv .venv
 source .venv/bin/activate

# 3. Install dependencies
 pip install -r requirements.txt

# 4. Create environment file
 cp .env.example .env

# 5. Run the app
 uvicorn app.main:app --reload
```

Open:

```text
http://localhost:8000
```

---

## Quick Start: Docker Compose

```bash
cp .env.example .env
docker compose up -d --build
```

Open:

```text
http://localhost:8000
```

Stop:

```bash
docker compose down
```

---

## Run with Monitoring

```bash
docker compose --profile monitoring up -d --build
```

Open:

```text
App:        http://localhost:8000
Prometheus: http://localhost:9090
Grafana:    http://localhost:3000
```

Default Grafana login is usually `admin/admin` unless you configure another password.

---

## Email Setup

The app works without SMTP. If SMTP is not configured, it writes a local preview file:

```text
reports/email_preview.html
```

To send real emails, edit `.env`:

```env
PUBLIC_BASE_URL=http://localhost:8000
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=your_username
SMTP_PASSWORD=your_password
SMTP_FROM=your_email@example.com
```

For Gmail, use an App Password rather than your normal account password.

---

## Important Localhost Note

If the report email contains `http://localhost:8000/reports/...`, that link only works on the same machine running the app. For access from your phone or another device, set `PUBLIC_BASE_URL` to a reachable URL such as:

```env
PUBLIC_BASE_URL=http://192.168.1.50:8000
```

For public access later, use a domain name, reverse proxy, Cloudflare Tunnel, AWS, or GCP.

---

## Manual Scan

After creating an alert, you can manually trigger a scan:

```bash
curl -X POST http://localhost:8000/api/run/1
```

Replace `1` with the subscription ID shown on the home page.

---

## Adding a New Job Provider

Create a new file in:

```text
app/providers/my_provider.py
```

Implement the provider class:

```python
from app.providers.base import JobProvider
from app.models import JobResult

class MyProvider(JobProvider):
    name = "my_provider"

    async def search(self, query: str, countries: list[str], work_mode: str, max_age_days: int):
        return [
            JobResult(
                title="Example DevOps Engineer",
                company="Example Company",
                source="My Provider",
                location="Singapore",
                work_mode="Hybrid",
                posted_at="2026-05-22",
                url="https://example.com/job"
            )
        ]
```

Then register it in:

```text
app/providers/registry.py
```

---

## Responsible Scraping Rules

- Prefer official APIs, RSS feeds, or public JSON endpoints.
- Respect each website's Terms of Service and robots.txt.
- Keep frequency low. This app caps scans at 3 times per day.
- Use a clear User-Agent where possible.
- Deduplicate results so the same job is not repeatedly emailed.
- Do not scrape behind logins unless the website explicitly allows it.

---

## DevOps Showcase Roadmap

### Weekend MVP

- Build FastAPI app
- Run locally with Docker Compose
- Add GitHub Actions CI
- Generate first report
- Commit to public GitHub repo

### After MVP

- Add authentication for users
- Add unsubscribe/pause alerts
- Add Cloudflare Tunnel or reverse proxy
- Add Grafana dashboard JSON
- Deploy to AWS Lightsail, ECS, or GCP Cloud Run
- Convert SQLite to Postgres for multi-user deployment
- Add queue-based worker using Redis/RQ or Celery if scale increases

---

## Commands Checklist

```bash
# Start app locally
uvicorn app.main:app --reload

# Start with Docker
docker compose up -d --build

# View logs
docker compose logs -f job-scraper

# Run tests
pytest

# Lint
ruff check app tests

# Start with monitoring
docker compose --profile monitoring up -d --build

# Stop everything
docker compose down
```

---

## License

MIT License. Use this project for learning, portfolio demonstrations, and responsible job-alert automation.

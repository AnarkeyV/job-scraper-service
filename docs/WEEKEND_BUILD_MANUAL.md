# Job Scraper Service - Weekend Build Manual

## Goal

Build a local-first job scraping and reporting website that can be demonstrated as a DevOps portfolio project by Monday, 25 May 2026.

The app lets a user enter:

- Main job search term, such as Entry Level DevOps Engineer
- Alternate job search term, such as Intern DevOps Engineer
- Posted-within timeframe, such as past 2 weeks or past 1 month
- Email address
- Report frequency
- Scan frequency, capped at 3 times per day
- Job sources
- Countries
- Remote, hybrid, or both

The app then scans in the background, stores matching jobs, generates a mobile-friendly report page, and sends or previews an email containing the report link.

---

## Recommended Weekend Scope

Do not try to build every cloud and DevOps feature immediately. Build in this order:

1. Local FastAPI app
2. SQLite storage
3. Background scheduler
4. Provider-based job fetching
5. HTML report page
6. Docker Compose
7. GitHub Actions
8. Monitoring with Prometheus and Grafana
9. Jenkinsfile, Ansible, Kubernetes, Terraform starter files

This gives you a complete and explainable project by Monday without making the app too heavy.

---

## Architecture in Plain English

The user opens the website and creates a job alert. The app stores that alert in SQLite. APScheduler runs background scans up to three times daily. Each scan calls selected job source providers, filters results, removes duplicates, and stores matching jobs. The app then creates an HTML report and sends the user a link by email. If email is not configured, the app creates an email preview file locally.

---

## Folder Structure

```text
job-scraper-service/
  app/
    main.py
    services.py
    scheduler.py
    db.py
    config.py
    providers/
    templates/
    static/
  data/
  reports/
  monitoring/
  terraform/
  ansible/
  k8s/
  tests/
  .github/workflows/
  Dockerfile
  docker-compose.yml
  Jenkinsfile
  README.md
```

---

## Step 1 - Open the Project

```bash
cd job-scraper-service
code .
```

Check that you can see `app/main.py`, `docker-compose.yml`, and `README.md`.

---

## Step 2 - Create the Environment File

```bash
cp .env.example .env
```

For local testing, leave SMTP empty. The app will still generate reports and an email preview.

---

## Step 3 - Run Locally Without Docker

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open:

```text
http://localhost:8000
```

Create your first job alert using:

```text
Main job: Entry Level DevOps Engineer
Alternate job: Intern DevOps Engineer
Posted within: Past 1 month
Country: Singapore
Work mode: Remote or Hybrid
Sources: Remotive, Arbeitnow, Mock demo source
```

---

## Step 4 - Check the First Report

After submitting the form, the first scan runs in the background.

If SMTP is not configured, check:

```text
reports/email_preview.html
```

The generated report can also be opened from:

```text
http://localhost:8000/reports/{report_id}
```

The report contains a table with:

- Job posting
- Company
- Source
- Location
- Work mode
- Posted date
- Direct job link

---

## Step 5 - Run with Docker Compose

Stop the local Python server first. Then run:

```bash
docker compose up -d --build
```

Check health:

```bash
curl http://localhost:8000/health
```

View logs:

```bash
docker compose logs -f job-scraper
```

Stop:

```bash
docker compose down
```

---

## Step 6 - Run with Monitoring

```bash
docker compose --profile monitoring up -d --build
```

Open:

```text
Application: http://localhost:8000
Prometheus:  http://localhost:9090
Grafana:     http://localhost:3000
```

The app exposes metrics at:

```text
http://localhost:8000/metrics
```

Prometheus scrapes those metrics. Grafana can use Prometheus as its data source.

---

## Step 7 - Run Tests and Linting

```bash
pytest
ruff check app tests
```

If the app passes these, your GitHub Actions workflow should also pass after pushing to GitHub.

---

## Step 8 - Push to GitHub

```bash
git init
git add .
git commit -m "Initial job scraper service MVP"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/job-scraper-service.git
git push -u origin main
```

GitHub Actions will run the CI workflow in `.github/workflows/ci.yml`.

---

## Step 9 - Jenkins Demonstration

The `Jenkinsfile` demonstrates an alternative CI/CD pipeline:

1. Checkout source code
2. Build Docker image
3. Run tests inside Docker
4. Start the app with Docker Compose
5. Smoke test `/health`
6. Tear down the stack

This is useful for explaining Jenkins even if GitHub Actions is your primary CI tool.

---

## Step 10 - Ansible Demonstration

Run:

```bash
ansible-playbook ansible/deploy-local.yml
```

This shows how Ansible can be used to trigger a repeatable local deployment command. In a real homelab, this can be expanded to install Docker, create directories, copy environment files, and restart services.

---

## Step 11 - Kubernetes Demonstration

The Kubernetes manifest is a starter file, not the recommended weekend runtime. Use it to explain future deployment.

```bash
kubectl apply -f k8s/deployment.yaml
```

For a MacBook or homelab, you can later test this with Docker Desktop Kubernetes, Minikube, or k3s.

---

## Step 12 - Terraform Demonstration

Terraform folders are intentionally minimal because cloud deployment should come after the local MVP works.

```text
terraform/aws/main.tf
terraform/gcp/main.tf
```

For your presentation, explain that Terraform will later provision AWS or GCP resources such as Cloud Run, ECS, EC2, Lightsail, or networking components.

---

## Recommended Cloud Choice

For this project, GCP Cloud Run is the simplest later deployment target because it can run a container with low operational overhead. AWS is also good, but AWS ECS or EC2/Lightsail may require more setup. For your weekend MVP, keep the project local and Docker-based first.

---

## Responsible Scraping Notes

Use official APIs, feeds, or public JSON endpoints first. Respect website terms, robots.txt, and rate limits. Avoid scraping behind logins. Keep scan frequency low. This project caps scanning at three times daily.

---

## Monday Demo Script

1. Explain the problem: job seekers repeatedly check different sites manually.
2. Show the landing page.
3. Create an alert for Entry Level DevOps Engineer.
4. Explain the frequency cap of three scans per day.
5. Explain source selection and country filtering.
6. Trigger a manual scan using the API endpoint.
7. Open the generated report.
8. Show the mobile-friendly table.
9. Show Docker Compose.
10. Show GitHub Actions workflow.
11. Show Prometheus metrics.
12. Explain future cloud deployment using Terraform.

---

## What to Improve After Monday

- Add login and user accounts
- Add unsubscribe or pause alert button
- Add Postgres for production
- Add Redis queue for worker separation
- Add stronger duplicate detection
- Add more source providers
- Add CSV export
- Add Cloudflare Tunnel or public domain
- Add actual Grafana dashboard JSON
- Add cloud deployment pipeline

---

## Troubleshooting

### The email does not send

Check `.env`. If SMTP is empty, this is expected. Open `reports/email_preview.html`.

### The report link does not open on mobile

`localhost` only works on the machine running the app. Change `PUBLIC_BASE_URL` to your machine's LAN IP address or a public URL.

### No jobs are found

Enable the Mock demo provider to prove the pipeline works. Then adjust search terms and countries.

### Docker port conflict

Another app may be using port 8000. Stop that app or change the port mapping in `docker-compose.yml`.

### Some job source fails

External sources can change their response format or temporarily block traffic. The provider pattern allows you to disable or replace one source without breaking the whole app.

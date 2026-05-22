# Job Scraper Service

A lightweight, local-first job alert web application that allows users to create job search subscriptions, scan selected job sources, generate mobile-friendly HTML reports, and send the results by email.

This project was built as a DevOps-focused portfolio project. The goal is not only to create a working job scraper, but also to demonstrate practical skills in application development, Docker, CI/CD, automation, monitoring, infrastructure planning, and future homelab deployment.

---

## Project Overview

Job Scraper Service helps users track job postings based on their preferred job title, alternative job title, country, work arrangement, job source, and scan/report frequency.

A user can submit a job alert through the web form. The application then saves the subscription, scans the selected job sources, generates a clean HTML job report, and emails the report link to the user.

The application is designed to be lightweight enough to run on a local machine, small homelab server, or cloud VM.

---

## Key Features

- Web landing page for creating job search alerts
- User-defined primary and alternative job titles
- Country and work arrangement filtering
- Remote, hybrid, or flexible work preference options
- Configurable job source selection
- Responsible scan frequency control
- Maximum recommended scan frequency: no more than 3 times per day
- SQLite database for local persistence
- HTML job report generation
- Mobile-friendly report layout
- Email delivery using SMTP
- Docker Compose support
- GitHub Actions CI workflow
- Jenkins pipeline starter file
- Ansible local deployment starter
- Kubernetes deployment starter
- Terraform starter folders for AWS and GCP
- Prometheus and Grafana monitoring starter setup

---

## Current MVP Status

The current working MVP supports:

- Creating a job alert from the website
- Saving the subscription into SQLite
- Running a job scan
- Saving job results
- Generating an HTML report
- Sending the report by email
- Running locally with Python
- Running with Docker Compose
- Passing local `pytest` tests
- Passing GitHub Actions CI

---

## Tech Stack

### Application

- Python
- FastAPI
- Jinja2
- SQLite
- APScheduler
- SMTP email sending
- HTML/CSS

### DevOps and Infrastructure

- Git
- GitHub
- GitHub Actions
- Docker
- Docker Compose
- Jenkins
- Ansible
- Kubernetes
- Terraform
- Prometheus
- Grafana

---

## Why This Project Was Built

This project was created to demonstrate practical Cloud Support and DevOps engineering skills through a realistic use case.

The project showcases:

- Building and running a web application
- Managing application configuration through environment variables
- Running the app locally and inside Docker
- Using Git and GitHub for version control
- Running automated tests through GitHub Actions
- Preparing deployment paths for Docker, Kubernetes, Ansible, and Terraform
- Designing a project that can later be hosted on a personal homelab or cloud platform

---

## Application Flow

```text
User opens website
        ↓
User submits job search alert
        ↓
Application saves subscription into SQLite
        ↓
Background scan runs
        ↓
Job results are collected
        ↓
HTML report is generated
        ↓
Email is sent to the user
        ↓
User opens the report link from email
```

---

## Example Use Case

A user may submit the following search:

```text
Job looking for: Entry Level DevOps Engineer
Alternate job: Intern DevOps Engineer
Country: Singapore
Work arrangement: Remote or Hybrid
Job posted duration: Within the past 1 month
Report frequency: Once a day
Scan frequency: Once a day
Email: user@example.com
```

The system will then scan the selected sources, generate a job report, and email the result to the user.

---

## Project Structure

```text
job-scraper-service/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── db.py
│   ├── models.py
│   ├── scheduler.py
│   ├── services.py
│   ├── providers/
│   │   ├── base.py
│   │   ├── mock.py
│   │   ├── remotive.py
│   │   ├── arbeitnow.py
│   │   ├── remoteok.py
│   │   └── registry.py
│   ├── static/
│   │   └── styles.css
│   └── templates/
│       ├── index.html
│       └── report.html
├── tests/
│   ├── conftest.py
│   └── test_health.py
├── ansible/
├── docs/
├── k8s/
├── monitoring/
├── terraform/
├── .github/
│   └── workflows/
├── Dockerfile
├── docker-compose.yml
├── Jenkinsfile
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## Local Setup

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/job-scraper-service.git
cd job-scraper-service
```

Replace `YOUR_USERNAME` with your actual GitHub username.

---

### 2. Create a Virtual Environment

```bash
python3 -m venv .venv
```

Activate the virtual environment:

```bash
source .venv/bin/activate
```

---

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

### 4. Create the Environment File

Copy the example environment file:

```bash
cp .env.example .env
```

Open `.env` and update the required values.

Example:

```env
APP_BASE_URL=http://127.0.0.1:8000

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_gmail_app_password
SMTP_FROM=your_email@gmail.com
```

Important: do not use your normal Gmail password. Use a Gmail App Password.

---

### 5. Run the Application Locally

```bash
uvicorn app.main:app
```

Open the application in your browser:

```text
http://127.0.0.1:8000
```

---

## Running with Docker Compose

Make sure Docker Desktop is running.

Build and start the application:

```bash
docker compose up --build
```

Open:

```text
http://127.0.0.1:8000
```

Stop the containers:

```bash
docker compose down
```

---

## Running Tests

Run:

```bash
pytest
```

Expected result:

```text
1 passed
```

Or, if needed:

```bash
python -m pytest
```

---

## Email Setup Notes

This project uses SMTP for sending job reports by email.

For Gmail:

1. Enable 2-Step Verification on your Google Account.
2. Create a Gmail App Password.
3. Use the generated app password in `.env`.
4. Do not commit `.env` to GitHub.

The `.gitignore` file should exclude:

```gitignore
.env
.venv/
data/
reports/
__pycache__/
.pytest_cache/
```

---

## GitHub Actions

This repository includes a GitHub Actions workflow to run basic CI checks.

The workflow is intended to:

- Install Python dependencies
- Run automated tests
- Confirm the application can be imported successfully

This helps ensure the application remains stable when changes are pushed to GitHub.

---

## Docker

Docker is included so that the project can run consistently across different machines.

This is useful for:

- Local development
- Homelab deployment
- Cloud VM deployment
- CI/CD pipelines
- Future Kubernetes deployment

---

## Jenkins

A `Jenkinsfile` is included as a starter pipeline.

This can be used later to demonstrate:

- Pipeline as Code
- Checkout from GitHub
- Dependency installation
- Test execution
- Docker image build
- Future deployment stages

---

## Ansible

The `ansible/` folder is included as a starter for local or server deployment automation.

Possible future uses:

- Install required packages
- Copy application files
- Start Docker Compose services
- Configure a homelab VM
- Automate repeatable deployment steps

---

## Kubernetes

The `k8s/` folder is included as a starter for container orchestration.

Possible future uses:

- Deploy the FastAPI app to a Kubernetes cluster
- Expose the app with a Service
- Add ConfigMaps and Secrets
- Add health checks
- Prepare for homelab Kubernetes or cloud Kubernetes deployment

---

## Terraform

The `terraform/` folder includes starter folders for AWS and GCP.

Possible future uses:

- Provision a small VM
- Set up networking
- Create firewall rules
- Prepare infrastructure for the app
- Demonstrate Infrastructure as Code

---

## Monitoring

The `monitoring/` folder includes a starter setup for Prometheus and Grafana.

Possible future improvements:

- Add application metrics endpoint
- Monitor uptime
- Monitor scan frequency
- Monitor email success/failure count
- Create Grafana dashboards
- Add alerting rules

---

## Responsible Scraping Approach

This project is designed to avoid aggressive scraping.

The intended rules are:

- Do not scan more than 3 times per day.
- Prefer public APIs or lightweight sources when available.
- Avoid heavy browser automation unless absolutely necessary.
- Respect robots.txt and website terms where applicable.
- Avoid scraping sites that explicitly disallow automated access.
- Add rate limiting when adding more providers.
- Cache and deduplicate results where possible.

This keeps the project lightweight and reduces the risk of being blocked by job portals.

---

## Current Limitations

The current version is an MVP and may not include all production features.

Known limitations:

- SQLite is used for local storage.
- Email delivery depends on SMTP configuration.
- Some job sources may require provider-specific logic.
- Full user authentication is not included.
- Report hosting is local unless deployed to a public server.
- The app is not yet production-hardened.
- Kubernetes, Terraform, Ansible, Jenkins, and monitoring are included as starter DevOps components but can be expanded further.

---

## Future Improvements

Planned improvements include:

- Add user authentication
- Add subscription management page
- Add unsubscribe link
- Add more job providers
- Add deduplication improvements
- Add PostgreSQL support
- Add proper background worker with Celery or RQ
- Add API documentation page
- Add Prometheus metrics endpoint
- Add Grafana dashboard
- Add production Docker image publishing
- Add Kubernetes secrets and config maps
- Add Terraform deployment for AWS or GCP
- Add Ansible playbook for homelab deployment
- Add CI/CD deployment workflow
- Add mobile UI improvements
- Add dark mode
- Add CSV export
- Add PDF report export

---

## Security Notes

Do not commit secrets to GitHub.

The following files and folders should not be committed:

```text
.env
.venv/
data/
reports/
```

Use `.env.example` to show required configuration values without exposing real credentials.

---

## Suggested Demo Script

A short demo flow:

```text
1. Open the website.
2. Explain the purpose of the job scraper.
3. Create a new job alert.
4. Show that the alert is saved.
5. Show the generated HTML report.
6. Show the email received.
7. Open the report from the email.
8. Show the GitHub repository.
9. Show the passing GitHub Actions workflow.
10. Explain Docker Compose support.
11. Explain future DevOps expansion with Jenkins, Ansible, Kubernetes, Terraform, Prometheus, and Grafana.
```

---

## Skills Demonstrated

This project demonstrates:

- Python web development
- FastAPI routing
- HTML template rendering
- SQLite database usage
- Background job execution
- SMTP email configuration
- Docker containerization
- Docker Compose orchestration
- Git and GitHub workflow
- GitHub Actions CI
- Basic automated testing
- DevOps project structuring
- Infrastructure as Code planning
- Monitoring planning
- Homelab deployment planning

---

## License

This project is intended for learning, portfolio demonstration, and local personal use.

Before deploying publicly or scraping third-party sites, review the terms of service of each data source.

---

## Author

Created as a Cloud Support and DevOps portfolio project.

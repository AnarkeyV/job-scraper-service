import hashlib
import json
import smtplib
import uuid
from datetime import datetime
from email.mime.text import MIMEText
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.config import settings
from app.db import get_conn
from app.models import JobResult
from app.providers.registry import PROVIDERS

TEMPLATE_DIR = Path(__file__).parent / "templates"
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), autoescape=select_autoescape())

def fingerprint(job: JobResult) -> str:
    raw = f"{job.source}|{job.company}|{job.title}|{job.url}".lower().encode()
    return hashlib.sha256(raw).hexdigest()

def create_subscription(form: dict) -> int:
    scan_frequency = min(int(form.get("scan_frequency", 1)), settings.max_scans_per_day)
    with get_conn() as conn:
        cur = conn.execute(
            """
            INSERT INTO subscriptions
            (main_query, alternate_query, email, posted_within_days, report_frequency, scan_frequency, providers, countries, work_mode)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                form["main_query"], form.get("alternate_query", ""), form["email"],
                int(form["posted_within_days"]), form["report_frequency"], scan_frequency,
                json.dumps(form.get("providers", [])), json.dumps(form.get("countries", [])), form["work_mode"],
            ),
        )
        conn.commit()
        return int(cur.lastrowid)

def list_subscriptions():
    with get_conn() as conn:
        return conn.execute("SELECT * FROM subscriptions ORDER BY created_at DESC").fetchall()

async def run_scan(subscription_id: int) -> tuple[int, str]:
    with get_conn() as conn:
        sub = conn.execute("SELECT * FROM subscriptions WHERE id = ?", (subscription_id,)).fetchone()
        if not sub:
            raise ValueError("Subscription not found")
        run_cur = conn.execute(
            "INSERT INTO scan_runs (subscription_id, status) VALUES (?, ?)",
            (subscription_id, "running"),
        )
        conn.commit()
        run_id = int(run_cur.lastrowid)

    queries = [sub["main_query"]]
    if sub["alternate_query"]:
        queries.append(sub["alternate_query"])
    providers = json.loads(sub["providers"] or "[]") or ["mock"]
    countries = json.loads(sub["countries"] or "[]")
    work_mode = sub["work_mode"]
    max_age_days = int(sub["posted_within_days"])

    inserted = 0
    error = None
    all_jobs: list[JobResult] = []
    try:
        for query in queries:
            for provider_key in providers:
                provider = PROVIDERS.get(provider_key)
                if not provider:
                    continue
                jobs = await provider.search(query, countries, work_mode, max_age_days)
                all_jobs.extend(jobs)
        with get_conn() as conn:
            for job in all_jobs:
                if not job.url:
                    continue
                try:
                    conn.execute(
                        """
                        INSERT INTO job_results
                        (subscription_id, title, company, source, location, work_mode, posted_at, url, fingerprint)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            subscription_id, job.title, job.company, job.source, job.location,
                            job.work_mode, job.posted_at, job.url, fingerprint(job)
                        ),
                    )
                    inserted += 1
                except Exception:
                    pass
            conn.execute(
                "UPDATE scan_runs SET status = ?, jobs_found = ?, finished_at = CURRENT_TIMESTAMP WHERE id = ?",
                ("success", inserted, run_id),
            )
            conn.commit()
    except Exception as exc:
        error = str(exc)
        with get_conn() as conn:
            conn.execute(
                "UPDATE scan_runs SET status = ?, error = ?, finished_at = CURRENT_TIMESTAMP WHERE id = ?",
                ("failed", error, run_id),
            )
            conn.commit()

    report_id = generate_report(subscription_id)
    send_report_email(subscription_id, report_id, inserted, error)
    return inserted, report_id

def generate_report(subscription_id: int) -> str:
    report_id = uuid.uuid4().hex[:12]
    with get_conn() as conn:
        sub = conn.execute("SELECT * FROM subscriptions WHERE id = ?", (subscription_id,)).fetchone()
        jobs = conn.execute(
            "SELECT * FROM job_results WHERE subscription_id = ? ORDER BY COALESCE(posted_at, discovered_at) DESC LIMIT 200",
            (subscription_id,),
        ).fetchall()
    template = env.get_template("report.html")
    html = template.render(subscription=sub, jobs=jobs, generated_at=datetime.now().strftime("%Y-%m-%d %H:%M"))
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    html_path = reports_dir / f"{report_id}.html"
    html_path.write_text(html, encoding="utf-8")
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO reports (id, subscription_id, html_path) VALUES (?, ?, ?)",
            (report_id, subscription_id, str(html_path)),
        )
        conn.commit()
    return report_id

def send_report_email(subscription_id: int, report_id: str, inserted: int, error: str | None):
    with get_conn() as conn:
        sub = conn.execute("SELECT * FROM subscriptions WHERE id = ?", (subscription_id,)).fetchone()
    report_url = f"{settings.public_base_url}/reports/{report_id}"
    subject = f"Job Scraper Report: {inserted} new job(s) found"
    body = f"""
    <h2>Your job scraper report is ready</h2>
    <p><strong>Search:</strong> {sub['main_query']}</p>
    <p><strong>New jobs found:</strong> {inserted}</p>
    <p><a href=\"{report_url}\">Open mobile-friendly job report</a></p>
    {f'<p><strong>Error:</strong> {error}</p>' if error else ''}
    <p>This is an automated report from your local Job Scraper Service.</p>
    """
    if not settings.smtp_host or not settings.smtp_from:
        Path("reports/email_preview.html").write_text(body, encoding="utf-8")
        print(f"Email not configured. Report URL: {report_url}")
        return
    msg = MIMEText(body, "html")
    msg["Subject"] = subject
    msg["From"] = settings.smtp_from
    msg["To"] = sub["email"]
    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
        server.starttls()
        if settings.smtp_username:
            server.login(settings.smtp_username, settings.smtp_password)
        server.send_message(msg)

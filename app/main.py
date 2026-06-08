from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Form, Request, BackgroundTasks, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

from app.db import init_db, get_conn
from app.scheduler import start_scheduler
from app.services import create_subscription, list_subscriptions, run_scan

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    start_scheduler()
    yield

app = FastAPI(title="Job Scraper Service", lifespan=lifespan)
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

SUBSCRIPTIONS_CREATED = Counter("job_scraper_subscriptions_created_total", "Total subscriptions created")
MANUAL_SCANS = Counter("job_scraper_manual_scans_total", "Manual scans triggered")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "subscriptions": list_subscriptions()})

@app.post("/subscribe")
async def subscribe(
    background_tasks: BackgroundTasks,
    main_query: str = Form(...),
    alternate_query: str = Form(""),
    email: str = Form(...),
    posted_within_days: int = Form(...),
    report_frequency: str = Form(...),
    scan_frequency: int = Form(...),
    providers: list[str] = Form([]),
    countries: str = Form(""),
    work_mode: str = Form(...),
):
    country_list = [c.strip() for c in countries.split(",") if c.strip()]
    sub_id = create_subscription({
        "main_query": main_query,
        "alternate_query": alternate_query,
        "email": email,
        "posted_within_days": posted_within_days,
        "report_frequency": report_frequency,
        "scan_frequency": scan_frequency,
        "providers": providers,
        "countries": country_list,
        "work_mode": work_mode,
    })
    SUBSCRIPTIONS_CREATED.inc()
    background_tasks.add_task(run_scan, sub_id)
    return RedirectResponse(url=f"/?created={sub_id}", status_code=303)

@app.post("/api/run/{subscription_id}")
async def manual_run(subscription_id: int, background_tasks: BackgroundTasks):
    MANUAL_SCANS.inc()
    background_tasks.add_task(run_scan, subscription_id)
    return {"message": "Scan started", "subscription_id": subscription_id}

@app.get("/provider-status", response_class=HTMLResponse)
async def provider_status(
    request: Request,
    provider: str = "",
    status: str = "",
):
    query = """
        SELECT
            ps.provider,
            ps.status,
            ps.jobs_found,
            ps.message,
            ps.finished_at,
            sr.id AS scan_run_id,
            sr.subscription_id,
            s.main_query,
            s.alternate_query
        FROM provider_status ps
        JOIN scan_runs sr ON ps.scan_run_id = sr.id
        JOIN subscriptions s ON sr.subscription_id = s.id
        WHERE 1 = 1
    """

    params = []

    if provider:
        query += " AND ps.provider = ?"
        params.append(provider)

    if status:
        query += " AND ps.status = ?"
        params.append(status)

    query += """
        ORDER BY ps.finished_at DESC, ps.id DESC
        LIMIT 100
    """

    with get_conn() as conn:
        statuses = conn.execute(query, params).fetchall()

        providers = conn.execute(
            """
            SELECT DISTINCT provider
            FROM provider_status
            ORDER BY provider
            """
        ).fetchall()

    return templates.TemplateResponse(
        "provider_status.html",
        {
            "request": request,
            "statuses": statuses,
            "providers": providers,
            "selected_provider": provider,
            "selected_status": status,
        },
    )

@app.get("/reports/{report_id}", response_class=HTMLResponse)
async def view_report(report_id: str):
    with get_conn() as conn:
        report = conn.execute("SELECT * FROM reports WHERE id = ?", (report_id,)).fetchone()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    path = Path(report["html_path"])
    if not path.exists():
        raise HTTPException(status_code=404, detail="Report file missing")
    return HTMLResponse(path.read_text(encoding="utf-8"))

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

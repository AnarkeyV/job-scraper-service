from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.db import get_conn
from app.services import run_scan

scheduler = AsyncIOScheduler()

async def scan_all_active():
    with get_conn() as conn:
        subs = conn.execute("SELECT id FROM subscriptions WHERE is_active = 1").fetchall()
    for sub in subs:
        await run_scan(int(sub["id"]))

def start_scheduler():
    if scheduler.running:
        return
    # Runs three times daily at 8am, 2pm, 8pm. Each subscription still stores its preferred scan count.
    scheduler.add_job(scan_all_active, "cron", hour="8,14,20", minute=0, id="scan_all_active", replace_existing=True)
    scheduler.start()

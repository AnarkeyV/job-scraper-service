import sqlite3
from pathlib import Path
from app.config import settings

SCHEMA = """
CREATE TABLE IF NOT EXISTS subscriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    main_query TEXT NOT NULL,
    alternate_query TEXT,
    email TEXT NOT NULL,
    posted_within_days INTEGER NOT NULL,
    report_frequency TEXT NOT NULL,
    scan_frequency INTEGER NOT NULL,
    providers TEXT NOT NULL,
    countries TEXT NOT NULL,
    work_mode TEXT NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS scan_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subscription_id INTEGER NOT NULL,
    status TEXT NOT NULL,
    jobs_found INTEGER NOT NULL DEFAULT 0,
    started_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    finished_at TEXT,
    error TEXT,
    FOREIGN KEY(subscription_id) REFERENCES subscriptions(id)
);
CREATE TABLE IF NOT EXISTS provider_status (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_run_id INTEGER NOT NULL,
    provider TEXT NOT NULL,
    status TEXT NOT NULL,
    jobs_found INTEGER NOT NULL DEFAULT 0,
    message TEXT,
    started_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    finished_at TEXT,
    FOREIGN KEY(scan_run_id) REFERENCES scan_runs(id)
);
CREATE TABLE IF NOT EXISTS job_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subscription_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    company TEXT NOT NULL,
    source TEXT NOT NULL,
    location TEXT,
    work_mode TEXT,
    posted_at TEXT,
    url TEXT NOT NULL,
    fingerprint TEXT NOT NULL UNIQUE,
    discovered_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(subscription_id) REFERENCES subscriptions(id)
);
CREATE TABLE IF NOT EXISTS reports (
    id TEXT PRIMARY KEY,
    subscription_id INTEGER NOT NULL,
    html_path TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(subscription_id) REFERENCES subscriptions(id)
);
"""

def get_conn():
    Path(settings.database_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(settings.database_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_conn() as conn:
        conn.executescript(SCHEMA)
        conn.commit()

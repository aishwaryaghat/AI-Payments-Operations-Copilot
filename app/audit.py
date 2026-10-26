"""Durable audit events: SQLite in demo mode or PostgreSQL in configured mode.

Never store prompts, access tokens, account numbers, or generated answers.
Database errors are surfaced: the request fails rather than silently dropping audits.
"""
import os
import sqlite3
from datetime import datetime, timezone

def audit_event(actor: str, action: str, outcome: str, detail: str = "") -> None:
    backend = os.getenv("COPILOT_AUDIT_BACKEND", "sqlite")
    if backend == "postgres":
        import psycopg
        with psycopg.connect(os.environ["DATABASE_URL"]) as con:
            with con.cursor() as cur:
                cur.execute(
                    "INSERT INTO audit_events (event_time, actor, action, outcome, detail) VALUES (%s, %s, %s, %s, %s)",
                    (datetime.now(timezone.utc), actor, action, outcome, detail[:200])
                )
        return
    if backend != "sqlite":
        raise ValueError("Unsupported audit backend")
    path = os.getenv("COPILOT_AUDIT_DB_PATH", "copilot_audit.db")
    with sqlite3.connect(path, timeout=5) as con:
        con.execute("""CREATE TABLE IF NOT EXISTS audit_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_time TEXT NOT NULL, actor TEXT NOT NULL,
            action TEXT NOT NULL, outcome TEXT NOT NULL, detail TEXT NOT NULL
        )""")
        con.execute(
            "INSERT INTO audit_events(event_time, actor, action, outcome, detail) VALUES (?, ?, ?, ?, ?)",
            (datetime.now(timezone.utc).isoformat(), actor, action, outcome, detail[:200])
        )

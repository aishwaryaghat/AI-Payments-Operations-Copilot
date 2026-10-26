"""Approved parameterized SQL analytics over synthetic SQLite or PostgreSQL."""
import os
import sqlite3
from datetime import date

# Whitelisted query shapes (table/column names never come from the user).
QUERY_PARTS = {
    "failed_count": ("COUNT(*)", "FAILED", "transactions"),
    "exception_count": ("COUNT(*)", "EXCEPTION", "transactions"),
    "reconciliation_total": ("COALESCE(SUM(amount_cents),0)", "SUCCESS", "cents")
}
SYNTHETIC = [
    (1, "FAILED", 10000, "2026-10-20"),
    (2, "FAILED", 25000, "2026-10-20"),
    (3, "EXCEPTION", 5000, "2026-10-20"),
    (4, "SUCCESS", 75000, "2026-10-20"),
    (5, "SUCCESS", 10000, "2026-10-21"),
]

def run_analytics(intent: str, business_date: date) -> dict:
    if intent not in QUERY_PARTS:
        raise ValueError("Unsupported analytics intent")
    aggregate, status, unit = QUERY_PARTS[intent]
    backend = os.getenv("COPILOT_ANALYTICS_BACKEND", "sqlite")
    if backend == "postgres":
        import psycopg
        with psycopg.connect(os.environ["DATABASE_URL"]) as db:
            with db.cursor() as cur:
                cur.execute("SET TRANSACTION READ ONLY")
                cur.execute(
                    f"SELECT {aggregate} FROM payments WHERE status = %s AND business_date = %s",
                    (status, business_date))
                result = cur.fetchone()[0]
        source = "postgres"
    elif backend == "sqlite":
        with sqlite3.connect(":memory:") as db:
            db.execute("CREATE TABLE payments (id INTEGER, status TEXT, amount_cents INTEGER, business_date TEXT)")
            db.executemany("INSERT INTO payments VALUES (?, ?, ?, ?)", SYNTHETIC)
            result = db.execute(
                f"SELECT {aggregate} FROM payments WHERE status = ? AND business_date = ?",
                (status, business_date.isoformat())).fetchone()[0]
        source = "synthetic_sqlite"
    else:
        raise ValueError("Unsupported analytics backend")
    return {"intent": intent, "business_date": business_date.isoformat(),
            "value": result, "unit": unit, "data_source": source}

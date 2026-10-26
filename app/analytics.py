import sqlite3
from datetime import date

# Strict allowlist. No model-generated SQL or arbitrary SQL input.
QUERIES = {
    "failed_count": "SELECT COUNT(*) FROM payments WHERE status = 'FAILED' AND business_date = ?",
    "exception_count": "SELECT COUNT(*) FROM payments WHERE status = 'EXCEPTION' AND business_date = ?",
    "reconciliation_total": "SELECT COALESCE(SUM(amount_cents),0) FROM payments WHERE status = 'SUCCESS' AND business_date = ?",
}
SYNTHETIC = [
    (1, "FAILED", 10000, "2026-10-20"),
    (2, "FAILED", 25000, "2026-10-20"),
    (3, "EXCEPTION", 5000, "2026-10-20"),
    (4, "SUCCESS", 75000, "2026-10-20"),
    (5, "SUCCESS", 10000, "2026-10-21"),
]

def run_analytics(intent: str, business_date: date) -> dict:
    if intent not in QUERIES:
        raise ValueError("Unsupported analytics intent")
    with sqlite3.connect(":memory:") as db:
        db.execute("CREATE TABLE payments (id INTEGER, status TEXT, amount_cents INTEGER, business_date TEXT)")
        db.executemany("INSERT INTO payments VALUES (?, ?, ?, ?)", SYNTHETIC)
        result = db.execute(QUERIES[intent], (business_date.isoformat(),)).fetchone()[0]
    return {"intent": intent, "business_date": business_date.isoformat(),
            "value": result, "unit": "cents" if intent == "reconciliation_total" else "transactions",
            "data_source": "synthetic"}

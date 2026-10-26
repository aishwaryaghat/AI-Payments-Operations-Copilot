# AI Payments Operations Copilot

A **synthetic-data demonstration** of a secure payment-operations assistant. It combines cited runbook retrieval with approved, parameterized payment analytics. This is a portfolio implementation, **not an Oracle production system**.

## Features
- Python FastAPI REST API with JWT authentication and role-based access.
- Local TF-IDF semantic-style retrieval (no external model, network, or API key needed) with document citations. Swap the retriever for embeddings/vector DB in production.
- Approved read-only SQLite analytics templates for synthetic transactions.
- PII redaction, prompt-injection pattern checks, request audit records.
- Automated tests for retrieval, analytics, authentication and safety.
- Java Spring Boot gateway scaffold can be added independently.

## Quick start
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
export COPILOT_JWT_SECRET="replace-with-a-long-random-secret"
uvicorn app.main:app --reload
pytest -q
```
Visit http://127.0.0.1:8000/docs.

## Example
```bash
curl -X POST http://localhost:8000/token -d "username=analyst&password=demo-analyst-password"
# Use the returned access_token:
curl -H "Authorization: Bearer TOKEN" -H "Content-Type: application/json" \
  -d '{"question":"How should ACH validation failures be handled?"}' \
  http://localhost:8000/ask
curl -H "Authorization: Bearer TOKEN" -H "Content-Type: application/json" \
  -d '{"intent":"failed_count","business_date":"2026-10-20"}' \
  http://localhost:8000/analytics
```

Demo accounts: `analyst/demo-analyst-password` and `viewer/demo-viewer-password`. **Never use these credentials in a real deployment.**

## Architecture
```
Client -> FastAPI JWT/RBAC -> request classifier
                             |-> runbook retrieval -> cited response
                             |-> approved SQL -> aggregate response
                 -> audit log and redaction
```

## Limitations
This implementation is intentionally minimal and runnable offline. It uses TF-IDF, not an embedding model or generative LLM; therefore it is a **retrieval-based prototype**, not a fully deployed LLM RAG system. SQLite is a synthetic demo database, not PostgreSQL. No Java/Spring Boot implementation is included in this initial version. The test suite is a baseline, **not the 64-case suite** claimed in the resume. Add real embeddings, LLM generation, a persistent audit store, production identity provider, and a vetted 64-case benchmark before making those claims about this repository.

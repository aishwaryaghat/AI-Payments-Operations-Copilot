# AI Payments Operations Copilot

A financial-operations portfolio application built around **cited retrieval-augmented generation, approved payment analytics, auditability, and role-based access**. It uses synthetic runbooks and transaction fixtures; it is not connected to Oracle or customer data.

## Architecture

```text
Client
  |-- Java Spring Boot gateway (gateway/, forwards request bearer token)
  v
Python FastAPI (/ask, /rag/ask, /analytics)
  |-- JWT verification: demo HS256 or externally issued OIDC RS256/JWKS
  |-- RBAC: analyst and viewer; analysts can query payment aggregates
  |-- /rag/ask: Sentence Transformers embeddings, persistent local FAISS top-K vector index,
  |              grounded OpenAI-compatible LLM inference and source IDs
  |-- /ask: offline TF-IDF runbook-retrieval fallback with citations
  |-- /analytics: strictly allowlisted parameterized SQL aggregations
  |                using synthetic SQLite or PostgreSQL
  |-- audit: persistent SQLite or PostgreSQL audit events (no query contents)
```

## Implemented features

| Feature | Implementation |
| --- | --- |
| Python API | FastAPI + Pydantic validation + OpenAPI docs |
| Java integration | Spring Boot gateway under `gateway/` |
| RAG embeddings | Sentence Transformers + local FAISS cosine-equivalent inner-product index persisted to disk |
| LLM answers | OpenAI-compatible chat-completions client; requires configured API key |
| Retrieval fallback | TF-IDF runbook search and source citations at `/ask` |
| Payment analytics | PostgreSQL / offline SQLite, allowlisted parameterized queries |
| Authentication | Demo JWT or external OIDC (RS256 JWKS + issuer/audience/expiry validation) |
| Authorization | Analyst-only analytics endpoints |
| Sensitive-data handling | Basic email/account-format redaction and injection-pattern screening |
| Durable audit | SQLite or PostgreSQL records containing actor/action/outcome |
| Regression tests | 64 parameterized cases, plus 10 baseline test functions |
| Development | Dockerfile, local PostgreSQL Compose, GitHub Actions pytest workflow |

The 64 reproducible regression cases are in `tests/test_regression_64.py`: 16 retrieval cases, 16 analytics cases, 16 prompt-pattern cases, and 16 access-control cases. They are **code-path regression cases**, not a separately measured 64-example LLM accuracy benchmark.

## Local quick start

Python 3.12 is recommended.

```bash
python -m venv .venv
# Linux / macOS
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
export COPILOT_JWT_SECRET="replace-with-a-long-random-secret" # set via PowerShell on Windows
uvicorn app.main:app --reload
```

Open `http://localhost:8000/docs`. For synthetic local testing, the two example accounts are `analyst/demo-analyst-password` and `viewer/demo-viewer-password`; **do not deploy them to a publicly reachable instance**.

Obtain a demo access token:

```bash
curl -X POST http://localhost:8000/token -d "username=analyst&password=demo-analyst-password"
```

Use the returned bearer token:

```bash
curl -H "Authorization: Bearer TOKEN" -H "Content-Type: application/json" \
  -d '{"question":"How are ACH file validation failures handled?"}' \
  http://localhost:8000/ask

curl -H "Authorization: Bearer TOKEN" -H "Content-Type: application/json" \
  -d '{"intent":"failed_count","business_date":"2026-10-20"}' \
  http://localhost:8000/analytics
```

## Enable embedding-based RAG + generative LLM

```bash
pip install -r requirements-rag.txt
export OPENAI_API_KEY="YOUR_API_KEY"
# Optional: export COPILOT_LLM_MODEL="gpt-4o-mini"
uvicorn app.main:app --reload
```

Call `POST /rag/ask` with `{"question":"How should a rejected ACH file be investigated?","top_k":3}` and a bearer token. The default embedding model is `sentence-transformers/all-MiniLM-L6-v2`; it downloads its weights on first use. FAISS saves a local vector index under `.copilot_vectors/` (configurable using `COPILOT_VECTOR_DIR`) for the synthetic corpus. Without an API key the endpoint still performs embedding retrieval and returns evidence/citations, but not a generative answer. LLM provider access can incur costs. Do not send customer information to an external model.

## PostgreSQL analytics and persistent audit

```bash
docker compose up -d postgres
export DATABASE_URL="postgresql://copilot:local-demo-only@localhost:5432/copilot"
export COPILOT_ANALYTICS_BACKEND=postgres
export COPILOT_AUDIT_BACKEND=postgres
uvicorn app.main:app --reload
```

The local container initializes `infra/postgres/schema.sql` with synthetic data and an `audit_events` table. For deployed systems, use separately provisioned least-privilege database identities for analytics (SELECT-only) and audit writing (INSERT-only), managed database secrets, backups and network restrictions. Do not use the Compose sample password outside a localhost demo.

## External identity provider (OIDC)

Configure environment variables `COPILOT_AUTH_MODE=oidc`, `OIDC_ISSUER`, `OIDC_AUDIENCE` and `OIDC_JWKS_URL`. In this mode, token verification uses RS256 signing keys served by the issuer's JWKS endpoint and validates issuer, audience and expiry. Users with an `analyst` role in the JWT `roles` claim can call analytics; all other valid identities receive viewer access. The demo `/token` route is disabled. Configure your actual identity provider's claim mapping accordingly.

The Spring Boot gateway starts with:

```bash
mvn -f gateway/pom.xml spring-boot:run
```

See `gateway/README.md` and `docs/architecture.md` for trust boundaries and deployment considerations.

## Test

```bash
pytest -q
```

GitHub Actions executes the default Python test suite on pushes and pull requests. Heavy model-based retrieval and external LLM provider calls are optional and are not exercised by these deterministic tests.

## Scope and deployment notes

This repository is an inspectable demonstration using **synthetic-only data**. The embedding RAG uses a persistent local FAISS index for a small synthetic runbook collection, not a horizontally scalable hosted vector database. Output citations identify retrieved passages, but generated claims are not independently verified sentence by sentence. The Java gateway currently delegates token verification to FastAPI. OIDC requires real identity-provider configuration, and externally hosted LLM generation requires provider credentials. PII filtering and prompt-injection screening are basic defenses, not a substitute for end-to-end security reviews. Further work for production includes document-level/tenant-level authorization, dedicated database accounts, full observability, adversarial evaluation and independent grounding checks.

See `docs/architecture.md` for implementation details and the remaining hardening work.

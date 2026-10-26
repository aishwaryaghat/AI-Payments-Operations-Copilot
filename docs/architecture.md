# Architecture, security boundaries and next steps

## Running components
- Python FastAPI API: authentication, request validation and role enforcement.
- Java Spring Boot: demonstration HTTP gateway. Access tokens are validated downstream in FastAPI.
- Retrieval: baseline TF-IDF and optional Sentence Transformers embeddings with OpenAI-compatible grounded response generation.
- Analytics: fixed query intents, parameterized predicates and synthetic SQLite or PostgreSQL.
- Persistent audit: SQLite or PostgreSQL writes to audit_events, storing event actor, action and outcome without full prompts.
- Identity: local demo JWT or issuer-configured RS256 OIDC token verification with JWKS.
- 64 parameterized regression cases plus baseline tests and a GitHub Actions pytest workflow.

## Trust boundaries
1. Never use model output to authorize tools or database access.
2. SQL aggregation templates use a fixed allowlist; parameters are bound by the DB driver.
3. Access verification occurs in FastAPI; the Java gateway forwards tokens but does not independently verify them.
4. OIDC verification checks signature, issuer, audience and expiry. Provider setup and claim mapping must be configured.
5. The included regex redaction and injection-pattern screening are defense-in-depth only and are not sufficient for production DLP.
6. Source IDs attached to LLM responses identify retrieved passages; claims are not independently verified against cited passages.
7. Data sources are synthetic. This repository is not connected to confidential company or customer information.
8. Production PostgreSQL must use least-privilege, separate analytics/audit accounts, network isolation and rotation of credentials.

## Scope of the 64-case suite
The 64 parameterized cases exercise 16 retrieval examples, 16 synthetic analytics cases,
16 disallowed request patterns and 16 analyst/viewer access conditions. The cases are
reproducible regression checks, not independent LLM grounding or model accuracy measurements.

## Deployment hardening still required
- Persist the vector index to FAISS/pgvector or another vector database for larger-scale search.
- Add ingestion for document PDFs, JSON and metadata-aware chunking with document-level entitlements.
- Add tenant-scoped retrieval and data authorization.
- Add response-grounding/citation validation and labeled LLM evaluation metrics.
- Apply robust PII detection, red-team testing, operational tracing and rate limiting.
- Add Spring gateway-level OIDC validation, consistent error mapping and telemetry.
- Separate PostgreSQL read-only analytics and insert-only audit accounts.
- Validate cloud deployment and disaster-recovery controls before production use.

This is a portfolio demonstration, not an Oracle or other institutional deployment.

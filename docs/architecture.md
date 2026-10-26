# Architecture, threat model and roadmap

## Current implementation (demo)
- Python FastAPI authentication and request validation.
- JWT and two hard-coded sample users for **local demonstration only**.
- Local TF-IDF retriever at `POST /ask`.
- Optional Sentence Transformers embeddings at `POST /rag/ask`. Optional LLM generation requires `OPENAI_API_KEY`.
- Synthetic SQLite data and three allowlisted analytics intents at `POST /analytics`.
- Regex-based PII redaction and injection-pattern screening. These are **not comprehensive** safeguards.
- Structured audit events emitted through Python logging; no durable audit storage yet.
- CI unit tests.

## Trust boundaries
1. Treat documents, user input and model output as untrusted.
2. Verify JWT identity at the API. Real deployment needs an external identity provider and rotated secrets.
3. Enforce data permissions server-side. No model-driven authorization.
4. Never allow arbitrary SQL from users or LLMs.
5. Avoid PII in external LLM requests; replace demo redaction with validated DLP.
6. Document-level entitlements, tenant-scoped indexing, durable audits and network controls are **not implemented**.
7. Model-generated citations are not automatically validated; use output-level citation verification before production.

## Next steps
- Replace in-memory TF-IDF/indexing with a versioned vector store (FAISS/pgvector).
- Add document parsing and chunking from real synthetic PDF and JSON datasets.
- Add metadata-filtered retrieval and reranking.
- Add Spring Boot business gateway with a real OAuth2/OIDC provider.
- Integrate PostgreSQL read-only roles with tenant isolation.
- Add the actual 64-case labeled evaluation suite with measured retrieval/answer/safety metrics.
- Run load, security and privacy testing before any real-world use.

This repo does not contain proprietary Oracle code or customer data.

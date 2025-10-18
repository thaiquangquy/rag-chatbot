```markdown
# research.md — RAG Chatbot for Company Wiki

## Purpose

Resolve technical unknowns (`NEEDS CLARIFICATION`) from `plan.md` and `spec.md` and produce concrete choices for Phase 1 design.

## Decisions

### Language and Runtime

- Decision: Python 3.11
- Rationale: Python has strong ML/AI ecosystem (transformers, OpenAI SDKs), web frameworks (FastAPI), and good developer ergonomics for rapid prototyping.
- Alternatives considered: Node.js (good for frontend/backend), Go (fast but less ML tooling). Rejected because of ecosystem advantages in Python.

### Web Backend Framework

- Decision: FastAPI
- Rationale: FastAPI is async, performant, provides automatic OpenAPI generation, and integrates well with Python typing and dependency injection.

### Frontend

- Decision: React (TypeScript) for Chat UI
- Rationale: Familiar ChatGPT-like UI patterns are easy to implement with React. TypeScript improves maintainability.

### LLM Provider

- Decision: Primary: OpenAI API (text-embedding-3-small & gpt-4o/others), Secondary: Ollama local LLM via OpenAI-compatible API for on-prem fallback
- Rationale: OpenAI provides high-quality embeddings and LLMs; Ollama offers local hosting for data residency and offline testing. Implement an abstraction layer to switch providers.

### Embedding Provider & Vector Store

- Decision: Use OpenAI embeddings (when using OpenAI) and FAISS (local) or Milvus/Weaviate for managed scaling
- Rationale: FAISS is simple for on-disk local prototype; provide connectors to Milvus/Weaviate for production scaling.

### Storage

- Decision: PostgreSQL for metadata (documents, sections, provenance) + file storage for raw artifacts (S3-compatible)
- Rationale: Relational metadata with strong consistency; object store for raw doc backups and retrieval URLs.

### Authentication to Google Docs

- Decision: Service account with domain-wide delegation (confirmed in spec)
- Rationale: Enables centralized ingestion and easier automation. Must include rotation and emergency revocation runbook (see Runbook section).

### Conversation State and Sessions

- Decision: Store session state in Redis (fast ephemeral storage) with durable transcripts in PostgreSQL

### Testing

- Decision: pytest with integration tests using testcontainers/postgres + local FAISS index

### Observability

- Decision: OpenTelemetry for tracing, Prometheus metrics, and structured JSON logs (stdout)

## Runbook: Credential Rotation & Compromise Handling

- Rotation cadence: rotate service account keys every 90 days (minimum), automated via CI/CD secrets manager integration.
- Detection: Monitor IAM admin activity logs and failed-auth spikes; alert on suspicious activity or key usage from unexpected IPs.
- Revocation: Have an automated playbook to revoke compromised keys, trigger index ingestion pause, and issue a new key via an automated pipeline.
- Fallback: Maintain a short-lived backup key set (rotated) and use provider-based delegation to re-issue keys quickly. Document manual override procedure in runbook.

## Open Questions (NEEDS CLARIFICATION)

- Deployment target (Cloud provider): NEEDS CLARIFICATION — affects managed vector store choice and object storage.
- Expected initial document corpus size beyond estimates (<500MB): confirm to size indexes and infra.
- Security posture: whether documents may include highly sensitive PII requiring additional controls (affects encryption and on-prem choices).

## Artifacts produced

- This `research.md` resolves most technical choices for Phase 1. Remaining open questions are listed above and need to be clarified with stakeholders.
```

# Tasks: RAG Chatbot for Company Wiki

This plan turns the spec and plan into concrete, independently testable tasks organized by user story.

## Phase 1 — Setup (project initialization)

- [x] T001 [P] Create FastAPI app entrypoint in backend/src/api/main.py
- [x] T002 [P] Add application settings module in backend/src/config/settings.py
- [x] T003 [P] Create Python dependency manifest in backend/requirements.txt (pin FastAPI, Uvicorn, SQLAlchemy, psycopg, redis, openai, faiss-cpu, opentelemetry-api, opentelemetry-sdk, prometheus-client, pydantic-settings, python-dotenv, pytest, testcontainers)
- [x] T004 [P] Configure tooling in backend/pyproject.toml (ruff, black, pytest)
- [x] T005 [P] Add initial healthcheck test in backend/tests/unit/test_healthcheck.py
- [x] T006 [P] Add Docker Compose for Postgres and Redis in docker-compose.yml
- [x] T007 [P] Initialize React+TypeScript app in frontend/package.json (Vite + React)
- [x] T008 [P] Configure TS compiler options in frontend/tsconfig.json
- [x] T009 [P] Create frontend entry page in frontend/src/pages/index.tsx
- [x] T010 [P] Scaffold ChatWindow component in frontend/src/components/ChatWindow.tsx
- [x] T011 [P] Add OpenTelemetry setup in backend/src/observability/otel.py
- [x] T012 [P] Create API routes package init in backend/src/api/routes/**init**.py

## Phase 2 — Foundational (blocking prerequisites)

- [x] T013 [P] Define ORM entities in backend/src/models/entities.py (Document, Section, Query, Response, Conversation)
- [x] T014 [P] Define API schemas in backend/src/models/schemas.py (Pydantic models)
- [x] T015 Create Alembic config in backend/alembic/env.py (database URL from settings)
- [x] T016 [P] Implement FAISS index wrapper in backend/src/vector/faiss_index.py
- [x] T017 [P] Implement Google Docs client in backend/src/integrations/google_docs_client.py (service account auth)
- [x] T018 [P] Implement API key auth middleware in backend/src/middleware/auth.py
- [x] T019 [P] Implement audit logging middleware in backend/src/middleware/audit.py (structured JSON)
- [x] T020 [P] Implement provider abstraction in backend/src/providers/llm_provider.py (OpenAI and Ollama adapters)
- [x] T021 [P] Add health endpoint in backend/src/api/routes/health.py and wire to main.py
- [x] T022 [P] Create text chunking utilities in backend/src/lib/chunking.py
- [x] T023 [P] Create embedding pipeline utilities in backend/src/lib/embedding.py

## Phase 3 — User Story 3: Multi-Document Context Ingestion (P1)

- [x] T024 [P] [US3] Add contract test for /ingest in backend/tests/contract/test_ingest_endpoint.py (accepts document_id, 202 + task_id)
- [x] T025 [US3] Implement ingestion service in backend/src/services/ingest_service.py (fetch, parse, chunk, persist)
- [x] T026 [US3] Implement /ingest route in backend/src/api/routes/ingest.py (enqueue background task)
- [x] T027 [P] [US3] Persist Document and Sections in backend/src/services/ingest_service.py (SQLAlchemy session)
- [x] T028 [P] [US3] Index sections in FAISS in backend/src/vector/faiss_index.py (upsert vectors)
- [x] T029 [US3] Implement refresh service in backend/src/services/refresh_service.py (re-index on update)
- [x] T030 [US3] Add ingestion→index integration test in backend/tests/integration/test_ingest_to_index.py
- [x] T031 [P] [US3] Add admin CLI to trigger ingestion in backend/src/cli/ingest_cli.py

## Phase 4 — User Story 1: Quick Answer Lookup (P1)

- [x] T032 [P] [US1] Add contract test for /chat in backend/tests/contract/test_chat_endpoint.py (request query+session_id; returns generated_text)
- [x] T033 [US1] Implement retrieval service in backend/src/services/retrieval_service.py (query embed + top_k search)
- [x] T034 [US1] Implement answer synthesis service in backend/src/services/answer_service.py (LLM compose from sections)
- [x] T035 [US1] Implement /chat route in backend/src/api/routes/chat.py (wire services)
- [x] T036 [P] [US1] Implement frontend API client in frontend/src/services/api.ts (POST /chat)
- [x] T037 [P] [US1] Implement MessageList component in frontend/src/components/MessageList.tsx
- [x] T038 [P] [US1] Implement MessageInput component in frontend/src/components/MessageInput.tsx
- [x] T039 [US1] Wire ChatWindow to API in frontend/src/components/ChatWindow.tsx (send/receive stream or full response)
- [x] T040 [US1] Add chat flow integration test in backend/tests/integration/test_chat_flow.py

## Phase 5 — User Story 2: Source Attribution & Verification (P1)

- [x] T041 [P] [US2] Implement source link builder in backend/src/utils/source_link.py (Google Docs section/heading links)
- [x] T042 [US2] Include sources in retrieval results in backend/src/services/retrieval_service.py (section_id, document_id, snippet, url)
- [x] T043 [US2] Update response schema with sources in backend/src/models/schemas.py
- [x] T044 [P] [US2] Implement SourceList component in frontend/src/components/SourceList.tsx
- [x] T045 [US2] Render sources in ChatWindow in frontend/src/components/ChatWindow.tsx (clickable links)
- [x] T046 [US2] Add contract test for sources in backend/tests/contract/test_chat_sources.py

## Phase 6 — User Story 4: Contextual Relevance & Answer Quality (P2)

- [x] T047 [P] [US4] Implement re-ranking heuristics in backend/src/pipelines/rerank.py (score combiner/filters)
- [x] T048 [US4] Add ambiguity detection and clarify prompts in backend/src/services/answer_service.py
- [x] T049 [US4] Add relevance unit tests in backend/tests/unit/test_relevance.py

## Phase 7 — User Story 5: Fallback for Unanswered Questions (P2)

- [x] T050 [US5] Implement no-answer threshold policy in backend/src/services/answer_service.py
- [x] T051 [P] [US5] Implement related topics suggester in backend/src/services/suggest_service.py
- [x] T052 [US5] Render fallback UX in frontend/src/components/ChatWindow.tsx (clear message)
- [x] T053 [US5] Add fallback contract test in backend/tests/contract/test_chat_fallback.py

## Phase 8 — Critical Bug Fix: FAISS Index Persistence

- [x] T076 [BUG] Add FAISS index persistence methods (save/load) in backend/src/vector/faiss_index.py with disk storage at data/faiss_index.bin
- [x] T077 [BUG] Update ingestion services and CLI to persist index after ingestion in backend/src/services/{ingest,refresh}\_service.py and backend/src/cli/ingest_cli.py
- [x] T078 [BUG] Update chat endpoint to load persisted index on startup in backend/src/api/routes/chat.py and add integration tests in backend/tests/integration/test_faiss_persistence.py

---

## Final Phase — Polish & Cross-Cutting

- [ ] T054 [P] Add OpenTelemetry tracing to /ingest and /chat in backend/src/observability/otel.py
- [ ] T055 [P] Expose Prometheus metrics endpoint in backend/src/api/routes/metrics.py
- [ ] T056 Update data model with sensitivity flag in backend/src/models/entities.py (is_sensitive: bool, sensitivity_level: enum)
- [ ] T057 Create migration for sensitivity flag in backend/alembic/versions/0002_add_sensitive_flag.py
- [ ] T058 Enforce audit for sensitive docs in backend/src/middleware/audit.py (log access to sensitive=true)
- [ ] T059 Add credential rotation runbook in specs/001-rag-chatbot-wiki/runbooks/credential-rotation.md
- [ ] T060 Add backend README in backend/README.md (run, env vars, endpoints)
- [ ] T061 [P] Add performance test suite (chat latency benchmarks; ingest timing) in backend/tests/performance/test_latency.py.
- [ ] T062 [P] Add Prometheus metrics contract test backend/tests/contract/test_metrics_endpoint.py.
- [ ] T063 Add distributed tracing spans (ingest, retrieval, answer synthesis) validation test backend/tests/integration/test_tracing_spans.py.
- [ ] T064 Add load sample script backend/src/cli/load_test_cli.py for generating concurrent chat queries (locust or simple asyncio) to validate p95 thresholds.
- [ ] T065 Add logging/retention configuration doc specs/001-rag-chatbot-wiki/runbooks/log-retention.md (defines retention 90 days + masking rules).
- [ ] T066 Implement conversation persistence (Redis + Postgres transcript) with tests backend/tests/integration/test_conversation_persistence.py.

- [ ] T067 [P] Add sensitive schema contract test in backend/tests/contract/test_sensitive_schema.py (includes is_sensitive fields)
- [ ] T068 Add migration verification test in backend/tests/integration/test_migration_sensitive_flag.py
- [ ] T069 Add sensitive access audit integration test in backend/tests/integration/test_sensitive_access_audit.py
- [ ] T070 Implement exponential backoff for Google API (HTTP 429/5xx) in backend/src/integrations/google_docs_client.py
- [ ] T071 [P] Add unit tests for backoff logic in backend/tests/unit/test_google_backoff.py
- [ ] T072 [P] Add ingestion throttling integration test in backend/tests/integration/test_ingest_throttling.py
- [ ] T073 Add source link behavior doc in specs/001-rag-chatbot-wiki/docs/source-linking.md (anchor limitations & fallbacks)
- [ ] T074 Implement sensitive data redaction in logging middleware in backend/src/middleware/audit.py
- [ ] T075 [P] Add unit tests for logging redaction in backend/tests/unit/test_logging_redaction.py

---

## Dependencies (story completion order)

- US3 (Ingestion) → US1 (Quick Answer) → US2 (Source Attribution)
- US4 (Relevance) and US5 (Fallback) build on US1 and can proceed after basic chat is functional
- **Phase 8 (Bug Fix)**: CRITICAL - Must complete before chat endpoint can function correctly with ingested data

## Parallel execution examples

- T024 [US3] contract test and T025 ingestion service can proceed in parallel with T028 FAISS indexing wrapper work
- T036/T037/T038 frontend components can proceed in parallel with T033/T034 backend services
- T041/T044 source link backend and frontend can proceed in parallel once /chat returns source placeholders
- T076-T078 (settings, save, load methods) can proceed in parallel
- T079-T082 (update services) must wait for T076-T078 completion

## Independent test criteria per story

- US3: POST /ingest accepts a valid Google Doc ID and returns 202 with task_id; ingestion results in sections present in DB and FAISS index
- US1: POST /chat returns generated_text derived from indexed content for a known query; p95 latency under 3s in local env
- US2: /chat response contains clickable source URLs that open the correct Google Doc section
- US4: Queries with ambiguous terms trigger clarify prompt or select most relevant intent; re-ranked results improve precision@k
- US5: Out-of-scope questions result in a clear no-answer response with related topics suggestions
- **Bug Fix (Phase 8)**: Chat endpoint successfully returns matching context for specific query "Thai Quang Quy" after document ingestion

## Implementation strategy (MVP first)

- MVP = US3 + US1 minimal (no re-ranking, basic sources) to deliver a working chat answering from indexed docs
- Next = US2 source attribution polish; then US4 relevance; then US5 fallback UX
- **Critical Bug**: Phase 8 bug fix is now BLOCKING for MVP - must be completed for functional chat endpoint

## Summary

**Total Tasks**: 78 (78 completed ✅)
**Tasks per User Story**:

- Setup (Phase 1): 12 tasks ✅
- Foundational (Phase 2): 11 tasks ✅
- US3 - Multi-Document Ingestion: 8 tasks ✅
- US1 - Quick Answer Lookup: 9 tasks ✅
- US2 - Source Attribution: 6 tasks ✅
- US4 - Contextual Relevance: 3 tasks ✅
- US5 - Fallback Handling: 4 tasks ✅
- **Phase 8 - Bug Fix**: 3 tasks ✅ (FAISS persistence)
- Polish & Cross-Cutting: 22 tasks (pending)

**Parallel Opportunities**: Tasks marked [P] can run in parallel within their phase
**MVP Scope**: US3 + US1 + US2 + Phase 8 bug fix ✅
**Format Validation**: ✅ All tasks follow checklist format with ID, optional [P] and [Story] labels, and file paths

````markdown
# quickstart.md — RAG Chatbot (local dev)

Prerequisites:

- Python 3.11
- Poetry or pip + virtualenv
- Docker (optional for Postgres/Redis)

1. Install dependencies

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt
```
````

2. Start dev services (Postgres, Redis)

```powershell
docker compose up -d
```

3. Run the ingestion (example)

```powershell
python -m rag_chatbot.ingest --document-id="<DOC_ID>" --service-account=secrets/service_account.json

py -m backend.src.cli.ingest_cli ingest "1GtNxpX3NYntobPpp8j2YJyeecbKsbTrdtDBzUgL6lsg" --source "https://docs.google.com/document/d/1GtNxpX3NYntobPpp8j2YJyeecbKsbTrdtDBzUgL6lsg/edit?tab=t.0"
```

4. Run the API server

```powershell
uvicorn backend.src.api.main:app --reload --port 8080
```

5. Open the chat UI (frontend)

- Frontend runs on http://localhost:3000 (React dev server)

Notes:

- Configure `OPENAI_API_KEY` or `OLLAMA_API` env var for LLM access.
- For on-prem/local LLM testing, install Ollama and run a compatible model.

```

```

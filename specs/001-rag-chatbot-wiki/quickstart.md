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
```

4. Run the API server

```powershell
uvicorn rag_chatbot.api:app --reload --port 8000
```

5. Open the chat UI (frontend)

- Frontend runs on http://localhost:3000 (React dev server)

Notes:

- Configure `OPENAI_API_KEY` or `OLLAMA_API` env var for LLM access.
- For on-prem/local LLM testing, install Ollama and run a compatible model.

```

```

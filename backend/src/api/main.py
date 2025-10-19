from fastapi import FastAPI

from backend.src.api.routes import router as api_router

app = FastAPI(title="RAG Chatbot API")

app.include_router(api_router)


@app.get("/")
def root() -> dict[str, str]:
    return {"status": "ok"}

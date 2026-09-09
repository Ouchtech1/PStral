"""Pstral demo API: local retrieval and SQL generation, without Oracle access."""

from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.endpoints import auth, chat
from app.core.auth import init_users_db
from app.core.config import settings
from app.domain.services.chat_service import ChatService
from app.infrastructure.database.audit_db import init_audit_db
from app.infrastructure.llm.ollama_client import OllamaClient
from app.infrastructure.rag.document_rag import DocumentRAG
from app.infrastructure.sql.sql_catalog import SQLCatalog


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pstral")


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings.validate_runtime()
    settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
    init_users_db()
    init_audit_db()

    rag = DocumentRAG()
    rag.initialize()
    catalog = SQLCatalog.from_path(settings.SQL_CATALOG_PATH)
    llm = OllamaClient()
    app.state.chat_service = ChatService(rag, catalog, llm)
    app.state.ollama_ready = await llm.model_is_available()
    if not app.state.ollama_ready:
        logger.warning("Le modèle local configuré est indisponible ; /ready restera en erreur.")
    yield
    await llm.close()


app = FastAPI(
    title=settings.PROJECT_NAME,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.middleware("http")
async def reject_large_requests(request: Request, call_next):
    content_length = request.headers.get("content-length")
    if content_length:
        try:
            too_large = int(content_length) > settings.MAX_HTTP_BODY_BYTES
        except ValueError:
            return Response(status_code=400, content="En-tête Content-Length invalide.")
        if too_large:
            return Response(status_code=413, content="Corps de requête trop volumineux.")
    return await call_next(request)


app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(chat.router, prefix=settings.API_V1_STR, tags=["chat"])


@app.get("/health")
def health_check():
    return {"status": "ok", "profile": settings.DEMO_PROFILE}


@app.get("/ready")
async def readiness(request: Request):
    service = getattr(request.app.state, "chat_service", None)
    if not service:
        raise HTTPException(status_code=503, detail="Initialisation en cours.")
    ready = await service.llm_client.model_is_available()
    request.app.state.ollama_ready = ready
    if not ready:
        raise HTTPException(status_code=503, detail="Le modèle local configuré est indisponible.")
    return {
        "status": "ready",
        "profile": settings.DEMO_PROFILE,
        "model": settings.OLLAMA_MODEL,
        "catalog_version": service.catalog.version,
        "corpus_version": service.rag.corpus_version,
    }

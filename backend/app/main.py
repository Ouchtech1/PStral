from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import httpx
import logging
import time
from app.core.config import settings
from app.api.v1.endpoints import chat, feedback, auth, audit, sql_execute, conversations
from app.infrastructure.database.oracle_client import db_client
from app.infrastructure.database.feedback_db import init_db
from app.infrastructure.database.audit_db import init_audit_db, log_action
from app.infrastructure.database.conversations_db import init_conversations_db
from app.core.auth import init_users_db, decode_token
from app.core.metrics import get_metrics, record_request

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- STARTUP ---
    logger.info("Starting up Pstral AI Assistant...")
    
    # 1. Connect Database
    await db_client.connect()
    init_db()
    
    # 2. Initialize Users Database
    init_users_db()
    logger.info("Users database initialized.")
    
    # 3. Initialize Audit Database
    init_audit_db()
    logger.info("Audit database initialized.")
    
    # 4. Initialize Conversations Database
    init_conversations_db()
    logger.info("Conversations database initialized.")
    
    # 5. Check Ollama
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            resp = await client.get(f"{settings.OLLAMA_BASE_URL}/api/tags")
            if resp.status_code == 200:
                models = [m['name'] for m in resp.json().get('models', [])]
                if settings.OLLAMA_MODEL in models:
                    logger.info(f"Ollama connected. Model '{settings.OLLAMA_MODEL}' found.")
                else:
                    logger.warning(f"Ollama connected, but model '{settings.OLLAMA_MODEL}' NOT found. Please run `ollama pull {settings.OLLAMA_MODEL}`.")
            else:
                logger.warning("Ollama reachable but returned error.")
    except Exception as e:
        logger.warning(f"Could not connect to Ollama at {settings.OLLAMA_BASE_URL}. AI features may fail. Error: {e}")

    yield
    
    # --- SHUTDOWN ---
    logger.info("Shutting down...")
    await db_client.close()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# CORS Security
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Audit Middleware
@app.middleware("http")
async def audit_middleware(request: Request, call_next):
    start_time = time.time()
    
    # Get user info from token if available
    user_id = None
    username = "anonymous"
    
    auth_header = request.headers.get("authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        token_data = decode_token(token)
        if token_data:
            username = token_data.username
    
    # Process request
    response = await call_next(request)
    
    # Calculate response time
    response_time_ms = int((time.time() - start_time) * 1000)
    
    # Log important actions (skip health checks and static files)
    path = request.url.path
    if not path.startswith("/health") and not path.startswith("/static"):
        # Determine action from path and method
        method = request.method
        action = f"{method} {path}"
        
        # Get client info
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        
        # Status
        status = "success" if response.status_code < 400 else "error"
        
        # Log to audit database (async-safe logging)
        try:
            log_action(
                user_id=user_id,
                username=username,
                action=action,
                resource=path,
                ip_address=ip_address,
                user_agent=user_agent,
                status=status,
                response_time_ms=response_time_ms
            )
        except Exception as e:
            logger.error(f"Failed to log audit: {e}")
    
    return response

# Router
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(chat.router, prefix=settings.API_V1_STR, tags=["chat"])
app.include_router(feedback.router, prefix=f"{settings.API_V1_STR}/feedback", tags=["feedback"])
app.include_router(audit.router, prefix=f"{settings.API_V1_STR}/audit", tags=["audit"])
app.include_router(sql_execute.router, prefix=f"{settings.API_V1_STR}/sql", tags=["sql"])
app.include_router(conversations.router, prefix=f"{settings.API_V1_STR}/conversations", tags=["conversations"])

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "database": "connected" if db_client.pool else "disconnected"
    }


@app.get("/metrics")
def metrics():
    """Prometheus metrics endpoint."""
    return get_metrics()

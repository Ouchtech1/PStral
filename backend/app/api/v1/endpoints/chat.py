import json
import time
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse

from app.core.auth import User, get_current_active_user
from app.domain.models.chat_models import ChatRequest
from app.domain.services.chat_service import ChatBusyError, ChatService
from app.infrastructure.database.audit_db import log_action


router = APIRouter()


def get_chat_service(request: Request) -> ChatService:
    return request.app.state.chat_service


@router.post("/chat")
async def chat(
    request: ChatRequest,
    http_request: Request,
    current_user: User = Depends(get_current_active_user),
    service: ChatService = Depends(get_chat_service),
):
    try:
        await service.try_acquire()
    except ChatBusyError as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(exc),
            headers={"Retry-After": "5"},
        ) from exc

    request_id = str(uuid4())

    async def event_generator():
        started_at = time.monotonic()
        outcome = "error"
        try:
            yield f"event: status\ndata: {json.dumps({'type': 'status', 'request_id': request_id, 'message': 'Préparation de la demande…'}, ensure_ascii=False)}\n\n"
            async for event in service.generate(request):
                event["request_id"] = request_id
                if event.get("type") == "done":
                    outcome = "success" if event.get("success") else "error"
                yield f"event: {event['type']}\ndata: {json.dumps(event, ensure_ascii=False)}\n\n"
                if await http_request.is_disconnected():
                    outcome = "cancelled"
                    break
        finally:
            service.release()
            log_action(
                user_id=current_user.id,
                username=current_user.username,
                action="CHAT_GENERATION",
                resource="/api/v1/chat",
                details={"mode": request.mode, "outcome": outcome, "duration_ms": int((time.monotonic() - started_at) * 1000)},
                status=outcome,
            )

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )

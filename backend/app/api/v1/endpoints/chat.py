from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from app.domain.models.chat_models import ChatRequest
from app.domain.services.chat_service import ChatService

router = APIRouter()

def get_chat_service():
    return ChatService()

import json

@router.post("/chat")
async def chat(request: ChatRequest, service: ChatService = Depends(get_chat_service)):
    
    async def event_generator():
        async for chunk in service.generate_response(request):
            # JSON encode the chunk to handle newlines and special chars safely
            data = json.dumps({"content": chunk})
            yield f"data: {data}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

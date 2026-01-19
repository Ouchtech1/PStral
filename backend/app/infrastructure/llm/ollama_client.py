import json
import httpx
from typing import AsyncGenerator, List
from app.core.config import settings
from app.domain.models.chat_models import Message

class OllamaClient:
    def __init__(self, base_url: str = settings.OLLAMA_BASE_URL):
        self.base_url = base_url
    
    def _limit_history(self, messages: list[Message]) -> list[Message]:
        """
        Limit message history to prevent context overflow.
        Keeps the first message (for context) and the last N messages.
        """
        max_messages = settings.MAX_HISTORY_MESSAGES
        
        if len(messages) <= max_messages:
            return messages
        
        # Keep first message (initial context) + last (max_messages - 1) messages
        return [messages[0]] + messages[-(max_messages - 1):]
    
    async def chat_stream(self, messages: list[Message], system_context: str) -> AsyncGenerator[str, None]:
        """
        Streams response from Ollama.
        """
        # Limit history to prevent token overflow
        limited_messages = self._limit_history(messages)
        
        # Inject system context into the first message or as a system prompt
        full_messages = [{"role": "system", "content": system_context}]
        
        for m in limited_messages:
            msg_dict = {"role": m.role, "content": m.content}
            if m.images:
                msg_dict["images"] = m.images
            full_messages.append(msg_dict)
        
        # Real implementation
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                async with client.stream(
                    "POST", 
                    f"{self.base_url}/api/chat", 
                    json={"model": settings.OLLAMA_MODEL, "messages": full_messages},
                ) as response:
                    async for line in response.aiter_lines():
                        if line:
                            try:
                                data = json.loads(line)
                                if "message" in data and "content" in data["message"]:
                                    yield data["message"]["content"]
                            except:
                                pass
            except httpx.ConnectError:
                yield "⚠️ **System Error**: Cannot connect to local AI engine (Ollama). Please ensure it is running (`ollama serve`)."
            except httpx.ReadTimeout:
                yield "⚠️ **Timeout**: The AI model is taking too long to respond."
            except Exception as e:
                yield f"⚠️ **Error**: {str(e)}"

from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class Message(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str
    images: Optional[List[str]] = None

class ChatRequest(BaseModel):
    messages: List[Message]
    stream: bool = True
    mode: Literal["sql", "email", "wiki", "chat"] = "chat"

class ChatResponse(BaseModel):
    content: str
    done: bool
    context: Optional[dict] = None

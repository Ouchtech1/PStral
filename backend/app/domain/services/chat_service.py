import os
from app.domain.models.chat_models import ChatRequest
from app.infrastructure.llm.ollama_client import OllamaClient
from app.core.security import validate_prompt
from app.core.prompts import PromptManager

class ChatService:
    def __init__(self):
        self.llm_client = OllamaClient()
        self.resources_path = "app/resources"

    def _load_context(self, mode: str) -> str:
        schema = ""
        packages = ""
        examples = ""
        
        if mode == "sql":
            try:
                with open(os.path.join(self.resources_path, "schema.txt"), "r") as f:
                    schema = f.read()
                with open(os.path.join(self.resources_path, "examples.txt"), "r") as f:
                    examples = f.read()
                with open(os.path.join(self.resources_path, "packages.txt"), "r") as f:
                    packages = f.read()
            except Exception:
                # Log warning here in real app
                pass
        
        return PromptManager.get_system_prompt(mode, schema, packages, examples)

    async def generate_response(self, request: ChatRequest):
        # 1. Security Check
        last_message = request.messages[-1].content
        validate_prompt(last_message)
        
        # 2. Context Loading
        system_context = self._load_context(request.mode)
        
        # 3. Call LLM (Stream)
        async for chunk in self.llm_client.chat_stream(request.messages, system_context):
            yield chunk

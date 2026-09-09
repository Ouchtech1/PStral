"""The two constrained demo journeys: sourced answers and closed SQL templates."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator
from typing import Any

from pydantic import ValidationError

from app.core.config import settings
from app.core.prompts import document_prompt, sql_selection_prompt
from app.domain.models.chat_models import ChatRequest
from app.infrastructure.llm.ollama_client import LLMError, LLMUnavailable, OllamaClient
from app.infrastructure.rag.document_rag import DocumentIndexError, DocumentRAG
from app.infrastructure.sql.sql_catalog import SQLCatalog, SQLCatalogError, SQLDecision


SQL_SELECTION_SCHEMA = {
    "type": "object",
    "properties": {
        "status": {"type": "string", "enum": ["sql", "clarification", "unsupported"]},
        "template_id": {"type": ["string", "null"]},
        "parameters": {"type": "object"},
        "question": {"type": ["string", "null"]},
    },
    "required": ["status", "template_id", "parameters", "question"],
    "additionalProperties": False,
}


class ChatBusyError(RuntimeError):
    pass


class ChatService:
    def __init__(self, rag: DocumentRAG, catalog: SQLCatalog, llm_client: OllamaClient) -> None:
        self.rag = rag
        self.catalog = catalog
        self.llm_client = llm_client
        self._generation_slot = asyncio.Semaphore(1)

    async def try_acquire(self) -> None:
        if self._generation_slot.locked():
            raise ChatBusyError("Une demande est déjà en cours. Réessayez dans quelques instants.")
        await self._generation_slot.acquire()

    def release(self) -> None:
        self._generation_slot.release()

    @staticmethod
    def _history(request: ChatRequest, reserved_chars: int) -> list[dict[str, str]]:
        """Keep complete recent messages within a conservative character budget."""
        latest = request.messages[-1]
        budget = max(0, (settings.MODEL_CONTEXT_TOKENS - settings.CHAT_OUTPUT_TOKENS) * 3 - reserved_chars)
        kept: list[dict[str, str]] = [{"role": latest.role, "content": latest.content}]
        remaining = budget - len(latest.content)
        for message in reversed(request.messages[:-1]):
            if len(message.content) > remaining:
                break
            kept.append({"role": message.role, "content": message.content})
            remaining -= len(message.content)
        return list(reversed(kept))

    async def generate(self, request: ChatRequest) -> AsyncGenerator[dict[str, Any], None]:
        if request.mode == "sql":
            async for event in self._generate_sql(request):
                yield event
            return
        async for event in self._generate_document_answer(request):
            yield event

    async def _generate_document_answer(self, request: ChatRequest) -> AsyncGenerator[dict[str, Any], None]:
        question = request.messages[-1].content
        yield {"type": "status", "message": "Recherche dans les documents internes…"}
        try:
            sources = self.rag.search(question, limit=2)
        except DocumentIndexError:
            yield {"type": "error", "message": "L'index documentaire local est indisponible."}
            yield {"type": "done", "success": False, "corpus_version": self.rag.corpus_version}
            return
        if not sources:
            yield {
                "type": "token",
                "content": "Je ne trouve pas cette information dans les documents disponibles.",
            }
            yield {"type": "done", "success": True, "corpus_version": self.rag.corpus_version}
            return

        source_payload = self.rag.source_payload(sources)
        yield {"type": "sources", "sources": source_payload, "corpus_version": self.rag.corpus_version}
        context = self.rag.prompt_context(sources)
        system_prompt = document_prompt(context)
        messages = self._history(request, reserved_chars=len(system_prompt) + len(context))

        emitted = False
        try:
            async with asyncio.timeout(settings.CHAT_TIMEOUT_SECONDS):
                async for chunk in self.llm_client.chat_stream(system_prompt, messages):
                    if chunk.content:
                        emitted = True
                        yield {"type": "token", "content": chunk.content}
                    if chunk.done:
                        if chunk.done_reason == "length":
                            yield {
                                "type": "error",
                                "message": "La synthèse a été tronquée ; consultez les extraits sources affichés.",
                            }
                            yield {"type": "done", "success": False, "corpus_version": self.rag.corpus_version}
                        elif not emitted:
                            yield {"type": "error", "message": "Le moteur local n'a produit aucune réponse."}
                            yield {"type": "done", "success": False, "corpus_version": self.rag.corpus_version}
                        else:
                            yield {"type": "done", "success": True, "corpus_version": self.rag.corpus_version}
                        return
            yield {"type": "error", "message": "Le moteur local a interrompu le flux sans confirmation."}
            yield {"type": "done", "success": False, "corpus_version": self.rag.corpus_version}
        except TimeoutError:
            yield {"type": "error", "message": "La génération locale a dépassé le délai autorisé."}
            yield {"type": "done", "success": False, "corpus_version": self.rag.corpus_version}
        except (LLMUnavailable, LLMError) as exc:
            yield {"type": "error", "message": str(exc)}
            yield {"type": "done", "success": False, "corpus_version": self.rag.corpus_version}

    async def _generate_sql(self, request: ChatRequest) -> AsyncGenerator[dict[str, Any], None]:
        question = request.messages[-1].content
        candidates = self.catalog.candidate_payload(question)
        if not candidates:
            yield {
                "type": "unsupported",
                "message": "Cette demande n'est pas couverte par le catalogue SQL de démonstration.",
            }
            yield {"type": "done", "success": True, "catalog_version": self.catalog.version}
            return

        yield {"type": "status", "message": "Sélection d'un modèle SQL autorisé…"}
        try:
            async with asyncio.timeout(settings.CHAT_TIMEOUT_SECONDS):
                raw_decision = await self.llm_client.chat_json(
                    sql_selection_prompt(candidates), question, SQL_SELECTION_SCHEMA
                )
            decision = SQLDecision.model_validate(raw_decision)
        except TimeoutError:
            yield {"type": "error", "message": "La sélection SQL a dépassé le délai autorisé."}
            yield {"type": "done", "success": False, "catalog_version": self.catalog.version}
            return
        except (LLMUnavailable, LLMError) as exc:
            yield {"type": "error", "message": str(exc)}
            yield {"type": "done", "success": False, "catalog_version": self.catalog.version}
            return
        except ValidationError:
            yield {"type": "clarification", "message": "Pouvez-vous reformuler votre demande SQL avec le critère manquant ?"}
            yield {"type": "done", "success": True, "catalog_version": self.catalog.version}
            return

        allowed_ids = {candidate["id"] for candidate in candidates}
        if decision.status == "unsupported" or not decision.template_id:
            yield {
                "type": "unsupported",
                "message": "Cette demande n'est pas couverte par le catalogue SQL de démonstration.",
            }
            yield {"type": "done", "success": True, "catalog_version": self.catalog.version}
            return
        if decision.template_id not in allowed_ids:
            yield {"type": "error", "message": "La sélection SQL du moteur n'est pas autorisée."}
            yield {"type": "done", "success": False, "catalog_version": self.catalog.version}
            return
        if decision.status == "clarification":
            yield {
                "type": "clarification",
                "message": decision.question or self.catalog.clarification_for(decision.template_id, decision.parameters)
                or "Pouvez-vous préciser le critère manquant ?",
            }
            yield {"type": "done", "success": True, "catalog_version": self.catalog.version}
            return
        try:
            clarification = self.catalog.clarification_for(decision.template_id, decision.parameters)
            if clarification:
                yield {"type": "clarification", "message": clarification}
                yield {"type": "done", "success": True, "catalog_version": self.catalog.version}
                return
            sql = self.catalog.render(decision.template_id, decision.parameters)
        except SQLCatalogError as exc:
            yield {"type": "error", "message": str(exc)}
            yield {"type": "done", "success": False, "catalog_version": self.catalog.version}
            return
        yield {"type": "sql", "content": sql, "template_id": decision.template_id}
        yield {"type": "done", "success": True, "catalog_version": self.catalog.version}

from __future__ import annotations

import asyncio

import pytest

from app.core.config import settings
from app.domain.models.chat_models import ChatRequest
from app.domain.services.chat_service import ChatBusyError, ChatService
from app.infrastructure.rag.document_rag import DocumentRAG
from app.infrastructure.sql.sql_catalog import SQLCatalog, SQLCatalogError


def test_document_index_is_local_and_returns_sources(tmp_path):
    index = DocumentRAG(settings.DOCUMENTS_DIR, tmp_path / "documents.db")
    index.initialize()

    sources = index.search("Que faire pour une demande de contrat ?")
    assert sources
    assert sources[0].source_id.startswith("DEMO-GUIDE-001:")
    assert "synthétique" in sources[0].title.lower()
    assert "[S1]" in index.prompt_context(sources)


def test_sql_catalog_only_renders_reviewed_read_queries():
    catalog = SQLCatalog.from_path(settings.SQL_CATALOG_PATH)
    assert catalog.candidate_payload("liste les contrats actifs")[0]["id"] == "active_contracts"

    query = catalog.render("surrenders_by_status", {"status": "en_attente"})
    assert "SELECT" in query
    assert "'EN_ATTENTE'" in query
    assert query.endswith(";")

    with pytest.raises(SQLCatalogError):
        catalog.render("surrenders_by_status", {"status": "DROP TABLE DEMO_RACHATS"})

    with pytest.raises(SQLCatalogError):
        catalog.render("encours_at_date", {"as_of_date": "31/01/2026"})

    with pytest.raises(SQLCatalogError):
        catalog.render("payments_in_period", {"start_date": "2026-04-01", "end_date": "2026-01-01"})


def test_chat_request_forbids_unbounded_or_assistant_ended_history():
    with pytest.raises(ValueError):
        ChatRequest(messages=[{"role": "assistant", "content": "fin"}])
    with pytest.raises(ValueError):
        ChatRequest(messages=[{"role": "user", "content": "x" * 2001}])


class FakeLLM:
    async def chat_json(self, system_prompt, user_message, response_format):
        return {
            "status": "sql",
            "template_id": "encours_at_date",
            "parameters": {"as_of_date": "2026-06-30"},
            "question": None,
        }


def test_sql_chat_path_emits_catalog_sql_without_execution():
    catalog = SQLCatalog.from_path(settings.SQL_CATALOG_PATH)
    service = ChatService(object(), catalog, FakeLLM())
    request = ChatRequest(mode="sql", messages=[{"role": "user", "content": "Donne l'encours au 2026-06-30"}])

    async def collect():
        return [event async for event in service.generate(request)]

    events = asyncio.run(collect())
    sql_events = [event for event in events if event["type"] == "sql"]
    assert len(sql_events) == 1
    assert "DATE '2026-06-30'" in sql_events[0]["content"]
    assert all(event["type"] != "execute" for event in events)


def test_chat_service_allows_only_one_generation_slot():
    service = ChatService(object(), SQLCatalog.from_path(settings.SQL_CATALOG_PATH), FakeLLM())

    async def check():
        await service.try_acquire()
        try:
            with pytest.raises(ChatBusyError):
                await service.try_acquire()
        finally:
            service.release()

    asyncio.run(check())

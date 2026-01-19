# RAG (Retrieval Augmented Generation) Module
# This module will handle context retrieval from various sources:
# - Oracle Database (schema, data context)
# - Documents (PDF, Word, internal wiki)

from .oracle_rag import OracleRAG
from .document_rag import DocumentRAG

__all__ = ['OracleRAG', 'DocumentRAG']


"""Retrieval components enabled by the isolated demonstration profile."""

# Keep the Oracle proof-of-concept module out of the import path. Importing it
# creates a client at module load time and would require production-only Oracle
# settings even though the demo never connects to that database.
from .document_rag import DocumentRAG

__all__ = ["DocumentRAG"]

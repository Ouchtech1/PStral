"""
Document RAG (Retrieval Augmented Generation) Module

This module handles context retrieval from internal documents:
- PDF documents
- Word documents
- Internal wiki pages
- Text files

Future enhancements:
- Vector embeddings for semantic search
- Document chunking and indexing
- Support for more document formats
"""

import logging
import os
from typing import Optional, List, Dict, Any
from pathlib import Path

logger = logging.getLogger("document_rag")


class DocumentRAG:
    """
    Retrieval Augmented Generation for document context.
    
    This class provides methods to retrieve relevant document context
    for enhancing LLM prompts with internal documentation.
    """
    
    def __init__(self, documents_path: str = "app/resources/documents"):
        self.documents_path = Path(documents_path)
        self.documents_cache: Dict[str, str] = {}
        self.index: List[Dict[str, Any]] = []
    
    async def initialize(self):
        """
        Initialize the document RAG system.
        Loads and indexes available documents.
        """
        if not self.documents_path.exists():
            self.documents_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created documents directory: {self.documents_path}")
        
        await self._build_index()
    
    async def _build_index(self):
        """
        Build an index of available documents.
        """
        self.index = []
        
        if not self.documents_path.exists():
            return
        
        for file_path in self.documents_path.glob("**/*"):
            if file_path.is_file() and file_path.suffix in ['.txt', '.md', '.sql']:
                try:
                    content = file_path.read_text(encoding='utf-8')
                    doc_entry = {
                        'path': str(file_path),
                        'name': file_path.name,
                        'type': file_path.suffix,
                        'size': len(content),
                        'preview': content[:200] if content else ""
                    }
                    self.index.append(doc_entry)
                    self.documents_cache[str(file_path)] = content
                except Exception as e:
                    logger.warning(f"Failed to index {file_path}: {e}")
        
        logger.info(f"Indexed {len(self.index)} documents")
    
    async def search_documents(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for relevant documents based on query.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching document entries
        """
        # TODO: Implement semantic search with embeddings
        # For now, simple keyword matching
        results = []
        query_lower = query.lower()
        
        for doc in self.index:
            content = self.documents_cache.get(doc['path'], "").lower()
            if query_lower in content or query_lower in doc['name'].lower():
                results.append(doc)
                if len(results) >= limit:
                    break
        
        return results
    
    async def get_document_content(self, path: str) -> Optional[str]:
        """
        Get the full content of a specific document.
        
        Args:
            path: Path to the document
            
        Returns:
            Document content or None if not found
        """
        return self.documents_cache.get(path)
    
    async def add_document(self, name: str, content: str, doc_type: str = ".txt") -> bool:
        """
        Add a new document to the RAG system.
        
        Args:
            name: Document name
            content: Document content
            doc_type: Document type/extension
            
        Returns:
            True if successful, False otherwise
        """
        try:
            file_path = self.documents_path / f"{name}{doc_type}"
            file_path.write_text(content, encoding='utf-8')
            
            # Update cache and index
            self.documents_cache[str(file_path)] = content
            self.index.append({
                'path': str(file_path),
                'name': file_path.name,
                'type': doc_type,
                'size': len(content),
                'preview': content[:200]
            })
            
            logger.info(f"Added document: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to add document {name}: {e}")
            return False
    
    def format_for_prompt(self, documents: List[Dict[str, Any]], max_chars: int = 4000) -> str:
        """
        Format retrieved documents for LLM prompt injection.
        
        Args:
            documents: List of document entries
            max_chars: Maximum characters to include
            
        Returns:
            Formatted context string
        """
        context_parts = ["# RELEVANT DOCUMENTATION:"]
        total_chars = 0
        
        for doc in documents:
            content = self.documents_cache.get(doc['path'], "")
            if total_chars + len(content) > max_chars:
                # Truncate to fit
                remaining = max_chars - total_chars
                if remaining > 100:
                    content = content[:remaining] + "\n... (truncated)"
                else:
                    break
            
            context_parts.append(f"\n## {doc['name']}\n{content}")
            total_chars += len(content)
        
        return "\n".join(context_parts)


# Global instance for easy access
document_rag = DocumentRAG()


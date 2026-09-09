"""Build the local document index before starting the demo server."""

from app.core.config import settings
from app.infrastructure.rag.document_rag import DocumentRAG


def main() -> None:
    rag = DocumentRAG()
    rag.initialize()
    print(f"Index prêt : {rag.index_path} (corpus {rag.corpus_version})")


if __name__ == "__main__":
    main()

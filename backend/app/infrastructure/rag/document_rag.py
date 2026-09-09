"""Local, lexical document retrieval for the Pstral demonstration."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from pathlib import Path
import re
import sqlite3
import unicodedata
from typing import Iterable

from app.core.config import settings


class DocumentIndexError(RuntimeError):
    pass


@dataclass(frozen=True)
class Source:
    source_id: str
    title: str
    version: str
    date: str
    section: str
    excerpt: str


_TERM_RE = re.compile(r"[\wÀ-ÖØ-öø-ÿ-]{2,}", re.UNICODE)
_HEADING_RE = re.compile(r"^#{1,6}\s+(.+?)\s*$")
_SYNONYMS = {
    "rachat": ("retrait",),
    "retrait": ("rachat",),
    "versement": ("paiement",),
    "contrat": ("police",),
    "beneficiaire": ("bénéficiaire",),
}


def _normalise(value: str) -> str:
    return "".join(
        char for char in unicodedata.normalize("NFD", value.lower())
        if unicodedata.category(char) != "Mn"
    )


def _terms(query: str) -> list[str]:
    terms: list[str] = []
    for raw in _TERM_RE.findall(_normalise(query)):
        if raw not in terms:
            terms.append(raw)
        for synonym in _SYNONYMS.get(raw, ()):
            if synonym not in terms:
                terms.append(synonym)
    return terms[:12]


def _chunks(section: str, text: str, target_words: int = 160, overlap_words: int = 24) -> Iterable[str]:
    paragraphs = [paragraph.strip() for paragraph in re.split(r"\n\s*\n", text) if paragraph.strip()]
    current: list[str] = []
    count = 0
    for paragraph in paragraphs:
        words = paragraph.split()
        if current and count + len(words) > target_words:
            yield "\n\n".join(current)
            overlap = " ".join(" ".join(current).split()[-overlap_words:])
            current = [overlap] if overlap else []
            count = len(overlap.split())
        current.append(paragraph)
        count += len(words)
    if current:
        yield "\n\n".join(current)


def _sections(text: str) -> Iterable[tuple[str, str]]:
    title = "Contenu"
    lines: list[str] = []
    for line in text.splitlines():
        heading = _HEADING_RE.match(line)
        if heading:
            if lines:
                yield title, "\n".join(lines).strip()
            title, lines = heading.group(1), []
        else:
            lines.append(line)
    if lines:
        yield title, "\n".join(lines).strip()


class DocumentRAG:
    def __init__(self, documents_path: Path | None = None, index_path: Path | None = None) -> None:
        self.documents_path = documents_path or settings.DOCUMENTS_DIR
        self.index_path = index_path or settings.document_index_path
        self.corpus_version = "unknown"

    def initialize(self) -> None:
        manifest_path = self.documents_path / "manifest.json"
        if not manifest_path.is_file():
            raise DocumentIndexError(f"Manifest documentaire absent : {manifest_path}")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.corpus_version = str(manifest.get("corpus_version", "unknown"))
        documents = manifest.get("documents")
        if not isinstance(documents, list) or not documents:
            raise DocumentIndexError("Le manifest doit contenir au moins un document.")

        fingerprint = self._fingerprint(manifest_path, documents)
        if self._is_current(fingerprint):
            return
        self._rebuild(documents, fingerprint)

    def _fingerprint(self, manifest_path: Path, documents: list[dict]) -> str:
        digest = sha256(manifest_path.read_bytes())
        for document in documents:
            relative = document.get("file")
            if not isinstance(relative, str):
                raise DocumentIndexError("Chaque document doit définir son fichier.")
            path = (self.documents_path / relative).resolve()
            if self.documents_path.resolve() not in path.parents or not path.is_file():
                raise DocumentIndexError(f"Document invalide ou absent : {relative}")
            digest.update(path.read_bytes())
        return digest.hexdigest()

    def _is_current(self, fingerprint: str) -> bool:
        if not self.index_path.is_file():
            return False
        try:
            with sqlite3.connect(self.index_path) as conn:
                row = conn.execute("SELECT value FROM metadata WHERE key = 'fingerprint'").fetchone()
            return bool(row and row[0] == fingerprint)
        except sqlite3.Error:
            return False

    def _rebuild(self, documents: list[dict], fingerprint: str) -> None:
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.index_path.with_suffix(".tmp")
        if temporary.exists():
            temporary.unlink()
        try:
            with sqlite3.connect(temporary) as conn:
                conn.execute("CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
                conn.execute(
                    """
                    CREATE VIRTUAL TABLE document_chunks USING fts5(
                        chunk_id UNINDEXED, source_id UNINDEXED, version UNINDEXED, date UNINDEXED,
                        title, section, content, tokenize = 'unicode61 remove_diacritics 2'
                    )
                    """
                )
                chunk_number = 0
                for document in documents:
                    required = ("id", "title", "version", "date", "file")
                    if any(not isinstance(document.get(field), str) or not document[field].strip() for field in required):
                        raise DocumentIndexError("Métadonnées documentaires incomplètes.")
                    text = (self.documents_path / document["file"]).read_text(encoding="utf-8")
                    for section, section_text in _sections(text):
                        for part in _chunks(section, section_text):
                            if not part:
                                continue
                            chunk_number += 1
                            conn.execute(
                                """
                                INSERT INTO document_chunks
                                (chunk_id, source_id, version, date, title, section, content)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                                """,
                                (
                                    f"{document['id']}:{chunk_number}",
                                    document["id"],
                                    document["version"],
                                    document["date"],
                                    document["title"],
                                    section,
                                    part,
                                ),
                            )
                if chunk_number == 0:
                    raise DocumentIndexError("Le corpus ne contient aucun extrait indexable.")
                conn.executemany(
                    "INSERT INTO metadata (key, value) VALUES (?, ?)",
                    [("fingerprint", fingerprint), ("corpus_version", self.corpus_version)],
                )
            temporary.replace(self.index_path)
        except Exception:
            if temporary.exists():
                temporary.unlink()
            raise

    def search(self, query: str, limit: int = 3) -> list[Source]:
        terms = _terms(query)
        if not terms:
            return []
        expression = " OR ".join(f'"{term.replace(chr(34), "")}"' for term in terms)
        try:
            with sqlite3.connect(self.index_path) as conn:
                rows = conn.execute(
                    """
                    SELECT chunk_id, title, version, date, section, content, bm25(document_chunks) AS score
                    FROM document_chunks
                    WHERE document_chunks MATCH ?
                    ORDER BY score
                    LIMIT ?
                    """,
                    (expression, max(1, min(limit, 3))),
                ).fetchall()
        except sqlite3.Error as exc:
            raise DocumentIndexError("Index documentaire indisponible.") from exc
        return [
            Source(
                source_id=row[0], title=row[1], version=row[2], date=row[3], section=row[4],
                excerpt=row[5][:700] + ("…" if len(row[5]) > 700 else ""),
            )
            for row in rows
        ]

    @staticmethod
    def source_payload(sources: list[Source]) -> list[dict]:
        return [asdict(source) for source in sources]

    @staticmethod
    def prompt_context(sources: list[Source]) -> str:
        return "\n\n".join(
            f"[S{index}] {source.title} — {source.section} ({source.version}, {source.date})\n{source.excerpt}"
            for index, source in enumerate(sources, start=1)
        )

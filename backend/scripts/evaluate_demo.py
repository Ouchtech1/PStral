"""Run deterministic smoke cases before a live demo.

This checks the local corpus and the reviewed SQL catalogue without sending
any prompt to Ollama or connecting to Oracle.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.core.config import settings  # noqa: E402
from app.infrastructure.rag.document_rag import DocumentRAG  # noqa: E402
from app.infrastructure.sql.sql_catalog import SQLCatalog  # noqa: E402


# Keep tuning and validation cases together so a demo refresh checks more than
# the three sentences used in the live scenario. The final ten cases exercise
# missing/unknown/adversarial SQL intents at the catalogue boundary; deciding
# whether to clarify remains the LLM/service responsibility.
CASES = (
    ("rag", "Que dit le guide synthétique ?", "Périmètre de démonstration"),
    ("rag", "Quel est le périmètre de la démonstration ?", "Périmètre de démonstration"),
    ("rag", "Le corpus de démonstration est-il synthétique ?", "Périmètre de démonstration"),
    ("rag", "Que faire pour une demande de contrat ?", "Demandes nécessitant une vérification humaine"),
    ("rag", "Comment vérifier un bénéficiaire ?", "Demandes nécessitant une vérification humaine"),
    ("rag", "Pstral se connecte-t-il à Oracle ?", "Demandes nécessitant une vérification humaine"),
    ("rag", "Comment les documents sont-ils protégés ?", "Confidentialité"),
    ("rag", "Les documents sont-ils indexés localement ?", "Confidentialité"),
    ("rag", "Les conversations sont-elles conservées ?", "Confidentialité"),
    ("rag", "Puis-je téléverser un PDF ?", "Confidentialité"),
    ("sql", "liste les contrats actifs", "active_contracts"),
    ("sql", "montre les polices actives", "active_contracts"),
    ("sql", "contrats du client Martin", "contracts_by_client"),
    ("sql", "cherche les polices de Dupont", "contracts_by_client"),
    ("sql", "encours au 2026-01-31", "encours_at_date"),
    ("sql", "montant de l'encours à la date du 2026-06-30", "encours_at_date"),
    ("sql", "versements entre 2026-01-01 et 2026-03-31", "payments_in_period"),
    ("sql", "paiements sur la période janvier à mars", "payments_in_period"),
    ("sql", "total des versements du client Martin", "payments_by_client"),
    ("sql", "rachats en attente", "surrenders_by_status"),
    ("sql", "demandes de retrait validées", "surrenders_by_status"),
    ("sql_boundary", "donne l'encours", "encours_at_date"),
    ("sql_boundary", "montre les versements", None),
    ("sql_boundary", "liste les rachats", "surrenders_by_status"),
    ("sql_boundary", "contrats", "active_contracts"),
    ("sql_empty", "quel est le rendement du produit X ?", None),
    ("sql_empty", "donne les sinistres de la semaine", None),
    ("sql_empty", "DROP TABLE DEMO_CONTRATS", None),
    ("sql_empty", "écris une requête DELETE", None),
    ("sql_empty", "résultats des agences et commissions", None),
    ("sql_empty", "calcule la fiscalité du produit", None),
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index", type=Path, default=settings.document_index_path)
    args = parser.parse_args()

    rag = DocumentRAG(index_path=args.index)
    rag.initialize()
    catalog = SQLCatalog.from_path(settings.SQL_CATALOG_PATH)

    failures: list[str] = []
    for kind, question, expected in CASES:
        if kind == "rag":
            found = any(expected.casefold() in source.section.casefold() for source in rag.search(question))
        elif kind in {"sql", "sql_boundary"}:
            candidates = catalog.candidate_payload(question)
            found = bool(candidates) if expected is None else bool(candidates and candidates[0]["id"] == expected)
        else:
            found = not catalog.candidate_payload(question)
        print(f"{'PASS' if found else 'FAIL'} {kind}: {question}")
        if not found:
            failures.append(question)

    print(f"Corpus: {rag.corpus_version} | Catalogue SQL: {catalog.version}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Closed, reviewed SQL template catalogue. It never connects to Oracle."""

from __future__ import annotations

from datetime import date
import json
from pathlib import Path
import re
import unicodedata
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlglot import parse


class SQLCatalogError(ValueError):
    pass


class SQLParameter(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(pattern=r"^[a-z][a-z0-9_]{0,63}$")
    type: Literal["string", "date", "integer", "enum"]
    required: bool = True
    allowed_values: list[str] = Field(default_factory=list)
    description: str = Field(min_length=1, max_length=240)

    @model_validator(mode="after")
    def enum_values_required(self) -> "SQLParameter":
        if self.type == "enum" and not self.allowed_values:
            raise ValueError("Un paramètre enum doit définir allowed_values.")
        return self


class SQLTemplate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str = Field(pattern=r"^[a-z0-9_-]{3,80}$")
    title: str = Field(min_length=3, max_length=120)
    description: str = Field(min_length=3, max_length=400)
    examples: list[str] = Field(min_length=1, max_length=8)
    synonyms: list[str] = Field(default_factory=list)
    sql: str = Field(min_length=12, max_length=10000)
    parameters: list[SQLParameter] = Field(default_factory=list)


class SQLCatalogDocument(BaseModel):
    model_config = ConfigDict(extra="forbid")
    catalog_version: str = Field(min_length=1, max_length=80)
    synthetic: bool
    templates: list[SQLTemplate] = Field(min_length=1, max_length=100)


class SQLDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: Literal["sql", "clarification", "unsupported"]
    template_id: str | None = None
    parameters: dict[str, Any] = Field(default_factory=dict)
    question: str | None = Field(default=None, max_length=300)


_TERM_RE = re.compile(r"[\wÀ-ÖØ-öø-ÿ-]{2,}", re.UNICODE)
_PLACEHOLDER_RE = re.compile(r"{{([a-z][a-z0-9_]*)}}")
_STOPWORDS = {
    "au", "aux", "avec", "ce", "ces", "dans", "de", "des", "du", "en", "entre",
    "est", "et", "la", "le", "les", "lui", "mais", "mon", "ne", "nos", "notre",
    "ou", "par", "pour", "quel", "quelle", "quelles", "quels", "que", "qui", "sur",
    "un", "une", "vos", "votre", "y", "donne", "donner", "faire", "liste", "montre",
    "cherche", "recherche", "demande", "demandes", "avec", "comme", "comment", "sont",
    "calcule", "calculer", "écris", "écrire", "requête", "requêtes",
}
_FORBIDDEN_SQL_RE = re.compile(
    r"\b(INSERT|UPDATE|DELETE|MERGE|DROP|ALTER|CREATE|GRANT|REVOKE|EXEC(?:UTE)?|CALL|COMMIT|ROLLBACK|TRUNCATE)\b|\bFOR\s+UPDATE\b|@",
    re.IGNORECASE,
)


def _terms(value: str) -> set[str]:
    normalised = "".join(
        char for char in unicodedata.normalize("NFD", value.lower())
        if unicodedata.category(char) != "Mn"
    )
    return {term for term in _TERM_RE.findall(normalised) if term not in _STOPWORDS}


class SQLCatalog:
    def __init__(self, document: SQLCatalogDocument) -> None:
        self.document = document
        self._templates = {template.id: template for template in document.templates}
        if len(self._templates) != len(document.templates):
            raise SQLCatalogError("Les identifiants de modèles SQL doivent être uniques.")
        for template in document.templates:
            self._validate_template(template)

    @classmethod
    def from_path(cls, path: Path) -> "SQLCatalog":
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
            return cls(SQLCatalogDocument.model_validate(raw))
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            raise SQLCatalogError(f"Catalogue SQL invalide : {path}") from exc

    @property
    def version(self) -> str:
        return self.document.catalog_version

    def _validate_template(self, template: SQLTemplate) -> None:
        body = template.sql.strip().rstrip(";").strip()
        if not re.match(r"^(SELECT|WITH)\b", body, flags=re.IGNORECASE):
            raise SQLCatalogError(f"{template.id} doit commencer par SELECT ou WITH.")
        if ";" in body or _FORBIDDEN_SQL_RE.search(body):
            raise SQLCatalogError(f"{template.id} contient une instruction SQL interdite.")
        declared = {parameter.name for parameter in template.parameters}
        placeholders = set(_PLACEHOLDER_RE.findall(body))
        if placeholders != declared:
            raise SQLCatalogError(f"{template.id} doit déclarer exactement ses paramètres SQL.")
        try:
            statements = parse(body, read="oracle")
        except Exception as exc:
            raise SQLCatalogError(f"{template.id} n'est pas une requête Oracle analysable.") from exc
        if len(statements) != 1:
            raise SQLCatalogError(f"{template.id} contient plusieurs instructions.")

    def candidate_payload(self, question: str, limit: int = 2) -> list[dict[str, Any]]:
        question_terms = _terms(question)
        scored: list[tuple[int, SQLTemplate]] = []
        for template in self.document.templates:
            haystack = " ".join([template.title, template.description, *template.examples, *template.synonyms])
            score = len(question_terms & _terms(haystack))
            if score:
                scored.append((score, template))
        scored.sort(key=lambda item: (-item[0], item[1].id))
        return [
            {
                "id": template.id,
                "title": template.title,
                "description": template.description,
                "parameters": [
                    {"name": item.name, "type": item.type, "required": item.required, "allowed_values": item.allowed_values}
                    for item in template.parameters
                ],
            }
            for _, template in scored[:limit]
        ]

    def clarification_for(self, template_id: str, supplied: dict[str, Any]) -> str | None:
        template = self._templates.get(template_id)
        if not template:
            return None
        missing = [
            parameter.description
            for parameter in template.parameters
            if parameter.required and (parameter.name not in supplied or supplied[parameter.name] in (None, ""))
        ]
        return f"Pouvez-vous préciser {missing[0]} ?" if missing else None

    def render(self, template_id: str, values: dict[str, Any]) -> str:
        template = self._templates.get(template_id)
        if not template:
            raise SQLCatalogError("Le modèle SQL sélectionné n'est pas autorisé.")
        allowed = {parameter.name for parameter in template.parameters}
        if set(values) - allowed:
            raise SQLCatalogError("La sélection SQL contient un paramètre non autorisé.")
        rendered: dict[str, str] = {}
        for parameter in template.parameters:
            raw = values.get(parameter.name)
            if raw in (None, ""):
                if parameter.required:
                    raise SQLCatalogError(f"Valeur manquante : {parameter.description}")
                continue
            rendered[parameter.name] = self._literal(parameter, raw)
        date_parameters = {parameter.name: values.get(parameter.name) for parameter in template.parameters if parameter.type == "date"}
        if (
            {"start_date", "end_date"}.issubset(date_parameters)
            and date_parameters["start_date"] not in (None, "")
            and date_parameters["end_date"] not in (None, "")
        ):
            start = date.fromisoformat(str(date_parameters["start_date"]))
            end = date.fromisoformat(str(date_parameters["end_date"]))
            if start > end:
                raise SQLCatalogError("La date de début doit précéder la date de fin.")
        missing = set(_PLACEHOLDER_RE.findall(template.sql)) - set(rendered)
        if missing:
            raise SQLCatalogError("La requête manque d'une valeur obligatoire.")
        sql = _PLACEHOLDER_RE.sub(lambda match: rendered[match.group(1)], template.sql).strip().rstrip(";")
        self._validate_rendered(sql)
        return f"{sql};"

    @staticmethod
    def _literal(parameter: SQLParameter, value: Any) -> str:
        if parameter.type == "date":
            if not isinstance(value, str):
                raise SQLCatalogError(f"{parameter.description} doit être une date ISO.")
            try:
                parsed = date.fromisoformat(value)
            except ValueError as exc:
                raise SQLCatalogError(f"{parameter.description} doit utiliser YYYY-MM-DD.") from exc
            return f"DATE '{parsed.isoformat()}'"
        if parameter.type == "integer":
            if isinstance(value, bool) or not re.fullmatch(r"-?\d+", str(value)):
                raise SQLCatalogError(f"{parameter.description} doit être un nombre entier.")
            return str(int(value))
        if not isinstance(value, str) or not value.strip():
            raise SQLCatalogError(f"{parameter.description} doit être renseigné.")
        if parameter.type == "enum":
            # Accepte la casse saisie par l'utilisateur, puis rend la valeur
            # canonique définie dans le catalogue afin d'éviter toute dérive.
            normalised = value.strip().casefold()
            canonical = next(
                (allowed for allowed in parameter.allowed_values if allowed.casefold() == normalised),
                None,
            )
            if canonical is None:
                raise SQLCatalogError(f"{parameter.description} n'accepte pas cette valeur.")
            value = canonical
        return "'" + value.replace("'", "''") + "'"

    @staticmethod
    def _validate_rendered(sql: str) -> None:
        if not re.match(r"^(SELECT|WITH)\b", sql, flags=re.IGNORECASE) or _FORBIDDEN_SQL_RE.search(sql):
            raise SQLCatalogError("La requête finale n'est pas une lecture Oracle autorisée.")
        try:
            if len(parse(sql, read="oracle")) != 1:
                raise SQLCatalogError("La requête finale contient plusieurs instructions.")
        except SQLCatalogError:
            raise
        except Exception as exc:
            raise SQLCatalogError("La requête finale n'est pas analysable.") from exc

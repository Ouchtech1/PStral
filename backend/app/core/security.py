import re
import logging
from typing import Tuple, Optional
from fastapi import HTTPException

# Configure structured logging
logger = logging.getLogger("security")

# Compile regexes once for performance
DANGEROUS_PATTERNS = [
    re.compile(r"\bDROP\b", re.IGNORECASE),
    re.compile(r"\bDELETE\b", re.IGNORECASE),
    re.compile(r"\bUPDATE\b", re.IGNORECASE),
    re.compile(r"\bTRUNCATE\b", re.IGNORECASE),
    re.compile(r"\bALTER\b", re.IGNORECASE),
    re.compile(r"\bGRANT\b", re.IGNORECASE),
    re.compile(r"\bREVOKE\b", re.IGNORECASE)
]

# SQL injection patterns
INJECTION_PATTERNS = [
    re.compile(r";\s*--", re.IGNORECASE),  # Comment after semicolon
    re.compile(r"'\s*OR\s+'1'\s*=\s*'1", re.IGNORECASE),  # Classic OR injection
    re.compile(r"UNION\s+ALL\s+SELECT", re.IGNORECASE),  # UNION injection
    re.compile(r"INTO\s+OUTFILE", re.IGNORECASE),  # File write
    re.compile(r"LOAD_FILE", re.IGNORECASE),  # File read
    re.compile(r"INFORMATION_SCHEMA", re.IGNORECASE),  # Schema enumeration
]


def validate_prompt(content: str):
    """
    Scans the prompt/content for dangerous SQL keywords using compiled regexes.
    Raises HTTPException if found and logs the incident.
    """
    for pattern in DANGEROUS_PATTERNS:
        match = pattern.search(content)
        if match:
            keyword = match.group(0).upper()
            logger.warning(f"SECURITY ALERT: Blocked restricted keyword '{keyword}' in user prompt. Content prefix: {content[:50]}...")
            raise HTTPException(
                status_code=400, 
                detail=f"Security Alert: Restricted keyword detected ({keyword}). This system is Read-Only."
            )
    return True


def filter_sql_prompt(query: str) -> Tuple[str, Optional[str]]:
    """
    Filter and sanitize SQL queries for execution.
    Returns: (filtered_query, reason_if_blocked)
    """
    # Check for dangerous patterns
    for pattern in DANGEROUS_PATTERNS:
        match = pattern.search(query)
        if match:
            keyword = match.group(0).upper()
            logger.warning(f"SQL FILTER: Blocked keyword '{keyword}' in query")
            return "", f"Mot-clé interdit: {keyword}"
    
    # Check for injection patterns
    for pattern in INJECTION_PATTERNS:
        if pattern.search(query):
            logger.warning(f"SQL FILTER: Potential injection detected in query")
            return "", "Tentative d'injection SQL détectée"
    
    # Remove multiple semicolons (prevent multiple statements)
    if query.count(';') > 1:
        logger.warning("SQL FILTER: Multiple statements detected")
        return "", "Les requêtes multiples ne sont pas autorisées"
    
    # Remove trailing semicolon for safety
    query = query.rstrip(';').strip()
    
    return query, None

import re
from typing import List


# Comprehensive list of SQL/GQL keywords that indicate mutating operations
MUTATING_KEYWORDS: List[str] = [
    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE",
    "CREATE", "GRANT", "REVOKE", "MERGE", "REPLACE", "UPSERT"
]


def is_mutating_query(query: str) -> bool:
    """Check for mutating SQL/GQL using tokenized keyword detection.
    
    Handles bypass attempts via:
    - Block comments (/* ... */)
    - Line comments (-- ...)
    - Tab/newline whitespace variations
    - Mixed-case keywords
    """
    # Remove block comments
    normalized = re.sub(r'/\*.*?\*/', ' ', query, flags=re.DOTALL)
    # Remove line comments
    normalized = re.sub(r'--.*?$', ' ', normalized, flags=re.MULTILINE)
    # Collapse all whitespace (tabs, newlines, multiple spaces) to single space
    normalized = re.sub(r'\s+', ' ', normalized).strip().upper()

    if not normalized:
        return False

    # Check if the statement starts with any mutating keyword
    first_word = normalized.split()[0] if normalized.split() else ""
    if first_word in MUTATING_KEYWORDS:
        return True

    # Also check for multi-statement injection via semicolons
    # e.g., "SELECT 1; DROP TABLE users"
    statements = [s.strip() for s in normalized.split(';') if s.strip()]
    for stmt in statements:
        stmt_first_word = stmt.split()[0] if stmt.split() else ""
        if stmt_first_word in MUTATING_KEYWORDS:
            return True

    return False

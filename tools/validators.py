import re
from core.exceptions import SQLValidationError


class SQLValidator:
    FORBIDDEN_KEYWORDS = {
        "DROP",
        "DELETE",
        "UPDATE",
        "INSERT",
        "ALTER",
        "TRUNCATE",
        "CREATE",
        "REPLACE",
        "GRANT",
        "REVOKE",
        "ATTACH",
        "DETACH",
        "COPY",
    }

    @classmethod
    def validate_readonly_sql(cls, sql: str) -> str:
        cleaned = sql.strip().rstrip(";")
        tokens = set(re.findall(r"\b[A-Z_]+\b", cleaned.upper()))
        illegal = tokens.intersection(cls.FORBIDDEN_KEYWORDS)
        if illegal:
            raise SQLValidationError(f"Unsafe SQL keywords detected: {illegal}")
        if not (cleaned.upper().startswith("SELECT") or cleaned.upper().startswith("WITH")):
            raise SQLValidationError("Only SELECT or WITH read-only queries are permitted.")
        return cleaned

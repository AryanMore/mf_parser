import re
from typing import List, Dict


class SQLExtractor:
    """
    Extract semantic information from EXEC SQL blocks.
    MVP v1:
    - operation detection
    - table extraction
    - join table extraction
    """

    TABLE_KEYWORDS = {"FROM", "JOIN", "UPDATE", "INTO"}

    def __init__(self):
        pass

    # -----------------------------------
    # Public entry
    # -----------------------------------
    def analyze(self, sql: str) -> Dict:
        sql_upper = sql.upper()

        return {
            "operation": self._extract_operation(sql_upper),
            "tables": self._extract_tables(sql_upper),
        }

    # -----------------------------------
    # Detect SQL operation
    # -----------------------------------
    def _extract_operation(self, sql: str):
        if "SELECT" in sql:
            return "SELECT"
        if "INSERT" in sql:
            return "INSERT"
        if "UPDATE" in sql:
            return "UPDATE"
        if "DELETE" in sql:
            return "DELETE"
        if "MERGE" in sql:
            return "MERGE"
        return None

    # -----------------------------------
    # Extract table names
    # -----------------------------------
    def _extract_tables(self, sql: str) -> List[str]:
        tables = []

        # normalize
        cleaned = re.sub(r"[(),;]", " ", sql)
        words = cleaned.split()

        for idx, word in enumerate(words):
            if word in self.TABLE_KEYWORDS:
                if idx + 1 < len(words):
                    table = words[idx + 1]

                    # Skip aliases or SQL keywords
                    if table not in {
                        "SELECT", "WHERE", "SET",
                        "VALUES", "ON", "AND"
                    }:
                        tables.append(table)

        return sorted(set(tables))
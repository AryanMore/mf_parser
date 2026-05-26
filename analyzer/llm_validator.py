import re
from models.schema import CobolProgram


class LLMValidator:
    """
    Validates LLM-generated documentation
    against parser-derived truth.

    Goal:
    reject unsupported factual claims.
    """

    def validate(
        self,
        text: str,
        program: CobolProgram
    ):
        result = {
            "valid": True,
            "issues": []
        }

        upper_text = text.upper()

        # -----------------------------------
        # Validate DB tables
        # -----------------------------------
        self._validate_sql_tables(
            upper_text,
            program,
            result
        )

        # -----------------------------------
        # Validate file names
        # -----------------------------------
        self._validate_files(
            upper_text,
            program,
            result
        )

        # -----------------------------------
        # Validate subprogram calls
        # -----------------------------------
        self._validate_calls(
            upper_text,
            program,
            result
        )

        # -----------------------------------
        # Validate copybooks
        # -----------------------------------
        self._validate_copybooks(
            upper_text,
            program,
            result
        )

        # -----------------------------------
        # Validate unsupported systems
        # -----------------------------------
        self._validate_forbidden_systems(
            upper_text,
            program,
            result
        )

        # -----------------------------------
        # Suspicious unsupported business claims
        # -----------------------------------
        self._validate_business_hallucinations(
            upper_text,
            result
        )

        return result

    # =====================================================
    # SQL tables
    # =====================================================
    def _validate_sql_tables(
        self,
        text,
        program,
        result
    ):
        known_tables = set()

        for sql in program.sql_blocks:
            for table in sql.tables:
                known_tables.add(
                    table.upper()
                )

        mentioned = self._extract_tokens(text)

        suspicious = []

        db_words = {
            "TABLE",
            "DATABASE",
            "DB2"
        }

        if any(
            word in text
            for word in db_words
        ):
            for token in mentioned:
                if (
                    token.endswith("TABLE")
                    or token in known_tables
                ):
                    continue

                # suspicious uppercase identifier
                if (
                    len(token) > 3
                    and token.isupper()
                    and token not in known_tables
                ):
                    suspicious.append(token)

        if suspicious and not known_tables:
            result["valid"] = False
            result["issues"].append(
                f"Unsupported DB references: {sorted(set(suspicious))}"
            )

    # =====================================================
    # Files
    # =====================================================
    def _validate_files(
        self,
        text,
        program,
        result
    ):
        known_files = {
            op.target.upper()
            for op in program.file_operations
        }

        for token in self._extract_tokens(text):
            if "FILE" in token:
                if token not in known_files:
                    result["issues"].append(
                        f"Unverified file reference: {token}"
                    )

    # =====================================================
    # Calls
    # =====================================================
    def _validate_calls(
        self,
        text,
        program,
        result
    ):
        known_calls = {
            c.upper()
            for c in program.calls
        }

        for token in self._extract_tokens(text):
            if token in known_calls:
                continue

            if token.startswith("CB") or token.startswith("COB"):
                result["issues"].append(
                    f"Unverified subprogram: {token}"
                )

    # =====================================================
    # Copybooks
    # =====================================================
    def _validate_copybooks(
        self,
        text,
        program,
        result
    ):
        known_copybooks = {
            c.upper()
            for c in program.copybooks
        }

        for token in self._extract_tokens(text):
            if token in known_copybooks:
                continue

            if token.startswith("CV") or token.startswith("CPY"):
                result["issues"].append(
                    f"Unverified copybook: {token}"
                )

    # =====================================================
    # Unsupported tech claims
    # =====================================================
    def _validate_forbidden_systems(
        self,
        text,
        program,
        result
    ):
        has_sql = len(program.sql_blocks) > 0

        if "DB2" in text and not has_sql:
            result["valid"] = False
            result["issues"].append(
                "DB2 mentioned but no SQL detected."
            )

        if "IMS" in text:
            result["issues"].append(
                "IMS claim not validated."
            )

        if "IDMS" in text:
            result["issues"].append(
                "IDMS claim not validated."
            )

    # =====================================================
    # Helpers
    # =====================================================
    def _extract_tokens(
        self,
        text: str
    ):
        return set(
            re.findall(
                r"\b[A-Z][A-Z0-9_-]{2,}\b",
                text
            )
        )
    
    # =====================================================
    # Business hallucination detection
    # =====================================================
    def _validate_business_hallucinations(
        self,
        text,
        result
    ):
        suspicious = [
            "BANKING SYSTEM",
            "CUSTOMER DATABASE",
            "PAYMENT ENGINE",
            "ERP SYSTEM",
            "ACCOUNTING PLATFORM",
            "CRM",
            "ORDER PIPELINE",
            "FINANCIAL ENGINE"
        ]

        for phrase in suspicious:
            if phrase in text:
                result["issues"].append(
                    f"Potential unsupported business inference: {phrase}"
                )
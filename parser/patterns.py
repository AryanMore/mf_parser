import re

# =========================================================
# METADATA
# =========================================================

PROGRAM_ID_PATTERN = re.compile(
    r"^\s*PROGRAM-ID\.\s+([A-Z0-9_-]+)\.?\s*$",
    re.IGNORECASE | re.MULTILINE
)

AUTHOR_PATTERN = re.compile(
    r"^\s*AUTHOR\.\s+(.+?)\.?\s*$",
    re.IGNORECASE | re.MULTILINE
)

DATE_WRITTEN_PATTERN = re.compile(
    r"^\s*DATE-WRITTEN\.\s+(.+?)\.?\s*$",
    re.IGNORECASE | re.MULTILINE
)


# =========================================================
# DIVISIONS
# =========================================================

DIVISION_PATTERN = re.compile(
    r"^\s*(IDENTIFICATION|ENVIRONMENT|DATA|PROCEDURE)\s+DIVISION\.\s*$",
    re.IGNORECASE | re.MULTILINE
)


# =========================================================
# SECTIONS
# COBOL SECTION labels
# Example:
# WORKING-STORAGE SECTION.
# FILE SECTION.
# INPUT-OUTPUT SECTION.
# =========================================================

SECTION_PATTERN = re.compile(
    r"^\s*([A-Z0-9-]+)\s+SECTION\.\s*$",
    re.IGNORECASE | re.MULTILINE
)


# =========================================================
# PARAGRAPHS
# Example:
# 1000-INIT.
# MAIN-PARA.
#
# Avoid matching:
# PROGRAM-ID.
# DIVISION.
# SECTION.
# =========================================================

PARAGRAPH_PATTERN = re.compile(
    r"^([A-Z0-9][A-Z0-9-]*)\.\s*$",
    re.IGNORECASE | re.MULTILINE
)


RESERVED_PARAGRAPH_WORDS = {
    # divisions / structure
    "PROGRAM-ID",
    "IDENTIFICATION",
    "ENVIRONMENT",
    "DATA",
    "PROCEDURE",
    "SECTION",
    "DIVISION",
    "AUTHOR",
    "DATE-WRITTEN",
    "FILE-CONTROL",
    "INPUT-OUTPUT",
    "WORKING-STORAGE",
    "FILE",

    # control keywords
    "END-IF",
    "END-PERFORM",
    "END-EVALUATE",
    "EXIT",
    "GOBACK",
    "STOP",
    "RUN",
    "ELSE",
    "WHEN",
    "IF",
    "PERFORM",
    "DISPLAY",
    "MOVE",
    "READ",
    "WRITE",
    "OPEN",
    "CLOSE",
    "CALL",
    "DELETE",
    "REWRITE",
}


# =========================================================
# VARIABLES (major fix)
#
# Supports:
# 01 WS-NAME PIC X(10).
# 05 AMT PIC S9(7)V99 COMP-3.
# 77 WS-COUNT PIC 9(4) VALUE 0.
# 05 ARR OCCURS 10 TIMES.
# 05 NEW REDEFINES OLD PIC X(10).
# =========================================================

VARIABLE_PATTERN = re.compile(
    r"""
    ^\s*
    (01|02|03|04|05|10|15|20|25|30|35|40|45|49|66|77|88)
    \s+
    ([A-Z0-9-]+)

    (?:\s+REDEFINES\s+([A-Z0-9-]+))?

    (?:\s+PIC\s+([A-Z0-9SVX\(\)\.\-]+))?

    (?:\s+OCCURS\s+([0-9]+(?:\s+TO\s+[0-9]+)?(?:\s+TIMES)?))?

    (?:\s+VALUE\s+(.+?))?

    (?:\s+(COMP|COMP-3|BINARY|PACKED-DECIMAL))?

    \.?\s*$
    """,
    re.IGNORECASE | re.MULTILINE | re.VERBOSE
)


# =========================================================
# COPY / CALL
# line-aware
# =========================================================

COPY_PATTERN = re.compile(
    r"^\s*COPY\s+([A-Z0-9_-]+)\.?\s*$",
    re.IGNORECASE | re.MULTILINE
)

CALL_PATTERN = re.compile(
    r"^\s*CALL\s+['\"]?([A-Z0-9_-]+)['\"]?",
    re.IGNORECASE | re.MULTILINE
)


# =========================================================
# FILE OPERATIONS
# Anchored to line starts to avoid STATUS false positives
# =========================================================

OPEN_PATTERN = re.compile(
    r"^\s*OPEN\s+(INPUT|OUTPUT|I-O|EXTEND)?\s+([A-Z0-9-]+)",
    re.IGNORECASE | re.MULTILINE
)

READ_PATTERN = re.compile(
    r"^\s*READ\s+([A-Z0-9-]+)",
    re.IGNORECASE | re.MULTILINE
)

WRITE_PATTERN = re.compile(
    r"^\s*WRITE\s+([A-Z0-9-]+)",
    re.IGNORECASE | re.MULTILINE
)

REWRITE_PATTERN = re.compile(
    r"^\s*REWRITE\s+([A-Z0-9-]+)",
    re.IGNORECASE | re.MULTILINE
)

CLOSE_PATTERN = re.compile(
    r"^\s*CLOSE\s+([A-Z0-9-]+)",
    re.IGNORECASE | re.MULTILINE
)

DELETE_PATTERN = re.compile(
    r"^\s*DELETE\s+([A-Z0-9-]+)",
    re.IGNORECASE | re.MULTILINE
)


# =========================================================
# SQL BLOCKS
# =========================================================

SQL_BLOCK_PATTERN = re.compile(
    r"EXEC\s+SQL(.*?)END-EXEC",
    re.IGNORECASE | re.DOTALL
)


# =========================================================
# FLOW (future)
# =========================================================

PERFORM_PATTERN = re.compile(
    r"^\s*PERFORM\s+([A-Z0-9-]+)",
    re.IGNORECASE | re.MULTILINE
)

IF_PATTERN = re.compile(
    r"\bIF\b",
    re.IGNORECASE
)

EVALUATE_PATTERN = re.compile(
    r"\bEVALUATE\b",
    re.IGNORECASE
)
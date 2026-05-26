from models.schema import (
    CobolProgram,
    ProgramMetadata,
    Variable,
    Section,
    Paragraph,
    FileOperation,
    SQLBlock,
)

from parser.preprocessor import CobolPreprocessor
from parser import patterns
from analyzer.sql_extractor import SQLExtractor


class CobolParser:
    """
    COBOL Parser MVP v1.1
    Improved accuracy for real enterprise COBOL.
    """

    def __init__(self):
        self.preprocessor = CobolPreprocessor()
        self.sql_extractor = SQLExtractor()

    # =====================================================
    # PUBLIC ENTRY
    # =====================================================
    def parse(self, raw_text: str) -> CobolProgram:
        text = self.preprocessor.preprocess(raw_text)

        program = CobolProgram()

        self._extract_metadata(text, program)
        self._extract_divisions(text, program)
        self._extract_sections(text, program)

        # variables before paragraphs
        self._extract_variables(text, program)

        self._extract_paragraphs(text, program)

        self._extract_copybooks(text, program)
        self._extract_calls(text, program)
        self._extract_file_operations(text, program)
        self._extract_sql_blocks(text, program)

        return program

    # =====================================================
    # METADATA
    # =====================================================
    def _extract_metadata(
        self,
        text: str,
        program: CobolProgram
    ):
        metadata = ProgramMetadata()

        match = patterns.PROGRAM_ID_PATTERN.search(text)
        if match:
            metadata.program_id = match.group(1).upper()

        match = patterns.AUTHOR_PATTERN.search(text)
        if match:
            metadata.author = match.group(1).strip()

        match = patterns.DATE_WRITTEN_PATTERN.search(text)
        if match:
            metadata.date_written = match.group(1).strip()

        program.metadata = metadata

    # =====================================================
    # DIVISIONS
    # =====================================================
    def _extract_divisions(
    self,
    text: str,
    program: CobolProgram
        ):
            """
            Preserve COBOL source order:
            IDENTIFICATION → ENVIRONMENT → DATA → PROCEDURE
            """

            seen = set()

            for match in patterns.DIVISION_PATTERN.finditer(text):
                name = (
                    match.group(1).upper()
                    + " DIVISION"
                )

                if name not in seen:
                    program.divisions.append(
                        name
                    )
                    seen.add(name)

    # =====================================================
    # SECTIONS
    # =====================================================
    def _extract_sections(
        self,
        text: str,
        program: CobolProgram
    ):
        seen = set()

        for match in patterns.SECTION_PATTERN.finditer(text):
            name = match.group(1).upper()

            if name not in seen:
                program.sections.append(
                    Section(name=name)
                )
                seen.add(name)

    # =====================================================
    # PARAGRAPHS
    # =====================================================
    def _extract_paragraphs(
        self,
        text: str,
        program: CobolProgram
    ):

        # -----------------------------------
        # Extract only PROCEDURE DIVISION
        # -----------------------------------
        procedure_start = text.upper().find(
            "PROCEDURE DIVISION."
        )

        if procedure_start == -1:
            return

        procedure_text = text[procedure_start:]

        section_names = {
            s.name.upper()
            for s in program.sections
        }

        variable_names = {
            v.name.upper()
            for v in program.variables
        }

        seen = set()

        for match in patterns.PARAGRAPH_PATTERN.finditer(
            procedure_text
        ):
            name = match.group(1).upper()

            # Skip reserved COBOL words
            if name in patterns.RESERVED_PARAGRAPH_WORDS:
                continue

            # Skip section labels
            if name in section_names:
                continue

            # Skip variable names
            if name in variable_names:
                continue

            # Most real COBOL paragraphs are numeric-prefixed
            # or hyphen-style labels.
            #
            # Examples:
            # 1000-INIT
            # MAIN-PARA
            # 9000-ABEND
            if "-" not in name:
                continue

            if name not in seen:
                program.paragraphs.append(
                    Paragraph(name=name)
                )
                seen.add(name)

    # =====================================================
    # VARIABLES
    # =====================================================
    def _extract_variables(
        self,
        text: str,
        program: CobolProgram
    ):
        seen = set()

        for match in patterns.VARIABLE_PATTERN.finditer(text):
            level = match.group(1)
            name = match.group(2).upper()
            redefines = match.group(3)
            pic = match.group(4)
            occurs = match.group(5)
            value = match.group(6)

            key = (level, name)

            if key in seen:
                continue

            # -------------------------------
            # Normalize fields
            # -------------------------------
            normalized_pic = None
            if pic:
                normalized_pic = (
                    pic.strip()
                    .rstrip(".")
                    .replace("  ", " ")
                )

            normalized_occurs = None
            if occurs:
                occurs_clean = (
                    occurs.strip()
                    .rstrip(".")
                    .replace("  ", " ")
                )

                if not occurs_clean.upper().startswith(
                    "OCCURS"
                ):
                    occurs_clean = (
                        f"OCCURS {occurs_clean}"
                    )

                normalized_occurs = (
                    occurs_clean
                )

            normalized_value = None
            if value:
                normalized_value = (
                    value.strip()
                    .rstrip(".")
                )

            normalized_redefines = None
            if redefines:
                normalized_redefines = (
                    redefines.strip()
                    .upper()
                    .rstrip(".")
                )

            # -------------------------------
            # Create variable
            # -------------------------------
            variable = Variable(
                level=level,
                name=name,
                pic=normalized_pic,
                value=normalized_value,
                occurs=normalized_occurs,
                redefines=normalized_redefines
            )

            program.variables.append(variable)
            seen.add(key)

    # =====================================================
    # COPYBOOKS
    # =====================================================
    def _extract_copybooks(
        self,
        text: str,
        program: CobolProgram
    ):
        copies = patterns.COPY_PATTERN.findall(text)

        program.copybooks = sorted(
            set(c.upper() for c in copies)
        )

    # =====================================================
    # CALLS
    # =====================================================
    def _extract_calls(
        self,
        text: str,
        program: CobolProgram
    ):
        calls = patterns.CALL_PATTERN.findall(text)

        program.calls = sorted(
            set(c.upper() for c in calls)
        )

    # =====================================================
    # FILE OPS
    # =====================================================
    def _extract_file_operations(
        self,
        text: str,
        program: CobolProgram
    ):
        seen = set()

        def add_op(op_type, target):
            key = (op_type, target)

            if key in seen:
                return

            program.file_operations.append(
                FileOperation(
                    operation=op_type,
                    target=target
                )
            )
            seen.add(key)

        # OPEN
        for match in patterns.OPEN_PATTERN.finditer(text):
            target = match.group(2).upper()
            add_op("OPEN", target)

        # READ
        for match in patterns.READ_PATTERN.finditer(text):
            target = match.group(1).upper()
            add_op("READ", target)

        # WRITE
        for match in patterns.WRITE_PATTERN.finditer(text):
            target = match.group(1).upper()
            add_op("WRITE", target)

        # REWRITE
        for match in patterns.REWRITE_PATTERN.finditer(text):
            target = match.group(1).upper()
            add_op("REWRITE", target)

        # CLOSE
        for match in patterns.CLOSE_PATTERN.finditer(text):
            target = match.group(1).upper()
            add_op("CLOSE", target)

        # DELETE
        for match in patterns.DELETE_PATTERN.finditer(text):
            target = match.group(1).upper()
            add_op("DELETE", target)

    # =====================================================
    # SQL
    # =====================================================
    def _extract_sql_blocks(
        self,
        text: str,
        program: CobolProgram
    ):
        for match in patterns.SQL_BLOCK_PATTERN.finditer(text):
            raw_sql = match.group(1).strip()

            sql_data = self.sql_extractor.analyze(
                raw_sql
            )

            sql_block = SQLBlock(
                raw_sql=raw_sql,
                operation=sql_data["operation"],
                tables=sql_data["tables"]
            )

            program.sql_blocks.append(sql_block)
from models.schema import CobolProgram


class SemanticEngine:
    """
    Deterministic comprehension engine.
    Converts parsed COBOL facts into
    semantic TOC sections.
    """

    # =====================================================
    # MASTER SUMMARY
    # =====================================================
    def generate_summary(
        self,
        program: CobolProgram
    ) -> str:
        return self.generate_program_overview(
            program
        )

    # =====================================================
    # 1.1 Program Overview
    # =====================================================
    def generate_program_overview(
        self,
        program: CobolProgram
    ) -> str:
        file_ops = len(
            program.file_operations
        )
        calls = len(program.calls)
        copybooks = len(
            program.copybooks
        )
        variables = len(
            program.variables
        )
        sections = len(
            program.sections
        )
        paragraphs = len(
            program.paragraphs
        )

        return (
            f"This COBOL program "
            f"'{program.metadata.program_id}' "
            f"contains {sections} major "
            f"sections, {paragraphs} "
            f"procedural paragraphs, "
            f"{variables} declared "
            f"variables, {file_ops} "
            f"file operations, "
            f"{calls} dependent "
            f"subprogram calls, and "
            f"{copybooks} copybook "
            f"references. The program "
            f"appears to follow a "
            f"structured batch-style "
            f"processing design."
        )

    # =====================================================
    # 1.2 Objectives
    # =====================================================
    def generate_objectives_summary(
        self,
        program: CobolProgram
    ) -> str:
        operations = {
            op.operation.upper()
            for op in program.file_operations
        }

        objectives = []

        if "READ" in operations:
            objectives.append(
                "read structured input records"
            )

        if "WRITE" in operations:
            objectives.append(
                "generate formatted output records"
            )

        if "REWRITE" in operations:
            objectives.append(
                "update existing file records"
            )

        if program.calls:
            objectives.append(
                "invoke dependent subprogram logic"
            )

        if not objectives:
            objectives.append(
                "execute structured procedural logic"
            )

        return (
            "The primary technical "
            "objective of this "
            "program is to "
            + ", ".join(objectives)
            + "."
        )

    # =====================================================
    # 1.3 Scope
    # =====================================================
    def generate_scope_summary(
        self,
        program: CobolProgram
    ) -> str:
        return (
            f"The scope of this "
            f"program includes "
            f"{len(program.sections)} "
            f"defined sections, "
            f"{len(program.paragraphs)} "
            f"procedural paragraphs, "
            f"{len(program.file_operations)} "
            f"file operations, "
            f"{len(program.calls)} "
            f"subprogram dependencies, "
            f"and structured data "
            f"definitions within "
            f"COBOL working storage."
        )

    # =====================================================
    # 1.4 Constraints
    # =====================================================
    def generate_constraints_summary(
        self,
        program: CobolProgram
    ) -> str:
        return (
            "This comprehension was "
            "derived only from parser-"
            "visible COBOL source. "
            "External runtime behavior, "
            "environment-specific "
            "execution, unresolved "
            "dependencies, and hidden "
            "system integrations were "
            "not inferred unless "
            "explicitly present in "
            "source code."
        )

    # =====================================================
    # 2. Database
    # =====================================================
    def generate_database_summary(
        self,
        program: CobolProgram
    ) -> str:
        if not program.sql_blocks:
            return (
                "No explicit database "
                "interaction was "
                "detected from parsed "
                "COBOL source."
            )

        tables = []

        for sql in program.sql_blocks:
            tables.extend(sql.tables)

        unique_tables = sorted(
            set(tables)
        )

        return (
            "The program contains "
            "embedded SQL activity "
            "interacting with the "
            "following tables: "
            + ", ".join(
                unique_tables
            )
            + "."
        )

    # =====================================================
    # 3. Architecture
    # =====================================================
    def generate_architecture_summary(
        self,
        program: CobolProgram
    ) -> str:
        return (
            "The architecture "
            "follows a modular "
            "batch-processing "
            "pattern involving "
            "structured paragraph "
            "execution, file "
            "handling, reusable "
            "copybook definitions, "
            "and dependent "
            "subprogram invocation."
        )

    # =====================================================
    # 3.1 Components
    # =====================================================
    def generate_component_diagram_text(
        self,
        program: CobolProgram
    ):
        lines = [
            program.metadata.program_id
            or "MAIN_PROGRAM"
        ]

        for call in program.calls:
            lines.append(
                f" ├── CALLS → {call}"
            )

        for cpy in program.copybooks:
            lines.append(
                f" ├── USES COPYBOOK → {cpy}"
            )

        return "\n".join(lines)

    # =====================================================
    # 3.2 Control Flow
    # =====================================================
    def generate_control_flow_summary(
        self,
        program: CobolProgram
    ):
        flow = (
            program.control_flow
        )

        return (
            f"The control flow "
            f"contains "
            f"{flow.perform_count} "
            f"PERFORM paths, "
            f"{flow.call_count} "
            f"subprogram calls, "
            f"{flow.if_count} "
            f"conditional IF "
            f"branches, "
            f"{flow.evaluate_count} "
            f"EVALUATE branches, "
            f"with an overall "
            f"complexity score "
            f"of "
            f"{flow.complexity_score}."
        )

    # =====================================================
    # 4.1 Program Structure
    # =====================================================
    def generate_program_structure_summary(
        self,
        program: CobolProgram
    ):
        divisions = (
            ", ".join(
                program.divisions
            )
            if program.divisions
            else "none detected"
        )

        return (
            "The program is "
            "organized into "
            "standard COBOL "
            "structural layers "
            f"including: "
            f"{divisions}. "
            f"It contains "
            f"{len(program.sections)} "
            f"sections and "
            f"{len(program.paragraphs)} "
            f"procedural "
            f"paragraphs."
        )

    # =====================================================
    # 4.2 Algorithms
    # =====================================================
    def generate_algorithm_summary(
        self,
        program: CobolProgram
    ) -> str:
        flow = (
            program.control_flow
        )

        operations = {
            op.operation.upper()
            for op in
            program.file_operations
        }

        insights = []

        if (
            "READ" in operations
            and "WRITE" in operations
        ):
            insights.append(
                "The program follows a sequential read-transform-write processing pattern."
            )

        if (
            flow.perform_count > 1
            and len(
                program.paragraphs
            ) > 3
        ):
            insights.append(
                "The procedural structure indicates batch-oriented execution across multiple processing stages."
            )

        if flow.if_count > 0:
            insights.append(
                f"The logic includes conditional branching with {flow.if_count} IF-based decision points."
            )

        if flow.evaluate_count > 0:
            insights.append(
                f"Multi-branch decision handling is present through {flow.evaluate_count} EVALUATE statements."
            )

        if flow.call_count > 0:
            insights.append(
                f"The program invokes {flow.call_count} dependent subprogram flow paths."
            )

        if flow.complexity_score >= 20:
            insights.append(
                "Overall control flow suggests high procedural complexity."
            )
        elif flow.complexity_score >= 10:
            insights.append(
                "Overall control flow suggests moderate procedural complexity."
            )

        if not insights:
            return (
                "No significant algorithmic complexity was deterministically identified."
            )

        return " ".join(
            insights
        )

    # =====================================================
    # 4.3 IO
    # =====================================================
    def generate_io_summary(
        self,
        program: CobolProgram
    ):
        ops = {}

        for op in program.file_operations:
            ops.setdefault(
                op.operation.upper(),
                []
            ).append(
                op.target
            )

        lines = []

        for operation, targets in ops.items():
            joined = ", ".join(
                targets
            )
            lines.append(
                f"{operation}: {joined}"
            )

        if not lines:
            return (
                "No explicit file "
                "I/O activity "
                "detected."
            )

        return "\n".join(lines)
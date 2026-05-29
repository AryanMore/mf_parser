import os
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

from models.schema import CobolProgram
from analyzer.semantic_engine import SemanticEngine

class PDFGenerator:
    """
    Generates enterprise COBOL comprehension PDF.
    Supports:
    - deterministic parser output
    - validated LLM sections
    """

    def __init__(
        self,
        output_dir: str = "output"
    ):
        self.semantic_engine = SemanticEngine()
        self.output_dir = output_dir
        os.makedirs(
            self.output_dir,
            exist_ok=True
        )

    # =====================================================
    # PUBLIC ENTRY
    # =====================================================
    def generate(
        self,
        program: CobolProgram
    ):
        program_name = (
            program.metadata.program_id
            if program.metadata.program_id
            else "unknown_program"
        )

        output_path = os.path.join(
            self.output_dir,
            f"{program_name}.pdf"
        )

        doc = SimpleDocTemplate(
            output_path
        )

        styles = (
            getSampleStyleSheet()
        )

        story = []

        enabled = getattr(
            program,
            "enabled_sections",
            {}
        )

        llm = getattr(
            program,
            "llm_sections",
            {}
        )

        # =====================================================
        # TITLE
        # =====================================================
        story.append(
            Paragraph(
                f"<b>COBOL Program Comprehension - {program_name}</b>",
                styles["Title"]
            )
        )
        story.append(
            Spacer(1, 12)
        )

        # =====================================================
        # 1. INTRODUCTION
        # =====================================================
        if enabled.get(
            "introduction"
        ):
            story.append(
                Paragraph(
                    "<b>1. Introduction</b>",
                    styles["Heading1"]
                )
            )

            # 1.1 Program Overview
            if enabled.get(
                "program_overview"
            ):
                story.append(
                    Paragraph(
                        "<b>1.1 Program Overview</b>",
                        styles["Heading2"]
                    )
                )
                story.append(
                    Paragraph(
                        llm.get(
                            "program_overview",
                            self.semantic_engine.generate_program_overview(program)
                        ),
                        styles["Normal"]
                    )
                )
                story.append(
                    Spacer(1, 10)
                )

            # 1.2 Objectives
            if enabled.get(
                "objectives"
            ):
                story.append(
                    Paragraph(
                        "<b>1.2 Objectives</b>",
                        styles["Heading2"]
                    )
                )
                story.append(
                    Paragraph(
                        llm.get(
                            "objectives",
                            self.semantic_engine.generate_objectives_summary(program)
                        ),
                        styles["Normal"]
                    )
                )
                story.append(
                    Spacer(1, 10)
                )

            # 1.3 Scope
            if enabled.get(
                "scope"
            ):
                story.append(
                    Paragraph(
                        "<b>1.3 Scope</b>",
                        styles["Heading2"]
                    )
                )
                story.append(
                    Paragraph(
                        llm.get(
                            "scope",
                            self.semantic_engine.generate_scope_summary(program)
                        ),
                        styles["Normal"]
                    )
                )
                story.append(
                    Spacer(1, 10)
                )

            # 1.4 Constraints
            if enabled.get(
                "assumptions_constraints"
            ):
                story.append(
                    Paragraph(
                        "<b>1.4 Assumptions and Constraints</b>",
                        styles["Heading2"]
                    )
                )
                story.append(
                    Paragraph(
                        llm.get(
                            "assumptions_constraints",
                            self.semantic_engine.generate_constraints_summary(program)
                        ),
                        styles["Normal"]
                    )
                )
                story.append(
                    Spacer(1, 14)
                )

        # =====================================================
        # 2. DATABASE DETAILS
        # =====================================================
        if (
            enabled.get("database_details")
            or enabled.get("ims_segments")
            or enabled.get("idms_records")
        ):
            story.append(
                Paragraph(
                    "<b>2. Database Details</b>",
                    styles["Heading1"]
                )
            )

            if enabled.get("db2_tables"):
                story.append(
                    Paragraph(
                        "<b>2.1 DB2 Tables</b>",
                        styles["Heading2"]
                    )
                )

                if program.sql_blocks:
                    for sql in program.sql_blocks:
                        for table in sql.tables:
                            story.append(
                                Paragraph(
                                    f"• {table}",
                                    styles["Normal"]
                                )
                            )
                else:
                    story.append(
                        Paragraph(
                            "No DB2 usage detected.",
                            styles["Normal"]
                        )
                    )

            else:
                story.append(
                    Paragraph("No DB2 usage detected.", styles["Normal"])
                )

            story.append(Spacer(1, 10))
            story.append(Paragraph("<b>2.2 IMS Segments</b>", styles["Heading2"]))
            story.append(
                Paragraph(
                    "No IMS segments detected from parser-visible source.",
                    styles["Normal"]
                )
            )
            story.append(Spacer(1, 10))
            story.append(Paragraph("<b>2.3 IDMS Records</b>", styles["Heading2"]))
            story.append(
                Paragraph(
                    "No IDMS records detected from parser-visible source.",
                    styles["Normal"]
                )
            )
            story.append(Spacer(1, 14))

        # =====================================================
        # 3. SYSTEM ARCHITECTURE
        # =====================================================
        if enabled.get(
            "system_architecture"
        ):
            story.append(
                Paragraph(
                    "<b>3. System Architecture</b>",
                    styles["Heading1"]
                )
            )

            # Components
            if enabled.get(
                "component_diagram"
            ):
                story.append(
                    Paragraph(
                        llm.get(
                            "architecture_refinement",
                            self.semantic_engine.generate_architecture_summary(program)
                        ),
                        styles["Normal"]
                    )
                )
                story.append(
                    Spacer(1, 10)
                )
                story.append(
                    Paragraph(
                        "<b>3.1 Component Diagram</b>",
                        styles["Heading2"]
                    )
                )

                components = set()
                components.update(
                    program.copybooks
                )
                components.update(
                    program.calls
                )

                for comp in sorted(
                    components
                ):
                    story.append(
                        Paragraph(
                            f"• {comp}",
                            styles["Normal"]
                        )
                    )

                story.append(
                    Spacer(1, 10)
                )

            # Control flow
            if enabled.get(
                "control_flow_diagram"
            ):
                story.append(
                    Paragraph(
                        "<b>3.2 Control Flow Diagram</b>",
                        styles["Heading2"]
                    )
                )

                story.append(
                    Paragraph(
                        f"PERFORM count: {program.control_flow.perform_count}",
                        styles["Normal"]
                    )
                )
                story.append(
                    Paragraph(
                        f"CALL count: {program.control_flow.call_count}",
                        styles["Normal"]
                    )
                )
                story.append(
                    Paragraph(
                        f"IF count: {program.control_flow.if_count}",
                        styles["Normal"]
                    )
                )
                story.append(
                    Paragraph(
                        f"EVALUATE count: {program.control_flow.evaluate_count}",
                        styles["Normal"]
                    )
                )
                story.append(
                    Paragraph(
                        f"Complexity score: {program.control_flow.complexity_score}",
                        styles["Normal"]
                    )
                )

                story.append(
                    Spacer(1, 8)
                )

                for edge in program.control_flow.edges:
                    story.append(
                        Paragraph(
                            f"• {edge.source} → {edge.target} ({edge.relation})",
                            styles["Normal"]
                        )
                    )

                story.append(
                    Spacer(1, 14)
                )

        # =====================================================
        # 4. DETAILED DESIGN
        # =====================================================
        if enabled.get(
            "detailed_design"
        ):
            story.append(
                Paragraph(
                    "<b>4. Detailed Design</b>",
                    styles["Heading1"]
                )
            )

            # 4.1 Program Structure
            if enabled.get(
                "program_structure"
            ):
                story.append(
                    Paragraph(
                        "<b>4.1 Program Structure</b>",
                        styles["Heading2"]
                    )
                )
                story.append(
                    Paragraph(
                        llm.get(
                            "structure_refinement",
                            self.semantic_engine.generate_program_structure_summary(program)
                        ),
                        styles["Normal"]
                    )
                )
                story.append(
                    Spacer(1, 10)
                )

                for section in (
                    program.sections
                ):
                    story.append(
                        Paragraph(
                            f"• {section.name}",
                            styles["Normal"]
                        )
                    )

                story.append(
                    Spacer(1, 10)
                )

            # 4.2 Algorithms
            if enabled.get(
                "algorithms"
            ):
                story.append(
                    Paragraph(
                        "<b>4.2 Algorithms</b>",
                        styles["Heading2"]
                    )
                )
                algorithm_summary = (
                    llm.get(
                        "algorithm_refinement",
                        self.semantic_engine.generate_algorithm_summary(program)
                    )
                )

                story.append(
                    Paragraph(
                        algorithm_summary,
                        styles["Normal"]
                    )
                )
                story.append(
                    Spacer(1, 10)
                )

            # 4.3 IO Specs
            if enabled.get(
                "io_specifications"
            ):
                story.append(
                    Paragraph(
                        "<b>4.3 Input/Output Specifications</b>",
                        styles["Heading2"]
                    )
                )

                io_data = [
                    ["Operation", "Target"]
                ]

                for op in (
                    program.file_operations
                ):
                    io_data.append([
                        op.operation,
                        op.target
                    ])

                io_table = Table(
                    io_data
                )

                io_table.setStyle(
                    TableStyle([
                        (
                            "BACKGROUND",
                            (0, 0),
                            (-1, 0),
                            colors.lightgrey
                        ),
                        (
                            "GRID",
                            (0, 0),
                            (-1, -1),
                            1,
                            colors.black
                        ),
                        (
                            "PADDING",
                            (0, 0),
                            (-1, -1),
                            5
                        ),
                    ])
                )

                story.append(
                    io_table
                )
                story.append(
                    Spacer(1, 14)
                )

        # =====================================================
        # APPENDIX
        # =====================================================
        story.append(
            Paragraph(
                "<b>Appendix A - Parsed Metadata</b>",
                styles["Heading1"]
            )
        )

        metadata_data = [
            ["Field", "Value"],
            [
                "Program ID",
                program.metadata.program_id or ""
            ],
            [
                "Author",
                program.metadata.author or ""
            ],
            [
                "Date Written",
                program.metadata.date_written or ""
            ],
        ]

        metadata_table = Table(
            metadata_data
        )

        metadata_table.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.lightgrey
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    1,
                    colors.black
                ),
                (
                    "PADDING",
                    (0, 0),
                    (-1, -1),
                    5
                ),
            ])
        )

        story.append(
            metadata_table
        )

        doc.build(
            story
        )

        return output_path

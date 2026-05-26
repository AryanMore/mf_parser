from models.schema import CobolProgram


class SectionRouter:
    """
    Determines which documentation sections
    are relevant for a parsed COBOL program.

    This becomes the source-of-truth gating layer
    before LLM or DOC generation.
    """

    def route(self, program: CobolProgram):
        sections = {}

        # =====================================================
        # 1. INTRODUCTION
        # Always valid
        # =====================================================
        sections["introduction"] = True
        sections["program_overview"] = True
        sections["objectives"] = True
        sections["scope"] = True
        sections["assumptions_constraints"] = True

        # =====================================================
        # 2. DATABASE DETAILS
        # Only if DB-like integrations detected
        # =====================================================
        has_sql = len(program.sql_blocks) > 0

        sections["database_details"] = has_sql
        sections["db2_tables"] = has_sql

        # Future expansion
        sections["ims_segments"] = self._has_ims(program)
        sections["idms_records"] = self._has_idms(program)

        # If IMS/IDMS exist, keep database_details on
        if sections["ims_segments"] or sections["idms_records"]:
            sections["database_details"] = True

        # =====================================================
        # 3. SYSTEM ARCHITECTURE
        # =====================================================
        has_dependencies = (
            len(program.calls) > 0
            or len(program.copybooks) > 0
            or len(program.file_operations) > 0
        )

        sections["system_architecture"] = has_dependencies
        sections["component_diagram"] = has_dependencies

        # Control flow only if meaningful
        sections["control_flow_diagram"] = (
            len(program.paragraphs) > 1
        )

        # =====================================================
        # 4. DETAILED DESIGN
        # =====================================================
        sections["detailed_design"] = True
        sections["program_structure"] = True

        # Algorithms only if procedural complexity exists
        sections["algorithms"] = (
            len(program.paragraphs) > 2
        )

        # I/O specs only if files are used
        sections["io_specifications"] = (
            len(program.file_operations) > 0
        )

        return sections

    # =====================================================
    # Future DB type detectors
    # =====================================================
    def _has_ims(self, program: CobolProgram):
        """
        Placeholder:
        detect IMS usage later.
        Example:
        PCB, DLI, GU/GN calls, etc.
        """
        return False

    def _has_idms(self, program: CobolProgram):
        """
        Placeholder:
        detect IDMS usage later.
        Example:
        OBTAIN, DB-END-OF-SET, etc.
        """
        return False
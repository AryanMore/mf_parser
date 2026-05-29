import json
import os
from models.schema import CobolProgram


class JSONGenerator:
    """
    Exports parsed COBOL model to JSON.
    """

    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    # -----------------------------------
    # Public entry
    # -----------------------------------
    def generate(self, program: CobolProgram):
        program_name = (
            program.metadata.program_id
            if program.metadata.program_id
            else "unknown_program"
        )

        output_path = os.path.join(
            self.output_dir,
            f"{program_name}.json"
        )

        payload = program.to_dict()
        enabled = getattr(program, "enabled_sections", {})
        payload["comprehension_toc"] = self._build_toc(enabled)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(
                payload,
                f,
                indent=4
            )

        return output_path

    def _build_toc(self, enabled: dict):
        def include(key: str):
            return bool(enabled.get(key, False))

        return [
            {
                "id": "1",
                "title": "Introduction",
                "included": include("introduction"),
                "children": [
                    {"id": "1.1", "title": "Program Overview", "included": include("program_overview")},
                    {"id": "1.2", "title": "Objectives", "included": include("objectives")},
                    {"id": "1.3", "title": "Scope", "included": include("scope")},
                    {"id": "1.4", "title": "Assumptions and Constraints", "included": include("assumptions_constraints")},
                ],
            },
            {
                "id": "2",
                "title": "Database Details",
                "included": include("database_details") or include("ims_segments") or include("idms_records"),
                "children": [
                    {"id": "2.1", "title": "DB2 Tables", "included": include("db2_tables")},
                    {"id": "2.2", "title": "IMS Segments", "included": include("ims_segments")},
                    {"id": "2.3", "title": "IDMS Records", "included": include("idms_records")},
                ],
            },
            {
                "id": "3",
                "title": "System Architecture",
                "included": include("system_architecture"),
                "children": [
                    {"id": "3.1", "title": "Component Diagram", "included": include("component_diagram")},
                    {"id": "3.2", "title": "Control Flow Diagram", "included": include("control_flow_diagram")},
                ],
            },
            {
                "id": "4",
                "title": "Detailed Design",
                "included": include("detailed_design"),
                "children": [
                    {"id": "4.1", "title": "Program Structure", "included": include("program_structure")},
                    {"id": "4.2", "title": "Algorithms", "included": include("algorithms")},
                    {"id": "4.3", "title": "Input/Output Specifications", "included": include("io_specifications")},
                ],
            },
        ]

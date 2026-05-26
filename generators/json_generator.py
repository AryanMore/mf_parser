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

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(
                program.to_dict(),
                f,
                indent=4
            )

        return output_path
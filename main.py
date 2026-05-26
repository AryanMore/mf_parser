import os
import sys

from parser.cobol_parser import CobolParser
from analyzer.flow_analyzer import FlowAnalyzer
from analyzer.semantic_engine import SemanticEngine
from analyzer.section_router import SectionRouter
from analyzer.llm_semantic_engine import LLMSemanticEngine
from analyzer.llm_validator import LLMValidator

from generators.json_generator import JSONGenerator
from generators.docx_generator import DOCXGenerator
from generators.pdf_generator import PDFGenerator


SUPPORTED_EXTENSIONS = {
    ".cbl",
    ".cob",
    ".cobol",
    ".cpy"
}


class CobolComprehensionEngine:
    """
    Enterprise-safe COBOL comprehension engine.

    Modes:
    - deterministic
    - llm
    """

    def __init__(
        self,
        use_llm: bool = False
    ):
        self.use_llm = use_llm

        # -------------------------------
        # Core parser
        # -------------------------------
        self.parser = CobolParser()

        # -------------------------------
        # Deterministic analyzer
        # -------------------------------
        self.semantic_engine = SemanticEngine()

        self.flow_analyzer = FlowAnalyzer()

        # -------------------------------
        # Section gating
        # -------------------------------
        self.section_router = SectionRouter()

        # -------------------------------
        # LLM pipeline
        # -------------------------------
        if self.use_llm:
            self.llm_engine = LLMSemanticEngine()
            self.validator = LLMValidator()

        # -------------------------------
        # Generators
        # -------------------------------
        self.json_generator = JSONGenerator()
        self.docx_generator = DOCXGenerator()
        self.pdf_generator = PDFGenerator()

    # =====================================================
    # SINGLE FILE
    # =====================================================
    def process_file(
        self,
        file_path: str
    ):
        print(f"\nProcessing: {file_path}")

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as f:
            raw_text = f.read()

        # -----------------------------------
        # Parse COBOL
        # -----------------------------------
        program = self.parser.parse(raw_text)
        program.control_flow = (
        self.flow_analyzer.analyze(
            raw_text,
            program
        )
    )

        # -----------------------------------
        # Route sections
        # -----------------------------------
        enabled_sections = (
            self.section_router.route(program)
        )

        # store for doc generators later
        program.enabled_sections = enabled_sections

        # -----------------------------------
        # Default deterministic summary
        # -----------------------------------
        program.summary = (
            self.semantic_engine
            .generate_summary(program)
        )

        # -----------------------------------
        # Optional LLM enhancement (V2.5)
        # -----------------------------------
        if self.use_llm:
            print("Running LLM intelligence layer...")
            print("Calling Ollama...")

            llm_sections = (
                self.llm_engine.generate_sections(
                    program,
                    enabled_sections
                )
            )

            print("Ollama returned.")

            combined_text = "\n".join(
                str(v)
                for v in llm_sections.values()
                if v
            )

            validation = self.validator.validate(
                combined_text,
                program
            )

            if validation["valid"]:
                print("LLM intelligence validated.")
                program.llm_sections = llm_sections
            else:
                print("LLM output rejected.")
                print("Validation issues:")
                for issue in validation["issues"]:
                    print(f" - {issue}")
                program.llm_sections = {}

        else:
            program.llm_sections = {}

        # -----------------------------------
        # Generate outputs
        # -----------------------------------
        json_path = (
            self.json_generator
            .generate(program)
        )

        docx_path = (
            self.docx_generator
            .generate(program)
        )

        pdf_path = (
            self.pdf_generator
            .generate(program)
        )

        print(f"JSON -> {json_path}")
        print(f"DOCX -> {docx_path}")
        print(f"PDF  -> {pdf_path}")

    # =====================================================
    # FOLDER MODE
    # =====================================================
    def process_folder(
        self,
        folder_path: str
    ):
        for root, _, files in os.walk(
            folder_path
        ):
            for file in files:
                ext = os.path.splitext(
                    file
                )[1].lower()

                if ext in SUPPORTED_EXTENSIONS:
                    path = os.path.join(
                        root,
                        file
                    )

                    self.process_file(path)


# =====================================================
# CLI
# =====================================================
def main():
    if len(sys.argv) < 2:
        print(
            "Usage:"
        )
        print(
            "python main.py <file_or_folder> [--llm]"
        )
        sys.exit(1)

    target = sys.argv[1]
    use_llm = "--llm" in sys.argv

    if not os.path.exists(target):
        print(
            f"Path not found: {target}"
        )
        sys.exit(1)

    engine = CobolComprehensionEngine(
        use_llm=use_llm
    )

    if os.path.isfile(target):
        ext = os.path.splitext(
            target
        )[1].lower()

        if ext not in SUPPORTED_EXTENSIONS:
            print(
                f"Unsupported file type: {ext}"
            )
            sys.exit(1)

        engine.process_file(target)

    elif os.path.isdir(target):
        engine.process_folder(target)


if __name__ == "__main__":
    main()
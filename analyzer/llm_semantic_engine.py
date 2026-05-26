import json
import ollama

from models.schema import CobolProgram


class LLMSemanticEngine:
    """
    LLM Enrichment Layer (V2.5)

    Single-call design.
    Enriches deterministic sections instead
    of replacing them.
    """

    def __init__(
        self,
        model: str = "llama3"
    ):
        self.model = model

    # =====================================================
    # MASTER ENTRY
    # =====================================================
    def generate_sections(
        self,
        program: CobolProgram,
        enabled_sections: dict = None
    ):
        prompt = self._build_prompt(
            program
        )

        raw = self._ask_llm(prompt)

        if not raw:
            return {}

        # --------------------------------
        # Strip markdown fences
        # --------------------------------
        cleaned = (
            raw.replace("```json", "")
            .replace("```", "")
            .strip()
        )

        # --------------------------------
        # Extract JSON body only
        # --------------------------------
        start = cleaned.find("{")
        end = cleaned.rfind("}")

        if start == -1 or end == -1:
            print("No JSON object found.")
            return {}

        json_body = cleaned[start:end + 1]

        try:
            parsed = json.loads(json_body)
            required_keys = [
                "objectives_refinement",
                "architecture_refinement",
                "structure_refinement",
                "algorithm_refinement",
                "business_logic",
                "program_walkthrough",
                "paragraph_explanations"
            ]

            for key in required_keys:
                parsed.setdefault(key, "")
            return parsed

        except Exception as e:
            print(f"LLM JSON parsing failed: {e}")
            print("Raw LLM output:")
            print(raw)
            return {}

    # =====================================================
    # PROMPT
    # =====================================================
    def _build_prompt(
        self,
        program: CobolProgram
    ):
        facts = {
            "program_id":
                program.metadata.program_id,

            "copybooks":
                program.copybooks,

            "calls":
                program.calls,

            "sections": [
                s.name
                for s in program.sections
            ],

            "paragraphs": [
                p.name
                for p in program.paragraphs
            ],

            "variables_count":
                len(
                    program.variables
                ),

            "file_operations": [
                {
                    "operation": op.operation,
                    "target": op.target
                }
                for op in
                program.file_operations
            ],

            "flow": {
                "perform_count":
                    program.control_flow.perform_count,
                "call_count":
                    program.control_flow.call_count,
                "if_count":
                    program.control_flow.if_count,
                "evaluate_count":
                    program.control_flow.evaluate_count,
                "complexity_score":
                    program.control_flow.complexity_score
            }
        }

        return f"""
You are generating enterprise COBOL comprehension.

STRICT RULES:
- Use ONLY supplied parser facts.
- Never invent systems, tables, customers, organizations.
- Infer cautiously.
- If uncertain, say:
  "Not fully inferable from parsed source."

CRITICAL OUTPUT RULES:
- Return ONLY raw JSON.
- Do NOT add explanation text.
- Do NOT add markdown.
- Do NOT add ```json fences.
- Do NOT say "Here is the JSON".
- Every value must be a JSON string.
- Escape line breaks using \\n.
- Must be valid json.loads() compatible output.

Exact JSON schema:
{{
  "objectives_refinement": "string",
  "architecture_refinement": "string",
  "structure_refinement": "string",
  "algorithm_refinement": "string",
  "business_logic": "string",
  "program_walkthrough": "1. step\\n2. step\\n3. step",
  "paragraph_explanations": "PARA: explanation\\nPARA: explanation"
}}

FACTS:
{json.dumps(facts, indent=2)}
"""

    # =====================================================
    # OLLAMA
    # =====================================================
    def _ask_llm(
        self,
        prompt: str
    ):
        try:
            response = ollama.chat(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            return (
                response["message"]
                ["content"]
                .strip()
            )

        except Exception as e:
            print(
                f"Ollama failed: {e}"
            )
            return ""
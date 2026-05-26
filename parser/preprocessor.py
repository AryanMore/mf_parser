from typing import List


class CobolPreprocessor:
    """
    COBOL fixed-format aware preprocessor.
    Safer for enterprise COBOL.
    """

    def preprocess(self, text: str) -> str:
        raw_lines = text.splitlines()

        cleaned = self._extract_code_area(raw_lines)
        cleaned = self._merge_continuations(cleaned)
        cleaned = self._remove_blank_lines(cleaned)

        return "\n".join(cleaned)

    # -----------------------------------
    # Extract COBOL code area
    # cols 1-6  = seq
    # col 7     = indicator
    # cols 8-72 = code
    # -----------------------------------
    def _extract_code_area(self, lines: List[str]) -> List[str]:
        cleaned = []

        for line in lines:
            if not line.strip():
                continue

            padded = line.ljust(72)

            indicator = padded[6]   # col 7
            code = padded[7:72].rstrip()  # cols 8-72

            # comment line
            if indicator == "*":
                continue

            cleaned.append(
                {
                    "indicator": indicator,
                    "code": code
                }
            )

        return cleaned

    # -----------------------------------
    # Merge continuation lines
    # col 7 = '-'
    # -----------------------------------
    def _merge_continuations(self, lines):
        merged = []
        current = ""

        for line in lines:
            indicator = line["indicator"]
            code = line["code"]

            if indicator == "-":
                current += " " + code.strip()
            else:
                if current:
                    merged.append(current.rstrip())
                current = code

        if current:
            merged.append(current.rstrip())

        return merged

    # -----------------------------------
    # Remove blanks
    # -----------------------------------
    def _remove_blank_lines(self, lines):
        return [line for line in lines if line.strip()]
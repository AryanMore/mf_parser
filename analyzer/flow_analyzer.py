from models.schema import (
    CobolProgram,
    FlowEdge,
    ControlFlow
)

from parser import patterns


class FlowAnalyzer:
    """
    Extracts procedural control flow
    from COBOL source.

    Produces:
    - PERFORM edges
    - CALL edges
    - FALLTHROUGH edges
    - complexity metrics
    """

    def analyze(
        self,
        text: str,
        program: CobolProgram
    ) -> ControlFlow:
        flow = ControlFlow()

        lines = text.splitlines()

        paragraph_names = [
            p.name.upper()
            for p in program.paragraphs
        ]

        paragraph_set = set(
            paragraph_names
        )

        # -----------------------------------
        # Paragraph ownership
        # Map line index → current paragraph
        # -----------------------------------
        current_paragraph = None
        line_owner = {}

        for idx, line in enumerate(lines):
            stripped = line.strip()

            for para in paragraph_names:
                if stripped == f"{para}.":
                    current_paragraph = para
                    break

            line_owner[idx] = (
                current_paragraph
            )

        # =====================================================
        # 1. PERFORM edges
        # =====================================================
        for idx, line in enumerate(lines):
            match = (
                patterns.PERFORM_PATTERN
                .search(line)
            )

            if not match:
                continue

            target = (
                match.group(1)
                .upper()
            )

            source = line_owner.get(
                idx
            )

            if (
                source
                and target in paragraph_set
            ):
                flow.edges.append(
                    FlowEdge(
                        source=source,
                        target=target,
                        relation="PERFORM"
                    )
                )

                flow.perform_count += 1

        # =====================================================
        # 2. CALL edges
        # =====================================================
        for idx, line in enumerate(lines):
            match = (
                patterns.CALL_PATTERN
                .search(line)
            )

            if not match:
                continue

            target = (
                match.group(1)
                .upper()
            )

            source = line_owner.get(
                idx
            )

            if source:
                flow.edges.append(
                    FlowEdge(
                        source=source,
                        target=target,
                        relation="CALL"
                    )
                )

                flow.call_count += 1

        # =====================================================
        # 3. FALLTHROUGH edges
        # Paragraph sequence
        # =====================================================
        for i in range(
            len(paragraph_names) - 1
        ):
            source = (
                paragraph_names[i]
            )
            target = (
                paragraph_names[i + 1]
            )

            flow.edges.append(
                FlowEdge(
                    source=source,
                    target=target,
                    relation="FALLTHROUGH"
                )
            )

        # =====================================================
        # 4. Complexity metrics
        # =====================================================
        full_text = text.upper()

        flow.if_count = len(
            patterns.IF_PATTERN.findall(
                full_text
            )
        )

        flow.evaluate_count = len(
            patterns.EVALUATE_PATTERN.findall(
                full_text
            )
        )

        flow.complexity_score = (
            flow.perform_count
            + flow.call_count
            + flow.if_count
            + (
                2
                * flow.evaluate_count
            )
        )

        # =====================================================
        # Deduplicate edges
        # =====================================================
        seen = set()
        unique_edges = []

        for edge in flow.edges:
            key = (
                edge.source,
                edge.target,
                edge.relation
            )

            if key in seen:
                continue

            unique_edges.append(
                edge
            )
            seen.add(key)

        flow.edges = unique_edges

        return flow
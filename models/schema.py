from dataclasses import dataclass, field, asdict
from typing import List, Optional


# =====================================================
# METADATA
# =====================================================

@dataclass
class ProgramMetadata:
    program_id: Optional[str] = None
    author: Optional[str] = None
    date_written: Optional[str] = None


# =====================================================
# VARIABLES
# =====================================================

@dataclass
class Variable:
    level: str
    name: str
    pic: Optional[str] = None
    value: Optional[str] = None
    occurs: Optional[str] = None
    redefines: Optional[str] = None


# =====================================================
# STRUCTURE
# =====================================================

@dataclass
class Section:
    name: str


@dataclass
class Paragraph:
    name: str


# =====================================================
# FILE OPS
# =====================================================

@dataclass
class FileOperation:
    operation: str
    target: str


# =====================================================
# SQL
# =====================================================

@dataclass
class SQLBlock:
    raw_sql: str
    operation: Optional[str] = None
    tables: List[str] = field(
        default_factory=list
    )


# =====================================================
# FLOW GRAPH
# =====================================================

@dataclass
class FlowEdge:
    """
    One control-flow relationship.
    Example:
    1000-INIT -> 2000-PROCESS (PERFORM)
    """

    source: str
    target: str
    relation: str   # PERFORM / CALL / FALLTHROUGH


@dataclass
class ControlFlow:
    """
    Overall control-flow intelligence.
    """

    edges: List[FlowEdge] = field(
        default_factory=list
    )

    perform_count: int = 0
    call_count: int = 0
    if_count: int = 0
    evaluate_count: int = 0

    complexity_score: int = 0


# =====================================================
# MAIN MODEL
# =====================================================

@dataclass
class CobolProgram:
    metadata: ProgramMetadata = field(
        default_factory=ProgramMetadata
    )

    divisions: List[str] = field(
        default_factory=list
    )

    sections: List[Section] = field(
        default_factory=list
    )

    paragraphs: List[Paragraph] = field(
        default_factory=list
    )

    variables: List[Variable] = field(
        default_factory=list
    )

    copybooks: List[str] = field(
        default_factory=list
    )

    calls: List[str] = field(
        default_factory=list
    )

    file_operations: List[FileOperation] = field(
        default_factory=list
    )

    sql_blocks: List[SQLBlock] = field(
        default_factory=list
    )

    # -----------------------------------
    # Flow intelligence
    # -----------------------------------
    control_flow: ControlFlow = field(
        default_factory=ControlFlow
    )

    # -----------------------------------
    # Documentation layers
    # -----------------------------------
    summary: str = ""

    llm_sections: dict = field(
        default_factory=dict
    )

    enabled_sections: dict = field(
        default_factory=dict
    )

    # -----------------------------------
    # Export
    # -----------------------------------
    def to_dict(self):
        return asdict(self)
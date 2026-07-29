from dataclasses import dataclass, field
from typing import List


@dataclass
class ReviewResult:
    """
    Resultado da crítica e revisão editorial emitida pelo CriticAgent sobre um post em Markdown.
    """

    quality_score: float  # 0.0 a 10.0
    approved: bool
    feedback_notes: List[str] = field(default_factory=list)
    revised_markdown: str = ""

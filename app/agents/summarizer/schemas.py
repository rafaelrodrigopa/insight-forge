from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class SummaryResult:
    """
    Estrutura padronizada de resposta contendo o resumo estruturado de um documento.
    """

    title: str
    summary: str
    key_points: List[str] = field(default_factory=list)
    topics: List[str] = field(default_factory=list)
    relevance_score: float = 0.0
    source_url: Optional[str] = None
    raw_content_title: Optional[str] = None

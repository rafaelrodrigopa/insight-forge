from dataclasses import dataclass, field
from typing import List


@dataclass
class ClassificationResult:
    """
    Resultado da classificação temática de um documento realizada pelo ClassifierAgent.
    """

    primary_category: str
    secondary_categories: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    confidence: float = 0.9

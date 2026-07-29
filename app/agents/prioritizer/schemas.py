from dataclasses import dataclass


@dataclass
class PriorityDecision:
    """
    Decisão editorial emitida pelo PrioritizerAgent indicando se a notícia merece virar artigo.
    """

    priority_score: float  # 0.0 a 100.0
    should_publish: bool
    reasoning: str

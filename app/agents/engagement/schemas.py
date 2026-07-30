from dataclasses import dataclass, field
from typing import Optional


@dataclass
class TargetPost:
    """
    Representa um post descoberto na rede com metadados para avaliação.
    """

    post_urn: str
    url: str
    title: str
    content: str
    author: Optional[str] = None
    published_at: Optional[str] = None
    topic: Optional[str] = None
    relevance_score: float = 0.0


@dataclass
class EngagementDecision:
    """
    Decisão gerada pela IA sobre curtir e comentar no post.
    """

    should_engage: bool
    suggested_reaction: str = "LIKE"  # LIKE, PRAISE, EMPATHY, INTEREST, APPRECIATION
    generated_comment: Optional[str] = None
    reasoning: Optional[str] = None

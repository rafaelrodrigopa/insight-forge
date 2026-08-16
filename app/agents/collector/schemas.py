from dataclasses import dataclass
from typing import Optional


@dataclass
class CollectedContent:
    title: str
    content: str
    source: str
    url: str
    published_at: Optional[str] = None
    ai_analysis: Optional[str] = None
    priority_boost: float = 1.0
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class PostContent:
    """
    Representação estruturada de um post/artigo em Markdown gerado pelo Writer Agent.
    """

    title: str
    slug: str
    date: str
    content_md: str
    topics: List[str] = field(default_factory=list)
    author: str = "Insight Forge AI Writer"
    source_url: Optional[str] = None
    file_path: Optional[str] = None
    image_path: Optional[str] = None

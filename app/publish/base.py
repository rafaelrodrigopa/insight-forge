from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from app.agents.writer.schemas import PostContent


@dataclass
class PublishResult:
    """
    Resultado padronizado da tentativa de publicação em qualquer canal.
    """

    publisher_name: str
    success: bool
    post_url: Optional[str] = None
    message: str = ""
    published_at: datetime = field(default_factory=datetime.now)


class BasePublisher(ABC):
    """
    Classe abstrata para todos os publicadores de conteúdo (Markdown, LinkedIn, WordPress, etc.).
    """

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def publish(self, post: PostContent) -> PublishResult:
        """
        Publica um PostContent no destino e retorna um PublishResult.
        """
        pass

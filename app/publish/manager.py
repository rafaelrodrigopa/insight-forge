from typing import List, Optional

from app.agents.writer.schemas import PostContent
from app.publish.base import BasePublisher, PublishResult
from app.publish.publishers.linkedin_publisher import LinkedInPublisherAdapter
from app.publish.publishers.markdown_publisher import MarkdownPublisher


class PublisherManager:
    """
    Orquestrador responsável por registrar e disparar publicações em múltiplos canais simultaneamente.
    """

    def __init__(self, publishers: Optional[List[BasePublisher]] = None):
        self.publishers: List[BasePublisher] = publishers or []

    def register_publisher(self, publisher: BasePublisher) -> None:
        """
        Adiciona um publicador à lista de canais ativos.
        """
        self.publishers.append(publisher)

    def publish_all(self, post: PostContent) -> List[PublishResult]:
        """
        Dispara a publicação de um post em todos os canais registrados.
        """
        results = []
        for pub in self.publishers:
            res = pub.publish(post)
            results.append(res)
        return results

    @classmethod
    def create_default(
        cls, enable_linkedin: bool = False
    ) -> "PublisherManager":
        """
        Factory method que instancia o gerenciador com os publicadores padrão configurados.
        """
        manager = cls()
        manager.register_publisher(MarkdownPublisher())
        if enable_linkedin:
            manager.register_publisher(LinkedInPublisherAdapter())
        return manager

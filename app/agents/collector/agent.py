from typing import List, Optional

from app.agents.collector.rss import RSSFetcher
from app.agents.collector.schemas import CollectedContent
from app.agents.collector.service import CollectorService
from app.providers.base import BaseLLMProvider


class CollectorAgent:
    """
    Agente especializado em descobrir e coletar conteúdos relevantes de fontes externas.
    """

    def __init__(
        self,
        llm_provider: Optional[BaseLLMProvider] = None,
        rss_fetcher: Optional[RSSFetcher] = None,
    ):
        self.service = CollectorService(
            llm_provider=llm_provider, rss_fetcher=rss_fetcher
        )

    def collect(
        self, source: str, analyze_with_ai: bool = True
    ) -> List[CollectedContent]:
        """
        Executa o processo de coleta de conteúdo de uma fonte (URL RSS ou texto bruto).
        """
        return self.service.collect(source, analyze_with_ai=analyze_with_ai)

    def collect_pool(
        self, max_items_per_feed: int = 5, analyze_with_ai: bool = False
    ) -> List[CollectedContent]:
        """
        Coleta notícias de todo o pool de feeds RSS configurados no sistema.
        """
        return self.service.collect_pool(
            max_items_per_feed=max_items_per_feed, analyze_with_ai=analyze_with_ai
        )
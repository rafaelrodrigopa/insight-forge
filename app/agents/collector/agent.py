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
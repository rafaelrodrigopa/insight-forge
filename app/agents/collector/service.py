from typing import List, Optional

from app.agents.collector.prompt import COLLECTOR_SYSTEM_PROMPT
from app.agents.collector.rss import RSSFetcher
from app.agents.collector.schemas import CollectedContent
from app.providers.base import BaseLLMProvider
from app.providers.gemini import GeminiChat


class CollectorService:
    """
    Serviço de orquestração do Agente Coletor: busca notícias RSS e analisa relevância via IA.
    """

    def __init__(
        self,
        llm_provider: Optional[BaseLLMProvider] = None,
        rss_fetcher: Optional[RSSFetcher] = None,
    ):
        self.llm = llm_provider or GeminiChat()
        self.fetcher = rss_fetcher or RSSFetcher()

    def collect(
        self, source: str, analyze_with_ai: bool = True
    ) -> List[CollectedContent]:
        """
        Coleta conteúdos da fonte informada (URL de RSS/Atom ou texto bruto).
        """
        results: List[CollectedContent] = []

        if source.startswith("http://") or source.startswith("https://"):
            raw_entries = self.fetcher.fetch_feed(source)
            for entry in raw_entries:
                ai_analysis = None
                if analyze_with_ai and self.llm:
                    prompt = (
                        f"{COLLECTOR_SYSTEM_PROMPT}\n\n"
                        f"Análise a relevância e resuma a seguinte notícia:\n"
                        f"Título: {entry['title']}\n"
                        f"Conteúdo: {entry['content']}\n"
                    )
                    try:
                        llm_res = self.llm.generate(prompt)
                        ai_analysis = llm_res.text
                    except Exception:
                        ai_analysis = None

                item = CollectedContent(
                    title=entry["title"],
                    content=entry["content"],
                    source=entry["source"],
                    url=entry["url"],
                    published_at=entry.get("published_at"),
                    ai_analysis=ai_analysis,
                )
                results.append(item)
        else:
            ai_analysis = None
            if analyze_with_ai and self.llm:
                prompt = f"{COLLECTOR_SYSTEM_PROMPT}\n\nFonte:\n{source}"
                try:
                    llm_res = self.llm.generate(prompt)
                    ai_analysis = llm_res.text
                except Exception:
                    ai_analysis = None

            results.append(
                CollectedContent(
                    title="Conteúdo Coletado Direto",
                    content=source,
                    source="Texto Direto",
                    url="",
                    ai_analysis=ai_analysis,
                )
            )

        return results
from typing import List, Optional

from app.agents.summarizer.schemas import SummaryResult
from app.agents.writer.schemas import PostContent
from app.agents.writer.service import WriterService
from app.providers.base import BaseLLMProvider


class WriterAgent:
    """
    Agente redator especializado em transformar resumos estruturados em posts Markdown.
    """

    def __init__(
        self,
        llm_provider: Optional[BaseLLMProvider] = None,
        posts_dir: str = "posts",
    ):
        self.service = WriterService(llm_provider=llm_provider, posts_dir=posts_dir)

    def write_post(
        self, summary: SummaryResult, publish_date: Optional[str] = None
    ) -> PostContent:
        """
        Gera e salva um post a partir de um SummaryResult.
        """
        return self.service.generate_post(summary, publish_date=publish_date)

    def write_posts_batch(
        self, summaries: List[SummaryResult], publish_date: Optional[str] = None
    ) -> List[PostContent]:
        """
        Gera e salva uma lista de posts a partir de múltiplos resumos.
        """
        return [
            self.service.generate_post(item, publish_date=publish_date)
            for item in summaries
        ]

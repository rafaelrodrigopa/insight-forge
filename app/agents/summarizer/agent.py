from typing import List, Optional

from app.agents.collector.schemas import CollectedContent
from app.agents.summarizer.schemas import SummaryResult
from app.agents.summarizer.service import SummarizerService
from app.providers.base import BaseLLMProvider


class SummarizerAgent:
    """
    Agente especialista responsável por consumir documentos e gerar resumos estruturados.
    """

    def __init__(self, llm_provider: Optional[BaseLLMProvider] = None):
        self.service = SummarizerService(llm_provider=llm_provider)

    def summarize(self, content: CollectedContent) -> SummaryResult:
        """
        Sumariza um único documento coletado.
        """
        return self.service.summarize(content)

    def summarize_batch(
        self, contents: List[CollectedContent]
    ) -> List[SummaryResult]:
        """
        Sumariza um conjunto de documentos coletados.
        """
        return [self.service.summarize(item) for item in contents]

from typing import List, Optional

from app.agents.collector.schemas import CollectedContent
from app.agents.prioritizer.schemas import PriorityDecision
from app.agents.prioritizer.service import PrioritizerService
from app.providers.base import BaseLLMProvider


class PrioritizerAgent:
    def __init__(self, llm_provider: Optional[BaseLLMProvider] = None):
        self.service = PrioritizerService(llm_provider=llm_provider)

    def evaluate(self, content: CollectedContent) -> PriorityDecision:
        return self.service.evaluate(content)

    def evaluate_batch(
        self, contents: List[CollectedContent]
    ) -> List[PriorityDecision]:
        return [self.service.evaluate(item) for item in contents]

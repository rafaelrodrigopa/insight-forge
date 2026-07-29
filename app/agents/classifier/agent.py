from typing import List, Optional

from app.agents.classifier.schemas import ClassificationResult
from app.agents.classifier.service import ClassifierService
from app.agents.collector.schemas import CollectedContent
from app.providers.base import BaseLLMProvider


class ClassifierAgent:
    def __init__(self, llm_provider: Optional[BaseLLMProvider] = None):
        self.service = ClassifierService(llm_provider=llm_provider)

    def classify(self, content: CollectedContent) -> ClassificationResult:
        return self.service.classify(content)

    def classify_batch(
        self, contents: List[CollectedContent]
    ) -> List[ClassificationResult]:
        return [self.service.classify(item) for item in contents]

from typing import Optional

from app.agents.critic.schemas import ReviewResult
from app.agents.critic.service import CriticService
from app.providers.base import BaseLLMProvider


class CriticAgent:
    def __init__(self, llm_provider: Optional[BaseLLMProvider] = None):
        self.service = CriticService(llm_provider=llm_provider)

    def review(self, markdown_text: str) -> ReviewResult:
        return self.service.review(markdown_text)

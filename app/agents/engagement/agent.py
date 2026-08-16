from typing import Optional

from app.agents.engagement.schemas import EngagementDecision, TargetPost
from app.agents.engagement.service import EngagementService
from app.providers.base import BaseLLMProvider


class EngagementAgent:
    """
    Agente especializado em avaliar e interagir autonomamente com a comunidade no LinkedIn.
    """

    def __init__(self, llm_provider: Optional[BaseLLMProvider] = None):
        self.service = EngagementService(llm_provider=llm_provider)

    def evaluate_and_comment(self, post: TargetPost) -> EngagementDecision:
        """
        Avalia o post da comunidade e gera o comentário/reação se alinhado ao perfil.
        """
        return self.service.evaluate_post(post)

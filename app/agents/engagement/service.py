import json
import re
from typing import Optional

from app.agents.engagement.prompt import ENGAGEMENT_EVALUATOR_PROMPT
from app.agents.engagement.schemas import EngagementDecision, TargetPost
from app.providers.base import BaseLLMProvider
from app.providers.gemini import GeminiChat


class EngagementService:
    """
    Serviço que utiliza LLM para avaliar relevância de posts do LinkedIn e redigir comentários autênticos.
    """

    def __init__(self, llm_provider: Optional[BaseLLMProvider] = None):
        self.llm = llm_provider or GeminiChat()

    def evaluate_post(self, post: TargetPost) -> EngagementDecision:
        """
        Avalia se um post deve receber interações e gera o comentário técnico caso positivo.
        """
        prompt = (
            f"{ENGAGEMENT_EVALUATOR_PROMPT}\n\n"
            f"Análise a seguinte publicação:\n"
            f"Título/Autor: {post.title} | {post.author or 'Desconhecido'}\n"
            f"Conteúdo do Post: {post.content[:1500]}\n\n"
            f"Responda EXCLUSIVAMENTE com o objeto JSON válido."
        )

        try:
            res = self.llm.generate(prompt)
            decision = self._parse_response(res.text)
            return decision
        except Exception as err:
            return EngagementDecision(
                should_engage=False,
                reasoning=f"Erro ao processar análise com IA: {err}",
            )

    @staticmethod
    def _parse_response(response_text: str) -> EngagementDecision:
        """
        Extrai e converte a resposta JSON do modelo em EngagementDecision.
        """
        json_match = re.search(r"\{[\s\S]*\}", response_text)
        if not json_match:
            return EngagementDecision(
                should_engage=False, reasoning="Resposta não continha JSON válido."
            )

        data = json.loads(json_match.group(0))
        should_engage = bool(data.get("should_engage", False))
        suggested_reaction = (data.get("suggested_reaction") or "LIKE").upper()
        generated_comment = data.get("generated_comment")
        reasoning = data.get("reasoning")

        if should_engage and not generated_comment:
            should_engage = False

        return EngagementDecision(
            should_engage=should_engage,
            suggested_reaction=suggested_reaction,
            generated_comment=generated_comment,
            reasoning=reasoning,
        )

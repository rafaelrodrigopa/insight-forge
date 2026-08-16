import re
from typing import Optional

from app.agents.collector.schemas import CollectedContent
from app.agents.prioritizer.prompt import PRIORITIZER_SYSTEM_PROMPT
from app.agents.prioritizer.schemas import PriorityDecision
from app.providers.base import BaseLLMProvider
from app.providers.gemini import GeminiChat


class PrioritizerService:
    def __init__(self, llm_provider: Optional[BaseLLMProvider] = None):
        self.llm = llm_provider or GeminiChat()

    def evaluate(self, content: CollectedContent) -> PriorityDecision:
        user_prompt = (
            f"Avalie a prioridade editorial da seguinte matéria:\n\n"
            f"Título: {content.title}\n"
            f"Conteúdo:\n{content.content[:1000]}\n"
        )
        try:
            res = self.llm.generate(
                prompt=user_prompt,
                system=PRIORITIZER_SYSTEM_PROMPT,
                temperature=0.3,
            )
            return self._parse_response(res.text)
        except Exception as err:
            return PriorityDecision(
                priority_score=70.0,
                should_publish=True,
                reasoning=f"Avaliado com prioridade padrão devido a: {err}",
            )

    @staticmethod
    def _parse_response(text: str) -> PriorityDecision:
        score = 75.0
        should_pub = True
        reasoning = "Conteúdo com boa relevância técnica."

        score_match = re.search(
            r"PONTUACAO_PRIORIDADE:\s*([\d.]+)", text, re.IGNORECASE
        )
        if score_match:
            try:
                score = float(score_match.group(1))
            except ValueError:
                score = 75.0

        pub_match = re.search(r"DEVE_PUBLICAR:\s*(SIM|NAO)", text, re.IGNORECASE)
        if pub_match:
            should_pub = pub_match.group(1).upper() == "SIM"

        reason_match = re.search(
            r"JUSTIFICATIVA:\s*(.+)", text, re.DOTALL | re.IGNORECASE
        )
        if reason_match:
            reasoning = reason_match.group(1).strip()

        return PriorityDecision(
            priority_score=score,
            should_publish=should_pub,
            reasoning=reasoning,
        )

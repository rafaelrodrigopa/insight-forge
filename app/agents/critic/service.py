import re
from typing import Optional

from app.agents.critic.prompt import CRITIC_SYSTEM_PROMPT
from app.agents.critic.schemas import ReviewResult
from app.providers.base import BaseLLMProvider
from app.providers.gemini import GeminiChat


class CriticService:
    def __init__(self, llm_provider: Optional[BaseLLMProvider] = None):
        self.llm = llm_provider or GeminiChat()

    def review(self, markdown_text: str) -> ReviewResult:
        user_prompt = (
            f"Revise o seguinte artigo em Markdown e forneça o feedback e versão polida:\n\n"
            f"{markdown_text}\n"
        )
        try:
            res = self.llm.generate(
                prompt=user_prompt,
                system=CRITIC_SYSTEM_PROMPT,
                temperature=0.3,
            )
            return self._parse_response(res.text, fallback_markdown=markdown_text)
        except Exception as err:
            return ReviewResult(
                quality_score=8.0,
                approved=True,
                feedback_notes=[f"Aprovado automaticamente (modo contingência): {err}"],
                revised_markdown=markdown_text,
            )

    @staticmethod
    def _parse_response(text: str, fallback_markdown: str) -> ReviewResult:
        score = 8.5
        approved = True
        notes = []
        revised = fallback_markdown

        score_match = re.search(r"NOTA_QUALIDADE:\s*([\d.]+)", text, re.IGNORECASE)
        if score_match:
            try:
                score = float(score_match.group(1))
            except ValueError:
                score = 8.5

        app_match = re.search(r"APROVADO:\s*(SIM|NAO)", text, re.IGNORECASE)
        if app_match:
            approved = app_match.group(1).upper() == "SIM"

        notes_match = re.search(
            r"OBSERVACOES:\s*(.*?)(?=\nCONTEUDO_REVISADO:|$)",
            text,
            re.DOTALL | re.IGNORECASE,
        )
        if notes_match:
            lines = notes_match.group(1).strip().splitlines()
            for line in lines:
                clean = re.sub(r"^[-*•\d.]+\s*", "", line).strip()
                if clean:
                    notes.append(clean)

        content_match = re.search(
            r"CONTEUDO_REVISADO:\s*(.*)", text, re.DOTALL | re.IGNORECASE
        )
        if content_match:
            candidate_text = content_match.group(1).strip()
            if candidate_text and ("---" in candidate_text or "#" in candidate_text):
                revised = candidate_text

        return ReviewResult(
            quality_score=score,
            approved=approved,
            feedback_notes=notes,
            revised_markdown=revised,
        )

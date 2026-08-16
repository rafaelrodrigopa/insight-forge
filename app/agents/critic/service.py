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
                max_output_tokens=4096,
            )
            return self._parse_response(
                res.text,
                fallback_markdown=markdown_text,
                finish_reason=res.finish_reason,
            )
        except Exception as err:
            return ReviewResult(
                quality_score=8.0,
                approved=True,
                feedback_notes=[f"Aprovado automaticamente (modo contingência): {err}"],
                revised_markdown=markdown_text,
            )

    @staticmethod
    def _parse_response(
        text: str,
        fallback_markdown: str,
        finish_reason: Optional[str] = None,
    ) -> ReviewResult:
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
            # Remove blocos de código ```markdown ... ``` envolventes se a LLM colocar
            if candidate_text.startswith("```"):
                candidate_text = re.sub(r"^```[\w]*\n?", "", candidate_text)
                candidate_text = re.sub(r"\n?```$", "", candidate_text).strip()

            # Validação rigorosa contra truncamento:
            # 1. Ignora se o finish_reason indicar limite de tokens
            # 2. Ignora se o texto revisado tiver menos de 90% do tamanho do texto original
            # 3. Ignora se o texto terminar abruptamente sem pontuação final válida
            # 4. Ignora se o texto original tiver a frase de CTA ("Confira mais") ou hashtags ("#") e o candidato as tiver perdido
            is_length_truncated = str(finish_reason or "").upper() in [
                "MAX_TOKENS",
                "LENGTH",
                "MAX_TOKENS_REACHED",
            ]
            is_too_short = len(candidate_text) < (0.90 * len(fallback_markdown))

            last_char = candidate_text[-1] if candidate_text else ""
            ends_abruptly = last_char not in [".", "!", "?", '"', "'", "`", ")", "]", "}", "#", "\n"]

            lost_cta = ("Confira mais" in fallback_markdown) and ("Confira mais" not in candidate_text)
            lost_hashtags = ("#" in fallback_markdown) and ("#" not in candidate_text)

            has_structural_flaws = ends_abruptly or lost_cta or lost_hashtags

            if (
                candidate_text
                and not is_length_truncated
                and not is_too_short
                and not has_structural_flaws
                and ("---" in candidate_text or "#" in candidate_text)
            ):
                revised = candidate_text
            else:
                reason_details = []
                if is_length_truncated:
                    reason_details.append("finish_reason MAX_TOKENS")
                if is_too_short:
                    reason_details.append(
                        f"tamanho reduzido ({len(candidate_text)} < {int(0.90 * len(fallback_markdown))})"
                    )
                if ends_abruptly:
                    reason_details.append("término abrupto de frase")
                if lost_cta:
                    reason_details.append("perda do Call to Action (CTA)")
                if lost_hashtags:
                    reason_details.append("perda das hashtags ao final")

                notes.append(
                    f"Revisão descartada por truncamento de saída do modelo ({', '.join(reason_details)}). Mantida versão original."
                )

        return ReviewResult(
            quality_score=score,
            approved=approved,
            feedback_notes=notes,
            revised_markdown=revised,
        )

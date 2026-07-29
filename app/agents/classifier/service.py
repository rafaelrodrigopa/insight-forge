import re
from typing import Optional

from app.agents.classifier.prompt import CLASSIFIER_SYSTEM_PROMPT
from app.agents.classifier.schemas import ClassificationResult
from app.agents.collector.schemas import CollectedContent
from app.providers.base import BaseLLMProvider
from app.providers.gemini import GeminiChat


class ClassifierService:
    def __init__(self, llm_provider: Optional[BaseLLMProvider] = None):
        self.llm = llm_provider or GeminiChat()

    def classify(self, content: CollectedContent) -> ClassificationResult:
        user_prompt = (
            f"Classifique o seguinte documento:\n\n"
            f"Título: {content.title}\n"
            f"Conteúdo:\n{content.content[:1000]}\n"
        )
        try:
            res = self.llm.generate(
                prompt=user_prompt,
                system=CLASSIFIER_SYSTEM_PROMPT,
                temperature=0.2,
            )
            return self._parse_response(res.text)
        except Exception:
            return ClassificationResult(
                primary_category="Python",
                secondary_categories=["Geral"],
                tags=["tecnologia"],
                confidence=0.5,
            )

    @staticmethod
    def _parse_response(text: str) -> ClassificationResult:
        primary = "Python"
        secondaries = []
        tags = []
        confidence = 0.9

        p_match = re.search(r"CATEGORIA_PRINCIPAL:\s*(.+)", text, re.IGNORECASE)
        if p_match:
            primary = p_match.group(1).strip()

        s_match = re.search(r"CATEGORIAS_SECUNDARIAS:\s*(.+)", text, re.IGNORECASE)
        if s_match:
            secondaries = [
                s.strip() for s in s_match.group(1).split(",") if s.strip()
            ]

        t_match = re.search(r"TAGS:\s*(.+)", text, re.IGNORECASE)
        if t_match:
            tags = [t.strip() for t in t_match.group(1).split(",") if t.strip()]

        c_match = re.search(r"CONFIANCA:\s*([\d.]+)", text, re.IGNORECASE)
        if c_match:
            try:
                confidence = float(c_match.group(1))
            except ValueError:
                confidence = 0.9

        return ClassificationResult(
            primary_category=primary,
            secondary_categories=secondaries,
            tags=tags,
            confidence=confidence,
        )

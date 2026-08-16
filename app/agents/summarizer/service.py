import re
from typing import List, Optional

from app.agents.collector.schemas import CollectedContent
from app.agents.summarizer.prompt import SUMMARIZER_SYSTEM_PROMPT
from app.agents.summarizer.schemas import SummaryResult
from app.providers.base import BaseLLMProvider
from app.providers.gemini import GeminiChat


class SummarizerService:
    """
    Serviço que consome documentos coletados e gera resumos estruturados utilizando LLM.
    """

    def __init__(self, llm_provider: Optional[BaseLLMProvider] = None):
        self.llm = llm_provider or GeminiChat()

    def summarize(self, content: CollectedContent) -> SummaryResult:
        """
        Gera um resumo estruturado a partir de um objeto CollectedContent.
        """
        user_prompt = (
            f"Analise o seguinte documento e forneça o resumo no formato especificado:\n\n"
            f"Título Original: {content.title}\n"
            f"Fonte: {content.source}\n"
            f"URL: {content.url}\n"
            f"Conteúdo:\n{content.content}\n"
        )

        try:
            response = self.llm.generate(
                prompt=user_prompt,
                system=SUMMARIZER_SYSTEM_PROMPT,
                temperature=0.3,
            )
            parsed_result = self._parse_llm_response(
                text=response.text,
                fallback_title=content.title,
                source_url=content.url,
            )
            return parsed_result
        except Exception as error:
            # Em caso de falha no provedor ou parsing, gera um resultado fallback gracioso
            return SummaryResult(
                title=content.title,
                summary=f"Resumo não gerado devido a erro: {str(error)}",
                key_points=[content.content[:200]] if content.content else [],
                topics=["Geral"],
                relevance_score=5.0,
                source_url=content.url,
                raw_content_title=content.title,
            )

    def _parse_llm_response(
        self, text: str, fallback_title: str, source_url: Optional[str] = None
    ) -> SummaryResult:
        """
        Parse do texto bruto de resposta do LLM para a estrutura SummaryResult.
        """
        title = fallback_title
        summary = ""
        key_points: List[str] = []
        topics: List[str] = []
        relevance_score = 7.0

        title_match = re.search(r"TITULO:\s*(.+)", text, re.IGNORECASE)
        if title_match:
            title = title_match.group(1).strip()

        summary_match = re.search(
            r"RESUMO:\s*(.*?)(?=\nPONTOS_CHAVE:|\nTOPICOS:|\nRELEVANCIA:|$)",
            text,
            re.DOTALL | re.IGNORECASE,
        )
        if summary_match:
            summary = summary_match.group(1).strip()
        else:
            summary = text.strip()

        key_points_match = re.search(
            r"PONTOS_CHAVE:\s*(.*?)(?=\nTOPICOS:|\nRELEVANCIA:|$)",
            text,
            re.DOTALL | re.IGNORECASE,
        )
        if key_points_match:
            points_block = key_points_match.group(1).strip()
            for line in points_block.splitlines():
                clean_line = re.sub(r"^[-*•\d.]+\s*", "", line).strip()
                if clean_line:
                    key_points.append(clean_line)

        topics_match = re.search(r"TOPICOS:\s*(.+)", text, re.IGNORECASE)
        if topics_match:
            raw_topics = topics_match.group(1).strip()
            topics = [t.strip() for t in raw_topics.split(",") if t.strip()]

        relevance_match = re.search(r"RELEVANCIA:\s*([\d.]+)", text, re.IGNORECASE)
        if relevance_match:
            try:
                relevance_score = float(relevance_match.group(1))
            except ValueError:
                relevance_score = 7.0

        return SummaryResult(
            title=title,
            summary=summary,
            key_points=key_points,
            topics=topics,
            relevance_score=relevance_score,
            source_url=source_url,
            raw_content_title=fallback_title,
        )

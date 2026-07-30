from dataclasses import dataclass, field
from datetime import datetime
import re
from typing import Any, Dict, List, Optional

from app.config.topics import TopicsConfig, topics_config
from app.agents.summarizer.schemas import SummaryResult


@dataclass
class RankedContent:
    """
    Objeto contendo a pontuação final (0-100) e os metadados de classificação do conteúdo.
    """

    item: Any
    score: float
    matched_topics: List[str] = field(default_factory=list)
    breakdown: Dict[str, float] = field(default_factory=dict)


class ContentScorer:
    """
    Mecanismo de pontuação de relevância e ranking para o Insight Forge.
    """

    def __init__(self, config: Optional[TopicsConfig] = None):
        self.topics_config = config or topics_config

    def score_content(
        self, item: Any, summary: Optional[SummaryResult] = None
    ) -> RankedContent:
        """
        Calcula a pontuação consolidada (0 a 100) de um item coletado ou resumido.
        """
        title = getattr(item, "title", str(item))
        content_text = getattr(item, "content", "")
        pub_date = getattr(item, "published_at", None)

        full_text = f"{title} {content_text}".lower()

        # 1. Pontuação por Tópicos (Máx: 40 pts)
        topic_score, matched_topics = self._calculate_topic_score(full_text)

        # 2. Pontuação por IA / Relevância (Máx: 30 pts)
        ai_score = self._calculate_ai_score(summary)

        # 3. Pontuação de Recência (Máx: 30 pts)
        recency_score = self._calculate_recency_score(pub_date)

        total_score = min(
            100.0, round(topic_score + ai_score + recency_score, 1)
        )

        return RankedContent(
            item=item,
            score=total_score,
            matched_topics=matched_topics,
            breakdown={
                "topic_score": topic_score,
                "ai_score": ai_score,
                "recency_score": recency_score,
            },
        )

    def rank_items(
        self, items: List[Any], summaries: Optional[List[SummaryResult]] = None
    ) -> List[RankedContent]:
        """
        Calcula o score de uma lista de itens e os ordena do maior para o menor score.
        """
        summary_map = {}
        if summaries:
            for s in summaries:
                summary_map[s.raw_content_title or s.title] = s

        ranked_list = []
        for item in items:
            title = getattr(item, "title", str(item))
            sum_obj = summary_map.get(title)
            ranked_list.append(self.score_content(item, summary=sum_obj))

        return sorted(ranked_list, key=lambda r: r.score, reverse=True)

    def _calculate_topic_score(self, text: str) -> (float, List[str]):
        matched = []
        accumulated_weight = 0.0

        # Mapeamento com variações regex precisas para evitar falsos positivos (ex: "ia" dentro de "notícia")
        topic_patterns = {
            "power_bi": r"\b(power\s*bi|dax|powerquery)\b",
            "powerbi": r"\b(power\s*bi|dax|powerquery)\b",
            "microsoft_fabric": r"\b(microsoft\s+fabric|fabric)\b",
            "fabric": r"\b(microsoft\s+fabric|fabric)\b",
            "dax": r"\bdax\b",
            "analytics": r"\b(analytics|bi|business\s+intelligence|dataform)\b",
            "bigquery": r"\b(bigquery|gcp\s+analytics)\b",
            "dataform": r"\bdataform\b",
            "engenharia_de_dados": r"\b(engenharia\s+de\s+dados|data\s+engineering|pipeline\s+de\s+dados)\b",
            "data_engineering": r"\b(data\s+engineering|engenharia\s+de\s+dados)\b",
            "python": r"\bpython\b",
            "sql": r"\bsql\b",
            "ia": r"\b(ia|inteligência\s+artificial|artificial\s+intelligence|llm|gpt)\b",
            "machine_learning": r"\b(machine\s+learning|aprendizado\s+de\s+máquina)\b",
            "cloud": r"\b(cloud|nuvem|azure|gcp|aws)\b",
            "automacao": r"\b(automação|automation)\b",
        }

        for topic in self.topics_config.get_all_topics():
            weight = self.topics_config.get_weight(topic)
            pattern = topic_patterns.get(
                topic, r"\b" + re.escape(topic.replace("_", " ")) + r"\b"
            )
            if re.search(pattern, text, re.IGNORECASE):
                matched.append(topic)
                accumulated_weight += weight

        score = min(40.0, accumulated_weight * 2.0)
        return round(score, 1), matched

    @staticmethod
    def _calculate_ai_score(summary: Optional[SummaryResult]) -> float:
        if not summary or summary.relevance_score is None:
            return 15.0  # Pontuação neutra caso não haja análise de IA prévia

        # Escala de 0-10 para 0-30 pts
        return round(summary.relevance_score * 3.0, 1)

    @staticmethod
    def _calculate_recency_score(pub_date: Optional[str]) -> float:
        if not pub_date:
            return 20.0  # Valor padrão para datas não especificadas

        # Se for string de data ISO ou pubDate RSS padrão
        now = datetime.now()
        try:
            # Tenta extrair ano e converter data simples
            for fmt in (
                "%Y-%m-%d",
                "%a, %d %b %Y %H:%M:%S %Z",
                "%a, %d %b %Y %H:%M:%S GMT",
            ):
                try:
                    dt = datetime.strptime(pub_date.strip(), fmt)
                    days_old = (now - dt).days
                    if days_old <= 1:
                        return 30.0
                    elif days_old <= 7:
                        return 25.0
                    elif days_old <= 30:
                        return 15.0
                    else:
                        return 5.0
                except ValueError:
                    continue
        except Exception:
            pass

        return 20.0

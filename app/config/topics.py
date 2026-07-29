from typing import Dict, List, Tuple


class TopicsConfig:
    """
    Gerenciador de tópicos de interesse e pesos estratégicos editoriais para o Ranking Engine.
    """

    DEFAULT_TOPICS: Dict[str, int] = {
        "ia": 10,
        "python": 10,
        "engenharia_de_dados": 10,
        "analytics": 10,
        "bigquery": 9,
        "power_bi": 9,
        "sql": 8,
        "cloud": 8,
        "automacao": 8,
        "linkedin": 7,
        "carreira": 5,
    }

    def __init__(self, custom_topics: Dict[str, int] | None = None):
        self._topics: Dict[str, int] = (
            custom_topics.copy() if custom_topics else self.DEFAULT_TOPICS.copy()
        )

    def get_weight(self, topic: str) -> int:
        """
        Retorna o peso editorial de um tópico (0 se não monitorado).
        """
        return self._topics.get(topic.lower().strip(), 0)

    def get_all_topics(self) -> List[str]:
        """
        Retorna a lista com os nomes de todos os tópicos monitorados.
        """
        return list(self._topics.keys())

    def get_ranked_topics(self) -> List[Tuple[str, int]]:
        """
        Retorna a lista de tópicos ordenada do maior para o menor peso.
        """
        return sorted(self._topics.items(), key=lambda item: item[1], reverse=True)

    def is_relevant(self, topic: str, min_weight: int = 5) -> bool:
        """
        Verifica se um tópico atinge o peso mínimo de relevância.
        """
        return self.get_weight(topic) >= min_weight

    def set_weight(self, topic: str, weight: int) -> None:
        """
        Define ou altera o peso de um determinado tópico (0 a 10).
        """
        normalized_weight = max(0, min(10, weight))
        self._topics[topic.lower().strip()] = normalized_weight


topics_config = TopicsConfig()

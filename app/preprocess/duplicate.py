from collections import Counter
import math
import re
from typing import List, TypeVar

T = TypeVar("T")


class ContentDeduplicator:
    """
    Mecanismo de deduplicação semântica baseado em similaridade de cosseno de termos (TF-IDF/N-grams).
    """

    def __init__(self, similarity_threshold: float = 0.60):
        self.threshold = similarity_threshold

    def deduplicate(self, items: List[T], text_extractor=None) -> List[T]:
        """
        Filtra e remove itens duplicados ou altamente similares da lista informada.
        """
        if not items:
            return []

        if text_extractor is None:

            def text_extractor(obj):
                if hasattr(obj, "title") and hasattr(obj, "content"):
                    return f"{obj.title} {obj.content}"
                if isinstance(obj, dict):
                    return f"{obj.get('title', '')} {obj.get('content', '')}"
                return str(obj)

        unique_items: List[T] = []
        vectors: List[Counter] = []

        for item in items:
            text = text_extractor(item)
            vector = self._text_to_vector(text)

            is_duplicate = False
            for existing_vec in vectors:
                similarity = self._cosine_similarity(vector, existing_vec)
                if similarity >= self.threshold:
                    is_duplicate = True
                    break

            if not is_duplicate:
                unique_items.append(item)
                vectors.append(vector)

        return unique_items

    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calcula o índice de similaridade (0.0 a 1.0) entre dois textos.
        """
        v1 = self._text_to_vector(text1)
        v2 = self._text_to_vector(text2)
        return self._cosine_similarity(v1, v2)

    @staticmethod
    def _text_to_vector(text: str) -> Counter:
        """
        Converte um texto em um vetor de contagem de palavras/n-gramas limpos.
        """
        words = re.findall(r"\w+", text.lower())
        # Filtra stopwords comuns em inglês e português
        stopwords = {
            "o",
            "a",
            "os",
            "as",
            "um",
            "uma",
            "de",
            "do",
            "da",
            "em",
            "para",
            "com",
            "não",
            "por",
            "que",
            "se",
            "e",
            "ou",
            "the",
            "a",
            "an",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "and",
            "or",
            "is",
            "are",
        }
        filtered_words = [w for w in words if len(w) > 2 and w not in stopwords]
        return Counter(filtered_words)

    @staticmethod
    def _cosine_similarity(vec1: Counter, vec2: Counter) -> float:
        """
        Calcula a similaridade de cosseno entre dois vetores de frequência.
        """
        intersection = set(vec1.keys()) & set(vec2.keys())
        numerator = sum(vec1[x] * vec2[x] for x in intersection)

        sum1 = sum(vec1[x] ** 2 for x in vec1.keys())
        sum2 = sum(vec2[x] ** 2 for x in vec2.keys())
        denominator = math.sqrt(sum1) * math.sqrt(sum2)

        if not denominator:
            return 0.0
        return float(numerator) / denominator

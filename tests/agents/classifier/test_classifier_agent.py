import unittest
from unittest.mock import MagicMock

from app.agents.classifier import ClassificationResult, ClassifierAgent
from app.agents.collector.schemas import CollectedContent
from app.providers import LLMResponse


SAMPLE_CLASSIFICATION = """CATEGORIA_PRINCIPAL: IA
CATEGORIAS_SECUNDARIAS: Python, Engenharia de Dados
TAGS: LLM, Multiagente, CrewAI
CONFIANCA: 0.95
"""


class TestClassifierAgent(unittest.TestCase):

    def setUp(self):
        self.sample_content = CollectedContent(
            title="Desenvolvimento Multiagente com Python",
            content="Artigo sobre orquestração de IA com CrewAI.",
            source="Tech Blog",
            url="https://tech.com/multiagent",
        )

    def test_classifier_agent_parsing(self):
        mock_llm = MagicMock()
        mock_llm.generate.return_value = LLMResponse(
            text=SAMPLE_CLASSIFICATION, model="gemini-3.5-flash"
        )

        agent = ClassifierAgent(llm_provider=mock_llm)
        result = agent.classify(self.sample_content)

        self.assertIsInstance(result, ClassificationResult)
        self.assertEqual(result.primary_category, "IA")
        self.assertIn("Python", result.secondary_categories)
        self.assertIn("LLM", result.tags)
        self.assertEqual(result.confidence, 0.95)


if __name__ == "__main__":
    unittest.main()

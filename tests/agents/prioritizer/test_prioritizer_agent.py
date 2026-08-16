import unittest
from unittest.mock import MagicMock

from app.agents.collector.schemas import CollectedContent
from app.agents.prioritizer import PriorityDecision, PrioritizerAgent
from app.providers import LLMResponse


SAMPLE_PRIORITY = """PONTUACAO_PRIORIDADE: 88.5
DEVE_PUBLICAR: SIM
JUSTIFICATIVA: Assunto de grande interesse para a comunidade de dados.
"""


class TestPrioritizerAgent(unittest.TestCase):

    def setUp(self):
        self.sample_content = CollectedContent(
            title="Novidades no BigQuery e Python",
            content="Novos recursos de análise preditiva.",
            source="Data Weekly",
            url="https://data.com/news",
        )

    def test_prioritizer_agent_evaluation(self):
        mock_llm = MagicMock()
        mock_llm.generate.return_value = LLMResponse(
            text=SAMPLE_PRIORITY, model="gemini-3.5-flash"
        )

        agent = PrioritizerAgent(llm_provider=mock_llm)
        result = agent.evaluate(self.sample_content)

        self.assertIsInstance(result, PriorityDecision)
        self.assertEqual(result.priority_score, 88.5)
        self.assertTrue(result.should_publish)
        self.assertIn("comunidade de dados", result.reasoning)


if __name__ == "__main__":
    unittest.main()

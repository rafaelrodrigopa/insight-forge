import unittest
from unittest.mock import MagicMock

from app.agents.collector.schemas import CollectedContent
from app.agents.summarizer import SummarizerAgent, SummarizerService, SummaryResult
from app.providers import LLMResponse


SAMPLE_LLM_TEXT_RESPONSE = """TITULO: Resumo - Python 3.15 Lançado com Sucesso
RESUMO: A nova versão do Python 3.15 traz melhorias significativas de desempenho e simplificações sintáticas para desenvolvedores de software.
PONTOS_CHAVE:
- Desempenho aprimorado em tempo de execução
- Novas sintaxes para tipagem estática
- Otimização no consumo de memória
TOPICOS: Python, Performance, Desenvolvimento
RELEVANCIA: 9.5
"""


class TestSummarizerAgent(unittest.TestCase):

    def setUp(self):
        self.sample_content = CollectedContent(
            title="Python 3.15 Lançado com Sucesso",
            content="Nova versão traz melhorias de desempenho e novas sintaxes.",
            source="Python Org",
            url="https://www.python.org/blog/python-3-15/",
            published_at="2026-07-27",
        )

    def test_summarizer_service_parsing(self):
        """Testa a geração e parsing do resumo estruturado via LLM Provider."""
        mock_llm = MagicMock()
        mock_llm.generate.return_value = LLMResponse(
            text=SAMPLE_LLM_TEXT_RESPONSE,
            model="gemini-2.0-flash",
        )

        service = SummarizerService(llm_provider=mock_llm)
        result = service.summarize(self.sample_content)

        self.assertIsInstance(result, SummaryResult)
        self.assertEqual(result.title, "Resumo - Python 3.15 Lançado com Sucesso")
        self.assertIn("nova versão do Python 3.15", result.summary)
        self.assertEqual(len(result.key_points), 3)
        self.assertIn("Desempenho aprimorado em tempo de execução", result.key_points)
        self.assertEqual(result.topics, ["Python", "Performance", "Desenvolvimento"])
        self.assertEqual(result.relevance_score, 9.5)
        self.assertEqual(result.source_url, "https://www.python.org/blog/python-3-15/")

    def test_summarizer_agent_batch(self):
        """Testa a sumarização em lote pelo SummarizerAgent."""
        mock_llm = MagicMock()
        mock_llm.generate.return_value = LLMResponse(
            text=SAMPLE_LLM_TEXT_RESPONSE,
            model="gemini-2.0-flash",
        )

        agent = SummarizerAgent(llm_provider=mock_llm)
        results = agent.summarize_batch([self.sample_content, self.sample_content])

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].title, "Resumo - Python 3.15 Lançado com Sucesso")
        self.assertEqual(results[1].relevance_score, 9.5)

    def test_summarizer_fallback_on_exception(self):
        """Testa a resiliência/fallback caso o LLM retorne erro."""
        mock_llm = MagicMock()
        mock_llm.generate.side_effect = RuntimeError("Conexão indisponível")

        agent = SummarizerAgent(llm_provider=mock_llm)
        result = agent.summarize(self.sample_content)

        self.assertEqual(result.title, "Python 3.15 Lançado com Sucesso")
        self.assertIn("Resumo não gerado devido a erro", result.summary)
        self.assertEqual(result.relevance_score, 5.0)


if __name__ == "__main__":
    unittest.main()

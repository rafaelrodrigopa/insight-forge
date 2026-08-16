import unittest
from unittest.mock import MagicMock, patch

from app.agents.collector import (
    CollectedContent,
    CollectorAgent,
    CollectorService,
    RSSFetcher,
)
from app.providers import LLMResponse


SAMPLE_RSS_XML = """<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
<channel>
 <title>Python Blog Teste</title>
 <link>https://www.python.org/blog/</link>
 <description>Feed de teste de notícias Python</description>
 <item>
  <title>Python 3.15 Lançado com Sucesso</title>
  <link>https://www.python.org/blog/python-3-15/</link>
  <description>&lt;p&gt;Nova versão traz melhorias de desempenho e novas sintaxes.&lt;/p&gt;</description>
  <pubDate>Mon, 27 Jul 2026 12:00:00 GMT</pubDate>
 </item>
</channel>
</rss>
"""


class TestCollectorAgent(unittest.TestCase):

    @patch("requests.get")
    def test_rss_fetcher_parse(self, mock_requests_get):
        """Testa a busca e parsing de RSS XML pelo RSSFetcher."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = SAMPLE_RSS_XML.encode("utf-8")
        mock_requests_get.return_value = mock_response

        fetcher = RSSFetcher()
        items = fetcher.fetch_feed("https://www.python.org/blog/rss")

        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["title"], "Python 3.15 Lançado com Sucesso")
        self.assertEqual(items[0]["url"], "https://www.python.org/blog/python-3-15/")
        self.assertIn("Nova versão traz melhorias", items[0]["content"])

    def test_collector_service_with_mocks(self):
        """Testa o CollectorService orquestrando a busca RSS e análise de IA."""
        mock_fetcher = MagicMock()
        mock_fetcher.fetch_feed.return_value = [
            {
                "id": "123",
                "title": "IA Revoluciona Engenharia de Dados",
                "url": "https://example.com/ia-data",
                "content": "Artigo sobre IA e BigQuery",
                "source": "Tech News",
                "published_at": "2026-07-29",
            }
        ]

        mock_llm = MagicMock()
        mock_llm.generate.return_value = LLMResponse(
            text="Conteúdo de alta relevância sobre IA.",
            model="gemini-2.0-flash",
        )

        service = CollectorService(llm_provider=mock_llm, rss_fetcher=mock_fetcher)
        results = service.collect(
            "https://example.com/feed.xml", analyze_with_ai=True
        )

        self.assertEqual(len(results), 1)
        self.assertIsInstance(results[0], CollectedContent)
        self.assertEqual(results[0].title, "IA Revoluciona Engenharia de Dados")
        self.assertEqual(results[0].ai_analysis, "Conteúdo de alta relevância sobre IA.")

    def test_collector_agent_collect_raw_text(self):
        """Testa o CollectorAgent coletando texto direto sem IA."""
        agent = CollectorAgent(llm_provider=MagicMock(), rss_fetcher=MagicMock())
        results = agent.collect("Texto explicativo direto", analyze_with_ai=False)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].title, "Conteúdo Coletado Direto")
        self.assertEqual(results[0].content, "Texto explicativo direto")
        self.assertIsNone(results[0].ai_analysis)


if __name__ == "__main__":
    unittest.main()

import os
import tempfile
import unittest
from unittest.mock import MagicMock

from app.agents.summarizer.schemas import SummaryResult
from app.agents.writer import PostContent, WriterAgent, WriterService
from app.providers import LLMResponse


SAMPLE_ARTICLE_MARKDOWN = """# Python 3.15 Lançado com Sucesso!

O lançamento da versão 3.15 do Python marca um avanço importante em performance e ergonomia de código.

## Principais Novidades
- Execução mais rápida
- Menor footprint de memória

## Conclusão
Qual sua novidade favorita nesta release? Deixe nos comentários!
"""


class TestWriterAgent(unittest.TestCase):

    def setUp(self):
        self.sample_summary = SummaryResult(
            title="Python 3.15 Lançado com Sucesso",
            summary="A nova versão do Python traz melhorias de desempenho.",
            key_points=["Execução mais rápida", "Menor uso de memória"],
            topics=["Python", "Performance"],
            relevance_score=9.5,
            source_url="https://www.python.org/blog/python-3-15/",
        )

    def test_writer_service_generate_post_and_save(self):
        """Testa se o WriterService gera o post e salva no disco corretamente."""
        mock_llm = MagicMock()
        mock_llm.generate.return_value = LLMResponse(
            text=SAMPLE_ARTICLE_MARKDOWN,
            model="gemini-2.0-flash",
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            service = WriterService(llm_provider=mock_llm, posts_dir=temp_dir)
            post = service.generate_post(self.sample_summary, publish_date="2026-07-29")

            self.assertIsInstance(post, PostContent)
            self.assertEqual(post.slug, "python-315-lancado-com-sucesso")
            self.assertEqual(post.date, "2026-07-29")
            self.assertTrue(os.path.exists(post.file_path))

            with open(post.file_path, "r", encoding="utf-8") as f:
                saved_content = f.read()

            self.assertIn('title: "Python 3.15 Lançado com Sucesso"', saved_content)
            self.assertIn("Python 3.15 Lançado com Sucesso!", saved_content)

    def test_writer_agent_batch(self):
        """Testa o WriterAgent processando um lote de resumos."""
        mock_llm = MagicMock()
        mock_llm.generate.return_value = LLMResponse(
            text=SAMPLE_ARTICLE_MARKDOWN,
            model="gemini-2.0-flash",
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            agent = WriterAgent(llm_provider=mock_llm, posts_dir=temp_dir)
            posts = agent.write_posts_batch(
                [self.sample_summary, self.sample_summary], publish_date="2026-07-29"
            )

            self.assertEqual(len(posts), 2)
            self.assertTrue(os.path.exists(posts[0].file_path))
            self.assertTrue(os.path.exists(posts[1].file_path))

    def test_writer_fallback_on_llm_exception(self):
        """Testa a geração em modo de contingência caso o LLM apresente erro."""
        mock_llm = MagicMock()
        mock_llm.generate.side_effect = RuntimeError("Erro no provedor LLM")

        with tempfile.TemporaryDirectory() as temp_dir:
            agent = WriterAgent(llm_provider=mock_llm, posts_dir=temp_dir)
            post = agent.write_post(self.sample_summary, publish_date="2026-07-29")

            self.assertIn("modo de contingência", post.content_md)
            self.assertTrue(os.path.exists(post.file_path))


if __name__ == "__main__":
    unittest.main()

import unittest
from app.agents.collector.schemas import CollectedContent
from app.agents.summarizer.schemas import SummaryResult
from app.config.topics import TopicsConfig
from app.ranking import ContentScorer, RankedContent


class TestRankingEngine(unittest.TestCase):

    def setUp(self):
        self.config = TopicsConfig(
            custom_topics={
                "python": 10,
                "ia": 10,
                "carreira": 2,
            }
        )
        self.scorer = ContentScorer(config=self.config)

        self.high_value_item = CollectedContent(
            title="Avanços em IA Generativa com Python e Inteligência Artificial",
            content="Como a IA e o Python estão revolucionando a indústria de software.",
            source="AI Journal",
            url="https://ai.org/news",
            published_at="2026-07-29",
        )

        self.low_value_item = CollectedContent(
            title="Dicas de Carreira para Desenvolvedores",
            content="Como organizar seu currículo e se preparar para entrevistas.",
            source="Blog Geral",
            url="https://blog.com/carreira",
            published_at="2026-07-01",
        )

    def test_score_content(self):
        """Testa o cálculo de pontuação para itens de alta e baixa relevância."""
        high_ranked = self.scorer.score_content(self.high_value_item)
        low_ranked = self.scorer.score_content(self.low_value_item)

        self.assertIsInstance(high_ranked, RankedContent)
        self.assertGreater(high_ranked.score, low_ranked.score)
        self.assertIn("python", high_ranked.matched_topics)
        self.assertIn("ia", high_ranked.matched_topics)

    def test_rank_items_sorting(self):
        """Testa se o método rank_items ordena corretamente do maior para o menor score."""
        items = [self.low_value_item, self.high_value_item]
        ranked_list = self.scorer.rank_items(items)

        self.assertEqual(len(ranked_list), 2)
        self.assertEqual(ranked_list[0].item, self.high_value_item)
        self.assertEqual(ranked_list[1].item, self.low_value_item)

    def test_score_with_ai_summary(self):
        """Testa a integração da pontuação da IA com o score total."""
        summary = SummaryResult(
            title="Avanços em IA Generativa com Python",
            summary="Resumo de teste",
            relevance_score=10.0,
        )

        ranked = self.scorer.score_content(self.high_value_item, summary=summary)
        self.assertEqual(ranked.breakdown["ai_score"], 30.0)


if __name__ == "__main__":
    unittest.main()

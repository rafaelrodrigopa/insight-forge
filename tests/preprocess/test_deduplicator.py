import unittest
from app.agents.collector.schemas import CollectedContent
from app.preprocess import ContentDeduplicator


class TestContentDeduplicator(unittest.TestCase):

    def setUp(self):
        self.deduplicator = ContentDeduplicator(similarity_threshold=0.70)

        self.doc1 = CollectedContent(
            title="Lançamento do Python 3.15 com melhorias de velocidade",
            content="A nova versão do Python traz diversas otimizações de performance e sintaxe.",
            source="Blog Python",
            url="https://python.org/blog/315",
        )

        # Doc 2 é praticamente igual ao Doc 1 de outra fonte
        self.doc2 = CollectedContent(
            title="Python 3.15 Lançado com Melhorias de Velocidade e Performance",
            content="A nova versão do Python traz diversas otimizações de performance e sintaxe.",
            source="Tech News",
            url="https://technews.com/python-315",
        )

        # Doc 3 é um assunto totalmente diferente
        self.doc3 = CollectedContent(
            title="Novidades no BigQuery e Cloud SQL",
            content="Google Cloud anuncia novas ferramentas de análise de dados em escala.",
            source="Cloud Weekly",
            url="https://cloud.com/news",
        )

    def test_calculate_similarity(self):
        """Testa o cálculo de similaridade entre dois textos similares e distintos."""
        sim_high = self.deduplicator.calculate_similarity(
            self.doc1.title, self.doc2.title
        )
        sim_low = self.deduplicator.calculate_similarity(
            self.doc1.title, self.doc3.title
        )

        self.assertGreater(sim_high, 0.60)
        self.assertLess(sim_low, 0.30)

    def test_deduplicate_list(self):
        """Testa se itens duplicados são removidos mantendo o único de destaque."""
        items = [self.doc1, self.doc2, self.doc3]
        unique_items = self.deduplicator.deduplicate(items)

        self.assertEqual(len(unique_items), 2)
        self.assertIn(self.doc1, unique_items)
        self.assertIn(self.doc3, unique_items)
        self.assertNotIn(self.doc2, unique_items)


if __name__ == "__main__":
    unittest.main()

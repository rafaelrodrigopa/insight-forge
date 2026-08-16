import unittest
from unittest.mock import MagicMock

from app.agents.critic import CriticAgent, ReviewResult
from app.providers import LLMResponse


SAMPLE_CRITIC_RESPONSE = """NOTA_QUALIDADE: 9.0
APROVADO: SIM
OBSERVACOES:
- Excelente fluidez e gancho inicial
- Formatação Markdown limpa
CONTEUDO_REVISADO:
---
title: "Artigo Revisado"
---
# Artigo Polido pelo CriticAgent
Texto revisado de alta qualidade.
"""


class TestCriticAgent(unittest.TestCase):

    def test_critic_agent_review(self):
        mock_llm = MagicMock()
        mock_llm.generate.return_value = LLMResponse(
            text=SAMPLE_CRITIC_RESPONSE, model="gemini-3.5-flash"
        )

        agent = CriticAgent(llm_provider=mock_llm)
        result = agent.review("# Texto Original\nTexto rascunho.")

        self.assertIsInstance(result, ReviewResult)
        self.assertEqual(result.quality_score, 9.0)
        self.assertTrue(result.approved)
        self.assertIn("Excelente fluidez", result.feedback_notes[0])
        self.assertIn("Artigo Polido", result.revised_markdown)


if __name__ == "__main__":
    unittest.main()

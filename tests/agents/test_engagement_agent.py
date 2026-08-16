import unittest
from unittest.mock import MagicMock, patch

from app.agents.engagement.agent import EngagementAgent
from app.agents.engagement.discoverer import PostDiscoverer
from app.agents.engagement.schemas import EngagementDecision, TargetPost
from app.agents.engagement.service import EngagementService


class TestEngagementModule(unittest.TestCase):

    def test_target_post_creation(self):
        post = TargetPost(
            post_urn="urn:li:activity:7123456789012345678",
            url="https://www.linkedin.com/posts/test-activity-7123456789012345678-abcd",
            title="Post de Teste Power BI",
            content="Conteudo sobre Microsoft Fabric e Power BI",
            topic="Power BI",
        )
        self.assertEqual(post.post_urn, "urn:li:activity:7123456789012345678")
        self.assertEqual(post.topic, "Power BI")

    def test_extract_linkedin_urn_variations(self):
        url1 = "https://www.linkedin.com/posts/user_powerbi-activity-7123456789012345678-xyz"
        url2 = "https://www.linkedin.com/feed/update/urn:li:share:9876543210987654321"

        urn1 = PostDiscoverer.extract_linkedin_urn(url1)
        urn2 = PostDiscoverer.extract_linkedin_urn(url2)

        self.assertEqual(urn1, "urn:li:activity:7123456789012345678")
        self.assertEqual(urn2, "urn:li:share:9876543210987654321")

    def test_engagement_service_parse_response_success(self):
        json_str = """
        {
          "should_engage": true,
          "suggested_reaction": "LIKE",
          "generated_comment": "Excelente otimizacao no Fabric!",
          "reasoning": "Post muito relevante sobre Power BI."
        }
        """
        decision = EngagementService._parse_response(json_str)
        self.assertTrue(decision.should_engage)
        self.assertEqual(decision.suggested_reaction, "LIKE")
        self.assertEqual(decision.generated_comment, "Excelente otimizacao no Fabric!")

    def test_engagement_agent_with_mock_llm(self):
        mock_llm = MagicMock()
        mock_llm.generate.return_value.text = """
        {
          "should_engage": true,
          "suggested_reaction": "PRAISE",
          "generated_comment": "Otima analise sobre BigQuery!",
          "reasoning": "Alinhado com a stack."
        }
        """

        agent = EngagementAgent(llm_provider=mock_llm)
        post = TargetPost(
            post_urn="urn:li:activity:1112223334445556667",
            url="https://example.com",
            title="BigQuery Test",
            content="Conteudo sobre GCP BigQuery e Dataform",
        )

        decision = agent.evaluate_and_comment(post)
        self.assertTrue(decision.should_engage)
        self.assertEqual(decision.suggested_reaction, "PRAISE")
        self.assertEqual(decision.generated_comment, "Otima analise sobre BigQuery!")


if __name__ == "__main__":
    unittest.main()

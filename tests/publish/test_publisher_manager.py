import os
import unittest
from unittest.mock import MagicMock, patch

from app.agents.writer.schemas import PostContent
from app.publish.base import BasePublisher, PublishResult
from app.publish.manager import PublisherManager
from app.publish.publishers.linkedin_publisher import LinkedInPublisherAdapter
from app.publish.publishers.markdown_publisher import MarkdownPublisher


class DummyPublisher(BasePublisher):
    def __init__(self, name="Dummy", should_succeed=True):
        super().__init__(name=name)
        self.should_succeed = should_succeed

    def publish(self, post: PostContent) -> PublishResult:
        return PublishResult(
            publisher_name=self.name,
            success=self.should_succeed,
            post_url="http://dummy.url" if self.should_succeed else None,
            message="Dummy publish result",
        )


class TestPublisherEcosystem(unittest.TestCase):

    def setUp(self):
        self.sample_post = PostContent(
            title="Post de Teste",
            slug="post-de-teste",
            date="2026-07-30",
            content_md="# Post de Teste\nConteudo de teste.",
            topics=["Python", "Testes"],
            source_url="https://example.com",
            file_path="posts/2026-07-30-post-de-teste.md",
        )

    def test_markdown_publisher_success(self):
        publisher = MarkdownPublisher(posts_dir="posts")
        res = publisher.publish(self.sample_post)

        self.assertTrue(res.success)
        self.assertEqual(res.publisher_name, "Markdown Local/Git")
        self.assertIn("posts/2026-07-30-post-de-teste.md", res.post_url)

    @patch("app.publish.publishers.linkedin_publisher.settings")
    def test_linkedin_publisher_without_credentials(self, mock_settings):
        mock_settings.LINKEDIN_ACCESS_TOKEN = None
        with patch.dict(os.environ, {}, clear=True):
            publisher = LinkedInPublisherAdapter()
            res = publisher.publish(self.sample_post)

            self.assertFalse(res.success)
            self.assertIn("LINKEDIN_ACCESS_TOKEN não configurado", res.message)

    def test_publisher_manager_registration_and_publish(self):
        pub1 = DummyPublisher("Pub1", should_succeed=True)
        pub2 = DummyPublisher("Pub2", should_succeed=False)

        manager = PublisherManager(publishers=[pub1, pub2])
        results = manager.publish_all(self.sample_post)

        self.assertEqual(len(results), 2)
        self.assertTrue(results[0].success)
        self.assertFalse(results[1].success)

    def test_publisher_manager_factory_default(self):
        manager = PublisherManager.create_default(enable_linkedin=False)
        self.assertEqual(len(manager.publishers), 1)
        self.assertIsInstance(manager.publishers[0], MarkdownPublisher)

        manager_with_linkedin = PublisherManager.create_default(enable_linkedin=True)
        self.assertEqual(len(manager_with_linkedin.publishers), 2)
        self.assertIsInstance(manager_with_linkedin.publishers[1], LinkedInPublisherAdapter)


if __name__ == "__main__":
    unittest.main()

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

    def test_find_associated_image_direct_path(self):
        post = PostContent(
            title="Teste Direct",
            slug="teste-direct",
            date="2026-07-30",
            content_md="...",
            image_path=__file__,  # Usa este arquivo de teste como caminho existente no disco
        )
        resolved = LinkedInPublisherAdapter._find_associated_image(post)
        self.assertEqual(resolved, __file__)

    def test_find_associated_image_markdown_link(self):
        with patch("os.path.exists") as mock_exists:
            def side_effect(path):
                return "custom-image.png" in path or "posts" in path
            mock_exists.side_effect = side_effect

            post = PostContent(
                title="Teste Markdown",
                slug="teste-markdown",
                date="2026-07-30",
                content_md="# Titulo\n![Imagem](images/custom-image.png)",
            )
            resolved = LinkedInPublisherAdapter._find_associated_image(post)
            self.assertIsNotNone(resolved)
            self.assertIn("custom-image.png", resolved)


    def test_find_associated_image_frontmatter(self):
        with patch("os.path.exists") as mock_exists:
            def side_effect(path):
                return "yaml-banner.png" in path or "posts" in path
            mock_exists.side_effect = side_effect

            post = PostContent(
                title="Teste YAML Frontmatter",
                slug="teste-yaml-frontmatter",
                date="2026-07-30",
                content_md="---\ntitle: 'Teste'\nimage: 'images/yaml-banner.png'\n---\n# Conteudo",
            )
            resolved = LinkedInPublisherAdapter._find_associated_image(post)
            self.assertIsNotNone(resolved)
            self.assertIn("yaml-banner.png", resolved)


    def test_linkedin_formatter_spacing_and_comment_link(self):
        from app.publish.publishers.linkedin_publisher import LinkedInFormatter

        input_md = (
            "Parágrafo sobre Microsoft Fabric.\n\n"
            "🔗 Confira mais sobre este e outros projetos no meu site: https://lnkd.in/dBDvddnA"
        )
        formatted = LinkedInFormatter.format_for_linkedin(input_md)

        self.assertIn("link no primeiro comentário", formatted)
        self.assertNotIn("https://lnkd.in/dBDvddnA", formatted)
        self.assertIn(
            "Parágrafo sobre Microsoft Fabric.\n\n🔗 Confira mais sobre este e outros projetos no meu site, link no primeiro comentário",
            formatted,
        )

    @patch("app.providers.linkedin.LinkedInPublisher")
    @patch("app.publish.publishers.linkedin_publisher.settings")
    def test_linkedin_publisher_adapter_posts_first_comment(self, mock_settings, mock_publisher_cls):
        mock_settings.LINKEDIN_ACCESS_TOKEN = "fake-token"
        mock_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.headers = {"X-RestLi-Id": "urn:li:share:123456"}
        mock_instance.publish_text.return_value = mock_response
        mock_instance.publish_image.return_value = mock_response
        mock_publisher_cls.return_value = mock_instance

        with patch.dict(os.environ, {"LINKEDIN_ACCESS_TOKEN": "fake-token"}):
            publisher = LinkedInPublisherAdapter()
            res = publisher.publish(self.sample_post)

            self.assertTrue(res.success)
            mock_instance.comment_on_post.assert_called_once_with(
                post_urn="urn:li:share:123456",
                text="Site/Portfólio: https://rafaelrodrigopa.com.br/linkedin-post",
            )


if __name__ == "__main__":
    unittest.main()


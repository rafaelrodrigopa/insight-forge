import os
import unittest
from unittest.mock import patch

from app.agents.writer.schemas import PostContent
from app.db.connection import DatabaseConnection
from app.db.repository import PostRepository


class TestPostRepository(unittest.TestCase):
    """
    Testes unitários para o repositório de dados PostgreSQL/SQLite.
    """

    def setUp(self):
        self.repo = PostRepository()
        self.test_post = PostContent(
            title="Post de Teste para Banco de Dados",
            slug="test-post-db-slug-unique",
            date="2026-08-15",
            content_md="# Post de Teste\nConteúdo em markdown...",
            topics=["IA", "PostgreSQL", "Testes"],
            source_url="https://example.com/test",
            image_path="posts/images/test.png",
        )
        self._clean_test_post()

    def tearDown(self):
        self._clean_test_post()

    def _clean_test_post(self):
        conn, _ = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM posts WHERE slug = ?;", (self.test_post.slug,))
        conn.commit()
        cursor.close()
        conn.close()

    def test_save_and_retrieve_post(self):
        res = self.repo.save_post(
            post=self.test_post,
            status="draft",
            priority_score=85,
            quality_score=9.0,
            formatted_linkedin_text="Texto formatado...",
        )
        self.assertIn(res["status"], ["draft", "published"])

        fetched = self.repo.get_post_by_slug(self.test_post.slug)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched["slug"], self.test_post.slug)
        self.assertEqual(fetched["title"], self.test_post.title)

    def test_list_pending_posts(self):
        self.repo.save_post(post=self.test_post, status="draft")
        pending = self.repo.list_pending_posts(limit=100)
        self.assertTrue(any(p["slug"] == self.test_post.slug for p in pending))

    def test_mark_as_published(self):
        self.repo.save_post(post=self.test_post, status="draft")
        success = self.repo.mark_as_published(
            slug=self.test_post.slug,
            post_url="https://www.linkedin.com/feed/update/urn:li:share:12345",
        )
        self.assertTrue(success)

        fetched = self.repo.get_post_by_slug(self.test_post.slug)
        self.assertEqual(fetched["status"], "published")
        self.assertEqual(
            fetched["post_url"],
            "https://www.linkedin.com/feed/update/urn:li:share:12345",
        )


if __name__ == "__main__":
    unittest.main()

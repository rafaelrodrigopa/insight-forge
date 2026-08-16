from datetime import datetime, timedelta
import unittest
from unittest.mock import MagicMock, patch

from app.db.connection import DatabaseConnection
from app.db.repository import PostRepository


class TestLinkedInSync(unittest.TestCase):
    """
    Testes unitários para verificação de posts excluídos no LinkedIn e flag ignore-history.
    """

    def setUp(self):
        self.repo = PostRepository()
        self.test_slug = "test-post-deleted-sync-slug"
        self._clean_test_post()

    def tearDown(self):
        self._clean_test_post()

    def _clean_test_post(self):
        conn, _ = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM posts WHERE slug = ?;", (self.test_slug,))
        conn.commit()
        cursor.close()
        conn.close()

    @patch("app.providers.linkedin.LinkedInPublisher")
    @patch.dict("os.environ", {"LINKEDIN_ACCESS_TOKEN": "mock_token"})
    def test_sync_deleted_posts_cleans_deleted_posts(self, mock_publisher_cls):
        """
        Testa se o sync_deleted_posts desmarca no SQLite um post que foi excluído no LinkedIn (404).
        """
        mock_publisher = MagicMock()
        mock_publisher.check_post_exists.return_value = False  # Simula post excluído no LinkedIn (404)
        mock_publisher_cls.return_value = mock_publisher

        # Inserção de um post marcado como publicado com post_url do LinkedIn
        conn, _ = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        now_iso = datetime.now().isoformat()
        cursor.execute(
            """
            INSERT INTO posts (slug, title, content_md, status, post_url, posted_at)
            VALUES (?, ?, ?, 'published', ?, ?);
            """,
            (
                self.test_slug,
                "Post Excluído de Teste",
                "Conteúdo",
                "https://www.linkedin.com/feed/update/urn:li:share:999999999",
                now_iso,
            ),
        )
        conn.commit()
        cursor.close()
        conn.close()

        cleaned_count = self.repo.sync_deleted_posts(days_window=30)
        self.assertGreaterEqual(cleaned_count, 1)

        fetched = self.repo.get_post_by_slug(self.test_slug)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched["status"], "deleted")
        self.assertIsNone(fetched["posted_at"])


if __name__ == "__main__":
    unittest.main()

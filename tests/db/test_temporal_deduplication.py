from datetime import datetime, timedelta
import os
import sqlite3
import unittest

from app.agents.writer.schemas import PostContent
from app.db.connection import DatabaseConnection
from app.db.repository import PostRepository


class TestTemporalDeduplication(unittest.TestCase):
    """
    Testes unitários para migração da coluna posted_at e controle de janela temporal no SQLite.
    """

    def setUp(self):
        self.repo = PostRepository()
        self.test_post_1 = PostContent(
            title="Notícia Ranqueada 1 - Relevância Alta",
            slug="noticia-ranqueada-1",
            date="2026-08-16",
            content_md="# Notícia 1\nConteúdo...",
            topics=["IA", "Python"],
            source_url="https://example.com/news-1",
        )
        self.test_post_2 = PostContent(
            title="Notícia Ranqueada 2 - Relevância Média",
            slug="noticia-ranqueada-2",
            date="2026-08-16",
            content_md="# Notícia 2\nConteúdo...",
            topics=["Power BI"],
            source_url="https://example.com/news-2",
        )

    def test_posted_at_column_migration(self):
        """
        Verifica se a coluna 'posted_at' é criada corretamente na tabela 'posts'.
        """
        conn, _ = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(posts);")
        columns = [column[1] for column in cursor.fetchall()]
        cursor.close()
        conn.close()

        self.assertIn("posted_at", columns)

    def test_is_recently_posted_within_30_days(self):
        """
        Testa se uma notícia postada há menos de 30 dias é identificada como recentemente postada.
        """
        # Salva post publicado recentemente (hoje)
        self.repo.save_post(
            post=self.test_post_1,
            status="published",
            posted_at=datetime.now().isoformat(),
        )

        is_recent_by_url = self.repo.is_recently_posted(
            source_url=self.test_post_1.source_url, days_window=30
        )
        is_recent_by_slug = self.repo.is_recently_posted(
            slug=self.test_post_1.slug, days_window=30
        )

        self.assertTrue(is_recent_by_url)
        self.assertTrue(is_recent_by_slug)

    def test_is_recently_posted_older_than_30_days(self):
        """
        Testa se uma notícia postada há mais de 30 dias NÃO é identificada como recente.
        """
        old_date = (datetime.now() - timedelta(days=40)).isoformat()
        old_post = PostContent(
            title="Notícia Antiga de 40 dias atrás",
            slug="noticia-antiga-40-dias",
            date="2026-07-07",
            content_md="# Notícia Antiga\nConteúdo...",
            topics=["Cloud"],
            source_url="https://example.com/news-old-40",
        )
        self.repo.save_post(
            post=old_post,
            status="published",
            posted_at=old_date,
        )

        is_recent = self.repo.is_recently_posted(
            source_url=old_post.source_url, slug=old_post.slug, days_window=30
        )
        self.assertFalse(is_recent)

    def test_record_posted_at(self):
        """
        Testa se record_posted_at atualiza corretamente a data no registro existente.
        """
        self.repo.save_post(post=self.test_post_2, status="draft")

        now_iso = datetime.now().isoformat()
        success = self.repo.record_posted_at(
            slug=self.test_post_2.slug,
            source_url=self.test_post_2.source_url,
            posted_at=now_iso,
        )
        self.assertTrue(success)

        fetched = self.repo.get_post_by_slug(self.test_post_2.slug)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched["status"], "published")
        self.assertIsNotNone(fetched["posted_at"])


if __name__ == "__main__":
    unittest.main()

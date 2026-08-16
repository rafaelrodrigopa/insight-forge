from datetime import datetime, timedelta
import json
from typing import Any, Dict, List, Optional
from app.db.connection import DatabaseConnection

class PostRepository:
    """
    Repositório de acesso a dados para criação, consulta e atualização de posts no banco.
    """

    def __init__(self):
        self.engine = DatabaseConnection.init_db()

    def save_post(
        self,
        post: Any,
        status: str = "draft",
        priority_score: int = 0,
        quality_score: float = 0.0,
        formatted_linkedin_text: Optional[str] = None,
        posted_at: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Salva ou atualiza um post no banco de dados.
        """
        conn, engine = DatabaseConnection.get_connection()
        cursor = conn.cursor()

        topics_val = post.topics or []
        timestamp_posted = posted_at or (datetime.now().isoformat() if status == "published" else None)

        if engine == "postgres":
            query = """
            INSERT INTO posts (
                slug, title, summary, content_md, formatted_linkedin_text,
                topics, source_url, image_path, priority_score, quality_score, status, posted_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (slug) DO UPDATE SET
                title = EXCLUDED.title,
                content_md = EXCLUDED.content_md,
                formatted_linkedin_text = EXCLUDED.formatted_linkedin_text,
                image_path = EXCLUDED.image_path,
                quality_score = EXCLUDED.quality_score,
                status = EXCLUDED.status,
                posted_at = COALESCE(EXCLUDED.posted_at, posts.posted_at),
                updated_at = CURRENT_TIMESTAMP
            RETURNING id, slug, status;
            """
            cursor.execute(
                query,
                (
                    post.slug,
                    post.title,
                    "",
                    post.content_md,
                    formatted_linkedin_text,
                    topics_val,
                    post.source_url,
                    post.image_path,
                    priority_score,
                    quality_score,
                    status,
                    timestamp_posted,
                ),
            )
            res = cursor.fetchone()
            conn.commit()
            post_id, slug, post_status = res[0], res[1], res[2]
        else:
            topics_json = json.dumps(topics_val)
            query = """
            INSERT INTO posts (
                slug, title, summary, content_md, formatted_linkedin_text,
                topics, source_url, image_path, priority_score, quality_score, status, posted_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (slug) DO UPDATE SET
                title = excluded.title,
                content_md = excluded.content_md,
                formatted_linkedin_text = excluded.formatted_linkedin_text,
                image_path = excluded.image_path,
                quality_score = excluded.quality_score,
                status = excluded.status,
                posted_at = COALESCE(excluded.posted_at, posts.posted_at),
                updated_at = CURRENT_TIMESTAMP;
            """
            cursor.execute(
                query,
                (
                    post.slug,
                    post.title,
                    "",
                    post.content_md,
                    formatted_linkedin_text,
                    topics_json,
                    post.source_url,
                    post.image_path,
                    priority_score,
                    quality_score,
                    status,
                    timestamp_posted,
                ),
            )
            conn.commit()
            post_id = cursor.lastrowid
            slug = post.slug
            post_status = status

        cursor.close()
        conn.close()

        return {"id": post_id, "slug": slug, "status": post_status, "engine": engine}

    def list_pending_posts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retorna a lista de posts pendentes (status 'draft') no banco.
        """
        conn, engine = DatabaseConnection.get_connection()
        cursor = conn.cursor()

        if engine == "postgres":
            cursor.execute(
                "SELECT id, slug, title, content_md, formatted_linkedin_text, image_path, source_url, status FROM posts WHERE status = 'draft' ORDER BY created_at ASC LIMIT %s;",
                (limit,),
            )
        else:
            cursor.execute(
                "SELECT id, slug, title, content_md, formatted_linkedin_text, image_path, source_url, status FROM posts WHERE status = 'draft' ORDER BY created_at ASC LIMIT ?;",
                (limit,),
            )

        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        posts = []
        for r in rows:
            posts.append(
                {
                    "id": r[0],
                    "slug": r[1],
                    "title": r[2],
                    "content_md": r[3],
                    "formatted_linkedin_text": r[4],
                    "image_path": r[5],
                    "source_url": r[6],
                    "status": r[7],
                }
            )
        return posts

    def mark_as_published(self, slug: str, post_url: Optional[str] = None) -> bool:
        """
        Marca um post como publicado no LinkedIn e grava a data de postagem.
        """
        conn, engine = DatabaseConnection.get_connection()
        cursor = conn.cursor()

        now = datetime.now()
        iso_now = now.isoformat()
        if engine == "postgres":
            cursor.execute(
                "UPDATE posts SET status = 'published', post_url = %s, published_at = %s, posted_at = %s, updated_at = CURRENT_TIMESTAMP WHERE slug = %s;",
                (post_url, now, iso_now, slug),
            )
        else:
            cursor.execute(
                "UPDATE posts SET status = 'published', post_url = ?, published_at = ?, posted_at = ?, updated_at = CURRENT_TIMESTAMP WHERE slug = ?;",
                (post_url, iso_now, iso_now, slug),
            )

        conn.commit()
        rows_affected = cursor.rowcount
        cursor.close()
        conn.close()

        return rows_affected > 0

    def is_recently_posted(
        self,
        source_url: Optional[str] = None,
        slug: Optional[str] = None,
        days_window: int = 30,
    ) -> bool:
        """
        Verifica se a notícia já possui registro de postagem nos últimos 'days_window' dias.
        """
        if not source_url and not slug:
            return False

        conn, engine = DatabaseConnection.get_connection()
        cursor = conn.cursor()

        cutoff_date = (datetime.now() - timedelta(days=days_window)).isoformat()
        cutoff_sql = (datetime.now() - timedelta(days=days_window)).strftime("%Y-%m-%d %H:%M:%S")

        clean_url = source_url.split("?")[0].strip() if source_url else ""

        if engine == "postgres":
            query = """
            SELECT COUNT(*) FROM posts
            WHERE (
                (%s != '' AND (source_url = %s OR source_url LIKE %s)) OR
                (%s != '' AND (slug = %s OR slug LIKE %s OR %s LIKE '%%' || slug || '%%'))
            ) AND (
                COALESCE(posted_at, published_at, created_at) >= %s
            );
            """
            cursor.execute(
                query,
                (
                    clean_url, source_url or "", clean_url + "%",
                    slug or "", slug or "", "%" + (slug or "") + "%", slug or "",
                    cutoff_date,
                ),
            )
        else:
            query = """
            SELECT COUNT(*) FROM posts
            WHERE (
                (? != '' AND (source_url = ? OR source_url LIKE ?)) OR
                (? != '' AND (slug = ? OR slug LIKE ? OR ? LIKE '%' || slug || '%'))
            ) AND (
                COALESCE(posted_at, published_at, created_at) >= ?
            );
            """
            cursor.execute(
                query,
                (
                    clean_url, source_url or "", clean_url + "%",
                    slug or "", slug or "", "%" + (slug or "") + "%", slug or "",
                    cutoff_date,
                ),
            )

        row = cursor.fetchone()
        count = row[0] if row else 0

        cursor.close()
        conn.close()

        return count > 0

    def record_posted_at(
        self,
        slug: str,
        source_url: Optional[str] = None,
        posted_at: Optional[str] = None,
        post_url: Optional[str] = None,
    ) -> bool:
        """
        Atualiza ou define o timestamp de postagem (posted_at) e a URL do post no banco.
        """
        conn, engine = DatabaseConnection.get_connection()
        cursor = conn.cursor()

        timestamp = posted_at or datetime.now().isoformat()

        if engine == "postgres":
            query = """
            UPDATE posts
            SET posted_at = %s,
                status = 'published',
                post_url = COALESCE(NULLIF(%s, ''), post_url),
                updated_at = CURRENT_TIMESTAMP
            WHERE slug = %s OR (%s IS NOT NULL AND %s != '' AND source_url = %s);
            """
            cursor.execute(query, (timestamp, post_url or "", slug, source_url, source_url, source_url))
        else:
            query = """
            UPDATE posts
            SET posted_at = ?,
                status = 'published',
                post_url = CASE WHEN ? IS NOT NULL AND ? != '' THEN ? ELSE post_url END,
                updated_at = CURRENT_TIMESTAMP
            WHERE slug = ? OR (? IS NOT NULL AND ? != '' AND source_url = ?);
            """
            cursor.execute(query, (timestamp, post_url or "", post_url or "", post_url or "", slug, source_url, source_url, source_url))

        conn.commit()
        rows_affected = cursor.rowcount
        cursor.close()
        conn.close()

        return rows_affected > 0

    def sync_deleted_posts(self, days_window: int = 30) -> int:
        """
        Consulta no LinkedIn a existência de posts marcados como publicados no banco.
        Se um post tiver sido excluído manualmente no LinkedIn (404), atualiza o SQLite
        marcando o status como 'deleted' e limpando o posted_at para liberá-lo no histórico.
        """
        import os
        import re
        from app.config.settings import settings

        token = os.getenv("LINKEDIN_ACCESS_TOKEN") or getattr(settings, "LINKEDIN_ACCESS_TOKEN", None)
        if not token:
            return 0

        conn, engine = DatabaseConnection.get_connection()
        cursor = conn.cursor()

        cutoff_date = (datetime.now() - timedelta(days=days_window)).isoformat()

        if engine == "postgres":
            query = """
            SELECT id, slug, title, post_url FROM posts
            WHERE post_url IS NOT NULL AND post_url != ''
              AND status = 'published'
              AND COALESCE(posted_at, published_at, created_at) >= %s;
            """
            cursor.execute(query, (cutoff_date,))
        else:
            query = """
            SELECT id, slug, title, post_url FROM posts
            WHERE post_url IS NOT NULL AND post_url != ''
              AND status = 'published'
              AND COALESCE(posted_at, published_at, created_at) >= ?;
            """
            cursor.execute(query, (cutoff_date,))

        rows = cursor.fetchall()
        if not rows:
            cursor.close()
            conn.close()
            return 0

        try:
            from app.providers.linkedin import LinkedInPublisher
            publisher = LinkedInPublisher()
        except Exception:
            cursor.close()
            conn.close()
            return 0

        cleaned_count = 0
        for row in rows:
            post_id, slug, title, post_url = row[0], row[1], row[2], row[3]
            urn_match = re.search(r"(urn:li:[^\s/?#]+|[0-9]{15,})", post_url)
            if not urn_match:
                continue

            urn = urn_match.group(1)
            exists = publisher.check_post_exists(urn)
            if not exists:
                print(f"   [LinkedIn Sync] [REMOVIDO] Post \"{title}\" (slug: {slug}) foi excluído no LinkedIn! Atualizando SQLite...")
                if engine == "postgres":
                    cursor.execute("UPDATE posts SET status = 'deleted', posted_at = NULL, updated_at = CURRENT_TIMESTAMP WHERE id = %s;", (post_id,))
                else:
                    cursor.execute("UPDATE posts SET status = 'deleted', posted_at = NULL, updated_at = CURRENT_TIMESTAMP WHERE id = ?;", (post_id,))
                conn.commit()
                cleaned_count += 1

        cursor.close()
        conn.close()

        return cleaned_count

    def get_post_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        """
        Busca um post específico pelo seu slug.
        """
        conn, engine = DatabaseConnection.get_connection()
        cursor = conn.cursor()

        if engine == "postgres":
            cursor.execute("SELECT id, slug, title, content_md, formatted_linkedin_text, image_path, status, post_url, posted_at FROM posts WHERE slug = %s;", (slug,))
        else:
            cursor.execute("SELECT id, slug, title, content_md, formatted_linkedin_text, image_path, status, post_url, posted_at FROM posts WHERE slug = ?;", (slug,))

        row = cursor.fetchone()
        cursor.close()
        conn.close()

        if not row:
            return None

        return {
            "id": row[0],
            "slug": row[1],
            "title": row[2],
            "content_md": row[3],
            "formatted_linkedin_text": row[4],
            "image_path": row[5],
            "status": row[6],
            "post_url": row[7],
            "posted_at": row[8],
        }

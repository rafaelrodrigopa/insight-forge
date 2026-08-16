from datetime import datetime
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
    ) -> Dict[str, Any]:
        """
        Salva ou atualiza um post no banco de dados.
        """
        conn, engine = DatabaseConnection.get_connection()
        cursor = conn.cursor()

        topics_val = post.topics or []

        if engine == "postgres":
            query = """
            INSERT INTO posts (
                slug, title, summary, content_md, formatted_linkedin_text,
                topics, source_url, image_path, priority_score, quality_score, status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (slug) DO UPDATE SET
                title = EXCLUDED.title,
                content_md = EXCLUDED.content_md,
                formatted_linkedin_text = EXCLUDED.formatted_linkedin_text,
                image_path = EXCLUDED.image_path,
                quality_score = EXCLUDED.quality_score,
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
                topics, source_url, image_path, priority_score, quality_score, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (slug) DO UPDATE SET
                title = excluded.title,
                content_md = excluded.content_md,
                formatted_linkedin_text = excluded.formatted_linkedin_text,
                image_path = excluded.image_path,
                quality_score = excluded.quality_score,
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
        Marca um post como publicado no LinkedIn.
        """
        conn, engine = DatabaseConnection.get_connection()
        cursor = conn.cursor()

        now = datetime.now()
        if engine == "postgres":
            cursor.execute(
                "UPDATE posts SET status = 'published', post_url = %s, published_at = %s, updated_at = CURRENT_TIMESTAMP WHERE slug = %s;",
                (post_url, now, slug),
            )
        else:
            cursor.execute(
                "UPDATE posts SET status = 'published', post_url = ?, published_at = ?, updated_at = CURRENT_TIMESTAMP WHERE slug = ?;",
                (post_url, now.isoformat(), slug),
            )

        conn.commit()
        rows_affected = cursor.rowcount
        cursor.close()
        conn.close()

        return rows_affected > 0

    def get_post_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        """
        Busca um post específico pelo seu slug.
        """
        conn, engine = DatabaseConnection.get_connection()
        cursor = conn.cursor()

        if engine == "postgres":
            cursor.execute("SELECT id, slug, title, content_md, formatted_linkedin_text, image_path, status, post_url FROM posts WHERE slug = %s;", (slug,))
        else:
            cursor.execute("SELECT id, slug, title, content_md, formatted_linkedin_text, image_path, status, post_url FROM posts WHERE slug = ?;", (slug,))

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
        }

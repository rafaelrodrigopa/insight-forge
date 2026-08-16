import os
import sqlite3
from typing import Any, Tuple


class DatabaseConnection:
    """
    Gerenciador unificado de conexão com banco de dados SQLite local (posts/insight_forge.db).
    """

    @staticmethod
    def get_connection() -> Tuple[Any, str]:
        """
        Retorna uma tupla (connection, engine_type) para o banco de dados SQLite.
        """
        db_path = os.path.join("posts", "insight_forge.db")
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        conn = sqlite3.connect(db_path)
        return conn, "sqlite"

    @classmethod
    def init_db(cls) -> str:
        """
        Inicializa a tabela 'posts' no banco de dados SQLite se não existir.
        """
        conn, engine = cls.get_connection()
        cursor = conn.cursor()

        create_table_sql = """
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slug TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            summary TEXT,
            content_md TEXT NOT NULL,
            formatted_linkedin_text TEXT,
            topics TEXT,
            source_url TEXT,
            image_path TEXT,
            priority_score INTEGER DEFAULT 0,
            quality_score REAL DEFAULT 0.0,
            status TEXT DEFAULT 'draft',
            post_url TEXT,
            published_at TIMESTAMP,
            posted_at DATETIME,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """

        cursor.execute(create_table_sql)

        # Migração automática: garante que a coluna 'posted_at' exista em bancos pré-existentes
        cursor.execute("PRAGMA table_info(posts);")
        columns = [column[1] for column in cursor.fetchall()]
        if "posted_at" not in columns:
            cursor.execute("ALTER TABLE posts ADD COLUMN posted_at DATETIME;")

        # Preenche posted_at retroativamente com created_at para posts antigos que possuem posted_at NULO
        cursor.execute("UPDATE posts SET posted_at = created_at WHERE posted_at IS NULL;")

        conn.commit()
        cursor.close()
        conn.close()

        return engine

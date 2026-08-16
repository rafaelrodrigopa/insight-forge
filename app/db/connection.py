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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """

        cursor.execute(create_table_sql)
        conn.commit()
        cursor.close()
        conn.close()

        return engine

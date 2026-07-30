import json
from pathlib import Path
from typing import Dict, Set

from app.config.settings import settings


class EngagementHistory:
    """
    Gerenciador de histórico de posts já interagidos para evitar duplicações.
    """

    def __init__(self, history_file: str = "engagement_history.json"):
        self.filepath = settings.BASE_DIR / history_file
        self._history: Dict[str, dict] = self._load()

    def _load(self) -> Dict[str, dict]:
        if self.filepath.exists():
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def is_interacted(self, post_urn: str) -> bool:
        """
        Verifica se o post_urn já foi processado anteriormente.
        """
        return post_urn in self._history

    def record_interaction(
        self,
        post_urn: str,
        reaction: str,
        comment: str,
        title: str = "",
        topic: str = "",
    ):
        """
        Registra uma interação com timestamp e detalhes.
        """
        import datetime

        self._history[post_urn] = {
            "interacted_at": datetime.datetime.now().isoformat(),
            "reaction": reaction,
            "comment": comment,
            "title": title,
            "topic": topic,
        }
        self._save()

    def _save(self):
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self._history, f, ensure_ascii=False, indent=2)
        except Exception as err:
            print(f" ⚠️ Erro ao salvar histórico de engajamento: {err}")

    def get_interacted_urns(self) -> Set[str]:
        return set(self._history.keys())

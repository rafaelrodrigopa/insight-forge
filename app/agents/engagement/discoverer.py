import re
from typing import List, Optional
import feedparser

from app.agents.engagement.schemas import TargetPost


class PostDiscoverer:
    """
    Descobridor autônomo que localiza posts recentes sobre Power BI, Fabric e Engenharia de Dados.
    """

    SEARCH_FEEDS = [
        {
            "topic": "Power BI",
            "url": "https://news.google.com/rss/search?q=Power+BI+LinkedIn",
        },
        {
            "topic": "Microsoft Fabric",
            "url": "https://news.google.com/rss/search?q=Microsoft+Fabric+LinkedIn",
        },
        {
            "topic": "BigQuery & Dataform",
            "url": "https://news.google.com/rss/search?q=BigQuery+OR+Dataform+LinkedIn",
        },
        {
            "topic": "Data Engineering",
            "url": "https://news.google.com/rss/search?q=Data+Engineering+LinkedIn",
        },
    ]

    def discover_recent_posts(self, max_posts: int = 10) -> List[TargetPost]:
        """
        Busca e extrai posts recentes do LinkedIn a partir de feeds RSS indexados.
        """
        import hashlib

        discovered: List[TargetPost] = []
        seen_urns = set()

        for search_info in self.SEARCH_FEEDS:
            topic = search_info["topic"]
            feed_url = search_info["url"]

            try:
                parsed = feedparser.parse(feed_url)
                for entry in parsed.entries:
                    link = entry.get("link", "")
                    title = entry.get("title", "")
                    summary = entry.get("summary", entry.get("description", ""))

                    urn = self.extract_linkedin_urn(link) or f"urn:li:share:{hashlib.md5(link.encode('utf-8')).hexdigest()}"
                    if urn in seen_urns:
                        continue

                    seen_urns.add(urn)
                    clean_content = re.sub(r"<[^>]+>", " ", summary).strip()

                    discovered.append(
                        TargetPost(
                            post_urn=urn,
                            url=link,
                            title=title.strip(),
                            content=clean_content,
                            author=self._extract_author_from_title(title),
                            published_at=entry.get("published"),
                            topic=topic,
                        )
                    )

                    if len(discovered) >= max_posts:
                        break
            except Exception as err:
                print(f" ⚠️ Erro ao descobrir posts para [{topic}]: {err}")
                continue

            if len(discovered) >= max_posts:
                break

        return discovered

    @staticmethod
    def extract_linkedin_urn(url: str) -> Optional[str]:
        """
        Extrai o URN padronizado do LinkedIn (urn:li:activity:... ou urn:li:share:...) da URL.
        """
        if not url:
            return None

        # Exemplo: urn:li:activity:7123456789012345678
        urn_match = re.search(r"urn:li:(activity|share|ugcPost):\d+", url)
        if urn_match:
            return urn_match.group(0)

        # Exemplo: activity-7123456789012345678
        activity_id_match = re.search(r"activity-(\d+)", url)
        if activity_id_match:
            return f"urn:li:activity:{activity_id_match.group(1)}"

        # Exemplo: ID numérico isolado na URL do LinkedIn
        digits_match = re.search(r"linkedin\.com/posts/.*?(\d{18,20})", url)
        if digits_match:
            return f"urn:li:activity:{digits_match.group(1)}"

        return None

    @staticmethod
    def _extract_author_from_title(title: str) -> Optional[str]:
        """
        Extrai o nome do autor do título retornado pelo mecanismo de busca.
        """
        if " - " in title:
            parts = title.split(" - ")
            return parts[0].strip()
        return None

import hashlib
import re
from typing import Any, Dict, List
import requests

try:
    import feedparser
except ImportError:
    feedparser = None


class RSSFetcher:
    """
    Leitor e parser de RSS e Atom feeds.
    """

    DEFAULT_USER_AGENT = (
        "InsightForge/1.0 (+https://github.com/rafaelrodrigopa/insight-forge)"
    )

    def fetch_feed(self, url: str, timeout: int = 15) -> List[Dict[str, Any]]:
        """
        Busca um feed RSS/Atom a partir da URL informada e retorna os itens padronizados.
        """
        headers = {"User-Agent": self.DEFAULT_USER_AGENT}

        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            content = response.content
        except Exception as error:
            raise RuntimeError(f"Erro ao buscar o feed RSS ({url}): {error}") from error

        entries: List[Dict[str, Any]] = []

        if feedparser is not None:
            parsed = feedparser.parse(content)
            source_title = (
                parsed.feed.get("title", url)
                if hasattr(parsed, "feed") and parsed.feed
                else url
            )

            for entry in parsed.entries:
                link = entry.get("link", "")
                title = entry.get("title", "")
                raw_summary = (
                    entry.get("summary", "")
                    or entry.get("description", "")
                    or ""
                )
                clean_summary = self._strip_html(raw_summary)
                published = entry.get("published", entry.get("updated", ""))

                item_id = (
                    entry.get("id")
                    or (
                        hashlib.md5(link.encode("utf-8")).hexdigest()
                        if link
                        else hashlib.md5(title.encode("utf-8")).hexdigest()
                    )
                )

                entries.append(
                    {
                        "id": item_id,
                        "title": title.strip(),
                        "url": link.strip(),
                        "content": clean_summary.strip(),
                        "source": source_title,
                        "published_at": published,
                    }
                )
        else:
            entries = self._fallback_parse_xml(content, url)

        return entries

    @staticmethod
    def _strip_html(text: str) -> str:
        """Remove tags HTML simples do texto."""
        if not text:
            return ""
        clean = re.sub(r"<[^>]+>", " ", text)
        return re.sub(r"\s+", " ", clean).strip()

    def _fallback_parse_xml(self, content: bytes, url: str) -> List[Dict[str, Any]]:
        import xml.etree.ElementTree as ET

        entries = []
        try:
            root = ET.fromstring(content)
            channel = root.find("channel")
            source_title = channel.findtext("title", default=url) if channel is not None else url
            items = channel.findall("item") if channel is not None else root.findall("{http://www.w3.org/2005/Atom}entry")

            for item in items:
                title = item.findtext("title", default="")
                link = item.findtext("link", default="")
                desc = item.findtext("description", default="")
                pub_date = item.findtext("pubDate", default="")

                item_id = hashlib.md5(link.encode("utf-8")).hexdigest() if link else title
                entries.append(
                    {
                        "id": item_id,
                        "title": title.strip(),
                        "url": link.strip(),
                        "content": self._strip_html(desc),
                        "source": source_title,
                        "published_at": pub_date,
                    }
                )
        except Exception:
            pass

        return entries

import os
from typing import Optional

from app.agents.writer.schemas import PostContent
from app.config.settings import settings
from app.publish.base import BasePublisher, PublishResult


class LinkedInPublisherAdapter(BasePublisher):
    """
    Adaptador de publicação integrado com a API oficial do LinkedIn.
    """

    def __init__(self):
        super().__init__(name="LinkedIn API")

    def publish(self, post: PostContent) -> PublishResult:
        """
        Publica o artigo no perfil/página do LinkedIn.
        """
        # Verifica se as credenciais do LinkedIn estão configuradas no ambiente
        linkedin_token = os.getenv("LINKEDIN_ACCESS_TOKEN") or getattr(
            settings, "LINKEDIN_ACCESS_TOKEN", None
        )

        if not linkedin_token:
            return PublishResult(
                publisher_name=self.name,
                success=False,
                post_url=None,
                message="LINKEDIN_ACCESS_TOKEN não configurado nas variáveis de ambiente. Post mantido em rascunho.",
            )

        try:
            from app.providers.linkedin import LinkedInPublisher

            publisher = LinkedInPublisher()

            # Remove frontmatter YAML antes de postar no texto do LinkedIn
            clean_text = self._strip_frontmatter(post.content_md)

            if post.source_url:
                response = publisher.publish_article(
                    text=clean_text,
                    url=post.source_url,
                    title=post.title,
                )
            else:
                response = publisher.publish_text(text=clean_text)

            if response and (
                getattr(response, "status_code", 0) in (200, 201)
                or getattr(response, "ok", False)
            ):
                post_id = getattr(response, "headers", {}).get("X-RestLi-Id", "OK")
                return PublishResult(
                    publisher_name=self.name,
                    success=True,
                    post_url=f"https://www.linkedin.com/feed/update/{post_id}",
                    message=f"Post publicado com sucesso no LinkedIn! (ID: {post_id})",
                )
            else:
                err_text = (
                    response.text if hasattr(response, "text") else str(response)
                )
                return PublishResult(
                    publisher_name=self.name,
                    success=False,
                    post_url=None,
                    message=f"Falha na API do LinkedIn: {err_text[:200]}",
                )

        except Exception as error:
            return PublishResult(
                publisher_name=self.name,
                success=False,
                post_url=None,
                message=f"Erro ao conectar à API do LinkedIn: {error}",
            )

    @staticmethod
    def _strip_frontmatter(text: str) -> str:
        """
        Remove o cabeçalho YAML frontmatter (--- ... ---) do conteúdo Markdown.
        """
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                return parts[2].strip()
        return text.strip()

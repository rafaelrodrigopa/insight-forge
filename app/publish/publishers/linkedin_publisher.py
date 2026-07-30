import os
import re
from typing import Optional

from app.agents.writer.schemas import PostContent
from app.config.settings import settings
from app.publish.base import BasePublisher, PublishResult


class LinkedInFormatter:
    """
    Formatador especializado que converte Markdown em texto limpo e legível para o LinkedIn.
    """

    @staticmethod
    def format_for_linkedin(text: str) -> str:
        # 1. Remove frontmatter YAML (--- ... ---)
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                text = parts[2]

        # 2. Remove sintaxe de imagem markdown ![alt](path)
        text = re.sub(r"!\[.*?\]\(.*?\)", "", text)

        # 3. Converte cabeçalhos ## ou ### em títulos limpos com emoji
        def _replace_header(match):
            level = len(match.group(1))
            title = match.group(2).strip()
            title = title.replace("`", "")
            icon = "📌" if level <= 2 else "💡"
            return f"\n{icon} {title.upper()}\n"

        text = re.sub(r"^(#{1,4})\s+(.+)$", _replace_header, text, flags=re.MULTILINE)

        # 4. Remove marcadores de bloco de código ```python ... ```
        text = re.sub(r"```[\w]*\n?", "", text)

        # 5. Remove crases simples de código `código` -> código
        text = re.sub(r"`([^`]+)`", r"\1", text)

        # 6. Remove itálicos/negritos de markdown *texto* ou _texto_ -> texto
        text = re.sub(r"\*([^*]+)\*", r"\1", text)
        text = re.sub(r"_([^_]+)_", r"\1", text)

        # 7. Remove linhas divisórias ---
        text = re.sub(r"^\s*---\s*$", "", text, flags=re.MULTILINE)

        # 8. Ajusta múltiplos saltos de linha
        text = re.sub(r"\n{3,}", "\n\n", text)

        return text.strip()


class LinkedInPublisherAdapter(BasePublisher):
    """
    Adaptador de publicação integrado com a API oficial do LinkedIn (suporta imagem anexada e texto limpo).
    """

    def __init__(self):
        super().__init__(name="LinkedIn API")

    def publish(self, post: PostContent) -> PublishResult:
        """
        Publica o artigo no perfil/página do LinkedIn.
        """
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

            # Formatador de texto para o LinkedIn (sem tags brutas de markdown)
            clean_text = LinkedInFormatter.format_for_linkedin(post.content_md)

            # Localiza a imagem gerada associada ao post (em posts/images)
            image_path = self._find_associated_image(post)

            if image_path and os.path.exists(image_path):
                response = publisher.publish_image(
                    text=clean_text, image_path=image_path
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
                    message=f"Post publicado com sucesso no LinkedIn com imagem anexada! (ID: {post_id})",
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
    def _find_associated_image(post: PostContent) -> Optional[str]:
        """
        Localiza o arquivo de imagem PNG associado a este post na pasta posts/images.
        """
        images_dir = "posts/images"
        if not os.path.exists(images_dir):
            return None

        # Tenta corresponder pelo slug limpo
        clean_slug = post.slug.replace("linkedin-", "")
        for filename in os.listdir(images_dir):
            if filename.endswith(".png") and clean_slug in filename:
                return os.path.join(images_dir, filename)

        # Fallback: pega a primeira imagem PNG da pasta se disponível
        png_files = [
            f for f in os.listdir(images_dir) if f.endswith(".png")
        ]
        if png_files:
            return os.path.join(images_dir, png_files[0])

        return None

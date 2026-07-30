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
        # 1. Remove frontmatter YAML (--- ... ---) apenas do topo do texto
        text = re.sub(r"^---[\s\S]*?---\s*", "", text)

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

        # 5. Converte links markdown [texto](url) para apenas a URL pura navegável no LinkedIn
        text = re.sub(r"\[([^\]]+)\]\((https?://[^\)]+)\)", r"\2", text)

        # 6. Remove crases simples de código `código` -> código
        text = re.sub(r"`([^`]+)`", r"\1", text)

        # 7. Remove negrito **texto** sem cruzar novas linhas \n
        text = re.sub(r"\*\*([^\*\n]+)\*\*", r"\1", text)

        # 8. Remove itálico *texto* apenas se não for asterisco isolado (sem cruzar \n)
        text = re.sub(r"(?<!\s)\*([^\*\n]+)\*(?!\s)", r"\1", text)

        # 9. Remove itálicos _texto_ preservando dunders como __all__
        text = re.sub(r"(?<!\w)_([^_]+)_(?!\w)", r"\1", text)

        # 10. Remove linhas divisórias ---
        text = re.sub(r"^\s*---\s*$", "", text, flags=re.MULTILINE)

        # 11. Ajusta múltiplos saltos de linha
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
        Hierarquia de Resolução:
        1. Atributo explícito post.image_path (se existir no disco)
        2. Campo de imagem no Frontmatter YAML (`image: ...` ou `image_path: ...`)
        3. Tag de imagem Markdown ![...](images/...) em post.content_md
        4. Busca em posts/images/ por correspondência de slug ou data
        5. Fallback: imagem PNG mais recentemente modificada/criada (mtime decrescente)
        """
        # 1. Atributo direto post.image_path
        if getattr(post, "image_path", None) and os.path.exists(post.image_path):
            return post.image_path

        images_dir = "posts/images"
        if not os.path.exists(images_dir):
            return None

        # 2. Busca no Frontmatter YAML por `image: "images/xyz.png"` ou `image_path: ...`
        if post.content_md:
            fm_match = re.search(r"^\s*image(?:_path)?:\s*[\"']?(?:posts/)?(?:images/)?([^\"'\s\n]+)[\"']?", post.content_md, re.MULTILINE)
            if fm_match:
                img_name = os.path.basename(fm_match.group(1))
                cand_path = os.path.join(images_dir, img_name)
                if os.path.exists(cand_path):
                    return cand_path

        # 3. Busca por tag de imagem no Markdown
        if post.content_md:
            img_match = re.search(r"!\[.*?\]\((?:posts/)?(?:images/)?([^\)]+)\)", post.content_md)
            if img_match:
                img_name = os.path.basename(img_match.group(1))
                cand_path = os.path.join(images_dir, img_name)
                if os.path.exists(cand_path):
                    return cand_path

        # 4. Correspondência por slug ou data
        clean_slug = post.slug.replace("linkedin-", "") if post.slug else ""
        for filename in os.listdir(images_dir):
            if filename.endswith(".png"):
                if (clean_slug and clean_slug in filename) or (post.date and post.date in filename):
                    return os.path.join(images_dir, filename)

        # 5. Fallback Seguro: pega a imagem PNG MAIS RECENTE no disco (ordem decrescente de mtime)
        png_files = [
            os.path.join(images_dir, f)
            for f in os.listdir(images_dir)
            if f.endswith(".png")
        ]
        if png_files:
            png_files.sort(key=lambda p: os.path.getmtime(p), reverse=True)
            return png_files[0]

        return None

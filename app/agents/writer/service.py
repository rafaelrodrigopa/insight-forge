from datetime import datetime
import os
import re
from typing import Optional

from app.agents.summarizer.schemas import SummaryResult
from app.agents.writer.prompt import LINKEDIN_WRITER_SYSTEM_PROMPT, WRITER_SYSTEM_PROMPT
from app.agents.writer.schemas import PostContent
from app.providers.base import BaseLLMProvider
from app.providers.gemini import GeminiChat


class WriterService:
    """
    Serviço responsável por gerar posts em Markdown e salvá-los no sistema de arquivos.
    """

    def __init__(
        self,
        llm_provider: Optional[BaseLLMProvider] = None,
        posts_dir: str = "posts",
    ):
        self.llm = llm_provider or GeminiChat()
        self.posts_dir = posts_dir

    def generate_linkedin_post(
        self,
        summary: SummaryResult,
        publish_date: Optional[str] = None,
        image_path: Optional[str] = None,
    ) -> PostContent:
        """
        Gera um post em formato otimizado para o LinkedIn e o salva no disco.
        """
        date_str = publish_date or datetime.now().strftime("%Y-%m-%d")
        slug = f"linkedin-{self._slugify(summary.title)}"

        user_prompt = (
            f"Crie um post de alto engajamento para o LinkedIn baseado nas seguintes informações:\n\n"
            f"Título Original: {summary.title}\n"
            f"Resumo Executivo: {summary.summary}\n"
            f"Pontos Chave:\n"
            + "\n".join(f"- {pt}" for pt in summary.key_points)
            + f"\nTópicos: {', '.join(summary.topics)}\n"
            f"Fonte Original: {summary.source_url or 'N/A'}\n"
        )

        try:
            response = self.llm.generate(
                prompt=user_prompt,
                system=LINKEDIN_WRITER_SYSTEM_PROMPT,
                temperature=0.6,
            )
            raw_markdown = response.text.strip()
        except Exception as error:
            raw_markdown = self._build_fallback_markdown(summary, str(error))

        if image_path:
            image_filename = os.path.basename(image_path)
            raw_markdown += f"\n\n![Imagem Ilustrativa](images/{image_filename})"

        full_markdown = self._add_frontmatter_if_missing(
            raw_markdown=raw_markdown,
            title=summary.title,
            date_str=date_str,
            topics=summary.topics,
            source_url=summary.source_url,
            image_path=image_path,
        )

        filename = f"{date_str}-{slug}.md"
        file_path = os.path.join(self.posts_dir, filename)

        self._save_to_disk(file_path, full_markdown)

        return PostContent(
            title=summary.title,
            slug=slug,
            date=date_str,
            content_md=full_markdown,
            topics=summary.topics,
            source_url=summary.source_url,
            file_path=file_path,
            image_path=image_path,
        )

    def generate_post(
        self, summary: SummaryResult, publish_date: Optional[str] = None
    ) -> PostContent:
        """
        Gera um post completo em Markdown a partir de um SummaryResult e o salva no disco.
        """
        date_str = publish_date or datetime.now().strftime("%Y-%m-%d")
        slug = self._slugify(summary.title)

        user_prompt = (
            f"Escreva um artigo/post em Markdown baseado nas seguintes informações:\n\n"
            f"Título Original: {summary.title}\n"
            f"Resumo Executivo: {summary.summary}\n"
            f"Pontos Chave:\n"
            + "\n".join(f"- {pt}" for pt in summary.key_points)
            + f"\nTópicos: {', '.join(summary.topics)}\n"
            f"Fonte Original: {summary.source_url or 'N/A'}\n"
        )

        try:
            response = self.llm.generate(
                prompt=user_prompt,
                system=WRITER_SYSTEM_PROMPT,
                temperature=0.6,
            )
            raw_markdown = response.text.strip()
        except Exception as error:
            raw_markdown = self._build_fallback_markdown(summary, str(error))

        # Adiciona Frontmatter YAML se não estiver presente
        full_markdown = self._add_frontmatter_if_missing(
            raw_markdown=raw_markdown,
            title=summary.title,
            date_str=date_str,
            topics=summary.topics,
            source_url=summary.source_url,
        )

        filename = f"{date_str}-{slug}.md"
        file_path = os.path.join(self.posts_dir, filename)

        self._save_to_disk(file_path, full_markdown)

        return PostContent(
            title=summary.title,
            slug=slug,
            date=date_str,
            content_md=full_markdown,
            topics=summary.topics,
            source_url=summary.source_url,
            file_path=file_path,
        )

    def _save_to_disk(self, file_path: str, content: str) -> None:
        """
        Salva o conteúdo Markdown no caminho de arquivo especificado.
        """
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

    @staticmethod
    def _slugify(text: str) -> str:
        """
        Converte uma string em um slug limpo para nome de arquivo ou URL.
        """
        import unicodedata
        text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
        text = text.lower().strip()
        text = re.sub(r"[^\w\s-]", "", text)
        text = re.sub(r"[\s_-]+", "-", text)
        return text.strip("-") or "post"

    @staticmethod
    def _add_frontmatter_if_missing(
        raw_markdown: str,
        title: str,
        date_str: str,
        topics: list,
        source_url: Optional[str],
        image_path: Optional[str] = None,
    ) -> str:
        if raw_markdown.startswith("---"):
            return raw_markdown

        topics_str = ", ".join(topics) if topics else "Geral"
        image_str = f"image: \"images/{os.path.basename(image_path)}\"\n" if image_path else ""
        frontmatter = (
            f"---\n"
            f"title: \"{title}\"\n"
            f"date: \"{date_str}\"\n"
            f"topics: [{topics_str}]\n"
            f"author: \"Insight Forge AI Writer\"\n"
            f"source_url: \"{source_url or ''}\"\n"
            f"{image_str}"
            f"---\n\n"
        )
        return frontmatter + raw_markdown

    @staticmethod
    def _build_fallback_markdown(summary: SummaryResult, error_msg: str) -> str:
        return (
            f"# {summary.title}\n\n"
            f"**Nota:** Artigo gerado em modo de contingência devido a: {error_msg}\n\n"
            f"## Resumo Executivo\n{summary.summary}\n\n"
            f"## Pontos Chave\n"
            + "\n".join(f"- {pt}" for pt in summary.key_points)
        )

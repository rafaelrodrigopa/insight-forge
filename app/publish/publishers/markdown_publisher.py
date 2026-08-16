import os
from typing import Optional

from app.agents.writer.schemas import PostContent
from app.publish.base import BasePublisher, PublishResult


class MarkdownPublisher(BasePublisher):
    """
    Publicador responsável por salvar e verificar arquivos de post em formato Markdown (.md).
    """

    def __init__(self, posts_dir: str = "posts"):
        super().__init__(name="Markdown Local/Git")
        self.posts_dir = posts_dir

    def publish(self, post: PostContent) -> PublishResult:
        """
        Garante que o post está salvo no diretório posts/ e retorna o resultado.
        """
        try:
            os.makedirs(self.posts_dir, exist_ok=True)
            file_path = post.file_path or os.path.join(
                self.posts_dir, f"{post.date}-{post.slug}.md"
            )

            if not os.path.exists(file_path):
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(post.content_md)

            return PublishResult(
                publisher_name=self.name,
                success=True,
                post_url=file_path,
                message=f"Post salvo com sucesso em: {file_path}",
            )
        except Exception as error:
            return PublishResult(
                publisher_name=self.name,
                success=False,
                post_url=None,
                message=f"Erro ao salvar post Markdown: {error}",
            )

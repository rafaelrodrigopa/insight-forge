from app.agents.writer.schemas import PostContent
from app.db.repository import PostRepository
from app.publish.base import BasePublisher, PublishResult
from app.publish.publishers.linkedin_publisher import LinkedInFormatter


class SQLitePublisherAdapter(BasePublisher):
    """
    Adaptador de publicação que grava artigos no banco de dados SQLite local.
    """

    def __init__(self):
        super().__init__(name="SQLite Database")
        self.repository = PostRepository()

    def publish(self, post: PostContent) -> PublishResult:
        """
        Salva o post gerado na tabela 'posts' do banco de dados SQLite.
        """
        try:
            formatted_text = LinkedInFormatter.format_for_linkedin(post.content_md)
            res = self.repository.save_post(
                post=post,
                status="draft",
                formatted_linkedin_text=formatted_text,
            )

            return PublishResult(
                publisher_name=self.name,
                success=True,
                post_url=None,
                message=f"Post '{post.slug}' salvo no banco de dados SQLite com status '{res.get('status')}'!",
            )
        except Exception as err:
            return PublishResult(
                publisher_name=self.name,
                success=False,
                post_url=None,
                message=f"Erro ao salvar post no banco de dados: {err}",
            )

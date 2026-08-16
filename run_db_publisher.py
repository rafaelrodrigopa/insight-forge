import argparse
import sys
from typing import Optional

from app.agents.writer.schemas import PostContent
from app.db.repository import PostRepository
from app.publish.publishers.linkedin_publisher import LinkedInPublisherAdapter


def publish_pending_posts(limit: int = 5, slug_filter: Optional[str] = None):
    print("==================================================")
    print("Insight Forge -- Publicador sob Demanda (PostgreSQL)")
    print("==================================================")

    repo = PostRepository()

    if slug_filter:
        post_dict = repo.get_post_by_slug(slug_filter)
        pending_posts = [post_dict] if post_dict and post_dict.get("status") == "draft" else []
    else:
        pending_posts = repo.list_pending_posts(limit=limit)

    if not pending_posts:
        print("\nNenhum post pendente com status 'draft' foi encontrado no banco de dados.")
        return

    print(f"\n[+] Encontrado(s) {len(pending_posts)} post(s) pendente(s) no banco de dados:")
    for idx, p in enumerate(pending_posts, 1):
        print(f"  {idx}. [{p['slug']}] {p['title']}")

    linkedin_publisher = LinkedInPublisherAdapter()

    for p in pending_posts:
        print(f"\n🚀 Disparando publicação no LinkedIn para: \"{p['title']}\"...")

        post_obj = PostContent(
            title=p["title"],
            slug=p["slug"],
            date="",
            content_md=p["content_md"],
            topics=[],
            image_path=p.get("image_path"),
            source_url=p.get("source_url"),
        )

        res = linkedin_publisher.publish(post_obj)

        if res.success:
            repo.mark_as_published(slug=p["slug"], post_url=res.post_url)
            print(f"   ✅ [SUCESSO]: {res.message}")
        else:
            print(f"   ⚠️ [FALHA]: {res.message}")

    print("\n==================================================")
    print("PROCESSAMENTO DO BANCO CONCLUÍDO!")
    print("==================================================")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Insight Forge -- Publica posts pendentes gravados no PostgreSQL/Database"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Quantidade máxima de posts pendentes a processar",
    )
    parser.add_argument(
        "--slug",
        type=str,
        default=None,
        help="Slug específico de um post no banco para publicar",
    )

    args = parser.parse_args()
    publish_pending_posts(limit=args.limit, slug_filter=args.slug)

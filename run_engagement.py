import argparse
import sys
from dotenv import load_dotenv

load_dotenv()
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from app.workflows.engagement_pipeline import run_engagement_pipeline


def main():
    parser = argparse.ArgumentParser(
        description="Insight Forge -- Pipeline de Engajamento Autônomo para o LinkedIn"
    )
    parser.add_argument(
        "--publish",
        action="store_true",
        help="Executa a publicação real das interações (Like + Comentários) na API do LinkedIn",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=3,
        help="Número máximo de posts a interagir por execução (padrão: 3)",
    )
    parser.add_argument(
        "--discover-limit",
        type=int,
        default=15,
        help="Número máximo de posts a pesquisar no feed (padrão: 15)",
    )

    args = parser.parse_args()

    run_engagement_pipeline(
        max_discovery=args.discover_limit,
        max_interactions=args.limit,
        enable_publish=args.publish,
    )


if __name__ == "__main__":
    main()

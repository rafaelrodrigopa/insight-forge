from datetime import datetime
import os
import sys
from typing import Optional

# Configura o stdout para UTF-8 em consoles Windows se necessário
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from app.agents.classifier import ClassifierAgent
from app.agents.collector import CollectorAgent
from app.agents.critic import CriticAgent
from app.agents.prioritizer import PrioritizerAgent
from app.agents.summarizer import SummarizerAgent
from app.agents.writer import WriterAgent
from app.preprocess import ContentDeduplicator
from app.publish import BannerGenerator, PublisherManager
from app.ranking import ContentScorer


def run_pipeline(
    source_url: Optional[str] = None,
    process_all: bool = False,
    platform: str = "markdown",
    enable_publish: bool = False,
    force_process: bool = False,
):
    url = source_url or "https://realpython.com/atom.xml"

    print("==================================================")
    print(f"Insight Forge -- Pipeline Multiagente ({platform.upper()})")
    print("==================================================")

    # 1. Agente Coletor
    collector = CollectorAgent()
    try:
        if source_url:
            print(f"Fonte configurada (Única): {source_url}\n")
            print("1. [CollectorAgent] Coletando notícias da fonte indicada...")
            collected_items = collector.collect(source_url, analyze_with_ai=False)
        else:
            print("Fonte configurada: Pool Multi-Feeds (Power BI, IA, Cloud, Geral & Mercado)\n")
            print("1. [CollectorAgent] Coletando notícias do Pool de Feeds RSS...")
            collected_items = collector.collect_pool(max_items_per_feed=5, analyze_with_ai=False)

        print(f"   -> {len(collected_items)} itens totais coletados no pool.")
    except Exception as err:
        print(f"Erro ao coletar feeds RSS: {err}")
        return

    if not collected_items:
        print("Nenhum item encontrado nas fontes informadas.")
        return

    # 2. Preprocessamento & Deduplicação
    print("\n2. [Preprocess] Deduplicando conteúdos...")
    deduplicator = ContentDeduplicator(similarity_threshold=0.60)
    unique_items = deduplicator.deduplicate(collected_items)
    removed_dups = len(collected_items) - len(unique_items)
    print(f"   -> {removed_dups} notícias duplicadas removidas ({len(unique_items)} únicas restantes).")

    # 3. Filtrar itens já gravados em posts/
    writer = WriterAgent()
    existing_files = os.listdir("posts") if os.path.exists("posts") else []
    existing_contents = []
    if os.path.exists("posts"):
        for fname in existing_files:
            if fname.endswith(".md"):
                fpath = os.path.join("posts", fname)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        existing_contents.append(f.read())
                except Exception:
                    pass

    unprocessed_items = []
    if force_process:
        unprocessed_items = unique_items
    else:
        for item in unique_items:
            slug = writer.service._slugify(item.title)
            already_exists = any(slug in filename for filename in existing_files)
            item_link = getattr(item, "link", None) or getattr(item, "source_url", None)
            if not already_exists and item_link:
                already_exists = any(item_link in content for content in existing_contents)
            if not already_exists:
                unprocessed_items.append(item)

    print(f"   -> {len(unprocessed_items)} notícias a processar.")

    if not unprocessed_items:
        print("\nTodas as notícias deste feed já foram processadas na pasta posts/!")
        print("Dica: Use a flag --force se desejar re-processar e publicar novamente.")
        return

    # 4. Agente Classificador
    print("\n3. [ClassifierAgent] Classificando categorias e tags técnicas...")
    classifier = ClassifierAgent()
    classification_result = classifier.classify(unprocessed_items[0])
    print(f"   -> Categoria Principal: {classification_result.primary_category}")
    print(f"   -> Categorias Secundárias: {', '.join(classification_result.secondary_categories)}")

    # 5. Agente Priorizador
    print("\n4. [PrioritizerAgent] Avaliando prioridade editorial...")
    prioritizer = PrioritizerAgent()
    priority_decision = prioritizer.evaluate(unprocessed_items[0])
    print(f"   -> Score Editorial: {priority_decision.priority_score}/100 | Publicar: {'SIM' if priority_decision.should_publish else 'NÃO'}")

    # 6. Ranking Engine
    print("\n5. [RankingEngine] Ranqueando relevância das notícias...")
    scorer = ContentScorer()
    ranked_items = scorer.rank_items(unprocessed_items)
    print("   -> Destaque selecionado pelo ranking:")
    target_item = ranked_items[0].item
    print(f"      Score {ranked_items[0].score}/100: \"{target_item.title}\"")

    items_to_process = [r.item for r in ranked_items] if process_all else [target_item]

    summarizer = SummarizerAgent()
    critic = CriticAgent()
    banner_generator = BannerGenerator(output_dir="posts/images")
    publisher_manager = PublisherManager.create_default(
        enable_linkedin=(platform == "linkedin" and enable_publish)
    )

    for idx, item in enumerate(items_to_process, 1):
        print(f"\n--- [{idx}/{len(items_to_process)}] Processando: \"{item.title}\" ---")

        # 7. Agente Sumarizador
        print("6. [SummarizerAgent] Gerando resumo estruturado...")
        summary_result = summarizer.summarize(item)
        print(f"   -> Tópicos: {', '.join(summary_result.topics)}")

        # Gerador de Imagem / Banner Visual Dinâmico para a Notícia
        print("   -> [BannerGenerator] Gerando imagem de capa personalizada...")
        today_str = datetime.now().strftime("%Y-%m-%d")
        item_slug = writer.service._slugify(item.title)
        image_path = banner_generator.generate_banner(
            title=item.title,
            topics=summary_result.topics,
            slug=item_slug,
            date_str=today_str,
        )
        print(f"   -> Imagem criada: {image_path}")

        # 8. Agente Redator
        print(f"7. [WriterAgent] Redigindo post para formato {platform.upper()}...")
        if platform == "linkedin":
            post_content = writer.write_linkedin_post(
                summary_result, image_path=image_path
            )
        else:
            post_content = writer.write_post(summary_result)
            post_content.image_path = image_path

        # 9. Agente Crítico / Revisor
        print("8. [CriticAgent] Revisando e polindo o post...")
        review_result = critic.review(post_content.content_md)
        print(f"   -> Nota de Qualidade Editorial: {review_result.quality_score}/10.0")

        # Atualiza o arquivo final com o conteúdo revisado pelo CriticAgent se aprovado
        if review_result.revised_markdown and review_result.approved:
            revised_md = review_result.revised_markdown
            if not revised_md.startswith("---"):
                revised_md = writer.service._add_frontmatter_if_missing(
                    raw_markdown=revised_md,
                    title=summary_result.title,
                    date_str=today_str,
                    topics=summary_result.topics,
                    source_url=summary_result.source_url,
                    image_path=image_path,
                )
            writer.service._save_to_disk(post_content.file_path, revised_md)
            post_content.content_md = revised_md
            post_content.image_path = image_path
            print(f"   -> Post revisado salvo em: {post_content.file_path}")

        # 10. Disparo dos Publicadores Multi-Canal
        print("\n9. [PublisherManager] Disparando publicadores ativos...")
        results = publisher_manager.publish_all(post_content)
        for res in results:
            status_icon = "✅" if res.success else "⚠️"
            print(f"   {status_icon} [{res.publisher_name}]: {res.message}")

    print("\n==================================================")
    print("PIPELINE MULTIAGENTE CONCLUÍDO COM SUCESSO!")
    print("==================================================")


if __name__ == "__main__":
    source_arg = None
    all_flag = False
    platform_arg = "markdown"
    publish_flag = False
    force_flag = False

    for arg in sys.argv[1:]:
        if arg == "--all":
            all_flag = True
        elif arg == "--linkedin":
            platform_arg = "linkedin"
        elif arg == "--publish":
            publish_flag = True
        elif arg == "--force":
            force_flag = True
        elif not arg.startswith("--"):
            source_arg = arg

    run_pipeline(
        source_arg,
        process_all=all_flag,
        platform=platform_arg,
        enable_publish=publish_flag,
        force_process=force_flag,
    )

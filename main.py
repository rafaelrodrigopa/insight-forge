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
from app.db.repository import PostRepository
from app.preprocess import ContentDeduplicator
from app.publish import BannerGenerator, PublisherManager
from app.ranking import ContentScorer

DAYS_WINDOW = 30


def run_pipeline(
    source_url: Optional[str] = None,
    process_all: bool = False,
    platform: str = "markdown",
    enable_publish: bool = False,
    force_process: bool = False,
    save_db: bool = False,
    ignore_history: bool = False,
):
    url = source_url or "https://realpython.com/atom.xml"

    print("==================================================")
    print(f"Insight Forge -- Pipeline Multiagente ({platform.upper()})")
    print("==================================================")

    repo = PostRepository()

    # Sincronização autônoma: verifica se algum post recente foi excluído no LinkedIn
    cleaned = repo.sync_deleted_posts(days_window=DAYS_WINDOW)
    if cleaned > 0:
        print(f"   [LinkedIn Sync] {cleaned} post(s) excluídos manualmente no perfil foram desmarcados no SQLite.\n")

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

    # 3. Filtrar itens já gravados em posts/ e no banco de dados SQLite
    writer = WriterAgent()
    existing_source_urls = set()
    existing_slugs = set()

    # Carrega URLs e slugs já salvos no banco SQLite
    try:
        conn, _ = repo.db.get_connection() if hasattr(repo, 'db') else (None, None)
        from app.db.connection import DatabaseConnection
        conn, _ = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT source_url, slug FROM posts WHERE COALESCE(posted_at, published_at, created_at) >= datetime('now', '-30 days');")
        for row in cursor.fetchall():
            if row[0]:
                existing_source_urls.add(row[0].strip())
                existing_source_urls.add(row[0].split("?")[0].strip())
            if row[1]:
                existing_slugs.add(row[1].strip())
        cursor.close()
        conn.close()
    except Exception:
        pass

    if os.path.exists("posts"):
        for fname in os.listdir("posts"):
            if fname.endswith(".md"):
                fpath = os.path.join("posts", fname)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        content = f.read()
                    import re as _re
                    url_match = _re.search(
                        r'^source_url:\s*["\']?([^"\'\s\n]+)["\']?',
                        content,
                        _re.MULTILINE,
                    )
                    if url_match and url_match.group(1):
                        existing_source_urls.add(url_match.group(1).strip())
                    slug_part = fname.rsplit(".", 1)[0]
                    slug_part = _re.sub(r"^\d{4}-\d{2}-\d{2}-", "", slug_part)
                    existing_slugs.add(slug_part)
                except Exception:
                    pass

    unprocessed_items = []
    if force_process:
        unprocessed_items = unique_items
    else:
        for item in unique_items:
            item_url = getattr(item, "url", "") or ""
            if item_url and item_url in existing_source_urls:
                continue
            slug = writer.service._slugify(item.title)
            if slug and any(slug in existing_slug for existing_slug in existing_slugs):
                continue
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

    # 6. Ranking Engine & Deduplicação por Janela Temporal (30 dias)
    if ignore_history:
        print(f"\n5. [RankingEngine] Ranqueando relevância (Flag --ignore-history ativada: ignorando trava de {DAYS_WINDOW} dias)...")
    else:
        print(f"\n5. [RankingEngine] Ranqueando relevância e verificando janela temporal ({DAYS_WINDOW} dias)...")

    scorer = ContentScorer()
    ranked_items = scorer.rank_items(unprocessed_items)

    eligible_ranked = []
    for r in ranked_items:
        item = r.item
        item_url = getattr(item, "url", "") or ""
        slug = writer.service._slugify(item.title)

        if not force_process and not ignore_history and repo.is_recently_posted(source_url=item_url, slug=slug, days_window=DAYS_WINDOW):
            print(f"   [Deduplicação Temporal] Ignorando \"{item.title}\" (já postada nos últimos {DAYS_WINDOW} dias). Avaliando próxima do ranking...")
            continue

        eligible_ranked.append(r)

    if not eligible_ranked:
        print(f"\n[Deduplicação Temporal] Todas as notícias ranqueadas já foram publicadas nos últimos {DAYS_WINDOW} dias.")
        print("Ciclo finalizado graciosamente sem disparar publicações duplicadas.")
        return

    target_item = eligible_ranked[0].item
    print(f"   -> Destaque selecionado pelo ranking (não postado nos últimos {DAYS_WINDOW} dias):")
    print(f"      Score {eligible_ranked[0].score}/100: \"{target_item.title}\"")

    items_to_process = [r.item for r in eligible_ranked] if process_all else [target_item]

    summarizer = SummarizerAgent()
    critic = CriticAgent()
    banner_generator = BannerGenerator(output_dir="posts/images")
    publisher_manager = PublisherManager.create_default(
        enable_linkedin=(platform == "linkedin" and enable_publish),
        enable_db=save_db,
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
        item_slug = writer.service._slugify(summary_result.title)
        image_path = banner_generator.generate_banner(
            title=summary_result.title,
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
        linkedin_post_url = None
        for res in results:
            status_icon = "✅" if res.success else "⚠️"
            print(f"   {status_icon} [{res.publisher_name}]: {res.message}")
            if res.post_url:
                linkedin_post_url = res.post_url

        # Registra no banco SQLite o histórico de postagem com a URL do post para controle de sincronização
        repo.record_posted_at(
            slug=post_content.slug,
            source_url=getattr(post_content, "source_url", None),
            post_url=linkedin_post_url,
        )

    print("\n==================================================")
    print("PIPELINE MULTIAGENTE CONCLUÍDO COM SUCESSO!")
    print("==================================================")


if __name__ == "__main__":
    source_arg = None
    all_flag = False
    platform_arg = "markdown"
    publish_flag = False
    force_flag = False
    db_flag = True
    ignore_history_flag = False

    for arg in sys.argv[1:]:
        clean_arg = arg.lstrip("-").lower()
        if clean_arg == "all":
            all_flag = True
        elif clean_arg == "linkedin":
            platform_arg = "linkedin"
        elif clean_arg in ("publish", "public"):
            publish_flag = True
        elif clean_arg == "force":
            force_flag = True
        elif clean_arg in ("no-db", "disable-db"):
            db_flag = False
        elif clean_arg in ("ignore-history", "ignorehistory", "no-history"):
            ignore_history_flag = True
        elif not arg.startswith("-"):
            source_arg = arg

    run_pipeline(
        source_arg,
        process_all=all_flag,
        platform=platform_arg,
        enable_publish=publish_flag,
        force_process=force_flag,
        save_db=db_flag,
        ignore_history=ignore_history_flag,
    )

import os
import sys
from typing import Optional

# Configura o stdout para UTF-8 em consoles Windows se necessário
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from app.agents.collector import CollectorAgent
from app.agents.summarizer import SummarizerAgent
from app.agents.writer import WriterAgent
from app.preprocess import ContentDeduplicator
from app.ranking import ContentScorer


def run_pipeline(source_url: Optional[str] = None, process_all: bool = False):
    url = source_url or "https://realpython.com/atom.xml"

    print("==================================================")
    print("Insight Forge -- Pipeline de Automação de Conteúdo")
    print("==================================================")
    print(f"Fonte configurada: {url}\n")

    # 1. Agente Coletor
    print("1. [CollectorAgent] Coletando notícias do feed...")
    collector = CollectorAgent()
    try:
        collected_items = collector.collect(url, analyze_with_ai=False)
        print(f"   -> {len(collected_items)} itens coletados no feed.")
    except Exception as err:
        print(f"Erro ao coletar feed RSS: {err}")
        return

    if not collected_items:
        print("Nenhum item encontrado na fonte informada.")
        return

    # 2. Deduplicação Semântica
    print("\n2. [Preprocess] Deduplicando notícias...")
    deduplicator = ContentDeduplicator(similarity_threshold=0.60)
    unique_items = deduplicator.deduplicate(collected_items)
    removed_dups = len(collected_items) - len(unique_items)
    print(f"   -> {removed_dups} notícias duplicadas removidas ({len(unique_items)} únicas restantes).")

    # 3. Filtrar itens já existentes em posts/
    writer = WriterAgent()
    existing_files = os.listdir("posts") if os.path.exists("posts") else []

    unprocessed_items = []
    for item in unique_items:
        slug = writer.service._slugify(item.title)
        already_exists = any(slug in filename for filename in existing_files)
        if not already_exists:
            unprocessed_items.append(item)

    print(f"   -> {len(unprocessed_items)} notícias inéditas disponíveis.")

    if not unprocessed_items:
        print("\nTodas as notícias deste feed já foram processadas na pasta posts/!")
        return

    # 4. Ranking Engine (Pontuação 0-100)
    print("\n3. [RankingEngine] Ranqueando relevância das notícias...")
    scorer = ContentScorer()
    ranked_items = scorer.rank_items(unprocessed_items)

    print("   -> Ranking dos principais destaques:")
    for idx, r in enumerate(ranked_items[:3], 1):
        topics_str = ", ".join(r.matched_topics) if r.matched_topics else "Geral"
        print(f"      #{idx} Score {r.score}/100: \"{r.item.title}\" (Tópicos: {topics_str})")

    items_to_process = [r.item for r in ranked_items] if process_all else [ranked_items[0].item]

    summarizer = SummarizerAgent()

    for idx, target_item in enumerate(items_to_process, 1):
        print(f"\n--- [{idx}/{len(items_to_process)}] Processando Destaque: \"{target_item.title}\" ---")

        # 5. Agente Sumarizador
        print("4. [SummarizerAgent] Gerando resumo estruturado via IA...")
        summary_result = summarizer.summarize(target_item)
        print(f"   -> Tópicos identificados: {', '.join(summary_result.topics)}")

        # Re-calcula o ranking refinado com a nota da IA
        refined_rank = scorer.score_content(target_item, summary=summary_result)
        print(f"   -> Score refinado final: {refined_rank.score}/100")

        # 6. Agente Redator
        print("5. [WriterAgent] Redigindo post em Markdown...")
        post_content = writer.write_post(summary_result)
        print(f"   -> Post salvo em: {post_content.file_path}")

    print("\n==================================================")
    print("PIPELINE CONCLUÍDO COM SUCESSO!")
    print("==================================================")


if __name__ == "__main__":
    source_arg = None
    all_flag = False

    for arg in sys.argv[1:]:
        if arg == "--all":
            all_flag = True
        elif not arg.startswith("--"):
            source_arg = arg

    run_pipeline(source_arg, process_all=all_flag)

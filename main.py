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
from app.ranking import ContentScorer


def run_pipeline(source_url: Optional[str] = None, process_all: bool = False):
    url = source_url or "https://realpython.com/atom.xml"

    print("==================================================")
    print("Insight Forge -- Pipeline Multiagente de Conteúdo")
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

    # 2. Preprocessamento & Deduplicação
    print("\n2. [Preprocess] Deduplicando conteúdos...")
    deduplicator = ContentDeduplicator(similarity_threshold=0.60)
    unique_items = deduplicator.deduplicate(collected_items)
    removed_dups = len(collected_items) - len(unique_items)
    print(f"   -> {removed_dups} notícias duplicadas removidas ({len(unique_items)} únicas restantes).")

    # 3. Filtrar itens já gravados em posts/
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

    for idx, item in enumerate(items_to_process, 1):
        print(f"\n--- [{idx}/{len(items_to_process)}] Processando: \"{item.title}\" ---")

        # 7. Agente Sumarizador
        print("6. [SummarizerAgent] Gerando resumo estruturado...")
        summary_result = summarizer.summarize(item)
        print(f"   -> Tópicos: {', '.join(summary_result.topics)}")

        # 8. Agente Redator
        print("7. [WriterAgent] Redigindo post em Markdown...")
        post_content = writer.write_post(summary_result)

        # 9. Agente Crítico / Revisor
        print("8. [CriticAgent] Revisando e polindo o artigo...")
        review_result = critic.review(post_content.content_md)
        print(f"   -> Nota de Qualidade Editorial: {review_result.quality_score}/10.0")

        # Atualiza o arquivo final com o conteúdo revisado pelo CriticAgent se aprovado
        if review_result.revised_markdown and review_result.approved:
            writer.service._save_to_disk(post_content.file_path, review_result.revised_markdown)
            print(f"   -> Post revisado salvo em: {post_content.file_path}")

    print("\n==================================================")
    print("PIPELINE MULTIAGENTE CONCLUÍDO COM SUCESSO!")
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

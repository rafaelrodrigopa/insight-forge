import os
import sys
from typing import Optional

# Configura o stdout para UTF-8 em consoles Windows se necessário
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from app.agents.collector import CollectorAgent
from app.agents.summarizer import SummarizerAgent
from app.agents.writer import WriterAgent


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
        print(f"   -> {len(collected_items)} itens encontrados no feed.")
    except Exception as err:
        print(f"Erro ao coletar feed RSS: {err}")
        return

    if not collected_items:
        print("Nenhum item encontrado na fonte informada.")
        return

    writer = WriterAgent()
    existing_files = os.listdir("posts") if os.path.exists("posts") else []

    # Encontra os itens do feed que ainda não foram gerados na pasta posts/
    unprocessed_items = []
    for item in collected_items:
        slug = writer.service._slugify(item.title)
        already_exists = any(slug in filename for filename in existing_files)
        if not already_exists:
            unprocessed_items.append(item)

    print(f"   -> {len(unprocessed_items)} novas notícias não processadas.")

    if not unprocessed_items:
        print("\nTodas as notícias deste feed já foram processadas e geradas na pasta posts/!")
        return

    items_to_process = unprocessed_items if process_all else [unprocessed_items[0]]

    summarizer = SummarizerAgent()

    for idx, target_item in enumerate(items_to_process, 1):
        print(f"\n--- [{idx}/{len(items_to_process)}] Processando: \"{target_item.title}\" ---")

        # 2. Agente Sumarizador
        print("2. [SummarizerAgent] Gerando resumo estruturado via IA...")
        summary_result = summarizer.summarize(target_item)
        print(f"   -> Tópicos: {', '.join(summary_result.topics)}")
        print(f"   -> Pontuação de Relevância: {summary_result.relevance_score}/10")

        # 3. Agente Redator
        print("3. [WriterAgent] Redigindo post em Markdown...")
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

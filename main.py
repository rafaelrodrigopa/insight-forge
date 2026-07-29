import sys
from typing import Optional

# Configura o stdout para UTF-8 em consoles Windows se necessário
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from app.agents.collector import CollectorAgent
from app.agents.summarizer import SummarizerAgent
from app.agents.writer import WriterAgent


def run_pipeline(source_url: Optional[str] = None):
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
        print(f"   -> {len(collected_items)} itens encontrados.")
    except Exception as err:
        print(f"Erro ao coletar feed RSS: {err}")
        return

    if not collected_items:
        print("Nenhum item encontrado na fonte informada.")
        return

    target_item = collected_items[0]
    print(f"   -> Processando item: \"{target_item.title}\"")

    # 2. Agente Sumarizador
    print("\n2. [SummarizerAgent] Gerando resumo estruturado via IA...")
    summarizer = SummarizerAgent()
    summary_result = summarizer.summarize(target_item)
    print(f"   -> Tópicos: {', '.join(summary_result.topics)}")
    print(f"   -> Pontuação de Relevância: {summary_result.relevance_score}/10")

    # 3. Agente Redator
    print("\n3. [WriterAgent] Redigindo post em Markdown...")
    writer = WriterAgent()
    post_content = writer.write_post(summary_result)

    print("\n==================================================")
    print("PIPELINE CONCLUÍDO COM SUCESSO!")
    print(f"Arquivo gerado: {post_content.file_path}")
    print("==================================================")


if __name__ == "__main__":
    feed_arg = sys.argv[1] if len(sys.argv) > 1 else None
    run_pipeline(feed_arg)

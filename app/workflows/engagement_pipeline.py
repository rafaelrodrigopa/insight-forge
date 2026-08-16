from typing import List, Optional

from app.agents.engagement.agent import EngagementAgent
from app.agents.engagement.discoverer import PostDiscoverer
from app.agents.engagement.history import EngagementHistory
from app.providers.linkedin.publisher import LinkedInPublisher


def run_engagement_pipeline(
    max_discovery: int = 15,
    max_interactions: int = 3,
    enable_publish: bool = True,
) -> int:
    """
    Executa o workflow completo de engajamento comunitário autônomo no LinkedIn:
    1. Descobre posts recentes em Power BI, Fabric, BigQuery e Data Engineering.
    2. Filtra posts já interagidos no histórico local.
    3. Avalia relevância e gera comentários técnicos via EngagementAgent.
    4. Dispara Like + Comentário via LinkedIn API.
    5. Registra o histórico de interações.
    """
    print("==================================================")
    print("Insight Forge -- Pipeline de Engajamento Autônomo")
    print("==================================================")

    # 1. Descoberta de Posts Recentes
    print("1. [PostDiscoverer] Buscando posts recentes da comunidade...")
    discoverer = PostDiscoverer()
    posts = discoverer.discover_recent_posts(max_posts=max_discovery)
    print(f"   -> {len(posts)} posts descobertos na rede.")

    if not posts:
        print("Nenhum post novo encontrado no momento.")
        return 0

    # 2. Filtragem contra histórico
    history = EngagementHistory()
    fresh_posts = [p for p in posts if not history.is_interacted(p.post_urn)]
    print(f"   -> {len(fresh_posts)} posts inéditos não interagidos.")

    if not fresh_posts:
        print("Todos os posts descobertos já foram interagidos anteriormente.")
        return 0

    # 3. Avaliação de Relevância e Geração de Comentários por IA
    print("\n2. [EngagementAgent] Avaliando posts com IA e gerando comentários...")
    agent = EngagementAgent()
    publisher = LinkedInPublisher() if enable_publish else None

    successful_interactions = 0

    for post in fresh_posts:
        if successful_interactions >= max_interactions:
            print(f"\n🎯 Limite de {max_interactions} interações diárias atingido.")
            break

        print(f"\n--- Avaliando: [{post.topic}] {post.title[:70]}... ---")
        decision = agent.evaluate_and_comment(post)

        if not decision.should_engage:
            print(f"   ❌ Rejeitado pela IA: {decision.reasoning or 'Não alinhado'}")
            continue

        print(f"   ✅ Aprovado! Reação: {decision.suggested_reaction}")
        print(f"   💬 Comentário Gerado: \"{decision.generated_comment}\"")

        # 4. Execução no LinkedIn
        if enable_publish and publisher:
            print(f"   🚀 Publicando Like + Comentário no LinkedIn ({post.post_urn})...")
            try:
                # Dispara Like
                publisher.react_to_post(post.post_urn, decision.suggested_reaction)
                # Dispara Comentário
                publisher.comment_on_post(post.post_urn, decision.generated_comment)

                # Grava no Histórico
                history.record_interaction(
                    post_urn=post.post_urn,
                    reaction=decision.suggested_reaction,
                    comment=decision.generated_comment or "",
                    title=post.title,
                    topic=post.topic or "",
                )
                successful_interactions += 1
                print("   ✅ Interação realizada com sucesso no LinkedIn!")
            except Exception as err:
                print(f"   ⚠️ Erro ao publicar interação na API do LinkedIn: {err}")
                if "403" in str(err):
                    print("   💡 [DICA DE PERMISSÃO]: Para liberar curtidas e comentários na API, ative o produto gratuito 'Community Management API' na sua conta de desenvolvedor do LinkedIn (https://www.linkedin.com/developers/apps).")
        else:
            print("   ℹ️ Modo de teste (sem publicação ativada).")
            history.record_interaction(
                post_urn=post.post_urn,
                reaction=decision.suggested_reaction,
                comment=decision.generated_comment or "",
                title=post.title,
                topic=post.topic or "",
            )
            successful_interactions += 1

    print("\n==================================================")
    print(f"PIPELINE DE ENGAJAMENTO CONCLUÍDO: {successful_interactions} interações realizadas!")
    print("==================================================")
    return successful_interactions

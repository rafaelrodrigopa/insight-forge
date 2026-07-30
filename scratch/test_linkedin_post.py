import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from app.agents.writer.schemas import PostContent
from app.publish.publishers.linkedin_publisher import LinkedInPublisherAdapter

post = PostContent(
    title="Insight Forge Multi-Agent Automated Test",
    slug="insight-forge-test",
    date="2026-07-30",
    content_md="""---
title: "Insight Forge Multi-Agent Automated Test"
date: "2026-07-30"
---

🚀 O Insight Forge agora está integrado com a API oficial do LinkedIn!

Este post foi gerado e publicado 100% de forma autônoma pela arquitetura de 6 agentes especializados de IA.

#Python #SoftwareEngineering #MultiAgent #AI #CleanCode""",
    topics=["Python", "AI"],
    source_url="https://github.com/rafaelrodrigopa/insight-forge",
    file_path="posts/2026-07-30-insight-forge-test.md",
)

adapter = LinkedInPublisherAdapter()
result = adapter.publish(post)

print("RESULTADO DA PUBLICAÇÃO NO LINKEDIN:")
print("Sucesso:", result.success)
print("URL do Post:", result.post_url)
print("Mensagem:", result.message)

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from app.agents.summarizer.schemas import SummaryResult
from app.agents.writer import WriterAgent
from app.publish.publishers.linkedin_publisher import LinkedInFormatter

summary = SummaryResult(
    title="Managing Imports With Python's __all__",
    summary="Explica como a variável dunder all em Python controla a exportação de módulos e define a API pública de pacotes.",
    key_points=[
        "Evita a poluição do namespace global em importações wildcard.",
        "Define explicitamente os símbolos públicos expostos pelo módulo.",
        "Protege funções auxiliares e dependências internas."
    ],
    topics=["Python", "Engenharia de Software", "Clean Code"],
    source_url="https://realpython.com/courses/managing-imports-dunder-all/",
)

writer = WriterAgent()
post = writer.write_linkedin_post(summary, image_path="posts/images/managing-imports-with-pythons-all.png")

formatted_text = LinkedInFormatter.format_for_linkedin(post.content_md)

print("==================================================")
print("NOVO POST FORMATADO PARA O LINKEDIN:")
print("==================================================")
print(formatted_text)

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from app.providers.linkedin import LinkedInPublisher

publisher = LinkedInPublisher()

test_text = """🚀 Teste de publicação automatizada pelo Insight Forge!

O ecossistema multiagente de IA está operacional e integrado via API oficial do LinkedIn.

#Python #SoftwareEngineering #MultiAgent #AI #CleanCode"""

res = publisher.publish_text(test_text)

print("STATUS CODE:", res.status_code)
print("HEADERS:", dict(res.headers))
print("BODY:", res.text)

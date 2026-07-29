import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from app.config.settings import settings
from google import genai

key = settings.GEMINI_API_KEY
client = genai.Client(api_key=key)

for m in ["gemini-3.6-flash", "gemini-3.5-flash-lite", "gemini-3.1-flash-lite"]:
    try:
        res = client.models.generate_content(model=m, contents="Test OK")
        print(f"SUCESSO [{m}]: {res.text.strip()}")
    except Exception as e:
        print(f"ERRO [{m}]: {str(e)[:150]}")

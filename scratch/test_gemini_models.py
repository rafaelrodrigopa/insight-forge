import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from app.config.settings import settings
from google import genai

key = settings.GEMINI_API_KEY
client = genai.Client(api_key=key)

test_models = [
    "gemini-flash-latest",
    "gemini-3.5-flash",
    "gemini-3.6-flash",
    "gemma-4-26b-a4b-it",
]

for model in test_models:
    try:
        res = client.models.generate_content(
            model=model,
            contents="Diga 'OK' em 1 palavra.",
        )
        print(f"SUCESSO [{model}]: {res.text.strip()}")
    except Exception as e:
        print(f"ERRO [{model}]: {str(e)[:150]}")

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from app.config.settings import settings
from google import genai
from google.genai import types

key = settings.GEMINI_API_KEY
client = genai.Client(api_key=key)

for m in ["gemini-3.1-flash-image", "gemini-2.5-flash-image", "gemini-3-pro-image"]:
    try:
        res = client.models.generate_content(
            model=m,
            contents="Create a high resolution technical cover image for a Python AI software article.",
            config=types.GenerateContentConfig(
                response_mime_type="image/jpeg"
            )
        )
        print(f"SUCESSO [{m}]: {len(res.candidates[0].content.parts)} partes retornadas.")
    except Exception as e:
        print(f"ERRO [{m}]: {str(e)[:150]}")

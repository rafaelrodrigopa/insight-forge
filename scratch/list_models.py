import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from app.config.settings import settings
from google import genai

key = settings.GEMINI_API_KEY
client = genai.Client(api_key=key)

print("Listing models:")
for m in client.models.list():
    print(m.name)

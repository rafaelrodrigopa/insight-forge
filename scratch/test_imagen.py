import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from app.config.settings import settings
from google import genai

key = settings.GEMINI_API_KEY
client = genai.Client(api_key=key)

imagen_models = [
    "imagen-4.0-fast-generate-001",
    "imagen-4.0-generate-001",
    "imagen-3.0-generate-002",
]

for model in imagen_models:
    try:
        res = client.models.generate_images(
            model=model,
            prompt="A modern sleek dark-mode tech banner for Python software engineering.",
            config=dict(number_of_images=1, output_mime_type="image/png"),
        )
        print(f"SUCESSO [{model}]: {len(res.generated_images)} imagens geradas!")
    except Exception as e:
        print(f"ERRO [{model}]: {str(e)[:150]}")

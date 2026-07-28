from app.providers.gemini import GeminiChat

chat = GeminiChat()

print(
    chat.generate(
        "Explique em uma frase o que é Business Intelligence."
    )
)
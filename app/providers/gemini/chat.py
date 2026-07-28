from .client import GeminiClient
from .models import GeminiModels


class GeminiChat:

    def __init__(self):
        self.client = GeminiClient().client

    def generate(self, prompt: str):

        response = self.client.models.generate_content(
            model=GeminiModels.FLASH,
            contents=prompt,
        )

        return response.text
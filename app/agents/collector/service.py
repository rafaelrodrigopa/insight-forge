from app.providers.gemini import GeminiChat

from .prompt import COLLECTOR_SYSTEM_PROMPT


class CollectorService:

    def __init__(self):
        self.gemini = GeminiChat()

    def collect(self, source: str):
        """
        Coleta conteúdos da fonte informada.
        """

        prompt = f"""
{COLLECTOR_SYSTEM_PROMPT}

Fonte:

{source}
"""

        return self.gemini.generate(prompt)
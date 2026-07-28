from .service import CollectorService


class CollectorAgent:

    def __init__(self):
        self.service = CollectorService()

    def collect(self, source: str):
        """
        Executa o processo de coleta de conteúdo.
        """

        return self.service.collect(source)
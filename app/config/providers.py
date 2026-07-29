from typing import Dict


class ProvidersConfig:
    """
    Configurações centralizadas para Provedores de IA e Destinos de Publicação.
    """

    DEFAULT_LLM_PROVIDER: str = "gemini"
    DEFAULT_LLM_MODEL: str = "gemini-2.0-flash"
    DEFAULT_TEMPERATURE: float = 0.7
    DEFAULT_MAX_OUTPUT_TOKENS: int = 2048

    PROVIDER_MODELS: Dict[str, Dict[str, str]] = {
        "gemini": {
            "flash": "gemini-2.0-flash",
            "pro": "gemini-1.5-pro",
            "flash_lite": "gemini-2.0-flash",
        },
        "openai": {
            "flash": "gpt-4o-mini",
            "pro": "gpt-4o",
        },
        "ollama": {
            "flash": "llama3:8b",
            "pro": "llama3:70b",
        },
    }

    def get_model(self, provider: str = "gemini", tier: str = "flash") -> str:
        """
        Retorna o identificador do modelo para um determinado provedor e nível.
        """
        provider_dict = self.PROVIDER_MODELS.get(provider.lower(), {})
        return provider_dict.get(tier.lower(), self.DEFAULT_LLM_MODEL)


providers_config = ProvidersConfig()

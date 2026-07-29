from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class LLMResponse:
    """
    Estrutura padronizada de resposta para provedores de LLM.
    """

    text: str
    model: str
    finish_reason: Optional[str] = None
    raw_response: Any = None


class BaseLLMProvider(ABC):
    """
    Interface abstrata base para todos os provedores de LLM (Gemini, OpenAI, Ollama, Claude, etc.).
    """

    @abstractmethod
    def generate(
        self,
        prompt: str,
        *,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_output_tokens: int = 2048,
    ) -> LLMResponse:
        """
        Gera uma resposta de texto de chamada única (single-turn).
        """
        pass

    @abstractmethod
    def send_message(self, prompt: str) -> LLMResponse:
        """
        Envia uma mensagem no contexto da sessão de conversa (multi-turn/histórico).
        """
        pass

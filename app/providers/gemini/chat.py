from typing import List, Optional

from app.providers.base import BaseLLMProvider, LLMResponse
from app.providers.gemini.client import GeminiClient
from app.providers.gemini.models import GeminiModels


class GeminiChat(BaseLLMProvider):
    """
    Serviço de chat e geração utilizando modelos Gemini com suporte a histórico de conversas (multi-turn).
    """

    def __init__(
        self,
        *,
        model: str = GeminiModels.FLASH,
        system: str | None = None,
        temperature: float = 0.7,
        max_output_tokens: int = 2048,
        client: GeminiClient | None = None,
    ):
        self.client = client or GeminiClient()

        self.model = model
        self.system = system
        self.temperature = temperature
        self.max_output_tokens = max_output_tokens

        self._chat_session = None
        self._history: List[dict] = []

    def _get_or_create_session(self):
        if self._chat_session is None:
            config = {
                "temperature": self.temperature,
                "max_output_tokens": self.max_output_tokens,
            }

            if self.system:
                config["system_instruction"] = self.system

            if hasattr(self.client, "client") and hasattr(
                self.client.client, "chats"
            ):
                try:
                    self._chat_session = self.client.client.chats.create(
                        model=self.model,
                        config=config,
                    )
                except Exception:
                    self._chat_session = None
        return self._chat_session

    def send_message(self, prompt: str) -> LLMResponse:
        """
        Envia uma mensagem no contexto da sessão de conversa (preserva o histórico).
        """
        session = self._get_or_create_session()

        if session is not None:
            try:
                response = session.send_message(prompt)

                finish_reason = None
                if hasattr(response, "candidates") and response.candidates:
                    candidate = response.candidates[0]
                    if (
                        hasattr(candidate, "finish_reason")
                        and candidate.finish_reason
                    ):
                        finish_reason = str(candidate.finish_reason)

                text_content = (
                    response.text
                    if hasattr(response, "text") and response.text is not None
                    else ""
                )

                self._history.append({"role": "user", "content": prompt})
                self._history.append({"role": "model", "content": text_content})

                return LLMResponse(
                    text=text_content,
                    model=self.model,
                    finish_reason=finish_reason,
                    raw_response=response,
                )
            except Exception as error:
                self.client._handle_exception(error)

        # Fallback para chamadas com mock client ou sem chat API
        res = self.generate(prompt)
        self._history.append({"role": "user", "content": prompt})
        self._history.append({"role": "model", "content": res.text})
        return res

    def generate(
        self,
        prompt: str,
        *,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_output_tokens: int = 2048,
    ) -> LLMResponse:
        """
        Gera uma resposta avulsa (single-turn) sem alterar a sessão principal.
        """
        sys_prompt = system or self.system
        return self.client.generate(
            model=self.model,
            prompt=prompt,
            system=sys_prompt,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
        )

    def clear_history(self):
        """
        Limpa a sessão de conversa e o histórico gravado.
        """
        self._chat_session = None
        self._history = []

    def get_history() -> List[dict]:
        """
        Retorna o histórico de mensagens gravadas.
        """
        return self._history
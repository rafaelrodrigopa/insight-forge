from google import genai

from app.config.settings import settings
from app.providers.base import LLMResponse
from app.providers.gemini.exceptions import (
    GeminiAuthenticationError,
    GeminiBadRequestError,
    GeminiException,
    GeminiPermissionError,
    GeminiRateLimitError,
    GeminiServerError,
    GeminiTimeoutError,
)


class GeminiClient:

    def __init__(self, api_key: str | None = None):
        key = api_key or settings.GEMINI_API_KEY
        if not key:
            raise GeminiAuthenticationError("GEMINI_API_KEY não foi configurada.")

        self.client = genai.Client(api_key=key)

    def generate(
        self,
        *,
        model: str,
        prompt: str,
        system: str | None = None,
        temperature: float = 0.7,
        max_output_tokens: int = 2048,
    ) -> LLMResponse:
        config = {
            "temperature": temperature,
            "max_output_tokens": max_output_tokens,
        }

        if system:
            config["system_instruction"] = system

        try:
            response = self.client.models.generate_content(
                model=model,
                contents=prompt,
                config=config,
            )

            finish_reason = None
            if hasattr(response, "candidates") and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, "finish_reason") and candidate.finish_reason:
                    finish_reason = str(candidate.finish_reason)

            text_content = (
                response.text
                if hasattr(response, "text") and response.text is not None
                else ""
            )

            return LLMResponse(
                text=text_content,
                model=model,
                finish_reason=finish_reason,
                raw_response=response,
            )
        except Exception as error:
            self._handle_exception(error)

    @staticmethod
    def _handle_exception(error: Exception):
        """
        Converte exceções da API do Gemini em exceções do provider.
        """
        if isinstance(error, GeminiException):
            raise error

        error_name = error.__class__.__name__.lower()
        error_msg = str(error)
        lower_msg = error_msg.lower()

        if "unauth" in error_name or "auth" in error_name or "api_key" in lower_msg:
            raise GeminiAuthenticationError(error_msg) from error

        if "permission" in error_name or "forbidden" in error_name:
            raise GeminiPermissionError(error_msg) from error

        if (
            "resourceexhausted" in error_name
            or "ratelimit" in error_name
            or "quota" in lower_msg
        ):
            raise GeminiRateLimitError(error_msg) from error

        if (
            "invalid" in error_name
            or "badrequest" in error_name
            or "not_found" in lower_msg
            or "not found" in lower_msg
            or "clienterror" in error_name
        ):
            raise GeminiBadRequestError(error_msg) from error

        if "timeout" in error_name or "deadline" in error_name:
            raise GeminiTimeoutError(error_msg) from error

        if "internal" in error_name or "server" in error_name:
            raise GeminiServerError(error_msg) from error

        raise GeminiException(error_msg) from error
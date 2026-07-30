import unittest
from unittest.mock import MagicMock, patch

from app.config.settings import settings
from app.providers import BaseLLMProvider, LLMResponse
from app.providers.gemini import (
    GeminiAuthenticationError,
    GeminiChat,
    GeminiClient,
    GeminiModels,
    GeminiRateLimitError,
)


class TestGeminiProvider(unittest.TestCase):

    def test_provider_inherits_base(self):
        """Testa se GeminiChat herda de BaseLLMProvider."""
        self.assertTrue(issubclass(GeminiChat, BaseLLMProvider))

    def test_gemini_models_constants(self):
        """Testa se as constantes dos modelos estão definidas."""
        self.assertEqual(GeminiModels.FLASH, "gemini-3.6-flash")
        self.assertEqual(GeminiModels.PRO, "gemini-2.5-pro")

    @patch("app.providers.gemini.client.genai.Client")
    def test_client_generate_returns_llm_response(self, mock_genai_client_cls):
        """Testa se GeminiClient.generate retorna uma instância de LLMResponse."""
        mock_client_instance = MagicMock()
        mock_genai_client_cls.return_value = mock_client_instance

        mock_response = MagicMock()
        mock_response.text = "Resposta de teste"
        mock_response.candidates = [MagicMock(finish_reason="STOP")]
        mock_client_instance.models.generate_content.return_value = mock_response

        client = GeminiClient(api_key="test_api_key")
        res = client.generate(model="gemini-2.0-flash", prompt="Olá")

        self.assertIsInstance(res, LLMResponse)
        self.assertEqual(res.text, "Resposta de teste")
        self.assertEqual(res.model, "gemini-2.0-flash")
        self.assertEqual(res.finish_reason, "STOP")

    @patch("app.providers.gemini.client.genai.Client")
    def test_client_exception_mapping(self, mock_genai_client_cls):
        """Testa se as exceções da SDK são mapeadas corretamente."""
        mock_client_instance = MagicMock()
        mock_genai_client_cls.return_value = mock_client_instance

        class CustomResourceExhausted(Exception):
            pass

        mock_client_instance.models.generate_content.side_effect = (
            CustomResourceExhausted("ResourceExhausted error")
        )

        client = GeminiClient(api_key="test_api_key")
        with self.assertRaises(GeminiRateLimitError):
            client.generate(model="gemini-2.0-flash", prompt="Olá")

    def test_chat_single_turn_and_history(self):
        """Testa o chat mantendo histórico de mensagens."""
        mock_client = MagicMock()
        mock_session = MagicMock()
        mock_session_response = MagicMock()
        mock_session_response.text = "Resposta via mock"
        mock_session_response.candidates = [MagicMock(finish_reason="STOP")]
        mock_session.send_message.return_value = mock_session_response
        mock_client.client.chats.create.return_value = mock_session

        chat = GeminiChat(client=mock_client)
        res = chat.send_message("Primeira mensagem")

        self.assertIsInstance(res, LLMResponse)
        self.assertEqual(res.text, "Resposta via mock")
        self.assertEqual(len(chat._history), 2)
        self.assertEqual(chat._history[0]["content"], "Primeira mensagem")
        self.assertEqual(chat._history[1]["content"], "Resposta via mock")

        chat.clear_history()
        self.assertEqual(len(chat._history), 0)

    def test_missing_api_key_raises_error(self):
        """Testa se chave ausente lança GeminiAuthenticationError."""
        with patch.object(settings, "GEMINI_API_KEY", None):
            with self.assertRaises(GeminiAuthenticationError):
                GeminiClient(api_key=None)


class TestGeminiLiveIntegration(unittest.TestCase):

    def test_live_chat_call(self):
        """Teste de integração ao vivo com a API do Gemini (se chave configurada)."""
        if not settings.GEMINI_API_KEY:
            self.skipTest("GEMINI_API_KEY não configurada em settings")

        try:
            chat = GeminiChat(model=GeminiModels.FLASH)
            response = chat.send_message("Responda em uma palavra: OK")

            self.assertIsInstance(response, LLMResponse)
            self.assertIsNotNone(response.text)
            self.assertTrue(len(response.text) > 0)
        except GeminiRateLimitError:
            self.skipTest(
                "Cota excedida na API do Gemini (Rate Limit). Teste de integração ignorado."
            )


if __name__ == "__main__":
    unittest.main()
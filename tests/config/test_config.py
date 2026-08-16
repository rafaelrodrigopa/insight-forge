import unittest
from pathlib import Path

from app.config import (
    ProvidersConfig,
    Settings,
    TopicsConfig,
    providers_config,
    settings,
    topics_config,
)


class TestConfigModule(unittest.TestCase):

    def test_settings_properties(self):
        """Testa se as propriedades do Settings estão definidas corretamente."""
        self.assertIsInstance(settings, Settings)
        self.assertIsInstance(settings.BASE_DIR, Path)
        self.assertIsInstance(settings.POSTS_DIR, Path)
        self.assertIsInstance(settings.SPECS_DIR, Path)
        self.assertIsInstance(settings.DEBUG, bool)
        self.assertIsInstance(settings.ENV, str)

    def test_topics_config_default_weights(self):
        """Testa se os pesos padrões dos tópicos estão corretos."""
        self.assertEqual(topics_config.get_weight("power_bi"), 10)
        self.assertEqual(topics_config.get_weight("python"), 9)
        self.assertEqual(topics_config.get_weight("bigquery"), 10)
        self.assertEqual(topics_config.get_weight("sql"), 9)
        self.assertEqual(topics_config.get_weight("ia"), 8)
        self.assertEqual(topics_config.get_weight("desconhecido"), 0)

    def test_topics_config_methods(self):
        """Testa os métodos auxiliares do TopicsConfig."""
        cfg = TopicsConfig()

        # Insensibilidade a maiúsculas/minúsculas e espaços
        self.assertEqual(cfg.get_weight("  POWER_BI  "), 10)

        # Relevância
        self.assertTrue(cfg.is_relevant("power_bi", min_weight=5))
        self.assertFalse(cfg.is_relevant("tecnologia", min_weight=8))

        # Alteração de peso
        cfg.set_weight("novo_topico", 7)
        self.assertEqual(cfg.get_weight("novo_topico"), 7)

        # Clamping de limites (0-10)
        cfg.set_weight("topico_limite", 15)
        self.assertEqual(cfg.get_weight("topico_limite"), 10)

    def test_providers_config_defaults(self):
        """Testa as configurações de provedores de IA."""
        self.assertEqual(providers_config.DEFAULT_LLM_PROVIDER, "gemini")
        self.assertEqual(providers_config.DEFAULT_LLM_MODEL, "gemini-2.0-flash")

        # Teste do resolvedor de modelos
        self.assertEqual(
            providers_config.get_model("gemini", "flash"), "gemini-2.0-flash"
        )
        self.assertEqual(
            providers_config.get_model("openai", "flash"), "gpt-4o-mini"
        )
        self.assertEqual(
            providers_config.get_model("ollama", "pro"), "llama3:70b"
        )
        self.assertEqual(
            providers_config.get_model("desconhecido", "flash"),
            providers_config.DEFAULT_LLM_MODEL,
        )


if __name__ == "__main__":
    unittest.main()

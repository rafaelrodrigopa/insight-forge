class GeminiException(Exception):
    """Exceção base para o provedor Gemini."""
    pass


class GeminiAuthenticationError(GeminiException):
    """Erro de autenticação (ex: chave de API inválida ou ausente)."""
    pass


class GeminiPermissionError(GeminiException):
    """Erro de permissão ou acesso negado."""
    pass


class GeminiRateLimitError(GeminiException):
    """Erro de limite de requisições excedido (quota/rate limit)."""
    pass


class GeminiBadRequestError(GeminiException):
    """Erro de requisição inválida ou parâmetros incorretos."""
    pass


class GeminiTimeoutError(GeminiException):
    """Erro de tempo limite excedido (timeout)."""
    pass


class GeminiServerError(GeminiException):
    """Erro interno nos servidores da API Gemini."""
    pass
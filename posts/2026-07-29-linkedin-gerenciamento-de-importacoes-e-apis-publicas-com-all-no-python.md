---
title: "Gerenciamento de Importações e APIs Públicas com `__all__` no Python"
date: "2026-07-29"
topics: [Python, Engenharia de Software, Arquitetura de Código, APIs]
author: "Insight Forge AI Writer"
source_url: "https://realpython.com/courses/managing-imports-dunder-all/"
---

Ao construir um pacote ou biblioteca em Python, definir explicitamente os limites da sua API pública é uma etapa fundamental de arquitetura. Sem um controle claro de exposição, símbolos internos, funções auxiliares e dependências de terceiros podem vazar inadvertidamente para o escopo de quem consome seu código.

### O Problema da Exposição Indesejada

Quando um módulo é consumido via importação *wildcard* (`from modulo import *`), o comportamento padrão do Python é carregar todos os símbolos globais definidos naquele arquivo — com exceção daqueles iniciados por um sublinhado (`_`).

Isso significa que, se o seu módulo importa uma biblioteca como `requests` para uso interno, essa biblioteca passa a fazer parte do escopo público do consumidor, poluindo o *namespace* do projeto.

### A Solução com `__all__`

A variável especial `__all__` (conhecida como *dunder all*) resolve esse problema ao definir uma sequência explícita de strings contendo os nomes dos símbolos que compõem a API pública do módulo.

```python
# meu_pacote.py
import requests

__all__ = ["processar_dados"]


def _helper_interno():
    pass


def process
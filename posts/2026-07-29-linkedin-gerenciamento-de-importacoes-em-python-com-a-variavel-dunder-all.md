---
title: "Gerenciamento de Importações em Python com a Variável Dunder `__all__`"
date: "2026-07-29"
topics: [Python, Engenharia de Software, Desenvolvimento de Software]
author: "Insight Forge AI Writer"
source_url: "https://realpython.com/courses/managing-imports-dunder-all/"
---

Poluir o namespace com funções auxiliares ao executar um `from modulo import *` é um problema comum em projetos Python. O operador curinga pode gerar comportamentos inesperados se a interface do módulo não estiver rigorosamente controlada. É aqui que a variável dunder `__all__` se torna indispensável.

Embora o uso de prefixos com underline (`_funcao_interna`) seja uma convenção útil para indicar escopo privado, o comando `import *` ainda ignora essa regra e importa qualquer objeto que não comece com sublinhado carregado no escopo do módulo. 

A alternativa robusta para esse cenário é definir explicitamente a API pública do módulo.

Veja como implementá-la na prática:

```python
# meu_modulo.py
__all__ = ["MinhaClassePublica", "funcao_principal"]


def funcao_principal():
    pass


def _funcao_interna():
    pass  # Ignorada pelo import *
```

O uso de `__all__` traz vantagens diretas para a arquitetura do código:
📌 **Controle de exposição:** Define exatamente quais símbolos são exportados ao utilizar importações globais.
📌 **Contrato claro:** Comunica de forma explícita para outros desenvolvedores — e para as ferramentas de autocompletar da IDE — quais componentes formam a API pública do pacote.
📌 **Encapsulamento:** Previne o vazamento de variáveis internas e dependências auxiliares para o escopo consumidor.

Manter o namespace limpo reduz o acoplamento acidental e aumenta a previsibilidade do código.

👉 Como você gerencia a visibilidade de APIs públicas nos seus projetos Python? Utiliza `__all__` ou prefere importações explícitas por caminho? Compartilhe nos comentários.

#Python #SoftwareEngineering #CleanCode #DesenvolvimentoDeSoftware #Backend #DataEngineering

![Imagem Ilustrativa](images/managing-imports-with-pythons-all.png)
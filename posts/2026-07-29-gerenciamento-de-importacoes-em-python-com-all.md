```markdown
---
title: "Gerenciamento de Importações em Python com `__all__`"
date: "2026-07-29"
topics: [Python, API Design, Engenharia de Software, Boas Práticas de Programação, Módulos e Pacotes]
author: "Insight Forge AI Writer"
source_url: "https://realpython.com/courses/managing-imports-dunder-all/"
---

# Python Clean Code: Como a Variável `__all__` Define a API Pública dos Seus Módulos

Ao desenvolver bibliotecas ou grandes sistemas em Python, a organização do código é um dos pilares para a manutenibilidade. No entanto, um problema comum costuma passar despercebido: a poluição do namespace. Quando outro desenvolvedor importa o seu módulo, ele tem acesso apenas ao que realmente importa ou acaba visualizando uma lista caótica de funções auxiliares, variáveis internas e dependências de terceiros no autocompletar da IDE?

Se você já utilizou a polêmica instrução `from modulo import *` (wildcard import), sabe que ela pode trazer efeitos colaterais indesejados. É exatamente aqui que entra a variável especial `__all__` (conhecida como *dunder all*), uma ferramenta essencial para o design de APIs robustas e limpas em Python.

---

## O que é e como funciona o `__all__`?

No Python, a variável `__all__` é uma sequência de strings (geralmente uma lista) definida no nível do módulo (escopo global do arquivo) ou no `__init__.py` de um pacote. Ela serve para declarar explicitamente quais atributos, funções ou classes devem ser exportados quando o módulo for importado usando o caractere curinga (`*`).

### O comportamento padrão (Sem `__all__`)

Por padrão, quando você executa `from modulo import *`, o Python importa todos os nomes que não começam com um sublinhado (`_`). Isso inclui não apenas as funções criadas para o usuário final, mas também as bibliotecas que você importou internamente para fazer o módulo funcionar.

Consulte o exemplo abaixo:

```python
# processador.py
import math  # Dependência interna

def calcular_area(raio):
    return math.pi * (raio ** 2)

def _auxiliar_interno():
    return "Processando..."
```

Se alguém executar `from processador import *`, terá acesso a `calcular_area`, mas também herdará o módulo
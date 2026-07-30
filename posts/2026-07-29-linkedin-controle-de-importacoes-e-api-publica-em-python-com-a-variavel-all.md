---
title: "Controle de Importações e API Pública em Python com a Variável `__all__`"
date: "2026-07-29"
topics: [Python, Engenharia de Software, Desenvolvimento de Software, Boas Práticas]
author: "Insight Forge AI Writer"
source_url: "https://realpython.com/courses/managing-imports-dunder-all/"
---

Ao desenvolver bibliotecas ou pacotes em Python, definir claramente quais elementos pertencem à interface pública é fundamental para garantir a manutenibilidade e prevenir o acoplamento indevido. Uma das formas mais diretas de gerenciar essa visibilidade e evitar a poluição do *namespace* é o uso da variável especial `__all__`.

![Controle de Importações em Python](images/managing-imports-with-pythons-all.png)

## O que é e como funciona a variável `__all__`

A `__all__` é uma sequência de strings (geralmente uma lista ou tupla) definida no nível de módulo ou pacote (`__init__.py`). Ela especifica explicitamente quais nomes devem ser exportados quando é realizada uma importação do tipo *wildcard* (`from modulo import *`).

Por
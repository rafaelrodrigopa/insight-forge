# Roadmap de Desenvolvimento

> Este roadmap define a evolução incremental do projeto **Insight Forge**, priorizando a validação da arquitetura antes da implementação de funcionalidades mais complexas.

---

# Sprint 1 — Estrutura do Projeto

## Objetivo

Criar a base estrutural do projeto.

## Entregas

- Estrutura inicial de diretórios.
- Configuração do repositório Git.
- Documentação inicial (`README.md`).
- Licença MIT.
- Especificação técnica (`specs/`).
- Configuração do ambiente Python.
- Arquivo `.gitignore`.
- Arquivo `.env.example`.

**Status:** ✅ Concluído

---

# Sprint 2 — Arquitetura de Providers

## Objetivo

Criar uma camada de abstração para todos os provedores externos, garantindo baixo acoplamento e facilidade para adicionar novas integrações.

## Estrutura

```text
providers/

├── base.py
├── openai.py
├── gemini.py
├── ollama.py
├── linkedin.py
└── ...
```

## Objetivos

- Definir interfaces comuns para provedores.
- Facilitar troca entre modelos de IA.
- Facilitar testes (Mock Providers).
- Evitar dependência direta de APIs específicas.

---

# Sprint 3 — Configuração Centralizada

## Objetivo

Centralizar todas as configurações do sistema.

## Estrutura

```text
config/

├── settings.py
├── providers.py
└── topics.py
```

## Objetivos

- Configurações gerais.
- Configuração dos provedores.
- Configuração dos modelos de IA.
- Definição dos tópicos monitorados.
- Pesos utilizados pelo Ranking Engine.

---

# Sprint 4 — Primeiro Collector

## Objetivo

Implementar o primeiro coletor de dados utilizando RSS.

### Justificativa

O RSS permite validar toda a arquitetura sem necessidade de:

- autenticação;
- APIs pagas;
- tokens;
- OAuth;
- limites de uso.

## Fluxo esperado

```text
RSS Feed
      │
      ▼
Collector
      │
      ▼
Document
```

## Entregas

- RSS Collector.
- Parser RSS.
- Conversão para objeto `Document`.
- Testes unitários.

**Status:** ✅ Concluído

---

# Sprint 5 — Integração com LLM

## Objetivo

Validar a comunicação com um modelo de linguagem.

## Fluxo

```text
Document
      │
      ▼
LLM
      │
      ▼
Resumo
```

## Objetivos

- Consumir um documento coletado.
- Enviar para um provedor de IA.
- Receber um resumo estruturado.
- Validar arquitetura dos Providers.

**Status:** ✅ Concluído

---

# Sprint 6 — Writer Agent

## Objetivo

Gerar o primeiro conteúdo automaticamente.

## Fluxo

```text
Document
      │
      ▼
Writer Agent
      │
      ▼
Markdown
```

## Entregas

- Writer Agent.
- Prompt inicial.
- Geração de arquivo Markdown.

Exemplo:

```text
posts/

2026-07-27-python-3-15.md
```

**Status:** ✅ Concluído

Ao final desta sprint, o projeto possuirá um **MVP funcional**, capaz de coletar uma notícia, processá-la com IA e gerar um rascunho de conteúdo.

---

# Sprint 7 — Ranking e Deduplicação

## Objetivo

Implementar inteligência na seleção dos conteúdos.

## Funcionalidades

- Ranking por relevância.
- Similaridade semântica.
- Deduplicação.
- Classificação por tópicos.

## Tecnologias previstas

- Sentence Transformers
- Cosine Similarity

**Status:** ✅ Concluído

---

# Sprint 8 — Agentes de IA

## Objetivo

Substituir prompts únicos por agentes especializados.

## Agentes

- Collector Agent
- Classifier Agent
- Prioritizer Agent
- Writer Agent
- Critic Agent

## Benefícios

- Baixo acoplamento.
- Melhor qualidade do conteúdo.
- Facilidade de evolução.
- Reutilização dos agentes.

---

# Sprint 9 — Automação

## Objetivo

Automatizar toda a execução do pipeline.

## Fluxo

```text
GitHub Actions

↓

Coleta

↓

Processamento

↓

Ranking

↓

Writer

↓

Critic

↓

Markdown

↓

Pull Request
```

## Objetivos

- Execução diária.
- Pipeline automatizado.
- Geração automática de Pull Requests.
- Revisão humana antes da publicação.

---

# Sprint 10 — Publicadores

## Objetivo

Adicionar múltiplos destinos para publicação.

## Publicadores previstos

- Markdown
- LinkedIn
- WordPress
- GitHub Pages
- Newsletter
- Medium
- Dev.to
- Threads
- X (Twitter)

---

# MVP

Ao término da Sprint 6, o sistema deverá ser capaz de executar o seguinte fluxo:

```text
RSS Feed

↓

Collector

↓

Document

↓

LLM

↓

Writer Agent

↓

Markdown

↓

posts/

2026-07-27-python-3-15.md
```

Este será o primeiro MVP funcional do projeto, validando a arquitetura principal antes da implementação das funcionalidades mais avançadas.

---

# Evolução Esperada

Após o MVP, novos coletores poderão ser adicionados sem alterar o restante da arquitetura.

Exemplo:

```text
RSS
      │
      ▼
Collector
```

poderá ser substituído por:

```text
GitHub Trending

↓

Collector
```

ou

```text
Reddit

↓

Collector
```

mantendo exatamente o mesmo fluxo interno do sistema.

Essa abordagem garante uma arquitetura modular, extensível e desacoplada, permitindo que novas fontes de dados e novos destinos de publicação sejam adicionados com o mínimo de impacto no restante do projeto.
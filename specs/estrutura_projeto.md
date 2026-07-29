# Insight Forge

> **Especificação Técnica Inicial (Technical Specification v0.1)**

## Visão Geral

O **Insight Forge** é um projeto open source desenvolvido em Python que automatiza o processo de descoberta, curadoria e geração de conteúdo utilizando Inteligência Artificial.

O objetivo do projeto é construir uma arquitetura modular capaz de coletar informações de diversas fontes, analisar sua relevância, classificá-las, eliminar duplicidades e transformá-las em conteúdos de alta qualidade para redes sociais, blogs e newsletters.

Ao contrário de soluções que apenas resumem notícias e publicam automaticamente, o Insight Forge adota uma abordagem baseada em **pipeline de dados + agentes especializados de IA**, priorizando qualidade editorial, relevância e alinhamento estratégico.

---

# Problema

Grande parte dos bots de geração de conteúdo seguem um fluxo extremamente simples:

```text
Google News
      │
      ▼
IA resume
      │
      ▼
Publica
```

Embora simples, essa abordagem gera diversos problemas:

- Conteúdo extremamente genérico.
- Baixo valor agregado.
- Pouca autoridade.
- Falta de contexto.
- Publicações repetitivas.
- Nenhum alinhamento com a identidade do autor.

O Insight Forge propõe substituir esse fluxo por uma arquitetura inteligente baseada em múltiplos estágios de processamento.

---

# Objetivos

O projeto possui os seguintes objetivos:

- Automatizar a descoberta de conteúdo relevante.
- Priorizar informações de maior impacto.
- Eliminar notícias duplicadas.
- Produzir conteúdo com linguagem natural.
- Manter consistência com os temas definidos pelo usuário.
- Permitir publicação em múltiplos canais.
- Servir como projeto de referência em arquitetura de IA aplicada à automação de conteúdo.

---

# Arquitetura Geral

```text
                GitHub Actions
                 (Scheduler)

                      │
                      ▼

                Data Collection

          RSS
          APIs
          Blogs
          GitHub Trending
          Hacker News
          Reddit
          Scientific Papers
          LinkedIn Trends*

                      │
                      ▼

              Data Normalization

        Remove HTML
        Language Detection
        Categories
        Publication Date
        Author
        Metadata
        Embeddings

                      │
                      ▼

                  Storage

          SQLite
          Supabase

                      │
                      ▼

              Ranking Engine

        Novelty
        Relevance
        Topic Match
        Source Reliability
        Popularity
        Similarity

                      │
                      ▼

              Deduplication

        Sentence Transformers
        Cosine Similarity

                      │
                      ▼

             Editorial AI Agent

        OpenAI
        Gemini
        Claude
        Ollama
        Outros

                      │
                      ▼

            Content Generation

        LinkedIn
        Blog
        Newsletter
        Threads
        X (Twitter)
        Markdown

                      │
                      ▼

             Validation Layer

        Fact Check
        Grammar
        Tone
        Technical Accuracy

                      │
                      ▼

                 Publication

        GitHub Pages
        WordPress
        LinkedIn API
```

---

# Arquitetura do Projeto

```text
insight-forge/

│
├── .github/
│   └── workflows/
│
├── config/
│   ├── settings.py
│   ├── providers.py
│   ├── topics.py
│   └── prompts.py
│
├── collectors/
│   ├── rss.py
│   ├── google_news.py
│   ├── github.py
│   ├── reddit.py
│   ├── hackernews.py
│   ├── arxiv.py
│   └── medium.py
│
├── preprocess/
│   ├── clean_text.py
│   ├── language.py
│   ├── embeddings.py
│   ├── duplicate.py
│   └── metadata.py
│
├── ranking/
│   ├── scorer.py
│   ├── priority.py
│   └── trends.py
│
├── agents/
│   ├── collector.py
│   ├── classifier.py
│   ├── prioritizer.py
│   ├── writer.py
│   └── critic.py
│
├── llm/
│   ├── openai.py
│   ├── gemini.py
│   ├── claude.py
│   └── ollama.py
│
├── publish/
│   ├── markdown.py
│   ├── linkedin.py
│   ├── wordpress.py
│   ├── github_pages.py
│   └── newsletter.py
│
├── storage/
│   ├── sqlite.py
│   └── supabase.py
│
├── prompts/
│   ├── linkedin.md
│   ├── article.md
│   ├── newsletter.md
│   └── critic.md
│
├── tests/
│
├── main.py
│
├── requirements.txt
│
└── README.md
```

---

# Fontes de Dados

## Inteligência Artificial

- OpenAI
- Anthropic
- Google DeepMind
- Mistral
- Meta AI
- Microsoft AI

---

## Engenharia de Dados

- Databricks
- Snowflake
- dbt
- Apache Foundation
- Confluent

---

## Cloud Computing

- Google Cloud
- AWS
- Azure
- Cloudflare

---

## Business Intelligence

- Power BI
- Tableau
- Looker

---

## Python

- Python.org
- PyPI
- GitHub Trending

---

## Comunidades

- Hacker News
- Reddit
- Medium
- Dev.to

---

# Pipeline de Processamento

## 1. Coleta

Responsável por consumir informações de múltiplas fontes.

Saída:

```text
Raw Documents
```

---

## 2. Normalização

Responsável por transformar documentos em um formato comum.

Processos:

- limpeza HTML
- remoção de caracteres
- idioma
- autor
- data
- categorias
- metadados

Saída:

```text
Normalized Documents
```

---

## 3. Embeddings

Cada documento recebe um embedding vetorial.

Objetivos:

- similaridade
- busca semântica
- deduplicação
- clustering

---

## 4. Ranking

Cada documento recebe uma pontuação.

Critérios:

- relevância
- novidade
- popularidade
- alinhamento com tópicos
- confiabilidade da fonte
- quantidade de fontes

Resultado:

```text
Score (0-100)
```

---

## 5. Deduplicação

Utiliza:

- Sentence Transformers
- Cosine Similarity

Objetivo:

Remover conteúdos praticamente iguais provenientes de fontes diferentes.

---

# Agentes Especializados

Ao invés de um único prompt extremamente complexo, o sistema utilizará múltiplos agentes especializados.

---

## Agente 1 — Collector

Responsabilidade:

Encontrar conteúdos relevantes.

Entrada:

```
Lista de fontes
```

Saída:

```
Documentos
```

---

## Agente 2 — Classifier

Responsabilidade:

Classificar cada documento.

Categorias iniciais:

- IA
- Python
- BigQuery
- SQL
- Analytics
- Engenharia de Dados
- Cloud
- Power BI
- Carreira

---

## Agente 3 — Prioritizer

Responsabilidade:

Responder:

> Essa notícia merece virar conteúdo?

Resultado:

```
Score
0 - 100
```

---

## Agente 4 — Writer

Responsabilidade:

Transformar a informação em conteúdo.

Diretrizes:

- linguagem natural
- storytelling
- início com gancho
- evitar aparência de texto gerado por IA
- CTA no final

---

## Agente 5 — Critic

Responsabilidade:

Revisar o conteúdo.

Critérios:

- parece IA?
- possui clichês?
- possui erros técnicos?
- está repetitivo?
- possui boa fluidez?

Resultado:

```
Nota
Sugestões
```

---

# Estratégia Editorial

O sistema não deverá seguir apenas tendências.

Ele deverá priorizar temas alinhados ao posicionamento do autor.

Exemplo:

```yaml
topics:

  analytics: 10

  ia: 10

  python: 10

  bigquery: 9

  power_bi: 9

  sql: 8

  cloud: 8

  engenharia_de_dados: 10

  carreira: 5

  linkedin: 7

  automacao: 8
```

Esses pesos influenciarão diretamente o algoritmo de ranking.

---

# Fluxo de Automação

Execução diária via GitHub Actions.

```text
08:00

↓

Coleta

↓

Normalização

↓

Ranking

↓

Deduplicação

↓

Seleciona Top 10

↓

Writer Agent

↓

Critic Agent

↓

Geração de Markdown

↓

Criação automática de Pull Request
```

O conteúdo **não será publicado automaticamente**.

O objetivo é gerar um Pull Request contendo os rascunhos para revisão humana.

Somente após aprovação o conteúdo poderá ser publicado.

---

# Publicação

O sistema deverá suportar múltiplos destinos.

Inicialmente:

- Markdown
- LinkedIn
- WordPress

Futuramente:

- GitHub Pages
- Newsletter
- Medium
- Dev.to
- Threads
- X

---

# Requisitos Não Funcionais

- Arquitetura modular.
- Fácil extensão.
- Código desacoplado.
- Suporte a múltiplos provedores de IA.
- Configuração por arquivos.
- Execução local ou GitHub Actions.
- Testável.
- Open Source.
- Documentado.

---

# Roadmap Inicial

## Fase 1

- Estrutura do projeto
- Sistema de configuração
- RSS Collector
- SQLite
- Markdown Export

---

## Fase 2

- Ranking
- Embeddings
- Deduplicação

---

## Fase 3

- Agentes de IA
- Writer
- Critic
- Pull Requests automáticos

---

## Fase 4

- Publicação
- LinkedIn
- WordPress
- Newsletter

---

# Visão de Longo Prazo

O Insight Forge deverá servir como uma referência de arquitetura para automação inteligente de conteúdo, demonstrando boas práticas de engenharia de software, engenharia de dados, processamento de linguagem natural e integração com modelos de linguagem (LLMs).

O projeto foi concebido para ser modular, extensível e independente de provedores específicos, permitindo a evolução contínua da arquitetura sem acoplamento a tecnologias ou APIs proprietárias.
# Ideia: Extração e Reuso de Agentes em Projetos Externos

**Data de Registro:** 16/08/2026  
**Status:** Arquivado para Referência Futura / Estratégia de Arquitetura  

---

## 1. Sugestão Original

> *"Dentro do insight-forge tem agentes que poderiam ser reutilizados, o que acha de extrairmos esses agentes de lá e deixar na pasta agentes para ser utilizado por qualquer projeto? Deixar esses agentes atuando fora do projeto independentemente precisaria deixá-los rodando e servindo aos outros projetos via API ou o projeto buscaria cada agente diretamente?"*

---

## 2. Análise Técnica & Viabilidade

### A. Agentes Reutilizáveis Identificados
O *Insight Forge* possui 6 agentes de inteligência altamente modulares e independentes da plataforma final:
- `CollectorAgent`: Coleta e extração de texto limpo a partir de feeds RSS / URLs.
- `ClassifierAgent`: Classificação de nichos técnicos (Cloud, SQL, IA) e tags via LLM.
- `PrioritizerAgent`: Avaliação editorial e atribuição de score de relevância (0-100).
- `SummarizerAgent`: Síntese de artigos extensos em tópicos e lições de arquitetura.
- `WriterAgent`: Redação de cópias especialistas em formato Markdown.
- `CriticAgent`: Revisão técnica de código, tom de voz e clareza.

### B. Abordagens de Integração Comparadas

1. **Abordagem 1: Import Direto via Path / Pacote Compartilhado (Adotada)**
   - **Funcionamento:** Os novos projetos (como `auto-gerac`) adicionam a pasta do *Insight Forge* ao `sys.path` ou importam a biblioteca diretamente (`from app.agents.writer.agent import WriterAgent`).
   - **Vantagens:** Zero refatoração no *Insight Forge*, zero consumo de memória RAM em background e latência zero (sem chamadas de rede locais).

2. **Abordagem 2: Serviço de Microserviço via API REST (Futuro)**
   - **Funcionamento:** Exposição dos agentes em um servidor FastAPI (`POST /api/v1/agents/...`).
   - **Vantagens:** Permite consumo por aplicações em outras linguagens (Node.js, Go) e painéis web no navegador.
   - **Desvantagem Atual:** Necessidade de manter um servidor em segundo plano consumindo memória RAM 24/7 para execuções que ocorrem em ciclos periódicos.

---

## 3. Decisão & Próximos Passos

- **Estratégia Atual:** Manter os agentes dentro do `insight-forge` e consumi-los diretamente via import no projeto `auto-gerac` e outros scripts de automação.
- **Evolução Futura:** Caso a biblioteca de agentes se expanda significativamente ou surja a necessidade de uma interface web desacoplada, os agentes serão migrados para um pacote próprio (`shared_agents`) ou expostos via API REST com FastAPI.

# Estimativa de Esforço — Agentes RAG Locais

## Premissas

- Hardware já disponível (GPU ≥ 16 GB VRAM, 32 GB RAM)
- SO instalado (Windows ou Linux)
- Stack base: Python + Ollama (`gemma4:12b` + `nomic-embed-text`) + ChromaDB
- "Triagem" = camada que classifica o pedido antes do RAG (tipo/urgência/routing para subcoleções)

---

## Arquitectura Multi-Agente

O Agente Líder e os Agentes Locais comunicam via **A2A (Agent-to-Agent)** com **JSON** como formato de mensagens.

**Fluxo:**
1. O Agente Líder recebe um pedido, prepara os documentos relevantes e metadados associados
2. Envia um pedido estruturado em JSON a um ou mais Agentes Locais
3. Cada Agente Local consulta o seu corpus próprio e devolve um parecer em JSON
4. O Agente Líder agrega os pareceres e produz a resposta final

```
Utilizador
    │
    ▼
┌─────────────────┐
│  Agente Líder   │  ← docs SIR + metadados + triagem
└────────┬────────┘
         │ A2A (JSON)
    ┌────┴────┐
    ▼         ▼
┌───────┐ ┌───────┐
│ Local │ │ Local │  ← cada um com o seu corpus/regras
└───────┘ └───────┘
```

---

## Agente Líder — Ambiente SIR do zero (com triagem + mais documentos)

| Tarefa | Esforço |
|---|---|
| Instalar Python, Ollama, pip packages | 0.25 d |
| Download modelos (`gemma4:12b` + `nomic-embed-text`) | 0.25 d |
| Setup da estrutura de pastas + config inicial | 0.25 d |
| Recolha e preparação de documentos SIR adicionais | 1–2 d |
| Indexação + validação do RAG base | 0.5 d |
| Desenvolvimento da camada de triagem | 2–3 d |
| Testes end-to-end + afinação do prompt | 1 d |
| **Total** | **5–7 man-days** |

> A triagem é o item mais pesado — implica definir categorias/regras, implementar um classificador (segundo prompt ao LLM ou keyword routing) e testar cobertura de casos. PDFs mal formatados ou scans são o maior risco de derrapagem na preparação de documentos.

---

## Agentes Locais — Agente adicional com outro conjunto de documentos/regras

Uma vez que o template existe, o custo marginal cai significativamente.

| Tarefa | Esforço |
|---|---|
| Clonar projeto, renomear coleção ChromaDB, ajustar configs | 0.25 d |
| Preparar e indexar novo conjunto de documentos | 0.5–1 d |
| Ajustar prompt e regras de domínio | 0.5 d |
| Testes e validação | 0.5 d |
| **Total por agente** | **1.5–2.5 man-days** |

> A reutilização do código é quase total a partir do segundo agente.

---

## Agente Expert Codigo — Análise eforms/Legacy SIR

Agente especializado em analisar como implementar em eforms os formulários SIR de uma aplicação legacy, com corpus misto: legislação SIR + leis adicionais + código fonte legacy (MD) + reverse engineering + código fonte eforms (MD). Sem triagem.

### Fase 1 — Preparação de documentos

| Tarefa | Esforço |
|---|---|
| Reverse engineering da app legacy — mapeamento de formulários, campos, validações e regras de negócio | 8–20 d |
| Produção do MD estruturado do RE (por formulário/módulo) | 3–6 d |
| Extração do código fonte legacy → MD | 1–2 d |
| Extração do código fonte eforms → MD | 1–2 d |
| Recolha e prep das leis adicionais | 1–2 d |
| **Subtotal** | **14–32 d** |

### Fase 2 — Construção do agente

| Tarefa | Esforço |
|---|---|
| Setup ambiente + indexação | 0.5 d |
| Estratégia de chunking para código (diferente de texto legal) | 1 d |
| Prompt engineering para raciocínio cruzado legacy→eforms | 2–3 d |
| Testes e validação com queries reais | 1–2 d |
| **Subtotal** | **4.5–6.5 d** |

| | Esforço estimado |
|---|---|
| Preparação de documentos (RE + MDs) | 14–32 man-days |
| Construção do agente | 4.5–6.5 man-days |
| **Total** | **18–38 man-days** |

> **Principais riscos de derrapagem:** qualidade do código legacy (spaghetti code, lógica em stored procedures), dimensão das bases de código, e necessidade de revisão humana para garantir paridade com a legislação atual. O investimento real está no RE — o agente em si é uma fração do esforço total.

---

## Resumo

| Agente | Esforço estimado |
|---|---|
| Agente Líder (com triagem) | 5–7 man-days |
| Cada Agente Local (outro domínio) | 1.5–2.5 man-days |
| Agente Expert Codigo (RE + construção) | 18–38 man-days |

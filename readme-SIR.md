# EspecialistaSIR

Bot de perguntas e respostas (RAG) sobre documentação SIR portuguesa. Corre inteiramente local — sem APIs cloud, sem telemetria.

## Requisitos

| Componente | Versão |
|---|---|
| Python | 3.10+ |
| Ollama | qualquer recente |
| Modelo LLM | `gemma4:12b` |
| Modelo de embedding | `nomic-embed-text` |

## Hardware recomendado

| | Mínimo | Recomendado |
|---|---|---|
| **RAM** | 16 GB | 32 GB |
| **VRAM (GPU)** | 16 GB | 16 GB+ |
| **Armazenamento** | 15 GB livres | — |

> `gemma4:12b` usa ~14 GB de VRAM em utilização real. É necessária uma GPU com pelo menos 16 GB de VRAM (ex: RTX 3080 Ti, RTX 4080, RTX 4090). Sem GPU compatível, o Ollama corre em CPU com impacto severo na velocidade.

---

### Dependências Python

```
pip install chromadb pypdf python-docx requests pymupdf
```

> Para ficheiros `.doc` (Word antigo) é necessário Microsoft Word instalado e o pacote `pywin32`.

### Modelos Ollama necessários

```
ollama pull gemma4:12b
ollama pull nomic-embed-text
```

---

## Estrutura do projecto

```
EspecialistaSIR/
├── especialista.py          # bot principal (RAG + interface CLI)
├── especialistaSIR.py       # versão anterior (referência)
├── conversor.py             # converte PDFs para Markdown via PyMuPDF
├── test_especialista.py     # testes de integração (pytest)
│
├── docs/                    # documentos indexados (PDF, MD, DOCX, DOC)
├── pdfs/                    # PDFs originais antes de conversão
├── conhecimentoSIR/         # base ChromaDB persistente (gerada automaticamente)
│
├── start_especialista.bat      # arranque completo (limpa GPU + BD + inicia bot)
├── start_especialistaSIR.bat   # arranque da versão anterior
├── limpar_gpu.bat              # descarrega todos os modelos Ollama da GPU
├── limpar_bd.bat               # apaga a base ChromaDB (força re-indexação)
└── correr_testes.bat           # corre pytest em modo verbose
```

---

## Como usar

### 1. Preparar os documentos

Coloque os ficheiros de legislação em `docs/`. Formatos suportados: `.pdf`, `.md`, `.docx`, `.doc`.

Se tiver PDFs que precisem de melhor extracção de texto, converta-os primeiro:

```
python conversor.py
```

O script converte o PDF de `pdfs/` para Markdown e guarda o resultado em `docs/`.

### 2. Iniciar o bot

```
start_especialista.bat
```

O script executa três passos automaticamente:
1. Descarrega da GPU quaisquer modelos Ollama que não sejam `gemma4:12b`
2. Apaga a base ChromaDB (re-indexação limpa)
3. Arranca `especialista.py`

Ou diretamente:

```
python especialista.py
```

### 3. Interagir

```
Pronto! Faça perguntas sobre os documentos (escreva 'sair' para terminar).

Você: qual o âmbito de aplicação do DL 169/2012?
A consultar...

IA: O Decreto-Lei n.º 169/2012 ...
```

Escreva `sair` ou pressione `Ctrl+C` para terminar. O modelo é descarregado da GPU automaticamente ao sair.

---

## Funcionamento interno

```
docs/ → extracção de texto → chunks (300 palavras, overlap 50)
                                  ↓
                        embeddings: nomic-embed-text (Ollama)
                                  ↓
                           ChromaDB (conhecimentoSIR/)
                                  ↓
pergunta → top-5 chunks relevantes → prompt → Ollama (gemma4:12b) → resposta
```

- **Indexação incremental** — apenas ficheiros novos em `docs/` são indexados; os já existentes são ignorados.
- **Gestão de GPU** — ao arrancar, o bot liberta outros modelos Ollama e mantém `gemma4:12b` em VRAM com `keep_alive: -1`. Ao sair, liberta-o.
- **Resposta limitada ao contexto** — o modelo responde apenas com base nos documentos indexados. Se a informação não estiver nos documentos, informa-o.

---

## Re-indexar documentos

Se adicionar ou remover documentos e quiser forçar uma re-indexação completa:

```
limpar_bd.bat
python especialista.py
```

> Não apague `docs/` — apenas `conhecimentoSIR/`.

---

## Configuração

As constantes no topo de `especialista.py`:

| Constante | Valor por omissão | Descrição |
|---|---|---|
| `PASTA_DOCS` | `./docs` | Pasta com os documentos a indexar |
| `PASTA_BD` | `./conhecimentoSIR` | Localização da base ChromaDB |
| `NOME_COLECAO` | `base_conhecimento_SIR` | Nome da colecção ChromaDB |
| `OLLAMA_URL` | `http://localhost:11434/api/generate` | Endpoint de geração do Ollama |
| `OLLAMA_EMBED_URL` | `http://localhost:11434/api/embed` | Endpoint de embeddings do Ollama |
| `OLLAMA_PS_URL` | `http://localhost:11434/api/ps` | Endpoint de estado de modelos do Ollama |
| `MODELO_LLM` | `gemma4:12b` | Modelo LLM a usar |
| `MODELO_EMBED` | `nomic-embed-text` | Modelo de embedding a usar |
| `OLLAMA_OPTIONS` | `{"num_ctx": 8192}` | Opções do Ollama (tamanho de contexto) |
| `DEBUG` | `True` | Activa logs de tokens, chunks e tamanho de prompt |

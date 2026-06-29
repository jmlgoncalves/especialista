# Especialista SIR — Requisitos e Instalação

Bot de perguntas e respostas sobre documentos usando RAG (ChromaDB + Ollama). Suporta PDF, MD, DOCX e DOC.

---

## Requisitos

| Componente | Versão mínima |
|---|---|
| Python | 3.9+ |
| Ollama | última estável |
| Modelo LLM | gemma4:12b |
| Modelo Embeddings | nomic-embed-text |

---

## Hardware recomendado

| | Mínimo | Recomendado |
|---|---|---|
| **RAM** | 16 GB | 32 GB |
| **VRAM (GPU)** | 16 GB | 16 GB+ |
| **Armazenamento** | 15 GB livres | — |

> `gemma4:12b` usa ~14 GB de VRAM em utilização real. É necessária uma GPU com pelo menos 16 GB de VRAM (ex: RTX 3080 Ti, RTX 4080, RTX 4090). Sem GPU compatível, o Ollama corre em CPU com impacto severo na velocidade.

---

## 1. Python

Descarregar e instalar em [python.org/downloads](https://www.python.org/downloads/)

Durante a instalação, ativar a opção **"Add Python to PATH"**.

Verificar instalação:
```bash
python --version
```

---

## 2. Bibliotecas Python

```bash
pip install chromadb pypdf requests python-docx
```

| Biblioteca | Função |
|---|---|
| `chromadb` | Base de dados vetorial para RAG |
| `pypdf` | Extração de texto de PDFs |
| `requests` | Chamadas HTTP ao Ollama |
| `python-docx` | Extração de texto de ficheiros DOCX |

> **Nota:** Ficheiros `.doc` (formato Word antigo) requerem Microsoft Word instalado (via `pywin32`).

---

## 3. Ollama

Descarregar e instalar em [ollama.com/download](https://ollama.com/download)

Verificar instalação:
```bash
ollama --version
```

Iniciar o serviço (necessário estar em execução antes de correr o bot):
```bash
ollama serve
```

---

## 4. Modelos Ollama

Descarregar o modelo LLM e o modelo de embeddings:
```bash
ollama pull gemma4:12b
ollama pull nomic-embed-text
```

Verificar se estão disponíveis:
```bash
ollama list
```

---

## 5. Estrutura de pastas

```
EspecialistaSIR/
├── docs/               ← colocar aqui os documentos a indexar
├── conhecimentoSIR/    ← criada automaticamente (base ChromaDB)
├── especialista.py
├── limpar_bd.bat       ← apaga a base de conhecimento
└── limpar_gpu.bat      ← descarrega modelos da GPU
```

Colocar os documentos (`.pdf`, `.md`, `.docx`, `.doc`) na pasta `docs/` antes de correr o bot.  
A pasta `conhecimentoSIR/` é criada automaticamente na primeira execução.

---

## 6. Executar

```bash
python especialista.py
```

Na primeira execução, o bot indexa todos os documentos da pasta `docs/`.  
Nas execuções seguintes, apenas indexa ficheiros novos que ainda não foram processados.

Para sair do chat, escrever `sair`.

---

## 7. Configuração

No topo de `especialista.py` estão as variáveis de configuração:

| Variável | Padrão | Descrição |
|---|---|---|
| `MODELO_LLM` | `gemma4:12b` | Modelo LLM usado para respostas |
| `MODELO_EMBED` | `nomic-embed-text` | Modelo de embeddings para indexação e retrieval |
| `DEBUG` | `False` | Mostra chunks devolvidos e métricas do Ollama |
| `MOSTRAR_FONTE` | `False` | Mostra citação do trecho do documento que suporta a resposta |

---

## Notas

- O Ollama tem de estar em execução (`ollama serve`) antes de iniciar o bot.
- Para adicionar novos documentos, basta colocar os ficheiros em `docs/` e reiniciar o bot.
- A base de conhecimento fica guardada em `conhecimentoSIR/` e persiste entre sessões.
- Ao mudar o `MODELO_EMBED`, é necessário apagar a base de conhecimento (`limpar_bd.bat`) e re-indexar.

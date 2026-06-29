# Especialista SIR — Requisitos e Instalação

Bot de perguntas e respostas sobre documentos usando RAG (ChromaDB + Ollama). Suporta PDF, MD, DOCX e DOC.

---

## Requisitos

| Componente | Versão mínima |
|---|---|
| Python | 3.9+ |
| Ollama | última estável |
| Modelo LLM | gemma4:12b |

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

## 4. Modelo gemma4:12b

Com o Ollama instalado, descarregar o modelo (requer ~8 GB de espaço):
```bash
ollama pull gemma4:12b
```

Verificar se o modelo está disponível:
```bash
ollama list
```

---

## 5. Estrutura de pastas

```
EspecialistaSIR/
├── docs/               ← colocar aqui os PDFs a indexar
├── conhecimentoSIR/    ← criada automaticamente (base ChromaDB)
└── especialista.py
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

## Notas

- O Ollama tem de estar em execução (`ollama serve`) antes de iniciar o bot.
- Para adicionar novos documentos, basta colocar os ficheiros em `docs/` e reiniciar o bot.
- A base de conhecimento fica guardada em `conhecimentoSIR/` e persiste entre sessões.

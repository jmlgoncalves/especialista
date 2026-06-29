import os
import glob
import signal
import sys
from pypdf import PdfReader
from docx import Document
import chromadb
from chromadb import EmbeddingFunction, Documents
import requests

PASTA_DOCS = "./docs"
PASTA_BD = "./conhecimentoSIR"
NOME_COLECAO = "base_conhecimento_SIR"
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_EMBED_URL = "http://localhost:11434/api/embed"
OLLAMA_PS_URL = "http://localhost:11434/api/ps"
MODELO_LLM = "gemma4:12b"
MODELO_EMBED = "nomic-embed-text"
OLLAMA_OPTIONS = {"num_ctx": 8192}
DEBUG = False


class OllamaEmbedding(EmbeddingFunction[Documents]):
    def __call__(self, input: Documents):
        r = requests.post(OLLAMA_EMBED_URL, json={"model": MODELO_EMBED, "input": input}, timeout=60)
        r.raise_for_status()
        return r.json()["embeddings"]

    def name(self):
        return MODELO_EMBED


EF = OllamaEmbedding()


def gerir_gpu_inicio():
    try:
        r = requests.get(OLLAMA_PS_URL, timeout=5)
        r.raise_for_status()
        modelos_ativos = r.json().get("models", [])
    except Exception:
        modelos_ativos = []

    for m in modelos_ativos:
        nome = m.get("name", "")
        if nome != MODELO_LLM:
            requests.post(OLLAMA_URL, json={"model": nome, "prompt": "", "keep_alive": 0}, timeout=10)
            print(f"  Descarregado da GPU: {nome}")

    print(f"A carregar {MODELO_LLM} na GPU...")
    try:
        requests.post(OLLAMA_URL, json={"model": MODELO_LLM, "keep_alive": -1}, timeout=30)
        print("Modelo pronto.")
    except requests.exceptions.Timeout:
        print("Aviso: timeout ao pré-carregar o modelo — será carregado na primeira pergunta.")


def descarregar_modelo():
    try:
        requests.post(OLLAMA_URL, json={"model": MODELO_LLM, "prompt": "", "keep_alive": 0}, timeout=10)
        print(f"\nModelo descarregado da GPU.")
    except Exception:
        pass


def extrair_texto(caminho):
    if caminho.endswith(".pdf"):
        reader = PdfReader(caminho)
        return "\n".join(t for p in reader.pages if (t := p.extract_text()))
    if caminho.endswith(".docx"):
        return "\n".join(p.text for p in Document(caminho).paragraphs if p.text.strip())
    if caminho.endswith(".doc"):
        try:
            import win32com.client
            word = win32com.client.Dispatch("Word.Application")
            word.Visible = False
            doc = word.Documents.Open(os.path.abspath(caminho))
            texto = doc.Content.Text
            doc.Close(False)
            word.Quit()
            return texto
        except Exception as e:
            raise RuntimeError(f"Erro ao ler .doc (requer Microsoft Word instalado): {e}")
    with open(caminho, encoding="utf-8") as f:
        return f.read()


def dividir_em_chunks(texto, tamanho=300, overlap=50):
    palavras = texto.split()
    chunks = []
    passo = tamanho - overlap
    for i in range(0, len(palavras), passo):
        chunk = " ".join(palavras[i:i + tamanho])
        if chunk:
            chunks.append(chunk)
    return chunks



def iniciar_base(cliente):
    colecao = cliente.get_or_create_collection(name=NOME_COLECAO, embedding_function=EF)

    # Descobre quais PDFs já foram indexados
    existentes = colecao.get(include=["metadatas"])
    fontes_indexadas = {m["fonte"] for m in existentes["metadatas"]} if existentes["metadatas"] else set()

    ficheiros_disponiveis = sum((glob.glob(os.path.join(PASTA_DOCS, f"*{ext}")) for ext in (".pdf", ".md", ".docx", ".doc")), [])
    ficheiros_novos = [p for p in ficheiros_disponiveis if os.path.basename(p) not in fontes_indexadas]

    if not ficheiros_novos:
        print(f"Base de conhecimento atualizada ({len(fontes_indexadas)} ficheiro(s) indexado(s)).")
        return colecao

    print(f"{len(ficheiros_novos)} ficheiro(s) novo(s) encontrado(s). A indexar...")

    id_base = len(existentes["ids"])
    for caminho in ficheiros_novos:
        nome = os.path.basename(caminho)
        print(f"  A digerir: {nome}")
        texto = extrair_texto(caminho)
        chunks = dividir_em_chunks(texto)

        if not chunks:
            print(f"  Aviso: sem texto extraído de {nome}")
            continue

        colecao.add(
            documents=chunks,
            metadatas=[{"fonte": nome}] * len(chunks),
            ids=[f"doc_{id_base + i}" for i in range(len(chunks))],
        )
        id_base += len(chunks)

    print(f"Indexação concluída. {id_base} blocos no total.")
    return colecao


def perguntar(colecao, pergunta):
    resultados = colecao.query(query_texts=[pergunta], n_results=5)
    if DEBUG:
        print(f"[DEBUG] chunks devolvidos: {len(resultados['documents'][0])}")
        for i, doc in enumerate(resultados["documents"][0]):
            print(f"[DEBUG] chunk {i}: {doc[:150]!r}")
    contexto = "\n---\n".join(resultados["documents"][0])

    prompt = f"""És o Especialista_SIR, um assistente especializado em documentação SIR (Sistema da Indústria Responsável). Responde sempre em português europeu.
Usa o seguinte contexto extraído de documentos para responder à pergunta.
Podes sintetizar e inferir com base no contexto. Só dizes que não tens informação se o contexto for completamente irrelevante para a pergunta.

CONTEXTO:
{contexto}

PERGUNTA:
{pergunta}

RESPOSTA:"""

    if DEBUG:
        print(f"[DEBUG] prompt: {len(prompt)} chars / ~{len(prompt.split())} palavras")
    try:
        r = requests.post(OLLAMA_URL, json={"model": MODELO_LLM, "prompt": prompt, "stream": False, "options": OLLAMA_OPTIONS}, timeout=120)
        r.raise_for_status()
        data = r.json()
        if DEBUG:
            print(f"[DEBUG] eval_count={data.get('eval_count')} prompt_eval_count={data.get('prompt_eval_count')}")
        resposta = data.get("response", "").strip()
        return resposta if resposta else f"Sem resposta do modelo. (contexto: {len(prompt)} chars)"
    except requests.exceptions.ConnectionError:
        return "Erro: não foi possível conectar ao Ollama. Verifique se está em execução."
    except Exception as e:
        return f"Erro: {e}"


if __name__ == "__main__":
    signal.signal(signal.SIGINT, lambda *_: (descarregar_modelo(), sys.exit(0)))

    print("A preparar GPU...")
    gerir_gpu_inicio()

    print("A conectar à base de conhecimento...")
    cliente = chromadb.PersistentClient(path=PASTA_BD)
    colecao = iniciar_base(cliente)

    print("\nPronto! Faça perguntas sobre os documentos (escreva 'sair' para terminar).\n")
    try:
        while True:
            pergunta = input("Você: ").strip()
            if not pergunta:
                continue
            if pergunta.lower() == "sair":
                break
            print("A consultar...")
            print(f"\nIA: {perguntar(colecao, pergunta)}\n")
    finally:
        descarregar_modelo()

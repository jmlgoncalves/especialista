import pytest
import requests
import chromadb

from especialista import (
    OLLAMA_PS_URL,
    PASTA_BD,
    NOME_COLECAO,
    MODELO_LLM,
    iniciar_base,
    perguntar,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def colecao():
    import especialista
    # chromadb >= 0.6 chama embed_query()/embed_documents() em vez de __call__.
    # OllamaEmbedding não os define; patchar para delegar a __call__.
    ef = especialista.EF
    ef.embed_query = lambda input: ef(input)
    ef.embed_documents = lambda input: ef(input)
    cliente = chromadb.PersistentClient(path=PASTA_BD)
    return iniciar_base(cliente)


@pytest.fixture(scope="session")
def modelo_ps():
    """Devolve o registo /api/ps do MODELO_LLM, ou falha se o Ollama não responder."""
    r = requests.get(OLLAMA_PS_URL, timeout=10)
    r.raise_for_status()
    modelos = r.json().get("models", [])
    match = next((m for m in modelos if MODELO_LLM in m.get("name", "")), None)
    return match


# ---------------------------------------------------------------------------
# Testes de estado do modelo
# ---------------------------------------------------------------------------

class TestModeloCarregado:

    def test_modelo_esta_na_memoria(self, modelo_ps):
        """gemma4:12b deve estar carregado (presente em /api/ps)."""
        assert modelo_ps is not None, (
            f"{MODELO_LLM} não está carregado em memória. "
            "Execute o bot ou use 'ollama run gemma4:12b' primeiro."
        )

    def test_sem_spill_de_memoria(self, modelo_ps):
        """Toda a memória do modelo deve estar em VRAM (sem spill para RAM)."""
        if modelo_ps is None:
            pytest.skip("Modelo não carregado — ignorado.")

        size_total = modelo_ps.get("size", 0)
        size_vram  = modelo_ps.get("size_vram", 0)

        assert size_vram >= size_total, (
            f"Spill detectado: {MODELO_LLM} ocupa {size_total / 1e9:.1f} GB no total "
            f"mas apenas {size_vram / 1e9:.1f} GB estão em VRAM."
        )


# ---------------------------------------------------------------------------
# Testes de RAG
# ---------------------------------------------------------------------------

PERGUNTA_DL = "dá me em 1 linha um resumo rapido do decreto lei 169 2012 sobre o SIR"
PERGUNTA_FONTE = "dá me uma resposta curta, o que indicaste foi da tua BD interna ou da tua BD RAG?"


class TestPerguntas:

    def test_resumo_dl_169_2012(self, colecao):
        """Deve devolver um resumo não vazio sobre o DL 169/2012."""
        resposta = perguntar(colecao, PERGUNTA_DL)

        assert resposta, "A resposta está vazia."
        assert len(resposta) >= 20, f"Resposta demasiado curta: {resposta!r}"
        assert not resposta.startswith("Erro"), f"O modelo devolveu um erro: {resposta}"

    def test_pergunta_fonte_da_resposta(self, colecao):
        """Deve devolver uma resposta válida sobre a origem (BD interna vs RAG)."""
        resposta = perguntar(colecao, PERGUNTA_FONTE)

        assert resposta, "A resposta está vazia."
        assert len(resposta) >= 10, f"Resposta demasiado curta: {resposta!r}"
        assert not resposta.startswith("Erro"), f"O modelo devolveu um erro: {resposta}"

        # Verifica que a resposta menciona a origem (RAG ou BD interna)
        termos_esperados = ["rag", "bd", "base", "documento", "contexto", "interna", "conhecimento"]
        resposta_lower = resposta.lower()
        assert any(t in resposta_lower for t in termos_esperados), (
            f"A resposta não menciona a origem da informação: {resposta!r}"
        )

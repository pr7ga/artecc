# app.py
import streamlit as st
import random

st.set_page_config(page_title="Jogo de Áudio", layout="centered")

# -----------------------------
# Inicialização de sessão
# -----------------------------
if "arquivos" not in st.session_state:
    # armazenaremos {1: {"bytes": ..., "nome": ..., "filename": ...}, ...}
    st.session_state.arquivos = {}
if "fase" not in st.session_state:
    st.session_state.fase = "config"  # config, esperando_numero, tocando_audio, resultado
if "mapa_random" not in st.session_state:
    st.session_state.mapa_random = {}
if "resposta_correta" not in st.session_state:
    st.session_state.resposta_correta = None
if "numero_escolhido" not in st.session_state:
    st.session_state.numero_escolhido = None
if "escolha_letra" not in st.session_state:
    st.session_state.escolha_letra = None
if "placar" not in st.session_state:
    st.session_state.placar = {"acertos": 0, "erros": 0}

# -----------------------------
# UI
# -----------------------------
st.title("🎵 Jogo de Áudio")

# -----------------------------
# Configuração pelo Master
# -----------------------------
if st.session_state.fase == "config":
    st.header("Configuração do Master (envie 5 MP3 e dê nomes)")

    for i in range(1, 6):
        uploaded = st.file_uploader(f"Carregue o arquivo {i}", type=["mp3"], key=f"file_{i}")
        nome = st.text_input(f"Nome para o arquivo {i}", key=f"nome_{i}")

        if uploaded is not None and nome.strip() != "":
            # Só sobrescreve se for um arquivo diferente do que está em sessão
            already = st.session_state.arquivos.get(i)
            if (already is None) or (already.get("filename") != uploaded.name) or (already.get("nome") != nome):
                # ler bytes e guardar na sessão
                file_bytes = uploaded.read()
                st.session_state.arquivos[i] = {
                    "bytes": file_bytes,
                    "nome": nome,
                    "filename": uploaded.name,
                }

    st.write(f"Arquivos carregados: {len(st.session_state.arquivos)}/5")
    if len(st.session_state.arquivos) == 5:
        if st.button("Iniciar Jogo"):
            st.session_state.fase = "esperando_numero"
            # garantir que mapa_random esteja vazio para iniciar rodada nova
            st.session_state.mapa_random = {}
            st.rerun()

# -----------------------------
# Etapa: Jogador escolhe número
# -----------------------------
elif st.session_state.fase == "esperando_numero":
    st.header("Rodada de Jogo")

    # Placar + reset
    st.subheader("📊 Placar")
    st.write(f"✅ Acertos: {st.session_state.placar['acertos']} | ❌ Erros: {st.session_state.placar['erros']}")
    if st.button("Resetar Placar"):
        st.session_state.placar = {"acertos": 0, "erros": 0}
        st.rerun()

    # Criar novo mapa se necessário (mapa: número de 1-5 -> índice do arquivo)
    if not st.session_sta_

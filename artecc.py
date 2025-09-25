import streamlit as st
import random

st.set_page_config(page_title="Jogo de Áudio", layout="centered")

# -----------------------------
# Inicialização de sessão
# -----------------------------
if "arquivos" not in st.session_state:
    st.session_state.arquivos = {}  # {1: {"file":..., "nome":...}, ...}
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

# -----------------------------
# Configuração pelo Master
# -----------------------------
st.title("🎵 Jogo de Áudio")

if st.session_state.fase == "config":
    st.header("Configuração do Master")
    for i in range(1, 6):
        file = st.file_uploader(f"Carregue o arquivo {i}", type=["mp3"], key=f"file_{i}")
        nome = st.text_input(f"Nome para o arquivo {i}", key=f"nome_{i}")
        if file and nome:
            st.session_state.arquivos[i] = {"file": file, "nome": nome}

    if len(st.session_state.arquivos) == 5:
        if st.button("Iniciar Jogo"):
            st.session_state.fase = "esperando_numero"
            st.rerun()

# -----------------------------
# Etapa: Jogador escolhe número
# -----------------------------
elif st.session_state.fase == "esperando_numero":
    st.header("Rodada de Jogo")

    # Criar novo mapa se necessário
    if not st.session_state.mapa_random:
        numeros = list(st.session_state.arquivos.keys())
        random.shuffle(numeros)
        st.session_state.mapa_random = {i + 1: numeros[i] for i in range(5)}

    escolha_num = st.radio(
        "Você quer escolher um número de 1 a 5 ou deixar o sistema escolher?",
        ["Escolher eu mesmo", "Sistema escolher"],
        key="modo_escolha"
    )

    if escolha_num == "Escolher eu mesmo":
        numero_escolhido = st.number_input("Escolha um número (1-5)", min_value=1, max_value=5, step=1)
    else:
        numero_escolhido = random.choice(range(1, 6))
        st.write(f"O sistema escolheu o número: **{numero_escolhido}**")

    if st.button("Confirmar escolha"):
        st.session_state.numero_escolhido = numero_escolhido
        idx_real = st.session_state.mapa_random[numero_escolhido]
        st.session_state.resposta_correta = idx_real
        st.session_state.fase = "tocando_audio"
        st.rerun()

# -----------------------------
# Etapa: Toca o áudio e jogador escolhe letra
# -----------------------------
elif st.session_state.fase == "tocando_audio":
    idx_real = st.session_state.resposta_correta
    arquivo = st.session_state.arquivos[idx_real]["file"]

    st.audio(arquivo.read(), format="audio/mpeg")

    opcoes = {letra: v["nome"] for letra, v in zip("abcde", st.session_state.arquivos.values())}
    st.session_state.escolha_letra = st.radio("Qual é a resposta correta?", list(opcoes.keys()), key="resposta_jogador")

    if st.button("Responder"):
        # Guardar resposta e ir para fase de resultado
        st.session_state.fase = "resultado"
        st.rerun()

# -----------------------------
# Etapa: Mostrar resultado
# -----------------------------
elif st.session_state.fase == "resultado":
    opcoes = {letra: v["nome"] for letra, v in zip("abcde", st.session_state.arquivos.values())}
    resposta_letra = list(opcoes.keys())[list(opcoes.values()).index(
        st.session_state.arquivos[st.session_state.resposta_correta]["nome"]
    )]

    if st.session_state.escolha_letra == resposta_letra:
        st.success("🎉 ACERTOU!")
    else:
        st.error("❌ ERROU!")

    if st.button("Jogar novamente"):
        st.session_state.mapa_random = {}
        st.session_state.numero_escolhido = None
        st.session_state.escolha_letra = None
        st.session_state.resposta_correta = None
        st.session_state.fase = "esperando_numero"
        st.rerun()

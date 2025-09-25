import streamlit as st
import random

st.set_page_config(page_title="Jogo de Áudio", layout="centered")

# -----------------------------
# Inicialização de sessão
# -----------------------------
if "arquivos" not in st.session_state:
    st.session_state.arquivos = {}  # {1: {"file":..., "nome":...}, ...}
if "rodada" not in st.session_state:
    st.session_state.rodada = 0
if "mapa_random" not in st.session_state:
    st.session_state.mapa_random = {}
if "resposta_correta" not in st.session_state:
    st.session_state.resposta_correta = None
if "fase" not in st.session_state:
    st.session_state.fase = "config"  # config, jogo, resultado


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
            st.session_state.fase = "jogo"
            st.rerun()

# -----------------------------
# Jogo do Jogador
# -----------------------------
elif st.session_state.fase == "jogo":
    st.header("Rodada de Jogo")

    # Randomização do mapa de números → arquivos
    numeros = list(st.session_state.arquivos.keys())
    random.shuffle(numeros)
    st.session_state.mapa_random = {i+1: numeros[i] for i in range(5)}

    escolha_num = st.radio(
        "Você quer escolher um número de 1 a 5 ou deixar o sistema escolher?",
        ["Escolher eu mesmo", "Sistema escolher"]
    )

    if escolha_num == "Escolher eu mesmo":
        numero_escolhido = st.number_input("Escolha um número (1-5)", min_value=1, max_value=5, step=1)
    else:
        numero_escolhido = random.choice(range(1, 6))
        st.write(f"O sistema escolheu o número: **{numero_escolhido}**")

    if st.button("Confirmar escolha"):
        idx_real = st.session_state.mapa_random[numero_escolhido]
        arquivo = st.session_state.arquivos[idx_real]["file"]
        st.session_state.resposta_correta = idx_real

        # Tocar áudio
        st.audio(arquivo.read(), format="audio/mpeg")

        # Mostrar opções
        st.subheader("Qual é a resposta correta?")
        opcoes = {letra: v["nome"] for letra, v in zip("abcde", st.session_state.arquivos.values())}
        escolha_letra = st.radio("Escolha uma opção:", list(opcoes.keys()), key="escolha_letra")

        if st.button("Responder"):
            # Verificar se acertou
            resposta_letra = list(opcoes.keys())[list(opcoes.values()).index(
                st.session_state.arquivos[st.session_state.resposta_correta]["nome"]
            )]
            if escolha_letra == resposta_letra:
                st.success("🎉 ACERTOU!")
            else:
                st.error("❌ ERROU!")

            if st.button("Jogar novamente"):
                st.session_state.fase = "jogo"
                st.rerun()

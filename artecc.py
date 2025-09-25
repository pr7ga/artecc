# app.py
import streamlit as st
import random
import os

st.set_page_config(page_title="ARTECC 2025 - 3º Ano - Ambientes Sonoros", layout="centered")

PASTA_ARQUIVOS = "arquivos_mp3"  # pasta no repositório

# -----------------------------
# Inicialização de sessão
# -----------------------------
if "arquivos" not in st.session_state:
    st.session_state.arquivos = {}  # {key: {"bytes":..., "nome":...}}
if "fase" not in st.session_state:
    st.session_state.fase = "config"  # config, esperando_numero, tocando_audio, resultado
if "arquivos_rodada" not in st.session_state:
    st.session_state.arquivos_rodada = {}  # 1..5 para rodada
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
if "placar_incrementado" not in st.session_state:
    st.session_state.placar_incrementado = False
if "modo_arquivos" not in st.session_state:
    st.session_state.modo_arquivos = None  # 'upload' ou 'repositorio'

# -----------------------------
# UI
# -----------------------------
st.markdown(
    """
    <div style='text-align: center; line-height: 1.2'>
        <h1 style='font-size:48px; margin:0;'>ARTECC 2025 - 3º Ano</h1>
        <h2 style='font-size:36px; margin:0;'>🎵 Ambientes Sonoros 🎵</h2>
    </div>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# Escolha do modo de arquivos
# -----------------------------
if st.session_state.fase == "config" and st.session_state.modo_arquivos is None:
    st.header("Escolha a fonte dos arquivos de áudio")
    escolha = st.radio(
        "Deseja usar os arquivos da pasta no repositório ou enviar pelo master?",
        ["Pasta no repositório", "Upload pelo master"]
    )
    if st.button("Confirmar escolha"):
        st.session_state.modo_arquivos = "repositorio" if escolha == "Pasta no repositório" else "upload"
        st.rerun()

# -----------------------------
# Carregar arquivos da pasta do repositório
# -----------------------------
if st.session_state.modo_arquivos == "repositorio" and st.session_state.fase == "config":
    st.header("Arquivos carregados da pasta do repositório")
    arquivos = {}
    if os.path.exists(PASTA_ARQUIVOS):
        for filename in os.listdir(PASTA_ARQUIVOS):
            if filename.endswith(".mp3"):
                filepath = os.path.join(PASTA_ARQUIVOS, filename)
                with open(filepath, "rb") as f:
                    arquivos[filename] = {"bytes": f.read(), "nome": filename}
        if len(arquivos) < 5:
            st.warning("É necessário ter pelo menos 5 arquivos MP3 na pasta.")
        else:
            st.session_state.arquivos = arquivos
            st.write(f"{len(arquivos)} arquivos carregados.")
            if st.button("Iniciar Jogo"):
                st.session_state.fase = "esperando_numero"
                st.rerun()
    else:
        st.error(f"A pasta '{PASTA_ARQUIVOS}' não existe no repositório.")

# -----------------------------
# Upload pelo master
# -----------------------------
elif st.session_state.modo_arquivos == "upload" and st.session_state.fase == "config":
    st.header("Upload de arquivos pelo master (mínimo 5)")
    uploaded_files = st.file_uploader(
        "Envie seus arquivos MP3",
        type=["mp3"],
        accept_multiple_files=True
    )
    if uploaded_files:
        for file in uploaded_files:
            key = file.name
            if key not in st.session_state.arquivos:
                st.session_state.arquivos[key] = {"bytes": file.read(), "nome": key}

    st.write(f"Arquivos carregados: {len(st.session_state.arquivos)}")
    if len(st.session_state.arquivos) >= 5:
        if st.button("Iniciar Jogo"):
            st.session_state.fase = "esperando_numero"
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

    if len(st.session_state.arquivos) < 5:
        st.warning("É necessário pelo menos 5 arquivos para jogar.")
    else:
        if not st.session_state.arquivos_rodada:
            arquivos_sorteados = random.sample(list(st.session_state.arquivos.keys()), 5)
            st.session_state.arquivos_rodada = {
                i+1: st.session_state.arquivos[k] for i, k in enumerate(arquivos_sorteados)
            }
            st.session_state.mapa_random = {}
            st.session_state.numero_escolhido = None
            st.session_state.resposta_correta = None
            st.session_state.escolha_letra = None
            st.session_state.placar_incrementado = False

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
            numeros = list(st.session_state.arquivos_rodada.keys())
            random.shuffle(numeros)
            st.session_state.mapa_random = {i+1: numeros[i] for i in range(5)}
            idx_real = st.session_state.mapa_random[numero_escolhido]
            st.session_state.resposta_correta = idx_real
            st.session_state.fase = "tocando_audio"
            st.session_state.placar_incrementado = False
            st.rerun()

# -----------------------------
# Etapa: Toca o áudio e jogador escolhe letra
# -----------------------------
elif st.session_state.fase == "tocando_audio":
    idx_real = st.session_state.resposta_correta
    arquivo_bytes = st.session_state.arquivos_rodada[idx_real]["bytes"]

    st.subheader("O áudio será reproduzido abaixo:")
    st.audio(arquivo_bytes, format="audio/mpeg")

    sorted_items = sorted(st.session_state.arquivos_rodada.items(), key=lambda x: x[0])
    filekey_to_letter = {}
    display_opcoes = []

    for i, (file_key, meta) in enumerate(sorted_items):
        letra = chr(ord("a") + i)
        filekey_to_letter[file_key] = letra
        display_opcoes.append(f"{letra} - {meta['nome']}")

    st.session_state.escolha_letra = st.radio(
        "Escolha uma opção:",
        options=display_opcoes,
        key="resposta_jogador"
    )

    if st.button("Responder"):
        st.session_state.escolha_letra = st.session_state.escolha_letra.split(" - ")[0]

        if not st.session_state.placar_incrementado:
            resposta_letra_correta = filekey_to_letter[st.session_state.resposta_correta]
            if st.session_state.escolha_letra == resposta_letra_correta:
                st.session_state.placar["acertos"] += 1
            else:
                st.session_state.placar["erros"] += 1
            st.session_state.placar_incrementado = True

        st.session_state.fase = "resultado"
        st.rerun()

# -----------------------------
# Etapa: Mostrar resultado
# -----------------------------
elif st.session_state.fase == "resultado":
    sorted_items = sorted(st.session_state.arquivos_rodada.items(), key=lambda x: x[0])
    filekey_to_letter = {}
    for i, (file_key, meta) in enumerate(sorted_items):
        letra = chr(ord("a") + i)
        filekey_to_letter[file_key] = letra

    corret_key = st.session_state.resposta_correta
    resposta_letra_correta = filekey_to_letter[corret_key]
    resposta_nome_correta = st.session_state.arquivos_rodada[corret_key]["nome"]

    if st.session_state.escolha_letra == resposta_letra_correta:
        st.markdown(
            "<h1 style='color:green; font-weight:bold; text-align:center;'>🎉 ACERTOU!</h1>",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            "<h1 style='color:red; font-weight:bold; text-align:center;'>❌ ERROU!</h1>",
            unsafe_allow_html=True
        )
        st.info(f"A resposta correta era: **{resposta_letra_correta} - {resposta_nome_correta}**")

    st.subheader("📊 Placar Atual")
    st.write(f"✅ Acertos: {st.session_state.placar['acertos']} | ❌ Erros: {st.session_state.placar['erros']}")

    if st.button("Jogar novamente"):
        st.session_state.arquivos_rodada = {}
        st.session_state.mapa_random = {}
        st.session_state.numero_escolhido = None
        st.session_state.escolha_letra = None
        st.session_state.resposta_correta = None
        st.session_state.fase = "esperando_numero"
        st.session_state.placar_incrementado = False
        st.rerun()

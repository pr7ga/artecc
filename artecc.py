# app.py
import streamlit as st
import random

st.set_page_config(page_title="Jogo de Áudio", layout="centered")

# -----------------------------
# Inicialização de sessão
# -----------------------------
if "arquivos" not in st.session_state:
    st.session_state.arquivos = {}  # {1: {"bytes": ..., "nome": ..., "filename": ...}, ...}
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
if "placar_incrementado" not in st.session_state:
    st.session_state.placar_incrementado = False  # variável auxiliar para evitar contagem múltipla

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
            already = st.session_state.arquivos.get(i)
            if (already is None) or (already.get("filename") != uploaded.name) or (already.get("nome") != nome):
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

    # Criar novo mapa se necessário
    if not st.session_state.mapa_random:
        numeros = list(st.session_state.arquivos.keys())
        random.shuffle(numeros)
        st.session_state.mapa_random = {i + 1: numeros[i] for i in range(5)}
        st.session_state.numero_escolhido = None
        st.session_state.resposta_correta = None
        st.session_state.escolha_letra = None
        st.session_state.placar_incrementado = False  # resetar flag para nova rodada

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
        st.session_state.placar_incrementado = False  # garantir flag zerada
        st.rerun()

# -----------------------------
# Etapa: Toca o áudio e jogador escolhe letra
# -----------------------------
elif st.session_state.fase == "tocando_audio":
    idx_real = st.session_state.resposta_correta
    arquivo_bytes = st.session_state.arquivos[idx_real]["bytes"]

    st.subheader("O áudio será reproduzido abaixo:")
    st.audio(arquivo_bytes, format="audio/mpeg")

    # Gerar opções a..e e mostrar "a - nome"
    sorted_items = sorted(st.session_state.arquivos.items(), key=lambda x: x[0])
    opcoes = {}
    filekey_to_letter = {}
    display_opcoes = []

    for i, (file_key, meta) in enumerate(sorted_items):
        letra = chr(ord("a") + i)
        opcoes[letra] = meta["nome"]
        filekey_to_letter[file_key] = letra
        display_opcoes.append(f"{letra} - {meta['nome']}")

    st.session_state.escolha_letra = st.radio(
        "Escolha uma opção:",
        options=display_opcoes,
        key="resposta_jogador"
    )

    if st.button("Responder"):
        # extrair apenas a letra
        st.session_state.escolha_letra = st.session_state.escolha_letra.split(" - ")[0]

        # Incrementar placar apenas uma vez por rodada
        if not st.session_state.placar_incrementado:
            corret_key = st.session_state.resposta_correta
            resposta_letra_correta = filekey_to_letter[corret_key]
            if st.session_state.escolha_letra == resposta_letra_correta:
                st.session_state.placar["acertos"] += 1
            else:
                st.session_state.placar["erros"] += 1
            st.session_state.placar_incrementado = True  # marca que já incrementou

        st.session_state.fase = "resultado"
        st.rerun()

# -----------------------------
# Etapa: Mostrar resultado
# -----------------------------
elif st.session_state.fase == "resultado":
    sorted_items = sorted(st.session_state.arquivos.items(), key=lambda x: x[0])
    filekey_to_letter = {}
    for i, (file_key, meta) in enumerate(sorted_items):
        letra = chr(ord("a") + i)
        filekey_to_letter[file_key] = letra

    corret_key = st.session_state.resposta_correta
    resposta_letra_correta = filekey_to_letter[corret_key]
    resposta_nome_correta = st.session_state.arquivos[corret_key]["nome"]

    if st.session_state.escolha_letra == resposta_letra_correta:
        st.success("🎉 ACERTOU!")
    else:
        st.error("❌ ERROU!")
        st.info(f"A resposta correta era: **{resposta_letra_correta} - {resposta_nome_correta}**")

    st.subheader("📊 Placar Atual")
    st.write(f"✅ Acertos: {st.session_state.placar['acertos']} | ❌ Erros: {st.session_state.placar['erros']}")

    if st.button("Jogar novamente"):
        st.session_state.mapa_random = {}
        st.session_state.numero_escolhido = None
        st.session_state.escolha_letra = None
        st.session_state.resposta_correta = None
        st.session_state.fase = "esperando_numero"
        st.session_state.placar_incrementado = False
        st.rerun()

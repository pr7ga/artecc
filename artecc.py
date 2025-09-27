# app.py
import streamlit as st
import random
import os

st.set_page_config(page_title="ARTECC 2025 - 3º Ano - Ambientes Sonoros", layout="centered")

PASTA_ARQUIVOS = "arquivos_mp3"

# -----------------------------
# Inicialização de sessão
# -----------------------------
if "arquivos" not in st.session_state:
    st.session_state.arquivos = {}  # todos os arquivos disponíveis (filename -> {"bytes","nome"})
if "fase" not in st.session_state:
    st.session_state.fase = "config"  # config, tocando_audio, resultado
if "arquivos_rodada" not in st.session_state:
    st.session_state.arquivos_rodada = {}  # mapa 1..5 -> meta
if "resposta_correta" not in st.session_state:
    st.session_state.resposta_correta = None
if "escolha_letra" not in st.session_state:
    st.session_state.escolha_letra = None
if "placar" not in st.session_state:
    st.session_state.placar = {"acertos": 0, "erros": 0}
if "placar_incrementado" not in st.session_state:
    st.session_state.placar_incrementado = False
if "modo_arquivos" not in st.session_state:
    st.session_state.modo_arquivos = None  # 'repositorio' ou 'upload'

# -----------------------------
# Funções utilitárias
# -----------------------------
def can_start_round():
    """Retorna True se há arquivos suficientes para sortear 5."""
    return isinstance(st.session_state.arquivos, dict) and len(st.session_state.arquivos) >= 5

def start_new_round():
    """Inicializa uma nova rodada: seleciona 5 arquivos e escolhe a resposta correta."""
    # validação
    if not can_start_round():
        return False
    try:
        arquivos_sorteados = random.sample(list(st.session_state.arquivos.keys()), 5)
    except Exception:
        return False
    st.session_state.arquivos_rodada = {i+1: st.session_state.arquivos[k] for i, k in enumerate(arquivos_sorteados)}
    # escolhe a chave 1..5 que será a correta
    st.session_state.resposta_correta = random.choice(list(st.session_state.arquivos_rodada.keys()))
    st.session_state.escolha_letra = None
    st.session_state.placar_incrementado = False
    return True

def safe_sorted_rodada_items():
    """Retorna lista ordenada de itens da rodada; se inconsistent, tenta reiniciar rodada."""
    ar = st.session_state.get("arquivos_rodada")
    if not isinstance(ar, dict) or len(ar) != 5:
        ok = start_new_round()
        if not ok:
            return []
    # se ainda inválido, devolve lista vazia
    ar = st.session_state.get("arquivos_rodada")
    if not isinstance(ar, dict):
        return []
    return sorted(ar.items(), key=lambda x: x[0])

# -----------------------------
# CSS (opcional)
# -----------------------------
st.markdown(
    """
    <style>
    .card {
        border-radius: 15px;
        padding: 14px;
        margin: 6px;
        font-size: 18px;
        font-weight: bold;
        text-align: center;
        background-color: #f6f9ff;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# Título
# -----------------------------
st.markdown(
    """
    <div style='text-align:center; line-height:1.2'>
        <h1 style='font-size:48px; margin:0;'>ARTECC 2025 - 3º Ano</h1>
        <h2 style='font-size:36px; margin:0;'>🎵 Ambientes Sonoros 🎵</h2>
    </div>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# Escolha do modo de arquivos (apenas em config)
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
    arquivos_locais = {}
    if os.path.exists(PASTA_ARQUIVOS):
        for filename in os.listdir(PASTA_ARQUIVOS):
            if filename.lower().endswith(".mp3"):
                filepath = os.path.join(PASTA_ARQUIVOS, filename)
                with open(filepath, "rb") as f:
                    arquivos_locais[filename] = {"bytes": f.read(), "nome": filename}
        if len(arquivos_locais) < 5:
            st.warning("É necessário ter pelo menos 5 arquivos MP3 na pasta.")
        else:
            st.session_state.arquivos = arquivos_locais
            st.write(f"{len(arquivos_locais)} arquivos disponíveis.")
            if st.button("🎮 Iniciar Jogo"):
                # ao iniciar, inicializa rodada imediatamente
                started = start_new_round()
                if started:
                    st.session_state.fase = "tocando_audio"
                else:
                    st.error("Erro ao iniciar rodada. Verifique os arquivos.")
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
        if st.button("🎮 Iniciar Jogo"):
            started = start_new_round()
            if started:
                st.session_state.fase = "tocando_audio"
            else:
                st.error("Erro ao iniciar rodada. Verifique os arquivos.")
            st.rerun()

# -----------------------------
# Tocando áudio / Jogador escolhe
# -----------------------------
elif st.session_state.fase == "tocando_audio":
    # garanta que há arquivos suficientes
    if not can_start_round():
        st.warning("Não há arquivos suficientes para iniciar o jogo. Volte à configuração.")
    else:
        # garantir que arquivos_rodada/resposta_correta válidos
        items = safe_sorted_rodada_items()
        if not items:
            st.warning("Não foi possível iniciar a rodada — verifique os arquivos e tente novamente.")
        else:
            # pegar bytes do arquivo correto (com guard)
            correct_key = st.session_state.get("resposta_correta")
            if correct_key not in st.session_state.arquivos_rodada:
                # reinicia rodada se inconsistente
                start_new_round()
                items = safe_sorted_rodada_items()
            arquivo_meta = st.session_state.arquivos_rodada.get(st.session_state.resposta_correta)
            arquivo_bytes = arquivo_meta.get("bytes") if arquivo_meta else None
            if arquivo_bytes is None:
                st.warning("Erro ao acessar o áudio da rodada — reiniciando rodada.")
                st.session_state.arquivos_rodada = {}
                st.session_state.resposta_correta = None
                st.session_state.placar_incrementado = False
                st.experimental_rerun()

            # Placar horizontal
            col1, col2 = st.columns(2)
            with col1:
                st.metric("✅ Acertos", st.session_state.placar["acertos"])
            with col2:
                st.metric("❌ Erros", st.session_state.placar["erros"])
            if st.button("🔄 Resetar Placar"):
                st.session_state.placar = {"acertos": 0, "erros": 0}
                st.rerun()

            # Player
            st.subheader("🎵 Ouça o áudio e tente identificar o ambiente")
            st.audio(arquivo_bytes, format="audio/mpeg")

            # Opções (5 colunas)
            st.subheader("Escolha uma opção:")
            sorted_items = items  # já validado
            filekey_to_letra = {}
            cols = st.columns(5)
            for i, (file_key, meta) in enumerate(sorted_items):
                letra = chr(ord("a") + i)
                filekey_to_letra[file_key] = letra
                nome_limpo = os.path.splitext(meta["nome"])[0]
                with cols[i]:
                    if st.button(nome_limpo, key=f"opt_{i}"):
                        # confirmação de consistência antes de contar
                        if st.session_state.resposta_correta not in filekey_to_letra:
                            # estado inconsistente — reinicia rodada
                            st.warning("Estado inconsistente detectado — reiniciando rodada.")
                            st.session_state.arquivos_rodada = {}
                            st.session_state.resposta_correta = None
                            st.session_state.escolha_letra = None
                            st.session_state.placar_incrementado = False
                            st.rerun()
                        st.session_state.escolha_letra = letra
                        if not st.session_state.placar_incrementado:
                            letra_correta = filekey_to_letra[st.session_state.resposta_correta]
                            if st.session_state.escolha_letra == letra_correta:
                                st.session_state.placar["acertos"] += 1
                            else:
                                st.session_state.placar["erros"] += 1
                            st.session_state.placar_incrementado = True
                        st.session_state.fase = "resultado"
                        st.rerun()

# -----------------------------
# Resultado
# -----------------------------
elif st.session_state.fase == "resultado":
    # valida estado
    if not isinstance(st.session_state.arquivos_rodada, dict) or len(st.session_state.arquivos_rodada) != 5:
        st.warning("Estado inconsistente na tela de resultado — reiniciando rodada.")
        st.session_state.fase = "tocando_audio"
        st.session_state.arquivos_rodada = {}
        st.session_state.resposta_correta = None
        st.session_state.escolha_letra = None
        st.session_state.placar_incrementado = False
        st.rerun()

    sorted_items = sorted(st.session_state.arquivos_rodada.items(), key=lambda x: x[0])
    filekey_to_letra = {file_key: chr(ord("a") + i) for i, (file_key, meta) in enumerate(sorted_items)}
    corret_key = st.session_state.resposta_correta

    # guard: corret_key deve existir
    if corret_key not in filekey_to_letra:
        st.warning("Estado inconsistente detectado — reiniciando rodada.")
        st.session_state.arquivos_rodada = {}
        st.session_state.resposta_correta = None
        st.session_state.escolha_letra = None
        st.session_state.placar_incrementado = False
        st.session_state.fase = "tocando_audio"
        st.rerun()

    letra_correta = filekey_to_letra[corret_key]
    nome_correto = os.path.splitext(st.session_state.arquivos_rodada[corret_key]["nome"])[0]

    if st.session_state.escolha_letra == letra_correta:
        st.markdown("<h1 style='color:green; font-weight:bold; text-align:center;'>🎉 ACERTOU!</h1>", unsafe_allow_html=True)
    else:
        st.markdown("<h1 style='color:red; font-weight:bold; text-align:center;'>❌ ERROU!</h1>", unsafe_allow_html=True)
        st.info(f"A resposta correta era: **{nome_correto}**")

    st.subheader("📊 Placar Atual")
    st.write(f"✅ Acertos: {st.session_state.placar['acertos']} | ❌ Erros: {st.session_state.placar['erros']}")

    if st.button("🔁 Jogar novamente"):
        st.session_state.arquivos_rodada = {}
        st.session_state.resposta_correta = None
        st.session_state.escolha_letra = None
        st.session_state.placar_incrementado = False
        # inicia nova rodada imediatamente
        started = start_new_round()
        if not started:
            # se não der pra iniciar (por falta de arquivos), volta pra config
            st.session_state.fase = "config"
        else:
            st.session_state.fase = "tocando_audio"
        st.rerun()

# app.py
import streamlit as st
import random
import os

# Toggle de debug (mude para True se quiser ver o estado interno)
DEBUG = False

st.set_page_config(page_title="ARTECC 2025 - 3º Ano - Ambientes Sonoros", layout="centered")

PASTA_ARQUIVOS = "arquivos_mp3"

# -----------------------------
# Inicialização de session_state
# -----------------------------
if "arquivos" not in st.session_state:
    st.session_state.arquivos = {}  # filename -> {"bytes","nome"}
if "fase" not in st.session_state:
    st.session_state.fase = "config"  # config, tocando_audio, resultado
if "arquivos_rodada_list" not in st.session_state:
    st.session_state.arquivos_rodada_list = []  # lista de 5 metas
if "resposta_index" not in st.session_state:
    st.session_state.resposta_index = None  # 0..4
if "escolha_index" not in st.session_state:
    st.session_state.escolha_index = None
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
    return isinstance(st.session_state.arquivos, dict) and len(st.session_state.arquivos) >= 5

def start_new_round():
    """Cria arquivos_rodada_list (5 itens) e resposta_index (0..4)."""
    if not can_start_round():
        return False
    filenames = list(st.session_state.arquivos.keys())
    try:
        sampled = random.sample(filenames, 5)
    except Exception:
        return False
    st.session_state.arquivos_rodada_list = [st.session_state.arquivos[f] for f in sampled]
    st.session_state.resposta_index = random.randrange(5)
    st.session_state.escolha_index = None
    st.session_state.placar_incrementado = False
    # optional: round id for uniqueness if needed
    st.session_state.round_id = st.session_state.get("round_id", 0) + 1
    return True

def ensure_round():
    """Garante que arquivos_rodada_list exista e tenha 5 itens; tenta start_new_round se não."""
    if not isinstance(st.session_state.arquivos_rodada_list, list) or len(st.session_state.arquivos_rodada_list) != 5:
        return start_new_round()
    return True

def safe_get_arquivo_bytes():
    """Retorna bytes do arquivo correto ou None (sem lançar)."""
    try:
        ri = st.session_state.resposta_index
        if ri is None:
            return None
        lst = st.session_state.arquivos_rodada_list
        if not isinstance(lst, list) or len(lst) != 5:
            return None
        meta = lst[ri]
        if not isinstance(meta, dict):
            return None
        return meta.get("bytes")
    except Exception:
        return None

# -----------------------------
# (Opcional) mostrar debug
# -----------------------------
if DEBUG:
    st.sidebar.header("DEBUG")
    st.sidebar.write("fase:", st.session_state.fase)
    st.sidebar.write("modo_arquivos:", st.session_state.modo_arquivos)
    st.sidebar.write("arquivos keys:", list(st.session_state.arquivos.keys()))
    st.sidebar.write("arquivos_rodada_list length:", len(st.session_state.arquivos_rodada_list))
    st.sidebar.write("resposta_index:", st.session_state.resposta_index)
    st.sidebar.write("escolha_index:", st.session_state.escolha_index)
    st.sidebar.write("placar_incrementado:", st.session_state.placar_incrementado)
    st.sidebar.write("round_id:", st.session_state.get("round_id"))

# -----------------------------
# CSS leve (opcional)
# -----------------------------
st.markdown(
    """
    <style>
    .card {
        border-radius: 12px;
        padding: 12px;
        margin: 6px;
        font-size: 16px;
        font-weight: bold;
        text-align: center;
        background-color: #f6f9ff;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# Cabeçalho
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
# Fluxo: escolha de fonte (apenas em config)
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
                ok = start_new_round()
                if ok:
                    st.session_state.fase = "tocando_audio"
                else:
                    st.error("Erro ao iniciar rodada.")
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
            ok = start_new_round()
            if ok:
                st.session_state.fase = "tocando_audio"
            else:
                st.error("Erro ao iniciar rodada.")
            st.rerun()

# -----------------------------
# Tocando áudio / seleção do jogador
# -----------------------------
elif st.session_state.fase == "tocando_audio":
    if not can_start_round():
        st.warning("Não há arquivos suficientes. Volte à configuração.")
    else:
        # garantir rodada válida (tenta criar se não existir)
        ok = ensure_round()
        if not ok:
            st.warning("Não foi possível iniciar a rodada. Verifique os arquivos.")
        else:
            # pegar bytes do arquivo correto de forma segura
            arquivo_bytes = safe_get_arquivo_bytes()
            if arquivo_bytes is None:
                # se não conseguimos obter bytes, reiniciamos a rodada e tentamos novamente
                st.warning("Estado inconsistente detectado — reiniciando rodada.")
                start_new_round()
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

            # Opções em 5 colunas
            st.subheader("Escolha uma opção:")
            cols = st.columns(5)
            for i, meta in enumerate(st.session_state.arquivos_rodada_list):
                nome_limpo = os.path.splitext(meta.get("nome", ""))[0]
                with cols[i]:
                    # key garante botão único por posição; round_id ajuda se quiser variar a key por rodada
                    if st.button(nome_limpo, key=f"opt_{i}_r{st.session_state.get('round_id',0)}"):
                        st.session_state.escolha_index = i
                        if not st.session_state.placar_incrementado:
                            if st.session_state.escolha_index == st.session_state.resposta_index:
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
    # valida estado da rodada
    rod = st.session_state.get("arquivos_rodada_list", [])
    if not isinstance(rod, list) or len(rod) != 5:
        st.warning("Estado inconsistente na tela de resultado — reiniciando rodada.")
        ok = start_new_round()
        if ok:
            st.session_state.fase = "tocando_audio"
        else:
            st.session_state.fase = "config"
        st.rerun()
    else:
        ri = st.session_state.resposta_index
        ei = st.session_state.escolha_index
        if ri is None:
            st.warning("Resposta inválida — reiniciando rodada.")
            start_new_round()
            st.rerun()
        nome_correto = os.path.splitext(st.session_state.arquivos_rodada_list[ri].get("nome",""))[0]

        if ei == ri:
            st.markdown("<h1 style='color:green; font-weight:bold; text-align:center;'>🎉 ACERTOU!</h1>", unsafe_allow_html=True)
        else:
            st.markdown("<h1 style='color:red; font-weight:bold; text-align:center;'>❌ ERROU!</h1>", unsafe_allow_html=True)
            st.info(f"A resposta correta era: **{nome_correto}**")

        st.subheader("📊 Placar Atual")
        st.write(f"✅ Acertos: {st.session_state.placar['acertos']} | ❌ Erros: {st.session_state.placar['erros']}")

        if st.button("🔁 Jogar novamente"):
            ok = start_new_round()
            if ok:
                st.session_state.fase = "tocando_audio"
            else:
                st.session_state.fase = "config"
            st.rerun()

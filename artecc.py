import streamlit as st
import os
import random

st.set_page_config(page_title="ARTECC 2025", layout="wide")

# -----------------------------
# Inicialização do estado
# -----------------------------
if "fase" not in st.session_state:
    st.session_state.fase = "menu"

if "placar" not in st.session_state:
    st.session_state.placar = {"acertos": 0, "erros": 0}

if "arquivos" not in st.session_state:
    st.session_state.arquivos = {}

if "round_id" not in st.session_state:
    st.session_state.round_id = 0

# -----------------------------
# Funções
# -----------------------------
def resetar_jogo():
    st.session_state.placar = {"acertos": 0, "erros": 0}
    st.session_state.fase = "menu"
    st.session_state.arquivos_rodada = {}
    st.session_state.arquivos_rodada_list = []
    st.session_state.escolha_index = None
    st.session_state.resposta_index = None
    st.session_state.placar_incrementado = False

def iniciar_rodada():
    if not st.session_state.arquivos:
        st.warning("Nenhum arquivo carregado!")
        return
    st.session_state.round_id += 1
    arquivos_escolhidos = random.sample(
        list(st.session_state.arquivos.items()),
        min(5, len(st.session_state.arquivos))
    )
    st.session_state.arquivos_rodada = {i: meta for i, (k, meta) in enumerate(arquivos_escolhidos)}
    st.session_state.arquivos_rodada_list = list(st.session_state.arquivos_rodada.values())
    st.session_state.resposta_index = random.randint(0, len(st.session_state.arquivos_rodada_list) - 1)
    st.session_state.escolha_index = None
    st.session_state.placar_incrementado = False
    st.session_state.fase = "jogo"

# -----------------------------
# Layout principal
# -----------------------------
st.markdown(
    """
    <div style='text-align: center;'>
        <h1 style='font-size: 36px;'>ARTECC 2025 - 3º Ano</h1>
        <h2 style='font-size: 28px;'>🎵 Ambientes Sonoros 🎵</h2>
    </div>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# Escolha da fonte dos arquivos
# -----------------------------
modo = st.radio(
    "Como deseja carregar os áudios?",
    ["📂 Usar arquivos do repositório", "⬆️ Upload manual"]
)

if modo == "📂 Usar arquivos do repositório":
    pasta = "audios"  # ajuste para o nome da pasta no seu repositório
    if os.path.exists(pasta):
        arquivos_repo = os.listdir(pasta)
        st.session_state.arquivos = {}
        for nome in arquivos_repo:
            caminho = os.path.join(pasta, nome)
            with open(caminho, "rb") as f:
                st.session_state.arquivos[nome] = {
                    "nome": nome,
                    "bytes": f.read()
                }
        st.success(f"{len(arquivos_repo)} arquivos carregados do repositório.")
    else:
        st.error(f"A pasta '{pasta}' não foi encontrada no repositório.")

else:  # Upload manual
    with st.expander("📂 Carregar arquivos de áudio"):
        arquivos = st.file_uploader(
            "Selecione os arquivos de áudio",
            type=["mp3", "wav", "ogg", "m4a"],
            accept_multiple_files=True
        )
        if arquivos:
            for file in arquivos:
                st.session_state.arquivos[file.name] = {
                    "nome": file.name,
                    "bytes": file.read()
                }

# -----------------------------
# Fase do jogo
# -----------------------------
if st.session_state.fase == "menu":
    if st.session_state.arquivos:
        if st.button("▶️ Iniciar Jogo"):
            iniciar_rodada()
    else:
        st.info("Carregue ou selecione arquivos de áudio para começar.")

elif st.session_state.fase == "jogo":
    resposta_index = st.session_state.resposta_index
    arquivos_rodada_list = st.session_state.arquivos_rodada_list

    meta_resposta = arquivos_rodada_list[resposta_index]
    st.audio(meta_resposta["bytes"], format="audio/mp3")
    st.subheader("🎵 Ouça o áudio e tente identificar o ambiente:")

    cols = st.columns(len(arquivos_rodada_list))
    for i, meta in enumerate(arquivos_rodada_list):
        nome_limpo = os.path.splitext(meta.get("nome", ""))[0]
        with cols[i]:
            if st.button(nome_limpo, key=f"resp_{i}_r{st.session_state.round_id}"):
                st.session_state.escolha_index = i
                if not st.session_state.placar_incrementado:
                    if i == resposta_index:
                        st.session_state.placar["acertos"] += 1
                    else:
                        st.session_state.placar["erros"] += 1
                    st.session_state.placar_incrementado = True
                st.session_state.fase = "resultado"
                st.rerun()

elif st.session_state.fase == "resultado":
    escolha = st.session_state.escolha_index
    resposta = st.session_state.resposta_index
    arquivos_rodada_list = st.session_state.arquivos_rodada_list

    if escolha == resposta:
        st.success("✅ Resposta correta!")
    else:
        st.error(f"❌ Resposta incorreta! O correto era: {os.path.splitext(arquivos_rodada_list[resposta]['nome'])[0]}")

    st.write(f"**Acertos:** {st.session_state.placar['acertos']} | **Erros:** {st.session_state.placar['erros']}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Próxima Rodada"):
            iniciar_rodada()
            st.rerun()
    with col2:
        if st.button("🏁 Resetar Jogo"):
            resetar_jogo()
            st.rerun()

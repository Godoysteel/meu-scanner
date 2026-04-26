import streamlit as st
import requests
from streamlit_autorefresh import st_autorefresh
import pandas as pd
from datetime import datetime

# ── CONFIG ───────────────────────────────────────────────────────────────────
st.set_page_config(page_title="GDscanner Elite", page_icon="⚽", layout="wide")
st_autorefresh(interval=30 * 1000, key="datarefresh")

if 'historico_entradas' not in st.session_state:
    st.session_state['historico_entradas'] = []

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Mono:wght@400;500&family=DM+Sans:wght@400;600&display=swap');

[data-testid="stAppViewContainer"] { background-color: #0D0A00 !important; }
[data-testid="stSidebar"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }
section.main { background-color: #0D0A00 !important; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.2rem !important; max-width: 900px !important; }

/* expander estilo escuro */
[data-testid="stExpander"] {
    background: #150F00 !important;
    border: 1px solid #3A2E00 !important;
    border-radius: 10px !important;
    margin-bottom: 16px !important;
}
[data-testid="stExpander"] summary { color: #C88600 !important; font-family: monospace !important; font-size: 0.8rem !important; }

/* tabs */
.stTabs [data-baseweb="tab-list"] { background: #150F00; border-radius: 8px; padding: 4px; gap: 4px; }
.stTabs [data-baseweb="tab"] { background: transparent; color: #8A7040 !important; border-radius: 6px; font-family: 'DM Mono', monospace; font-size: 0.8rem; letter-spacing: 1px; }
.stTabs [aria-selected="true"] { background: #2A1F00 !important; color: #F5A800 !important; border-bottom: 2px solid #F5A800 !important; }

/* título */
.gd-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 2.4rem;
    color: #F5A800;
    letter-spacing: 5px;
    text-align: center;
    border-bottom: 1px solid #3A2E00;
    padding-bottom: 14px;
    margin-bottom: 22px;
}
.gd-subtitle {
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    color: #5A4500;
    text-align: center;
    letter-spacing: 3px;
    margin-top: -18px;
    margin-bottom: 22px;
    text-transform: uppercase;
}

/* card */
.card {
    background: #1A1400;
    border: 1px solid #3A2E00;
    border-left: 4px solid #F5A800;
    border-radius: 10px;
    padding: 0;
    margin-bottom: 16px;
    overflow: hidden;
}
.card-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: #110D00;
    padding: 8px 16px;
    border-bottom: 1px solid #2A2000;
}
.card-liga {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    color: #C88600;
    letter-spacing: 1.5px;
    text-transform: uppercase;
}
.card-tempo {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1rem;
    color: #F5A800;
    background: #2A1F00;
    border: 1px solid #5A4000;
    border-radius: 5px;
    padding: 1px 10px;
}
.card-placar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 16px;
    gap: 12px;
}
.time-h {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.35rem;
    color: #FFF8E0;
    letter-spacing: 1px;
    flex: 1;
}
.time-a {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.35rem;
    color: #FFF8E0;
    letter-spacing: 1px;
    flex: 1;
    text-align: right;
}
.placar-vs {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.8rem;
    color: #F5A800;
    letter-spacing: 6px;
}

/* stat boxes */
.stat-wrap {
    background: #130F00;
    border-top: 1px solid #2A2000;
    padding: 10px 16px 12px;
}
.stat-label {
    color: #6A5520;
    font-family: 'DM Mono', monospace;
    font-size: 0.62rem;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    text-align: center;
    margin-bottom: 4px;
}
.stat-value {
    color: #FFF8E0;
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.5rem;
    text-align: center;
    line-height: 1;
}
.stat-value.destaque { color: #F5A800; }

/* barra de progresso posse */
.barra-wrap { margin-top: 2px; }
.barra-bg {
    background: #2A2000;
    border-radius: 3px;
    height: 5px;
    width: 100%;
    overflow: hidden;
}
.barra-fill {
    height: 100%;
    border-radius: 3px;
    background: linear-gradient(90deg, #F5A800, #C88600);
}

/* alerta sem jogos */
.sem-jogos {
    text-align: center;
    padding: 60px 20px;
    color: #5A4500;
    font-family: 'DM Mono', monospace;
    font-size: 0.85rem;
    letter-spacing: 1px;
}

/* botão */
.stButton > button {
    background: #2A1F00 !important;
    color: #F5A800 !important;
    border: 1px solid #5A4000 !important;
    border-radius: 8px !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.75rem !important;
    letter-spacing: 1px !important;
    width: 100% !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: #3A2F00 !important;
    border-color: #F5A800 !important;
}

/* dataframe */
.stDataFrame { background: #1A1400 !important; }
</style>
""", unsafe_allow_html=True)

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown('<div class="gd-title">⚽ GDSCANNER ELITE</div>', unsafe_allow_html=True)
st.markdown(f'<div class="gd-subtitle">AO VIVO · ATUALIZADO ÀS {datetime.now().strftime("%H:%M:%S")}</div>', unsafe_allow_html=True)

# ── FILTROS (expander — funciona no mobile) ───────────────────────────────────
with st.expander("⚙️ Filtros & Configurações", expanded=False):
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        som_ativo  = st.toggle("🔔 Alerta Sonoro", value=False)
        minuto_min = st.slider("⏱ Minuto mínimo", 1, 15, 1)
        minuto_max = st.slider("⏱ Minuto máximo", 15, 45, 28)
    with col_f2:
        min_chutes = st.number_input("🥅 Mín. chutes a gol", 0, 20, 0)
        min_cantos = st.number_input("🚩 Mín. escanteios",   0, 20, 0)
        min_posse  = st.number_input("⚽ Mín. posse (%)",    0, 100, 0)

# ── API ───────────────────────────────────────────────────────────────────────
API_KEY = "7cd42ac471d260d53b033d7ec69ef53a"
HEADERS = {"x-apisports-key": API_KEY}

def get_stats(f_id):
    """Busca estatísticas de um fixture. Retorna dict com chaves h_* e a_*."""
    try:
        url = f"https://v3.football.api-sports.io/fixtures/statistics?fixture={f_id}"
        res = requests.get(url, headers=HEADERS, timeout=8).json().get("response", [])
        if len(res) < 2:
            return None
        d = {}
        for i, lado in enumerate(['h', 'a']):
            st_list = res[i]['statistics']
            def pegar(tipo, padrao=0):
                v = next((x['value'] for x in st_list if x['type'] == tipo), padrao)
                return v if v is not None else padrao
            # Chutes a gol (no alvo)
            d[f'{lado}_chg'] = int(pegar("Shots on Goal", 0))
            # Total finalizações
            d[f'{lado}_cht'] = int(pegar("Total Shots", 0))
            # Escanteios
            d[f'{lado}_esc'] = int(pegar("Corner Kicks", 0))
            # Posse
            posse = str(pegar("Ball Possession", "0%")).replace('%', '')
            d[f'{lado}_po'] = int(posse) if posse.isdigit() else 0
        return d
    except Exception:
        return None

def play_alert():
    st.components.v1.html(
        '<audio autoplay><source src="https://www.soundjay.com/buttons/sounds/button-3.mp3" type="audio/mp3"></audio>',
        height=0
    )

def registrar(jogo_nome, tempo, stats):
    entrada = {
        "Horário": datetime.now().strftime("%H:%M"),
        "Jogo": jogo_nome,
        "Min": tempo,
        "Chute Gol (C|V)": f"{stats['h_chg']} | {stats['a_chg']}",
        "Finalizações (C|V)": f"{stats['h_cht']} | {stats['a_cht']}",
        "Escanteios (C|V)": f"{stats['h_esc']} | {stats['a_esc']}",
        "Posse (C|V)": f"{stats['h_po']}% | {stats['a_po']}%",
        "Status": "⏳ Aguardando"
    }
    st.session_state['historico_entradas'].append(entrada)
    st.toast(f"✅ Entrada registrada: {jogo_nome}", icon="⚽")

# ── ABAS ──────────────────────────────────────────────────────────────────────
tab_scanner, tab_historico = st.tabs(["🚀 Scanner Ao Vivo", "📋 Histórico"])

with tab_scanner:
    try:
        res_live = requests.get(
            "https://v3.football.api-sports.io/fixtures?live=all",
            headers=HEADERS, timeout=10
        ).json().get("response", [])

        jogos_ok   = []
        tem_alerta = False

        for j in res_live:
            fixture = j.get("fixture", {})
            status  = fixture.get("status", {})
            teams   = j.get("teams",  {})
            goals   = j.get("goals",  {})
            league  = j.get("league", {})

            tempo = status.get("elapsed")
            gh    = goals.get("home") or 0
            ga    = goals.get("away") or 0

            # Filtro base: 0x0 dentro do intervalo configurado
            if tempo is None or not (minuto_min <= tempo <= minuto_max) or gh != 0 or ga != 0:
                continue

            stats = get_stats(fixture.get("id"))
            if stats is None:
                # Mostra mesmo sem stats (jogo muito recente)
                stats = {"h_chg":0,"a_chg":0,"h_cht":0,"a_cht":0,"h_esc":0,"a_esc":0,"h_po":50,"a_po":50}

            # Filtros de pressão da sidebar
            total_chg = stats['h_chg'] + stats['a_chg']
            total_cht = stats['h_cht'] + stats['a_cht']
            total_esc = stats['h_esc'] + stats['a_esc']
            max_po    = max(stats['h_po'], stats['a_po'])

            if total_chg < min_chutes or total_esc < min_cantos or max_po < min_posse:
                continue

            jogos_ok.append({
                "fid":   fixture.get("id"),
                "tempo": tempo,
                "home":  teams.get("home", {}).get("name", "?"),
                "away":  teams.get("away", {}).get("name", "?"),
                "liga":  league.get("name", ""),
                "pais":  league.get("country", ""),
                "stats": stats,
            })
            tem_alerta = True

        if tem_alerta and som_ativo:
            play_alert()

        # ── Contador ──────────────────────────────────────────────────────────
        col_info1, col_info2 = st.columns([1, 1])
        with col_info1:
            st.markdown(f"**{len(jogos_ok)}** jogo(s) nos critérios")
        with col_info2:
            st.markdown(f"<div style='text-align:right;color:#5A4500;font-size:0.75rem;font-family:monospace'>Total ao vivo: {len(res_live)}</div>", unsafe_allow_html=True)

        if not jogos_ok:
            st.markdown("""
                <div class="sem-jogos">
                    ⏳<br><br>
                    AGUARDANDO JOGOS NOS CRITÉRIOS<br>
                    <span style="color:#3A2800">0×0 · MINUTO CONFIGURADO · SEM GOLS</span>
                </div>
            """, unsafe_allow_html=True)

        # ── Cards ─────────────────────────────────────────────────────────────
        for jogo in jogos_ok:
            s    = jogo['stats']
            nome = f"{jogo['home']} vs {jogo['away']}"

            # Calcula largura da barra de posse
            po_h_pct = s['h_po']
            po_a_pct = s['a_po']

            st.markdown(f"""
            <div class="card">
                <div class="card-top">
                    <span class="card-liga">🏆 {jogo['liga']} · {jogo['pais']}</span>
                    <span class="card-tempo">⏱ {jogo['tempo']}'</span>
                </div>
                <div class="card-placar">
                    <span class="time-h">{jogo['home']}</span>
                    <span class="placar-vs">0 × 0</span>
                    <span class="time-a">{jogo['away']}</span>
                </div>
                <div class="stat-wrap">
                    <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:8px;margin-bottom:8px">
                        <div>
                            <div class="stat-label">🥅 Chute Gol</div>
                            <div class="stat-value destaque">{s['h_chg']} · {s['a_chg']}</div>
                        </div>
                        <div>
                            <div class="stat-label">🎯 Finalizações</div>
                            <div class="stat-value">{s['h_cht']} · {s['a_cht']}</div>
                        </div>
                        <div>
                            <div class="stat-label">🚩 Escanteios</div>
                            <div class="stat-value">{s['h_esc']} · {s['a_esc']}</div>
                        </div>
                        <div>
                            <div class="stat-label">⚽ Posse</div>
                            <div class="stat-value">{s['h_po']}% · {s['a_po']}%</div>
                        </div>
                    </div>
                    <div class="stat-label" style="margin-bottom:4px">POSSE DE BOLA</div>
                    <div style="display:flex;align-items:center;gap:8px">
                        <span style="font-family:'DM Mono',monospace;font-size:0.7rem;color:#C88600;min-width:32px">{s['h_po']}%</span>
                        <div class="barra-bg" style="flex:1">
                            <div class="barra-fill" style="width:{po_h_pct}%"></div>
                        </div>
                        <div class="barra-bg" style="flex:1;transform:scaleX(-1)">
                            <div class="barra-fill" style="width:{po_a_pct}%"></div>
                        </div>
                        <span style="font-family:'DM Mono',monospace;font-size:0.7rem;color:#C88600;min-width:32px;text-align:right">{s['a_po']}%</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if st.button(f"📥 REGISTRAR ENTRADA · {jogo['home'].upper()}", key=f"reg_{jogo['fid']}"):
                registrar(nome, jogo['tempo'], s)

    except Exception as e:
        st.error(f"Erro ao conectar com a API: {e}")

with tab_historico:
    st.subheader("📋 Entradas Registradas na Sessão")

    if st.session_state['historico_entradas']:
        df = pd.DataFrame(st.session_state['historico_entradas'])

        # Editor para marcar resultado
        df_editado = st.data_editor(
            df,
            column_config={
                "Status": st.column_config.SelectboxColumn(
                    "Status",
                    options=["⏳ Aguardando", "✅ Green", "❌ Red", "🔁 Empate"],
                    required=True,
                )
            },
            use_container_width=True,
            hide_index=True,
            key="editor_historico"
        )
        st.session_state['historico_entradas'] = df_editado.to_dict('records')

        col1, col2 = st.columns(2)
        with col1:
            greens = sum(1 for e in st.session_state['historico_entradas'] if e['Status'] == "✅ Green")
            reds   = sum(1 for e in st.session_state['historico_entradas'] if e['Status'] == "❌ Red")
            total  = len(st.session_state['historico_entradas'])
            taxa   = round(greens / total * 100) if total > 0 else 0
            st.metric("✅ Greens", greens)
            st.metric("❌ Reds",   reds)
            st.metric("📊 Taxa Green", f"{taxa}%")
        with col2:
            if st.button("🗑️ Limpar Histórico"):
                st.session_state['historico_entradas'] = []
                st.rerun()
    else:
        st.markdown("<div style='color:#5A4500;font-family:monospace;padding:40px 0;text-align:center'>Nenhuma entrada registrada nesta sessão.</div>", unsafe_allow_html=True)

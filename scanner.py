import streamlit as st
import requests
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

# 1. Configurações da Página
st.set_page_config(page_title="GDscanner Elite", layout="wide")
st_autorefresh(interval=30 * 1000, key="datarefresh")

st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #0e1117; }
    .main-title { color: #ffffff; font-size: 32px; font-weight: bold; text-align: center; margin-bottom: 10px; border-bottom: 2px solid #10b981; padding-bottom: 10px; }
    .card-verde { background-color: #064e3b; border-left: 8px solid #10b981; border-radius: 10px; padding: 15px; margin-bottom: 10px; }
    .card-amarelo { background-color: #451a03; border-left: 8px solid #fbbf24; border-radius: 10px; padding: 15px; margin-bottom: 10px; }
    .card-normal { background-color: #1c1f26; border-left: 8px solid #4b5563; border-radius: 10px; padding: 15px; margin-bottom: 10px; }
    .card-transmissao { background-color: #262730; border-radius: 8px; padding: 10px; margin-bottom: 5px; border: 1px solid #4b5563; }
    .badge { padding: 4px 12px; border-radius: 5px; font-weight: bold; color: white; margin-right: 10px; font-size: 12px; }
    .stat-label { color: #9ca3af; font-size: 11px; text-transform: uppercase; }
    .stat-value { font-size: 18px; font-weight: bold; color: white; }
    .tv-label { color: #10b981; font-weight: bold; font-size: 13px; }
    </style>
    """, unsafe_allow_html=True)

# --- CABEÇALHO ---
st.markdown('<div class="main-title">🛰️ GDscanner Elite</div>', unsafe_allow_html=True)

# --- SIDEBAR (CONFIGURAÇÕES) ---
st.sidebar.title("Configurações")
som_ativo = st.sidebar.toggle("🔔 Alerta Sonoro", value=False)

# Novo: Lista de transmissões (Simulação de base de dados para as principais ligas)
st.sidebar.divider()
st.sidebar.subheader("📺 Onde Assistir (Hoje)")

# Dicionário de exemplo (Pode ser expandido manualmente ou via API de TV futuramente)
transmissoes = [
    {"hora": "16:00", "jogo": "Real Madrid vs Barça", "canal": "Star+ / ESPN"},
    {"hora": "Ao Vivo", "jogo": "Man. City vs Arsenal", "canal": "ESPN"},
    {"hora": "18:30", "jogo": "Flamengo vs Palmeiras", "canal": "Premiere / Globo"}
]

for t in transmissoes:
    st.sidebar.markdown(f"""
        <div class="card-transmissao">
            <span style="color:#ffaa00; font-size:12px;">{t['hora']}</span><br>
            <span style="color:white; font-weight:bold;">{t['jogo']}</span><br>
            <span class="tv-label">📺 {t['canal']}</span>
        </div>
    """, unsafe_allow_html=True)

# --- FUNÇÕES ---
def play_alert():
    audio_url = "https://www.soundjay.com/buttons/sounds/button-3.mp3"
    audio_html = f'<audio autoplay><source src="{audio_url}" type="audio/mp3"></audio>'
    st.markdown(audio_html, unsafe_allow_html=True)

API_KEY = "7cd42ac471d260d53b033d7ec69ef53a"
HEADERS = {"x-apisports-key": API_KEY}

def get_stats(f_id):
    url = f"https://v3.football.api-sports.io/fixtures/statistics?fixture={f_id}"
    try:
        res = requests.get(url, headers=HEADERS).json().get("response", [])
        if len(res) >= 2:
            d = {}
            for i, s in enumerate(['h', 'a']):
                st_list = res[i]['statistics']
                ch_on = next((x['value'] for x in st_list if x['type'] == "Shots on Goal"), 0) or 0
                ch_off = next((x['value'] for x in st_list if x['type'] == "Shots off Goal"), 0) or 0
                d[f'{s}_ch'] = ch_on + ch_off
                d[f'{s}_esc'] = next((x['value'] for x in st_list if x['type'] == "Corner Kicks"), 0) or 0
                posse = next((x['value'] for x in st_list if x['type'] == "Ball Possession"), "0%")
                d[f'{s}_po'] = int(str(posse).replace('%','')) if posse else 0
            return d
    except: return None

# --- SCANNER DE PRESSÃO (LÓGICA PRINCIPAL) ---
try:
    res_live = requests.get("https://v3.football.api-sports.io/fixtures?live=all", headers=HEADERS).json().get("response", [])
    jogos_lista = []
    alerta_disparado = False

    for j in res_live:
        t = j["fixture"]["status"]["elapsed"]
        gh, ga = (j["goals"]["home"] or 0), (j["goals"]["away"] or 0)
        
        # Filtro GDscanner: 5' até 28' e placar 0x0
        if t is not None and 5 <= t <= 28 and gh == 0 and ga == 0:
            stats = get_stats(j["fixture"]["id"])
            if stats:
                total_ch = stats['h_ch'] + stats['a_ch']
                max_po = max(stats['h_po'], stats['a_po'])
                total_esc = stats['h_esc'] + stats['a_esc']

                # Verde: 3 chutes + 65% posse ou 4 escanteios
                if (total_ch >= 3 and max_po >= 65) or total_esc >= 4:
                    p, cl, lb, co = 2, "card-verde", "🔥 PRESSÃO ALTA", "#10b981"
                    alerta_disparado = True
                elif total_ch >= 1 or max_po >= 55:
                    p, cl, lb, co = 1, "card-amarelo", "⚠️ INTERESSANTE", "#fbbf24"
                else:
                    p, cl, lb, co = 0, "card-normal", "🔍 MONITORANDO", "#4b5563"
                
                jogos_lista.append({"p": p, "t": t, "h": j["teams"]["home"]["name"], "a": j["teams"]["away"]["name"], "s": stats, "cl": cl, "lb": lb, "co": co})

    if alerta_disparado and som_ativo:
        play_alert()

    jogos_lista.sort(key=lambda x: x['p'], reverse=True)

    if not jogos_lista:
        st.info("Buscando jogos no critério GDscanner (0x0 | 5' a 28')...")

    for jogo in jogos_lista:
        st.markdown(f"""
            <div class="{jogo['cl']}">
                <span class="badge" style="background-color: {jogo['co']}">{jogo['lb']}</span>
                <span style="color: #ffaa00; font-weight: bold;">⏱ {jogo['t']}'</span> 
                <span style="color:white; margin-left:10px; font-weight: bold;">{jogo['h']} vs {jogo['a']}</span>
            </div>
        """, unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f'<p class="stat-label">Chutes</p><p class="stat-value">{jogo["s"]["h_ch"]} | {jogo["s"]["a_ch"]}</p>', unsafe_allow_html=True)
        with c2: st.markdown(f'<p class="stat-label">Cantos</p><p class="stat-value">{jogo["s"]["h_esc"]} | {jogo["s"]["a_esc"]}</p>', unsafe_allow_html=True)
        with c3: st.markdown(f'<p class="stat-label">Posse</p><p class="stat-value">{jogo["s"]["h_po"]}% | {jogo["s"]["a_po"]}%</p>', unsafe_allow_html=True)
        st.divider()

except Exception as e:
    st.error("Conectando à API...")

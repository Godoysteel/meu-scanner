import streamlit as st
import requests
from streamlit_autorefresh import st_autorefresh

# 1. Configurações da Página
st.set_page_config(page_title="PRO Scanner Elite", layout="wide")

# Atualiza sozinho a cada 30 segundos
st_autorefresh(interval=30 * 1000, key="datarefresh")

st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #0e1117; }
    .card-verde { background-color: #064e3b; border-left: 8px solid #10b981; border-radius: 10px; padding: 15px; margin-bottom: 10px; }
    .card-amarelo { background-color: #451a03; border-left: 8px solid #fbbf24; border-radius: 10px; padding: 15px; margin-bottom: 10px; }
    .card-normal { background-color: #1c1f26; border-left: 8px solid #4b5563; border-radius: 10px; padding: 15px; margin-bottom: 10px; }
    .badge { padding: 4px 12px; border-radius: 5px; font-weight: bold; color: white; margin-right: 10px; font-size: 12px; }
    .stat-label { color: #9ca3af; font-size: 11px; text-transform: uppercase; margin-bottom: 2px; }
    .stat-value { font-size: 18px; font-weight: bold; color: white; margin-top: 0px; }
    </style>
    """, unsafe_allow_html=True)

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
                # Soma chutes no alvo + fora do alvo
                ch_on = next((x['value'] for x in st_list if x['type'] == "Shots on Goal"), 0) or 0
                ch_off = next((x['value'] for x in st_list if x['type'] == "Shots off Goal"), 0) or 0
                d[f'{s}_ch'] = ch_on + ch_off
                d[f'{s}_esc'] = next((x['value'] for x in st_list if x['type'] == "Corner Kicks"), 0) or 0
                posse = next((x['value'] for x in st_list if x['type'] == "Ball Possession"), "0%")
                d[f'{s}_po'] = int(str(posse).replace('%','')) if posse else 0
            return d
    except: return None

st.title("🛰️ Monitor Elite: 0x0 até 28'")
st.caption("Auto-refresh ativo | Verde: Pressão confirmada")

try:
    res_live = requests.get("https://v3.football.api-sports.io/fixtures?live=all", headers=HEADERS).json().get("response", [])
    jogos_lista = []

    for j in res_live:
        t = j["fixture"]["status"]["elapsed"]
        gh, ga = (j["goals"]["home"] or 0), (j["goals"]["away"] or 0)
        
        # Monitora dos 5' aos 28' em 0x0
        if t is not None and 5 <= t <= 28 and gh == 0 and ga == 0:
            stats = get_stats(j["fixture"]["id"])
            if stats:
                total_ch = stats['h_ch'] + stats['a_ch']
                max_po = max(stats['h_po'], stats['a_po'])
                total_esc = stats['h_esc'] + stats['a_esc']

                # CRITÉRIO VERDE: Sua regra de posse + chutes ou pressão por escanteios
                if (total_ch >= 3 and max_po >= 65) or total_esc >= 4:
                    p, cl, lb, co = 2, "card-verde", "🔥 PRESSÃO ALTA", "#10b981"
                elif total_ch >= 1 or max_po >= 55:
                    p, cl, lb, co = 1, "card-amarelo", "⚠️ FICANDO BOM", "#fbbf24"
                else:
                    p, cl, lb, co = 0, "card-normal", "🔍 MONITORANDO", "#4b5563"
                
                jogos_lista.append({"p": p, "t": t, "h": j["teams"]["home"]["name"], "a": j["teams"]["away"]["name"], "s": stats, "cl": cl, "lb": lb, "co": co})

    jogos_lista.sort(key=lambda x: x['p'], reverse=True)

    for jogo in jogos_lista:
        st.markdown(f"""
            <div class="{jogo['cl']}">
                <span class="badge" style="background-color: {jogo['co']}">{jogo['lb']}</span>
                <span style="color: #ffaa00; font-weight: bold;">⏱ {jogo['t']}'</span> 
                <span style="font-size: 16px; margin-left: 10px; color: white;">{jogo['h']} vs {jogo['a']}</span>
            </div>
        """, unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns(3)
        with c1: 
            st.markdown(f'<p class="stat-label">Chutes Totais</p><p class="stat-value">{jogo["s"]["h_ch"]} | {jogo["s"]["a_ch"]}</p>', unsafe_allow_html=True)
        with c2: 
            st.markdown(f'<p class="stat-label">Escanteios</p><p class="stat-value">{jogo["s"]["h_esc"]} | {jogo["s"]["a_esc"]}</p>', unsafe_allow_html=True)
        with c3: 
            st.markdown(f'<p class="stat-label">Posse de Bola</p><p class="stat-value">{jogo["s"]["h_po"]}% | {jogo["s"]["a_po"]}%</p>', unsafe_allow_html=True)
        st.divider()

except Exception as e:
    st.error("Erro ao carregar dados da API. Aguarde a próxima atualização.")

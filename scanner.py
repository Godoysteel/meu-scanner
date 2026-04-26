import streamlit as st
import requests
from streamlit_autorefresh import st_autorefresh

# 1. Configurações de Interface
st.set_page_config(page_title="PRO Scanner Live", layout="wide")

# Atualiza automaticamente a cada 30 segundos
st_autorefresh(interval=30 * 1000, key="datarefresh")

st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #0e1117; }
    .card-verde { background-color: #064e3b; border-left: 8px solid #10b981; border-radius: 10px; padding: 15px; margin-bottom: 10px; }
    .card-amarelo { background-color: #451a03; border-left: 8px solid #fbbf24; border-radius: 10px; padding: 15px; margin-bottom: 10px; }
    .card-normal { background-color: #1c1f26; border-left: 8px solid #4b5563; border-radius: 10px; padding: 15px; margin-bottom: 10px; }
    .badge { padding: 4px 12px; border-radius: 5px; font-weight: bold; color: white; margin-right: 10px; font-size: 12px; }
    .stat-label { color: #9ca3af; font-size: 11px; text-transform: uppercase; }
    .stat-value { font-size: 18px; font-weight: bold; color: white; }
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
                ch_on = next((x['value'] for x in st_list if x['type'] == "Shots on Goal"), 0) or 0
                ch_off = next((x['value'] for x in st_list if x['type'] == "Shots off Goal"), 0) or 0
                d[f'{s}_ch_total'] = ch_on + ch_off
                d[f'{s}_ch_alvo'] = ch_on
                posse_raw = next((x['value'] for x in st_list if x['type'] == "Ball Possession"), "0%")
                d[f'{s}_po'] = int(str(posse_raw).replace('%','')) if posse_raw else 0
            return d
    except: return None

# --- EXECUÇÃO AUTOMÁTICA ---
st.title("🛰️ Monitor de Pressão em Tempo Real")
st.caption("Atualização automática ativa (30s) | Filtro: 0x0 até 28'")

with st.spinner('Escaneando mercado...'):
    res_live = requests.get("https://v3.football.api-sports.io/fixtures?live=all", headers=HEADERS).json().get("response", [])
    jogos_lista = []
    
    for j in res_live:
        t = j["fixture"]["status"]["elapsed"]
        gh = j["goals"]["home"] if j["goals"]["home"] is not None else 0
        ga = j["goals"]["away"] if j["goals"]["away"] is not None else 0
        
        if t is not None and t <= 28 and gh == 0 and ga == 0:
            stats = get_stats(j["fixture"]["id"])
            if stats:
                total_chutes = stats['h_ch_total'] + stats['a_ch_total']
                max_posse = max(stats['h_po'], stats['a_po'])
                
                if total_chutes >= 4 or max_posse >= 68:
                    prio, classe, label, cor = 2, "card-verde", "🔥 PRESSÃO ALTA", "#10b981"
                elif total_chutes >= 2 or max_posse >= 58:
                    prio, classe, label, cor = 1, "card-amarelo", "⚠️ FICANDO BOM", "#fbbf24"
                else:
                    prio, classe, label, cor = 0, "card-normal", "🔍 OBSERVANDO", "#4b5563"
                
                jogos_lista.append({
                    "prio": prio, "tempo": t, "home": j["teams"]["home"]["name"],
                    "away": j["teams"]["away"]["name"], "stats": stats, "classe": classe, 
                    "label": label, "cor": cor
                })

    jogos_lista.sort(key=lambda x: x['prio'], reverse=True)

    for jogo in jogos_lista:
        st.markdown(f"""
            <div class="{jogo['classe']}">
                <span class="badge" style="background-color: {jogo['cor']}">{jogo['label']}</span>
                <span style="color: #ffaa00; font-weight: bold;">⏱ {jogo['tempo']}'</span> 
                <span style="font-size: 16px; margin-left: 10px; color: white;">{jogo['home']} vs {jogo['away']}</span>
            </div>
        """, unsafe_allow_html=True)
        
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.markdown(f'<p class="stat-label">Chutes {jogo["home"]}</p><p class="stat-value">{jogo["stats"]["h_ch_total"]}</p>', unsafe_allow_html=True)
        with c2: st.markdown(f'<p class="stat-label">Posse {jogo["home"]}</p><p class="stat-value">{jogo["stats"]["h_po"]}%</p>', unsafe_allow_html=True)
        with c3: st.markdown(f'<p class="stat-label">Chutes {jogo["away"]}</p><p class="stat-value">{jogo["stats"]["a_ch_total"]}</p>', unsafe_allow_html=True)
        with c4: st.markdown(f'<p class="stat-label">Posse {jogo["away"]}</p><p class="stat-value">{jogo["stats"]["a_po"]}%</p>', unsafe_allow_html=True)

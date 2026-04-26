import streamlit as st
import requests
import pandas as pd

# 1. Configurações de Estilo e Layout
st.set_page_config(page_title="PRO Scanner - Brasilcana", layout="wide", initial_sidebar_state="collapsed")

# CSS para interface profissional (Dark Mode e Cards)
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #0e1117; }
    .main-card {
        background-color: #1c1f26;
        border-radius: 15px;
        padding: 20px;
        border-left: 5px solid #00ffcc;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    .time-badge {
        background-color: #ffaa00;
        color: black;
        padding: 2px 8px;
        border-radius: 5px;
        font-weight: bold;
        font-size: 14px;
    }
    .stat-label { color: #808495; font-size: 12px; text-transform: uppercase; }
    .stat-value { font-size: 22px; font-weight: bold; color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

API_KEY = "7cd42ac471d260d53b033d7ec69ef53a"
HEADERS = {"x-apisports-key": API_KEY}

def get_stats(f_id):
    url = f"https://v3.football.api-sports.io/fixtures/statistics?fixture={f_id}"
    try:
        res = requests.get(url, headers=HEADERS).json().get("response", [])
        if len(res) >= 2:
            data = {}
            for i, side in enumerate(['home', 'away']):
                s_list = res[i]['statistics']
                data[f'{side}_chutes'] = next((s['value'] for s in s_list if s['type'] == "Shots on Goal"), 0) or 0
                data[f'{side}_posse'] = next((s['value'] for s in s_list if s['type'] == "Ball Possession"), "0%") or "0%"
            return data
    except: return None
    return None

# Título e Header
st.title("⚽ PRO Scanner: Estratégia Late 0x0")
st.caption("Filtro Ativo: Empates em 0x0 | Tempo: 0' até 28' | Atualização em Tempo Real")

if st.button('🔄 SCANNEAR MERCADO AGORA', use_container_width=True):
    with st.spinner('Analisando ligas ao vivo...'):
        url_live = "https://v3.football.api-sports.io/fixtures?live=all"
        todos_jogos = requests.get(url_live, headers=HEADERS).json().get("response", [])
        
        encontrados = 0
        
        for j in todos_jogos:
            tempo = j["fixture"]["status"]["elapsed"]
            gh = j["goals"]["home"] or 0
            ga = j["goals"]["away"] or 0
            
            if tempo is not None and tempo <= 28 and gh == 0 and ga == 0:
                encontrados += 1
                f_id = j["fixture"]["id"]
                home = j["teams"]["home"]["name"]
                away = j["teams"]["away"]["name"]
                stats = get_stats(f_id)
                
                # Renderização do Card Profissional
                st.markdown(f"""
                    <div class="main-card">
                        <span class="time-badge">⏱ {tempo}'</span>
                        <span style="margin-left: 15px; font-size: 18px; font-weight: 500;">{home} vs {away}</span>
                    </div>
                """, unsafe_allow_html=True)
                
                col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
                
                if stats:
                    with col1:
                        st.markdown(f'<p class="stat-label">Chutes {home}</p>', unsafe_allow_html=True)
                        st.markdown(f'<p class="stat-value">{stats["home_chutes"]}</p>', unsafe_allow_html=True)
                    with col2:
                        st.markdown(f'<p class="stat-label">Posse {home}</p>', unsafe_allow_html=True)
                        st.markdown(f'<p class="stat-value">{stats["home_posse"]}</p>', unsafe_allow_html=True)
                    with col3:
                        st.markdown(f'<p class="stat-label">Chutes {away}</p>', unsafe_allow_html=True)
                        st.markdown(f'<p class="stat-value">{stats["away_chutes"]}</p>', unsafe_allow_html=True)
                    with col4:
                        st.markdown(f'<p class="stat-label">Posse {away}</p>', unsafe_allow_html=True)
                        st.markdown(f'<p class="stat-value">{stats["away_posse"]}</p>', unsafe_allow_html=True)
                
                st.divider()

        if encontrados == 0:
            st.warning("🔍 Nenhum jogo encontrado nos critérios de 0x0 até 28 minutos no momento.")

st.markdown("---")
st.info("💡 Dica: Jogos com mais de 3 chutes a gol antes dos 25' indicam alta tendência de golo HT.")
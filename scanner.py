import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# 1. Configuração de Estilo (Mantendo o padrão Elite que você gosta)
st.set_page_config(page_title="GDscanner Desvantagem", layout="wide")

# Lógica para buscar eventos (Cartões Vermelhos)
def verificar_vermelhos(f_id, headers):
    try:
        url = f"https://v3.football.api-sports.io/fixtures/events?fixture={f_id}&type=Card"
        events = requests.get(url, headers=headers, timeout=5).json().get("response", [])
        vermelhos_h = sum(1 for e in events if e['detail'] == 'Red Card' and e['team']['id'] == team_h_id)
        vermelhos_a = sum(1 for e in events if e['detail'] == 'Red Card' and e['team']['id'] == team_a_id)
        return vermelhos_h, vermelhos_a
    except:
        return 0, 0

# --- INTERFACE ---
st.markdown('<h1 style="color:#F5A800; text-align:center;">⚽ SCANNER DE DESVANTAGEM</h1>', unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ Filtros Estratégicos")
    min_posse_dominio = st.slider("Mínimo Posse Domínio (%)", 60, 80, 70)
    tempo_max = st.slider("Minuto Máximo", 10, 90, 35)

# --- LÓGICA DE BUSCA ---
API_KEY = "7cd42ac471d260d53b033d7ec69ef53a"
HEADERS = {"x-apisports-key": API_KEY}

try:
    res = requests.get("https://v3.football.api-sports.io/fixtures?live=all", headers=HEADERS).json().get("response", [])
    
    for j in res:
        fixture_id = j['fixture']['id']
        tempo = j['fixture']['status']['elapsed']
        gh, ga = (j['goals']['home'] or 0), (j['goals']['away'] or 0)
        
        # FILTRO: Empatado + Tempo de Início
        if tempo and tempo <= tempo_max and gh == ga:
            
            # Aqui buscamos as estatísticas para medir o "Desparelho"
            # (Usando a função get_stats que já validamos antes)
            s = get_stats(fixture_id) # Considere a função get_stats implementada
            
            if s:
                dominio_h = s['h_po'] >= min_posse_dominio or s['h_cht'] >= (s['a_cht'] * 3 if s['a_cht'] > 0 else 5)
                dominio_a = s['a_po'] >= min_posse_dominio or s['a_cht'] >= (s['h_cht'] * 3 if s['h_cht'] > 0 else 5)
                
                # Se houver domínio ou vermelho (vermelho exige chamada extra opcional)
                if dominio_h or dominio_a:
                    cor_card = "#FF4B4B" if (dominio_h or dominio_a) else "#10b981"
                    
                    st.markdown(f"""
                    <div style="background:#1a1a1a; border-left:8px solid {cor_card}; padding:15px; border-radius:10px; margin-bottom:10px;">
                        <h3 style="margin:0; color:white;">🔥 JOGO DESPARELHO: {j['teams']['home']['name']} vs {j['teams']['away']['name']}</h3>
                        <p style="color:#F5A800; font-weight:bold;">⏱ {tempo}' | Placar: {gh}x{ga}</p>
                        <p style="color:white; font-size:14px;">Posse: {s['h_po']}% vs {s['a_po']}% | Chutes: {s['h_cht']} vs {s['a_cht']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"REGISTRAR ENTRADA: {j['teams']['home']['name']}", key=f"btn_{fixture_id}"):
                        st.toast("Oportunidade salva no histórico!")

except Exception as e:
    st.error(f"Erro ao processar scanner: {e}")

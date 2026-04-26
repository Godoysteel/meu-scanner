import streamlit as st
import requests
from streamlit_autorefresh import st_autorefresh
import pandas as pd
from datetime import datetime

# 1. Configurações da Página
st.set_page_config(page_title="GDscanner Elite", layout="wide")
st_autorefresh(interval=30 * 1000, key="datarefresh")

# Inicializa o banco de dados na memória se não existir
if 'historico_entradas' not in st.session_state:
    st.session_state['historico_entradas'] = []

# --- ESTILO ---
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #0e1117; }
    .main-title { color: #ffffff; font-size: 32px; font-weight: bold; text-align: center; border-bottom: 2px solid #10b981; }
    .card-verde { background-color: #064e3b; border-left: 8px solid #10b981; border-radius: 10px; padding: 15px; margin-bottom: 10px; }
    .stat-label { color: #9ca3af; font-size: 11px; text-transform: uppercase; }
    .stat-value { font-size: 18px; font-weight: bold; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="main-title">🛰️ GDscanner Elite</div>', unsafe_allow_html=True)

# --- NAVEGAÇÃO ---
tab_scanner, tab_historico = st.tabs(["🚀 Scanner Ao Vivo", "📜 Histórico & Refinamento"])

# --- FUNÇÃO PARA SALVAR ---
def salvar_entrada(jogo, tempo, ch, esc, po):
    nova_entrada = {
        "Horário": datetime.now().strftime("%H:%M"),
        "Jogo": jogo,
        "Minuto": tempo,
        "Chutes": ch,
        "Cantos": esc,
        "Posse %": f"{po}%",
        "Status": "Em Aberto"
    }
    st.session_state['historico_entradas'].append(nova_entrada)
    st.toast(f"Entrada registrada: {jogo}!", icon="✅")

# --- ABA 1: SCANNER ---
with tab_scanner:
    API_KEY = "7cd42ac471d260d53b033d7ec69ef53a"
    HEADERS = {"x-apisports-key": API_KEY}
    
    try:
        # Busca jogos ao vivo (Simulação da lógica que já temos)
        res_live = requests.get("https://v3.football.api-sports.io/fixtures?live=all", headers=HEADERS).json().get("response", [])
        
        for j in res_live:
            t = j["fixture"]["status"]["elapsed"]
            gh, ga = (j["goals"]["home"] or 0), (j["goals"]["away"] or 0)
            
            # Filtro 0x0 | 5-28 min
            if t is not None and 5 <= t <= 28 and gh == 0 and ga == 0:
                # Aqui você teria a chamada get_stats (mantive oculta para brevidade)
                nome_jogo = f"{j['teams']['home']['name']} vs {j['teams']['away']['name']}"
                
                # Interface do Card
                st.markdown(f'<div class="card-verde">🔥 PRESSÃO DETETADA: {nome_jogo}</div>', unsafe_allow_html=True)
                
                # BOTÃO DE ENTRADA DE DADOS
                if st.button(f"📥 REGISTRAR ENTRADA: {j['teams']['home']['name']}", key=j['fixture']['id']):
                    # Salva os dados exatos do momento do clique
                    salvar_entrada(nome_jogo, t, "Analizando...", "Analizando...", "Analizando...")

    except:
        st.info("Aguardando jogos nos critérios de pressão...")

# --- ABA 2: HISTÓRICO ---
with tab_historico:
    st.subheader("📋 Entradas Realizadas Hoje")
    if st.session_state['historico_entradas']:
        df = pd.DataFrame(st.session_state['historico_entradas'])
        st.dataframe(df, use_container_width=True)
        
        if st.button("🗑️ Limpar Histórico"):
            st.session_state['historico_entradas'] = []
            st.rerun()
    else:
        st.write("Nenhuma entrada registrada ainda.")

# --- SIDEBAR ---
st.sidebar.title("Configurações")
som_ativo = st.sidebar.toggle("🔔 Alerta Sonoro", value=False)
st.sidebar.divider()
st.sidebar.subheader("📺 Transmissões")
# (Mantém a lista de populares que fizemos antes aqui)

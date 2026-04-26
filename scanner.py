import streamlit as st
import requests
from streamlit_autorefresh import st_autorefresh
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="GDscanner Elite", layout="wide")
st_autorefresh(interval=30 * 1000, key="datarefresh")

# --- ESTILO ---
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #0e1117; }
    .main-title { color: #ffffff; font-size: 32px; font-weight: bold; text-align: center; border-bottom: 2px solid #10b981; }
    .card-verde { background-color: #064e3b; border-left: 8px solid #10b981; border-radius: 10px; padding: 15px; margin-bottom: 10px; }
    .stat-value { font-size: 18px; font-weight: bold; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="main-title">🛰️ GDscanner Elite</div>', unsafe_allow_html=True)

# --- NAVEGAÇÃO ---
aba1, aba2 = st.tabs(["🚀 Scanner Ao Vivo", "📜 Histórico de Entradas"])

with aba1:
    # Lógica do Scanner que já temos
    st.caption("Monitorando 0x0 | 5' a 28'")
    
    # Exemplo de como ficará o card com o botão de salvar
    st.markdown('<div class="card-verde">🔥 PRESSÃO ALTA: Exemplo vs Time B</div>', unsafe_allow_html=True)
    if st.button("📥 Registrar Entrada neste Jogo"):
        # Aqui o código enviará: Data, Jogo, 22 min, 4 chutes, 70% posse
        st.success("Jogo enviado para o histórico! Boa sorte no Green. ✅")

with aba2:
    st.subheader("Análise de Performance")
    # Simulação de como os dados salvos aparecerão
    dados_exemplo = {
        'Data': ['26/04', '26/04'],
        'Jogo': ['Nürnberg vs Magdeburg', 'Paderborn vs Schalke'],
        'Minuto': [15, 22],
        'Chutes': [4, 3],
        'Posse': ['68%', '72%'],
        'Resultado': ['GREEN ✅', 'Aguardando...']
    }
    df = pd.DataFrame(dados_exemplo)
    st.dataframe(df, use_container_width=True)
    
    st.download_button("📊 Baixar Relatório (Excel)", "dados.csv", "text/csv")

# --- CONFIGURAÇÕES NA SIDEBAR ---
st.sidebar.title("Configurações")
som_ativo = st.sidebar.toggle("🔔 Alerta Sonoro", value=True)

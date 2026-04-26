import streamlit as st
import requests
from streamlit_autorefresh import st_autorefresh
import pandas as pd
from datetime import datetime

# 1. Configurações da Página
st.set_page_config(page_title="GDscanner Elite", layout="wide")
# Auto-refresh a cada 30 segundos
st_autorefresh(interval=30 * 1000, key="datarefresh")

# Inicializa o banco de dados na memória se não existir (para o histórico de sessão)
if 'historico_entradas' not in st.session_state:
    st.session_state['historico_entradas'] = []

# --- ESTILO CSS REVISADO PARA MÁXIMA VISIBILIDADE ---
st.markdown("""
    <style>
    /* Fundo da aplicação */
    [data-testid="stAppViewContainer"] { background-color: #0e1117; }
    
    /* Título Principal */
    .main-title { color: #ffffff; font-size: 32px; font-weight: bold; text-align: center; border-bottom: 2px solid #10b981; padding-bottom: 10px; margin-bottom: 20px; }
    
    /* Contêiner do Card do Jogo */
    .card-jogo { 
        border: 1px solid #2d3748; 
        border-radius: 12px; 
        padding: 15px; 
        margin-bottom: 15px; 
        background-color: #1a202c;
    }

    /* Barra de Alerta Verde - Correção de Contraste */
    .alerta-pressao { 
        background-color: #064e3b; /* Verde escuro de fundo */
        border-left: 8px solid #10b981; /* Borda verde viva */
        border-radius: 8px; 
        padding: 10px; 
        margin-bottom: 10px; 
    }
    
    /* Texto do Time - Branco Puro e Negrito */
    .team-names-txt { 
        color: #ffffff !important; /* Branco puro forçado */
        font-size: 18px; 
        font-weight: bold !important; /* Negrito forçado */
        margin-bottom: 0px;
    }
    
    /* Tempo de Jogo */
    .tempo-txt { 
        color: #ffaa00; 
        font-weight: bold; 
        margin-left: 10px;
    }

    /* Estilo das Estatísticas */
    .stat-box { 
        text-align: center; 
        padding: 5px; 
    }
    .stat-label { 
        color: #a0aec0; 
        font-size: 12px; 
        text-transform: uppercase; 
        letter-spacing: 1px;
        margin-bottom: 2px;
    }
    .stat-value { 
        color: #ffffff; 
        font-size: 20px; 
        font-weight: bold; 
        margin-top: 0px;
    }

    /* Estilo do Botão de Registro */
    .stButton > button {
        background-color: #ffffff !important;
        color: #0e1117 !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        width: 100% !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CABEÇALHO DO APP ---
st.markdown('<div class="main-title">🛰️ GDscanner Elite</div>', unsafe_allow_html=True)

# --- CONFIGURAÇÕES NA SIDEBAR ---
st.sidebar.title("🛠️ Painel")
som_ativo = st.sidebar.toggle("🔔 Alerta Sonoro", value=False)
st.sidebar.divider()
st.sidebar.subheader("📺 Transmissões")
# Adicione a lista de populares que fizemos antes aqui se desejar

# --- LÓGICA DE ÁUDIO ---
def play_alert():
    audio_url = "https://www.soundjay.com/buttons/sounds/button-3.mp3"
    audio_html = f'<audio autoplay><source src="{audio_url}" type="audio/mp3"></audio>'
    st.components.v1.html(audio_html, height=0)

# --- LÓGICA DE REGISTRO DE DADOS ---
def registrar_entrada_historico(jogo, tempo, ch_h, ch_a, esc_h, esc_a, po_h, po_a):
    hora_atual = datetime.now().strftime("%H:%M")
    entrada = {
        "Horário": hora_atual,
        "Jogo": jogo,
        "Minuto": tempo,
        "Chutes (C|V)": f"{ch_h} | {ch_a}",
        "Cantos (C|V)": f"{esc_h} | {esc_a}",
        "Posse (C|V)": f"{po_h}% | {po_a}%",
        "Status": "Aguardando ✅/❌"
    }
    st.session_state['historico_entradas'].append(entrada)
    st.toast(f"Entrada registrada para {jogo}!", icon="✅")

# --- CONEXÃO API ---
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
                # Soma chutes no alvo + fora
                ch_on = next((x['value'] for x in st_list if x['type'] == "Shots on Goal"), 0) or 0
                ch_off = next((x['value'] for x in st_list if x['type'] == "Shots off Goal"), 0) or 0
                d[f'{s}_ch'] = ch_on + ch_off
                # Cantos
                d[f'{s}_esc'] = next((x['value'] for x in st_list if x['type'] == "Corner Kicks"), 0) or 0
                # Posse de bola
                posse = next((x['value'] for x in st_list if x['type'] == "Ball Possession"), "0%")
                d[f'{s}_po'] = int(str(posse).replace('%','')) if posse else 0
            return d
    except Exception: return None

# --- NAVEGAÇÃO POR ABAS ---
tab_scanner, tab_historico = st.tabs(["🚀 Scanner Ao Vivo", "📜 Histórico & Refinamento"])

with tab_scanner:
    try:
        # Busca jogos ao vivo
        res_live = requests.get("https://v3.football.api-sports.io/fixtures?live=all", headers=HEADERS).json().get("response", [])
        jogos_detectados = []
        alerta_verde = False

        for j in res_live:
            t = j["fixture"]["status"]["elapsed"]
            gh, ga = (j["goals"]["home"] or 0), (j["goals"]["away"] or 0)
            
            # Filtro GDscanner: 0x0 | 5' a 28'
            if t is not None and 5 <= t <= 28 and gh == 0 and ga == 0:
                stats = get_stats(j["fixture"]["id"])
                if stats:
                    # Regras de prioridade
                    total_ch = stats['h_ch'] + stats['a_ch']
                    max_po = max(stats['h_po'], stats['a_po'])
                    total_esc = stats['h_esc'] + stats['a_esc']

                    # Verde: 3 chutes + 65% posse OU 4 escanteios
                    if (total_ch >= 3 and max_po >= 65) or total_esc >= 4:
                        jogos_detectados.append({"id": j["fixture"]["id"], "t": t, "h": j["teams"]["home"]["name"], "a": j["teams"]["away"]["name"], "s": stats})
                        alerta_verde = True

        # Som de Alerta se houver jogos verdes
        if alerta_verde and som_ativo:
            play_alert()

        # Exibição dos Jogos
        if not jogos_detectados:
            st.info("Aguardando jogos nos critérios de pressão (0x0 | 5' a 28')...")

        for jogo in jogos_detectados:
            # Novo Card do Jogo
            with st.container():
                st.markdown(f"""
                    <div class="card-jogo">
                        <div class="alerta-pressao">
                            <span class="team-names-txt">🔥 {jogo['h']} vs {jogo['a']}</span>
                            <span class="tempo-txt">⏱ {jogo['t']}'</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Exibição das Estatísticas em Colunas
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.markdown(f'<div class="stat-box"><p class="stat-label">Chutes (C|V)</p><p class="stat-value">{jogo["s"]["h_ch"]} | {jogo["s"]["a_ch"]}</p></div>', unsafe_allow_html=True)
                with c2:
                    st.markdown(f'<div class="stat-box"><p class="stat-label">Cantos (C|V)</p><p class="stat-value">{jogo["s"]["h_esc"]} | {jogo["s"]["a_esc"]}</p></div>', unsafe_allow_html=True)
                with c3:
                    st.markdown(f'<div class="stat-box"><p class="stat-label">Posse (C|V)</p><p class="stat-value">{jogo["s"]["h_po"]}% | {jogo["s"]["a_po"]}%</p></div>', unsafe_allow_html=True)
                
                # Espaço antes do botão
                st.markdown("<br>", unsafe_allow_html=True)
                
                # BOTÃO DE REGISTRO COM KEY ÚNICA
                if st.button(f"📥 REGISTRAR ENTRADA: {jogo['h']}", key=f"reg_{jogo['id']}"):
                    registrar_entrada_historico(
                        f"{jogo['h']} vs {jogo['a']}", jogo['t'],
                        jogo['s']['h_ch'], jogo['s']['a_ch'],
                        jogo['s']['esc_h'], jogo['s']['esc_a'],
                        jogo['s']['po_h'], jogo['s']['po_a']
                    )

    except Exception as e:
        st.error("Conectando ao sinal da API...")

with tab_historico:
    st.subheader("📋 Entradas Realizadas na Sessão")
    if st.session_state['historico_entradas']:
        df = pd.DataFrame(st.session_state['historico_entradas'])
        st.dataframe(df, use_container_width=True)
        
        if st.button("🗑️ Limpar Histórico de Sessão"):
            st.session_state['historico_entradas'] = []
            st.rerun()
    else:
        st.write("Nenhuma entrada registrada nesta sessão.")

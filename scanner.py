import streamlit as st
import requests

# 1. Configurações de Estilo
st.set_page_config(page_title="PRO Scanner Elite", layout="wide")

st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #0e1117; }
    .card-verde { background-color: #064e3b; border-left: 8px solid #10b981; border-radius: 10px; padding: 15px; margin-bottom: 10px; }
    .card-amarelo { background-color: #451a03; border-left: 8px solid #fbbf24; border-radius: 10px; padding: 15px; margin-bottom: 10px; }
    .card-normal { background-color: #1c1f26; border-left: 8px solid #4b5563; border-radius: 10px; padding: 15px; margin-bottom: 10px; }
    .badge { padding: 2px 10px; border-radius: 5px; font-weight: bold; color: black; margin-right: 10px; }
    .stat-box { background: rgba(255,255,255,0.05); padding: 10px; border-radius: 5px; text-align: center; }
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
                d[f'{s}_ch'] = next((x['value'] for x in st_list if x['type'] == "Shots on Goal"), 0) or 0
                posse_str = next((x['value'] for x in st_list if x['type'] == "Ball Possession"), "0%") or "0%"
                d[f'{s}_po'] = int(str(posse_str).replace('%',''))
            return d
    except: return None

st.title("🏆 PRO Scanner Elite: 0x0 Intelligence")

if st.button('🔄 SCANNEAR AGORA', use_container_width=True):
    with st.spinner('Analisando comportamento dos times...'):
        res_live = requests.get("https://v3.football.api-sports.io/fixtures?live=all", headers=HEADERS).json().get("response", [])
        
        jogos_lista = []
        for j in res_live:
            t = j["fixture"]["status"]["elapsed"]
            gh, ga = (j["goals"]["home"] or 0), (j["goals"]["away"] or 0)
            
            if t is not None and t <= 28 and gh == 0 and ga == 0:
                stats = get_stats(j["fixture"]["id"])
                if stats:
                    # Lógica de Classificação
                    total_chutes = stats['h_ch'] + stats['a_ch']
                    max_posse = max(stats['h_po'], stats['a_po'])
                    
                    prioridade = 0 # 0=Cinza, 1=Amarelo, 2=Verde
                    classe = "card-normal"
                    label = "MONITORANDO"
                    cor_badge = "#9ca3af"

                    if total_chutes >= 3 or max_posse >= 65:
                        prioridade = 2
                        classe = "card-verde"
                        label = "🔥 ENTRADA CONFIRMADA"
                        cor_badge = "#10b981"
                    elif total_chutes >= 1 or max_posse >= 58:
                        prioridade = 1
                        classe = "card-amarelo"
                        label = "⚠️ INTERESSANTE"
                        cor_badge = "#fbbf24"
                    
                    jogos_lista.append({
                        "prio": prioridade, "tempo": t, "home": j["teams"]["home"]["name"],
                        "away": j["teams"]["away"]["name"], "stats": stats, "classe": classe, 
                        "label": label, "cor": cor_badge
                    })

        # ORDENAR: Verdes primeiro, depois Amarelos
        jogos_lista.sort(key=lambda x: x['prio'], reverse=True)

        for jogo in jogos_lista:
            st.markdown(f"""
                <div class="{jogo['classe']}">
                    <span class="badge" style="background-color: {jogo['cor']}">{jogo['label']}</span>
                    <span style="color: #ffaa00; font-weight: bold;">⏱ {jogo['tempo']}'</span> 
                    <span style="font-size: 18px; margin-left: 10px;">{jogo['home']} 0x0 {jogo['away']}</span>
                </div>
            """, unsafe_allow_html=True)
            
            c1, c2, c3, c4 = st.columns(4)
            with c1: st.metric(f"🎯 Chutes {jogo['home']}", jogo['stats']['h_ch'])
            with c2: st.metric(f"⚽ Posse {jogo['home']}", f"{jogo['stats']['h_po']}%")
            with c3: st.metric(f"🎯 Chutes {jogo['away']}", jogo['stats']['a_ch'])
            with c4: st.metric(f"⚽ Posse {jogo['away']}", f"{jogo['stats']['a_po']}%")
            st.divider()

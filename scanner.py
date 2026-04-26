# ... (Mantenha o CSS e Imports anteriores)

# ── NOVA LÓGICA DE FILTRAGEM ──────────────────────────────────────────────────
with tab1:
    try:
        # Busca jogos ao vivo
        res = requests.get("https://v3.football.api-sports.io/fixtures?live=all", headers=HEADERS).json().get("response", [])
        jogos_filtrados = []

        for j in res:
            tempo = j["fixture"]["status"]["elapsed"]
            gh, ga = (j["goals"]["home"] or 0), (j["goals"]["away"] or 0)
            
            # 1. Critério de Empate e Tempo
            # Buscamos empates (0x0, 1x1, etc) dentro do tempo configurado
            if tempo and 5 <= tempo <= minuto_max and gh == ga:
                
                # Verificação de Cartão Vermelho
                vermelho_h = j["events"] # Algumas rotas da API trazem eventos direto, outras não. 
                # Se a API-Sports não trouxer na rota principal, checamos via stats:
                
                s = get_stats(j["fixture"]["id"])
                if s:
                    # Lógica de Desvantagem / Desparelho:
                    # Um time tem > 70% de posse OU o dobro de chutes do outro
                    desparelho = (s['h_po'] >= 70 or s['a_po'] >= 70) or \
                                 (s['h_cht'] > s['a_cht'] * 2 if s['a_cht'] > 0 else s['h_cht'] > 3)
                    
                    # Se houver desvantagem clara ou desequilíbrio técnico
                    if desparelho:
                        jogos_filtrados.append({"info": j, "stats": s, "tipo": "🔥 DESPARELHO"})
                    
                    # Nota: Para cartões vermelhos precisos, a API exige a rota de 'events'.
                    # Se quiser adicionar cartões, podemos fazer uma segunda chamada de API por jogo,
                    # mas isso consome mais créditos da sua chave.

        if not jogos_filtrados:
            st.markdown('<div style="text-align:center; padding:50px; color:#666;">BUSCANDO JOGOS DESPARELHOS...</div>', unsafe_allow_html=True)
        else:
            for jogo in jogos_filtrados:
                inf = jogo["info"]
                st_j = jogo["stats"]
                tipo_alerta = jogo["tipo"]
                
                st.markdown(f"""
                <div class="card" style="border-left: 6px solid #ff4b4b if 'VERMELHO' in tipo_alerta else #F5A800">
                    <div class="card-top">
                        <span class="card-liga">🏆 {inf['league']['name']} · {tipo_alerta}</span>
                        <span class="card-tempo">{inf['fixture']['status']['elapsed']}'</span>
                    </div>
                    <div class="time-display">
                        {inf['teams']['home']['name']} <span class="vs-badge">{gh} X {ga}</span> {inf['teams']['away']['name']}
                    </div>
                    <div class="stats-grid">
                        <div class="stat-box">
                            <span class="stat-label">CHUTES A GOL</span>
                            <span class="stat-value destaque">{st_j['h_chg']} | {st_j['a_chg']}</span>
                        </div>
                        <div class="stat-box">
                            <span class="stat-label">POSSE %</span>
                            <span class="stat-value">{st_j['h_po']}% | {st_j['a_po']}%</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Botão de registro mantido para seu histórico
                if st.button(f"REGISTRAR OPORTUNIDADE: {inf['teams']['home']['name']}", key=f"btn_{inf['fixture']['id']}"):
                    # (Lógica de salvar no historico_entradas)
                    pass

    except Exception as e:
        st.error(f"Erro ao buscar desvantagens: {e}")

import streamlit as st
from conteudo import Conteudo
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def render(df):
    conteudo = Conteudo(df)
    
    times = sorted(pd.concat([df['time_mandante'], df['time_visitante']]).unique())
    
    st.title("🏟️ Times")
    st.markdown("---")

    # ── Filtro de time ──────────────────────────────
    
    time_selecionado = st.selectbox("Selecione um time", times)
    
    ap = conteudo.aproveitamento_time(time_selecionado)
    
    # ── Cards de métricas ───────────────────────────
    def card(titulo, valor, cor="#00a550"):
        return f"""
        <div style="
            background: linear-gradient(135deg, #1e1e2e, #2a2a3e);
            border-left: 4px solid {cor};
            border-radius: 10px;
            padding: 16px 20px;
            text-align: center;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        ">
            <div style="color: #aaa; font-size: 13px; margin-bottom: 6px;">{titulo}</div>
            <div style="color: white; font-size: 28px; font-weight: bold;">{valor}</div>
        </div>
        """

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.markdown(card("Total de Jogos", ap['total'], "#4a9eff"), unsafe_allow_html=True)
    c2.markdown(card("Vitórias", ap['vitorias'], "#00a550"), unsafe_allow_html=True)
    c3.markdown(card("Empates", ap['empates'], "#ffa500"), unsafe_allow_html=True)
    c4.markdown(card("Derrotas", ap['derrotas'], "#ff4b4b"), unsafe_allow_html=True)
    c5.markdown(card("Aproveitamento", f"{ap['pct_vitoria']}%", "#9b59b6"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    c6, c7, c8 = st.columns(3)
    c6.markdown(card("Gols Marcados", ap['gols_marcados'], "#00a550"), unsafe_allow_html=True)
    c7.markdown(card("Gols Sofridos", ap['gols_sofridos'], "#ff4b4b"), unsafe_allow_html=True)
    saldo_cor = "#00a550" if ap['saldo'] >= 0 else "#ff4b4b"
    c8.markdown(card("Saldo de Gols", f"{'+' if ap['saldo'] > 0 else ''}{ap['saldo']}", saldo_cor), unsafe_allow_html=True)

    # ── Gráficos: Aproveitamento geral + Mandante vs Visitante ──
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Aproveitamento Geral")
        fig1 = go.Figure(go.Pie(
            labels=['Vitórias', 'Empates', 'Derrotas'],
            values=[ap['vitorias'], ap['empates'], ap['derrotas']],
            hole=0.4,
            marker_colors=['#00a550', '#ffa500', '#ff4b4b']
        ))
        fig1.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            legend=dict(orientation='h', y=-0.1)
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        st.subheader("🏠 Mandante vs 🚌 Visitante")
        mv = conteudo.desempenho_mandante_visitante(time_selecionado)
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(name='Vitórias', x=mv['tipo'], y=mv['vitorias'], marker_color='#00a550'))
        fig2.add_trace(go.Bar(name='Empates', x=mv['tipo'], y=mv['empates'], marker_color='#ffa500'))
        fig2.add_trace(go.Bar(name='Derrotas', x=mv['tipo'], y=mv['derrotas'], marker_color='#ff4b4b'))
        fig2.update_layout(
            barmode='group',
            yaxis_title='% de Jogos',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            legend=dict(orientation='h', y=-0.2)
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    st.markdown("---")

    # ── Evolução ao longo dos anos ──────────────────
    st.subheader(f"📈 Evolução do Aproveitamento — {time_selecionado}")
    evolucao = conteudo.evolucao_time(time_selecionado)
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=evolucao['ano_campeonato'],
        y=evolucao['aproveitamento'],
        mode='lines+markers',
        line=dict(color='#00a550', width=2),
        marker=dict(size=8),
        name='Aproveitamento %'
    ))
    fig3.update_layout(
        xaxis_title='Temporada',
        yaxis_title='Aproveitamento %',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    st.plotly_chart(fig3, use_container_width=True)
    
    st.markdown("---")

   # ── Head-to-head ────────────────────────────────
    st.subheader("⚔️ Head-to-Head")
    col3, col4 = st.columns(2)
    with col3:
        time1 = st.selectbox("Time 1", times, key='h2h_time1')
    with col4:
        time2 = st.selectbox("Time 2", [t for t in times if t != time1], key='h2h_time2')
    
    if time1 and time2:
        h2h = conteudo.head_to_head(time1, time2)
    
    if h2h['total'] == 0:
        st.warning("Esses times nunca se enfrentaram no Brasileirão.")
    else:
        # ── Cards vitórias ──
        d1, d2, d3 = st.columns(3)
        d1.markdown(card(f"Vitórias {time1}", h2h['vitorias_time1'], "#00a550"), unsafe_allow_html=True)
        d2.markdown(card("Empates", h2h['empates'], "#ffa500"), unsafe_allow_html=True)
        d3.markdown(card(f"Vitórias {time2}", h2h['vitorias_time2'], "#ff4b4b"), unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # ── Cards gols ──
        e1, e2, e3 = st.columns(3)
        e1.markdown(card(f"Gols {time1}", h2h['gols_time1'], "#00a550"), unsafe_allow_html=True)
        e2.markdown(card("Total de Jogos", h2h['total'], "#4a9eff"), unsafe_allow_html=True)
        e3.markdown(card(f"Gols {time2}", h2h['gols_time2'], "#ff4b4b"), unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)

        # ── Gráfico de tendência ──
        st.subheader(f"📈 Tendência nos Confrontos — {time1} vs {time2}")
        evolucao = conteudo.evolucao_h2h(time1, time2)
        
        fig_h2h = go.Figure()
        fig_h2h.add_trace(go.Scatter(
            x=evolucao['ano_campeonato'],
            y=evolucao[f'aproveitamento_{time1}'],
            mode='lines+markers',
            name=time1,
            line=dict(color='#00a550', width=2),
            marker=dict(size=8)
        ))
        fig_h2h.add_trace(go.Scatter(
            x=evolucao['ano_campeonato'],
            y=evolucao[f'aproveitamento_{time2}'],
            mode='lines+markers',
            name=time2,
            line=dict(color='#ff4b4b', width=2),
            marker=dict(size=8)
        ))
        fig_h2h.update_layout(
            xaxis_title='Temporada',
            yaxis_title='% de Vitórias nos Confrontos',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            legend=dict(orientation='h', y=-0.2)
        )
        st.plotly_chart(fig_h2h, use_container_width=True)

        # ── Últimos confrontos ──
        st.subheader("📋 Últimos Confrontos")
        st.dataframe(h2h['jogos'], use_container_width=True, hide_index=True)

    # ── Ranking geral ───────────────────────────────
    st.subheader("🏅 Ranking Geral de Times")
    ranking = conteudo.ranking_times()
    st.dataframe(ranking, use_container_width=True)
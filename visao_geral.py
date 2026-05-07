import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from conteudo import Conteudo

def render(df):
    conteudo = Conteudo(df)
    campeoes, ranking = conteudo.campeoes_por_ano()
    gols = conteudo.gols_e_tendencia()
    mandante = conteudo.vantagem_mandante()

    st.title("📊 Visão Geral")

    # ── Ranking e Campeões ──────────────────────────
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🏆 Ranking de Títulos")
        st.dataframe(ranking, use_container_width=True, hide_index=False)
    with col2:
        st.subheader("📅 Campeões por Ano")
        st.dataframe(campeoes, use_container_width=True, hide_index=True)

    st.markdown("---")

    # ── Gráficos lado a lado ────────────────────────
    col3, col4 = st.columns(2)

    with col3:
        st.subheader("⚽ Média de Gols por Temporada")
        fig1 = go.Figure()

        fig1.add_trace(go.Bar(
            x=gols['ano_campeonato'],
            y=gols['media_gols'],
            name='Média de Gols',
            marker_color='#00a550'
        ))

        fig1.add_trace(go.Scatter(
            x=gols['ano_campeonato'],
            y=gols['tendencia'],
            name='Tendência',
            line=dict(color='#ff4b4b', width=2, dash='dash')
        ))

        fig1.update_layout(
            xaxis_title='Temporada',
            yaxis_title='Média de Gols por Jogo',
            legend=dict(orientation='h', y=-0.2),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col4:
        st.subheader("🏠 Vantagem do Mandante por Temporada")
        fig2 = go.Figure()

        fig2.add_trace(go.Bar(
            x=mandante['ano_campeonato'],
            y=mandante['pct_vitoria_mandante'],
            name='Vitória Mandante',
            marker_color='#00a550'
        ))
        fig2.add_trace(go.Bar(
            x=mandante['ano_campeonato'],
            y=mandante['pct_empate'],
            name='Empate',
            marker_color='#ffa500'
        ))
        fig2.add_trace(go.Bar(
            x=mandante['ano_campeonato'],
            y=mandante['pct_vitoria_visitante'],
            name='Vitória Visitante',
            marker_color='#ff4b4b'
        ))

        fig2.update_layout(
            barmode='stack',
            xaxis_title='Temporada',
            yaxis_title='% de Jogos',
            legend=dict(orientation='h', y=-0.2),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )
        st.plotly_chart(fig2, use_container_width=True)
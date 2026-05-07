import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from conteudo import Conteudo

def card(titulo, valor, subtitulo="", cor="#00a550"):
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
        <div style="color: white; font-size: 22px; font-weight: bold;">{valor}</div>
        <div style="color: #aaa; font-size: 11px; margin-top: 4px;">{subtitulo}</div>
    </div>
    """

def render(df):
    conteudo = Conteudo(df)

    st.title("📈 Análise Tática")
    st.info("⚠️ Os dados táticos estão disponíveis apenas para temporadas mais recentes.")
    st.markdown("---")

    # ── Eficiência Ofensiva ─────────────────────────
    st.subheader("🎯 Eficiência Ofensiva por Time")
    st.caption("Percentual de chutes convertidos em gol — quanto maior, mais eficiente o ataque.")

    eficiencia = conteudo.eficiencia_ofensiva()

    col1, col2 = st.columns([1, 1])

    with col1:
        fig1 = go.Figure(go.Bar(
            x=eficiencia['conversao_%'],
            y=eficiencia['time'],
            orientation='h',
            marker_color='#00a550',
            text=eficiencia['conversao_%'].astype(str) + '%',
            textposition='outside'
        ))
        fig1.update_layout(
            xaxis_title='Conversão %',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            height=600,
            yaxis=dict(autorange='reversed')
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.dataframe(
            eficiencia[['time', 'gols_por_jogo', 'chutes_por_jogo', 'conversao_%']].rename(columns={
                'time': 'Time',
                'gols_por_jogo': 'Gols/Jogo',
                'chutes_por_jogo': 'Chutes/Jogo',
                'conversao_%': 'Conversão %'
            }),
            use_container_width=True,
            hide_index=True,
            height=600
        )

    st.markdown("---")

    # ── Perfil Tático por Time ──────────────────────
    st.subheader("🕸️ Perfil Tático por Time")
    st.caption("Radar com as médias táticas do time selecionado.")

    times = sorted(pd.concat([df['time_mandante'], df['time_visitante']]).unique())
    time_selecionado = st.selectbox("Selecione um time", times, key='tatica_time')

    perfil = conteudo.perfil_tatico(time_selecionado)
    categorias = list(perfil.keys())
    valores = list(perfil.values())
    categorias_fechadas = categorias + [categorias[0]]
    valores_fechados = valores + [valores[0]]

    fig2 = go.Figure(go.Scatterpolar(
        r=valores_fechados,
        theta=categorias_fechadas,
        fill='toself',
        fillcolor='rgba(0, 165, 80, 0.2)',
        line=dict(color='#00a550', width=2),
        name=time_selecionado
    ))
    fig2.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, color='black'),
            angularaxis=dict(color='white')
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=450
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    # ── Evolução Tática por Temporada ───────────────
    st.subheader("📅 Evolução Tática por Temporada")
    st.caption("Como o estilo de jogo do Brasileirão mudou ao longo dos anos.")

    evolucao = conteudo.evolucao_tatica()

    metrica = st.selectbox("Selecione a métrica", [
        'chutes_por_jogo', 'faltas_por_jogo',
        'escanteios_por_jogo', 'defesas_por_jogo'
    ], format_func=lambda x: x.replace('_', ' ').title())

    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=evolucao['ano_campeonato'],
        y=evolucao[metrica],
        mode='lines+markers',
        line=dict(color='#4a9eff', width=2),
        marker=dict(size=8),
        name=metrica
    ))
    fig3.update_layout(
        xaxis_title='Temporada',
        yaxis_title='Média por Jogo',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("---")

    # ── Desempenho de Goleiros ──────────────────────
    st.subheader("🧤 Desempenho de Goleiros por Time")
    st.caption("Médias de defesas e gols sofridos por jogo.")

    goleiros = conteudo.desempenho_goleiros()

    col3, col4 = st.columns([1, 1])
    with col3:
        fig4 = go.Figure(go.Bar(
            x=goleiros['defesas_por_jogo'],
            y=goleiros['time'],
            orientation='h',
            marker_color='#4a9eff',
            name='Defesas/Jogo'
        ))
        fig4.update_layout(
            title='Defesas por Jogo',
            xaxis_title='Média de Defesas',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            height=500,
            yaxis=dict(autorange='reversed')
        )
        st.plotly_chart(fig4, use_container_width=True)

    with col4:
        fig5 = go.Figure(go.Bar(
            x=goleiros['gols_sofridos_por_jogo'],
            y=goleiros['time'],
            orientation='h',
            marker_color='#ff4b4b',
            name='Gols Sofridos/Jogo'
        ))
        fig5.update_layout(
            title='Gols Sofridos por Jogo',
            xaxis_title='Média de Gols Sofridos',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            height=500,
            yaxis=dict(autorange='reversed')
        )
        st.plotly_chart(fig5, use_container_width=True)

    st.markdown("---")

    
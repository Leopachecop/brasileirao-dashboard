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
    recordes = conteudo.recordes_historicos()

    st.title("⚽ Partidas")
    st.markdown("---")

    # ── Recordes históricos ─────────────────────────
    st.subheader("🏆 Recordes Históricos")

    c1, c2, c3 = st.columns(3)
    c1.markdown(card(
        "Maior Goleada",
        recordes['maior_goleada']['placar'],
        f"em {recordes['maior_goleada']['ano']}",
        "#ff4b4b"
    ), unsafe_allow_html=True)
    c2.markdown(card(
        "Jogo com Mais Gols",
        recordes['mais_gols']['placar'],
        f"{recordes['mais_gols']['total']} gols em {recordes['mais_gols']['ano']}",
        "#ffa500"
    ), unsafe_allow_html=True)
    c3.markdown(card(
        "Maior Público",
        f"{recordes['maior_publico']['publico']:,}".replace(",", "."),
        f"{recordes['maior_publico']['jogo']} — {recordes['maior_publico']['ano']}",
        "#4a9eff"
    ), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    c4, c5, c6 = st.columns(3)
    c4.markdown(card("Total de Partidas", f"{recordes['total_partidas']:,}".replace(",", "."), "", "#9b59b6"), unsafe_allow_html=True)
    c5.markdown(card("Total de Gols", f"{recordes['total_gols']:,}".replace(",", "."), "", "#00a550"), unsafe_allow_html=True)
    c6.markdown(card("Média de Gols por Jogo", recordes['media_gols'], "", "#ffa500"), unsafe_allow_html=True)

    st.markdown("---")

    # ── Maiores goleadas ────────────────────────────
    st.subheader("💥 Maiores Goleadas Históricas")
    n_goleadas = st.slider("Quantas goleadas exibir?", min_value=5, max_value=30, value=10)
    goleadas = conteudo.maiores_goleadas(n_goleadas)
    st.dataframe(goleadas, use_container_width=True, hide_index=True)

    st.markdown("---")

    # ── Maiores públicos ────────────────────────────
    st.subheader("🏟️ Jogos com Maior Público")
    n_publicos = st.slider("Quantos jogos exibir?", min_value=5, max_value=30, value=10, key='slider_publico')
    publicos = conteudo.maiores_publicos(n_publicos)

    col1, col2 = st.columns([2, 1])
    with col1:
        st.dataframe(publicos, use_container_width=True, hide_index=True)
    with col2:
        fig = go.Figure(go.Bar(
            x=publicos['Público'],
            y=publicos['Mandante'] + ' x ' + publicos['Visitante'],
            orientation='h',
            marker_color='#4a9eff'
        ))
        fig.update_layout(
            xaxis_title='Público',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ── Gols por rodada ─────────────────────────────
    st.subheader("📊 Média de Gols por Rodada")
    rodada = conteudo.gols_por_rodada()

    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=rodada['rodada'],
        y=rodada['media_gols'],
        marker_color='#00a550',
        name='Média de Gols'
    ))
    fig2.update_layout(
        xaxis_title='Rodada',
        yaxis_title='Média de Gols',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    st.plotly_chart(fig2, use_container_width=True)
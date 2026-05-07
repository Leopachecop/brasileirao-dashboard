import streamlit as st

def render_menu():
    with st.sidebar:
        st.title("⚽ Brasileirão")
        st.markdown("---")
        
        pagina = st.radio(
            "Navegação",
            options=[
                "Visão Geral",
                "Times",
                "Partidas",
                "Análise Tática"
            ]
        )
    
    return pagina
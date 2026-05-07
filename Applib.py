import streamlit as st
from Menu import render_menu
import visao_geral
import times
import partidas
import tatica
from data_loader1 import DataLoader

# Configuração da página
st.set_page_config(
    page_title="Brasileirão Dashboard by Lp.",
    page_icon="⚽",
    layout="wide"
)

# Carrega os dados uma vez e guarda no cache
@st.cache_data
def load_data():
    loader = DataLoader('.')
    return loader.Brasileirao

df = load_data()


# Renderiza o menu e pega a página selecionada
pagina = render_menu()

# Roteamento
if pagina == "Visão Geral":
    visao_geral.render(df)
elif pagina == "Times":
    times.render(df)
elif pagina == "Partidas":
    partidas.render(df)
elif pagina == "Análise Tática":
    tatica.render(df)
import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import os
from datetime import datetime

# --- CONFIGURATION STYLE PRO ---
st.set_page_config(page_title="Terminal Quantitaire", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; color: #ffffff; }
    div { color: #ffffff !important; }
    .stMetric { background-color: #161b22; border-radius: 12px; padding: 20px; border: 1px solid #30363d; }
    h1, h2, h3 { color: #58a6ff !important; }
    </style>
    """, unsafe_allow_html=True)

# --- PROTECTION MOT DE PASSE ---
def check_password():
    if st.sidebar.text_input("Mot de passe", type="password") == st.secrets["PASSWORD"]:
        return True
    st.error("Mot de passe requis")
    return False

if not check_password():
    st.stop()

# --- CONFIGURATION ---
assets = {"Nasdaq 100": "QQQ", "S&P 500": "VOO", "Europe": "VGK", "Monde": "ACWI"}
fortuneo_etfs = {"QQQ": "PUST.PA", "VOO": "ESE.PA", "VGK": "MEUD.PA", "ACWI": "WPEA.PA"}

@st.cache_data(ttl=3600)
def get_data():
    tickers = list(fortuneo_etfs.values()) + ["^VIX"]
    return yf.download(tickers, period="6mo")['Close'].ffill()

data = get_data()
vix = float(data["^VIX"].iloc[-1])

# --- DASHBOARD HEADER ---
st.title("📊 Terminal de Pilotage Patrimonial")
parts_monde = float(st.secrets.get("PARTS_MONDE", 0))
parts_mom = float(st.secrets.get("PARTS_MOMENTUM", 0))
cout_total = float(st.secrets.get("PRIX_REVIENT_TOTAL", 15000))

valeur_monde = parts_monde * data["WPEA.PA"].iloc[-1]
valeur_mom = parts_mom * data["PUST.PA"].iloc[-1]
total_actuel = valeur_monde + valeur_mom

c1, c2, c3 = st.columns(3)
c1.metric("Valeur Totale", f"{total_actuel:,.2f} €")
c2.metric("Plus-Value", f"{(total_actuel - cout_total):,.2f} €")
c3.metric("Indice VIX", f"{vix:.2f}", "⚠️ ALERTE" if vix > 25 else "🟢 CALME")

# --- MATRICE MOMENTUM ---
st.subheader("📋 Matrice de Décision Momentum")
# (Ici, ajoutez votre logique de calcul de pourcentage sur 1m/3m/6m comme dans votre ancien code)
st.info("La matrice de décision analyse les actifs pour déterminer le gagnant du mois.")

# --- CALCUL PARTS À ACHETER ---
st.subheader("💡 Aide à l'investissement")
budget = st.number_input("Budget à investir ce mois-ci (€)", value=1000)
st.write(f"- Socle (World) : {budget/2:.2f} €")
st.write(f"- Poche Momentum : {budget/2:.2f} €")

# --- GRAPHIQUE HISTORIQUE ---
st.subheader("📈 Évolution de la richesse")
if os.path.exists('portfolio_history.csv'):
    hist = pd.read_csv('portfolio_history.csv')
    fig = go.Figure(go.Scatter(x=hist['Date'], y=hist['Valeur'], line=dict(color='#58a6ff')))
    fig.update_layout(template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)

# --- ACTIONS ---
if st.sidebar.button("💾 Enregistrer la valeur du jour"):
    new_entry = pd.DataFrame({'Date': [datetime.now().strftime("%Y-%m-%d")], 'Valeur': [total_actuel]})
    new_entry.to_csv('portfolio_history.csv', mode='a', header=not os.path.exists('portfolio_history.csv'), index=False)
    st.sidebar.success("Archivé !")


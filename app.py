import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import os

# --- CONFIGURATION STYLE PRO DARK ---
st.set_page_config(page_title="Terminal Quantitaire Pro", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; color: #ffffff; }
    div.stMetric { background-color: #161b22; border-radius: 12px; padding: 20px; border: 1px solid #30363d; }
    h1, h2, h3 { color: #58a6ff; }
    .css-1r6slb0 { background-color: #161b22; }
    </style>
    """, unsafe_allow_html=True)

# --- 1. DONNÉES & VIX ---
@st.cache_data(ttl=3600)
def get_data():
    tickers = ["PUST.PA", "ESE.PA", "MEUD.PA", "WPEA.PA", "^VIX"]
    df = yf.download(tickers, period="1y")['Close']
    return df.ffill()

data = get_data()
vix = float(data["^VIX"].iloc[-1])
market_status = "🟢 CALME" if vix < 15 else "🟠 VOLATIL" if vix < 25 else "🔴 ALERTE CRASH"

# --- 2. CALCULS ---
parts_monde = float(st.secrets.get("PARTS_MONDE", 0))
parts_mom = float(st.secrets.get("PARTS_MOMENTUM", 0))
cout_total = float(st.secrets.get("PRIX_REVIENT_TOTAL", 15000))

valeur_monde = parts_monde * data["WPEA.PA"].iloc[-1]
valeur_mom = parts_mom * data["PUST.PA"].iloc[-1]
total_actuel = valeur_monde + valeur_mom
pv = total_actuel - cout_total
rendement = (pv / cout_total) * 100

# --- 3. DASHBOARD ---
st.title("📊 Terminal de Pilotage Patrimonial")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Valeur Totale", f"{total_actuel:,.2f} €")
c2.metric("Plus-Value Latente", f"{pv:,.2f} €", f"{rendement:.2f} %")
c3.metric("Indice de Peur (VIX)", f"{vix:.2f}", market_status)
c4.metric("Capital Initial", f"{cout_total:,.2f} €")

# --- 4. ANALYSE DU VIX (LOGIQUE D'ALERTE) ---
if vix > 25:
    st.error("⚠️ **ALERTE : Le marché est sous tension extrême (VIX > 25).** La poche Momentum doit rester en CASH.")
else:
    st.success("✅ **SITUATION NORMALE : Le marché est stable.** Vous pouvez suivre la stratégie Momentum.")

# --- 5. GRAPHIQUE & TABLEAU ---
col_graph, col_tab = st.columns([2, 1])

with col_graph:
    st.subheader("📈 Évolution de votre Richesse")
    if os.path.exists('portfolio_history.csv'):
        hist = pd.read_csv('portfolio_history.csv')
        fig = go.Figure(go.Scatter(x=hist['Date'], y=hist['Valeur'], fill='tozeroy', line=dict(color='#58a6ff')))
        fig.update_layout(template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

with col_tab:
    st.subheader("📋 État des Positions")
    df_pos = pd.DataFrame({"Actif": ["MSCI World", "Nasdaq (Momentum)"], "Valeur (€)": [valeur_monde, valeur_mom]})
    st.table(df_pos)

# --- 6. SIDEBAR ---
st.sidebar.header("🎛️ Commandes")
if st.sidebar.button("💾 Enregistrer la valeur du jour"):
    new_entry = pd.DataFrame({'Date': [datetime.now().strftime("%Y-%m-%d")], 'Valeur': [total_actuel]})
    new_entry.to_csv('portfolio_history.csv', mode='a', header=not os.path.exists('portfolio_history.csv'), index=False)
    st.sidebar.success("Donnée archivée !")


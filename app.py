import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- CONFIGURATION STYLE PRO ---
st.set_page_config(page_title="Terminal Quantitaire - Automatisé", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; border-radius: 8px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.02); border: 1px solid #e9ecef; }
    div.stButton > button:first-child { background-color: #007bff; color: white; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- FONCTION DE VÉRIFICATION DU MOT DE PASSE ---
def check_password():
    if "password_correct" not in st.session_state:
        st.title("🔒 Accès Sécurisé")
        password = st.text_input("Veuillez saisir le mot de passe administrateur :", type="password")
        if st.button("Se connecter"):
            if password == st.secrets.get("PASSWORD", ""):
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("❌ Mot de passe incorrect.")
        return False
    return True

if not check_password():
    st.stop()

# --- 1. CONFIGURATION DES ACTIFS ---
assets = {
    "États-Unis (S&P 500)": "VOO", # VOO est très stable sur Yahoo Finance
    "Europe (Stoxx 600)": "VGK",
    "Émergents (MSCI EM)": "EEM",
    "Monde (Socle Principal)": "ACWI"
}

# Correspondance exacte avec les ETF PEA sur Fortuneo
fortuneo_etfs = {
    "VOO": "ESE.PA",   # S&P 500 (BNP)
    "VGK": "MEUD.PA",  # Stoxx 600 (Amundi)
    "EEM": "PAEEM.PA", # Émergents (Amundi)
    "ACWI": "WPEA.PA"  # Monde (BlackRock)
}

@st.cache_data(ttl=3600)
def load_data():
    dict_data = {}
    all_tickers = list(assets.values()) + list(fortuneo_etfs.values()) + ["^VIX"]
    for ticker in all_tickers:
        try:
            df_hist = yf.download(ticker, period="2y", progress=False, auto_adjust=True)
            if not df_hist.empty:
                if isinstance(df_hist.columns, pd.MultiIndex):
                    dict_data[ticker] = df_hist['Close'][ticker]
                else:
                    dict_data[ticker] = df_hist['Close']
        except Exception:
            pass
    return pd.DataFrame(dict_data).ffill()

data = load_data()

# --- 2. CALCULS STRATÉGIQUES MULTI-HORIZONS ---
moms = {}
vix = float(data["^VIX"].iloc[-1]) if "^VIX" in data.columns and not data["^VIX"].empty else 15.0
market_stress = "Crise / Alerte" if vix > 25 else "Opportunité / Calme" if vix < 15 else "Normal"

for name, ticker in assets.items():
    if ticker in data.columns and len(data[ticker]) >= 200:
        current = float(data[ticker].iloc[-1])
        past_1m = float(data[ticker].iloc[-21])
        past_3m = float(data[ticker].iloc[-63])
        past_6m = float(data[ticker].iloc[-126])
        
        score_1m = ((current / past_1m) - 1) * 100
        score_3m = ((current / past_3m) - 1) * 100
        score_6m = ((current / past_6m) - 1) * 100
        
        sma200_series = data[ticker].rolling(200).mean()
        sma200 = float(sma200_series.iloc[-1]) if len(sma200_series) >= 200 else current
        trend_ok = current > sma200
        
        if score_6m > 0 and trend_ok:
            status = "🟢 ACHAT"
        elif score_6m > 0 or trend_ok:
            status = "🟠 NEUTRE"
        else:
            status = "🔴 CASH"
            
        moms[name] = {
            "Prix Actuel": f"{current:.2f}$",
            "Momentum 1 Mois": f"{score_1m:.2f}%",
            "Momentum 3 Mois": f"{score_3m:.2f}%",
            "Momentum 6 Mois (Signal)": f"{score_6m:.2f}%",
            "Au-dessus SMA 200": "Oui" if trend_ok else "Non",
            "Statut Système": status,
            "_score_6m_raw": score_6m,
            "_ticker_ref": ticker
        }

poche_momentum_assets = {k: v for k, v in moms.items() if k != "Monde (Socle Principal)"}
winner = max(poche_momentum_assets, key=lambda x: poche_momentum_assets[x]["_score_6m_raw"])
signal_final = winner
if vix > 25:
    signal_final = "CASH / SÉCURITÉ COMPTE ESPÈCES"

# --- 3. SYNCHRONISATION DU PORTEFEUILLE VIRTUEL (VIA SECRETS) ---
parts_monde = float(st.secrets.get("PARTS_MONDE", 0.0))
parts_momentum = float(st.secrets.get("PARTS_MOMENTUM", 0.0))
cash_pea = float(st.secrets.get("CASH_PEA", 0.0))

prix_wpea = float(data["WPEA.PA"].iloc[-1]) if "WPEA.PA" in data.columns else 5.0
ticker_momentum_actuel = fortuneo_etfs[poche_momentum_assets[winner]["_ticker_ref"]]
prix_momentum = float(data[ticker_momentum_actuel].iloc[-1]) if ticker_momentum_actuel in data.columns else 0.0

valeur_monde = parts_monde * prix_wpea
valeur_momentum = parts_momentum * prix_momentum
total_portefeuille = valeur_monde + valeur_momentum + cash_pea

# --- 4. INTERFACE PRINCIPALE ---
st.title("🏛️ Terminal Quantitaire - Pilotage Automatique")
st.write(f"Mise à jour et synchronisation : {datetime.now().strftime('%d/%m/%Y à %H:%M')}")
st.markdown("---")

col_tot, col_wpea, col_mom_poche, col_csh = st.columns(4)
with col_tot: st.metric("💰 VALEUR GLOBALE PEA", f"{total_portefeuille:,.2f} €")
with col_wpea: st.metric("🌍 MSCI World (WPEA)", f"{valeur_monde:,.2f} €", f"{parts_monde:.0f} parts")
with col_mom_poche: st.metric("⚡ POCHE MOMENTUM", f"{valeur_momentum:,.2f} €", f"{parts_momentum:.0f} parts")
with col_csh: st.metric("💶 COMPTE ESPÈCES", f"{cash_pea:,.2f} €")

st.markdown("---")

col_sig, col_vix, col_stress = st.columns(3)
with col_sig: st.metric("🚨 ACTION STRATÉGIQUE", signal_final)
with col_vix: st.metric("📊 INDICE VIX", f"{vix:.2f}", delta=market_stress, delta_color="inverse")
with col_stress: st.metric("🔥 MEILLEUR MOMENTUM (6M)", poche_momentum_assets[winner]["Momentum 6 Mois (Signal)"])

# --- 5. ASSISTANT D'ORDRE AUTOMATIQUE (SIDEBAR) ---
st.sidebar.header("🧮 Ordre Fortuneo Automatique")

# Création d'un "Formulaire" (bloque le calcul tant qu'on ne clique pas sur le bouton)
with st.sidebar.form(key="form_versement"):
    apport_mois = st.number_input("Versement ce mois-ci (€)", value=1000, step=100)
    bouton_valider = st.form_submit_button(label="✅ Valider le versement")

# NOUVEAU CALCUL : On prend le versement validé + l'argent qui dort déjà sur le compte espèces
cash_disponible = apport_mois + cash_pea

# On divise cet argent en deux parts égales (50% / 50%)
besoin_monde = cash_disponible * 0.50
besoin_momentum = cash_disponible * 0.50

st.sidebar.markdown("---")
st.sidebar.subheader("📝 Votre ordre au millimètre :")

# Sécurité pour éviter la division par zéro si le prix de l'ETF ne s'est pas chargé
parts_wpea_a_acheter = int(besoin_monde / prix_wpea) if prix_wpea > 0 else 0

st.sidebar.info(f"**1. Pour le MSCI World (WPEA) :**\nVerser **{besoin_monde:.2f} €** (Achetez environ {parts_wpea_a_acheter} parts)")

if signal_final != "CASH / SÉCURITÉ COMPTE ESPÈCES":
    st.sidebar.success(f"**2. Pour la Poche Momentum ({signal_final}) :**\nVerser **{besoin_momentum:.2f} €** sur l'ETF associé chez Fortuneo.")
else:
    st.sidebar.error(f"**2. Alerte Risque :**\nLaissez vos **{besoin_momentum:.2f} €** bien au chaud sur votre compte espèces Fortuneo.")

# --- 6. GRAPHIQUE ---
st.subheader("📈 Graphique de force relative et sa Moyenne Mobile (SMA 200)")
fig = go.Figure()
colors = {"États-Unis (S&P 500)": "#1f77b4", "Europe (Stoxx 600)": "#ff7f0e", "Émergents (MSCI EM)": "#9467bd", "Monde (Socle Principal)": "#7f7f7f"}

for name, ticker in assets.items():
    if ticker in data.columns and len(data[ticker]) >= 200:
        prices_6m = data[ticker].tail(126)
        base_price = data[ticker].iloc[-126]
        norm_prices = (prices_6m / base_price) * 100
        sma200_raw = data[ticker].rolling(200).mean()
        norm_sma200 = (sma200_raw.tail(126) / base_price) * 100
        is_winner = (name == winner)
        color = "#28a745" if is_winner else colors[name]
        
        fig.add_trace(go.Scatter(x=norm_prices.index, y=norm_prices, name=name, line=dict(width=3.5 if is_winner else 1.5, color=color)))
        fig.add_trace(go.Scatter(x=norm_sma200.index, y=norm_sma200, name=f"SMA 200 - {name}", line=dict(width=1, color=color, dash="dot"), showlegend=False))

fig.update_layout(template="plotly_white", hovermode="x unified", height=400)
st.plotly_chart(fig, use_container_width=True)

# --- 7. TABLEAU MULTI-HORIZONS ---
st.subheader("📋 Matrice de Décision Multi-Horizons (1m, 3m, 6m)")
df_display = pd.DataFrame(moms).T[["Prix Actuel", "Momentum 1 Mois", "Momentum 3 Mois", "Momentum 6 Mois (Signal)", "Au-dessus SMA 200", "Statut Système"]]
st.table(df_display)


import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Portfolio PEA", layout="centered", initial_sidebar_state="collapsed")

# --- 2. PROTECTION PAR MOT DE PASSE ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Écran de connexion si l'utilisateur n'est pas authentifié
if not st.session_state.authenticated:
    st.markdown("""
        <style>
        .stApp { background-color: #0d1321; color: #ffffff; }
        .login-box { background-color: #172033; padding: 30px; border-radius: 15px; border: 1px solid #23304c; margin-top: 50px; }
        h2 { color: #ffffff !important; text-align: center; }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='login-box'>", unsafe_allow_html=True)
    st.markdown("<h2>🏛️ Terminal Alpha Zen</h2>", unsafe_allow_html=True)
    st.write("<br>", unsafe_allow_html=True)
    
    password_input = st.text_input("Veuillez entrer votre mot de passe :", type="password")
    
    if st.button("⚡ Déverrouiller le Cockpit", use_container_width=True):
        # Vérification par rapport à vos Secrets Streamlit
        if password_input == st.secrets.get("PASSWORD"):
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Mot de passe incorrect. Accès refusé.")
            
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()  # Arrête l'exécution du reste du code tant qu'on n'est pas connecté

# --- 3. STYLE CSS AVANCÉ DE L'APPLICATION ---
st.markdown("""
    <style>
    .stApp { background-color: #0d1321; color: #ffffff; }
    
    /* Style des conteneurs/cartes d'actifs */
    div[data-testid="stVerticalBlock"] > div[style*="flex-direction: column;"] {
        background-color: #172033;
        border-radius: 15px;
        padding: 15px;
        border: 1px solid #23304c;
    }
    
    /* Onglets Streamlit */
    .stTabs [data-baseweb="tab-list"] { gap: 24px; background-color: #0d1321; }
    .stTabs [data-baseweb="tab"] { color: #8a96a8; font-weight: bold; }
    .stTabs [aria-selected="true"] { color: #00d28f !important; border-bottom: 3px solid #00d28f; }
    
    /* Typographie et couleurs spécifiques */
    h1, h2, h3 { color: #ffffff !important; }
    .vert-crypto { color: #00d28f; font-weight: bold; }
    .bleu-invest { color: #3b82f6; font-weight: bold; }
    .orange-liq { color: #f59e0b; font-weight: bold; }
    
    /* Badges Catégories & Types */
    .badge-type { background-color: #1e293b; font-size: 12px; padding: 2px 6px; border-radius: 4px; color: #ffffff; font-weight: bold; }
    .badge-socle { background-color: #064e3b; color: #34d399; padding: 2px 8px; border-radius: 5px; font-size: 12px; font-weight: bold; }
    .badge-momentum { background-color: #1e3a8a; color: #93c5fd; padding: 2px 8px; border-radius: 5px; font-size: 12px; font-weight: bold; }
    .badge-satellite { background-color: #7c2d12; color: #fdba74; padding: 2px 8px; border-radius: 5px; font-size: 12px; font-weight: bold; }
    .badge-secteur { background-color: #1e1b4b; color: #c7d2fe; padding: 2px 8px; border-radius: 5px; font-size: 12px; }
    
    .btn-ordre { background-color: #00d28f; color: #0d1321; border-radius: 8px; padding: 5px 15px; text-decoration: none; font-weight: bold;}
    </style>
    """, unsafe_allow_html=True)

# --- 4. TOUTES VOS DONNÉES (12 Actifs) ---
capital_initial = 10000
investi = 9437
liquidites = 563
plus_value = 0

actifs = [
    # SOCLE ZEN
    {"ticker": "EWLD", "nom": "Amundi PEA MSCI World", "isin": "FR001400U5Q4", "qte": 65, "valeur": 1983, "cours": 30.50, "cible": 20, "cat": "Socle ZEN", "type": "ETF", "secteur": "Monde", "mom": 57, "mom_text": "⚡ Moyen"},
    {"ticker": "PE500", "nom": "Amundi PEA S&P 500", "isin": "FR0011871128", "qte": 35, "valeur": 1477, "cours": 42.20, "cible": 15, "cat": "Socle ZEN", "type": "ETF", "secteur": "USA", "mom": 62, "mom_text": "⚡ Moyen"},
    {"ticker": "PUST", "nom": "Amundi PEA Nasdaq-100", "isin": "FR0011871110", "qte": 17, "valeur": 949, "cours": 55.80, "cible": 10, "cat": "Socle ZEN", "type": "ETF", "secteur": "Tech US", "mom": 70, "mom_text": "🔥 Fort"},
    {"ticker": "PCEU", "nom": "Amundi PEA MSCI Europe", "isin": "FR0013412038", "qte": 4, "valeur": 474, "cours": 118.40, "cible": 5, "cat": "Socle ZEN", "type": "ETF", "secteur": "Europe", "mom": 55, "mom_text": "⚡ Moyen"},
    
    # MOMENTUM
    {"ticker": "GUARD", "nom": "BNP Défense", "isin": "LU2082324318", "qte": 0, "valeur": 0, "cours": 105.20, "cible": 10, "cat": "Momentum", "type": "ETF", "secteur": "Défense", "mom": 85, "mom_text": "🔥 Fort"},
    {"ticker": "SU", "nom": "Schneider Electric", "isin": "FR0000121972", "qte": 0, "valeur": 0, "cours": 228.50, "cible": 5, "cat": "Momentum", "type": "Action", "secteur": "Industrie", "mom": 68, "mom_text": "⚡ Moyen"},
    {"ticker": "AI", "nom": "Air Liquide", "isin": "FR0000120073", "qte": 0, "valeur": 0, "cours": 188.40, "cible": 3, "cat": "Momentum", "type": "Action", "secteur": "Industrie", "mom": 60, "mom_text": "⚡ Moyen"},
    {"ticker": "AM", "nom": "Dassault Aviation", "isin": "FR0014004L86", "qte": 0, "valeur": 0, "cours": 204.00, "cible": 5, "cat": "Momentum", "type": "Action", "secteur": "Défense", "mom": 72, "mom_text": "🔥 Fort"},
    {"ticker": "HO", "nom": "Thales", "isin": "FR0000121329", "qte": 0, "valeur": 0, "cours": 158.20, "cible": 5, "cat": "Momentum", "type": "Action", "secteur": "Défense", "mom": 75, "mom_text": "🔥 Fort"},
    {"ticker": "STM", "nom": "STMicroelectronics", "isin": "NL0000226223", "qte": 0, "valeur": 0, "cours": 39.50, "cible": 5, "cat": "Momentum", "type": "Action", "secteur": "Tech EU", "mom": 40, "mom_text": "❄️ Faible"},

    # SATELLITE
    {"ticker": "SAN", "nom": "Sanofi", "isin": "FR0000120578", "qte": 0, "valeur": 0, "cours": 92.00, "cible": 7, "cat": "Satellite", "type": "Action", "secteur": "Santé", "mom": 55, "mom_text": "⚡ Moyen"},
    {"ticker": "PAEEM", "nom": "Amundi PEA Émergents", "isin": "FR0013412020", "qte": 0, "valeur": 0, "cours": 44.60, "cible": 5, "cat": "Satellite", "type": "ETF", "secteur": "Émergents", "mom": 61, "mom_text": "⚡ Moyen"}
]

# --- 5. HEADER PRINCIPAL ---
col_logo, col_titre, col_btn = st.columns([1, 3, 2])
with col_titre:
    st.markdown("### Portfolio\n<span style='color: #8a96a8;'>PEA Fortuneo · Stratégie Alpha Zen</span>", unsafe_allow_html=True)
with col_btn:
    st.markdown("<br><button style='background-color: #00d28f; color: #0d1321; border: none; padding: 10px 20px; border-radius: 10px; font-weight: bold; width: 100%;'>⚡ Répartir le capital</button>", unsafe_allow_html=True)

st.write("") 

# --- 6. SYSTÈME D'ONGLETS ---
tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "💼 Portefeuille", "📋 Transactions"])

# ==========================================
# ONGLET 1 : DASHBOARD
# ==========================================
with tab1:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"<div style='text-align: center; background-color: #172033; padding: 20px; border-radius: 10px;'>Poids Total<br><span class='vert-crypto' style='font-size: 24px;'>{capital_initial:,.0f} €</span><br><span style='font-size: 12px; color: #8a96a8;'>Capital: 10 000 €</span></div>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align: center; background-color: #172033; padding: 20px; border-radius: 10px; margin-top: 15px;'>Plus-Value<br><span class='vert-crypto' style='font-size: 24px;'>+{plus_value} €</span><br><span style='font-size: 12px; color: #8a96a8;'>+0,00 %</span></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div style='text-align: center; background-color: #172033; padding: 20px; border-radius: 10px;'>Investi<br><span class='bleu-invest' style='font-size: 24px;'>{investi:,.0f} €</span><br><span style='font-size: 12px; color: #8a96a8;'>12 lignes actives</span></div>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align: center; background-color: #172033; padding: 20px; border-radius: 10px; margin-top: 15px;'>Liquidités<br><span class='orange-liq' style='font-size: 24px;'>{liquidites} €</span><br><span style='font-size: 12px; color: #8a96a8;'>5,6% du capital</span></div>", unsafe_allow_html=True)

    st.write("---")
    st.markdown("#### Répartition stratégique")
    fig = go.Figure(data=[go.Pie(labels=['Socle ZEN', 'Momentum', 'Satellite'], 
                                 values=[50, 38, 12], 
                                 hole=.6,
                                 marker_colors=['#00d28f', '#3b82f6', '#f59e0b'],
                                 textinfo='none')])
    fig.update_layout(showlegend=True, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(t=0, b=0, l=0, r=0), font=dict(color='#ffffff'))
    st.plotly_chart(fig, use_container_width=True)

# ==========================================
# ONGLET 2 : PORTEFEUILLE
# ==========================================
with tab2:
    def render_actifs(liste_actifs, badge_class):
        for actif in liste_actifs:
            with st.container():
                col_gauche, col_droite = st.columns([3, 1])
                with col_gauche:
                    st.markdown(f"""
                    <span style='font-size: 18px; font-weight: bold; color: #00d28f;'>{actif['ticker']}</span> 
                    <span class='badge-type'>{actif['type']}</span>
                    <span class='{badge_class}'>{actif['cat']}</span>
                    <span class='badge-secteur'>{actif['secteur']}</span>
                    <br><span style='color: #8a96a8; font-size: 13px;'>{actif['nom']}<br>{actif['isin']}</span>
                    """, unsafe_allow_html=True)
                    
                    cA, cB = st.columns(2)
                    cA.markdown(f"<span style='color: #8a96a8; font-size: 12px;'>QTÉ / VALEUR</span><br><span style='font-weight: bold; font-size: 18px;'>{actif['qte']}</span><br><span style='color: #8a96a8; font-size: 13px;'>{actif['valeur']} €</span>", unsafe_allow_html=True)
                    cB.markdown(f"<span style='color: #8a96a8; font-size: 12px;'>+/- VALUE</span><br><span class='vert-crypto' style='font-size: 18px;'>-</span><br><span class='vert-crypto' style='font-size: 13px;'>0,0%</span>", unsafe_allow_html=True)
                    
                    st.progress(actif['mom'] / 100)
                    st.markdown(f"<span style='color: #f59e0b; font-size: 12px; font-weight: bold;'>{actif['mom_text']}</span>", unsafe_allow_html=True)
                    
                with col_droite:
                    st.markdown(f"<div style='text-align: right; color: #8a96a8; font-size: 12px;'>COURS<br><span style='color: white; font-size: 18px; font-weight: bold;'>{actif['cours']:.2f} €</span></div>", unsafe_allow_html=True)
                    st.write("")
                    st.markdown(f"<div style='text-align: right;'><span style='color: #8a96a8; font-size: 12px;'>CIBLE</span><br><span style='color: #00d28f; font-weight: bold; font-size: 16px;'>{actif['cible']}%</span><br><br><span class='btn-ordre'>💸 Ordre</span></div>", unsafe_allow_html=True)
            st.write("---")

    st.markdown("### <span style='color: #00d28f;'>|</span> SOCLE ZEN", unsafe_allow_html=True)
    render_actifs([a for a in actifs if a['cat'] == "Socle ZEN"], "badge-socle")
    
    st.markdown("### <span style='color: #3b82f6;'>|</span> MOMENTUM", unsafe_allow_html=True)
    render_actifs([a for a in actifs if a['cat'] == "Momentum"], "badge-momentum")

    st.markdown("### <span style='color: #f59e0b;'>|</span> SATELLITE", unsafe_allow_html=True)
    render_actifs([a for a in actifs if a['cat'] == "Satellite"], "badge-satellite")

# ==========================================
# ONGLET 3 : TRANSACTIONS
# ==========================================
with tab3:
    st.info("Historique des transactions à venir...")

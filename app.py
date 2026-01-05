import streamlit as st
import pandas as pd
from groq import Groq

# -------------------------------------------------------------
# CONFIG GLOBALE
# -------------------------------------------------------------
st.set_page_config(page_title="ATLAS – Générateur de séjour parfait", layout="wide")

# Petit thème custom
st.markdown(
    """
    <style>
    /* Body */
    body {
        background: #050816;
        color: #f5f5f5;
    }

    /* Titre principal */
    .atlas-title {
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
        background: linear-gradient(90deg, #ffb703, #fb7185, #38bdf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .atlas-subtitle {
        font-size: 1.1rem;
        color: #e5e7eb;
        margin-bottom: 1.5rem;
    }

    /* Boîtes */
    .atlas-box {
        background: #0b1020;
        border-radius: 16px;
        padding: 1.1rem 1.4rem;
        border: 1px solid #1f2937;
    }

    /* Boutons */
    div.stButton > button:first-child {
        font-weight: 600;
        border-radius: 999px;
        padding: 0.6rem 1.6rem;
        border: none;
        background: linear-gradient(135deg, #6366f1, #ec4899);
        color: white;
    }

    div.stButton > button:first-child:hover {
        background: linear-gradient(135deg, #4f46e5, #db2777);
    }

    /* Badges */
    .atlas-badge {
        display: inline-block;
        padding: 0.25rem 0.7rem;
        border-radius: 999px;
        background: rgba(148, 163, 184, 0.2);
        font-size: 0.8rem;
        margin-right: 0.35rem;
        margin-bottom: 0.35rem;
    }

    /* Cartes lieux */
    .atlas-card {
        background: #020617;
        border-radius: 14px;
        padding: 0.9rem 1rem;
        border: 1px solid #1e293b;
        height: 100%;
    }

    .atlas-card-title {
        font-weight: 700;
        font-size: 1.05rem;
        margin-bottom: 0.35rem;
    }

    .atlas-card-city {
        font-size: 0.9rem;
        color: #9ca3af;
        margin-bottom: 0.4rem;
    }

    .atlas-link {
        color: #38bdf8 !important;
        text-decoration: none;
        font-weight: 500;
    }
    .atlas-link:hover {
        text-decoration: underline;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------------------------------------------
# ENTÊTE ATLAS
# -------------------------------------------------------------
st.markdown('<div class="atlas-title">ATLAS</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="atlas-subtitle">Crée un itinéraire inspirant et personnalisé en quelques secondes.</div>',
    unsafe_allow_html=True,
)

# -------------------------------------------------------------
# CHARGEMENT DES DONNÉES
# -------------------------------------------------------------
@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_excel("data.xlsx")
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("/", "_")
        .str.replace("-", "_")
    )
    return df


df = load_data()

# colonnes possibles
note_col_candidates = [c for c in df.columns if "note" in c]
note_col = note_col_candidates[0] if note_col_candidates else None

image_col = None
for candidate in ["lien_images", "image_url", "photo", "image"]:
    if candidate in df.columns:
        image_col = candidate
        break

# -------------------------------------------------------------
# UI – CHOIX PAYS & CATÉGORIE
# -------------------------------------------------------------
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="atlas-box">', unsafe_allow_html=True)
        pays = st.selectbox("🌍 Choisissez un pays :", sorted(df["pays"].unique()))
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="atlas-box">', unsafe_allow_html=True)
        categories = sorted(df[df["pays"] == pays]["categorie"].unique())
        categorie = st.selectbox("🎯 Choisissez une catégorie d’activité :", categories)
        st.markdown("</div>", unsafe_allow_html=True)

# Filtrage des lieux
lieux = df[(df["pays"] == pays) & (df["categorie"] == categorie)]

if lieux.empty:
    st.error("Aucun lieu trouvé pour cette combinaison.")
else:
    st.success(f"🔎 {len(lieux)} lieu(x) trouvé(s)")

# -------------------------------------------------------------
# FONCTIONS UTILITAIRES
# -------------------------------------------------------------
def construire_prompt(pays: str, categorie: str, lieux_df: pd.DataFrame) -> str:
    """Construit le prompt à envoyer au modèle Groq."""
    lignes = []
    for _, row in lieux_df.iterrows():
        nom = row.get("nom_lieu", "Lieu")
        ville = row.get("ville", "")
        prix = row.get("prix", "")
        note = row.get(note_col, "") if note_col else ""
        ideal = row.get("ideal_pour", "")
        url_resa = row.get("url_reservation", "")

        ligne = f"- **{nom}** ({ville})"
        if prix != "":
            ligne += f" — {prix}€"
        if note != "":
            ligne += f" — ⭐ {note}/5"
        if ideal:
            ligne += f" — Idéal pour : {ideal}"
        if u

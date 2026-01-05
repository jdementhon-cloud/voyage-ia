import streamlit as st
import pandas as pd
from groq import Groq
from pathlib import Path

# -------------------------------------------------------------
# CONFIG
# -------------------------------------------------------------
st.set_page_config(
    page_title="ATLAS – Générateur de séjour parfait",
    layout="wide"
)

# -------------------------------------------------------------
# CSS GLOBAL — TEXTE NOIR FORCÉ
# -------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800;900&display=swap');

    /* RESET GLOBAL */
    * {
        font-family: 'Montserrat', sans-serif !important;
        color: #000000 !important;
    }

    body, .stApp {
        background-color: #F7EDE2 !important;
    }

    /* CONTENEUR */
    .block-container {
        max-width: 1200px;
        padding-top: 2.5rem;
        padding-bottom: 3rem;
    }

    /* TITRES */
    .atlas-title {
        font-size: 3.3rem;
        font-weight: 900;
        letter-spacing: -0.03em;
        color: #BF5A4E !important;
        margin-bottom: 0.2rem;
    }

    .atlas-subtitle {
        font-size: 1.05rem;
        color: #374151 !important;
        margin-bottom: 2rem;
        font-weight: 500;
    }

    /* CARTES */
    .atlas-box,
    .atlas-card {
        background: #ffffff !important;
        border-radius: 18px;
        padding: 1.2rem;
        border: 1px solid #e5e7eb;
        box-shadow: 0 12px 30px rgba(0,0,0,0.08);
    }

    .atlas-card-title {
        font-size: 1.05rem;
        font-weight: 800;
        margin-top: 0.6rem;
    }

    .atlas-card-city {
        font-size: 0.9rem;
        color: #374151 !important;
        margin-bottom: 0.4rem;
    }

    /* BADGES */
    .atlas-badge {
        display: inline-block;
        padding: 0.25rem 0.7rem;
        border-radius: 999px;
        background: rgba(191,90,78,0.15);
        border: 1px solid rgba(191,90,78,0.35);
        font-size: 0.75rem;
        font-weight: 600;
    }

    /* LIENS */
    a.atlas-link {
        color: #BF5A4E !important;
        font-weight: 700;
        text-decoration: none;
    }

    a.atlas-link:hover {
        text-decoration: underline;
    }

    /* BOUTONS */
    button {
        background-color: #BF5A4E !important;
        color: #ffffff !important;
        border-radius: 999px !important;
        font-weight: 800 !important;
        border: none !important;
        padding: 0.65rem 1.6rem !important;
    }

    /* SELECT / INPUT */
    input, textarea {
        color: #000000 !important;
    }

    div[data-baseweb="select"] * {
        color: #000000 !important;
    }

    div[data-baseweb="select"] {
        background: #ffffff !important;
        border-radius: 14px !important;
        border: 1px solid #e5e7eb !important;
    }

    label {
        color: #000000 !important;
        font-weight: 600;
    }

    /* ALERTES */
    .stAlert * {
        color: #000000 !important;
    }

    img {
        border-radius: 14px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------------------------------------------
# HEADER AVEC LOGO
# -------------------------------------------------------------
logo_path = Path(__file__).parent / "assets" / "logo_atlas.png"

col_logo, col_title = st.columns([2, 7], vertical_alignment="center")

with col_logo:
    if logo_path.exists():
        st.image(str(logo_path), width=130)

with col_title:
    st.markdown('<div class="atlas-title">ATLAS</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="atlas-subtitle">Voyager mieux, sans réfléchir plus.</div>',
        unsafe_allow_html=True,
    )

# -------------------------------------------------------------
# DATA
# -------------------------------------------------------------
@st.cache_data
def load_data():
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

note_col = next((c for c in df.columns if "note" in c), None)
image_col = next((c for c in ["lien_images", "image_url", "photo", "image"] if c in df.columns), None)

# -------------------------------------------------------------
# FILTRES
# -------------------------------------------------------------
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

lieux = df[(df["pays"] == pays) & (df["categorie"] == categorie)]

if lieux.empty:
    st.error("Aucun lieu trouvé pour cette combinaison.")
else:
    st.success(f"🔎 {len(lieux)} lieu(x) trouvé(s)")

# -------------------------------------------------------------
# LIEUX
# -------------------------------------------------------------
st.markdown("## 📍 Vos lieux sélectionnés")

cols = st.columns(3)
for i, (_, row) in enumerate(lieux.iterrows()):
    with cols[i % 3]:
        st.markdown('<div class="atlas-card">', unsafe_allow_html=True)

        if image_col and pd.notna(row.get(image_col)):
            st.image(row[image_col], use_column_width=True)

        st.markdown(
            f'<div class="atlas-card-title">{row.get("nom_lieu","Lieu")}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="atlas-card-city">{row.get("ville","")}</div>',
            unsafe_allow_html=True,
        )

        if note_col and row.get(note_col):
            st.markdown(
                f'<span class="atlas-badge">⭐ {row[note_col]}/5</span>',
                unsafe_allow_html=True,
            )

        if row.get("url_reservation"):
            st.markdown(
                f'<p><a class="atlas-link" href="{row["url_reservation"]}" target="_blank">🔗 Voir / réserver</a></p>',
                unsafe_allow_html=True,
            )

        st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------------------
# IA
# -------------------------------------------------------------
def construire_prompt(pays, categorie, lieux_df):
    lignes = []
    for _, row in lieux_df.iterrows():
        lignes.append(f"- {row.get('nom_lieu')} ({row.get('ville')})")
    return f"""
Crée un itinéraire de 3 jours à {pays} autour de {categorie}.
Lieux :
{chr(10).join(lignes)}
"""

def appeler_ia(prompt):
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    res = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=1800,
    )
    return res.choices[0].message.content

st.markdown("---")
if st.button("✨ Générer mon séjour parfait"):
    with st.spinner("🤖 Génération en cours…"):
        st.session_state["resultat"] = appeler_ia(
            construire_prompt(pays, categorie, lieux)
        )

if "resultat" in st.session_state:
    st.markdown("## 🧳 Votre séjour personnalisé")
    st.markdown(st.session_state["resultat"])

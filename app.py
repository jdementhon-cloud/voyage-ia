import streamlit as st
import pandas as pd
from groq import Groq

# -------------------------------------------------------------
# CONFIG GLOBALE
# -------------------------------------------------------------
st.set_page_config(
    page_title="ATLAS – Générateur de séjour parfait",
    layout="wide"
)

# -------------------------------------------------------------
# STYLE (Montserrat + #BF5A4E)
# -------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800;900&display=swap');

    :root {
        --primary: #BF5A4E;
        --primary-soft: rgba(191, 90, 78, 0.12);
        --primary-border: rgba(191, 90, 78, 0.25);

        --bg: #fafafa;
        --card: #ffffff;
        --text: #1f2937;
        --muted: #6b7280;
        --border: #e5e7eb;

        --radius: 18px;
        --shadow: 0 12px 30px rgba(15, 23, 42, 0.08);
    }

    html, body, [class*="css"] {
        font-family: 'Montserrat', sans-serif;
    }

    .stApp {
        background: var(--bg);
        color: var(--text);
    }

    .block-container {
        max-width: 1200px;
        padding-top: 2.2rem;
        padding-bottom: 3rem;
    }

    .atlas-title {
        font-size: 3.2rem;
        font-weight: 900;
        letter-spacing: -0.03em;
        margin-bottom: 0.15rem;
        color: var(--primary);
    }

    .atlas-subtitle {
        font-size: 1.05rem;
        color: var(--muted);
        margin-bottom: 1.8rem;
        font-weight: 500;
    }

    .atlas-box {
        background: var(--card);
        border-radius: var(--radius);
        padding: 1.15rem 1.3rem;
        border: 1px solid var(--border);
        box-shadow: var(--shadow);
    }

    .atlas-card {
        background: var(--card);
        border-radius: var(--radius);
        padding: 1rem 1.05rem;
        border: 1px solid var(--border);
        box-shadow: var(--shadow);
        height: 100%;
    }

    .atlas-card-title {
        font-size: 1.05rem;
        font-weight: 800;
        margin-top: 0.6rem;
        margin-bottom: 0.25rem;
    }

    .atlas-card-city {
        font-size: 0.9rem;
        color: var(--muted);
        margin-bottom: 0.4rem;
        font-weight: 500;
    }

    .atlas-badge {
        display: inline-block;
        padding: 0.25rem 0.7rem;
        border-radius: 999px;
        background: var(--primary-soft);
        border: 1px solid var(--primary-border);
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 0.35rem;
        margin-bottom: 0.35rem;
    }

    .atlas-link {
        color: var(--primary) !important;
        text-decoration: none;
        font-weight: 700;
    }

    .atlas-link:hover {
        text-decoration: underline;
    }

    div.stButton > button:first-child {
        font-family: 'Montserrat', sans-serif;
        font-weight: 800;
        border-radius: 999px;
        padding: 0.65rem 1.6rem;
        border: 1px solid var(--primary-border);
        background: var(--primary);
        color: white;
        box-shadow: 0 10px 20px rgba(191, 90, 78, 0.35);
        transition: all 0.15s ease;
    }

    div.stButton > button:first-child:hover {
        filter: brightness(1.05);
        transform: translateY(-1px);
    }

    div[data-baseweb="select"] > div {
        border-radius: 14px;
        border: 1px solid var(--border);
        background: white;
    }

    img {
        border-radius: 14px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------------------------------------------
# HEADER AVEC LOGO SVG (MÉTHODE FIABLE STREAMLIT CLOUD)
# -------------------------------------------------------------
col_logo, col_title = st.columns([1, 8], vertical_alignment="center")

with col_logo:
    st.image("assets/logo_atlas.svg", width=60)

with col_title:
    st.markdown('<div class="atlas-title">ATLAS</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="atlas-subtitle">Voyager mieux, sans réfléchir plus.</div>',
        unsafe_allow_html=True,
    )

# -------------------------------------------------------------
# CHARGEMENT DES DONNÉES
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

image_col = next(
    (c for c in ["lien_images", "image_url", "photo", "image"] if c in df.columns),
    None,
)

# -------------------------------------------------------------
# UI – CHOIX PAYS & CATÉGORIE
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
# PROMPT IA
# -------------------------------------------------------------
def construire_prompt(pays, categorie, lieux_df):
    lignes = []
    for _, row in lieux_df.iterrows():
        ligne = f"- **{row.get('nom_lieu','Lieu')}** ({row.get('ville','')})"
        if note_col and row.get(note_col):
            ligne += f" — ⭐ {row[note_col]}/5"
        lignes.append(ligne)

    return f"""
Tu es un expert en voyages.

Crée un itinéraire **de 3 jours** à **{pays}** autour de **{categorie}**.

Lieux disponibles :
{chr(10).join(lignes)}

Structure par jour, conseils pratiques, ton chaleureux.
"""


def appeler_ia(prompt):
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "Tu es un expert des voyages haut de gamme."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=1800,
    )
    return completion.choices[0].message.content

# -------------------------------------------------------------
# AFFICHAGE DES LIEUX
# -------------------------------------------------------------
st.markdown("### 📍 Vos lieux sélectionnés")

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

        st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------------------
# GÉNÉRATION IA
# -------------------------------------------------------------
st.markdown("---")
st.markdown("## 🧠 Générer un séjour parfait")

if st.button("✨ Générer mon séjour parfait"):
    with st.spinner("🤖 Génération en cours…"):
        resultat = appeler_ia(construire_prompt(pays, categorie, lieux))
        st.session_state["resultat"] = resultat

if "resultat" in st.session_state:
    st.markdown("### 🧳 Votre séjour personnalisé")
    st.markdown(st.session_state["resultat"])

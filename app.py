import streamlit as st
import pandas as pd
from groq import Groq

# --------------------------------------------------
# CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="ATLAS – Générateur de séjour",
    layout="wide",
)

st.markdown(
    """
    <style>
    .atlas-title {
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
        background: linear-gradient(90deg, #6366f1, #ec4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .atlas-subtitle {
        color: #6b7280;
        margin-bottom: 2rem;
    }
    .lieu-card {
        background: #0f172a;
        border-radius: 14px;
        padding: 1rem;
        border: 1px solid #1e293b;
        height: 100%;
    }
    .lieu-title {
        font-weight: 700;
        font-size: 1.05rem;
        margin-top: 0.5rem;
    }
    .lieu-city {
        font-size: 0.9rem;
        color: #9ca3af;
        margin-bottom: 0.4rem;
    }
    a {
        color: #38bdf8;
        text-decoration: none;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.markdown('<div class="atlas-title">ATLAS</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="atlas-subtitle">Crée un séjour sur-mesure, inspirant et concret.</div>',
    unsafe_allow_html=True,
)

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_excel("data.xlsx")
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("-", "_")
        .str.replace("/", "_")
    )
    return df


df = load_data()

# Colonnes utiles
image_col = None
for c in ["image_url", "lien_images", "photo", "image"]:
    if c in df.columns:
        image_col = c
        break

note_col = next((c for c in df.columns if "note" in c), None)

# --------------------------------------------------
# UI – SELECTEURS
# --------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    pays = st.selectbox("🌍 Choisissez un pays", sorted(df["pays"].unique()))

with col2:
    categories = sorted(df[df["pays"] == pays]["categorie"].unique())
    categorie = st.selectbox("🎯 Choisissez une catégorie", categories)

lieux = df[(df["pays"] == pays) & (df["categorie"] == categorie)]

if lieux.empty:
    st.warning("Aucun lieu trouvé pour cette sélection.")
else:
    st.success(f"{len(lieux)} lieu(x) trouvé(s)")

# --------------------------------------------------
# AFFICHAGE DES LIEUX (PHOTOS + INFOS)
# --------------------------------------------------
st.markdown("### 📍 Lieux disponibles")

cols = st.columns(3)
for i, (_, row) in enumerate(lieux.iterrows()):
    with cols[i % 3]:
        st.markdown('<div class="lieu-card">', unsafe_allow_html=True)

        if image_col and pd.notna(row.get(image_col)):
            st.image(row[image_col], use_column_width=True)

        st.markdown(
            f'<div class="lieu-title">{row.get("nom_lieu","Lieu")}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="lieu-city">{row.get("ville","")}</div>',
            unsafe_allow_html=True,
        )

        if note_col and pd.notna(row.get(note_col)):
            st.markdown(f"⭐ {row[note_col]}/5")

        if pd.notna(row.get("ideal_pour", None)):
            st.markdown(f"🎯 {row['ideal_pour']}")

        if pd.notna(row.get("url_reservation", None)):
            st.markdown(
                f"[🔗 Voir / réserver]({row['url_reservation']})",
                unsafe_allow_html=True,
            )

        st.markdown("</div>", unsafe_allow_html=True)

# --------------------------------------------------
# PROMPT IA
# --------------------------------------------------
def construire_prompt(pays, categorie, lieux_df):
    description = ""
    for _, row in lieux_df.iterrows():
        description += (
            f"- {row.get('nom_lieu')} ({row.get('ville')})\n"
            f"  Réservation : {row.get('url_reservation','')}\n"
        )

    return f"""
Tu es un expert en organisation de voyages.

Crée un **itinéraire détaillé de 3 jours** à **{pays}**,
autour de la thématique **{categorie}**.

Voici les lieux à intégrer dans l’itinéraire :

{description}

Contraintes :
- Chaque jour doit inclure au moins un des lieux listés
- Indique clairement les journées (Jour 1, Jour 2, Jour 3)
- Intègre naturellement les lieux dans le récit
- Donne des conseils pratiques (rythme, moment de la journée)
- À la fin, fais une section **🔗 Liens de réservation** listant tous les liens

Ton style doit être clair, inspirant et concret.
"""

# --------------------------------------------------
# APPEL IA
# --------------------------------------------------
def generer_sejour(prompt):
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "Tu es un expert en voyages."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=1600,
    )
    return completion.choices[0].message.content


# --------------------------------------------------
# BOUTON GÉNÉRATION (IMPORTANT)
# --------------------------------------------------
st.markdown("---")

if st.button("✨ Générer mon séjour", type="primary"):
    with st.spinner("ATLAS prépare votre séjour..."):
        prompt = construire_prompt(pays, categorie, lieux)
        resultat = generer_sejour(prompt)
        st.session_state["resultat"] = resultat

# --------------------------------------------------
# AFFICHAGE DU SÉJOUR
# --------------------------------------------------
if "resultat" in st.session_state:
    st.markdown("## 🧳 Votre séjour personnalisé")
    st.markdown(st.session_state["resultat"])

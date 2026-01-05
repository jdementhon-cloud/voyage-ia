import streamlit as st
import pandas as pd
from groq import Groq
from pathlib import Path

# -------------------------------------------------------------
# CONFIG
# -------------------------------------------------------------
st.set_page_config(page_title="ATLAS – Générateur de séjour parfait", layout="wide")

# -------------------------------------------------------------
# CSS
# -------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800;900&display=swap');

    :root{
      --primary:#BF5A4E;
      --bg:#F7EDE2;
      --card:#ffffff;
      --text:#111827;   /* noir doux */
      --muted:#6b7280;
      --border:#e5e7eb;
      --radius:18px;
      --shadow:0 12px 30px rgba(0,0,0,0.08);
      --hover: rgba(191,90,78,0.10);
    }

    html, body, .stApp{
      background: var(--bg) !important;
      font-family: 'Montserrat', sans-serif !important;
    }

    .block-container{
      max-width:1200px;
      padding-top:2.5rem;
      padding-bottom:3rem;
    }

    /* --------------------------------------------------
       TEXTE (y compris résultat IA)
    -------------------------------------------------- */
    .stMarkdown, .stMarkdown *,
    .stText, .stText *,
    .stCaption, .stCaption *,
    .stSubheader, .stSubheader *,
    .stHeader, .stHeader *,
    .stTitle, .stTitle * {
      color: var(--text) !important;
    }

    label, .stSelectbox label{
      color: var(--text) !important;
      font-weight: 600 !important;
    }

    /* --------------------------------------------------
       HEADER
    -------------------------------------------------- */
    .atlas-title{
      font-size:3.3rem;
      font-weight:900;
      letter-spacing:-0.03em;
      color: var(--primary) !important;
      margin-bottom:0.2rem;
    }
    .atlas-subtitle{
      font-size:1.05rem;
      color: #374151 !important;
      margin-bottom:2rem;
      font-weight:500;
    }

    /* Cards / boxes */
    .atlas-box, .atlas-card{
      background: var(--card) !important;
      border-radius: var(--radius);
      padding: 1.2rem;
      border: 1px solid var(--border);
      box-shadow: var(--shadow);
    }

    .atlas-card-title{
      font-size:1.05rem;
      font-weight:800;
      margin-top:0.6rem;
      margin-bottom:0.25rem;
      color: var(--text) !important;
    }
    .atlas-card-city{
      font-size:0.9rem;
      color: #374151 !important;
      margin-bottom:0.4rem;
      font-weight:500;
    }

    .atlas-badge{
      display:inline-block;
      padding:0.25rem 0.7rem;
      border-radius:999px;
      background: rgba(191,90,78,0.15);
      border: 1px solid rgba(191,90,78,0.35);
      font-size:0.75rem;
      font-weight:600;
      color: var(--text) !important;
      margin-right:0.35rem;
      margin-bottom:0.35rem;
    }

    a.atlas-link{
      color: var(--primary) !important;
      font-weight:700;
      text-decoration:none;
    }
    a.atlas-link:hover{ text-decoration:underline; }

    /* Buttons */
    div.stButton > button{
      background: var(--primary) !important;
      color: #ffffff !important;
      border-radius:999px !important;
      font-weight:800 !important;
      border:none !important;
      padding:0.65rem 1.6rem !important;
    }

    /* --------------------------------------------------
       ✅ SELECTBOX : NOIR SUR BLANC (CONTROL + DROPDOWN)
       On cible BaseWeb très explicitement + portal/popover/menu
    -------------------------------------------------- */

    /* CONTROL (le champ visible) */
    div[data-baseweb="select"] > div{
      background: #ffffff !important;
      border: 1px solid var(--border) !important;
      border-radius: 14px !important;
      box-shadow: none !important;
    }

    /* Valeur sélectionnée / input */
    div[data-baseweb="select"] span,
    div[data-baseweb="select"] input{
      color: var(--text) !important;
      -webkit-text-fill-color: var(--text) !important;
      background: transparent !important;
    }

    /* Placeholder (évite blanc sur blanc) */
    div[data-baseweb="select"] [data-baseweb="select"] span[aria-hidden="true"],
    div[data-baseweb="select"] span[aria-hidden="true"]{
      color: var(--muted) !important;
      -webkit-text-fill-color: var(--muted) !important;
    }

    /* Chevron (flèche) */
    div[data-baseweb="select"] svg{
      fill: var(--text) !important;
    }

    /* DROPDOWN — BaseWeb popover/menu (portal) */
    div[data-baseweb="popover"],
    div[data-baseweb="popover"] > div{
      background: #ffffff !important;
      color: var(--text) !important;
      border-radius: 14px !important;
    }

    div[data-baseweb="menu"]{
      background: #ffffff !important;
      color: var(--text) !important;
      border: 1px solid var(--border) !important;
      border-radius: 14px !important;
      box-shadow: 0 18px 40px rgba(0,0,0,0.18) !important;
      overflow: hidden !important;
    }

    /* Items du menu */
    div[data-baseweb="menu"] *{
      background: #ffffff !important;
      color: var(--text) !important;
    }

    /* Hover / option active */
    div[data-baseweb="menu"] [role="option"]:hover{
      background: var(--hover) !important;
      color: var(--text) !important;
    }

    /* Fallback selon versions : listbox */
    [role="listbox"], [role="listbox"] *{
      background: #ffffff !important;
      color: var(--text) !important;
    }
    [role="listbox"] [role="option"]:hover{
      background: var(--hover) !important;
    }

    /* Images */
    img{ border-radius:14px; }

    /* Alerts */
    .stAlert, .stAlert * { color: var(--text) !important; }

    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------------------------------------------
# HEADER (logo PNG)
# -------------------------------------------------------------
logo_path = Path(__file__).parent / "assets" / "logo_atlas.png"

col_logo, col_title = st.columns([2, 7], vertical_alignment="center")
with col_logo:
    if logo_path.exists():
        st.image(str(logo_path), width=130)
    else:
        st.warning("Logo introuvable : assets/logo_atlas.png")

with col_title:
    st.markdown('<div class="atlas-title">ATLAS</div>', unsafe_allow_html=True)
    st.markdown('<div class="atlas-subtitle">Voyager mieux, sans réfléchir plus.</div>', unsafe_allow_html=True)

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

        st.markdown(f'<div class="atlas-card-title">{row.get("nom_lieu","Lieu")}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="atlas-card-city">{row.get("ville","")}</div>', unsafe_allow_html=True)

        if note_col and row.get(note_col):
            st.markdown(f'<span class="atlas-badge">⭐ {row[note_col]}/5</span>', unsafe_allow_html=True)

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
        nom = row.get("nom_lieu", "Lieu")
        ville = row.get("ville", "")
        note = row.get(note_col, "") if note_col else ""
        url = row.get("url_reservation", "")

        line = f"- {nom} ({ville})"
        if note != "":
            line += f" — ⭐ {note}/5"
        if url:
            line += f"\n  🔗 Réservation : {url}"
        lignes.append(line)

    return f"""
Tu es un expert en voyages.

Crée un itinéraire inspirant et réaliste de 3 jours à {pays}, centré sur {categorie}.

Lieux disponibles :
{chr(10).join(lignes)}

Format : Jour 1 / Jour 2 / Jour 3 + conseils pratiques + conclusion.
Ton chaleureux, précis, rassurant.
"""

def appeler_ia(prompt: str) -> str:
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

st.markdown("---")
st.markdown("## 🧠 Générer un séjour parfait")

if st.button("✨ Générer mon séjour parfait"):
    if lieux.empty:
        st.error("Impossible de générer un séjour : aucun lieu pour cette sélection.")
    else:
        with st.spinner("🤖 Génération en cours…"):
            st.session_state["resultat"] = appeler_ia(construire_prompt(pays, categorie, lieux))

if "resultat" in st.session_state:
    st.markdown("## 🧳 Votre séjour personnalisé")
    st.markdown(st.session_state["resultat"])

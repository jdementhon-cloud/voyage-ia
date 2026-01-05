import streamlit as st
import pandas as pd
from groq import Groq

# -------------------------------------------------------------
# CONFIG GLOBALE
# -------------------------------------------------------------
st.set_page_config(page_title="ATLAS – Générateur de séjour parfait", layout="wide")

# -------------------------------------------------------------
# STYLE (Montserrat + couleur principale #BF5A4E)
# -------------------------------------------------------------
st.markdown(
    """
    <style>
    /* --------------------------------------------------
       IMPORT FONT
    -------------------------------------------------- */
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800;900&display=swap');

    /* --------------------------------------------------
       VARIABLES
    -------------------------------------------------- */
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

    /* --------------------------------------------------
       BASE
    -------------------------------------------------- */
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

    /* --------------------------------------------------
       TITRES
    -------------------------------------------------- */
    .atlas-title {
        font-size: 3.2rem;
        font-weight: 900;
        letter-spacing: -0.03em;
        margin-bottom: 0.2rem;
        color: var(--primary);
    }

    .atlas-subtitle {
        font-size: 1.05rem;
        color: var(--muted);
        margin-bottom: 1.8rem;
        font-weight: 500;
    }

    /* --------------------------------------------------
       BOX / CARDS
    -------------------------------------------------- */
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
        margin-top: 0.7rem;
        margin-bottom: 0.25rem;
        color: var(--text);
    }

    .atlas-card-city {
        font-size: 0.9rem;
        color: var(--muted);
        margin-bottom: 0.4rem;
        font-weight: 500;
    }

    /* --------------------------------------------------
       BADGES
    -------------------------------------------------- */
    .atlas-badge {
        display: inline-block;
        padding: 0.25rem 0.7rem;
        border-radius: 999px;
        background: var(--primary-soft);
        border: 1px solid var(--primary-border);
        color: var(--text);
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 0.35rem;
        margin-bottom: 0.35rem;
    }

    /* --------------------------------------------------
       LIENS
    -------------------------------------------------- */
    .atlas-link {
        color: var(--primary) !important;
        text-decoration: none;
        font-weight: 700;
    }

    .atlas-link:hover {
        text-decoration: underline;
    }

    /* --------------------------------------------------
       BOUTONS
    -------------------------------------------------- */
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

    div.stButton > button:first-child:active {
        transform: translateY(0);
    }

    /* --------------------------------------------------
       INPUTS
    -------------------------------------------------- */
    div[data-baseweb="select"] > div {
        font-family: 'Montserrat', sans-serif;
        border-radius: 14px;
        border: 1px solid var(--border);
        background: white;
    }

    /* --------------------------------------------------
       IMAGES
    -------------------------------------------------- */
    img {
        border-radius: 14px;
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
    '<div class="atlas-subtitle">Voyager mieux, sans réfléchir plus.</div>',
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
        if url_resa:
            ligne += f"\n  🔗 Réservation : {url_resa}"
        lignes.append(ligne)

    texte_lieux = "\n".join(lignes)

    prompt = f"""
Tu es un expert en voyages et créateur d'itinéraires sur-mesure.

Crée un **itinéraire inspirant et réaliste de 3 jours** à **{pays}**, centré sur la catégorie d’activités **{categorie}**.

Voici la liste des lieux à intégrer (au minimum quelques-uns dans l’itinéraire) :

{texte_lieux}

### FORMAT ATTENDU

- Présente ton résultat en sections claires :
  - **Jour 1** : programme détaillé, rythme de la journée, visites, pauses, ambiance.
  - **Jour 2** : idem.
  - **Jour 3** : idem.
- Indique explicitement quand l’un des lieux listés est utilisé (par son nom).
- Donne quelques conseils pratiques : horaires recommandés, durée sur place, ambiance, budget.
- Termine par une courte conclusion qui donne envie de partir.

Le ton doit être chaleureux, précis, rassurant, mais pas trop long.
"""
    return prompt.strip()


def appeler_ia(prompt: str) -> str:
    """Appel à l'API Groq avec le modèle llama-3.1-8b-instant."""
    try:
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
    except Exception as e:
        return f"❌ Erreur lors de l’appel à l’IA : {e}"

# -------------------------------------------------------------
# AFFICHAGE DES LIEUX (PHOTOS, SANS CARTE)
# -------------------------------------------------------------
st.markdown("### 📍 Vos lieux sélectionnés")

if not lieux.empty:
    st.markdown("### ✨ Suggestions de spots")

    cols = st.columns(3)
    for i, (_, row) in enumerate(lieux.iterrows()):
        with cols[i % 3]:
            st.markdown('<div class="atlas-card">', unsafe_allow_html=True)

            nom = row.get("nom_lieu", "Lieu")
            ville = row.get("ville", "")
            note = row.get(note_col, None) if note_col else None
            ideal = row.get("ideal_pour", "")
            url_resa = row.get("url_reservation", "")

            # Image
            if image_col and pd.notna(row.get(image_col, None)):
                try:
                    st.image(row[image_col], use_column_width=True)
                except Exception:
                    pass

            st.markdown(f'<div class="atlas-card-title">{nom}</div>', unsafe_allow_html=True)
            if ville:
                st.markdown(
                    f'<div class="atlas-card-city">{ville}</div>', unsafe_allow_html=True
                )

            # Badges
            if note not in [None, ""]:
                st.markdown(
                    f'<span class="atlas-badge">⭐ {note}/5</span>',
                    unsafe_allow_html=True,
                )
            if ideal:
                st.markdown(
                    f'<span class="atlas-badge">🎯 {ideal}</span>',
                    unsafe_allow_html=True,
                )

            if url_resa:
                st.markdown(
                    f'<p><a class="atlas-link" href="{url_resa}" target="_blank">🔗 Voir la page / réserver</a></p>',
                    unsafe_allow_html=True,
                )

            st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------------------
# GÉNÉRATION DU SÉJOUR AVEC L’IA (SANS PDF)
# -------------------------------------------------------------
st.markdown("---")
st.markdown("## 🧠 Générer un séjour parfait avec ATLAS")

col_button, _ = st.columns([1, 3])
with col_button:
    lancer = st.button("✨ Générer mon séjour parfait")

if lancer and lieux.empty:
    st.error("Impossible de générer un séjour : aucun lieu pour cette sélection.")
elif lancer:
    with st.spinner("🤖 L’IA prépare votre séjour, un instant…"):
        prompt = construire_prompt(pays, categorie, lieux)
        resultat = appeler_ia(prompt)
        st.session_state["atlas_resultat"] = resultat

# Affichage du résultat
if "atlas_resultat" in st.session_state:
    st.markdown("### 🧳 Votre séjour personnalisé")
    st.markdown(st.session_state["atlas_resultat"])

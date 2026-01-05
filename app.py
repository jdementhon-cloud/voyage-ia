import streamlit as st
st.error("✅ NOUVELLE VERSION EN LIGNE — SANS PDF / SANS CARTE")
import pandas as pd
from groq import Groq

# Marqueur pour vérifier que c'est bien CE fichier qui tourne
st.write("✅ ATLAS — VERSION SANS PDF NI CARTE")

# -------------------------------------------------------------
# CONFIG GLOBALE
# -------------------------------------------------------------
st.set_page_config(page_title="ATLAS – Générateur de séjour parfait", layout="wide")

# Petit thème custom
st.markdown(
    """
    <style>
    body { background: #050816; color: #f5f5f5; }

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

    .atlas-box {
        background: #0b1020;
        border-radius: 16px;
        padding: 1.1rem 1.4rem;
        border: 1px solid #1f2937;
    }

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

    .atlas-badge {
        display: inline-block;
        padding: 0.25rem 0.7rem;
        border-radius: 999px;
        background: rgba(148, 163, 184, 0.2);
        font-size: 0.8rem;
        margin-right: 0.35rem;
        margin-bottom: 0.35rem;
    }

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
    .atlas-link:hover { text-decoration: underline; }
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

lieux = df[(df["pays"] == pays) & (df["categorie"] == categorie)]

if lieux.empty:
    st.error("Aucun lieu trouvé pour cette combinaison.")
else:
    st.success(f"🔎 {len(lieux)} lieu(x) trouvé(s)")

# -------------------------------------------------------------
# FONCTIONS UTILITAIRES
# -------------------------------------------------------------
def construire_prompt(pays: str, categorie: str, lieux_df: pd.DataFrame) -> str:
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

    return f"""
Tu es un expert en voyages et créateur d'itinéraires sur-mesure.

Crée un **itinéraire inspirant et réaliste de 3 jours** à **{pays}**, centré sur la catégorie d’activités **{categorie}**.

Voici la liste des lieux à intégrer (au minimum quelques-uns dans l’itinéraire) :

{texte_lieux}

### FORMAT ATTENDU
- **Jour 1**, **Jour 2**, **Jour 3** : programme détaillé, rythme, pauses, ambiance.
- Indique explicitement quand un lieu listé est utilisé (par son nom).
- Conseils pratiques : horaires, durée, ambiance, budget.
- Conclusion courte qui donne envie de partir.

Ton chaleureux, précis, rassurant, pas trop long.
""".strip()

def appeler_ia(prompt: str) -> str:
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
# AFFICHAGE DES LIEUX (SANS CARTE)
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

            if image_col and pd.notna(row.get(image_col, None)):
                try:
                    st.image(row[image_col], use_column_width=True)
                except Exception:
                    pass

            st.markdown(f'<div class="atlas-card-title">{nom}</div>', unsafe_allow_html=True)
            if ville:
                st.markdown(f'<div class="atlas-card-city">{ville}</div>', unsafe_allow_html=True)

            if note not in [None, ""]:
                st.markdown(f'<span class="atlas-badge">⭐ {note}/5</span>', unsafe_allow_html=True)
            if ideal:
                st.markdown(f'<span class="atlas-badge">🎯 {ideal}</span>', unsafe_allow_html=True)

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
        st.session_state["atlas_resultat"] = appeler_ia(prompt)

if "atlas_resultat" in st.session_state:
    st.markdown("### 🧳 Votre séjour personnalisé")
    st.markdown(st.session_state["atlas_resultat"])

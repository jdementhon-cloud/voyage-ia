import streamlit as st
import pandas as pd
from groq import Groq
from fpdf import FPDF
import io

# ======================================================
# CONFIG GLOBALE
# ======================================================
st.set_page_config(
    page_title="ATLAS – Générateur de séjour parfait",
    page_icon="🌍",
    layout="wide",
)

# Petit header stylé
st.markdown(
    """
    <style>
    .atlas-title {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        font-size: 42px;
        font-weight: 800;
        margin-bottom: 0.25rem;
    }
    .atlas-subtitle {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        font-size: 16px;
        color: #666;
        margin-bottom: 1.5rem;
    }
    .atlas-pill {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 999px;
        background: linear-gradient(90deg, #7C3AED, #06B6D4);
        color: white;
        font-size: 11px;
        letter-spacing: .08em;
        text-transform: uppercase;
        margin-bottom: 0.5rem;
    }
    .atlas-card {
        border-radius: 14px;
        padding: 1rem 1.25rem;
        background: rgba(255,255,255,0.85);
        box-shadow: 0 10px 30px rgba(15,23,42,0.08);
        border: 1px solid rgba(148,163,184,0.25);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="atlas-pill">ATLAS</div>', unsafe_allow_html=True)
st.markdown('<div class="atlas-title">Générateur de séjour parfait (IA)</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="atlas-subtitle">Crée un itinéraire personnalisé à partir de ta base de données voyage.</div>',
    unsafe_allow_html=True,
)

# ======================================================
# CHARGEMENT DES DONNÉES
# ======================================================
@st.cache_data
def load_data():
    df = pd.read_excel("data.xlsx")
    # Normalisation des noms de colonnes
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("/", "_")
        .str.replace("-", "_")
    )
    return df


df = load_data()

# Helper debug (optionnel)
with st.expander("🔍 Colonnes détectées :", expanded=False):
    st.write(list(df.columns))

# Détection de la colonne de note
note_col_candidates = [c for c in df.columns if "note" in c]
note_col = note_col_candidates[0] if note_col_candidates else None

# Vérifications minimum
required_cols = ["pays", "ville", "nom_lieu", "categorie", "url_reservation"]
missing = [c for c in required_cols if c not in df.columns]
if missing:
    st.error(f"Colonnes manquantes dans data.xlsx : {missing}")
    st.stop()

# ======================================================
# UI : CHOIX PAYS + CATÉGORIE
# ======================================================
with st.container():
    col_pays, col_cat = st.columns(2)

    with col_pays:
        pays = st.selectbox(
            "🌍 Choisissez un pays :",
            sorted(df["pays"].dropna().unique()),
        )

    # Filtrer les catégories disponibles pour ce pays
    categories_dispo = (
        df[df["pays"] == pays]["categorie"].dropna().sort_values().unique()
    )

    with col_cat:
        categorie = st.selectbox(
            "🍀 Choisissez une catégorie d’activité :",
            categories_dispo,
        )

# Lieux filtrés
lieux = df[(df["pays"] == pays) & (df["categorie"] == categorie)]

if lieux.empty:
    st.warning("Aucun lieu trouvé pour cette combinaison pays + catégorie.")
    st.stop()
else:
    st.success(f"🔎 {len(lieux)} lieu(x) trouvé(s) pour ce combo.")

# ======================================================
# AFFICHAGE DES LIEUX (AVEC IMAGES)
# ======================================================
st.markdown("### 📍 Lieux sélectionnés")

has_image_col = "lien_images" in df.columns

# On limite l'affichage détaillé à 6 lieux pour l'esthétique
subset_lieux = lieux.head(6)

cards_cols = st.columns(3)
for idx, (_, row) in enumerate(subset_lieux.iterrows()):
    col = cards_cols[idx % 3]
    with col:
        st.markdown('<div class="atlas-card">', unsafe_allow_html=True)
        # Image si dispo
        if has_image_col and pd.notna(row["lien_images"]):
            try:
                st.image(
                    row["lien_images"],
                    use_column_width=True,
                )
            except Exception:
                pass
        st.markdown(f"**{row['nom_lieu']}** — {row['ville']}")
        if note_col and pd.notna(row[note_col]):
            st.markdown(f"⭐ **{row[note_col]}/5**")
        if "prix" in df.columns and pd.notna(row.get("prix", None)):
            st.markdown(f"💶 Prix indicatif : {row['prix']}")
        if "ideal_pour" in df.columns and pd.notna(row.get("ideal_pour", None)):
            st.markdown(f"🎯 Idéal pour : {row['ideal_pour']}")
        if pd.notna(row["url_reservation"]):
            st.markdown(f"[🔗 Réserver]({row['url_reservation']})")
        st.markdown("</div>", unsafe_allow_html=True)

st.divider()

# ======================================================
# CONSTRUCTION DU PROMPT IA
# ======================================================
def construire_prompt(pays: str, categorie: str, lieux_df: pd.DataFrame) -> str:
    """Construit le message envoyé à l'IA à partir des lieux filtrés."""
    texte = ""

    for _, row in lieux_df.iterrows():
        texte += f"- **{row['nom_lieu']}** à **{row['ville']}**\n"
        if note_col and pd.notna(row[note_col]):
            texte += f"  Note : {row[note_col]}/5\n"
        if "ideal_pour" in lieux_df.columns and pd.notna(row.get("ideal_pour", None)):
            texte += f"  Ideal pour : {row['ideal_pour']}\n"
        if pd.notna(row["url_reservation"]):
            texte += f"  Lien de reservation : {row['url_reservation']}\n"
        texte += "\n"

    prompt = f"""
Tu es un expert en organisation de voyages haut de gamme.

Crée un **itinéraire complet et réaliste de 3 jours** à **{pays}**, centré sur la catégorie d’activités **{categorie}**.

### Lieux à intégrer dans le séjour :

{texte}

### FORMAT ATTENDU :

- Jour 1 : programme détaillé (matin, après-midi, soir), avec au moins un des lieux ci-dessus
- Jour 2 : programme détaillé avec au moins un des lieux
- Jour 3 : programme détaillé avec au moins un des lieux
- Pour chaque jour, explique pourquoi les lieux choisis sont intéressants
- Ajoute des conseils pratiques (horaires, durée, ambiance, type de public)
- Termine par une section :

Liens de reservation recommends (reprends les liens fournis).

Style chaleureux, inspirant, premium, clair et structuré.
"""
    return prompt


# ======================================================
# APPEL GROQ
# ======================================================
def generer_sejour(prompt: str) -> str:
    """Appelle l'API Groq pour générer le texte du séjour."""
    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])

        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": "Tu es un travel designer qui conçoit des séjours sur-mesure.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=1700,
        )

        return completion.choices[0].message.content

    except Exception as e:
        return f"Erreur API : {e}"


# ======================================================
# OUTILS PDF – VERSION SÉCURISÉE (SANS UNICODE)
# ======================================================
def to_latin1(text: str) -> str:
    """
    FPDF ne supporte que latin-1.
    On enlève donc tous les caractères non compatibles (emojis, etc.).
    """
    if text is None:
        return ""
    return text.encode("latin-1", "ignore").decode("latin-1")


def creer_pdf(contenu: str, titre: str) -> bytes:
    """Crée un PDF en mémoire à partir du texte généré (latin-1 only)."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    titre_safe = to_latin1(titre)
    contenu_safe = to_latin1(contenu)

    pdf.set_title(titre_safe)

    # Titre
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, titre_safe, ln=True)
    pdf.ln(4)

    # Corps
    pdf.set_font("Helvetica", "", 11)
    for line in contenu_safe.split("\n"):
        pdf.multi_cell(0, 6, line)

    # Retour en bytes
    return pdf.output(dest="S").encode("latin-1", "ignore")


# ======================================================
# BOUTON : GÉNÉRER LE SÉJOUR
# ======================================================
if "atlas_resultat" not in st.session_state:
    st.session_state["atlas_resultat"] = None
    st.session_state["atlas_texte_pdf"] = None

st.markdown("### ✨ Génération du séjour")

generer = st.button(
    "✨ Générer mon séjour parfait",
    use_container_width=True,
    type="primary",
)

if generer:
    with st.spinner("🤖 ATLAS prépare ton itinéraire sur-mesure…"):
        prompt = construire_prompt(pays, categorie, lieux)
        resultat = generer_sejour(prompt)

    st.session_state["atlas_resultat"] = resultat

    # Texte à injecter dans le PDF (sans emojis)
    liens_txt = ""
    for _, row in lieux.iterrows():
        if pd.notna(row["url_reservation"]):
            liens_txt += f"- {row['nom_lieu']} ({row['ville']}) : {row['url_reservation']}\n"

    texte_pdf = (
        f"ATLAS – Séjour à {pays} ({categorie})\n\n"
        + resultat
        + "\n\n-----------------------------\n"
        + "Liens de reservation issus de la base :\n"
        + liens_txt
    )
    st.session_state["atlas_texte_pdf"] = texte_pdf

# ======================================================
# AFFICHAGE RÉSULTAT + EXPORT PDF
# ======================================================
if st.session_state["atlas_resultat"]:
    st.markdown("### 🧳 Votre séjour personnalisé")

    st.markdown('<div class="atlas-card">', unsafe_allow_html=True)
    st.markdown(st.session_state["atlas_resultat"])
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### 📄 Exporter")
    if st.session_state["atlas_texte_pdf"]:
        pdf_bytes = creer_pdf(
            st.session_state["atlas_texte_pdf"],
            f"ATLAS – Séjour {pays}",
        )
        st.download_button(
            label="📄 Télécharger le séjour en PDF",
            data=pdf_bytes,
            file_name=f"ATLAS_sejour_{pays}_{categorie}.pdf",
            mime="application/pdf",
        )
else:
    st.info("Clique sur **« Générer mon séjour parfait »** pour créer ton itinéraire.")

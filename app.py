import streamlit as st
import pandas as pd
from groq import Groq
from fpdf import FPDF
from unidecode import unidecode
import folium
from streamlit.components.v1 import html

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

# colonnes possibles
note_col_candidates = [c for c in df.columns if "note" in c]
note_col = note_col_candidates[0] if note_col_candidates else None

image_col = None
for candidate in ["lien_images", "image_url", "photo", "image"]:
    if candidate in df.columns:
        image_col = candidate
        break

lat_col = "latitude" if "latitude" in df.columns else None
lon_col = "longitude" if "longitude" in df.columns else None

# -------------------------------------------------------------
# UI – CHOIX PAYS & CATÉGORIE
# -------------------------------------------------------------
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        with st.container():
            st.markdown('<div class="atlas-box">', unsafe_allow_html=True)
            pays = st.selectbox("🌍 Choisissez un pays :", sorted(df["pays"].unique()))
            st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        with st.container():
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
def construire_prompt(pays, categorie, lieux_df):
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
    return prompt


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


def creer_pdf(contenu: str, titre: str) -> bytes:
    """Crée un PDF simple à partir d’un texte (sans accent pour compatibilité FPDF)."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Titre
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, unidecode(titre), ln=True)
    pdf.ln(5)

    # Corps
    pdf.set_font("Helvetica", "", 12)
    texte = unidecode(contenu)  # enlève les accents pour éviter les erreurs d'encodage

    for ligne in texte.split("\n"):
        l = ligne.strip()
        if not l:
            pdf.ln(4)
        else:
            pdf.multi_cell(0, 6, l)

    # Retour en bytes
    pdf_bytes = pdf.output(dest="S").encode("latin-1")
    return pdf_bytes


def afficher_carte_folium(lieux_df):
    """Affiche une carte Folium avec les lieux."""
    if lat_col is None or lon_col is None:
        st.info("🌍 Carte indisponible : aucune colonne latitude/longitude trouvée.")
        return

    sub = lieux_df.dropna(subset=[lat_col, lon_col])
    if sub.empty:
        st.info("🌍 Carte indisponible : coordonnées manquantes pour ces lieux.")
        return

    center_lat = sub[lat_col].astype(float).mean()
    center_lon = sub[lon_col].astype(float).mean()

    m = folium.Map(location=[center_lat, center_lon], zoom_start=11)

    for _, row in sub.iterrows():
        nom = row.get("nom_lieu", "Lieu")
        ville = row.get("ville", "")
        popup = f"{nom} – {ville}"
        folium.Marker(
            location=[float(row[lat_col]), float(row[lon_col])],
            popup=popup,
        ).add_to(m)

    html_data = m._repr_html_()
    html(html_data, height=420)


# -------------------------------------------------------------
# AFFICHAGE DES LIEUX (PHOTOS + CARTE)
# -------------------------------------------------------------
st.markdown("### 📍 Vos lieux sélectionnés")

if not lieux.empty:
    # Ligne de carte
    with st.container():
        st.markdown('<div class="atlas-box">', unsafe_allow_html=True)
        st.subheader("Carte des lieux")
        afficher_carte_folium(lieux)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### ✨ Suggestions de spots")

    # Affichage en grille
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
                    st.image(
                        row[image_col],
                        use_column_width=True,
                    )
                except Exception:
                    pass

            st.markdown(f'<div class="atlas-card-title">{nom}</div>', unsafe_allow_html=True)
            if ville:
                st.markdown(
                    f'<div class="atlas-card-city">{ville}</div>', unsafe_allow_html=True
                )

            # Badges
            badges = []
            if note not in [None, ""]:
                badges.append(f"⭐ {note}/5")
            if ideal:
                badges.append(f"🎯 {ideal}")
            if badges:
                for b in badges:
                    st.markdown(f'<span class="atlas-badge">{b}</span>', unsafe_allow_html=True)

            if url_resa:
                st.markdown(
                    f'<p><a class="atlas-link" href="{url_resa}" target="_blank">🔗 Voir la page / réserver</a></p>',
                    unsafe_allow_html=True,
                )

            st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------------------
# GÉNÉRATION DU SÉJOUR AVEC L’IA
# -------------------------------------------------------------
st.markdown("---")
st.markdown("## 🧠 Générer un séjour parfait avec ATLAS")

col_button, col_empty = st.columns([1, 3])
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

    # ---------------------------------------------------------
    # EXPORT PDF
    # ---------------------------------------------------------
    st.markdown("### 📄 Exporter")

    col_pdf, _ = st.columns([1, 3])
    with col_pdf:
        if st.button("📥 Télécharger en PDF"):
            texte_pdf = st.session_state["atlas_resultat"]
            titre_pdf = f"ATLAS – Séjour {pays}"
            pdf_bytes = creer_pdf(texte_pdf, titre_pdf)
            st.download_button(
                label="⬇️ Télécharger le fichier PDF",
                data=pdf_bytes,
                file_name=f"ATLAS_sejour_{pays}.pdf".replace(" ", "_"),
                mime="application/pdf",
            )

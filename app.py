# app.py — ATLAS ✨
import io
import textwrap

import pandas as pd
import streamlit as st
from groq import Groq
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


# --------------------------------------------------
# ⚙️ CONFIG GLOBALE
# --------------------------------------------------
st.set_page_config(
    page_title="ATLAS – Générateur de séjour parfait",
    page_icon="🌍",
    layout="wide",
)

# 🎨 CSS pour une interface plus jolie
st.markdown(
    """
    <style>
    /* Police & fond */
    body, .main {
        background: radial-gradient(circle at top left, #151c3c 0, #050814 45%, #020308 100%) !important;
        color: #f5f5f7;
        font-family: -apple-system, system-ui, BlinkMacSystemFont, "SF Pro Text", sans-serif;
    }
    .stApp {
        background: transparent;
    }

    /* En-tête ATLAS */
    .atlas-title {
        font-size: 3rem;
        font-weight: 800;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        text-align: center;
        color: #ffffff;
    }
    .atlas-subtitle {
        text-align: center;
        color: #c5c7ff;
        margin-bottom: 2rem;
    }

    /* Conteneur principal */
    .atlas-card {
        background: linear-gradient(145deg, rgba(18, 24, 58, 0.95), rgba(20, 32, 80, 0.98));
        border-radius: 22px;
        padding: 1.5rem 1.8rem;
        border: 1px solid rgba(110, 125, 255, 0.45);
        box-shadow: 0 18px 45px rgba(0, 0, 0, 0.55);
    }

    /* Bouton principal */
    .stButton>button {
        border-radius: 999px;
        border: none;
        padding: 0.75rem 1.75rem;
        font-weight: 600;
        background: linear-gradient(90deg, #7b5cff, #ff6fb1);
        color: white;
        box-shadow: 0 12px 25px rgba(0, 0, 0, 0.45);
    }
    .stButton>button:hover {
        opacity: 0.94;
        box-shadow: 0 15px 30px rgba(0, 0, 0, 0.6);
    }

    /* Cartes lieux */
    .place-title {
        font-weight: 600;
        font-size: 1rem;
    }
    .place-tag {
        font-size: 0.85rem;
        color: #d0d3ff;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# 📂 LOAD DATA
# --------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_excel("data.xlsx")
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("/", "_")
        .str.replace("-", "_")
    )
    return df


df = load_data()

# colonne de note (ex : note_5)
note_candidates = [c for c in df.columns if "note" in c or "5" in c]
note_col = note_candidates[0] if note_candidates else None


# --------------------------------------------------
# 🔐 CONFIG GROQ
# --------------------------------------------------
def get_groq_client():
    return Groq(api_key=st.secrets["GROQ_API_KEY"])


# --------------------------------------------------
# 🧾 CONSTRUCTION DU PROMPT
# --------------------------------------------------
def construire_prompt(pays: str, categorie: str, lieux: pd.DataFrame) -> str:
    blocs = []

    for _, row in lieux.iterrows():
        nom = row.get("nom_lieu", "")
        ville = row.get("ville", "")
        note = row.get(note_col, "")
        ideal = row.get("ideal_pour", "")
        url_resa = row.get("url_reservation", "")

        bloc = (
            f"- **{nom}** ({ville})\n"
            f"  ⭐ Note : {note}/5\n"
            f"  🏷️ Idéal pour : {ideal}\n"
            f"  🔗 Réservation : {url_resa}\n"
        )
        blocs.append(bloc)

    texte_lieux = "\n".join(blocs)

    prompt = f"""
Tu es un expert en organisation de voyages et guide touristique.

Crée un **itinéraire complet et réaliste de 3 jours** à **{pays}**, pour la catégorie d’activité **{categorie}**.

Voici la liste des lieux à intégrer IMPÉRATIVEMENT dans les propositions :

{texte_lieux}

FORMAT ATTENDU :
- **Jour 1 :** programme détaillé, activités, explications
- **Jour 2 :** programme détaillé
- **Jour 3 :** programme détaillé
- Mentionne clairement **dans quel jour apparaît chaque lieu**
- Chaque jour doit contenir au moins **un des lieux listés**
- Ajoute des conseils pratiques (horaires, transport, durée)
- Termine par un bloc :
### 🔗 Liens de réservation  
et liste tous les liens fournis.

Sois inspirant, premium, mais concret et réaliste.
"""
    return prompt


# --------------------------------------------------
# 🤖 APPEL IA
# --------------------------------------------------
def generer_sejour(prompt: str) -> str:
    try:
        client = get_groq_client()
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "Tu es un expert en voyages de luxe."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=1800,
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"❌ Erreur API : {e}"


# --------------------------------------------------
# 🧾 PDF (Option A – reportlab)
# --------------------------------------------------
def creer_pdf(contenu: str, titre: str) -> bytes:
    """Crée un PDF simple à partir du texte généré."""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    c.setTitle(titre)

    # Titre
    c.setFont("Helvetica-Bold", 16)
    c.drawString(40, height - 60, titre)

    # Corps
    text = c.beginText(40, height - 90)
    text.setFont("Helvetica", 11)

    for line in contenu.split("\n"):
        wrapped = textwrap.wrap(line, 95) or [""]
        for subline in wrapped:
            text.textLine(subline)

    c.drawText(text)
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.getvalue()


# --------------------------------------------------
# 🧠 SESSION STATE
# --------------------------------------------------
if "sejour_texte" not in st.session_state:
    st.session_state["sejour_texte"] = None


# --------------------------------------------------
# 🧭 UI ATLAS
# --------------------------------------------------
st.markdown("<h1 class='atlas-title'>ATLAS</h1>", unsafe_allow_html=True)
st.markdown(
    "<p class='atlas-subtitle'>Crée un itinéraire inspirant et ultra-personnalisé en quelques clics.</p>",
    unsafe_allow_html=True,
)

with st.container():
    st.markdown("<div class='atlas-card'>", unsafe_allow_html=True)

    # Sélecteurs
    cols_top = st.columns(2)
    with cols_top[0]:
        pays_liste = sorted(df["pays"].dropna().unique())
        pays = st.selectbox("🌍 Choisissez un pays", pays_liste)

    with cols_top[1]:
        df_pays = df[df["pays"] == pays]
        categories = sorted(df_pays["categorie"].dropna().unique())
        categorie = st.selectbox("🎯 Choisissez une catégorie d’activité", categories)

    # Lieux filtrés
    lieux = df_pays[df_pays["categorie"] == categorie]

    if lieux.empty:
        st.error("Aucun lieu trouvé pour cette combinaison.")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.success(f"🔎 {len(lieux)} lieu(x) trouvé(s) pour ce séjour.")

        st.markdown("### 📍 Lieux suggérés par ATLAS")
        lieux_affiches = lieux.copy()

        # Affichage des lieux sous forme de cartes
        # On limite éventuellement l'affichage pour ne pas surcharger (ex : 9)
        max_cards = 9
        lieux_affiches = lieux_affiches.head(max_cards)

        for start in range(0, len(lieux_affiches), 3):
            row_df = lieux_affiches.iloc[start : start + 3]
            cols_cards = st.columns(len(row_df))
            for col, (_, row) in zip(cols_cards, row_df.iterrows()):
                with col:
                    nom = row.get("nom_lieu", "Lieu")
                    ville = row.get("ville", "")
                    note = row.get(note_col, None)
                    ideal = row.get("ideal_pour", "")
                    prix = row.get("prix", None)
                    img_url = row.get("lien_images", None)
                    url_resa = row.get("url_reservation", None)

                    if img_url and pd.notna(img_url):
                        st.image(img_url, use_column_width=True)

                    st.markdown(f"<p class='place-title'>{nom}</p>", unsafe_allow_html=True)
                    st.markdown(
                        f"<p class='place-tag'>📍 {ville}</p>",
                        unsafe_allow_html=True,
                    )
                    details = []
                    if note is not None and pd.notna(note):
                        details.append(f"⭐ {note}/5")
                    if prix is not None and pd.notna(prix):
                        details.append(f"💶 {prix} €")
                    if ideal:
                        details.append(f"👥 {ideal}")

                    if details:
                        st.markdown(" • ".join(details))

                    if url_resa and pd.notna(url_resa):
                        st.markdown(f"[🔗 Réserver]({url_resa})")

        st.markdown("</div>", unsafe_allow_html=True)

# --------------------------------------------------
# 🚀 BOUTON GÉNÉRATION
# --------------------------------------------------
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<div class='atlas-card'>", unsafe_allow_html=True)

if st.button("✨ Générer mon séjour parfait", use_container_width=True):
    with st.spinner("🤖 L’IA prépare votre séjour, un instant..."):
        prompt = construire_prompt(pays, categorie, lieux)
        resultat = generer_sejour(prompt)
        st.session_state["sejour_texte"] = resultat

# Affichage du résultat
if st.session_state["sejour_texte"]:
    st.markdown("## 🧳 Votre séjour personnalisé")
    st.markdown(st.session_state["sejour_texte"])

    # Bouton de téléchargement PDF
    pdf_bytes = creer_pdf(
        st.session_state["sejour_texte"], f"ATLAS – Séjour {pays} ({categorie})"
    )
    st.download_button(
        label="📄 Télécharger ce séjour en PDF",
        data=pdf_bytes,
        file_name=f"atlas_sejour_{pays.lower()}_{categorie.lower()}.pdf",
        mime="application/pdf",
    )

st.markdown("</div>", unsafe_allow_html=True)

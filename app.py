import streamlit as st
import pandas as pd
from groq import Groq
from fpdf import FPDF

# ============================================================
# CONFIGURATION GÉNÉRALE
# ============================================================
st.set_page_config(page_title="ATLAS – Générateur de Séjour", layout="wide")

st.markdown("""
<style>
    .main {background-color: #fafafa;}
    h1 {font-size: 3rem; font-weight: 700; color: #222;}
    .stButton>button {
        background-color:#4b6ef5;
        color:white;
        border-radius:8px;
        padding:12px 25px;
        font-size:1.1rem;
    }
</style>
""", unsafe_allow_html=True)

st.title("🌍 **ATLAS – Créateur de séjours personnalisés**")


# ============================================================
# CHARGEMENT DATA
# ============================================================
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

note_col = [c for c in df.columns if "note" in c or "5" in c][0]


# ============================================================
# SÉLECTIONS UTILISATEUR
# ============================================================
pays = st.selectbox("🌎 Choisissez un pays :", sorted(df["pays"].unique()))

categories = sorted(df[df["pays"] == pays]["categorie"].unique())
categorie = st.selectbox("🎨 Choisissez une catégorie d’activité :", categories)

lieux_df = df[(df["pays"] == pays) & (df["categorie"] == categorie)]

if lieux_df.empty:
    st.error("Aucun lieu trouvé pour cette combinaison.")
else:
    st.success(f"{len(lieux_df)} lieu(x) trouvé(s) ✔")


# ============================================================
# PROMPT IA
# ============================================================
def construire_prompt(pays, categorie, lieux_df):
    texte = ""
    for _, row in lieux_df.iterrows():
        texte += (
            f"- **{row['nom_lieu']}** ({row['ville']})\n"
            f"  ⭐ Note : {row[note_col]}/5\n"
            f"  🏷️ Idéal pour : {row['ideal_pour']}\n"
            f"  🔗 Réservation : {row['url_reservation']}\n\n"
        )

    return f"""
Tu es un expert mondial en création de séjours haut de gamme.

Crée un **itinéraire complet de 3 jours** pour un voyage à **{pays}**.
Catégorie d’activité : **{categorie}**.

Voici les lieux que tu dois absolument intégrer au fil des journées :

{texte}

FORMAT ATTENDU :
- Itinéraire détaillé jour par jour
- Intégration cohérente des lieux fournis
- Conseils d’organisation, horaires, ambiance
- Un paragraphe final : **Liens de réservation**
"""


# ============================================================
# NETTOYAGE TEXTE POUR PDF
# ============================================================
def nettoyer_ligne(ligne: str) -> str:
    if not ligne:
        return ""

    ligne = ligne.encode("latin-1", "ignore").decode("latin-1")

    invisibles = [
        "\u202f", "\u2007", "\u2009", "\u200A", "\u200B",
        "\u2060", "\u00A0", "\u2028", "\u2029"
    ]
    for c in invisibles:
        ligne = ligne.replace(c, " ")

    ligne = ligne.replace("–", "-").replace("—", "-")

    return ligne.strip()


def creer_pdf(contenu: str, titre: str) -> bytes:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    titre_safe = nettoyer_ligne(titre)
    contenu_lignes = contenu.split("\n")

    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, titre_safe, ln=True)
    pdf.ln(4)

    pdf.set_font("Helvetica", "", 11)

    for ligne in contenu_lignes:
        propre = nettoyer_ligne(ligne)
        if not propre:
            pdf.ln(2)
            continue
        pdf.multi_cell(0, 6, propre)

    return pdf.output(dest="S").encode("latin-1", "ignore")


# ============================================================
# IA – GROQ
# ============================================================
def generer_sejour(prompt):
    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "Tu es un expert en voyages de luxe."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=1600,
            temperature=0.7,
        )
        return completion.choices[0].message.content

    except Exception as e:
        return f"❌ Erreur IA : {e}"


# ============================================================
# ACTION : GÉNERATION
# ============================================================
if st.button("✨ Générer mon séjour parfait"):

    with st.spinner("✈️ ATLAS prépare votre itinéraire..."):
        prompt = construire_prompt(pays, categorie, lieux_df)
        resultat = generer_sejour(prompt)

    st.session_state["atlas_resultat"] = resultat
    st.markdown("### 🎉 Votre séjour personnalisé :")
    st.markdown(resultat)


# ============================================================
# EXPORT PDF
# ============================================================
if "atlas_resultat" in st.session_state:
    st.subheader("📄 Exporter")

    if st.button("📥 Télécharger en PDF"):
        pdf_bytes = creer_pdf(
            st.session_state["atlas_resultat"],
            f"ATLAS – Séjour {pays}"
        )
        st.download_button(
            "Télécharger le PDF",
            data=pdf_bytes,
            file_name="sejour_atlas.pdf",
            mime="application/pdf"
        )

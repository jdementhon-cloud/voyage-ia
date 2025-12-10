import streamlit as st
import pandas as pd
from groq import Groq
import base64
import io
import re
from fpdf import FPDF

# ----------------------------------------------------
# CONFIGURATION GÉNÉRALE DE L’APPLICATION
# ----------------------------------------------------
st.set_page_config(page_title="ATLAS – Générateur de séjour", layout="wide")

st.markdown("""
<style>
h1 {
    text-align: center;
    font-size: 3rem !important;
    font-weight: 800;
    letter-spacing: -1px;
}
.stButton > button {
    width: 100%;
    border-radius: 12px;
    font-size: 1.1rem;
    padding: 14px;
}
</style>
""", unsafe_allow_html=True)

st.title("🌍 ATLAS – Créateur de séjours inspirants")

# ----------------------------------------------------
# CHARGEMENT DES DONNÉES
# ----------------------------------------------------
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
note_col = [c for c in df.columns if "note" in c][0]


# ----------------------------------------------------
# FONCTIONS UTILITAIRES
# ----------------------------------------------------

# 🔵 Retirer images Markdown avant PDF
def retirer_images_markdown(texte: str) -> str:
    return re.sub(r'!\[.*?\]\(.*?\)', '', texte)

# 🔵 Afficher images dans Streamlit
def afficher_images_streamlit(texte: str):
    images = re.findall(r'!\[.*?\]\((.*?)\)', texte)
    if images:
        st.subheader("📸 Images associées")
        for url in images:
            st.image(url, use_column_width=True)

# 🔵 Création du PDF propre
def creer_pdf(texte, titre="ATLAS – Séjour"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Titre
    pdf.set_font("Arial", "B", 20)
    pdf.cell(0, 15, titre, ln=True)

    # Contenu safe
    pdf.set_font("Arial", size=12)
    ligne_safe = texte.replace("•", "-").replace("\t", " ")

    for line in ligne_safe.split("\n"):
        pdf.multi_cell(0, 8, line)

    pdf_bytes = pdf.output(dest="S").encode("latin-1", errors="ignore")
    return pdf_bytes


# ----------------------------------------------------
# PROMPT IA
# ----------------------------------------------------
def construire_prompt(pays, categorie, lieux):
    texte = ""
    for _, row in lieux.iterrows():
        texte += (
            f"- **{row['nom_lieu']}** ({row['ville']})\n"
            f"  ⭐ Note : {row[note_col]}/5\n"
            f"  🏷️ Idéal pour : {row['ideal_pour']}\n"
            f"  🔗 Réservation : {row['url_reservation']}\n\n"
        )

    prompt = f"""
Tu es un expert en organisation de voyages premium.

Crée un **itinéraire réaliste et inspirant de 3 jours** à **{pays}**, dans la catégorie **{categorie}**.

### Voici les lieux que tu dois ABSOLUMENT intégrer :

{texte}

### FORMAT DEMANDÉ :
- Jour 1 : programme clair
- Jour 2 : programme clair
- Jour 3 : programme clair
- Chaque jour doit intégrer au moins un lieu listé
- Ajouter conseils pratiques + horaires + ambiance
- En fin de texte, ajoute un bloc :

### 🔗 Liens de réservation

Style premium, fluide, inspirant.
"""
    return prompt


# ----------------------------------------------------
# APPEL À L’IA (GROQ)
# ----------------------------------------------------
def generer_sejour(prompt):
    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])

        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "Tu es un expert en voyages premium."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=1600,
        )

        return completion.choices[0].message.content

    except Exception as e:
        return f"❌ Erreur API : {e}"


# ----------------------------------------------------
# INTERFACE UTILISATEUR
# ----------------------------------------------------
pays = st.selectbox("🌐 Choisissez un pays :", sorted(df["pays"].unique()))
categories = sorted(df[df["pays"] == pays]["categorie"].unique())
categorie = st.selectbox("🍀 Choisissez une catégorie d’activité :", categories)

lieux = df[(df["pays"] == pays) & (df["categorie"] == categorie)]

if lieux.empty:
    st.error("Aucun lieu trouvé.")
else:
    st.success(f"{len(lieux)} lieu(x) trouvé(s) ✔️")


# ----------------------------------------------------
# BOUTON DE GÉNÉRATION IA
# ----------------------------------------------------
if st.button("✨ Générer mon séjour parfait", type="primary"):

    with st.spinner("🧭 Création de votre itinéraire…"):
        prompt = construire_prompt(pays, categorie, lieux)
        resultat = generer_sejour(prompt)

    st.session_state["atlas_resultat"] = resultat

    st.success("🎉 Séjour généré avec succès !")
    st.markdown(resultat)
    afficher_images_streamlit(resultat)


# ----------------------------------------------------
# BLOC EXPORT PDF
# ----------------------------------------------------
st.subheader("📄 Exporter")

if "atlas_resultat" in st.session_state:

    # Nettoyage automatique pour PDF
    texte_pdf = retirer_images_markdown(st.session_state["atlas_resultat"])

    fichier_pdf = creer_pdf(texte_pdf, f"ATLAS – Séjour {pays}")

    st.download_button(
        label="📥 Télécharger le PDF",
        data=fichier_pdf,
        file_name=f"ATLAS_Sejour_{pays}.pdf",
        mime="application/pdf"
    )

else:
    st.info("Générez d'abord un séjour pour pouvoir exporter en PDF.")

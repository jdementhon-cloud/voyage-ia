import streamlit as st
import pandas as pd
from groq import Groq
from fpdf import FPDF

# ---------------------------------------------------
# 🎨 CONFIGURATION DE LA PAGE
# ---------------------------------------------------
st.set_page_config(page_title="ATLAS – Générateur de Séjours IA", layout="wide")

st.markdown(
    """
    <h1 style='text-align:center; font-size: 50px; margin-bottom: -10px;'>🌍 ATLAS</h1>
    <p style='text-align:center; font-size:20px; color:#666;'>Crée ton séjour parfait en quelques secondes grâce à l’IA.</p>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------
# 📂 CHARGEMENT DES DONNÉES
# ---------------------------------------------------
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

# Identification automatique de la colonne note
note_col_candidates = [c for c in df.columns if "note" in c or "5" in c]
note_col = note_col_candidates[0] if note_col_candidates else None

# ---------------------------------------------------
# 🧭 INTERFACE UTILISATEUR
# ---------------------------------------------------
st.subheader("🎯 Choix du séjour")

col1, col2 = st.columns(2)

with col1:
    pays = st.selectbox("🌎 Choisissez un pays :", sorted(df["pays"].unique()))

with col2:
    categories = sorted(df[df["pays"] == pays]["categorie"].unique())
    categorie = st.selectbox("🏷️ Choisissez une catégorie d’activité :", categories)

lieux = df[(df["pays"] == pays) & (df["categorie"] == categorie)]

if lieux.empty:
    st.error("❌ Aucun lieu trouvé pour cette combinaison.")
else:
    st.success(f"🔍 {len(lieux)} lieu(x) trouvé(s) ✔")

# ---------------------------------------------------
# 📄 AFFICHAGE DES LIEUX + IMAGES
# ---------------------------------------------------
st.subheader("📸 Lieux disponibles")

for _, row in lieux.iterrows():
    with st.container(border=True):
        cols = st.columns([1, 3])
        with cols[0]:
            try:
                st.image(row["lien_images"], use_column_width=True)
            except:
                st.write("Aucune image")
        with cols[1]:
            st.markdown(
                f"""
                ### {row['nom_lieu']} ({row['ville']})
                ⭐ **Note :** {row[note_col]}/5  
                👥 **Idéal pour :** {row['ideal_pour']}  
                💰 **Prix :** {row['prix']}  
                🔗 [Lien de réservation]({row['url_reservation']})
                """
            )

# ---------------------------------------------------
# 🧠 PROMPT IA
# ---------------------------------------------------
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
Tu es un expert en organisation de voyages.

Crée un **itinéraire complet de 3 jours** à **{pays}**, spécialité **{categorie}**.

Voici les lieux à intégrer dans l’itinéraire :

{texte}

FORMAT ATTENDU :
- Plan détaillé jour par jour
- Intègre les lieux de manière cohérente (au moins un par jour)
- Conseils pratiques (horaires, transport, durée)
- À la fin, récapitule tous les liens dans un bloc “🔗 Réservations”

Style premium, clair, inspirant.
"""
    return prompt


# ---------------------------------------------------
# 🤖 APPEL API GROQ
# ---------------------------------------------------
def generer_sejour(prompt):
    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])

        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "Tu es un expert en voyages de luxe."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=1600,
        )

        return completion.choices[0].message.content

    except Exception as e:
        return f"❌ Erreur API : {e}"


# ---------------------------------------------------
# 📄 PDF EXPORT (fpdf2)
# ---------------------------------------------------
def creer_pdf(contenu: str, titre: str) -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 10, titre, ln=True)

    pdf.ln(5)
    pdf.set_font("Helvetica", size=12)

    for line in contenu.split("\n"):
        pdf.multi_cell(0, 8, line)

    return pdf.output(dest="S").encode("latin1")


# ---------------------------------------------------
# 🔘 BOUTON DE GÉNÉRATION
# ---------------------------------------------------
st.subheader("✨ Génération du séjour")

if st.button("🚀 Générer mon séjour parfait", type="primary"):
    with st.spinner("L’IA prépare votre séjour..."):
        prompt = construire_prompt(pays, categorie, lieux)
        resultat = generer_sejour(prompt)
        st.session_state["sejour_texte"] = resultat

    st.success("🎉 Séjour généré ! Voici votre proposition :")
    st.markdown(resultat)

    # Bouton PDF
    pdf_bytes = creer_pdf(resultat, f"ATLAS – Séjour {pays}")
    st.download_button(
        label="📄 Télécharger le séjour en PDF",
        data=pdf_bytes,
        file_name=f"atlas_sejour_{pays.lower()}_{categorie.lower()}.pdf",
        mime="application/pdf",
    )

import streamlit as st
import pandas as pd
import pdfkit
import base64
import tempfile
from groq import Groq

# -----------------------------------
# CONFIG
# -----------------------------------
st.set_page_config(page_title="ATLAS — Voyage IA", layout="wide")

# STYLE
st.markdown("""
<style>
.title-atlas {
    font-size: 60px;
    font-weight: 800;
    text-align: center;
    color: #1e1e1e;
    margin-bottom: -10px;
}
.subtitle-atlas {
    font-size: 22px;
    text-align: center;
    color: #555;
    margin-bottom: 40px;
}
.place-card {
    background: white;
    padding: 15px;
    border-radius: 12px;
    margin-bottom: 15px;
    border: 1px solid #eee;
}
.place-img {
    width: 100%;
    border-radius: 10px;
    margin-bottom: 10px;
}
.result-box {
    padding: 20px;
    background: #ffffff;
    border-radius: 12px;
    border-left: 6px solid #6a5af9;
    margin-top: 20px;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------------
# TITLE ATLAS
# -----------------------------------
st.markdown("<div class='title-atlas'>ATLAS</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle-atlas'>Créateur d’itinéraires personnalisés grâce à l’IA</div>",
            unsafe_allow_html=True)

# -----------------------------------
# LOAD DATA
# -----------------------------------
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

# -----------------------------------
# INPUTS
# -----------------------------------
pays = st.selectbox("🌍 Destination :", sorted(df["pays"].unique()))
categories = sorted(df[df["pays"] == pays]["categorie"].unique())
categorie = st.selectbox("🍀 Catégorie d’activité :", categories)

lieux = df[(df["pays"] == pays) & (df["categorie"] == categorie)]

if lieux.empty:
    st.error("❌ Aucun lieu trouvé.")
else:
    st.success(f"🔎 {len(lieux)} lieu(x) trouvé(s)")

# -----------------------------------
# PROMPT BUILDER
# -----------------------------------
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
Tu es un expert du voyage haut de gamme.

Génère un **itinéraire inspirant et détaillé de 3 jours** à **{pays}**, 
centré sur l’activité **{categorie}**, en intégrant les lieux suivants :

{texte}

Format attendu :
- Jour 1 : programme détaillé + au moins un lieu
- Jour 2 : programme détaillé + au moins un lieu
- Jour 3 : programme détaillé + au moins un lieu

Puis ajoute un bloc :

### 🔗 Liens de réservation  
Liste simplement les liens fournis.
"""
    return prompt


# -----------------------------------
# CALL IA
# -----------------------------------
def generer_sejour(prompt):
    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])

        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "Tu es un expert en création de voyages."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=1600,
        )

        return completion.choices[0].message.content

    except Exception as e:
        return f"❌ Erreur API : {e}"


# -----------------------------------
# GENERATE ROUTE
# -----------------------------------
result_html = ""

if st.button("✨ Générer mon séjour parfait"):
    with st.spinner("🧭 ATLAS prépare votre voyage…"):
        prompt = construire_prompt(pays, categorie, lieux)
        resultat = generer_sejour(prompt)

    st.markdown("<div class='result-box'>", unsafe_allow_html=True)
    st.markdown("### 🎉 Votre séjour personnalisé :")
    st.markdown(resultat)

    # 📸 DISPLAY IMAGES OF ALL PLACES
    st.markdown("### 🖼️ Images des lieux sélectionnés")

    img_html = ""
    for _, row in lieux.iterrows():
        if pd.notna(row["lien_images"]):
            st.markdown(
                f"""
                <div class='place-card'>
                    <img src="{row['lien_images']}" class='place-img'>
                    <b>{row['nom_lieu']}</b> – {row['ville']}
                </div>
                """,
                unsafe_allow_html=True,
            )
            img_html += f"<h3>{row['nom_lieu']}</h3><img src='{row['lien_images']}' width='500'><br>"

    st.markdown("</div>", unsafe_allow_html=True)

    # -----------------------------------------------------
    # PDF EXPORT
    # -----------------------------------------------------
    st.markdown("### 📄 Télécharger en PDF")

    pdf_content = f"""
    <h1>ATLAS — Voyage personnalisé</h1>
    <h2>{pays} — {categorie}</h2>
    <br>
    {resultat}
    <br><br>
    <h2>Images</h2>
    {img_html}
    """

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        pdfkit.from_string(pdf_content, tmp_file.name)
        pdf_bytes = open(tmp_file.name, "rb").read()

    st.download_button(
        label="📄 Télécharger le PDF",
        data=pdf_bytes,
        file_name="ATLAS_sejour.pdf",
        mime="application/pdf"
    )

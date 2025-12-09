import streamlit as st
import pandas as pd
from groq import Groq

# -------------------------------
# CONFIGURATION GÉNÉRALE
# -------------------------------
st.set_page_config(
    page_title="Générateur de Séjour Parfait",
    layout="wide",
)

# -------------------------------
# CSS – STYLE PREMIUM
# -------------------------------
st.markdown("""
<style>

body {
    background-color: #f7f9fc;
    font-family: "Inter", sans-serif;
}

/* Cartes élégantes */
.card {
    background: white;
    padding: 25px;
    border-radius: 16px;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.06);
    margin-bottom: 20px;
}

/* Bouton premium */
.stButton > button {
    background-color: #6c63ff;
    color: white;
    border-radius: 12px;
    padding: 12px 26px;
    font-size: 18px;
    border: none;
    transition: 0.2s ease-in-out;
}

.stButton > button:hover {
    background-color: #574ff7;
    transform: scale(1.03);
}

/* Bloc résultat IA */
.result-box {
    background: #eef2ff;
    padding: 25px;
    border-radius: 16px;
    border-left: 6px solid #6c63ff;
    margin-top: 18px;
}

.header-title {
    font-size: 38px;
    font-weight: 800;
    text-align: center;
    margin-bottom: 5px;
}

.subheader {
    text-align: center;
    font-size: 18px;
    color: #6366f1;
    margin-bottom: 40px;
}

</style>
""", unsafe_allow_html=True)

# -------------------------------
# HEADER
# -------------------------------
st.markdown("""
<div class='header-title'>✨ Générateur de séjour parfait (IA)</div>
<div class='subheader'>Crée un itinéraire inspirant et personnalisé en quelques secondes</div>
""", unsafe_allow_html=True)

# -------------------------------
# CHARGEMENT DES DONNÉES
# -------------------------------
df = pd.read_excel("data.xlsx")
df.columns = df.columns.str.lower().str.replace(" ", "_")

# -------------------------------
# FORMULAIRE UTILISATEUR
# -------------------------------
st.markdown("<div class='card'>", unsafe_allow_html=True)

pays = st.selectbox("🌍 Choisissez un pays :", sorted(df["pays"].dropna().unique()))

categories_dispo = df[df["pays"] == pays]["categorie"].dropna().unique()
categorie = st.selectbox("🎨 Choisissez une catégorie d’activité :", sorted(categories_dispo))

st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------
# FILTRAGE LIEUX
# -------------------------------
lieux = df[(df["pays"] == pays) & (df["categorie"] == categorie)]

if lieux.empty:
    st.error("😕 Aucun lieu trouvé pour cette activité.")
else:
    st.success(f"🔎 {len(lieux)} lieu(x) trouvé(s) ✔️")


# -------------------------------
# PROMPT IA
# -------------------------------
def construire_prompt(pays, categorie, lieux):
    texte = ""
    for _, row in lieux.iterrows():
        texte += (
            f"- **{row['nom_lieu']}**\n"
            f"  • Prix : {row['prix']}€\n"
            f"  • ⭐ Note : {row['note5']}/5\n"
            f"  • Idéal pour : {row['ideal_pour']}\n"
            f"  • 🔗 Réservation : {row['url_reservation']}\n\n"
        )

    prompt = f"""
Crée un **itinéraire parfait d’une journée** à **{pays}**, autour du thème **{categorie}**.

Voici les lieux disponibles :
{texte}

Délivre :
- Un programme **heure par heure**
- Une mise en scène immersive
- Conseils pratiques
- Intègre les **liens de réservation**
- Un texte fluide, inspirant, premium.
"""

    return prompt

# -------------------------------
# IA GROQ
# -------------------------------
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def generer_sejour(prompt):
    try:
        response = client.chat.completions.create(
            model="llama3-70b-8k-instant",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1200,
        )
        return response.choices[0].message["content"]
    except Exception as e:
        return f"❌ Erreur API : {e}"


# -------------------------------
# BOUTON GÉNÉRATION
# -------------------------------
st.markdown("<div class='card'>", unsafe_allow_html=True)

if st.button("✨ Générer mon séjour parfait", use_container_width=True):
    with st.spinner("⏳ L’IA prépare votre séjour sur mesure..."):
        prompt = construire_prompt(pays, categorie, lieux)
        resultat = generer_sejour(prompt)

    st.markdown("<div class='result-box'>", unsafe_allow_html=True)
    st.markdown("### 🧳 Votre séjour personnalisé :")
    st.write(resultat)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

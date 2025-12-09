import streamlit as st
import pandas as pd
from groq import Groq
import os

# ----------------------------------------------------
# 1️⃣ Charger la clé API (depuis Streamlit Cloud ou local)
# ----------------------------------------------------
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY"))

if not GROQ_API_KEY:
    st.error("❌ Clé API Groq manquante. Ajoutez-la dans Settings → Secrets.")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

# ----------------------------------------------------
# 2️⃣ Charger le dataset
# ----------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_excel("data.xlsx")
    df.columns = df.columns.str.strip()
    return df

df = load_data()

# ----------------------------------------------------
# 3️⃣ Titre & description
# ----------------------------------------------------
st.set_page_config(page_title="Séjour parfait IA", layout="wide")

st.markdown(
    """
    # 🌍 Générateur de séjour parfait (IA)

    Choisissez un **pays** et une **catégorie d’activité**, l’IA se charge du reste ✨  
    """
)

# ----------------------------------------------------
# 4️⃣ Menus déroulants
# ----------------------------------------------------
pays_list = sorted(df["PAYS"].dropna().unique())
selected_pays = st.selectbox("Choisissez un pays :", pays_list)

filtered = df[df["PAYS"] == selected_pays]

categories = sorted(filtered["CATEGORIE"].dropna().unique())
selected_cat = st.selectbox("Choisissez une catégorie d’activité :", categories)

# ----------------------------------------------------
# 5️⃣ Fonction IA
# ----------------------------------------------------
def generate_itinerary(pays, categorie):
    lieux = df[(df["PAYS"] == pays) & (df["CATEGORIE"] == categorie)]

    lieux_text = ""
    for _, row in lieux.iterrows():
        lieux_text += f"- **{row['NOM_LIEU']}** ({row['VILLE']}), idéal pour : {row['POUR_QUI']}\n"

    prompt = f"""
    Tu es un expert du voyage haut de gamme.
    Crée un **séjour parfait** pour quelqu’un voyageant en **{pays}**, 
    intéressé par la catégorie **{categorie}**.

    Les lieux disponibles :
    {liens_text}

    Format attendu :
    - Une introduction inspirante
    - Un plan jour par jour (5 à 7 jours)
    - Recommandations personnalisées
    - Suggestions premium
    """

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content

# ----------------------------------------------------
# 6️⃣ Bouton : générer le séjour
# ----------------------------------------------------
if st.button("✨ Générer mon séjour parfait"):
    with st.spinner("⏳ L’IA prépare votre séjour..."):
        try:
            result = generate_itinerary(selected_pays, selected_cat)
            st.success("🎉 Séjour généré avec succès !")
            st.markdown(result)
        except Exception as e:
            st.error(f"❌ Erreur API : {e}")

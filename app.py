import streamlit as st
import pandas as pd
from groq import Groq

# =========================
#  CONFIG GROQ
# =========================

GROQ_API_KEY = st.secrets["GROQ_API_KEY"]  
client = Groq(api_key=GROQ_API_KEY)

# =========================
#  LOAD DATA
# =========================

@st.cache_data
def load_data():
    df = pd.read_excel("data.xlsx")

    df.columns = (
        df.columns.str.lower()
        .str.strip()
        .str.replace(" ", "_")
        .str.replace("'", "")
        .str.replace("/", "")
    )
    return df

df = load_data()

# =========================
#  UI TITLE
# =========================

st.title("🌍 Générateur de Séjour Parfait (IA)")

# =========================
#  SELECTORS
# =========================

pays_list = sorted(df["pays"].dropna().unique())
pays = st.selectbox("Choisissez un pays :", pays_list)

# Filtrer les catégories disponibles UNIQUEMENT pour ce pays
categories_disponibles = sorted(df[df["pays"] == pays]["categorie"].dropna().unique())
categorie = st.selectbox("Choisissez une catégorie d’activité :", categories_disponibles)

# Filtrage final
lieux = df[(df["pays"] == pays) & (df["categorie"] == categorie)]

if len(lieux) == 0:
    st.error("Aucun lieu disponible pour cette combinaison.")
    st.stop()

# =========================
#  GENERATION PROMPT
# =========================

def generer_prompt(pays, categorie, lieux):

    texte_lieux = ""
    for _, row in lieux.iterrows():
        texte_lieux += (
            f"- {row['nom_lieu']} ({row['ville']}) | "
            f"{row['prix']}€ | ⭐ {row['note5']}/5 | "
            f"Idéal pour : {row['ideal_pour']}\n"
        )

    prompt = f"""
Tu es un expert en voyages.

Crée un **programme d’une journée parfaite** à **{pays}**, 
autour de la catégorie : **{categorie}**.

Voici les lieux possibles :
{texte_lieux}

🎯 Format demandé :
- Programme horaire clair (matin / midi / après-midi / soir)
- Explications courtes mais inspirantes
- Donner envie d’y aller
- Conseils pratiques
- Intégrer le plus possible les lieux listés
"""
    return prompt

# =========================
#  IA CALL
# =========================

def generer_sejour(prompt):
    response = client.chat.completions.create(
        model="llama3-70b-8192",   # ⬅️ MODELE QUI MARCHE
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1200,
    )
    return response.choices[0].message["content"]

# =========================
#  BTN → GENERATE TRIP
# =========================

if st.button("✨ Générer mon séjour parfait"):
    with st.spinner("L’IA prépare votre programme..."):
        prompt = generer_prompt(pays, categorie, lieux)
        resultat = generer_sejour(prompt)

    st.subheader("📅 Votre journée parfaite :")
    st.write(resultat)

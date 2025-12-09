import streamlit as st
import pandas as pd
from groq import Groq
import os

# =========================
#  CONFIG GROQ
# =========================

GROQ_API_KEY = st.secrets["GROQ_API_KEY"]  # depuis Streamlit Cloud
client = Groq(api_key=GROQ_API_KEY)

# =========================
#  CHARGEMENT DU FICHIER EXCEL
# =========================

@st.cache_data
def load_data():
    df = pd.read_excel("data.xlsx")

    # Normalisation colonnes
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
#  AFFICHAGE DES COLONNES
# =========================

st.title("Test Application Voyage – Version Simple")

st.subheader("Colonnes détectées :")
st.json(list(df.columns))

# =========================
#  SÉLECTEURS
# =========================

pays_list = sorted(df["pays"].dropna().unique())
categorie_list = sorted(df["categorie"].dropna().unique())

pays = st.selectbox("🌍 Choisissez un pays :", pays_list)
categorie = st.selectbox("🍽️ Choisissez une catégorie d’activité :", categorie_list)

# Filtrage après sélection
lieux = df[(df["pays"] == pays) & (df["categorie"] == categorie)]

st.subheader("Lieux sélectionnés :")
st.write(lieux)

# =========================
#  FONCTION PROMPT
# =========================

def generer_prompt(pays, categorie, lieux):
    texte_lieux = ""

    for _, row in lieux.iterrows():
        texte_lieux += (
            f"- {row['nom_lieu']} | "
            f"Prix : {row['prix']}€ | "
            f"⭐ {row['note5']}/5 | "
            f"Idéal pour : {row['ideal_pour']} | "
            f"Réservation : {row['url_reservation']}\n"
        )

    prompt = f"""
Tu es un expert en voyages.

Crée un **séjour parfait de 3 jours** à **{pays}**, 
centré sur la catégorie : **{categorie}**.

Voici une liste des meilleurs lieux :

{texte_lieux}

Format attendu :
- 🗓️ Programme détaillé jour par jour
- ✨ Explication de pourquoi ces lieux sont incroyables
- 💡 Astuces pratiques
- 🔗 Liens de réservation déjà fournis

Reste clair, inspirant, et efficace.
"""
    return prompt

# =========================
#  GENERATION DU SEJOUR
# =========================

def generer_sejour(prompt):
    response = client.chat.completions.create(
        model="llama-3.1-70b-versatile",   # modèle Groq PREMIUM qui marche
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1200,
    )
    return response.choices[0].message["content"]

# =========================
#  BOUTON
# =========================

if st.button("✨ Générer mon séjour parfait"):
    if len(lieux) == 0:
        st.error("Aucun lieu trouvé pour cette combinaison.")
    else:
        st.info("⏳ L’IA prépare votre séjour...")
        prompt = generer_prompt(pays, categorie, lieux)
        resultat = generer_sejour(prompt)
        st.success("🎉 Séjour généré avec succès !")
        st.write(resultat)

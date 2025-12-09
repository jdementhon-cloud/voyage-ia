import streamlit as st
import pandas as pd
from groq import Groq
import os

st.title("Générateur de séjour parfait (IA)")

# ============================
#   CHARGEMENT FICHIER
# ============================
try:
    df = pd.read_excel("data.xlsx")
except Exception as e:
    st.error(f"Erreur lors du chargement du fichier : {e}")
    st.stop()

st.subheader("Colonnes détectées :")
st.write(list(df.columns))

# Normalisation
df.columns = (
    df.columns
    .str.lower()
    .str.replace(" ", "_")
    .str.replace("é", "e")
    .str.replace("'", "")
)

st.subheader("Colonnes après normalisation :")
st.write(list(df.columns))

# ============================
#   SELECTBOX PAYS
# ============================
pays = st.selectbox(
    "🌍 Choisissez un pays :",
    sorted(df["pays"].dropna().unique())
)

# ============================
#   SELECTBOX CATEGORIE
# ============================
categories = sorted(df[df["pays"] == pays]["categorie"].dropna().unique())
categorie = st.selectbox(
    "🍽️ Choisissez une catégorie d’activité :",
    categories
)

# Filtrer le tableau
lieux = df[(df["pays"] == pays) & (df["categorie"] == categorie)]

st.subheader("Lieux sélectionnés :")
if lieux.empty:
    st.warning("Aucun résultat trouvé.")
    st.stop()
else:
    st.dataframe(lieux)

# ============================
#    FONCTION PROMPT
# ============================
def construire_prompt(pays, categorie, lieux):
    texte = ""

    for _, row in lieux.iterrows():
        nom = row.get("nom_lieu", "")
        prix = row.get("prix", "")
        note = row.get("note_5", "")        # <-- CORRECTION ICI
        ideal = row.get("ideal_pour", "")
        url = row.get("url_reservation", "")

        texte += f"- {nom} | {prix}€ | ⭐ {note}/5 | Idéal pour : {ideal} | Réserver : {url}\n"

    prompt = f"""
Tu es un expert en voyages.

Produit un séjour parfait de 3 jours à {pays}.
La catégorie choisie est : {categorie}.

Liste des lieux recommandés :
{texte}

Ton output doit inclure :
- Un plan jour par jour
- Les raisons des choix
- Des conseils utiles
- Un ton inspirant et premium
"""
    return prompt


# ============================
#   API GROQ
# ============================
if "GROQ_API_KEY" not in st.secrets:
    st.error("⚠️ GROQ_API_KEY manquante dans Streamlit Cloud.")
    st.stop()

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def generer_sejour(prompt):
    response = client.chat.completions.create(
        model="deepseek-r1-distill-qwen-32b",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1200,
    )
    return response.choices[0].message["content"]


# ============================
#   BOUTON IA
# ============================
if st.button("✨ Générer mon séjour parfait"):
    with st.spinner("L’IA prépare votre séjour…"):
        prompt = construire_prompt(pays, categorie, lieux)
        resultat = generer_sejour(prompt)

    st.subheader("🧳 Séjour généré par l’IA :")
    st.write(resultat)

import streamlit as st
import pandas as pd
from groq import Groq
import os

st.title("Générateur de séjour parfait (IA)")

# ============================
#   CHARGEMENT DU FICHIER
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

# ============================
#   SELECTBOX PAYS
# ============================
pays = st.selectbox("🌍 Choisissez un pays :", sorted(df["pays"].dropna().unique()))

# ============================
#   SELECTBOX CATEGORIE
# ============================
categories = sorted(df[df["pays"] == pays]["categorie"].dropna().unique())
categorie = st.selectbox("🎨 Choisissez une catégorie d’activité :", categories)

# Filtrer le tableau
lieux = df[(df["pays"] == pays) & (df["categorie"] == categorie)]

st.subheader("Lieux sélectionnés :")
if lieux.empty:
    st.warning("Aucun résultat trouvé.")
    st.stop()
else:
    st.dataframe(lieux)

# ============================
#       GENERATEUR IA
# ============================
def construire_prompt(pays, categorie, lieux):
    texte = ""
    for _, row in lieux.iterrows():
        nom = row["nom_lieu"]
        prix = row["prix"]
        note = row["note5"]
        ideal = row["ideal_pour"]
        url = row["url_reservation"]

        texte += f"- {nom} | {prix}€ | ⭐ {note}/5 | Pour : {ideal} | Réserver : {url}\n"

    prompt = f"""
Tu es un expert en voyages.

Produit un séjour parfait de 3 jours à {pays}.
La catégorie d’activité est : {categorie}.

Voici les lieux recommandés à intégrer :
{texte}

Ton output doit inclure :
- Un plan jour par jour
- Les raisons de chaque choix
- Des conseils pratiques
- Un ton inspirant et premium

Réponds uniquement avec le texte final.
"""

    return prompt


# ============================
#   API GROQ
# ============================
groq_api = st.secrets["GROQ_API_KEY"] if "GROQ_API_KEY" in st.secrets else None

if not groq_api:
    st.error("⚠️ GROQ_API_KEY est introuvable dans Streamlit Cloud.")
    st.stop()

client = Groq(api_key=groq_api)


def generer_sejour(prompt):
    response = client.chat.completions.create(
        model="deepseek-r1-distill-qwen-32b",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1200,
    )
    return response.choices[0].message["content"]


# ============================
#   BOUTON DE GENERATION
# ============================
if st.button("✨ Générer mon séjour parfait"):
    with st.spinner("L’IA prépare votre séjour…"):
        prompt = construire_prompt(pays, categorie, lieux)
        resultat = generer_sejour(prompt)

    st.subheader("🧳 Séjour généré par l’IA :")
    st.write(resultat)

import streamlit as st
import pandas as pd
import unicodedata
import os
from groq import Groq

# ---------------------------------------------------
# 1. Fonction de nettoyage de texte (accents, espaces)
# ---------------------------------------------------
def clean_text(x):
    if isinstance(x, str):
        x = x.strip().lower()
        x = "".join(
            c for c in unicodedata.normalize("NFD", x)
            if unicodedata.category(c) != "Mn"
        )
    return x

# ---------------------------------------------------
# 2. Chargement du dataset
# ---------------------------------------------------
st.title("🌍 Générateur de Séjour Parfait (IA)")

df = pd.read_excel("data.xlsx")

# Normalisation des colonnes : minuscules + sans accents + underscores
df.columns = [
    clean_text(col).replace(" ", "_").replace("/", "_")
    for col in df.columns
]

st.write("🔍 Colonnes détectées :", df.columns.tolist())

# Nettoyage du contenu
for col in df.columns:
    if df[col].dtype == "object":
        df[col] = df[col].apply(clean_text)

# ---------------------------------------------------
# 3. Interfaces : Sélecteurs Pays & Catégories
# ---------------------------------------------------
pays_list = sorted(df["pays"].unique())
categorie_list = sorted(df["categorie"].unique())

pays = st.selectbox("🌎 Choisissez un pays :", pays_list)
categorie = st.selectbox("🎯 Choisissez une catégorie d’activité :", categorie_list)

# Filtrage des lieux correspondant aux choix utilisateur
filtre = df[(df["pays"] == pays) & (df["categorie"] == categorie)]

if filtre.empty:
    st.error("❌ Aucun lieu ne correspond à cette sélection.")
    st.stop()

# Réduire la liste pour le prompt IA
lieux = filtre.head(5)

# ---------------------------------------------------
# 4. Construire le prompt IA
# ---------------------------------------------------
def generer_prompt(pays, categorie, lieux):
    texte = ""
    for _, row in lieux.iterrows():
        texte += (
            f"- {row['nom_lieu']} | prix : {row['prix']}€ | "
            f"note : {row['note5']}/5 | "
            f"idéal pour : {row['ideal_pour']} | "
            f"réservation : {row.get('url_reservation', 'non_disponible')}\n"
        )

    prompt = f"""
Tu es un expert en voyages.

Ta mission : créer un **séjour parfait de 3 jours** en **{pays}**,
pour une personne recherchant des activités dans la catégorie : **{categorie}**.

Voici les lieux potentiels à utiliser :  
{texte}

💡 Format attendu :
- Un planning détaillé des 3 jours (matin / après-midi / soir)
- Explication du choix des lieux
- Conseils pratiques
- Ajout des liens de réservation quand disponibles

Style : clair, professionnel, inspirant.
"""
    return prompt

prompt = generer_prompt(pays, categorie, lieux)

# ---------------------------------------------------
# 5. Appel à l’API Groq (LLM)
# ---------------------------------------------------
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

if st.button("✨ Générer le séjour parfait"):
    with st.spinner("⏳ L’IA prépare votre séjour…"):

        try:
            response = client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )

            texte_ia = response.choices[0].message["content"]
            st.success("🎉 Voici votre séjour parfait :")
            st.write(texte_ia)

        except Exception as e:
            st.error("🔥 Erreur lors de l'appel à l'IA :")
            st.exception(e)

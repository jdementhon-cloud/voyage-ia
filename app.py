import streamlit as st
import pandas as pd
from groq import Groq
import os

# ============================================================
# CONFIG STREAMLIT
# ============================================================
st.set_page_config(page_title="Séjour Parfait IA", page_icon="✨", layout="centered")
st.markdown("<h1 style='text-align:center;'>✨ Générateur de séjour parfait (IA)</h1>", unsafe_allow_html=True)

# ============================================================
# CHARGEMENT DES DONNÉES
# ============================================================
df = pd.read_excel("data.xlsx")

# Normalisation colonnes
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

# Colonnes attendues
required_cols = ["pays", "categorie", "nom_lieu", "prix", "note5", "ideal_pour", "url_reservation"]

if not all(col in df.columns for col in required_cols):
    st.error("❌ Erreur : Les colonnes du fichier Excel ne correspondent pas à ce que l’application attend.")
    st.stop()

# ============================================================
# INTERFACE UTILISATEUR
# ============================================================

pays_selection = st.selectbox("🌍 Choisissez un pays :", sorted(df["pays"].unique()))

df_filtre_pays = df[df["pays"] == pays_selection]

# Filtre des catégories selon le pays
categories_dispos = sorted(df_filtre_pays["categorie"].dropna().unique())

categorie_selection = st.selectbox("🍀 Choisissez une catégorie d’activité :", categories_dispos)

# Lieux filtrés
lieux = df_filtre_pays[df_filtre_pays["categorie"] == categorie_selection]

# Message si aucun lieu trouvé
if lieux.empty:
    st.error("Aucun lieu trouvé pour cette combinaison.")
    st.stop()

# ============================================================
# IA — Construction du prompt
# ============================================================
def construire_prompt(pays, categorie, lieux):
    texte = ""
    for _, row in lieux.iterrows():
        texte += (
            f"- {row['nom_lieu']} | Prix : {row['prix']}€ | ⭐ {row['note5']}/5\n"
            f"  Idéal pour : {row['ideal_pour']}\n"
            f"  Réserver : {row['url_reservation']}\n\n"
        )

    prompt = f"""
Tu es un expert en organisation de voyages.

Crée pour moi un **séjour parfait de 3 jours** à **{pays}**, en me proposant des activités dans la catégorie **{categorie}**.

Voici la liste des lieux à utiliser :

{texte}

### FORMAT ATTENDU :
- 🗓️ Description détaillée de chaque journée (Jour 1, Jour 2, Jour 3)
- ✨ Pourquoi ces lieux sont intéressants
- 🔗 Inclure les liens de réservation intégrés naturellement dans le texte
- 💡 Conseils pratiques personnalisés

Génère le texte en français, fluide, inspirant et agréable à lire.
"""
    return prompt

# ============================================================
# GROQ API
# ============================================================
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generer_sejour(prompt):
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500,
        )
        return response.choices[0].message["content"]
    except Exception as e:
        return None, e

# ============================================================
# BOUTON — LANCER L'IA
# ============================================================
if st.button("✨ Générer mon séjour parfait"):
    st.info("⏳ L’IA prépare votre séjour, un instant…")

    prompt = construire_prompt(pays_selection, categorie_selection, lieux)
    result = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1500
    )

    texte = result.choices[0].message["content"]

    st.success("✨ Voici votre séjour parfait :")
    st.markdown(texte)


import streamlit as st
import pandas as pd
from groq import Groq

st.set_page_config(page_title="Voyage IA", layout="centered")

# ------------------------------
# Charger les données
# ------------------------------
df = pd.read_excel("data.xlsx")

# Normalisation des colonnes
df.columns = [c.lower().strip().replace(" ", "_") for c in df.columns]

# Identifier automatiquement la colonne de note
possible_note_cols = ["note5", "note_5", "note", "note_sur_5", "note/5"]
col_note = None
for col in possible_note_cols:
    if col in df.columns:
        col_note = col
        break

if col_note is None:
    st.error("⚠️ Aucune colonne de notation trouvée dans le fichier Excel !")
    st.stop()

# ------------------------------
# IA
# ------------------------------
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def construire_prompt(pays, categorie, lieux):
    texte = ""

    for _, row in lieux.iterrows():
        note_value = row[col_note] if not pd.isna(row[col_note]) else "N/A"

        texte += (
            f"- {row['nom_lieu']} | "
            f"Prix : {row['prix']}€ | ⭐ {note_value}/5 | "
            f"Idéal pour : {row['ideal_pour']} | "
            f"Réserver : {row['url_reservation']}\n"
        )

    prompt = f"""
Tu es un expert en création de voyages.

Génère un **itinéraire parfait de 2 jours** pour quelqu’un voyageant à **{pays}**, 
dans la catégorie d’activité **{categorie}**.

Voici la liste des lieux recommandés :

{texte}

Exigences :
- Décris le voyage **jour par jour**
- Explique pourquoi chaque lieu est exceptionnel
- Ajoute des conseils pratiques
- Style clair, inspirant et professionnel.
"""
    return prompt


# ------------------------------
# Interface
# ------------------------------
st.title("✨ Générateur de séjour parfait (IA)")

# Choix pays
pays = st.selectbox("🌍 Choisissez un pays :", sorted(df["pays"].unique()))

# Choix catégorie filtrée automatiquement
categories_disponibles = sorted(df[df["pays"] == pays]["categorie"].unique())
categorie = st.selectbox("🍀 Choisissez une catégorie d’activité :", categories_disponibles)

# Récup lieux
lieux = df[(df["pays"] == pays) & (df["categorie"] == categorie)]

if lieux.empty:
    st.error("❌ Aucun lieu disponible pour cette combinaison.")
    st.stop()

# ------------------------------
# Bouton génération
# ------------------------------
if st.button("✨ Générer mon séjour parfait"):
    with st.spinner("🤖 L’IA prépare votre voyage…"):
        prompt = construire_prompt(pays, categorie, lieux)

        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1200,
        )

        texte_final = response.choices[0].message["content"]

    st.success("Votre séjour personnalisé est prêt ✨")
    st.write(texte_final)

import streamlit as st
import pandas as pd
from groq import Groq

# ------------------------------
# CONFIGURATION PAGE
# ------------------------------
st.set_page_config(page_title="Générateur de séjour parfait", layout="wide")

st.title("✨ Générateur de séjour parfait (IA)")

# ------------------------------
# CHARGEMENT DU FICHIER EXCEL
# ------------------------------

@st.cache_data
def load_data():
    df = pd.read_excel("data.xlsx")

    # Normalisation douce des noms de colonnes
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("/", "_")
        .str.replace("-", "_")
    )
    return df

df = load_data()


# ------------------------------
# DÉTECTION AUTOMATIQUE DE LA COLONNE "NOTE"
# ------------------------------

def detect_note_column(columns):
    """
    Trouve automatiquement une colonne correspondant à une note / rating.
    Compatible avec note5, note_5, note, note_sur_5, note/5 ...
    """
    possible_keywords = ["note", "rating", "stars", "5"]

    for col in columns:
        for key in possible_keywords:
            if key in col:
                return col

    return None  # Cas très improbable


note_col = detect_note_column(df.columns)


# ------------------------------
# INTERFACE : CHOIX DU PAYS & CATÉGORIE
# ------------------------------

pays_list = sorted(df["pays"].unique())
pays = st.selectbox("🌍 Choisissez un pays :", pays_list)

# catégories disponibles uniquement pour ce pays
categories_dispo = sorted(df[df["pays"] == pays]["categorie"].unique())
categorie = st.selectbox("🍀 Choisissez une catégorie d’activité :", categories_dispo)


# ------------------------------
# SÉLECTION DES LIEUX POUR CE PAYS + CATÉGORIE
# ------------------------------

lieux_selectionnes = df[(df["pays"] == pays) & (df["categorie"] == categorie)]

if lieux_selectionnes.empty:
    st.error("Aucun lieu trouvé pour cette combinaison.")
else:
    st.success(f"{len(lieux_selectionnes)} lieu(x) trouvé(s) ✔")


# ------------------------------
# CONSTRUCTION DU PROMPT IA
# ------------------------------

def construire_prompt(pays, categorie, lieux):
    texte = ""

    for _, row in lieux.iterrows():
        texte += (
            f"- **{row['nom_lieu']}** ({row['ville']})\n"
            f"  - ⭐ Note : {row[note_col]}/5\n"
            f"  - Idéal pour : {row['ideal_pour']}\n"
            f"  - 🔗 Réservation : {row['url_reservation']}\n\n"
        )

    prompt = f"""
Tu es un expert en voyages.

Crée un **séjour parfait de 3 jours** à **{pays}**, dans la catégorie **{categorie}**.

Voici les lieux disponibles :

{texte}

Donne :
- un programme détaillé jour par jour  
- pourquoi ces lieux sont intéressants  
- des conseils pratiques  
- et termine par un récapitulatif de **tous les liens de réservation**.

Sois clair, inspirant et structuré.
"""

    return prompt


# ------------------------------
# APPEL À GROQ (LLAMA 3.1)
# ------------------------------

def generer_sejour(prompt):
    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])

        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "Tu es un expert en organisation de voyages."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=1500,
            temperature=0.7
        )

        return completion.choices[0].message["content"]

    except Exception as e:
        return f"❌ Erreur API : {e}"


# ------------------------------
# BOUTON
# ------------------------------

if st.button("✨ Générer mon séjour parfait", type="primary"):

    with st.spinner("🤖 L’IA prépare votre séjour, un instant..."):
        prompt = construire_prompt(pays, categorie, lieux_selectionnes)
        resultat = generer_sejour(prompt)

    st.success("🎉 Séjour généré ! Voici votre proposition :")
    st.markdown(resultat)



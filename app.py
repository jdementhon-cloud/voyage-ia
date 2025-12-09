import streamlit as st
import pandas as pd
from groq import Groq

# -----------------------
#  CONFIG
# -----------------------
st.set_page_config(page_title="Générateur de Séjour Parfait", layout="wide")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# -----------------------
#  FUNCTIONS
# -----------------------

def nettoyer_colonnes(df):
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    return df


def construire_prompt(pays, categorie, lieux):
    texte = ""

    for _, row in lieux.iterrows():
        texte += (
            f"- **{row['nom_lieu']}** ({row['ville']})\n"
            f"  - Prix : {row['prix']}€\n"
            f"  - ⭐ Note : {row['note5']}/5\n"
            f"  - Idéal pour : {row['ideal_pour']}\n"
            f"  - 🔗 Réservation : {row['url_reservation']}\n\n"
        )

    prompt = f"""
Tu es un expert en voyages.

Crée un **séjour parfait de 3 jours** à **{pays}**, avec des activités dans la catégorie **{categorie}**.

Voici les lieux disponibles à intégrer dans ton plan :

{texte}

Délivre :
- un programme détaillé jour par jour  
- pourquoi ces lieux sont intéressants  
- des conseils pratiques  
- et à la fin, récapitule tous les **liens de réservation** fournis.

Format : clair, inspirant, facile à lire.
"""

    return prompt


def generer_sejour(prompt):
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500,
        )

        # Correct access
        return response.choices[0].message.content

    except Exception as e:
        return f"❌ Erreur IA : {e}"


# -----------------------
#  LOAD DATA
# -----------------------

df = pd.read_excel("data.xlsx")
df = nettoyer_colonnes(df)

# -----------------------
#  UI
# -----------------------

st.title("✨ Générateur de séjour parfait (IA)")

# --- CHOIX PAYS
pays_disponibles = sorted(df["pays"].unique())
pays = st.selectbox("🌍 Choisissez un pays :", pays_disponibles)

# --- CHOIX CATEGORIE (filtrée selon le pays)
categories = sorted(df[df["pays"] == pays]["categorie"].unique())
categorie = st.selectbox("🍀 Choisissez une catégorie d’activité :", categories)

# --- FILTRAGE DES LIEUX
lieux_selectionnes = df[(df["pays"] == pays) & (df["categorie"] == categorie)]

# --- GENERATION SEJOUR
if st.button("✨ Générer mon séjour parfait"):
    if lieux_selectionnes.empty:
        st.error("Aucun lieu trouvé pour cette combinaison.")
    else:
        st.info("⏳ L’IA prépare votre séjour, un instant…")

        prompt = construire_prompt(pays, categorie, lieux_selectionnes)
        resultat = generer_sejour(prompt)

        st.success("🎉 Séjour généré ! Voici votre proposition :")
        st.write(resultat)

        # Affichage des liens de réservation à part
        st.subheader("🔗 Liens de réservation :")
        for _, row in lieux_selectionnes.iterrows():
            st.markdown(f"- [{row['nom_lieu']}]({row['url_reservation']})")

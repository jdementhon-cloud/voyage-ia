import streamlit as st
import pandas as pd
from groq import Groq
import os

# ================================
#       CONFIGURATION STREAMLIT
# ================================
st.set_page_config(page_title="Séjour parfait (IA)", layout="centered")

st.markdown(
    "<h1 style='text-align:center'>✨ Générateur de séjour parfait (IA)</h1>",
    unsafe_allow_html=True,
)

# ================================
#          CHARGEMENT DATA
# ================================
@st.cache_data
def load_data():
    df = pd.read_excel("data.xlsx")
    df.columns = df.columns.str.lower().str.strip()

    df.rename(
        columns={
            "note/5": "note5",
            "idéal_pour": "ideal_pour",
            "nombre_d’avis": "nombre_davis",
        },
        inplace=True,
        errors="ignore"
    )
    return df

df = load_data()

# ================================
#          INTERFACE
# ================================
pays_list = sorted(df["pays"].dropna().unique())
pays = st.selectbox("🌍 Choisissez un pays :", pays_list)

# Filtrage dynamique des catégories selon le pays
categories_list = sorted(df[df["pays"] == pays]["categorie"].dropna().unique())
categorie = st.selectbox("🍀 Choisissez une catégorie d’activité :", categories_list)

# Lieux sélectionnés
lieux = df[(df["pays"] == pays) & (df["categorie"] == categorie)]

# ================================
#   FONCTION : CONSTRUIRE PROMPT
# ================================
def construire_prompt(pays, categorie, lieux):
    texte = ""
    for _, row in lieux.iterrows():
        texte += (
            f"- **{row['nom_lieu']}**, {row['ville']} — ⭐ {row['note5']}/5\n"
            f"  👉 Idéal pour : {row['ideal_pour']}\n"
            f"  💰 Prix : {row['prix']}€\n"
            f"  🔗 Réservation : {row['url_reservation']}\n\n"
        )

    prompt = f"""
Tu es un expert en organisation de voyages.

Crée un **séjour parfait de 3 jours** pour une personne visitant **{pays}**, 
dans le thème : **{categorie}**.

Voici les lieux recommandés à inclure dans l'itinéraire :

{texte}

FORMAT ATTENDU :
- Une organisation **jour par jour**
- Une explication courte de pourquoi chaque lieu est choisi
- Des conseils pratiques
- Ajoute les liens de réservation fournis dans les lieux
- Ton ton doit être inspirant et fluide

Rédige maintenant le séjour parfait.
"""
    return prompt

# ================================
#   GROQ : APPEL AU MODÈLE IA
# ================================
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generer_sejour(prompt):
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",  # ✅ Modèle correct
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500,
        )
        return response.choices[0].message["content"]
    except Exception as e:
        return None, e

# ================================
#   BOUTON GENERATION IA
# ================================
st.write("")  # espace visuel

if st.button("✨ Générer mon séjour parfait", type="primary"):

    if lieux.empty:
        st.error("Aucun lieu trouvé pour cette combinaison.")
    else:
        st.info("⏳ L’IA prépare votre séjour, un instant...")

        prompt = construire_prompt(pays, categorie, lieux)
        texte, erreur = generer_sejour(prompt)

        if erreur:
            st.error("Erreur lors de l’appel à l’IA.")
            st.code(str(erreur))
        else:
            st.success("🎉 Votre séjour est prêt !")
            st.markdown(texte)


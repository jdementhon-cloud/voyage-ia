import streamlit as st
import pandas as pd
from groq import Groq
import os

# ---- CONFIG ----
st.set_page_config(page_title="Voyage IA Premium", layout="wide")

# Clé API Groq
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# ---- FONCTIONS ----
def generer_prompt(pays, categorie, lieux):
    """
    Construit un prompt premium pour générer un séjour complet.
    """
    description_lieux = "\n".join([
        f"- {row['nom_lieu']} | {row['prix']}€ | Note: {row['note/5']} ⭐ | Idéal pour: {row['ideal_pour']}"
        for _, row in lieux.iterrows()
    ])

    prompt = f"""
Tu es un *expert premium en création de voyages sur mesure*.

Ta mission : créer **le séjour parfait** pour une personne se rendant dans **{pays}**, 
cherchant une expérience **{categorie}**.

Voici les activités disponibles pour cette destination :

{description_lieux}

⚠️ Impératifs :
- Structure ta réponse en 4 sections :
  1️⃣ **Résumé du séjour** (1 paragraphe)
  2️⃣ **Planning parfait sur 2 jours** (format clair, avec horaires)
  3️⃣ **Top recommandations personnalisées**
  4️⃣ **Liens directs de réservation** (utilise uniquement les URLs fournies dans le dataset)

- Mets en avant les lieux qui correspondent le mieux à la catégorie.
- Garde un ton professionnel mais engageant.
- Retourne du texte structuré, lisible, premium.

Réponds uniquement en français.
"""
    return prompt


def generer_contenu_ia(prompt):
    """
    Appel Groq avec modèle premium.
    """
    reponse = client.chat.completions.create(
        model="llama3-8b-8192",   # modèle Groq efficace & rapide
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return reponse.choices[0].message["content"]


# ---- INTERFACE ----
st.title("🌍✨ Générateur de séjour parfait (version PREMIUM IA)")

# Chargement du dataset
df = pd.read_csv("data.csv") if "data.csv" in os.listdir() else pd.read_excel("data.xlsx")

# Normalisation des colonnes
df.columns = df.columns.str.lower().str.replace(" ", "_")

st.subheader("Choisissez un pays et une catégorie d'activité")

pays_list = sorted(df["pays"].unique())
categorie_list = sorted(df["categorie"].unique())

col1, col2 = st.columns(2)
with col1:
    pays = st.selectbox("Pays :", pays_list)

with col2:
    categorie = st.selectbox("Catégorie d’activité :", categorie_list)

if st.button("✨ Générer mon séjour premium"):
    # Filtrer les lieux correspondants
    lieux = df[df["pays"] == pays]

    if lieux.empty:
        st.error("Aucun lieu trouvé pour ce pays.")
    else:
        with st.spinner("🤖 L’IA prépare un séjour exceptionnel…"):
            prompt = generer_prompt(pays, categorie, lieux)
            try:
                texte_ia = generer_contenu_ia(prompt)
                st.success("🎉 Votre séjour premium est prêt !")
                st.markdown(texte_ia)

                # Ajouter une zone d'expansion avec les données brutes
                with st.expander("Voir les lieux utilisés (dataset)"):
                    st.write(lieux)

            except Exception as e:
                st.error(f"Erreur IA : {e}")


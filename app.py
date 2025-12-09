import streamlit as st
import pandas as pd
from groq import Groq

st.set_page_config(page_title="Voyage IA", layout="centered")

# ------------------------------
# 🔑 Chargement des données
# ------------------------------
df = pd.read_excel("data.xlsx")

# Nettoyage colonnes
df.columns = [c.lower().strip().replace(" ", "_") for c in df.columns]

# ------------------------------
# 🧠 Client IA
# ------------------------------
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# ------------------------------
# 🛠️ Prompt generator
# ------------------------------
def construire_prompt(pays, categorie, lieux):
    texte = ""
    
    for _, row in lieux.iterrows():
        texte += (
            f"- {row['nom_lieu']} | "
            f"Prix : {row['prix']}€ | ⭐ {row['note5']}/5 | "
            f"Idéal pour : {row['ideal_pour']} | "
            f"Réservation : {row['url_reservation']}\n"
        )

    prompt = f"""
Tu es un expert en création de voyages.

Génère un **itinéraire parfait de 2 jours** pour quelqu’un voyageant à **{pays}**, 
dans la catégorie d’activité **{categorie}**.

Voici les lieux recommandés :

{texte}

Exigences :
- Décris le voyage **jour par jour**
- Explique pourquoi chaque lieu est exceptionnel
- Ajoute des conseils pratiques
- Utilise un style clair, inspirant et professionnel.
"""
    return prompt


# ------------------------------
# 🎨 Interface
# ------------------------------
st.title("✨ Générateur de séjour parfait (IA)")

# ▪️ Sélection pays
pays = st.selectbox("🌍 Choisissez un pays :", sorted(df["pays"].unique()))

# ▪️ Filtrage dynamique des catégories
categories_disponibles = sorted(df[df["pays"] == pays]["categorie"].unique())

categorie = st.selectbox("🍀 Choisissez une catégorie d’activité :", categories_disponibles)

# ▪️ Recherche des lieux correspondants
lieux = df[(df["pays"] == pays) & (df["categorie"] == categorie)]

if lieux.empty:
    st.error("Aucun lieu trouvé pour cette combinaison.")
else:
    # Pas de tableau, pas de cadre → TOUT CLEAN
    st.write(f"{len(lieux)} lieu(x) trouvé(s) ✔️")

    # ------------------------------
    # ▶️ Bouton pour générer le séjour
    # ------------------------------
    if st.button("✨ Générer mon séjour parfait"):
        with st.spinner("🤖 L’IA prépare votre itinéraire…"):
            prompt = construire_prompt(pays, categorie, lieux)

            response = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1200,
            )

            texte_final = response.choices[0].message["content"]

        st.success("Votre séjour personnalisé est prêt ✨")
        st.write(texte_final)

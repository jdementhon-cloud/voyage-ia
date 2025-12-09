import os
import streamlit as st
import pandas as pd
from groq import Groq

# Chargement de la clé API depuis l'environnement (Streamlit Cloud)
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

# -----------------------
# Chargement des données
# -----------------------
df = pd.read_excel("data.xlsx")

# Normalisation des colonnes
df.columns = (
    df.columns
    .str.lower()
    .str.replace(" ", "_")
    .str.replace("/", "")
)

st.title("🌍 Générateur de séjour parfait (IA)")

st.write("Choisissez un **pays** et une **catégorie d’activité**, l’IA s’occupe du reste ✨")

# Vérification colonne disponibles
st.write("### Colonnes disponibles :")
st.json(df.columns.tolist())

# -----------------------
# Sélections utilisateur
# -----------------------
pays = st.selectbox("Choisissez un pays :", sorted(df["pays"].unique()))
categorie = st.selectbox("Choisissez une catégorie d’activité :", sorted(df["categorie"].unique()))

# Filtrage selon choix
filtre = df[(df["pays"] == pays) & (df["categorie"] == categorie)]

if filtre.empty:
    st.error("Aucun résultat trouvé pour cette combinaison.")
    st.stop()

# Sélectionne 3 lieux max pour ne pas surcharger le prompt
lieux = filtre.sample(min(3, len(filtre))).to_dict(orient="records")

# -----------------------
# Prompt IA
# -----------------------
def generer_prompt(pays, categorie, lieux):
    description_lieux = "\n".join([
        f"- {l['nom_lieu']} : {l['prix']}€ | ⭐ {l['note5']} | Idéal pour : {l['ideal_pour']}"
        for l in lieux
    ])

    prompt = f"""
Tu es un expert en création de voyages.

Crée un **séjour parfait de 3 jours** à **{pays}**, basé sur la catégorie : **{categorie}**.

Voici des lieux sélectionnés :

{description_lieux}

⚡ Instructions :
- Propose un programme jour par jour
- Inclure : activités, astuces locales, budget estimé, meilleur moment de la journée
- Style : clair, inspirant, dynamique
"""

    return prompt

# -----------------------
# Appel Groq
# -----------------------
def generer_sejour(prompt):
    try:
        response = client.chat.completions.create(
            model="mixtral-8x7b-32768",  # modèle fiable et disponible
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        return response.choices[0].message["content"]

    except Exception as e:
        return f"❌ Erreur API : {e}"

# -----------------------
# Bouton IA
# -----------------------
if st.button("✨ Générer mon séjour parfait"):
    with st.spinner("⏳ L’IA prépare votre séjour…"):
        prompt = generer_prompt(pays, categorie, lieux)
        sejour = generer_sejour(prompt)

    st.write("## 🏖️ Votre séjour personnalisé")
    st.write(sejour)

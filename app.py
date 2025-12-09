import streamlit as st
import pandas as pd
from groq import Groq
import os

# -------------------------------
#  CONFIG GROQ
# -------------------------------
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# -------------------------------
#  CHARGEMENT DES DONNÉES
# -------------------------------
df = pd.read_excel("data.xlsx")
df.columns = df.columns.str.lower().str.strip()

# normalisation colonnes
rename_map = {
    "pays": "pays",
    "ville": "ville",
    "nom_lieu": "nom_lieu",
    "categorie": "categorie",
    "pour_qui": "pour_qui",
    "latitude": "latitude",
    "longitude": "longitude",
    "prix": "prix",
    "note5": "note5",
    "nombre_d'avis": "nombre_avis",
    "ideal_pour": "ideal_pour",
    "lien_images": "lien_images",
    "url_reservation": "url_reservation"
}

df = df.rename(columns=rename_map)

# -------------------------------
#  FONCTION : CONSTRUIRE LE PROMPT
# -------------------------------
def construire_prompt(pays, categorie, lieux):
    texte = ""

    for _, row in lieux.iterrows():
        texte += (
            f"- {row['nom_lieu']} ({row['ville']}) | "
            f"Prix : {row['prix']}€ | ⭐ {row['note5']}/5 | "
            f"Idéal pour : {row['ideal_pour']} | "
            f"Réservation : {row['url_reservation']}\n"
        )

    prompt = f"""
Tu es un expert en création d’itinéraires de voyage.

Crée un **séjour parfait de 3 jours** à **{pays}**, dans le thème : **{categorie}**.

Voici les lieux disponibles :
{texte}

INSTRUCTIONS :
- Donne un planning J1 / J2 / J3 clair.
- Explique pourquoi chaque lieu est exceptionnel.
- Ajoute des conseils d'expert.
- Référence les lieux dans l'ordre logique d'une vraie journée.

Format attendu : texte clair, structuré, sans liste brute.
"""

    return prompt


# -------------------------------
#  FONCTION IA : APPEL GROQ
# -------------------------------
def generer_sejour(prompt):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",  # modèle sûr et dispo
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1500,
    )
    return response.choices[0].message["content"]


# -------------------------------
#  INTERFACE STREAMLIT
# -------------------------------
st.title("✨ Générateur de Séjour Parfait – IA ✨")

# Choix du pays
pays = st.selectbox("🌍 Choisissez un pays :", sorted(df["pays"].unique()))

# Filtrer les catégories disponibles pour ce pays
categories_dispo = sorted(df[df["pays"] == pays]["categorie"].unique())
categorie = st.selectbox("🎨 Choisissez une catégorie d’activité :", categories_dispo)

# Filtrer les lieux correspondant au choix
lieux = df[(df["pays"] == pays) & (df["categorie"] == categorie)]

# Aucun lieu → message
if lieux.empty:
    st.error("Aucun lieu trouvé pour cette combinaison.")
    st.stop()

st.success(f"{len(lieux)} lieux trouvés ✔️")

# Bouton
if st.button("✨ Générer mon séjour parfait"):
    st.info("⏳ L’IA prépare votre séjour, un instant...")

    prompt = construire_prompt(pays, categorie, lieux)
    resultat = generer_sejour(prompt)

    st.subheader("🌅 Votre séjour parfait :")
    st.write(resultat)

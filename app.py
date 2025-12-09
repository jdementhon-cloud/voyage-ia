import streamlit as st
import pandas as pd
from groq import Groq

# =========================
#  CONFIG GROQ
# =========================

GROQ_API_KEY = st.secrets["GROQ_API_KEY"]  
client = Groq(api_key=GROQ_API_KEY)

# =========================
#  LOAD DATA
# =========================

@st.cache_data
def load_data():
    df = pd.read_excel("data.xlsx")

    df.columns = (
        df.columns.str.lower()
        .str.strip()
        .str.replace(" ", "_")
        .str.replace("'", "")
        .str.replace("/", "")
    )
    return df

df = load_data()

# =========================
#  UI TITLE
# =========================

st.title("🌍 Générateur de Séjour Parfait (IA)")

# =========================
#  SELECTORS
# =========================

pays_list = sorted(df["pays"].dropna().unique())
pays = st.selectbox("Choisissez un pays :", pays_list)

# Filtrer les catégories disponibles UNIQUEMENT pour ce pays
categories_disponibles = sorted(df[df["pays"] == pays]["categorie"].dropna().unique())
categorie = st.selectbox("Choisissez une catégorie d’activité :", categories_disponibles)

# Filtrage final
lieux = df[(df["pays"] == pays) & (df["categorie"] == categorie)]

# =========================
#  AFFICHAGE DES LIEUX TROUVÉS
# =========================

if len(lieux) == 0:
    st.error("Aucun lieu disponible pour cette combinaison.")
    st.stop()

st.subheader("Lieux disponibles :")
st.dataframe(lieux[["nom_lieu", "ville", "prix", "note5", "ideal_pour", "url_reservation"]])

# =========================
#  GENERATION PROMPT
# =========================

def generer_prompt(pays, categorie, lieux):

    texte_lieux = ""
    for _, row in lieux.iterrows():
        texte_lieux += (
            f"- **{row['nom_lieu']}** ({row['ville']})\n"
            f"  - Prix : {row['prix']}€\n"
            f"  - ⭐ Note : {row['note5']}/5\n"
            f"  - Idéal pour : {row['ideal_pour']}\n"
            f"  - 🔗 Réservation : {row['url_reservation']}\n\n"
        )

    prompt = f"""
Tu es un expert en voyages.

📍 Crée un **séjour parfait de 3 jours** à **{pays}**  
Catégorie d’activité : **{categorie}**

Voici la liste des lieux recommandés :

{texte_lieux}

🎯 Format demandé :
- Itinéraire détaillé jour par jour
- Explication des choix
- Recommandations pratiques
- Ajouter les liens de réservation déjà fournis
- Ton inspirant mais clair

Merci !
"""
    return prompt

# =========================
#  IA CALL
# =========================

def generer_sejour(prompt):
    response = client.chat.completions.create(
        model="llama-3.1-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1500,
    )
    return response.choices[0].message["content"]

# =========================
#  BTN → GENERATE TRIP
# =========================

if st.button("✨ Générer mon séjour parfait"):
    with st.spinner("L’IA prépare votre programme..."):
        prompt = generer_prompt(pays, categorie, lieux)
        resultat = generer_sejour(prompt)

    st.subheader("🎉 Votre séjour personnalisé :")
    st.write(resultat)

    st.subheader("🔗 Liens de réservation :")
    for _, row in lieux.iterrows():
        st.markdown(f"- [{row['nom_lieu']}]({row['url_reservation']})")

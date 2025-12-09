import streamlit as st
import pandas as pd
from groq import Groq

# ---------------------------
#  CONFIG
# ---------------------------

st.set_page_config(page_title="Générateur de séjour parfait", layout="wide")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])


# ---------------------------
#  CHARGEMENT DES DONNÉES
# ---------------------------

@st.cache_data
def charger_donnees():
    df = pd.read_excel("data.xlsx")

    # Normalisation automatique des colonnes
    df.columns = df.columns.str.lower().str.replace(" ", "_")

    df.rename(
        columns={
            "note/5": "note5",
            "note_5": "note5",
            "nombre_d’avis": "nombre_davis",
            "nombre_d'avis": "nombre_davis",
            "idéal_pour": "ideal_pour",
            "ideal_pour": "ideal_pour",
            "ideal pour": "ideal_pour",
            "pour_qui": "ideal_pour",  # fallback
        },
        inplace=True,
        errors="ignore",
    )

    return df


df = charger_donnees()


# ---------------------------
#  FONCTION PROMPT IA
# ---------------------------

def construire_prompt(pays, categorie, lieux):
    texte = ""

    for _, row in lieux.iterrows():

        ideal = row.get("ideal_pour", "Non précisé")
        prix = row.get("prix", "Non indiqué")
        note = row.get("note5", "N/A")
        url = row.get("url_reservation", "Aucun lien fourni")

        texte += (
            f"- **{row['nom_lieu']}**, {row.get('ville', '')} — ⭐ {note}/5\n"
            f"  👉 Idéal pour : {ideal}\n"
            f"  💰 Prix : {prix}€\n"
            f"  🔗 Réservation : {url}\n\n"
        )

    prompt = f"""
Tu es un expert en voyages.

Crée un **séjour parfait de 3 jours** pour quelqu’un visitant **{pays}**,
centré sur la catégorie d’activité **{categorie}**.

Voici les lieux recommandés à inclure dans l’itinéraire :

{texte}

FORMAT ATTENDU :
- Une organisation détaillée **jour par jour**
- Explication du choix des lieux
- Conseils pratiques
- Un ton humain, inspirant et fluide
- Inclure les liens de réservation dans le texte
"""

    return prompt


# ---------------------------
#  FONCTION APPEL GROQ
# ---------------------------

def generer_sejour(prompt):
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500,
        )

        return response.choices[0].message["content"]

    except Exception as e:
        return f"❌ Erreur : {e}"


# ---------------------------
#  INTERFACE STREAMLIT
# ---------------------------

st.markdown("<h1>✨ Générateur de séjour parfait (IA)</h1>", unsafe_allow_html=True)

# Sélecteur pays
pays_liste = sorted(df["pays"].dropna().unique())
pays = st.selectbox("🌎 Choisissez un pays :", pays_liste)

# Sélecteur catégorie filtré selon pays
categories_dispo = sorted(df[df["pays"] == pays]["categorie"].dropna().unique())
categorie = st.selectbox("🍀 Choisissez une catégorie d’activité :", categories_dispo)

# Recherche des lieux correspondant
lieux = df[(df["pays"] == pays) & (df["categorie"] == categorie)]

# Bouton
generer = st.button("✨ Générer mon séjour parfait")

# ---------------------------
#  ACTION : GENERATION IA
# ---------------------------

if generer:

    if lieux.empty:
        st.error("Aucun lieu trouvé pour cette combinaison.")
    else:
        with st.spinner("⏳ L’IA prépare votre séjour, un instant…"):
            prompt = construire_prompt(pays, categorie, lieux)
            resultat = generer_sejour(prompt)

        st.success("🎉 Séjour généré ! Voici votre proposition :")
        st.markdown(resultat)

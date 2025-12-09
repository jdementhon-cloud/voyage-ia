import streamlit as st
import pandas as pd
from groq import Groq

# -------------------------------------
# CONFIG STREAMLIT
# -------------------------------------
st.set_page_config(page_title="Générateur de séjour parfait", layout="wide")

st.title("✨ Générateur de séjour parfait (IA)")

# -------------------------------------
# CHARGEMENT DES DONNÉES
# -------------------------------------
df = pd.read_excel("data.xlsx")

# Nettoyage des colonnes (minuscules)
df.columns = df.columns.str.lower().str.replace(" ", "_")

# -------------------------------------
# INTERFACE UTILISATEUR
# -------------------------------------

# ---- Choix du pays ----
pays = st.selectbox("🌍 Choisissez un pays :", sorted(df["pays"].dropna().unique()))

# ---- Choix de catégorie filtrée par pays ----
categories_disponibles = df[df["pays"] == pays]["categorie"].dropna().unique()
categorie = st.selectbox("🍀 Choisissez une catégorie d’activité :", sorted(categories_disponibles))

# ---- Filtrer les lieux correspondants ----
lieux_selectionnes = df[(df["pays"] == pays) & (df["categorie"] == categorie)]

if lieux_selectionnes.empty:
    st.error("Aucun lieu trouvé pour cette combinaison.")
else:
    st.success(f"{len(lieux_selectionnes)} lieu(x) trouvé(s) ✔")

# =====================================
# 🗺️ CARTE INTERACTIVE
# =====================================
st.subheader("🗺️ Carte interactive des lieux sélectionnés")

if "latitude" in lieux_selectionnes.columns and "longitude" in lieux_selectionnes.columns:
    
    lieux_map = lieux_selectionnes[["nom_lieu", "latitude", "longitude"]].dropna()

    if not lieux_map.empty:
        st.map(
            lieux_map.rename(columns={"latitude": "lat", "longitude": "lon"}),
            zoom=10,
            use_container_width=True
        )

        with st.expander("Voir les lieux affichés sur la carte"):
            st.dataframe(lieux_map)

    else:
        st.info("Aucune coordonnée disponible pour afficher la carte.")
else:
    st.info("Les colonnes latitude/longitude sont introuvables dans vos données.")

# =====================================
# IA – CONSTRUCTION DU PROMPT
# =====================================

def construire_prompt(pays, categorie, lieux):
    texte = ""
    for _, row in lieux.iterrows():
        texte += (
            f"- **{row['nom_lieu']}**\n"
            f"  • Prix : {row['prix']}€\n"
            f"  • ⭐ Note : {row['note5']}/5\n"
            f"  • Idéal pour : {row['ideal_pour']}\n"
            f"  • 🔗 Réservation : {row['url_reservation']}\n\n"
        )

    prompt = f"""
Tu es un expert en création d’itinéraires de voyage.

Crée un **séjour parfait de 1 journée** à **{pays}**, basé sur la catégorie **{categorie}**.

Voici les lieux proposés :

{texte}

Génère un texte structuré contenant :
- 🗓️ Un programme complet heure par heure
- 🎯 Pourquoi ces lieux sont parfaits
- 🚶 Conseils de transport et optimisations
- 🔗 Intègre les liens de réservation dans le texte

Format court, clair et immersif.
"""

    return prompt


# =====================================
# IA – GÉNÉRATION AVEC GROQ
# =====================================

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def generer_sejour(prompt):
    try:
        response = client.chat.completions.create(
            model="llama3-70b-8k-instant",  # modèle fiable
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1200,
        )
        return response.choices[0].message["content"]
    except Exception as e:
        return f"❌ Erreur : {e}"


# =====================================
# BOUTON – GÉNÉRER LE SÉJOUR
# =====================================

if st.button("✨ Générer mon séjour parfait", use_container_width=True):
    with st.spinner("⏳ L’IA prépare votre séjour, un instant…"):
        prompt = construire_prompt(pays, categorie, lieux_selectionnes)
        resultat = generer_sejour(prompt)

    st.subheader("🎉 Séjour généré ! Voici votre proposition :")
    st.write(resultat)

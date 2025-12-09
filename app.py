import streamlit as st
import pandas as pd
from groq import Groq

# ----------------------------
# CONFIG STREAMLIT
# ----------------------------
st.set_page_config(page_title="Séjour Parfait IA", layout="centered")

st.markdown("<h1 style='text-align:center;'>✨ Générateur de séjour parfait (IA)</h1>", unsafe_allow_html=True)

# Chargement du fichier Excel
df = pd.read_excel("data.xlsx")

# Normalisation colonnes
df.columns = [c.lower().strip().replace(" ", "_").replace("/", "_") for c in df.columns]

# Liste des pays
pays_list = sorted(df["pays"].dropna().unique())

# ----------------------------
# CHOIX DU PAYS
# ----------------------------
pays = st.selectbox("🌍 Choisissez un pays :", pays_list)

# Filtrage catégories disponibles pour CE pays
df_filtre_pays = df[df["pays"] == pays]
categories_disponibles = sorted(df_filtre_pays["categorie"].dropna().unique())

categorie = st.selectbox("🍀 Choisissez une catégorie d’activité :", categories_disponibles)

# ----------------------------
# FILTRAGE LIEUX
# ----------------------------
lieux = df_filtre_pays[df_filtre_pays["categorie"] == categorie]

if len(lieux) == 0:
    st.error("Aucun lieu trouvé pour cette combinaison.")
    st.stop()

# ----------------------------
# CONSTRUCTION DU PROMPT
# ----------------------------
def construire_prompt(pays, categorie, lieux):
    texte = ""

    for _, row in lieux.iterrows():
        texte += (
            f"- **{row['nom_lieu']}** à {row['ville']} "
            f"({row['prix']}€) ⭐ {row['note_5']}/5\n"
            f"  👉 Idéal pour : {row['ideal_pour']}\n"
            f"  🔗 Réservation : {row['url_reservation']}\n\n"
        )

    prompt = f"""
Tu es un expert en création de voyages premium.

Génère un **séjour parfait de 3 jours** à **{pays}** basé sur cette catégorie :
👉 **{categorie}**

Voici les lieux à intégrer absolument :

{texte}

### Format attendu :
- **Jour 1**, **Jour 2**, **Jour 3**
- Itinéraire complet + ambiance + conseils
- Pourquoi chaque lieu est exceptionnel
- Intégration des **liens de réservation**
- Style immersif et inspirant

Commence maintenant ⬇️
"""
    return prompt

# ----------------------------
# BOUTON GÉNÉRATION IA
# ----------------------------
if st.button("✨ Générer mon séjour parfait"):

    st.info("⏳ L’IA prépare votre séjour, un instant…")

    prompt = construire_prompt(pays, categorie, lieux)

    client = Groq(api_key=st.secrets["GROQ_API_KEY"])

    try:
        response = client.chat.completions.create(
            model="llama3-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500
        )

        texte_final = response.choices[0].message["content"]

        st.success("🎉 Votre séjour parfait est prêt !")
        st.markdown(texte_final)

    except Exception as e:
        st.error("Erreur lors de l’appel à l’IA.")
        st.code(str(e))

import streamlit as st
import pandas as pd
from groq import Groq
import unidecode

# --- Chargement du dataset ---
df = pd.read_excel("data.xlsx")

# Normalisation des colonnes pour éviter les KeyError
df.columns = [unidecode.unidecode(c).lower().replace(" ", "_") for c in df.columns]

# --- Client Groq ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.title("🌍 Générateur de séjour parfait (IA)")

# Pays
pays = st.selectbox("Choisissez un pays :", sorted(df["pays"].unique()))

# Catégories du pays choisi
categories = sorted(df[df["pays"] == pays]["categorie"].dropna().unique())
categorie = st.selectbox("Choisissez une catégorie d’activité :", categories)

if st.button("✨ Générer mon séjour parfait"):
    st.info("⏳ L’IA prépare votre séjour...")

    lieux = df[(df["pays"] == pays) & (df["categorie"] == categorie)]

    # On sélectionne les colonnes nettoyées
    colonnes_dispo = lieux.columns.tolist()
    st.write("Colonnes disponibles :", colonnes_dispo)  # Debug utile

    # Colonnes simplifiées (version normalisée)
    colonnes_simplifiees = ["nom_lieu", "prix", "note/5", "ideal_pour"]
    colonnes_simplifiees = [c for c in colonnes_simplifiees if c in colonnes_dispo]

    lieux_simplifies = lieux[colonnes_simplifiees].head(12)
    lieux_text = lieux_simplifies.to_string(index=False)

    prompt = f"""
    Crée un séjour parfait en {pays} pour la catégorie {categorie}.
    Voici les lieux possibles :
    {lieux_text}
    """

    try:
        response = client.chat.completions.create(
            model="llama3-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        texte = response.choices[0].message["content"]
        st.success("🎉 Voici votre séjour parfait :")
        st.write(texte)

    except Exception as e:
        st.error(f"Erreur Groq : {e}")

import streamlit as st
import pandas as pd
from groq import Groq

# --- Chargement du dataset ---
df = pd.read_excel("data.xlsx")
df.columns = df.columns.str.strip()

# --- Client Groq (clé chargée depuis Streamlit Secrets) ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- Interface Streamlit ---
st.title("🌍 Générateur de séjour parfait (IA)")
st.write("Choisissez un **pays** et une **catégorie d’activité**, l’IA se charge du reste ✨")

pays = st.selectbox("Choisissez un pays :", sorted(df["PAYS"].unique()))

categories = sorted(df[df["PAYS"] == pays]["CATEGORIE"].dropna().unique())
categorie = st.selectbox("Choisissez une catégorie d’activité :", categories)

# --- Bouton ---
if st.button("✨ Générer mon séjour parfait"):
    st.info("⏳ L’IA prépare votre séjour...")

    # Filtre les lieux correspondants
    lieux = df[(df["PAYS"] == pays) & (df["CATEGORIE"] == categorie)]

    # Convertit les lieux trouvés en texte lisible
    lieux_text = lieux.to_string(index=False)

    # Prompt IA
    prompt = f"""
    Tu es une IA experte en voyage.
    Crée un séjour parfait en {pays} basé sur la catégorie {categorie}.
    Utilise uniquement les lieux suivants :

    {lieux_text}

    Donne un plan clair, structuré, inspirant et agréable à lire.
    """

    # Appel API Groq
    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    # Récupération du texte
    texte = response.choices[0].message["content"]

    st.success("🎉 Voici votre séjour parfait :")
    st.write(texte)

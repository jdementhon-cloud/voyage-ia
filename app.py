import streamlit as st
import pandas as pd
from groq import Groq

# --- Chargement du dataset ---
df = pd.read_excel("data.xlsx")
df.columns = df.columns.str.strip()

# --- Client Groq (clé sécurisée dans Streamlit Cloud) ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- Interface ---
st.title("🌍 Générateur de séjour parfait (IA)")
st.write("Choisissez un **pays** et une **catégorie d’activité**, l’IA se charge du reste ✨")

pays = st.selectbox("Choisissez un pays :", sorted(df["PAYS"].unique()))

categories = sorted(df[df["PAYS"] == pays]["CATEGORIE"].dropna().unique())
categorie = st.selectbox("Choisissez une catégorie d’activité :", categories)

# --- Action ---
if st.button("✨ Générer mon séjour parfait"):
    st.info("⏳ L’IA prépare votre séjour...")

    lieux = df[(df["PAYS"] == pays) & (df["CATEGORIE"] == categorie)]

    # 🔥 On réduit les infos envoyées à l’IA pour éviter BadRequest
    lieux_simplifies = lieux[["NOM_LIEU", "PRIX", "NOTE/5", "IDÉAL POUR"]].head(12)

    lieux_text = lieux_simplifies.to_string(index=False)

    prompt = f"""
    Tu es une IA experte en voyage.
    Crée un séjour parfait en {pays} pour la catégorie {categorie}.

    Voici une sélection réduite de lieux à utiliser :
    {lieux_text}

    Donne un plan clair, structuré, détaillé et inspirationnel.
    """

    try:
        response = client.chat.completions.create(
            model="llama3-8b-instant",   # 🔥 Modèle valide Groq
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        texte = response.choices[0].message["content"]
        st.success("🎉 Voici votre séjour parfait :")
        st.write(texte)

    except Exception as e:
        st.error(f"Erreur Groq : {e}")

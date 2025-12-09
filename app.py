import streamlit as st
import pandas as pd

st.title("Test affichage Streamlit")

# --- Chargement du fichier ---
st.write("Chargement du fichier...")

df = pd.read_excel("data.xlsx")

# Normalisation des colonnes (évite les accents)
df.columns = df.columns.str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')

st.write("Colonnes détectées :", list(df.columns))

# Menu simple
pays = st.selectbox("Choisissez un pays", sorted(df["pays"].unique()))
categorie = st.selectbox("Choisissez une catégorie", sorted(df["categorie"].unique()))

st.write("Si tu vois cette phrase, l’app FONCTIONNE 👍")

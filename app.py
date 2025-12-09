import streamlit as st
import pandas as pd
import os
import unicodedata
from groq import Groq

# =============================
# 1 — Chargement du fichier Excel
# =============================

@st.cache_data
def load_data():
    df = pd.read_excel("data.xlsx")

    # Normalisation des colonnes
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    # Fonction pour nettoyer le texte (accents, espaces, minuscule)
    def clean_text(x):
        if isinstance(x, str):
            x = x.strip().lower()
            x = "".join(
                c for c in unicodedata.normalize("NFD", x)
                if unicodedata.category(c) != "Mn"
            )
        return x

    # Création de colonnes normalisées
    df["pays_clean"] = df["pays"].apply(clean_text)
    df["categorie_clean"] = df["categorie"].apply(clean_text)

    return df, clean_text

df, clean_text = load_data()

st.title("🌍 Générateur de séjour parfait (IA)")

st.write("Choisissez un **pays** et une **catégorie d’activité**, l’IA se charge du reste ✨")

# =============================
# 2 — Sélecteurs utilisateur
# =============================

pays = st.selectbox("Choisissez un pays :", sorted(df["pays"].unique()))
categorie = st.selectbox("Choisissez une catégorie d’activité :", sorted(df["categorie"].unique()))

# =============================
# 3 — Filtrage intelligent
# =============================

filtre = df[
    (df["pays_clean"] == clean_text(pays)) &
    (df["categorie_clean"] == clean_text(categorie))
]

if filtre.empty:
    st.error("Aucun résultat trouvé pour cette combinaison.")
    st.stop()

# On simplifie les infos pour l’IA
lieux_simplifies = filtre[[
    "nom_lieu", "prix", "note5", "ideal_pour", "url_reservation"
]].head(5)

# =============================
# 4 — Construction du prompt IA
# =============================

def generer_prompt(pays, categorie, lieux):
    texte_lieux = ""
    for _, row in lieux.iterrows():
        texte_lieux += (
            f"- {ro

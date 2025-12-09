import streamlit as st
import pandas as pd

# ============================
#   CHARGEMENT DU FICHIER
# ============================
st.title("Test Application Voyage – Version Simple")

try:
    df = pd.read_excel("data.xlsx")
except Exception as e:
    st.error(f"Erreur lors du chargement du fichier : {e}")
    st.stop()

st.subheader("Colonnes détectées :")
st.write(list(df.columns))

# ============================
#   CORRECTION DES NOMS DE COLONNES (pour enlever espaces/accents)
# ============================

df.columns = (
    df.columns
    .str.lower()
    .str.replace(" ", "_")
    .str.replace("é", "e")
    .str.replace("'", "")
)

st.subheader("Colonnes après normalisation :")
st.write(list(df.columns))

# ============================
#   SELECTBOX PAYS
# ============================
if "pays" not in df.columns:
    st.error("La colonne 'pays' est absente du fichier Excel.")
    st.stop()

pays_selectionne = st.selectbox("Choisissez un pays :", sorted(df["pays"].dropna().unique()))

# ============================
#   SELECTBOX CATEGORIE
# ============================
if "categorie" not in df.columns:
    st.error("La colonne 'categorie' est absente du fichier Excel.")
    st.stop()

categories_dispos = sorted(df[df["pays"] == pays_selectionne]["categorie"].dropna().unique())

categorie_selectionnee = st.selectbox("Choisissez une catégorie :", categories_dispos)

# ============================
#   AFFICHAGE DES LIEUX
# ============================
st.subheader("Résultats :")

resultats = df[(df["pays"] == pays_selectionne) & (df["categorie"] == categorie_selectionnee)]

if resultats.empty:
    st.warning("Aucun résultat trouvé pour cette combinaison.")
else:
    st.dataframe(resultats)

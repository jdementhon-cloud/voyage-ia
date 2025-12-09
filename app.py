import streamlit as st
import pandas as pd
from groq import Groq

# -----------------------------------
# CONFIG
# -----------------------------------
st.set_page_config(page_title="ATLAS — Voyage IA", layout="wide")

# STYLE CSS PERSONNALISÉ
st.markdown("""
<style>
body {
    background-color: #f5f6fa;
}
.title-atlas {
    font-size: 60px;
    font-weight: 800;
    text-align: center;
    color: #1e1e1e;
    margin-bottom: -10px;
}
.subtitle-atlas {
    font-size: 22px;
    text-align: center;
    color: #555;
    margin-bottom: 40px;
}
.stButton>button {
    background: linear-gradient(90deg, #6a5af9, #805af9);
    color: white;
    padding: 14px 28px;
    border-radius: 12px;
    font-size: 18px;
    border: none;
}
.stButton>button:hover {
    background: linear-gradient(90deg, #5847e8, #6e47e8);
    color: white;
}
.result-box {
    padding: 20px;
    background: #ffffff;
    border-radius: 12px;
    border-left: 6px solid #6a5af9;
    margin-top: 20px;
}
</style>
""", unsafe_allow_html=True)


# -----------------------------------
# TITRE ATLAS
# -----------------------------------
st.markdown("<div class='title-atlas'>ATLAS</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle-atlas'>Créateur d’itinéraires personnalisés grâce à l’IA</div>",
            unsafe_allow_html=True)


# -----------------------------------
# LOAD DATA
# -----------------------------------
@st.cache_data
def load_data():
    df = pd.read_excel("data.xlsx")
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("/", "_")
        .str.replace("-", "_")
    )
    return df

df = load_data()

# Trouver automatiquement la colonne 'note'
note_col_candidates = [c for c in df.columns if "note" in c]
note_col = note_col_candidates[0] if note_col_candidates else None


# -----------------------------------
# UI — CHOIX UTILISATEUR
# -----------------------------------
pays = st.selectbox("🌍 Choisissez une destination :", sorted(df["pays"].unique()))

categories = sorted(df[df["pays"] == pays]["categorie"].unique())
categorie = st.selectbox("🍀 Sélectionnez une catégorie d’activité :", categories)

lieux = df[(df["pays"] == pays) & (df["categorie"] == categorie)]

if lieux.empty:
    st.error("❌ Aucun lieu trouvé pour cette destination et catégorie.")
else:
    st.success(f"🔎 {len(lieux)} lieu(x) disponible(s)")


# -----------------------------------
# PROMPT BUILDER
# -----------------------------------
def construire_prompt(pays, categorie, lieux):
    texte = ""

    for _, row in lieux.iterrows():
        texte += (
            f"- **{row['nom_lieu']}** ({row['ville']})\n"
            f"  ⭐ Note : {row[note_col]}/5\n"
            f"  🏷️ Idéal pour : {row['ideal_pour']}\n"
            f"  🔗 Réservation : {row['url_reservation']}\n\n"
        )

    prompt = f"""
Tu es un expert du voyage haut de gamme.

Génère un **itinéraire inspirant et détaillé de 3 jours** à **{pays}**, 
spécialement centré sur l’activité **{categorie}**.

### Lieux à intégrer obligatoirement :
{texte}

### Format attendu :

**Jour 1 :**  
- activités détaillées  
- intégration d’un des lieux fournis  
- conseils pratiques (durée, transport, horaires)

**Jour 2 :** idem

**Jour 3 :** idem

### À la fin :
Créer un bloc :

### 🔗 Liens de réservation  
- Liste tous les liens fournis

Style premium, immersif, clair, inspirant.
"""
    return prompt


# -----------------------------------
# IA CALL
# -----------------------------------
def generer_sejour(prompt):
    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])

        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "Tu es un expert en création de voyages sur mesure."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=1500,
        )

        # Important : accès correct au contenu
        return completion.choices[0].message.content

    except Exception as e:
        return f"❌ Erreur API : {e}"


# -----------------------------------
# BOUTON
# -----------------------------------
if st.button("✨ Générer mon séjour parfait"):
    with st.spinner("🧭 ATLAS prépare votre itinéraire sur mesure…"):
        prompt = construire_prompt(pays, categorie, lieux)
        resultat = generer_sejour(prompt)

    st.markdown("<div class='result-box'>", unsafe_allow_html=True)
    st.markdown("### 🎉 Votre séjour personnalisé :")
    st.markdown(resultat)
    st.markdown("</div>", unsafe_allow_html=True)

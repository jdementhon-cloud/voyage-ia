import streamlit as st
import pandas as pd
from groq import Groq

# ---------------------------------------------------
# 🔑 Configuration
# ---------------------------------------------------
st.set_page_config(
    page_title="✨ Générateur de séjour parfait (IA)",
    layout="wide"
)

st.markdown(
    """
    <style>
        .title {
            font-size: 42px;
            font-weight: 800;
            color: #4A4AFC;
            text-align: center;
            margin-bottom: 20px;
        }
        .subtitle {
            font-size: 20px;
            font-weight: 600;
            color: #333;
        }
        .result-box {
            background: #F3F8FF;
            padding: 20px;
            border-radius: 12px;
            border-left: 6px solid #4A4AFC;
            margin-top: 20px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("<div class='title'>✨ Générateur de séjour parfait (IA)</div>", unsafe_allow_html=True)

# ---------------------------------------------------
# 📂 Chargement des données
# ---------------------------------------------------
df = pd.read_excel("data.xlsx")

# Normalisation colonnes (mise en minuscules)
df.columns = [c.lower().strip() for c in df.columns]

# ---------------------------------------------------
# 📌 Sélecteurs utilisateur
# ---------------------------------------------------
st.markdown("<div class='subtitle'>🌍 Choisissez un pays :</div>", unsafe_allow_html=True)
pays = st.selectbox("", sorted(df["pays"].unique()))

# Filtrer catégories disponibles pour ce pays uniquement
categories_dispo = sorted(df[df["pays"] == pays]["categorie"].unique())

st.markdown("<div class='subtitle'>🍀 Choisissez une catégorie d’activité :</div>", unsafe_allow_html=True)
categorie = st.selectbox("", categories_dispo)

# ---------------------------------------------------
# 🔍 Filtrer les lieux
# ---------------------------------------------------
lieux_selectionnes = df[(df["pays"] == pays) & (df["categorie"] == categorie)]

if lieux_selectionnes.empty:
    st.error("❌ Aucun lieu trouvé pour cette combinaison.")
    st.stop()

st.success(f"🔍 {len(lieux_selectionnes)} lieu(x) trouvé(s) ✔️")

# ---------------------------------------------------
# ✨ Fonction IA : création du prompt
# ---------------------------------------------------
def construire_prompt(pays, categorie, lieux):
    texte = ""
    for _, row in lieux.iterrows():
        prix = row.get("prix", "N/A")
        note = row.get("note5", "N/A")
        ideal = row.get("ideal_pour", "N/A")
        url = row.get("url_reservation", "")

        texte += (
            f"- **{row['nom_lieu']}** | ⭐ {note}/5 | Prix : {prix}€ | "
            f"Idéal pour : {ideal} | 🔗 Réservation : {url}\n"
        )

    prompt = f"""
Tu es un expert en création de voyages haut de gamme.

💡 Crée un **séjour parfait de 3 jours** à **{pays}**,
spécialisé dans les activités **{categorie}**.

Voici les lieux à intégrer dans le séjour :

{texte}

Contraintes :
- Décris chaque journée clairement (Jour 1, Jour 2, Jour 3)
- Explique pourquoi ces lieux sont exceptionnels
- Ajoute conseils pratiques et astuces
- Intègre les liens de réservation dans les activités
- Rédaction inspirante, fluide et agréable
"""

    return prompt


# ---------------------------------------------------
# 🚀 Appel à Groq (IA)
# ---------------------------------------------------
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def generer_sejour(prompt):
    try:
        response = client.chat.completions.create(
            model="llama3-8b-instant",   # 🔥 modèle public OK
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1400,
        )
        return response.choices[0].message.content

    except Exception as e:
        return f"❌ Erreur API : {e}"


# ---------------------------------------------------
# 🎉 Bouton de génération
# ---------------------------------------------------
if st.button("✨ Générer mon séjour parfait", use_container_width=True):
    with st.spinner("🧠 L’IA prépare votre séjour, un instant…"):
        prompt = construire_prompt(pays, categorie, lieux_selectionnes)
        resultat = generer_sejour(prompt)

    st.markdown("<div class='result-box'>", unsafe_allow_html=True)
    st.markdown("### 🧳 Votre séjour personnalisé :")
    st.write(resultat)
    st.markdown("</div>", unsafe_allow_html=True)

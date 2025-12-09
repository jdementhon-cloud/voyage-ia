import streamlit as st
import pandas as pd
from groq import Groq

# -----------------------------------
# CONFIG
# -----------------------------------
st.set_page_config(page_title="Générateur de séjour parfait (IA)", layout="wide")
st.title("✨ Générateur de séjour parfait (IA)")

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
note_col_candidates = [c for c in df.columns if "note" in c or "5" in c]
note_col = note_col_candidates[0] if note_col_candidates else None


# -----------------------------------
# UI
# -----------------------------------
pays = st.selectbox("🌍 Choisissez un pays :", sorted(df["pays"].unique()))

categories = sorted(df[df["pays"] == pays]["categorie"].unique())
categorie = st.selectbox("🍀 Choisissez une catégorie d’activité :", categories)

lieux = df[(df["pays"] == pays) & (df["categorie"] == categorie)]

if lieux.empty:
    st.error("Aucun lieu trouvé pour cette combinaison.")
else:
    st.success(f"{len(lieux)} lieu(x) trouvé(s) ✔")


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
Tu es un expert en organisation de voyages et guide touristique professionnel.

Crée un **itinéraire complet et réaliste de 3 jours** à **{pays}**, pour la catégorie d’activité **{categorie}**.

### Voici la liste des lieux à intégrer impérativement dans les propositions :

{texte}

### FORMAT ATTENDU :

- **Jour 1 :** programme détaillé, activités, explications
- **Jour 2 :** programme détaillé
- **Jour 3 :** programme détaillé
- Mentionne clairement **dans quel jour apparaît chaque lieu**
- Chaque jour doit contenir au moins **un des lieux listés**
- Ajoute des conseils pratiques (horaires, transport, durée)
- À la fin, fais un bloc :

### 🔗 Liens de réservation  

Liste tous les liens fournis, en markdown.

Sois concis mais inspirant. Style premium, cohérent, structuré.
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
                {"role": "system", "content": "Tu es un expert en voyages de luxe."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=1600,
        )

        # ⚠️ Correction importante ici (plus de message["content"])
        return completion.choices[0].message.content

    except Exception as e:
        return f"❌ Erreur API : {e}"


# -----------------------------------
# BUTTON
# -----------------------------------
if st.button("✨ Générer mon séjour parfait", type="primary"):

    with st.spinner("🤖 L’IA prépare votre séjour, un instant..."):
        prompt = construire_prompt(pays, categorie, lieux)
        resultat = generer_sejour(prompt)

    st.success("🎉 Séjour généré ! Voici votre proposition :")
    st.markdown(resultat)

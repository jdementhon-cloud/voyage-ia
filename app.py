import streamlit as st
import pandas as pd
from groq import Groq

# -------------------------------------------------------------
# 🎨 CONFIG – Branding ATLAS
# -------------------------------------------------------------
st.set_page_config(page_title="ATLAS – Voyage IA", layout="wide")

# CSS personnalisé
st.markdown("""
    <style>
        body {
            background-color: #F7F7FB;
        }

        .main-title {
            font-size: 64px !important;
            font-weight: 900 !important;
            text-align: center;
            color: #1A237E;
            letter-spacing: 4px;
            margin-top: -30px;
        }

        .subtitle {
            text-align: center;
            margin-top: -20px;
            font-size: 20px;
            color: #424242;
            font-weight: 400;
        }

        .atlas-card {
            background: white;
            padding: 25px;
            border-radius: 14px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.08);
            margin-bottom: 20px;
        }

        .stButton>button {
            background: linear-gradient(90deg, #4C57FF, #6C6CFF);
            color: white;
            border: none;
            padding: 14px 26px;
            font-size: 18px;
            border-radius: 10px;
            font-weight: 600;
            transition: 0.3s;
        }

        .stButton>button:hover {
            background: linear-gradient(90deg, #313BFF, #5A5AFF);
            transform: scale(1.03);
        }

        .result-box {
            background: #EEF1FF;
            padding: 25px;
            border-radius: 12px;
            border-left: 6px solid #4C57FF;
            margin-top: 25px;
            font-size: 18px;
            line-height: 1.6;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='main-title'>ATLAS</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Votre créateur intelligent de séjours parfaits</div>", unsafe_allow_html=True)
st.write("")


# -------------------------------------------------------------
# 📂 LOAD DATA
# -------------------------------------------------------------
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

note_cols = [c for c in df.columns if "note" in c or "5" in c]
note_col = note_cols[0] if note_cols else None


# -------------------------------------------------------------
# 🧭 SELECTION ZONE
# -------------------------------------------------------------
st.markdown("<div class='atlas-card'>", unsafe_allow_html=True)

pays = st.selectbox("🌍 Sélectionnez une destination :", sorted(df["pays"].unique()))

categories = sorted(df[df["pays"] == pays]["categorie"].unique())
categorie = st.selectbox("🎨 Choisissez un type d’expérience :", categories)

lieux = df[(df["pays"] == pays) & (df["categorie"] == categorie)]

if lieux.empty:
    st.error("❌ Aucun lieu trouvé pour cette combinaison.")
else:
    st.success(f"🔎 {len(lieux)} lieu(x) trouvé(s) ✔️")

st.markdown("</div>", unsafe_allow_html=True)


# -------------------------------------------------------------
# 🧠 PROMPT BUILDER
# -------------------------------------------------------------
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
Tu es un expert en organisation de voyages premium.

Crée un **itinéraire réel de 3 jours** à **{pays}**, sur le thème **{categorie}**, avec :

### 🎯 OBJECTIFS
- Une structure claire : Jour 1, Jour 2, Jour 3  
- Chaque jour doit inclure **au moins un des lieux listés**
- Récit élégant, inspirant, fluide et réaliste  
- Conseils pratiques (horaires, durée, déplacement)  
- Mise en contexte culturelle ou sensorielle  
- Lien de réservation intégré dans la partie du lieu  

### 📍 LIEUX À INTÉGRER
{texte}

### 📦 FORMAT FINAL
- Paragraphes immersifs
- Programme précis et optimisé
- Bloc final :  
### 🔗 Liens de réservation
+ liste des liens fournis

Rédige tout en français.
"""

    return prompt


# -------------------------------------------------------------
# 🤖 IA CALL
# -------------------------------------------------------------
def generer_sejour(prompt):
    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])

        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "Tu es un expert en voyages de luxe."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.65,
            max_tokens=1600,
        )

        return completion.choices[0].message.content

    except Exception as e:
        return f"❌ Erreur API : {e}"


# -------------------------------------------------------------
# 🚀 GENERATE BUTTON
# -------------------------------------------------------------
st.markdown("<div class='atlas-card'>", unsafe_allow_html=True)

if st.button("✨ Générer mon séjour parfait", use_container_width=True):
    with st.spinner("🧭 ATLAS construit votre itinéraire..."):
        prompt = construir e_prompt(pays, categorie, lieux)
        resultat = generer_sejour(prompt)

    st.markdown("<div class='result-box'>", unsafe_allow_html=True)
    st.markdown("### 🧳 Votre séjour personnalisé par ATLAS :")
    st.markdown(resultat)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

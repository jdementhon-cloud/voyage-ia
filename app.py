import streamlit as st
import pandas as pd
from groq import Groq

# -------------------------------
# CONFIG GÉNÉRALE
# -------------------------------
st.set_page_config(
    page_title="Générateur de Séjour Parfait",
    layout="wide",
)

# -------------------------------
# CSS – STYLE PREMIUM
# -------------------------------
st.markdown("""
<style>

body {
    background-color: #f7f9fc;
    font-family: "Inter", sans-serif;
}

/* Cartes élégantes */
.card {
    background: white;
    padding: 25px;
    border-radius: 16px;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.06);
    margin-bottom: 20px;
}

/* Bouton premium */
.stButton > button {
    background-color: #6c63ff;
    color: white;
    border-radius: 12px;
    padding: 12px 26px;
    font-size: 18px;
    border: none;
    transition: 0.2s ease-in-out;
}

.stButton > button:hover {
    background-color: #574ff7;
    transform: scale(1.03);
}

/* Bloc résultat IA */
.result-box {
    background: #eef2ff;
    padding: 25px;
    border-radius: 16px;
    border-left: 6px solid #6c63ff;
    margin-top: 18px;
}

.header-title {
    font-size: 38px;
    font-weight: 800;
    text-align: center;
    margin-bottom: 5px;
}

.subheader {
    text-align: center;
    font-size: 18px;
    color: #6366f1;
    margin-bottom: 40px;
}

</style>
""", unsafe_allow_html=True)

# -------------------------------
# HEADER
# -------------------------------
st.markdown("""
<div class='header-title'>✨ Générateur de séjour parfait (IA)</div>
<div class='subheader'>Crée un itinéraire inspirant et personnalisé en quelques secondes</div>
""", unsafe_allow_html=True)

# -------------------------------
# CHARGEMENT DES DONNÉES
# -------------------------------
df = pd.read_excel("data.xlsx")
# Nettoyage simple des noms de colonnes
df.columns = df.columns.str.lower().str.replace(" ", "_")

# --- Détection robuste de la colonne de note (/5) ---
NOTE_COL = None
for candidate in ["note5", "note_5", "note/5"]:
    if candidate in df.columns:
        NOTE_COL = candidate
        break

if NOTE_COL is None:
    st.error("Impossible de trouver la colonne de note (/5) dans votre fichier Excel.")
    st.stop()

# On suppose que ces colonnes existent après ton nettoyage :
# pays, ville, nom_lieu, categorie, pour_qui, latitude, longitude,
# prix, <NOTE_COL>, nombre_davis, ideal_pour, lien_images, url_reservation

# -------------------------------
# FORMULAIRE UTILISATEUR
# -------------------------------
st.markdown("<div class='card'>", unsafe_allow_html=True)

pays = st.selectbox("🌍 Choisissez un pays :", sorted(df["pays"].dropna().unique()))

categories_dispo = df[df["pays"] == pays]["categorie"].dropna().unique()
categorie = st.selectbox("🎨 Choisissez une catégorie d’activité :", sorted(categories_dispo))

st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------
# FILTRAGE LIEUX
# -------------------------------
lieux = df[(df["pays"] == pays) & (df["categorie"] == categorie)]

if lieux.empty:
    st.error("😕 Aucun lieu trouvé pour cette activité.")
else:
    st.success(f"🔎 {len(lieux)} lieu(x) trouvé(s) ✔️")

# -------------------------------
# PROMPT IA
# -------------------------------
def construire_prompt(pays, categorie, lieux):
    texte = ""
    for _, row in lieux.iterrows():
        # Sécurité : certaines colonnes peuvent être nulles
        nom = row.get("nom_lieu", "Lieu")
        prix = row.get("prix", "N.C.")
        note = row.get(NOTE_COL, "N.C.")
        ideal = row.get("ideal_pour", "N.C.")
        url = row.get("url_reservation", "")

        texte += (
            f"- **{nom}**\n"
            f"  • Prix : {prix}€\n"
            f"  • ⭐ Note : {note}/5\n"
            f"  • Idéal pour : {ideal}\n"
            + (f"  • 🔗 Réservation : {url}\n\n" if pd.notna(url) and url != "" else "\n")
        )

    prompt = f"""
Crée un **itinéraire parfait d’une journée** à **{pays}**, autour du thème **{categorie}**.

Voici les lieux disponibles :
{texte}

Délivre :
- Un programme **heure par heure**
- Une mise en scène immersive
- Des conseils pratiques
- Intègre les **liens de réservation** fournis
- Un texte fluide, inspirant, premium, en français.
"""

    return prompt

# -------------------------------
# IA GROQ
# -------------------------------
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def generer_sejour(prompt: str) -> str:
    try:
        response = client.chat.completions.create(
            model="llama3-70b-8k-instant",  # modèle dispo
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1200,
        )
        # ⚠️ CORRECTION ICI : on doit utiliser .content, pas ["content"]
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Erreur API : {e}"

# -------------------------------
# BOUTON GÉNÉRATION
# -------------------------------
st.markdown("<div class='card'>", unsafe_allow_html=True)

if st.button("✨ Générer mon séjour parfait", use_container_width=True):
    if lieux.empty:
        st.error("Aucun lieu disponible pour générer un séjour.")
    else:
        with st.spinner("⏳ L’IA prépare votre séjour sur mesure..."):
            prompt = construire_prompt(pays, categorie, lieux)
            resultat = generer_sejour(prompt)

        st.markdown("<div class='result-box'>", unsafe_allow_html=True)
        st.markdown("### 🧳 Votre séjour personnalisé :")
        st.write(resultat)
        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

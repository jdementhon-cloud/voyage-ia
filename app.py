import streamlit as st
import pandas as pd
from groq import Groq
from fpdf import FPDF
from unidecode import unidecode
import folium
from streamlit.components.v1 import html

# =====================================================
# CONFIG
# =====================================================
st.set_page_config(page_title="ATLAS", layout="wide")

st.markdown("""
<style>
body { background-color: #050816; color: #f5f5f5; }
.atlas-title {
    font-size: 3.2rem;
    font-weight: 900;
    background: linear-gradient(90deg, #facc15, #ec4899, #38bdf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.atlas-sub { color: #cbd5f5; margin-bottom: 1.5rem; }
.card {
    background: #020617;
    padding: 1rem;
    border-radius: 16px;
    border: 1px solid #1e293b;
}
.badge {
    display: inline-block;
    padding: 0.25rem 0.6rem;
    background: rgba(148,163,184,0.2);
    border-radius: 999px;
    font-size: 0.8rem;
    margin-right: 0.3rem;
}
a { color: #38bdf8 !important; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="atlas-title">ATLAS</div>', unsafe_allow_html=True)
st.markdown('<div class="atlas-sub">Itinéraires intelligents & expériences sur-mesure</div>', unsafe_allow_html=True)

# =====================================================
# DATA
# =====================================================
@st.cache_data
def load_data():
    df = pd.read_excel("data.xlsx")
    df.columns = (
        df.columns.str.lower()
        .str.replace(" ", "_")
        .str.replace("/", "_")
        .str.replace("-", "_")
    )
    return df

df = load_data()

note_col = next((c for c in df.columns if "note" in c), None)
image_col = next((c for c in df.columns if "image" in c or "photo" in c), None)

# =====================================================
# SELECTEURS
# =====================================================
pays = st.selectbox("🌍 Pays", sorted(df["pays"].unique()))
categories = sorted(df[df["pays"] == pays]["categorie"].unique())
categorie = st.selectbox("🎯 Catégorie", categories)

lieux = df[(df["pays"] == pays) & (df["categorie"] == categorie)]

if lieux.empty:
    st.error("Aucun lieu trouvé.")
    st.stop()

st.success(f"{len(lieux)} lieu(x) trouvé(s)")

# =====================================================
# CARTE GLOBALE
# =====================================================
st.markdown("## 🗺️ Carte des lieux")

if {"latitude", "longitude"}.issubset(lieux.columns):
    m = folium.Map(
        location=[
            lieux["latitude"].mean(),
            lieux["longitude"].mean()
        ],
        zoom_start=11
    )
    for _, r in lieux.iterrows():
        folium.Marker(
            [r["latitude"], r["longitude"]],
            popup=f"{r['nom_lieu']} – {r['ville']}"
        ).add_to(m)

    html(m._repr_html_(), height=420)
else:
    st.info("Coordonnées GPS manquantes")

# =====================================================
# CARTES LIEUX
# =====================================================
st.markdown("## 📍 Lieux")

cols = st.columns(3)
for i, (_, r) in enumerate(lieux.iterrows()):
    with cols[i % 3]:
        st.markdown('<div class="card">', unsafe_allow_html=True)

        if image_col and pd.notna(r[image_col]):
            st.image(r[image_col], use_column_width=True)

        st.markdown(f"### {r['nom_lieu']}")
        st.caption(r["ville"])

        if note_col:
            st.markdown(f"<span class='badge'>⭐ {r[note_col]}/5</span>", unsafe_allow_html=True)
        if pd.notna(r.get("ideal_pour", None)):
            st.markdown(f"<span class='badge'>🎯 {r['ideal_pour']}</span>", unsafe_allow_html=True)

        if pd.notna(r.get("url_reservation", None)):
            st.markdown(f"[🔗 Réserver]({r['url_reservation']})")

        st.markdown("</div>", unsafe_allow_html=True)

# =====================================================
# PROMPT
# =====================================================
def build_prompt():
    texte = ""
    for _, r in lieux.iterrows():
        texte += f"- {r['nom_lieu']} ({r['ville']})\n"

    return f"""
Tu es un expert voyage.

Crée un itinéraire **sur 3 jours** à **{pays}**, catégorie **{categorie}**.

Lieux disponibles :
{texte}

Contraintes :
- Chaque jour doit inclure au moins un lieu
- Ton fluide, premium
- Conseils pratiques
"""

# =====================================================
# IA
# =====================================================
def generate_itinerary(prompt):
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "Tu es un expert en voyages."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=1600,
        temperature=0.7
    )
    return completion.choices[0].message.content

# =====================================================
# PDF SAFE
# =====================================================
def generate_pdf(text, title):
    pdf = FPDF()
    pdf.set_auto_page_break(True, 15)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, unidecode(title), ln=True)
    pdf.ln(5)

    pdf.set_font("Helvetica", "", 11)
    for line in unidecode(text).split("\n"):
        pdf.multi_cell(0, 6, line)

    return pdf.output(dest="S").encode("latin-1")

# =====================================================
# ACTION
# =====================================================
if st.button("✨ Générer mon séjour"):
    with st.spinner("ATLAS réfléchit…"):
        result = generate_itinerary(build_prompt())
        st.session_state["result"] = result

if "result" in st.session_state:
    st.markdown("## 🧳 Itinéraire")
    st.markdown(st.session_state["result"])

    pdf_bytes = generate_pdf(
        st.session_state["result"],
        f"ATLAS – Séjour {pays}"
    )

    st.download_button(
        "📄 Télécharger le PDF",
        data=pdf_bytes,
        file_name=f"ATLAS_{pays}.pdf",
        mime="application/pdf"
    )

import streamlit as st
import pandas as pd
from groq import Groq
from pathlib import Path

# -------------------------------------------------------------
# CONFIG
# -------------------------------------------------------------
st.set_page_config(
    page_title="ATLAS – Générateur de séjour parfait",
    layout="wide"
)

# -------------------------------------------------------------
# CSS — TEXTE NOIR + SELECTBOX CLAIRES
# -------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800;900&display=swap');

    body, .stApp {
        background-color: #F7EDE2;
        font-family: 'Montserrat', sans-serif;
    }

    /* CONTENEUR */
    .block-container {
        max-width: 1200px;
        padding-top: 2.5rem;
        padding-bottom: 3rem;
    }

    /* TEXTE GLOBAL (hors inputs) */
    h1, h2, h3, h4, h5, h6,
    p {
        color: #000000;
    }

    label {
        color: #000000;
        font-weight: 600;
    }

    /* TITRES */
    .atlas-title {
        font-size: 3.3rem;
        font-weight: 900;
        letter-spacing: -0.03em;
        color: #BF5A4E;
        margin-bottom: 0.2rem;
    }

    .atlas-subtitle {
        font-size: 1.05rem;
        color: #374151;
        margin-bottom: 2rem;
        font-weight: 500;
    }

    /* CARTES */
    .atlas-box,
    .atlas-card {
        background: #ffffff;
        border-radius: 18px

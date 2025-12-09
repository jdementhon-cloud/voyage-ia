def generer_prompt(pays, categorie, lieux):
    texte_lieux = ""
    for _, row in lieux.iterrows():
        texte_lieux += (
            f"- {row['nom_lieu']} | "
            f"Prix : {row['prix']}€ | "
            f"⭐ {row['note5']}/5 | "
            f"Idéal pour : {row['ideal_pour']} | "
            f"Réservation : {row['url_reservation']}\n"
        )

    prompt = f"""
Tu es un expert en voyages.

Crée pour moi un **séjour parfait de 3 jours** à **{pays}**, 
centré sur la catégorie d’activités : **{categorie}**.

Voici la liste des meilleurs lieux à intégrer dans le séjour :

{texte_lieux}

Format attendu :
- 🗓️ Une proposition détaillée jour par jour
- ✨ Pourquoi ces lieux sont exceptionnels
- 💡 Conseils pratiques
- 🔗 Inclure les liens de réservation fournis dans les lieux

Reste concis mais inspirant.
"""
    return prompt

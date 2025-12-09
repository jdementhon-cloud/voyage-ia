def generer_prompt(pays, categorie, lieux):
    description_lieux = "\n".join([
        f"- {row['nom_lieu']} | {row['prix']}€ | Note: {row['note/5']} ⭐ | Idéal pour: {row['idéal_pour']}"
        for _, row in lieux.iterrows()
    ])

    prompt = f"""
Tu es un expert premium en création de voyages sur mesure.

Destination : **{pays}**
Catégorie choisie : **{categorie}**

Voici les activités disponibles :

{description_lieux}

Créer :
1️⃣ Un résumé du séjour  
2️⃣ Un planning parfait sur 2 jours  
3️⃣ Les meilleures suggestions personnalisées  
4️⃣ Les liens directs de réservation  

Réponds uniquement en français.
"""
    return prompt


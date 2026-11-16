"""Génère /llms.txt : un résumé de l'entreprise pour les assistants IA (ChatGPT, Claude, Perplexity…).
Lancer après build_problemes.py : python3 build_llms.py"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_villes, build_problemes

SITE = "https://reseauartisansfrance.com"


def main():
    deps = {}
    for v in build_villes.VILLES:
        deps.setdefault(v["dep"], []).append(v)
    lines = [
        "# Réseau Artisans France",
        "",
        "> Entreprise de plomberie et de chauffage qui intervient en Drôme, en Ardèche et en Isère "
        "(Valence, Romans-sur-Isère, Grenoble, Vienne, Annonay, Tournon-sur-Rhône, Montélimar et leurs environs). "
        "Dépannage 24h/24 et 7j/7 : fuite d'eau, WC et canalisations bouchés, chauffe-eau en panne, chaudière gaz en panne. "
        "Projets : rénovation de salle de bain, remplacement de baignoire par une douche, remplacement de chaudière gaz. "
        "Devis écrit gratuit avant les travaux, paiement après l'intervention, au prix juste.",
        "",
        "- Téléphone : 06 23 83 20 29 (+33 6 23 83 20 29), 24h/24 et 7j/7",
        "- WhatsApp : https://wa.me/33623832029",
        f"- Site : {SITE}/",
        "- Avis clients : 5,0/5 sur Google",
        "- Entreprise immatriculée au RCS (Kbis 105406755)",
        "",
        "## Services",
        "",
    ]
    for p in build_problemes.PROBLEMES:
        lines.append(f"- [{p['nom']}]({SITE}/{p['slug']}/)")
    lines += [f"- [Rénovation de salle de bain]({SITE}/salle-de-bain/)", f"- [Remplacement de chaudière gaz]({SITE}/chaudiere/)", "", "## Conseils", ""]
    import build_conseils
    for a in build_conseils.ARTICLES:
        lines.append(f"- [{a['titre']}]({SITE}/conseils/{a['slug']}/) : {a['desc']}")
    lines += ["", "## Zones d'intervention", ""]
    for dep in ("Drôme", "Ardèche", "Isère"):
        lines.append(f"### {dep}")
        lines.append("")
        for v in deps.get(dep, []):
            lines.append(f"- [Plombier à {v['ville']} ({v['cp']})]({SITE}/{v['slug']}/) : aussi {', '.join(v['voisines'][:5])}")
        lines.append("")
    lines += ["## Bon à savoir", "",
              "- Intervention 24h/24 et 7j/7, y compris le soir, le week-end et les jours fériés ; le tarif est annoncé avant l'intervention.",
              "- L'heure d'arrivée est donnée au téléphone selon la commune et les interventions en cours.",
              "- Rapport d'intervention et facture détaillée fournis pour l'assurance ou le syndic en cas de dégât des eaux.",
              "- L'entreprise ne monte pas de dossiers d'aides de l'État (MaPrimeRénov', CEE).", ""]
    open(os.path.join(HERE, "llms.txt"), "w", encoding="utf-8").write("\n".join(lines))
    print("llms.txt :", len(lines), "lignes")


if __name__ == "__main__":
    main()

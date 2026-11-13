"""Pages « problème » (fuite d'eau, débouchage, chauffe-eau, chaudière), en version zone entière + Valence + Grenoble.
Met aussi à jour : liens de l'accueil, données structurées de l'accueil (toutes les communes), sitemap.xml.
Ordre : python3 build_problemes.py   (relance build_villes.py en premier, puis génère le reste)"""
import json, os, re, subprocess, sys, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
TEL = "+33623832029"
SITE = "https://reseauartisansfrance.com"

# Toutes les communes desservies (déclarées à Google dans les données structurées de l'accueil)
COMMUNES = {
 "Drôme": ["Valence", "Bourg-lès-Valence", "Portes-lès-Valence", "Saint-Marcel-lès-Valence", "Malissard", "Beaumont-lès-Valence",
           "Montélier", "Chabeuil", "Étoile-sur-Rhône", "Beauvallon", "Montéléger", "Alixan", "Châteauneuf-sur-Isère", "Pont-de-l'Isère",
           "Romans-sur-Isère", "Bourg-de-Péage", "Mours-Saint-Eusèbe", "Génissieux", "Peyrins", "Saint-Paul-lès-Romans", "Chatuzange-le-Goubet",
           "Tain-l'Hermitage", "Mercurol-Veaunes", "Chanos-Curson", "Érôme", "Crozes-Hermitage", "Beaumont-Monteux", "Saint-Vallier",
           "Crest", "Aouste-sur-Sye", "Eurre", "Allex", "Grane", "Upie", "Montélimar", "Livron-sur-Drôme", "Loriol-sur-Drôme", "Saint-Rambert-d'Albon", "Montmeyran", "Anneyron"],
 "Ardèche": ["Annonay", "Davézieux", "Boulieu-lès-Annonay", "Roiffieux", "Saint-Marcel-lès-Annonay", "Vernosc-lès-Annonay", "Quintenas",
             "Talencieux", "Saint-Désirat", "Peaugres", "Serrières", "Andance", "Sarras",
             "Guilherand-Granges", "Saint-Péray", "Cornas", "Soyons", "Toulaud", "Châteaubourg", "Alboussière", "Charmes-sur-Rhône",
             "Tournon-sur-Rhône", "Mauves", "Saint-Jean-de-Muzols", "Lemps", "Glun", "Privas", "La Voulte-sur-Rhône", "Le Pouzin", "Le Teil"],
 "Isère": ["Grenoble", "Échirolles", "Saint-Martin-d'Hères", "Fontaine", "Seyssinet-Pariset", "Seyssins", "Sassenage", "Saint-Égrève",
           "Meylan", "La Tronche", "Eybens", "Le Pont-de-Claix", "Gières", "Poisat", "Claix", "Montbonnot-Saint-Martin", "Saint-Ismier",
           "Voiron", "Coublevie", "Moirans", "Saint-Jean-de-Moirans", "Rives", "Voreppe", "Chanas", "Roussillon", "Le Péage-de-Roussillon", "Salaise-sur-Sanne", "Saint-Maurice-l'Exil"],
}

PROBLEMES = [
 dict(slug="fuite-d-eau", nom="Fuite d'eau", h1="Fuite d'eau ?", short="fuite d'eau",
      title="Fuite d'eau : plombier en urgence 24h/24", lead="Fuite sous l'évier, tuyau percé, dégât des eaux, compteur qui tourne : <b>un plombier vient couper, trouver l'origine et réparer</b>, au prix juste.",
      symptomes=["De l'eau qui coule sous l'évier, le lavabo ou le WC", "Une tache d'humidité au plafond ou sur un mur", "Le compteur d'eau qui tourne alors que tout est fermé", "Une facture d'eau qui grimpe sans raison", "Un dégât des eaux chez vous ou chez le voisin du dessous"],
      etapes=["On vous aide au téléphone à couper l'eau pour limiter les dégâts", "Sur place, on localise l'origine de la fuite, sans tout casser quand c'est possible", "On répare : raccord, joint, tuyau, robinetterie", "On vous remet une facture détaillée et un rapport pour votre assurance"],
      faq=[("Ma recherche de fuite est-elle prise en charge par l'assurance ?", "En cas de dégât des eaux, la recherche de fuite est souvent couverte par l'assurance habitation. Nous vous remettons le rapport et la facture. Vérifiez auprès de votre assureur."),
           ("Que faire tout de suite en cas de fuite ?", "Coupez l'arrivée d'eau générale (souvent près du compteur), coupez l'électricité si l'eau approche des prises, et prenez des photos pour l'assurance."),
           ("Pouvez-vous trouver une fuite invisible ?", "Oui : quand le compteur tourne sans raison ou qu'une tache apparaît, on cherche l'origine de la fuite avant de réparer.")]),
 dict(slug="debouchage", nom="WC et canalisations bouchés", h1="WC ou canalisation bouché ?", short="débouchage",
      title="Débouchage WC, évier, canalisation : plombier en urgence", lead="WC bouché, évier qui ne s'écoule plus, douche qui déborde, mauvaises odeurs : <b>un plombier débouche avec du matériel professionnel</b>, au prix juste.",
      symptomes=["Le WC qui déborde ou se vide très lentement", "L'évier, le lavabo ou la douche qui ne s'écoule plus", "Des gargouillis et des remontées d'odeurs", "Plusieurs appareils bouchés en même temps (canalisation principale)", "Un regard extérieur qui déborde"],
      etapes=["Au téléphone, on vous dit quoi ne pas faire (pas de produit chimique, pas de chasse d'eau en boucle)", "Sur place, débouchage manuel ou au furet selon le cas", "Pour les canalisations très encrassées : curage ou hydrocurage", "Si le bouchon revient, inspection par caméra pour trouver la cause"],
      faq=[("Faut-il verser un déboucheur chimique en attendant ?", "Évitez : ces produits abîment les canalisations et peuvent brûler en cas de projection. Ne tirez pas la chasse en boucle si le WC déborde."),
           ("Le débouchage est-il à la charge du propriétaire ou du locataire ?", "En général, le débouchage courant est à la charge du locataire, sauf si la cause vient d'un défaut de l'installation. On vous remet une facture détaillée."),
           ("Pourquoi mon WC se bouche-t-il souvent ?", "Lingettes, pente insuffisante, canalisation entartrée ou abîmée : une inspection par caméra permet de trouver la vraie cause.")]),
 dict(slug="chauffe-eau-en-panne", nom="Chauffe-eau en panne", h1="Chauffe-eau en panne ?", short="chauffe-eau",
      title="Chauffe-eau en panne : dépannage et remplacement rapide", lead="Plus d'eau chaude, ballon qui fuit, disjoncteur qui saute : <b>un plombier diagnostique, répare ou remplace votre chauffe-eau</b>, au prix juste.",
      symptomes=["Plus d'eau chaude du tout, ou eau tiède", "De l'eau qui coule sous le ballon ou par le groupe de sécurité", "Le disjoncteur du chauffe-eau qui saute", "Un ballon qui fait du bruit ou une eau couleur rouille", "Un chauffe-eau de plus de 10 ans qui chauffe mal"],
      etapes=["Au téléphone : on vous fait vérifier le disjoncteur et on vous dit si on peut venir et quand", "Sur place : diagnostic (résistance, thermostat, groupe de sécurité, anode)", "On vous dit franchement s'il vaut mieux réparer ou remplacer", "En cas de remplacement : devis clair, dépose de l'ancien ballon et pose du nouveau"],
      faq=[("Faut-il réparer ou remplacer mon chauffe-eau ?", "Ça dépend de son âge et de la panne : une résistance ou un thermostat se remplacent ; une cuve qui fuit impose le remplacement. On vous le dit franchement après diagnostic."),
           ("Mon chauffe-eau fuit, que faire ?", "Coupez l'alimentation électrique du ballon au tableau, fermez l'arrivée d'eau froide du chauffe-eau, et appelez-nous."),
           ("Remplacez-vous le chauffe-eau dans la journée ?", "Quand le modèle est disponible, oui c'est souvent possible. On vous le confirme au téléphone.")]),
 dict(slug="depannage-chaudiere", nom="Chaudière en panne", h1="Chaudière en panne ?", short="chaudière",
      title="Dépannage chaudière gaz : plus de chauffage ni d'eau chaude", lead="Chaudière gaz en panne, code erreur, plus de chauffage ou d'eau chaude : <b>un chauffagiste diagnostique et répare</b>, ou vous propose un remplacement avec un devis clair.",
      symptomes=["Plus de chauffage et/ou plus d'eau chaude", "Un code erreur affiché sur la chaudière", "La chaudière qui se met en sécurité ou s'éteint", "Une pression qui baisse sans arrêt", "Des bruits anormaux ou une chaudière très ancienne"],
      etapes=["Au téléphone : on vous fait vérifier la pression et le code erreur", "Sur place : diagnostic et réparation quand c'est possible", "Si la chaudière est trop ancienne : devis de remplacement clair, sans engagement", "Remplacement : dépose de l'ancienne, pose et mise en service comprises"],
      faq=[("Quelles chaudières dépannez-vous ?", "Les chaudières gaz murales et au sol des grandes marques. Appelez-nous avec la marque et le code erreur."),
           ("Ma chaudière perd sa pression, que faire ?", "Notez la pression affichée et le code erreur, puis appelez-nous : une pression qui baisse sans arrêt signale souvent une fuite ou un vase d'expansion à vérifier."),
           ("Faut-il remplacer une vieille chaudière ?", "Pas forcément. On répare quand ça vaut le coup, et on vous dit franchement quand le remplacement est plus raisonnable.")]),

 dict(slug="chauffage-chaudiere-gaz", nom="Chauffage et chaudière gaz", h1="Chauffage, chaudière gaz ?", short="chauffage", projet=True, devis="../chaudiere/",
      title="Chauffagiste : remplacement et entretien de chaudière gaz, radiateurs", lead="Chaudière gaz trop ancienne, radiateurs qui chauffent mal, entretien annuel : <b>un chauffagiste local vient voir, vous explique et vous fait un devis clair</b>, au prix juste.",
      symptomes=["Une chaudière gaz de plus de 15 ans qui tombe souvent en panne", "Des radiateurs froids en haut ou qui chauffent mal", "L'entretien annuel obligatoire de la chaudière à faire", "Des radiateurs ou robinets thermostatiques à remplacer", "Une fuite sur le circuit de chauffage"],
      etapes=["Visite gratuite : on regarde l'installation et vos besoins", "Devis écrit et détaillé, sans engagement", "Dépose de l'ancienne chaudière, pose de la nouvelle et mise en service", "Conseils d'utilisation et entretien annuel si vous le souhaitez"],
      faq=[("Faut-il remplacer ma vieille chaudière ?", "Pas forcément : si elle est réparable à un coût raisonnable, on vous le dit. On vous conseille le remplacement seulement quand il est plus raisonnable."),
           ("L'entretien de la chaudière gaz est-il obligatoire ?", "Oui, l'entretien annuel d'une chaudière gaz est obligatoire. Nous pouvons le réaliser et vous remettre l'attestation."),
           ("Mes radiateurs chauffent mal, que faire ?", "Souvent, une purge suffit. Si le problème persiste, on vérifie le circuit, la pression et les robinets.")]),
 dict(slug="renovation-salle-de-bain", nom="Rénovation de salle de bain", h1="Refaire votre salle de bain ?", short="salle de bain", projet=True, devis="../salle-de-bain/",
      title="Rénovation de salle de bain : douche à l'italienne, remplacement de baignoire", lead="Baignoire à remplacer par une douche, salle de bain vieillissante, douche à l'italienne : <b>un seul artisan local s'occupe de tout, de A à Z</b>, au prix juste.",
      symptomes=["Une baignoire difficile à enjamber, à remplacer par une douche", "Une salle de bain vieillissante : carrelage, meuble, robinetterie", "Une envie de douche à l'italienne", "Des joints noircis, une humidité qui revient", "Un lavabo ou un meuble vasque à changer"],
      etapes=["Visite gratuite à domicile pour voir la pièce et vos envies", "Devis écrit et détaillé, avec les délais", "Dépose, plomberie, carrelage, pose des équipements et finitions", "Chantier propre, délais respectés, un seul interlocuteur"],
      faq=[("Combien de temps durent les travaux ?", "Ça dépend du projet : un remplacement de baignoire par une douche est rapide, une rénovation complète prend plus de temps. Le délai est indiqué sur le devis."),
           ("Faut-il plusieurs artisans ?", "Non : on s'occupe de tout, de la dépose aux finitions, avec un seul interlocuteur."),
           ("La visite est-elle payante ?", "Non, la visite et le devis sont gratuits et sans engagement.")]),
 dict(slug="travaux-plomberie", nom="Travaux de plomberie", h1="Des travaux de plomberie ?", short="travaux", projet=True, devis="",
      title="Travaux de plomberie : installation, remplacement de tuyauterie, sanitaires", lead="Remplacer une tuyauterie, installer un WC, un évier, un lave-linge, déplacer une arrivée d'eau : <b>un plombier expérimenté réalise vos travaux</b>, au prix juste.",
      symptomes=["Une tuyauterie ancienne à remplacer (plomb, acier, fuites à répétition)", "Un WC, un lavabo ou un évier à installer ou à changer", "Un raccordement de lave-linge ou de lave-vaisselle", "Une arrivée d'eau ou une évacuation à déplacer", "Une robinetterie ou un mitigeur à remplacer"],
      etapes=["Vous nous décrivez le projet au téléphone, avec photos si possible", "Visite et devis gratuits si nécessaire", "Travaux réalisés proprement, dans les délais annoncés", "Facture détaillée et conseils d'entretien"],
      faq=[("Faites-vous les petits travaux ?", "Oui : remplacement de mitigeur, de WC, raccordement d'électroménager… aucun chantier n'est trop petit."),
           ("Faut-il changer une tuyauterie en plomb ?", "Oui, c'est recommandé pour la qualité de l'eau. On vous fait un devis pour la remplacer."),
           ("Intervenez-vous pour les propriétaires bailleurs ?", "Oui, pour les particuliers, les bailleurs et les professionnels, avec facture détaillée.")]),
]

LIEUX = [None,
         dict(ville="Valence", cp="26000", slug="valence", page="plombier-valence"),
         dict(ville="Grenoble", cp="38000", slug="grenoble", page="plombier-grenoble")]


def base():
    s = open(os.path.join(HERE, "index.html"), encoding="utf-8").read()
    s = re.sub(r'<script type="application/ld\+json">.*?</script>\n', "", s, flags=re.S)
    s = s.replace('<meta name="facebook-domain-verification" content="zgn82bjjiiikyrotvltoshbax3lbhl" />\n', "")
    s = re.sub(r'(href|src)="assets/', r'\1="../assets/', s)
    s = s.replace('href="mentions-legales.html"', 'href="../mentions-legales.html"').replace('href="confidentialite.html"', 'href="../confidentialite.html"')
    return s


def page(p, lieu):
    s = base()
    V = lieu["ville"] if lieu else None
    slug = p["slug"] + (f"-{lieu['slug']}" if lieu else "")
    url = f"{SITE}/{slug}/"
    where = f" à {V}" if V else " en Drôme, Ardèche et Isère"
    title = f"{p['title']}{(' à ' + V) if V else ''} | Réseau Artisans France"
    desc = f"{p['nom']}{where} ? Plombier disponible 24h/24 et 7j/7, au prix juste. Entreprise locale basée à Annonay."
    s = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", s, count=1, flags=re.S)
    s = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{desc}">', s, count=1)
    s = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{url}">', s, count=1)
    if p.get("projet"):
        s = re.sub(r'<!-- EN ATTENDANT -->\s*<section id="reflexes">.*?</section>', '', s, count=1, flags=re.S)
    s = s.replace("Urgence plomberie · Drôme-Ardèche", f"{p['nom']} · {V + ' ' + lieu['cp'] if V else 'Drôme · Ardèche · Isère'}", 1)
    s = re.sub(r'<h1 class="h1-near">.*?</h1>', f'<h1 class="h1-near"><span>{p["h1"]}</span><span class="near">{("Visite et devis gratuits" + (" à&nbsp;" + V if V else "")) if p.get("projet") else ("Un plombier" + (" à&nbsp;" + V if V else "") + " vient chez&nbsp;vous")}</span></h1>', s, count=1, flags=re.S)
    s = re.sub(r'<p class="lead">.*?</p>', f'<p class="lead">{p["lead"]}</p>', s, count=1, flags=re.S)
    if V:
        s = s.replace("<span data-ville>Valence</span>", f"<span data-ville>{V}</span>")
    # Bloc problème avant les urgences
    others = " · ".join(f'<a href="../{q["slug"]}{("-" + lieu["slug"]) if lieu else ""}/">{q["nom"]}</a>' for q in PROBLEMES if q is not p)
    villes = (f'<a href="../{lieu["page"]}/">Plombier à {V}</a>' if lieu else
              " · ".join(f'<a href="../{p["slug"]}-{l["slug"]}/">{p["nom"]} à {l["ville"]}</a>' for l in LIEUX if l))
    bloc = f'''<section id="probleme">
    <div class="wrap">
      <h2>{p["nom"]}{where} : on s'en occupe</h2>
      <div class="grid g2">
        <div class="card"><h3>Vous reconnaissez ces signes ?</h3><ul>{"".join(f"<li>{x}</li>" for x in p["symptomes"])}</ul></div>
        <div class="card"><h3>Comment on intervient</h3><ol>{"".join(f"<li>{x}</li>" for x in p["etapes"])}</ol></div>
      </div>
      <p class="sub">On travaille au prix juste : devis écrit avant les travaux, paiement après intervention.</p>
      {('<p><a class="btn btn-call" href="' + p["devis"] + '">Demander mon devis gratuit</a></p>') if p.get("devis") else ""}
      <p>Voir aussi : {others}. {villes}.</p>
    </div>
  </section>
  '''
    s = s.replace('<section class="alt" id="urgences">', bloc + '<section class="alt" id="urgences">', 1)
    extra = "".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in p["faq"])
    s = re.sub(r'(<section id="faq">.*?<h2>Questions fréquentes</h2>)', lambda m: m.group(1) + "\n      " + extra, s, count=1, flags=re.S)
    area = [V] if V else [c for l in COMMUNES.values() for c in l]
    ld = {"@context": "https://schema.org", "@type": "Service", "serviceType": p["nom"], "name": f"{p['nom']}{where}", "url": url,
          "provider": {"@type": "Plumber", "name": "Réseau Artisans France", "telephone": TEL, "url": SITE + "/",
                       "address": {"@type": "PostalAddress", "streetAddress": "60 rue des Bouvreuils", "postalCode": "07100", "addressLocality": "Annonay", "addressCountry": "FR"}},
          "areaServed": [{"@type": "City", "name": c} for c in dict.fromkeys(area)]}
    s = s.replace("</head>", f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>\n</head>', 1)
    return slug, s


def update_home(villes):
    p = os.path.join(HERE, "index.html")
    s = open(p, encoding="utf-8").read()
    links_v = " · ".join(f'<a href="/{v["slug"]}/">{v["ville"]}</a>' for v in villes)
    links_p = " · ".join(f'<a href="/{q["slug"]}/">{q["nom"]}</a>' for q in PROBLEMES if not q.get("projet"))
    links_j = " · ".join(f'<a href="/{q["slug"]}/">{q["nom"]}</a>' for q in PROBLEMES if q.get("projet"))
    s = re.sub(r'<p class="legal">Nos pages par ville :.*?</p>(\n\s*<p class="legal">Urgences :.*?</p>)?(\n\s*<p class="legal">Projets :.*?</p>)?',
               f'<p class="legal">Nos pages par ville : {links_v}</p>\n      <p class="legal">Urgences : {links_p}</p>\n      <p class="legal">Projets : {links_j}</p>', s, count=1, flags=re.S)
    ld = {"@context": "https://schema.org", "@type": "Plumber", "name": "Réseau Artisans France", "url": SITE + "/", "telephone": TEL,
          "image": SITE + "/assets/raf-logo.png",
          "address": {"@type": "PostalAddress", "streetAddress": "60 rue des Bouvreuils", "postalCode": "07100", "addressLocality": "Annonay", "addressCountry": "FR"},
          "areaServed": [{"@type": "City", "name": c} for c in dict.fromkeys(c for l in COMMUNES.values() for c in l)],
          "openingHoursSpecification": {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], "opens": "00:00", "closes": "23:59"}}
    s = re.sub(r'<script type="application/ld\+json">.*?</script>\n', "", s, flags=re.S)
    s = s.replace("</head>", f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>\n</head>', 1)
    open(p, "w", encoding="utf-8").write(s)


def sitemap(slugs):
    d = datetime.date.today().isoformat()
    urls = ["", "salle-de-bain/", "chaudiere/"] + [x + "/" for x in slugs]
    body = "\n".join(f"  <url><loc>{SITE}/{u}</loc><lastmod>{d}</lastmod></url>" for u in urls)
    open(os.path.join(HERE, "sitemap.xml"), "w", encoding="utf-8").write(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{body}\n</urlset>\n')


if __name__ == "__main__":
    sys.path.insert(0, HERE)
    import build_villes
    update_home(build_villes.VILLES)           # 1. accueil (liens + communes)
    build_villes.BASE = open(os.path.join(HERE, "index.html"), encoding="utf-8").read()
    for v in build_villes.VILLES:              # 2. pages ville (à partir de l'accueil à jour)
        d = os.path.join(HERE, v["slug"]); os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(build_villes.page(v))
    slugs = [v["slug"] for v in build_villes.VILLES]
    for p in PROBLEMES:                        # 3. pages problème
        for lieu in LIEUX:
            slug, html = page(p, lieu)
            d = os.path.join(HERE, slug); os.makedirs(d, exist_ok=True)
            open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(html)
            slugs.append(slug)
    sitemap(slugs)                             # 4. sitemap
    print(len(slugs), "pages :", ", ".join(slugs))

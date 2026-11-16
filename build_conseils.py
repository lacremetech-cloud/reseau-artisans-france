"""Partie « Conseils » : une page d'accueil /conseils/ et des articles pratiques.
Chaque article répond à une vraie question de client, avec un résumé à citer, une FAQ balisée
et des liens vers les pages de service. Construit à partir de index.html (même en-tête, même style).
Appelé par build_problemes.py (qui gère aussi le sitemap) ; lancement seul : python3 build_conseils.py"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import seo

SITE = "https://reseauartisansfrance.com"
TEL = "+33623832029"
DATE = "2026-11-16"
# Image de tête par article : (fichier dans assets/, texte alternatif, légende, largeur, hauteur)
# « vraie » = photo d'une intervention de l'équipe ; sinon « Photo d'illustration ».
IMAGES = {
 "fuite-d-eau-que-faire": ("intervention-raccord.jpg", "Remplacement d'un raccord de plomberie qui fuyait", "Intervention de l'équipe Réseau Artisans France : remplacement d'un raccord.", 800, 1000),
 "wc-bouche-que-faire": ("conseils/canalisation-exterieure.jpg", "Tranchée le long d'une maison pour accéder à une canalisation d'évacuation", "Intervention de l'équipe Réseau Artisans France sur une canalisation extérieure.", 562, 1000),
 "chauffe-eau-ne-chauffe-plus": ("intervention-tuyauterie.jpg", "Réparation de tuyauterie par un plombier", "Intervention de l'équipe Réseau Artisans France sur une tuyauterie.", 800, 1000),
 "chaudiere-gaz-en-panne": ("ch-tech.jpg", "Chauffagiste contrôlant une chaudière gaz murale", "Photo d'illustration.", 1000, 1241),
 "canalisations-gel-hiver": ("intervention-regard-compteur.jpg", "Regard de compteur d'eau ouvert pendant une intervention", "Intervention de l'équipe Réseau Artisans France sur un regard de compteur d'eau.", 800, 1000),
 "remplacer-baignoire-par-douche": ("ba1-apres.jpg", "Douche à l'italienne avec paroi vitrée et meuble en chêne", "Image d'illustration : exemple de douche après remplacement d'une baignoire.", 900, 1116),
}
# Vrais avis Google (texte exact, prénom + initiale). Un par article ; ce n'est pas forcément un avis sur ce sujet précis.
AVIS_URL = "https://share.google/ummoZs7w7M8uVlmeo"
AVIS = {
 "fuite-d-eau-que-faire": ("Intervention rapide pour un problème de fuite d’eau. Travail propre et efficace, avec de bons conseils. Entreprise sérieuse et ponctuelle. Je recommande sans hésiter !", "Zoulihka R."),
 "wc-bouche-que-faire": ("Très bonne expérience ! J’avais une urgence en plomberie et l’entreprise a été très réactive. Le plombier était ponctuel, professionnel et efficace. Le problème a été résolu rapidement et le travail est propre.", "Khadija B."),
 "chauffe-eau-ne-chauffe-plus": ("Un binôme au top, rapide, efficace et pleins de bon conseils ! Encore merci !", "Kylian P."),
 "chaudiere-gaz-en-panne": ("Techniciens compétents et sympathiques", "Patricia B."),
 "canalisations-gel-hiver": ("Hyper réactifs et professionnels! Au top, rien à dire c'est parfait !", "Audrey B."),
 "remplacer-baignoire-par-douche": ("Technicien excellent irréprochable très agréable souriant je vous recommande fortement l'entreprise RÉSEAU ARTISANS FRANCE entreprise très sérieuse 👍👍👍", "Anthony M."),
}
ADDR = {"@type": "PostalAddress", "streetAddress": "60 rue des Bouvreuils", "postalCode": "07100", "addressLocality": "Annonay", "addressCountry": "FR"}

ARTICLES = [
 dict(slug="fuite-d-eau-que-faire",
      titre="Fuite d'eau : que faire en attendant le plombier ?",
      court="Fuite d'eau : les bons réflexes",
      desc="Fuite sous l'évier, tuyau percé, dégât des eaux : les gestes à faire tout de suite, comment trouver l'origine et quand appeler un plombier.",
      bref="En cas de fuite d'eau, coupez d'abord l'arrivée d'eau générale (près du compteur ou sous l'évier), coupez l'électricité si l'eau approche des prises, épongez et prenez des photos pour l'assurance. Un plombier localise ensuite l'origine de la fuite et répare. Réseau Artisans France intervient 24h/24 en Drôme, Ardèche et Isère.",
      service=("fuite-d-eau", "Fuite d'eau : intervention 24h/24"),
      sections=[
       ("1. Coupez l'eau tout de suite", ["Le robinet d'arrivée générale se trouve le plus souvent près du compteur d'eau : dans la cuisine, la salle de bain, un placard technique, le garage ou la cave. En appartement, il peut aussi être sur le palier.",
         "Si la fuite vient d'un seul appareil (WC, lavabo, machine à laver), un petit robinet d'arrêt juste avant l'appareil suffit souvent."]),
       ("2. Mettez-vous en sécurité", ["Si l'eau coule près des prises, d'un tableau électrique ou d'un plafonnier, coupez l'électricité au disjoncteur, au moins sur la zone concernée. Ne touchez pas un appareil électrique les pieds dans l'eau."]),
       ("3. Limitez les dégâts", ["Épongez, placez une bassine sous la fuite, déplacez les meubles et les objets de valeur. En immeuble, prévenez le voisin du dessous et le syndic : une fuite peut traverser le plancher."]),
       ("4. Prenez des photos", ["Photographiez la fuite, les traces d'eau et les dégâts. Elles servent pour votre assurance habitation, et vous pouvez les envoyer au plombier par WhatsApp pour qu'il prépare le bon matériel."]),
       ("Fuite invisible : comment la repérer ?", ["Fermez tous les robinets et regardez le compteur : s'il continue de tourner, il y a une fuite quelque part. Autres signes : une tache au plafond ou sur un mur, une odeur d'humidité, une facture d'eau qui grimpe sans raison.",
         "Dans ce cas, un plombier fait une recherche de fuite pour trouver l'origine sans tout casser. Un rapport vous est remis pour l'assurance."]),
      ],
      faq=[("Mon assurance prend-elle en charge la fuite ?", "En cas de dégât des eaux, la recherche de fuite est souvent couverte par l'assurance habitation. Déclarez le sinistre rapidement et gardez la facture et le rapport du plombier. Les conditions dépendent de votre contrat."),
           ("Puis-je réparer une fuite moi-même ?", "Un joint de robinet ou un flexible desserré, parfois oui. Pour une fuite sur une canalisation, encastrée ou invisible, mieux vaut un plombier : une réparation mal faite peut provoquer un dégât des eaux plus important."),
           ("Que faire si la fuite vient du voisin du dessus ?", "Coupez votre électricité si l'eau approche des prises, prévenez le voisin et le syndic, et faites un constat amiable de dégât des eaux. Prenez des photos.")]),
 dict(slug="wc-bouche-que-faire",
      titre="WC bouché : que faire avant d'appeler un plombier ?",
      court="WC bouché : les solutions",
      desc="WC bouché ou qui se vide mal : les gestes simples à essayer, ce qu'il ne faut jamais faire, et quand appeler un plombier pour un débouchage.",
      bref="Pour un WC bouché, arrêtez de tirer la chasse, essayez une ventouse ou de l'eau chaude (pas bouillante) avec du liquide vaisselle. N'utilisez pas de produit chimique agressif. Si le WC reste bouché ou si plusieurs évacuations refoulent, un plombier débouche avec un furet ou par hydrocurage.",
      service=("debouchage", "Débouchage WC et canalisations"),
      sections=[
       ("1. Arrêtez de tirer la chasse", ["Chaque chasse d'eau ajoute de l'eau dans une cuvette qui ne se vide plus : c'est le meilleur moyen de la faire déborder. Si besoin, fermez le petit robinet d'arrivée d'eau du réservoir."]),
       ("2. Essayez la ventouse", ["Une ventouse à WC (forme en cloche) bien plaquée au fond de la cuvette, avec des mouvements de va-et-vient, suffit souvent pour un bouchon de papier."]),
       ("3. Eau chaude et liquide vaisselle", ["Versez un bon trait de liquide vaisselle, puis un seau d'eau chaude, pas bouillante (l'eau bouillante peut fêler la céramique). Laissez agir une vingtaine de minutes."]),
       ("Ce qu'il ne faut pas faire", ["Évitez les déboucheurs chimiques très agressifs : ils abîment les canalisations et sont dangereux si un plombier doit intervenir ensuite. Ne forcez pas avec un objet rigide qui pourrait rayer ou fissurer la cuvette."]),
       ("Quand appeler un plombier ?", ["Si le WC reste bouché après ces essais, si l'eau remonte dans la douche ou l'évier quand vous tirez la chasse, ou si le problème revient souvent : le bouchon est plus loin dans la canalisation. Le plombier utilise un furet, un curage, voire une inspection par caméra pour trouver la cause."]),
      ],
      faq=[("Pourquoi mon WC se bouche-t-il souvent ?", "Trop de papier, des lingettes (même dites « biodégradables »), du tartre ou une canalisation mal inclinée. Une inspection caméra permet de trouver la vraie cause."),
           ("Les lingettes peuvent-elles aller dans les WC ?", "Non. Elles ne se désagrègent pas comme le papier toilette et sont l'une des premières causes de bouchons."),
           ("Un plombier peut-il venir le soir ou le week-end ?", "Oui, Réseau Artisans France intervient 24h/24 et 7j/7. Le tarif du soir et du week-end vous est indiqué avant l'intervention.")]),
 dict(slug="chauffe-eau-ne-chauffe-plus",
      titre="Chauffe-eau qui ne chauffe plus : les causes et que faire",
      court="Chauffe-eau en panne : les causes",
      desc="Plus d'eau chaude ? Les vérifications simples à faire sur un chauffe-eau électrique, les pannes courantes et quand réparer ou remplacer.",
      bref="Si votre chauffe-eau électrique ne chauffe plus, vérifiez d'abord le disjoncteur et le contacteur jour/nuit au tableau électrique. Si tout est en ordre, la panne vient souvent du thermostat ou de la résistance, que l'on remplace. Un chauffe-eau qui fuit par la cuve doit en général être remplacé.",
      service=("chauffe-eau-en-panne", "Chauffe-eau en panne : dépannage"),
      sections=[
       ("1. Vérifiez le tableau électrique", ["Le disjoncteur du chauffe-eau a peut-être sauté. Vérifiez aussi le contacteur jour/nuit : s'il est sur « arrêt » ou en mode heures creuses alors que vous n'en avez pas, le ballon ne chauffe pas."]),
       ("2. Laissez-lui le temps", ["Après une coupure ou un gros puisage d'eau chaude, un ballon peut mettre plusieurs heures à remonter en température, surtout s'il ne chauffe qu'en heures creuses."]),
       ("Les pannes les plus courantes", ["Thermostat défaillant, résistance hors service (souvent entartrée), sécurité qui s'est déclenchée : ces pièces se remplacent. Dans les zones où l'eau est calcaire, le tartre use plus vite la résistance."]),
       ("Le chauffe-eau fuit", ["Une fuite au groupe de sécurité (le robinet sous le ballon) est normale goutte à goutte pendant la chauffe, mais pas en continu. Une fuite par la cuve elle-même signifie en général que le ballon est percé : il faut le remplacer. Coupez l'électricité et l'arrivée d'eau froide du ballon."]),
       ("Réparer ou remplacer ?", ["Tout dépend de l'âge du chauffe-eau, de la panne et du prix des pièces. Après diagnostic, un plombier vous dit franchement ce qui est le plus raisonnable, avec un devis écrit."]),
      ],
      faq=[("Combien de temps dure un chauffe-eau électrique ?", "Souvent entre 10 et 15 ans, selon la qualité de l'eau et l'entretien. Au-delà, une panne importante pousse plutôt au remplacement."),
           ("Faut-il détartrer un chauffe-eau ?", "Dans les régions où l'eau est calcaire, un entretien régulier prolonge la durée de vie de la résistance et du ballon."),
           ("Le remplacement se fait-il dans la journée ?", "Souvent oui, pour un remplacement à l'identique, selon la disponibilité du modèle. Le délai vous est annoncé au téléphone.")]),
 dict(slug="chaudiere-gaz-en-panne",
      titre="Chaudière gaz en panne : les vérifications avant d'appeler",
      court="Chaudière gaz en panne",
      desc="Plus de chauffage ou d'eau chaude avec une chaudière gaz : les vérifications simples, les bons réflexes de sécurité et quand appeler un chauffagiste.",
      bref="Si votre chaudière gaz s'arrête, vérifiez la pression d'eau sur le manomètre, l'alimentation électrique, l'arrivée de gaz et le thermostat d'ambiance, puis notez le code erreur affiché. En cas d'odeur de gaz, n'actionnez aucun interrupteur, aérez, sortez et appelez Urgence Sécurité Gaz au 0 800 47 33 33.",
      service=("depannage-chaudiere", "Dépannage de chaudière gaz"),
      sections=[
       ("Odeur de gaz : la sécurité d'abord", ["N'allumez et n'éteignez aucun appareil électrique, ne faites pas de flamme, ouvrez les fenêtres, fermez le robinet de gaz si vous le pouvez, sortez du logement et appelez Urgence Sécurité Gaz (GRDF) au 0 800 47 33 33, joignable 24h/24."]),
       ("1. Regardez la pression", ["Le manomètre de la chaudière indique la pression d'eau du circuit de chauffage. Si elle est trop basse, la chaudière se met en sécurité. La notice de votre chaudière indique la plage normale et comment la remettre à niveau."]),
       ("2. Électricité, gaz et thermostat", ["Vérifiez que la chaudière est bien alimentée (voyants allumés, disjoncteur), que le robinet de gaz est ouvert et que le thermostat d'ambiance demande bien du chauffage (piles, programmation)."]),
       ("3. Notez le code erreur", ["La plupart des chaudières affichent un code en cas de panne. Notez-le avec la marque et le modèle de la chaudière : le chauffagiste saura mieux quoi apporter. Un seul redémarrage selon la notice est possible ; si la panne revient, n'insistez pas."]),
       ("Entretien annuel", ["L'entretien d'une chaudière gaz est obligatoire chaque année. Il limite les pannes, maintient le bon rendement et contrôle la sécurité de l'appareil."]),
      ],
      faq=[("Ma chaudière s'allume puis s'arrête, pourquoi ?", "Pression trop basse, problème d'allumage ou d'évacuation des fumées : seul un diagnostic sur place permet de trouver la cause. Notez le code erreur avant d'appeler."),
           ("Faut-il réparer ou remplacer une vieille chaudière ?", "Ça dépend de son âge, de la panne et du prix des pièces. Le chauffagiste vous donne un avis honnête après le diagnostic, avec un devis écrit."),
           ("Intervenez-vous l'hiver le soir et le week-end ?", "Oui, 24h/24 et 7j/7. Le tarif est annoncé avant l'intervention.")]),
 dict(slug="canalisations-gel-hiver",
      titre="Canalisations et gel : comment protéger vos tuyaux en hiver",
      court="Protéger ses canalisations du gel",
      desc="Éviter que les tuyaux gèlent ou éclatent en hiver : isolation, robinets extérieurs, maison inoccupée, et que faire si une canalisation a gelé.",
      bref="Pour protéger vos canalisations du gel, isolez les tuyaux et le compteur exposés au froid, coupez et videz les robinets extérieurs, et gardez un chauffage minimum dans un logement inoccupé. Si un tuyau a gelé ou éclaté, coupez l'eau et ne le chauffez jamais à la flamme.",
      service=("fuite-d-eau", "Canalisation éclatée : intervention 24h/24"),
      sections=[
       ("Où le gel frappe-t-il ?", ["Les tuyaux qui passent dans un garage, une cave, un vide sanitaire, des combles non isolés ou le long d'un mur extérieur, le compteur d'eau dans un regard extérieur, et les robinets de jardin."]),
       ("Avant l'hiver", ["Isolez les tuyaux exposés avec des manchons isolants. Protégez le compteur dans son regard (plaque isolante, pas de paille humide). Coupez l'eau du robinet extérieur depuis l'intérieur, puis ouvrez-le pour le vider."]),
       ("Pendant les grands froids", ["Dans une maison ou un local inoccupé, gardez un chauffage hors gel. Si vous partez longtemps, coupez l'eau générale et videz les canalisations exposées."]),
       ("Un tuyau a gelé", ["Coupez l'arrivée d'eau, ouvrez le robinet concerné et réchauffez doucement le tuyau (sèche-cheveux, linges chauds). Jamais de chalumeau ni de flamme : risque d'incendie et de tuyau qui éclate."]),
       ("Un tuyau a éclaté", ["Coupez l'eau générale, coupez l'électricité si l'eau approche des prises, épongez et prenez des photos pour l'assurance. Un plombier remplace le tronçon abîmé."]),
      ],
      faq=[("À partir de quelle température les tuyaux gèlent-ils ?", "Le risque apparaît dès que la température descend sous 0 °C plusieurs heures, surtout pour les tuyaux non isolés et exposés au vent."),
           ("Un tuyau gelé va-t-il forcément éclater ?", "Non, mais l'eau en gelant prend du volume et peut fendre le tuyau. La fuite apparaît souvent au dégel : surveillez après avoir réchauffé."),
           ("Le dégât des eaux dû au gel est-il couvert ?", "Souvent, à condition d'avoir pris les précautions demandées par le contrat (logement chauffé, eau coupée en cas d'absence). Vérifiez votre contrat.")]),
 dict(slug="remplacer-baignoire-par-douche",
      titre="Remplacer une baignoire par une douche : étapes et conseils",
      court="Baignoire remplacée par une douche",
      desc="Remplacer sa baignoire par une douche à l'italienne ou un receveur extra-plat : les étapes, la durée des travaux et les points à vérifier avant le devis.",
      bref="Remplacer une baignoire par une douche se fait en général en quelques jours : dépose de la baignoire, reprise de l'évacuation, pose d'un receveur extra-plat ou d'une douche à l'italienne, étanchéité, faïence et paroi. Une visite sur place permet de vérifier l'évacuation et de faire un devis précis.",
      service=("salle-de-bain", "Rénovation de salle de bain : devis gratuit"),
      sections=[
       ("Pourquoi remplacer la baignoire ?", ["Plus de place dans la salle de bain, un accès plus facile (pas d'enjambement), moins de consommation d'eau au quotidien et une pièce plus facile à nettoyer."]),
       ("Receveur extra-plat ou douche à l'italienne ?", ["Le receveur extra-plat se pose sur le sol et reste très accessible. La douche à l'italienne, de plain-pied, demande de pouvoir donner de la pente vers l'évacuation : la visite sur place permet de savoir si c'est faisable."]),
       ("Les étapes des travaux", ["Dépose et évacuation de la baignoire, reprise de la plomberie et de l'évacuation, pose du receveur ou de la douche, étanchéité (le point le plus important), faïence ou panneaux muraux, paroi, mitigeur ou colonne de douche."]),
       ("Combien de temps ?", ["Souvent quelques jours pour un remplacement simple, davantage si la salle de bain est refaite entièrement. La date et la durée sont fixées avec vous dans le devis."]),
       ("Avant de demander un devis", ["Notez les dimensions de la baignoire, prenez quelques photos de la pièce et de l'évacuation, et pensez à vos envies : paroi fixe ou porte, barre de maintien, siège, niche de rangement."]),
      ],
      faq=[("Faut-il refaire toute la salle de bain ?", "Pas forcément. On peut remplacer seulement la baignoire par une douche et reprendre la faïence autour. Le devis détaille poste par poste."),
           ("La douche à l'italienne est-elle possible partout ?", "Pas toujours : il faut pouvoir créer la pente vers l'évacuation. Sinon, un receveur extra-plat donne un résultat très proche."),
           ("La visite et le devis sont-ils gratuits ?", "Oui, la visite et le devis écrit sont gratuits et sans engagement.")]),
]


def base():
    s = open(os.path.join(HERE, "index.html"), encoding="utf-8").read()
    s = re.sub(r'<script type="application/ld\+json"[^>]*>.*?</script>\n', "", s, flags=re.S)
    s = s.replace('<meta name="facebook-domain-verification" content="zgn82bjjiiikyrotvltoshbax3lbhl" />\n', "")
    s = re.sub(r'<meta name="msvalidate.01"[^>]*>\n', "", s)
    return s


def shell(s, depth, title, desc, url, main, ld):
    pre = "../" * depth
    s = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", s, count=1, flags=re.S)
    s = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{desc}">', s, count=1)
    s = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{url}">', s, count=1)
    s = re.sub(r'(href|src)="assets/', rf'\1="{pre}assets/', s)
    s = s.replace('href="mentions-legales.html"', f'href="{pre}mentions-legales.html"').replace('href="confidentialite.html"', f'href="{pre}confidentialite.html"')
    final = re.search(r'(<!-- CTA FINAL -->\s*<section class="final">.*?</section>)', s, re.S).group(1)
    s = re.sub(r"<main>.*?</main>", lambda m: f"<main>\n{main}\n  {final}\n</main>", s, count=1, flags=re.S)
    s = s.replace("</head>", f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>\n</head>', 1)
    return s


def article(a):
    url = f"{SITE}/conseils/{a['slug']}/"
    sec = "".join(f"<h2>{h}</h2>" + "".join(f"<p>{p}</p>" for p in ps) for h, ps in a["sections"])
    faq = "".join(f"<details><summary>{q}</summary><p>{r}</p></details>" for q, r in a["faq"])
    autres = " · ".join(f'<a href="../{b["slug"]}/">{b["court"]}</a>' for b in ARTICLES if b is not a)
    svc, svc_nom = a["service"]
    img = IMAGES[a["slug"]]
    av_txt, av_nom = AVIS[a["slug"]]
    avis = (f'<figure class="avis-post"><div class="stars" aria-label="5 étoiles sur 5">★★★★★</div>'
            f'<blockquote>« {av_txt} »</blockquote><figcaption><b>{av_nom}</b> · Avis Google · '
            f'<a href="{AVIS_URL}" target="_blank" rel="noopener">5,0/5 sur Google, voir tous les avis</a></figcaption></figure>')
    main = f'''  <section class="article">
    <div class="wrap">
      <p class="crumbs"><a href="../../">Accueil</a> › <a href="../">Conseils</a></p>
      <h1>{a["titre"]}</h1>
      <p class="meta">Par Réseau Artisans France, plombiers chauffagistes en Drôme, Ardèche et Isère · mis à jour le 16 novembre 2026</p>
      <div class="intro-post">
        <p class="bref"><b>En bref :</b> {a["bref"]}</p>
        <figure class="post-img"><img src="../../assets/{img[0]}" alt="{img[1]}" width="{img[3]}" height="{img[4]}" loading="eager"><figcaption>{img[2]}</figcaption></figure>
      </div>
      {sec}
      {avis}
      <div class="cta-box"><p><b>Besoin d'un plombier maintenant ?</b> Réseau Artisans France intervient 24h/24 et 7j/7, au prix juste : devis écrit avant les travaux, paiement après l'intervention.</p>
        <p><a class="btn btn-call js-call" href="tel:{TEL}"><svg class="ic"><use href="#i-phone"/></svg><span class="js-num">06 23 83 20 29</span></a> <a href="../../{svc}/">{svc_nom}</a></p></div>
    </div>
  </section>
  <section id="faq">
    <div class="wrap">
      <h2>Questions fréquentes</h2>
      {faq}
      <p class="legal">À lire aussi : {autres}.</p>
    </div>
  </section>'''
    ld = {"@context": "https://schema.org", "@type": "Article", "headline": a["titre"], "description": a["desc"], "url": url,
          "datePublished": DATE, "dateModified": DATE, "inLanguage": "fr-FR",
          "author": {"@type": "Organization", "name": "Réseau Artisans France", "url": SITE + "/"},
          "publisher": {"@type": "Plumber", "name": "Réseau Artisans France", "url": SITE + "/", "telephone": TEL, "address": ADDR,
                        "logo": {"@type": "ImageObject", "url": SITE + "/assets/raf-logo.png"}},
          "mainEntityOfPage": url, "image": f"{SITE}/assets/{IMAGES[a['slug']][0]}"}
    s = shell(base(), 2, f"{a['titre']} | Réseau Artisans France", a["desc"], url, main, ld)
    return seo.enrich(s, url, [("Conseils", SITE + "/conseils/"), (a["court"], url)])


def hub():
    url = f"{SITE}/conseils/"
    def carte(a):
        projet = a["service"][0] == "salle-de-bain"
        tag = '<span class="tag-post projet">Projet</span>' if projet else '<span class="tag-post urgence">Urgence</span>'
        return (f'<a class="card post{" projet" if projet else ""}" href="{a["slug"]}/" data-q="{a["titre"]} {a["desc"]} {a["bref"]}">'
                f'<span class="thumb"><img src="../assets/{IMAGES[a["slug"]][0]}" alt="" width="{IMAGES[a["slug"]][3]}" height="{IMAGES[a["slug"]][4]}" loading="lazy"></span>{tag}<h3>{a["titre"]}</h3><p>{a["desc"]}</p><span class="lire">Lire le conseil →</span></a>')
    cards = "".join(carte(a) for a in ARTICLES)
    main = f'''  <section class="article alt conseils">
    <div class="wrap">
      <p class="crumbs"><a href="../">Accueil</a> › Conseils</p>
      <h1>Conseils de <mark>plombier</mark></h1>
      <p class="bref"><b>En bref :</b> des réponses simples aux urgences les plus courantes (fuite d'eau, WC bouché, chauffe-eau ou chaudière en panne, gel des canalisations) et aux projets de salle de bain, par Réseau Artisans France, plombiers chauffagistes en Drôme, Ardèche et Isère.</p>
      <div class="searchbar"><svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7" fill="none" stroke="currentColor" stroke-width="2"/><path d="m20 20-4-4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
        <input id="q-conseils" type="search" placeholder="Rechercher un conseil : fuite, WC, chauffe-eau, gel…" aria-label="Rechercher un conseil" autocomplete="off"></div>
      <div class="grid g2 posts" id="posts">{cards}</div>
      <p class="vide" id="vide" hidden>Aucun conseil ne correspond. Votre problème n'est pas dans la liste ? Appelez-nous au <a class="js-call" href="tel:{TEL}"><span class="js-num">06 23 83 20 29</span></a>, on vous conseille gratuitement.</p>
    </div>
  </section>
  <script>
  (function(){{
    var n=function(t){{return t.toLowerCase().normalize("NFD").replace(/[\\u0300-\\u036f]/g,"");}};
    var q=document.getElementById("q-conseils"),cs=[].slice.call(document.querySelectorAll("#posts .post")),v=document.getElementById("vide");
    q.addEventListener("input",function(){{
      var m=n(q.value).split(/\\s+/).filter(Boolean),k=0;
      cs.forEach(function(c){{var t=n(c.getAttribute("data-q"));var ok=m.every(function(w){{return t.indexOf(w)>-1;}});c.hidden=!ok;if(ok)k++;}});
      v.hidden=k>0;
    }});
  }})();
  </script>'''
    ld = {"@context": "https://schema.org", "@type": "CollectionPage", "name": "Conseils de plombier", "url": url, "inLanguage": "fr-FR",
          "hasPart": [{"@type": "Article", "headline": a["titre"], "url": f"{url}{a['slug']}/"} for a in ARTICLES]}
    s = shell(base(), 1, "Conseils de plombier : fuite, WC bouché, chauffe-eau, chaudière | Réseau Artisans France",
              "Les bons réflexes en cas de fuite d'eau, WC bouché, chauffe-eau ou chaudière en panne, gel des canalisations, et conseils pour remplacer une baignoire par une douche.", url, main, ld)
    return seo.enrich(s, url, [("Conseils", url)])


def build():
    d = os.path.join(HERE, "conseils"); os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(hub())
    slugs = ["conseils"]
    for a in ARTICLES:
        p = os.path.join(d, a["slug"]); os.makedirs(p, exist_ok=True)
        open(os.path.join(p, "index.html"), "w", encoding="utf-8").write(article(a))
        slugs.append(f"conseils/{a['slug']}")
    return slugs


if __name__ == "__main__":
    print(build())

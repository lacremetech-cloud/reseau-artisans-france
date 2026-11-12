"""Génère une page « plombier + ville » par commune à partir de la page d'accueil (urgence).
Chaque page garde la même base (services, engagements, avis, FAQ) et ajoute un contenu propre à la ville.
Lancer : python3 build_villes.py"""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = open(os.path.join(HERE, "index.html"), encoding="utf-8").read()
TEL = "+33623832029"

VILLES = [
 dict(slug="plombier-valence", ville="Valence", cp="26000", dep="Drôme",
      quartiers=["Centre-ville", "Fontbarlettes", "Le Plan", "Polygone", "Châteauvert", "Valensolles", "Les Baumes", "Laprat"],
      voisines=["Bourg-lès-Valence", "Portes-lès-Valence", "Guilherand-Granges", "Saint-Péray", "Saint-Marcel-lès-Valence", "Malissard", "Beaumont-lès-Valence", "Montélier", "Chabeuil", "Étoile-sur-Rhône"],
      intro="Valence, c'est notre secteur principal : nos plombiers y interviennent toutes les semaines, du centre-ville aux quartiers résidentiels.",
      local=["Dans les immeubles anciens du centre-ville, les colonnes d'eau et les évacuations ont souvent plusieurs décennies : fuites sur raccords, canalisations entartrées et WC qui se bouchent font partie de nos interventions les plus fréquentes.",
             "Dans les maisons des quartiers comme Valensolles, Les Baumes ou Laprat, ce sont plutôt les chauffe-eau fatigués et les recherches de fuite (compteur qui tourne, tache au plafond) qui nous font venir.",
             "En copropriété, on travaille aussi bien pour les particuliers que pour les syndics et les agences : rapport d'intervention fourni pour l'assurance en cas de dégât des eaux."],
      faq=[("Intervenez-vous partout à Valence ?", "Oui, dans tous les quartiers de Valence et dans les communes autour : Bourg-lès-Valence, Portes-lès-Valence, Guilherand-Granges, Saint-Péray, Malissard… Appelez-nous, on vous donne l'heure d'arrivée au téléphone."),
           ("Pouvez-vous intervenir dans un appartement en copropriété ?", "Oui. Si la fuite vient des parties communes, on vous aide à identifier l'origine et on fournit le rapport pour le syndic et l'assurance.")]),
 dict(slug="plombier-romans-sur-isere", ville="Romans-sur-Isère", cp="26100", dep="Drôme",
      quartiers=["Centre historique", "La Monnaie", "Les Balmes", "Saint-Nicolas", "Les Chasses", "La Presle"],
      voisines=["Bourg-de-Péage", "Mours-Saint-Eusèbe", "Génissieux", "Peyrins", "Saint-Paul-lès-Romans", "Châtillon-Saint-Jean", "Chatuzange-le-Goubet", "Alixan"],
      intro="Romans-sur-Isère et le pays de Romans font partie de notre zone d'intervention quotidienne, à une vingtaine de minutes de Valence.",
      local=["Dans le centre historique de Romans, les maisons de ville anciennes ont souvent des évacuations en fonte et des installations qui ont été modifiées au fil des années : on y intervient régulièrement pour des débouchages et des fuites sur canalisations.",
             "Côté Bourg-de-Péage, Génissieux ou Mours-Saint-Eusèbe, ce sont surtout des maisons individuelles : chauffe-eau en panne, fuites sous évier, WC qui fuient en continu.",
             "Nous intervenons aussi sur le pays de Romans pour les projets : remplacement de baignoire par une douche, rénovation de salle de bain, remplacement de chaudière gaz."],
      faq=[("Combien de temps pour venir à Romans ?", "Comptez en général le temps de trajet depuis Valence, soit une vingtaine de minutes, selon nos interventions en cours. L'heure exacte vous est annoncée au téléphone."),
           ("Intervenez-vous à Bourg-de-Péage et dans les villages autour ?", "Oui : Bourg-de-Péage, Mours-Saint-Eusèbe, Génissieux, Peyrins, Saint-Paul-lès-Romans, Chatuzange-le-Goubet, Alixan…")]),
 dict(slug="plombier-bourg-les-valence", ville="Bourg-lès-Valence", cp="26500", dep="Drôme",
      quartiers=["Centre", "Les Chirouzes", "Le Valentin", "Les Pêchers", "La Cité Chabeuil"],
      voisines=["Valence", "Saint-Marcel-lès-Valence", "Châteauneuf-sur-Isère", "Guilherand-Granges", "Pont-de-l'Isère", "Saint-Péray"],
      intro="Bourg-lès-Valence est juste au nord de Valence : c'est l'une des communes où nous pouvons arriver le plus vite.",
      local=["Entre les résidences des Chirouzes, le Valentin et les maisons des quartiers pavillonnaires, nos interventions vont du débouchage de WC et d'évier à la recherche de fuite et au remplacement de chauffe-eau.",
             "Pour les maisons des années 70 à 90, les chauffe-eau électriques arrivent souvent en fin de vie : quand le ballon fuit ou ne chauffe plus, on vous dit franchement s'il vaut mieux réparer ou remplacer.",
             "Pour les fuites, on coupe, on trouve l'origine et on répare, avec un rapport pour votre assurance habitation."],
      faq=[("Êtes-vous rapides à Bourg-lès-Valence ?", "Bourg-lès-Valence est collée à Valence, c'est l'une des communes où l'on arrive le plus vite. L'heure d'arrivée vous est donnée au téléphone."),
           ("Faites-vous aussi les salles de bain à Bourg-lès-Valence ?", "Oui : remplacement de baignoire par une douche, rénovation complète, avec visite et devis gratuits.")]),
 dict(slug="plombier-guilherand-granges", ville="Guilherand-Granges", cp="07500", dep="Ardèche",
      quartiers=["Centre", "Les Granges", "Crussol", "Le Pont"],
      voisines=["Saint-Péray", "Cornas", "Soyons", "Toulaud", "Châteaubourg", "Valence"],
      intro="Guilherand-Granges, de l'autre côté du Rhône face à Valence, fait partie de notre secteur côté Ardèche.",
      local=["Côté Ardèche, entre Guilherand-Granges, Saint-Péray et Cornas, on intervient surtout dans des maisons individuelles et de petites résidences : fuites, WC bouchés, chauffe-eau en panne.",
             "Sur les maisons construites à flanc de coteau autour de Saint-Péray et Toulaud, les évacuations longues et les regards extérieurs demandent parfois un curage ou une inspection par caméra : on a le matériel pour.",
             "Un seul numéro pour les deux rives du Rhône : que vous soyez à Valence ou à Guilherand, c'est la même équipe."],
      faq=[("Venez-vous côté Ardèche ?", "Oui : Guilherand-Granges, Saint-Péray, Cornas, Soyons, Toulaud, Châteaubourg… L'heure d'arrivée vous est annoncée au téléphone."),
           ("Pouvez-vous inspecter une canalisation extérieure ?", "Oui, avec une caméra d'inspection pour trouver l'origine exacte du problème. La vidéo peut être remise pour l'assurance.")]),
 dict(slug="plombier-tournon-sur-rhone", ville="Tournon-sur-Rhône", cp="07300", dep="Ardèche",
      quartiers=["Centre-ville", "Quai Farconnet", "Les Luettes", "Saint-Antoine"],
      voisines=["Tain-l'Hermitage", "Mauves", "Saint-Jean-de-Muzols", "Lemps", "Plats", "Glun", "Vion"],
      intro="Tournon-sur-Rhône et ses environs, côté Ardèche face à Tain-l'Hermitage, sont dans notre zone d'intervention.",
      local=["Dans le centre ancien de Tournon, les maisons de ville et petits immeubles ont souvent des canalisations anciennes : fuites sur raccords, évacuations bouchées, robinetterie à remplacer.",
             "Dans les villages autour, de Mauves à Saint-Jean-de-Muzols, on intervient surtout sur des maisons individuelles : chauffe-eau, fuites, recherche de fuite quand le compteur tourne sans raison.",
             "Pour les projets, on se déplace aussi pour une visite gratuite : salle de bain, remplacement de baignoire par une douche, chaudière gaz."],
      faq=[("Intervenez-vous à Tournon et à Tain ?", "Oui, des deux côtés du Rhône : Tournon-sur-Rhône, Tain-l'Hermitage, Mauves, Saint-Jean-de-Muzols, Glun, Vion…"),
           ("Le déplacement est-il plus cher pour Tournon ?", "On travaille au prix juste, déplacement compris dans le devis. Pas de surprise sur la facture.")]),
 dict(slug="plombier-tain-l-hermitage", ville="Tain-l'Hermitage", cp="26600", dep="Drôme",
      quartiers=["Centre", "Les Rochas", "La Plaine", "Les Granges"],
      voisines=["Tournon-sur-Rhône", "Mercurol-Veaunes", "Chanos-Curson", "Érôme", "Crozes-Hermitage", "Pont-de-l'Isère", "Beaumont-Monteux"],
      intro="Tain-l'Hermitage et les villages du vignoble, côté Drôme, font partie de notre secteur, entre Valence et le nord de la Drôme.",
      local=["À Tain et autour, entre maisons de ville du centre et maisons individuelles des villages du vignoble, on intervient pour les fuites, les débouchages et les chauffe-eau en panne.",
             "Pour les maisons isolées de Mercurol-Veaunes, Chanos-Curson ou Crozes-Hermitage, on vous indique au téléphone l'heure d'arrivée réaliste plutôt qu'une promesse qu'on ne tiendrait pas.",
             "Chaudière gaz en panne ou trop ancienne ? Diagnostic sur place et devis clair pour le remplacement, dépose, pose et mise en service comprises."],
      faq=[("Venez-vous dans les villages autour de Tain ?", "Oui : Mercurol-Veaunes, Chanos-Curson, Érôme, Crozes-Hermitage, Pont-de-l'Isère, Beaumont-Monteux… et Tournon de l'autre côté du Rhône."),
           ("Remplacez-vous les chaudières gaz à Tain ?", "Oui. Visite et devis gratuits, avec dépose de l'ancienne chaudière, pose et mise en service.")]),
 dict(slug="plombier-grenoble", ville="Grenoble", cp="38000", dep="Isère",
      quartiers=["Centre-ville", "Championnet", "Île Verte", "Saint-Bruno", "Les Eaux-Claires", "Villeneuve", "Europole", "Berriat"],
      voisines=["Échirolles", "Saint-Martin-d'Hères", "Fontaine", "Seyssinet-Pariset", "Saint-Égrève", "Meylan", "Eybens", "Sassenage", "Le Pont-de-Claix", "Seyssins"],
      intro="Nous intervenons à Grenoble et dans toute l'agglomération, pour les urgences comme pour les projets.",
      local=["Dans les immeubles du centre, de l'Île Verte ou de Championnet, beaucoup de colonnes et d'évacuations sont anciennes : fuites sur raccords, dégâts des eaux chez le voisin du dessous et canalisations bouchées font partie des interventions les plus courantes.",
             "Dans l'agglomération, d'Échirolles à Meylan en passant par Saint-Martin-d'Hères et Fontaine, on intervient en appartement comme en maison : chauffe-eau en panne, WC qui fuient, recherche de fuite quand le compteur tourne.",
             "Pour éviter les mauvaises surprises, on vous demande au téléphone de décrire le problème, et si possible une photo sur WhatsApp : l'heure d'arrivée vous est annoncée avant de venir."],
      faq=[("Intervenez-vous dans toute l'agglomération grenobloise ?", "Oui : Grenoble, Échirolles, Saint-Martin-d'Hères, Fontaine, Seyssinet-Pariset, Saint-Égrève, Meylan, Eybens, Sassenage… L'heure d'arrivée vous est annoncée au téléphone."),
           ("Pouvez-vous fournir un rapport pour le syndic ou l'assurance ?", "Oui. En cas de dégât des eaux en copropriété, on vous remet un rapport d'intervention et une facture détaillée pour votre assurance et votre syndic.")]),
 dict(slug="plombier-annonay", ville="Annonay", cp="07100", dep="Ardèche",
      quartiers=["Centre-ville", "Le Zodiaque", "Fontanes", "Bernaudin", "Les Perrières", "Vissenty"],
      voisines=["Davézieux", "Boulieu-lès-Annonay", "Roiffieux", "Saint-Marcel-lès-Annonay", "Vernosc-lès-Annonay", "Quintenas", "Talencieux"],
      intro="Notre siège est à Annonay : c'est ici que l'entreprise est implantée, au nord de l'Ardèche.",
      local=["À Annonay, entre les rues en pente du centre ancien et les quartiers plus récents, les problèmes les plus fréquents sont les fuites sur canalisations anciennes, les WC et éviers bouchés, et les chauffe-eau en fin de vie.",
             "Dans le bassin d'Annonay, de Davézieux à Boulieu-lès-Annonay, on intervient pour les particuliers comme pour les commerces et les professionnels.",
             "Projet de salle de bain ou de remplacement de chaudière ? Visite et devis gratuits, par une entreprise locale implantée à Annonay."],
      faq=[("Êtes-vous vraiment basés à Annonay ?", "Oui, le siège de Réseau Artisans France est au 60 rue des Bouvreuils, 07100 Annonay."),
           ("Intervenez-vous dans tout le bassin d'Annonay ?", "Oui : Davézieux, Boulieu-lès-Annonay, Roiffieux, Saint-Marcel-lès-Annonay, Vernosc-lès-Annonay, Quintenas, Talencieux…")]),
 dict(slug="plombier-portes-les-valence", ville="Portes-lès-Valence", cp="26800", dep="Drôme",
      voisines=["Valence", "Étoile-sur-Rhône", "Beauvallon", "Montéléger", "Beaumont-lès-Valence", "Soyons", "Charmes-sur-Rhône"],
      intro="Portes-lès-Valence, au sud de Valence, fait partie de notre secteur d'intervention de tous les jours.",
      local=["Entre les résidences et les maisons individuelles de Portes-lès-Valence, nos interventions les plus fréquentes sont les fuites sous évier, les WC qui fuient ou se bouchent et les chauffe-eau qui ne chauffent plus.",
             "Pour les fuites invisibles (compteur qui tourne, facture d'eau qui grimpe), on recherche l'origine sans tout casser et on vous remet un rapport pour l'assurance.",
             "Au sud de Valence, on intervient aussi à Étoile-sur-Rhône, Beauvallon et Montéléger : l'heure d'arrivée vous est annoncée au téléphone."],
      faq=[("Venez-vous à Portes-lès-Valence le soir et le week-end ?", "Oui, nous intervenons 24h/24 et 7j/7. Le tarif du soir et du week-end vous est indiqué avant l'intervention."),
           ("Intervenez-vous à Étoile-sur-Rhône et Beauvallon ?", "Oui, ainsi qu'à Montéléger, Beaumont-lès-Valence et Soyons.")]),
 dict(slug="plombier-saint-peray", ville="Saint-Péray", cp="07130", dep="Ardèche",
      voisines=["Guilherand-Granges", "Cornas", "Toulaud", "Saint-Romain-de-Lerps", "Alboussière", "Châteaubourg", "Valence"],
      intro="Saint-Péray, au pied du château de Crussol, est dans notre secteur côté Ardèche, juste en face de Valence.",
      local=["À Saint-Péray, on intervient surtout dans des maisons individuelles : fuites, WC bouchés, chauffe-eau en panne, robinetterie à remplacer.",
             "Pour les maisons sur les hauteurs et à flanc de coteau, les évacuations longues demandent parfois un curage ou une inspection par caméra : on a le matériel.",
             "Même équipe des deux côtés du Rhône : un seul numéro pour Saint-Péray, Guilherand-Granges et Valence."],
      faq=[("Intervenez-vous à Saint-Péray et Toulaud ?", "Oui, ainsi qu'à Cornas, Saint-Romain-de-Lerps, Alboussière et Châteaubourg."),
           ("Pouvez-vous déboucher une canalisation extérieure ?", "Oui, par curage ou hydrocurage selon le cas, avec inspection caméra si besoin.")]),
 dict(slug="plombier-bourg-de-peage", ville="Bourg-de-Péage", cp="26300", dep="Drôme",
      voisines=["Romans-sur-Isère", "Chatuzange-le-Goubet", "Alixan", "Saint-Paul-lès-Romans", "Mours-Saint-Eusèbe", "Génissieux"],
      intro="Bourg-de-Péage, de l'autre côté de l'Isère face à Romans, fait partie de notre zone d'intervention dans le pays de Romans.",
      local=["À Bourg-de-Péage, entre maisons de ville et lotissements, on intervient pour les fuites, les débouchages de WC et d'évier et les chauffe-eau en panne.",
             "Quand le compteur tourne sans raison, on cherche la fuite sans tout casser et on vous remet un rapport pour votre assurance habitation.",
             "On se déplace aussi pour les projets : remplacement de baignoire par une douche, rénovation de salle de bain, remplacement de chaudière gaz."],
      faq=[("Intervenez-vous à Bourg-de-Péage et Romans ?", "Oui, des deux côtés de l'Isère, ainsi qu'à Chatuzange-le-Goubet, Alixan et Saint-Paul-lès-Romans."),
           ("Vos prix sont-ils clairs ?", "Oui : on travaille au prix juste, avec un devis écrit avant les travaux.")]),
 dict(slug="plombier-crest", ville="Crest", cp="26400", dep="Drôme",
      voisines=["Aouste-sur-Sye", "Eurre", "Allex", "Grane", "Chabrillan", "Divajeu", "Upie"],
      intro="Crest et la vallée de la Drôme font partie de notre secteur, au sud-est de Valence.",
      local=["Dans le centre ancien de Crest, les maisons de ville ont souvent des canalisations anciennes : fuites sur raccords et évacuations qui se bouchent sont fréquentes.",
             "Dans les villages autour, d'Aouste-sur-Sye à Allex et Grane, on intervient surtout pour des chauffe-eau en panne, des fuites et des recherches de fuite.",
             "Pour les communes plus éloignées, on vous donne au téléphone une heure d'arrivée réaliste plutôt qu'une promesse qu'on ne tiendrait pas."],
      faq=[("Venez-vous à Crest et dans la vallée de la Drôme ?", "Oui : Crest, Aouste-sur-Sye, Eurre, Allex, Grane, Chabrillan, Divajeu, Upie… L'heure d'arrivée vous est annoncée au téléphone."),
           ("Remplacez-vous les chauffe-eau à Crest ?", "Oui, diagnostic sur place et remplacement si besoin, avec un devis clair avant les travaux.")]),
 dict(slug="plombier-echirolles", ville="Échirolles", cp="38130", dep="Isère",
      quartiers=["Village Sud", "Les Essarts", "Surieux", "La Luire", "Village 2", "Ouest"],
      voisines=["Grenoble", "Eybens", "Le Pont-de-Claix", "Saint-Martin-d'Hères", "Bresson", "Jarrie", "Claix"],
      intro="Échirolles, au sud de Grenoble, fait partie de notre secteur dans l'agglomération grenobloise.",
      local=["Dans les grands ensembles d'Échirolles, les colonnes d'eau et les évacuations communes sont souvent à l'origine des fuites et des dégâts des eaux chez le voisin du dessous.",
             "Dans les maisons et petites résidences, ce sont surtout les chauffe-eau en panne, les WC qui fuient et les canalisations bouchées.",
             "En copropriété, on vous remet un rapport d'intervention pour le syndic et l'assurance."],
      faq=[("Intervenez-vous partout à Échirolles ?", "Oui, dans tous les quartiers d'Échirolles et autour : Eybens, Le Pont-de-Claix, Jarrie, Claix… L'heure d'arrivée vous est annoncée au téléphone."),
           ("Fournissez-vous un rapport pour le syndic ?", "Oui, avec une facture détaillée pour l'assurance.")]),
 dict(slug="plombier-saint-martin-d-heres", ville="Saint-Martin-d'Hères", cp="38400", dep="Isère",
      quartiers=["Croix-Rouge", "Renaudie", "Champberton", "Portail Rouge", "Campus"],
      voisines=["Grenoble", "Gières", "Poisat", "Eybens", "Meylan", "Venon", "Échirolles"],
      intro="Saint-Martin-d'Hères, à l'est de Grenoble, fait partie de notre zone d'intervention dans l'agglomération.",
      local=["Entre les résidences, les logements étudiants autour du campus et les maisons, nos interventions vont du WC bouché à la fuite sous évier et au chauffe-eau en panne.",
             "Pour les propriétaires bailleurs et les agences, on intervient rapidement et on envoie la facture détaillée et le rapport.",
             "Fuite invisible ? On localise l'origine sans tout casser."],
      faq=[("Intervenez-vous pour les propriétaires bailleurs ?", "Oui, pour les particuliers, les bailleurs et les agences, avec facture et rapport d'intervention."),
           ("Venez-vous à Gières et Poisat ?", "Oui, ainsi qu'à Eybens, Meylan et Venon.")]),
 dict(slug="plombier-fontaine", ville="Fontaine", cp="38600", dep="Isère",
      voisines=["Grenoble", "Seyssinet-Pariset", "Sassenage", "Seyssins", "Saint-Égrève", "Noyarey", "Veurey-Voroize"],
      intro="Fontaine, à l'ouest de Grenoble, fait partie de notre secteur dans l'agglomération grenobloise.",
      local=["À Fontaine, on intervient en appartement comme en maison : fuites, WC et éviers bouchés, chauffe-eau qui ne chauffe plus.",
             "Dans les immeubles, une fuite peut vite toucher le voisin du dessous : on coupe, on trouve l'origine et on répare, avec un rapport pour l'assurance.",
             "On couvre aussi Seyssinet-Pariset, Sassenage et Seyssins avec la même équipe."],
      faq=[("Intervenez-vous à Fontaine et Sassenage ?", "Oui, ainsi qu'à Seyssinet-Pariset, Seyssins, Saint-Égrève et Noyarey."),
           ("En combien de temps pouvez-vous venir ?", "On vous donne une heure d'arrivée précise au téléphone, selon nos interventions en cours.")]),
 dict(slug="plombier-meylan", ville="Meylan", cp="38240", dep="Isère",
      quartiers=["Les Béalières", "Plaine Fleurie", "Haut-Meylan", "Inovallée", "Le Charlaix"],
      voisines=["Grenoble", "La Tronche", "Montbonnot-Saint-Martin", "Corenc", "Saint-Ismier", "Biviers", "Saint-Martin-d'Hères"],
      intro="Meylan, au nord-est de Grenoble, fait partie de notre secteur dans l'agglomération.",
      local=["À Meylan, on intervient surtout dans des maisons et des résidences : chauffe-eau en panne, fuites, robinetterie à remplacer, WC qui fuient en continu.",
             "Pour les entreprises d'Inovallée, on intervient aussi sur les sanitaires et les réseaux d'évacuation, avec curage si besoin.",
             "Projet de salle de bain ou de remplacement de chaudière gaz ? Visite et devis gratuits."],
      faq=[("Intervenez-vous pour les entreprises ?", "Oui, pour les particuliers comme pour les professionnels, avec facture détaillée."),
           ("Venez-vous à La Tronche et Montbonnot ?", "Oui, ainsi qu'à Corenc, Saint-Ismier et Biviers.")]),
 dict(slug="plombier-voiron", ville="Voiron", cp="38500", dep="Isère",
      voisines=["Coublevie", "Saint-Jean-de-Moirans", "Moirans", "La Buisse", "Saint-Étienne-de-Crossey", "Chirens", "Rives"],
      intro="Voiron et le pays voironnais font partie de notre secteur, au nord-ouest de Grenoble.",
      local=["À Voiron et Coublevie, on intervient en maison comme en appartement : fuites d'eau, WC bouchés, chauffe-eau en panne, recherche de fuite.",
             "Dans les maisons plus anciennes du centre, les canalisations et évacuations demandent parfois un curage ou une inspection par caméra.",
             "On couvre aussi Moirans, Saint-Jean-de-Moirans, La Buisse et Rives : l'heure d'arrivée vous est annoncée au téléphone."],
      faq=[("Intervenez-vous à Voiron et Coublevie ?", "Oui, ainsi qu'à Moirans, Saint-Jean-de-Moirans, La Buisse, Saint-Étienne-de-Crossey et Rives."),
           ("Vos prix sont-ils clairs ?", "Oui : on travaille au prix juste, avec un devis écrit avant les travaux.")]),
]


def li(items):
    return "".join(f"<li>{x}</li>" for x in items)


def page(v):
    s = BASE
    V, CP = v["ville"], v["cp"]
    url = f"https://reseauartisansfrance.com/{v['slug']}/"
    title = f"Plombier à {V} ({CP}) : urgence 24h/24, fuite, WC bouché, chauffe-eau | Réseau Artisans France"
    desc = f"Plombier à {V} et alentours : fuite d'eau, WC bouché, chauffe-eau en panne. Intervention 24h/24 et 7j/7, au prix juste. Entreprise locale."
    s = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", s, count=1, flags=re.S)
    s = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{desc}">', s, count=1)
    s = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{url}">', s, count=1)
    s = re.sub(r'<script type="application/ld\+json">.*?</script>\n', "", s, flags=re.S)
    s = s.replace('<meta name="facebook-domain-verification" content="zgn82bjjiiikyrotvltoshbax3lbhl" />\n', "")
    # Chemins relatifs : la page est dans un sous-dossier
    s = re.sub(r'(href|src)="assets/', r'\1="../assets/', s)
    s = s.replace('href="mentions-legales.html"', 'href="../mentions-legales.html"').replace('href="confidentialite.html"', 'href="../confidentialite.html"')
    s = s.replace("Urgence plomberie · Drôme-Ardèche", f"Plombier à {V} · {CP}", 1)
    s = s.replace("<span>Votre plombier,</span>", f"<span>Votre plombier à {V},</span>", 1)
    s = s.replace("<span data-ville>Valence</span>", f"<span data-ville>{V}</span>")
    # Bloc zones : communes propres à la ville
    zones = re.search(r'(<section class="alt" id="zones">.*?</section>)', s, re.S).group(1)
    new_zones = f'''<section class="alt" id="zones">
    <div class="wrap">
      <h2>Plombier à {V} et dans les communes voisines</h2>
      <p class="sub">Nous intervenons à {V} ({CP}) et autour, côté {v["dep"]}.</p>
      <div class="chips">{"".join(f'<span class="chip"><svg class="ic"><use href="#i-pin"/></svg>{x}</span>' for x in [V] + v["voisines"])}</div>
      <p class="legal">Votre commune n'est pas dans la liste ? Appelez-nous, on vous dit tout de suite si on peut venir.</p>
    </div>
  </section>'''
    s = s.replace(zones, new_zones, 1)
    # Bloc local inséré avant les urgences
    local = f'''<section id="local">
    <div class="wrap">
      <h2>Votre plombier à {V}</h2>
      <p class="sub">{v["intro"]}</p>
      {"".join(f"<p>{p}</p>" for p in v["local"])}
      {("<p><b>Quartiers où nous intervenons :</b> " + ", ".join(v["quartiers"]) + ".</p>") if v.get("quartiers") else ""}
      <p>Urgences : <a href="../fuite-d-eau/">fuite d'eau</a> · <a href="../debouchage/">WC et canalisations bouchés</a> · <a href="../chauffe-eau-en-panne/">chauffe-eau en panne</a> · <a href="../depannage-chaudiere/">chaudière en panne</a>.</p>
      <p>Pour un projet, voir aussi : <a href="../salle-de-bain/">rénovation de salle de bain</a> et <a href="../chaudiere/">remplacement de chaudière gaz</a>.</p>
    </div>
  </section>
  '''
    s = s.replace('<section class="alt" id="urgences">', local + '<section class="alt" id="urgences">', 1)
    # FAQ locale ajoutée en tête de la FAQ
    extra = "".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in v["faq"])
    s = re.sub(r'(<section id="faq">.*?<h2>Questions fréquentes</h2>)', lambda m: m.group(1) + "\n      " + extra, s, count=1, flags=re.S)
    # Données structurées
    ld = {"@context": "https://schema.org", "@type": "Plumber", "name": "Réseau Artisans France", "url": url,
          "telephone": TEL, "image": "https://reseauartisansfrance.com/assets/raf-logo.png",
          "address": {"@type": "PostalAddress", "streetAddress": "60 rue des Bouvreuils", "postalCode": "07100", "addressLocality": "Annonay", "addressCountry": "FR"},
          "areaServed": [{"@type": "City", "name": x} for x in [V] + v["voisines"]],
          "openingHoursSpecification": {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], "opens": "00:00", "closes": "23:59"}}
    s = s.replace("</head>", f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>\n</head>', 1)
    return s


if __name__ == "__main__":
    for v in VILLES:
        d = os.path.join(HERE, v["slug"]); os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(page(v))
        print(v["slug"])

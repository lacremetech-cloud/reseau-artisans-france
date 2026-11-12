"""Génère /salle-de-bain/index.html et /chaudiere/index.html à partir d'un gabarit commun.
Lancer : python3 build_landings.py"""
import os

TEL, TELH = "+33623832029", "06 23 83 20 29"
ICONS = """<svg width="0" height="0" style="position:absolute" aria-hidden="true">
<symbol id="i-phone" viewBox="0 0 24 24"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.13.96.36 1.9.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.91.34 1.85.57 2.81.7A2 2 0 0 1 22 16.92z"/></symbol>
<symbol id="i-check" viewBox="0 0 24 24"><path d="M20 6 9 17l-5-5"/></symbol>
</svg>"""
CHK = '<svg class="ic"><use href="#i-check"/></svg>'
REVIEWS = [
 ("Intervention rapide pour un problème de fuite d’eau. Travail propre et efficace, avec de bons conseils. Entreprise sérieuse et ponctuelle. Je recommande sans hésiter !", "Zoulihka R."),
 ("Très bonne expérience ! J’avais une urgence en plomberie et l’entreprise a été très réactive. Le plombier était ponctuel, professionnel et efficace. Le problème a été résolu rapidement et le travail est propre.", "Khadija B."),
 ("Technicien excellent, irréprochable, très agréable, souriant. Je vous recommande fortement l’entreprise, entreprise très sérieuse.", "Anthony M."),
]
TRUST = [
 ("🇫🇷", "Entreprise locale", "Des artisans de la Drôme et de l'Ardèche, pas une plateforme ni un centre d'appel."),
 ("🛠", "Plus de 10 ans d'expérience", "Des professionnels qui connaissent leur métier et vous conseillent honnêtement."),
 ("💶", "Au prix juste", "Un devis gratuit, écrit et détaillé poste par poste. Pas de surprise sur la facture."),
 ("⚡", "Rapide et propre", "On intervient vite, on protège votre intérieur et on laisse les lieux propres."),
 ("📅", "Délais respectés", "La date des travaux est fixée avec vous, et on s'y tient."),
]
ZONES = ["Valence", "Bourg-lès-Valence", "Romans-sur-Isère", "Guilherand-Granges", "Saint-Péray", "Tournon-sur-Rhône", "Tain-l'Hermitage", "Chabeuil", "Crest", "Montélimar", "Grenoble", "Échirolles"]


def opts(name, items, required=False):
    r = ' required' if required else ''
    return '<div class="opts">' + "".join(f'<label><input type="radio" name="{name}" value="{v}"{r}>{v}</label>' for v in items) + '</div>'


def slider(before, after, alt_b, alt_a, eager=False):
    lz = '' if eager else ' loading="lazy"'
    return (f'<div class="cmp" style="--pos:50%">'
            f'<img src="../assets/{after}" alt="{alt_a}" width="900" height="1116"{lz}>'
            f'<div class="cmp-b"><img src="../assets/{before}" alt="{alt_b}" width="900" height="1116"{lz}></div>'
            f'<span class="lab av">AVANT</span><span class="lab ap">APRÈS</span><span class="cmp-h" aria-hidden="true"></span>'
            f'<input type="range" min="0" max="100" value="50" aria-label="Comparer avant et après"></div>')


def page(p):
    steps = "".join(f'<div class="card step"><h3>{t}</h3><p>{d}</p></div>' for t, d in p["steps"])
    done = "".join(f"<li>{CHK}{x}</li>" for x in p["list"])
    ticks = "".join(f"<li>{CHK}<span>{x}</span></li>" for x in p["ticks"])
    photos = "".join(f'<img src="../assets/{f}" alt="{a}" width="800" height="1000" loading="lazy">' for f, a in p["photos"])
    revs = "".join(f'<figure class="card review" style="margin:0"><div class="stars">★★★★★</div><blockquote>« {t} »</blockquote><figcaption><b>{n}</b> · Avis Google · octobre 2026</figcaption></figure>' for t, n in REVIEWS)
    faq = "".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in p["faq"])
    trust = "".join(f'<div class="trust-item"><span class="t-ic" aria-hidden="true">{i}</span><div><b>{t}</b><p>{d}</p></div></div>' for i, t, d in TRUST)
    gallery = "".join(slider(b, a, ab, aa) for b, a, ab, aa in p.get("gallery", []))
    zones = "".join(f'<span class="chip">{z}</span>' for z in ZONES)
    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{p['title']}</title>
<meta name="description" content="{p['desc']}">
<link rel="canonical" href="https://reseauartisansfrance.com/{p['slug']}/">
<link rel="icon" type="image/png" href="../assets/favicon.png">
<link rel="apple-touch-icon" href="../assets/apple-touch-icon.png">
<meta property="og:title" content="{p['title']}">
<meta property="og:description" content="{p['desc']}">
<meta property="og:image" content="https://reseauartisansfrance.com/assets/{p['after']}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Archivo+Black&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../assets/landing.css">
</head>
<body class="brut">
{ICONS}
<header class="top"><div class="tricolore"></div><div class="wrap">
  <a href="/" aria-label="Réseau Artisans France, accueil"><img class="brand-logo" src="../assets/raf-logo.png" alt="RAF, Réseau Artisans France" width="640" height="256"></a>
  <a class="btn btn-call js-call" href="tel:{TEL}"><svg class="ic"><use href="#i-phone"/></svg><span class="num js-num">{TELH}</span><span class="lbl">Appeler</span></a>
</div></header>

<main>
<section class="hero"><div class="wrap hero-grid">
  <div>
    <span class="eyebrow">{p['eyebrow']}</span>
    <h1>{p['h1']}</h1>
    {('<p class="tagline">' + p['tagline'] + '</p>') if p.get('tagline') else ''}
    <p class="lead">{p['lead']}</p>
    <ul class="ticks">{ticks}</ul>
    {slider(p['before'], p['after'], p['before_alt'], p['after_alt'], eager=True)}
    <p class="illus">Faites glisser pour comparer · {p['illus']}</p>
  </div>

  <form class="form-card" id="devis" data-page="{p['slug']}" data-cta="{p['cta']}" novalidate>
    <div class="fields">
      <h2>{p['form_title']}</h2>
      <p class="hint">{p['form_hint']}</p>
      <fieldset><legend>Votre projet</legend>{opts('projet', p['projets'])}</fieldset>
      <fieldset><legend>Quand ?</legend>{opts('delai', p['delais'])}</fieldset>
      <div class="f-row two">
        <div><label class="l" for="nom">Nom</label><input type="text" id="nom" name="nom" autocomplete="name" required></div>
        <div><label class="l" for="tel">Téléphone</label><input type="tel" id="tel" name="tel" autocomplete="tel" inputmode="tel" required></div>
      </div>
      <div class="f-row"><div><label class="l" for="ville">Commune</label><input type="text" id="ville" name="ville" autocomplete="address-level2" required></div></div>
      <div class="f-row"><div><label class="l" for="message">Précisions <span style="font-weight:500;color:var(--muted)">(facultatif)</span></label><textarea id="message" name="message" placeholder="{p['placeholder']}"></textarea></div></div>
      <input class="hp" type="text" name="site" tabindex="-1" autocomplete="off" aria-hidden="true">
      <label class="optin"><input type="checkbox" name="mesure" value="oui"> J'accepte que Meta (Facebook, Instagram) soit informé de ma demande pour mesurer l'efficacité des publicités. <span>Facultatif.</span></label>
      <button class="btn btn-call submit" type="submit">{p['cta']}</button>
      <p class="err" role="alert"></p>
      <p class="legal-mini">Vos coordonnées servent à vous rappeler pour ce projet. <a href="../confidentialite.html">Confidentialité</a></p>
      <div class="or">ou</div>
      <a class="btn alt-call js-call" href="tel:{TEL}"><svg class="ic"><use href="#i-phone"/></svg>Appeler le <span class="js-num">{TELH}</span></a>
    </div>
    <div class="thanks" aria-live="polite">
      <div class="big">✅</div>
      <h2>Demande bien reçue !</h2>
      <p>Un artisan vous rappelle rapidement pour en parler et fixer la visite. Pensez à décrocher, même si le numéro est inconnu.</p>
      <a class="btn btn-navy js-call" href="tel:{TEL}">Pressé ? Appelez le <span class="js-num">{TELH}</span></a>
    </div>
  </form>
</div></section>

{('<section class="gal"><div class="wrap"><h2>' + p['gal_title'] + '</h2><p class="sub">' + p['gal_sub'] + '</p><div class="gal-grid">' + gallery + '</div><p class="illus">' + p['illus'] + '</p></div></section>') if gallery else ''}

<section class="trust"><div class="wrap">
  <h2>Pourquoi nous faire confiance</h2>
  <div class="trust-grid">{trust}</div>
</div></section>

<section class="alt"><div class="wrap">
  <h2>Comment ça se passe</h2>
  <p class="sub">{p['steps_sub']}</p>
  <div class="grid g4 steps">{steps}</div>
</div></section>

<section><div class="wrap">
  <h2>{p['list_title']}</h2>
  <p class="sub">{p['list_sub']}</p>
  <ul class="list">{done}</ul>
</div></section>

<section class="alt"><div class="wrap">
  <h2>{p['photos_title']}</h2>
  <p class="sub">Photos d'illustration.</p>
  <div class="photos">{photos}</div>
</div></section>

<section><div class="wrap">
  <h2>Ce que nos clients disent de nous</h2>
  <p class="sub"><span class="stars">★★★★★</span> <b>5,0/5</b> sur Google · avis sur nos interventions de plomberie</p>
  <div class="grid g3">{revs}</div>
</div></section>

<section class="alt"><div class="wrap">
  <h2>Où intervenons-nous ?</h2>
  <p class="sub">Drôme, nord Ardèche et agglomération de Grenoble. Votre commune n'est pas listée ? Demandez quand même.</p>
  <div class="chips">{zones}</div>
</div></section>

<section><div class="wrap">
  <h2>Questions fréquentes</h2>
  {faq}
</div></section>

<section class="final"><div class="wrap">
  <h2>{p['final_title']}</h2>
  <p>{p['final_sub']}</p>
  <a class="btn btn-call" href="#devis" style="font-size:18px;padding:16px 28px">{p['cta']}</a>
</div></section>
</main>

<footer><div class="wrap">
  RÉSEAU ARTISANS FRANCE · SAS au capital de 1 000 € · Siège : 60 rue des Bouvreuils, 07100 Annonay<br>
  SIRET 105 406 755 00014 · RCS Aubenas 105 406 755 · <a href="mailto:contact@reseauartisansfrance.com">contact@reseauartisansfrance.com</a> · Tél. <a class="js-call" href="tel:{TEL}"><span class="js-num">{TELH}</span></a><br>
  <a href="../mentions-legales.html">Mentions légales</a> · <a href="../confidentialite.html">Confidentialité</a> · <a href="#" class="js-cookies" hidden>Gérer les cookies</a> · © 2026 Réseau Artisans France
</div></footer>

<div class="stickycta">
  <a class="btn btn-call" href="#devis">{p['sticky']}</a>
  <a class="btn btn-navy js-call" href="tel:{TEL}" aria-label="Appeler"><svg class="ic"><use href="#i-phone"/></svg></a>
</div>
<script src="../assets/devis.js" defer></script>
<script>document.querySelectorAll(".cmp input").forEach(function(r){{r.addEventListener("input",function(){{r.parentNode.style.setProperty("--pos",r.value+"%");}});}});</script>
<script src="../assets/suivi-appels.js" defer></script>
</body>
</html>
"""


SDB = dict(
 slug="salle-de-bain",
 title="Rénovation de salle de bain – Drôme, Ardèche, Grenoble | Réseau Artisans France",
 desc="Rénovation complète de salle de bain et WC, remplacement de baignoire par une douche. Un seul artisan du début à la fin. Visite et devis gratuits à domicile.",
 eyebrow="Valence · Drôme · Ardèche · Grenoble",
 h1="Il est temps de refaire <em>votre salle de bain.</em>",
 tagline="Un seul artisan local, de A à Z.",
 lead="Baignoire remplacée par une douche, salle de bain complète, WC : <b>on s'occupe de tout</b>, plomberie, carrelage et finitions.",
 ticks=["Prix juste : devis gratuit, détaillé, sans surprise", "Intervention professionnelle, un seul artisan de A à Z", "Délais respectés : la date est fixée avec vous", "Entreprise locale, plus de 10 ans d\'expérience"],
 before="ba3-avant.jpg", before_alt="Salle de bain des années 80 avec baignoire carrelée et lavabo colonne", after="ba3-apres.jpg", after_alt="La même salle de bain refaite avec une douche à l'italienne et un meuble vasque",
 illus="Images d'illustration : exemples de transformation.",
 gal_title="Avant / après : ce qu'on peut faire chez vous", gal_sub="Baignoire remplacée par une douche, douche plain-pied sécurisée, salle de bain complète.",
 gallery=[("ba2-avant.jpg", "ba2-apres.jpg", "Salle de bain rose avec baignoire", "Douche plain-pied avec siège et barre d'appui"),
          ("ba4-avant.jpg", "ba4-apres.jpg", "Petite salle de bain avec baignoire et WC", "Douche vitrée, WC suspendu et meuble bois"),
          ("ba1-avant.jpg", "ba1-apres.jpg", "Salle de bain avec baignoire et rideau", "Douche à l'italienne et meuble chêne")],
 form_title="Demandez votre devis gratuit", form_hint="2 minutes. Un artisan local vous rappelle pour fixer la visite gratuite.",
 projets=["Salle de bain complète", "Baignoire → douche", "Rénovation WC", "Autre projet"],
 delais=["Dès que possible", "Dans 1 à 3 mois", "Plus tard", "Je me renseigne"],
 placeholder="Ex. : salle de bain de 6 m², remplacer la baignoire par une douche à l'italienne…",
 cta="Demander mon devis gratuit", sticky="Mon devis gratuit",
 steps_sub="Simple et sans engagement : vous savez exactement ce qui sera fait et combien ça coûte avant de signer.",
 steps=[("Vous décrivez votre projet", "Par le formulaire ou par téléphone, en 2 minutes."), ("Visite gratuite chez vous", "On prend les mesures, on regarde l'existant et on discute de vos envies."), ("Devis écrit et détaillé", "Tout est chiffré poste par poste. Vous prenez le temps de décider."), ("Les travaux", "Un seul artisan coordonne tout, du démontage aux finitions.")],
 list_title="On s'occupe de tout", list_sub="Vous n'avez pas à courir après plusieurs entreprises.",
 list=["Dépose de l'ancienne salle de bain et évacuation des gravats", "Plomberie : arrivées d'eau et évacuations", "Remplacement de baignoire par une douche plain-pied", "Douche à l'italienne, receveur extra-plat, paroi vitrée", "Carrelage sol et murs, faïence", "Meuble vasque, miroir, sèche-serviettes", "WC suspendu ou classique", "Finitions et nettoyage du chantier"],
 photos_title="Des idées pour votre future salle de bain", photos=[("sdb-douche.jpg", "Douche à l'italienne avec paroi vitrée"), ("sdb-double.jpg", "Salle de bain avec double vasque"), ("sdb-pose.jpg", "Pose de carrelage mural")],
 faq=[("Combien coûte la rénovation d'une salle de bain ?", "Tout dépend de la surface, de l'état de l'existant et des équipements choisis. C'est pour ça qu'on se déplace : après la visite gratuite, vous recevez un devis écrit et détaillé, sans engagement."),
      ("Combien de temps durent les travaux ?", "Un remplacement de baignoire par une douche se fait généralement en quelques jours, une salle de bain complète demande plus de temps. La durée est indiquée sur le devis."),
      ("Est-ce que je dois acheter les équipements moi-même ?", "Non. On peut fournir et poser l'ensemble. Si vous avez déjà choisi certains équipements, on en discute à la visite."),
      ("La visite et le devis sont-ils vraiment gratuits ?", "Oui, sans engagement."),
      ("Intervenez-vous dans ma commune ?", "Nous intervenons dans la Drôme, le nord de l'Ardèche et l'agglomération de Grenoble. Indiquez votre commune dans le formulaire : on vous dit tout de suite si c'est possible.")],
 final_title="Il est temps de refaire votre salle de bain.", final_sub="Décrivez votre projet en 2 minutes : un artisan vous rappelle pour fixer la visite gratuite.",
)

CH = dict(
 slug="chaudiere",
 title="Remplacement de chaudière gaz – Drôme, Ardèche, Grenoble | Réseau Artisans France",
 desc="Chaudière en panne ou trop ancienne ? Remplacement de chaudière gaz : dépose, pose et mise en service. Visite et devis gratuits.",
 eyebrow="Chaudière gaz · Drôme · Ardèche · Isère",
 h1="Chaudière en panne ou trop vieille ? <em>On la remplace.</em>",
 lead="Dépannage, remplacement de chaudière gaz, entretien : <b>un chauffagiste près de chez vous</b> vient voir, vous explique et vous donne un devis clair.",
 ticks=["Prix juste : devis gratuit, détaillé, sans surprise", "Intervention professionnelle et propre", "Dépose, pose et mise en service comprises", "Chauffagistes locaux, plus de 10 ans d\'expérience"],
 before="ch-avant.jpg", before_alt="Ancienne chaudière gaz murale", after="ch-apres.jpg", after_alt="Chaudière gaz neuve installée au même endroit", illus="Photos d'illustration.",
 form_title="Votre devis chaudière", form_hint="2 minutes. Un chauffagiste vous rappelle rapidement.",
 projets=["Remplacer ma chaudière", "Chaudière en panne", "Entretien annuel", "Autre demande"],
 delais=["Urgent", "Dans le mois", "Avant l'hiver prochain", "Je me renseigne"],
 placeholder="Ex. : chaudière gaz de 2006, plus d'eau chaude depuis ce matin…",
 cta="Recevoir mon devis gratuit", sticky="Mon devis gratuit",
 steps_sub="Vous savez ce qui sera fait et combien ça coûte avant de vous engager.",
 steps=[("Vous nous contactez", "Formulaire ou téléphone : décrivez votre chaudière et le problème."), ("Diagnostic sur place", "Le chauffagiste regarde l'installation et vous conseille : réparer ou remplacer."), ("Devis clair", "Matériel, dépose, pose et mise en service : tout est détaillé."), ("Installation", "Ancienne chaudière retirée, nouvelle posée et mise en route.")],
 list_title="Ce que nous faisons", list_sub="Pour les chaudières gaz murales des maisons et appartements.",
 list=["Diagnostic de panne", "Remplacement de chaudière gaz", "Dépose et évacuation de l'ancienne chaudière", "Raccordements et mise en service", "Entretien annuel de chaudière", "Conseils pour bien régler votre chauffage"],
 photos_title="Votre chauffage entre de bonnes mains", photos=[("ch-tech.jpg", "Chauffagiste contrôlant une chaudière"), ("ch-apres.jpg", "Chaudière gaz neuve"), ("ch-chaud.jpg", "Salon chauffé en hiver")],
 faq=[("Faut-il réparer ou remplacer ma chaudière ?", "Ça dépend de son âge, de la panne et du coût des pièces. Le chauffagiste vous donne son avis honnête après le diagnostic."),
      ("Combien coûte le remplacement d'une chaudière ?", "Le prix dépend du modèle et de votre installation. Après la visite, vous recevez un devis écrit qui comprend le matériel, la pose et la mise en service."),
      ("Combien de temps dure le remplacement ?", "En général une journée pour un remplacement à l'identique. Le délai d'intervention vous est donné au téléphone."),
      ("Proposez-vous des aides de l'État ?", "Nous ne montons pas de dossiers d'aides (MaPrimeRénov', CEE). Nous vous proposons un devis clair pour une chaudière gaz performante."),
      ("Faites-vous l'entretien annuel ?", "Oui. L'entretien de la chaudière gaz est obligatoire chaque année et prolonge sa durée de vie.")],
 final_title="Ne passez pas l'hiver avec une chaudière fatiguée", final_sub="Décrivez votre situation en 2 minutes : un chauffagiste vous rappelle.",
)

if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    for p in (SDB, CH):
        os.makedirs(os.path.join(here, p["slug"]), exist_ok=True)
        open(os.path.join(here, p["slug"], "index.html"), "w").write(page(p))
        print(p["slug"])

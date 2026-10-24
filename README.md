# Réseau Artisans France — landing « Plombier urgence Valence »

Site statique (HTML/CSS, aucun build) servant de page d'atterrissage aux campagnes Google Ads Search.

## Fichiers
- `index.html` : landing principale
- `mentions-legales.html`, `confidentialite.html` : pages légales
- `assets/` : logos, favicon, photos d'interventions

## Ville dynamique
Le nom de la ville dans le titre (h1, FAQ, `<title>`) s'adapte à l'URL, uniquement pour les communes desservies (liste fermée dans le script en bas de `index.html`). Sinon, « Valence » s'affiche.

- `?ville=<slug>` : lien forcé, ex. `?ville=guilherand-granges`
- `?loc=<id Google>` : rempli automatiquement par Google Ads avec le suffixe d'URL finale `loc={loc_physical_ms}`

Communes : valence, bourg-les-valence, portes-les-valence, guilherand-granges, saint-peray, chabeuil, beaumont-les-valence, etoile-sur-rhone, montelier, malissard, saint-marcel-les-valence, cornas, soyons.

## Mise en ligne
Hébergement statique au choix (GitHub Pages, Netlify, Cloudflare Pages). Le domaine `reseauartisansfrance.com` est chez Squarespace Domains : faire pointer le DNS vers l'hébergeur choisi.

## À compléter
- Mentions légales : hébergeur et médiateur de la consommation.

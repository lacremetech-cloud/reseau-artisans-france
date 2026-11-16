"""Données structurées communes à toutes les pages : FAQ (FAQPage) et fil d'Ariane (BreadcrumbList).
Les questions sont lues directement dans les <details> de la page : ce que Google et les IA lisent
dans le balisage est exactement ce que le visiteur voit.
Idempotent : les blocs marqués data-seo sont supprimés puis recréés à chaque passage."""
import html as H
import json, re

SITE = "https://reseauartisansfrance.com"


def _txt(s):
    s = re.sub(r"<[^>]+>", "", s)
    return re.sub(r"\s+", " ", H.unescape(s)).strip()


def faq_items(page):
    out = []
    for q, a in re.findall(r"<details><summary>(.*?)</summary><p>(.*?)</p></details>", page, flags=re.S):
        q, a = _txt(q), _txt(a)
        if q and a and q not in (x[0] for x in out):
            out.append((q, a))
    return out


def enrich(page, url, crumbs):
    """crumbs : liste de (nom, url) après l'accueil, ex. [("Plombier à Valence", url)]."""
    page = re.sub(r'<script type="application/ld\+json" data-seo="[^"]*">.*?</script>\n', "", page, flags=re.S)
    blocs = []
    faq = faq_items(page)
    if faq:
        blocs.append(("faq", {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}))
    if crumbs:
        items = [("Accueil", SITE + "/")] + crumbs
        blocs.append(("ariane", {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(items)]}))
    tags = "".join(f'<script type="application/ld+json" data-seo="{k}">{json.dumps(d, ensure_ascii=False)}</script>\n' for k, d in blocs)
    return page.replace("</head>", tags + "</head>", 1)

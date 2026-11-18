// Prospection B2B (syndics, agences…) : séquence de 3 e-mails envoyés par Make depuis contact@.
// Base : Neon, tables prospects et prospect_events.
//  GET  ?a=o&id=…            pixel d'ouverture (gif 1x1)
//  GET  ?a=c&id=…            clic vers la page /pros/ (puis redirection)
//  GET  ?a=stop&id=…         désinscription (page de confirmation)
//  POST ?a=due&n=25          (x-ingest-key) e-mails à envoyer maintenant, déjà rédigés
//  POST ?a=sent              (x-ingest-key) {id, step, thread_id, message_id} après envoi
//  POST ?a=reply             (x-ingest-key) {from, snippet} quand un prospect répond
//  POST ?a=bounce            (x-ingest-key) {email} adresse en erreur
//  GET  ?a=stats             (x-ingest-key) compteurs pour le bilan
import { neon } from '@neondatabase/serverless';
import crypto from 'crypto';

const sql = neon(process.env.DATABASE_URL);
const INGEST_KEY = process.env.INGEST_KEY || '';
const BASE = 'https://reseauartisansfrance.com';
const TEL = '06 23 83 20 29';
const SIGNATAIRE = process.env.PROSPECT_SIGNATAIRE || "L'équipe Réseau Artisans France";
const DELAIS = { 1: 4, 2: 5 }; // jours avant la relance suivante
const GIF = Buffer.from('R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7', 'base64');
const UUID = /^[0-9a-f-]{36}$/i;

const safeEq = (a, b) => a && b && a.length === b.length && crypto.timingSafeEqual(Buffer.from(a), Buffer.from(b));
const esc = (s) => String(s || '').replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
function json(res, status, data) {
  res.status(status).setHeader('Content-Type', 'application/json');
  res.setHeader('Cache-Control', 'no-store');
  res.end(JSON.stringify(data));
}
async function readBody(req) {
  if (req.body && typeof req.body === 'object') return req.body;
  if (typeof req.body === 'string') { try { return JSON.parse(req.body); } catch { return Object.fromEntries(new URLSearchParams(req.body)); } }
  const chunks = [];
  for await (const c of req) chunks.push(c);
  const raw = Buffer.concat(chunks).toString();
  try { return JSON.parse(raw || '{}'); } catch { return Object.fromEntries(new URLSearchParams(raw)); }
}
const ev = (id, action, detail = null) => sql`insert into prospect_events(prospect_id, action, detail) values (${id}, ${action}, ${detail})`;

// ---------- textes ----------
const CIBLE = {
  syndic: { qui: 'vos copropriétés et logements en gestion', lieux: 'vos immeubles' },
  agence: { qui: 'les logements que vous gérez', lieux: 'vos logements en gestion' },
  hotel: { qui: 'votre établissement', lieux: 'votre établissement' },
};
function contenu(p, step) {
  const c = CIBLE[p.segment] || CIBLE.syndic;
  const ville = p.ville ? p.ville.toLowerCase().replace(/(^|[\s-])(\p{L})/gu, (m) => m.toUpperCase()).replace(/-(Sur|Les|Lès|De|Du|La|Le|En)-/g, (m) => m.toLowerCase()) : '';
  const aVille = ville ? ` à ${ville}` : '';
  const lien = `${BASE}/api/prospect?a=c&id=${p.id}`;
  let sujet, paras;
  if (step === 1) {
    sujet = `Plombier pour ${c.lieux}${aVille}`;
    paras = [
      'Bonjour,',
      `Nous sommes Réseau Artisans France, plombiers chauffagistes installés en Drôme-Ardèche. Nous intervenons à Valence, Grenoble, Saint-Étienne et alentours, et nous aimerions faire partie de vos prestataires pour les dépannages de ${c.qui}.`,
      'Concrètement :\n– on décroche 24h/24 et on intervient rapidement, avec un camion équipé ;\n– on prend rendez-vous directement avec l\'occupant ;\n– vous recevez un devis avant toute intervention ;\n– puis les photos avant / après et une facture détaillée.',
      `Tout est présenté ici : ${lien}`,
      'Le plus simple pour nous juger : confiez-nous votre prochaine fuite ou votre prochain WC bouché.',
    ];
  } else if (step === 2) {
    sujet = `Re: Plombier pour ${c.lieux}${aVille}`;
    paras = [
      'Bonjour,',
      `Je me permets de revenir vers vous : avez-vous déjà un plombier attitré pour ${c.lieux}${aVille} ?`,
      'Si oui, nous pouvons être votre solution de secours le soir et le week-end, quand il n\'est pas disponible.',
      'Un simple « oui » en réponse à ce message et je vous envoie notre Kbis, notre attestation d\'assurance et notre RIB pour le référencement.',
    ];
  } else {
    sujet = `Re: Plombier pour ${c.lieux}${aVille}`;
    paras = [
      'Bonjour,',
      'Dernier message de ma part, promis.',
      `Le jour où une fuite ou un dégât des eaux tombe un vendredi soir, notre numéro est le ${TEL} : on décroche 24h/24.`,
      'Bonne continuation,',
    ];
  }
  const stop = `${BASE}/api/prospect?a=stop&id=${p.id}`;
  const signature = `${SIGNATAIRE}\nPlomberie · chauffage · dépannage 24h/24\n${TEL} · reseauartisansfrance.com`;
  const pied = `Vous ne souhaitez plus recevoir nos messages ? ${stop}`;
  const text = paras.join('\n\n') + '\n\n' + signature + '\n\n' + pied;
  const html =
    '<div style="font-family:Arial,sans-serif;font-size:14px;line-height:1.5;color:#222">' +
    paras.map((t) => '<p>' + esc(t).replace(/\n/g, '<br>').replace(esc(lien), `<a href="${lien}">${BASE.replace('https://', '')}/pros</a>`) + '</p>').join('') +
    `<p>${esc(signature).replace(/\n/g, '<br>')}</p>` +
    `<p style="font-size:11px;color:#888">Vous ne souhaitez plus recevoir nos messages ? <a href="${stop}" style="color:#888">Cliquez ici</a>.</p>` +
    `<img src="${BASE}/api/prospect?a=o&id=${p.id}" width="1" height="1" alt="" style="display:block">` +
    '</div>';
  return { sujet, text, html };
}

// ---------- handler ----------
export default async function handler(req, res) {
  const a = String(req.query.a || '');
  const id = String(req.query.id || '');
  try {
    if (a === 'o') {
      if (UUID.test(id)) {
        const r = await sql`update prospects set opens = opens + 1, first_open_at = coalesce(first_open_at, now()), last_open_at = now() where id = ${id} returning id`;
        if (r.length) await ev(id, 'ouverture');
      }
      res.setHeader('Content-Type', 'image/gif');
      res.setHeader('Cache-Control', 'no-store, max-age=0');
      return res.status(200).end(GIF);
    }
    if (a === 'c') {
      if (UUID.test(id)) {
        const r = await sql`update prospects set clicks = clicks + 1 where id = ${id} returning segment`;
        if (r.length) await ev(id, 'clic');
      }
      res.setHeader('Location', `${BASE}/pros/?utm_source=email&utm_medium=prospection&utm_campaign=b2b`);
      return res.status(302).end();
    }
    if (a === 'stop') {
      if (UUID.test(id)) {
        const r = await sql`update prospects set status = 'stop', stopped_at = now() where id = ${id} and status <> 'stop' returning id`;
        if (r.length) await ev(id, 'desinscription');
      }
      res.setHeader('Content-Type', 'text/html; charset=utf-8');
      return res.status(200).end('<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Désinscription</title><body style="font-family:Arial,sans-serif;max-width:520px;margin:60px auto;padding:0 16px;color:#222"><h1 style="font-size:22px">C\'est noté.</h1><p>Vous ne recevrez plus de messages de Réseau Artisans France. Désolés pour le dérangement.</p></body>');
    }

    if (!safeEq(String(req.headers['x-ingest-key'] || ''), INGEST_KEY)) return json(res, 401, { error: 'clé' });

    if (a === 'due') {
      const n = Math.min(Math.max(parseInt(req.query.n || '25', 10) || 25, 1), 60);
      const rows = await sql`select * from prospects where status = 'actif' and step < 3 and next_at <= now()
                             order by step desc, created_at limit ${n}`;
      return json(res, 200, { items: rows.map((p) => { const step = p.step + 1; const m = contenu(p, step); return { id: p.id, to: p.email, step, thread_id: p.thread_id, message_id: p.message_id, subject: m.sujet, text: m.text, html: m.html }; }) });
    }
    if (a === 'sent') {
      const b = await readBody(req);
      if (!UUID.test(String(b.id || ''))) return json(res, 400, { error: 'id' });
      const step = parseInt(b.step, 10);
      const jours = DELAIS[step];
      const r = await sql`update prospects set step = ${step},
          sent1_at = case when ${step} = 1 then now() else sent1_at end,
          sent2_at = case when ${step} = 2 then now() else sent2_at end,
          sent3_at = case when ${step} = 3 then now() else sent3_at end,
          thread_id = coalesce(${b.thread_id || null}, thread_id),
          message_id = coalesce(message_id, ${b.message_id || null}),
          next_at = case when ${jours || null}::int is null then null else now() + make_interval(days => ${jours || 0}) end,
          status = case when ${step} >= 3 then 'termine' else status end
        where id = ${b.id} and step = ${step - 1} returning id`;
      if (r.length) await ev(b.id, 'envoi', 'étape ' + step);
      return json(res, 200, { ok: r.length > 0 });
    }
    if (a === 'reply' || a === 'bounce') {
      const b = await readBody(req);
      const m = String(b.from || b.email || '').toLowerCase().match(/[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}/);
      if (!m) return json(res, 400, { error: 'email' });
      const r = a === 'reply'
        ? await sql`update prospects set status = 'repondu', replied_at = now(), reply_snippet = ${String(b.snippet || '').slice(0, 500)} where lower(email) = ${m[0]} and status in ('actif','termine') returning id, nom, ville`
        : await sql`update prospects set status = 'bounce' where lower(email) = ${m[0]} returning id, nom, ville`;
      for (const p of r) await ev(p.id, a === 'reply' ? 'reponse' : 'erreur', String(b.snippet || '').slice(0, 300));
      return json(res, 200, { ok: r.length > 0, prospect: r[0] || null });
    }
    if (a === 'stats') {
      const [s] = await sql`select count(*)::int total,
          count(*) filter (where sent1_at is not null)::int contactes,
          count(*) filter (where opens > 0)::int ouverts,
          count(*) filter (where clicks > 0)::int clics,
          count(*) filter (where status = 'repondu')::int reponses,
          count(*) filter (where status = 'stop')::int desinscrits,
          count(*) filter (where status = 'bounce')::int erreurs,
          count(*) filter (where status = 'actif' and step = 0)::int a_contacter
        from prospects`;
      return json(res, 200, s);
    }
    return json(res, 404, { error: 'action' });
  } catch (e) {
    console.error(e);
    return json(res, 500, { error: 'serveur' });
  }
}

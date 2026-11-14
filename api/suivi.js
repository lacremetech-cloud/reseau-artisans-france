// API de l'outil de suivi des leads RAF (reseauartisansfrance.com/suivi)
// Base : Neon Postgres (DATABASE_URL). Accès par code PIN -> jeton signé (SUIVI_SECRET).
// Make envoie les leads et la dépense pub avec l'en-tête x-ingest-key (INGEST_KEY).
import { neon } from '@neondatabase/serverless';
import crypto from 'crypto';

const sql = neon(process.env.DATABASE_URL);
const SECRET = process.env.SUIVI_SECRET || '';
const INGEST_KEY = process.env.INGEST_KEY || '';
const COMMISSION = 0.25;

const STATUTS = ['nouveau', 'relancer', 'rappele', 'devis', 'planifie', 'termine', 'perdu', 'faux'];
const SOURCES = ['lsa', 'google_ads', 'meta', 'site', 'fiche_google', 'bouche_a_oreille', 'autre', 'inconnu'];
const PLATFORMS = ['meta', 'google_ads', 'lsa'];

// ---------- jeton ----------
function sign(payload) {
  const body = Buffer.from(JSON.stringify(payload)).toString('base64url');
  const mac = crypto.createHmac('sha256', SECRET).update(body).digest('base64url');
  return body + '.' + mac;
}
function verify(token) {
  if (!token || !SECRET) return null;
  const [body, mac] = String(token).split('.');
  if (!body || !mac) return null;
  const good = crypto.createHmac('sha256', SECRET).update(body).digest('base64url');
  if (mac.length !== good.length || !crypto.timingSafeEqual(Buffer.from(mac), Buffer.from(good))) return null;
  const p = JSON.parse(Buffer.from(body, 'base64url').toString());
  if (!p.exp || p.exp < Date.now()) return null;
  return p;
}
const safeEq = (a, b) => a && b && a.length === b.length && crypto.timingSafeEqual(Buffer.from(a), Buffer.from(b));

// ---------- utilitaires ----------
const num = (v) => (v === '' || v === null || v === undefined || isNaN(Number(v)) ? null : Math.round(Number(v) * 100) / 100);
const txt = (v, max = 2000) => (v === null || v === undefined ? null : String(v).trim().slice(0, max) || null);
function normPhone(t) {
  if (!t) return null;
  let d = String(t).replace(/[^\d+]/g, '');
  if (d.startsWith('+33')) d = '0' + d.slice(3);
  else if (d.startsWith('0033')) d = '0' + d.slice(4);
  else if (/^33\d{9}$/.test(d)) d = '0' + d.slice(2);
  return d || null;
}
function send(res, status, data) {
  res.status(status).setHeader('Content-Type', 'application/json');
  res.setHeader('Cache-Control', 'no-store');
  res.end(JSON.stringify(data));
}
async function readBody(req) {
  if (req.body && typeof req.body === 'object') return req.body;
  if (typeof req.body === 'string') { try { return JSON.parse(req.body); } catch { return {}; } }
  const chunks = [];
  for await (const c of req) chunks.push(c);
  const raw = Buffer.concat(chunks).toString();
  try { return JSON.parse(raw || '{}'); } catch { return Object.fromEntries(new URLSearchParams(raw)); }
}
async function logEvent(leadId, by, action, detail) {
  await sql`insert into lead_events(lead_id, by_user, action, detail) values (${leadId}, ${by}, ${action}, ${detail})`;
}

// ---------- création / dédoublonnage d'un lead ----------
async function upsertLead(d, by) {
  const tel = normPhone(d.telephone);
  // un identifiant vide côté Make donne « lsa- » ou « fb- » : on l'ignore
  const ext = /^[a-z]+-$/.test(String(d.ext_id || '')) ? null : txt(d.ext_id, 200);
  const source = SOURCES.includes(d.source) ? d.source : 'inconnu';
  const created = d.created_at ? new Date(d.created_at) : new Date();
  if (ext) {
    const ex = await sql`select id from leads where ext_id = ${ext}`;
    if (ex.length) return { id: ex[0].id, duplicate: true };
  }
  if (tel) {
    // même numéro dans les 3 derniers jours et pas clôturé : on rattache au lead existant
    const ex = await sql`select id, source from leads where (telephone = ${tel} or position(${tel} in coalesce(autres_tel, '')) > 0)
      and created_at > ${created}::timestamptz - interval '3 days' and statut not in ('termine','perdu','faux')
      order by created_at desc limit 1`;
    if (ex.length) {
      await logEvent(ex[0].id, by, 'relance', `Nouveau contact (${source}${d.campagne ? ' · ' + d.campagne : ''})${d.message ? ' : ' + txt(d.message, 300) : ''}`);
      if (ex[0].source === 'inconnu' && source !== 'inconnu') await sql`update leads set source = ${source}, campagne = coalesce(campagne, ${txt(d.campagne, 200)}) where id = ${ex[0].id}`;
      return { id: ex[0].id, merged: true };
    }
  }
  const r = await sql`insert into leads (created_at, source, campagne, lead_type, ville, nom, telephone, besoin, message, ext_id, statut, updated_by)
    values (${created}, ${source}, ${txt(d.campagne, 200)}, ${txt(d.lead_type, 50)}, ${txt(d.ville, 120)}, ${txt(d.nom, 160)}, ${tel},
            ${txt(d.besoin, 300)}, ${txt(d.message)}, ${ext}, 'nouveau', ${by}) returning id`;
  await logEvent(r[0].id, by, 'creation', `Lead ${source}${d.campagne ? ' · ' + d.campagne : ''}`);
  return { id: r[0].id, created: true };
}

// ---------- tableau de bord ----------
async function dashboard(from, to) {
  const f = from || '2000-01-01', t = to || '2100-01-01';
  const leads = await sql`select source, statut, count(*)::int n from leads
    where created_at >= ${f}::date and created_at < (${t}::date + 1) group by source, statut`;
  const done = await sql`select l.id, l.termine_at, l.created_at, l.source, l.ville, l.nom, l.besoin, l.montant, l.frais_gasoil, l.frais_materiel, l.frais_autres, l.avis_demande,
      (select count(*)::int from lead_photos p where p.lead_id = l.id) photos
    from leads l where statut = 'termine' and coalesce(termine_at, created_at) >= ${f}::date and coalesce(termine_at, created_at) < (${t}::date + 1)
    order by coalesce(termine_at, created_at)`;
  const spend = await sql`select day, platform, sum(amount)::float amount, bool_or(estimated) est from ad_spend
    where day >= ${f}::date and day <= ${t}::date group by day, platform order by day`;
  return { leads, done, spend, commission_rate: COMMISSION };
}

// ---------- handler ----------
export default async function handler(req, res) {
  try {
    // Photo en GET (pour <img src>)
    if (req.method === 'GET') {
      const u = new URL(req.url, 'http://x');
      const pid = u.searchParams.get('photo');
      if (pid && verify(u.searchParams.get('t'))) {
        const r = await sql`select mime, data from lead_photos where id = ${pid}`;
        if (!r.length) return send(res, 404, { error: 'introuvable' });
        res.status(200).setHeader('Content-Type', r[0].mime);
        res.setHeader('Cache-Control', 'private, max-age=86400');
        return res.end(Buffer.from(r[0].data));
      }
      return send(res, 401, { error: 'non autorisé' });
    }
    if (req.method !== 'POST') return send(res, 405, { error: 'méthode' });
    const b = await readBody(req);
    const action = b.action;

    // ----- entrées Make (clé) -----
    if (action === 'ingest' || action === 'spend') {
      if (!safeEq(String(req.headers['x-ingest-key'] || ''), INGEST_KEY)) return send(res, 401, { error: 'clé' });
      if (action === 'ingest') return send(res, 200, await upsertLead(b, 'auto'));
      const rows = (Array.isArray(b.rows) ? b.rows : [b]).filter((r) => r && r.day && PLATFORMS.includes(r.platform));
      // Un relevé automatique remplace tout ce qui existait pour ce jour et cette plateforme (pas de double compte).
      const seen = new Set();
      for (const r of rows) {
        const k = r.day + '|' + r.platform;
        if (seen.has(k)) continue;
        seen.add(k);
        await sql`delete from ad_spend where day = ${r.day} and platform = ${r.platform}`;
      }
      let n = 0;
      for (const r of rows) {
        if (!r.day || !PLATFORMS.includes(r.platform)) continue;
        await sql`insert into ad_spend(day, platform, campagne, amount, estimated, updated_at)
          values (${r.day}, ${r.platform}, ${txt(r.campagne, 200) || ''}, ${num(r.amount) || 0}, ${!!r.estimated}, now())
          on conflict (day, platform, campagne) do update set amount = ad_spend.amount + excluded.amount, estimated = excluded.estimated, updated_at = now()`;
        n++;
      }
      return send(res, 200, { ok: true, rows: n });
    }

    // ----- connexion -----
    if (action === 'login') {
      const pin = String(b.pin || '').replace(/\D/g, '');
      if (pin.length < 4) return send(res, 400, { error: 'Code incomplet' });
      const r = await sql`select id, name, role from users where active and pin_hash = crypt(${pin}, pin_hash) limit 1`;
      if (!r.length) { await new Promise((ok) => setTimeout(ok, 800)); return send(res, 401, { error: 'Code incorrect' }); }
      const u = r[0];
      return send(res, 200, { token: sign({ id: u.id, name: u.name, role: u.role, exp: Date.now() + 1000 * 60 * 60 * 24 * 90 }), name: u.name, role: u.role });
    }

    const me = verify(b.token);
    if (!me) return send(res, 401, { error: 'Session expirée, reconnecte-toi' });

    switch (action) {
      case 'leads': {
        const rows = await sql`select l.id, l.created_at, l.source, l.campagne, l.lead_type, l.ville, l.nom, l.telephone, l.besoin, l.statut, l.statut_at,
            l.rdv_at, l.relance_at, l.nb_relances, l.montant, l.avis_demande, l.updated_by, left(l.note, 200) note, left(l.message, 200) message, l.autres_tel,
            (select count(*)::int from lead_photos p where p.lead_id = l.id) photos
          from leads l order by l.created_at desc limit 400`;
        return send(res, 200, { leads: rows });
      }
      case 'lead': {
        const r = await sql`select * from leads where id = ${b.id}`;
        if (!r.length) return send(res, 404, { error: 'introuvable' });
        const photos = await sql`select id, created_at, by_user from lead_photos where lead_id = ${b.id} order by created_at`;
        const events = await sql`select at, by_user, action, detail from lead_events where lead_id = ${b.id} order by at desc limit 50`;
        return send(res, 200, { lead: r[0], photos, events });
      }
      case 'create': {
        const out = await upsertLead({ ...b.lead, source: b.lead?.source || 'inconnu' }, me.name);
        return send(res, 200, out);
      }
      case 'update': {
        const cur = await sql`select * from leads where id = ${b.id}`;
        if (!cur.length) return send(res, 404, { error: 'introuvable' });
        const c = cur[0], p = b.patch || {};
        const next = {
          statut: STATUTS.includes(p.statut) ? p.statut : c.statut,
          source: SOURCES.includes(p.source) ? p.source : c.source,
          rdv_at: 'rdv_at' in p ? (p.rdv_at ? new Date(p.rdv_at) : null) : c.rdv_at,
          relance_at: 'relance_at' in p ? (p.relance_at ? new Date(p.relance_at) : null) : c.relance_at,
          montant: 'montant' in p ? num(p.montant) : c.montant,
          frais_gasoil: 'frais_gasoil' in p ? num(p.frais_gasoil) || 0 : c.frais_gasoil,
          frais_materiel: 'frais_materiel' in p ? num(p.frais_materiel) || 0 : c.frais_materiel,
          frais_autres: 'frais_autres' in p ? num(p.frais_autres) || 0 : c.frais_autres,
          frais_detail: 'frais_detail' in p ? txt(p.frais_detail, 500) : c.frais_detail,
          avis_demande: 'avis_demande' in p ? !!p.avis_demande : c.avis_demande,
          note: 'note' in p ? txt(p.note) : c.note,
          ville: 'ville' in p ? txt(p.ville, 120) : c.ville,
          nom: 'nom' in p ? txt(p.nom, 160) : c.nom,
          besoin: 'besoin' in p ? txt(p.besoin, 300) : c.besoin,
          telephone: 'telephone' in p ? normPhone(p.telephone) : c.telephone,
        };
        const statutChange = next.statut !== c.statut;
        // chaque « Pas répondu » compte une tentative d'appel de plus
        const nbRelances = (c.nb_relances || 0) + (p.statut === 'relancer' ? 1 : 0);
        const termineAt = next.statut === 'termine' ? (c.termine_at || new Date()) : null;
        const avisAt = next.avis_demande ? (c.avis_at || new Date()) : null;
        await sql`update leads set statut = ${next.statut}, statut_at = ${statutChange ? new Date() : c.statut_at}, source = ${next.source},
            rdv_at = ${next.rdv_at}, relance_at = ${next.relance_at}, nb_relances = ${nbRelances}, montant = ${next.montant}, frais_gasoil = ${next.frais_gasoil}, frais_materiel = ${next.frais_materiel},
            frais_autres = ${next.frais_autres}, frais_detail = ${next.frais_detail}, avis_demande = ${next.avis_demande}, avis_at = ${avisAt},
            note = ${next.note}, ville = ${next.ville}, nom = ${next.nom}, besoin = ${next.besoin}, telephone = ${next.telephone},
            termine_at = ${termineAt}, updated_at = now(), updated_by = ${me.name} where id = ${b.id}`;
        const changes = [];
        if (p.statut === 'relancer') changes.push('pas répondu, à relancer (tentative ' + nbRelances + ')');
        else if (statutChange) changes.push('état : ' + next.statut);
        if (next.source !== c.source) changes.push('source : ' + next.source);
        if (String(next.montant) !== String(c.montant)) changes.push('montant : ' + (next.montant ?? '—') + ' €');
        if (next.avis_demande !== c.avis_demande) changes.push('avis demandé : ' + (next.avis_demande ? 'oui' : 'non'));
        if (+new Date(next.rdv_at || 0) !== +new Date(c.rdv_at || 0)) changes.push('intervention : ' + (next.rdv_at ? new Date(next.rdv_at).toISOString() : '—'));
        if (changes.length) await logEvent(b.id, me.name, 'modif', changes.join(' · '));
        return send(res, 200, { ok: true });
      }
      case 'photo': {
        const m = /^data:(image\/(?:jpeg|png|webp));base64,(.+)$/.exec(String(b.data || ''));
        if (!m) return send(res, 400, { error: 'image invalide' });
        const buf = Buffer.from(m[2], 'base64');
        if (buf.length > 1_500_000) return send(res, 413, { error: 'photo trop lourde' });
        const r = await sql`insert into lead_photos(lead_id, mime, data, by_user) values (${b.id}, ${m[1]}, ${buf}, ${me.name}) returning id`;
        await logEvent(b.id, me.name, 'photo', 'Photo ajoutée');
        return send(res, 200, { id: r[0].id });
      }
      case 'merge': {
        // Rattache la fiche « from » à la fiche « into » : tout est regroupé dans « into », puis « from » est supprimée.
        if (!b.from || !b.into || b.from === b.into) return send(res, 400, { error: 'fiches invalides' });
        const rows = await sql`select * from leads where id in (${b.from}, ${b.into})`;
        const A = rows.find((r) => r.id === b.from), B = rows.find((r) => r.id === b.into);
        if (!A || !B) return send(res, 404, { error: 'introuvable' });
        const RANK = { faux: 0, perdu: 1, nouveau: 2, relancer: 3, rappele: 4, devis: 5, planifie: 6, termine: 7 };
        const statut = (RANK[A.statut] ?? 0) > (RANK[B.statut] ?? 0) ? A.statut : B.statut;
        const pick = (k) => (B[k] !== null && B[k] !== undefined && B[k] !== '' ? B[k] : A[k]);
        const sum = (k) => (+A[k] || 0) + (+B[k] || 0);
        const tels = new Set([...(B.autres_tel || '').split(/[,\s]+/), ...(A.autres_tel || '').split(/[,\s]+/), A.telephone].filter((t) => t && t !== pick('telephone')));
        const notes = [B.note, A.note].filter(Boolean).join('\n');
        const msgs = [B.message, A.message].filter(Boolean).join('\n');
        const montant = A.montant != null && B.montant != null ? sum('montant') : pick('montant');
        await sql`update leads set
            nom = ${pick('nom')}, telephone = ${pick('telephone')}, autres_tel = ${[...tels].join(', ') || null},
            ville = ${pick('ville')}, besoin = ${pick('besoin')}, campagne = ${pick('campagne')}, lead_type = ${pick('lead_type')},
            source = ${B.source !== 'inconnu' ? B.source : A.source}, ext_id = ${pick('ext_id')},
            created_at = ${new Date(Math.min(+new Date(A.created_at), +new Date(B.created_at)))},
            statut = ${statut}, statut_at = now(), rdv_at = ${pick('rdv_at')}, relance_at = ${pick('relance_at')},
            nb_relances = ${(A.nb_relances || 0) + (B.nb_relances || 0)},
            montant = ${montant}, frais_gasoil = ${sum('frais_gasoil')}, frais_materiel = ${sum('frais_materiel')}, frais_autres = ${sum('frais_autres')},
            frais_detail = ${[B.frais_detail, A.frais_detail].filter(Boolean).join(' · ') || null},
            avis_demande = ${!!(A.avis_demande || B.avis_demande)}, avis_at = ${pick('avis_at')},
            termine_at = ${statut === 'termine' ? pick('termine_at') || new Date() : null},
            note = ${notes || null}, message = ${msgs || null}, updated_at = now(), updated_by = ${me.name}
          where id = ${B.id}`;
        await sql`update lead_photos set lead_id = ${B.id} where lead_id = ${A.id}`;
        await sql`update lead_events set lead_id = ${B.id} where lead_id = ${A.id}`;
        await sql`delete from leads where id = ${A.id}`;
        await logEvent(B.id, me.name, 'fusion', `Fiche rattachée : ${A.nom || A.telephone || A.ville || 'sans nom'}${A.montant != null ? ' (' + A.montant + ' €)' : ''}`);
        return send(res, 200, { ok: true, id: B.id });
      }
      case 'photo_delete': {
        await sql`delete from lead_photos where id = ${b.photo_id}`;
        return send(res, 200, { ok: true });
      }
      case 'dashboard':
        return send(res, 200, await dashboard(b.from, b.to));
      case 'spend_set': {
        if (!PLATFORMS.includes(b.platform) || !b.day) return send(res, 400, { error: 'données' });
        // La saisie manuelle remplace le montant du jour pour cette plateforme.
        await sql`delete from ad_spend where day = ${b.day} and platform = ${b.platform}`;
        await sql`insert into ad_spend(day, platform, campagne, amount, estimated, updated_at)
          values (${b.day}, ${b.platform}, 'saisie', ${num(b.amount) || 0}, false, now())`;
        return send(res, 200, { ok: true });
      }
      default:
        return send(res, 400, { error: 'action inconnue' });
    }
  } catch (e) {
    console.error(e);
    return send(res, 500, { error: 'Erreur serveur' });
  }
}

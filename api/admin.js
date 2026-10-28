// api/admin.js — Dashboard Dusun Kita
// Endpoint serverless (Vercel). Baca/tulis scripts/state.json + antrian.json,
// trigger scrape (IG) + apply (generate data.js + push).
//
// Mode (?m=):
//   status  -> statistik + daftar antrian + warga
//   set     -> ubah status antrian (?name=&status=approved|rejected|pending)
//   scrape  -> jalankan otomasi.py --antrian
//   apply   -> jalankan otomasi.py --apply
//
// Keamanan: pakai ADMIN_KEY (env) biar tidak sembarang orang akses.
import { execSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';

const ROOT = process.cwd();
const STATE = path.join(ROOT, 'scripts', 'state.json');
const ANTRIAN = path.join(ROOT, 'scripts', 'antrian.json');

function jread(p, fallback) {
  try { return JSON.parse(fs.readFileSync(p, 'utf8')); }
  catch (e) { return fallback; }
}
function jwrite(p, data) {
  fs.mkdirSync(path.dirname(p), { recursive: true });
  fs.writeFileSync(p, JSON.stringify(data, null, 2));
}

function ok(res, data) { res.status(200).json({ ok: true, ...data }); }
function err(res, msg) { res.status(400).json({ ok: false, error: msg }); }

export default async function handler(req, res) {
  const key = String(process.env.ADMIN_KEY || '');
  const m = String(req.query.m || req.query.mode || 'status');

  // proteksi: kalau ADMIN_KEY diset, wajib cocok (via ?key= atau header x-admin-key)
  if (key && req.query.key !== key && req.headers['x-admin-key'] !== key) {
    return res.status(401).json({ ok: false, error: 'Unauthorized' });
  }

  if (m === 'status') {
    const s = jread(STATE, {});
    const antrian = jread(ANTRIAN, []);
    const warga = s.residents || [];
    const pending = antrian.filter(a => a.status === 'pending').length;
    return ok(res, {
      day: s.day || 1,
      warga: warga.length,
      antrian: pending,
      followers: s.followers || 0,
      target: s.target || 1000,
      updated: s.updated || '-',
      web: (process.env.WEB_URL || 'https://trustdigitalteam.github.io/dusunkita/'),
      antrianList: antrian,
      wargaList: warga.map(r => ({ name: r.name, nick: r.nick, day: r.day, roof: r.roof, wall: r.wall })),
    });
  }

  if (m === 'set') {
    const name = String(req.query.name || '').toLowerCase();
    const status = ['approved', 'rejected', 'pending'].includes(req.query.status) ? req.query.status : null;
    if (!name || !status) return err(res, 'Param name/status tidak valid');
    const antrian = jread(ANTRIAN, []);
    let found = false;
    for (const a of antrian) {
      if ((a.name || '').toLowerCase() === name) { a.status = status; found = true; }
    }
    if (!found) return err(res, 'Antrian tidak ditemukan');
    jwrite(ANTRIAN, antrian);
    return ok(res, { msg: 'Status diperbarui' });
  }

  if (m === 'scrape' || m === 'apply') {
    const flag = m === 'scrape' ? '--antrian' : '--apply';
    const script = path.join(ROOT, 'scripts', 'otomasi.py');
    try {
      const out = execSync(`python3 ${script} ${flag}`, {
        env: { ...process.env },
        timeout: 120000,
        cwd: ROOT,
      }).toString();
      return ok(res, { msg: out.slice(-500) });
    } catch (e) {
      const so = (e.stdout || '').toString();
      const se = (e.stderr || '').toString();
      return err(res, (so || se).slice(-500));
    }
  }

  return err(res, 'Mode tidak dikenal');
}

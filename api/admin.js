// api/admin.js — Dashboard Dusun Kita (Redis-backed)
// Baca state dari Upstash Redis (bukan file lokal).
// Scrape/apply = trigger ke VPS via webhook (bukan execSync).
//
// Mode (?m=):
//   status  -> summary + antrian + warga dari Redis
//   set     -> ubah status antrian (?name=&status=approved|rejected|pending)
//   scrape  -> trigger VPS webhook untuk jalankan otomasi.py --antrian
//   apply   -> trigger VPS webhook untuk jalankan otomasi.py --apply
//
// Keamanan: ADMIN_KEY wajib cocok (?key= atau header x-admin-key).
import { execSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';

const KV_URL = String(process.env.KV_REST_API_URL || '').replace(/\/$/, '');
const KV_TOKEN = String(process.env.KV_REST_API_TOKEN || '');
const ADMIN_KEY = String(process.env.ADMIN_KEY || '');
const VPS_WEBHOOK = String(process.env.VPS_WEBHOOK_URL || ''); // opsional: URL webhook VPS untuk trigger scrape/apply

function jparse(s) { try { return s ? JSON.parse(s) : null } catch (e) { return null } }

async function kv(cmd) {
  const r = await fetch(KV_URL, {
    method: 'POST',
    headers: { Authorization: 'Bearer ' + KV_TOKEN, 'Content-Type': 'application/json' },
    body: JSON.stringify(cmd),
  });
  const j = await r.json().catch(() => ({}));
  if (!r.ok || j.error) throw new Error('db: ' + (j.error || r.status));
  return j.result;
}

async function kvMany(cmds) {
  const r = await fetch(KV_URL + '/pipeline', {
    method: 'POST',
    headers: { Authorization: 'Bearer ' + KV_TOKEN, 'Content-Type': 'application/json' },
    body: JSON.stringify(cmds),
  });
  const j = await r.json().catch(() => []);
  if (!r.ok) throw new Error('db: ' + r.status);
  return j.map(x => x && x.result);
}

function ok(res, data) { res.status(200).json({ ok: true, ...data }); }
function err(res, msg) { res.status(400).json({ ok: false, error: msg }); }

export default async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');

  // proteksi: ADMIN_KEY wajib cocok
  if (ADMIN_KEY && req.query.key !== ADMIN_KEY && req.headers['x-admin-key'] !== ADMIN_KEY) {
    return res.status(401).json({ ok: false, error: 'Unauthorized' });
  }

  if (!KV_URL || !KV_TOKEN) {
    return res.status(500).json({ ok: false, error: 'Database belum tersambung' });
  }

  const m = String(req.query.m || req.query.mode || 'status');

  // STATUS: baca summary + antrian + warga dari Redis
  if (m === 'status') {
    try {
      const [sumRaw, antrianRaw, wargaRaw] = await kvMany([
        ['GET', 'dusun:summary'],
        ['GET', 'dusun:antrian'],
        ['GET', 'dusun:warga'],
      ]);
      const summary = jparse(sumRaw) || { day: 1, warga: 0, buildings: 0, followers: 0, target: 1000, updated: '-' };
      const antrian = jparse(antrianRaw) || [];
      const warga = jparse(wargaRaw) || [];
      const pending = antrian.filter(a => a.status === 'pending').length;
      return ok(res, {
        day: summary.day,
        warga: summary.warga,
        buildings: summary.buildings || 0,
        antrian: pending,
        followers: summary.followers,
        target: summary.target,
        updated: summary.updated,
        web: 'https://dusunkita.vercel.app/',
        antrianList: antrian,
        wargaList: warga,
      });
    } catch (e) {
      // fallback: kalau Redis kosong (belum ada sync), return default
      return ok(res, {
        day: 1, warga: 0, buildings: 0, antrian: 0,
        followers: 0, target: 1000, updated: '-',
        web: 'https://dusunkita.vercel.app/',
        antrianList: [], wargaList: [],
        note: 'Redis belum di-sync. Jalankan scrape pertama kali di VPS.',
      });
    }
  }

  // SET: ubah status antrian di Redis
  if (m === 'set') {
    const name = String(req.query.name || '').toLowerCase();
    const status = ['approved', 'rejected', 'pending'].includes(req.query.status) ? req.query.status : null;
    if (!name || !status) return err(res, 'Param name/status tidak valid');
    try {
      const antrianRaw = await kv(['GET', 'dusun:antrian']);
      const antrian = jparse(antrianRaw) || [];
      let found = false;
      for (const a of antrian) {
        if ((a.name || '').toLowerCase() === name) { a.status = status; found = true; }
      }
      if (!found) return err(res, 'Antrian tidak ditemukan');
      await kv(['SET', 'dusun:antrian', JSON.stringify(antrian)]);
      return ok(res, { msg: 'Status diperbarui' });
    } catch (e) {
      return err(res, 'Gagal baca/tulis Redis: ' + String(e.message || e).slice(0, 100));
    }
  }

  // SCRAPE / APPLY: trigger VPS webhook (bukan execSync)
  if (m === 'scrape' || m === 'apply') {
    if (!VPS_WEBHOOK) {
      return err(res, 'Scrape/apply hanya bisa dijalankan dari VPS (cron Hermes 19:30/19:40 WIB). Dashboard ini read-only.');
    }
    try {
      const flag = m === 'scrape' ? 'antrian' : 'apply';
      const r = await fetch(VPS_WEBHOOK + '?mode=' + flag, {
        method: 'POST',
        headers: { 'x-admin-key': ADMIN_KEY },
        timeout: 120000,
      });
      const text = await r.text();
      return ok(res, { msg: text.slice(-500) });
    } catch (e) {
      return err(res, 'Gagal trigger VPS: ' + String(e.message || e).slice(0, 100));
    }
  }

  return err(res, 'Mode tidak dikenal');
}

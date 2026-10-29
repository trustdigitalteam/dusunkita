// api/video.js — Video pipeline endpoint (render trigger + status)
//
// Mode (?m=):
//   pipeline -> daftar step pipeline + status terakhir
//   trigger  -> trigger render via VPS webhook (?ep=1)
//   status   -> status render terakhir dari Redis
//
// Keamanan: ADMIN_KEY wajib cocok.
import fs from 'node:fs';

const KV_URL = String(process.env.KV_REST_API_URL || '').replace(/\/$/, '');
const KV_TOKEN = String(process.env.KV_REST_API_TOKEN || '');
const ADMIN_KEY = String(process.env.ADMIN_KEY || '');
const VPS_WEBHOOK = String(process.env.VPS_WEBHOOK_URL || '');

function jparse(s) { try { return s ? JSON.parse(s) : null } catch { return null } }

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

function ok(res, data) { res.status(200).json({ ok: true, ...data }); }
function err(res, msg) { res.status(400).json({ ok: false, error: msg }); }

const PIPELINE_STEPS = [
  { id: 'state', label: 'State Dusun', desc: 'BACA state.json (hari, warga, bangunan, goal)' },
  { id: 'screenshot', label: 'Screenshot Peta', desc: 'Playwright capture peta dusun (peta-only, 9:16)' },
  { id: 'brief', label: 'Brief + Naskah', desc: 'Generate shot list + overlay + VO naskah (docs/episodes/EP-NNN.md)' },
  { id: 'tts', label: 'Voiceover (Gemini)', desc: 'TTS id-ID dari naskah brief → 3 WAV (per shot)' },
  { id: 'render', label: 'Remotion Render', desc: '3 shot × 5 detik = 15 detik video 1080×1920 H.264' },
  { id: 'mix', label: 'Mix VO + BGM', desc: 'Voiceover + ambience BGM fade in/out' },
  { id: 'push', label: 'Push → Vercel', desc: 'git commit + push → deploy auto-serve /videos/EP-NNN.mp4' },
];

export default async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');

  if (ADMIN_KEY && req.query.key !== ADMIN_KEY && req.headers['x-admin-key'] !== ADMIN_KEY) {
    return res.status(401).json({ ok: false, error: 'Unauthorized' });
  }

  const m = String(req.query.m || 'pipeline');

  // PIPELINE: tampil semua step + status terakhir dari Redis
  if (m === 'pipeline') {
    let renderStatus = null;
    try {
      const raw = await kv(['GET', 'dusun:video-status']);
      renderStatus = jparse(raw);
    } catch { renderStatus = null; }

    const steps = PIPELINE_STEPS.map(s => ({
      ...s,
      status: renderStatus?.[s.id] || 'idle',
    }));

    return ok(res, {
      steps,
      lastRender: renderStatus,
      ep: renderStatus?.ep || null,
      videoUrl: renderStatus?.ok ? `https://dusunkita.my.id/videos/EP-${String(renderStatus.ep).padStart(3, '0')}-final.mp4` : null,
    });
  }

  // TRIGGER: jalankan render via VPS webhook
  if (m === 'trigger') {
    if (!VPS_WEBHOOK) {
      return err(res, 'VPS_WEBHOOK_URL belum dikonfigurasi. Set di Vercel env: VPS_WEBHOOK_URL=https://dusunkita.my.id/webhook/render');
    }
    const ep = parseInt(req.query.ep || '1');
    try {
      // set status rendering di Redis
      const now = new Date().toISOString().slice(0, 16).replace('T', ' ');
      const status = { ep, started: now, state: 'rendering', steps: {} };
      PIPELINE_STEPS.forEach(s => status.steps[s.id] = s.id === 'state' ? 'running' : 'idle');
      await kv(['SET', 'dusun:video-status', JSON.stringify(status)]);

      // trigger VPS
      const r = await fetch(VPS_WEBHOOK + '?ep=' + ep, {
        method: 'POST',
        headers: { 'x-admin-key': ADMIN_KEY },
      });
      const text = await r.text();
      return ok(res, { msg: 'Render #' + ep + ' ditrigger. ' + text.slice(0, 200) });
    } catch (e) {
      return err(res, 'Gagal trigger: ' + String(e.message || e).slice(0, 200));
    }
  }

  // STATUS: status render terakhir
  if (m === 'status') {
    try {
      const raw = await kv(['GET', 'dusun:video-status']);
      const s = jparse(raw);
      return ok(res, { status: s || 'belum pernah render' });
    } catch {
      return ok(res, { status: 'belum pernah render' });
    }
  }

  return err(res, 'Mode tidak dikenal: ' + m);
}

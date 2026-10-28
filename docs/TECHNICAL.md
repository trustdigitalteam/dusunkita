# Dusun Kita — Struktur Teknis & Roadmap

## Struktur Repo (base = befthr/negerikomen)

```
dusunkita/
├─ index.html (703KB)   SPA peta kampung (React/Vite build)
├─ data.js (280KB)      database kampung (JSON statis, diganti tiap hari)
├─ konsol.js (59KB)     14 mini game arcade
├─ liga.js (29KB)       Liga Dusun (kompetisi skor antar warga)
├─ ambil-komen.html     tool scrape komentar IG (internal)
├─ sw.js, manifest.json PWA
├─ api/                 Vercel serverless functions (backend)
│   ├─ followers.js     follower count dari Graph API IG
│   ├─ kartu.js (86KB)  INTI: validasi Kartu Komen + konfirmasi kades
│   ├─ trakteer.js      webhook Trakteer → auto-apply donasi
│   ├─ _terapkan.js     logika apply (warna/emas/tingkat/ruko/item)
│   └─ _kavling.js      39 kavling eksklusif + kavling biasa
├─ docs/                blueprint + lore (folder baru)
└─ scripts/             otomasi (folder baru)
```

## Backend (hybrid storage)
- `data.js` = JSON statis (data besar, jarang berubah)
- **Upstash Redis (KV)** via env `KV_REST_API_URL` + `KV_REST_API_TOKEN` — state dinamis:
  - saldo genteng, pesanan warna/ruko/item, antrean, juragan, goal kampung
- Env Vercel: `IG_TOKEN`, `TRAKTEER_WEBHOOK_TOKEN`, `KV_REST_API_URL`, `KV_REST_API_TOKEN`

## Monetisasi (dari kartu.js + trakteer.js)
- Kode pesanan: `WARNA-XXXX`, `EMAS-XXXX`, `RUKO-XXXX`, `ITEM-XXXX`, `TINGKAT-XXXX`
- Saldo Bata + `DOMPET-XXXX` (wallet virtual)
- Goal kampung (crowdfunding) + cicilan
- Auto-apply: lunas → diterapkan otomatis (warna/emas/item); ruko & papan nama → konfirmasi kades

## Identitas yang Perlu Diganti (rebrand)
Grep `index.html` + `manifest.json` + `data.js`:
- `negerikomen` (76x), `Negeri Komen` (30x), `NEGERI KOMEN` (1x)
- `Bata` (75x), `Juragan Bata` (7x) — bisa dipertahankan kalau tetap pakai lore genteng
- `Pak Kades` (25x) → `Pak RT`, `kades` (20x)
- `trakteer`/`Trakteer` (60x) — ganti kalau ganti platform donasi

## Roadmap Implementasi
1. [x] Clone base repo
2. [x] Analisa struktur (kartu.js, liga.js, index.html)
3. [ ] Rebrand identitas → Dusun Kita (nama/logo/lore/karakter)
4. [ ] Tambah fitur Alpha City: pekerjaan+gaji, live layer, membership
5. [ ] Otomasi update harian (scrape komen → generate data.js → commit → deploy)
6. [ ] Deploy Vercel + verifikasi

## Otomasi Update Harian (rencana scripts/)
```
cron 18:50 → scrape komen IG (ambil-komen.html / API)
          → parse nama+warna → generate data.js
          → git commit data.js → push → Vercel auto-deploy
cron 15:30 → generate brief episode Reels (otomasi)
16:00 → posting episode Reels (manual)
cron 24:00 → notif rekap Telegram
```

## Catatan Keamanan
- `KV_REST_API_TOKEN` + `IG_TOKEN` + `TRAKTEER_WEBHOOK_TOKEN` = rahasia, simpan di env Vercel (bukan di repo).
- Jangan ubah `x`/`y` warga manual (rumah pindah).
- `_kavling.js` harus sinkron dengan `desaBangun()` di index.html.

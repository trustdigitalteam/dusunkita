---
name: dusunkita-world-building
description: Bangun "konten interaktif world-building" (format komen = jadi bagian dunia) dari repo befthr/negerikomen. Rebrand ke identitas baru + fitur Alpha City (live/pekerjaan/gaji) + otomasi update harian + deploy GitHub Pages. Reusable buat niche apa pun (kuliner, fesyen, gaming, dll).
---

# Dusun Kita — Skill World-Building dari Komentar

## Trigger
- User minta bangun/replikasi format "komen = jadi bagian dunia" (Negeri Komen / Alpha City style)
- User minta rebrand repo `befthr/negerikomen` ke identitas baru
- Niche: entertainment interaktif, UGC world-building, game sosial komunitas

## Konsep Inti (Prinsip)
1. **Konten = game, bukan iklan.** Tidak ada CTA jualan.
2. Uang masuk lewat **kepemilikan & status virtual**, bukan "beli barang".
3. Akuisisi = komen nama+warna (barrier nol, konversi 61.8% terbukti).
4. Retention = serial harian jam tetap + live 24/7 + ekonomi virtual + leaderboard.

## Sumber (Repo Referensi)
- `github.com/befthr/negerikomen` — base lengkap (SPA + 14 mini game + liga + KV + Trakteer webhook)
- Struktur: `index.html` (703KB SPA), `data.js` (database kampung JSON), `konsol.js` (game), `liga.js`, `api/*` (Vercel serverless), `ambil-komen.html` (tool scrape manual)

## Langkah (Reusable)

### 1. Clone + Rapikan
```bash
git clone https://github.com/befthr/negerikomen.git <folder>
cd <folder> && mkdir -p docs scripts
```

### 2. Pilih Identitas (cek ketersediaan dulu)
- Cek IG handle FREE: `curl -s "https://www.instagram.com/api/v1/users/web_profile_info/?username=<name>" -H "User-Agent: Mozilla/5.0" -H "X-IG-App-ID: 936619743392459"`
- Cek domain: `curl -s "https://rdap.pandi.id/domain/<name>.my.id"`
- Pilih nama ikonik + "milik bersama" (kata "kita" = kepemilikan kolektif)

### 3. Rebrand (urutan penting: ganti yang panjang dulu)
```bash
cp index.html index.html.bak; cp data.js data.js.bak
sed -i \
  -e 's/Juragan Genteng/Sesepuh/g' \
  -e 's/kepala desa/Pak RT/g' \
  -e 's/Pak Kades/Pak RT/g' \
  -e 's/Negeri Komen/Dusun Kita/g' \
  -e 's/negerikomen/dusunkita/g' \
  -e 's/Genteng/Bata/g' \
  index.html
```
- **JANGAN ganti variabel internal**: `genteng` (array BENDA), `goal:genteng` (KV key), `kk-kades` (CSS class), `desaBangun()`/`NAMA_DESA` (fungsi/var). Ganti = rusak.
- Ganti juga: manifest.json, privasi.html, sw.js, README.md, konsol.js, liga.js, ambil-komen.html, api/*.js (OWNER + teks brand).

### 4. Reset data.js (hari-1 kosong)
Pakai `scripts/generate_data.py --reset` → account, day=1, kavling=50, residents=[].

### 5. Fitur Alpha City
- **Live layer**: tambah card `<div class="card live">` + CSS + JS `muatLive()`/`parseLiveId()` (baca `data.js` field `live.url`).
- **Pekerjaan/gaji**: base sudah punya (Loker + gaji Receh + kontrak), tinggal tema-kan.

### 6. Otomasi (scripts/otomasi.py)
- Scrape komentar via Graph API (`me/media` → `{id}/comments?fields=...replies{...}`)
- Parse "nama + warna atap + warna tembok" → warga baru
- Update state.json → generate data.js → git push → auto-deploy
- Mode: `--dry-run`, `--no-push`, full

### 7. Deploy
- **GitHub Pages** (static, tanpa login): buat repo → `gh api repos/X/pages -X PUT` source=gh-pages branch → push
- **Vercel** (buat API functions): butuh login/token. package.json `"type":"module"` + vercel.json.

## Pitfalls (yang sudah ketemu)
1. **GitHub Pages = static only.** API functions (`api/*.js`) mati. Butuh Vercel buat follower/kartu/trakteer.
2. **gh token tanpa `workflow` scope** → tidak bisa push `.github/workflows`. Pakai branch `gh-pages` legacy + `gh api pages -X PUT` langsung.
3. **Canvas kosong (0 pixel)** saat residents=0 — bukan bug, frame render butuh data; verifikasi dengan cek `getImageData` non-black count.
4. **`vercel deploy --temporary`** = URL expired 59 menit + butuh claim. Untuk permanen perlu login.
5. **Vercel CLI `npx vercel` timeout** → `npm install -g vercel` sekali, lalu pakai `vercel` langsung.
6. **CF token `cfut_*` cuma Zone.DNS Edit** → tidak bisa deploy Cloudflare Pages.
7. **`document.write('<script...')` di index.html** = block script pemisah, jangan digabung saat parse/edit.
8. **Sed ganti `Genteng`→`Bata`** akan ikut ganti string di data.js lama; backup dulu + reset data.js setelahnya.

## Prasyarat Akun (di luar kode, WAJIB untuk live penuh)
1. IG handle → Business/Creator account
2. Facebook Page (jembatan token)
3. Meta Developer App → `IG_TOKEN` long-lived (graph.instagram.com)
4. (opsional) Trakteer buat donasi, YouTube buat live

## Monetisasi Tersembunyi (bertahap)
| Fase | Aksi | Bentuk di mata warga |
|---|---|---|
| 1 | Trakteer/donasi | "Gotong royong bangun dusun" |
| 2 | Kavling premium | "Reward warga loyal" |
| 3 | Affiliate ("warung warga") | "Bu Sari buka warung" |
| 4 | Sponsorship gedung | "Balai desa disponsori X" |

## Verifikasi
- JS valid: `node -e "new Function(scriptBlock)"` per block
- Peta render: browser console `getImageData` hitung non-black pixel
- Live: `curl -s URL -o /dev/null -w "%{http_code}"` = 200
- Brand: `grep -c "Dusun Kita" index.html`

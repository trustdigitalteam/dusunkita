# Dusun Kita — Otomasi Update Harian

## Alur (sama dengan ambil-komen.html, otomatis penuh)

```
cron 19:30 WIB  →  scripts/otomasi.py
   1. Scrape komentar postingan @dusunkita (Graph API Instagram)
   2. Parse "nama + warna bata + warna tembok" → warga baru
   3. Update state.json (residents++, day++, updated)
   4. Generate data.js
   5. git commit + push → GitHub Pages auto-deploy
```

## File

| File | Fungsi |
|---|---|
| `scripts/otomasi.py` | inti: scrape + parse + generate + push |
| `scripts/cron.sh` | wrapper cron (set IG_TOKEN) |
| `scripts/generate_data.py` | generate data.js dari state (--reset / harian) |
| `scripts/state.json` | state kampung (git-ignored, lokal) |
| `ambil-komen.html` | tool manual (referensi, browser) |

## Setup

### 1. Prasyarat akun (WAJIB, belum ada)
- IG `@dusunkita` → jadikan **Business/Creator**
- Hubungkan ke **Facebook Page**
- Buat **Meta Developer App** → `Instagram Graph API` → long-lived access token

### 2. Set token
```bash
export IG_TOKEN=IGAA...
# atau tulis di cron environment
```

### 3. Inisialisasi state (sekali)
```bash
python3 scripts/generate_data.py --reset
```

### 4. Test
```bash
python3 scripts/otomasi.py --dry-run   # scrape + parse saja
python3 scripts/otomasi.py --no-push   # update data.js tanpa push
python3 scripts/otomasi.py             # full: scrape + generate + push
```

### 5. Cron (Hermes)
```
schedule: 30 19 * * *
script: bash /root/negerikita/scripts/cron.sh
```

## Catatan
- `IG_TOKEN` = rahasia, jangan commit (ada di .gitignore via .env)
- Parser warna: atap/bata/genteng/roof → roof, tembok/wall/dinding/warna → wall
- Warna dikenal: merah, merah muda/pink, biru/toska, hijau, kuning/orange, ungu, putih, hitam, abu, coklat, krem
- Slot pekarangan: grid 10 kolom, mulai koordinat 44,44 (ikut referensi)
- Graph API hanya baca komentar dari postingan milik @dusunkita sendiri (bukan akun lain)

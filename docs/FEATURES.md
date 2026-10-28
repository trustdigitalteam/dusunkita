# Dusun Kita — Fitur (Pekerjaan/Gaji + Live)

## Status Fitur

### 1. Pekerjaan & Gaji (sudah ada di base, sudah di-tema-kan)
Base `befthr/negerikomen` sudah punya sistem kerja lengkap, tinggal tema "Dusun Kita":
- **Loker Dusun** (milik Pak RT) — lowongan resmi: Tukang Kerja Bakti, Penjaga Warung, Satpam Dusun, Asisten Pak RT
- **Loker Warga** (swasta) — pemilik bangunan buka lowongan, atur gaji sendiri
- **Gaji per pekan** (Receh) — cair otomatis, kontrak 7/14/30 hari
- **Lencana karyawan** — plang + ikon di atap rumah (satpam/penjaga/marbot/karyawan)
- **Ekonomi Receh** — gaji → saldo → belanja di toko/dealer/upgrade rumah

Perubahan tema yang diterapkan:
- `Kepala desa` → `Pak RT`
- `Loker Negeri` → `Loker Dusun`, `Loker Swasta` → `Loker Warga`
- `Satpam Kampung` → `Satpam Dusun`
- `Rental playadalahmain` → `Rental Playstation Kita`
- `Stadion Desa` → `Lapangan Dusun`, `Liga Dusun` → `Liga Gang`
- `rumah` → `pekarangan` (di konteks kerja)

### 2. Live Layer (FITUR BARU — dari Alpha City, ditambah)
Base tidak punya live. Ditambahkan:
- **Card "🔴 Live Dusun"** di sidebar (setelah stats)
- **Embed YouTube** via config `data.js` field `live`
- **Fallback** kalau tidak ada URL → pesan "belum ada siaran"

Config di `data.js`:
```json
"live": {
  "url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "label": "🔴 Sedang live",
  "jadwal": "tiap hari 19.00-24.00 WIB"
}
```
- `url` kosong → card disembunyikan otomatis
- `url` diisi → iframe YouTube muncul (parse `youtu.be`, `?v=`, `/live/`, atau ID 11 char)

## Cara Pakai (update harian)
1. Isi `live.url` di `scripts/state.json` saat mau pasang live
2. `python3 scripts/generate_data.py` → data.js update
3. Deploy

## File yang Diubah
- `index.html` — card live + CSS + JS `muatLive()`/`parseLiveId()`
- `scripts/generate_data.py` — tambah field `live`, `loker`, `lowongan`
- `data.js` — hasil regenerate (field baru masuk)

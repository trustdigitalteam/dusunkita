# Dusun Kita — Alur Konten Sinkron (Loop Tertutup)

## Prinsip: Konten = Input, Web = Output

Satu loop yang nyambung: video → komen → scrape → approve → peta → video berikutnya.
Semua data dari **satu sumber kebenaran** = `data.js` (dipush, dibaca web + dashboard).

## Loop Harian (jadwal)

| Jam (WIB) | Aksi | Aktor |
|---|---|---|
| 19:00 | Posting episode "Hari ke-N" + CTA komen nama+warna | Admin (manual/konten) |
| 19:30 | Scrape komen otomatis → `antrian.json` | cron `otomasi.py --antrian` |
| 19:35 | Review antrian di dashboard → approve/reject | Admin |
| 19:40 | Generate `data.js` + push → web live | `otomasi.py --apply` |
| 20:00+ | (opsional) live YouTube → card "Live Dusun" aktif | Admin |

## Format Konten (CTA wajib seragam)

Tiap episode wajib ada 1 baris CTA yang sama, biar parser kebaca:
```
Komen: NAMA, BATA <warna>, TEMBOK <warna>
Contoh: Budi, bata merah, tembok biru
```

Pola yang dikenali parser:
- `atap/bata/genteng/roof <warna>` → warna atap
- `tembok/wall/dinding <warna>` → warna tembok
- nama = kata sebelum koma, atau username

## Jenis Konten (feed serial + retention)

| Jenis | Tujuan | Frekuensi |
|---|---|---|
| Episode update dusun (reels) | akuisisi warga baru | tiap hari 19:00 |
| Pengumuman warga baru | FOMO + rasa memiliki | dalam episode |
| Tantangan/voting (nama gang, bangunan) | engagement | 2-3x/minggu |
| Live YouTube "Dusun tumbuh" | retention 24/7 | harian |
| Story "hari ini di dusun" | top-up engagement | harian |

## Loop Konten → Data (detail)

1. **Video episode** menampilkan: peta hari ini (screenshot web), jumlah warga, warga baru kemarin, tantangan besok.
2. **CTA komen** → warga komen nama+warna.
3. **Scrape** tarik komen postingan episode → antrian.
4. **Approve** → warga masuk `residents[]` di `state.json`.
5. **Generate** → `data.js` = window.NK_DATA (dipush).
6. **Web** render peta + daftar warga baru.
7. **Video besok** ambil angka dari `data.js` (hari, warga, warga baru) → jadi script episode. Loop.

## Dashboard (admin.html)

Baca `antrian.json` + `state.json` (lokal di VPS):
- Statistik: hari ke-, total warga, follower, target, antrian pending
- Antrian komentar (username, teks, warna terdeteksi) → tombol **Approve** / **Tolak**
- Tombol **Generate & Push** → jalankan `otomasi.py --apply`
- Log cron terakhir

## Sinkronisasi Teknis (wajib konsisten)

| Konfig | Nilai final | Lokasi |
|---|---|---|
| Handle IG | `@dusunkita.id` | semua file |
| Domain | `dusunkita.my.id` | semua file |
| Trakteer | `trakteer.id/dusunkitaindonesia` (tanpa titik) | state.json + index.html |
| Unit donasi | Bata | state.json + index.html |
| Pemimpin | Pak RT | index.html |

## Sumber Kebenaran

```
scripts/state.json  ← kerja lokal (git-ignored), dibaca otomasi + dashboard
        │ generate_data.py
        ▼
data.js             ← DIPUSH, dibaca web + GitHub Pages (sumber publik)
```

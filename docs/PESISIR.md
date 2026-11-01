# Dusun Kita v2 — Kampung Pesisir (rebrand total, beda dari Negeri Komen)

> Status: **RENCANA — belum dieksekusi.** Menunggu approval Arie.
> Prinsip: mulai dari NOL (day=1, 0 warga). Beda SUASANA, BANGUNAN, KONSEP, ITEM, dan CARA PRODUKSI KONTEN dari Negeri Komen.

---

## 1. SUASANA / IDENTITAS VISUAL (bedakan total)

Negeri Komen = senja tropis hangat (oranye `#F2C230` / `#C4402F`), gunung, terowongan, 3 desa, WebGL 3D.

**Dusun Kita = kampung pesisir** — palet dingin laut:

| Elemen | Negeri Komen (lama) | Dusun Kita Pesisir (baru) |
|---|---|---|
| Palet dasar | senja oranye `#F2C230`/`#C4402F` | laut `#2F7AA3`, pasir `#EAD7A4`, bakau `#2F7D5B`, teal `#7FD0D2` |
| Langit | sunset warm | biru laut + awan cumulus putih |
| Geografi | gunung + terowongan | **laut lepas + sungai + muara** |
| Rumah | genteng merah | **rumah panggung bambu + atap nipah** |
| Transportasi | angkot + helikopter + truk | **getek/rakit + perahu jukung** |
| Rendering | WebGL Three.js (3D) | tetap canvas 2D (hemat, feel beda) |

---

## 2. BANGUNAN & KONSEP — khas pesisir (bukan tiruan NC)

**3 kampung** → ganti jadi **3 kampung tepi sungai**:

| Nama | Posisi |
|---|---|
| Kampung Bata | muara (dekat laut) |
| Kampung Senja | tengah |
| Kampung Waru | hulu |

Dihubungkan **sungai + getek**, bukan terowongan/angkot.

### Fasilitas (ganti infra NC: gardu/menara air/BTS/angkot)

| NC (referensi) | Dusun Kita Pesisir (baru) |
|---|---|
| Sawah + Pintu Air | 🐟 **Tambak Bata** (udang/bandeng) |
| Menara Air | 🕳️ **Sumur Bata** |
| Halte Angkot + angkot biru | 🛶 **Dermaga Getek** + getek bolak-balik (animasi) |
| Tugu pendukung | 🌴 **Pohon Waru** (titik kumpul + harta karun) |
| Pasar Senggol | 🎣 **Pasar Kaget** (jual-beli ikan) |
| Balai Desa | 🏚️ **Balai RT** |
| — | ⛵ **Galangan Perahu** (tempat bikin getek) |

**Aturan nama brand unik** (sudah ada di skill): jangan generik — "Warung Nagasari", "Tambak Gento", "Balai Waru", dst.

---

## 3. ITEM EKSKLUSIF — re-skin total (bukan copy GENTO/NAGASARI/MBULAN)

| Negeri Komen | Dusun Kita Pesisir | Efek |
|---|---|---|
| GENTO robot (22) | **GETEK MESIN** (getek bermotor) | jalan keliling sungai |
| NAGASARI naga (25) | **LELE RAKSASA** | berenang di sungai, sembur air |
| MBULAN kucing (20) | **BURUNG WARU** (burung malam) | siang di pohon, malam terbang |
| Karpet Terbang (23) | **BALON UDARA BATA** | rumah melayang |
| Patromax lampu (12) | **LENTERA PESISIR** | malam terang + kunang-kunang |
| Lampu Sorot (19) | **LAMPU SUAR PELABUHAN** | username terpampang di langit malam |

Harga Bata menyesuaikan nanti saat implementasi.

---

## 4. MINI GAME — mulai 1, berkembang nanti

Tema pesisir, beda dari konsol.js NC (14 game) + Panen Sawah.

| # | Nama | Mekanik | Status |
|---|---|---|---|
| 1 | **Tangkap Bata** | getek di muara tangkap bata merah dihanyutkan arus; hindari kayu lapuk; bonus bata emas | RENCANA |
| 2 | Getek Menyeberang | rakit vs arus sungai | backlog |
| 3 | Panjat Pohon Waru | ambil bata di pohon | backlog |
| 4 | Liga Getek | balap getek di sungai (ganti Liga Dusun NC) | backlog |

---

## 5. CARA PRODUKSI KONTEN — beda dari NC

| Tahap | Negeri Komen | Dusun Kita Pesisir |
|---|---|---|
| Footage | screen-record zoom/pan | screen-record pesisir (Playwright, sudah ada) |
| Voiceover | Mbak Tena penyiar TV | **Pak RT** + "Bu Waru" (warung) |
| Hook | "HARI KE-N" + BREAKING NEWS | "HARI KE-N DI DUSUN KITA" + cerita muara |
| CTA | komen "RUMAH" | komen "BATA" (warna bata + tembok) |
| Caption | teaser kejutan pekan depan | sama, gaya Pak RT santai pesisir |

---

## 6. DASHBOARD STUDIO (gap dari NC)

Negeri Komen pakai `ambil-komen.html` (scrape IG → CSV → Claude → data.js) + Trakteer webhook.

Dusun Kita `admin.html` sudah ada tapi kurang panel:

| # | Fitur | Field | Prioritas |
|---|---|---|---|
| 1 | Set Quest | `quest` | 1 |
| 2 | Tambah Loker | `loker[]` | 2 |
| 3 | Set Voucher (Shopee) | `voucher` | 3 |
| 4 | Set Tontonan (TV) | `tontonan.items[]` | 4 |
| 5 | Tambah Award | `awards[]` | 5 |
| 6 | Tambah Dusun | `dusun[]` | 6 |
| 7 | Ganti Goal | `goalKampung` | 7 |
| 8 | Toggle fitur | `setir/gento/gentoMain` | 8 |
| 9 | Approve massal | — | 9 |
| 10 | Hapus warga | `residents[]` | 10 |
| 11 | Edit warga | warna/nick/kavling | 11 |
| 12 | **Panel Getek** (jadwal) | `getek[]` | baru |
| 13 | **Panel Tambak** (hasil panen) | `tambak[]` | baru |

---

## 7. STRUKTUR MAP — UBAH TOTAL (pesisir, bukan grid darat)

> Map sekarang = warisan NC: grid persegi `N=91`, `C=45`, blok `S=6`, 2 jalan besar bersilang di tengah (balai Pak RT), sungai kecil hiasan di tepi utara, tema blok sawah/empang/lapangan.

### Target baru — kampung pesisir
1. **Laut lepas** di sisi selatan (pengganti sawah tepi) — biru gradasi + ombak + perahu jukung
2. **Muara + sungai besar** yang membelah kampung jadi 3: Kampung Bata (muara) · Kampung Senja (tengah) · Kampung Waru (hulu)
3. **Getek/rakit** bolak-balik di sungai (ganti angkot + perahu hias)
4. **Rumah panggung + atap nipah** (ganti genteng merah)
5. **Jalan setapak pasir** menyusur sungai (ganti jalan aspal grid)
6. **Dermaga getek** di tiap kampung + galangan perahu
7. **Tambak** (kotak air payau) ganti sawah darat
8. **Pohon waru + kelapa + bakau** ganti pohon generik

### Detail teknis (saat eksekusi)
| Komponen | File/fungsi | Perubahan |
|---|---|---|
| Grid & geometri | `N=91,C=45,S=6` + `drawWorld` | ganti sumbu: sungai jadi sumbu utama, bukan jalan |
| Sungai | `drawSungai()` (baris 862) | perbesar dari 3→6+ petak, buat jadi pemisah 3 kampung |
| Jalan | `jenisJalan()` (845) + `JALAN_SEG` | aspal → pasir/tanah, menyusur sungai |
| Rumah | `drawHouse()` (952) | genteng → atap nipah + panggung |
| Laut | baru `drawLaut()` | sisi selatan, gradasi + ombak + jukung |
| Transportasi | `drawAngkot()` (1410) | → `drawGetek()` bolak-balik sungai |
| Sawah | `drawSawah()` (831) | → `drawTambak()` (air payau) |
| Tema blok | `temaBlok()` (882) | sawah/empang → tambak/muara/bakau |
| Fasilitas | `BTYPES` + `infraDaftar` | gardu/menara air/BTS → sumur/dermaga/galangan |

### Catatan anti-bug (warisan dari porting NC)
- Jangan port blok wholesale → identifier collision (`PDH`, `LOKP`, `kavTerisi`, dll). Cek `node --check api/*.js` + parse `<script>` index.html setelah tiap blok.
- `drawHouse` + `drawTema` dipakai banyak tempat — ubah di 1 fungsi, jangan duplikat.
- Posisi kavling `x,y` harus **stabil** (warga lama tidak pindah) — ubah geometri lewat fungsi `wx()/wy()` + `tilesOf()`, bukan geser data resident.
- Rebrand sweep: grep `Kades/kades/Genteng/lembarpeta/Komen` setelah ubah.

**Status: RENCANA.** Refactor map = effort BESAR, dikerjakan step-by-step tiap "lanjut".

---

## 8. URUTAN EKSEKUSI (hemat kredit, 1 arah)

1. Palet + identitas visual di `index.html` (CSS var + canvas color) — senja → pesisir
2. Rumah panggung + atap nipah (ganti drawing genteng → nipah)
3. Sungai + getek + dermaga (ganti jalan/angkot)
4. 3 kampung + Tambak + Sumur + Pasar Kaget (bangunan)
5. Item eksklusif re-skin (GETEK MESIN, LELE RAKSASA, dst)
6. Mini game Tangkap Bata
7. Konten + dashboard studio panel

**Belum ada yang dieksekusi.** Tiap step tunggu perintah "lanjut" dari Arie.

# Roadmap Dusun Kita — 45 Hari + Fitur Dashboard

> Semua sesuai struktur GitHub Negeri Komen. Semua mulai dari NOL.
> Link referensi: https://github.com/befthr/negerikomen
> Repo kita: https://github.com/trustdigitalteam/dusunkita

## Link Semua Referensi

| Item | Link |
|---|---|
| **Negeri Komen (referensi)** | https://github.com/befthr/negerikomen |
| — index.html (web+game) | https://raw.githubusercontent.com/befthr/negerikomen/main/index.html |
| — data.js (data harian) | https://raw.githubusercontent.com/befthr/negerikomen/main/data.js |
| — api/kartu.js (56 aksi) | https://raw.githubusercontent.com/befthr/negerikomen/main/api/kartu.js |
| — konsol.js (14 mini game) | https://raw.githubusercontent.com/befthr/negerikomen/main/konsol.js |
| — liga.js (liga bola) | https://raw.githubusercontent.com/befthr/negerikomen/main/liga.js |
| — README (alur update harian) | https://github.com/befthr/negerikomen/blob/main/README.md |
| **Dusun Kita (repo kita)** | https://github.com/trustdigitalteam/dusunkita |
| — Dashboard admin | https://dusunkita.vercel.app/admin.html |
| — Web live | https://dusunkita.vercel.app/ |
| — Docs | https://github.com/trustdigitalteam/dusunkita/tree/main/docs |

## Nama Fasilitas (sudah di-bedakan dari Negeri Komen)

| Negeri Komen | Dusun Kita (baru) |
|---|---|
| Desa Komen-Komen Sejahtera | Dusun Kita Sejahtera |
| Toko Pak Kades | Toko Pak RT |
| TB Genteng Jaya Jaya Joss | **TB Sinar Bata** |
| Rental Playstation | **Rental Konsel Kita** |
| Genteng (mata uang traktir) | Bata |

## ROADMAP 45 HARI

### FASE 0 — Persiapan (H-1 s.d. Hari 0)
- [x] Reset state dari nol (day=1, 0 warga, loker kosong)
- [x] Semua fitur match GitHub (56 aksi, 26 bangunan)
- [x] Kejutan Pekan reset (29 Okt–3 Nov)
- [x] Nama fasilitas di-bedakan
- [ ] **POSTING REELS PERTAMA** (EP0, script ready: `docs/KONTEN-EP0.md`)
- [ ] Buat akun Trakteer + set webhook (unit = "Bata")
- [ ] Isi `voucher.url` = link Shopee Affiliate kamu

### FASE 1 — Minggu 1: Membuka Dusun (29 Okt – 4 Nov)
| Hari | Tanggal | Task | Konten |
|---|---|---|---|
| 1 | 29 Okt | Buka pendaftaran warga (Kejutan 🏘️) | EP1 "Dusun Kita Dibuka" |
| 2 | 30 Okt | Harta Karun mulai (Kejutan 🔍) | EP2 "Warga pertama + peti harta" |
| 3 | 31 Okt | Voting Tetangga Idaman (Kejutan 🏆) | EP3 "Papan Idaman pekan 1" |
| 4 | 1 Nov | TV Komen + Tontonan (Kejutan 📺) | EP4 "TV Kampung nyala" |
| 5 | 2 Nov | Balon Bata (Kejutan 🎈) + Harta mulai jalan auto | EP5 "Langit Dusun Kita" |
| 6 | 3 Nov | Pasar Dusun (Kejutan 🧺) | EP6 "Pasar Dusun buka" |
| 7 | 4 Nov | Loker pertama dibuka (set `loker[]`) | EP7 "Loker pertama" |

**Auto tiap hari:** cron 19:30 scrape → approve di dashboard → cron 19:40 apply → web live.
**Auto harta:** 2–3 peti/hari (HMAC), max 3x/pekan per warga.

### FASE 2 — Minggu 2: Ekonomi Mulai (5 Nov – 11 Nov)
| Hari | Tanggal | Task | Konten |
|---|---|---|---|
| 8 | 5 Nov | Konsol dibuka (sewa 4 Bata) | EP8 "Konsol Dusun Kita" |
| 9 | 6 Nov | **QUEST UFO** (set `quest` di state.json) | EP9 "UFO nyasar!" |
| 10 | 7 Nov | Lapangan bola + Liga (8 sesi/hari) | EP10 "Liga Dusun" |
| 11 | 8 Nov | Gaji mingguan pertama cair | EP11 "Gaji pertama warga" |
| 12 | 9 Nov | Warga beli item (sepeda/motor/ayunan) | EP12 "Pekarangan warga" |
| 13 | 10 Nov | Ruko pertama (20 Bata) | EP13 "Ruko pertama" |
| 14 | 11 Nov | Pindah rumah pertama (Truk/Heli) | EP14 "Pindahan" |

### FASE 3 — Minggu 3: Ekspansi (12 Nov – 18 Nov)
| Hari | Tanggal | Task | Konten |
|---|---|---|---|
| 15–18 | 12–15 Nov | Upgrade goal: 100→200 Bata ("Puskesmas Dusun") | EP15 "Goal baru" |
| 19 | 16 Nov | Loker ke-2 (penjaga warung/bakso) | EP16 |
| 20 | 17 Nov | **Dusun baru** (warga bikin dusun sendiri, set `dusun[]`) | EP17 "Dusun pertama" |
| 21 | 18 Nov | Item eksklusif: GENTO robot (22 Bata) | EP18 "Robot dusun" |

### FASE 4 — Minggu 4: Komunitas (19 Nov – 25 Nov)
| Hari | Tanggal | Task | Konten |
|---|---|---|---|
| 22 | 19 Nov | Naga / Patromax / Sorot dibuka | EP19 "Malam dusun" |
| 23 | 20 Nov | Papan Tetangga Idaman pekan 2 | EP20 |
| 24 | 21 Nov | Voucher Shopee aktif di web (monetisasi jalan) | EP21 |
| 25 | 22 Nov | Misi: 100 warga | EP22 |
| 26 | 23 Nov | Quest UFO #2 (kode baru) | EP23 |
| 27 | 24 Nov | Awards: "Warga 100 Pertama" | EP24 |
| 28 | 25 Nov | Pasar Malam (bangunan `pasarmalam`) | EP25 |

### FASE 5 — Pasca-Bulan 1 (26–45 Nov)
| Tanggal | Task |
|---|---|
| 26–30 Nov | Upgrade goal: 200→400 Bata ("Sekolah Dusun") |
| 31 Nov–2 Des | Misi 250 warga + 2 dusun baru |
| 3–7 Des | Dealer motor + coffee shop + penginapan |
| 8–14 Des | **Monumen Tetangga Idaman** (pajang 3 juara) |
| 15–21 Des | Misi 500 warga + voting dusun terbaik |
| 22–30 Des | Upgrade goal: 400→800 Bata ("Balai Dusun V2") |
| 31 Des–15 Jan | **Rangkaian tahun baru** — quest spesial, loker ganda, target 1000 warga |

### Trigger Upgrade Goal (otomatis oleh Pak RT)
```
100 Bata → Balai Dusun (goal awal)
200 Bata → Puskesmas Dusun
400 Bata → Sekolah Dusun
800 Bata → Balai Dusun V2 + Gerbang
1000+   → Desa Baru (target follower)
```
Set di `state.json` → `goalKampung: {judul, target, awal}` → generate_data → deploy.

## DASHBOARD ADMIN — Fitur yang KURANG (belum bisa)

**BISA sekarang:**
- ✅ `m=status` — baca hari/warga/antrian/follower
- ✅ `m=set` — approve/reject antrian (1 nama/request)
- ✅ `m=scrape`/`m=apply` — **cuma kalau `VPS_WEBHOOK_URL` ada di .env (BELUM)**

**BELUM BISA (perlu ditambah di `api/admin.js` + `admin.html`):**

| # | Fitur | Field yang diset | Estimasi |
|---|---|---|---|
| 1 | Set Quest UFO | `quest: {tanggal,start,end,code}` | 30 mnt |
| 2 | Tambah Loker | `loker[]` | 1 jam |
| 3 | Set Voucher (Shopee) | `voucher: {url,label}` | 30 mnt |
| 4 | Set Tontonan (TV) | `tontonan.items[]` | 30 mnt |
| 5 | Tambah Award | `awards[]` | 30 mnt |
| 6 | Tambah Dusun | `dusun[]` | 30 mnt |
| 7 | Ganti Goal | `goalKampung` | 30 mnt |
| 8 | Toggle fitur | `setir/gento/gentoMain` | 15 mnt |
| 9 | Approve massal | semua pending → approved | 15 mnt |
| 10 | Hapus warga | dari `residents[]` | 30 mnt |
| 11 | Edit warga | warna/nick/kavling | 1 jam |
| 12 | Trigger scrape/apply manual | butuh `VPS_WEBHOOK_URL` | 15 mnt |

**Alur set dari dashboard:** dashboard tulis Redis → VPS cron 19:40 baca Redis → generate_data → push → live.

## Alur Tiap Hari (10 menit)

```
19:00  Posting reels + screenshot footage (5 mnt)
19:30  Cron scrape → cek dashboard → approve (2 mnt)
19:40  Cron apply → web live auto
MALAM  Set quest/loker/voucher (kalau ada event) → deploy (3 mnt)
```

## Catatan Anti-Bug

- Semua fitur dari GitHub Negeri Komen sudah match (56 aksi, 26 bangunan, harta, quest)
- `JOBS` fallback = `[]` (loker kosong dari nol)
- `HARTA_MULAI` = 2 Nov (reset dari nol)
- `KEJUTAN` = 29 Okt–3 Nov (reset dari nol)
- `NAMA_DESA_OLEH` = dusunkita.id (bukan alifrmnxhrn)
- Semua `node --check` lulus, 0 hardcoded lembarpeta/kades/Genteng

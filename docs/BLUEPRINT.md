# Dusun Kita — Blueprint Konsep Gabungan

Gabungan 2 referensi: **Negeri Komen** (akuisisi murah, komen = rumah) × **Alpha City** (retention kuat, live + ekonomi + game).

## Prinsip Inti
- Konten = game, bukan iklan. Tidak ada CTA jualan.
- Uang masuk lewat **kepemilikan & status virtual**, bukan "beli barang".
- Warga merasa *berkontribusi ke dunianya*, bukan *ditawarin produk*.

## Warisan Konsep

| Aspek | Dari Negeri Komen | Dari Alpha City |
|---|---|---|
| Akuisisi | komen nama+warna = rumah gratis | — |
| Retention | serial harian jam tetap | live 24/7 |
| Kepemilikan | rumah di peta | kota + gedung hasil voting |
| Status | Juragan, gelar, bendera emas | EXP + leaderboard |
| Game | 14 mini game + Liga | mini game + ekonomi |
| Ekonomi | wallet genteng + upgrade | koin + sewa + kerja |
| Monetisasi | Trakteer tiered | membership |

## Mekanik Utama
1. **Lahir jadi warga** — komen `nama + warna rumah + warna atap`, barrier nol (61.8% konversi terbukti).
2. **Dunia hidup** — peta tumbuh tiap hari, live harian, warga baru "datang".
3. **Warga menentukan** — voting gedung, nama dusun, keputusan diumumkan tiap episode.
4. **Ekonomi tersembunyi** — pekerjaan → gaji (koin) → upgrade rumah. Terasa main, bukan belanja.
5. **Status & gamifikasi** — Juragan (donatur), leaderboard 5 warga aktif, kontes berkala.

## Loop Harian
```
19:00  Episode "Hari ke-N" (IG Reels)
19:00-24:00  Live (YouTube) — kampung berubah real-time
sepanjang hari  Web (SPA) — cek rumah, kerja, upgrade, peta
```
1. Nonton → pengen rumah → komen (barrier nol)
2. Lihat rumah muncul → bangga → balik
3. Voting → pengen menang → ajak teman
4. Kerja + gaji → upgrade → balik tiap hari
5. Aktif → leaderboard → status → loyal

## Monetisasi Tersembunyi (bertahap)
| Fase | Kapan | Aksi | Bentuk di mata warga |
|---|---|---|---|
| 1 | Hari 1-14 | Trakteer "Gotong Royong Bata" | Sumbang pembangunan kampung |
| 2 | Hari 15-30 | Kavling premium (pantai/gunung/waduk) | Reward warga loyal |
| 3 | Bulan 2 | "Warung warga" (affiliate) | Cerita warga buka warung |
| 4 | Bulan 3 | Sponsorship gedung | "Balai desa disponsori X" |

## Aturan Anti-Jualan (wajib)
- Tidak ada CTA "beli", "cek harga", "link produk".
- Donasi = "sumbang pembangunan" / "traktir" (lore, bukan transaksi).
- Produk/affiliate = cerita warga ("Bu Sari buka warung"), bukan iklan.

## Fitur yang Ditambahkan ke Base (dari repo negerikomen)
Repo `befthr/negerikomen` = base (SPA + 14 game + liga + KV + Trakteer webhook). Tambahan Alpha City:
1. **Live layer** — embed live 24/7 + sinkron warga "datang" real-time.
2. **Pekerjaan + gaji** — sistem job (satpam/warung/nelayan/petani) + koin kampung.
3. **Membership/patron tier** — rumah eksklusif member (ala Alpha City).

## Keunggulan vs Referensi
- Referensi masih manual harian → kita otomasi (scrape komen → generate data.js → commit → deploy).
- Moat = kecepatan + komunitas + brand, bukan teknologi (barrier teknis rendah).

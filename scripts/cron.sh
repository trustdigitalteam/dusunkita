#!/usr/bin/env bash
# Dusun Kita — cron harian: scrape komen IG -> antrian (review dulu)
# Jalankan tiap hari ~19:30 WIB (setelah episode tayang 19:00).
# Setelah review di dashboard, admin jalankan --apply manual / cron kedua.
set -euo pipefail
cd /root/dusunkita

if [ -z "${IG_TOKEN:-}" ]; then
  echo "IG_TOKEN belum di-set. Set di cron environment atau file .env." >&2
  exit 1
fi

# 19:30 — scrape komen + follower, masuk antrian (TANPA ubah state/push)
python3 scripts/otomasi.py --antrian >> /root/dusunkita/scripts/cron.log 2>&1

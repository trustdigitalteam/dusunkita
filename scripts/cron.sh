#!/usr/bin/env bash
# Dusun Kita — cron harian: scrape komen IG -> generate data.js -> push
# Jalankan tiap hari ~19:30 WIB (setelah episode tayang 19:00).
set -euo pipefail
cd /root/dusunkita

# Token IG long-lived (dari Meta Developer App). Set di sini atau di environment.
if [ -z "${IG_TOKEN:-}" ]; then
  echo "IG_TOKEN belum di-set. Set di cron environment atau file .env." >&2
  exit 1
fi

python3 scripts/otomasi.py >> /root/dusunkita/scripts/cron.log 2>&1

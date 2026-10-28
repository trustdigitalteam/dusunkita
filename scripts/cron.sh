#!/usr/bin/env bash
# Dusun Kita — cron harian: scrape komen IG -> antrian (review dulu)
# Jalankan tiap hari ~19:30 WIB (setelah episode tayang 19:00).
set -euo pipefail
cd /root/dusunkita

# Load IG_TOKEN dari .env
if [ -f .env ]; then
  set -a; source .env; set +a
fi

if [ -z "${IG_TOKEN:-}" ]; then
  echo "IG_TOKEN belum di-set." >&2
  exit 1
fi

python3 scripts/otomasi.py --antrian >> /root/dusunkita/scripts/cron.log 2>&1

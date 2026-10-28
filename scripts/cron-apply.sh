#!/usr/bin/env bash
# Dusun Kita — apply harian: antrian approved -> state -> data.js -> push
# Jalankan tiap hari ~19:40 WIB (setelah admin review antrian).
set -euo pipefail
cd /root/dusunkita

if [ -z "${IG_TOKEN:-}" ]; then
  echo "IG_TOKEN belum di-set." >&2
  exit 1
fi

python3 scripts/otomasi.py --apply >> /root/dusunkita/scripts/cron.log 2>&1

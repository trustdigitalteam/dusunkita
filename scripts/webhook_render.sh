#!/bin/bash
# VPS webhook receiver: terima trigger → jalankan render_episode.py → update status Redis
# Dipanggil oleh Vercel /api/video.js (VPS_WEBHOOK_URL) atau manual.
# Usage: webhook_render.sh <ep>
set -e
EP="${1:-1}"
ROOT="/root/dusunkita"
STATUS="$ROOT/videos/render-status.json"
ADMIN_KEY="dusunkita-45b03625615b0371"
KV_URL="${KV_REST_API_URL:-}"
KV_TOKEN="${KV_REST_API_TOKEN:-}"

echo "Webhook: render EP-$EP $(date '+%H:%M:%S')"

# tulis status awal
echo "{\"ep\":$EP,\"state\":\"running\",\"started\":\"$(date '+%Y-%m-%d %H:%M')\"}" > "$STATUS"

# jalankan render (TTS + Remotion)
cd "$ROOT"
source /root/.hermes/.env 2>/dev/null
export GEMINI_API_KEY="${GEMINI_API_KEY:-$(grep '^GEMINI_API_KEY=' /root/.hermes/.env | cut -d= -f2)}"
if [ -n "$GEMINI_API_KEY" ]; then
  python3 scripts/render_episode.py --ep "$EP" 2>&1 || true
fi

# push status ke Redis (biar dashboard bisa pantau)
if [ -n "$KV_URL" ] && [ -n "$KV_TOKEN" ]; then
  ST=$(cat "$STATUS")
  curl -s -X POST "$KV_URL" \
    -H "Authorization: Bearer $KV_TOKEN" \
    -H "Content-Type: application/json" \
    -d "[$\"SET\", \"dusun:video-status\", $(python3 -c "import json;print(json.dumps('$ST'))")]" > /dev/null
fi

# commit + push (biar video bisa di-serve Vercel)
cd "$ROOT"
git add videos/EP-$(printf %03d $EP)-final.mp4 2>/dev/null || true
git commit -m "video: EP-$(printf %03d $EP) render $(date '+%H:%M')" -q 2>/dev/null || true
git push -q 2>/dev/null || true

echo "DONE EP-$EP"

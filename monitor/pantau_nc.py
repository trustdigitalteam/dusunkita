#!/usr/bin/env python3
"""Pantau repo Negeri Komen — report commit/baru fitur sejak baseline.
Silent (stdout kosong) kalau belum ada commit baru → cron tidak mengirim apa-apa.
Output: diff commit + diff file penting + flag fitur baru.
"""
import json, os, sys, urllib.request, datetime

BASELINE_FILE = "/root/dusunkita/monitor/nc_baseline.json"
REPO = "befthr/negerikomen"

def get(url, token=None):
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": "hermes-monitor"})
    if token: req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

token = os.environ.get("GITHUB_TOKEN")
commits = get(f"https://api.github.com/repos/{REPO}/commits?per_page=30", token)
latest = commits[0]["sha"]

# baseline
try:
    bl_sha = json.load(open(BASELINE_FILE)).get("sha")
except Exception:
    bl_sha = None

# Belum ada baseline → simpan, silent
if bl_sha is None:
    json.dump({"sha": latest, "ts": datetime.datetime.utcnow().isoformat()}, open(BASELINE_FILE, "w"))
    sys.exit(0)

# Tidak ada commit baru → silent
if bl_sha == latest:
    sys.exit(0)

new = [c for c in commits if c["sha"] != bl_sha]
if not new:
    # baseline belum ada di daftar 30 commit → kemungkinan sangat lama, report semua
    new = commits

lines = [f"📡 Update Negeri Komen — {len(new)} commit baru (baseline {bl_sha[:8]} → {latest[:8]})"]
for c in new:
    lines.append(f"• {c['sha'][:8]} {c['commit']['message'].splitlines()[0]}")

# detail file commit terakhir
try:
    files = get(f"https://api.github.com/repos/{REPO}/commits/{latest}").get("files", [])
except Exception:
    files = []

fitur_keywords = ["harta", "tontonan", "voucher", "setir", "gento", "naga", "patromax", "live", "sorot", "kecamatan", "monumen", "lampu", "taman", "pasar", "pantai"]
if files:
    lines.append("\n📝 File berubah di commit terakhir:")
    for f in files[:15]:
        hit = any(k in f["filename"].lower() or k in (f.get("patch") or "")[:3000].lower() for k in fitur_keywords)
        lines.append(f"  {f['status'][:3]} {f['filename']} ({f['additions']:+}/{f['deletions']:-}){' ⚡fitur' if hit else ''}")

# update baseline
json.dump({"sha": latest, "ts": datetime.datetime.utcnow().isoformat()}, open(BASELINE_FILE, "w"))
print("\n".join(lines))

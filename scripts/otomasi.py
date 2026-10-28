#!/usr/bin/env python3
"""Dusun Kita — otomasi update harian.

Alur (sama dengan ambil-komen.html, tapi otomatis):
  1. Scrape komentar postingan terbaru @dusunkita.id via Graph API Instagram
  2. Parse komentar "nama + warna bata + warna tembok" -> warga baru
  3. Update state.json (residents bertambah, followers, day++)
  4. Generate data.js
  5. git commit + push (GitHub Pages auto-deploy)

Env (jangan commit):
  IG_TOKEN  = long-lived access token Instagram Graph API
  (opsional) GH_BRANCH = branch push (default: main)

Pemakaian:
  python3 scripts/otomasi.py            # scrape + update + push
  python3 scripts/otomasi.py --dry-run  # scrape + parse saja, tanpa tulis/push
  python3 scripts/otomasi.py --no-push  # update data.js tanpa push
"""
import json, os, re, sys, subprocess, time
from datetime import datetime, timezone, timedelta
from urllib.parse import urlencode
from urllib.request import urlopen, Request

WIB = timezone(timedelta(hours=7))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "scripts", "state.json")
OUT = os.path.join(ROOT, "data.js")

# Upstash Redis untuk sync state ke dashboard admin (Vercel)
KV_URL = os.environ.get("KV_REST_API_URL", "").rstrip("/")
KV_TOKEN = os.environ.get("KV_REST_API_TOKEN", "")

def redis_cmd(cmd):
    """Eksekusi satu Redis command via Upstash REST API."""
    if not KV_URL or not KV_TOKEN:
        return None
    try:
        req = Request(KV_URL, data=json.dumps(cmd).encode(),
                      headers={"Authorization": f"Bearer {KV_TOKEN}", "Content-Type": "application/json"})
        with urlopen(req, timeout=10) as r:
            return json.loads(r.read()).get("result")
    except Exception:
        return None

def sync_redis(state):
    """Push state + antrian ke Redis supaya dashboard admin Vercel bisa baca."""
    if not KV_URL or not KV_TOKEN:
        return
    try:
        # state lengkap
        redis_cmd(["SET", "dusun:state", json.dumps(state, ensure_ascii=False)])
        # summary untuk dashboard
        summary = {
            "day": state.get("day", 1),
            "warga": len(state.get("residents", [])),
            "buildings": len(state.get("buildings", [])),
            "followers": state.get("followers", 0),
            "target": state.get("target", 1000),
            "updated": state.get("updated", datetime.now(WIB).strftime("%Y-%m-%d")),
        }
        redis_cmd(["SET", "dusun:summary", json.dumps(summary, ensure_ascii=False)])
        # antrian
        antrian = load_antrian()
        redis_cmd(["SET", "dusun:antrian", json.dumps(antrian, ensure_ascii=False)])
        # warga list (singkat)
        warga_list = [{"name": r.get("name"), "nick": r.get("nick", ""), "day": r.get("day", 1),
                       "roof": r.get("roof", ""), "wall": r.get("wall", "")}
                      for r in state.get("residents", [])]
        redis_cmd(["SET", "dusun:warga", json.dumps(warga_list, ensure_ascii=False)])
        log("  sync ke Redis OK")
    except Exception as e:
        log(f"  sync Redis gagal: {e}")

# Grid peta = identik dengan index.html (const T=40,N=91,C=45,S=6).
C = 45
S = 6
N = 91


def mod(a, m):
    return a % m


def is_road(x, y):
    return mod(x - C, S) == 0 or mod(y - C, S) == 0


def tiles_of(b):
    w = b.get("w") or 3
    return [(b["x"] + i, b["y"] + j) for i in range(w) for j in range(w)]

# warna yang dikenali -> kode warna peta (wall/roof)
WARNA = {
    "merah": "merah", "merah muda": "merah muda", "pink": "merah muda",
    "biru": "biru", "biru muda": "biru", "toska": "biru", "tosca": "biru",
    "hijau": "hijau", "hijau muda": "hijau",
    "kuning": "kuning", "orange": "kuning", "oranye": "kuning",
    "ungu": "ungu", "ungu muda": "ungu", "violet": "ungu",
    "putih": "putih", "hitam": "hitam", "abu": "abu", "abu-abu": "abu",
    "coklat": "coklat", "cokelat": "coklat", "krem": "krem",
}
DEFAULT_WALL = "putih"
DEFAULT_ROOF = "merah"


def log(msg):
    print(f"[{datetime.now(WIB).strftime('%H:%M:%S')}] {msg}")


def get_json(url):
    req = Request(url, headers={"User-Agent": "dusunkita.id-bot/1.0"})
    with urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def fb(url, params, token):
    """GET Facebook Graph API (bukan graph.instagram.com)."""
    q = dict(params)
    q["access_token"] = token
    return get_json("https://graph.facebook.com/v21.0/" + url + "?" + urlencode(q))


def resolve_ig(token, username="dusunkita.id"):
    """Cari IG business account berdasarkan username (bukan media terbanyak).

    Kembalikan (ig_id, page_token) atau (None, None).
    """
    pages = fb("me/accounts", {"fields": "id,name,access_token", "limit": 100}, token)
    for p in pages.get("data", []):
        ptok = p.get("access_token", token)
        try:
            r = fb(p["id"], {"fields": "instagram_business_account{id,username,media_count}"}, ptok)
            iba = r.get("instagram_business_account")
            if iba and iba.get("id"):
                uname = (iba.get("username") or "").lower()
                if username and uname == username.lower():
                    return iba["id"], ptok
                if not username:
                    return iba["id"], ptok
        except Exception:
            continue
    return None, None


def fetch_followers(token):
    """Ambil jumlah follower IG (untuk sync angka di web)."""
    try:
        ig_id, ptok = resolve_ig(token)
        if not ig_id:
            return None, None
        f = fb(ig_id, {"fields": "followers_count,username"}, ptok)
        if f.get("followers_count") is not None:
            return int(f["followers_count"]), f.get("username")
    except Exception:
        pass
    return None, None


def load_state():
    if os.path.exists(STATE):
        with open(STATE) as f:
            return json.load(f)
    return None


def save_state(s):
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    with open(STATE, "w") as f:
        json.dump(s, f, ensure_ascii=False, indent=2)


def fetch_comments(token, limit=5, max_pages=10):
    """Ambil komentar dari N postingan terbaru akun IG business.

    token = page access token (dari /me/accounts), yang sudah bisa akses
    instagram_business_account + instagram_manage_comments.
    """
    # 1. cari IG business account @dusunkita.id (pin username, bukan media terbanyak)
    ig_id, page_token = resolve_ig(token)
    if not ig_id:
        log("ERROR: IG @dusunkita.id tidak ditemukan. Link dulu ke FB Page 'Dusun Kita Virtual'.")
        return []
    log(f"  pakai IG business account {ig_id}")

    # 2. ambil media terbaru
    media = fb(f"{ig_id}/media", {
        "fields": "id,caption,timestamp,comments_count", "limit": limit
    }, page_token)

    rows = []
    fields = "id,text,timestamp,like_count,username,from{username},replies{id,text,timestamp,like_count,username,from{username}}"
    for m in media.get("data", []):
        mid = m["id"]
        url = f"{mid}/comments"
        pages_done = 0
        after = None
        while pages_done < max_pages:
            params = {"fields": fields, "limit": 50}
            if after:
                params["after"] = after
            j = fb(url, params, page_token)
            for c in j.get("data", []):
                u = ((c.get("from") or {}).get("username")) or c.get("username", "")
                rows.append({"t": c.get("timestamp"), "u": u, "x": c.get("text", ""), "l": c.get("like_count", 0), "rep": False})
                rp = c.get("replies")
                while rp:
                    for r in rp.get("data", []):
                        ru = ((r.get("from") or {}).get("username")) or r.get("username", "")
                        rows.append({"t": r.get("timestamp"), "u": ru, "x": r.get("text", ""), "l": r.get("like_count", 0), "rep": True})
                    rp = rp.get("paging", {}).get("next") and get_json(rp["paging"]["next"])
            nxt = j.get("paging", {}).get("cursors", {}).get("after")
            if not nxt:
                break
            after = nxt
            pages_done += 1

    rows.sort(key=lambda r: r.get("t") or "")
    return rows


def parse_warna(teks):
    """Deteksi warna bata (atap) dan tembok dari teks komentar."""
    t = teks.lower()
    roof, wall = None, None
    # pola "atap X tembok Y" / "bata X tembok Y" / "genteng X tembok Y"
    m = re.search(r"(?:atap|bata|genteng|roof)\s*(?:nya|warna)?\s*:?\s*([a-z]+(?:\s[a-z]+)?)", t)
    if m and m.group(1) in WARNA:
        roof = WARNA[m.group(1)]
    m2 = re.search(r"(?:tembok|wall|dinding|warna)\s*(?:nya|warna)?\s*:?\s*([a-z]+(?:\s[a-z]+)?)", t)
    if m2 and m2.group(1) in WARNA:
        wall = WARNA[m2.group(1)]
    return roof or DEFAULT_ROOF, wall or DEFAULT_WALL


def parse_warga(rows):
    """Dari komentar, hasilkan daftar warga baru (nama + warna)."""
    warga = []
    seen = set()
    for r in rows:
        if r["rep"]:
            continue  # cuma komentar utama
        u = (r.get("u") or "").strip()
        if not u:
            continue
        teks = (r.get("x") or "").strip()
        if len(teks) < 2:
            continue
        # skip komentar balasan petunjuk / admin
        if u.lower() in ("dusunkita.id",):
            continue
        roof, wall = parse_warna(teks)
        # nama = kata-kata sebelum warna, atau username
        nama = teks.split(",")[0].strip() if "," in teks else teks
        nama = re.sub(r"(?:atap|bata|genteng|tembok|wall|roof|warna)[^,]*", "", nama, flags=re.I).strip()
        nama = nama or u
        nama = re.sub(r"\s+", " ", nama).strip()[:40]
        if u.lower() in seen:
            continue
        seen.add(u.lower())
        warga.append({"name": u, "nick": nama, "roof": roof, "wall": wall, "teks": teks, "day": None})
    return warga


def next_slot(state):
    """Cari pekarangan kosong (x,y) sesuai grid peta index.html.

    Mirip logika PLOTS di index.html: kavling = bukan jalan + bukan RESERVED,
    dipilih dari yang terdekat ke pusat (C,C).
    """
    residents = state.get("residents", []) or []
    buildings = state.get("buildings", []) or []
    occ = {(r["x"], r["y"]) for r in residents}
    used = set()
    for b in buildings:
        for t in tiles_of(b):
            used.add(t)
    # RESERVED: posisi OWNER (C+1,C+1) + sekitar warung/pos ronda (dari index.html)
    reserved = {(C + 1, C + 1), (C - 1, C + 1), (C + 1, C - 1), (C - 1, C - 1)}
    for (x0, y0) in [(C + 2, C - 4), (C - 4, C + 2)]:
        for i in range(3):
            for j in range(3):
                reserved.add((x0 + i, y0 + j))

    plots = []
    for x in range(1, N - 1):
        for y in range(1, N - 1):
            if is_road(x, y) or (x, y) in reserved:
                continue
            lx = mod(x - C, S)
            ly = mod(y - C, S)
            if not (lx == 1 or lx == 5 or ly == 1 or ly == 5):
                continue
            if max(abs(x - C), abs(y - C)) > 43:
                continue
            if (x, y) in occ or (x, y) in used:
                continue
            plots.append((x, y, abs(x - C) + abs(y - C)))

    plots.sort(key=lambda p: p[2])
    if plots:
        return plots[0][0], plots[0][1]
    # fallback: grid sederhana kalau penuh
    return C + (len(occ) % S), C + (len(occ) // S)


ANTRIAN = os.path.join(ROOT, "scripts", "antrian.json")


def load_antrian():
    if os.path.exists(ANTRIAN):
        with open(ANTRIAN) as f:
            return json.load(f)
    return []


def save_antrian(a):
    os.makedirs(os.path.dirname(ANTRIAN), exist_ok=True)
    with open(ANTRIAN, "w") as f:
        json.dump(a, f, ensure_ascii=False, indent=2)


def main():
    dry = "--dry-run" in sys.argv
    no_push = "--no-push" in sys.argv
    mode_antrian = "--antrian" in sys.argv
    mode_apply = "--apply" in sys.argv

    token = os.environ.get("IG_TOKEN", "").strip()
    if not token:
        log("ERROR: IG_TOKEN belum di-set. Export dulu: export IG_TOKEN=IGAA...")
        sys.exit(1)

    state = load_state()
    if not state:
        log("ERROR: scripts/state.json belum ada. Jalankan generate_data.py --reset dulu.")
        sys.exit(1)

    # MODE ANTRIAN: scrape -> simpan ke antrian.json (tanpa ubah state)
    if mode_antrian:
        log("Mengambil komentar -> antrian.json ...")
        rows = fetch_comments(token)
        log(f"  {len(rows)} komentar/balasan diambil")
        warga = parse_warga(rows)
        existing = {r["name"].lower() for r in state.get("residents", [])}
        antrian = load_antrian()
        seen = {a["name"].lower() for a in antrian}
        baru = 0
        for w in warga:
            if w["name"].lower() in existing or w["name"].lower() in seen:
                continue
            antrian.append({
                "name": w["name"], "nick": w["nick"],
                "roof": w["roof"], "wall": w["wall"],
                "teks": w.get("teks", ""), "at": datetime.now(WIB).isoformat(),
                "status": "pending",
            })
            seen.add(w["name"].lower())
            baru += 1
        save_antrian(antrian)
        log(f"  +{baru} antrian baru (total antrian: {len(antrian)})")
        # sync antrian ke Redis
        sync_redis(state)
        log("Selesai (antrian.json). Review di dashboard, lalu jalankan --apply.")
        return

    # MODE APPLY: ambil antrian ber-status 'approved' -> masuk state -> push
    if mode_apply:
        antrian = load_antrian()
        approved = [a for a in antrian if a.get("status") == "approved"]
        if not approved:
            log("Tidak ada antrian ber-status approved. Setujui dulu di dashboard/antrian.json.")
            return
        existing = {r["name"].lower() for r in state.get("residents", [])}
        day = state.get("day", 1)
        added = 0
        for a in approved:
            if a["name"].lower() in existing:
                continue
            x, y = next_slot(state)
            state["residents"].append({
                "name": a["name"], "x": x, "y": y, "day": day,
                "nick": a["nick"], "roof": a["roof"], "wall": a["wall"],
            })
            existing.add(a["name"].lower())
            added += 1
        # tandai approved -> applied, hapus rejected
        state["day"] += 1
        state["updated"] = datetime.now(WIB).strftime("%Y-%m-%d")
        fl, uname = fetch_followers(token)
        if fl is not None:
            state["followers"] = fl
            log(f"  follower: {fl} (@{uname})")
        save_state(state)
        # bersihkan antrian yang sudah diproses
        antrian = [a for a in antrian if a.get("status") == "pending"]
        save_antrian(antrian)
        log(f"  +{added} warga di-apply (hari -> {state['day']})")

        js = "window.NK_DATA = " + json.dumps(state, ensure_ascii=False, indent=1) + ";"
        with open(OUT, "w") as f:
            f.write(js)
        log(f"  data.js ditulis ({os.path.getsize(OUT)} bytes)")

        # sync ke Redis supaya dashboard admin Vercel bisa baca
        sync_redis(state)

        if not no_push:
            branch = os.environ.get("GH_BRANCH", "main")
            subprocess.run(["git", "-C", ROOT, "add", "data.js"], check=True)
            r = subprocess.run(["git", "-C", ROOT, "commit", "-m", f"Hari ke-{state['day']}: +{added} warga baru"], capture_output=True, text=True)
            if r.returncode == 0:
                subprocess.run(["git", "-C", ROOT, "push", "origin", branch], check=True)
                log(f"  pushed ke {branch}")
            else:
                log("  (tidak ada perubahan untuk di-commit)")
        log("Selesai (apply).")
        return

    # MODE DEFAULT: scrape -> langsung apply (tanpa antrian)
    log("Mengambil komentar...")
    rows = fetch_comments(token)
    log(f"  {len(rows)} komentar/balasan diambil")

    warga = parse_warga(rows)
    log(f"  {len(warga)} warga baru terdeteksi")

    if dry:
        for w in warga[:20]:
            log(f"  DRY: @{w['name']} nick='{w['nick']}' bata={w['roof']} tembok={w['wall']}")
        log("DRY-RUN selesai (tidak ada perubahan)")
        return

    existing = {r["name"].lower() for r in state.get("residents", [])}
    added = 0
    day = state.get("day", 1)
    for w in warga:
        if w["name"].lower() in existing:
            continue
        x, y = next_slot(state)
        state["residents"].append({
            "name": w["name"], "x": x, "y": y, "day": day,
            "nick": w["nick"], "roof": w["roof"], "wall": w["wall"],
        })
        existing.add(w["name"].lower())
        added += 1

    state["day"] += 1
    state["updated"] = datetime.now(WIB).strftime("%Y-%m-%d")
    # sync follower dari IG
    fl, uname = fetch_followers(token)
    if fl is not None:
        state["followers"] = fl
        log(f"  follower: {fl} (@{uname})")
    save_state(state)
    log(f"  +{added} warga ditambahkan (hari -> {state['day']})")

    js = "window.NK_DATA = " + json.dumps(state, ensure_ascii=False, indent=1) + ";"
    with open(OUT, "w") as f:
        f.write(js)
    log(f"  data.js ditulis ({os.path.getsize(OUT)} bytes)")

    # sync ke Redis supaya dashboard admin Vercel bisa baca
    sync_redis(state)

    if no_push:
        log("--no-push: selesai tanpa push.")
        return

    branch = os.environ.get("GH_BRANCH", "main")
    subprocess.run(["git", "-C", ROOT, "add", "data.js"], check=True)
    r = subprocess.run(["git", "-C", ROOT, "commit", "-m", f"Hari ke-{state['day']}: +{added} warga baru"], capture_output=True, text=True)
    if r.returncode == 0:
        subprocess.run(["git", "-C", ROOT, "push", "origin", branch], check=True)
        log(f"  pushed ke {branch}")
    else:
        log("  (tidak ada perubahan untuk di-commit)")
    log("Selesai.")


if __name__ == "__main__":
    main()

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
G = "https://graph.instagram.com/"

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
    # 1. cari IG business account yang terhubung ke page (pilih yang punya media)
    pages = fb("me/accounts", {"fields": "id,name,access_token", "limit": 100}, token)
    page_token = token
    ig_id = None
    best = None  # (media_count, ig_id, page_token)
    for p in pages.get("data", []):
        try:
            r = fb(p["id"], {"fields": "instagram_business_account{id,username,media_count}"}, p.get("access_token", token))
            iba = r.get("instagram_business_account")
            if iba and iba.get("id"):
                mc = int(iba.get("media_count") or 0)
                if best is None or mc > best[0]:
                    best = (mc, iba["id"], p.get("access_token", token))
        except Exception:
            continue
    if not best:
        log("ERROR: tidak ada IG business account terhubung ke page. Link dulu @dusunkita.id ke FB Page.")
        return []
    ig_id, page_token = best[1], best[2]
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
        warga.append({"name": u, "nick": nama, "roof": roof, "wall": wall, "day": None})
    return warga


def next_slot(state):
    """Cari pekarangan kosong (x,y) di grid kampung."""
    used = {(r["x"], r["y"]) for r in state.get("residents", [])}
    # grid 50 pekarangan: 10 kolom x 5 baris, mulai offset 44,44 seperti referensi
    for i in range(50):
        x = 44 + (i % 10)
        y = 44 + (i // 10)
        if (x, y) not in used:
            return x, y
    return 44 + (len(used) % 10), 44 + (len(used) // 10)


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
        save_state(state)
        # bersihkan antrian yang sudah diproses
        antrian = [a for a in antrian if a.get("status") == "pending"]
        save_antrian(antrian)
        log(f"  +{added} warga di-apply (hari -> {state['day']})")

        js = "window.NK_DATA = " + json.dumps(state, ensure_ascii=False, indent=1) + ";"
        with open(OUT, "w") as f:
            f.write(js)
        log(f"  data.js ditulis ({os.path.getsize(OUT)} bytes)")

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
    state["followers"] = state.get("followers", 1)
    save_state(state)
    log(f"  +{added} warga ditambahkan (hari -> {state['day']})")

    js = "window.NK_DATA = " + json.dumps(state, ensure_ascii=False, indent=1) + ";"
    with open(OUT, "w") as f:
        f.write(js)
    log(f"  data.js ditulis ({os.path.getsize(OUT)} bytes)")

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

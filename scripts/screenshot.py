#!/usr/bin/env python3
"""Auto-screenshot peta Dusun Kita (1080x1920) untuk footage reels.

Jalankan dari VPS:
  python3 scripts/screenshot.py                  # screenshot peta hari ini
  python3 scripts/screenshot.py --day 3          # simulasi (QA, ?harta=qa)
  python3 scripts/screenshot.py --zoom-out       # view seluruh kampung
  python3 scripts/screenshot.py --output /tmp/p.png

Output: PNG 1080x1920 (9:16) — siap di-edit di CapCut/Premiere sebagai shot 1/5.

Cron: /root/.hermes/scripts/dk_screenshot.sh (daily 15:00 WIB)
"""
import os, sys, json, argparse, datetime, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "screenshots")
WEB = os.environ.get("DK_WEB", "https://dusunkita.vercel.app")
WIB = datetime.timezone(datetime.timedelta(hours=7))

def load_state():
    p = os.path.join(ROOT, "scripts", "state.json")
    return json.load(open(p)) if os.path.exists(p) else {}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--zoom-out", action="store_true", help="view seluruh kampung (fit)")
    ap.add_argument("--output", default="", help="path output (default: screenshots/peta-HHMM-YYYYMMDD.png)")
    ap.add_argument("--qa", action="store_true", help="tambah ?harta=qa&kat=waduk&emas=1")
    args = ap.parse_args()

    state = load_state()
    day = state.get("day", 1)

    # output path
    now = datetime.datetime.now(WIB)
    if args.output:
        out = args.output
    else:
        os.makedirs(OUT_DIR, exist_ok=True)
        out = os.path.join(OUT_DIR, f"peta-hari{day}-{now.strftime('%Y%m%d-%H%M')}.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)

    # buka web via headless chromium
    from playwright.sync_api import sync_playwright

    url = WEB + "/"
    if args.qa:
        url += "?harta=qa&kat=waduk&emas=1"

    with sync_playwright() as p:
        b = p.chromium.launch(args=["--no-sandbox"])
        pg = b.new_page(viewport={"width": 1080, "height": 1920}, device_scale_factor=1)
        pg.goto(url, wait_until="networkidle", timeout=60000)
        # tunggu peta render (canvas)
        pg.wait_for_timeout(3000)
        # zoom out view (klik tombol fit-all) atau scroll ke tengah
        try:
            # klik tombol "Lihat seluruh kampung" kalau ada
            pg.click("button[title='Lihat seluruh kampung'], button:has-text('⌂')", timeout=3000, force=True)
            pg.wait_for_timeout(1500)
        except Exception:
            pass
        # screenshot seluruh page (9:16 = peta dominan)
        pg.screenshot(path=out, full_page=False, clip={"x":0,"y":0,"width":1080,"height":1920})
        b.close()

    size = os.path.getsize(out)
    print(f"Screenshot: {out}")
    print(f"Ukuran: {size//1024} KB ({size} bytes)")
    print(f"Hari: ke-{day}, warga: {len(state.get('residents',[]))}, bangunan: {len(state.get('buildings',[]))}")
    print(f"Siap di-edit sebagai shot footage reels EP-{state.get('day',1):03d}")

if __name__ == "__main__":
    main()

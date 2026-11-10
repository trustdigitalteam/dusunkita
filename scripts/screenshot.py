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
        pg.wait_for_selector("#map", timeout=30000)
        pg.wait_for_timeout(3500)

        # ===== mode: peta saja (default) / seluruh halaman =====
        if not args.full:
            # screenshot element #map saja (peta polos, tanpa UI chrome)
            # padasi kanvas jadi 9:16 (1080x1920) biar pas reels
            el = pg.query_selector("#map")
            box = el.bounding_box()
            # scale canvas ke lebar 1080, tinggi proporsional, lalu crop/pad 9:16
            el.screenshot(path=out, omit_background=False)
            b.close()
            # post-process: pad jadi 1080x1920 (9:16) dengan background senja
            _pad_to_reels(out)
            size = os.path.getsize(out)
            print(f"Peta saja: {out}")
            print(f"Ukuran: {size//1024} KB · {os.path.basename(out)} · peta polos #map")
            print(f"Hari ke-{day}, warga: {len(state.get('residents',[]))}, bangunan: {len(state.get('buildings',[]))}")
            print("Siap jadi footage reels EP-%03d (overlay ditambahkan di Remotion)." % day)
            return
        else:
            # mode full: zoom-out + screenshot halaman
            try:
                pg.click("button[title='Lihat seluruh kampung'], button:has-text('⌂')", timeout=3000, force=True)
                pg.wait_for_timeout(1500)
            except Exception:
                pass
            pg.screenshot(path=out, full_page=False, clip={"x":0,"y":0,"width":1080,"height":1920})
            b.close()
            size = os.path.getsize(out)
            print(f"Screenshot full: {out} ({size//1024} KB)")
            print("Siap di-edit sebagai shot footage reels EP-%03d" % day)
            return


def _pad_to_reels(path):
    """Pad/crop PNG peta ke 1080x1920 (9:16) dengan background senja tropis."""
    from PIL import Image
    im = Image.open(path).convert("RGB")
    W, H = 1080, 1920
    # scale ke lebar 1080, tinggi proporsional
    rw, rh = im.size
    scale = W / rw
    im2 = im.resize((W, max(1, int(rh * scale))), Image.LANCZOS)
    # canvas 9:16, isi warna senja (gradient sederhana: atas senja oranye → bawah tanah)
    canvas = Image.new("RGB", (W, H), (58, 74, 53))
    # gradasi vertikal senja
    top = (92, 74, 94)      # ungu senja
    bot = (58, 74, 53)       # hijau gelap
    for y in range(H):
        t = y / H
        r = int(top[0] * (1 - t) + bot[0] * t)
        g = int(top[1] * (1 - t) + bot[1] * t)
        b = int(top[2] * (1 - t) + bot[2] * t)
        for x in range(W):
            canvas.putpixel((x, y), (r, g, b))
    # tempel peta di tengah (vertikal center)
    ph = im2.size[1]
    oy = max(0, (H - ph) // 2)
    canvas.paste(im2, (0, min(oy, H - ph)))
    canvas.save(path)

if __name__ == "__main__":
    main()

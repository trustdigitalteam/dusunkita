#!/usr/bin/env python3
"""Dusun Kita — generate data.js kampung.

Menghasilkan data.js dari state JSON (scripts/state.json) dengan brand Dusun Kita.
Pemakaian:
  python3 scripts/generate_data.py            # baca state.json -> data.js
  python3 scripts/generate_data.py --reset    # reset ke hari-1 kosong
State disimpan di scripts/state.json supaya data warga bertambah tiap hari.
"""
import json, re, sys, os
from datetime import datetime, timezone, timedelta

WIB = timezone(timedelta(hours=7))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "scripts", "state.json")
OUT = os.path.join(ROOT, "data.js")

BASE = {
    "version": 1,
    "account": "dusunkita",
    "day": 1,
    "updated": "",
    "kavling": 50,
    "followers": 1,
    "target": 1000,
    "supOthers": 0,
    "tontonan": {"akun": [], "items": []},
    "trakteer": {"url": "https://trakteer.id/dusunkita", "unit": "Bata"},
    "voucher": {"url": "", "label": ""},
    "toko": {"csv": "", "form": "", "fUser": "", "fKode": ""},
    "quest": {},
    "goalKampung": {"judul": "Bantu Pak RT Bangun Balai Dusun", "target": 100, "awal": 0},
    "setir": True,
    "gento": True,
    "gentoMain": True,
    "live": {"url": "", "label": "", "jadwal": ""},
    "gaji": {"default": 2, "warung": 2, "ronda": 2, "bakso": 2, "padang": 2, "marbot": 2, "kerja bakti": 2},
    "loker": [],
    "lowongan": {"url": ""},
    "dusun": [],
    "residents": [],
    "buildings": [],
    "awards": [],
    "juraganHistory": [],
}


def load_state():
    if os.path.exists(STATE):
        with open(STATE) as f:
            return json.load(f)
    return dict(BASE)


def save_state(s):
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    with open(STATE, "w") as f:
        json.dump(s, f, ensure_ascii=False, indent=2)


def main():
    reset = "--reset" in sys.argv
    if reset:
        s = dict(BASE)
        s["updated"] = datetime.now(WIB).strftime("%Y-%m-%d")
        save_state(s)
        print("State di-reset ke hari-1 kosong.")
    else:
        s = load_state()
        s["day"] += 1
        s["updated"] = datetime.now(WIB).strftime("%Y-%m-%d")
        save_state(s)
        print(f"Hari ke-{s['day']} (updated {s['updated']}).")

    js = "window.NK_DATA = " + json.dumps(s, ensure_ascii=False, indent=1) + ";"
    with open(OUT, "w") as f:
        f.write(js)
    print(f"data.js ditulis ({os.path.getsize(OUT)} bytes).")


if __name__ == "__main__":
    main()

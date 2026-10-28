#!/usr/bin/env python3
"""Generate brief konten reels harian untuk Dusun Kita.

Baca state.json (atau Redis kalau VPS) → output docs/EPISODE-NNNN.md
Isi: shot list + voiceover + caption + brief Claude-video — semua auto dari
keadaan dusun hari itu.

Jalankan dari VPS:
  python3 scripts/konten.py                     # brief episode terbaru
  python3 scripts/konten.py --ep 1              # episode spesifik
  python3 scripts/konten.py --dry               # cetak ke stdout, jangan save
"""
import json, os, sys, datetime, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WIB = datetime.timezone(datetime.timedelta(hours=7))

HASHTAGS = ["#dusunkita", "#kartukomen", "#desadigital", "#komunitasindonesia",
            "#wargadasar", "#kampungvirtual", "#worldbuilding", "#interaktif",
            "#gameindonesia", "#desaseni"]

# ---------- state ----------
def load_state():
    p = os.path.join(ROOT, "scripts", "state.json")
    with open(p) as f:
        return json.load(f)

def hari_wib():
    return datetime.datetime.now(WIB)

def warga_baru_hari(state, day):
    """Warga yang masuk di hari ke-<day> (atau hari ini)."""
    return [r for r in state.get("residents", []) if r.get("day") == day]

def bangunan_nya(state):
    """Ringkasan bangunan + starter (Pos Ronda & Warung)."""
    blds = state.get("buildings", [])
    if not blds:
        return ["Pos Ronda", "Warung"]  # STARTER di index.html
    return [b.get("name", b.get("type", "?")) for b in blds]

def kejutan_terdekat(state):
    """Ambil KEJUTAN dari index.html (hardcoded)."""
    idx = open(os.path.join(ROOT, "index.html")).read()
    m = re.search(r"const KEJUTAN=\[(.*?)\];", idx, re.S)
    if not m:
        return []
    items = re.findall(r"\{d:'([^']*)',ic:'([^']*)',q:'([^']*)',n:'([^']*)'([^}]*)\}", m.group(1))
    out = []
    for d, ic, q, n, extra in items:
        out.append({"d": d, "ic": ic, "q": q, "n": n, "buka": "buka:true" in extra})
    return out

def kejutan_hari(state, date_str):
    for k in kejutan_terdekat(state):
        if k["d"] == date_str:
            return k
    return None

# ---------- episode ----------
def episode_no():
    ep_dir = os.path.join(ROOT, "docs", "episodes")
    os.makedirs(ep_dir, exist_ok=True)
    nums = [int(m) for f in os.listdir(ep_dir) if (m := re.search(r"(\d+)", f))]
    return (max(nums) + 1) if nums else 1

def fmt_warga_short(ws, max_n=3):
    if not ws:
        return "belum ada"
    lines = []
    for w in ws[:max_n]:
        c = f" — bata {w.get('roof', '?')}, tembok {w.get('wall', '?')}"
        nick = f" ({w['nick']})" if w.get("nick") else ""
        lines.append(f"@{w['name']}{nick}{c}")
    if len(ws) > max_n:
        lines.append(f"+ {len(ws) - max_n} warga lainnya")
    return "\n".join(lines)

def build_ep(ep, state):
    now = hari_wib()
    date_str = now.strftime("%Y-%m-%d")
    day = state.get("day", 1)
    residents = state.get("residents", [])
    n_res = len(residents)
    baru = warga_baru_hari(state, day)
    blds = bangunan_nya(state)
    n_bld = len(blds)
    fol = state.get("followers", 0)
    goal = state.get("goalKampung", {})
    g_judul = goal.get("judul", "Bangun Balai Dusun")
    g_target = goal.get("target", 100)
    g_awal = goal.get("awal", 0)
    sup = state.get("supOthers", 0)
    kej = kejutan_hari(state, date_str)
    quest = state.get("quest") or {}
    loker = state.get("loker", [])
    akun = state.get("account", "dusunkita.id")

    # pilih fokus episode:
    if not residents:
        focus = "pembukaan"
    elif baru:
        focus = "warga_baru"
    elif kej and not kej["buka"]:
        focus = "kejutan"
    elif loker:
        focus = "loker"
    elif quest.get("tanggal"):
        focus = "quest"
    else:
        focus = "progres"

    # ---------- SHOT LIST ----------
    shots = []
    if focus == "pembukaan":
        shots.append(("Hook", "Peta Dusun Kita dari atas. Kosong. Palet senja.",
                      f"DUSUN KITA DIBUKA 🏘️\nHari ke-{day} · {n_res} warga",
                      f"Assalamualaikum. Saya Pak RT. Dusun Kita resmi dibuka hari ke-{day}."))
        shots.append(("Fasilitas", "Zoom ke bangunan awal.",
                      f"Mulai dari awal:\n" + "\n".join(f"✅ {b}" for b in blds[:4]),
                      f"Jauh dari keramaian, ini kampung kami. Sudah ada {' dan '.join(blds[:2])}."))
        shots.append(("Cara Gabung", "Animasi teks cara ikut.",
                      f"CARA JADI WARGA:\n1. Follow @{akun}\n2. Komen:\nNAMA, BATA <warna>, TEMBOK <warna>",
                      f"Cara ikut gampang. Follow @{akun}, komen nama dan warna rumah kamu."))
        shots.append(("Goal", f"Highlight lokasi goal: {g_judul}.",
                      f"GOAL KAMPUNG:\n{g_judul.upper()}\nTarget: {g_target} Bata",
                      f"Target kami: {g_judul.lower()}. Butuh {g_target} Bata."))
    elif focus == "warga_baru":
        shots.append(("Hook", f"Screenshot peta, zoom ke {len(baru)} rumah baru.",
                      f"HARI KE-{day} · {n_res} WARGA",
                      f"Hari ke-{day} di Dusun Kita. Ada {len(baru)} warga baru hari ini."))
        shots.append(("Perkenalan", "Zoom tiap rumah baru, tampilkan nama.",
                      "Warga baru hari ini:\n" + fmt_warga_short(baru),
                      "Selamat datang di Dusun Kita. " + " ".join("@" + w["name"] for w in baru[:3]) + "."))
        shots.append(("Goal", f"Progress {g_judul}.",
                      f"{g_judul.upper()}\n{sup}/{g_target} Bata",
                      f"Progress {g_judul.lower()}: {sup} dari {g_target} Bata."))
    elif focus == "kejutan":
        shots.append(("Hook", "Peta malam, suasana mistis ringan.",
                      f"{kej['ic']} HARI INI {date_str[8:]:.>2}/{date_str[5:]:.>2} WIB",
                      kej["q"]))
        shots.append(("Penjelasan", "Teks besar info kejutan.",
                      f"KEJUTAN MALAM INI:\n{kej['n'].upper()}",
                      f"Jam 19.00 nanti ada kejutan: {kej['n'].lower()}."))
        shots.append(("CTA", "Logo + URL.",
                      f"Siapin Kartu Komen 🔑\n@{akun}",
                      "Wajib login Kartu Komen biar bisa ikutan."))
    elif focus == "loker":
        j = loker[0]
        shots.append(("Hook", "Papan loker di peta.",
                      f"🔨 LOKER DUSUN\nDibutuhkan: {j.get('title', '?')}",
                      f"Ada lowongan di Dusun Kita: {j.get('title', 'posisi baru')}."))
        shots.append(("Detail", "Deskripsi loker.",
                      f"{j.get('note', '')}",
                      j.get("note", "Kirim lamaran via Kartu Komen.")))
    else:  # progres
        shots.append(("Hook", "Screenshot peta full.",
                      f"HARI KE-{day} · {n_res} WARGA\n{sup}/{g_target} Bata",
                      f"Update Dusun Kita hari ke-{day}."))
        shots.append(("Progres", "Zoom area berkembang.",
                      f"{g_judul.upper()}\n{sup}/{g_target} Bata ({round(sup*100/g_target)}%)",
                      f"{g_judul}: {sup} dari {g_target} Bata."))
    # CTA akhir (semua fokus)
    shots.append(("CTA", "Logo Dusun Kita, peta zoom out.",
                  f"Komen sekarang:\nNAMA, BATA <warna>, TEMBOK <warna>\n\n@{akun}",
                  f"Yuk gabung Dusun Kita. Komen sekarang, rumah kamu nunggu."))

    # ---------- CAPTION ----------
    if focus == "pembukaan":
        caption = f"""Dusun Kita dibuka! 🏘️

Hari ke-{day}. Kami mulai dari nol — {' dan '.join(blds[:2])} saja.

Cara gabung:
1️⃣ Follow @{akun}
2️⃣ Komen: NAMA, BATA <warna>, TEMBOK <warna>

Contoh: Budi, bata merah, tembok biru

Besok pagi rumah kamu muncul di peta.

{g_judul}: {sup}/{g_target} Bata 🧱

@dusunkita.id
"""
    elif focus == "warga_baru":
        caption = f"""Hari ke-{day} di Dusun Kita 🏘️

{n_res} warga · {n_bld} bangunan · {fol} follower

Warga baru hari ini:
{fmt_warga_short(baru, 4)}

{g_judul}: {sup}/{g_target} Bata 🧱

Komen untuk gabung:
NAMA, BATA <warna>, TEMBOK <warna>

dusunkita.vercel.app
"""
    elif focus == "kejutan":
        caption = f"""{kej['ic']} {kej['n'].upper()} — {date_str} 🏘️

{kej['q']}

Jam 19.00 WIB. Wajib login Kartu Komen 🔑

@{akun}
"""
    elif focus == "loker":
        j = loker[0]
        caption = f"""🔨 LOKER DUSUN — {j.get('title', '?')}

{g_judul}: {sup}/{g_target} Bata

Kirim lamaran via Kartu Komen.

@dusunkita.id
"""
    else:
        caption = f"""Update Dusun Kita — Hari ke-{day} 🏘️

{n_res} warga · {n_bld} bangunan · {fol} follower
{g_judul}: {sup}/{g_target} Bata ({round(sup*100/g_target)}%)

Komen untuk gabung:
NAMA, BATA <warna>, TEMBOK <warna>

dusunkita.vercel.app
"""

    hashtags = " ".join(HASHTAGS)

    # ---------- BRIEF CLAUDE VIDEO ----------
    brief = f"""# Brief Video Dusun Kita — Episode {ep:03d}

## State
- Hari ke-{day} ({date_str})
- {n_res} warga
- {n_bld} bangunan: {', '.join(blds[:5])}
- {fol} follower
- Goal: {g_judul} ({sup}/{g_target} Bata)
- Focus episode: {focus}
"""
    if kej:
        brief += f"- Kejutan malam ini: {kej['ic']} {kej['n']}\n"
    if quest:
        brief += f"- Quest: {quest.get('name', 'UFO')} {quest.get('tanggal', '')}\n"

    brief += """
## Shot List
"""
    for i, (judul, vis, overlay, vo) in enumerate(shots, 1):
        brief += f"\n### Shot {i} — {judul}\n**Visual:** {vis}\n**Overlay:**\n```\n{overlay}\n```\n**Voiceover:** \"{vo}\"\n"

    brief += f"""
## Caption
```
{caption.strip()}
{hashtags}
```

## Brand
- Palet: senja tropis (#8B3A2E, #D4762A, #E8D4B0, #7A4A2C)
- Tokoh: Pak RT
- Web: dusunkita.vercel.app
- Logo: https://dusunkita.vercel.app/logo.png
- 30 detik, 9:16, 1080x1920, 30fps
"""
    return brief, caption, shots, focus

def main():
    dry = "--dry" in sys.argv
    ep = 1
    if "--ep" in sys.argv:
        ep = int(sys.argv[sys.argv.index("--ep") + 1])
    state = load_state()
    brief, caption, shots, focus = build_ep(ep, state)
    out = f"docs/episodes/EP-{ep:03d}.md"
    if dry:
        print(brief)
        print("\n---CAPTION---\n")
        print(caption)
    else:
        os.makedirs(os.path.join(ROOT, "docs", "episodes"), exist_ok=True)
        with open(os.path.join(ROOT, out), "w") as f:
            f.write(brief)
        print(f"Tulis {out} (focus: {focus})")
        print(f"Episode berikutnya: {ep + 1}")

if __name__ == "__main__":
    main()

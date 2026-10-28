#!/usr/bin/env python3
"""Render video reels Dusun Kita dari brief episode + screenshot peta.

Baca docs/episodes/EP-NNN.md (shot list + overlay) → generate:
  - PNG overlay per shot (Pillow)
  - MP4 1080x1920 30fps (ffmpeg), shot 5× 6 detik = 30 detik
  - BGM: silent (voiceover manual / tambah BGM sendiri)

Jalankan:
  python3 scripts/render_video.py --ep 1
Output: videos/EP-001.mp4
"""
import json, os, re, sys, argparse, datetime
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1080, 1920
FPS = 30
SHOT_SEC = 6

def load_ep(ep_num):
    p = os.path.join(ROOT, f"docs/episodes/EP-{ep_num:03d}.md")
    if not os.path.exists(p):
        print(f"EP-{ep_num:03d}.md tidak ada. Jalankan: python3 scripts/konten.py")
        sys.exit(1)
    text = open(p).read()
    shots = []
    parts = re.split(r"\n### Shot \d+ — ", text)[1:]
    for i, part in enumerate(parts, 1):
        first_line = part.split("\n", 1)[0].strip()
        judul = first_line
        visual = ""
        m = re.search(r"\*\*Visual:\*\*\s*(.+)", part)
        if m: visual = m.group(1).strip()
        ov = ""
        mo = re.search(r"\*\*Overlay:\*\*\s*\n```\s*(.*?)```", part, re.S)
        if mo: ov = mo.group(1).strip()
        vo = ""
        mv = re.search(r'\*\*Voiceover:\*\*\s*"?(.+?)"?\s*$', part, re.M)
        if mv: vo = mv.group(1).strip().strip('"')
        shots.append({"idx": i, "judul": judul, "visual": visual, "overlay": ov, "voiceover": vo})
    return shots, text

def get_screenshot(ep_num, idx):
    """Ambil screenshot terbaru dari folder, atau fallback ke shot1."""
    ss_dir = os.path.join(ROOT, "screenshots")
    if not os.path.exists(ss_dir):
        return None
    files = sorted(f for f in os.listdir(ss_dir) if f.startswith("shot") and f.endswith(".png"))
    if not files:
        files = sorted(f for f in os.listdir(ss_dir) if f.startswith("peta") and f.endswith(".png"))
    if not files:
        print("Tidak ada screenshot. Jalankan: python3 scripts/screenshot.py")
        sys.exit(1)
    # pakai shot sesuai idx, fallback ke shot1
    name = f"shot{idx}-"
    match = [f for f in files if f.startswith(name)]
    if match:
        return os.path.join(ss_dir, match[0])
    return os.path.join(ss_dir, files[0])  # fallback

def make_overlay(idx, judul, overlay_text, path):
    """Buat overlay PNG 1080x1920: background semi-transparan + text overlay."""
    bg = Image.new("RGBA", (W, H), (0,0,0,0))
    dr = ImageDraw.Draw(bg)
    # cari font
    font_big = None; font_med = None; font_sm = None
    for fp in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
               "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"]:
        if os.path.exists(fp):
            try:
                font_big = ImageFont.truetype(fp, 56)
                font_med = ImageFont.truetype(fp, 36)
                font_sm  = ImageFont.truetype(fp, 28)
            except Exception:
                pass
            break
    if font_big is None:
        font_big = ImageFont.load_default(); font_med = font_big; font_sm = font_big

    # box transparan di tengah
    lines = (overlay_text or "").split("\n")
    box_h = 80 + len(lines)*60
    box_y = H//2 - box_h//2
    dr.rounded_rectangle([80, box_y, W-80, box_y+box_h], radius=30, fill=(28,37,32,220))
    # judul
    dr.text((W//2, box_y+30), f"Shot {idx} · {judul}", font=font_sm, fill=(242,194,48,255), anchor="mt")
    # overlay text
    y = box_y + 80
    for ln in lines:
        dr.text((W//2, y), ln, font=font_big, fill=(255,255,255,255), anchor="mt")
        y += 60
    bg.save(path)
    return path

def render_mp4(ep_num, shots):
    out_dir = os.path.join(ROOT, "videos"); os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, f"EP-{ep_num:03d}.mp4")
    overlay_files = []
    for i, s in enumerate(shots, 1):
        ss = get_screenshot(ep_num, i)
        ov = os.path.join(out_dir, f"ep{ep_num:03d}-shot{i}-overlay.png")
        if ss:
            make_overlay(i, s["judul"], s.get("overlay",""), ov)
        overlay_files.append((ss, ov))
    # ffmpeg: each shot 6 detik (loop screenshot + overlay), concat
    import subprocess
    cmd = ["ffmpeg","-y","-loglevel","error"]
    for j,(ss,ov) in enumerate(overlay_files):
        if ss:
            cmd += ["-loop","1","-framerate","30","-t",str(SHOT_SEC),"-i",ss]
        # overlay
        cmd += ["-loop","1","-framerate","30","-t",str(SHOT_SEC),"-i",ov]
    # filter: overlay + concat
    n = len(overlay_files)
    filter_parts = []
    for j in range(n):
        ss_i = j*2; ov_i = j*2+1
        filter_parts.append(f"[{ss_i}:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}[s{j}]")
        filter_parts.append(f"[s{j}][{ov_i}:v]overlay=0:0[sh{j}]")
    concat = "".join(f"[sh{j}]" for j in range(n))
    filter_parts.append(f"{concat}concat=n={n}:v=1:a=0[out]")
    cmd += ["-filter_complex",";".join(filter_parts),"-map","[out]","-r","30",
            "-c:v","libx264","-pix_fmt","yuv420p","-crf","20","-preset","fast",
            "-t",str(n*SHOT_SEC),out]
    print("Rendering:", " ".join(cmd[:10]), "…")
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("FFMPEG ERROR:", r.stderr[-800:])
        sys.exit(1)
    sz = os.path.getsize(out)
    print(f"✅ Video: {out}")
    print(f"Ukuran: {sz//1024} KB ({sz} bytes), durasi: {n*SHOT_SEC}s, {n} shot")
    print(f"Siap posting di IG reels. Tambah BGM/voiceover manual di CapCut kalau mau.")
    return out

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--ep", type=int, default=1)
    args = ap.parse_args()
    shots, raw = load_ep(args.ep)
    print(f"EP-{args.ep:03d}: {len(shots)} shot")
    for s in shots: print(f"  Shot {s['idx']} — {s['judul']} (overlay: {s.get('overlay','')[:30]!r})")
    render_mp4(args.ep, shots)

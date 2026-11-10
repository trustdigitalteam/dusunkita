#!/usr/bin/env python3
"""Render reels Dusun Kita (1080x1920, 30fps, 30s) dari brief + screenshot.
Improvement: overlay drop shadow (tanpa box), zoom-in pelan per shot, fade antar shot, BGM.
Jalankan: python3 scripts/render_video.py --ep 1
Output: videos/EP-001-final.mp4
"""
import json, os, re, sys, argparse, subprocess
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1080, 1920
FPS = 30
SHOT_SEC = 6
FADE = 0.4  # detik fade di tiap boundary

# teks overlay per shot (authoritative: versi brief EP-001)
OVERLAYS = {
1: ["DUSUN KITA DIBUKA", "Hari ke-1 · 0 warga"],
2: ["Mulai dari 0:", "✅ Pos Ronda", "✅ Warung", "❌ Belum ada warga"],
3: ["CARA JADI WARGA:", "1. Follow @dusunkita.id", "2. Komen: NAMA, BATA <warna>,", "   TEMBOK <warna>", "Contoh: Budi, bata merah,"],
4: ["GOAL: BANGUN BALAI DUSUN", "Target: 100 Bata"],
5: ["Komen sekarang:", "NAMA, BATA <warna>, TEMBOK <warna>", "@dusunkita.id", "dusunkita.vercel.app"],
}

def font(sz):
    for fp in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
               "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
               "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf"]:
        if os.path.exists(fp):
            try: return ImageFont.truetype(fp, sz)
            except Exception: pass
    return ImageFont.load_default()

def make_overlay(idx, path):
    lines = OVERLAYS.get(idx, [])
    img = Image.new("RGBA", (W, H), (0,0,0,0))
    dr = ImageDraw.Draw(img)
    f_big = font(60)
    f_med = font(40)
    f_sm  = font(34)
    n = len(lines)
    # posisi tengah vertical
    block_h = n*70
    y0 = H//2 - block_h//2
    for i, ln in enumerate(lines):
        sz = f_big if i == 0 else (f_sm if (len(ln) > 22 or ln.startswith(("   ","Contoh"))) else f_med)
        x = W//2
        yy = y0 + i*70
        # drop shadow (offset 3px hitam, lalu teks utama putih)
        dr.text((x+3, yy+3), ln, font=sz, fill=(0,0,0,255), anchor="mt")
        dr.text((x, yy), ln, font=sz, fill=(255,255,255,255), anchor="mt")
    img.save(path)

def get_base_screenshot():
    ss_dir = os.path.join(ROOT, "screenshots")
    files = [f for f in os.listdir(ss_dir) if f.startswith("peta") and f.endswith(".png")]
    files.sort()
    if not files:
        print("Tidak ada screenshot peta. Jalankan: python3 scripts/screenshot.py"); sys.exit(1)
    return os.path.join(ss_dir, files[-1])

def get_bgm():
    # cari BGM: prefer ambience dari repo NC/DK, fallback silent
    for cand in [os.path.join(ROOT,"ambience.mp3"),
                 "/root/.hermes/skills/negeri-komen/references/media/ambience.mp3"]:
        if os.path.exists(cand): return cand
    return None

def render(ep_num):
    out_dir = os.path.join(ROOT, "videos"); os.makedirs(out_dir, exist_ok=True)
    base = get_base_screenshot()
    bgm = get_bgm()
    out = os.path.join(out_dir, f"EP-{ep_num:03d}-final.mp4")

    # 1) buat overlay per shot
    ovs = []
    for i in range(1, 6):
        p = os.path.join(out_dir, f"ep{ep_num:03d}-o{i}.png")
        make_overlay(i, p); ovs.append(p)

    # 2) zoom-in + fade per shot via filter_complex
    # tiap shot: base loop 6s, zoompan in (1.0->1.12), fade out/in, overlay text
    n = 5
    filt = []
    for j in range(n):
        zsrc = f"z{j}"
        # zoom-in via zoompan (zoom 1.0 -> 1.12 over 180 frames). x/y center.
        filt.append(
            f"[{j}:v]scale=1620:2880,zoompan=z=min(zoom+0.000666\\,1.12):d=180:"
            f"x=(iw-iw/zoom)/2:y=(ih-ih/zoom)/2:s=1080x1920:fps=30[{zsrc}]"
        )
        # fade: in 0.4s (shot pertama skip in), out 0.4s (shot terakhir skip out)
        f_in = 0 if j == 0 else FADE
        f_out = 0 if j == n-1 else FADE
        chain = f"[{zsrc}]"
        if f_in: chain += f"fade=t=in:st=0:d={f_in},"
        if f_out: chain += f"fade=t=out:st={SHOT_SEC-f_out}:d={f_out},"
        chain += f"[zov{j}]"
        filt.append(chain)
        # overlay text
        filt.append(f"[zov{j}][{j+5}:v]overlay=0:0[sh{j}]")
    concat = "".join(f"[sh{j}]" for j in range(n))
    filt.append(f"{concat}concat=n={n}:v=1:a=0[vout]")

    cmd = ["ffmpeg","-y","-loglevel","error"]
    for _ in range(n):
        cmd += ["-loop","1","-framerate","30","-t",str(SHOT_SEC),"-i", base]
    for p in ovs:
        cmd += ["-loop","1","-framerate","30","-t",str(SHOT_SEC),"-i", p]

    r = None
    import tempfile
    ffile = os.path.join(out_dir, f"ep{ep_num:03d}-filter.txt")
    with open(ffile, "w") as f:
        f.write(";\n".join(filt) + "\n")
    if bgm:
        cmd += ["-stream_loop","-1","-i", bgm]
        audio_in = 10
        filt.append(f"[{audio_in}:a]atrim=0:{n*SHOT_SEC},afade=t=out:st={n*SHOT_SEC-1.5}:d=1.5[aout]")
        # tulis ulang filter file dengan audio chain
        with open(ffile,"w") as f: f.write(";\n".join(filt)+"\n")
        cmd += ["-filter_complex_script", ffile,
                "-map","[vout]","-map","[aout]",
                "-r","30","-c:v","libx264","-pix_fmt","yuv420p","-crf","21","-preset","medium",
                "-c:a","aac","-b:a","128k","-ar","44100","-ac","2",
                "-t",str(n*SHOT_SEC),"-movflags","+faststart", out]
    else:
        with open(ffile,"w") as f: f.write(";\n".join(filt)+"\n")
        cmd += ["-filter_complex_script", ffile,
                "-map","[vout]",
                "-r","30","-c:v","libx264","-pix_fmt","yuv420p","-crf","21","-preset","medium",
                "-t",str(n*SHOT_SEC),"-movflags","+faststart", out]

    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        print("FFMPEG ERROR:", r.stderr[-1500:]); sys.exit(1)
    sz = os.path.getsize(out)
    print(f"✅ {out}")
    print(f"   {sz//1024} KB · 1080x1920 · 30fps · {n*SHOT_SEC}s · 5 shot · zoom-in · fade · {'BGM' if bgm else 'silent'}")
    print(f"   Voiceover: manual (rekam/TTS di CapCut). TTS id-ID tidak tersedia di VPS.")

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--ep", type=int, default=1); args = ap.parse_args()
    render(args.ep)

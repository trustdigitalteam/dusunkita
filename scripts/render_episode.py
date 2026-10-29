#!/usr/bin/env python3
"""Render video episode Dusun Kita (Remotion + Gemini TTS).

Pipeline: brief → TTS → Remotion render → output MP4.
Dipanggil oleh VPS webhook (dashboard admin trigger) atau cron.

Jalankan:
  GEMINI_API_KEY=*** python3 scripts/render_episode.py --ep 1

Langkah:
  1. Generate 3 VO WAV dari brief (Gemini TTS)
  2. Copy ke remotion/public/
  3. npx remotion render EP-NNN → videos/EP-NNN-final.mp4
  4. Update status JSON (baca oleh webhook Vercel)
"""
import os, sys, json, time, subprocess, base64, struct, urllib.request, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_gemini_key():
    k = os.environ.get("GEMINI_API_KEY")
    if k: return k
    env = os.path.expanduser("~/.hermes/.env")
    if os.path.exists(env):
        for line in open(env):
            m = re.match(r'GEMINI_API_KEY=([A-Za-z0-9_-]+)', line.strip())
            if m: return m.group(1)
    return None

def vo_from_brief(ep):
    p = os.path.join(ROOT, f"docs/episodes/EP-{ep:03d}.md")
    txt = open(p).read()
    return [m.group(1).strip() for m in re.finditer(r'\*\*Voiceover:\*\*\s*"([^"]+)"', txt, re.S)]

def tts_synth(text, out, key, model="gemini-3.1-flash-tts-preview", voice="Kore"):
    payload = {"contents":[{"parts":[{"text":text}]}],"generationConfig":{"responseModalities":["AUDIO"],"speechConfig":{"voiceConfig":{"prebuiltVoiceConfig":{"voiceName":voice}}}}}
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers={"Content-Type":"application/json"})
    for attempt in range(5):
        try:
            d = json.loads(urllib.request.urlopen(req, timeout=60).read())
            raw = base64.b64decode(d["candidates"][0]["content"]["parts"][0]["inlineData"]["data"])
            # wrap l16 PCM 24kHz mono → WAV
            dl = len(raw)
            with open(out, "wb") as f:
                f.write(b'RIFF'); f.write(struct.pack('<I', 36+dl)); f.write(b'WAVEfmt ')
                f.write(struct.pack('<IHHIIHH', 16,1,1,24000,24000*2,2,2))
                f.write(b'data'); f.write(struct.pack('<I', dl)); f.write(raw)
            return os.path.getsize(out)
        except Exception as e:
            if "429" in str(e) and attempt < 4:
                time.sleep(30*(attempt+1))
                continue
            raise
    raise RuntimeError("TTS quota habis")

def render(ep, status):
    key = get_gemini_key()
    if not key:
        status["tts"] = "error: GEMINI_API_KEY tidak ada"
        return False

    # Step: TTS
    status["screenshot"] = "done (pakai screenshot terakhir)"
    status["brief"] = "done"
    status["tts"] = "running"
    vos = vo_from_brief(ep)
    for i, text in enumerate(vos, 1):
        out = os.path.join(ROOT, "remotion", "public", f"vo-EP-{ep:03d}-shot{i}.wav")
        n = tts_synth(text, out, key)
        print(f"  shot{i}: {n//1024}KB WAV")
        time.sleep(15)
    status["tts"] = "done"

    # Step: Render
    status["render"] = "running"
    r = subprocess.run(
        ["npx", "remotion", "render", f"EP-{ep:03d}", f"../videos/EP-{ep:03d}-final.mp4", "--codec", "h264", "--concurrency", "2"],
        cwd=os.path.join(ROOT, "remotion"),
        capture_output=True, text=True, timeout=600,
    )
    out = os.path.join(ROOT, f"videos/EP-{ep:03d}-final.mp4")
    if r.returncode == 0 and os.path.exists(out):
        status["render"] = "done"
        status["mix"] = "done"
        status["ok"] = True
        status["output"] = out
        status["size"] = os.path.getsize(out)
        print(f"✅ {out} ({os.path.getsize(out)//1024}KB)")
    else:
        status["render"] = "error: " + r.stderr[-300:]
        status["ok"] = False
        print(f"❌ render gagal:\n{r.stderr[-500:]}")
    return status["ok"]

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--ep", type=int, default=1)
    ap.add_argument("--status", default=os.path.join(ROOT, "videos/render-status.json"))
    args = ap.parse_args()

    ep = args.ep
    status = {"ep": ep, "started": time.strftime("%Y-%m-%d %H:%M"), "state": "running"}
    open(args.status, "w").write(json.dumps(status, indent=2))
    print(f"== Render EP-{ep:03d} ==")
    try:
        render(ep, status)
    except Exception as e:
        status["state"] = "error"; status["ok"] = False
        status["error"] = str(e)[:300]
        print(f"❌ {e}")
    status["state"] = "done" if status.get("ok") else "error"
    status["finished"] = time.strftime("%Y-%m-%d %H:%M")
    open(args.status, "w").write(json.dumps(status, indent=2))
    print(f"== Status: {status['state']} ==")
    sys.exit(0 if status.get("ok") else 1)

if __name__ == "__main__":
    main()

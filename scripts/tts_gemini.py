#!/usr/bin/env python3
"""Generate voiceover id-ID dari brief episode (Gemini TTS, gratis 500 req/jam).

Baca naskah voiceover di docs/episodes/EP-NNN.md (baris **Voiceover:** per shot),
generate 1 MP3 per shot, simpan ke videos/vo-EP-NNN-shotM.mp3.

Jalankan:
  GEMINI_API_KEY=*** python3 scripts/tts_gemini.py --ep 1

Output:
  videos/vo-EP-001-shot1.mp3 ... shot5.mp3
"""
import os, re, json, sys, base64, urllib.request, argparse, urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "videos")

def voiceover_lines(ep_num):
    p = os.path.join(ROOT, f"docs/episodes/EP-{ep_num:03d}.md")
    txt = open(p).read()
    # extract voiceover per shot: "### Shot N — ..." block, baris **Voiceover:** "..."
    lines = []
    for m in re.finditer(r'\*\*Voiceover:\*\*\s*"([^"]+)"', txt, re.S):
        lines.append(m.group(1).strip())
    return lines

def synth(text, out_path, key, model="gemini-2.5-flash-preview-tts", voice="Kore"):
    payload = {
        "contents": [{"parts": [{"text": text}]}],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}},
        },
    }
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
    resp = urllib.request.urlopen(req, timeout=60)
    data = json.loads(resp.read())
    for p in data["candidates"][0]["content"]["parts"]:
        if "inlineData" in p:
            audio = base64.b64decode(p["inlineData"]["data"])
            open(out_path, "wb").write(audio)
            return len(audio)
    raise RuntimeError(f"no audio in response: {json.dumps(data)[:200]}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ep", type=int, required=True)
    ap.add_argument("--voice", default="Kore", help="prebuilt Gemini voice")
    ap.add_argument("--model", default="gemini-2.5-flash-preview-tts")
    args = ap.parse_args()

    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        # coba dari .hermes/.env
        env = os.path.expanduser("~/.hermes/.env")
        if os.path.exists(env):
            for line in open(env):
                m = re.match(r'GEMINI_API_KEY=([A-Za-z0-9_-]+)', line.strip())
                if m:
                    key = m.group(1)
                    break
    if not key:
        sys.exit("GEMINI_API_KEY tidak ada (env atau ~/.hermes/.env)")

    lines = voiceover_lines(args.ep)
    if not lines:
        sys.exit(f"Tidak ada voiceover di EP-{args.ep:03d}.md")

    os.makedirs(OUT, exist_ok=True)
    ok = 0
    for i, text in enumerate(lines, start=1):
        out = os.path.join(OUT, f"vo-EP-{args.ep:03d}-shot{i}.mp3")
        if os.path.exists(out) and os.path.getsize(out) > 1000:
            print(f"shot{i}: already exists, skip")
            ok += 1
            continue
        try:
            n = synth(text, out, key, model=args.model, voice=args.voice)
            ok += 1
            print(f"shot{i}: {len(text):3d} char -> {n//1024} KB ({os.path.basename(out)})")
        except Exception as e:
            print(f"shot{i}: GAGAL - {str(e)[:120]}")
        # delay antar request (rate limit Gemini 500/hr)
        import time
        time.sleep(3)
    print(f"✅ {ok}/{len(lines)} voiceover di {OUT}")

if __name__ == "__main__":
    main()

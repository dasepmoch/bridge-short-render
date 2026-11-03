#!/usr/bin/env python3
"""What-if voiceover via Microsoft Edge neural TTS (id-ID-GadisNeural), placed at the
same story windows as the original Indonesian cut. Emits voice/voice.wav (48kHz mono),
voice/words.json (per-word timings for the mixer's ducking) and subs_whatif.srt."""
import json, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
VOICE = os.path.join(HERE, "voice")
os.makedirs(VOICE, exist_ok=True)
SR = 48000
TOTAL = 67.5
VOICE_NAME = "id-ID-GadisNeural"

SENT = [
    (0.10, "Apa jadinya kalau tujuh puluh empat prajurit itu nggak berbaris serempak? Mungkin tak ada cerita ini."),
    (4.43, "Tahun 1831, jembatan besi di atas sungai ini adalah kebanggaan seluruh kota."),
    (9.53, "Pagi itu mereka menyeberang berempat-empat, setiap bot menghantam papan di saat yang sama."),
    (14.90, "Jembatan mulai memantul di bawah kaki mereka, kecil, tapi teratur."),
    (17.90, "Orang normal pasti melambat. Mereka malah tertawa dan makin kompak."),
    (21.53, "Seseorang bersiul lagu mars, dan hentakan kaki mengikuti irama, makin keras tiap langkah."),
    (27.53, "Pantulan membesar, rantai berderit, dan tak ada satu pun yang memecah langkah."),
    (33.00, "Satu baut patah. Ujung jembatan ambruk ke sungai, bersama seluruh barisan."),
    (37.95, "Untungnya, sungainya cuma sedalam lutut."),
    (40.15, "Yang tenggelam hari itu cuma harga diri mereka."),
    (43.53, "Sekarang putar ulang pagi itu, dengan satu perbedaan kecil saja."),
    (47.13, "Bayangkan komandannya berteriak sebelum jembatan: pecah langkah! Jalan sesuka kalian."),
    (54.10, "Satu cepat, satu lambat, satu melamun. Hentakan kaki jatuh di waktu yang acak."),
    (57.93, "Tanpa irama bersama, pantulan jembatan tak pernah sempat membesar."),
    (62.20, "Itulah kenapa sampai hari ini, tentara dilarang melangkah serempak di atas jembatan."),
]

def run(cmd):
    subprocess.run(cmd, check=True, capture_output=True)

def dur(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", path], capture_output=True, text=True)
    return float(out.stdout.strip())

def atempo_chain(ratio):
    parts = []
    r = ratio
    while r > 2.0:
        parts.append(2.0); r /= 2.0
    while r < 0.5:
        parts.append(0.5); r /= 0.5
    parts.append(r)
    return ",".join(f"atempo={p:.4f}" for p in parts)

def srt_ts(t):
    h = int(t // 3600); m = int((t % 3600) // 60); s = int(t % 60); ms = int(round((t - int(t)) * 1000))
    if ms == 1000: s += 1; ms = 0
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def wrap(text, width=30):
    words = text.split()
    lines = []
    cur = ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > width:
            lines.append(cur); cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur: lines.append(cur)
    if len(lines) <= 2: return "\n".join(lines)
    mid = (len(lines) + 1) // 2
    return " ".join(lines[:mid]) + "\n" + " ".join(lines[mid:])

words = []
segs = []
subs = []
for i, (start, text) in enumerate(SENT):
    nxt = SENT[i + 1][0] if i + 1 < len(SENT) else TOTAL - 0.05
    window = nxt - start - 0.12
    mp3 = os.path.join(VOICE, f"s{i:02d}.mp3")
    if os.path.exists(mp3): os.remove(mp3)
    last = None
    for attempt in range(3):
        try:
            run(["edge-tts", "--voice", VOICE_NAME, "--text", text, "--write-media", mp3])
            last = None
            break
        except Exception as e:
            last = e; time.sleep(3 * (attempt + 1))
    if last is not None: raise last
    d = dur(mp3)
    ratio = max(0.80, min(1.80, d / window))
    eff_dur = d / ratio
    wav = os.path.join(VOICE, f"s{i:02d}.wav")
    run(["ffmpeg", "-y", "-v", "error", "-i", mp3, "-af",
         f"{atempo_chain(ratio)},aresample={SR},aformat=sample_fmts=s16:channel_layouts=mono",
         "-ar", str(SR), "-ac", "1", wav])
    segs.append((start, wav))
    subs.append((start, start + eff_dur, text))
    ws = text.replace(":", "").replace("?", "").split()
    weights = [len(w) + 1 for w in ws]
    tot = sum(weights)
    t = start
    for w, wt in zip(ws, weights):
        wd = eff_dur * wt / tot
        words.append({"w": w, "s": round(t, 3), "e": round(t + wd, 3)})
        t += wd
    print(f"s{i:02d} start={start:.2f} raw={d:.2f}s ratio={ratio:.3f} eff={eff_dur:.2f}s window={window:.2f}s")

inputs = []
filters = []
for j, (start, wav) in enumerate(segs):
    inputs += ["-i", wav]
    filters.append(f"[{j}:a]adelay={int(start*1000)}:all=1[a{j}]")
mix = "".join(f"[a{j}]" for j in range(len(segs)))
filters.append(f"{mix}amix=inputs={len(segs)}:normalize=0,atrim=0:{TOTAL},aresample={SR}[out]")
fc = ";".join(filters)
run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", fc,
     "-map", "[out]", "-ar", str(SR), "-ac", "1", os.path.join(VOICE, "voice.wav")])
json.dump(words, open(os.path.join(VOICE, "words.json"), "w"), indent=1)

with open(os.path.join(HERE, "subs_whatif.srt"), "w", encoding="utf-8") as f:
    for k, (s, e, text) in enumerate(subs, 1):
        f.write(f"{k}\n{srt_ts(s)} --> {srt_ts(e)}\n{wrap(text)}\n\n")
print("voice.wav duration:", dur(os.path.join(VOICE, "voice.wav")), "words:", len(words), "subs:", len(subs))

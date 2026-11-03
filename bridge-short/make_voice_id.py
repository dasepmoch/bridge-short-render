#!/usr/bin/env python3
"""Generate English voiceover for the bridge short via Google Translate TTS (free),
place each sentence at its story target time, time-stretch to fit its window,
and emit voice.wav (48kHz mono) + words.json with per-word timings."""
import json, os, subprocess, sys, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
VOICE = os.path.join(HERE, "voice")
os.makedirs(VOICE, exist_ok=True)
SR = 48000
TOTAL = 67.5

# (start_seconds, sentence) — starts follow templates/audio timeline sections
SENT = [
    (0.10, "Tujuh puluh empat tentara merobohkan jembatan besi cuma dengan berjalan di atasnya."),
    (4.43, "Tahun 1831, jembatan baru di atas sungai ini adalah kebanggaan seluruh kota."),
    (9.53, "Mereka berbaris pulang berempat-empat, setiap bot menghantam papan di saat yang sama."),
    (14.90, "Di tengah jalan, jembatan mulai memantul di bawah kaki mereka."),
    (17.90, "Orang normal pasti melambat. Mereka malah tertawa."),
    (21.53, "Seseorang bersiul lagu mars, dan seluruh barisan menghentak ikut irama, makin keras tiap langkah."),
    (27.53, "Pantulan membesar, rantai berderit, dan tak ada yang mau memecah langkah lebih dulu."),
    (33.00, "Lalu satu baut patah, dan ujung jembatan ambruk ke sungai."),
    (37.95, "Untungnya, sungai itu cuma sedalam lutut."),
    (40.15, "Sialnya, sungai itu cuma sedalam lutut."),
    (43.53, "Begini, tiap jembatan punya irama goyangannya sendiri."),
    (47.13, "Pernah mendorong anak di ayunan? Dorongannya kecil, tapi kalau pas momennya, ayunan makin tinggi."),
    (54.10, "Tujuh puluh empat langkah serempak itu mendorong jembatan seperti ayunan."),
    (57.93, "Tak ada yang tewas, tapi tentara membuat aturan: dilarang melangkah serempak di jembatan."),
    (62.20, "Kini tentara paling disiplin pun menyeberang jembatan seperti turis."),
]

def run(cmd):
    subprocess.run(cmd, check=True, capture_output=True)

def dur(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", path], capture_output=True, text=True)
    return float(out.stdout.strip())

def atempo_chain(ratio):
    # ratio = input_dur / target_dur (>1 means speed up); build chain of atempo 0.5..2.0
    parts = []
    r = ratio
    while r > 2.0:
        parts.append(2.0); r /= 2.0
    while r < 0.5:
        parts.append(0.5); r /= 0.5
    parts.append(r)
    return ",".join(f"atempo={p:.4f}" for p in parts)

words = []
segs = []
for i, (start, text) in enumerate(SENT):
    nxt = SENT[i + 1][0] if i + 1 < len(SENT) else TOTAL - 0.05
    window = nxt - start - 0.12
    mp3 = os.path.join(VOICE, f"s{i:02d}.mp3")
    if not os.path.exists(mp3):
        q = urllib.parse.quote(text)
        run(["curl", "-s", "--max-time", "40", "-A", "Mozilla/5.0",
             f"https://translate.google.com/translate_tts?ie=UTF-8&client=tw-ob&tl=id&q={q}",
             "-o", mp3])
    d = dur(mp3)
    ratio = d / window
    # only stretch within sane bounds; if TTS shorter, let it end early (small pause)
    ratio = max(0.80, min(1.80, ratio))
    eff_dur = d / ratio
    wav = os.path.join(VOICE, f"s{i:02d}.wav")
    run(["ffmpeg", "-y", "-v", "error", "-i", mp3, "-af",
         f"{atempo_chain(ratio)},aresample={SR},aformat=sample_fmts=s16:channel_layouts=mono",
         "-ar", str(SR), "-ac", "1", wav])
    segs.append((start, wav))
    # per-word timings: proportional to word length inside the effective duration
    ws = text.replace(":", "").replace("?", "").split()
    weights = [len(w) + 1 for w in ws]
    tot = sum(weights)
    t = start
    for w, wt in zip(ws, weights):
        wd = eff_dur * wt / tot
        words.append({"w": w, "s": round(t, 3), "e": round(t + wd, 3)})
        t += wd
    print(f"s{i:02d} start={start:.2f} raw={d:.2f}s ratio={ratio:.3f} eff={eff_dur:.2f}s window={window:.2f}s")

# assemble full track: silence base + adelay each segment, mix
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
print("voice.wav duration:", dur(os.path.join(VOICE, "voice.wav")), "words:", len(words))

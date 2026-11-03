#!/usr/bin/env python3
import os, re, shutil, subprocess, sys
SRC = "frames_in"; SEQ = "frames_seq"; TOTAL = 2025
frames = {}
for f in os.listdir(SRC):
    m = re.fullmatch(r"element-(\d+)\.jpeg", f)
    if m: frames[int(m.group(1))] = os.path.join(SRC, f)
missing = [i for i in range(TOTAL) if i not in frames]
print(f"frames present: {len(frames)}/{TOTAL}, missing: {len(missing)}")
if missing:
    print("MISSING first 50:", missing[:50]); sys.exit(2)
os.makedirs(SEQ, exist_ok=True)
for i in range(TOTAL):
    dst = os.path.join(SEQ, f"f{i:04d}.jpeg")
    if not os.path.exists(dst): shutil.copy(frames[i], dst)
subprocess.run(["ffmpeg", "-y", "-v", "error", "-framerate", "30", "-i", os.path.join(SEQ, "f%04d.jpeg"),
  "-i", "bridge-short/audio/mix.wav", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
  "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", "bridge-short-bahasa.mp4"], check=True)
print("assembled bridge-short-bahasa.mp4", os.path.getsize("bridge-short-bahasa.mp4"))

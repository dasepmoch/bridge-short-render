#!/usr/bin/env python3
"""Assemble the what-if cut: frames_in/element-*.jpeg + bridge-short/audio/mix.wav
-> out/whatif-serempak.mp4 with burned-in Indonesian subtitles (subs_whatif.srt)."""
import os, re, shutil, subprocess, sys
SRC = "frames_in"; SEQ = "frames_seq"; TOTAL = 2025
os.makedirs("out", exist_ok=True)
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
  "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", "out/whatif-raw.mp4"], check=True)
style = "FontSize=11,PrimaryColour=&HFFFFFF&,OutlineColour=&H99000000&,BorderStyle=1,Outline=2,Shadow=0,Alignment=2,MarginV=40"
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", "out/whatif-raw.mp4",
  "-vf", f"subtitles=bridge-short/subs_whatif.srt:force_style='{style}'",
  "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
  "-c:a", "copy", "-movflags", "+faststart", "out/whatif-serempak.mp4"], check=True)
print("assembled out/whatif-serempak.mp4", os.path.getsize("out/whatif-serempak.mp4"))

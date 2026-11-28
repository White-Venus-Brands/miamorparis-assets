"""Re-mux the loop reels so nothing outlasts the video (28 Nov fix).
WhatsApp/phone players ignore the MP4 edit list, so the AAC tail (+21 ms) played past the last video frame -> a black flash
at the loop point. Now: audio ends 45 ms before the video (inside the last frames, even with AAC priming), and a
_silent copy with no audio track at all (add the sound in Instagram) for a perfect loop.
Usage: python3 remux_loops.py WORKDIR"""
import os, subprocess, sys
WORK = sys.argv[1].rstrip("/") + "/"; P = os.path.dirname(os.path.abspath(__file__)) + "/.."
JOBS = [(f"{P}/2026-11-28-loops/loop_{n}", WORK + f"fr_loop_{n}/", f, L) for n, f, L in
        [("flip", 50, .8), ("cradle", 50, .8), ("giftpop", 50, .8), ("hat", 50, .8), ("carousel", 50, 2.4), ("pause_p", 25, .48), ("pause_m", 25, .48)]]
for out, fd, fps, L in JOBS:
    n = int(round(L * fps)); v = ["-framerate", str(fps), "-i", fd + "%04d.jpg"]
    enc = ["-frames:v", str(n), "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p", "-r", str(fps), "-movflags", "+faststart"]
    subprocess.run(["ffmpeg", "-v", "error", "-y"] + v + ["-i", fd + "a.wav", "-map", "0:v", "-map", "1:a", "-af", f"atrim=0:{L - .045:.3f},afade=t=out:st={L - .065:.3f}:d=0.02"]
                   + enc + ["-c:a", "aac", "-b:a", "256k", out + ".mp4"], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y"] + v + enc + ["-an", out + "_silent.mp4"], check=True)
    print("ok", out)

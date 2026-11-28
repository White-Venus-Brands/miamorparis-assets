"""Moisturiser version of the Jingle Bells -> Punjabi Jingle Bell switch reel (28 Nov): identical edit, timing and audio,
the 12 Santa-hat moisturiser renders (6 men's, 6 women's, alternating) instead of the perfumes.
Usage: python3 build_m_switch.py WORKDIR SONG.m4a   (WORKDIR must hold fr_switch/a2.wav from build_switch_orig.py)"""
import os, shutil, subprocess, sys
D = os.path.dirname(os.path.abspath(__file__)) + "/"
sys.path.insert(0, D + "../2026-11-28-jingle-switch")
import build_switch_orig as O
S = O.S; G = S.G
G.D = D; G._c.clear()
G.LIST = [("marhaba", "PAPA"), ("flora5", "MUMMY"), ("mraqua", "BHAI"), ("misspoem", "DIDI"), ("derossa", "YOUR BOYFRIEND"), ("loveair", "YOUR GIRLFRIEND"),
          ("smuggler", "THE BOSS"), ("bouquet", "BHABHI"), ("holdmi", "CHACHU"), ("missaqua", "YOUR BESTIE"), ("moksha", "SECRET SANTA"), ("ombre", "YOURSELF")]
if __name__ == "__main__":
    if os.environ.get("ONLY"):
        for x in os.environ["ONLY"].split(","): S.frame(float(x)).save(S.WORK + f"m_{x}.jpg", quality=85)
        sys.exit()
    fd = S.WORK + "fr_mswitch/"; os.makedirs(fd, exist_ok=True)
    for i in range(int(round(S.TOTAL * S.FPS))):
        t = i / S.FPS; im = S.frame(t).convert("RGBA"); O.karaoke(im, t); im.convert("RGB").save(fd + f"{i:04d}.jpg", quality=93)
    shutil.copy(S.WORK + "fr_switch/a2.wav", fd + "a.wav")
    enc = ["-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p", "-r", str(S.FPS), "-movflags", "+faststart"]
    base = ["ffmpeg", "-v", "error", "-y", "-framerate", str(S.FPS), "-i", fd + "%04d.jpg"]
    subprocess.run(base + ["-i", fd + "a.wav", "-map", "0:v", "-map", "1:a"] + enc + ["-c:a", "aac", "-b:a", "256k", "-shortest", D + "moisturiser_switch.mp4"], check=True)
    subprocess.run(base + enc + ["-an", D + "moisturiser_switch_silent.mp4"], check=True)
    print("done", S.TOTAL)

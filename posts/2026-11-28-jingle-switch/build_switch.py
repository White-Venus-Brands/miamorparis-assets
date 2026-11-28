"""'Jingle Bells -> Punjabi Jingle Bell' switch reel (28 Nov).
IMG_5374: Tannay mouths 'Jingle bells, jingle bells, jingle all the way' (silent take) -> an original rendition of the
public-domain 'Jingle Bells' melody (Pierpont, 1857), synthesised here, timed to his mouth (q = 0.25 s from 0.25 s).
IMG_5375: side-eye at the boring version -> record scratch -> Punjabi Jingle Bell drop exactly as his hand goes up.
Then the 12 Santa-hat product renders on the beat (from build_gift12), the grid, the end card.
Usage: python3 build_switch.py WORKDIR"""
import os, subprocess, sys, wave
import numpy as np
from PIL import Image

WORK = sys.argv[1].rstrip("/") + "/"; os.makedirs(WORK, exist_ok=True)
D = os.path.dirname(os.path.abspath(__file__)) + "/"; R = os.path.normpath(D + "../..") + "/"
sys.path.insert(0, R + "posts/2026-11-27-jingle-shorts"); _a = sys.argv; sys.argv = [_a[0], WORK]
import build_gift12 as G
sys.argv = _a
J = G.J; W, H, FPS, SR, P = J.W, J.H, J.FPS, J.SR, J.P
A = "/mnt/user-data/attachments/e1dc2e45-c278-5714-b377-734372e7d29a/"
C1, C2 = A + "9301ba5f-IMG_5374.mov", A + "653df6b1-IMG_5375.mov"
L1 = 5.32; HAND = 2.85
DROP = round((L1 + HAND) * FPS) / FPS            # Punjabi Jingle Bell drop lands as the hand goes up
SONG_DROP = J.DR[0]                               # 4.46 s in the song
OFF = DROP - SONG_DROP                            # timeline t = song time + OFF
T = [DROP + P * (4 + 2 * k) for k in range(12)]   # products after 4 beats of bhangra
G0 = T[-1] + 2 * P; E0 = G0 + 4 * P; TOTAL = round((E0 + 2.4) * FPS) / FPS
SCRATCH = DROP - .42

def frames(src, tag):
    fd = WORK + f"f_{tag}/"
    if not os.path.isdir(fd) or not os.listdir(fd):
        os.makedirs(fd, exist_ok=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-vf", f"fps={FPS},scale={W}:{H}", "-q:v", "2", fd + "%04d.jpg"], check=True)
    return fd, sorted(os.listdir(fd))
F1, F2 = frames(C1, "c1"), frames(C2, "c2")
def clip(F, t):
    fd, fs = F; im = Image.open(fd + fs[max(0, min(int(t * FPS), len(fs) - 1))]).convert("RGB")
    a = np.asarray(im).astype(np.float32) / 255; a = .03 + a * .95; a = a ** np.array([.97, 1., 1.05])
    return Image.fromarray(np.clip(a * 255, 0, 255).astype(np.uint8)).convert("RGBA")

def frame(t):
    if t < L1:
        im = clip(F1, t); J.popt(im, 260, "EVERY CHRISTMAS PARTY:", t, J.MS(70))
    elif t < T[0]:
        im = clip(F2, t - L1)
        if t >= DROP and t - DROP < .4: im = J.punch(im, t - DROP)
        if t < DROP: J.popt(im, 260, "MEANWHILE, US:", t - L1 - .5, J.MS(76)) if t - L1 > .5 else None
        else: J.popt(im, 260, "PUNJABI CHRISTMAS", t - DROP, J.MS(88), J.GOLD)
        if t >= DROP: im.alpha_composite(J.snow(t))
    elif t < G0:
        i = max(j for j, s in enumerate(T) if s <= t); u = t - T[i]; name, who = G.LIST[i]
        im = G.kb(G.card(name), u / (2 * P)).convert("RGBA")
        if u < .3: im = J.punch(im, u * 1.2)
        J.popt(im, 210, "FOR " + who, u, J.MS(84)); im.alpha_composite(J.snow(t))
    elif t < E0:
        im = G.frame(G.G0 + (t - G0)).convert("RGBA")
    else:
        im = J.festive(t); im.alpha_composite(J.snow(t)); J.endcard(im, t - E0, "Christmas gift list: sorted")
    J.flash(im, t - DROP, a=170)
    if abs(t - L1) < .04: J.flash(im, 0, (255, 255, 255), 60)
    if t > TOTAL - .5: im.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(255 * J.ss((t - TOTAL + .5) / .5)))))
    if t < .2: im.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(255 * (1 - t / .2)))))
    return im.convert("RGB")

# ---------- audio ----------
NOTE = {"C": 261.63, "D": 293.66, "E": 329.63, "F": 349.23, "G": 392.0}
MEL = [("E", 1), ("E", 1), ("E", 2), ("E", 1), ("E", 1), ("E", 2), ("E", 1), ("G", 1), ("C", 1.5), ("D", .5), ("E", 4),
       ("F", 1), ("F", 1), ("F", 1.5), ("F", .5), ("F", 1), ("E", 1), ("E", 1), ("E", .5), ("E", .5), ("E", 1), ("D", 1), ("D", 1), ("E", 1), ("D", 2), ("G", 2)]
CHORDS = [("C", [130.81, 164.81, 196.0])] * 4 + [("F", [174.61, 220.0, 261.63]), ("C", [130.81, 164.81, 196.0]), ("D", [146.83, 185.0, 220.0]), ("G", [98.0, 123.47, 146.83])]
Q, T0 = .25, .25
def jingle(n):
    out = np.zeros(n, np.float32); rng = np.random.default_rng(2)
    def add(sig, t0, g=1.):
        i = int(t0 * SR); m = min(len(sig), n - i)
        if m > 0: out[i:i + m] += g * sig[:m]
    t = T0
    for nt, d in MEL:                                    # glockenspiel melody, one octave up
        f = NOTE[nt] * 2; L = int((d * Q + .6) * SR); x = np.arange(L) / SR
        add((np.sin(2 * np.pi * f * x) + .35 * np.sin(2 * np.pi * 2.76 * f * x) * np.exp(-x * 9)) * np.exp(-x * 3.2) * .32, t); t += d * Q
    for b, (_, ch) in enumerate(CHORDS):                 # oom-pah piano: bass on 1 & 3, chord on 2 & 4
        for k in range(4):
            tb = T0 + (b * 4 + k) * Q; L = int(.45 * SR); x = np.arange(L) / SR; env = np.exp(-x * 7)
            if k % 2 == 0: add(np.sin(2 * np.pi * ch[0] / 2 * x) * env * .32, tb)
            else: add(sum(np.sin(2 * np.pi * f * x) for f in ch) * env * .09, tb)
    for k in range(int((n / SR - T0) / (Q / 2))):        # sleigh bells on 8ths
        L = int(.08 * SR); x = np.arange(L) / SR; nz = rng.standard_normal(L).astype(np.float32)
        nz = np.diff(np.concatenate([[0], nz])); add(nz * np.exp(-x * 45) * (.06 if k % 2 else .1), T0 + k * Q / 2)
    return out
def scratch():
    L = int(.38 * SR); x = np.arange(L) / SR; rng = np.random.default_rng(5)
    f = 1800 * np.exp(-x * 7) + 200; ph = 2 * np.pi * np.cumsum(f) / SR
    nz = rng.standard_normal(L).astype(np.float32) * np.sin(ph) ** 2
    return (np.sin(ph * .5) * .5 + nz * .6) * np.minimum(1, x / .01) * np.exp(-x * 4) * .5

def build_audio(path):
    n = int(round(TOTAL * SR))
    jb = jingle(n); fade_at = int(SCRATCH * SR); jb[fade_at:] *= np.exp(-np.arange(n - fade_at) / SR * 40)
    song = np.zeros((n, 2), np.float32); s0 = int((SONG_DROP - .06) * SR); i0 = int((DROP - .06) * SR); m = min(len(J.SNG) - s0, n - i0)
    song[i0:i0 + m] = J.SNG[s0:s0 + m]
    jb2 = np.stack([jb, jb], 1); r_song = np.sqrt(np.mean(song[i0:] ** 2)); r_jb = np.sqrt(np.mean(jb2[int(.3 * SR):fade_at] ** 2))
    jb2 *= r_song / r_jb * 10 ** (-3 / 20)
    sc = scratch(); k = int(SCRATCH * SR); jb2[k:k + len(sc)] += np.stack([sc, sc], 1) * r_song / .05 * .18
    mix = jb2 + song; fo = int(.6 * SR); mix[-fo:] *= np.linspace(1, 0, fo)[:, None]; mix *= 10 ** (-1 / 20) / np.max(np.abs(mix))
    with wave.open(path, "wb") as w_:
        w_.setnchannels(2); w_.setsampwidth(2); w_.setframerate(SR); w_.writeframes((mix * 32767).astype(np.int16).tobytes())

if __name__ == "__main__":
    only = os.environ.get("ONLY")
    if only:
        for s_ in only.split(","): frame(float(s_)).save(WORK + f"sw_{s_}.jpg", quality=85)
        print("DROP", DROP, "first product", round(T[0], 2), "grid", round(G0, 2), "end", round(E0, 2), "TOTAL", TOTAL); sys.exit()
    fd = WORK + "fr_switch/"; os.makedirs(fd, exist_ok=True)
    for i in range(int(round(TOTAL * FPS))): frame(i / FPS).save(fd + f"{i:04d}.jpg", quality=93)
    build_audio(fd + "a.wav")
    base = ["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", fd + "%04d.jpg"]
    enc = ["-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p", "-r", str(FPS), "-movflags", "+faststart"]
    subprocess.run(base + ["-i", fd + "a.wav", "-map", "0:v", "-map", "1:a"] + enc + ["-c:a", "aac", "-b:a", "256k", "-shortest", D + "jingle_switch.mp4"], check=True)
    print("done", TOTAL)

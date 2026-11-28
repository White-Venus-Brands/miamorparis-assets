"""'Thumb up, thumb down' interactive Reel (28 Nov).
The viewer holds the phone in the right hand and moves the thumb up/down in a small zone bottom-right, one stroke per beat
of Punjabi Jingle Bell. A small guide dot there moves with the beat. Every clip is a boomerang of a real moment from
Tannay's footage that follows the thumb: up = it rises, down = it drops / presses. Each action runs 2 reps, then cuts.
  1 hand goes up (IMG_5375)   2 spray press (IMG_5076)   3 body wash raised to camera (IMG_5211)
  4 gift box scroll (IMG_5213)   5 candles lifted (IMG_5216)   6 hand swipe (IMG_5222)   7 point at you (IMG_5215)
Minimal text: one line at the start. Usage: python3 build_thumb.py WORKDIR  (ONLY=t,t renders test frames)"""
import math, os, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

WORK = sys.argv[1].rstrip("/") + "/"; os.makedirs(WORK, exist_ok=True)
D = os.path.dirname(os.path.abspath(__file__)) + "/"; R = os.path.normpath(D + "../..") + "/"
sys.path.insert(0, R + "posts/2026-11-27-jingle-shorts"); _a = sys.argv; sys.argv = [_a[0], WORK, "santa"]
import build_jingle as J
sys.argv = _a
W, H, FPS, SR, P = J.W, J.H, J.FPS, J.SR, J.P
SP = "/tmp/claude-0/-home-claude/e1dc2e45-c278-5714-b377-734372e7d29a/scratchpad/"
A = "/mnt/user-data/attachments/e1dc2e45-c278-5714-b377-734372e7d29a/"
def frames(src, tag):
    fd = WORK + f"f_{tag}/"
    if not os.path.isdir(fd) or not os.listdir(fd):
        os.makedirs(fd, exist_ok=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-vf", f"fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}",
                        "-q:v", "2", fd + "%04d.jpg"], check=True)
    return fd
# (folder, first frame, last frame, forward = thumb 'up' or 'down', grade?)
ACTS = [(frames(A + "653df6b1-IMG_5375.mov", "5375"), 67, 76, "up", True),
        (frames(A + "3c60885a-IMG_5076.mov", "5076"), 39, 47, "down", True),
        (SP + "bfspec/f25_5211/", 3, 13, "up", False),
        (frames(A + "a14d9f64-IMG_5213.mov", "5213"), 24, 36, "up", True),
        (SP + "bfspec/f25_5216/", 49, 59, "up", False),
        (SP + "bfspec/f25_5222/", 82, 92, "down", False),
        (SP + "bfspec/f25_5215/", 182, 190, "up", False)]
DROP = 2.8; SONG0 = J.DR[0] - DROP
E0 = DROP + len(ACTS) * 4 * P; TOTAL = round((E0 + 2.4) * FPS) / FPS
_ls = {}
def get(fd, i, grade):
    if fd not in _ls: _ls[fd] = sorted(f for f in os.listdir(fd) if f.endswith(".jpg"))
    im = Image.open(fd + _ls[fd][int(i)]).convert("RGB")
    if im.size != (W, H): im = im.resize((W, H), Image.LANCZOS)
    if grade:
        a = np.asarray(im).astype(np.float32) / 255; a = .03 + a * .95; a = a ** np.array([.97, 1., 1.05]); im = Image.fromarray(np.clip(a * 255, 0, 255).astype(np.uint8))
    return im.convert("RGBA")
def thumb_p(t):
    """guide position: 0 = thumb down, 1 = thumb up. Beat k from the drop: even = up stroke, odd = down stroke"""
    if t < DROP:                                                             # demo before the drop: two slow strokes
        u = (t - .9) / (DROP - .9)
        return 0 if u < 0 else .5 - .5 * math.cos(2 * math.pi * 2 * J.cl(u))
    k = int((t - DROP) / P); u = J.ss((t - DROP - k * P) / (P * .8))
    return u if k % 2 == 0 else 1 - u
def guide(im, p, a=1.0):
    x, y = 820, 1660 - 150 * p; lay = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((x - 46, 1660 - 150 - 62, x + 46, 1660 + 62), radius=46, outline=(255, 255, 255, int(110 * a)), width=5)
    d.ellipse((x - 40, y - 40, x + 40, y + 40), fill=(255, 255, 255, int(185 * a)), outline=(226, 186, 112, int(255 * a)), width=7)
    im.alpha_composite(lay.filter(ImageFilter.GaussianBlur(1)))

def frame(t):
    p = thumb_p(t)
    if t < DROP:
        fd, a, b, fw, g = ACTS[0]; im = get(fd, a, g)
        im.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, 110)))
        J.popt(im, 1250, "thumb up, thumb down", t - .2, J.BOD(84), J.GOLD2, 0); J.popt(im, 1350, "with me", t - .5, J.BOD(84), J.GOLD2, 0)
        guide(im, p)
    elif t < E0:
        k = int((t - DROP) / (4 * P)); fd, a, b, fw, g = ACTS[k]; q = p if fw == "up" else 1 - p
        im = get(fd, a + q * (b - a), g)
        if t - (DROP + k * 4 * P) < .08: J.flash(im, t - (DROP + k * 4 * P), a=90, d=.08)
        guide(im, p, .9)
    else:
        im = J.festive(t); im.alpha_composite(J.snow(t)); J.endcard(im, t - E0, "Thumb workout: done")
    if t < .15: im.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(255 * (1 - t / .15)))))
    if t > TOTAL - .5: im.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(255 * J.ss((t - TOTAL + .5) / .5)))))
    return im.convert("RGB")

def psst():
    L = int(.35 * SR); x = np.arange(L) / SR; n = np.random.default_rng(2).standard_normal(L)
    hp = np.diff(np.concatenate([[0], n])); return hp * np.minimum(1, x / .01) * np.exp(-x * 9)
def tick():
    L = int(.03 * SR); x = np.arange(L) / SR; return np.sin(2 * np.pi * 1800 * x) * np.exp(-x * 160)
def build_audio(path):
    n = int(round(TOTAL * SR)); s0 = int(SONG0 * SR); m = J.SNG[s0:s0 + n].copy()
    if len(m) < n: m = np.pad(m, ((0, n - len(m)), (0, 0)))
    rm = np.sqrt(np.mean(m[int(DROP * SR):] ** 2)); ps = psst(); ps /= np.max(np.abs(ps)); tk = tick(); tk /= np.max(np.abs(tk))
    for b in range(len(ACTS) * 4):
        t0 = DROP + b * P; i = int(t0 * SR); seg = m[i:i + len(tk)]; seg += (tk * rm * .5)[:len(seg)][:, None]
        if b // 4 == 1 and b % 2 == 1: seg = m[i:i + len(ps)]; seg += (ps * rm * 1.3)[:len(seg)][:, None]   # spray on the press
    fo = int(.6 * SR); m[-fo:] *= np.linspace(1, 0, fo)[:, None]; m *= 10 ** (-1 / 20) / np.max(np.abs(m))
    with wave.open(path, "wb") as w_: w_.setnchannels(2); w_.setsampwidth(2); w_.setframerate(SR); w_.writeframes((m * 32767).astype(np.int16).tobytes())

if __name__ == "__main__":
    only = os.environ.get("ONLY")
    if only:
        for s_ in only.split(","): frame(float(s_)).save(WORK + f"th_{s_}.jpg", quality=85)
        print("E0", round(E0, 2), "TOTAL", TOTAL); sys.exit()
    fd = WORK + "fr_thumb/"; os.makedirs(fd, exist_ok=True)
    for i in range(int(round(TOTAL * FPS))): frame(i / FPS).save(fd + f"{i:04d}.jpg", quality=93)
    build_audio(fd + "a.wav")
    base = ["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", fd + "%04d.jpg"]
    enc = ["-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p", "-r", str(FPS), "-movflags", "+faststart"]
    subprocess.run(base + ["-i", fd + "a.wav", "-map", "0:v", "-map", "1:a"] + enc + ["-c:a", "aac", "-b:a", "256k", "-shortest", D + "thumb_reel.mp4"], check=True)
    subprocess.run(base + enc + ["-an", D + "thumb_reel_silent.mp4"], check=True)
    print("done", TOTAL)

"""GTA VI launch-day Reel from Tannay's 4 illustrations (src/). The copied 'Grand Theft Aroma' title and
'...has a new obsession' line on s1 are cropped out; our own text on top. Also writes a clean carousel cover.
Usage: python3 build.py OUTDIR"""
import math, os, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

D = os.path.dirname(os.path.abspath(__file__)) + "/"
OUT = (sys.argv[1].rstrip("/") + "/") if len(sys.argv) > 1 else "/tmp/gta/"
os.makedirs(OUT + "f", exist_ok=True)
W, H, FPS = 1080, 1920, 30
WHITE, GOLD, PINK, INK = (255, 255, 255), (255, 196, 60), (255, 170, 200), (16, 4, 20)
def F(s, w="Black"): return ImageFont.truetype(f"/usr/share/fonts/opentype/inter/Inter-{w}.otf", s)
def cl(x): return max(0.0, min(1.0, x))
def ss(x): x = cl(x); return x * x * (3 - 2 * x)
def back(x): x = cl(x); c = 1.7; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2

src = {k: Image.open(D + f"src/{k}.png").convert("RGB") for k in ("s1", "car", "pool", "heli")}
CLEAN1 = src["s1"].crop((190, 470, 886, 1340))          # lens + glasses, no copied title or tagline

def fill(img, fx=.5, fy=.5):
    """scale to cover 9:16, return big image + max offsets"""
    s = max(W / img.width, H / img.height)
    return img.resize((math.ceil(img.width * s), math.ceil(img.height * s)), Image.LANCZOS)
def fitw(img):
    fg = img.resize((W, int(img.height * W / img.width)), Image.LANCZOS)
    bg = fill(img).crop((0, 0, W, H)).filter(ImageFilter.GaussianBlur(45))
    bg = Image.blend(bg, Image.new("RGB", (W, H), (20, 4, 30)), .35)
    bg.paste(fg, (0, (H - fg.height) // 2)); return bg
BIG = {"s1": fitw(CLEAN1), "car": fill(src["car"]), "pool": fill(src["pool"]), "heli": fill(src["heli"])}
def view(k, p, zoom=(1.0, 1.08), pan=(.5, .5)):
    b = BIG[k]; z = zoom[0] + (zoom[1] - zoom[0]) * p
    w, h = W / z, H / z
    fx = pan[0] + (pan[1] - pan[0]) * p if isinstance(pan[0], float) and isinstance(pan, tuple) and len(pan) == 2 else .5
    x0 = (b.width - w) * fx; y0 = (b.height - h) * .5
    return b.resize((W, H), Image.LANCZOS, box=(x0, y0, x0 + w, y0 + h)).convert("RGBA")

def text(im, xy, s, f, fill=WHITE, sw=9, a=1.0, scale=1.0, anchor="ma"):
    if a <= 0: return
    lay = Image.new("RGBA", (W, 400)); ImageDraw.Draw(lay).text((W // 2, 40), s, font=f, fill=fill, stroke_width=sw, stroke_fill=INK, anchor="ma")
    bb = lay.getbbox(); lay = lay.crop(bb)
    if scale != 1: lay = lay.resize((max(1, int(lay.width * scale)), max(1, int(lay.height * scale))), Image.LANCZOS)
    if a < 1: lay.putalpha(lay.getchannel("A").point(lambda v: int(v * a)))
    im.alpha_composite(lay, (int(xy[0] - lay.width / 2), int(xy[1] - (lay.height - (bb[3] - bb[1])) / 2)))

def stars(im, cx, y, n_on, size=78, pop_t=None):
    d = ImageDraw.Draw(im); n = 5; gap = size * 1.25; x0 = cx - gap * (n - 1) / 2
    for i in range(n):
        on = i < n_on; s = size * (1 + (.5 * (1 - back((pop_t - i * .12) / .25)) if (pop_t is not None and on) else 0))
        cx_ = x0 + i * gap; pts = []
        for k in range(10):
            r = s / 2 if k % 2 == 0 else s / 4.6; ang = -math.pi / 2 + k * math.pi / 5
            pts.append((cx_ + r * math.cos(ang), y + r * math.sin(ang)))
        d.polygon(pts, fill=WHITE if on else (90, 90, 90), outline=INK, width=6)

SHADE = Image.new("RGBA", (W, H)); _d = ImageDraw.Draw(SHADE)
for y in range(H):
    a = int(150 * max(1 - y / 520, (y - (H - 520)) / 520, 0)); _d.line([(0, y), (W, y)], fill=(10, 0, 20, a))

# timeline
T = [3.6, 7.0, 10.4, 15.5]
def frame(t):
    if t < T[0]:
        p = t / T[0]; im = view("s1", p, (1.0, 1.12)); im.alpha_composite(SHADE)
        stars(im, W / 2, 190, min(5, int(t / .25) + 1) if t > .3 else 0, pop_t=t - .3)
        text(im, (W / 2, 290), "WANTED LEVEL: MAX", F(64), a=ss((t - 1.4) / .2), scale=1 + .3 * (1 - back((t - 1.4) / .3)))
        text(im, (W / 2, 1620), "Delhi's most wanted", F(84), fill=GOLD, a=ss((t - 2.0) / .2))
        text(im, (W / 2, 1730), "just dropped.", F(84), a=ss((t - 2.4) / .2))
        return im
    if t < T[1]:
        t0 = T[0]; p = (t - t0) / (T[1] - t0); im = view("car", p, (1.0, 1.1), (.35, .62)); im.alpha_composite(SHADE)
        text(im, (W / 2, 150), "MISSION 1", F(54), fill=PINK, sw=7, a=ss((t - t0 - .1) / .2))
        text(im, (W / 2, 230), "Steal the show.", F(92), a=ss((t - t0 - .3) / .2), scale=1 + .2 * (1 - back((t - t0 - .3) / .3)))
        text(im, (W / 2, 1680), "Marhaba Oudh. Grab it first.", F(60, "ExtraBold"), fill=GOLD, sw=7, a=ss((t - t0 - 1.2) / .25))
        return im
    if t < T[2]:
        t0 = T[1]; p = (t - t0) / (T[2] - t0); im = view("pool", p, (1.06, 1.0), (.58, .42)); im.alpha_composite(SHADE)
        text(im, (W / 2, 150), "MISSION 2", F(54), fill=PINK, sw=7, a=ss((t - t0 - .1) / .2))
        text(im, (W / 2, 230), "Lie low. Smell rich.", F(88), a=ss((t - t0 - .3) / .2), scale=1 + .2 * (1 - back((t - t0 - .3) / .3)))
        text(im, (W / 2, 1650), "Love Is In The Air", F(60, "ExtraBold"), fill=GOLD, sw=7, a=ss((t - t0 - 1.1) / .25))
        text(im, (W / 2, 1735), "& Miss Poem", F(60, "ExtraBold"), fill=GOLD, sw=7, a=ss((t - t0 - 1.4) / .25))
        return im
    t0 = T[2]; p = (t - t0) / (T[3] - t0); im = view("heli", ss(min(1, p * 1.4)), (1.0, 1.0)); im.alpha_composite(SHADE)
    text(im, (W / 2, 120), "MISSION 3", F(54), fill=PINK, sw=7, a=ss((t - t0 - .1) / .2))
    text(im, (W / 2, 200), "The airlift.", F(92), a=ss((t - t0 - .3) / .2), scale=1 + .2 * (1 - back((t - t0 - .3) / .3)))
    t1 = t0 + 2.6
    if t > t1:   # mission passed card
        im.alpha_composite(Image.new("RGBA", (W, H), (10, 0, 20, int(120 * ss((t - t1) / .3)))))
        text(im, (W / 2, 760), "MISSION PASSED", F(118), fill=GOLD, sw=11, a=ss((t - t1) / .15), scale=1 + .35 * (1 - back((t - t1) / .35)))
        text(im, (W / 2, 910), "Respect +100", F(64, "ExtraBold"), a=ss((t - t1 - .5) / .2))
        text(im, (W / 2, 1010), "O-17, Lajpat Nagar-II", F(48, "Bold"), fill=PINK, sw=6, a=ss((t - t1 - .9) / .2))
    if t > T[3] - .5: im.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(255 * ss((t - T[3] + .5) / .5)))))
    return im

def audio(path):
    sr = 44100; n = int(T[3] * sr); tt = np.arange(n) / sr; a = np.zeros(n)
    def note(f, t0, dur, v, harm=(1, .4, .15)):
        i0 = int(t0 * sr); m = min(n - i0, int(dur * sr)); x = np.arange(m) / sr
        env = np.minimum(1, x / .01) * np.exp(-x / (dur * .4))
        a[i0:i0 + m] += v * env * sum(h * np.sin(2 * np.pi * f * (k + 1) * x) for k, h in enumerate(harm))
    bpm = 100; b = 60 / bpm; t = 0.0; k = 0
    bass = [55, 55, 65.4, 49]
    while t < T[3] - .6:
        note(50, t, .3, .6, (1,)); note(bass[(k // 4) % 4], t + b / 2, .25, .25)
        if k % 2 == 1:   # clap-ish
            i0 = int(t * sr); m = int(.08 * sr); a[i0:i0 + m] += .25 * np.random.default_rng(k).standard_normal(m) * np.exp(-np.arange(m) / (.02 * sr))
        t += b; k += 1
    for i in range(5): note(1318.5, .3 + i * .25 * 0 + i * .12, .2, .12)       # star blips
    t1 = T[2] + 2.6
    for i, f in enumerate((523.3, 659.3, 784, 1046.5)): note(f, t1 + i * .1, 1.4, .16)   # mission chime
    a *= np.minimum(1, (T[3] - tt) / .6); a = np.tanh(a * 1.3) * .85
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((a * 32767).astype(np.int16).tobytes())

def cover45():
    c = CLEAN1.resize((1080, 1350), Image.LANCZOS).convert("RGBA")
    sh = Image.new("RGBA", c.size); d = ImageDraw.Draw(sh)
    for y in range(420): d.line([(0, y), (1080, y)], fill=(10, 0, 20, int(150 * (1 - y / 420))))
    c.alpha_composite(sh); d = ImageDraw.Draw(c)
    d.text((540, 60), "MOST WANTED", font=F(120), fill=WHITE, stroke_width=10, stroke_fill=INK, anchor="ma")
    tmp = Image.new("RGBA", c.size); stars(tmp, 540, 250, 5, size=70); c.alpha_composite(tmp)
    d.text((540, 1250), "Delhi edition  ·  swipe →", font=F(44, "ExtraBold"), fill=GOLD, stroke_width=6, stroke_fill=INK, anchor="ma")
    c.convert("RGB").save(D + "carousel_cover_clean.jpg", quality=95)

if __name__ == "__main__":
    only = os.environ.get("ONLY")
    if only:
        for s in only.split(","): frame(float(s)).convert("RGB").save(OUT + f"still_{s}.jpg", quality=85)
        cover45(); sys.exit()
    cover45(); audio(OUT + "a.wav")
    for i in range(int(T[3] * FPS)): frame(i / FPS).convert("RGB").save(OUT + f"f/{i:04d}.png", compress_level=1)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", OUT + "f/%04d.png", "-i", OUT + "a.wav",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "15", "-preset", "medium", "-c:a", "aac", "-b:a", "192k", "-shortest",
                    "-movflags", "+faststart", D + "most_wanted_reel.mp4"], check=True)
    frame(3.0).convert("RGB").save(D + "reel_cover.jpg", quality=94)
    print("done")

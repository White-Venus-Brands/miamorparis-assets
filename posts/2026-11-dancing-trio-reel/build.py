"""Reel: the three-bottle server-room dance (Love Is In The Air, Moksha, Miss Poem).
Parody of the viral AI dance meme. No faces, no names, no person or company identified: the bottles are the cast.
1080x1920, 30 fps, ~18 s. Real cutouts for LIITA + Moksha; Miss Poem cut from Tannay's AI still (-> isAiGenerated true).
Usage: python3 build.py WORKDIR   (ONLY=1,9 for stills)"""
import math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

D = os.path.dirname(os.path.abspath(__file__)) + "/"
R = D + "../../"
OUT = sys.argv[1].rstrip("/") + "/" if len(sys.argv) > 1 else "/tmp/trio/"
LOGO = Image.open(R + "assets/cutouts/logo_gold.png").convert("RGBA")
W, H, FPS = 1080, 1920, 30
GOLD, IVORY = (226, 186, 112), (250, 245, 236)
BPM = 124; BEAT = 60 / BPM

def inter(s, w="Black"): return ImageFont.truetype(f"/usr/share/fonts/opentype/inter/InterDisplay-{w}.otf", s)
def pop(s, w="Medium"): return ImageFont.truetype(f"/usr/share/fonts/truetype/google-fonts/Poppins-{w}.ttf", s)
def lora(s): return ImageFont.truetype("/usr/share/fonts/truetype/google-fonts/Lora-Italic-Variable.ttf", s)
def cl(x): return max(0.0, min(1.0, x))
def ss(x): x = cl(x); return x * x * (3 - 2 * x)
def back(x): x = cl(x); c = 1.9; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2
def win(t, a, b, fi=.2, fo=.2): return ss((t - a) / fi) * (1 - ss((t - (b - fo)) / fo))

T_TAGS, T_Q, T_A, END = 3.9, 8.7, 11.6, 14.6
DUR = END + 3.8

# ---------- cast ----------
def miss_poem():
    im = Image.open(R + "posts/2026-11-honey-trap-reel/src/02.png").convert("RGBA")
    m = Image.new("L", im.size, 0); d = ImageDraw.Draw(m)
    d.rounded_rectangle((290, 766, 657, 924), 10, fill=255); d.rectangle((398, 920, 552, 996), fill=255); d.rounded_rectangle((258, 990, 682, 1516), 26, fill=255)
    im.putalpha(m.filter(ImageFilter.GaussianBlur(1.5))); return im.crop((250, 760, 690, 1522))
def fit(im, h): return im.resize((int(im.width * h / im.height), h), Image.LANCZOS)
CAST = [  # name, cutout, x, height, sleeve colour, leg colour, pattern
    ("Love Is In The Air", fit(Image.open(R + "assets/cutouts/liita.png").convert("RGBA"), 420), 215, (168, 30, 36), (236, 200, 170), "floral"),
    ("Moksha", fit(Image.open(R + "assets/cutouts/moksha.png").convert("RGBA"), 500), 540, (22, 22, 24), (22, 22, 24), "leather"),
    ("Miss Poem", fit(miss_poem(), 330), 900, (120, 122, 128), (120, 122, 128), "suit"),
]
FLOOR = 1500

# ---------- set: server room ----------
rng = np.random.default_rng(4)
LEDS = [(side, rng.integers(0, 4), rng.integers(0, 46), rng.uniform(0, 6.3), rng.uniform(1, 5)) for side in (0, 1) for _ in range(260)]
def room(t):
    im = Image.new("RGBA", (W, H), (9, 10, 14, 255)); d = ImageDraw.Draw(im)
    d.polygon([(0, FLOOR - 60), (W, FLOOR - 60), (W, H), (0, H)], fill=(34, 34, 42, 255))
    d.rectangle((230, 250, W - 230, FLOOR - 60), fill=(26, 28, 38, 255))
    for side in (0, 1):
        for c in range(4):
            x0 = 14 + c * 54 if side == 0 else W - 14 - (c + 1) * 54
            d.rectangle((x0, 180 - c * 0, x0 + 46, FLOOR + 40 - c * 26), fill=(14, 16, 24, 255), outline=(40, 46, 66, 255), width=2)
    for side, c, row, ph, sp in LEDS:
        x0 = 14 + c * 54 if side == 0 else W - 14 - (c + 1) * 54
        y = 200 + row * 27
        if y > FLOOR - c * 26: continue
        on = 0.5 + 0.5 * math.sin(t * sp + ph); col = (90, 170, 255) if (row + c) % 5 else (120, 255, 190)
        d.rectangle((x0 + 8, y, x0 + 38, y + 5), fill=tuple(int(v * (0.25 + 0.75 * on)) for v in col) + (255,))
    glow = Image.new("RGBA", im.size); dg = ImageDraw.Draw(glow)
    dg.ellipse((140, FLOOR - 110, W - 140, FLOOR + 190), fill=(120, 160, 255, 46)); im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(60)))
    return im

# ---------- dancers ----------
def limb(d, pts, col, w):
    d.line(pts, fill=col + (255,), width=w, joint="curve")
    for p in pts: d.ellipse((p[0] - w / 2, p[1] - w / 2, p[0] + w / 2, p[1] + w / 2), fill=col + (255,))
def dancer(im, t, idx, entered=1.0):
    name, cut, x, sleeve, leg, pat = CAST[idx]
    ph = t / BEAT * math.pi                      # one bounce per beat
    squat = 34 * abs(math.sin(ph)) ** 1.5
    sway = 16 * math.sin(ph / 2 + idx * .5)
    fl = FLOOR + (70 if idx == 1 else 0); cx = x + sway; by = fl - 210 + squat      # bottle bottom
    by += (1 - entered) * 900
    top = by - cut.height; d = ImageDraw.Draw(im)
    # shadow
    sh = Image.new("RGBA", im.size); ImageDraw.Draw(sh).ellipse((cx - 170, fl - 10, cx + 170, fl + 40), fill=(0, 0, 0, 150)); im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14))); d = ImageDraw.Draw(im)
    # legs (wide squat, knees out)
    for sgn in (-1, 1):
        hip = (cx + sgn * 55, by - 20); knee = (cx + sgn * (130 + squat * .5), by + 90 - squat * .2); foot = (cx + sgn * 105, fl + 6)
        limb(d, [hip, knee, foot], leg, 38)
        d.rounded_rectangle((foot[0] - 50 + sgn * 18, foot[1] - 14, foot[0] + 50 + sgn * 18, foot[1] + 26), 16, fill=(12, 12, 14, 255))
    # back arm, bottle, front arm: alternating fist pumps
    def arm(sgn, front):
        p = math.sin(ph + (0 if sgn > 0 else math.pi))          # -1..1
        sh_ = (cx + sgn * (cut.width / 2 - 26), top + cut.height * .48)
        el = (sh_[0] + sgn * 62, sh_[1] + 30 - 14 * p)
        fist = (el[0] + sgn * (-10 + 22 * p), el[1] - 80 - 36 * p)
        limb(d, [sh_, el] if pat == "floral" else [sh_, el, fist], sleeve, 34)
        if pat == "floral":
            limb(d, [el, fist], (236, 200, 170), 28)
            for k in range(3): d.ellipse((sh_[0] + sgn * (20 + k * 28) - 7, sh_[1] + 8 + k * 9 - 7, sh_[0] + sgn * (20 + k * 28) + 7, sh_[1] + 8 + k * 9 + 7), fill=(240, 200, 120, 255))
        if pat == "leather": d.line([sh_, el, fist], fill=(120, 120, 130, 255), width=4)
        d.ellipse((fist[0] - 26, fist[1] - 26, fist[0] + 26, fist[1] + 26), fill=(250, 248, 244, 255), outline=(40, 40, 44, 255), width=4)
    arm(-1, False); arm(1, False)
    tilt = 4 * math.sin(ph / 2 + idx)
    b = cut.rotate(tilt, expand=True, resample=Image.BICUBIC)
    im.alpha_composite(b, (int(cx - b.width / 2), int(by - cut.height - (b.height - cut.height) / 2)))
    return cx, top

def ctext(im, y, s, f, col, a, blur=10, scale=1.0, x=None):
    if a <= 0: return
    lay = Image.new("RGBA", (W + 400, 320)); ImageDraw.Draw(lay).text((lay.width / 2, 30), s, font=f, fill=col + (int(255 * a),), anchor="ma")
    bb = lay.getbbox()
    if not bb: return
    lay = lay.crop(bb)
    if scale != 1: lay = lay.resize((max(1, int(lay.width * scale)), max(1, int(lay.height * scale))), Image.LANCZOS)
    xx = (W - lay.width) // 2 if x is None else int(x - lay.width / 2)
    sh = Image.new("RGBA", lay.size, (0, 0, 0, 0)); sh.putalpha(lay.getchannel("A").point(lambda v: int(v * .9)))
    pad = blur * 3; big = Image.new("RGBA", (lay.width + 2 * pad, lay.height + 2 * pad)); big.alpha_composite(sh, (pad, pad))
    im.alpha_composite(big.filter(ImageFilter.GaussianBlur(blur)), (xx - pad, int(y) - pad + 4)); im.alpha_composite(lay, (xx, int(y)))

def tag(im, cx, y, s, a, k):
    if a <= 0: return
    f = inter(32, "Bold"); w_ = ImageDraw.Draw(im).textlength(s, font=f); lay = Image.new("RGBA", im.size); d = ImageDraw.Draw(lay)
    yy = y - 30 * (1 - k)
    d.rounded_rectangle((cx - w_ / 2 - 22, yy - 32, cx + w_ / 2 + 22, yy + 32), 32, fill=GOLD + (255,)); d.polygon([(cx - 14, yy + 30), (cx + 14, yy + 30), (cx, yy + 52)], fill=GOLD + (255,))
    d.text((cx, yy), s, font=f, fill=(40, 10, 14, 255), anchor="mm"); lay.putalpha(lay.getchannel("A").point(lambda v: int(v * a))); im.alpha_composite(lay)

def frame(t):
    im = room(t)
    pos = []
    order = [0, 2, 1]
    for n, idx in enumerate(order):
        pos.append((idx, dancer(im, t, idx, back((t - .1 - n * .25) / .5))))
    pos = dict(pos)
    if t < T_TAGS:
        ctext(im, 300, "Guess the meme. 👀".replace(" 👀", ""), inter(100), IVORY, win(t, .9, T_TAGS, .15), scale=1 + .2 * (1 - back((t - .9) / .3)))
        ctext(im, 430, "No names. IYKYK.", lora(60), GOLD, win(t, 1.6, T_TAGS, .2))
    elif t < T_Q:
        ctext(im, 300, "Introducing the cast:", inter(76), IVORY, win(t, T_TAGS, T_Q, .2))
        for n, idx in enumerate((0, 1, 2)):
            t0 = T_TAGS + .5 + n * 1.1
            cx, top = pos[idx]; tag(im, min(max(cx, 190), W - 190), top - 80, CAST[idx][0], ss((t - t0) / .15) * (1 - ss((t - T_Q + .2) / .2)), back((t - t0) / .3))
    elif t < T_A:
        ctext(im, 300, "Trying NOT to leave", inter(88), IVORY, win(t, T_Q, T_A, .15))
        ctext(im, 405, "a scent behind?", inter(88), IVORY, win(t, T_Q + .2, T_A, .15))
    elif t < END:
        ctext(im, 300, "Then we're", inter(96), GOLD, win(t, T_A, END, .12), scale=1 + .25 * (1 - back((t - T_A) / .3)))
        ctext(im, 415, "not the ones.", inter(96), GOLD, win(t, T_A + .15, END, .12))
        ctext(im, 1640, "Everyone will know you were there.", lora(52), IVORY, win(t, T_A + 1.0, END, .2))
    else:
        u = t - END; dark = Image.new("RGBA", im.size, (6, 6, 10, int(215 * ss(u / .5)))); im.alpha_composite(dark)
        lg = LOGO.resize((230, int(LOGO.height * 230 / LOGO.width)), Image.LANCZOS); a = ss((u - .2) / .4)
        lg.putalpha(lg.getchannel("A").point(lambda v: int(v * a))); im.alpha_composite(lg, ((W - 230) // 2, 420))
        ctext(im, 680, "Extrait de parfum.", inter(72), IVORY, ss((u - .4) / .4))
        ctext(im, 780, "Leaves an impression. Always.", lora(56), GOLD, ss((u - .7) / .4))
        a3 = ss((u - 1.1) / .4)
        if a3 > 0:
            f = inter(46, "Black"); lab = "DM FOR PRICES"; w_ = ImageDraw.Draw(im).textlength(lab, font=f); lay = Image.new("RGBA", im.size); dl = ImageDraw.Draw(lay); y = 960
            dl.rounded_rectangle(((W - w_) / 2 - 50, y - 50, (W + w_) / 2 + 50, y + 50), 50, fill=GOLD + (255,)); dl.text((W / 2, y), lab, font=f, fill=(40, 8, 16, 255), anchor="mm")
            lay.putalpha(lay.getchannel("A").point(lambda v: int(v * a3))); im.alpha_composite(lay)
        ctext(im, 1060, "OR VISIT US AT LAJPAT NAGAR-II", pop(36, "Bold"), (226, 180, 110), ss((u - 1.3) / .4), 6)
    if t > DUR - .5: im = Image.blend(im, Image.new("RGBA", im.size, (0, 0, 0, 255)), ss((t - DUR + .5) / .5))
    return im.convert("RGB")

SR = 44100
def audio(path):
    from scipy.signal import lfilter
    n = int(SR * DUR); out = np.zeros((n, 2), np.float32); r = np.random.default_rng(2)
    def add(sig, at, g=1.0, pan=0.0):
        i = int(at * SR); j = min(n, i + len(sig))
        if i >= n or j <= i: return
        s = sig[: j - i] * g; out[i:j, 0] += s * (1 - pan); out[i:j, 1] += s * (1 + pan)
    def env(L, a=.003, rel=.15): x = np.arange(int(L * SR)) / SR; return np.minimum(1, x / a) * np.exp(-x / rel)
    def tone(f, L, a=.005, rel=.2, h=(1, .5, .3)): x = np.arange(int(L * SR)) / SR; return sum(g * np.sin(2 * np.pi * f * (i + 1) * x) for i, g in enumerate(h)) * env(L, a, rel)
    kick = lambda: np.sin(2 * np.pi * (48 + 110 * np.exp(-np.arange(int(.32 * SR)) / SR / .04)) * np.arange(int(.32 * SR)) / SR) * env(.32, .002, .11)
    hat = lambda: lfilter([1, -1], [1, -.6], r.normal(0, 1, int(.05 * SR))) * env(.05, .001, .012)
    clap = lambda: lfilter([1, -1], [1, -.5], r.normal(0, 1, int(.12 * SR))) * env(.12, .002, .03)
    bass = [55, 55, 65.4, 49]; lead = [440, 523.3, 659.3, 523.3, 587.3, 523.3, 440, 392]
    k = 0; t = 0.0
    while t < DUR - .4:
        add(kick(), t, .7); add(hat(), t + BEAT / 2, .14)
        if k % 2 == 1: add(clap(), t, .16)
        b = bass[(k // 4) % 4]; add(tone(b, BEAT * .45, .004, .12, (1, .7, .4)), t, .22); add(tone(b * 2, BEAT * .3, .004, .08, (1, .5)), t + BEAT / 2, .14)
        if t > .9: add(tone(lead[k % 8], BEAT * .4, .004, .1, (1, .3, .2)), t + (BEAT / 2 if k % 2 else 0), .06, .3 * math.sin(k))
        t += BEAT; k += 1
    for i in range(3): add(tone(1318.5, .25, .002, .08, (1,)), T_TAGS + .5 + i * 1.1, .08)
    add(kick(), T_A, 1.3)
    for f in (880, 1108.7, 1318.5): add(tone(f, 1.2, .003, .5, (1,)), T_A + .05, .05)
    out = np.tanh(out * 1.3)
    fd = np.ones(n); fd[-int(.8 * SR):] = np.linspace(1, 0, int(.8 * SR)); out *= fd[:, None]
    import scipy.io.wavfile as wf; wf.write(path, SR, (out / max(1e-9, np.abs(out).max()) * .89 * 32767).astype(np.int16))

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    only = os.environ.get("ONLY")
    ts = [float(x) for x in only.split(",")] if only else [i / FPS for i in range(int(DUR * FPS))]
    for t in ts:
        frame(t).save(OUT + (f"t_{t:05.2f}.jpg" if only else f"{int(round(t * FPS)):04d}.jpg"), quality=92)
    if not only:
        audio(OUT + "a.wav")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", OUT + "%04d.jpg", "-i", OUT + "a.wav",
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "19", "-preset", "medium", "-c:a", "aac", "-b:a", "192k",
                        "-movflags", "+faststart", "-shortest", D + "dancing_trio_reel.mp4"], check=True)
        frame(2.66).save(D + "cover.jpg", quality=92)
        print("ok", DUR)

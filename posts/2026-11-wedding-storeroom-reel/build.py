"""Reel: 'Har shaadi ke baad, ghar ka store room.'  Wedding season, no people. 1080x1920, 30 fps, ~27 s.
Stills supplied by Tannay (10 Nov 2026, AI-generated -> isAiGenerated true). Soothing pace, ASMR unboxing,
running counter 'SHAADI GIFTS: 0->47' that pays off as 'GIFTS ACTUALLY USED: 1'.
Own audio: tanpura drone + santoor-like plucks + soft SFX. No prices.
Usage: python3 build.py WORKDIR   (ONLY=1.5,10.5 for stills)"""
import math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance

D = os.path.dirname(os.path.abspath(__file__)) + "/"
R = D + "../../"
OUT = sys.argv[1].rstrip("/") + "/" if len(sys.argv) > 1 else "/tmp/wed/"
LOGO = Image.open(R + "assets/cutouts/logo_gold.png").convert("RGBA")
W, H, FPS = 1080, 1920, 30
GOLD, IVORY = (226, 186, 112), (252, 244, 232)

def inter(s, w="Black"): return ImageFont.truetype(f"/usr/share/fonts/opentype/inter/InterDisplay-{w}.otf", s)
def lora(s, it=True): return ImageFont.truetype("/usr/share/fonts/truetype/google-fonts/Lora-" + ("Italic-Variable" if it else "Variable") + ".ttf", s)
def pop(s, w="Bold"): return ImageFont.truetype(f"/usr/share/fonts/truetype/google-fonts/Poppins-{w}.ttf", s)
def cl(x): return max(0.0, min(1.0, x))
def ss(x): x = cl(x); return x * x * (3 - 2 * x)

# ---------- shots: (src, start, end, zoom0, zoom1, (fx0, fy0), (fx1, fy1)) focus = relative centre ----------
# Timed to the ElevenLabs narration (VO_OFFSET 0.5 s; Simran 9w21nMuk8CWXIME31V1S, 10 Nov)
SHOTS = [
    ("01", 0.0, 3.9, 1.00, 1.09, (.5, .5), (.5, .45)),     # store room, push in
    ("10", 3.7, 6.6, 1.06, 1.00, (.5, .5), (.5, .5)),      # casserole
    ("11", 6.4, 8.8, 1.00, 1.07, (.5, .52), (.5, .5)),     # dinner set
    ("12", 8.6, 10.6, 1.07, 1.00, (.5, .5), (.5, .5)),     # clock
    ("01", 10.4, 11.3, 1.02, 1.04, (.5, .55), (.5, .58)),  # store room again...
    ("09", 10.6, 14.0, 1.04, 1.12, (.5, .58), (.5, .62)),  # ...lights go out, spotlight on empty shelf
    ("08", 13.8, 15.4, 1.00, 1.06, (.5, .55), (.5, .6)),   # empty wedding table
    ("06", 15.2, 17.0, 1.08, 1.00, (.5, .55), (.5, .55)),  # closed box, bow
    ("07", 16.8, 18.0, 1.00, 1.05, (.5, .55), (.5, .55)),  # ribbon loose
    ("04", 17.8, 18.6, 1.00, 1.04, (.5, .5), (.5, .48)),   # lid half open
    ("03", 18.4, 20.1, 1.00, 1.06, (.5, .55), (.5, .6)),   # open, petals
    ("02", 19.9, 22.8, 1.08, 1.00, (.5, .55), (.5, .55)),  # bottle close-up
]
END = 22.6
DUR = END + 4.4
XF = {10.6: 0.9}  # longer dissolve for the lights-out moment
VO_OFFSET = 0.5

_src = {}
def src(name):
    if name not in _src:
        im = Image.open(D + f"src/{name}.png").convert("RGB")
        _src[name] = im.resize((int(W * 1.12), int(H * 1.12)), Image.LANCZOS)
    return _src[name]

def shot_frame(sh, t):
    name, t0, t1, z0, z1, f0, f1 = sh
    u = ss((t - t0) / (t1 - t0)); z = z0 + (z1 - z0) * u
    fx = f0[0] + (f1[0] - f0[0]) * u; fy = f0[1] + (f1[1] - f0[1]) * u
    im = src(name); base = W * 1.12
    cw, ch = im.width / z, im.height / z
    cx = fx * im.width; cy = fy * im.height
    x0 = min(max(cx - cw / 2, 0), im.width - cw); y0 = min(max(cy - ch / 2, 0), im.height - ch)
    return im.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch))

def plate(t):
    act = [s for s in SHOTS if s[1] <= t < s[2]]
    if not act: act = [SHOTS[-1]]
    if len(act) == 1: return shot_frame(act[0], t)
    a, b = act[0], act[1]
    xf = XF.get(b[1], a[2] - b[1]); k = ss((t - b[1]) / xf)
    return Image.blend(shot_frame(a, t), shot_frame(b, t), k)

# ---------- overlays ----------
TOPG = np.linspace(1, 0, 760) ** 1.6
TOPGRAD = Image.new("RGBA", (W, H))
_g = np.zeros((H, W, 4), np.uint8); _g[:760, :, 3] = (TOPG * 150).astype(np.uint8)[:, None]; TOPGRAD = Image.fromarray(_g, "RGBA")

def text_lay(s, f, col):
    lay = Image.new("RGBA", (W, 300)); ImageDraw.Draw(lay).text((W / 2, 20), s, font=f, fill=col + (255,), anchor="ma")
    return lay.crop(lay.getbbox())

def ctext(im, y, s, f, col, a, blur=10):
    if a <= 0: return
    lay = text_lay(s, f, col)
    if a < 1: lay.putalpha(lay.getchannel("A").point(lambda v: int(v * a)))
    sh = Image.new("RGBA", lay.size, (0, 0, 0, 0)); sh.putalpha(lay.getchannel("A").point(lambda v: int(v * 0.85)))
    pad = blur * 3; big = Image.new("RGBA", (lay.width + 2 * pad, lay.height + 2 * pad)); big.alpha_composite(sh, (pad, pad))
    x = (W - lay.width) // 2
    im.alpha_composite(big.filter(ImageFilter.GaussianBlur(blur)), (x - pad, int(y) - pad + 4)); im.alpha_composite(lay, (x, int(y)))

def win(t, a, b, fi=0.35, fo=0.3):   # alpha for a text window [a,b]
    return ss((t - a) / fi) * (1 - ss((t - (b - fo)) / fo))

# (start, end, y, text, kind)
CAPS_HI = [
    (0.6, 3.6, 360, "Har shaadi ke baad,", "s"), (2.2, 3.6, 460, "ghar ka store room.", "s"),
    (3.85, 6.3, 390, "Casserole.", "s"), (4.85, 6.3, 490, "Abhi bhi plastic mein.", "s"),
    (6.6, 8.5, 390, "Dinner set no. 4", "s"),
    (8.8, 10.4, 390, "Ghadi.", "s"), (9.55, 10.4, 490, "Teesri.", "s"),
    (10.75, 13.7, 360, "Par ek gift...", "s"), (12.0, 13.7, 460, "kabhi store room nahi jaata.", "s"),
    (13.95, 16.8, 360, "Is shaadi season,", "s"), (15.25, 16.8, 460, "kuch aisa gift karo...", "s"),
    (18.15, 19.6, 360, "jo roz use ho.", "s"),
    (19.7, 22.5, 360, "Aur har spray pe,", "s"), (21.15, 22.5, 460, "aapki yaad aaye.", "s"),
]
CAPS_EN = [  # English VO (Simran, en), offset 0.4 s
    (0.55, 3.6, 360, "After every wedding,", "s"), (2.3, 3.6, 460, "there's a store room.", "s"),
    (3.95, 6.3, 390, "A casserole.", "s"), (5.0, 6.3, 490, "Still in its plastic.", "s"),
    (6.8, 8.5, 390, "Dinner set no. 4", "s"),
    (8.95, 10.45, 390, "A clock.", "s"), (9.55, 10.45, 490, "The third one.", "s"),
    (11.1, 13.7, 360, "But one gift...", "s"), (12.3, 13.7, 460, "never ends up in there.", "s"),
    (14.2, 16.8, 360, "This wedding season,", "s"), (15.6, 16.8, 460, "give something...", "s"),
    (17.6, 19.55, 360, "they'll use every day.", "s"),
    (19.65, 22.5, 360, "And with every spray,", "s"), (21.2, 22.5, 460, "they'll think of you.", "s"),
]
EN = os.environ.get("EN") == "1"
CAPS = CAPS_EN if EN else CAPS_HI

def counter(im, t):
    d = ImageDraw.Draw(im)
    if t < 10.9:
        n = int(round(47 * ss(t / 9.8) if t < 9.8 else 47))
        lab = (f"WEDDING GIFTS: {n}" if EN else f"SHAADI GIFTS: {n}"); fill = (20, 10, 8, 170); col = (255, 236, 210)
        a = ss(t / 0.4) * (1 - ss((t - 10.5) / 0.4))
    elif 20.3 <= t < 22.55:
        lab = "GIFTS ACTUALLY USED: 1"; fill = GOLD + (235,); col = (40, 10, 14); a = ss((t - 20.3) / 0.3) * (1 - ss((t - 22.3) / 0.25))
    else: return
    f = inter(38, "Bold"); tw = d.textlength(lab, font=f)
    lay = Image.new("RGBA", im.size); dl = ImageDraw.Draw(lay); y = 225
    dl.rounded_rectangle(((W - tw) / 2 - 34, y, (W + tw) / 2 + 34, y + 70), 35, fill=fill)
    dl.text((W / 2, y + 35), lab, font=f, fill=col + (255,), anchor="mm")
    if a < 1: lay.putalpha(lay.getchannel("A").point(lambda v: int(v * a)))
    im.alpha_composite(lay)

rng = np.random.default_rng(5)
DUST = [(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(1.5, 4), rng.uniform(8, 30), rng.uniform(0, 6.28)) for _ in range(70)]
PETALS = [(rng.uniform(-50, W + 50), rng.uniform(-900, 0), rng.uniform(18, 34), rng.uniform(90, 170), rng.uniform(0, 6.28), rng.uniform(.6, 1.4)) for _ in range(16)]
def particles(im, t, petals=0.0):
    lay = Image.new("RGBA", im.size); d = ImageDraw.Draw(lay)
    for x, y, r, sp, ph in DUST:
        yy = (y - t * sp) % H; xx = x + 14 * math.sin(t * .6 + ph); a = int(60 + 60 * math.sin(t * 2 + ph))
        d.ellipse((xx - r, yy - r, xx + r, yy + r), fill=(255, 220, 150, max(0, a)))
    if petals > 0:
        for x, y, r, sp, ph, sc in PETALS:
            yy = y + (t - 18.4) * sp; xx = x + 40 * math.sin((t - 18.4) * .9 + ph)
            if -60 < yy < H + 60:
                ang = (t * 40 * sc + ph * 57) % 360
                p = Image.new("RGBA", (int(r * 2.4), int(r * 1.4))); ImageDraw.Draw(p).ellipse((0, 0, p.width - 1, p.height - 1), fill=(178, 24, 40, int(220 * petals)))
                p = p.rotate(ang, expand=True, resample=Image.BICUBIC); lay.alpha_composite(p, (int(xx), int(yy)))
    im.alpha_composite(lay.filter(ImageFilter.GaussianBlur(1.2)))

# ---------- end card ----------
_endbg = None
def endbg():
    global _endbg
    if _endbg is None:
        im = src("05").resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(18))
        _endbg = ImageEnhance.Brightness(im).enhance(0.38).convert("RGBA")
    return _endbg

def scene_end(t):
    u = t - END
    base = shot_frame(SHOTS[-1], t).convert("RGBA")
    im = Image.blend(base, endbg(), ss(u / 0.6))
    lg = LOGO.resize((210, int(LOGO.height * 210 / LOGO.width)), Image.LANCZOS)
    a = ss((u - 0.3) / 0.5); lg.putalpha(lg.getchannel("A").point(lambda v: int(v * a))); im.alpha_composite(lg, ((W - 210) // 2, 260))
    ctext(im, 520, "THE WEDDING GIFT SET", inter(70, "Black"), GOLD, ss((u - 0.5) / 0.4), 8)
    ctext(im, 620, "Body wash  ·  Perfume  ·  Moisturiser", pop(40, "Medium"), IVORY, ss((u - 0.7) / 0.4), 6)
    ctext(im, 680, "in one gift box", lora(46), (240, 222, 200), ss((u - 0.8) / 0.4), 6)
    # small real-render thumbnail of the open box
    a2 = ss((u - 0.9) / 0.5)
    if a2 > 0:
        th = src("03").resize((300, 533), Image.LANCZOS).convert("RGBA")
        m = Image.new("L", th.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, 299, 532), 26, fill=int(255 * a2)); th.putalpha(m)
        fr = Image.new("RGBA", (308, 541)); ImageDraw.Draw(fr).rounded_rectangle((0, 0, 307, 540), 30, fill=GOLD + (int(255 * a2),)); fr.alpha_composite(th, (4, 4))
        im.alpha_composite(fr, ((W - 308) // 2, 780))
    ctext(im, 1345, "Shown: Love Is In The Air", pop(34, "Medium"), (230, 210, 190), ss((u - 1.1) / 0.4), 6)
    a3 = ss((u - 1.4) / 0.4)
    if a3 > 0:
        f = inter(46, "Black"); lab = "DM FOR PRICES"; d = ImageDraw.Draw(im); tw = d.textlength(lab, font=f)
        lay = Image.new("RGBA", im.size); dl = ImageDraw.Draw(lay); y = 1480
        dl.rounded_rectangle(((W - tw) / 2 - 50, y - 50, (W + tw) / 2 + 50, y + 50), 50, fill=GOLD + (255,))
        dl.text((W / 2, y), lab, font=f, fill=(40, 8, 16, 255), anchor="mm"); lay.putalpha(lay.getchannel("A").point(lambda v: int(v * a3))); im.alpha_composite(lay)
    ctext(im, 1570, "OR VISIT US AT LAJPAT NAGAR-II", pop(36, "Bold"), (226, 180, 110), ss((u - 1.6) / 0.4), 6)
    return im

def frame(t):
    if t >= END: im = scene_end(t)
    else:
        im = plate(t).convert("RGBA"); im.alpha_composite(TOPGRAD)
        particles(im, t, petals=ss((t - 18.4) / 0.5) if t > 18.4 else 0)
        for a, b, y, s, k in CAPS:
            if a <= t < b: ctext(im, y, s, lora(74), IVORY, win(t, a, b))
        counter(im, t)
    if t < 0.5: im = Image.blend(Image.new("RGBA", im.size, (0, 0, 0, 255)), im, ss(t / 0.5))
    if t > DUR - 0.6: im = Image.blend(im, Image.new("RGBA", im.size, (0, 0, 0, 255)), ss((t - DUR + 0.6) / 0.6))
    return im.convert("RGB")

# ---------- audio ----------
SR = 44100
def audio(path):
    n = int(SR * DUR); out = np.zeros((n, 2), np.float32); r = np.random.default_rng(3)
    def add(sig, at, g=1.0, pan=0.0):
        i = int(at * SR); j = min(n, i + len(sig))
        if i >= n: return
        s = sig[: j - i] * g; out[i:j, 0] += s * (1 - pan) ; out[i:j, 1] += s * (1 + pan)
    def pluck(f, L=2.4, damp=0.996):
        N = int(SR / f); buf = r.uniform(-1, 1, N); m = int(L * SR); y = np.zeros(m)
        for k in range(m):
            y[k] = buf[k % N]; buf[k % N] = damp * 0.5 * (buf[k % N] + buf[(k + 1) % N])
        y2 = y + 0.6 * np.concatenate([np.zeros(int(.012 * SR)), y[:-int(.012 * SR)]])  # double-strike shimmer like santoor
        return y2 / (np.abs(y2).max() + 1e-9)
    # tanpura-ish drone: Pa-Sa-Sa-Sa on D
    sa = 146.83
    tt = np.arange(n) / SR
    drone = np.zeros(n)
    for f, g in ((sa * 0.75, .5), (sa, .6), (sa * 2, .35)):
        drone += g * sum(h * np.sin(2 * np.pi * f * (i + 1) * tt + i) for i, h in enumerate((1, .5, .35, .2, .12)))
    drone *= (0.8 + 0.2 * np.sin(2 * np.pi * 0.25 * tt)) * 0.045
    out[:, 0] += drone; out[:, 1] += drone
    # Yaman-flavoured phrase, slow (D E F# G# A B C#)
    sc = [1, 9 / 8, 5 / 4, 45 / 32, 3 / 2, 27 / 16, 15 / 8, 2, 9 / 4, 5 / 2]
    phrase = [7, 6, 4, 5, 4, 2, 4, 3, 2, 0, 2, 4, 7, 9, 8, 7, 4, 5, 4, 2]
    cache = {}
    beat = 60 / 66
    k = 0; t = 0.6
    while t < DUR - 1.5:
        deg = phrase[k % len(phrase)]; f = sa * 2 * sc[deg]
        if deg not in cache: cache[deg] = pluck(f)
        g = 0.10 if not (10.6 <= t < 13.4) else 0.05
        add(cache[deg], t, g, pan=0.25 * math.sin(k))
        if k % 4 == 0:
            bd = [0, 4, 2, 0][(k // 4) % 4]
            if ("b", bd) not in cache: cache[("b", bd)] = pluck(sa * sc[bd], 3.0, 0.997)
            add(cache[("b", bd)], t, 0.09)
        t += beat * (1 if k % 4 != 3 else 2); k += 1
    # soft counter ticks during 0-8.6
    tick = np.sin(2 * np.pi * 3200 * np.arange(int(.025 * SR)) / SR) * np.exp(-np.arange(int(.025 * SR)) / SR / .006)
    last = -1
    for i in range(int(9.8 * FPS)):
        tt_ = i / FPS; nn = int(round(47 * ss(tt_ / 9.8)))
        if nn != last: add(tick, tt_, 0.05); last = nn
    # lights-out: low "thoom" + air
    th = np.sin(2 * np.pi * 55 * np.arange(int(1.6 * SR)) / SR) * np.exp(-np.arange(int(1.6 * SR)) / SR / .5); add(th, 10.6, 0.35)
    # ribbon slide (silky noise), lid lift (soft whump), reveal chime
    nz = r.normal(0, 1, int(.9 * SR)); from scipy.signal import lfilter
    rib = lfilter([1, -1], [1, -0.85], nz) * np.hanning(len(nz)) * 0.05; add(rib, 16.8, 1.0, 0.3)
    wh = lfilter([1], [1, -0.97], r.normal(0, 1, int(.6 * SR))) * np.hanning(int(.6 * SR)) * 0.012; add(wh, 17.8)
    for i, f in enumerate((1174.7, 1480, 1760, 2349.3)):
        x = np.arange(int(2.5 * SR)) / SR; add(np.sin(2 * np.pi * f * x) * np.exp(-x / .9) * 0.05, 18.4 + i * 0.09, 1.0, (-0.4, 0.4, -0.2, 0.2)[i])
    # end swell
    x = np.arange(int(4.4 * SR)) / SR
    for f in (sa / 2, sa * 3 / 4, sa, sa * 5 / 4 * 2):
        add(np.sin(2 * np.pi * f * x) * np.minimum(1, x / 1.2) * np.exp(-x / 3) * 0.05, END)
    out = np.tanh(out * 1.6) * 0.8
    fd = np.ones(n); fd[-int(1.0 * SR):] = np.linspace(1, 0, int(1.0 * SR)); out *= fd[:, None]
    fi = np.ones(n); fi[:int(0.4 * SR)] = np.linspace(0, 1, int(0.4 * SR)); out *= fi[:, None]
    import scipy.io.wavfile as wf; wf.write(path, SR, (out / max(1e-9, np.abs(out).max()) * 0.89 * 32767).astype(np.int16))

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
                        "-movflags", "+faststart", "-shortest", D + ("wedding_storeroom_reel_bed_en.mp4" if EN else "wedding_storeroom_reel_bed.mp4")], check=True)
        if not EN: frame(1.9).save(D + "cover.jpg", quality=92)
        print("ok", DUR)

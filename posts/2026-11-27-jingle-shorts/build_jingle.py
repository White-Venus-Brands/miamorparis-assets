"""Three Christmas shorts cut to 'Punjabi Jingle Bell' (Tannay's screen-rec of the reel sound, 27 Nov).
Song analysed: ~151 bpm (beat 0.398 s); intro break -> DROP 4.46; dips -> drops 31.76, 40.44, 44.59.
  A  santa  (0.0-16.4)  Santa Paaji's gift list: Tannay in the Santa look, then one bottle per 2 beats, then per beat
  B  sorted (26.0-47.0) Christmas shopping, sorted: splits / grids / photos on the beat, black + 'wait for it' into the drop
  C  dance  (39.0-59.0) the bottles, in Santa hats, dance on the beat
Each comes with the song (may get muted: song from another reel) and silent (add the sound in the app at the given start).
Usage: python3 build_jingle.py WORKDIR {santa|sorted|dance}"""
import math, os, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy.signal import find_peaks, stft

WORK = sys.argv[1].rstrip("/") + "/"; WHICH = sys.argv[2]
D = os.path.dirname(os.path.abspath(__file__)) + "/"; R = os.path.normpath(D + "../..") + "/"
sys.path.insert(0, R + "posts/2026-11-27-xmas-sample")
W, H, FPS, SR = 1080, 1920, 25, 48000
GOLD, GOLD2, IVORY = (226, 186, 112), (240, 208, 150), (250, 245, 236)
SONG = "/tmp/claude-0/-home-claude/e1dc2e45-c278-5714-b377-734372e7d29a/scratchpad/aud8/trk.wav"
XMAS = "/tmp/claude-0/-home-claude/e1dc2e45-c278-5714-b377-734372e7d29a/scratchpad/xmas/"
DROPS = [4.46, 31.76, 40.44, 44.59]
SEG = {"santa": (0.0, 16.4), "sorted": (26.0, 47.0), "dance": (39.0, 59.0)}[WHICH]

def MS(s, st="Black"):
    f = ImageFont.truetype("/usr/share/fonts/truetype/google-fonts/ofl/montserrat/Montserrat[wght].ttf", s); f.set_variation_by_name(st); return f
def BOD(s):
    f = ImageFont.truetype(R + "assets/fonts/BodoniModa-Italic[opsz,wght].ttf", s); f.set_variation_by_name("SemiBold Italic"); return f
def cl(x): return max(0., min(1., x))
def ss(x): x = cl(x); return x * x * (3 - 2 * x)
def back(x): x = cl(x); c = 1.7; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2

# ---------- song: onsets + beat grid ----------
with wave.open(SONG) as w: SNG = np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, 2).astype(np.float32) / 32768
m = SNG.mean(1); f_, t_, Z = stft(m, SR, nperseg=2048, noverlap=1536); Mg = np.log1p(np.abs(Z) * 100)
fl = np.maximum(0, np.diff(Mg, axis=1)).sum(0); fl = (fl - fl.mean()) / fl.std()
pk, _ = find_peaks(fl, height=1.5, distance=int(.2 / (512 / SR))); ONS = t_[1:][pk]
P = .3978
def grid(a, b):
    o = ONS[(ONS > a) & (ONS < b)]; ph = np.angle(np.mean(np.exp(2j * np.pi * (o % P) / P))) / (2 * np.pi) * P % P
    k0 = math.ceil((a - ph) / P); return [ph + k * P for k in range(k0, int((b - ph) / P) + 1)]
S0, S1 = SEG; BEATS = [b - S0 for b in grid(S0, S1)]; DR = [d - S0 for d in DROPS if S0 < d < S1]
TOTAL = round((S1 - S0) * FPS) / FPS
def fr(x): return round(x * FPS) / FPS

# ---------- look ----------
RNG = np.random.default_rng(4)
BOKEH = [(RNG.uniform(0, W), RNG.uniform(0, H), RNG.uniform(30, 110), RNG.uniform(.15, .45), RNG.uniform(0, 6.28)) for _ in range(26)]
FLAKES = [dict(x=RNG.uniform(0, W), y=RNG.uniform(-H, H), v=RNG.uniform(70, 170), r=RNG.uniform(3, 9), sw=RNG.uniform(10, 40), ph=RNG.uniform(0, 6.28), a=RNG.uniform(110, 210)) for _ in range(100)]
_bg = None
def festive(t):
    global _bg
    if _bg is None:
        yy, xx = np.mgrid[0:H, 0:W]; r = np.sqrt(((xx - W / 2) / W) ** 2 + ((yy - H * .45) / H) ** 2)
        k = np.clip(1 - r * 1.6, 0, 1)[..., None]
        _bg = (np.array([8, 22, 16]) + k * np.array([22, 58, 38])).astype(np.uint8)
    im = Image.fromarray(_bg).convert("RGBA"); lay = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(lay)
    for x, y, r, a, ph in BOKEH:
        yy = (y - 18 * t) % H; aa = a * (.6 + .4 * math.sin(t * 1.5 + ph))
        d.ellipse((x - r, yy - r, x + r, yy + r), fill=GOLD + (int(255 * aa * .35),))
    im.alpha_composite(lay.filter(ImageFilter.GaussianBlur(18))); return im
def snow(t):
    lay = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(lay)
    for f in FLAKES:
        y = (f["y"] + f["v"] * t) % (H + 40) - 20; x = f["x"] + f["sw"] * math.sin(t * 1.3 + f["ph"])
        d.ellipse((x - f["r"], y - f["r"], x + f["r"], y + f["r"]), fill=(255, 255, 255, int(f["a"])))
    return lay.filter(ImageFilter.GaussianBlur(1.5))

_argv = sys.argv; _tmp = "/tmp/claude-0/-home-claude/e1dc2e45-c278-5714-b377-734372e7d29a/scratchpad/"
sys.argv = [_argv[0], _tmp + "xt", _tmp + "xt", _tmp + "models/u2net_human_seg.onnx"]
from xmas_look import make_hat          # the same Santa hat as the Christmas reel
sys.argv = _argv
CUT = {}
def bottle(name, h, hat=True):
    key = (name, h, hat)
    if key not in CUT:
        im = Image.open(R + f"assets/cutouts/{name}.png").convert("RGBA"); im = im.resize((int(im.width * h / im.height), h), Image.LANCZOS)
        if hat:
            a = np.asarray(im.getchannel("A")); rows = np.where(a.max(1) > 40)[0]; top = rows.min()
            cols = np.where(a[top + 2: top + max(6, h // 12)].max(0) > 40)[0]; cw = (cols.max() - cols.min()) if len(cols) else im.width // 2
            hw = int(min(max(cw * 1.35, im.width * .35), im.width * .6)); hat_im, (hx, hy) = make_hat(hw); hat_im = hat_im.rotate(-8, resample=Image.BICUBIC, center=(hx, hy))
            pad = hat_im.height; can = Image.new("RGBA", (max(im.width, hat_im.width + 40), im.height + pad), (0, 0, 0, 0))
            ox = (can.width - im.width) // 2; can.alpha_composite(im, (ox, pad))
            cx = ox + (cols.min() + cols.max()) / 2 if len(cols) else can.width / 2
            can.alpha_composite(hat_im, (int(cx - hx), int(pad + top + hw * .12 - hy)))
            im = can
        CUT[key] = im
    return CUT[key]
def put(im, b, cx, cy, sc=1.0, ang=0.0, shadow=True):
    if sc != 1.0: b = b.resize((max(1, int(b.width * sc)), max(1, int(b.height * sc))), Image.LANCZOS)
    if ang: b = b.rotate(ang, resample=Image.BICUBIC, expand=True)
    if shadow:
        sh = Image.new("RGBA", b.size, (0, 0, 0, 0)); sh.putalpha(b.getchannel("A").point(lambda v: int(v * .45)))
        im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(16)), (int(cx - b.width / 2 + 10), int(cy - b.height / 2 + 24)))
    im.alpha_composite(b, (int(cx - b.width / 2), int(cy - b.height / 2)))

def text(im, y, s, f, fill, a=1.0, stroke=0, maxw=940):
    lay = Image.new("RGBA", (W * 2, 500)); dd = ImageDraw.Draw(lay)
    dd.text((W, 250), s, font=f, fill=fill, anchor="mm", stroke_width=stroke, stroke_fill=(0, 0, 0)); lay = lay.crop(lay.getbbox())
    if lay.width > maxw: lay = lay.resize((maxw, int(lay.height * maxw / lay.width)), Image.LANCZOS)
    if a < 1: lay.putalpha(lay.getchannel("A").point(lambda v: int(v * a)))
    sh = Image.new("RGBA", lay.size); sh.putalpha(lay.getchannel("A").point(lambda v: int(v * .6)))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)), ((W - lay.width) // 2, y - lay.height // 2 + 6)); im.alpha_composite(lay, ((W - lay.width) // 2, y - lay.height // 2))
def popt(im, y, s, u, f, fill=IVORY, stroke=5):
    lay = Image.new("RGBA", (W * 2, 500)); ImageDraw.Draw(lay).text((W, 250), s, font=f, fill=fill, anchor="mm", stroke_width=stroke, stroke_fill=(0, 0, 0)); lay = lay.crop(lay.getbbox())
    sc = min(1, 900 / lay.width) * (.55 + .45 * back(u / .25)); lay = lay.resize((max(1, int(lay.width * sc)), max(1, int(lay.height * sc))), Image.LANCZOS)
    im.alpha_composite(lay, ((W - lay.width) // 2, y - lay.height // 2))
def flash(im, u, col=(255, 236, 200), a=150, d=.14):
    if 0 <= u < d: im.alpha_composite(Image.new("RGBA", (W, H), col + (int(a * (1 - u / d)),)))
def punch(im, u):
    z = 1 + .2 * (1 - ss(u / .35))
    if z <= 1.001: return im
    w, h = W / z, H / z; return im.resize((W, H), Image.LANCZOS, box=((W - w) / 2, (H - h) / 2, (W + w) / 2, (H + h) / 2))
def endcard(im, u, line1="Gift list: sorted"):
    im.alpha_composite(Image.new("RGBA", (W, H), (6, 10, 8, int(220 * ss(u / .3)))))
    lg = Image.open(R + "assets/cutouts/logo_gold.png").convert("RGBA"); lg = lg.resize((230, int(230 * lg.height / lg.width)), Image.LANCZOS)
    a = ss((u - .1) / .35); lg.putalpha(lg.getchannel("A").point(lambda v: int(v * a))); im.alpha_composite(lg, ((W - lg.width) // 2, 640 - lg.height // 2))
    text(im, 850, "Mi Amor Paris", BOD(86), GOLD2, ss((u - .25) / .3))
    text(im, 960, line1, MS(46, "SemiBold"), IVORY, ss((u - .45) / .3))
    text(im, 1040, "Lajpat Nagar · R Cube Monad Mall · miamorparis.in", MS(30, "Medium"), (215, 205, 190), ss((u - .6) / .3))
    text(im, 1120, "comment SCENT for the quiz", MS(38, "Medium"), (215, 205, 190), ss((u - .75) / .3))

def last_beat(t):
    b = [x for x in BEATS if x <= t]; return (t - b[-1]) if b else 9

# ---------- A: Santa Paaji ki gift list ----------
LIST = [("MUMMY", "flora5_perf", "Flora 5"), ("PAPA", "derossa", "De Rossa Oudh"), ("DIDI", "missaqua_perf", "Miss Aqua"), ("BHAI", "mraqua_perf", "Mr Aqua"),
        ("THE BOSS", "moksha", "Moksha"), ("SECRET SANTA", "liita", "Love Is In The Air"), ("YOURSELF", "moksha_bodywash", "Moksha body wash"), ("YOUR CRUSH", "missaqua_bw", "Miss Aqua body wash")]
def face(k, i):
    fs = sorted(os.listdir(XMAS + f"f25_{k}")); im = Image.open(XMAS + f"f25_{k}/" + fs[min(i, len(fs) - 1)]).convert("RGB")
    a = np.asarray(im).astype(np.float32) / 255; a = .03 + a * .95; a = a ** np.array([.97, 1., 1.05]); return Image.fromarray(np.clip(a * 255, 0, 255).astype(np.uint8)).convert("RGBA")
def santa(t):
    d0 = DR[0]; slow = [d0 + 2 * P * k for k in range(8)]; fast0 = slow[-1] + 2 * P; fast = [fast0 + P * k for k in range(8)]; end0 = fast[-1] + P
    if t < d0:
        if t < 2.4: im = face("5227", int(t * FPS))
        elif t < 3.9: im = face("5222", 55 + int((t - 2.4) * FPS))
        else: im = Image.new("RGBA", (W, H), (0, 0, 0, 255))
        im.alpha_composite(snow(t))
        if t < 2.4: popt(im, 330, "SANTA IS PUNJABI", t, MS(100)); popt(im, 450, "THIS YEAR", t - .2, MS(100), GOLD)
        elif t < 3.9: popt(im, 330, "AND HE SHOPS IN", t - 2.4, MS(84)); popt(im, 440, "LAJPAT NAGAR", t - 2.6, MS(96), GOLD)
        else: text(im, 960, "Santa Paaji ki gift list...", BOD(80), GOLD2, ss((t - 3.9) / .2))
        if t < .25: im.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(255 * (1 - t / .25)))))
        return im
    if t >= end0:
        im = festive(t); put(im, bottle("moksha", 760), W / 2, 1180, .9); im.alpha_composite(snow(t)); endcard(im, t - end0); return im
    im = festive(t)
    if t < fast0:
        i = max(j for j, s in enumerate(slow) if s <= t); u = t - slow[i]; who, nm, label = LIST[i]
        put(im, bottle(nm, 820), W / 2, 1060, 1 + .12 * (1 - back(u / .3)), 4 * math.sin(t * 7.85))
        popt(im, 330, "FOR " + who, u, MS(96)); text(im, 1650, label, BOD(74), GOLD2, ss(u / .2))
    else:
        i = max(j for j, s in enumerate(fast) if s <= t); u = t - fast[i]; who, nm, label = LIST[i]
        put(im, bottle(nm, 820), W / 2, 1060, 1 + .15 * (1 - back(u / .2)))
        popt(im, 330, who, u, MS(110), GOLD)
    im.alpha_composite(snow(t))
    if 0 <= t - d0 < .4: im = punch(im, t - d0)
    flash(im, t - d0, a=170); return im

# ---------- B: Christmas shopping, sorted ----------
PHOTOS = {"trio": R + "posts/2026-11-marhaba-yellow/src/trio.png", "inbox": R + "posts/2026-11-marhaba-yellow/src/inbox.png",
          "zeenat": R + "posts/2026-11-02-oudh-candles/zeenat_4.jpg", "aries": R + "posts/2026-11-21-black-friday-reel/src/zodiac_aries.jpg",
          "gemini": R + "posts/2026-11-21-black-friday-reel/src/zodiac_gemini.jpg", "abyad": R + "posts/2026-11-02-oudh-candles/abyad_1.jpg"}
_ph = {}
def photo(k, w, h, z=1.0):
    if k not in _ph: _ph[k] = Image.open(PHOTOS[k]).convert("RGB")
    im = _ph[k]; s = max(w / im.width, h / im.height) * z; q = im.resize((int(im.width * s) + 1, int(im.height * s) + 1), Image.LANCZOS)
    return q.crop(((q.width - w) // 2, (q.height - h) // 2, (q.width - w) // 2 + w, (q.height - h) // 2 + h)).convert("RGBA")
def tile_bottle(nm, w, h, t):
    can = festive(t).resize((w, h), Image.LANCZOS); b = bottle(nm, int(h * .78), True); put(can, b, w / 2, h * .55, 1.0, shadow=False); return can
def splitv(a, b):
    can = Image.new("RGBA", (W, H), GOLD + (255,)); hh = (H - 18) // 2; can.alpha_composite(a, (6, 6)); can.alpha_composite(b, (6, hh + 12)); return can
def grid4(items):
    can = Image.new("RGBA", (W, H), GOLD + (255,)); cw, ch = (W - 18) // 2, (H - 18) // 2
    for i, it in enumerate(items): can.alpha_composite(it, (6 + (i % 2) * (cw + 6), 6 + (i // 2) * (ch + 6)))
    return can
def sorted_(t):
    tt = t + S0; cw, ch = (W - 18) // 2, (H - 18) // 2; hh = (H - 18) // 2 - 6
    cuts = [b for b in BEATS if b < TOTAL][::2]
    i = max([j for j, c in enumerate(cuts) if c <= t] or [0]); u = t - (cuts[i] if cuts else 0)
    if tt < 30.5:      # hook + two-panel splits every 2 beats
        seq = [("photo", "trio"), ("bottle", "moksha"), ("photo", "inbox"), ("bottle", "derossa"), ("photo", "zeenat"), ("bottle", "liita"), ("photo", "abyad"), ("bottle", "missaqua_perf")]
        k = seq[i % 8]; k2 = seq[(i + 3) % 8]
        mk = lambda kk, w, h: photo(kk[1], w, h, 1 + .05 * u) if kk[0] == "photo" else tile_bottle(kk[1], w, h, t)
        im = splitv(mk(k, W - 12, hh), mk(k2, W - 12, hh)); im = punch(im, u) if u < .2 else im
        if t < 2.6: popt(im, 960, "CHRISTMAS SHOPPING", t, MS(92)); popt(im, 1080, "SORTED IN 20 SECONDS", t - .25, MS(64), GOLD)
    elif tt < 31.76:   # the dip: black, wait for it
        im = Image.new("RGBA", (W, H), (0, 0, 0, 255)); text(im, 960, "wait for it...", BOD(84), GOLD2, ss((tt - 30.5) / .3))
    elif tt < 40.44:   # grids every 2 beats
        pool = ["moksha", "derossa", "flora5_perf", "mraqua_perf", "missaqua_perf", "liita", "moksha_bodywash", "mraqua_bw"]
        im = grid4([tile_bottle(pool[(i + j) % 8], cw, ch, t) if (i + j) % 3 else photo(["trio", "zeenat", "inbox", "gemini"][(i + j) % 4], cw, ch) for j in range(4)])
        if u < .3: im = punch(im, u)
        if 31.76 <= tt < 33.0: popt(im, 960, "FOR EVERYONE", tt - 31.76, MS(110))
    elif tt < 44.59:   # one hero per beat
        b = [x for x in BEATS if x <= t]; u2 = t - b[-1]; heroes = ["moksha", "derossa", "liita", "flora5_perf", "mraqua_perf", "missaqua_perf"]
        im = festive(t); put(im, bottle(heroes[len(b) % 6], 820), W / 2, 1080, 1 + .15 * (1 - back(u2 / .2))); im.alpha_composite(snow(t))
        if 40.44 <= tt < 41.6: popt(im, 330, "ONE FOR THEM", tt - 40.44, MS(100))
        if 42.0 <= tt < 43.3: popt(im, 330, "ONE FOR YOU", tt - 42.0, MS(100), GOLD)
    else:
        e0 = 44.59 + 1.2
        if tt < e0:
            im = grid4([tile_bottle(n, cw, ch, t) for n in ["moksha", "liita", "derossa", "missaqua_perf"]]); im = punch(im, tt - 44.59) if tt - 44.59 < .35 else im
        else:
            im = festive(t); put(im, bottle("liita", 760), W / 2, 1180, .9); im.alpha_composite(snow(t)); endcard(im, tt - e0, "Christmas: sorted")
    for d in DR: flash(im, t - d, a=170)
    return im

# ---------- C: the bottles dance ----------
TROUPE = ["derossa", "moksha", "liita", "mraqua_perf", "flora5_perf", "missaqua_perf"]
POS = [(250, 760), (540, 720), (830, 760), (250, 1360), (540, 1320), (830, 1360)]
def dance(t):
    tt = t + S0; im = festive(t); started = tt >= 40.44; big = 44.59 <= tt < 45.8; solo0 = 50.2; end0 = 56.6
    if tt >= end0:
        for j, (nm, (x, y)) in enumerate(zip(TROUPE, POS)): put(im, bottle(nm, 430), x, y + 60, .75)
        im.alpha_composite(snow(t)); endcard(im, tt - end0, "Merry Christmas"); return im
    b = [x for x in BEATS if x <= t]; u = (t - b[-1]) if b else 9; n = len(b)
    if solo0 <= tt < end0:          # each bottle gets a solo, 2 beats each
        k = int((tt - solo0) / (2 * P)) % 6
        for j, (nm, (x, y)) in enumerate(zip(TROUPE, POS)):
            if j != k: put(im, bottle(nm, 430), x, y, .8, 6 * math.sin(t * 7.9 + j))
        im.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, 110)))
        put(im, bottle(TROUPE[k], 820), W / 2, 1040, 1 + .12 * (1 - back(u / .25)), 10 * math.sin(t * 7.9))
        nm = {"derossa": "De Rossa Oudh", "moksha": "Moksha", "liita": "Love Is In The Air", "mraqua_perf": "Mr Aqua", "flora5_perf": "Flora 5", "missaqua_perf": "Miss Aqua"}[TROUPE[k]]
        text(im, 1650, nm, BOD(78), GOLD2)
    else:
        for j, (nm, (x, y)) in enumerate(zip(TROUPE, POS)):
            if started:
                ph = (n + j) % 2; hop = (1 - ss(u / .3)) * (60 if not big else 140) * (1 if ph else .4)
                ang = (9 if (n + j) % 2 else -9) * (1.8 if big else 1)
                put(im, bottle(nm, 430), x, y - hop, 1 + .05 * (1 - ss(u / .2)), ang)
            else: put(im, bottle(nm, 430), x, y)
        if not started: popt(im, 300, "WHEN THE BOTTLES HEAR", t, MS(70)); popt(im, 390, "PUNJABI JINGLE BELL", t - .25, MS(78), GOLD)
        if 46.2 <= tt < 49.8: text(im, 300, "Merry Christmas", BOD(96), GOLD2, ss((tt - 46.2) / .3) * (1 - ss((tt - 49.5) / .3)))
    im.alpha_composite(snow(t))
    for d in DR: flash(im, t - d, a=150)
    if big: im = punch(im, tt - 44.59)
    return im

RENDER = {"santa": santa, "sorted": sorted_, "dance": dance}[WHICH]
def frame(t):
    im = RENDER(t)
    if t > TOTAL - .5: im.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(255 * ss((t - TOTAL + .5) / .5)))))
    return im.convert("RGB")

if __name__ == "__main__":
    only = os.environ.get("ONLY")
    if only:
        for s_ in only.split(","): frame(float(s_)).save(WORK + f"j_{WHICH}_{s_}.jpg", quality=85)
        print("beats", [round(b, 2) for b in BEATS[:12]], "drops", DR); sys.exit()
    fd = WORK + f"fr_{WHICH}/"; os.makedirs(fd, exist_ok=True)
    for i in range(int(round(TOTAL * FPS))): frame(i / FPS).save(fd + f"{i:04d}.jpg", quality=93)
    a = SNG[int(S0 * SR):int(S1 * SR)].copy(); fi = int((.02 if S0 == 0 else .25) * SR); a[:fi] *= np.linspace(0, 1, fi)[:, None]
    fo = int(.6 * SR); a[-fo:] *= np.linspace(1, 0, fo)[:, None]; a *= 10 ** (-1 / 20) / np.max(np.abs(a))
    with wave.open(fd + "a.wav", "wb") as w_:
        w_.setnchannels(2); w_.setsampwidth(2); w_.setframerate(SR); w_.writeframes((a * 32767).astype(np.int16).tobytes())
    base = ["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", fd + "%04d.jpg"]
    enc = ["-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p", "-r", str(FPS), "-movflags", "+faststart"]
    subprocess.run(base + ["-i", fd + "a.wav", "-map", "0:v", "-map", "1:a"] + enc + ["-c:a", "aac", "-b:a", "256k", "-shortest", D + f"jingle_{WHICH}.mp4"], check=True)
    subprocess.run(base + enc + ["-an", D + f"jingle_{WHICH}_silent.mp4"], check=True)
    print("done", WHICH, TOTAL)

"""Reel: 'Diwali gifts, ranked. Brutally honest.'  Tier list, no people. 1080x1920, 30 fps, ~23 s.
Usual Diwali gifts (emoji cards) drop into D..A; the REAL Smuggler gift-box photo lands in S tier.
No prices (DM for prices). Original synthesized SFX; IG library music added at scheduling.
Usage: python3 build.py WORKDIR   (ONLY=2.0,5.5 for stills)"""
import math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy.signal import lfilter

D = os.path.dirname(os.path.abspath(__file__)) + "/"
R = D + "../../"
sys.path.insert(0, R + "ops/stories"); import diwali  # noqa: E402
LOGO = Image.open(R + "assets/cutouts/logo_gold.png").convert("RGBA")
OUT = sys.argv[1].rstrip("/") + "/" if len(sys.argv) > 1 else "/tmp/tier/"
W, H, FPS = 1080, 1920, 30
GOLD, IVORY = (226, 186, 112), (250, 240, 226)

def inter(s, w="Black"): return ImageFont.truetype(f"/usr/share/fonts/opentype/inter/InterDisplay-{w}.otf", s)
def lora(s, it=True): return ImageFont.truetype("/usr/share/fonts/truetype/google-fonts/Lora-" + ("Italic-Variable" if it else "Variable") + ".ttf", s)
def pop(s, w="Bold"): return ImageFont.truetype(f"/usr/share/fonts/truetype/google-fonts/Poppins-{w}.ttf", s)
def cl(x): return max(0.0, min(1.0, x))
def ss(x): x = cl(x); return x * x * (3 - 2 * x)
def back(x): x = cl(x); c = 1.9; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2
def lerp(a, b, u): return a + (b - a) * u

# ---------- timeline ----------
HOOK_END = 2.4
STEP = 3.0
ITEMS = [  # tier, emoji, name, one-liner (each line held >= 1 s)
    ("D", "🍬", "Soan papdi", "Ghoom ke wapas aa jayegi."),
    ("C", "🍽️", "Dinner set", "Pichhle saal wala abhi bhi dabbe mein hai."),
    ("B", "🥜", "Dry fruits", "Kaju gayab. Kishmish bachi."),
    ("A", "🍫", "Chocolate hamper", "Pyaar hai. Par 2 din ka."),
]
T_ITEM = [HOOK_END + k * STEP for k in range(len(ITEMS))]
S_START = HOOK_END + len(ITEMS) * STEP        # 14.4
S_REVEAL = S_START + 1.3                      # box appears
S_FLY = S_START + 3.2                         # flies into S row
END = S_START + 4.8                           # 19.2
DUR = END + 4.6                               # 23.8

TIERS = ["S", "A", "B", "C", "D"]
TCOL = {"S": (226, 186, 112), "A": (255, 160, 110), "B": (255, 214, 120), "C": (170, 220, 140), "D": (130, 180, 235)}
BX0, BY0, ROWH, LABW = 60, 600, 176, 170      # board
SLOT_X = BX0 + LABW + 30
TILE = 150

# ---------- assets ----------
yy = np.linspace(0, 1, H)[:, None, None]
BG = (np.array([62, 12, 28]) * (1 - yy) + np.array([20, 4, 10]) * yy) * np.ones((1, W, 1))
BGIMG = Image.fromarray(BG.astype(np.uint8)).convert("RGBA")
rng = np.random.default_rng(11)
bok = Image.new("RGBA", (W, H * 2)); bd = ImageDraw.Draw(bok)
for _ in range(55):
    x, y, r = rng.uniform(0, W), rng.uniform(0, H * 2), rng.uniform(5, 28)
    bd.ellipse((x - r, y - r, x + r, y + r), fill=GOLD + (int(rng.uniform(20, 70)),))
bok = bok.filter(ImageFilter.GaussianBlur(7))

def background(t):
    im = BGIMG.copy(); off = int(t * 35) % H
    im.alpha_composite(bok.crop((0, H - off, W, 2 * H - off))); return im

EMO = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf", 109)
_emo = {}
def emoji(ch, size):
    k = (ch, size)
    if k not in _emo:
        lay = Image.new("RGBA", (160, 160)); ImageDraw.Draw(lay).text((80, 80), ch, font=EMO, embedded_color=True, anchor="mm")
        lay = lay.crop(lay.getbbox()); s = size / max(lay.size)
        _emo[k] = lay.resize((max(1, int(lay.width * s)), max(1, int(lay.height * s))), Image.LANCZOS)
    return _emo[k]

BOX = diwali.boxphoto("smuggler").convert("RGB")
_box = {}
def boxcard(size, key="smuggler"):
    k = (key, size)
    if k not in _box:
        src = BOX if key == "smuggler" else diwali.boxphoto(key).convert("RGB")
        im = src.resize((size, size), Image.LANCZOS).convert("RGBA")
        rad = max(10, size // 18)
        m = Image.new("L", (size, size), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, size - 1, size - 1), rad, fill=255); im.putalpha(m)
        b = max(3, size // 80)
        fr = Image.new("RGBA", (size + 2 * b, size + 2 * b)); ImageDraw.Draw(fr).rounded_rectangle((0, 0, size + 2 * b - 1, size + 2 * b - 1), rad + b, fill=GOLD + (255,))
        fr.alpha_composite(im, (b, b)); _box[k] = fr
    return _box[k]

def tile(ch):  # item tile used on the board
    t = Image.new("RGBA", (TILE, TILE)); d = ImageDraw.Draw(t)
    d.rounded_rectangle((0, 0, TILE - 1, TILE - 1), 22, fill=(255, 248, 238, 255))
    e = emoji(ch, 104); t.alpha_composite(e, ((TILE - e.width) // 2, (TILE - e.height) // 2)); return t

def fade(img, a):
    if a >= 1: return img
    img = img.copy(); img.putalpha(img.getchannel("A").point(lambda v: int(v * a))); return img

def scaled(img, s):
    return img.resize((max(1, int(img.width * s)), max(1, int(img.height * s))), Image.LANCZOS)

def shadow_paste(im, lay, x, y, blur=12, strength=0.7):
    sh = Image.new("RGBA", lay.size, (0, 0, 0, 0)); sh.putalpha(lay.getchannel("A").point(lambda v: int(v * strength)))
    pad = blur * 3; big = Image.new("RGBA", (lay.width + 2 * pad, lay.height + 2 * pad)); big.alpha_composite(sh, (pad, pad))
    im.alpha_composite(big.filter(ImageFilter.GaussianBlur(blur)), (int(x) - pad, int(y) - pad + 8)); im.alpha_composite(lay, (int(x), int(y)))

def text_layer(lines):
    lay = Image.new("RGBA", (W, 600)); d = ImageDraw.Draw(lay); y = 10
    for s, f, c in lines:
        d.text((W / 2, y), s, font=f, fill=c + (255,), anchor="ma"); y += f.size * 1.15
    return lay.crop(lay.getbbox())

def ctext(im, y, s, f, col, a=1.0, shadow=True):
    lay = fade(text_layer([(s, f, col)]), a)
    if shadow: shadow_paste(im, lay, (W - lay.width) / 2, y, 8, 0.8)
    else: im.alpha_composite(lay, ((W - lay.width) // 2, int(y)))

def wrapped(im, y, s, f, col, a=1.0, maxw=940):
    words, lines, cur = s.split(), [], ""
    d0 = ImageDraw.Draw(im)
    for w_ in words:
        c = (cur + " " + w_).strip()
        if d0.textlength(c, font=f) > maxw and cur: lines.append(cur); cur = w_
        else: cur = c
    lines.append(cur)
    for i, l in enumerate(lines): ctext(im, y + i * f.size * 1.18, l, f, col, a)

# ---------- board ----------
def row_y(tier): return BY0 + TIERS.index(tier) * ROWH

def board(im, t, alpha=1.0, pulse_s=0.0):
    lay = Image.new("RGBA", im.size); d = ImageDraw.Draw(lay)
    for i, tr in enumerate(TIERS):
        y = BY0 + i * ROWH
        d.rounded_rectangle((BX0, y, W - BX0, y + ROWH - 12), 18, fill=(255, 255, 255, 22))
        col = TCOL[tr]
        if tr == "S" and pulse_s > 0:
            k = 0.5 + 0.5 * math.sin(pulse_s * 14); col = tuple(int(lerp(c, 255, 0.35 * k)) for c in col)
        d.rounded_rectangle((BX0, y, BX0 + LABW, y + ROWH - 12), 18, fill=col + (255,))
        d.text((BX0 + LABW / 2, y + (ROWH - 12) / 2), tr, font=inter(96), fill=(30, 10, 16, 255), anchor="mm")
    im.alpha_composite(fade(lay, alpha))

def placed_tiles(im, t):
    """Items that have landed stay on the board."""
    for k, (tr, ch, _, _) in enumerate(ITEMS):
        land = T_ITEM[k] + 1.55
        if t >= land:
            x, y = SLOT_X, row_y(tr) + (ROWH - 12 - TILE) / 2
            bounce = 1 + 0.12 * math.exp(-(t - land) * 10) * math.cos((t - land) * 30)
            tl = scaled(tile(ch), bounce)
            im.alpha_composite(tl, (int(x + (TILE - tl.width) / 2), int(y + (TILE - tl.height) / 2)))
            ImageDraw.Draw(im).text((x + TILE + 26, y + TILE / 2), ITEMS[k][2], font=pop(40, "SemiBold") if os.path.exists("/usr/share/fonts/truetype/google-fonts/Poppins-SemiBold.ttf") else pop(40, "Bold"), fill=IVORY + (235,), anchor="lm")
    if t >= S_FLY + 0.5:
        x, y = SLOT_X, row_y("S") + (ROWH - 12 - TILE) / 2
        bc = boxcard(TILE - 6); im.alpha_composite(bc, (int(x), int(y)))
        ImageDraw.Draw(im).text((x + TILE + 26, y + TILE / 2), "Mi Amor Paris gift set", font=pop(40, "Bold"), fill=GOLD + (255,), anchor="lm")

# ---------- scenes ----------
def scene_hook(im, t):
    board(im, t, ss((t - 0.5) / 0.5))
    s1 = back(t / 0.3); lay = scaled(text_layer([("DIWALI GIFTS,", inter(112), IVORY)]), 1.6 - 0.6 * s1)
    shadow_paste(im, fade(lay, ss(t / 0.12)), (W - lay.width) / 2, 170 + (1 - s1) * -30, 14)
    if t > 0.55:
        u = back((t - 0.55) / 0.3); lay = scaled(text_layer([("RANKED.", inter(150), GOLD)]), 1.5 - 0.5 * u)
        shadow_paste(im, fade(lay, ss((t - 0.55) / 0.12)), (W - lay.width) / 2, 300, 14)
    if t > 1.2: ctext(im, 470, "Brutally honest. Sorry relatives.", lora(52), (240, 220, 200), ss((t - 1.2) / 0.3))

def scene_item(im, t, k):
    tr, ch, name, line = ITEMS[k]; u = t - T_ITEM[k]
    board(im, t); placed_tiles(im, t)
    # card: pop in at top (0-0.3), hold, fly to row (1.1-1.55)
    if u < 1.55:
        big = 230
        if u < 1.1:
            s = back(u / 0.3); x = W / 2 - big / 2; y = 190; sz = big * (0.4 + 0.6 * s)
        else:
            v = ss((u - 1.1) / 0.45); sz = lerp(big, TILE, v)
            x = lerp(W / 2 - big / 2, SLOT_X, v); y = lerp(190, row_y(tr) + (ROWH - 12 - TILE) / 2, v)
        tl = scaled(tile(ch), sz / TILE)
        shadow_paste(im, tl, x + (big - tl.width) / 2 if u < 1.1 else x, y + (big - tl.height) / 2 if u < 1.1 else y, 14, 0.6)
        if u < 1.15: ctext(im, 445 if u < 1.1 else 445, name, inter(64, "ExtraBold"), IVORY, ss(u / 0.2) * (1 - ss((u - 1.0) / 0.15)))
    # one-liner after it lands (held ~1.4 s)
    if u >= 1.5:
        a = ss((u - 1.5) / 0.2) * (1 - ss((u - STEP + 0.12) / 0.12))
        ctext(im, 200, f"{tr} TIER", inter(58, "Black"), TCOL[tr], a)
        wrapped(im, 290, line, lora(66), IVORY, a)

def scene_s(im, t):
    u = t - S_START
    board(im, t, pulse_s=u if u < 1.3 else 0); placed_tiles(im, t)
    if u < 1.3:
        ctext(im, 230, "Aur S tier mein...", inter(84, "Black"), GOLD, ss(u / 0.25))
        dots = "." * (1 + int(u * 4) % 3); ctext(im, 360, dots, inter(84, "Black"), IVORY, ss(u / 0.25))
    elif u < 3.2:
        v = u - 1.3
        # gold burst + dim board
        dim = Image.new("RGBA", im.size, (10, 2, 6, int(228 * ss(v / 0.2)))); im.alpha_composite(dim)
        rays = Image.new("RGBA", im.size); rd = ImageDraw.Draw(rays); cx, cy = W / 2, 820
        for i in range(18):
            ang = i * math.pi / 9 + v * 0.4
            rd.polygon([(cx, cy), (cx + 1400 * math.cos(ang - 0.07), cy + 1400 * math.sin(ang - 0.07)), (cx + 1400 * math.cos(ang + 0.07), cy + 1400 * math.sin(ang + 0.07))], fill=GOLD + (int(40 * ss(v / 0.3)),))
        im.alpha_composite(rays.filter(ImageFilter.GaussianBlur(4)))
        s = back(v / 0.35); bc = boxcard(int(640 * (0.5 + 0.5 * s)))
        shadow_paste(im, fade(bc, ss(v / 0.1)), (W - bc.width) / 2, cy - bc.height / 2, 24, 0.8)
        ctext(im, 180, "S TIER", inter(96, "Black"), GOLD, ss(v / 0.2))
        ctext(im, 300, "Mi Amor Paris Diwali gift set", pop(50, "Bold"), IVORY, ss((v - 0.2) / 0.25))
        if v > 0.7: ctext(im, 1190, "Body wash + perfume + moisturiser", pop(44, "Medium"), (240, 222, 200), ss((v - 0.7) / 0.25))
        if v > 0.9: ctext(im, 1290, "Har spray pe yaad aaoge.", lora(70), GOLD, ss((v - 0.9) / 0.25))
    else:
        v = ss((u - 3.2) / 0.5); big = int(lerp(640, TILE - 6, v))
        dim = Image.new("RGBA", im.size, (10, 2, 6, int(228 * (1 - v)))); im.alpha_composite(dim)
        if u < 3.7:
            bc = boxcard(big); x = lerp((W - 640) / 2, SLOT_X, v); y = lerp(820 - 320, row_y("S") + (ROWH - 12 - TILE) / 2, v)
            shadow_paste(im, bc, x, y, 16, 0.7)
        if u > 3.8: ctext(im, 230, "Debate closed.", inter(84, "Black"), IVORY, ss((u - 3.8) / 0.2))

def scene_end(im, t):
    u = t - END
    lg = scaled(LOGO, 220 / LOGO.width); im.alpha_composite(fade(lg, ss(u / 0.4)), ((W - lg.width) // 2, 150))
    ctext(im, 370, "THE DIWALI GIFT SETS", inter(74, "Black"), GOLD, ss((u - 0.15) / 0.35))
    ctext(im, 470, "Buy one perfume, get the whole Diwali set", pop(42, "Medium"), IVORY, ss((u - 0.35) / 0.35))
    keys = ["liita", "smuggler", "moksha", "holdmi", "flora5"]
    for i, kk in enumerate(keys):
        a = ss((u - 0.5 - i * 0.08) / 0.35)
        if a > 0:
            bc = fade(boxcard(186, kk), a); im.alpha_composite(bc, (int(W / 2 - 2.5 * 196 + i * 196 + 2), 590))
    ctext(im, 860, "10 scents  ·  for her & for him", pop(40, "Medium"), (240, 222, 200), ss((u - 0.8) / 0.35))
    ctext(im, 990, "Delhi NCR delivery within 2-3 hours*", inter(54, "ExtraBold"), (150, 230, 175), ss((u - 1.0) / 0.35))
    a2 = ss((u - 1.3) / 0.35)
    if a2 > 0:
        f = inter(48, "Black"); lab = "DM FOR PRICES & DIWALI DEALS"; d = ImageDraw.Draw(im); tw = d.textlength(lab, font=f)
        lay = Image.new("RGBA", im.size); dl = ImageDraw.Draw(lay); y = 1180
        dl.rounded_rectangle(((W - tw) / 2 - 48, y - 52, (W + tw) / 2 + 48, y + 52), 52, fill=GOLD + (255,))
        dl.text((W / 2, y), lab, font=f, fill=(40, 8, 16, 255), anchor="mm"); im.alpha_composite(fade(lay, a2))
    ctext(im, 1290, "OR VISIT US AT LAJPAT NAGAR-II", pop(38, "Bold"), (226, 180, 110), ss((u - 1.5) / 0.35))
    ctext(im, 1380, "*During office hours", pop(32, "Medium"), (220, 200, 180), ss((u - 1.5) / 0.35), shadow=False)

def frame(t):
    im = background(t)
    if t < HOOK_END: scene_hook(im, t)
    elif t < S_START: scene_item(im, t, int((t - HOOK_END) // STEP))
    elif t < END: scene_s(im, t)
    else: scene_end(im, t)
    for tc in [HOOK_END, S_REVEAL, END]:
        if 0 <= t - tc < 0.08: im = Image.blend(im, Image.new("RGBA", im.size, (255, 245, 230, 255)), 0.5 * (1 - (t - tc) / 0.08))
    for k in range(len(ITEMS)):   # landing shake
        v = t - (T_ITEM[k] + 1.55)
        if 0 <= v < 0.18:
            m = int(10 * (1 - v / 0.18)); im = im.transform(im.size, Image.AFFINE, (1, 0, rng.integers(-m, m + 1), 0, 1, rng.integers(-m, m + 1)), fillcolor=(20, 4, 10, 255))
    return im.convert("RGB")

# ---------- audio (SFX + light beat; IG music is layered on Instagram) ----------
SR = 44100
def audio(path):
    n = int(SR * DUR); out = np.zeros(n, np.float32)
    def add(sig, at, g=1.0):
        i = int(at * SR); j = min(n, i + len(sig))
        if i < n: out[i:j] += sig[: j - i] * g
    def env(L, a=0.005, r=0.2):
        x = np.arange(int(L * SR)) / SR; return np.minimum(1, x / a) * np.exp(-x / r)
    def tone(f, L, g, a=.01, r=.3, harm=(1, .5, .25)):
        x = np.arange(int(L * SR)) / SR; return sum(h * np.sin(2 * np.pi * f * (i + 1) * x) for i, h in enumerate(harm)) * env(L, a, r) * g
    kick = lambda: np.sin(2 * np.pi * (48 + 110 * np.exp(-np.arange(int(.35 * SR)) / SR / .04)) * np.arange(int(.35 * SR)) / SR) * env(.35, .002, .12)
    noise = lambda L, s: np.random.default_rng(s).normal(0, 1, int(L * SR))
    hat = lambda: lfilter([1, -1], [1, -0.6], noise(.05, 1)) * env(.05, .001, .012) * 0.2
    beat = 60 / 112
    k = 0
    while k * beat < END:
        b = k * beat
        if b > 0.5 and not (S_START <= b < S_REVEAL): add(kick(), b, 0.55); add(hat(), b + beat / 2)
        k += 1
    for at in (0.0, 0.55): add(kick(), at, 1.3)                        # hook slams
    for kk in range(len(ITEMS)):
        t0 = T_ITEM[kk]
        add(tone(660, .15, .25, r=.05, harm=(1, .3)), t0)                # pop
        w = lfilter([1], [1, -0.9], noise(.45, kk)) * np.hanning(int(.45 * SR)) * 0.05; add(w, t0 + 1.1)  # whoosh
        add(kick(), t0 + 1.55, 1.1)                                       # thud
        add(tone([196, 220, 247, 294][kk], .4, .18, r=.15), t0 + 1.6)    # rising stinger D->A
    # drumroll
    L = S_REVEAL - S_START; roll = noise(L, 9) * (0.03 + 0.12 * np.linspace(0, 1, int(L * SR))) * (0.6 + 0.4 * np.sign(np.sin(2 * np.pi * 18 * np.arange(int(L * SR)) / SR)))
    add(lfilter([1, -0.5], [1], roll), S_START)
    add(kick(), S_REVEAL, 1.5)
    for f in (523.3, 659.3, 784, 1046.5): add(tone(f, 2.8, .08, r=1.0, harm=(1, .35)), S_REVEAL)   # reveal chord
    for f in (1568, 2093, 2637): add(tone(f, 1.2, .05, r=.4, harm=(1,)), S_REVEAL + 0.15)
    add(kick(), S_FLY + 0.5, 0.9)
    for f in (130.8, 196, 261.6, 329.6, 392): add(tone(f, 4.0, .09, a=.25, r=1.6, harm=(1, .4, .2)), END)
    out = np.tanh(out * 1.1) * 0.85
    fd = np.ones(n); fd[-int(0.7 * SR):] = np.linspace(1, 0, int(0.7 * SR)); out *= fd
    import scipy.io.wavfile as wf; wf.write(path, SR, (np.stack([out, np.roll(out, 80)], 1) * 32767).astype(np.int16))

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
                        "-movflags", "+faststart", "-shortest", D + "diwali_gift_tier_list.mp4"], check=True)
        frame(1.8).save(D + "cover.jpg", quality=92)
        print("ok", DUR)

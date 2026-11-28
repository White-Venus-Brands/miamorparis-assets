"""'Swipe right on every beat' interactive Reel (28 Nov).
Intro tells the viewer to put a thumb on the screen and swipe right on every beat. From the Punjabi Jingle Bell drop,
every 2 beats the whole screen whips right (the viewer's swipe) and something happens, built on this month's trends
(trend research 18 Nov): the Shanaya 'imported hai?' trend, 'It's time', Add to cart, the IPL trade card, Delhi air
(one dry joke, no health claim), No-no-no-YES shaadi gifts, the dating-app match, a slot machine, then the end card.
Usage: python3 build_swipe.py WORKDIR   (ONLY=t,t,... renders test frames)"""
import math, os, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

WORK = sys.argv[1].rstrip("/") + "/"; os.makedirs(WORK, exist_ok=True)
D = os.path.dirname(os.path.abspath(__file__)) + "/"; R = os.path.normpath(D + "../..") + "/"
sys.path.insert(0, R + "posts/2026-11-27-jingle-shorts"); _a = sys.argv; sys.argv = [_a[0], WORK, "santa"]
import build_jingle as J
sys.argv = _a
W, H, FPS, SR, P = J.W, J.H, J.FPS, J.SR, J.P
GOLD, GOLD2, IVORY = J.GOLD, J.GOLD2, J.IVORY
RED, GREEN = (214, 58, 58), (70, 190, 120)
def fr(x): return round(x * FPS) / FPS
DROP = 3.18; SONG0 = J.DR[0] - DROP; SEG = 2 * P
PANELS = 18; SW = [DROP + k * SEG for k in range(PANELS + 1)]          # swipe k starts panel k (panel PANELS = the 'you swiped' card)
E0 = SW[-1] + SEG; TOTAL = fr(E0 + 2.6)

_cut = {}
def cut(n, h):
    if (n, h) not in _cut:
        im = Image.open(R + f"assets/cutouts/{n}.png").convert("RGBA"); _cut[(n, h)] = im.resize((int(im.width * h / im.height), h), Image.LANCZOS)
    return _cut[(n, h)]
def stand(im, b, cx, y, a=1.0):
    sh = Image.new("RGBA", (W, H)); ImageDraw.Draw(sh).ellipse((cx - b.width * .55, y - 16, cx + b.width * .55, y + 16), fill=(0, 0, 0, 120)); im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(12)))
    im.alpha_composite(b, (int(cx - b.width / 2), int(y - b.height)))
def bubble(im, y, s, fill=(250, 248, 244), fg=(20, 20, 20), f=None, right=False):
    f = f or J.BOD(76); d = ImageDraw.Draw(im); b = d.textbbox((0, 0), s, font=f); w, h = b[2] - b[0], b[3] - b[1]
    x0 = (W - w) / 2 - 50; x1 = x0 + w + 100; d.rounded_rectangle((x0, y, x1, y + h + 70), radius=48, fill=fill + (255,))
    tx = x1 - 70 if right else x0 + 70; d.polygon([(tx - 22, y + h + 66), (tx + 22, y + h + 66), (tx + (30 if right else -30), y + h + 110)], fill=fill + (255,))
    d.text((x0 + 50 - b[0], y + 35 - b[1]), s, font=f, fill=fg)
def stamp(im, s, col, u, y=1150, ang=-14):
    if u < 0: return
    lay = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(lay); f = J.MS(170); b = d.textbbox((0, 0), s, font=f); w, h = b[2] - b[0], b[3] - b[1]
    x0, y0 = (W - w) / 2 - 40, y - h / 2 - 40; d.rounded_rectangle((x0, y0, x0 + w + 80, y0 + h + 80), radius=24, outline=col + (255,), width=14)
    d.text((x0 + 40 - b[0], y0 + 40 - b[1]), s, font=f, fill=col + (255,))
    sc = 1.6 - .6 * J.ss(u / .12); lay = lay.rotate(ang, center=(W / 2, y), resample=Image.BICUBIC)
    lay = lay.resize((int(W * sc), int(H * sc)), Image.LANCZOS).crop((int((W * sc - W) / 2), int(y * sc - y), int((W * sc - W) / 2) + W, int(y * sc - y) + H))
    lay.putalpha(lay.getchannel("A").point(lambda v: int(v * J.ss(u / .08)))); im.alpha_composite(lay)
def gray(im):
    g = im.convert("L").convert("RGBA"); return Image.blend(g, Image.new("RGBA", (W, H), (70, 70, 72, 255)), .35)
def haze(im, a):
    rng = np.random.default_rng(1); n = (rng.random((H // 8, W // 8)) * 255).astype(np.uint8)
    hz = Image.fromarray(n).resize((W, H), Image.BICUBIC).filter(ImageFilter.GaussianBlur(30)).point(lambda v: int(150 + v * .35))
    lay = Image.new("RGBA", (W, H), (150, 146, 138, 255)); lay.putalpha(hz.point(lambda v: int(v * a))); im.alpha_composite(lay)
def heart(d, cx, cy, s, col):
    d.ellipse((cx - s, cy - s * .6, cx, cy + s * .4), fill=col); d.ellipse((cx, cy - s * .6, cx + s, cy + s * .4), fill=col); d.polygon([(cx - s * .97, cy), (cx + s * .97, cy), (cx, cy + s * 1.15)], fill=col)
def cart(im, n_in, u):
    d = ImageDraw.Draw(im); y = 1500
    d.line((170, 1060, 250, 1060), fill=GOLD + (255,), width=14); d.polygon([(250, 1060), (900, 1060), (840, y), (300, y)], outline=GOLD + (255,), width=12)
    for k in range(1, 5): x = 250 + k * 130; d.line((x, 1060, x - 12 * k + 30, y), fill=GOLD + (120,), width=4)
    d.ellipse((330, y + 30, 400, y + 100), outline=GOLD + (255,), width=12); d.ellipse((750, y + 30, 820, y + 100), outline=GOLD + (255,), width=12)
    names = ["flora5_perf", "liita", "mraqua_perf"]
    for k in range(n_in):
        b = cut(names[k], 380); x = 420 + k * 170; yb = y - 20
        if k == n_in - 1: yb -= (1 - J.ss(u / .3)) * 1300
        im.alpha_composite(b, (int(x - b.width / 2), int(yb - b.height)))
_xm = None
def xmas_card():
    global _xm
    if _xm is None:
        src = Image.open(R + "posts/2026-11-27-jingle-shorts/xmas12/moksha.png").convert("RGB"); fg = src.resize((W, int(src.height * W / src.width)), Image.LANCZOS)
        bg = src.resize((int(src.width * H / src.height), H), Image.LANCZOS); bg = bg.crop(((bg.width - W) // 2, 0, (bg.width - W) // 2 + W, H)).filter(ImageFilter.GaussianBlur(40))
        bg = Image.blend(bg, Image.new("RGB", (W, H), (8, 6, 6)), .45); bg.paste(fg, (0, (H - fg.height) // 2 + 60)); _xm = bg.convert("RGBA")
    return _xm.copy()
SLOT = ["derossa", "moksha", "liita", "flora5_perf", "mraqua_perf"]
def slots(im, u, stop):
    d = ImageDraw.Draw(im); d.rounded_rectangle((70, 700, 1010, 1380), radius=40, fill=(10, 10, 10, 255), outline=GOLD + (255,), width=10)
    for c in range(3):
        x0 = 100 + c * 300; win = Image.new("RGBA", (280, 620), (245, 240, 232, 255))
        off = 1e9 if stop else (u * (2600 + 500 * c)) % (len(SLOT) * 300)
        for k in range(len(SLOT) + 2):
            name = "flora5_perf" if stop else SLOT[k % len(SLOT)]; b = cut(name, 240); y = 310 - b.height / 2 + (0 if stop else k * 300 - off + 300)
            if stop and k: break
            win.alpha_composite(b, (int(140 - b.width / 2), int(y)))
        if not stop: win = win.filter(ImageFilter.GaussianBlur(3))
        im.alpha_composite(win, (x0, 730))

def panel(i, u, t):
    if i in (2, 8, 9, 10):
        im = J.festive(t) if i not in (2,) else J.festive(t)
    else: im = J.festive(t)
    tx = lambda y, s, f, c=IVORY: J.text(im, y, s, f, c)
    if i == 0:
        tx(300, "A SHANAYA SMELLED", J.MS(74)); tx(390, "MY PERFUME", J.MS(74)); bubble(im, 560, "Imported hai?"); stand(im, cut("derossa", 760), 540, 1640)
    elif i == 1:
        tx(300, "ME:", J.MS(74)); bubble(im, 420, "Haan. Lajpat Nagar se.", GOLD, (12, 10, 8), right=True); stand(im, cut("derossa", 760), 540, 1640)
        tx(1730, "Mi Amor Paris, O-17, Lajpat Nagar-II", J.BOD(50), GOLD2)
    elif i == 2:
        im = Image.new("RGBA", (W, H), (88, 88, 90, 255)); stand(im, cut("moksha", 700), 540, 1560); im = gray(im); tx(330, "A NORMAL TUESDAY", J.MS(80), (230, 230, 230))
    elif i == 3:
        b = J.bottle("moksha", 700); stand(im, b, 540, 1560); J.popt(im, 330, "IT'S TIME.", u, J.MS(140), GOLD); im.alpha_composite(J.snow(t))
    elif i in (4, 5, 6):
        n = i - 3; tx(250, f"ADD TO CART ({n})", J.MS(88), GOLD)
        tx(360, ["it's for my cousin's wedding", "pocket size. doesn't count.", "the sangeet outfit needs its own scent"][n - 1], J.BOD(62), IVORY); cart(im, n, u)
    elif i == 7:
        d = ImageDraw.Draw(im); d.rounded_rectangle((80, 420, 1000, 1500), radius=40, fill=(12, 12, 12, 240), outline=GOLD + (255,), width=8)
        tx(540, "OFFICIAL TRADE", J.MS(96), GOLD); d.line((300, 640, 340, 690, 420, 600), fill=GREEN + (255,), width=16, joint="curve")
        tx(780, "Your 5-year-old deo", J.BOD(70)); tx(880, "to", J.BOD(56), GOLD2); stand(im, cut("moksha", 420), 540, 1360); tx(1440, "Fee: undisclosed.", J.BOD(58), GOLD2)
    elif i in (8, 9):
        stand(im, cut("mraqua_perf", 780), 540, 1640)
        if i == 8: haze(im, .95); tx(330, "DELHI AIR THIS WEEK:", J.MS(72), (40, 40, 40)); tx(440, "severe", J.BOD(90), (40, 40, 40))
        else: haze(im, .9 * (1 - J.ss(u / .25)) + .12); tx(330, "CAN'T FIX THE AIR.", J.MS(80)); tx(440, "can fix how you smell.", J.BOD(80), GOLD2)
    elif i in (10, 11, 12):
        tx(280, "SHAADI GIFTS:", J.MS(84), GOLD); item = ["Dry fruit box no. 7", "A six-glass set", "Bedsheet set, still in plastic,"][i - 10]
        tx(900, item, J.BOD(92))
        if i == 12: tx(1010, "someone else's name card on it", J.BOD(60), GOLD2)
        stamp(im, "NO", RED, u - .05, y=1260)
    elif i == 13:
        im = xmas_card(); tx(250, "SHAADI GIFTS:", J.MS(84), GOLD); stamp(im, "YES", GREEN, u - .05, y=1500, ang=10)
    elif i == 14:
        tx(300, "SINGLE THIS CHRISTMAS", J.MS(76)); stand(im, cut("mraqua_perf", 820), 540, 1640)
    elif i == 15:
        tx(300, "IT'S A MATCH", J.MS(110), GOLD); a = cut("mraqua_perf", 760); b = cut("missaqua_perf", 760)
        stand(im, a, 380 - 120 * (1 - J.ss(u / .25)), 1640); stand(im, b, 700 + 300 * (1 - J.ss(u / .25)), 1640)
        lay = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(lay)
        for k in range(7):
            v = J.cl(u / .7 - k * .06); heart(d, 540 + 260 * math.sin(k * 2.1), 760 - 420 * v + 40 * k, 34 + 6 * (k % 3), (226, 70, 90, int(255 * (1 - v))))
        im.alpha_composite(lay); tx(1730, "Mr Aqua + Miss Aqua", J.BOD(64), GOLD2)
    elif i == 16:
        tx(300, "YOUR CHRISTMAS SCENT IS...", J.MS(70)); slots(im, u, False)
    elif i == 17:
        tx(300, "YOUR CHRISTMAS SCENT IS...", J.MS(70)); slots(im, u, True); J.popt(im, 1560, "FLORA 5", u, J.MS(130), GOLD); im.alpha_composite(J.snow(t))
    elif i == 18:
        tx(780, "YOU SWIPED RIGHT", J.MS(90)); tx(900, "18 TIMES.", J.MS(130), GOLD); tx(1060, "your thumb deserves a gift", J.BOD(70), GOLD2)
    return im

def thumb_dot(im, x, y, a=1.0, trail=0):
    lay = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(lay)
    if trail: d.rounded_rectangle((x - trail, y - 26, x, y + 26), radius=26, fill=(255, 255, 255, int(70 * a)))
    d.ellipse((x - 58, y - 58, x + 58, y + 58), fill=(255, 255, 255, int(110 * a)), outline=(255, 255, 255, int(230 * a)), width=6)
    im.alpha_composite(lay.filter(ImageFilter.GaussianBlur(1.5)))

def intro(t):
    im = J.festive(t); im.alpha_composite(J.snow(t))
    J.popt(im, 400, "PUT YOUR THUMB", t - .1, J.MS(96)); J.popt(im, 510, "ON THE SCREEN", t - .3, J.MS(96))
    if t > 1.2: J.popt(im, 1500, "swipe right on every beat", t - 1.2, J.BOD(78), GOLD2, 0)
    if t > 2.3: J.popt(im, 1640, "ready?", t - 2.3, J.MS(70), GOLD)
    x = 200
    if 1.5 < t < 2.2: x = 200 + 680 * J.ss((t - 1.5) / .45)                # demo swipe
    thumb_dot(im, x, 1150, .9, trail=int(max(0, x - 200)))
    J.text(im, 1150, "→", J.MS(120), IVORY, a=.5 if x < 300 else 0)
    return im

def frame(t):
    if t < DROP: im = intro(t)
    elif t < E0:
        k = max(j for j, s in enumerate(SW) if s <= t); u = t - SW[k]; v = J.ss(u / .2)
        cur = panel(k, u, t)
        if v < 1 and k > 0:                                                # whole screen whips right
            prev = panel(k - 1, u + SEG, t); im = Image.new("RGBA", (W, H)); dx = int(W * v)
            im.alpha_composite(prev, (dx, 0)); im.alpha_composite(cur, (dx - W, 0)); im = im.filter(ImageFilter.GaussianBlur(4 * math.sin(math.pi * v)))
        elif v < 1:
            im = Image.new("RGBA", (W, H)); dx = int(W * v); im.alpha_composite(intro(t), (dx, 0)); im.alpha_composite(cur, (dx - W, 0))
        else: im = cur
        nxt = SW[k + 1] if k + 1 < len(SW) else E0; w = t - (nxt - .26)
        if 0 <= w < .26: x = 140 + 800 * J.ss(w / .26); thumb_dot(im, x, 1780, .8, trail=int(x - 140))   # the cue: swipe now
        J.flash(im, u, a=60, d=.1)
    else:
        im = J.festive(t); im.alpha_composite(J.snow(t)); J.endcard(im, t - E0, "Swipe right on Christmas")
    if t < .15: im.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(255 * (1 - t / .15)))))
    if t > TOTAL - .5: im.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(255 * J.ss((t - TOTAL + .5) / .5)))))
    return im.convert("RGB")

def ding():
    L = int(.6 * SR); x = np.arange(L) / SR; return sum(np.sin(2 * np.pi * f * x) * g for f, g in [(1568, .5), (2093, .35), (3136, .15)]) * np.exp(-x * 6)
def whoosh():
    L = int(.24 * SR); rng = np.random.default_rng(5); n = rng.standard_normal(L); y = np.zeros(L); a = 0.
    for i in range(L): c = .03 + .3 * math.sin(math.pi * i / L); a = c * n[i] + (1 - c) * a; y[i] = a
    return y * np.sin(np.pi * np.arange(L) / L)
def build_audio(path):
    n = int(round(TOTAL * SR)); s0 = int(SONG0 * SR); m = J.SNG[s0:s0 + n].copy()
    if len(m) < n: m = np.pad(m, ((0, n - len(m)), (0, 0)))
    rm = np.sqrt(np.mean(m[int(DROP * SR):] ** 2)); wh = whoosh(); wh /= np.max(np.abs(wh)); dg = ding(); dg /= np.max(np.abs(dg))
    for k, s in enumerate(SW):
        i = int((s - .1) * SR); m[i:i + len(wh)] += (wh * rm * 1.4)[:len(m[i:i + len(wh)])][:, None]
        if k in (1, 3, 13, 15, 17):
            i = int(s * SR); seg = m[i:i + len(dg)]; seg += (dg * rm * 1.2)[:len(seg)][:, None]
    fo = int(.6 * SR); m[-fo:] *= np.linspace(1, 0, fo)[:, None]; m *= 10 ** (-1 / 20) / np.max(np.abs(m))
    with wave.open(path, "wb") as w_: w_.setnchannels(2); w_.setsampwidth(2); w_.setframerate(SR); w_.writeframes((m * 32767).astype(np.int16).tobytes())

if __name__ == "__main__":
    only = os.environ.get("ONLY")
    if only:
        for s_ in only.split(","): frame(float(s_)).save(WORK + f"sw_{s_}.jpg", quality=85)
        print("swipes", [round(x, 2) for x in SW], "end", round(E0, 2), "TOTAL", TOTAL); sys.exit()
    fd = WORK + "fr_swipe/"; os.makedirs(fd, exist_ok=True)
    for i in range(int(round(TOTAL * FPS))): frame(i / FPS).save(fd + f"{i:04d}.jpg", quality=93)
    build_audio(fd + "a.wav")
    base = ["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", fd + "%04d.jpg"]
    enc = ["-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p", "-r", str(FPS), "-movflags", "+faststart"]
    subprocess.run(base + ["-i", fd + "a.wav", "-map", "0:v", "-map", "1:a"] + enc + ["-c:a", "aac", "-b:a", "256k", "-shortest", D + "swipe_right_reel.mp4"], check=True)
    subprocess.run(base + enc + ["-an", D + "swipe_right_reel_silent.mp4"], check=True)
    print("done", TOTAL)

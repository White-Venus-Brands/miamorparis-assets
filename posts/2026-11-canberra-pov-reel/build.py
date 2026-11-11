"""Reel: 'POV: you flew Delhi -> Canberra to visit the Finnish Embassy... on 10 November.'
Comedy riff on the 'closed for an internal planning day' meme. All graphics drawn in code; product stills
reused from Tannay's AI images (-> isAiGenerated true). 1080x1920, 30 fps, ~23 s. No embassy logos/flags.
Usage: python3 build.py WORKDIR   (ONLY=1,9 for stills)"""
import math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance

D = os.path.dirname(os.path.abspath(__file__)) + "/"
R = D + "../../"
OUT = sys.argv[1].rstrip("/") + "/" if len(sys.argv) > 1 else "/tmp/pov/"
LOGO = Image.open(R + "assets/cutouts/logo_gold.png").convert("RGBA")
W, H, FPS = 1080, 1920, 30
GOLD, IVORY, INK, NAVY = (226, 186, 112), (250, 245, 236), (30, 28, 34), (14, 22, 44)
LIITA = R + "posts/2026-11-wedding-storeroom-reel/src/02.png"   # Love Is In The Air bottle
SMOKE = R + "posts/2026-11-honey-trap-reel/src/05.png"          # Miss Poem cap with smoke
HERO = R + "posts/2026-11-honey-trap-reel/src/09.png"           # Miss Poem hero
BOX = R + "posts/2026-11-wedding-storeroom-reel/src/03.png"

def inter(s, w="Black"): return ImageFont.truetype(f"/usr/share/fonts/opentype/inter/InterDisplay-{w}.otf", s)
def pop(s, w="Medium"): return ImageFont.truetype(f"/usr/share/fonts/truetype/google-fonts/Poppins-{w}.ttf", s)
def lora(s, it=False): return ImageFont.truetype("/usr/share/fonts/truetype/google-fonts/Lora-" + ("Italic-Variable" if it else "Variable") + ".ttf", s)
def mono(s, b=True): return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono" + ("-Bold" if b else "") + ".ttf", s)
EMO = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf", 109)
def cl(x): return max(0.0, min(1.0, x))
def ss(x): x = cl(x); return x * x * (3 - 2 * x)
def back(x): x = cl(x); c = 1.9; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2
def win(t, a, b, fi=.25, fo=.2): return ss((t - a) / fi) * (1 - ss((t - (b - fo)) / fo))

# timeline
T_PACK, T_FLY, T_DOOR, T_SAD, T_TWIST, T_GUARD, END = 2.8, 6.0, 9.6, 12.2, 14.4, 17.2, 19.4
DUR = END + 3.8
CUTS = [T_PACK, T_FLY, T_DOOR, T_SAD, T_TWIST, T_GUARD, END]

_emo = {}
def emoji(ch, size):
    k = (ch, size)
    if k not in _emo:
        lay = Image.new("RGBA", (180, 180)); ImageDraw.Draw(lay).text((90, 90), ch, font=EMO, embedded_color=True, anchor="mm")
        lay = lay.crop(lay.getbbox()); s = size / max(lay.size); _emo[k] = lay.resize((int(lay.width * s), int(lay.height * s)), Image.LANCZOS)
    return _emo[k]

_img = {}
def photo(path, t, t0, t1, z0, z1, fx=.5, fy=.5):
    if path not in _img: _img[path] = Image.open(path).convert("RGB")
    im = _img[path]; u = ss((t - t0) / max(.01, t1 - t0)); z = z0 + (z1 - z0) * u
    s = max(W / im.width, H / im.height) * z; cw, ch = W / s, H / s
    x0 = min(max(fx * im.width - cw / 2, 0), im.width - cw); y0 = min(max(fy * im.height - ch / 2, 0), im.height - ch)
    return im.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch)).convert("RGBA")

def ctext(im, y, s, f, col, a, blur=10, scale=1.0, shadow=True, x=None):
    if a <= 0: return
    lay = Image.new("RGBA", (W + 400, 320)); ImageDraw.Draw(lay).text((lay.width / 2, 30), s, font=f, fill=col + (int(255 * a),), anchor="ma")
    bb = lay.getbbox()
    if not bb: return
    lay = lay.crop(bb)
    if scale != 1: lay = lay.resize((max(1, int(lay.width * scale)), max(1, int(lay.height * scale))), Image.LANCZOS)
    xx = (W - lay.width) // 2 if x is None else int(x - lay.width / 2)
    if shadow:
        sh = Image.new("RGBA", lay.size, (0, 0, 0, 0)); sh.putalpha(lay.getchannel("A").point(lambda v: int(v * .85)))
        pad = blur * 3; big = Image.new("RGBA", (lay.width + 2 * pad, lay.height + 2 * pad)); big.alpha_composite(sh, (pad, pad))
        im.alpha_composite(big.filter(ImageFilter.GaussianBlur(blur)), (xx - pad, int(y) - pad + 4))
    im.alpha_composite(lay, (xx, int(y)))

def paste_shadow(im, lay, x, y, blur=24, k=.55):
    sh = Image.new("RGBA", lay.size, (0, 0, 0, 0)); sh.putalpha(lay.getchannel("A").point(lambda v: int(v * k)))
    pad = blur * 3; big = Image.new("RGBA", (lay.width + 2 * pad, lay.height + 2 * pad)); big.alpha_composite(sh, (pad, pad))
    im.alpha_composite(big.filter(ImageFilter.GaussianBlur(blur)), (int(x) - pad + 8, int(y) - pad + 18)); im.alpha_composite(lay, (int(x), int(y)))

def grad_bg(top, bot):
    yy = np.linspace(0, 1, H)[:, None, None]
    return Image.fromarray((np.array(top) * (1 - yy) + np.array(bot) * yy * np.ones((1, W, 1))).astype(np.uint8)).convert("RGBA")
BG_SKY = grad_bg((120, 180, 235), (250, 214, 170))
BG_NAVY = grad_bg((10, 18, 40), (24, 40, 78))
BG_GREY = grad_bg((96, 102, 112), (54, 58, 66))

# ---------- props ----------
def boarding_pass(t):
    bw, bh = 940, 520; bp = Image.new("RGBA", (bw, bh)); d = ImageDraw.Draw(bp)
    d.rounded_rectangle((0, 0, bw - 1, bh - 1), 34, fill=(255, 255, 255, 255))
    d.rounded_rectangle((0, 0, bw - 1, 120), 34, fill=(24, 40, 78, 255)); d.rectangle((0, 80, bw - 1, 120), fill=(24, 40, 78, 255))
    d.text((40, 60), "BOARDING PASS", font=inter(40, "Black"), fill=(255, 255, 255, 255), anchor="lm")
    d.text((bw - 40, 60), "✈", font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 54), fill=GOLD + (255,), anchor="rm")
    d.text((60, 190), "DEL", font=inter(120, "Black"), fill=INK + (255,), anchor="lm"); d.text((bw - 60, 190), "CBR", font=inter(120, "Black"), fill=INK + (255,), anchor="rm")
    d.text((60, 262), "New Delhi", font=pop(30), fill=(120, 120, 130, 255), anchor="lm"); d.text((bw - 60, 262), "Canberra", font=pop(30), fill=(120, 120, 130, 255), anchor="rm")
    for x in range(330, 610, 24): d.ellipse((x, 186, x + 8, 194), fill=(180, 180, 190, 255))
    d.line((40, 320, bw - 40, 320), fill=(225, 225, 232, 255), width=3)
    for i, (k, v) in enumerate([("DATE", "10 NOV"), ("SEAT", "1A"), ("PURPOSE OF VISIT", "")]):
        x = 60 + i * 230
        d.text((x, 360), k, font=pop(24, "SemiBold") if os.path.exists("/usr/share/fonts/truetype/google-fonts/Poppins-SemiBold.ttf") else pop(24, "Bold"), fill=(140, 140, 150, 255))
        d.text((x, 395), v, font=inter(46, "Black"), fill=INK + (255,))
    pv = "Finnish Embassy 🥹"
    d.text((520, 395), "Finnish Embassy", font=inter(44, "Black"), fill=(200, 30, 40, 255))
    return bp

def checklist(t, u):
    cw, chh = 880, 900; card = Image.new("RGBA", (cw, chh)); d = ImageDraw.Draw(card)
    d.rounded_rectangle((0, 0, cw - 1, chh - 1), 30, fill=(255, 251, 240, 255))
    for y in range(170, chh, 92): d.line((40, y, cw - 40, y), fill=(200, 220, 240, 255), width=2)
    d.text((cw / 2, 90), "PACKING LIST", font=inter(60, "Black"), fill=INK + (255,), anchor="mm")
    items = [("Passport", .25), ("Sunscreen", .55), ("Itinerary: Embassy. Only.", .85), ("Perfume", 1.25)]
    y = 230
    for s, t0 in items:
        if u > t0:
            k = ss((u - t0) / .15)
            d.text((60, y), s, font=pop(42) if s != "Perfume" else inter(46, "Black"), fill=INK + (int(255 * k),), anchor="lm")
            box = (cw - 120, y - 30, cw - 60, y + 30); d.rounded_rectangle(box, 10, outline=(60, 160, 90, int(255 * k)), width=6)
            if u > t0 + .15: d.line((box[0] + 10, y, box[0] + 26, y + 18, box[2] - 8, y - 22), fill=(60, 160, 90, 255), width=8)
        y += 150
    if u > 1.55:  # extra checks on perfume
        for j in range(3):
            if u > 1.55 + j * .12:
                bx = cw - 200 - j * 70; d.line((bx, 680, bx + 16, 698, bx + 44, 658), fill=(60, 160, 90, 255), width=8)
    return card

def flight_map(t, u):
    im = BG_NAVY.copy(); d = ImageDraw.Draw(im)
    for x in range(0, W, 90): d.line((x, 0, x, H), fill=(40, 60, 100, 255), width=1)
    for y in range(0, H, 90): d.line((0, y, W, y), fill=(40, 60, 100, 255), width=1)
    A, B = (260, 620), (820, 1420)
    ctrl = (980, 760)
    def bez(p):
        return ((1 - p) ** 2 * A[0] + 2 * (1 - p) * p * ctrl[0] + p ** 2 * B[0], (1 - p) ** 2 * A[1] + 2 * (1 - p) * p * ctrl[1] + p ** 2 * B[1])
    prog = ss(u / 2.6)
    pts = [bez(i / 120) for i in range(121)]
    for i in range(0, 120, 3):
        if i / 120 <= prog: d.line((*pts[i], *pts[min(120, i + 1)]), fill=GOLD + (255,), width=8)
    for (x, y), lab in ((A, "DELHI"), (B, "CANBERRA")):
        d.ellipse((x - 22, y - 22, x + 22, y + 22), fill=(255, 90, 90, 255)); d.ellipse((x - 9, y - 9, x + 9, y + 9), fill=(255, 255, 255, 255))
        d.text((x, y + 60 if lab == "CANBERRA" else y - 60), lab, font=inter(52, "Black"), fill=(255, 255, 255, 255), anchor="mm")
    px, py = bez(prog); qx, qy = bez(min(1, prog + .01)); ang = math.degrees(math.atan2(-(qy - py), qx - px))
    pl = emoji("✈️", 120).rotate(ang - 45 + 0, expand=True, resample=Image.BICUBIC) if prog < 1 else None
    if pl: im.alpha_composite(pl, (int(px - pl.width / 2), int(py - pl.height / 2)))
    km = int(10364 * prog)
    ctext(im, 260, f"{km:,} km", mono(110), (255, 255, 255), 1, 8)
    ctext(im, 1640, "14 hours. 1 layover. 0 regrets.", inter(56, "Bold"), (220, 230, 250), win(t, T_FLY + .9, T_DOOR, .3), 8)
    return im

def door(t, u):
    im = BG_GREY.copy(); d = ImageDraw.Draw(im)
    d.rectangle((0, 1500, W, H), fill=(70, 66, 62, 255))  # pavement
    d.rectangle((190, 330, 890, 1500), fill=(48, 42, 40, 255)); d.rectangle((230, 370, 850, 1500), fill=(120, 84, 58, 255))
    for x0 in (260, 560):
        d.rectangle((x0, 420, x0 + 260, 860), outline=(96, 66, 44, 255), width=10); d.rectangle((x0, 920, x0 + 260, 1440), outline=(96, 66, 44, 255), width=10)
    d.ellipse((520, 900, 556, 936), fill=(214, 180, 110, 255))
    # taped notice swings in
    k = back(u / .4); sw = 12 * (1 - k)
    note = Image.new("RGBA", (560, 520)); dn = ImageDraw.Draw(note)
    dn.rectangle((0, 0, 559, 519), fill=(252, 252, 250, 255))
    for i, line in enumerate(["CLOSED", "for an internal", "planning day", "", "Tuesday, 10 November"]):
        f = inter(84, "Black") if i == 0 else lora(46)
        dn.text((280, 80 + i * 78 + (14 if i else 0)), line, font=f, fill=(200, 30, 40, 255) if i == 0 else (30, 30, 30, 255), anchor="mm")
    for tx in (40, 520):
        dn.rectangle((tx - 40, -10, tx + 40, 26), fill=(240, 230, 190, 200))
    note = note.rotate(-3 + sw, expand=True, resample=Image.BICUBIC)
    a = ss(u / .2); note.putalpha(note.getchannel("A").point(lambda v: int(v * a)))
    paste_shadow(im, note, 540 - note.width / 2, 560, 16, .5)
    return im

def guard_bubble(im, t, u):
    bw, bh = 860, 300; b = Image.new("RGBA", (bw, bh + 60)); db = ImageDraw.Draw(b)
    db.rounded_rectangle((0, 0, bw - 1, bh), 50, fill=(255, 255, 255, 245)); db.polygon([(140, bh - 4), (230, bh - 4), (120, bh + 58)], fill=(255, 255, 255, 245))
    db.text((50, 46), "SECURITY GUARD:", font=inter(38, "Black"), fill=(120, 120, 130, 255))
    db.text((50, 120), "“Ma’am, it’s closed...", font=lora(56, True), fill=INK + (255,))
    db.text((50, 196), "but what are you wearing?”", font=lora(56, True), fill=INK + (255,))
    s = .6 + .4 * back(u / .35); b = b.resize((int(b.width * s), int(b.height * s)), Image.LANCZOS)
    paste_shadow(im, b, W / 2 - b.width / 2, 300, 18, .45)

# ---------- frame ----------
rng = np.random.default_rng(3)
RAIN = [(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(26, 60), rng.uniform(1400, 2000)) for _ in range(140)]
def rain(im, t, a):
    lay = Image.new("RGBA", im.size); d = ImageDraw.Draw(lay)
    for x, y, L, sp in RAIN:
        yy = (y + t * sp) % H; d.line((x, yy, x - 6, yy + L), fill=(200, 210, 230, int(110 * a)), width=2)
    im.alpha_composite(lay)

def frame(t):
    if t < T_PACK:
        im = BG_SKY.copy()
        ctext(im, 300, "POV: you flew from", inter(80), INK, win(t, .1, T_PACK, .15), shadow=False)
        ctext(im, 395, "Delhi to Canberra", inter(80), INK, win(t, .3, T_PACK, .15), shadow=False)
        ctext(im, 490, "just to visit the", inter(80), INK, win(t, .5, T_PACK, .15), shadow=False)
        ctext(im, 585, "Finnish Embassy 🇫🇮" if False else "Finnish Embassy.", inter(80), (200, 30, 40), win(t, .7, T_PACK, .15), shadow=False)
        bp = boarding_pass(t); u = t - .9
        if u > 0:
            s = .7 + .3 * back(u / .35); bp = bp.rotate(-4, expand=True, resample=Image.BICUBIC); bp = bp.resize((int(bp.width * s), int(bp.height * s)), Image.LANCZOS)
            paste_shadow(im, bp, W / 2 - bp.width / 2, 820 + 40 * (1 - ss(u / .3)))
    elif t < T_FLY:
        u = t - T_PACK; im = BG_SKY.copy()
        card = checklist(t, u).rotate(2, expand=True, resample=Image.BICUBIC)
        paste_shadow(im, card, W / 2 - card.width / 2, 320)
        if u > 1.3:
            k = back((u - 1.3) / .35); bot = photo(LIITA, t, T_PACK, T_FLY, 1.0, 1.0).resize((300, 533), Image.LANCZOS)
            m = Image.new("L", bot.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, 299, 532), 28, fill=255); bot.putalpha(m)
            bot = bot.rotate(-8, expand=True, resample=Image.BICUBIC); s = .5 + .5 * k; bot = bot.resize((int(bot.width * s), int(bot.height * s)), Image.LANCZOS)
            paste_shadow(im, bot, 700 - bot.width / 2, 1270 - bot.height / 2 + 120)
            ctext(im, 1500, "(x3, obviously)", lora(52, True), INK, ss((u - 1.9) / .2), shadow=False, x=330)
    elif t < T_DOOR:
        im = flight_map(t, t - T_FLY)
    elif t < T_SAD:
        u = t - T_DOOR; im = door(t, u)
        ctext(im, 1250, "Arrived. 10 November.", inter(72), IVORY, win(t, T_DOOR + .9, T_SAD, .2))
    elif t < T_TWIST:
        u = t - T_SAD; im = door(t, 2.0)
        im = ImageEnhance.Color(ImageEnhance.Brightness(im.convert("RGB")).enhance(.55)).enhance(.3).convert("RGBA"); rain(im, t, 1)
        ctext(im, 1180, "Bad day to be a", inter(84), IVORY, win(t, T_SAD + .1, T_TWIST, .2))
        ctext(im, 1285, "Finnish embassy in", inter(84), IVORY, win(t, T_SAD + .1, T_TWIST, .2))
        ctext(im, 1390, "Canberra enthusiast.", inter(84), IVORY, win(t, T_SAD + .1, T_TWIST, .2))
        ctext(im, 1530, emoji and "😭", ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10), IVORY, 0)
        e = emoji("😭", 150); im.alpha_composite(e, (W // 2 - 75, 1540)) if u > .5 else None
    elif t < T_GUARD:
        u = t - T_TWIST; im = photo(SMOKE, t, T_TWIST, T_GUARD, 1.0, 1.1, .5, .4)
        ctext(im, 300, "But honestly?", inter(84), IVORY, win(t, T_TWIST + .1, T_GUARD, .2))
        ctext(im, 410, "I smelled incredible.", inter(92), GOLD, win(t, T_TWIST + .6, T_GUARD, .2), scale=1 + .25 * (1 - back((u - .6) / .3)))
    elif t < END:
        u = t - T_GUARD; im = photo(HERO, t, T_GUARD, END + 4, 1.08, 1.0)
        im = ImageEnhance.Brightness(im.convert("RGB")).enhance(.75).convert("RGBA")
        guard_bubble(im, t, u)
        ctext(im, 1560, "Trip: 10/10. Worth it.", inter(70), IVORY, win(t, T_GUARD + 1.1, END, .2))
    else:
        u = t - END
        bg = ImageEnhance.Brightness(photo(BOX, t, END, DUR, 1.0, 1.0).filter(ImageFilter.GaussianBlur(22))).enhance(.32)
        im = Image.blend(photo(HERO, t, T_GUARD, END + 4, 1.08, 1.0), bg, ss(u / .5))
        lg = LOGO.resize((220, int(LOGO.height * 220 / LOGO.width)), Image.LANCZOS); a = ss((u - .2) / .4)
        lg.putalpha(lg.getchannel("A").point(lambda v: int(v * a))); im.alpha_composite(lg, ((W - 220) // 2, 400))
        ctext(im, 650, "Plans get cancelled.", lora(64, True), IVORY, ss((u - .4) / .4))
        ctext(im, 740, "Smelling good doesn't.", lora(64, True), GOLD, ss((u - .8) / .4))
        a3 = ss((u - 1.2) / .4)
        if a3 > 0:
            f = inter(46, "Black"); lab = "DM FOR PRICES"; tw = ImageDraw.Draw(im).textlength(lab, font=f)
            lay = Image.new("RGBA", im.size); dl = ImageDraw.Draw(lay); y = 920
            dl.rounded_rectangle(((W - tw) / 2 - 50, y - 50, (W + tw) / 2 + 50, y + 50), 50, fill=GOLD + (255,))
            dl.text((W / 2, y), lab, font=f, fill=(40, 8, 16, 255), anchor="mm"); lay.putalpha(lay.getchannel("A").point(lambda v: int(v * a3))); im.alpha_composite(lay)
        ctext(im, 1020, "OR VISIT US AT LAJPAT NAGAR-II", pop(36, "Bold"), (226, 180, 110), ss((u - 1.4) / .4), 6)
    # whip-pan blur on cuts
    for tc in CUTS:
        v = t - tc
        if 0 <= v < .12:
            k = 1 - v / .12; im = im.filter(ImageFilter.BoxBlur(int(30 * k))) if k > .1 else im
    if t > DUR - .5: im = Image.blend(im, Image.new("RGBA", im.size, (0, 0, 0, 255)), ss((t - DUR + .5) / .5))
    return im.convert("RGB")

# ---------- audio ----------
SR = 44100
def audio(path):
    from scipy.signal import lfilter
    n = int(SR * DUR); out = np.zeros((n, 2), np.float32); r = np.random.default_rng(8)
    def add(sig, at, g=1.0, pan=0.0):
        i = int(at * SR); j = min(n, i + len(sig))
        if i >= n or j <= i: return
        s = sig[: j - i] * g; out[i:j, 0] += s * (1 - pan); out[i:j, 1] += s * (1 + pan)
    def env(L, a=.003, rel=.15): x = np.arange(int(L * SR)) / SR; return np.minimum(1, x / a) * np.exp(-x / rel)
    def tone(f, L, a=.01, rel=.3, h=(1, .4, .2), vib=0):
        x = np.arange(int(L * SR)) / SR; ph = 2 * np.pi * f * x + vib * np.sin(2 * np.pi * 5.5 * x)
        return sum(g * np.sin((i + 1) * ph) for i, g in enumerate(h)) * env(L, a, rel)
    kick = lambda: np.sin(2 * np.pi * (50 + 90 * np.exp(-np.arange(int(.3 * SR)) / SR / .04)) * np.arange(int(.3 * SR)) / SR) * env(.3, .002, .1)
    hat = lambda: lfilter([1, -1], [1, -.6], r.normal(0, 1, int(.05 * SR))) * env(.05, .001, .012)
    whoosh = lambda: lfilter([1], [1, -.9], r.normal(0, 1, int(.35 * SR))) * np.hanning(int(.35 * SR))
    # 1) upbeat travel tune (whistle melody) 0 -> T_DOOR
    beat = 60 / 128; mel = [784, 880, 988, 784, 1175, 988, 880, 784, 659, 784, 880, 659, 587, 659, 784, 880]
    t = .1; k = 0
    while t < T_DOOR - .1:
        add(kick(), t, .45) if k % 2 == 0 else add(hat(), t, .15)
        add(hat(), t + beat / 2, .1)
        f = mel[k % len(mel)]; add(tone(f, beat * .9, .01, .18, (1, .15), vib=.3), t, .07, .2)
        if k % 4 == 0: add(tone([196, 220, 175, 196][(k // 4) % 4], beat * 4, .02, .8, (1, .5, .3)), t, .07)
        t += beat; k += 1
    # pen checks
    for t0 in (.25, .55, .85, 1.25, 1.55, 1.67, 1.79): add(tone(1500, .12, .002, .04, (1,)), T_PACK + t0 + .15, .06)
    # plane flyover: rising noise + doppler tone during map
    add(lfilter([1], [1, -.97], r.normal(0, 1, int(2.8 * SR))) * np.hanning(int(2.8 * SR)) * .06, T_FLY + .2)
    # 2) door: needle scratch, then sad violin
    sc = np.sin(2 * np.pi * np.cumsum(np.linspace(1200, 150, int(.3 * SR))) / SR) * env(.3, .002, .1); add(sc, T_DOOR, .2)
    add(kick(), T_DOOR + .45, 1.2)
    for i, f in enumerate((392, 370, 349.2, 329.6, 311.1, 293.7)):
        add(tone(f, 1.0, .12, .7, (1, .5, .35, .25, .15), vib=.6), T_DOOR + 1.0 + i * .65, .06)
    # rain hiss under the sad bit
    rn = lfilter([1, -1], [1, -.2], r.normal(0, 1, int((T_TWIST - T_SAD) * SR))) * .015; add(rn, T_SAD)
    # 3) twist: sparkle + warm groove
    for i, f in enumerate((1046.5, 1318.5, 1568, 2093)): add(tone(f, 1.4, .003, .5, (1,)), T_TWIST + .55 + i * .06, .05)
    t = T_TWIST + .1; k = 0; beat2 = 60 / 116
    prog = [(261.6, 329.6, 392), (220, 261.6, 329.6), (174.6, 220, 261.6), (196, 246.9, 293.7)]
    while t < DUR - .6:
        add(kick(), t, .45);  add(hat(), t + beat2 / 2, .1)
        ch = prog[(k // 4) % 4]; add(tone(ch[k % 3] * 2, .45, .005, .22, (1, .3)), t, .05, .3 * math.sin(k))
        if k % 4 == 0: add(tone(ch[0] / 2, beat2 * 4, .02, 1.0, (1, .5)), t, .06)
        t += beat2; k += 1
    # guard bubble pop
    add(tone(880, .15, .002, .05, (1, .3)), T_GUARD + .05, .1)
    for tc in CUTS: add(whoosh(), tc - .12, .05)
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
                        "-movflags", "+faststart", "-shortest", D + "canberra_pov_reel.mp4"], check=True)
        frame(2.4).save(D + "cover.jpg", quality=92)
        print("ok", DUR)

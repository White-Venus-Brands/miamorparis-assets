"""Christmas sample reel (27 Nov): Tannay's existing takes, re-cut into a Christmas gift-list line, with the Christmas look
(red shirt + Santa hat, xmas_look.py) on every talking frame, light snowfall, Decibold sound #6 (softest),
its bass return landing on 'gift sets' and again on the end card. Words are his (Scribe), except 5213 whose word
timings are spread evenly inside its transcribed span.  Usage: python3 build_xmas.py WORKDIR"""
import os, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

WORK = sys.argv[1].rstrip("/") + "/"; sys.argv = [sys.argv[0], WORK]
HERE = os.path.dirname(os.path.abspath(__file__)) + "/"
BF = os.path.normpath(HERE + "../2026-11-23-bf-talking-reel") + "/"; sys.path.insert(0, BF)
import build_spec as S
from scipy.signal import butter, sosfilt
W, H, FPS, SR, fr, ss = S.W, S.H, S.FPS, S.SR, S.fr, S.ss
GOLD, GOLD2, IVORY = S.GOLD, S.GOLD2, S.IVORY

S.SRC["5213"] = S.A + "a14d9f64-IMG_5213.mov"
S.WORDS["5213"] = [("Your", .72, .86), ("entire", .92, 1.42), ("gift", 1.50, 1.86), ("list.", 1.94, 2.62)]
LN = {}
for k in ("5213", "5227", "5211", "5212"):
    ws = S.WORDS[k]; LN[k] = (max(0, ws[0][1] - .12), ws[-1][2] + .18, ws)
ws = S.WORDS["5226"][5:]; LN["5226"] = (ws[0][1] - .12, ws[-1][2] + .18, ws)
ws = S.WORDS["5222"][7:]; LN["5222"] = (ws[0][1] - .15, ws[-1][2] + .25, ws)
ORDER = ["5227", "5211", "5212", "5213", "5226", "5222"]   # open on him in the hat; 5213 is gift-box B-roll
TL = []; t = .5
for k in ORDER:
    a0, a1, _ = LN[k]; TL.append((k, a0, a1, t)); t += (a1 - a0) + .14
VO_END = fr(t); OUT0 = fr(VO_END + .1); TOTAL = fr(OUT0 + 3.2)
S.TL = TL
def at(k, wi):
    kk, a0, a1, st = [x for x in TL if x[0] == k][0]; ws = LN[k][2]
    return st + (ws[wi][1] - a0)
T_GIFT = fr(at("5212", 3))
DROPS = [T_GIFT]; S.DROPS = DROPS

EDL = {"5213": [(0, "face", None, 1.0), (3, "still", "trio", 1)],
       "5227": [(0, "face", None, 1.08), (2, "spray", "moksha_v", 1), (3, "spray", "poem_v", 1)],
       "5211": [(0, "face", None, 1.0), (2, "still", "wash1", 1)],
       "5212": [(0, "face", None, 1.0), (3, "still", "trio", 1), (4, "still", "inbox", 1)],
       "5226": [(0, "still", "window", 1), (5, "face", None, 1.1), (10, "spray", "ombre_v", 1)],
       "5222": [(0, "face", None, 1.15)]}
SH = []
for i_, (k, a0, a1, st) in enumerate(TL):
    ed = EDL[k]
    for i, (wi, kind, arg, zoom) in enumerate(ed):
        t0 = st if i == 0 else at(k, wi)
        t1 = at(k, ed[i + 1][0]) if i + 1 < len(ed) else (TL[i_ + 1][3] if i_ + 1 < len(TL) else OUT0)
        SH.append([fr(t0), fr(t1), kind, arg, zoom, k])
SH[0][0] = 0.0
for i in range(1, len(SH)): SH[i - 1][1] = SH[i][0]
SHOTS = [tuple(s) for s in SH]
# what Tannay films for each slot (placeholder version); keyed by (clip, shot number inside that line)
SLOT = {("5227", 0): ("YOU, TO CAMERA", "Christmas outfit + Santa hat", "\"Get your signature scents.\""),
        ("5227", 1): ("B-ROLL", "Moksha spray, slow-mo, lamp behind", "Step 3"),
        ("5227", 2): ("B-ROLL", "Second bottle spray, slow-mo", "Step 3"),
        ("5211", 0): ("YOU, TO CAMERA", "Holding the body wash", "\"Your body washes\""),
        ("5211", 1): ("B-ROLL", "Body wash, label to camera", "Step 2"),
        ("5212", 0): ("B-ROLL", "Gift set, lid opening, top-down", "Step 4"),
        ("5212", 1): ("B-ROLL", "Gift sets in front of fairy lights", "Step 5"),
        ("5212", 2): ("B-ROLL", "Gift box with ribbon", "Step 4"),
        ("5213", 0): ("B-ROLL", "Hands tying a ribbon on a gift box", "Step 4"),
        ("5213", 1): ("B-ROLL", "All gift sets next to the tree", "Step 5"),
        ("5226", 0): ("B-ROLL", "Store entrance, Lajpat Nagar", "walk in, handheld"),
        ("5226", 1): ("YOU, TO CAMERA", "In the store", "\"...R Cube Monad Mall, Noida...\""),
        ("5226", 2): ("B-ROLL", "Order being packed, top-down", "Step 4"),
        ("5222", 0): ("YOU, TO CAMERA", "Smile + wave", "\"Happy shopping.\"")}
SLOTS = []; _c = {}
for s_ in SHOTS:
    n_ = _c.get(s_[5], 0); _c[s_[5]] = n_ + 1; SLOTS.append(SLOT.get((s_[5], n_)))
PH = os.environ.get("PLACEHOLDER") == "1"
def placeholder(i, lu, dur):
    kind_, what, line = SLOTS[i]
    im = Image.new("RGBA", (W, H), (22, 20, 20, 255)); d = ImageDraw.Draw(im)
    for x in range(60, W - 60, 36): d.line((x, 60, x + 18, 60), fill=GOLD, width=4); d.line((x, H - 60, x + 18, H - 60), fill=GOLD, width=4)
    for y in range(60, H - 60, 36): d.line((60, y, 60, y + 18), fill=GOLD, width=4); d.line((W - 60, y, W - 60, y + 18), fill=GOLD, width=4)
    text_c(im, 900, f"SHOT {i + 1}", S.MS(40, "Bold"), GOLD)
    text_c(im, 990, kind_, S.MS(76, "Black"), IVORY)
    text_c(im, 1095, what, S.MS(46, "SemiBold"), (225, 215, 200))
    text_c(im, 1170, line, S.MS(40, "Medium"), GOLD2)
    text_c(im, 1250, f"{dur:.1f} s", S.MS(36, "Medium"), (170, 160, 150))
    return im
POPS = [("5227", 0, "CHRISTMAS SHOPPING", .9), ("5213", 2, "GIFT LIST: SORTED", 1.1), ("5212", 3, "GIFT SETS", .9), ("5226", 13, "miamorparis.in", 1.0), ("5222", 0, "HAPPY SHOPPING", 1.0)]
S.POPT = [(at(k, wi), at(k, wi) + hold, txt) for k, wi, txt, hold in POPS]
S.POPT.sort(); S.POPT = [(a_, min(b_, S.POPT[j + 1][0]) if j + 1 < len(S.POPT) else b_, t_) for j, (a_, b_, t_) in enumerate(S.POPT)]   # a new pop ends the last one
S.CAPS = []
for k, a0, a1, st in TL:
    ws = [(w_, st + (s_ - a0), st + (e_ - a0)) for w_, s_, e_ in LN[k][2] if w_]
    for i in range(0, len(ws), 3):
        ch = ws[i:i + 3]; nxt = ws[i + 3][1] if i + 3 < len(ws) else ch[-1][2] + .25
        S.CAPS.append((ch[0][1] - .05, min(nxt, ch[-1][2] + .35), ch))

# ---------- snow ----------
RNG = np.random.default_rng(7); NF = 110
FL = [dict(x=RNG.uniform(0, W), y=RNG.uniform(-H, H), v=RNG.uniform(60, 160), r=RNG.uniform(3, 9), sw=RNG.uniform(10, 40), ph=RNG.uniform(0, 6.28), a=RNG.uniform(110, 210)) for _ in range(NF)]
def snow(t):
    lay = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(lay)
    for f in FL:
        y = (f["y"] + f["v"] * t) % (H + 40) - 20; x = f["x"] + f["sw"] * np.sin(t * 1.3 + f["ph"])
        d.ellipse((x - f["r"], y - f["r"], x + f["r"], y + f["r"]), fill=(255, 255, 255, int(f["a"])))
    return lay.filter(ImageFilter.GaussianBlur(1.6))

def text_c(im, y, s, f, fill, a=1.0):
    lay = Image.new("RGBA", (W, 400)); d = ImageDraw.Draw(lay); d.text((W // 2, 200), s, font=f, fill=fill, anchor="mm"); lay = lay.crop(lay.getbbox())
    if lay.width > 940: lay = lay.resize((940, int(lay.height * 940 / lay.width)), Image.LANCZOS)
    lay.putalpha(lay.getchannel("A").point(lambda v: int(v * a))); im.alpha_composite(lay, ((W - lay.width) // 2, y - lay.height // 2))

def endcard(u):
    im = Image.new("RGBA", (W, H), (8, 6, 6, 255))
    glow = Image.new("RGBA", (W, H)); ImageDraw.Draw(glow).ellipse((120, 520, W - 120, 1260), fill=GOLD + (55,)); im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(120)))
    lg = Image.open(S.R + "assets/cutouts/logo_gold.png").convert("RGBA"); lg = lg.resize((240, int(240 * lg.height / lg.width)), Image.LANCZOS)
    a = ss(u / .35); lg.putalpha(lg.getchannel("A").point(lambda v: int(v * a))); im.alpha_composite(lg, ((W - lg.width) // 2, 640 - lg.height // 2))
    for y, s_, f, col, d0 in [(840, "Merry Christmas", S.BOD(96), GOLD2, .2), (950, "from Mi Amor Paris", S.MS(42, "SemiBold"), IVORY, .45),
                              (1030, "Lajpat Nagar · R Cube Monad Mall · miamorparis.in", S.MS(30, "Medium"), (215, 205, 190), .6),
                              (1110, "comment SCENT for the quiz", S.MS(38, "Medium"), (215, 205, 190), .8)]:
        text_c(im, y, s_, f, col, ss((u - d0) / .3))
    d = ImageDraw.Draw(im); lw = int(300 * ss((u - .3) / .4)); d.rectangle(((W - lw) // 2, 905, (W + lw) // 2, 907), fill=GOLD + (255,))
    im.alpha_composite(snow(OUT0 + u))
    return im

def frame(t):
    if t >= OUT0: return endcard(t - OUT0)
    i = max(j for j, s in enumerate(SHOTS) if s[0] <= t + 1e-6); t0, t1, kind, arg, zoom, k = SHOTS[i]; lu = t - t0
    if PH and SLOTS[i]:
        im = placeholder(i, lu, t1 - t0)
    else:
        if kind == "face":
            kk, a0, a1, st = [x for x in TL if x[0] == k][0]; im = S.face(k, a0 + (t - st), zoom)
        else: im = S.shot(kind, arg, lu, t1 - t0)
        for d in DROPS:
            if 0 <= t - d < .4: im = S.punch(im, t - d)
        im = S.grade(im).convert("RGBA")
    if lu < .06 and i > 0: im.alpha_composite(Image.new("RGBA", (W, H), (255, 245, 225, int(45 * (1 - lu / .06)))))
    for d in DROPS:
        if 0 <= t - d < .14: im.alpha_composite(Image.new("RGBA", (W, H), (245, 214, 150, int(120 * (1 - (t - d) / .14)))))
    im.alpha_composite(snow(t))
    popping = False
    for p0, p1, txt in S.POPT:
        if p0 <= t < p1: S.pop(im, txt, t - p0); popping = True
    if not popping: S.captions(im, t)
    if t < .3: im.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(255 * (1 - t / .3)))))
    return im

def music(n):
    with wave.open(S.R + "assets/music/decibold_trk6.wav") as w_:
        x = np.frombuffer(w_.readframes(w_.getnframes()), np.int16).reshape(-1, 2).astype(np.float32) / 32768
    out = np.zeros((n, 2), np.float32)
    def place(a, b, t0, xf=.3, g=1.0):
        seg = x[int(max(0, a) * SR):int(b * SR)].copy(); i = int(round(t0 * SR))
        if i < 0: seg = seg[-i:]; i = 0
        m = min(len(seg), n - i)
        if m <= 0: return
        seg = seg[:m]; r = np.ones(m, np.float32); k = min(int(xf * SR), m // 2)
        r[:k] = np.linspace(0, 1, k); r[-k:] = np.minimum(r[-k:], np.linspace(1, 0, k)); out[i:i + m] += g * seg * r[:, None]
    off = T_GIFT - 25.72                           # bass return on 'gift sets'
    place(-off, 29.3, 0); e = 29.3 + off; pre = OUT0 - (25.72 - 24.3)
    t0 = e - .6
    while t0 < pre:
        place(8.0, 8.0 + min(15.36, pre + .4 - t0) + .3, t0, xf=.6); t0 += 15.36
    place(24.3, 30.53, pre, .4)                    # and again on the end card
    fo = int(.8 * SR); out[-fo:] *= np.linspace(1, 0, fo)[:, None]
    return out - .35 * sosfilt(butter(2, 90, "low", fs=SR, output="sos"), out, axis=0)

def build_audio(path):
    n = int(round(TOTAL * SR)); vo = np.zeros(n, np.float32); speak = np.zeros(n, np.float32)
    for k, a0, a1, st in TL:
        xx = S.clean_voice(k, a0, a1); i0 = int(round(st * SR)); m = min(n - i0, len(xx)); vo[i0:i0 + m] += xx[:m]; speak[i0:i0 + m] = 1
    sp = speak > 0; vo *= (10 ** (-18 / 20)) / np.sqrt(np.mean(vo[sp] ** 2))
    mu = music(n); mu *= (10 ** (-26 / 20)) / np.sqrt(np.mean(mu ** 2))
    k_ = np.ones(int(.12 * SR)) / int(.12 * SR); hold = np.clip(np.convolve(speak, k_, "same"), 0, 1)
    under = 20 * np.log10(np.sqrt(np.mean(mu[sp] ** 2))); floor = float(np.clip(10 ** ((-18 - 14.5 - under) / 20), .2, .6))
    mm = mu * (1 - (1 - floor) * hold)[:, None]; mix = vo[:, None] + mm; g = 10 ** (-1 / 20) / np.max(np.abs(mix)); mix *= g
    with wave.open(path, "wb") as w_:
        w_.setnchannels(2); w_.setsampwidth(2); w_.setframerate(SR); w_.writeframes((mix * 32767).astype(np.int16).tobytes())
    v = 20 * np.log10(np.sqrt(np.mean((vo * g)[sp] ** 2))); m_ = 20 * np.log10(np.sqrt(np.mean((mm * g)[sp] ** 2)))
    q = np.sqrt(np.convolve(mm.mean(1) ** 2, np.ones(SR // 4) / (SR // 4), "same")); quiet = 20 * np.log10(q[SR // 2:-SR].min() + 1e-9)
    print(f"voice {v:.1f} | music under voice {m_:.1f} (gap {v - m_:.1f}) | duck {floor:.2f} | quietest music {quiet:.1f}")

if __name__ == "__main__":
    print("TOTAL", TOTAL, "TL", [(k, round(st, 2)) for k, _, _, st in TL], "GIFT", T_GIFT)
    only = os.environ.get("ONLY")
    if only:
        for s_ in only.split(","): frame(float(s_)).convert("RGB").save(WORK + f"xm{'p' if PH else ''}_{s_}.jpg", quality=85)
        sys.exit()
    fd = WORK + ("fr_xmas_ph/" if PH else "fr_xmas/"); os.makedirs(fd, exist_ok=True)
    for i in range(int(round(TOTAL * FPS))): frame(i / FPS).convert("RGB").save(fd + f"{i:04d}.jpg", quality=93)
    build_audio(WORK + "mix_xmas.wav")
    out = HERE + ("christmas_reel_TEMPLATE_empty.mp4" if PH else "christmas_reel_sample_filled.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", fd + "%04d.jpg", "-i", WORK + "mix_xmas.wav", "-map", "0:v", "-map", "1:a",
                    "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p", "-r", str(FPS), "-c:a", "aac", "-b:a", "256k",
                    "-shortest", "-movflags", "+faststart", out], check=True)
    print("done", out)

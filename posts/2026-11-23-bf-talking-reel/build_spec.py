"""Black Friday talking Reel, rebuilt to Tannay's EDITING_SPEC (ops/EDITING_SPEC.md), 25 Nov.
Exact words from ElevenLabs Scribe (ops/transcribe/bf_takes_2026-11-23*), so every clip sits in script order and every caption
is his word. Spec: 25 fps / CRF 18 / AAC 256k; voice clean (RNNoise -> FFT denoise -> hum notch -> warmth EQ -> de-ess ->
gentle comp, fixed gain, no loudnorm); words never cut; music under the whole reel, ducked to 0.35 held over each line,
-8 dB vs voice RMS, 90 Hz low end tamed, peak -1 dBFS, numpy sample-exact mix; karaoke captions (3 words, active word gold);
keyword pop-ups autofit <= 940 px; pictures change on the word; punch-zoom 1.2->1.0 + soft gold flash on drops; splits/grids
with thin gold borders; warm soft grade + vignette; teeth whitened.  Usage: python3 build_spec.py WORKDIR"""
import math, os, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

D = os.path.dirname(os.path.abspath(__file__)) + "/"
R = os.path.normpath(D + "../..") + "/"
WORK = (sys.argv[1].rstrip("/") + "/") if len(sys.argv) > 1 else "/tmp/bfs/"
os.makedirs(WORK, exist_ok=True)
sys.argv = [sys.argv[0], WORK + "bfr"]; sys.path.insert(0, R + "posts/2026-11-21-black-friday-reel"); sys.path.append(D)
import build as B                     # spray clips + mist fx, wash/photo helpers
from teeth import Whitener

W, H, FPS, SR = 1080, 1920, 25, 48000
GOLD, GOLD2, IVORY, INK = (226, 186, 112), (240, 208, 150), (250, 245, 236), (10, 8, 8)
A = "/mnt/user-data/attachments/e1dc2e45-c278-5714-b377-734372e7d29a/"
SRC = {"5211": A + "5f1d5c70-IMG_5211.mov", "5212": A + "450a0d04-IMG_5212.mov", "5215": "/mnt/user-data/uploads/IMG_5215.mov",
       "5216": A + "e252d6fe-IMG_5216.mov", "5222": A + "f232ce78-IMG_5222.mov", "5226": A + "8b5e12e2-IMG_5226.mov",
       "5227": A + "6f7ae372-IMG_5227.mov", "5228": A + "b72277c6-IMG_5228.mov"}
OFFS = {"5211": 0.0, "5212": 3.675, "5215": 15.419, "5216": 25.408, "5222": 32.923, "5226": 38.923, "5227": 48.4, "5228": 53.355}
# Scribe words (global time in the joined file) -> clip-local
WORDS_G = [("Your", .54, .66), ("body", .74, .98), ("washes", 1.04, 1.64), ("and", 4.24, 4.34), ("your", 4.4, 4.56), ("entire", 4.64, 5.32),
    ("gift", 5.4, 5.58), ("sets.", 5.64, 6.14), ("Buy", 17.12, 17.28), ("one,", 17.36, 17.54), ("get", 17.8, 17.96), ("one", 18.02, 18.14),
    ("free,", 18.22, 18.42), ("or", 18.92, 19.1), ("simply", 19.38, 19.66), ("just", 19.72, 19.84), ("take", 19.9, 20.06), ("50%", 20.1, 20.7),
    ("off", 20.74, 20.88), ("on", 20.94, 21.1), ("the", 21.16, 21.22), ("product", 21.26, 21.6), ("you", 21.64, 21.72), ("like.", 21.78, 22.08),
    ("Your", 22.8, 22.92), ("pick.", 23.02, 23.28), ("Plus,", 26.02, 26.42), ("there's", 26.64, 26.78), ("a", 26.84, 26.88), ("clearance", 26.94, 27.32),
    ("sale", 27.4, 27.74), ("on", 27.96, 28.2), ("all", 28.32, 28.54), ("the", 28.58, 28.68), ("candles,", 28.74, 29.32), ("even", 29.98, 30.16),
    ("the", 30.18, 30.28), ("oud", 30.32, 30.5), ("ones.", 30.6, 30.96), ("It's", 33.04, 33.22), ("Black", 33.26, 33.48), ("Friday,", 33.52, 33.78),
    ("guys.", 33.86, 34.28), ("Don't", 34.46, 34.64), ("miss", 34.66, 34.84), ("out.", 34.92, 35.18), ("Happy", 35.5, 35.74), ("shopping.", 35.78, 36.22),
    ("It's", 39.14, 39.3), ("on", 39.4, 39.58), ("till", 39.62, 39.74), ("the", 39.78, 39.86), ("27th", 39.92, 40.7), ("in", 41.22, 41.34),
    ("store", 41.42, 41.72), ("at", 41.76, 41.9), ("Lajpat", 41.96, 42.34), ("Nagar", 42.38, 42.78), ("or", 43.0, 43.22), ("R Cube", 43.36, 43.58),
    ("Monad", 43.62, 43.9), ("Mall,", 43.96, 44.12), ("Noida", 44.18, 44.54), ("or", 45.14, 45.26), ("visit", 45.52, 45.74),
    ("us", 45.78, 45.9), ("online.", 45.96, 46.4), ("Get", 49.08, 49.24), ("your", 49.3, 49.4), ("signature", 49.46, 49.9), ("scents.", 49.98, 50.42),
    ("Black", 54.04, 54.36), ("Friday", 54.42, 54.72), ("at", 54.76, 54.88), ("Mi", 54.92, 55.08), ("Amor", 55.1, 55.22), ("Paris", 55.28, 55.58),
    ("is", 55.64, 55.76), ("live.", 55.84, 56.38)]
def clip_of(t):
    best = None
    for k, o in OFFS.items():
        if o <= t and (best is None or o > OFFS[best]): best = k
    return best
WORDS = {}
for w_, s_, e_ in WORDS_G:
    k = clip_of(s_); WORDS.setdefault(k, []).append((w_, round(s_ - OFFS[k], 3), round(e_ - OFFS[k], 3)))

# script order (line, clip). Each line keeps ALL its words: in = first word - 0.12, out = last word + 0.18
ORDER = ["5228", "5227", "5211", "5212", "5215", "5216", "5226", "5222"]
LINES = []
for k in ORDER:
    ws = WORDS[k]; LINES.append((k, max(0, ws[0][1] - .12), ws[-1][2] + .18, ws))
GAP = 0.12
# MUSIC: Tannay's Decibold sound #7 (screen-rec 1795162146). Analysed (STFT flux + bass env): calm melodic bed 1.90-5.8,
# pause 5.8-6.45, DROP 6.45, pause 10.37-10.8, drop 10.8, breakdown 12.3-14.3, DROP 14.3, pause 18.0-18.38, final drop 18.38,
# outro tail 20.4-22.5. ~94 bpm half-time feel, 0.16 s hit grid.
TRK = R + "assets/music/decibold_trk7.wav"
M_D1, M_P1, M_D2, M_D3, M_P4, M_D4, M_END = 6.45, 10.37, 10.8, 14.3, 18.0, 18.38, 22.5
OUT_ONS = [18.38, 18.62, 18.79, 19.03, 19.27, 19.43, 19.66, 19.90, 20.15]   # 8 beat cuts, then logo card
OUTRO = M_END - M_D4
def fr(x): return round(x * FPS) / FPS
t = 0.6               # music-only breath before the first word
TL = []               # (clip, a0, a1, start)
for k, a0, a1, ws in LINES:
    if k == "5216":   # land "Plus" on the second big drop
        T1_ = fr(TL[-1][3] + (WORDS["5215"][4][2] - TL[-1][1])); T2_ = fr(TL[-1][3] + (WORDS["5215"][9][1] - TL[-1][1]))
        T3_ = fr(T2_ + (M_D3 - M_D2)); t = max(t, T3_ - (ws[0][1] - a0) + .02)
    TL.append((k, a0, a1, t)); t += (a1 - a0) + GAP
VO_END = fr(t); TOTAL = fr(VO_END + OUTRO)
def gword(k, i): return [x for x in TL if x[0] == k][0]
def wt(k, idx, end=False):
    """timeline time of word idx in clip k (start, or end)"""
    kk, a0, a1, st = [x for x in TL if x[0] == k][0]; w_ = WORDS[k][idx]; return st + ((w_[2] if end else w_[1]) - a0)
def at(k, wi): return wt(k, wi[1], True) if isinstance(wi, tuple) else wt(k, wi)
T1, T2 = fr(wt("5215", 4, True)), fr(wt("5215", 9)); T3 = fr(T2 + (M_D3 - M_D2))

# ---------------- fonts ----------------
def MS(s, st="Black"):
    f = ImageFont.truetype("/usr/share/fonts/truetype/google-fonts/ofl/montserrat/Montserrat[wght].ttf", s); f.set_variation_by_name(st); return f
def BOD(s):
    f = ImageFont.truetype(R + "assets/fonts/BodoniModa-Italic[opsz,wght].ttf", s); f.set_variation_by_name("SemiBold Italic"); return f
def COR(s):
    f = ImageFont.truetype(R + "assets/fonts/CormorantGaramond[wght].ttf", s); f.set_variation_by_name("SemiBold"); return f
def cl(x): return max(0.0, min(1.0, x))
def ss(x): x = cl(x); return x * x * (3 - 2 * x)
def back(x): x = cl(x); c = 1.7; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2

# ---------------- footage ----------------
CACHE = {}
def face_frames(k):
    if k in CACHE: return CACHE[k]
    fd = WORK + f"f25_{k}/"
    if not os.path.isdir(fd) or not os.listdir(fd):
        os.makedirs(fd, exist_ok=True)
        vf = f"fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}" if k != "5212" else f"fps={FPS},scale={W}:-2"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", SRC[k], "-vf", vf, "-q:v", "2", fd + "%04d.jpg"], check=True)
        if k != "5212":
            import cv2
            wtn = Whitener()
            for f in sorted(os.listdir(fd)): cv2.imwrite(fd + f, wtn(cv2.imread(fd + f)), [cv2.IMWRITE_JPEG_QUALITY, 95])
    CACHE[k] = sorted(os.listdir(fd)); return CACHE[k]
def face(k, src_t, zoom=1.0, cy=760):
    fs = face_frames(k); fd = WORK + f"f25_{k}/"
    im = Image.open(fd + fs[max(0, min(int(round(src_t * FPS)), len(fs) - 1))]).convert("RGB")
    if k == "5212":
        bg = im.resize((int(im.width * H / im.height), H), Image.LANCZOS); bg = bg.crop(((bg.width - W) // 2, 0, (bg.width - W) // 2 + W, H)).filter(ImageFilter.GaussianBlur(40))
        q = im.resize((int(im.width * 1.25), int(im.height * 1.25)), Image.LANCZOS); bg.paste(q, ((W - q.width) // 2, (H - q.height) // 2)); im = bg
    if zoom != 1.0:
        w, h = W / zoom, H / zoom; x0 = (W - w) / 2; y0 = min(max(cy - h / 2, 0), H - h)
        im = im.resize((W, H), Image.LANCZOS, box=(x0, y0, x0 + w, y0 + h))
    return im
def kb(im, p, z0=1.0, z1=1.08):
    """Ken Burns push-in, cover 9:16"""
    z = z0 + (z1 - z0) * p; s = max(W / im.width, H / im.height) * z
    q = im.resize((int(im.width * s) + 1, int(im.height * s) + 1), Image.LANCZOS)
    return q.crop(((q.width - W) // 2, (q.height - H) // 2, (q.width - W) // 2 + W, (q.height - H) // 2 + H))
def fitw(im, p):
    """still fit to width over its own blur, slow push"""
    s = W / im.width * (1 + .07 * p); q = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    bg = im.resize((int(im.width * H / im.height), H), Image.LANCZOS); bg = bg.crop(((bg.width - W) // 2, 0, (bg.width - W) // 2 + W, H)).filter(ImageFilter.GaussianBlur(45))
    bg = Image.blend(bg, Image.new("RGB", (W, H), INK), .35); bg.paste(q, ((W - q.width) // 2, (H - q.height) // 2)); return bg
def L(p): return Image.open(R + p).convert("RGB")
ST = {"trio": L("posts/2026-11-marhaba-yellow/src/trio.png"), "inbox": L("posts/2026-11-marhaba-yellow/src/inbox.png"),
      "window": L("posts/2026-11-marhaba-yellow/src/window.png"), "jersey": L("posts/2026-11-marhaba-yellow/src/jersey.png"),
      "zeenat": L("posts/2026-11-02-oudh-candles/zeenat_4.jpg"), "abyad": L("posts/2026-11-02-oudh-candles/abyad_1.jpg"),
      "aleud": L("posts/2026-11-02-oudh-candles/aleud_1.jpg"), "sandali": L("posts/2026-11-02-oudh-candles/sandali_1.jpg")}
for z in ("aries", "taurus", "gemini", "cancer"): ST[z] = L(f"posts/2026-11-21-black-friday-reel/src/zodiac_{z}.jpg")
for i, p in enumerate(B.WASH): ST[f"wash{i}"] = Image.open(p).convert("RGB")
def spray(key, lu): return B.spray(key, .3 + lu, 1).convert("RGB")
def tile(kind, arg, lu, dur, w, h):
    im = shot(kind, arg, lu, dur)
    s = max(w / W, h / H); q = im.resize((int(W * s) + 1, int(H * s) + 1), Image.LANCZOS)
    return q.crop(((q.width - w) // 2, (q.height - h) // 2, (q.width - w) // 2 + w, (q.height - h) // 2 + h))
def split(a, b, lu, dur):
    can = Image.new("RGB", (W, H), GOLD); hh = (H - 18) // 2
    can.paste(tile(*a, lu, dur, W - 12, hh - 6), (6, 6)); can.paste(tile(*b, lu, dur, W - 12, hh - 6), (6, hh + 12)); return can
def grid(items, lu, dur):
    can = Image.new("RGB", (W, H), GOLD); cw, ch = (W - 18) // 2, (H - 18) // 2
    for i, it in enumerate(items):
        can.paste(tile(*it, lu, dur, cw, ch), (6 + (i % 2) * (cw + 6), 6 + (i // 2) * (ch + 6)))
    return can
def shot(kind, arg, lu, dur):
    p = cl(lu / max(dur, .01))
    if kind == "spray": return spray(arg, lu)
    if kind == "still": return kb(ST[arg], p) if arg in ("trio", "inbox", "window", "jersey") else fitw(ST[arg], p)
    if kind == "split": return split(arg[0], arg[1], lu, dur)
    if kind == "grid": return grid(arg, lu, dur)
    if kind == "black": return Image.new("RGB", (W, H), (0, 0, 0))

# ---------------- edit decision list: shots hang on WORDS ----------------
# per line: list of (word index where the shot starts, kind, arg, zoom). Face shots: kind "face" arg=None.
EDL = {
    "5228": [(0, "face", None, 1.0), (5, "spray", "ombre_h", 1), (6, "face", None, 1.2)],                               # ...Paris -> mist, "is live" punch
    "5227": [(0, "face", None, 1.12), (2, "spray", "moksha_v", 1), (3, "spray", "poem_v", 1)],                           # signature / scents
    "5211": [(0, "face", None, 1.0), (2, "still", "wash1", 1)],                                                         # washes
    "5212": [(0, "face", None, 1.0), (3, "still", "trio", 1), (4, "still", "inbox", 1)],                                # entire (box) / gift / sets
    "5215": [(0, "black", None, 1), (("end", 4), "spray", "ombre_h", 1),                                   # turning line over BLACK -> drop
             (9, "split", (("still", "wash0"), ("still", "wash2")), 1), (11, "grid", (("spray", "moksha_v"), ("still", "trio"), ("still", "wash3"), ("spray", "ombre_v")), 1),
             (16, "face", None, 1.25)],
    "5216": [(0, "still", "zeenat", 1), (3, "face", None, 1.12), (5, "still", "aries", 1), (6, "still", "taurus", 1), (8, "still", "gemini", 1),
             (9, "split", (("still", "abyad"), ("still", "aleud")), 1)],
    "5226": [(0, "face", None, 1.0), (4, "face", None, 1.25), (5, "still", "window", 1), (10, "face", None, 1.12), (15, "spray", "ombre_v", 1)],
    "5222": [(0, "face", None, 1.0), (4, "face", None, 1.22), (7, "face", None, 1.3)],
}
# keyword pop-ups (clip, word index, text, hold seconds) and DROPS (timeline times with punch + flash)
POPS = [("5228", 7, "IS LIVE", .9), ("5215", ("end", 4), "BUY 1 GET 1 FREE", 1.3), ("5215", 9, "50% OFF", 1.1), ("5215", 16, "YOUR PICK", .65),
        ("5216", 3, "CLEARANCE SALE", 1.2), ("5226", 4, "TILL 27 NOV", 1.0), ("5226", 15, "miamorparis.in", 1.0),
        ("5222", 4, "DON'T MISS OUT", .9), ("5222", 7, "HAPPY SHOPPING", .9)]


SHOTS = []   # (t0, t1, kind, arg, zoom, clip)
for k, a0, a1, st in TL:
    e = EDL[k]
    for i, (wi, kind, arg, zoom) in enumerate(e):
        t0 = st if i == 0 else at(k, wi)
        t1 = (at(k, e[i + 1][0]) if i + 1 < len(e) else (TL[TL.index((k, a0, a1, st)) + 1][3] if k != TL[-1][0] else VO_END))
        SHOTS.append((round(t0 * FPS) / FPS, round(t1 * FPS) / FPS, kind, arg, zoom, k))
SHOTS[0] = (0.0,) + SHOTS[0][1:]
POPT = [(at(k, wi), at(k, wi) + hold, txt) for k, wi, txt, hold in POPS]
DROPS = [T1, T2, T3]
for i in range(1, len(SHOTS)):            # a cut just before a drop waits for the drop
    for d in DROPS:
        if 0 < d - SHOTS[i][0] <= .15: SHOTS[i] = (d,) + SHOTS[i][1:]; SHOTS[i - 1] = SHOTS[i - 1][:1] + (d,) + SHOTS[i - 1][2:]
CAPS = []    # karaoke chunks of 3 words: (t0, t1, [(word, ws, we)])
for k, a0, a1, st in TL:
    ws = [(w_, st + (s_ - a0), st + (e_ - a0)) for w_, s_, e_ in WORDS[k] if w_]
    for i in range(0, len(ws), 3):
        ch = ws[i:i + 3]; nxt = ws[i + 3][1] if i + 3 < len(ws) else ch[-1][2] + .25
        CAPS.append((ch[0][1] - .05, min(nxt, ch[-1][2] + .35), ch))

# ---------------- look ----------------
VIG = Image.new("L", (W, H), 0); _v = np.zeros((H, W), np.float32)
yy, xx = np.mgrid[0:H, 0:W]; _v = ((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 1.7)) ** 2
VIG = np.clip(1 - .28 * np.clip(_v - .35, 0, 1.2), .66, 1).astype(np.float32)[..., None]
def grade(im):
    a = np.asarray(im).astype(np.float32) / 255
    a = .04 + a * .94                                    # lift blacks a touch, soft
    a = a ** np.array([.97, 1.0, 1.05], np.float32)       # warm
    a = .5 + (a - .5) * .96                               # gentle contrast
    hl = np.clip((a - .75) / .25, 0, 1); a = a + hl * np.array([.015, .01, -.01], np.float32)   # creamy highlights
    a = a * VIG
    return Image.fromarray(np.clip(a * 255, 0, 255).astype(np.uint8))

def text_img(s, f, fill, stroke=0, sfill=(0, 0, 0)):
    tmp = Image.new("RGBA", (W * 3, 600)); d = ImageDraw.Draw(tmp)
    d.text((W * 1.5, 300), s, font=f, fill=fill, anchor="mm", stroke_width=stroke, stroke_fill=sfill)
    return tmp.crop(tmp.getbbox())
def pop(im, s, u):
    """big keyword pop-up: Montserrat Black, ivory with gold underline, scale-pop, autofit <= 940 px"""
    lay = text_img(s.upper() if not s.endswith(".in") else s, MS(150), IVORY, 6, (0, 0, 0))
    fit = min(1.0, 940 / lay.width) * .9; sc = fit * (.55 + .45 * back(u / .3))      # back() peaks ~1.1 -> never wider than 940 px
    lay = lay.resize((max(1, int(lay.width * sc)), max(1, int(lay.height * sc))), Image.LANCZOS)
    a = ss(u / .08); lay.putalpha(lay.getchannel("A").point(lambda v: int(v * a)))
    sh = Image.new("RGBA", lay.size); sh.putalpha(lay.getchannel("A").point(lambda v: int(v * .7)))
    y = 640; im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)), ((W - lay.width) // 2, y - lay.height // 2 + 8))
    im.alpha_composite(lay, ((W - lay.width) // 2, y - lay.height // 2))
    lw = int(lay.width * .55 * ss((u - .1) / .25)); d = ImageDraw.Draw(im)
    if lw > 4: d.rectangle(((W - lw) // 2, y + lay.height // 2 + 18, (W + lw) // 2, y + lay.height // 2 + 24), fill=GOLD + (255,))
def captions(im, t):
    for c0, c1, ch in CAPS:
        if c0 <= t < c1:
            if any(c0 < d <= t for d in DROPS) or any(d <= t < d + .3 for d in DROPS): return
            f = MS(62, "ExtraBold"); d0 = ImageDraw.Draw(Image.new("RGB", (1, 1))); sp = d0.textlength(" ", font=f)
            words = [w_ for w_, _, _ in ch]; ws_ = [d0.textlength(w_, font=f) for w_ in words]; tw = sum(ws_) + sp * (len(words) - 1)
            lay = Image.new("RGBA", (int(tw) + 40, 110)); d = ImageDraw.Draw(lay); x = 20
            for (w_, s_, e_), ww in zip(ch, ws_):
                col = GOLD if s_ - .03 <= t < e_ + .08 else (255, 255, 255)
                d.text((x, 14), w_, font=f, fill=col, stroke_width=5, stroke_fill=(0, 0, 0)); x += ww + sp
            fit = min(1.0, 940 / lay.width); lay = lay.resize((int(lay.width * fit), int(lay.height * fit)), Image.LANCZOS)
            a = ss((t - c0) / .08); lay.putalpha(lay.getchannel("A").point(lambda v: int(v * a)))
            im.alpha_composite(lay, ((W - lay.width) // 2, 1500)); return

# ---------------- outro (fixed, beat-cut) ----------------
OUT_T0 = VO_END
def outro(u, beat=None):
    seq = [("spray", "moksha_v"), ("spray", "ombre_h"), ("still", "trio"), ("still", "zeenat"),
           ("split", (("spray", "poem_v"), ("still", "inbox"))), ("split", (("still", "aries"), ("still", "wash1"))),
           ("grid", (("spray", "moksha_v"), ("still", "trio"), ("still", "gemini"), ("spray", "ombre_v"))),
           ("grid", (("still", "window"), ("still", "abyad"), ("still", "wash0"), ("spray", "poem_h")))]
    cuts = [fr(o - M_D4) for o in OUT_ONS]
    n = max(i for i, c in enumerate(cuts) if c <= u + 1e-6)
    if n < 8:
        kind, arg = seq[n]; lu = u - cuts[n]; im = shot(kind, arg, lu, cuts[n + 1] - cuts[n]).convert("RGB")
        if n < 4: im = punch(im, lu)
        return im, lu
    return None, u - cuts[8]
def endcard(u):
    im = Image.new("RGBA", (W, H), (8, 6, 6, 255))
    glow = Image.new("RGBA", (W, H)); ImageDraw.Draw(glow).ellipse((120, 520, W - 120, 1260), fill=GOLD + (55,)); im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(120)))
    lg = Image.open(R + "assets/cutouts/logo_gold.png").convert("RGBA"); lg = lg.resize((260, int(260 * lg.height / lg.width)), Image.LANCZOS)
    a = ss(u / .35); sc = 1 + .12 * (1 - ss(u / .5)); lg = lg.resize((int(lg.width * sc), int(lg.height * sc)), Image.LANCZOS)
    lg.putalpha(lg.getchannel("A").point(lambda v: int(v * a))); im.alpha_composite(lg, ((W - lg.width) // 2, 660 - lg.height // 2))
    for y, s, f, col, d0 in [(860, "Mi Amor Paris", BOD(84), GOLD2, .2), (980, "Black Friday ends 27 Nov", MS(46, "SemiBold"), IVORY, .45),
                             (1060, "comment SCENT for the quiz", MS(38, "Medium"), (215, 205, 190), .7)]:
        lay = text_img(s, f, col); aa = ss((u - d0) / .3); lay.putalpha(lay.getchannel("A").point(lambda v: int(v * aa)))
        im.alpha_composite(lay, ((W - lay.width) // 2, y - lay.height // 2))
    d = ImageDraw.Draw(im); lw = int(300 * ss((u - .3) / .4)); d.rectangle(((W - lw) // 2, 916, (W + lw) // 2, 918), fill=GOLD + (255,))
    return im

def punch(im, lu):
    """drop punch-zoom 1.2 -> 1.0"""
    z = 1 + .2 * (1 - ss(lu / .35))
    if z > 1.001:
        w, h = W / z, H / z; im = im.resize((W, H), Image.LANCZOS, box=((W - w) / 2, (H - h) / 2, (W + w) / 2, (H + h) / 2))
    return im

BEAT = 60 / 96
def frame(t):
    if t >= OUT_T0:
        u = t - OUT_T0; im, eu = outro(u)
        if im is None: return endcard(eu)
        im = grade(im).convert("RGBA")
        if eu < .06: im.alpha_composite(Image.new("RGBA", (W, H), (255, 240, 205, int(110 * (1 - eu / .06)))))
        return im
    s = [x for x in SHOTS if x[0] <= t][-1]; t0, t1, kind, arg, zoom, k = s; lu = t - t0
    if kind == "face":
        kk, a0, a1, st = [x for x in TL if x[0] == k][0]; src = a0 + (t - st)
        im = face(k, src, zoom)
    else:
        im = shot(kind, arg, lu, t1 - t0)
    for d in DROPS:
        if 0 <= t - d < .4: im = punch(im, t - d)
    im = grade(im).convert("RGBA")
    for d in DROPS:
        if 0 <= t - d < .14: im.alpha_composite(Image.new("RGBA", (W, H), (245, 214, 150, int(150 * (1 - (t - d) / .14)))))
    if lu < .06 and t0 > 0 and kind != "black":   # soft cut breath
        im.alpha_composite(Image.new("RGBA", (W, H), (255, 245, 225, int(45 * (1 - lu / .06)))))
    popping = False
    for p0, p1, txt in POPT:
        if p0 <= t < p1: pop(im, txt, t - p0); popping = True
    if not popping: captions(im, t)
    if t < .3: im.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(255 * (1 - t / .3)))))
    return im

# ---------------- audio ----------------
def clean_voice(k, a0, a1):
    """RNNoise -> FFT denoise (noise floor from the pauses) -> hum notch -> warmth/clarity EQ -> de-esser -> gentle comp. No loudnorm."""
    out = WORK + f"v_{k}.wav"
    af = (f"atrim={a0}:{a1},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=mono,highpass=f=75,"
          f"arnndn=m={R}assets/audio/rnnoise_bd.rnnn:mix=0.85,afftdn=nr=10:nf=-42:tn=1,"
          "equalizer=f=50:t=q:w=8:g=-18,equalizer=f=100:t=q:w=8:g=-12,equalizer=f=150:t=q:w=8:g=-8,"
          "equalizer=f=220:t=q:w=1.0:g=2,equalizer=f=3200:t=q:w=1.2:g=2.5,equalizer=f=450:t=q:w=1.2:g=-1.5,"
          "deesser=i=0.35:f=0.5,acompressor=threshold=-22dB:ratio=2.5:attack=8:release=120:makeup=1")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", SRC[k], "-af", af, "-ar", str(SR), out], check=True)
    with wave.open(out) as w: x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    return x
def read_wav(p):
    with wave.open(p) as w:
        x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
        if w.getnchannels() == 2: x = x.reshape(-1, 2).mean(1)
        sr = w.getframerate()
    if sr != SR: x = np.interp(np.arange(int(len(x) * SR / sr)) / SR * sr, np.arange(len(x)), x)
    return x

def music(n):
    """Tannay's track #7 re-arranged sample-exact on the edit: calm bed looped (2.56 s bar loop, crossfaded) under the opening,
    its own pause+DROP on 'free' (black -> drop), pause+drop on '50%', breakdown under 'Your pick', big drop on 'Plus',
    calm bed again under store info + closer, pause then final drop for the beat-cut outro, natural tail under the end card."""
    with wave.open(TRK) as w: x = np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, 2).astype(np.float32) / 32768
    out = np.zeros((n, 2), np.float32); XF = int(.06 * SR)
    def place(a, b, t0, xf=XF, g=1.0):
        seg = x[int(a * SR):int(b * SR)].copy(); i = int(round(t0 * SR))
        if i < 0: seg = seg[-i:]; i = 0
        m = min(len(seg), n - i)
        if m <= 0: return
        seg = seg[:m]; r = np.ones(m, np.float32); k = min(xf, m // 2)
        r[:k] = np.linspace(0, 1, k); r[-k:] = np.minimum(r[-k:], np.linspace(1, 0, k)); out[i:i + m] += g * seg * r[:, None]
    LA, LB = 1.90, 4.46; LL = LB - LA
    def calm(t_from, t_to):           # loop the calm bar backwards from t_to (last piece ends exactly at t_to)
        e = t_to
        while e > t_from - .01:
            s0 = max(t_from - .06, e - LL - .06); place(LB - (e - s0), LB, s0); e -= LL
    # 1) opening bed, track's own run-in to the first drop (pause 5.8-6.45 sits under the black)
    calm(0, T1 - (M_D1 - LA)); place(LA, M_D1, T1 - (M_D1 - LA))
    place(LB - .7, LB, T1 - .7, xf=int(.2 * SR), g=.35)           # keep a soft bed inside the track's pre-drop gap (never silent)
    place(M_D1, 7.70 + .06, T1)                                  # DROP on 'free'
    place(M_P1 - .06, M_D3, T2 - (M_D2 - M_P1))                  # pause -> drop on '50%' -> breakdown
    place(M_D3, M_P4 + .15, T3, xf=int(.15 * SR))                # DROP on 'Plus'
    calm(T3 + (M_P4 - M_D3), VO_END - (M_D4 - M_P4))             # calm under store info + closer
    place(M_P4 - .06, M_END, VO_END - (M_D4 - M_P4))             # pause -> final drop -> tail
    fi = int(.3 * SR); out[:fi] *= np.linspace(0, 1, fi)[:, None]
    from scipy.signal import butter, sosfilt                    # tame lows: subtract 0.35 of a 90 Hz lowpass
    lo = sosfilt(butter(2, 90, "low", fs=SR, output="sos"), out, axis=0); out = out - .35 * lo
    fo = int(.6 * SR); out[-fo:] *= np.linspace(1, 0, fo)[:, None]
    return out.astype(np.float32)

def build_audio(out):
    n = int(TOTAL * SR); vo = np.zeros(n, np.float32); speak = np.zeros(n, np.float32)
    for k, a0, a1, st in TL:
        x = clean_voice(k, a0, a1); i0 = int(round(st * SR)); m = min(n - i0, len(x)); vo[i0:i0 + m] += x[:m]
        speak[i0:i0 + m] = 1                               # hold the duck over the whole line
    rms_v = np.sqrt(np.mean(vo[speak > 0] ** 2)); vo *= (10 ** (-18 / 20)) / rms_v      # fixed gain to -18 dBFS RMS
    m = music(n); rms_m = np.sqrt(np.mean(m ** 2)); m *= (10 ** (-18 / 20)) / rms_m * 10 ** (-8 / 20)   # bed = voice -8 dB
    k_ = np.ones(int(.12 * SR)) / int(.12 * SR); duck = 1 - .5 * np.clip(np.convolve(speak, k_, "same"), 0, 1)   # -> 0.5 while speaking (lands the voice ~13-14 dB over the bed)
    m = m * duck[:, None]; mix = vo[:, None] + m
    mix *= 10 ** (-1 / 20) / np.max(np.abs(mix))           # peak -1 dBFS
    with wave.open(out, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype(np.int16).tobytes())
    sp = speak > 0; g = 10 ** (-1 / 20) / np.max(np.abs(vo[:, None] + m))
    v_db = 20 * np.log10(np.sqrt(np.mean((vo * g)[sp] ** 2))); m_db = 20 * np.log10(np.sqrt(np.mean((m * g)[sp] ** 2)))
    m_open = 20 * np.log10(np.sqrt(np.mean((m * g)[~sp] ** 2)) + 1e-9)
    mm = np.sqrt(np.convolve(m.mean(1) ** 2, np.ones(SR // 4) / (SR // 4), "same")); quiet = 20 * np.log10(mm[SR // 2:-SR].min() + 1e-9)
    print(f"voice {v_db:.1f} dB | music under voice {m_db:.1f} dB (gap {v_db - m_db:.1f} dB) | music alone {m_open:.1f} dB | quietest music 250ms {quiet:.1f} dB")

if __name__ == "__main__":
    only = os.environ.get("ONLY")
    if only:
        for s in only.split(","): frame(float(s)).convert("RGB").save(WORK + f"sp_{s}.jpg", quality=85)
        print("TOTAL", TOTAL, "VO_END", round(VO_END, 2), "shots", len(SHOTS), "drops", DROPS, "TL", [(k, round(st, 2)) for k, _, _, st in TL]); sys.exit()
    fd = WORK + "fr/"; os.makedirs(fd, exist_ok=True)
    N = int(round(TOTAL * FPS))
    for i in range(N): frame(i / FPS).convert("RGB").save(fd + f"{i:04d}.jpg", quality=93)
    build_audio(WORK + "mix.wav")
    name = D + "black_friday_spec_v1.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", fd + "%04d.jpg", "-i", WORK + "mix.wav", "-map", "0:v", "-map", "1:a",
                    "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p", "-r", str(FPS), "-c:a", "aac", "-b:a", "256k",
                    "-shortest", "-movflags", "+faststart", name], check=True)
    frame(T1 + .5).convert("RGB").save(D + "cover_spec.jpg", quality=94)
    print("done", N, "frames")

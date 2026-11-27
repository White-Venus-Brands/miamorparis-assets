"""27 Nov: 'Black Friday ends tonight' reel. Re-cut of Tannay's Black Friday takes (exact Scribe words) for the last day:
hook card on the drop -> offer -> candles -> where -> 'ENDS TONIGHT' beat -> closer -> end card.
Music: Decibold sound #3 (156 bpm), its drops landed on the hook, 'clearance', and 'Don't miss out'.
Usage: python3 build_lastday.py WORKDIR"""
import os, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

WORK = sys.argv[1].rstrip("/") + "/"; sys.argv = [sys.argv[0], WORK]
D = os.path.dirname(os.path.abspath(__file__)) + "/"; sys.path.insert(0, D)
import build_spec as S
from scipy.signal import butter, find_peaks, sosfilt, stft
W, H, FPS, SR, fr, ss = S.W, S.H, S.FPS, S.SR, S.fr, S.ss
GOLD, GOLD2, IVORY = S.GOLD, S.GOLD2, S.IVORY

# ---------- music map (track 3): drops 6.0 / 15.1 / 21.3 / 27.49 ----------
OFF = -5.7                      # timeline t = track u + OFF  -> drop 6.0 lands at 0.3
def T(u): return fr(u + OFF)
HOOK_END = 1.7

# ---------- lines (5226 starts at "in store...", 'till the 27th' dropped: it's the last day) ----------
L = {k: (a0, a1, ws) for k, a0, a1, ws in [(x[0], x[1], x[2], x[3]) for x in S.LINES]}
ws26 = S.WORDS["5226"][5:]
L["5226"] = (ws26[0][1] - .12, ws26[-1][2] + .18, ws26)
TL = []
def put(k, st): TL.append((k, L[k][0], L[k][1], st)); return st + (L[k][1] - L[k][0])
e = put("5215", HOOK_END)
w = S.WORDS["5216"]; st = T(15.1) - (w[3][1] - L["5216"][0])         # 'clearance' on the 15.1 drop
e = put("5216", max(e + .12, st))
e = put("5226", e + .12)
GAP_T0 = e + .05                                                     # 'ENDS TONIGHT' beat in the gap
w = S.WORDS["5222"]; st = T(27.49) - (w[4][1] - L["5222"][0])        # "Don't" on the 27.49 drop
VO_START22 = max(e + 1.0, st); e = put("5222", VO_START22)
VO_END = fr(e); OUT0 = VO_END + .1; TOTAL = fr(OUT0 + 3.0)
S.TL = TL
DROPS = [T(6.0), T(15.1), T(27.49)]
S.DROPS = DROPS

EDL = {"5215": [(0, "face", None, 1.0), (("end", 4), "spray", "ombre_h", 1), (9, "split", (("still", "wash0"), ("still", "wash2")), 1),
                (11, "grid", (("spray", "moksha_v"), ("still", "trio"), ("still", "wash3"), ("spray", "ombre_v")), 1), (16, "face", None, 1.25)],
       "5216": S.EDL["5216"],
       "5226": [(0, "still", "window", 1), (5, "face", None, 1.12), (10, "spray", "ombre_v", 1)],
       "5222": S.EDL["5222"]}
def at(k, wi):
    kk, a0, a1, st = [x for x in TL if x[0] == k][0]; ws = L[k][2]
    if isinstance(wi, tuple): return st + (ws[wi[1]][2] - a0)
    return st + (ws[wi][1] - a0)
SH = [[0.0, HOOK_END, "hook", None, 1, None]]
for i_, (k, a0, a1, st) in enumerate(TL):
    ed = EDL[k]
    for i, (wi, kind, arg, zoom) in enumerate(ed):
        t0 = st if i == 0 else at(k, wi)
        t1 = at(k, ed[i + 1][0]) if i + 1 < len(ed) else (TL[i_ + 1][3] if i_ + 1 < len(TL) else OUT0)
        SH.append([fr(t0), fr(t1), kind, arg, zoom, k])
for i in range(1, len(SH)):                      # close gaps: previous shot holds until the next starts
    SH[i - 1][1] = SH[i][0]
for i in range(1, len(SH)):
    for d in DROPS:
        if 0 < d - SH[i][0] <= .15 and SH[i - 1][0] + .2 < d: SH[i][0] = d; SH[i - 1][1] = d
# the 'ENDS TONIGHT' gap: hold a mist shot
gi = [i for i, s in enumerate(SH) if s[5] == "5222"][0]
SH.insert(gi, [fr(GAP_T0), SH[gi][0], "spray", "moksha_v", 1, None]); SH[gi - 1][1] = fr(GAP_T0)
SHOTS = [tuple(s) for s in SH]
POPS = [("5215", ("end", 4), "BUY 1 GET 1 FREE", 1.3), ("5215", 9, "50% OFF", 1.1), ("5215", 16, "YOUR PICK", .65),
        ("5216", 3, "CLEARANCE SALE", 1.2), ("5226", 13, "miamorparis.in", 1.0), ("5222", 4, "DON'T MISS OUT", .9), ("5222", 7, "HAPPY SHOPPING", .9)]
S.POPT = [(at(k, wi), at(k, wi) + hold, txt) for k, wi, txt, hold in POPS] + [(GAP_T0, SHOTS[gi][1] if False else VO_START22 + .1, "ENDS TONIGHT")]
S.CAPS = []
for k, a0, a1, st in TL:
    ws = [(w_, st + (s_ - a0), st + (e_ - a0)) for w_, s_, e_ in L[k][2] if w_]
    for i in range(0, len(ws), 3):
        ch = ws[i:i + 3]; nxt = ws[i + 3][1] if i + 3 < len(ws) else ch[-1][2] + .25
        S.CAPS.append((ch[0][1] - .05, min(nxt, ch[-1][2] + .35), ch))

def text_c(im, y, s, f, fill, a=1.0, stroke=0):
    lay = Image.new("RGBA", (W, 400)); d = ImageDraw.Draw(lay)
    d.text((W // 2, 200), s, font=f, fill=fill, anchor="mm", stroke_width=stroke, stroke_fill=(0, 0, 0)); lay = lay.crop(lay.getbbox())
    if lay.width > 940: lay = lay.resize((940, int(lay.height * 940 / lay.width)), Image.LANCZOS)
    lay.putalpha(lay.getchannel("A").point(lambda v: int(v * a))); im.alpha_composite(lay, ((W - lay.width) // 2, y - lay.height // 2))

def hook_card(t):
    """black, gold glow, 'BLACK FRIDAY' then 'ENDS TONIGHT' slams in on the drop"""
    im = S.grade(S.spray("ombre_h", t)).convert("RGBA")
    im.alpha_composite(Image.new("RGBA", (W, H), (6, 4, 4, 200)))
    text_c(im, 760, "BLACK FRIDAY", S.MS(64, "SemiBold"), GOLD2, ss(t / .25))
    if t >= DROPS[0]:
        u = t - DROPS[0]; f = S.MS(int(150 * (1 + .35 * (1 - S.back(u / .3)))))
        text_c(im, 900, "ENDS", f, IVORY, 1, 5); text_c(im, 1060, "TONIGHT", f, IVORY, 1, 5)
        d = ImageDraw.Draw(im); lw = int(420 * ss((u - .1) / .3)); d.rectangle(((W - lw) // 2, 1160, (W + lw) // 2, 1166), fill=GOLD + (255,))
        text_c(im, 1240, "Buy 1 Get 1 Free  ·  or 50% off", S.MS(44, "SemiBold"), (230, 220, 205), ss((u - .3) / .3))
    return im

def endcard(u):
    im = Image.new("RGBA", (W, H), (8, 6, 6, 255))
    glow = Image.new("RGBA", (W, H)); ImageDraw.Draw(glow).ellipse((120, 520, W - 120, 1260), fill=GOLD + (55,)); im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(120)))
    lg = Image.open(S.R + "assets/cutouts/logo_gold.png").convert("RGBA"); lg = lg.resize((260, int(260 * lg.height / lg.width)), Image.LANCZOS)
    a = ss(u / .35); lg.putalpha(lg.getchannel("A").point(lambda v: int(v * a))); im.alpha_composite(lg, ((W - lg.width) // 2, 660 - lg.height // 2))
    for y, s_, f, col, d0 in [(860, "Mi Amor Paris", S.BOD(84), GOLD2, .2), (980, "Black Friday ends tonight", S.MS(46, "SemiBold"), IVORY, .45),
                              (1050, "Lajpat Nagar · R Cube Monad Mall · miamorparis.in", S.MS(30, "Medium"), (215, 205, 190), .6),
                              (1130, "comment SCENT for the quiz", S.MS(38, "Medium"), (215, 205, 190), .8)]:
        text_c(im, y, s_, f, col, ss((u - d0) / .3))
    d = ImageDraw.Draw(im); lw = int(300 * ss((u - .3) / .4)); d.rectangle(((W - lw) // 2, 916, (W + lw) // 2, 918), fill=GOLD + (255,))
    return im

def pill(im):
    f = S.MS(30, "Bold"); txt = "LAST DAY  ·  ENDS TONIGHT"; d = ImageDraw.Draw(im); tw = d.textlength(txt, font=f)
    x0, y0 = (W - tw) / 2 - 26, 210; d.rounded_rectangle((x0, y0, x0 + tw + 52, y0 + 58), radius=29, fill=GOLD + (235,))
    d.text((W // 2, y0 + 30), txt, font=f, fill=(20, 14, 10), anchor="mm")

def frame(t):
    if t >= OUT0: return endcard(t - OUT0)
    i = max(j for j, s in enumerate(SHOTS) if s[0] <= t + 1e-6); t0, t1, kind, arg, zoom, k = SHOTS[i]; lu = t - t0
    if kind == "hook":
        im = hook_card(t)
    else:
        if kind == "face":
            kk, a0, a1, st = [x for x in TL if x[0] == k][0]; im = S.face(k, a0 + (t - st), zoom)
        else: im = S.shot(kind, arg, lu, t1 - t0)
        for d in DROPS:
            if 0 <= t - d < .4: im = S.punch(im, t - d)
        im = S.grade(im).convert("RGBA")
        if lu < .06 and i > 0: im.alpha_composite(Image.new("RGBA", (W, H), (255, 245, 225, int(45 * (1 - lu / .06)))))
        pill(im)
    for d in DROPS:
        if 0 <= t - d < .14: im.alpha_composite(Image.new("RGBA", (W, H), (245, 214, 150, int(150 * (1 - (t - d) / .14)))))
    if kind != "hook":
        popping = False
        for p0, p1, txt in S.POPT:
            if p0 <= t < p1: S.pop(im, txt, t - p0); popping = True
        if not popping: S.captions(im, t)
    if t < .2: im.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(255 * (1 - t / .2)))))
    return im

def music(n):
    with wave.open(S.R + "assets/music/decibold_trk3.wav") as w_:
        x = np.frombuffer(w_.readframes(w_.getnframes()), np.int16).reshape(-1, 2).astype(np.float32) / 32768
    out = np.zeros((n, 2), np.float32)
    def place(a, b, t0, xf=.06, g=1.0):
        seg = x[int(a * SR):int(b * SR)].copy(); i = int(round(t0 * SR))
        if i < 0: seg = seg[-i:]; i = 0
        m = min(len(seg), n - i)
        if m <= 0: return
        seg = seg[:m]; r = np.ones(m, np.float32); k = min(int(xf * SR), m // 2)
        r[:k] = np.linspace(0, 1, k); r[-k:] = np.minimum(r[-k:], np.linspace(1, 0, k)); out[i:i + m] += g * seg * r[:, None]
    place(5.7, 29.6, 0.0); e = 29.6 + OFF
    while e < TOTAL: place(21.3 - .06, 24.372 + .06, e - .06); e += 3.072      # 2-bar loop after the track runs out
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
    print("TOTAL", TOTAL, "TL", [(k, round(st, 2)) for k, _, _, st in TL], "DROPS", DROPS, "GAP", round(GAP_T0, 2))
    only = os.environ.get("ONLY")
    if only:
        for s_ in only.split(","): frame(float(s_)).convert("RGB").save(WORK + f"ld_{s_}.jpg", quality=85)
        sys.exit()
    fd = WORK + "fr_lastday/"; os.makedirs(fd, exist_ok=True)
    for i in range(int(round(TOTAL * FPS))): frame(i / FPS).convert("RGB").save(fd + f"{i:04d}.jpg", quality=93)
    build_audio(WORK + "mix_lastday.wav")
    out = D + "black_friday_last_day.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", fd + "%04d.jpg", "-i", WORK + "mix_lastday.wav", "-map", "0:v", "-map", "1:a",
                    "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p", "-r", str(FPS), "-c:a", "aac", "-b:a", "256k",
                    "-shortest", "-movflags", "+faststart", out], check=True)
    print("done", out)

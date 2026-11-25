"""Black Friday talking reel, one edit per Decibold sound (tracks 1-6; track 7 = build_spec.py).
Same exact-word captions, voice chain and spec look as build_spec.py, but each edit is cut to its own song:
the song is analysed (STFT flux onsets + bass envelope), arranged sample-exact so its drop hits on 'free' and its
last drop opens the outro, every picture cut snaps to the nearest onset, and each version has its own visual style.
Usage: python3 build_music.py <trk1..trk6> WORKDIR"""
import os, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

NAME = sys.argv[1]; WORK = sys.argv[2].rstrip("/") + "/"
sys.argv = [sys.argv[0], WORK]
D = os.path.dirname(os.path.abspath(__file__)) + "/"; sys.path.insert(0, D)
import build_spec as S
from scipy.signal import butter, find_peaks, sosfilt, stft

W, H, FPS, SR, fr, ss = S.W, S.H, S.FPS, S.SR, S.fr, S.ss

# ---------- timeline: lines back to back ----------
t = 0.6; TL = []
for k, a0, a1, ws in S.LINES: TL.append((k, a0, a1, t)); t += (a1 - a0) + S.GAP
S.TL = TL; VO_END = fr(t)
T1 = fr(S.wt("5215", 4, True)); T2 = fr(S.wt("5215", 9))

# ---------- music arrangement per track ----------
def load(i):
    with wave.open(S.R + f"assets/music/decibold_trk{i}.wav") as w:
        return np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, 2).astype(np.float32) / 32768
class Arr:
    def __init__(s, x, n): s.x = x; s.n = n; s.out = np.zeros((n, 2), np.float32)
    def place(s, a, b, t0, xf=.06, g=1.0):
        seg = s.x[int(a * SR):int(b * SR)].copy(); i = int(round(t0 * SR))
        if i < 0: seg = seg[-i:]; i = 0
        m = min(len(seg), s.n - i)
        if m <= 0: return
        seg = seg[:m]; r = np.ones(m, np.float32); k = min(int(xf * SR), m // 2)
        if k > 0: r[:k] = np.linspace(0, 1, k); r[-k:] = np.minimum(r[-k:], np.linspace(1, 0, k))
        s.out[i:i + m] += g * seg * r[:, None]
    def lead_in(s, a, b, run_end, t_anchor, xf=.06):
        """track [a, run_end) ends at t_anchor; before it, loop [a, b) backwards to timeline 0"""
        st = t_anchor - (run_end - a); s.place(a, run_end + xf, st, xf); e = st; L = b - a
        while e > -.01: s.place(b - min(L, e + xf) - xf, b + xf, e - min(L, e + xf) - xf, xf); e -= L
    def loop(s, a, b, t_from, t_to, xf=.06):
        L = b - a; t0 = t_from
        while t0 < t_to - .01:
            ln = min(L, t_to - t0); s.place(a, a + ln + xf, t0, xf); t0 += L

def arrange(n):
    """returns (stereo music, timeline drops, outro start, lowpass-mix envelope or None)"""
    if NAME == "trk1":   # 74 bpm: melodic bass + riser, drums drop at 10.25; 2-bar loop 18.31-24.77; natural end
        x = load(1); A = Arr(x, n); off = T1 - 10.25
        A.place(0, 24.77 + .06, off); e = 24.77 + off; tail = 26.91; tl0 = TOTAL - (30.32 - tail)
        A.loop(18.31, 24.77, e, tl0); A.place(tail, 30.32, tl0, .1)
        return A.out, [T1], None
    if NAME == "trk2":   # 135 bpm groove, break 19.6-21.3 -> drop 21.34 on 'free'; dip 39.6-41.7 into outro
        x = load(2); A = Arr(x, n); off = T1 - 21.34
        A.place(max(0, -off), 39.06 + .06, max(0, off)); e = 39.06 + off; pre = OUT0 - (41.71 - 39.6)
        A.loop(30.17, 37.26, e, pre); A.place(39.6, 41.71 + .06, pre); A.place(21.34, 21.34 + (TOTAL - OUT0) + .1, OUT0)
        return A.out, [T1, OUT0], None
    if NAME == "trk3":   # 156 bpm: calm 0-6 -> DROP 6.0 on 'free'; drops 15.1 / 21.3 / 27.49 fall on the lines naturally
        x = load(3); A = Arr(x, n); off = T1 - 6.0
        A.lead_in(1.5, 4.572, 6.0, T1); A.place(6.0, 29.6, T1); e = 29.6 + off
        A.loop(21.3, 24.372, e - .06, TOTAL)
        return A.out, [T1, 15.1 + off, 21.3 + off, OUT0], None
    if NAME == "trk4":   # 131 bpm: beat -> long breakdown 7.3-13.58 under the build-up -> DROP 13.58 on 'free'
        x = load(4); A = Arr(x, n); off = T1 - 13.58; bar = 1.835
        A.place(-off, 7.3 + .06, 0); A.place(7.3, 13.58 + .02, 7.3 + off, g=2.8)     # lift the very quiet breakdown (+9 dB) so the bed never drops out
        A.place(13.58, 20.97 + .06, T1); e = 20.97 + off; pre = OUT0 - 2.0
        A.loop(13.58, 13.58 + 3 * bar, e, pre); A.place(11.58, 13.58 + .06, pre, g=2.8); A.place(13.58, 13.58 + (TOTAL - OUT0) + .1, OUT0)
        drops = [T1] + [e + i * 3 * bar for i in range(6) if e + i * 3 * bar < pre - .5] + [OUT0]
        return A.out, drops, None
    if NAME == "trk5":   # 129 bpm steady groove: muffled (lowpass) under the build-up, filter opens on 'free'; dips before the outro
        x = load(5); A = Arr(x, n); off = T1 - 12.35
        A.place(-off, 39.75, 0)
        env = np.ones(n, np.float32); i1 = int(T1 * SR); env[:i1] = 0; env[i1:i1 + int(.05 * SR)] = np.linspace(0, 1, int(.05 * SR))
        o0, o1 = int((OUT0 - 1.6) * SR), int(OUT0 * SR); env[o0:o1] = np.linspace(1, .1, o1 - o0); env[o1:o1 + int(.05 * SR)] = np.linspace(.1, 1, int(.05 * SR))
        return A.out, [T1, OUT0], env
    if NAME == "trk6":   # soft pads; bass returns at 25.72 -> on 'free' and again to open the outro
        x = load(6); A = Arr(x, n); off = T1 - 25.72
        A.place(-off, 30.53, 0, .3); e = 30.53 + off; pre = OUT0 - (25.72 - 24.3)
        A.loop(8.0, 23.36, e - .4, pre + .4, xf=.4); A.place(24.3, 30.53, pre, .4)
        return A.out, [T1, OUT0], None

# outro start: on the song's last drop near the end of the voice
OUT0 = VO_END
if NAME == "trk3": OUT0 = fr(max(VO_END - .3, 27.49 + T1 - 6.0)) if 27.49 + T1 - 6.0 > VO_END - .3 else VO_END
if NAME == "trk5":
    hits = [h + T1 - 12.35 for h in (31.72, 32.63, 33.56, 34.49, 35.41)]; OUT0 = fr(min(h for h in hits if h >= VO_END - .05))
if NAME == "trk1":
    hits = [h + T1 - 10.25 for h in (18.31, 19.93, 21.54, 22.61, 24.76)]
    OUT0 = VO_END
OUTRO = 4.2; TOTAL = fr(OUT0 + OUTRO); N = int(round(TOTAL * SR))
MUS, VDROPS, LPENV = arrange(N)
if LPENV is not None:   # muffled version = 350 Hz lowpass, crossfaded by envelope
    lp = sosfilt(butter(4, 350, "low", fs=SR, output="sos"), MUS, axis=0) * 1.6
    MUS = MUS * LPENV[:, None] + lp * (1 - LPENV[:, None])
fo = int(.25 * SR); MUS[:fo] *= np.linspace(0, 1, fo)[:, None]; fo = int(.7 * SR); MUS[-fo:] *= np.linspace(1, 0, fo)[:, None]
MUS = MUS - .35 * sosfilt(butter(2, 90, "low", fs=SR, output="sos"), MUS, axis=0)    # tame lows
VDROPS = sorted(set(fr(d) for d in VDROPS if .5 < d < TOTAL - .5))

# onsets of the arranged song (for cuts)
m1 = MUS.mean(1); f_, t_, Z = stft(m1, SR, nperseg=2048, noverlap=1536); Mg = np.log1p(np.abs(Z) * 100)
fl = np.maximum(0, np.diff(Mg, axis=1)).sum(0); fl = (fl - fl.mean()) / (fl.std() + 1e-9)
pk, pr = find_peaks(fl, height=1.2, distance=int(.14 / (512 / SR))); ONS = t_[1:][pk]; ONS_S = pr["peak_heights"]
STRONG = ONS[ONS_S > np.percentile(ONS_S, 60)] if len(ONS) else ONS

# ---------- edit decision list (shared shots, styled per song) ----------
EDL = dict(S.EDL)
EDL["5215"] = [(0, "face", None, 1.0)] + S.EDL["5215"][1:]
SH = []
for k, a0, a1, st in TL:
    e = EDL[k]
    for i, (wi, kind, arg, zoom) in enumerate(e):
        t0 = st if i == 0 else S.at(k, wi)
        t1 = S.at(k, e[i + 1][0]) if i + 1 < len(e) else (TL[TL.index((k, a0, a1, st)) + 1][3] if k != TL[-1][0] else OUT0)
        SH.append([fr(t0), fr(t1), kind, arg, zoom, k])
SH[0][0] = 0.0; SH[-1][1] = OUT0
for i in range(1, len(SH)):            # snap cuts onto the beat (<= 0.1 s), drops win
    c = SH[i][0]; cand = [d for d in VDROPS if abs(d - c) <= .15] or [o for o in ONS if abs(o - c) <= .1]
    if cand:
        c2 = fr(min(cand, key=lambda o: abs(o - c)))
        if SH[i - 1][0] + .2 < c2 < SH[i][1] - .2: SH[i][0] = c2; SH[i - 1][1] = c2
SHOTS = [tuple(s) for s in SH]
S.DROPS = VDROPS; S.SHOTS = SHOTS
S.POPT = [(S.at(k, wi), S.at(k, wi) + hold, txt) for k, wi, txt, hold in S.POPS]
S.CAPS = []
for k, a0, a1, st in TL:
    ws = [(w_, st + (s_ - a0), st + (e_ - a0)) for w_, s_, e_ in S.WORDS[k] if w_]
    for i in range(0, len(ws), 3):
        ch = ws[i:i + 3]; nxt = ws[i + 3][1] if i + 3 < len(ws) else ch[-1][2] + .25
        S.CAPS.append((ch[0][1] - .05, min(nxt, ch[-1][2] + .35), ch))

# outro cuts on the song's onsets after OUT0
oc = [OUT0]
for o in ONS:
    if o > oc[-1] + .2 and len(oc) < 9: oc.append(fr(o if o - oc[-1] <= .5 else oc[-1] + .32))
while len(oc) < 9: oc.append(fr(oc[-1] + .3))
OUT_CUTS = [c - OUT0 for c in oc]

STYLE = {"trk1": "split_pulse", "trk2": "whip_grid", "trk3": "letterbox", "trk4": "mono_breakdown", "trk5": "flash_shake", "trk6": "soft_dissolve"}[NAME]
SEQ = {"whip_grid": [("grid", (("spray", "moksha_v"), ("still", "trio"), ("still", "gemini"), ("spray", "ombre_v"))), ("spray", "poem_h"),
                     ("grid", (("still", "window"), ("still", "abyad"), ("still", "wash0"), ("spray", "poem_v"))), ("still", "zeenat"),
                     ("split", (("spray", "poem_v"), ("still", "inbox"))), ("spray", "ombre_h"), ("grid", (("still", "aries"), ("still", "wash1"), ("still", "taurus"), ("still", "trio"))), ("still", "window")],
       }.get(STYLE, [("spray", "moksha_v"), ("spray", "ombre_h"), ("still", "trio"), ("still", "zeenat"),
                     ("split", (("spray", "poem_v"), ("still", "inbox"))), ("split", (("still", "aries"), ("still", "wash1"))),
                     ("grid", (("spray", "moksha_v"), ("still", "trio"), ("still", "gemini"), ("spray", "ombre_v"))),
                     ("grid", (("still", "window"), ("still", "abyad"), ("still", "wash0"), ("spray", "poem_h")))])

def render(s, t):
    t0, t1, kind, arg, zoom, k = s; lu = t - t0
    if kind == "face":
        kk, a0, a1, st = [x for x in TL if x[0] == k][0]; return S.face(k, a0 + (t - st), zoom)
    im = S.shot(kind, arg, lu, t1 - t0)
    if STYLE == "split_pulse" and kind in ("still", "spray"):      # product on top, Tannay talking underneath
        kk, a0, a1, st = [x for x in TL if x[0] == k][0]
        can = Image.new("RGB", (W, H), S.GOLD); hh = (H - 18) // 2
        top = im.resize((W - 12, int((W - 12) * H / W)), Image.LANCZOS).crop((0, (int((W - 12) * H / W) - hh + 6) // 2, W - 12, (int((W - 12) * H / W) - hh + 6) // 2 + hh - 6))
        fc = S.face(k, a0 + (t - st), 1.0).resize((W - 12, int((W - 12) * H / W)), Image.LANCZOS); fc = fc.crop((0, 300, W - 12, 300 + hh - 6))
        can.paste(top, (6, 6)); can.paste(fc, (6, hh + 12)); im = can
    return im

def zoomblur(im, k):
    acc = np.asarray(im).astype(np.float32); n = 1
    for z in (1 + .05 * k, 1 + .1 * k, 1 + .16 * k):
        w, h = W / z, H / z; acc += np.asarray(im.resize((W, H), Image.BILINEAR, box=((W - w) / 2, (H - h) / 2, (W + w) / 2, (H + h) / 2))); n += 1
    return Image.fromarray((acc / n).astype(np.uint8))

def outro_frame(u):
    n = max(i for i, c in enumerate(OUT_CUTS) if c <= u + 1e-6)
    if n >= 8: return S.endcard(u - OUT_CUTS[8])
    kind, arg = SEQ[n]; lu = u - OUT_CUTS[n]; im = S.shot(kind, arg, lu, OUT_CUTS[n + 1] - OUT_CUTS[n]).convert("RGB")
    if n < 4: im = S.punch(im, lu)
    if STYLE == "whip_grid" and lu < .12: im = zoomblur(im, 1 - lu / .12)
    im = S.grade(im).convert("RGBA")
    if lu < .06: im.alpha_composite(Image.new("RGBA", (W, H), (255, 240, 205, int(110 * (1 - lu / .06)))))
    return im

RNG = np.random.default_rng(3)
def frame(t):
    if t >= OUT0: return outro_frame(t - OUT0)
    i = max(j for j, s in enumerate(SHOTS) if s[0] <= t + 1e-6); s = SHOTS[i]; lu = t - s[0]
    im = render(s, t)
    if STYLE == "soft_dissolve" and i > 0 and lu < .3:
        im = Image.blend(render(SHOTS[i - 1], t), im, ss(lu / .3))
    if STYLE == "whip_grid" and i > 0 and lu < .12: im = zoomblur(im, 1 - lu / .12)
    if STYLE == "split_pulse" and t > T1:
        ob = [o for o in STRONG if 0 <= t - o < .18]
        if ob:
            z = 1 + .04 * (1 - ss((t - ob[-1]) / .18)); w, h = W / z, H / z
            im = im.resize((W, H), Image.LANCZOS, box=((W - w) / 2, (H - h) / 2, (W + w) / 2, (H + h) / 2))
    for d in VDROPS:
        if 0 <= t - d < .4: im = S.punch(im, t - d) if STYLE != "soft_dissolve" else im.resize((W, H), Image.LANCZOS, box=(W * .03 * (1 - ss((t - d) / .5)), H * .03 * (1 - ss((t - d) / .5)), W - W * .03 * (1 - ss((t - d) / .5)), H - H * .03 * (1 - ss((t - d) / .5))))
        if STYLE == "flash_shake" and 0 <= t - d < .3:
            a = 22 * (1 - (t - d) / .3); dx, dy = RNG.integers(-1, 2, 2) * a
            im = im.resize((int(W * 1.04), int(H * 1.04))).crop((int(W * .02 + dx), int(H * .02 + dy), int(W * .02 + dx) + W, int(H * .02 + dy) + H))
    if STYLE == "mono_breakdown" and t < T1 + .25:
        im = ImageEnhance.Color(im).enhance(.12 + .88 * ss((t - T1) / .25))
    im = S.grade(im).convert("RGBA")
    for d in VDROPS:
        fl_a = 70 if STYLE == "soft_dissolve" else 150
        if 0 <= t - d < .14: im.alpha_composite(Image.new("RGBA", (W, H), (245, 214, 150, int(fl_a * (1 - (t - d) / .14)))))
    if STYLE == "flash_shake" and i > 0 and lu < .08:
        im.alpha_composite(Image.new("RGBA", (W, H), (255, 252, 245, int(120 * (1 - lu / .08)))))
    elif lu < .06 and i > 0 and STYLE != "soft_dissolve":
        im.alpha_composite(Image.new("RGBA", (W, H), (255, 245, 225, int(45 * (1 - lu / .06)))))
    if STYLE == "letterbox" and t < T1 + .3:
        bh = int(190 * (1 - ss((t - T1) / .3))); d_ = ImageDraw.Draw(im)
        if bh > 0: d_.rectangle((0, 0, W, bh), fill=(0, 0, 0, 255)); d_.rectangle((0, H - bh, W, H), fill=(0, 0, 0, 255))
    popping = False
    for p0, p1, txt in S.POPT:
        if p0 <= t < p1: S.pop(im, txt, t - p0); popping = True
    if not popping: S.captions(im, t)
    if t < .3: im.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(255 * (1 - t / .3)))))
    return im

def build_audio(out):
    vo = np.zeros(N, np.float32); speak = np.zeros(N, np.float32)
    for k, a0, a1, st in TL:
        x = S.clean_voice(k, a0, a1); i0 = int(round(st * SR)); m = min(N - i0, len(x)); vo[i0:i0 + m] += x[:m]; speak[i0:i0 + m] = 1
    sp = speak > 0
    vo *= (10 ** (-18 / 20)) / np.sqrt(np.mean(vo[sp] ** 2))                       # fixed gain
    m = MUS * ((10 ** (-26 / 20)) / np.sqrt(np.mean(MUS ** 2)))                     # bed = voice -8 dB
    k_ = np.ones(int(.12 * SR)) / int(.12 * SR); hold = np.clip(np.convolve(speak, k_, "same"), 0, 1)
    under = 20 * np.log10(np.sqrt(np.mean(m[sp] ** 2)))
    floor = float(np.clip(10 ** ((-18 - 14.5 - under) / 20), .2, .6))              # voice sits ~14-15 dB over the music
    duck = 1 - (1 - floor) * hold; mm = m * duck[:, None]; mix = vo[:, None] + mm
    g = 10 ** (-1 / 20) / np.max(np.abs(mix)); mix *= g
    with wave.open(out, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype(np.int16).tobytes())
    v_db = 20 * np.log10(np.sqrt(np.mean((vo * g)[sp] ** 2))); m_db = 20 * np.log10(np.sqrt(np.mean((mm * g)[sp] ** 2)))
    q = np.sqrt(np.convolve(mm.mean(1) ** 2, np.ones(SR // 4) / (SR // 4), "same")); quiet = 20 * np.log10(q[SR // 2:-SR].min() + 1e-9)
    print(f"{NAME}: duck {floor:.2f} | voice {v_db:.1f} dB | music under voice {m_db:.1f} dB (gap {v_db - m_db:.1f}) | quietest music {quiet:.1f} dB")

if __name__ == "__main__":
    print(NAME, STYLE, "TOTAL", TOTAL, "T1", T1, "OUT0", OUT0, "VDROPS", VDROPS, "outro cuts", [round(c, 2) for c in OUT_CUTS])
    only = os.environ.get("ONLY")
    if only:
        for s_ in only.split(","): frame(float(s_)).convert("RGB").save(WORK + f"{NAME}_{s_}.jpg", quality=85)
        sys.exit()
    fd = WORK + f"fr_{NAME}/"; os.makedirs(fd, exist_ok=True)
    have = len(os.listdir(fd)) - 2          # resume; redo the last two (may be half-written)
    for i in range(int(round(TOTAL * FPS))):
        if i >= have: frame(i / FPS).convert("RGB").save(fd + f"{i:04d}.jpg", quality=93)
    build_audio(WORK + f"mix_{NAME}.wav")
    num = NAME[-1]; out = D + f"black_friday_music{num}_{STYLE}.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", fd + "%04d.jpg", "-i", WORK + f"mix_{NAME}.wav", "-map", "0:v", "-map", "1:a",
                    "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p", "-r", str(FPS), "-c:a", "aac", "-b:a", "256k",
                    "-shortest", "-movflags", "+faststart", out], check=True)
    print("done", out)

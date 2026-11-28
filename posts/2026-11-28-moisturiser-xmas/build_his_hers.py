"""'His & Hers' moisturiser reel (28 Nov) on Punjabi Jingle Bell.
Hook: Tannay's side-eye (IMG_5375) 'WHO FINISHED MY MOISTURISER?' -> drop on his hand raise -> 6 matched pairs
(his slides in on the beat, hers lands 2 beats later) -> 12-up grid -> Tannay pointing 'Your pick.' (his own line, IMG_5215,
Black Friday takes 23 Nov) -> end card.
Usage: python3 build_his_hers.py WORKDIR"""
import os, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

WORK = sys.argv[1].rstrip("/") + "/"; os.makedirs(WORK, exist_ok=True)
D = os.path.dirname(os.path.abspath(__file__)) + "/"; R = os.path.normpath(D + "../..") + "/"
sys.path.insert(0, R + "posts/2026-11-27-jingle-shorts"); _a = sys.argv; sys.argv = [_a[0], WORK, "santa"]
import build_jingle as J
sys.argv = _a
W, H, FPS, SR, P = J.W, J.H, J.FPS, J.SR, J.P
C2 = "/mnt/user-data/attachments/e1dc2e45-c278-5714-b377-734372e7d29a/653df6b1-IMG_5375.mov"
PICK = "/tmp/claude-0/-home-claude/e1dc2e45-c278-5714-b377-734372e7d29a/scratchpad/bfspec/f25_5215/"   # graded frames of IMG_5215
TAKES = R + "ops/transcribe/bf_takes_2026-11-23.mp3"; PICK_OFF = 15.419                                     # IMG_5215 starts here in the takes
PAIRS = [("mraqua", "missaqua", "Mr Aqua & Miss Aqua"), ("derossa", "loveair", "Dë Rossa Oudh & Love Is In The Air"),
         ("marhaba", "flora5", "Marhaba Oudh & Flora 5"), ("smuggler", "ombre", "Smuggler & Ombré"),
         ("holdmi", "misspoem", "Hold Mi & Miss Poem"), ("moksha", "bouquet", "Moksha & Bouquet")]

def fr(x): return round(x * FPS) / FPS
DROP = fr(2.85)                                   # his hand goes up
SONG0 = J.DR[0] - DROP                            # song time = t + SONG0
T0 = DROP + 4 * P; PT = [T0 + 4 * P * k for k in range(6)]
G0 = PT[-1] + 4 * P; Y0 = G0 + 4 * P             # grid, then 'Your pick.'
V0, V1 = 7.30, 8.10                               # IMG_5215: 'Your' 7.38, 'pick.' 7.60-7.86, pointing at camera
E0 = Y0 + (V1 - V0); TOTAL = fr(E0 + 2.4)

def frames(src, tag):
    fd = WORK + f"f_{tag}/"
    if not os.path.isdir(fd) or not os.listdir(fd):
        os.makedirs(fd, exist_ok=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-vf", f"fps={FPS},scale={W}:{H}", "-q:v", "2", fd + "%04d.jpg"], check=True)
    return fd, sorted(os.listdir(fd))
F2 = frames(C2, "c2"); FP = (PICK, sorted(os.listdir(PICK)))
def clip(F, t, grade=True):
    fd, fs = F; im = Image.open(fd + fs[max(0, min(int(t * FPS), len(fs) - 1))]).convert("RGB")
    if grade:
        a = np.asarray(im).astype(np.float32) / 255; a = .03 + a * .95; a = a ** np.array([.97, 1., 1.05])
        im = Image.fromarray(np.clip(a * 255, 0, 255).astype(np.uint8))
    return im.convert("RGBA")

_p = {}
def panel(name):
    """half-screen 1080x960 crop centred on the tube"""
    if name not in _p:
        im = Image.open(D + f"xmas12/{name}.png").convert("RGB"); w, h = im.size; ch = w * 960 / 1080
        y0 = 290 if h > w else 70; _p[name] = im.crop((0, y0, w, y0 + ch)).resize((W, 960), Image.LANCZOS).convert("RGBA")
    return _p[name]

def pill(im, x, y, s, f, fg=(10, 10, 10), bg=J.GOLD):
    d = ImageDraw.Draw(im); b = d.textbbox((0, 0), s, font=f); w, h = b[2] - b[0], b[3] - b[1]
    d.rounded_rectangle((x, y, x + w + 44, y + h + 30), radius=(h + 30) // 2, fill=bg + (240,)); d.text((x + 22 - b[0], y + 15 - b[1]), s, font=f, fill=fg)

def seam(im, s, a):
    lay = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(lay); f = J.BOD(60)
    d.rectangle((0, 956, W, 964), fill=J.GOLD + (255,))
    b = d.textbbox((0, 0), s, font=f); w, h = b[2] - b[0], b[3] - b[1]; sc = min(1, 960 / (w + 80))
    if sc < 1: f = J.BOD(int(60 * sc)); b = d.textbbox((0, 0), s, font=f); w, h = b[2] - b[0], b[3] - b[1]
    d.rounded_rectangle(((W - w) / 2 - 40, 960 - h / 2 - 26, (W + w) / 2 + 40, 960 + h / 2 + 26), radius=40, fill=(8, 8, 8, 235), outline=J.GOLD + (255,), width=3)
    d.text(((W - w) / 2 - b[0], 960 - h / 2 - b[1]), s, font=f, fill=J.GOLD2 + (255,))
    lay.putalpha(lay.getchannel("A").point(lambda v: int(v * a))); im.alpha_composite(lay)

def pair_frame(k, u):
    his, hers, title = PAIRS[k]; im = J.festive(k * 4 * P + u).copy()
    s1 = J.ss(u / .22); im.alpha_composite(panel(his), (int(-W * (1 - s1)), 0))
    u2 = u - 2 * P
    if u2 >= 0: s2 = J.ss(u2 / .22); im.alpha_composite(panel(hers), (int(W * (1 - s2)), 960))
    elif u > .15: J.popt(im, 1440, "and for her...", u - .15, J.BOD(84), J.GOLD2, 0)
    im.alpha_composite(J.snow(u + k * 3))
    if u >= .12: pill(im, 60, 852, "HIS", J.MS(44))
    if u2 >= .12: pill(im, 60, 996, "HERS", J.MS(44)); seam(im, title, J.ss((u2 - .12) / .2))
    if u < .3: im = J.punch(im, u * 1.3)
    elif 0 <= u2 < .3: im = J.punch(im, u2 * 1.3)
    return im

def grid(u):
    im = J.festive(0).copy(); cw, ch = (W - 24) // 3, 420
    for half, names in enumerate([[p[0] for p in PAIRS], [p[1] for p in PAIRS]]):
        for k, n in enumerate(names):
            th = Image.open(D + f"xmas12/{n}.png").convert("RGB"); s = max(cw / th.width, ch / th.height); th = th.resize((int(th.width * s) + 1, int(th.height * s) + 1), Image.LANCZOS)
            th = th.crop(((th.width - cw) // 2, (th.height - ch) // 2, (th.width - cw) // 2 + cw, (th.height - ch) // 2 + ch))
            x = 6 + (k % 3) * (cw + 6); y = (100 if half == 0 else 1030) + (k // 3) * (ch + 6)
            if J.ss((u - .05 * k - .25 * half) / .18) > 0: im.paste(th, (x, y))
    J.popt(im, 50, "FOR HIM", u, J.MS(64), J.GOLD); J.popt(im, 980, "FOR HER", u - .25, J.MS(64), J.GOLD)
    im.alpha_composite(J.snow(u))
    if u < .3: im = J.punch(im, u * 1.3)
    return im

def frame(t):
    if t < DROP + 4 * P and t < 4.84:
        im = clip(F2, t)
        if t < DROP:
            J.popt(im, 250, "WHO FINISHED", t - .1, J.MS(92)); J.popt(im, 360, "MY MOISTURISER?", t - .35, J.MS(92))
            if t > 1.5: J.popt(im, 470, "(it's always her)", t - 1.5, J.BOD(78), J.GOLD2, 0)
        else:
            if t - DROP < .4: im = J.punch(im, t - DROP)
            J.popt(im, 250, "THIS CHRISTMAS:", t - DROP, J.MS(84)); J.popt(im, 370, "HIS & HERS", t - DROP - .2, J.MS(110), J.GOLD)
            im.alpha_composite(J.snow(t))
    elif t < G0:
        k = min(5, int((t - T0) // (4 * P))); im = pair_frame(k, t - PT[k])
    elif t < Y0:
        im = grid(t - G0)
    elif t < E0:
        u = t - Y0; im = clip(FP, V0 + u, grade=False)
        if u < .3: im = J.punch(im, u * 1.3)
        sung = V0 + u >= 7.38; J.popt(im, 1480, "YOUR", u - .08, J.MS(96), J.GOLD if sung else J.IVORY)
        J.popt(im, 1600, "PICK.", u - .3, J.MS(96), J.GOLD if V0 + u >= 7.60 else J.IVORY)
    else:
        im = J.festive(t); im.alpha_composite(J.snow(t)); J.endcard(im, t - E0, "His & hers: sorted")
    J.flash(im, t - DROP, a=170)
    for x in PT + [G0, Y0]: J.flash(im, t - x, a=90, d=.1)
    if t > TOTAL - .5: im.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(255 * J.ss((t - TOTAL + .5) / .5)))))
    if t < .15: im.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(255 * (1 - t / .15)))))
    return im.convert("RGB")

def voice():
    a0, a1 = PICK_OFF + V0 - .05, PICK_OFF + V1
    af = (f"atrim={a0}:{a1},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=mono,highpass=f=75,"
          f"arnndn=m={R}assets/audio/rnnoise_bd.rnnn:mix=0.85,afftdn=nr=10:nf=-42:tn=1,"
          "equalizer=f=50:t=q:w=8:g=-18,equalizer=f=100:t=q:w=8:g=-12,equalizer=f=150:t=q:w=8:g=-8,"
          "equalizer=f=220:t=q:w=1.0:g=2,equalizer=f=3200:t=q:w=1.2:g=2.5,equalizer=f=450:t=q:w=1.2:g=-1.5,"
          "deesser=i=0.35:f=0.5,acompressor=threshold=-22dB:ratio=2.5:attack=8:release=120:makeup=1")
    out = WORK + "v_pick.wav"; subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", TAKES, "-af", af, "-ar", str(SR), out], check=True)
    with wave.open(out) as w_: return np.frombuffer(w_.readframes(w_.getnframes()), np.int16).astype(np.float32) / 32768

def build_audio(path):
    n = int(round(TOTAL * SR)); s0 = int(SONG0 * SR); m = J.SNG[s0:s0 + n].copy()
    if len(m) < n: m = np.pad(m, ((0, n - len(m)), (0, 0)))
    v = voice(); i0 = int((Y0 - .05) * SR); vv = np.zeros(n, np.float32); vv[i0:i0 + len(v)] = v[:n - i0]
    duck = np.ones(n, np.float32); a, b = int((Y0 - .12) * SR), int((E0 + .05) * SR); r = int(.08 * SR)
    duck[a:b] = 10 ** (-14 / 20); duck[a - r:a] = np.linspace(1, 10 ** (-14 / 20), r); duck[b:b + r] = np.linspace(10 ** (-14 / 20), 1, r)
    m *= duck[:, None]
    rv = np.sqrt(np.mean(v[np.abs(v) > .02] ** 2)) + 1e-9; rm = np.sqrt(np.mean(m[a:b] ** 2)) + 1e-9
    vv *= rm * 10 ** (15 / 20) / rv                                            # voice 15 dB over the ducked bed
    mix = m + vv[:, None]; fo = int(.6 * SR); mix[-fo:] *= np.linspace(1, 0, fo)[:, None]; mix *= 10 ** (-1 / 20) / np.max(np.abs(mix))
    with wave.open(path, "wb") as w_:
        w_.setnchannels(2); w_.setsampwidth(2); w_.setframerate(SR); w_.writeframes((mix * 32767).astype(np.int16).tobytes())

if __name__ == "__main__":
    only = os.environ.get("ONLY")
    if only:
        for s_ in only.split(","): frame(float(s_)).save(WORK + f"hh_{s_}.jpg", quality=85)
        print("DROP", DROP, "pairs", [round(x, 2) for x in PT], "grid", round(G0, 2), "pick", round(Y0, 2), "end", round(E0, 2), "TOTAL", TOTAL); sys.exit()
    fd = WORK + "fr_hh/"; os.makedirs(fd, exist_ok=True)
    for i in range(int(round(TOTAL * FPS))): frame(i / FPS).save(fd + f"{i:04d}.jpg", quality=93)
    build_audio(fd + "a.wav")
    base = ["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", fd + "%04d.jpg"]
    enc = ["-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p", "-r", str(FPS), "-movflags", "+faststart"]
    subprocess.run(base + ["-i", fd + "a.wav", "-map", "0:v", "-map", "1:a"] + enc + ["-c:a", "aac", "-b:a", "256k", "-shortest", D + "his_hers_reel.mp4"], check=True)
    print("done", TOTAL)

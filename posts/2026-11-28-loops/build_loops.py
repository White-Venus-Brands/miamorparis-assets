"""Seamless loop Reels (28 Nov): real Mi Amor Paris bottles (studio cutouts), each loop's last frame flows into its first.
  flip      0.8 s  Dë Rossa falls, flips, sticks the landing, gets thrown back up (gravity is symmetric, so it loops)
  cradle    0.8 s  5 bottles as a Newton's cradle: left swings out/in, click, right swings out/in, click
  giftpop   0.8 s  lid pops, Love Is In The Air rises out of the box, sinks back, lid shuts
  hat       0.8 s  Santa hat drops onto Mr Aqua's cap and bounces back up
  carousel  2.4 s  6 bottles orbit one full turn
  pause_p   0.48 s 12 Christmas perfume renders, one per frame: 'pause it, that's your scent'
  pause_m   0.48 s same with the 12 moisturisers
Audio: a slice of the Punjabi Jingle Bell drop, the exact loop length, + synthesized SFX (click, thud, pop, whoosh).
Usage: python3 build_loops.py WORKDIR [name,name...]"""
import math, os, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

WORK = sys.argv[1].rstrip("/") + "/"; ONLY = sys.argv[2].split(",") if len(sys.argv) > 2 else None
D = os.path.dirname(os.path.abspath(__file__)) + "/"; R = os.path.normpath(D + "../..") + "/"
sys.path.insert(0, R + "posts/2026-11-27-jingle-shorts"); _a = sys.argv; sys.argv = [_a[0], WORK, "santa"]
import build_jingle as J
sys.argv = _a
W, H, SR = J.W, J.H, J.SR
GOLD, GOLD2, IVORY = J.GOLD, J.GOLD2, J.IVORY
RNG = np.random.default_rng(11)

# ---------- loop-safe look ----------
_base = None
BOK = [(RNG.uniform(0, W), RNG.uniform(0, H), RNG.uniform(30, 110), RNG.uniform(.15, .45), RNG.uniform(0, 6.28), RNG.integers(1, 3)) for _ in range(26)]
def bg(t, L):
    global _base
    if _base is None: _base = J.festive(0).convert("RGB"); _base = np.asarray(J.festive(0))[..., :3].copy()
    im = Image.new("RGBA", (W, H)); yy, xx = np.mgrid[0:H, 0:W]
    r = np.sqrt(((xx - W / 2) / W) ** 2 + ((yy - H * .45) / H) ** 2); k = np.clip(1 - r * 1.6, 0, 1)[..., None]
    im = Image.fromarray((np.array([8, 22, 16]) + k * np.array([22, 58, 38])).astype(np.uint8)).convert("RGBA")
    lay = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(lay)
    for x, y, rr, a, ph, n in BOK:
        aa = a * (.6 + .4 * math.sin(2 * math.pi * n * t / L + ph)); d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=GOLD + (int(255 * aa * .35),))
    im.alpha_composite(lay.filter(ImageFilter.GaussianBlur(18))); return im
_bgc = {}
def BG(t, L):
    k = (round(t, 4), L)
    if k not in _bgc: _bgc[k] = bg(t, L)
    return _bgc[k].copy()
def snow(im, t, L):
    """cross-faded so frame L == frame 0"""
    w = t / L; a = J.snow(t); b = J.snow(t - L + 40)
    a.putalpha(a.getchannel("A").point(lambda v: int(v * (1 - w)))); b.putalpha(b.getchannel("A").point(lambda v: int(v * w)))
    im.alpha_composite(a); im.alpha_composite(b)
def cut(name, h):
    im = Image.open(R + f"assets/cutouts/{name}.png").convert("RGBA"); return im.resize((int(im.width * h / im.height), h), Image.LANCZOS)
def podium(im, cx, y, w=560):
    d = ImageDraw.Draw(im); h = w * .22
    d.rectangle((cx - w / 2, y, cx + w / 2, y + 90), fill=(214, 208, 200, 255)); d.ellipse((cx - w / 2, y + 90 - h / 2, cx + w / 2, y + 90 + h / 2), fill=(196, 188, 178, 255))
    d.ellipse((cx - w / 2, y - h / 2, cx + w / 2, y + h / 2), fill=(236, 232, 226, 255), outline=GOLD + (255,), width=6)
def shadow(im, cx, y, w, a):
    lay = Image.new("RGBA", (W, H)); ImageDraw.Draw(lay).ellipse((cx - w / 2, y - w * .09, cx + w / 2, y + w * .09), fill=(0, 0, 0, int(150 * a)))
    im.alpha_composite(lay.filter(ImageFilter.GaussianBlur(12)))
def title(im, l1, l2=None, y=240):
    J.text(im, y, l1, J.MS(78), IVORY, stroke=0)
    if l2: J.text(im, y + 105, l2, J.BOD(66), GOLD2)
def sparkles(im, cx, cy, rad, a, t, L, n=14):
    lay = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(lay)
    for i in range(n):
        ang = i / n * 6.283 + 2 * math.pi * t / L; r = rad * (.8 + .3 * math.sin(i * 2.1)); x, y = cx + r * math.cos(ang), cy + r * math.sin(ang) * .8
        s = 6 + 8 * abs(math.sin(i + 2 * math.pi * 2 * t / L)); d.polygon([(x, y - s * 2), (x + s * .4, y), (x, y + s * 2), (x - s * .4, y)], fill=GOLD2 + (int(255 * a),))
        d.polygon([(x - s * 2, y), (x, y - s * .4), (x + s * 2, y), (x, y + s * .4)], fill=GOLD2 + (int(255 * a),))
    im.alpha_composite(lay)

# ---------- loops ----------
def flip(t, L):
    im = BG(t, L); y0 = 1400; podium(im, 540, y0); title(im, "STUCK THE LANDING", "Dë Rossa Oudh", y=1660)
    s = abs(2 * t / L - 1); h = 1250 * (1 - (1 - s) ** 2); ang = -360 * (t / L) + 180
    b = cut("derossa", 560); sq = max(0, 1 - abs(t - L / 2) / .05)
    b = b.resize((int(b.width * (1 + .07 * sq)), int(b.height * (1 - .08 * sq))), Image.LANCZOS)
    shadow(im, 540, y0, 300 * (1 - .6 * min(1, h / 900)), 1 - .7 * min(1, h / 900))
    J.put(im, b, 540, y0 - h - b.height / 2 + 10, ang=ang, shadow=False); snow(im, t, L); return im
def cradle(t, L):
    im = BG(t, L); title(im, "CLICK. CLACK.", "Christmas, on loop")
    names = ["mraqua_perf", "flora5_perf", "liita", "moksha", "derossa"]; bs = [cut(n, 280) for n in names]
    ws = [b.width * .8 for b in bs]; x0 = 540 - sum(ws) / 2; py, Ls, A = 720, 400, math.radians(20)
    d = ImageDraw.Draw(im); d.rounded_rectangle((x0 - 30, py - 22, x0 + sum(ws) + 30, py + 4), radius=12, fill=GOLD + (255,))
    for i, b in enumerate(bs):
        px = x0 + sum(ws[:i]) + ws[i] / 2; th = 0
        if i == 0 and t < L / 2: th = -A * math.sin(math.pi * t / (L / 2))
        if i == 4 and t >= L / 2: th = A * math.sin(math.pi * (t - L / 2) / (L / 2))
        tx, ty = px + Ls * math.sin(th), py + Ls * math.cos(th)
        d.line((px, py, tx, ty), fill=GOLD2 + (255,), width=4)
        cx, cy = tx + b.height / 2 * math.sin(th), ty + b.height / 2 * math.cos(th)
        J.put(im, b, cx, cy, ang=math.degrees(th), shadow=False)
    snow(im, t, L); return im
def lerp(a, b, x): return a + (b - a) * x
def giftpop(t, L):
    im = BG(t, L); title(im, "UNWRAP. REPEAT.", "Love Is In The Air")
    u = t / L; lift = J.ss(u / .18) * (1 - J.ss((u - .78) / .2)); rise = J.back((u - .06) / .36) * (1 - J.ss((u - .56) / .26))
    bx0, bx1, by0, by1 = 230, 850, 1130, 1560
    b = cut("liita", 540); bt = lerp(by1 - 40, by0 - 70, rise)                    # bottle bottom y
    lay = Image.new("RGBA", (W, H)); lay.alpha_composite(b, (540 - b.width // 2, int(bt - b.height)))
    mask = Image.new("L", (W, H), 0); ImageDraw.Draw(mask).rectangle((0, 0, W, by0 + 20), fill=255); lay.putalpha(Image.fromarray(np.minimum(np.asarray(lay.getchannel("A")), np.asarray(mask))))
    d = ImageDraw.Draw(im); d.rectangle((bx0 + 10, by0 - 12, bx1 - 10, by0 + 30), fill=(4, 4, 4, 255))   # box opening
    im.alpha_composite(lay)
    d = ImageDraw.Draw(im); d.rectangle((bx0, by0, bx1, by1), fill=(14, 14, 14, 255)); d.rectangle((520, by0, 560, by1), fill=GOLD + (255,)); d.rectangle((bx0, 1320, bx1, 1360), fill=GOLD + (255,))
    lid = Image.new("RGBA", (700, 330)); ld = ImageDraw.Draw(lid); ld.rectangle((10, 200, 690, 320), fill=(20, 20, 20, 255)); ld.rectangle((330, 200, 370, 320), fill=GOLD + (255,))
    ld.ellipse((240, 90, 350, 210), outline=GOLD + (255,), width=26); ld.ellipse((350, 90, 460, 210), outline=GOLD + (255,), width=26)
    lid = lid.rotate(14 * lift, resample=Image.BICUBIC, center=(350, 320)); im.alpha_composite(lid, (540 - 350, int(by0 - 320 + 8 - 420 * lift)))
    if rise > .3: sparkles(im, 540, bt - 270, 330, min(1, (rise - .3) / .4), t, L)
    shadow(im, 540, by1 + 6, 700, .9); snow(im, t, L); return im
def hat(t, L):
    im = BG(t, L); title(im, "HATS OFF", "to Mr Aqua"); y0 = 1520; podium(im, 540, y0)
    b = cut("mraqua_perf", 820); a = np.asarray(b.getchannel("A")); top = np.where(a.max(1) > 40)[0].min()
    sq = max(0, 1 - abs(t - L / 2) / .06); bb = b.resize((b.width, int(b.height * (1 - .03 * sq))), Image.LANCZOS)
    shadow(im, 540, y0, 330, 1); im.alpha_composite(bb, (540 - bb.width // 2, y0 + 10 - bb.height))
    captop = y0 + 10 - bb.height + top * bb.height / b.height
    hw = 230; hi, (hx, hy) = J.make_hat(hw); s = abs(2 * t / L - 1); h = 650 * (1 - (1 - s) ** 2)
    hi = hi.resize((hi.width, int(hi.height * (1 - .1 * sq))), Image.LANCZOS); hy *= (1 - .1 * sq)
    hi = hi.rotate(-8 + 25 * (t / L - .5) * 2 * s, resample=Image.BICUBIC, center=(hx, hy), expand=False)
    im.alpha_composite(hi, (int(540 - hx), int(captop + hw * .16 - hy - h))); snow(im, t, L); return im
CAR = ["mraqua_perf", "derossa", "liita", "flora5_perf", "moksha", "missaqua_perf"]
def carousel(t, L):
    im = BG(t, L); title(im, "SIX SCENTS", "one Christmas"); podium(im, 540, 1480, 900)
    items = []
    for i, n in enumerate(CAR):
        th = 2 * math.pi * (i / 6 + t / L); z = math.cos(th); x = 540 + 360 * math.sin(th); y = 1480 - 40 * z
        items.append((z, n, x, y))
    for z, n, x, y in sorted(items):
        sc = .72 + .28 * (z + 1) / 2; b = cut(n, int(660 * sc))
        if z < .3: b = Image.blend(Image.new("RGBA", b.size, (8, 20, 14, 0)), b, 1)  # keep alpha
        dim = .55 + .45 * (z + 1) / 2; arr = np.asarray(b).astype(np.float32); arr[..., :3] *= dim; b = Image.fromarray(arr.astype(np.uint8))
        im.alpha_composite(b, (int(x - b.width / 2), int(y - b.height + 30)))
    snow(im, t, L); return im
def pause_set(names, folder, label):
    cards = []
    for n in names:
        src = Image.open(folder + n + ".png").convert("RGB"); fg = src.resize((W, int(src.height * W / src.width)), Image.LANCZOS)
        bgi = src.resize((int(src.width * H / src.height), H), Image.LANCZOS); bgi = bgi.crop(((bgi.width - W) // 2, 0, (bgi.width - W) // 2 + W, H)).filter(ImageFilter.GaussianBlur(40))
        bgi = Image.blend(bgi, Image.new("RGB", (W, H), (8, 6, 6)), .45); bgi.paste(fg, (0, (H - fg.height) // 2 + 60)); im = bgi.convert("RGBA")
        J.text(im, 230, "PAUSE IT.", J.MS(110), IVORY); J.text(im, 1690, label, J.BOD(64), GOLD2); cards.append(im)
    return lambda t, L: cards[min(len(cards) - 1, int(round(t * 25)))].copy()
PP = ["flora5", "derossa", "liita", "moksha", "misspoem", "mraqua", "bouquet", "marhaba", "missaqua", "smuggler", "holdmi", "ombre"]
PM = ["marhaba", "flora5", "mraqua", "misspoem", "derossa", "loveair", "smuggler", "bouquet", "holdmi", "missaqua", "moksha", "ombre"]

# ---------- audio ----------
def click(): L = int(.05 * SR); x = np.arange(L) / SR; return (np.sin(2 * np.pi * 2400 * x) * .6 + np.sin(2 * np.pi * 3700 * x) * .4) * np.exp(-x * 120)
def thud(): L = int(.18 * SR); x = np.arange(L) / SR; return np.sin(2 * np.pi * (90 + 60 * np.exp(-x * 30)) * x) * np.exp(-x * 22)
def pop(): L = int(.12 * SR); x = np.arange(L) / SR; return np.sin(2 * np.pi * (700 - 3000 * x) * x) * np.exp(-x * 35)
def whoosh(d=.25):
    L = int(d * SR); x = np.arange(L) / SR; n = RNG.standard_normal(L).astype(np.float32); y = np.zeros(L); a = 0
    for i in range(L): c = .02 + .25 * math.sin(math.pi * i / L); a = c * n[i] + (1 - c) * a; y[i] = a
    return y * np.sin(np.pi * x / d) * 2.5
SFX = {"flip": [(.4, thud, .9), (.08, whoosh, .35), (.55, whoosh, .35)], "cradle": [(0, click, .7), (.4, click, .7)],
       "giftpop": [(.02, pop, .8), (.5, whoosh, .3)], "hat": [(.4, thud, .45)], "carousel": [], "pause_p": [], "pause_m": []}
def audio(name, L, path):
    n = int(round(L * SR)); s0 = int((J.DR[0] - .02) * SR); a = J.SNG[s0:s0 + n].copy(); f = int(.004 * SR)
    a[:f] *= np.linspace(0, 1, f)[:, None]; a[-f:] *= np.linspace(1, 0, f)[:, None]; rm = np.sqrt(np.mean(a ** 2))
    for t0, fn, g in SFX[name]:
        s = fn(); i = int(t0 * SR); m = min(len(s), n - i); a[i:i + m] += (s[:m] / (np.max(np.abs(s)) + 1e-9) * rm * 3 * g)[:, None]
        if len(s) > m: a[:len(s) - m] += (s[m:] / (np.max(np.abs(s)) + 1e-9) * rm * 3 * g)[:, None]   # wrap the tail to the loop start
    a *= 10 ** (-1 / 20) / np.max(np.abs(a))
    with wave.open(path, "wb") as w_: w_.setnchannels(2); w_.setsampwidth(2); w_.setframerate(SR); w_.writeframes((a * 32767).astype(np.int16).tobytes())

JOBS = {"flip": (flip, .8, 50), "cradle": (cradle, .8, 50), "giftpop": (giftpop, .8, 50), "hat": (hat, .8, 50), "carousel": (carousel, 2.4, 50)}
if __name__ == "__main__":
    test = os.environ.get("TEST")
    if not ONLY or "pause_p" in ONLY or "pause_m" in ONLY:
        JOBS["pause_p"] = (pause_set(PP, R + "posts/2026-11-27-jingle-shorts/xmas12/", "that's your Christmas scent"), .48, 25)
        JOBS["pause_m"] = (pause_set(PM, R + "posts/2026-11-28-moisturiser-xmas/xmas12/", "that's your Christmas gift"), .48, 25)
    for name, (fn, L, fps) in JOBS.items():
        if ONLY and name not in ONLY: continue
        N = int(round(L * fps))
        if test:
            c = Image.new("RGB", (5 * 216, 384))
            for j, k in enumerate(np.linspace(0, N - 1, 5).astype(int)): c.paste(fn(k / fps, L).convert("RGB").resize((216, 384)), (j * 216, 0))
            c.save(WORK + f"loop_{name}.jpg", quality=85); continue
        fd = WORK + f"fr_loop_{name}/"; os.makedirs(fd, exist_ok=True)
        for i in range(N): fn(i / fps, L).convert("RGB").save(fd + f"{i:04d}.jpg", quality=93)
        audio(name, L, fd + "a.wav")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(fps), "-i", fd + "%04d.jpg", "-i", fd + "a.wav", "-map", "0:v", "-map", "1:a",
                        "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p", "-r", str(fps), "-c:a", "aac", "-b:a", "256k",
                        "-t", f"{N / fps:.4f}", "-movflags", "+faststart", D + f"loop_{name}.mp4"], check=True)
        print("ok", name, N / fps, flush=True)

"""Reel: 'POV: Diwali party in 2 hours. You forgot the gift.'  1080x1920, 30 fps, ~17 s.
Real gift-box photos only. No prices (DM for prices). Original synthesized audio."""
import math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy.signal import lfilter

D = os.path.dirname(os.path.abspath(__file__)) + "/"
SRC = D + "../2026-11-03-gift-sets-3x3/source/"
LOGO = Image.open(D + "../../assets/cutouts/logo_gold.png").convert("RGBA")
OUT = sys.argv[1] if len(sys.argv) > 1 else "/tmp/fg_frames/"
W, H, FPS = 1080, 1920, 30
# Time warp (Tannay 3 Nov: first half too fast to read). Scenes are written in "story" time;
# real time is stretched over the hook + options so every line gets ~1 s to be read.
KN = [(0.0, 0.0), (1.5, 0.75), (2.6, 1.35), (3.4, 1.85), (4.5, 1.95), (6.1, 2.75), (7.7, 3.55), (9.0, 4.45), (9.7, 5.0)]
SHIFT = KN[-1][0] - KN[-1][1]
def ST(r):  # real -> story
    if r >= KN[-1][0]: return r - SHIFT
    for (r0, s0), (r1, s1) in zip(KN, KN[1:]):
        if r < r1: return s0 + (s1 - s0) * (r - r0) / (r1 - r0)
def RT(s):  # story -> real
    if s >= KN[-1][1]: return s + SHIFT
    for (r0, s0), (r1, s1) in zip(KN, KN[1:]):
        if s < s1: return r0 + (r1 - r0) * (s - s0) / (s1 - s0)
DUR = 17.0 + SHIFT
GOLD, IVORY, WINE, RED = (226, 186, 112), (250, 240, 226), (58, 10, 22), (235, 72, 72)

def inter(s, w="Black"): return ImageFont.truetype(f"/usr/share/fonts/opentype/inter/InterDisplay-{w}.otf", s)
def lora(s, it=True): return ImageFont.truetype("/usr/share/fonts/truetype/google-fonts/Lora-" + ("Italic-Variable" if it else "Variable") + ".ttf", s)
def pop(s, w="Bold"): return ImageFont.truetype(f"/usr/share/fonts/truetype/google-fonts/Poppins-{w}.ttf", s)
def cl(x): return max(0.0, min(1.0, x))
def ss(x): x = cl(x); return x * x * (3 - 2 * x)
def back(x):  # overshoot ease
    x = cl(x); c = 1.9; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2

# ---------- background: wine gradient + drifting gold bokeh ----------
yy = np.linspace(0, 1, H)[:, None, None]
BG = (np.array([88, 16, 34]) * (1 - yy) + np.array([30, 5, 12]) * yy) * np.ones((1, W, 1))
rng = np.random.default_rng(7)
bok = Image.new("RGBA", (W, H * 2)); bd = ImageDraw.Draw(bok)
for _ in range(70):
    x, y, r = rng.uniform(0, W), rng.uniform(0, H * 2), rng.uniform(6, 34)
    a = int(rng.uniform(25, 90)); bd.ellipse((x - r, y - r, x + r, y + r), fill=GOLD + (a,))
bok = bok.filter(ImageFilter.GaussianBlur(6))
bok = Image.alpha_composite(bok, bok.crop((0, 0, W, H * 2)))  # strengthen
BGIMG = Image.fromarray(BG.astype(np.uint8)).convert("RGBA")

def background(t, dim=1.0):
    im = BGIMG.copy(); off = int(t * 45) % H
    im.alpha_composite(bok.crop((0, H - off, W, 2 * H - off)))
    if dim < 1: im = Image.blend(Image.new("RGBA", (W, H), (0, 0, 0, 255)), im, dim)
    return im

def ctext(d, y, s, f, fill, anchor="ma"): d.text((W / 2, y), s, font=f, fill=fill, anchor=anchor)

def scaled_text_layer(lines, scale, alpha, y0):
    """lines: [(text, font, color)] centred; rendered then scaled about its centre (pop-in)."""
    lay = Image.new("RGBA", (W, 700)); d = ImageDraw.Draw(lay); y = 20
    for s, f, c in lines:
        d.text((W / 2, y), s, font=f, fill=c + (255,), anchor="ma"); y += f.size * 1.12
    bb = lay.getbbox()
    if not bb: return None, 0
    lay = lay.crop(bb)
    if scale != 1: lay = lay.resize((max(1, int(lay.width * scale)), max(1, int(lay.height * scale))), Image.LANCZOS)
    if alpha < 1: lay.putalpha(lay.getchannel("A").point(lambda v: int(v * alpha)))
    return lay, (W - lay.width) // 2

def shadowed(im, lay, x, y, blur=10, strength=0.85):
    sh = Image.new("RGBA", lay.size, (0, 0, 0, 0)); sh.putalpha(lay.getchannel("A").point(lambda v: int(v * strength)))
    pad = blur * 3; big = Image.new("RGBA", (lay.width + pad * 2, lay.height + pad * 2)); big.alpha_composite(sh, (pad, pad))
    im.alpha_composite(big.filter(ImageFilter.GaussianBlur(blur)), (x - pad, y - pad + 6)); im.alpha_composite(lay, (x, y))

# ---------- countdown pill (runs the whole video: keeps them watching) ----------
def countdown(im, t, calm=False):
    secs = 2 * 3600 - 1 - int(t * 7)          # ticks a bit faster than real time for urgency
    hh, mm, s_ = secs // 3600, secs % 3600 // 60, secs % 60
    lab = f"PARTY IN  {hh:02d}:{mm:02d}:{s_:02d}"
    f = inter(40, "Bold"); d0 = ImageDraw.Draw(im); tw = d0.textlength(lab, font=f)
    blink = (int(t * 2) % 2 == 0) and not calm
    col = (255, 255, 255) if calm else (255, 236, 236)
    fill = (40, 120, 70, 230) if calm else ((210, 40, 50, 235) if blink else (150, 22, 34, 235))
    lay = Image.new("RGBA", im.size); d = ImageDraw.Draw(lay)
    x0, x1, y0 = (W - tw) / 2 - 40, (W + tw) / 2 + 40, 230
    d.rounded_rectangle((x0, y0, x1, y0 + 78), 39, fill=fill)
    d.ellipse((x0 + 22, y0 + 31, x0 + 38, y0 + 47), fill=(255, 255, 255, 255 if blink or calm else 120))
    d.text((W / 2 + 10, y0 + 39), lab, font=f, fill=col + (255,), anchor="mm"); im.alpha_composite(lay)

# ---------- scenes ----------
OPTIONS = [("Dry fruit box no. 47", 1.95), ("Another diya set", 2.75), ("Re-gift the sone papdi", 3.55)]
BOXES = [("bouquet", "FOR HER"), ("derossa", "FOR HIM"), ("misspoem", "FOR HER"), ("holdmi", "FOR HIM"), ("flora5", "FOR HER"), ("mraqua", "FOR HIM")]
PH = {}
def card(name, size):
    k = (name, size)
    if k not in PH:
        im = Image.open(SRC + name + "_box.jpg").convert("RGB").resize((size, size), Image.LANCZOS).convert("RGBA")
        m = Image.new("L", (size, size), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, size - 1, size - 1), 34, fill=255); im.putalpha(m)
        fr = Image.new("RGBA", (size + 12, size + 12)); ImageDraw.Draw(fr).rounded_rectangle((0, 0, size + 11, size + 11), 40, fill=GOLD + (255,))
        fr.alpha_composite(im, (6, 6)); PH[k] = fr
    return PH[k]

def scene_hook(im, t):
    # 0.0–1.85: two slams
    d = ImageDraw.Draw(im)
    ctext(d, 420, "POV:", pop(54, "Bold"), GOLD + (int(255 * ss(t / 0.15)),))
    for i, (txt, t0, y) in enumerate((("DIWALI PARTY\nIN 2 HOURS.", 0.0, 540), ("YOU FORGOT\nTHE GIFT.", 0.75, 960))):
        u = t - t0
        if u < 0: continue
        sc = 1.6 - 0.6 * back(u / 0.22); al = ss(u / 0.08)
        col = IVORY if i == 0 else (255, 120, 110)
        lines = [(l, inter(128), col) for l in txt.split("\n")]
        lay, x = scaled_text_layer(lines, sc, al, y)
        if lay is None: continue
        jx = int(rng.normal(0, 9)) if 0 < u < 0.3 and i == 1 else 0
        cy = y + 130   # keep the block centred while it scales
        shadowed(im, lay, x + jx, int(cy - lay.height / 2), 12)
    if t > 1.35:
        ctext(ImageDraw.Draw(im), 1400, "( the panic is real )", lora(52), (240, 210, 170, int(255 * ss((t - 1.35) / 0.3))))

def scene_options(im, t):
    # 1.85–5.0: options get struck out
    d = ImageDraw.Draw(im)
    ctext(d, 420, "Your options:", lora(84), GOLD + (255,))
    f = inter(70, "ExtraBold")
    for i, (txt, ts) in enumerate(OPTIONS):
        y = 680 + i * 240; u = t - (ts - 0.6)
        if u < 0: continue
        al = ss(u / 0.18); dx = int((1 - ss(u / 0.25)) * 120)
        tw = d.textlength(txt, font=f); x0 = (W - tw) / 2
        d.text((x0 + dx, y), txt, font=f, fill=IVORY + (int(255 * al),))
        st = cl((t - ts) / 0.22)        # strike-through draws across
        if st > 0:
            d.line((x0 - 20, y + 48, x0 - 20 + (tw + 40) * st, y + 44), fill=RED + (255,), width=12)
        if t - ts > 0.22:
            ctext(d, y + 108, ["(it's been gifted 3 times already)", "(they have 40)", "(they WILL know)"][i], pop(44, "Bold"), (255, 175, 165, int(255 * ss((t - ts - 0.22) / 0.2))))
    if t > 4.45:
        u = t - 4.45; lay, x = scaled_text_layer([("OR...", inter(150), GOLD)], 1.4 - 0.4 * back(u / 0.25), ss(u / 0.1), 0)
        im2 = Image.new("RGBA", im.size, (20, 4, 8, int(200 * ss(u / 0.15)))); im.alpha_composite(im2)
        shadowed(im, lay, x, 860 - lay.height // 2, 14)

def scene_boxes(im, t):
    # 5.0–10.4: six real gift boxes, quick cuts with a slide-in
    u = t - 5.0; i = min(5, int(u / 0.9)); v = u - i * 0.9
    d = ImageDraw.Draw(im)
    ctext(d, 350, "Buy one perfume.", inter(78, "ExtraBold"), IVORY + (255,))
    ctext(d, 445, "Get the whole Diwali set.", lora(76), GOLD + (255,))
    size = 860; c = card(BOXES[i][0], size)
    sl = 1 - ss(v / 0.22); x = (W - c.width) // 2 + int(sl * (W * 0.9) * (1 if i % 2 else -1))
    zoom = 1 + 0.03 * cl(v / 0.9)
    cz = c.resize((int(c.width * zoom), int(c.height * zoom)), Image.BILINEAR) if zoom > 1.001 else c
    y = 590 - (cz.height - c.height) // 2; x -= (cz.width - c.width) // 2
    sh = Image.new("RGBA", (W, H)); ImageDraw.Draw(sh).rounded_rectangle((x + 20, y + 40, x + cz.width - 20, y + cz.height + 30), 40, fill=(0, 0, 0, 150))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(24))); im.alpha_composite(cz, (x, y))
    tag = BOXES[i][1]; f = inter(46, "Black"); tw = d.textlength(tag, font=f)
    lay = Image.new("RGBA", im.size); dl = ImageDraw.Draw(lay); ty = 1500
    dl.rounded_rectangle(((W - tw) / 2 - 34, ty, (W + tw) / 2 + 34, ty + 82), 41, fill=GOLD + (255,))
    dl.text((W / 2, ty + 41), tag, font=f, fill=(40, 8, 16, 255), anchor="mm"); im.alpha_composite(lay)
    ctext(d, 1630, "body wash  +  perfume  +  moisturiser", pop(36, "Medium"), (240, 220, 200, 255))

def scene_payoff(im, t):
    # 10.4–13.6: delivery payoff
    u = t - 10.4; d = ImageDraw.Draw(im)
    ctext(d, 420, "Delhi NCR delivery in", pop(58, "Medium"), (240, 225, 205, int(255 * ss(u / 0.2))))
    lay, x = scaled_text_layer([("2-3 HOURS*", inter(160), GOLD)], 1.5 - 0.5 * back((u - 0.15) / 0.25), ss((u - 0.15) / 0.1), 0)
    if lay is not None and u > 0.15: shadowed(im, lay, x, 520, 14)
    if u > 0.9:
        a = ss((u - 0.9) / 0.3)
        ctext(d, 800, "Party's in 2 hours.", lora(76), (IVORY + (int(255 * a),)))
        ctext(d, 900, "You're basically early.", lora(76), (255, 200, 140, int(255 * a)))
    if u > 1.7:
        ctext(d, 1080, "Gift sorted. Panic cancelled.", inter(56, "ExtraBold"), (140, 230, 170, int(255 * ss((u - 1.7) / 0.25))))
    ctext(d, 1700, "*During office hours", pop(32, "Medium"), (230, 210, 190, 230))

def scene_end(im, t):
    u = t - 13.6
    lg = LOGO.resize((240, int(LOGO.height * 240 / LOGO.width)), Image.LANCZOS); al = ss(u / 0.5)
    lg.putalpha(lg.getchannel("A").point(lambda v: int(v * al))); im.alpha_composite(lg, ((W - 240) // 2, 360))
    d = ImageDraw.Draw(im)
    ctext(d, 620, "THE DIWALI GIFT SETS", inter(70, "Black"), GOLD + (int(255 * ss((u - 0.2) / 0.4)),))
    ctext(d, 720, "10 scents  ·  for her & for him", pop(40, "Medium"), (240, 222, 200, int(255 * ss((u - 0.4) / 0.4))))
    a2 = ss((u - 0.8) / 0.4)
    if a2 > 0:
        f = inter(46, "Black"); lab = "DM FOR PRICES & DIWALI DEALS"; tw = d.textlength(lab, font=f)
        lay = Image.new("RGBA", im.size); dl = ImageDraw.Draw(lay); y = 900
        dl.rounded_rectangle(((W - tw) / 2 - 46, y - 50, (W + tw) / 2 + 46, y + 50), 50, fill=GOLD + (int(255 * a2),))
        dl.text((W / 2, y), lab, font=f, fill=(40, 8, 16, int(255 * a2)), anchor="mm"); im.alpha_composite(lay)
    ctext(d, 1010, "OR VISIT US AT LAJPAT NAGAR-II", pop(36, "Bold"), (226, 180, 110, int(255 * ss((u - 1.1) / 0.4))))
    # small row of the six real boxes
    a3 = ss((u - 1.3) / 0.5)
    if a3 > 0:
        for k, (n, _) in enumerate(BOXES):
            c = card(n, 150).copy(); c.putalpha(c.getchannel("A").point(lambda v: int(v * a3)))
            im.alpha_composite(c, (int(W / 2 - 3 * 168 + k * 168 + 6), 1200))
    ctext(d, 1700, "*Delhi NCR 2-3 hr delivery during office hours", pop(28, "Medium"), (220, 200, 180, int(200 * ss((u - 1.3) / 0.5))))

def frame(tr):
    t = ST(tr)
    if t < 1.85: im = background(tr); scene_hook(im, t)
    elif t < 5.0: im = background(tr); scene_options(im, t)
    elif t < 10.4: im = background(tr, 0.85); scene_boxes(im, t)
    elif t < 13.6: im = background(tr); scene_payoff(im, t)
    else: im = background(tr); scene_end(im, t)
    if t < 13.6: countdown(im, tr, calm=t >= 10.4)
    # quick white flash on cuts
    for tc in (1.85, 5.0, 10.4, 13.6):
        if 0 <= t - tc < 0.08: im = Image.blend(im, Image.new("RGBA", im.size, (255, 245, 230, 255)), 0.5 * (1 - (t - tc) / 0.08))
    if t < 0.3 or 0.75 <= t < 1.05:  # hook shake
        u = t if t < 0.3 else t - 0.75; m = int(14 * (1 - u / 0.3)); im = im.transform(im.size, Image.AFFINE, (1, 0, rng.integers(-m, m + 1), 0, 1, rng.integers(-m, m + 1)), fillcolor=(30, 5, 12, 255))
    return im.convert("RGB")

# ---------- audio ----------
SR = 44100
def audio(path):
    n = int(SR * DUR); out = np.zeros(n, np.float32); tt = np.arange(n) / SR
    def addr(sig, at, g=1.0):
        i = int(at * SR); j = min(n, i + len(sig)); out[i:j] += sig[: j - i] * g
    def add(sig, at, g=1.0):   # at in story time
        i = int(RT(at) * SR); j = min(n, i + len(sig)); out[i:j] += sig[: j - i] * g
    def env(L, a=0.005, r=0.2):
        x = np.arange(int(L * SR)) / SR; return np.minimum(1, x / a) * np.exp(-x / r)
    kick = lambda: np.sin(2 * np.pi * (50 + 120 * np.exp(-np.arange(int(.35 * SR)) / SR / .04)) * np.arange(int(.35 * SR)) / SR) * env(.35, .002, .12)
    hat = lambda: lfilter([1, -1], [1, -0.6], np.random.default_rng(1).normal(0, 1, int(.06 * SR))) * env(.06, .001, .015) * 0.25
    tick = lambda f=2400: np.sin(2 * np.pi * f * np.arange(int(.04 * SR)) / SR) * env(.04, .001, .008)
    beat = 60 / 128
    for k in range(int(RT(13.6) / beat)):   # driving beat until end card (real time)
        b = k * beat; addr(kick(), b, 0.8 if b > 1.2 else 0.0); addr(hat(), b + beat / 2, 1.0)
    for k in range(int(RT(10.4) * 2)):      # clock tick-tock
        addr(tick(2600 if k % 2 == 0 else 1900), k * 0.5, 0.18)
    # bass line (minor, urgent) then major at payoff
    def tone(f, L, g, a=.01, r=.3, harm=(1, .5, .25)):
        x = np.arange(int(L * SR)) / SR; s = sum(h * np.sin(2 * np.pi * f * (i + 1) * x) for i, h in enumerate(harm)); return s * env(L, a, r) * g
    seq = [55, 55, 65.4, 61.7]
    for k in range(int(RT(10.4) / (beat * 2))): addr(tone(seq[k % 4], beat * 2, 0.32, r=.25), k * beat * 2)
    for k in range(int((13.6 - 10.4) / (beat * 2)) + 1): add(tone([65.4, 73.4, 82.4, 98][k % 4], beat * 2, 0.32, r=.3), 10.4 + k * beat * 2)
    # slams
    for at in (0.0, 0.75): add(kick(), at, 1.3); add(lfilter([1], [1, -0.97], np.random.default_rng(2).normal(0, 1, int(.4 * SR))) * env(.4, .002, .1) * 0.02, at)
    # strikes (scratchy marker swipe)
    for _, ts in OPTIONS:
        nz = np.random.default_rng(3).normal(0, 1, int(.22 * SR)); sw = lfilter([1, -1], [1, -0.3], nz) * np.hanning(len(nz)) * 0.22; add(sw, ts)
        add(tone(180, .25, .25, r=.1, harm=(1, .7, .5, .3)), ts + 0.2)   # "nope" buzz
    # whooshes on cuts
    for at in (1.8, 4.4, 4.95, 10.35, 13.55):
        nz = np.random.default_rng(int(at * 10)).normal(0, 1, int(.5 * SR)); w = lfilter([1], [1, -0.92], nz) * np.hanning(len(nz)) * 0.05; addr(w, RT(at) - 0.2)
    for k in range(6): add(tick(3800), 5.0 + k * 0.9, 0.25); add(kick(), 5.0 + k * 0.9, 0.5)
    # payoff ding + end chord
    for f in (880, 1108.7, 1318.5): add(tone(f, 2.5, .09, r=.8, harm=(1, .3)), 10.55)
    for f in (130.8, 164.8, 196, 261.6, 329.6): add(tone(f, 3.4, .1, a=.3, r=1.6, harm=(1, .4, .2)), 13.6)
    for f in (1568, 2093, 2637): add(tone(f, 1.5, .05, r=.5, harm=(1,)), 14.4)
    out = np.tanh(out * 1.1) * 0.85
    fade = np.ones(n); fade[-int(0.6 * SR):] = np.linspace(1, 0, int(0.6 * SR)); out *= fade
    st = np.stack([out, np.roll(out, 90)], 1)
    import scipy.io.wavfile as wf; wf.write(path, SR, (st * 32767).astype(np.int16))

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
                        "-movflags", "+faststart", "-shortest", D + "forgot_the_gift_reel.mp4"], check=True)
        print("ok")

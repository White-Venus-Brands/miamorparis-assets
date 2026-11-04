"""Reel: 'POV: Delhi girl ki Diwali checklist'  1080x1920, 30 fps, ~19 s. Tannay 4 Nov wording.
Real product photos/cutouts only. No prices. Own SFX (IG library music added at publish)."""
import math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy.signal import lfilter

D = os.path.dirname(os.path.abspath(__file__)) + "/"
R = D + "../../"
OUT = sys.argv[1] if len(sys.argv) > 1 else "/tmp/dc_frames/"
W, H, FPS, DUR = 1080, 1920, 30, 19.0
GOLD, IVORY, TEAL = (226, 186, 112), (250, 242, 230), (14, 58, 55)
LOGO = Image.open(R + "assets/cutouts/logo_gold.png").convert("RGBA")
BOTTLE = Image.open(R + "assets/cutouts/liita.png").convert("RGBA")
BOXES = [R + "posts/2026-11-03-gift-sets-3x3/source/misspoem_box.jpg", R + "posts/2026-11-gift-boxes-for-him/source/derossa_box.jpg",
         R + "posts/2026-11-03-gift-boxes-for-her/source/liita_box.jpg", R + "posts/2026-11-gift-boxes-for-him/source/holdmi_box.jpg"]

def inter(s, w="Black"): return ImageFont.truetype(f"/usr/share/fonts/opentype/inter/InterDisplay-{w}.otf", s)
def lora(s, it=True): return ImageFont.truetype("/usr/share/fonts/truetype/google-fonts/Lora-" + ("Italic-Variable" if it else "Variable") + ".ttf", s)
def pop(s, w="Bold"): return ImageFont.truetype(f"/usr/share/fonts/truetype/google-fonts/Poppins-{w}.ttf", s)
def cl(x): return max(0.0, min(1.0, x))
def ss(x): x = cl(x); return x * x * (3 - 2 * x)
def back(x): x = cl(x); c = 1.7; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2

ITEMS = ["Diwali outfit shopping", "Card party invite", "Khan Market brunch", "Gift boxes for the family", "The scent everyone asks about"]
T0, STEP, TICK = 0.9, 1.9, 0.9          # item i appears at T0 + i*STEP, ticks TICK later
APPEAR = [T0 + i * STEP for i in range(5)]; TICKS = [a + TICK for a in APPEAR]
Q_T, A_T, END_T = 10.6, 12.2, 15.0

# ---------- background: deep teal (the gift-box colour) with drifting gold sparkles ----------
yy = np.linspace(0, 1, H)[:, None, None]
BG = Image.fromarray(((np.array([22, 74, 70]) * (1 - yy) + np.array([6, 26, 25]) * yy) * np.ones((1, W, 1))).astype(np.uint8)).convert("RGBA")
rng = np.random.default_rng(3)
SP = [(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(2, 6), rng.uniform(0, 6.28), rng.uniform(8, 30)) for _ in range(90)]
def background(t):
    im = BG.copy(); lay = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(lay)
    for x, y, r, ph, sp in SP:
        yy_ = (y - t * sp) % H; a = int(70 + 70 * math.sin(t * 2.2 + ph))
        d.ellipse((x - r, yy_ - r, x + r, yy_ + r), fill=GOLD + (max(0, a),))
    im.alpha_composite(lay.filter(ImageFilter.GaussianBlur(1.2))); return im

def shadow_paste(im, lay, x, y, blur=16, op=0.55, dy=10):
    sh = Image.new("RGBA", (lay.width + blur * 6, lay.height + blur * 6)); a = lay.getchannel("A").point(lambda v: int(v * op))
    blk = Image.new("RGBA", lay.size, (0, 0, 0, 255)); blk.putalpha(a); sh.alpha_composite(blk, (blur * 3, blur * 3))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(blur)), (x - blur * 3, y - blur * 3 + dy)); im.alpha_composite(lay, (x, y))

CARD = {}
def boxcard(p, s):
    if (p, s) not in CARD:
        c = Image.open(p).convert("RGB").resize((s, s), Image.LANCZOS).convert("RGBA")
        m = Image.new("L", (s, s), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, s - 1, s - 1), 22, fill=255); c.putalpha(m)
        f = Image.new("RGBA", (s + 8, s + 8)); ImageDraw.Draw(f).rounded_rectangle((0, 0, s + 7, s + 7), 26, fill=GOLD + (255,)); f.alpha_composite(c, (4, 4)); CARD[(p, s)] = f
    return CARD[(p, s)]

def checklist(im, t, dim=1.0):
    d = ImageDraw.Draw(im)
    # title is on screen from frame 1 (hook)
    sc = 1.25 - 0.25 * back(t / 0.3)
    lay = Image.new("RGBA", (W, 300)); dl = ImageDraw.Draw(lay)
    dl.text((W / 2, 20), "POV:", font=pop(52), fill=GOLD + (255,), anchor="ma")
    dl.text((W / 2, 92), "Delhi girl ki", font=inter(96), fill=IVORY + (255,), anchor="ma")
    dl.text((W / 2, 192), "Diwali checklist", font=lora(92), fill=GOLD + (255,), anchor="ma")
    if sc != 1: lay = lay.resize((int(W * sc), int(300 * sc)), Image.LANCZOS)
    if dim < 1: lay.putalpha(lay.getchannel("A").point(lambda v: int(v * dim)))
    shadow_paste(im, lay, (W - lay.width) // 2, 250 - (lay.height - 300) // 2, 12, 0.7)
    # ivory paper card
    ca = ss(t / 0.4) * dim
    if ca <= 0: return
    card = Image.new("RGBA", (920, 860)); dc = ImageDraw.Draw(card)
    dc.rounded_rectangle((0, 0, 919, 859), 36, fill=(252, 247, 238, int(245 * ca)))
    for i, txt in enumerate(ITEMS):
        u = t - APPEAR[i]
        if u < 0: continue
        a = ss(u / 0.25) * ca; dx = int((1 - ss(u / 0.3)) * 60); y = 60 + i * 160
        bx, by = 56 + dx, y + 8
        dc.rounded_rectangle((bx, by, bx + 76, by + 76), 16, outline=(176, 132, 60, int(255 * a)), width=6)
        f = inter(54, "ExtraBold")
        col = (40, 24, 20) if i < 4 else (120, 20, 40)
        dc.text((bx + 112, y + 46), txt if dc.textlength(txt, font=f) < 680 else txt, font=f if dc.textlength(txt, font=f) < 680 else inter(46, "ExtraBold"), fill=col + (int(255 * a),), anchor="lm")
        k = cl((t - TICKS[i]) / 0.25)
        if k > 0:   # gold check mark drawn stroke by stroke
            dc.rounded_rectangle((bx, by, bx + 76, by + 76), 16, fill=(200, 156, 80, int(255 * min(1, k * 2) * ca)))
            p1, p2, p3 = (bx + 16, by + 40), (bx + 32, by + 58), (bx + 62, by + 20)
            if k < 0.4: q = k / 0.4; dc.line([p1, (p1[0] + (p2[0] - p1[0]) * q, p1[1] + (p2[1] - p1[1]) * q)], fill=(255, 255, 255, int(255 * ca)), width=10)
            else:
                q = (k - 0.4) / 0.6; dc.line([p1, p2, (p2[0] + (p3[0] - p2[0]) * q, p2[1] + (p3[1] - p2[1]) * q)], fill=(255, 255, 255, int(255 * ca)), width=10, joint="curve")
    shadow_paste(im, card, 80, 640, 20, 0.5 * ca)

def boxes_strip(im, t, dim=1.0):
    u = t - APPEAR[3]
    if u < 0: return
    s = 210
    for k, p in enumerate(BOXES):
        v = u - k * 0.15
        if v < 0: continue
        a = ss(v / 0.3) * dim; c = boxcard(p, s).copy(); c.putalpha(c.getchannel("A").point(lambda q: int(q * a)))
        x = 60 + k * 245; y = 1550 + int((1 - back(v / 0.4)) * 120)
        shadow_paste(im, c, x, y, 12, 0.5 * a)

def bubble(im, t, t0, text, right, y, fill, fg, font):
    u = t - t0
    if u < 0: return
    d0 = ImageDraw.Draw(im); tw = d0.textlength(text, font=font); bw, bh = int(tw + 90), int(font.size * 1.9)
    b = Image.new("RGBA", (bw + 30, bh + 30)); db = ImageDraw.Draw(b)
    db.rounded_rectangle((0, 0, bw, bh), bh // 2, fill=fill + (255,))
    tail = [(bw - 60, bh - 10), (bw - 10, bh + 24), (bw - 30, bh - 30)] if right else [(60, bh - 10), (10, bh + 24), (30, bh - 30)]
    db.polygon(tail, fill=fill + (255,)); db.text((bw / 2, bh / 2), text, font=font, fill=fg + (255,), anchor="mm")
    sc = 0.6 + 0.4 * back(u / 0.3); b2 = b.resize((max(1, int(b.width * sc)), max(1, int(b.height * sc))), Image.LANCZOS)
    b2.putalpha(b2.getchannel("A").point(lambda v: int(v * ss(u / 0.12))))
    x = (W - 70 - b2.width) if right else 70
    shadow_paste(im, b2, int(x), int(y + (b.height - b2.height) / 2), 14, 0.45)

def payoff(im, t):
    dim = 1 - ss((t - Q_T) / 0.4) * 0.93
    checklist(im, t, dim); boxes_strip(im, t, dim)
    bubble(im, t, Q_T, "Wait, what are you wearing?", False, 760, (236, 232, 226), (30, 30, 30), pop(46, "SemiBold") if os.path.exists("/usr/share/fonts/truetype/google-fonts/Poppins-SemiBold.ttf") else pop(46, "Medium"))
    bubble(im, t, A_T, "Mi Amor Paris ✨" if False else "Mi Amor Paris.", True, 920, GOLD, (36, 10, 16), inter(58, "Black"))
    u = t - (A_T + 0.2)
    if u > 0:   # real bottle rises in, whole and uncropped
        h = 620; b = BOTTLE.resize((int(BOTTLE.width * h / BOTTLE.height), h), Image.LANCZOS)
        a = ss(u / 0.4); b.putalpha(b.getchannel("A").point(lambda v: int(v * a)))
        glow = Image.new("RGBA", (W, H)); ImageDraw.Draw(glow).ellipse((W / 2 - 330, 1150, W / 2 + 330, 1800), fill=(255, 196, 120, int(70 * a)))
        im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(60)))
        y = 1160 + int((1 - back(u / 0.6)) * 260); shadow_paste(im, b, (W - b.width) // 2, y, 22, 0.6, 24)

def txt(im, xy, s_, font, fill):
    lay = Image.new("RGBA", im.size); ImageDraw.Draw(lay).text(xy, s_, font=font, fill=fill, anchor="ma"); im.alpha_composite(lay)

def endcard(im, t):
    u = t - END_T; d = ImageDraw.Draw(im)
    lg = LOGO.resize((230, int(LOGO.height * 230 / LOGO.width)), Image.LANCZOS); lg.putalpha(lg.getchannel("A").point(lambda v: int(v * ss(u / 0.4))))
    im.alpha_composite(lg, ((W - 230) // 2, 300))
    txt(im, (W / 2, 520), "Love Is In The Air", lora(76), GOLD + (int(255 * ss((u - 0.2) / 0.4)),))
    txt(im, (W / 2, 625), "fruity  ·  floral  ·  citrus", pop(38, "Medium"), (236, 226, 210, int(255 * ss((u - 0.4) / 0.4))))
    h = 560; b = BOTTLE.resize((int(BOTTLE.width * h / BOTTLE.height), h), Image.LANCZOS); b.putalpha(b.getchannel("A").point(lambda v: int(v * ss((u - 0.1) / 0.4))))
    shadow_paste(im, b, (W - b.width) // 2, 730, 22, 0.6, 24)
    a2 = ss((u - 0.8) / 0.4)
    if a2 > 0:
        f = inter(48, "Black"); lab = "DM FOR PRICES & DIWALI DEALS"; tw = d.textlength(lab, font=f)
        lay = Image.new("RGBA", im.size); dl = ImageDraw.Draw(lay); y = 1400
        dl.rounded_rectangle(((W - tw) / 2 - 46, y - 50, (W + tw) / 2 + 46, y + 50), 50, fill=GOLD + (int(255 * a2),))
        dl.text((W / 2, y), lab, font=f, fill=(36, 10, 16, int(255 * a2)), anchor="mm"); im.alpha_composite(lay)
    txt(im, (W / 2, 1490), "OR VISIT US AT LAJPAT NAGAR-II", pop(36), (226, 190, 120, int(255 * ss((u - 1.1) / 0.4))))

def frame(t):
    im = background(t)
    if t < Q_T: checklist(im, t); boxes_strip(im, t)
    elif t < END_T: payoff(im, t)
    else: endcard(im, t)
    if 0 <= t - END_T < 0.1: im = Image.blend(im, Image.new("RGBA", im.size, (255, 246, 230, 255)), 0.45 * (1 - (t - END_T) / 0.1))
    return im.convert("RGB")

# ---------- SFX (light: the IG library track carries the music) ----------
SR = 44100
def audio(path):
    n = int(SR * DUR); out = np.zeros(n, np.float32)
    def add(sig, at, g=1.0):
        i = int(at * SR); j = min(n, i + len(sig)); out[i:j] += sig[: j - i] * g
    def env(L, a=.003, r=.2): x = np.arange(int(L * SR)) / SR; return np.minimum(1, x / a) * np.exp(-x / r)
    def tone(f, L, g, a=.005, r=.3, harm=(1, .4)):
        x = np.arange(int(L * SR)) / SR; return sum(h * np.sin(2 * np.pi * f * (i + 1) * x) for i, h in enumerate(harm)) * env(L, a, r) * g
    beat = 60 / 112
    for k in range(int(END_T / beat)):
        x = np.arange(int(.3 * SR)) / SR; add(np.sin(2 * np.pi * (48 + 90 * np.exp(-x / .05)) * x) * env(.3, .002, .1), k * beat, .5)
        add(lfilter([1, -1], [1, -.6], np.random.default_rng(k).normal(0, 1, int(.05 * SR))) * env(.05, .001, .012) * .12, k * beat + beat / 2)
    for i, tk in enumerate(TICKS):                     # pen tick + bright ding per check
        add(lfilter([1, -1], [1, -.2], np.random.default_rng(9).normal(0, 1, int(.08 * SR))) * np.hanning(int(.08 * SR)) * .25, tk)
        for f in (1318.5, 1975.5): add(tone(f * (1 + 0.06 * i), .6, .1, r=.2), tk + .08)
    for at in APPEAR:
        nz = np.random.default_rng(int(at * 10)).normal(0, 1, int(.25 * SR)); add(lfilter([1], [1, -.9], nz) * np.hanning(len(nz)) * .03, at - .05)
    add(tone(880, .25, .15, r=.08), Q_T); add(tone(1175, .25, .15, r=.08), A_T)   # message pops
    for f in (1568, 2093, 2637, 3136): add(tone(f, 1.6, .05, r=.6, harm=(1,)), A_T + .25 + (f - 1568) / 20000)
    for f in (261.6, 329.6, 392, 523.3): add(tone(f, 3.5, .07, a=.3, r=1.5, harm=(1, .3, .15)), END_T)
    out = np.tanh(out * 1.2) * .8; fade = np.ones(n); fade[-int(.6 * SR):] = np.linspace(1, 0, int(.6 * SR)); out *= fade
    import scipy.io.wavfile as wf; wf.write(path, SR, (np.stack([out, np.roll(out, 80)], 1) * 32767).astype(np.int16))

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True); only = os.environ.get("ONLY")
    ts = [float(x) for x in only.split(",")] if only else [i / FPS for i in range(int(DUR * FPS))]
    for t in ts: frame(t).save(OUT + (f"t_{t:05.2f}.jpg" if only else f"{int(round(t * FPS)):04d}.jpg"), quality=92)
    if not only:
        audio(OUT + "a.wav")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", OUT + "%04d.jpg", "-i", OUT + "a.wav", "-c:v", "libx264", "-pix_fmt", "yuv420p",
                        "-crf", "19", "-preset", "medium", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest", D + "delhi_checklist_reel.mp4"], check=True)
        print("ok")

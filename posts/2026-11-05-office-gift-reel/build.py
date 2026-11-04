"""Reel: 'Office ne kya diya?' (Diwali office gift: soan papdi -> gift yourself)  1080x1920, 30 fps, 21 s.
Stills supplied by Tannay (4 Nov) in source/, Ken Burns + Hinglish dialogue captions, real gift-box photo, end card. No prices."""
import math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy.signal import lfilter

D = os.path.dirname(os.path.abspath(__file__)) + "/"; R = D + "../../"
OUT = sys.argv[1] if len(sys.argv) > 1 else "/tmp/ak_frames/"
W, H, FPS, DUR = 1080, 1920, 30, 25.2
GOLD, IVORY, WINE, GREEN = (226, 186, 112), (250, 242, 230), (110, 18, 36), (22, 84, 52)
LOGO = Image.open(R + "assets/cutouts/logo_gold.png").convert("RGBA")
BOX = R + "posts/2026-11-03-gift-sets-3x3/source/misspoem_box.jpg"

def inter(s, w="Black"): return ImageFont.truetype(f"/usr/share/fonts/opentype/inter/InterDisplay-{w}.otf", s)
def lora(s, it=True): return ImageFont.truetype("/usr/share/fonts/truetype/google-fonts/Lora-" + ("Italic-Variable" if it else "Variable") + ".ttf", s)
def pop(s, w="Bold"): return ImageFont.truetype(f"/usr/share/fonts/truetype/google-fonts/Poppins-{w}.ttf", s)
def cl(x): return max(0.0, min(1.0, x))
def ss(x): x = cl(x); return x * x * (3 - 2 * x)
def back(x): x = cl(x); c = 1.7; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2

# (start, image, speaker, line, kenburns (z0, z1, dx, dy))
VO = 2.6   # ElevenLabs voice (Simran, Creative Claw) starts here; cuts follow its word timings
SHOTS = [
    (0.0, "01", None, None, (1.00, 1.10, 0, 0)),
    (VO + 0.00, "02", "ME", "Arre wah, Diwali gift!", (1.04, 1.12, 0, 0)),
    (VO + 2.60, "03", "ME", "...soan papdi.", (1.0, 1.10, 0, 0.02)),
    (VO + 4.50, "12", "ME", "Phir se?", (1.10, 1.02, 0, 0)),
    (VO + 5.90, "11", "ME", "Thank you, but... no thank you.", (1.02, 1.10, 0, 0)),
    (VO + 8.45, "05", "ME", "Toh is baar maine socha...", (1.0, 1.10, 0, 0)),
    (VO + 10.60, "09", "ME", "Apna Diwali gift, main khud lungi.", (1.08, 1.0, 0, 0)),
    (VO + 13.35, "06", "ME", "Miss Poem, by Mi Amor Paris.", (1.02, 1.10, 0, 0)),
    (VO + 15.90, "08", "ME", "Khud ke liye. Khud ke paise se.", (1.0, 1.08, 0, -0.02)),
    (VO + 18.30, "07", None, None, (1.0, 1.08, 0, -0.03)),
]
END_T = VO + 18.30
SRC = {}
def src(name):
    if name not in SRC:
        im = Image.open(D + "source/" + name + ".png").convert("RGB")
        s = max(W / im.width, H / im.height) * 1.16
        SRC[name] = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    return SRC[name]

def kenburns(name, u, kb):
    z0, z1, dx, dy = kb; im = src(name); z = z0 + (z1 - z0) * ss(u)
    cw, ch = W / (z * 1.0) * (im.width / (W * 1.16)) , 0
    # crop window in source pixels: base window = W*1.16/z... keep it simple: window size = (W, H) * im.width/(W*1.16) / z * 1.16
    k = im.width / (W * 1.16); ww, hh = W * 1.16 * k / (1.16 * z) * 1.0, H * 1.16 * k / (1.16 * z)
    ww, hh = W * k / z * 1.0, H * k / z
    cx = im.width / 2 + dx * im.width * ss(u); cy = im.height / 2 + dy * im.height * ss(u)
    box = (cx - ww / 2, cy - hh / 2, cx + ww / 2, cy + hh / 2)
    return im.resize((W, H), Image.BICUBIC, box=box).convert("RGBA")

def shadow_paste(im, lay, x, y, blur=14, op=0.6, dy=6):
    sh = Image.new("RGBA", (lay.width + blur * 6, lay.height + blur * 6)); blk = Image.new("RGBA", lay.size, (0, 0, 0, 255))
    blk.putalpha(lay.getchannel("A").point(lambda v: int(v * op))); sh.alpha_composite(blk, (blur * 3, blur * 3))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(blur)), (x - blur * 3, y - blur * 3 + dy)); im.alpha_composite(lay, (x, y))

def wrap(d, text, f, maxw):
    out, cur = [], ""
    for w_ in text.split():
        t = (cur + " " + w_).strip()
        if d.textlength(t, font=f) <= maxw: cur = t
        else: out.append(cur); cur = w_
    out.append(cur); return out

def caption(im, u, speaker, line):  # line shown while it is spoken
    """speaker tag + big line in a box, lower third (above IG UI)"""
    a = ss(u / 0.12); sc = 0.85 + 0.15 * back(u / 0.25)
    f = inter(70, "Black") if line != "__none__" else lora(70)
    tmp = ImageDraw.Draw(Image.new("RGB", (1, 1))); lines = wrap(tmp, line, f, 880)
    lh = int(f.size * 1.18); bw = int(max(tmp.textlength(l, font=f) for l in lines)) + 80; bh = lh * len(lines) + 56
    tagh = 64 if speaker in ("AUNTY", "HER") else 0
    lay = Image.new("RGBA", (bw, bh + tagh)); d = ImageDraw.Draw(lay)
    if speaker in ("AUNTY", "HER"):
        tf = inter(36, "Black"); tw = d.textlength(speaker, font=tf)
        d.rounded_rectangle((0, 0, tw + 44, 56), 28, fill=(GREEN if speaker == "AUNTY" else WINE) + (255,))
        d.text((22, 28), speaker, font=tf, fill=IVORY + (255,), anchor="lm")
    fill = GOLD + (245,) if speaker in ("HER", "ME") else (255, 252, 246, 240)
    d.rounded_rectangle((0, tagh, bw - 1, tagh + bh - 1), 30, fill=fill)
    for i, l in enumerate(lines): d.text((bw / 2, tagh + 28 + i * lh + lh / 2), l, font=f, fill=(28, 14, 14, 255), anchor="mm")
    if sc != 1: lay = lay.resize((max(1, int(lay.width * sc)), max(1, int(lay.height * sc))), Image.LANCZOS)
    lay.putalpha(lay.getchannel("A").point(lambda v: int(v * a)))
    shadow_paste(im, lay, (W - lay.width) // 2, 1240 + int((1 - sc) * 60))

def hook(im, t):
    a = 1.0 if t < 0.05 else 1.0
    lay = Image.new("RGBA", (W, 360)); d = ImageDraw.Draw(lay)
    d.text((W / 2, 20), "POV:", font=pop(54), fill=GOLD + (255,), anchor="ma")
    d.text((W / 2, 96), "Some offices gave", font=inter(96), fill=IVORY + (255,), anchor="ma")
    d.text((W / 2, 210), "iPhones this Diwali.", font=lora(90), fill=GOLD + (255,), anchor="ma")
    top = Image.new("RGBA", (W, 640)); top.putalpha(Image.linear_gradient("L").rotate(180).resize((W, 640)).point(lambda v: int(v * 0.75)))
    im.alpha_composite(Image.composite(Image.new("RGBA", (W, 640), (8, 2, 4, 255)), Image.new("RGBA", (W, 640)), top.getchannel("A")))
    shadow_paste(im, lay, 0, 170, 12, 0.8)
    if t > 0.9:
        caption(im, t - 0.9, None, "Meri office ne diya...")

def endcard(im, t):
    u = t - END_T
    g = Image.new("RGBA", (W, H)); g.putalpha(Image.linear_gradient("L").resize((W, H)).point(lambda v: int(min(255, v * 1.15) * 0.9 * ss(u / 0.6))))
    im.alpha_composite(Image.composite(Image.new("RGBA", (W, H), (20, 4, 8, 255)), Image.new("RGBA", (W, H)), g.getchannel("A")))
    def txt(xy, s_, f, col, al):
        lay = Image.new("RGBA", im.size); ImageDraw.Draw(lay).text(xy, s_, font=f, fill=col + (int(255 * al),), anchor="ma"); im.alpha_composite(lay)
    txt((W / 2, 1000), "Aapko kya mila?", inter(92), IVORY, ss((u - 0.3) / 0.4))
    txt((W / 2, 1110), "Comment karo.", lora(88), GOLD, ss((u - 0.7) / 0.4))
    lg = LOGO.resize((200, int(LOGO.height * 200 / LOGO.width)), Image.LANCZOS); lg.putalpha(lg.getchannel("A").point(lambda v: int(v * ss((u - 1.1) / 0.4))))
    im.alpha_composite(lg, ((W - 200) // 2, 1250))
    a2 = ss((u - 1.5) / 0.4)
    if a2 > 0:
        f = inter(46, "Black"); lab = "DM FOR PRICES & DIWALI DEALS"; tw = ImageDraw.Draw(im).textlength(lab, font=f)
        lay = Image.new("RGBA", im.size); dl = ImageDraw.Draw(lay); y = 1470
        dl.rounded_rectangle(((W - tw) / 2 - 44, y - 48, (W + tw) / 2 + 44, y + 48), 48, fill=GOLD + (int(255 * a2),))
        dl.text((W / 2, y), lab, font=f, fill=(36, 10, 16, int(255 * a2)), anchor="mm"); im.alpha_composite(lay)
    txt((W / 2, 1555), "OR VISIT US AT LAJPAT NAGAR-II", pop(34), (232, 196, 130), ss((u - 1.8) / 0.4))

def giftcard(im, u):
    s = 380; c = Image.open(BOX).convert("RGB").resize((s, s), Image.LANCZOS).convert("RGBA")
    m = Image.new("L", (s, s), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, s - 1, s - 1), 26, fill=255); c.putalpha(m)
    f = Image.new("RGBA", (s + 10, s + 70)); df = ImageDraw.Draw(f); df.rounded_rectangle((0, 0, s + 9, s + 69), 30, fill=GOLD + (255,)); f.alpha_composite(c, (5, 5))
    df.text(((s + 10) / 2, s + 36), "Miss Poem Diwali set", font=pop(30), fill=(36, 10, 16, 255), anchor="mm")
    sc = 0.5 + 0.5 * back(u / 0.35); f = f.resize((int(f.width * sc), int(f.height * sc)), Image.LANCZOS)
    f.putalpha(f.getchannel("A").point(lambda v: int(v * ss(u / 0.15)))); f = f.rotate(-4, expand=True, resample=Image.BICUBIC)
    shadow_paste(im, f, W - f.width - 50, 560, 18, 0.6)

def frame(t):
    i = max(k for k, s in enumerate(SHOTS) if s[0] <= t)
    t0, name, spk, line, kb = SHOTS[i]; t1 = SHOTS[i + 1][0] if i + 1 < len(SHOTS) else DUR
    im = kenburns(name, (t - t0) / (t1 - t0), kb)
    if i == 0: hook(im, t)
    elif line and t < END_T: caption(im, t - t0 - 0.1, spk, line)
    if VO + 13.6 <= t < VO + 15.9: giftcard(im, t - (VO + 13.6))
    if t >= END_T: endcard(im, t)
    if i in (6, 8) and 0 <= t - t0 < 0.1: im = Image.blend(im, Image.new("RGBA", im.size, (255, 240, 210, 255)), 0.35 * (1 - (t - t0) / 0.1))
    return im.convert("RGB")

SR = 44100
def audio(path):
    n = int(SR * DUR); out = np.zeros(n, np.float32)
    def add(sig, at, g=1.0):
        i = int(at * SR); j = min(n, i + len(sig)); out[i:j] += sig[: j - i] * g
    def env(L, a=.003, r=.2): x = np.arange(int(L * SR)) / SR; return np.minimum(1, x / a) * np.exp(-x / r)
    def tone(f, L, g, a=.005, r=.3, harm=(1, .4)):
        x = np.arange(int(L * SR)) / SR; return sum(h * np.sin(2 * np.pi * f * (i + 1) * x) for i, h in enumerate(harm)) * env(L, a, r) * g
    for k, s in enumerate(SHOTS):
        if k: nz = np.random.default_rng(k).normal(0, 1, int(.3 * SR)); add(lfilter([1], [1, -.9], nz) * np.hanning(len(nz)) * .035, s[0] - .15)
    for f in (1568, 2093, 2637, 3136): add(tone(f, 1.4, .04, r=.5, harm=(1,)), VO + 13.5)   # Mi Amor Paris sparkle
    for f in (261.6, 329.6, 392, 523.3): add(tone(f, 4.0, .06, a=.3, r=1.6, harm=(1, .3)), END_T)
    for k, f in enumerate((233.1, 220.0, 207.7, 196.0)):   # "womp womp womp wommmp" on the soan papdi reveal
        add(tone(f, .5 if k < 3 else 1.1, .16, a=.02, r=.35 if k < 3 else .7, harm=(1, .6, .4, .2)), VO + 2.75 + k * .32)
    out = np.tanh(out * 1.2) * .8; fade = np.ones(n); fade[-int(.6 * SR):] = np.linspace(1, 0, int(.6 * SR)); out *= fade
    import scipy.io.wavfile as wf; wf.write(path, SR, (np.stack([out, np.roll(out, 80)], 1) * 32767).astype(np.int16))

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True); only = os.environ.get("ONLY")
    ts = [float(x) for x in only.split(",")] if only else [i / FPS for i in range(int(DUR * FPS))]
    for t in ts: frame(t).save(OUT + (f"t_{t:05.2f}.jpg" if only else f"{int(round(t * FPS)):04d}.jpg"), quality=92)
    if not only:
        audio(OUT + "a.wav")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", OUT + "%04d.jpg", "-i", OUT + "a.wav", "-c:v", "libx264", "-pix_fmt", "yuv420p",
                        "-crf", "19", "-preset", "medium", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest", D + "office_gift_reel.mp4"], check=True)
        print("ok")

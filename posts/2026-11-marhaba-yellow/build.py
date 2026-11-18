"""Reel: 'Someone has to keep wearing yellow' - Marhaba Oudh, moment post for the No. 7 yellow jersey retiring (17 Nov 2026).
No name, no photo, no logo of any team or player: a plain yellow jersey with a 7 is the only nod.
Real product photos only. 1080x1920, 30 fps, ~16 s.  Usage: python3 build.py OUTDIR"""
import math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

D = os.path.dirname(os.path.abspath(__file__)) + "/"
R = D + "../../"
SRC = R + "posts/2026-11-03-marhaba-edit/"
OUT = (sys.argv[1].rstrip("/") + "/") if len(sys.argv) > 1 else "/tmp/marhaba_yellow/"
os.makedirs(OUT + "f", exist_ok=True)
W, H, FPS = 1080, 1920, 30
YEL, GOLD, IVORY, NAVY = (253, 204, 22), (226, 186, 112), (250, 245, 236), (22, 30, 70)
LOGO = Image.open(R + "assets/cutouts/logo_gold.png").convert("RGBA")

def inter(s, w="Black"): return ImageFont.truetype(f"/usr/share/fonts/opentype/inter/Inter-{w}.otf", s)
def lora(s): return ImageFont.truetype("/usr/share/fonts/truetype/google-fonts/Lora-Italic-Variable.ttf", s)
def cl(x): return max(0.0, min(1.0, x))
def ss(x): x = cl(x); return x * x * (3 - 2 * x)
def back(x): x = cl(x); c = 1.7; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2
def win(t, a, b, fi=.2, fo=.2): return ss((t - a) / fi) * (1 - ss((t - (b - fo)) / fo))

def ctext(im, y, s, f, col, a, blur=10, scale=1.0):
    if a <= 0: return
    lay = Image.new("RGBA", (W + 400, 340)); ImageDraw.Draw(lay).text((lay.width / 2, 30), s, font=f, fill=col + (int(255 * a),), anchor="ma")
    bb = lay.getbbox()
    if not bb: return
    lay = lay.crop(bb)
    if scale != 1: lay = lay.resize((max(1, int(lay.width * scale)), max(1, int(lay.height * scale))), Image.LANCZOS)
    xx = (W - lay.width) // 2
    sh = Image.new("RGBA", lay.size); sh.putalpha(lay.getchannel("A").point(lambda v: int(v * .85)))
    pad = blur * 3; big = Image.new("RGBA", (lay.width + 2 * pad, lay.height + 2 * pad)); big.alpha_composite(sh, (pad, pad))
    im.alpha_composite(big.filter(ImageFilter.GaussianBlur(blur)), (xx - pad, int(y) - pad + 4)); im.alpha_composite(lay, (xx, int(y)))

# ---------- photos: blurred fill + sharp centre, slow push ----------
def prep(path):
    im = Image.open(path).convert("RGB")
    bg = im.resize((int(H * im.width / im.height) if im.width / im.height < W / H else W * 2, H), Image.LANCZOS)
    bg = im.resize((max(W, int(H * im.width / im.height)), H), Image.LANCZOS)
    bg = bg.crop(((bg.width - W) // 2, 0, (bg.width - W) // 2 + W, H)).filter(ImageFilter.GaussianBlur(40))
    bg = Image.blend(bg, Image.new("RGB", (W, H), (0, 0, 0)), .45)
    fg = im.resize((W, int(W * im.height / im.width)), Image.LANCZOS)
    return bg, fg
PH = {k: prep(SRC + v) for k, v in dict(main="perfume_main.jpg", gel="gel_B_2.jpg", cream="cream_front.jpg", mini="mini_life_1.jpg").items()}
PH["set"] = prep(R + "posts/2026-11-gift-boxes-for-him/source/marhaba_box.jpg")
def photo(key, p, cy=960, zoom=.06):
    bg, fg = PH[key]; im = bg.convert("RGBA")
    s = 1 + zoom * p; f = fg.resize((int(fg.width * s), int(fg.height * s)), Image.LANCZOS)
    im.paste(f, ((W - f.width) // 2, int(cy - f.height / 2))); return im

# ---------- the jersey (plain, no logos) ----------
def jersey(t, a_hang):
    im = Image.new("RGBA", (W, H), (10, 10, 12, 255)); d = ImageDraw.Draw(im)
    spot = Image.new("RGBA", (W, H)); ImageDraw.Draw(spot).ellipse((90, 380, W - 90, 1620), fill=(255, 220, 120, 60)); im.alpha_composite(spot.filter(ImageFilter.GaussianBlur(120)))
    sway = 2.2 * math.sin(t * 1.3)
    j = Image.new("RGBA", (900, 1000)); dj = ImageDraw.Draw(j)
    body = [(250, 120), (360, 80), (450, 120), (540, 80), (650, 120), (860, 260), (770, 420), (690, 360), (690, 960), (210, 960), (210, 360), (130, 420), (40, 260)]
    dj.polygon(body, fill=YEL + (255,))
    dj.polygon([(360, 80), (450, 170), (540, 80), (515, 76), (450, 130), (385, 76)], fill=NAVY + (255,))       # collar
    for x0 in (210, 690): dj.line([(x0, 360), (x0, 960)], fill=(220, 172, 10, 255), width=6)
    dj.line([(40, 260), (130, 420)], fill=NAVY + (255,), width=16); dj.line([(860, 260), (770, 420)], fill=NAVY + (255,), width=16)  # cuffs
    dj.text((450, 600), "7", font=inter(430), fill=NAVY + (255,), anchor="mm")
    shade = Image.new("L", j.size, 0); ImageDraw.Draw(shade).rectangle((0, 700, 900, 1000), fill=70)
    j = Image.composite(Image.new("RGBA", j.size, (0, 0, 0, 255)), j, Image.composite(shade.filter(ImageFilter.GaussianBlur(120)), Image.new("L", j.size, 0), j.getchannel("A")))
    d.line([(W // 2, 380), (W // 2, 520)], fill=(150, 150, 150, 255), width=4)   # hanger wire
    d.arc((W // 2 - 180, 470, W // 2 + 180, 680), 200, 340, fill=(170, 170, 170, 255), width=10)
    jr = j.rotate(sway, resample=Image.BICUBIC, center=(450, 80))
    a = jr.getchannel("A").point(lambda v: int(v * a_hang)); jr.putalpha(a)
    im.alpha_composite(jr, ((W - 900) // 2, 500)); return im

T1, T2, T3, T4, T5, END = 3.3, 6.3, 9.4, 12.0, 14.4, 17.0
def frame(t):
    if t < T2:
        im = jersey(t, 1.0 if t < T1 else 1 - .55 * ss((t - T1) / 1.2))
        ctext(im, 170, "The most famous", inter(78), IVORY, win(t, .3, T1, .2))
        ctext(im, 265, "yellow jersey", inter(96), YEL, win(t, .5, T1, .2), scale=1 + .15 * (1 - back((t - .5) / .35)))
        ctext(im, 1610, "just retired.", inter(96), IVORY, win(t, 1.3, T1, .2), scale=1 + .15 * (1 - back((t - 1.3) / .35)))
        ctext(im, 200, "Someone has to keep", inter(80), IVORY, win(t, T1 + .2, T2, .2, .15))
        ctext(im, 300, "wearing yellow.", inter(96), YEL, win(t, T1 + .5, T2, .2, .15), scale=1 + .15 * (1 - back((t - T1 - .5) / .35)))
        if t > T2 - .25:   # flash to white
            im.alpha_composite(Image.new("RGBA", (W, H), (255, 250, 230, int(255 * ss((t - T2 + .25) / .25)))))
        return im
    if t < T3:
        p = (t - T2) / (T3 - T2); im = photo("main", p, 1000)
        if t < T2 + .3: im.alpha_composite(Image.new("RGBA", (W, H), (255, 250, 230, int(255 * (1 - ss((t - T2) / .3))))))
        ctext(im, 230, "Reporting for duty.", inter(84), IVORY, win(t, T2 + .3, T3, .2, .15))
        ctext(im, 1560, "Marhaba Oudh", lora(92), YEL, win(t, T2 + .8, T3, .25, .15))
        return im
    if t < T4:   # quick routine cuts
        seg = [("gel", "Wash."), ("cream", "Layer."), ("set", "Gift.")]
        k = min(2, int((t - T3) / ((T4 - T3) / 3))); t0 = T3 + k * (T4 - T3) / 3
        im = photo(seg[k][0], (t - t0) / ((T4 - T3) / 3), 980, .08)
        ctext(im, 1540, seg[k][1], inter(120), YEL, 1, scale=1 + .3 * (1 - back((t - t0) / .25)))
        return im
    if t < T5:
        im = photo("mini", (t - T4) / (T5 - T4), 960)
        ctext(im, 200, "Seven sprays.", inter(96), YEL, win(t, T4 + .15, T5, .2, .15), scale=1 + .2 * (1 - back((t - T4 - .15) / .3)))
        ctext(im, 320, "For old times' sake.", lora(76), IVORY, win(t, T4 + .7, T5, .2, .15))
        return im
    im = Image.new("RGBA", (W, H), (10, 10, 12, 255))
    spot = Image.new("RGBA", (W, H)); ImageDraw.Draw(spot).ellipse((140, 520, W - 140, 1400), fill=(253, 204, 22, 50)); im.alpha_composite(spot.filter(ImageFilter.GaussianBlur(110)))
    a = ss((t - T5) / .4); lg = LOGO.resize((320, int(320 * LOGO.height / LOGO.width)), Image.LANCZOS); lg.putalpha(lg.getchannel("A").point(lambda v: int(v * a)))
    im.alpha_composite(lg, ((W - lg.width) // 2, 640))
    ctext(im, 640 + lg.height + 60, "Marhaba Oudh", lora(88), YEL, a)
    ctext(im, 640 + lg.height + 190, "Still wearing yellow.", inter(60, "Bold"), IVORY, ss((t - T5 - .5) / .4))
    ctext(im, 1500, "O-17, Lajpat Nagar-II  ·  miamorparis.in", inter(40, "Bold"), GOLD, ss((t - T5 - .9) / .4))
    return im

def audio(path):
    sr = 44100; n = int(END * sr); tt = np.arange(n) / sr; a = np.zeros(n)
    def note(f, t0, dur, v):
        i0 = int(t0 * sr); m = min(n - i0, int(dur * sr)); x = np.arange(m) / sr
        env = np.minimum(1, x / .04) * np.exp(-x / (dur * .45))
        a[i0:i0 + m] += v * env * (np.sin(2 * np.pi * f * x) + .35 * np.sin(4 * np.pi * f * x) + .12 * np.sin(6 * np.pi * f * x))
    # slow, warm pad under the jersey, then a lift
    for f, v in ((110, .10), (164.8, .07), (220, .06), (277.2, .05)):
        a[:int(T2 * sr)] += v * np.sin(2 * np.pi * f * tt[:int(T2 * sr)]) * np.minimum(1, tt[:int(T2 * sr)] / 1.2)
    a[int((T2 - .6) * sr):int(T2 * sr)] *= np.linspace(1, .2, int(.6 * sr))
    rng = np.random.default_rng(1); sw = int(.6 * sr); i = int((T2 - .6) * sr)
    a[i:i + sw] += .18 * rng.standard_normal(sw) * np.linspace(0, 1, sw) ** 2            # whoosh into the reveal
    beat = .5
    t = T2
    while t < END - .3:
        note(55, t, .35, .55)                                                             # kick-ish
        for k, f in enumerate((440, 554.4, 659.3)): note(f, t + .25, .3, .05)
        t += beat
    for k, t0 in enumerate((T3, T3 + (T4 - T3) / 3, T3 + 2 * (T4 - T3) / 3)): note(880, t0, .25, .12)
    for k, f in enumerate((440, 554.4, 659.3, 880)): note(f, T5 + k * .12, 1.6, .12)
    a *= np.minimum(1, (END - tt) / .8)
    a = np.tanh(a * 1.4) * .8
    import wave
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((a * 32767).astype(np.int16).tobytes())

if __name__ == "__main__":
    only = os.environ.get("ONLY")
    if only:
        for s in only.split(","): frame(float(s)).convert("RGB").save(OUT + f"still_{s}.jpg", quality=85)
        sys.exit()
    N = int(END * FPS)
    for i in range(N): frame(i / FPS).convert("RGB").save(OUT + f"f/{i:04d}.jpg", quality=92)
    audio(OUT + "a.wav")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", OUT + "f/%04d.jpg", "-i", OUT + "a.wav",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "veryfast", "-c:a", "aac", "-b:a", "192k", "-shortest",
                    "-movflags", "+faststart", D + "marhaba_yellow_reel.mp4"], check=True)
    frame(2.4).convert("RGB").save(D + "cover.jpg", quality=92)
    print("done")

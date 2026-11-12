"""Reel: 'Another week, another CEO scandal. Meanwhile, my only affair...'
Riffs on the week's CEO-affair news WITHOUT naming any person or company. The joke is on the viewer's own
'relationship' with perfume. Reuses Tannay's AI product stills (-> isAiGenerated true). 1080x1920, 30 fps, ~21 s.
Usage: python3 build.py WORKDIR   (ONLY=1,9 for stills)"""
import math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance

D = os.path.dirname(os.path.abspath(__file__)) + "/"
R = D + "../../"
OUT = sys.argv[1].rstrip("/") + "/" if len(sys.argv) > 1 else "/tmp/ns/"
LOGO = Image.open(R + "assets/cutouts/logo_gold.png").convert("RGBA")
W, H, FPS = 1080, 1920, 30
GOLD, IVORY, INK, RED = (226, 186, 112), (250, 245, 236), (30, 28, 34), (205, 30, 40)
POEM = R + "posts/2026-11-honey-trap-reel/src/09.png"
POEM2 = R + "posts/2026-11-honey-trap-reel/src/06.png"
LIITA = R + "posts/2026-11-wedding-storeroom-reel/src/02.png"

def inter(s, w="Black"): return ImageFont.truetype(f"/usr/share/fonts/opentype/inter/InterDisplay-{w}.otf", s)
def pop(s, w="Medium"): return ImageFont.truetype(f"/usr/share/fonts/truetype/google-fonts/Poppins-{w}.ttf", s)
def lora(s, it=False): return ImageFont.truetype("/usr/share/fonts/truetype/google-fonts/Lora-" + ("Italic-Variable" if it else "Variable") + ".ttf", s)
def tw(s): return ImageFont.truetype("/usr/share/texmf/fonts/opentype/public/lm/lmmono10-regular.otf", s)
def cl(x): return max(0.0, min(1.0, x))
def ss(x): x = cl(x); return x * x * (3 - 2 * x)
def back(x): x = cl(x); c = 1.9; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2
def win(t, a, b, fi=.25, fo=.2): return ss((t - a) / fi) * (1 - ss((t - (b - fo)) / fo))
def typed(s, t, t0, cps=34): return s[:int(max(0, t - t0) * cps)]

T_MEAN, T_FORM, T_CONF, T_SECOND, T_FINE, END = 3.0, 5.2, 10.4, 12.2, 15.0, 17.6
DUR = END + 3.8
CUTS = [T_MEAN, T_FORM, T_CONF, T_SECOND, T_FINE, END]

_img = {}
def photo(path, t, t0, t1, z0, z1, fx=.5, fy=.5):
    if path not in _img: _img[path] = Image.open(path).convert("RGB")
    im = _img[path]; u = ss((t - t0) / max(.01, t1 - t0)); z = z0 + (z1 - z0) * u
    s = max(W / im.width, H / im.height) * z; cw, ch = W / s, H / s
    x0 = min(max(fx * im.width - cw / 2, 0), im.width - cw); y0 = min(max(fy * im.height - ch / 2, 0), im.height - ch)
    return im.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch)).convert("RGBA")

def ctext(im, y, s, f, col, a, blur=10, scale=1.0, shadow=True):
    if a <= 0: return
    lay = Image.new("RGBA", (W + 400, 320)); ImageDraw.Draw(lay).text((lay.width / 2, 30), s, font=f, fill=col + (int(255 * a),), anchor="ma")
    bb = lay.getbbox()
    if not bb: return
    lay = lay.crop(bb)
    if scale != 1: lay = lay.resize((max(1, int(lay.width * scale)), max(1, int(lay.height * scale))), Image.LANCZOS)
    x = (W - lay.width) // 2
    if shadow:
        sh = Image.new("RGBA", lay.size, (0, 0, 0, 0)); sh.putalpha(lay.getchannel("A").point(lambda v: int(v * .85)))
        pad = blur * 3; big = Image.new("RGBA", (lay.width + 2 * pad, lay.height + 2 * pad)); big.alpha_composite(sh, (pad, pad))
        im.alpha_composite(big.filter(ImageFilter.GaussianBlur(blur)), (x - pad, int(y) - pad + 4))
    im.alpha_composite(lay, (x, int(y)))

def paste_shadow(im, lay, x, y, blur=24, k=.55):
    sh = Image.new("RGBA", lay.size, (0, 0, 0, 0)); sh.putalpha(lay.getchannel("A").point(lambda v: int(v * k)))
    pad = blur * 3; big = Image.new("RGBA", (lay.width + 2 * pad, lay.height + 2 * pad)); big.alpha_composite(sh, (pad, pad))
    im.alpha_composite(big.filter(ImageFilter.GaussianBlur(blur)), (int(x) - pad + 8, int(y) - pad + 18)); im.alpha_composite(lay, (int(x), int(y)))

def grad(top, bot):
    yy = np.linspace(0, 1, H)[:, None, None]
    return Image.fromarray((np.array(top) * (1 - yy) + np.array(bot) * yy * np.ones((1, W, 1))).astype(np.uint8)).convert("RGBA")
BG_NEWS = grad((12, 20, 48), (30, 46, 96))
TICK = "TECH WORLD IN SHOCK   ·   BOARD CALLS EMERGENCY MEETING   ·   INTERNET HAS OPINIONS   ·   GROUP CHATS ON FIRE   ·   "

def news(t):
    im = BG_NEWS.copy(); bars = Image.new("RGBA", im.size); db = ImageDraw.Draw(bars)
    for i in range(9):  # studio light bars
        x = (i * 190 + t * 60) % (W + 200) - 100; db.polygon([(x, 0), (x + 70, 0), (x - 160, H), (x - 230, H)], fill=(90, 130, 220, 30))
    im.alpha_composite(bars); d = ImageDraw.Draw(im)
    k = back(t / .3)
    bw = int(620 * k); d.rectangle((W / 2 - bw / 2, 430, W / 2 + bw / 2, 560), fill=RED + (255,))
    if t > .15: d.text((W / 2, 495), "BREAKING NEWS", font=inter(70), fill=(255, 255, 255, 255), anchor="mm")
    if int(t * 3) % 2 == 0: d.ellipse((90, 250, 124, 284), fill=RED + (255,))
    d.text((140, 267), "LIVE", font=inter(40, "Bold"), fill=(255, 255, 255, 255), anchor="lm")
    ctext(im, 660, "Another week,", inter(96), IVORY, win(t, .5, T_MEAN, .15))
    ctext(im, 775, "another CEO scandal.", inter(96), IVORY, win(t, .9, T_MEAN, .15))
    ctext(im, 940, "(yes, a second one)", lora(54, True), (200, 215, 245), win(t, 1.7, T_MEAN, .2))
    d = ImageDraw.Draw(im); d.rectangle((0, 1500, W, 1590), fill=(245, 245, 245, 255)); d.rectangle((0, 1500, 20, 1590), fill=RED + (255,))
    f = inter(44, "Bold"); L = d.textlength(TICK, font=f); x = -((t * 260) % L)
    while x < W: d.text((x, 1545), TICK, font=f, fill=INK + (255,), anchor="lm"); x += L
    return im

def warm(t, path=POEM, b=.3):
    key = ("w", path)
    if key not in _img: _img[key] = ImageEnhance.Brightness(photo(path, 0, 0, 1, 1, 1).filter(ImageFilter.GaussianBlur(24))).enhance(b)
    return _img[key].copy()

def form(im, t):
    u = t - T_FORM; cw, ch = 940, 1060; card = Image.new("RGBA", (cw, ch)); d = ImageDraw.Draw(card)
    d.rounded_rectangle((0, 0, cw - 1, ch - 1), 26, fill=(248, 242, 228, 255))
    d.rectangle((0, 0, cw - 1, 150), fill=(40, 34, 30, 255)); d.rounded_rectangle((0, 0, cw - 1, 60), 26, fill=(40, 34, 30, 255))
    d.text((cw / 2, 58), "RELATIONSHIP DISCLOSURE FORM", font=inter(44, "Black"), fill=GOLD + (255,), anchor="mm")
    d.text((cw / 2, 114), "(filed voluntarily, with pride)", font=lora(32, True), fill=(220, 210, 190, 255), anchor="mm")
    rows = [("NAME", "Me", .3), ("IN A RELATIONSHIP WITH", "Miss Poem", .9), ("TOGETHER SINCE", "the first spray", 1.7), ("REPORTED TO HR", "Not required", 2.6), ("STATUS", "Extremely committed", 3.5)]
    y = 215
    for k, v, t0 in rows:
        d.text((60, y), k, font=pop(30, "Bold"), fill=(140, 120, 100, 255)); d.line((60, y + 118, cw - 60, y + 118), fill=(200, 190, 170, 255), width=2)
        if u > t0: d.text((60, y + 46), typed(v, u, t0), font=tw(62), fill=RED + (255,) if k == "STATUS" else INK + (255,))
        y += 165
    card = card.rotate(1.2, expand=True, resample=Image.BICUBIC)
    s = .9 + .1 * back(u / .35); card = card.resize((int(card.width * s), int(card.height * s)), Image.LANCZOS)
    a = ss(u / .2); card.putalpha(card.getchannel("A").point(lambda v: int(v * a)))
    paste_shadow(im, card, W / 2 - card.width / 2, 400)

def stamp(im, t, t0, cx, cy, text, t_end):
    u = t - t0
    if u <= 0: return
    s = .9 + 1.2 * (1 - back(u / .18)); a = ss(u / .06) * (1 - ss((t - (t_end - .15)) / .15))
    st = Image.new("RGBA", (720, 190)); ds = ImageDraw.Draw(st)
    ds.rounded_rectangle((6, 6, 714, 184), 14, fill=(250, 246, 236, 245), outline=(40, 150, 80, 255), width=10); ds.text((360, 96), text, font=inter(78), fill=(40, 150, 80, 240), anchor="mm")
    st = st.rotate(-7, expand=True, resample=Image.BICUBIC); st = st.resize((int(st.width * s), int(st.height * s)), Image.LANCZOS)
    st.putalpha(st.getchannel("A").point(lambda v: int(v * a))); im.alpha_composite(st, (int(cx - st.width / 2), int(cy - st.height / 2)))

def pill(im, y, lab, a):
    if a <= 0: return
    f = inter(46, "Black"); w_ = ImageDraw.Draw(im).textlength(lab, font=f); lay = Image.new("RGBA", im.size); dl = ImageDraw.Draw(lay)
    dl.rounded_rectangle(((W - w_) / 2 - 50, y - 50, (W + w_) / 2 + 50, y + 50), 50, fill=GOLD + (255,)); dl.text((W / 2, y), lab, font=f, fill=(40, 8, 16, 255), anchor="mm")
    lay.putalpha(lay.getchannel("A").point(lambda v: int(v * a))); im.alpha_composite(lay)

def frame(t):
    if t < T_MEAN: im = news(t)
    elif t < T_FORM:
        im = Image.blend(news(T_MEAN - .01), photo(POEM, t, T_MEAN, T_FORM + 1, 1.0, 1.0, .5, .2), ss((t - T_MEAN) / .35))
        g = Image.new("RGBA", im.size, (0, 0, 0, 90)); im.alpha_composite(g)
        ctext(im, 250, "Meanwhile,", inter(100), IVORY, win(t, T_MEAN + .2, T_FORM, .2))
        ctext(im, 375, "my only affair:", inter(100), GOLD, win(t, T_MEAN + .7, T_FORM, .2), scale=1 + .2 * (1 - back((t - T_MEAN - .7) / .3)))
    elif t < T_CONF:
        im = warm(t); form(im, t)
    elif t < T_SECOND:
        im = Image.new("RGBA", (W, H), (8, 6, 6, 255)); u = t - T_CONF
        shake = int(8 * math.exp(-u * 4) * math.sin(u * 60))
        ctext(im, 720 + shake, "CONFESSION:", inter(70, "Black"), RED, win(t, T_CONF + .05, T_SECOND, .1), shadow=False)
        ctext(im, 850 + shake, "There is", inter(120), IVORY, win(t, T_CONF + .5, T_SECOND, .1), shadow=False)
        ctext(im, 990 + shake, "a second one.", inter(120), IVORY, win(t, T_CONF + .5, T_SECOND, .1), shadow=False)
    elif t < T_FINE:
        u = t - T_SECOND; im = photo(LIITA, t, T_SECOND, T_FINE, 1.12, 1.0, .5, .55)
        if u < .12: im = Image.blend(im, Image.new("RGBA", im.size, (255, 245, 230, 255)), .7 * (1 - u / .12))
        g = np.zeros((H, W, 4), np.uint8); g[:760, :, 3] = (np.linspace(1, 0, 760) ** 1.4 * 190).astype(np.uint8)[:, None]; im.alpha_composite(Image.fromarray(g, "RGBA"))
        ctext(im, 300, "Love Is In The Air.", inter(88), IVORY, win(t, T_SECOND + .2, T_FINE, .2))
        ctext(im, 420, "Weekends only.", lora(64, True), GOLD, win(t, T_SECOND + 1.0, T_FINE, .2))
    elif t < END:
        u = t - T_FINE; im = warm(t, POEM2, .4)
        for i, (p, x, rot) in enumerate(((POEM2, 300, -5), (LIITA, 780, 5))):
            th = photo(p, 0, 0, 1, 1, 1, .5, .55).resize((440, 782), Image.LANCZOS); m = Image.new("L", th.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, 439, 781), 30, fill=255); th.putalpha(m)
            fr = Image.new("RGBA", (452, 794)); ImageDraw.Draw(fr).rounded_rectangle((0, 0, 451, 793), 34, fill=GOLD + (255,)); fr.alpha_composite(th, (6, 6))
            k = back((u - i * .12) / .35); fr = fr.rotate(rot, expand=True, resample=Image.BICUBIC)
            paste_shadow(im, fr, x - fr.width / 2, 700 + 500 * (1 - k))
        ctext(im, 300, "They know about", inter(84), IVORY, win(t, T_FINE + .2, END, .2)); ctext(im, 405, "each other.", inter(84), IVORY, win(t, T_FINE + .2, END, .2))
        ctext(im, 1570, "Everyone's fine.", lora(66, True), GOLD, win(t, T_FINE + 1.0, END, .2))
        stamp(im, t, T_FINE + 1.5, W / 2, 1100, "NO SCANDAL", END)
    else:
        u = t - END; im = warm(t, POEM, .3)
        lg = LOGO.resize((220, int(LOGO.height * 220 / LOGO.width)), Image.LANCZOS); a = ss((u - .15) / .4)
        lg.putalpha(lg.getchannel("A").point(lambda v: int(v * a))); im.alpha_composite(lg, ((W - 220) // 2, 400))
        ctext(im, 650, "The only affair worth having:", lora(60, True), IVORY, ss((u - .35) / .4))
        ctext(im, 745, "you and your signature scent.", lora(60, True), GOLD, ss((u - .7) / .4))
        pill(im, 930, "DM FOR PRICES", ss((u - 1.1) / .4))
        ctext(im, 1030, "OR VISIT US AT LAJPAT NAGAR-II", pop(36, "Bold"), (226, 180, 110), ss((u - 1.3) / .4), 6)
    for tc in CUTS:
        v = t - tc
        if 0 <= v < .1 and tc not in (T_CONF, T_SECOND): im = im.filter(ImageFilter.BoxBlur(int(26 * (1 - v / .1)) + 1))
    if t > DUR - .5: im = Image.blend(im, Image.new("RGBA", im.size, (0, 0, 0, 255)), ss((t - DUR + .5) / .5))
    return im.convert("RGB")

SR = 44100
def audio(path):
    from scipy.signal import lfilter
    n = int(SR * DUR); out = np.zeros((n, 2), np.float32); r = np.random.default_rng(12)
    def add(sig, at, g=1.0, pan=0.0):
        i = int(at * SR); j = min(n, i + len(sig))
        if i >= n or j <= i: return
        s = sig[: j - i] * g; out[i:j, 0] += s * (1 - pan); out[i:j, 1] += s * (1 + pan)
    def env(L, a=.003, rel=.15): x = np.arange(int(L * SR)) / SR; return np.minimum(1, x / a) * np.exp(-x / rel)
    def tone(f, L, a=.01, rel=.3, h=(1, .4, .2)): x = np.arange(int(L * SR)) / SR; return sum(g * np.sin(2 * np.pi * f * (i + 1) * x) for i, g in enumerate(h)) * env(L, a, rel)
    kick = lambda: np.sin(2 * np.pi * (50 + 90 * np.exp(-np.arange(int(.3 * SR)) / SR / .04)) * np.arange(int(.3 * SR)) / SR) * env(.3, .002, .1)
    hat = lambda: lfilter([1, -1], [1, -.6], r.normal(0, 1, int(.05 * SR))) * env(.05, .001, .012)
    # news sting: brassy stabs + urgent ticking pulse
    for i, (f, at) in enumerate(((220, 0), (220, .22), (329.6, .44), (440, .8))):
        for m in (1, 1.5, 2): add(tone(f * m, .7, .005, .3, (1, .7, .5, .35)), at, .05)
    t = 1.2
    while t < T_MEAN - .1: add(tone(880, .06, .002, .02, (1,)), t, .05); add(kick(), t, .3) if int(t * 4) % 2 == 0 else None; t += .25
    sc = np.sin(2 * np.pi * np.cumsum(np.linspace(1100, 180, int(.28 * SR))) / SR) * env(.28, .002, .1); add(sc, T_MEAN - .05, .16)
    # smooth lounge groove T_MEAN -> T_CONF and T_SECOND -> end
    prog = [(261.6, 329.6, 392, 493.9), (220, 261.6, 329.6, 392), (174.6, 220, 261.6, 329.6), (196, 246.9, 293.7, 349.2)]
    beat = 60 / 104
    for a0, a1 in ((T_MEAN + .1, T_CONF - .1), (T_SECOND + .05, DUR - .5)):
        t = a0; k = 0
        while t < a1:
            add(kick(), t, .4); add(hat(), t + beat / 2, .1)
            ch = prog[(k // 4) % 4]
            if k % 4 == 0:
                for f in ch: add(tone(f, beat * 3.6, .03, 1.0, (1, .3, .1)), t, .03)
                add(tone(ch[0] / 2, beat * 3.6, .02, 1.0, (1, .5)), t, .07)
            add(tone(ch[(k * 2) % 4] * 2, .4, .005, .2, (1, .25)), t + beat / 2, .04, .3 * math.sin(k))
            t += beat; k += 1
    # typewriter for the form
    for v, t0 in (("Me", .3), ("Miss Poem", .9), ("the first spray", 1.7), ("Not required", 2.6), ("Extremely committed", 3.5)):
        for c in range(len(v)):
            ck = lfilter([1, -1], [1, -.2], r.normal(0, 1, int(.02 * SR))) * env(.02, .0005, .005); add(ck, T_FORM + t0 + c / 34, .22, r.uniform(-.2, .2))
    # confession: silence, heartbeat, DUN DUN
    add(kick(), T_CONF + .05, 1.4)
    for f in (55, 110, 164.8): add(tone(f, 1.6, .005, .7, (1, .6, .4)), T_CONF + .5, .14)
    for f in (51.9, 103.8, 155.6): add(tone(f, 1.2, .005, .6, (1, .6, .4)), T_CONF + 1.05, .14)
    # reveal sparkle, stamp
    for i, f in enumerate((1046.5, 1318.5, 1568, 2093)): add(tone(f, 1.4, .003, .5, (1,)), T_SECOND + .02 + i * .06, .05)
    add(kick(), T_FINE + 1.65, 1.8); add(lfilter([1], [1, -.9], r.normal(0, 1, int(.1 * SR))) * env(.1, .001, .025), T_FINE + 1.65, .3)
    out = np.tanh(out * 1.3)
    fd = np.ones(n); fd[-int(.8 * SR):] = np.linspace(1, 0, int(.8 * SR)); out *= fd[:, None]
    import scipy.io.wavfile as wf; wf.write(path, SR, (out / max(1e-9, np.abs(out).max()) * .89 * 32767).astype(np.int16))

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
                        "-movflags", "+faststart", "-shortest", D + "no_scandal_reel.mp4"], check=True)
        frame(2.4).save(D + "cover.jpg", quality=92)
        print("ok", DUR)

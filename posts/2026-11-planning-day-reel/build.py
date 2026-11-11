"""Reel: 'We held an internal planning day too.'  Rides the Finnish-embassy-in-Canberra 'closed for an internal
planning day' meme (10 Nov 2026). No embassy logos/flags, no claims about store hours. 1080x1920, 30 fps, ~22 s.
Product imagery reused from Tannay's wedding + honey-trap stills (AI -> isAiGenerated true).
Usage: python3 build.py WORKDIR   (ONLY=1,9 for stills)"""
import math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance

D = os.path.dirname(os.path.abspath(__file__)) + "/"
R = D + "../../"
OUT = sys.argv[1].rstrip("/") + "/" if len(sys.argv) > 1 else "/tmp/plan/"
LOGO = Image.open(R + "assets/cutouts/logo_gold.png").convert("RGBA")
W, H, FPS = 1080, 1920, 30
GOLD, IVORY, INK = (226, 186, 112), (250, 245, 236), (34, 26, 22)
BOX = R + "posts/2026-11-wedding-storeroom-reel/src/03.png"      # open Love Is In The Air gift box
BOTTLE = R + "posts/2026-11-honey-trap-reel/src/09.png"          # Miss Poem hero

def inter(s, w="Black"): return ImageFont.truetype(f"/usr/share/fonts/opentype/inter/InterDisplay-{w}.otf", s)
def pop(s, w="Medium"): return ImageFont.truetype(f"/usr/share/fonts/truetype/google-fonts/Poppins-{w}.ttf", s)
def lora(s, it=False): return ImageFont.truetype("/usr/share/fonts/truetype/google-fonts/Lora-" + ("Italic-Variable" if it else "Variable") + ".ttf", s)
def cl(x): return max(0.0, min(1.0, x))
def ss(x): x = cl(x); return x * x * (3 - 2 * x)
def back(x): x = cl(x); c = 1.9; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2

T_GOLD = 5.6          # aurora -> Mi Amor warm world
T_MIN = 8.2           # meeting minutes card
T_STAMP = 13.25       # stamp lands on the minutes
T_OUT = 14.6          # outcome: products
T_BOTTLE = 16.8
END = 19.2
DUR = END + 4.0

# ---------- aurora background (procedural, low-res then upscaled) ----------
LW, LH = 216, 384
ly, lx = np.mgrid[0:LH, 0:LW] / np.array([LH, LW])[:, None, None]
rng = np.random.default_rng(2)
STARS = [(rng.uniform(0, W), rng.uniform(0, H * .55), rng.uniform(.8, 2.4), rng.uniform(0, 6.3)) for _ in range(110)]
def aurora(t):
    sky = np.zeros((LH, LW, 3)); sky[..., 0] = 4 + 10 * ly; sky[..., 1] = 8 + 18 * ly; sky[..., 2] = 22 + 30 * ly
    for k, (base, amp, freq, sp, col, wid) in enumerate([(0.30, .06, 2.2, .25, (60, 255, 150), .07), (0.40, .05, 3.1, -.18, (40, 220, 170), .06), (0.24, .04, 1.6, .12, (150, 90, 255), .05)]):
        c = base + amp * np.sin(2 * np.pi * (freq * lx + sp * t)) + .02 * np.sin(2 * np.pi * (5 * lx - .4 * t + k))
        curtain = np.exp(-((ly - c) / wid) ** 2) + 0.8 * np.clip((ly - c) / .25, 0, 1) * np.exp(-(ly - c) / .12) * (ly > c)
        shimmer = 0.75 + 0.25 * np.sin(2 * np.pi * (14 * lx + 1.3 * t + k))
        sky += (curtain * shimmer)[..., None] * np.array(col) * 0.55
    ground = ly > 0.82; sky[ground] *= 0.15
    im = Image.fromarray(np.clip(sky, 0, 255).astype(np.uint8)).resize((W, H), Image.BICUBIC).filter(ImageFilter.GaussianBlur(6)).convert("RGBA")
    d = ImageDraw.Draw(im)
    for x, y, r, ph in STARS:
        a = int(140 + 110 * math.sin(t * 2 + ph)); d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 255, a))
    return im

# ---------- warm world ----------
def cover_img(path, z=1.0, fx=.5, fy=.5):
    im = Image.open(path).convert("RGB"); s = max(W / im.width, H / im.height) * z
    im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    x0 = int((im.width - W) * fx); y0 = int((im.height - H) * fy)
    return im.crop((x0, y0, x0 + W, y0 + H)).convert("RGBA")
_cache = {}
def warm_bg(t):
    if "boxblur" not in _cache:
        _cache["boxblur"] = ImageEnhance.Brightness(cover_img(BOX).filter(ImageFilter.GaussianBlur(24))).enhance(0.35)
    return _cache["boxblur"].copy()

def kb(path, t, t0, t1, z0, z1):
    u = ss((t - t0) / max(.01, t1 - t0)); z = z0 + (z1 - z0) * u
    key = (path,)
    if key not in _cache: _cache[key] = Image.open(path).convert("RGB")
    im = _cache[key]; s = max(W / im.width, H / im.height) * z
    cw, ch = W / s, H / s; x0 = (im.width - cw) / 2; y0 = (im.height - ch) / 2
    return im.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch)).convert("RGBA")

# ---------- text ----------
def tl(s, f, col, a=1.0, anchor="ma"):
    lay = Image.new("RGBA", (W, 300)); ImageDraw.Draw(lay).text((W / 2, 30), s, font=f, fill=col + (int(255 * a),), anchor=anchor)
    bb = lay.getbbox(); return lay.crop(bb) if bb else None
def ctext(im, y, s, f, col, a, blur=10, scale=1.0, shadow=True):
    if a <= 0: return
    lay = tl(s, f, col, a)
    if lay is None: return
    if scale != 1: lay = lay.resize((max(1, int(lay.width * scale)), max(1, int(lay.height * scale))), Image.LANCZOS)
    x = (W - lay.width) // 2
    if shadow:
        sh = Image.new("RGBA", lay.size, (0, 0, 0, 0)); sh.putalpha(lay.getchannel("A").point(lambda v: int(v * .85)))
        pad = blur * 3; big = Image.new("RGBA", (lay.width + 2 * pad, lay.height + 2 * pad)); big.alpha_composite(sh, (pad, pad))
        im.alpha_composite(big.filter(ImageFilter.GaussianBlur(blur)), (x - pad, int(y) - pad + 4))
    im.alpha_composite(lay, (x, int(y)))
def typed(s, t, t0, cps=24): n = int(max(0, t - t0) * cps); return s[:n]
def win(t, a, b, fi=.3, fo=.25): return ss((t - a) / fi) * (1 - ss((t - (b - fo)) / fo))

def notice_card(im, t, a):
    """Plain 'official notice' card like the embassy's post: centred, small caps label, calm serif."""
    if a <= 0: return
    cw, ch = 900, 760; card = Image.new("RGBA", (cw, ch), (250, 250, 248, int(238 * a))); d = ImageDraw.Draw(card)
    d.text((cw / 2, 70), "OFFICIAL NOTICE", font=inter(34, "Bold"), fill=(110, 110, 110, int(255 * a)), anchor="mm")
    d.line((cw / 2 - 60, 110, cw / 2 + 60, 110), fill=(180, 180, 180, int(255 * a)), width=2)
    body = ["The Embassy of Finland", "in Canberra was closed", "for an internal planning", "day on 10 November."]
    full = " ".join(body); shown = typed(full, t, 0.35, 52); y = 175; used = 0
    for line in body:
        seg = shown[used: used + len(line)]; used += len(line) + 1
        d.text((cw / 2, y), seg, font=lora(64), fill=(30, 30, 30, int(255 * a)), anchor="ma"); y += 92
    if t > 2.2:
        k = ss((t - 2.2) / .3)
        d.text((cw / 2, 610), "Regular hours resumed the next day.", font=pop(34), fill=(120, 120, 120, int(255 * a * k)), anchor="mm")
    sh = Image.new("RGBA", card.size, (0, 0, 0, 0)); sh.putalpha(card.getchannel("A").point(lambda v: int(v * .5)))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(30)), ((W - cw) // 2, 470)); im.alpha_composite(card, ((W - cw) // 2, 450))

def minutes_card(im, t):
    u = t - T_MIN; a = ss(u / .35) * (1 - ss((t - (T_OUT - .2)) / .2))
    if a <= 0: return
    cw, ch = 940, 1040; card = Image.new("RGBA", (cw, ch), (246, 238, 222, int(245 * a))); d = ImageDraw.Draw(card)
    lg = LOGO.resize((150, int(LOGO.height * 150 / LOGO.width)), Image.LANCZOS); lg.putalpha(lg.getchannel("A").point(lambda v: int(v * a)))
    card.alpha_composite(lg, ((cw - 150) // 2, 40))
    d.text((cw / 2, 250), "INTERNAL PLANNING DAY", font=inter(48, "Black"), fill=(150, 104, 40, int(255 * a)), anchor="mm")
    d.text((cw / 2, 305), "Minutes of the meeting", font=lora(40, True), fill=(90, 70, 60, int(255 * a)), anchor="mm")
    items = [("1.", "Wedding season starts 21 Nov.", .5), ("2.", "Everyone needs a gift.", 1.6), ("3.", "Nobody wants another dinner set.", 2.7), ("4.", "Decision: smell incredible.", 3.9)]
    y = 410
    for n, s, t0 in items:
        if u > t0:
            k = ss((u - t0) / .25); txt = typed(s, u, t0, 45)
            col = (150, 30, 40) if n == "4." else INK
            d.text((70, y), n, font=inter(46, "Bold"), fill=col + (int(255 * a * k),))
            d.text((140, y), txt, font=inter(46, "Bold" if n == "4." else "Medium"), fill=col + (int(255 * a * k),))
        y += 130
    card = card.rotate(-1.2, expand=True, resample=Image.BICUBIC)
    sh = Image.new("RGBA", card.size, (0, 0, 0, 0)); sh.putalpha(card.getchannel("A").point(lambda v: int(v * .6)))
    s0 = 0.92 + 0.08 * back(u / .4); card = card.resize((int(card.width * s0), int(card.height * s0)), Image.LANCZOS); sh = sh.resize(card.size)
    x = (W - card.width) // 2; y0 = 430
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(26)), (x + 10, y0 + 18)); im.alpha_composite(card, (x, y0))

def stamp(im, t, cx, cy, text):
    u = t - T_STAMP
    if u <= 0: return
    s = 0.9 + 1.2 * (1 - back(u / .18)); a = ss(u / .06) * (1 - ss((t - (T_OUT - .2)) / .2))
    st = Image.new("RGBA", (760, 190)); ds = ImageDraw.Draw(st)
    ds.rounded_rectangle((6, 6, 754, 184), 14, outline=(200, 30, 40, 240), width=10)
    ds.text((380, 96), text, font=inter(70), fill=(200, 30, 40, 240), anchor="mm")
    st = st.rotate(-8, expand=True, resample=Image.BICUBIC); st = st.resize((int(st.width * s), int(st.height * s)), Image.LANCZOS)
    st.putalpha(st.getchannel("A").point(lambda v: int(v * a * .95))); im.alpha_composite(st, (int(cx - st.width / 2), int(cy - st.height / 2)))

def frame(t):
    if t < T_GOLD:
        im = aurora(t)
        if t < 3.3: notice_card(im, t, ss(t / .3) * (1 - ss((t - 3.1) / .2)))
        else:
            ctext(im, 640, "The internet", inter(104), IVORY, win(t, 3.35, T_GOLD, .2))
            ctext(im, 770, "has not recovered.", inter(104), IVORY, win(t, 3.85, T_GOLD, .2))
            ctext(im, 960, "(80 million views later)", lora(52, True), (200, 230, 220), win(t, 4.5, T_GOLD, .25))
    else:
        base = warm_bg(t)
        if t < T_GOLD + .6:  # aurora -> warm dissolve with gold flash
            k = ss((t - T_GOLD) / .6); base = Image.blend(aurora(t), base, k)
        im = base
        if t < T_MIN:
            lg = LOGO.resize((260, int(LOGO.height * 260 / LOGO.width)), Image.LANCZOS)
            a = win(t, T_GOLD + .2, T_MIN, .3); lg.putalpha(lg.getchannel("A").point(lambda v: int(v * a))); im.alpha_composite(lg, ((W - 260) // 2, 420))
            ctext(im, 700, "So we held one too.", inter(96), IVORY, win(t, T_GOLD + .4, T_MIN, .25), scale=1 + .2 * (1 - back((t - T_GOLD - .4) / .3)))
        elif t < T_OUT:
            minutes_card(im, t)
            stamp(im, t, W / 2 + 60, 1395, "PLAN APPROVED")
        else:
            # outcome: gift box hero, then Miss Poem, stamp
            u = t - T_OUT
            hero = kb(BOX, t, T_OUT, T_BOTTLE, 1.12, 1.0) if t < T_BOTTLE - .1 else kb(BOTTLE, t, T_BOTTLE - .1, END + 4, 1.08, 1.0)
            if T_BOTTLE - .4 < t < T_BOTTLE - .1:
                hero = Image.blend(hero, kb(BOTTLE, t, T_BOTTLE - .1, END + 4, 1.08, 1.0), ss((t - (T_BOTTLE - .4)) / .3))
            k = ss(u / .3); im = Image.blend(im, hero, k)
            grad = Image.new("RGBA", (W, H)); g = np.zeros((H, W, 4), np.uint8); g[:700, :, 3] = (np.linspace(1, 0, 700) ** 1.5 * 170).astype(np.uint8)[:, None]; im.alpha_composite(Image.fromarray(g, "RGBA"))
            if t < T_BOTTLE:
                ctext(im, 300, "PLANNING OUTCOME:", inter(56, "Black"), GOLD, win(t, T_OUT + .1, T_BOTTLE, .25))
                ctext(im, 390, "The wedding gift sets.", inter(80), IVORY, win(t, T_OUT + .5, T_BOTTLE, .25))
            else:
                ctext(im, 300, "PLANNING OUTCOME:", inter(56, "Black"), GOLD, win(t, T_BOTTLE, END, .15))
                ctext(im, 390, "Smell like this.", inter(88), IVORY, win(t, T_BOTTLE + .1, END, .2))
    if t >= END:
        u = t - END
        endbg = ImageEnhance.Brightness(kb(BOTTLE, END, END, END + 1, 1.0, 1.0).filter(ImageFilter.GaussianBlur(22))).enhance(.32)
        im = Image.blend(im, endbg, ss(u / .5))
        lg = LOGO.resize((220, int(LOGO.height * 220 / LOGO.width)), Image.LANCZOS); a = ss((u - .2) / .4)
        lg.putalpha(lg.getchannel("A").point(lambda v: int(v * a))); im.alpha_composite(lg, ((W - 220) // 2, 420))
        ctext(im, 660, "For emergency gift assistance,", lora(56, True), IVORY, ss((u - .4) / .4))
        ctext(im, 740, "please DM us.", lora(56, True), IVORY, ss((u - .6) / .4))
        a3 = ss((u - .9) / .4)
        if a3 > 0:
            f = inter(46, "Black"); lab = "DM FOR PRICES"; tw = ImageDraw.Draw(im).textlength(lab, font=f)
            lay = Image.new("RGBA", im.size); dl = ImageDraw.Draw(lay); y = 920
            dl.rounded_rectangle(((W - tw) / 2 - 50, y - 50, (W + tw) / 2 + 50, y + 50), 50, fill=GOLD + (255,))
            dl.text((W / 2, y), lab, font=f, fill=(40, 8, 16, 255), anchor="mm"); lay.putalpha(lay.getchannel("A").point(lambda v: int(v * a3))); im.alpha_composite(lay)
        ctext(im, 1020, "OR VISIT US AT LAJPAT NAGAR-II", pop(36, "Bold"), (226, 180, 110), ss((u - 1.1) / .4), 6)
        ctext(im, 1140, "#northernlights", pop(34), (150, 230, 200), ss((u - 1.5) / .4), 6)
    if t < .2: im = Image.blend(Image.new("RGBA", im.size, (0, 0, 0, 255)), im, ss(t / .2))
    if t > DUR - .5: im = Image.blend(im, Image.new("RGBA", im.size, (0, 0, 0, 255)), ss((t - DUR + .5) / .5))
    return im.convert("RGB")

# ---------- audio ----------
SR = 44100
def audio(path):
    from scipy.signal import lfilter
    n = int(SR * DUR); out = np.zeros((n, 2), np.float32); r = np.random.default_rng(6); tt = np.arange(n) / SR
    def add(sig, at, g=1.0, pan=0.0):
        i = int(at * SR); j = min(n, i + len(sig))
        if i >= n or j <= i: return
        s = sig[: j - i] * g; out[i:j, 0] += s * (1 - pan); out[i:j, 1] += s * (1 + pan)
    def env(L, a=.003, rel=.15): x = np.arange(int(L * SR)) / SR; return np.minimum(1, x / a) * np.exp(-x / rel)
    def tone(f, L, a=.01, rel=.4, h=(1, .4, .2)): x = np.arange(int(L * SR)) / SR; return sum(g * np.sin(2 * np.pi * f * (i + 1) * x) for i, g in enumerate(h)) * env(L, a, rel)
    # 1) nordic ambient pad (aurora) 0 -> T_GOLD: slow minor chord with shimmer
    pad = np.zeros(n); m = tt < T_GOLD + .3
    for f in (110, 130.8, 164.8, 220, 329.6):
        pad += np.sin(2 * np.pi * f * tt + np.sin(2 * np.pi * .2 * tt)) * (.5 + .5 * np.sin(2 * np.pi * .13 * tt + f))
    pad *= .03 * m * np.minimum(1, tt / .6) * np.clip((T_GOLD + .3 - tt) / .4, 0, 1)
    out[:, 0] += pad; out[:, 1] += np.roll(pad, 300)
    for k in range(10): add(tone(1760 * (1.5 if k % 2 else 1), 1.2, .005, .5, (1,)), .5 + k * .45, .02, (-.5 if k % 2 else .5))
    # typing ticks for the notice
    for c in range(int(1.7 * 52)):
        ck = lfilter([1, -1], [1, -.3], r.normal(0, 1, int(.012 * SR))) * env(.012, .0005, .003); add(ck, .35 + c / 52, .1)
    # "has not recovered": sad trombone-ish descending
    for i, f in enumerate((233, 220, 207.7, 196)):
        add(tone(f, .55 if i < 3 else 1.2, .02, .35 if i < 3 else .8, (1, .6, .4, .3)), 3.4 + i * .42, .07)
    # record scratch into warm world
    sc = np.sin(2 * np.pi * np.cumsum(np.linspace(900, 200, int(.25 * SR))) / SR) * env(.25, .002, .08); add(sc, T_GOLD - .05, .15)
    # 2) warm upbeat groove T_GOLD -> END: soft kick, claps, plucked major arps
    beat = 60 / 112; t = T_GOLD + .2; k = 0
    kick = lambda: np.sin(2 * np.pi * (50 + 90 * np.exp(-np.arange(int(.3 * SR)) / SR / .04)) * np.arange(int(.3 * SR)) / SR) * env(.3, .002, .1)
    clap = lambda: lfilter([1, -1], [1, -.5], r.normal(0, 1, int(.12 * SR))) * env(.12, .002, .03)
    prog = [(261.6, 329.6, 392), (220, 261.6, 329.6), (174.6, 220, 261.6), (196, 246.9, 293.7)]
    while t < END + 3.2:
        add(kick(), t, .5)
        if k % 2 == 1: add(clap(), t, .12)
        ch = prog[(k // 4) % 4]
        add(tone(ch[k % 3] * 2, .5, .005, .25, (1, .3)), t, .06, .3 * math.sin(k))
        add(tone(ch[(k + 1) % 3] * 2, .4, .005, .2, (1, .3)), t + beat / 2, .045, -.3 * math.sin(k))
        if k % 4 == 0: add(tone(ch[0] / 2, beat * 4, .02, 1.2, (1, .5)), t, .07)
        t += beat; k += 1
    # minutes: pen ticks for each item
    for t0 in (.5, 1.6, 2.7, 3.9):
        add(tone(1320, .2, .002, .06, (1,)), T_MIN + t0, .05)
    # stamp thud + chime
    add(kick(), T_STAMP + .15, 1.8); add(lfilter([1], [1, -.9], r.normal(0, 1, int(.1 * SR))) * env(.1, .001, .025), T_STAMP + .15, .3)
    for i, f in enumerate((1046.5, 1318.5, 1568)): add(tone(f, 1.6, .003, .6, (1,)), T_STAMP + .3 + i * .07, .05)
    out = np.tanh(out * 1.3)
    fd = np.ones(n); fd[-int(.9 * SR):] = np.linspace(1, 0, int(.9 * SR)); out *= fd[:, None]
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
                        "-movflags", "+faststart", "-shortest", D + "planning_day_reel.mp4"], check=True)
        frame(2.6).save(D + "cover.jpg", quality=92)
        print("ok", DUR)

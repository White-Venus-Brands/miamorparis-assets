"""Black Friday sale (live now, ends Black Friday 27 Nov 2026) Reel, Tannay's English VO. Real footage only: spray clips (spray-rating/src2),
body wash studio shots, Marhaba photos. Offer stays secret: 'comment anything, we DM the offers'.
Segment starts live in CUES so the edit can be retimed to the recorded VO.
Usage: python3 build.py OUTDIR [vo.wav]"""
import json, math, os, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

D = os.path.dirname(os.path.abspath(__file__)) + "/"
R = D + "../../"
ATT = "/mnt/user-data/attachments/e1dc2e45-c278-5714-b377-734372e7d29a/"
OUT = (sys.argv[1].rstrip("/") + "/") if len(sys.argv) > 1 else "/tmp/bf/"
VO = sys.argv[2] if len(sys.argv) > 2 else None
sys.path.insert(0, R + "posts/2026-11-spray-rating"); from mist_fx import background, enhance
os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1080, 1920, 30
GOLD, GOLD2, IVORY, INK = (226, 186, 112), (250, 214, 140), (250, 245, 236), (8, 6, 6)

# line starts (s) for: hook, scent, bodywash, gifts, dates, offer, dm, end
CUES = json.load(open(D + "cues.json")) if os.path.exists(D + "cues.json") else \
    {"hook": 0.0, "scent": 2.6, "wash": 4.1, "gifts": 5.5, "dates": 7.6, "offer": 11.0, "dm": 14.2, "end": 18.0}

def MS(size, style="Black"):
    f = ImageFont.truetype("/usr/share/fonts/truetype/google-fonts/ofl/montserrat/Montserrat[wght].ttf", size); f.set_variation_by_name(style); return f
def LORA(s): return ImageFont.truetype("/usr/share/fonts/truetype/google-fonts/Lora-Italic-Variable.ttf", s)
def cl(x): return max(0.0, min(1.0, x))
def ss(x): x = cl(x); return x * x * (3 - 2 * x)
def back(x): x = cl(x); c = 1.7; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2

def text(im, cy, s, font, fill=IVORY, a=1.0, scale=1.0, track=0, shadow=True):
    if a <= 0: return
    lay = Image.new("RGBA", (W * 2, 500)); d = ImageDraw.Draw(lay)
    if track:
        x = 0; widths = [d.textlength(ch, font=font) + track for ch in s]; x0 = (lay.width - sum(widths)) / 2
        for ch, w_ in zip(s, widths): d.text((x0, 60), ch, font=font, fill=fill); x0 += w_
    else: d.text((lay.width / 2, 60), s, font=font, fill=fill, anchor="ma")
    bb = lay.getbbox()
    if not bb: return
    lay = lay.crop(bb)
    if scale != 1: lay = lay.resize((max(1, int(lay.width * scale)), max(1, int(lay.height * scale))), Image.LANCZOS)
    if a < 1: lay.putalpha(lay.getchannel("A").point(lambda v: int(v * a)))
    x = (W - lay.width) // 2; y = int(cy - lay.height / 2)
    if shadow:
        sh = Image.new("RGBA", (lay.width + 60, lay.height + 60)); m = lay.getchannel("A").point(lambda v: int(v * .8))
        sh.paste((0, 0, 0, 255), (30, 30), m); im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(12)), (x - 30, y - 26))
    im.alpha_composite(lay, (x, y))

def gold_line(im, cy, w, a=1.0):
    d = ImageDraw.Draw(im); d.rectangle(((W - w) // 2, cy - 2, (W + w) // 2, cy + 2), fill=GOLD + (int(255 * a),))

SHADE = Image.new("RGBA", (W, H)); _d = ImageDraw.Draw(SHADE)
for y in range(H): _d.line([(0, y), (W, y)], fill=(0, 0, 0, int(170 * max(1 - y / 560, (y - (H - 640)) / 640, 0))))

# ---------- spray clips: extract, mist-boost, slow-mo around the peak ----------
CLIPS = {"ombre_h": ("v6", 3.4, 4.3), "moksha_v": ("v1", 0.0, 0.2), "poem_v": ("v3", 5.6, 6.6), "poem_h": ("v4", 1.2, 2.0), "ombre_v": ("v5", 0.4, 1.0)}
CACHE = {}
def clip_frames(key):
    if key in CACHE: return CACHE[key]
    v, st, peak = CLIPS[key]; fd = OUT + f"c_{key}/"; os.makedirs(fd, exist_ok=True)
    if not os.listdir(fd):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(st), "-t", "3.2", "-i", R + f"posts/2026-11-spray-rating/src2/{v}.mov",
                        "-vf", f"fps=30,scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},eq=gamma=1.06:contrast=1.08",
                        "-q:v", "2", fd + "%04d.jpg"], check=True)
    ims = [Image.open(fd + f).convert("RGB") for f in sorted(os.listdir(fd))]
    bg = background(ims); ims = [enhance(im, bg, k=3.6, cap=85) for im in ims]
    CACHE[key] = (ims, peak - st); return CACHE[key]
def spray(key, u, dur):
    """u = time into the shot. Plays at 1x, slows to 0.4x around the peak."""
    ims, pk = clip_frames(key)
    a0 = max(0, pk - .35)                      # source time where slow-mo starts
    lead = min(a0, .5); s0 = a0 - lead        # start a bit before
    tsrc = s0 + u if u < lead else a0 + (u - lead) * .4
    x = tsrc * 30; j = min(int(x), len(ims) - 2); f = x - j
    return Image.blend(ims[j], ims[j + 1], cl(f)).convert("RGBA")

# ---------- stills ----------
def fit_white(path, zoom):
    im = Image.open(path).convert("RGB"); im = ImageOps.exif_transpose(im)
    can = Image.new("RGB", (W, H), (246, 244, 241)); s = H * .78 / im.height * zoom
    p = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    can.paste(p, ((W - p.width) // 2, (H - p.height) // 2 + 40)); return can.convert("RGBA")
WASH = [ATT + f for f in ("14a68f49-IMG_0086_copy.jpg", "1a5e6885-IMG_0067_copy.jpg", "715ec5b1-IMG_0061_copy.jpg", "328411ec-IMG_0075_copy.jpg")]
WASH_IM = [Image.open(p).convert("RGB") for p in WASH]
def wash(i, p):
    im = WASH_IM[i]; can = Image.new("RGB", (W, H), (246, 244, 241)); s = H * .8 / im.height * (1 + .05 * p)
    q = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    can.paste(q, ((W - q.width) // 2, (H - q.height) // 2 + 80)); return can.convert("RGBA")
PH = {k: Image.open(R + f"posts/2026-11-marhaba-yellow/src/{k}.png").convert("RGB") for k in ("trio", "inbox")}
def photo(k, p, z0=1.0, z1=1.08):
    src = PH[k]; z = z0 + (z1 - z0) * p; sw, sh = src.size; w, h = sw / z, sh / z
    x0 = (sw - w) / 2; y0 = (sh - h) / 2
    return src.resize((W, H), Image.LANCZOS, box=(x0, y0, x0 + w, y0 + h)).convert("RGBA")

# ---------- frame ----------
def frame(t):
    C = CUES
    if t < C["scent"]:                                   # HOOK
        u = t - C["hook"]; im = spray("ombre_h", u, C["scent"] - C["hook"]); im.alpha_composite(SHADE)
        if u < .12: im.alpha_composite(Image.new("RGBA", (W, H), (255, 240, 210, int(255 * (1 - u / .12)))))
        text(im, 300, "BLACK", MS(190), fill=IVORY, a=ss((u - .15) / .1), scale=1 + .4 * (1 - back((u - .15) / .3)))
        text(im, 480, "FRIDAY", MS(190), fill=GOLD2, a=ss((u - .45) / .1), scale=1 + .4 * (1 - back((u - .45) / .3)))
        gold_line(im, 610, int(560 * ss((u - .8) / .4)))
        text(im, 680, "M I   A M O R   P A R I S", MS(44, "SemiBold"), fill=IVORY, a=ss((u - 1.0) / .3))
        if u > 1.5:   # LIVE NOW pill
            a = ss((u - 1.5) / .15); pill = Image.new("RGBA", (420, 96)); pd = ImageDraw.Draw(pill)
            pd.rounded_rectangle((0, 0, 419, 95), 48, fill=(214, 40, 40, int(255 * a)))
            pd.ellipse((40, 36, 64, 60), fill=(255, 255, 255, int(255 * a * (.5 + .5 * math.sin(u * 9) ** 2))))
            pd.text((235, 48), "SALE LIVE", font=MS(46, "ExtraBold"), fill=(255, 255, 255, int(255 * a)), anchor="mm")
            sc = 1 + .3 * (1 - back((u - 1.5) / .3)); pill = pill.resize((int(420 * sc), int(96 * sc)), Image.LANCZOS)
            im.alpha_composite(pill, ((W - pill.width) // 2, 790 - pill.height // 2))
        return im
    if t < C["wash"]:                                    # SIGNATURE SCENT
        u = t - C["scent"]; im = spray("moksha_v", u, C["wash"] - C["scent"]); im.alpha_composite(SHADE)
        text(im, 250, "Your", LORA(80), fill=GOLD2, a=ss(u / .2))
        text(im, 370, "SIGNATURE SCENT", MS(96), a=ss((u - .15) / .2), scale=1 + .2 * (1 - back((u - .15) / .3)))
        return im
    if t < C["gifts"]:                                   # BODY WASH quick cuts
        u = t - C["wash"]; dur = C["gifts"] - C["wash"]; n = len(WASH); k = min(n - 1, int(u / (dur / n)))
        im = wash(k, (u - k * dur / n) / (dur / n))
        g = Image.new("RGBA", (W, H)); gd = ImageDraw.Draw(g)
        for y in range(420): gd.line([(0, y), (W, y)], fill=(0, 0, 0, int(160 * (1 - y / 420))))
        im.alpha_composite(g)
        text(im, 190, "Your", LORA(80), fill=GOLD2)
        text(im, 300, "BODY WASH", MS(110))
        return im
    if t < C["dates"]:                                   # GIFT LIST
        u = t - C["gifts"]; dur = C["dates"] - C["gifts"]; half = dur * .5
        im = photo("trio", u / dur) if u < half else photo("inbox", (u - half) / half, 1.06, 1.0)
        if abs(u - half) < .1: im.alpha_composite(Image.new("RGBA", (W, H), (255, 240, 210, int(200 * (1 - abs(u - half) / .1)))))
        im.alpha_composite(SHADE)
        text(im, 230, "Your entire", LORA(80), fill=GOLD2, a=ss(u / .2))
        text(im, 350, "GIFT LIST", MS(120), a=ss((u - .15) / .2), scale=1 + .2 * (1 - back((u - .15) / .3)))
        return im
    if t < C["offer"]:                                   # DATES
        u = t - C["dates"]; im = spray("poem_v", u, C["offer"] - C["dates"]); im.alpha_composite(SHADE)
        text(im, 290, "NOW – 27 NOV", MS(122), fill=GOLD2, a=ss(u / .15), scale=1 + .3 * (1 - back(u / .3)))
        text(im, 450, "ENDS ON BLACK FRIDAY", MS(70, "ExtraBold"), a=ss((u - .3) / .2))
        gold_line(im, 560, int(420 * ss((u - .6) / .3)))
        text(im, 1560, "IN STORE · LAJPAT NAGAR-II", MS(50, "Bold"), a=ss((u - 1.4) / .25))
        text(im, 1640, "+ ONLINE · miamorparis.in", MS(50, "Bold"), fill=GOLD2, a=ss((u - 2.2) / .25))
        return im
    if t < C["dm"]:                                      # OFFER: CLASSIFIED
        u = t - C["offer"]; im = spray("ombre_v", u, C["dm"] - C["offer"]); im.alpha_composite(SHADE)
        im.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(90 * ss(u / .3)))))
        text(im, 520, "THE OFFER?", MS(110), a=ss(u / .2))
        bar_w = int(760 * ss((u - .6) / .35)); d = ImageDraw.Draw(im)
        if bar_w > 4:
            d.rectangle(((W - 760) // 2, 660, (W - 760) // 2 + bar_w, 790), fill=(4, 4, 4)); d.rectangle(((W - 760) // 2, 660, (W - 760) // 2 + bar_w, 790), outline=GOLD, width=3)
        if u > 1.1:   # stamp
            st = Image.new("RGBA", (700, 200)); sd = ImageDraw.Draw(st)
            sd.rounded_rectangle((8, 8, 692, 192), 18, outline=(214, 40, 40), width=10)
            sd.text((350, 100), "CLASSIFIED", font=MS(104), fill=(214, 40, 40), anchor="mm")
            sc = 1 + .6 * (1 - back((u - 1.1) / .25)); st = st.resize((int(700 * sc * .9), int(200 * sc * .9)), Image.LANCZOS).rotate(-8, expand=True, resample=Image.BICUBIC)
            st.putalpha(st.getchannel("A").point(lambda v: int(v * ss((u - 1.1) / .1)))); im.alpha_composite(st, ((W - st.width) // 2, 725 - st.height // 2))
        text(im, 950, "Not saying it here.", LORA(70), fill=GOLD2, a=ss((u - 1.6) / .3))
        return im
    u = t - C["dm"]                                       # DM CTA + end card
    im = Image.new("RGBA", (W, H), (8, 6, 6, 255))
    glow = Image.new("RGBA", (W, H)); ImageDraw.Draw(glow).ellipse((90, 520, W - 90, 1300), fill=(226, 186, 112, 45)); im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(120)))
    text(im, 540, "Comment", LORA(110), fill=GOLD2, a=ss(u / .2))
    text(im, 720, "ANYTHING 👇" if False else "ANYTHING", MS(170), a=ss((u - .25) / .15), scale=1 + .4 * (1 - back((u - .25) / .3)))
    text(im, 890, "we'll send you the offers.", LORA(72), fill=IVORY, a=ss((u - .8) / .3))
    if u > 1.0:   # bouncing arrow to the comments
        d = ImageDraw.Draw(im); y = 1700 + 18 * math.sin((u - 1.0) * 6); a = int(255 * ss((u - 1.0) / .3))
        d.polygon([(W - 160, y), (W - 100, y), (W - 130, y + 50)], fill=GOLD + (a,)); d.rectangle((W - 140, y - 70, W - 120, y), fill=GOLD + (a,))
    gold_line(im, 1010, int(520 * ss((u - 1.2) / .4)))
    lg = Image.open(R + "assets/cutouts/logo_gold.png").convert("RGBA"); lg = lg.resize((200, int(200 * lg.height / lg.width)), Image.LANCZOS)
    a = ss((u - 1.4) / .4); lg.putalpha(lg.getchannel("A").point(lambda v: int(v * a))); im.alpha_composite(lg, ((W - lg.width) // 2, 1080))
    text(im, 1080 + lg.height + 70, "BLACK FRIDAY SALE · ENDS 27 NOV", MS(46, "Bold"), fill=GOLD2, a=ss((u - 1.7) / .3))
    text(im, 1080 + lg.height + 140, "O-17, Lajpat Nagar-II  ·  miamorparis.in", MS(38, "SemiBold"), a=ss((u - 2.0) / .3))
    return im

def music(path, dur):
    """dark, slow trap-ish bed (synth), sits under the VO."""
    sr = 44100; n = int(dur * sr); tt = np.arange(n) / sr; a = np.zeros(n)
    def add(sig, t0):
        i0 = int(t0 * sr); m = min(n - i0, len(sig)); a[i0:i0 + m] += sig[:m]
    bpm = 140; b = 60 / bpm
    x = np.arange(int(.5 * sr)) / sr
    kick = .9 * np.sin(2 * np.pi * (45 + 90 * np.exp(-x * 30)) * x) * np.exp(-x * 7)
    hat = np.random.default_rng(1).standard_normal(int(.05 * sr)) * np.exp(-np.arange(int(.05 * sr)) / 300) * .12
    pad_notes = [(55, 65.4, 82.4), (49, 61.7, 73.4)]
    t = 0.0; k = 0
    while t < dur:
        if k % 8 in (0, 3, 6): add(kick, t)
        add(hat, t + b / 2)
        if k % 2 == 0: add(hat * .6, t)
        t += b; k += 1
    for bar in range(int(dur / (b * 8)) + 1):
        notes = pad_notes[bar % 2]; t0 = bar * b * 8; L = int(b * 8 * sr); x = np.arange(L) / sr
        env = np.minimum(1, x / .3) * np.minimum(1, (b * 8 - x) / .3)
        sig = sum(.05 * np.sin(2 * np.pi * f * 2 * x) + .03 * np.sin(2 * np.pi * f * 4 * x + .3) for f in notes) * env
        add(sig, t0)
    for t0 in (CUES["hook"] + .15, CUES["hook"] + .45, CUES["dates"], CUES["dm"] + .25):   # impacts
        x = np.arange(int(.8 * sr)) / sr; add(.6 * np.sin(2 * np.pi * (40 + 60 * np.exp(-x * 8)) * x) * np.exp(-x * 4), t0)
    a *= np.minimum(1, (dur - tt) / .8); a = np.tanh(a * 1.2) * .7
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((a * 32767).astype(np.int16).tobytes())

if __name__ == "__main__":
    only = os.environ.get("ONLY")
    if only:
        for s in only.split(","): frame(float(s)).convert("RGB").save(OUT + f"still_{s}.jpg", quality=85)
        sys.exit()
    dur = CUES["end"]; os.makedirs(OUT + "f", exist_ok=True)
    for i in range(int(dur * FPS)): frame(i / FPS).convert("RGB").save(OUT + f"f/{i:04d}.png", compress_level=1)
    music(OUT + "m.wav", dur)
    name = "black_friday_reel" + ("" if VO else "_draft") + ".mp4"
    if VO:   # VO on top, music ducked to 25%
        af = "[1:a]volume=0.25[m];[2:a]aresample=44100,volume=1.0[v];[m][v]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[a]"
        cmd = ["ffmpeg", "-y", "-v", "error", "-framerate", str(FPS), "-i", OUT + "f/%04d.png", "-i", OUT + "m.wav", "-i", VO,
               "-filter_complex", af, "-map", "0:v", "-map", "[a]"]
    else:
        cmd = ["ffmpeg", "-y", "-v", "error", "-framerate", str(FPS), "-i", OUT + "f/%04d.png", "-i", OUT + "m.wav", "-map", "0:v", "-map", "1:a"]
    subprocess.run(cmd + ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "15", "-preset", "medium", "-c:a", "aac", "-b:a", "192k",
                          "-shortest", "-movflags", "+faststart", D + name], check=True)
    frame(CUES["hook"] + 1.6).convert("RGB").save(D + "cover.jpg", quality=94)
    print("done", name)

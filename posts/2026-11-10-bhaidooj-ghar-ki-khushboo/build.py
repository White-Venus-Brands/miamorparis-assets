"""Reel: Bhai Dooj 'Ghar ki khushboo'. Brother abroad can't come home; sister sends a parcel.
Tannay's stills (source/01..16), ElevenLabs dialogue (Creative Claw, two parts mixed in later), real Mr Aqua gift-box photo.
1080x1920, 30 fps. Own soft piano bed; voices added with add_audio_to_video at A_OFF and B_OFF."""
import math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

D = os.path.dirname(os.path.abspath(__file__)) + "/"; R = D + "../../"
OUT = sys.argv[1] if len(sys.argv) > 1 else "/tmp/bd_frames/"
W, H, FPS = 1080, 1920, 30
GOLD, IVORY = (226, 186, 112), (250, 242, 230)
LOGO = Image.open(R + "assets/cutouts/logo_gold.png").convert("RGBA")
BOX = R + "posts/2026-11-gift-boxes-for-him/source/mraqua_box.jpg"

def inter(s, w="Black"): return ImageFont.truetype(f"/usr/share/fonts/opentype/inter/InterDisplay-{w}.otf", s)
def lora(s, it=True): return ImageFont.truetype("/usr/share/fonts/truetype/google-fonts/Lora-" + ("Italic-Variable" if it else "Variable") + ".ttf", s)
def pop(s, w="Bold"): return ImageFont.truetype(f"/usr/share/fonts/truetype/google-fonts/Poppins-{w}.ttf", s)
def cl(x): return max(0.0, min(1.0, x))
def ss(x): x = cl(x); return x * x * (3 - 2 * x)
def back(x): x = cl(x); c = 1.5; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2

A_OFF, B_OFF = 3.0, 20.4          # part A (10.4 s) and part B (13.36 s) voice offsets
# (start, image, kind, text, kenburns)  kind: hook | CHHOTI | BHAIYA | narr | end
SHOTS = [
    (0.0, "12", "hook", None, (1.00, 1.08, 0, 0)),
    (A_OFF + 0.00, "15", "CHHOTI", "Bhaiya, is baar Bhai Dooj pe aa rahe ho na?", (1.04, 1.12, 0, 0)),
    (A_OFF + 3.40, "16", "BHAIYA", "Nahi aa paunga, Chhoti... exams hain.", (1.08, 1.0, 0, 0)),
    (A_OFF + 6.73, "13", "CHHOTI", "Tumne pichhle saal bhi yahi bola tha.", (1.02, 1.12, 0, 0)),
    (A_OFF + 9.22, "14", "BHAIYA", "Sorry yaar...", (1.10, 1.02, 0, 0)),
    (13.9, "11", "narr", "Phir usne kuch socha...", (1.0, 1.08, 0, 0)),
    (15.6, "09", "narr", "Bhai Dooj se 3 din pehle.", (1.04, 1.10, 0, 0.02)),
    (17.3, "10", "narr", "Thoda sa ghar, ek parcel mein.", (1.08, 1.0, 0, 0)),
    (18.8, "08", "narr", "Bhai Dooj ki subah...", (1.0, 1.08, 0, 0)),
    (B_OFF + 0.00, "07", "BHAIYA", "Chhoti... ye parcel tumne bheja?", (1.04, 1.12, 0, 0)),
    (B_OFF + 2.72, "06", "CHHOTI", "Khol ke dekho na!", (1.0, 1.08, 0, 0)),
    (B_OFF + 4.16, "17", None, None, (1.0, 1.10, 0, 0.02)),
    (B_OFF + 4.95, "18", None, None, (1.0, 1.08, 0, 0)),
    (B_OFF + 6.20, "05", "BHAIYA", "Ye toh... bilkul ghar jaisi khushboo hai.", (1.12, 1.02, 0, 0)),
    (B_OFF + 8.96, "03", "BHAIYA", "Happy Bhai Dooj, Chhoti.", (1.0, 1.08, 0, 0)),
    (B_OFF + 10.88, "01", "CHHOTI", "Happy Bhai Dooj, bhaiya.", (1.02, 1.10, 0, 0)),
    (B_OFF + 13.50, "02", "end", None, (1.0, 1.06, 0, 0)),
]
END_T = B_OFF + 13.50
DUR = END_T + 5.6

SRC = {}
def src(name):
    if name not in SRC:
        im = Image.open(D + "source/" + name + ".png").convert("RGB")
        s = max(W / im.width, H / im.height) * 1.16
        SRC[name] = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    return SRC[name]

CONTAIN = {"18"}   # non-9:16 product shot: show it whole (fit width) over a blurred fill, never crop the products
_BG = {}
def contain(name, u, kb):
    z0, z1 = kb[0], kb[1]; z = z0 + (z1 - z0) * ss(u)
    im = Image.open(D + "source/" + name + ".png").convert("RGB")
    if name not in _BG:
        b = im.resize((int(im.width * H / im.height * 1.3), int(H * 1.3))).filter(ImageFilter.GaussianBlur(25)).resize((60, int(60 * H / W))).resize((int(im.width * H / im.height * 1.3), int(H * 1.3)), Image.BICUBIC).filter(ImageFilter.GaussianBlur(30))
        _BG[name] = b.crop(((b.width - W) // 2, (b.height - H) // 2, (b.width - W) // 2 + W, (b.height - H) // 2 + H))
    bg = Image.eval(_BG[name], lambda v: int(v * 0.55)).convert("RGBA")
    w = int(W * 0.98 * (0.97 + 0.03 * (z - 1) / 0.08)); h = int(im.height * w / im.width)
    bg.alpha_composite(im.resize((w, h), Image.LANCZOS).convert("RGBA"), ((W - w) // 2, (H - h) // 2 - 60))
    return bg

def kenburns(name, u, kb):
    if name in CONTAIN: return contain(name, u, kb)
    z0, z1, dx, dy = kb; im = src(name); z = z0 + (z1 - z0) * ss(u)
    k = 1.0; ww, hh = W * k / z, H * k / z
    cx = im.width / 2 + dx * im.width * ss(u); cy = im.height / 2 + dy * im.height * ss(u)
    return im.resize((W, H), Image.BICUBIC, box=(cx - ww / 2, cy - hh / 2, cx + ww / 2, cy + hh / 2)).convert("RGBA")

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

TAGCOL = {"CHHOTI": (18, 92, 92), "BHAIYA": (48, 52, 64)}
def caption(im, u, who, line):
    a = ss(u / 0.15); sc = 0.9 + 0.1 * back(u / 0.3)
    f = inter(64, "ExtraBold"); tmp = ImageDraw.Draw(Image.new("RGB", (1, 1))); lines = wrap(tmp, line, f, 860)
    lh = int(f.size * 1.2); bw = int(max(tmp.textlength(l, font=f) for l in lines)) + 76; bh = lh * len(lines) + 52; tagh = 62
    lay = Image.new("RGBA", (max(bw, 260), bh + tagh)); d = ImageDraw.Draw(lay)
    tf = inter(34, "Black"); tw = d.textlength(who, font=tf)
    d.rounded_rectangle((0, 0, tw + 44, 54), 27, fill=TAGCOL[who] + (255,)); d.text((22, 27), who, font=tf, fill=IVORY + (255,), anchor="lm")
    d.rounded_rectangle((0, tagh, bw - 1, tagh + bh - 1), 28, fill=(GOLD + (245,)) if who == "CHHOTI" else (255, 252, 246, 240))
    for i, l in enumerate(lines): d.text((bw / 2, tagh + 26 + i * lh + lh / 2), l, font=f, fill=(28, 14, 14, 255), anchor="mm")
    lay = lay.resize((max(1, int(lay.width * sc)), max(1, int(lay.height * sc))), Image.LANCZOS)
    lay.putalpha(lay.getchannel("A").point(lambda v: int(v * a)))
    shadow_paste(im, lay, (W - lay.width) // 2, 1250)

def narr(im, u, text, y=1300):
    a = ss(u / 0.4) * (1 - ss((u - 1.5) / 0.3))
    g = Image.new("RGBA", (W, 700)); g.putalpha(Image.linear_gradient("L").resize((W, 700)).point(lambda v: int(v * 0.7 * a)))
    im.alpha_composite(Image.composite(Image.new("RGBA", (W, 700), (6, 4, 4, 255)), Image.new("RGBA", (W, 700)), g.getchannel("A")), (0, H - 700))
    lay = Image.new("RGBA", (W, 200)); d = ImageDraw.Draw(lay); d.text((W / 2, 20), text, font=lora(66), fill=IVORY + (int(255 * a),), anchor="ma")
    shadow_paste(im, lay, 0, y, 10, 0.8 * a)

def hook(im, t):
    top = Image.new("RGBA", (W, 760)); top.putalpha(Image.linear_gradient("L").rotate(180).resize((W, 760)).point(lambda v: int(v * 0.8)))
    im.alpha_composite(Image.composite(Image.new("RGBA", (W, 760), (6, 4, 4, 255)), Image.new("RGBA", (W, 760)), top.getchannel("A")))
    lay = Image.new("RGBA", (W, 420)); d = ImageDraw.Draw(lay)
    d.text((W / 2, 10), "Pehli baar...", font=lora(84), fill=GOLD + (255,), anchor="ma")
    d.text((W / 2, 130), "Bhai Dooj pe", font=inter(96), fill=IVORY + (255,), anchor="ma")
    d.text((W / 2, 245), "bhaiya ghar nahi aayega.", font=inter(76), fill=IVORY + (255,), anchor="ma")
    shadow_paste(im, lay, 0, 190, 12, 0.85)

def giftcard(im, u):
    s = 520; c = Image.open(BOX).convert("RGB").resize((s, s), Image.LANCZOS).convert("RGBA")
    m = Image.new("L", (s, s), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, s - 1, s - 1), 30, fill=255); c.putalpha(m)
    f = Image.new("RGBA", (s + 12, s + 84)); df = ImageDraw.Draw(f); df.rounded_rectangle((0, 0, s + 11, s + 83), 34, fill=GOLD + (255,)); f.alpha_composite(c, (6, 6))
    df.text(((s + 12) / 2, s + 45), "Mr Aqua gift set", font=pop(34), fill=(36, 10, 16, 255), anchor="mm")
    sc = 0.55 + 0.45 * back(u / 0.45); f = f.resize((int(f.width * sc), int(f.height * sc)), Image.LANCZOS)
    f.putalpha(f.getchannel("A").point(lambda v: int(v * ss(u / 0.2))))
    shadow_paste(im, f, (W - f.width) // 2, 1080 - f.height // 2, 22, 0.65)

def endcard(im, t):
    u = t - END_T
    g = Image.new("RGBA", (W, H)); g.putalpha(Image.new("L", (W, H), int(150 * ss(u / 0.8))))
    im.alpha_composite(Image.composite(Image.new("RGBA", (W, H), (10, 5, 4, 255)), Image.new("RGBA", (W, H)), g.getchannel("A")))
    def txt(xy, s_, f, col, al):
        lay = Image.new("RGBA", im.size); ImageDraw.Draw(lay).text(xy, s_, font=f, fill=col + (int(255 * al),), anchor="ma"); shadow_paste(im, lay, 0, 0, 8, 0.6 * al, 3)
    txt((W / 2, 250), "Ghar door ho sakta hai...", lora(74), IVORY, ss((u - 0.4) / 0.6))
    txt((W / 2, 350), "uski khushboo nahi.", lora(80), GOLD, ss((u - 1.2) / 0.6))
    lg = LOGO.resize((210, int(LOGO.height * 210 / LOGO.width)), Image.LANCZOS); lg.putalpha(lg.getchannel("A").point(lambda v: int(v * ss((u - 2.0) / 0.5))))
    im.alpha_composite(lg, ((W - 210) // 2, 1250))
    txt((W / 2, 1440), "Is Bhai Dooj, gift a fragrance that feels like home.", pop(36, "Medium"), IVORY, ss((u - 2.3) / 0.5))
    a2 = ss((u - 2.7) / 0.4)
    if a2 > 0:
        f = inter(44, "Black"); lab = "DM FOR PRICES"; tw = ImageDraw.Draw(im).textlength(lab, font=f)
        lay = Image.new("RGBA", im.size); dl = ImageDraw.Draw(lay); y = 1560
        dl.rounded_rectangle(((W - tw) / 2 - 50, y - 46, (W + tw) / 2 + 50, y + 46), 46, fill=GOLD + (int(255 * a2),))
        dl.text((W / 2, y), lab, font=f, fill=(36, 10, 16, int(255 * a2)), anchor="mm"); im.alpha_composite(lay)
    txt((W / 2, 1640), "OR VISIT US AT LAJPAT NAGAR-II", pop(32), (232, 196, 130), ss((u - 3.0) / 0.4))

def frame(t):
    i = max(k for k, s in enumerate(SHOTS) if s[0] <= t)
    t0, name, kind, text, kb = SHOTS[i]; t1 = SHOTS[i + 1][0] if i + 1 < len(SHOTS) else DUR
    im = kenburns(name, (t - t0) / (t1 - t0), kb)
    if kind == "hook": hook(im, t)
    elif kind in ("CHHOTI", "BHAIYA"): caption(im, t - t0 - 0.1, kind, text)
    elif kind == "narr": narr(im, t - t0, text)
    if kind == "end": endcard(im, t)
    # soft dip-through-black on the montage cuts
    for tc in (13.9, 15.6, 17.3, 18.8, B_OFF, END_T):
        dd = abs(t - tc)
        if dd < 0.18: im = Image.blend(im, Image.new("RGBA", im.size, (0, 0, 0, 255)), 0.45 * (1 - dd / 0.18))
    return im.convert("RGB")

# ---------- soft piano bed (voices are mixed in later at A_OFF / B_OFF) ----------
SR = 44100
def audio(path):
    n = int(SR * DUR); out = np.zeros(n, np.float32)
    def add(sig, at, g=1.0):
        i = int(at * SR); j = min(n, i + len(sig)); out[i:j] += sig[: j - i] * g
    def piano(f, L, g):
        x = np.arange(int(L * SR)) / SR; e = np.exp(-x / 1.1) * np.minimum(1, x / .006)
        return (np.sin(2 * np.pi * f * x) + .45 * np.sin(4 * np.pi * f * x) * np.exp(-x / .4) + .2 * np.sin(6 * np.pi * f * x) * np.exp(-x / .25)) * e * g
    chords = [(220.0, 261.6, 329.6), (174.6, 220.0, 261.6), (130.8, 196.0, 261.6), (196.0, 246.9, 293.7)]   # Am F C G
    beat = 0.62; k = 0
    t = 0.0
    while t < DUR - 2:
        ch = chords[(k // 4) % 4]; note = ch[k % 3] * (2 if k % 4 == 3 else 1)
        loud = .05 if A_OFF < t < 13.9 or B_OFF < t < END_T else .085      # duck under dialogue
        add(piano(note, 2.5, loud), t)
        if k % 4 == 0: add(piano(ch[0] / 2, 3.5, loud * 1.2), t)
        t += beat; k += 1
    for f in (523.3, 659.3, 784.0): add(piano(f, 4, .05), B_OFF + 4.95)      # gift reveal shimmer
    for f in (130.8, 196.0, 261.6, 329.6): add(piano(f, 5, .06), END_T)
    out = np.tanh(out * 1.4) * .7; fade = np.ones(n); fade[-int(1.2 * SR):] = np.linspace(1, 0, int(1.2 * SR)); out *= fade
    import scipy.io.wavfile as wf; wf.write(path, SR, (np.stack([out, np.roll(out, 120)], 1) * 32767).astype(np.int16))

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True); only = os.environ.get("ONLY")
    ts = [float(x) for x in only.split(",")] if only else [i / FPS for i in range(int(DUR * FPS))]
    for t in ts: frame(t).save(OUT + (f"t_{t:05.2f}.jpg" if only else f"{int(round(t * FPS)):04d}.jpg"), quality=92)
    if not only:
        audio(OUT + "a.wav")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", OUT + "%04d.jpg", "-i", OUT + "a.wav", "-c:v", "libx264", "-pix_fmt", "yuv420p",
                        "-crf", "19", "-preset", "medium", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest", D + "bhaidooj_ghar_ki_khushboo.mp4"], check=True)
        print("ok")

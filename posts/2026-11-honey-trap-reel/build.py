"""Reel: 'Someone got past security.'  Spy-thriller nod to the honey-trap news (Tannay 10 Nov: names the "Chinese spy"; no person named).
Miss Poem extrait de parfum. Tannay stills (10 Nov 2026, AI-generated -> isAiGenerated true). 1080x1920, 30 fps, ~24 s.
Sound design is all synthesized: drone, heartbeat, CCTV clicks, typewriter, stamp, stinger. No prices.
Usage: python3 build.py WORKDIR   (ONLY=1.0,8.0 for stills)"""
import math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance, ImageChops

D = os.path.dirname(os.path.abspath(__file__)) + "/"
R = D + "../../"
OUT = sys.argv[1].rstrip("/") + "/" if len(sys.argv) > 1 else "/tmp/spy/"
LOGO = Image.open(R + "assets/cutouts/logo_gold.png").convert("RGBA")
W, H, FPS = 1080, 1920, 30
GOLD, IVORY, RED, GREEN = (226, 186, 112), (250, 244, 236), (225, 38, 38), (120, 255, 160)

def inter(s, w="Black"): return ImageFont.truetype(f"/usr/share/fonts/opentype/inter/InterDisplay-{w}.otf", s)
def pop(s, w="Bold"): return ImageFont.truetype(f"/usr/share/fonts/truetype/google-fonts/Poppins-{w}.ttf", s)
def mono(s): return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", s)
def mono_b(s): return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", s)
def tw_font(s): return ImageFont.truetype("/usr/share/texmf/fonts/opentype/public/lm/lmmono10-regular.otf", s)
def cl(x): return max(0.0, min(1.0, x))
def ss(x): x = cl(x); return x * x * (3 - 2 * x)
def back(x): x = cl(x); c = 1.9; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2

# (src, t0, t1, z0, z1, focus0, focus1, look)   look: cctv | film
SHOTS = [
    ("01", 0.0, 2.5, 1.00, 1.10, (.5, .5), (.42, .42), "cctv"),   # corridor CCTV
    ("12", 2.5, 4.7, 1.00, 1.12, (.5, .55), (.6, .66), "film"),   # empty CEO office, push to chip
    ("11", 4.7, 6.8, 1.08, 1.00, (.55, .55), (.55, .55), "film"), # gloved hand, CLASSIFIED
    ("10", 6.8, 9.2, 1.00, 1.30, (.5, .5), (.55, .5), "film"),    # surveillance photo, zoom into red circle
    ("08", 9.2, 11.2, 1.10, 1.00, (.6, .5), (.6, .5), "film"),    # macro label, laser dot
    ("07", 11.2, 14.4, 1.00, 1.06, (.45, .65), (.45, .7), "film"),# typewriter + report
    ("05", 14.4, 16.0, 1.00, 1.08, (.5, .4), (.5, .35), "film"),  # macro cap, smoke
    ("03", 16.0, 18.2, 1.04, 1.00, (.5, .5), (.5, .5), "film"),   # stamp on the file
    ("09", 18.2, 20.6, 1.10, 1.00, (.5, .55), (.5, .55), "film"), # hero, city bar
]
END = 20.6
DUR = END + 4.2
CUTS = [s[1] for s in SHOTS[1:]] + [END]

_src = {}
def src(name):
    if name not in _src:
        im = Image.open(D + f"src/{name}.png").convert("RGB")
        s = max(W * 1.15 / im.width, H * 1.15 / im.height)
        _src[name] = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    return _src[name]

def shot_frame(sh, t):
    name, t0, t1, z0, z1, f0, f1, look = sh
    u = ss((t - t0) / (t1 - t0)); z = z0 + (z1 - z0) * u
    fx = f0[0] + (f1[0] - f0[0]) * u; fy = f0[1] + (f1[1] - f0[1]) * u
    im = src(name); base = min(im.width / W, im.height / H)   # px per output px at z=1
    cw, ch = W * base / z, H * base / z
    cx, cy = fx * im.width, fy * im.height
    x0 = min(max(cx - cw / 2, 0), im.width - cw); y0 = min(max(cy - ch / 2, 0), im.height - ch)
    return im.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch))

rng = np.random.default_rng(9)
NOISE = [Image.fromarray((rng.normal(0, 1, (H // 2, W // 2)) * 18 + 128).clip(0, 255).astype(np.uint8)).resize((W, H)) for _ in range(6)]
SCAN = Image.new("L", (W, H), 0); _d = ImageDraw.Draw(SCAN)
for y in range(0, H, 4): _d.line((0, y, W, y), fill=40)
yy, xx = np.mgrid[0:H, 0:W]
VIG = Image.fromarray((np.clip(((xx - W / 2) / (W * .7)) ** 2 + ((yy - H / 2) / (H * .62)) ** 2, 0, 1) * 210).astype(np.uint8))

def grade(im, look, t):
    if look == "cctv":
        g = ImageEnhance.Contrast(im.convert("L")).enhance(1.15)
        im = Image.merge("RGB", (g.point(lambda v: int(v * .55)), g, g.point(lambda v: int(v * .65))))
        im = Image.blend(im, Image.merge("RGB", [NOISE[int(t * 24) % 6]] * 3), 0.16)
        im = Image.composite(Image.new("RGB", im.size, (0, 0, 0)), im, SCAN)
    else:
        im = ImageEnhance.Contrast(im).enhance(1.06)
        im = Image.blend(im, Image.merge("RGB", [NOISE[int(t * 24) % 6]] * 3), 0.05)
    im = Image.composite(Image.new("RGB", im.size, (0, 0, 0)), im, VIG)
    return im

def map_pt(name, t, px, py):
    """Where a point given as a fraction of the source image lands in the output frame at time t."""
    sh = [x for x in SHOTS if x[0] == name][0]
    _, t0, t1, z0, z1, f0, f1, _l = sh
    u = ss((t - t0) / (t1 - t0)); z = z0 + (z1 - z0) * u
    fx = f0[0] + (f1[0] - f0[0]) * u; fy = f0[1] + (f1[1] - f0[1]) * u
    im = src(name); base = min(im.width / W, im.height / H); cw, ch = W * base / z, H * base / z
    x0 = min(max(fx * im.width - cw / 2, 0), im.width - cw); y0 = min(max(fy * im.height - ch / 2, 0), im.height - ch)
    return (px * im.width - x0) / cw * W, (py * im.height - y0) / ch * H

def plate(t):
    act = [s for s in SHOTS if s[1] <= t < s[2]] or [SHOTS[-1]]
    sh = act[0]; im = grade(shot_frame(sh, t), sh[7], t)
    # glitch on cuts: RGB split + jitter for 0.12 s
    for tc in CUTS:
        u = t - tc
        if 0 <= u < 0.14:
            k = int(26 * (1 - u / 0.14)); r, g, b = im.split()
            im = Image.merge("RGB", (ImageChops.offset(r, k, 0), g, ImageChops.offset(b, -k, 0)))
            band = int(rng.integers(0, H - 200)); strip = im.crop((0, band, W, band + 160)); im.paste(strip, (int(rng.integers(-60, 60)), band))
    return im.convert("RGBA")

# ---------- text helpers ----------
def tlay(s, f, col, a=1.0, stroke=0):
    lay = Image.new("RGBA", (W, 400)); ImageDraw.Draw(lay).text((W / 2, 40), s, font=f, fill=col + (int(255 * a),), anchor="ma", stroke_width=stroke, stroke_fill=(0, 0, 0, int(200 * a)))
    bb = lay.getbbox(); return lay.crop(bb) if bb else None

def ctext(im, y, s, f, col, a, blur=12, scale=1.0):
    if a <= 0: return
    lay = tlay(s, f, col, a)
    if lay is None: return
    if scale != 1: lay = lay.resize((max(1, int(lay.width * scale)), max(1, int(lay.height * scale))), Image.LANCZOS)
    sh = Image.new("RGBA", lay.size, (0, 0, 0, 0)); sh.putalpha(lay.getchannel("A").point(lambda v: int(v * .9)))
    pad = blur * 3; big = Image.new("RGBA", (lay.width + 2 * pad, lay.height + 2 * pad)); big.alpha_composite(sh, (pad, pad))
    x = (W - lay.width) // 2
    im.alpha_composite(big.filter(ImageFilter.GaussianBlur(blur)), (x - pad, int(y) - pad + 5)); im.alpha_composite(lay, (x, int(y)))

def typed(s, t, t0, cps=22):
    n = int(max(0, t - t0) * cps); return s[:n] + ("█" if (n < len(s) and int(t * 6) % 2 == 0) else "")

def win(t, a, b, fi=0.25, fo=0.2): return ss((t - a) / fi) * (1 - ss((t - (b - fo)) / fo))

def cctv_hud(im, t):
    d = ImageDraw.Draw(im); f = mono_b(34)
    if int(t * 2) % 2 == 0: d.ellipse((60, 250, 88, 278), fill=RED + (255,))
    d.text((104, 264), "REC", font=f, fill=(255, 255, 255, 235), anchor="lm")
    secs = 13 * 60 + 7 + t * 1.0
    d.text((W - 60, 264), f"02:{int(secs // 60):02d}:{int(secs % 60):02d}", font=f, fill=(255, 255, 255, 235), anchor="rm")
    d.text((60, H - 330), "CAM 07 · FLOOR 21 · EXEC WING", font=mono(30), fill=(220, 255, 230, 200))

def reticle(im, t, cx, cy, r, a):
    lay = Image.new("RGBA", im.size); d = ImageDraw.Draw(lay); c = RED + (int(255 * a),)
    rr = r * (1.6 - 0.6 * ss((t - 9.4) / 0.35))
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = cx + sx * rr, cy + sy * rr
            d.line((x, y, x - sx * 60, y), fill=c, width=6); d.line((x, y, x, y - sy * 60), fill=c, width=6)
    d.line((cx - 26, cy, cx + 26, cy), fill=c, width=3); d.line((cx, cy - 26, cx, cy + 26), fill=c, width=3)
    im.alpha_composite(lay)

# ---------- scenes ----------
def overlays(im, t):
    if t < 2.5:
        cctv_hud(im, t)
        ctext(im, 420, "A Chinese spy", inter(96), IVORY, win(t, 0.15, 2.5, 0.12), scale=1 + 0.25 * (1 - back(t / 0.3)))
        ctext(im, 530, "got past his security.", inter(86), IVORY, win(t, 0.55, 2.5, 0.12))
    elif t < 4.7:
        ctext(im, 380, "No break-in.", inter(84), IVORY, win(t, 2.6, 4.7))
        ctext(im, 485, "No hacking.", inter(84), IVORY, win(t, 3.3, 4.7))
    elif t < 6.8:
        ctext(im, 380, "Just one clue", inter(84), IVORY, win(t, 4.8, 6.8))
        ctext(im, 485, "left behind...", inter(84), IVORY, win(t, 5.4, 6.8))
    elif t < 9.2:
        ctext(im, 330, "EVIDENCE #47", mono_b(48), (255, 210, 120), win(t, 6.9, 9.2))
        ctext(im, 410, "Hotel bar. 11:52 PM.", inter(78, "ExtraBold"), IVORY, win(t, 7.3, 9.2))
    elif t < 11.2:
        cx, cy = map_pt("08", t, 583 / 941, 843 / 1672); reticle(im, t, cx, cy, 120, ss((t - 9.3) / 0.2))
        a = win(t, 9.75, 11.2, 0.1)
        if a > 0:
            f = mono_b(54); lab = "TARGET IDENTIFIED"; d = ImageDraw.Draw(im); tw = d.textlength(lab, font=f)
            lay = Image.new("RGBA", im.size); dl = ImageDraw.Draw(lay)
            blink = 1.0 if int(t * 5) % 2 == 0 else 0.75
            dl.rectangle(((W - tw) / 2 - 30, 300, (W + tw) / 2 + 30, 390), fill=RED + (int(230 * a * blink),))
            dl.text((W / 2, 345), lab, font=f, fill=(255, 255, 255, int(255 * a)), anchor="mm"); im.alpha_composite(lay)
    elif t < 14.4:
        # typed intel report on a paper card (top), synced to typewriter sound
        a = ss((t - 11.3) / 0.25) * (1 - ss((t - 14.2) / 0.2))
        if a > 0:
            card = Image.new("RGBA", (900, 430), (238, 228, 205, int(240 * a))); d = ImageDraw.Draw(card)
            f = tw_font(46); fb = tw_font(52)
            lines = [("CODENAME:", "MISS POEM", 11.35), ("NOTES:", "floral, sweet, elegant", 12.0), ("EFFECT:", "impossible to forget", 12.85)]
            y = 40
            for k, v, t0 in lines:
                txt = typed(k + " " + v, t, t0, 26)
                d.text((44, y), txt, font=fb if k == "CODENAME:" else f, fill=(30, 22, 18, int(255 * a))); y += 110
            card = card.rotate(-1.5, expand=True, resample=Image.BICUBIC)
            sh = Image.new("RGBA", card.size, (0, 0, 0, 0)); sh.putalpha(card.getchannel("A").point(lambda v: int(v * .6)))
            im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)), (88, 300)); im.alpha_composite(card, (80, 290))
    elif t < 16.0:
        ctext(im, 380, "Nobody resisted.", inter(90), IVORY, win(t, 14.5, 16.0))
    elif t < 18.2:
        ctext(im, 300, "VERDICT", mono_b(52), (255, 210, 120), win(t, 16.1, 18.2))
        u = t - 16.65
        if u > 0:  # stamp slams onto the empty page
            s = 0.62 + 1.0 * (1 - back(u / 0.18)); a = ss(u / 0.06) * (1 - ss((t - 18.0) / 0.2))
            st = Image.new("RGBA", (620, 170)); ds = ImageDraw.Draw(st)
            ds.rounded_rectangle((6, 6, 614, 164), 12, outline=RED + (235,), width=10)
            ds.text((310, 88), "IRRESISTIBLE", font=inter(84), fill=RED + (235,), anchor="mm")
            st = st.rotate(9, expand=True, resample=Image.BICUBIC)
            st = st.resize((int(st.width * s), int(st.height * s)), Image.LANCZOS)
            st.putalpha(st.getchannel("A").point(lambda v: int(v * a * 0.92)))
            sx, sy = map_pt("03", t, 0.675, 0.53); im.alpha_composite(st, (int(sx - st.width / 2), int(sy - st.height / 2)))
    elif t < END:
        ctext(im, 330, "MISSION:", inter(80), IVORY, win(t, 18.3, END))
        ctext(im, 430, "IRRESISTIBLE.", inter(112), GOLD, win(t, 18.55, END, 0.12), scale=1 + 0.3 * (1 - back((t - 18.55) / 0.3)))

_endbg = None
def endcard(t):
    global _endbg
    if _endbg is None:
        _endbg = ImageEnhance.Brightness(grade(shot_frame(SHOTS[-1], END), "film", END).filter(ImageFilter.GaussianBlur(20))).enhance(0.35).convert("RGBA")
    u = t - END
    im = Image.blend(plate(min(t, END - 0.01)), _endbg, ss(u / 0.5))
    lg = LOGO.resize((230, int(LOGO.height * 230 / LOGO.width)), Image.LANCZOS)
    a = ss((u - 0.2) / 0.5); lg.putalpha(lg.getchannel("A").point(lambda v: int(v * a))); im.alpha_composite(lg, ((W - 230) // 2, 380))
    ctext(im, 650, "MISS POEM", inter(92), GOLD, ss((u - 0.4) / 0.4), 8)
    ctext(im, 770, "extrait de parfum", pop(44, "Medium"), IVORY, ss((u - 0.55) / 0.4), 6)
    ctext(im, 900, "Choose your weapon.", ImageFont.truetype("/usr/share/fonts/truetype/google-fonts/Lora-Italic-Variable.ttf", 66), (240, 222, 200), ss((u - 0.8) / 0.4), 8)
    a3 = ss((u - 1.1) / 0.4)
    if a3 > 0:
        f = inter(48, "Black"); lab = "DM FOR PRICES"; d = ImageDraw.Draw(im); tw = d.textlength(lab, font=f)
        lay = Image.new("RGBA", im.size); dl = ImageDraw.Draw(lay); y = 1100
        dl.rounded_rectangle(((W - tw) / 2 - 50, y - 52, (W + tw) / 2 + 50, y + 52), 52, fill=GOLD + (255,))
        dl.text((W / 2, y), lab, font=f, fill=(40, 8, 16, 255), anchor="mm"); lay.putalpha(lay.getchannel("A").point(lambda v: int(v * a3))); im.alpha_composite(lay)
    ctext(im, 1200, "OR VISIT US AT LAJPAT NAGAR-II", pop(36, "Bold"), (226, 180, 110), ss((u - 1.3) / 0.4), 6)
    return im

def frame(t):
    if t >= END: im = endcard(t)
    else:
        im = plate(t); overlays(im, t)
    if t < 0.25: im = Image.blend(Image.new("RGBA", im.size, (0, 0, 0, 255)), im, ss(t / 0.25))
    if t > DUR - 0.5: im = Image.blend(im, Image.new("RGBA", im.size, (0, 0, 0, 255)), ss((t - DUR + 0.5) / 0.5))
    return im.convert("RGB")

# ---------- audio ----------
SR = 44100
def audio(path):
    from scipy.signal import lfilter
    n = int(SR * DUR); out = np.zeros((n, 2), np.float32); r = np.random.default_rng(4); tt = np.arange(n) / SR
    def add(sig, at, g=1.0, pan=0.0):
        i = int(at * SR); j = min(n, i + len(sig))
        if i >= n or j <= i: return
        s = sig[: j - i] * g; out[i:j, 0] += s * (1 - pan); out[i:j, 1] += s * (1 + pan)
    def env(L, a=.003, rel=.15): x = np.arange(int(L * SR)) / SR; return np.minimum(1, x / a) * np.exp(-x / rel)
    # low drone with slow beating + rising tension until END
    drone = (np.sin(2 * np.pi * 55 * tt) + .6 * np.sin(2 * np.pi * 55.7 * tt) + .35 * np.sin(2 * np.pi * 82.4 * tt)) * 0.09
    rise = np.clip(tt / END, 0, 1) ** 2; drone *= (0.6 + 0.6 * rise) * (tt < END + 0.05)
    out[:, 0] += drone; out[:, 1] += drone
    # high string-like tension (filtered noise) creeping in
    hs = lfilter([1], [1, -0.995], r.normal(0, 1, n)); hs = lfilter([1, -1], [1, -0.7], hs); hs = hs / np.abs(hs).max() * 0.05 * rise * (tt < END)
    out[:, 0] += hs; out[:, 1] += np.roll(hs, 200)
    # heartbeat, speeding up from 62 to 118 bpm until END
    def thump(): x = np.arange(int(.25 * SR)) / SR; return np.sin(2 * np.pi * (45 + 40 * np.exp(-x / .03)) * x) * env(.25, .003, .07)
    t = 1.0
    while t < END - 0.3:
        add(thump(), t, 0.9); add(thump(), t + 0.17, 0.55)
        bpm = 62 + 56 * (t / END) ** 1.5; t += 60 / bpm
    # CCTV relay clicks at start
    clk = r.normal(0, 1, int(.01 * SR)) * env(.01, .0005, .002)
    for k in range(5): add(clk, 0.05 + k * 0.5, 0.25)
    # camera shutter / glitch on every cut
    for tc in CUTS:
        sh = lfilter([1, -1], [1, -0.4], r.normal(0, 1, int(.09 * SR))) * env(.09, .001, .02); add(sh, tc, 0.35)
        gl = np.sign(np.sin(2 * np.pi * 900 * np.arange(int(.08 * SR)) / SR)) * env(.08, .001, .03) * 0.06; add(gl, tc + .01, 1, 0.3)
    # reticle lock beeps
    for k in range(3): add(np.sin(2 * np.pi * 2200 * np.arange(int(.07 * SR)) / SR) * env(.07, .002, .03), 9.35 + k * 0.14, 0.18)
    add(np.sin(2 * np.pi * 1600 * np.arange(int(.35 * SR)) / SR) * env(.35, .002, .2), 9.78, 0.16)
    # typewriter clacks synced to typed text + carriage bell
    for k_, v_, t0 in [("CODENAME:", "MISS POEM", 11.35), ("NOTES:", "floral, sweet, elegant", 12.0), ("EFFECT:", "impossible to forget", 12.85)]:
        L = len(k_ + " " + v_)
        for c in range(L):
            if (k_ + " " + v_)[c] == " ": continue
            ck = lfilter([1, -1], [1, -0.2], r.normal(0, 1, int(.025 * SR))) * env(.025, .0005, .006)
            add(ck, t0 + c / 26 + r.uniform(-.006, .006), 0.32, r.uniform(-.2, .2))
    add(np.sin(2 * np.pi * 2637 * np.arange(int(.6 * SR)) / SR) * env(.6, .001, .25), 14.0, 0.08)
    # stamp slam
    add(thump(), 16.83, 2.2); add(lfilter([1], [1, -0.9], r.normal(0, 1, int(.12 * SR))) * env(.12, .001, .03), 16.83, 0.25)
    # final stinger + resolve
    x = np.arange(int(3.5 * SR)) / SR
    for f in (55, 110, 164.8, 220, 261.6):
        add(np.sin(2 * np.pi * f * x) * env(3.5, .005, 1.2) * 0.12, 18.2)
    br = lfilter([1], [1, -0.98], r.normal(0, 1, int(1.2 * SR))) * np.linspace(0, 1, int(1.2 * SR)) ** 2 * 0.02; add(br, 17.0)   # riser
    for f in (440, 554.4, 659.3, 880):
        add(np.sin(2 * np.pi * f * np.arange(int(3 * SR)) / SR) * env(3, .3, 1.4) * 0.04, END + 0.2)
    out = np.tanh(out * 1.4)
    fd = np.ones(n); fd[-int(0.8 * SR):] = np.linspace(1, 0, int(0.8 * SR)); out *= fd[:, None]
    import scipy.io.wavfile as wf; wf.write(path, SR, (out / max(1e-9, np.abs(out).max()) * 0.89 * 32767).astype(np.int16))

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
                        "-movflags", "+faststart", "-shortest", D + "honey_trap_reel.mp4"], check=True)
        print("ok", DUR)

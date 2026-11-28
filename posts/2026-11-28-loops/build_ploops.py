"""Perfume loop Reels, set 2 (28 Nov): real bottle cutouts, seamless loops, different ideas from set 1.
  p_seesaw  0.8 s  Mr Aqua vs Miss Aqua on a gold seesaw
  p_kaleido 1.2 s  kaleidoscope: 2 rings of bottles turning opposite ways (8-fold, so a quarter turn loops)
  p_globe   1.6 s  Flora 5 inside a snow globe, snow swirling on closed orbits
  p_rain    1.6 s  it's raining bottles (each falls exactly one screen per loop)
  p_mood    2.4 s  pick your Christmas mood: bottle + colour swap on every beat
  p_stack   1.6 s  six bottles drop into a pyramid, then fly back up (boomerang)
Usage: python3 build_ploops.py WORKDIR [name,name...]"""
import math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

WORK = sys.argv[1].rstrip("/") + "/"; ONLY = sys.argv[2].split(",") if len(sys.argv) > 2 else None
D = os.path.dirname(os.path.abspath(__file__)) + "/"; sys.path.insert(0, D); _a = sys.argv; sys.argv = [_a[0], WORK]
import build_mloops as M
sys.argv = _a
B, J = M.B, M.J; W, H, SR = B.W, B.H, B.SR; GOLD, GOLD2, IVORY = B.GOLD, B.GOLD2, B.IVORY
_c = {}
def bot(n, h):
    if (n, h) not in _c: _c[(n, h)] = B.cut(n, h)
    return _c[(n, h)]

def seesaw(t, L):
    im = B.BG(t, L); B.title(im, "WHO WINS CHRISTMAS?", "Mr Aqua vs Miss Aqua", y=230)
    th = 13 * math.sin(2 * math.pi * t / L); pv = (540, 1400); half = 430; r = math.radians(th)
    d = ImageDraw.Draw(im); d.polygon([(pv[0], pv[1] - 10), (pv[0] - 120, pv[1] + 260), (pv[0] + 120, pv[1] + 260)], fill=GOLD + (255,))
    d.rectangle((pv[0] - 220, pv[1] + 260, pv[0] + 220, pv[1] + 285), fill=(120, 96, 56, 255))
    plank = Image.new("RGBA", (2 * half + 40, 34)); ImageDraw.Draw(plank).rounded_rectangle((0, 0, 2 * half + 40, 34), radius=14, fill=(236, 232, 226, 255), outline=GOLD + (255,), width=5)
    M.rot_about(im, plank, -th, half + 20, 17, pv[0], pv[1])
    for n, side in [("mraqua_perf", -1), ("missaqua_perf", 1)]:
        b = bot(n, 520); ex = pv[0] + side * (half - 90) * math.cos(r); ey = pv[1] + side * (half - 90) * math.sin(r) - 17
        M.rot_about(im, b, -th, b.width / 2, b.height, ex, ey)
    B.snow(im, t, L); return im

RING1 = ["derossa", "liita"] * 4; RING2 = ["mraqua_perf", "flora5_perf"] * 4
def kaleido(t, L):
    im = B.BG(t, L); c = (540, 1040); u = t / L
    for ring, names, rad, h, spin in [(0, RING1, 405, 250, 90), (1, RING2, 190, 140, -90)]:
        for i, n in enumerate(names):
            a = i * 45 + spin * u + (22.5 if ring else 0); b = bot(n, h)
            x = c[0] + rad * math.sin(math.radians(a)); y = c[1] - rad * math.cos(math.radians(a))
            M.rot_about(im, b, -a, b.width / 2, b.height / 2, x, y)
    lg = Image.open(B.R + "assets/cutouts/logo_gold.png").convert("RGBA"); lg = lg.resize((150, int(150 * lg.height / lg.width)), Image.LANCZOS)
    im.alpha_composite(lg, (c[0] - lg.width // 2, c[1] - lg.height // 2))
    B.title(im, "STARE FOR 3 SECONDS", None, y=230); J.text(im, 1720, "then comment the one you saw first", J.BOD(58), GOLD2); return im

GL = [(np.random.default_rng(i).uniform(40, 360), np.random.default_rng(i + 99).uniform(0, 6.28), np.random.default_rng(i + 7).choice([-2, -1, 1, 2]),
       np.random.default_rng(i + 3).uniform(4, 10)) for i in range(110)]
def globe(t, L):
    im = B.BG(t, L); B.title(im, "CHRISTMAS, BOTTLED", "Flora 5", y=230); c = (540, 1020); R = 400; u = t / L
    d = ImageDraw.Draw(im); d.polygon([(c[0] - 300, c[1] + 360), (c[0] + 300, c[1] + 360), (c[0] + 360, c[1] + 560), (c[0] - 360, c[1] + 560)], fill=(70, 40, 20, 255))
    d.rectangle((c[0] - 360, c[1] + 540, c[0] + 360, c[1] + 580), fill=GOLD + (255,)); d.rectangle((c[0] - 300, c[1] + 352, c[0] + 300, c[1] + 372), fill=GOLD + (255,))
    inner = Image.new("RGBA", (W, H)); idr = ImageDraw.Draw(inner); idr.ellipse((c[0] - R, c[1] - R, c[0] + R, c[1] + R), fill=(14, 40, 28, 255))
    b = bot("flora5_perf", 420); inner.alpha_composite(b, (c[0] - b.width // 2, c[1] + 330 - b.height))
    sn = Image.new("RGBA", (W, H)); sd = ImageDraw.Draw(sn)
    for rr, ph, k, s in GL:
        a = ph + 2 * math.pi * k * u; x = c[0] + rr * math.cos(a); y = c[1] + rr * .8 * math.sin(a) + 30 * math.sin(2 * math.pi * u + ph)
        sd.ellipse((x - s, y - s, x + s, y + s), fill=(250, 252, 255, 220))
    inner.alpha_composite(sn)
    mask = Image.new("L", (W, H), 0); ImageDraw.Draw(mask).ellipse((c[0] - R, c[1] - R, c[0] + R, c[1] + R), fill=255); inner.putalpha(Image.fromarray(np.minimum(np.asarray(inner.getchannel("A")), np.asarray(mask))))
    im.alpha_composite(inner)
    gl = Image.new("RGBA", (W, H)); gd = ImageDraw.Draw(gl); gd.ellipse((c[0] - R, c[1] - R, c[0] + R, c[1] + R), outline=(255, 255, 255, 90), width=6)
    gd.arc((c[0] - R + 50, c[1] - R + 50, c[0] + R - 50, c[1] + R - 50), 200, 250, fill=(255, 255, 255, 150), width=22); im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(2)))
    B.snow(im, t, L); return im

RAINN = ["derossa", "moksha", "liita", "flora5_perf", "mraqua_perf", "missaqua_perf"] * 3
RA = [(np.random.default_rng(i).uniform(110, 970), i / 18 + np.random.default_rng(i + 50).uniform(-.02, .02), np.random.default_rng(i + 9).choice([-1, 1]),
       np.random.default_rng(i + 21).uniform(0, 360), np.random.default_rng(i + 4).uniform(230, 330)) for i in range(18)]
def rain(t, L):
    im = B.BG(t, L); u = t / L
    for (x, ph, sp, a0, h), n in sorted(zip(RA, RAINN), key=lambda z: z[0][4]):
        y = -250 + (H + 500) * ((u + ph) % 1); b = bot(n, int(h)); M.rot_about(im, b, a0 + 360 * sp * u, b.width / 2, b.height / 2, x, y)
    B.snow(im, t, L)
    lay = Image.new("RGBA", (W, H)); ImageDraw.Draw(lay).rounded_rectangle((90, 160, 990, 420), radius=40, fill=(6, 14, 10, 190)); im.alpha_composite(lay)
    B.title(im, "IT'S RAINING GIFTS", "catch one", y=245); return im

MOOD = [("derossa", "DATE NIGHT", (28, 12, 12)), ("moksha", "CALM", (14, 32, 22)), ("liita", "IN LOVE", (70, 24, 40)),
        ("flora5_perf", "GOLDEN", (64, 42, 10)), ("mraqua_perf", "FRESH", (10, 48, 46)), ("missaqua_perf", "SOFT", (24, 54, 58))]
def mood(t, L):
    k = int(t / (L / 6)) % 6; u = t - k * L / 6; n, word, col = MOOD[k]
    yy, xx = np.mgrid[0:H:4, 0:W:4]; r = np.sqrt(((xx - W / 2) / W) ** 2 + ((yy - H * .5) / H) ** 2); g = np.clip(1 - r * 1.5, 0, 1)[..., None]
    im = Image.fromarray((np.array(col) * .45 + g * np.array(col) * 1.1).clip(0, 255).astype(np.uint8)).resize((W, H)).convert("RGBA")
    J.text(im, 230, "PICK YOUR CHRISTMAS MOOD", J.MS(64), IVORY)
    sc = .55 + .45 * J.back(u / .16); b = bot(n, 760); b = b.resize((max(1, int(b.width * sc)), max(1, int(b.height * sc))), Image.LANCZOS)
    M.drop_shadow(im, 380, 700, 1500, .9); im.alpha_composite(b, (540 - b.width // 2, 1500 - b.height))
    J.popt(im, 1680, word, u, J.MS(120), GOLD); B.snow(im, t, L); return im

STK = [("moksha", 315, 0), ("liita", 540, 0), ("flora5_perf", 765, 0), ("derossa", 430, 1), ("mraqua_perf", 650, 1), ("missaqua_perf", 540, 2)]
def stack(t, L):
    im = B.BG(t, L); B.title(im, "BUILD YOUR CHRISTMAS", "six scents, one tower", y=230); y0 = 1580; B.podium(im, 540, y0, 820)
    u = t / L; f = u * 2 if u < .5 else 2 - u * 2
    for i, (n, x, lvl) in enumerate(STK):
        b = bot(n, 330); base = y0 + 8 - lvl * 306; s0 = i * .13; k = J.cl((f - s0) / .2); drop = (1 - k * k) * 1700
        sq = max(0, 1 - abs(k - 1) * 8) if k > .9 else 0; bb = b.resize((int(b.width * (1 + .06 * sq)), int(b.height * (1 - .06 * sq))), Image.LANCZOS)
        if k > 0: im.alpha_composite(bb, (int(x - bb.width / 2), int(base - bb.height - drop)))
    B.snow(im, t, L); return im

B.SFX.update({"p_seesaw": [(.2, B.thud, .35), (.6, B.thud, .35)], "p_kaleido": [], "p_globe": [], "p_rain": [],
              "p_mood": [(i * .4, B.pop, .5) for i in range(6)], "p_stack": [(.13 * i / 2 * 1.6 + .16, B.thud, .4) for i in range(6)]})
JOBS = {"p_seesaw": (seesaw, .8), "p_kaleido": (kaleido, 1.2), "p_globe": (globe, 1.6), "p_rain": (rain, 1.6), "p_mood": (mood, 2.4), "p_stack": (stack, 1.6)}
if __name__ == "__main__":
    test = os.environ.get("TEST"); fps = 50
    for name, (fn, L) in JOBS.items():
        if ONLY and name not in ONLY: continue
        N = int(round(L * fps))
        if test:
            c = Image.new("RGB", (5 * 216, 384))
            for j, k in enumerate(np.linspace(0, N - 1, 5).astype(int)): c.paste(fn(k / fps, L).convert("RGB").resize((216, 384)), (j * 216, 0))
            c.save(WORK + f"{name}.jpg", quality=85); continue
        fd = WORK + f"fr_{name}/"; os.makedirs(fd, exist_ok=True)
        for i in range(N): fn(i / fps, L).convert("RGB").save(fd + f"{i:04d}.jpg", quality=93)
        B.audio(name, L, fd + "a.wav"); out = D + name
        v = ["-framerate", str(fps), "-i", fd + "%04d.jpg"]
        enc = ["-frames:v", str(N), "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p", "-r", str(fps), "-movflags", "+faststart"]
        subprocess.run(["ffmpeg", "-v", "error", "-y"] + v + ["-i", fd + "a.wav", "-map", "0:v", "-map", "1:a", "-af", f"atrim=0:{L - .045:.3f},afade=t=out:st={L - .065:.3f}:d=0.02"]
                       + enc + ["-c:a", "aac", "-b:a", "256k", out + ".mp4"], check=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y"] + v + enc + ["-an", out + "_silent.mp4"], check=True)
        print("ok", name, flush=True)

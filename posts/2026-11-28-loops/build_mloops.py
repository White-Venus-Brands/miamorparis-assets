"""Winter moisturiser loop Reels (28 Nov): Tannay's 12 studio tube shots (assets/cutouts/tubes), seamless loops.
  m_domino   1.6 s  men's row topples right, women's row topples left, then everything stands back up (boomerang)
  m_hisher   0.8 s  6 tube pairs flipping his <-> hers in a wave
  m_fan      0.8 s  12 tubes fan out like a hand of cards and close
  m_hypno    0.8 s  Moksha swinging like a hypnotist's watch over a turning spiral: 'you are getting very soft'
  m_squad    0.8 s  12 tubes doing a Mexican wave
  m_shake    1.6 s  snow piles on Smuggler, it shakes it off
Audio: Punjabi Jingle Bell drop slice of the loop length + SFX; audio ends 45 ms before the video (no black flash), + _silent.
Usage: python3 build_mloops.py WORKDIR [name,name...]"""
import math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

WORK = sys.argv[1].rstrip("/") + "/"; ONLY = sys.argv[2].split(",") if len(sys.argv) > 2 else None
D = os.path.dirname(os.path.abspath(__file__)) + "/"; sys.path.insert(0, D); _a = sys.argv; sys.argv = [_a[0], WORK]
import build_loops as B
sys.argv = _a
J = B.J; W, H, SR = B.W, B.H, B.SR; GOLD, GOLD2, IVORY = B.GOLD, B.GOLD2, B.IVORY
TUBES = B.R + "assets/cutouts/tubes/"
MEN = ["mraqua", "derossa", "marhaba", "smuggler", "holdmi", "moksha"]; WOMEN = ["missaqua", "loveair", "flora5", "ombre", "misspoem", "bouquet"]
_t = {}
def tube(n, h):
    if (n, h) not in _t:
        im = Image.open(TUBES + n + ".png").convert("RGBA"); _t[(n, h)] = im.resize((int(im.width * h / im.height), h), Image.LANCZOS)
    return _t[(n, h)]
def rot_about(im, img, ang, px, py, wx, wy):
    """paste img rotated by ang degrees (ccw) about its pixel (px,py), which lands on world (wx,wy)"""
    S = int(math.hypot(img.width, img.height) * 2) + 4; c = Image.new("RGBA", (S, S)); c.alpha_composite(img, (int(S / 2 - px), int(S / 2 - py)))
    if ang: c = c.rotate(ang, resample=Image.BICUBIC, center=(S / 2, S / 2))
    im.alpha_composite(c, (int(wx - S / 2), int(wy - S / 2)))
def drop_shadow(im, x0, x1, y, a=.8):
    lay = Image.new("RGBA", (W, H)); ImageDraw.Draw(lay).ellipse((x0, y - 14, x1, y + 14), fill=(0, 0, 0, int(140 * a))); im.alpha_composite(lay.filter(ImageFilter.GaussianBlur(10)))
def shelf(im, y, x0=40, x1=W - 40):
    d = ImageDraw.Draw(im); d.rectangle((x0, y, x1, y + 22), fill=GOLD + (255,)); d.rectangle((x0, y + 22, x1, y + 34), fill=(120, 96, 56, 255))

def domino(t, L):
    im = B.BG(t, L); B.title(im, "DRY SKIN:", "knocked out for winter", y=230)
    u = t / L; f = u * 2 if u < .5 else 2 - u * 2                    # 0 -> 1 -> 0 (boomerang)
    f = J.ss(f / .9)
    for row, names, y, dirn in [(0, MEN, 1020, -1), (1, WOMEN, 1640, 1)]:
        shelf(im, y); h = 330; sp = 172; x0 = 540 - sp * 2.5
        tubes = [tube(n, h) for n in names]; order = list(range(6)) if dirn < 0 else list(range(5, -1, -1))
        for rank, i in enumerate(order):                                   # each one starts when the previous reaches it
            b = tubes[i]; k = J.cl((f * 6 * .62 - rank * .55) / .9); ang = 78 * (k ** 1.8) * dirn
            cx = x0 + sp * i; px = b.width if dirn < 0 else 0
            rot_about(im, b, ang, px, b.height, cx + (b.width / 2 if dirn < 0 else -b.width / 2), y)
    B.snow(im, t, L); return im

PAIRS = list(zip(MEN, WOMEN))
def hisher(t, L):
    im = B.BG(t, L); B.title(im, "HIS OR HERS?", "pick your side", y=210)
    for k, (m, w) in enumerate(PAIRS):
        cx = 190 + (k % 3) * 350; cy = 650 + (k // 3) * 690
        ph = 2 * math.pi * (t / L - k * .06); c = math.cos(ph); b = tube(m if c >= 0 else w, 540)
        sx = max(.03, abs(c)); bb = b.resize((max(2, int(b.width * sx)), b.height), Image.LANCZOS)
        drop_shadow(im, cx - 90, cx + 90, cy + 300); im.alpha_composite(bb, (int(cx - bb.width / 2), int(cy + 300 - bb.height)))
        lab = "HIS" if c >= 0 else "HERS"; J.text(im, cy + 345, lab, J.MS(40), GOLD if c >= 0 else GOLD2)
    B.snow(im, t, L); return im

def fan(t, L):
    im = B.BG(t, L); B.title(im, "PICK ONE", "no wrong answers this winter", y=230)
    f = math.sin(math.pi * t / L) ** 2; names = [x for p in PAIRS for x in p]
    for i, n in enumerate(names):
        b = tube(n, 720); ang = (i - 5.5) / 5.5 * 58 * f
        rot_about(im, b, -ang, b.width / 2, b.height, 540, 1640)
    B.snow(im, t, L); return im

_sp = {}
def spiral(t, L, n=6):
    key = round(t, 4)
    if key not in _sp:
        yy, xx = np.mgrid[0:H:2, 0:W:2].astype(np.float32); dx, dy = xx - W / 2, yy - 1000; r = np.hypot(dx, dy); th = np.arctan2(dy, dx)
        v = np.sin(n * th + r * .025 - 2 * math.pi * t / L)                 # n arms, one arm-period per loop -> seamless
        k = (v > 0).astype(np.float32) * np.clip(1 - r / 1500, 0, 1)[..., None][..., 0]
        a = np.zeros(xx.shape + (4,), np.uint8); a[..., :3] = GOLD; a[..., 3] = (k * 55).astype(np.uint8)
        _sp[key] = Image.fromarray(a).resize((W, H), Image.BILINEAR)
    return _sp[key]
def hypno(t, L):
    im = B.BG(t, L); im.alpha_composite(spiral(t, L)); B.title(im, "YOU ARE GETTING", None, y=200); J.text(im, 300, "VERY SOFT.", J.MS(96), GOLD)
    th = math.radians(24) * math.sin(2 * math.pi * t / L); pv = (540, 420); Ls = 620
    tx, ty = pv[0] + Ls * math.sin(th), pv[1] + Ls * math.cos(th)
    d = ImageDraw.Draw(im); d.line((pv[0], pv[1], tx, ty), fill=GOLD2 + (255,), width=5); d.ellipse((pv[0] - 12, pv[1] - 12, pv[0] + 12, pv[1] + 12), fill=GOLD + (255,))
    b = tube("moksha", 560); rot_about(im, b, -math.degrees(th) * -1, b.width / 2, 0, tx, ty)
    J.text(im, 1760, "keep watching the tube...", J.BOD(60), GOLD2); return im

def squad(t, L):
    im = B.BG(t, L); B.title(im, "THE WINTER SQUAD", "12 tubes, one season", y=230)
    for row, names, y in [(0, MEN, 1060), (1, WOMEN, 1700)]:
        shelf(im, y)
        for i, n in enumerate(names):
            k = row * 6 + i; ph = (t / L - k / 12) % 1; hop = max(0, math.sin(2 * math.pi * ph)) ; up = 170 * hop ** .8
            sq = max(0, -math.sin(2 * math.pi * ph)); b = tube(n, 440); bb = b.resize((int(b.width * (1 + .05 * sq)), int(b.height * (1 - .05 * sq))), Image.LANCZOS)
            cx = 540 + (i - 2.5) * 165; drop_shadow(im, cx - 70 + up * .2, cx + 70 - up * .2, y, 1 - .6 * hop)
            im.alpha_composite(bb, (int(cx - bb.width / 2), int(y - bb.height - up)))
    B.snow(im, t, L); return im

FLY = [(np.random.default_rng(3).uniform(-1, 1), np.random.default_rng(i).uniform(.3, 1)) for i in range(40)]
def shake(t, L):
    im = B.BG(t, L); y0 = 1520; B.podium(im, 540, y0); B.title(im, "SHAKE OFF WINTER", "Smuggler, ready", y=230)
    b = tube("smuggler", 900); u = t / L; pile = J.ss(u / .78); shk = J.cl((u - .78) / .12) * (1 - J.cl((u - .9) / .1))
    ang = 9 * math.sin(2 * math.pi * 7 * (u - .78)) * shk if .78 < u < 1 else 0
    top = y0 + 10 - b.height; cx = 540
    can = Image.new("RGBA", (b.width + 80, b.height + 120)); can.alpha_composite(b, (40, 120))
    if u < .8:                                                           # snow cap grows on the crimp end
        cap = Image.new("L", can.size, 0); cd = ImageDraw.Draw(cap); hh = 80 * pile; w2 = b.width / 2 + 14 * pile; xc = 40 + b.width / 2
        cd.ellipse((xc - w2, 120 - hh, xc + w2, 120 + hh * .45), fill=255)
        for j in range(7): x = xc + (j - 3) / 3 * w2 * .7; r = 36 * pile; cd.ellipse((x - r, 120 - hh * .75 - r * .5, x + r, 120 - hh * .75 + r * .9), fill=255)
        cap = cap.filter(ImageFilter.GaussianBlur(2.5)); sn = Image.new("RGBA", can.size, (246, 249, 255, 255)); sn.putalpha(cap)
        shade = Image.new("RGBA", can.size, (200, 210, 225, 0)); can.alpha_composite(sn)
    rot_about(im, can, ang, can.width / 2, can.height, cx, y0 + 10)
    if .8 <= u:                                                          # flung snow
        k = J.cl((u - .8) / .2); d = ImageDraw.Draw(im)
        for i in range(40):
            rng = np.random.default_rng(i); vx = rng.uniform(-1, 1) * 520; vy = -rng.uniform(150, 600); r = rng.uniform(6, 16)
            x = cx + vx * k; y = top - 40 + vy * k + 900 * k * k
            d.ellipse((x - r, y - r, x + r, y + r), fill=(250, 252, 255, int(255 * (1 - k))))
    B.snow(im, t, L); return im

B.SFX.update({"m_domino": [(.12 + .1 * i, B.click, .35) for i in range(6)], "m_hisher": [], "m_fan": [(.05, B.whoosh, .3), (.45, B.whoosh, .3)],
              "m_hypno": [], "m_squad": [], "m_shake": [(1.27, B.whoosh, .5), (1.33, B.whoosh, .4)]})
JOBS = {"m_domino": (domino, 1.6), "m_hisher": (hisher, .8), "m_fan": (fan, .8), "m_hypno": (hypno, .8), "m_squad": (squad, .8), "m_shake": (shake, 1.6)}
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

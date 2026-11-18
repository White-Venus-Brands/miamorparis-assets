"""v2: same Marhaba 'still wearing yellow' edit, using Tannay's 8-panel grid (src/grid.png).
NOTE: the grid images look AI-generated -> tick Instagram's AI label if asked. Usage: python3 build2.py OUTDIR"""
import os, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter
import build as B
from build import W, H, FPS, YEL, GOLD, IVORY, ctext, inter, lora, ss, back, win, LOGO

D = B.D; OUT = (sys.argv[1].rstrip("/") + "/") if len(sys.argv) > 1 else "/tmp/my2/"
os.makedirs(OUT + "f", exist_ok=True)
G = Image.open(D + "src/grid.png").convert("RGB")
XS, YS = [0, 333, 666, 999, 1330], [0, 590, 1182]
def panel(i):
    r, c = divmod(i, 4)
    p = G.crop((XS[c] + 3, YS[r] + 3, XS[c + 1] - 3, YS[r + 1] - 3))
    p = p.resize((W, int(W * p.height / p.width)), Image.LANCZOS).filter(ImageFilter.UnsharpMask(3, 60, 2))
    if p.height < H: p = p.resize((int(p.width * H / p.height), H), Image.LANCZOS)
    return p
P = [panel(i) for i in range(8)]
P[6] = P[6].crop((0, 0, P[6].width, int(P[6].height * .78))).resize((int(P[6].width * H / (P[6].height * .78)), H), Image.LANCZOS)  # keep the mist, lose most of the bottle

def kb(i, p, zoom=.08, dy=0):
    im = P[i]; s = 1 + zoom * p; w, h = int(W * s * im.width / W), int(H * s * im.height / H)
    z = im.resize((max(w, W), max(h, H)), Image.LANCZOS)
    x0 = (z.width - W) // 2; y0 = int((z.height - H) // 2 + dy * p)
    return z.crop((x0, y0, x0 + W, y0 + H)).convert("RGBA")
_g = Image.new("L", (1, H))
for _y in range(H): _g.putpixel((0, _y), int(170 * max(1 - _y / 520, (_y - (H - 560)) / 560, 0)))
SHADE = Image.merge("RGBA", [Image.new("L", (W, H), 0)] * 3 + [_g.resize((W, H))])
def shade(im):
    im.alpha_composite(SHADE); return im

CUTS = [(0, 3.3), (1, 6.3), (2, 8.6), (3, 10.4), (5, 12.0), (4, 13.1), (6, 15.0), (7, 18.0)]
END = CUTS[-1][1]
def frame(t):
    k = next(n for n, (_, e) in enumerate(CUTS) if t < e or n == len(CUTS) - 1)
    t0 = 0 if k == 0 else CUTS[k - 1][1]; i, t1 = CUTS[k]; p = (t - t0) / (t1 - t0)
    im = shade(kb(i, p))
    if k and t - t0 < .12: im.alpha_composite(Image.new("RGBA", (W, H), (255, 245, 210, int(200 * (1 - (t - t0) / .12)))))
    if k == 0:
        ctext(im, 150, "The most famous", inter(78), IVORY, win(t, .3, t1, .2))
        ctext(im, 245, "yellow jersey", inter(96), YEL, win(t, .5, t1, .2), scale=1 + .15 * (1 - back((t - .5) / .35)))
        ctext(im, 1640, "just retired.", inter(96), IVORY, win(t, 1.3, t1, .2), scale=1 + .15 * (1 - back((t - 1.3) / .35)))
    elif k == 1:
        ctext(im, 150, "Someone has to keep", inter(80), IVORY, win(t, t0 + .2, t1, .2))
        ctext(im, 250, "wearing yellow.", inter(96), YEL, win(t, t0 + .5, t1, .2), scale=1 + .15 * (1 - back((t - t0 - .5) / .35)))
    elif k == 2:
        ctext(im, 1620, "Reporting for duty.", inter(84), IVORY, win(t, t0 + .2, t1, .2))
    elif k == 3:
        ctext(im, 1600, "Marhaba Oudh", lora(100), YEL, win(t, t0 + .1, t1, .25))
    elif k in (4, 5):
        ctext(im, 1600, "Wash. Layer." if k == 4 else "Gift.", inter(120), YEL, 1, scale=1 + .3 * (1 - back((t - t0) / .25)))
    elif k == 6:
        ctext(im, 170, "Seven sprays.", inter(96), YEL, win(t, t0 + .1, t1, .2), scale=1 + .2 * (1 - back((t - t0 - .1) / .3)))
        ctext(im, 290, "For old times' sake.", lora(76), IVORY, win(t, t0 + .6, t1, .2))
    else:
        a = ss((t - t0 - .3) / .4)
        lg = LOGO.resize((230, int(230 * LOGO.height / LOGO.width)), Image.LANCZOS); lg.putalpha(lg.getchannel("A").point(lambda v: int(v * a)))
        ctext(im, 1560, "Still wearing yellow.", inter(80), YEL, ss((t - t0 - .5) / .4))
        ctext(im, 1700, "O-17, Lajpat Nagar-II  ·  miamorparis.in", inter(40, "Bold"), IVORY, ss((t - t0 - 1.0) / .4))
    if t > END - .5: im.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(255 * ss((t - END + .5) / .5)))))
    return im

if __name__ == "__main__":
    only = os.environ.get("ONLY")
    if only:
        for s in only.split(","): frame(float(s)).convert("RGB").save(OUT + f"still_{s}.jpg", quality=85)
        sys.exit()
    B.T2, B.T3, B.T4, B.T5, B.END = 3.4, 8.6, 13.1, 15.0, END   # reuse the music, retimed to the new cuts
    B.audio(OUT + "a.wav")
    for n in range(int(END * FPS)): frame(n / FPS).convert("RGB").save(OUT + f"f/{n:04d}.jpg", quality=92)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", OUT + "f/%04d.jpg", "-i", OUT + "a.wav",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "veryfast", "-c:a", "aac", "-b:a", "192k", "-shortest",
                    "-movflags", "+faststart", D + "marhaba_yellow_reel_v2.mp4"], check=True)
    frame(2.4).convert("RGB").save(D + "cover_v2.jpg", quality=92)
    print("done")

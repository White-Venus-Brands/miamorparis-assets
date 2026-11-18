"""v3: Marhaba 'still wearing yellow' from Tannay's 4 real photos (src/trio, jersey, window, inbox; 941x1672).
Usage: python3 build3.py OUTDIR"""
import os, subprocess, sys
from PIL import Image, ImageFilter
import build as B
from build import W, H, FPS, YEL, IVORY, ctext, inter, lora, ss, back, win
from build2 import SHADE

D = B.D; OUT = (sys.argv[1].rstrip("/") + "/") if len(sys.argv) > 1 else "/tmp/my3/"
os.makedirs(OUT + "f", exist_ok=True)
P = {k: Image.open(D + f"src/{k}.png").convert("RGB") for k in ("trio", "jersey", "window", "inbox")}   # keep source res; resample once per frame

def view(k, cx, cy, z):
    """crop centred on (cx, cy) in 0..1 coords at zoom z (1 = full frame)."""
    src = P[k]; SW, SH = src.size; w, h = SW / z, SH / z
    x0 = min(max(cx * SW - w / 2, 0), SW - w); y0 = min(max(cy * SH - h / 2, 0), SH - h)
    out = src.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + w, y0 + h), reducing_gap=None) if False else src.resize((W, H), Image.LANCZOS, box=(x0, y0, x0 + w, y0 + h))
    return out.filter(ImageFilter.UnsharpMask(1.6, 70, 1)).convert("RGBA")
def lerp(a, b, p): return a + (b - a) * p

# (photo, start view, end view, end time)   view = (cx, cy, zoom)
CUTS = [("jersey", (.82, .56, 2.6), (.80, .55, 2.2), 3.3),     # close on the 7
        ("jersey", (.62, .5, 1.6), (.5, .5, 1.0), 6.3),         # pull out: bottle on the jersey
        ("inbox", (.5, .5, 1.12), (.5, .52, 1.0), 8.6),
        ("window", (.45, .55, 1.0), (.4, .58, 1.12), 10.6),
        ("trio", (.5, .62, 1.18), (.5, .6, 1.0), 13.1),
        ("jersey", (.45, .52, 1.5), (.45, .5, 1.75), 15.2),     # bottle close-up for the seven sprays
        ("trio", (.5, .55, 1.0), (.5, .55, 1.06), 18.0)]
END = CUTS[-1][3]

def frame(t):
    k = next(n for n, c in enumerate(CUTS) if t < c[3] or n == len(CUTS) - 1)
    t0 = 0 if k == 0 else CUTS[k - 1][3]; name, a, b, t1 = CUTS[k]; p = ss((t - t0) / (t1 - t0)) if k == 1 else (t - t0) / (t1 - t0)
    im = view(name, *(lerp(a[i], b[i], p) for i in range(3))); im.alpha_composite(SHADE)
    if k > 1 and t - t0 < .12: im.alpha_composite(Image.new("RGBA", (W, H), (255, 245, 210, int(200 * (1 - (t - t0) / .12)))))
    if k == 0:
        ctext(im, 150, "The most famous", inter(78), IVORY, win(t, .3, t1 + .3, .2))
        ctext(im, 245, "yellow jersey", inter(96), YEL, win(t, .5, t1 + .3, .2), scale=1 + .15 * (1 - back((t - .5) / .35)))
        ctext(im, 1640, "just retired.", inter(96), IVORY, win(t, 1.3, t1 + .3, .2), scale=1 + .15 * (1 - back((t - 1.3) / .35)))
    elif k == 1:
        ctext(im, 150, "Someone has to keep", inter(80), IVORY, win(t, t0 + .5, t1, .2))
        ctext(im, 250, "wearing yellow.", inter(96), YEL, win(t, t0 + .8, t1, .2), scale=1 + .15 * (1 - back((t - t0 - .8) / .35)))
    elif k == 2:
        ctext(im, 1620, "Reporting for duty.", inter(84), IVORY, win(t, t0 + .2, t1, .2))
    elif k == 3:
        ctext(im, 1600, "Marhaba Oudh", lora(100), YEL, win(t, t0 + .1, t1, .25))
    elif k == 4:
        w = ["Wash.", "Spray.", "Layer."]; xs = [220, 540, 860]
        for n in range(3):
            tn = t0 + .2 + n * .55
            if t > tn:
                f = inter(84); lay = Image.new("RGBA", (W, H)); ctext(lay, 1630, w[n], f, YEL, 1, scale=1 + .3 * (1 - back((t - tn) / .25)))
                bb = lay.getbbox(); cx = (bb[0] + bb[2]) / 2; im.alpha_composite(lay, (int(xs[n] - cx), 0))
    elif k == 5:
        ctext(im, 170, "Seven sprays.", inter(96), YEL, win(t, t0 + .1, t1, .2), scale=1 + .2 * (1 - back((t - t0 - .1) / .3)))
        ctext(im, 290, "For old times' sake.", lora(76), IVORY, win(t, t0 + .6, t1, .2))
    else:
        ctext(im, 170, "Still wearing yellow.", inter(84), YEL, ss((t - t0 - .3) / .4))
        ctext(im, 1690, "O-17, Lajpat Nagar-II  ·  miamorparis.in", inter(40, "Bold"), IVORY, ss((t - t0 - .9) / .4))
    if t > END - .5: im.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(255 * ss((t - END + .5) / .5)))))
    return im

if __name__ == "__main__":
    only = os.environ.get("ONLY")
    if only:
        for s in only.split(","): frame(float(s)).convert("RGB").save(OUT + f"still_{s}.jpg", quality=85)
        sys.exit()
    B.T2, B.T3, B.T4, B.T5, B.END = 3.4, 8.6, 13.1, 15.2, END
    B.audio(OUT + "a.wav")
    for n in range(int(END * FPS)): frame(n / FPS).convert("RGB").save(OUT + f"f/{n:04d}.png", compress_level=1)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", OUT + "f/%04d.png", "-i", OUT + "a.wav",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "14", "-preset", "slow", "-profile:v", "high", "-tune", "film", "-c:a", "aac", "-b:a", "192k", "-shortest",
                    "-movflags", "+faststart", D + "marhaba_yellow_reel_v3_hq.mp4"], check=True)
    frame(5.8).convert("RGB").save(D + "cover_v3.jpg", quality=92)
    print("done")

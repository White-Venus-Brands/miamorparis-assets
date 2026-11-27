"""'Santa ki gift list': Tannay's 12 Christmas product renders (27 Nov) cut to Punjabi Jingle Bell (song 0:00-0:16.4).
Hook over the intro break, one scent per 2 beats from the drop (4.46 s) with who it's for, a 12-up grid, end card.
Usage: python3 build_gift12.py WORKDIR"""
import os, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

WORK = sys.argv[1].rstrip("/") + "/"
D = os.path.dirname(os.path.abspath(__file__)) + "/"
sys.argv = [sys.argv[0], WORK, "santa"]; sys.path.insert(0, D)
import build_jingle as J
W, H, FPS, SR, P = J.W, J.H, J.FPS, J.SR, J.P
LIST = [("flora5", "MUMMY"), ("derossa", "PAPA"), ("liita", "YOUR GIRLFRIEND"), ("moksha", "YOUR BOYFRIEND"), ("misspoem", "DIDI"), ("mraqua", "BHAI"),
        ("bouquet", "BHABHI"), ("marhaba", "CHACHU"), ("missaqua", "YOUR BESTIE"), ("smuggler", "THE BOSS"), ("holdmi", "SECRET SANTA"), ("ombre", "YOURSELF")]
D0 = J.DR[0]; T = [D0 + 2 * P * k for k in range(12)]; G0 = T[-1] + 2 * P; E0 = G0 + 4 * P; TOTAL = round((E0 + 2.4) * FPS) / FPS   # end card gets 2.4 s

_c = {}
def card(name):
    """4:5 render on a blurred 9:16 extension of itself"""
    if name not in _c:
        im = Image.open(D + f"xmas12/{name}.png").convert("RGB"); fg = im.resize((W, int(im.height * W / im.width)), Image.LANCZOS)
        bg = im.resize((int(im.width * H / im.height), H), Image.LANCZOS); bg = bg.crop(((bg.width - W) // 2, 0, (bg.width - W) // 2 + W, H)).filter(ImageFilter.GaussianBlur(40))
        bg = Image.blend(bg, Image.new("RGB", (W, H), (8, 6, 6)), .45); bg.paste(fg, (0, (H - fg.height) // 2 + 60)); _c[name] = bg
    return _c[name]
def kb(im, u, z0=1.0, z1=1.06):
    z = z0 + (z1 - z0) * J.ss(u); w, h = W / z, H / z
    return im.resize((W, H), Image.LANCZOS, box=((W - w) / 2, (H - h) / 2 + 30 * (z - 1), (W + w) / 2, (H + h) / 2 + 30 * (z - 1)))

def frame(t):
    if t < D0:   # intro break: blurred tease + hook
        im = card("moksha").filter(ImageFilter.GaussianBlur(12 * (1 - J.ss((t - 2.5) / 1.8)) + 2)).convert("RGBA")
        im.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, 120)))
        J.popt(im, 820, "SANTA KI GIFT LIST", t, J.MS(100)); J.popt(im, 950, "12 PEOPLE. 12 SCENTS.", t - .4, J.MS(70), J.GOLD)
        if t > 2.2: J.popt(im, 1060, "tag yours", t - 2.2, J.BOD(70), J.GOLD2, 0)
    elif t < G0:
        i = max(j for j, s in enumerate(T) if s <= t); u = t - T[i]; name, who = LIST[i]
        im = kb(card(name), u / (2 * P)).convert("RGBA")
        if u < .3: im = J.punch(im, u * 1.2)
        top = Image.new("RGBA", (W, H)); ImageDraw.Draw(top).rectangle((0, 0, W, 300), fill=(0, 0, 0, 0)); im.alpha_composite(top)
        J.popt(im, 210, "FOR " + who, u, J.MS(84))
    elif t < E0:  # all 12 at once
        im = Image.new("RGBA", (W, H), J.GOLD + (255,)); cw, ch = (W - 24) // 3, (H - 30) // 4
        for k, (name, _) in enumerate(LIST):
            th = Image.open(D + f"xmas12/{name}.png").convert("RGB"); s = max(cw / th.width, ch / th.height); th = th.resize((int(th.width * s) + 1, int(th.height * s) + 1), Image.LANCZOS)
            th = th.crop(((th.width - cw) // 2, (th.height - ch) // 2, (th.width - cw) // 2 + cw, (th.height - ch) // 2 + ch))
            im.paste(th, (6 + (k % 3) * (cw + 6), 6 + (k // 3) * (ch + 6)))
        if t - G0 < .35: im = J.punch(im, t - G0)
    else:
        im = J.festive(t); im.alpha_composite(J.snow(t)); J.endcard(im, t - E0, "Christmas gift list: sorted")
    if t >= D0 and t < E0: im.alpha_composite(J.snow(t))
    J.flash(im, t - D0, a=170)
    if t > TOTAL - .5: im.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(255 * J.ss((t - TOTAL + .5) / .5)))))
    return im.convert("RGB")

if __name__ == "__main__":
    only = os.environ.get("ONLY")
    if only:
        for s_ in only.split(","): frame(float(s_)).save(WORK + f"g12_{s_}.jpg", quality=85)
        print("cuts", [round(x, 2) for x in T], "grid", round(G0, 2), "end", round(E0, 2)); sys.exit()
    fd = WORK + "fr_g12/"; os.makedirs(fd, exist_ok=True)
    for i in range(int(round(TOTAL * FPS))): frame(i / FPS).save(fd + f"{i:04d}.jpg", quality=93)
    a = J.SNG[0:int(TOTAL * SR)].copy(); fo = int(.6 * SR); a[-fo:] *= np.linspace(1, 0, fo)[:, None]; a *= 10 ** (-1 / 20) / np.max(np.abs(a))
    with wave.open(fd + "a.wav", "wb") as w_:
        w_.setnchannels(2); w_.setsampwidth(2); w_.setframerate(SR); w_.writeframes((a * 32767).astype(np.int16).tobytes())
    base = ["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", fd + "%04d.jpg"]
    enc = ["-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p", "-r", str(FPS), "-movflags", "+faststart"]
    subprocess.run(base + ["-i", fd + "a.wav", "-map", "0:v", "-map", "1:a"] + enc + ["-c:a", "aac", "-b:a", "256k", "-shortest", D + "jingle_gift12.mp4"], check=True)
    subprocess.run(base + enc + ["-an", D + "jingle_gift12_silent.mp4"], check=True)
    print("done", TOTAL)

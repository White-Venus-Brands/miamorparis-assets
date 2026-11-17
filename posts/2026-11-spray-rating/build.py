"""Reel: 'Rating every spray we make. Honestly.'  Tannay's real phone clips (17 Nov 2026), graded to show the mist,
score cards + quips, broken spray as the hook. Real footage -> isAiGenerated false. 1080x1920, 30 fps.
Usage: python3 build.py WORKDIR"""
import math, os, subprocess, sys, json
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

D = os.path.dirname(os.path.abspath(__file__)) + "/"
R = D + "../../"
OUT = sys.argv[1].rstrip("/") + "/" if len(sys.argv) > 1 else "/tmp/spr/"
LOGO = Image.open(R + "assets/cutouts/logo_gold.png").convert("RGBA")
W, H, FPS = 1080, 1920, 30
GOLD, IVORY, INK, RED, GREEN = (226, 186, 112), (250, 245, 236), (30, 24, 20), (215, 40, 45), (70, 190, 110)

# (clip, start, dur, label, score, quip)
SEGS = [
    ("IMG_5071", 0.9, 3.4, "SPRAY #1", "0/10", "...it's broken 💀"),
    ("IMG_5073", 4.9, 2.2, "SPRAY #2", "7.5/10", "Tiny puff. Shy, but it tried."),
    ("IMG_5067", 2.3, 2.2, "SPRAY #3", "8/10", "Soft cloud. Very polite."),
    ("IMG_5068b", 1.7, 2.1, "SPRAY #4", "8/10", "Smooth. Zero drip."),
    ("IMG_5069", 5.3, 2.2, "SPRAY #5", "8.5/10", "Double pump. Main character."),
    ("IMG_5074", 9.4, 2.2, "SPRAY #6", "8.5/10", "Straight jet. No hesitation."),
    ("IMG_5070", 2.5, 2.2, "SPRAY #7", "9/10", "Laser-fine mist. Show-off."),
    ("IMG_5076", 1.2, 3.6, "SPRAY #8", "10/10 🏆", "The cloud. The legend."),
]
END_DUR = 3.6
GRADE = "eq=gamma=1.22:contrast=1.28:saturation=1.05,curves=all='0/0 0.05/0.09 0.2/0.32 0.6/0.72 1/1',unsharp=5:5:0.6"

def inter(s, w="Black"): return ImageFont.truetype(f"/usr/share/fonts/opentype/inter/InterDisplay-{w}.otf", s)
def pop(s, w="Medium"): return ImageFont.truetype(f"/usr/share/fonts/truetype/google-fonts/Poppins-{w}.ttf", s)
def lora(s): return ImageFont.truetype("/usr/share/fonts/truetype/google-fonts/Lora-Italic-Variable.ttf", s)
EMO = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf", 109)
def cl(x): return max(0.0, min(1.0, x))
def ss(x): x = cl(x); return x * x * (3 - 2 * x)
def back(x): x = cl(x); c = 1.9; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2

def emoji(ch, size):
    lay = Image.new("RGBA", (180, 180)); ImageDraw.Draw(lay).text((90, 90), ch, font=EMO, embedded_color=True, anchor="mm")
    lay = lay.crop(lay.getbbox()); s = size / max(lay.size); return lay.resize((int(lay.width * s), int(lay.height * s)), Image.LANCZOS)

def text_with_emoji(s, font, col, a=1.0):
    """Render text; a trailing emoji (after a space) is drawn with the colour emoji font."""
    parts = s.rsplit(" ", 1); emo = None
    if len(parts) == 2 and any(ord(c) > 0x2600 for c in parts[1]): s, emo = parts
    d0 = ImageDraw.Draw(Image.new("RGBA", (1, 1))); bb = d0.textbbox((0, 0), s, font=font)
    tw, th = bb[2], bb[3]; e = emoji(emo, int(font.size * 1.05)) if emo else None
    wtot = tw + (e.width + 16 if e else 0)
    lay = Image.new("RGBA", (wtot + 10, max(th, e.height if e else 0) + 20)); d = ImageDraw.Draw(lay)
    d.text((0, 6), s, font=font, fill=col + (int(255 * a),))
    if e:
        e = e.copy(); e.putalpha(e.getchannel("A").point(lambda v: int(v * a))); lay.alpha_composite(e, (tw + 16, max(0, (th - e.height) // 2 + 8)))
    return lay

def shadowed(im, lay, x, y, blur=12, k=.9):
    sh = Image.new("RGBA", lay.size, (0, 0, 0, 0)); sh.putalpha(lay.getchannel("A").point(lambda v: int(v * k)))
    pad = blur * 3; big = Image.new("RGBA", (lay.width + 2 * pad, lay.height + 2 * pad)); big.alpha_composite(sh, (pad, pad))
    im.alpha_composite(big.filter(ImageFilter.GaussianBlur(blur)), (int(x) - pad, int(y) - pad + 4)); im.alpha_composite(lay, (int(x), int(y)))

def ctext(im, y, s, f, col, a, scale=1.0):
    if a <= 0: return
    lay = text_with_emoji(s, f, col, a)
    if scale != 1: lay = lay.resize((max(1, int(lay.width * scale)), max(1, int(lay.height * scale))), Image.LANCZOS)
    shadowed(im, lay, (W - lay.width) / 2, y)

def score_card(im, u, label, score, quip, winner=False, y0=230):
    """Pops in at u=0.55 s of the segment."""
    k = u - 0.55
    if k <= 0: return
    s = .6 + .4 * back(k / .3); a = ss(k / .12)
    cw, ch = 860, 330; card = Image.new("RGBA", (cw, ch)); d = ImageDraw.Draw(card)
    d.rounded_rectangle((0, 0, cw - 1, ch - 1), 40, fill=(250, 246, 238, 238))
    d.rounded_rectangle((0, 0, cw - 1, ch - 1), 40, outline=GOLD + (255,), width=6)
    d.text((44, 40), label, font=inter(40, "Bold"), fill=(140, 110, 70, 255))
    sc_col = RED if score.startswith("0/") else (GREEN if winner else INK)
    sc = text_with_emoji(score, inter(118), sc_col); card.alpha_composite(sc, (40, 84))
    q = text_with_emoji(quip, pop(40, "Medium"), (60, 52, 46)); card.alpha_composite(q, (46, 238))
    card = card.resize((int(cw * s), int(ch * s)), Image.LANCZOS); card.putalpha(card.getchannel("A").point(lambda v: int(v * a)))
    shadowed(im, card, (W - card.width) / 2, y0 - (card.height - ch * s) / 2, 22, .55)

def run(cmd): subprocess.run(cmd, check=True)

def main():
    os.makedirs(OUT, exist_ok=True)
    frames = []; seg_audio = []; t_cursor = 0.0; marks = []
    for i, (clip, st, du, label, score, quip) in enumerate(SEGS):
        fd = OUT + f"s{i}/"; os.makedirs(fd, exist_ok=True)
        src = D + "src/" + clip + ".mov"
        run(["ffmpeg", "-v", "error", "-y", "-ss", str(st), "-t", str(du), "-i", src,
             "-vf", f"fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},{GRADE}", "-q:v", "3", fd + "%04d.jpg"])
        run(["ffmpeg", "-v", "error", "-y", "-ss", str(st), "-t", str(du), "-i", src, "-vn", "-ac", "2", "-ar", "44100", OUT + f"a{i}.wav"])
        n = len([f for f in os.listdir(fd) if f.endswith(".jpg")])
        for j in range(n): frames.append((i, fd + f"{j + 1:04d}.jpg", j / FPS))
        marks.append(t_cursor); seg_audio.append((OUT + f"a{i}.wav", t_cursor)); t_cursor += n / FPS
    total = t_cursor + END_DUR
    last = frames[-1][1]
    for k in range(int(END_DUR * FPS)): frames.append((-1, last, k / FPS))
    json.dump({"marks": marks, "total": total}, open(OUT + "marks.json", "w"))
    # compose
    for idx, (si, path, u) in enumerate(frames):
        im = Image.open(path).convert("RGBA")
        g = np.zeros((H, W, 4), np.uint8); g[:640, :, 3] = (np.linspace(1, 0, 640) ** 1.6 * 150).astype(np.uint8)[:, None]; im.alpha_composite(Image.fromarray(g, "RGBA"))
        if si == 0:
            ctext(im, 250, "Rating every spray", inter(92), IVORY, ss(u / .15), scale=1 + .25 * (1 - back(u / .3)))
            ctext(im, 360, "we make. Honestly.", inter(92), GOLD, ss((u - .25) / .15))
        if si >= 0:
            clip, st, du, label, score, quip = SEGS[si]
            if si > 0: score_card(im, u + .5, label, score, quip, winner=(si == len(SEGS) - 1))
            else: score_card(im, u - 1.1, label, score, quip, y0=560)
        else:
            k = ss(u / .5); dark = Image.new("RGBA", im.size, (8, 6, 6, int(225 * k))); im.alpha_composite(dark)
            lg = LOGO.resize((220, int(LOGO.height * 220 / LOGO.width)), Image.LANCZOS); a = ss((u - .2) / .4)
            lg.putalpha(lg.getchannel("A").point(lambda v: int(v * a))); im.alpha_composite(lg, ((W - 220) // 2, 420))
            ctext(im, 660, "Which number should", inter(78), IVORY, ss((u - .4) / .3))
            ctext(im, 760, "we restock first? 👇", inter(78), GOLD, ss((u - .55) / .3))
            a3 = ss((u - 1.0) / .4)
            if a3 > 0:
                f = inter(46, "Black"); lab = "DM FOR PRICES"; w_ = ImageDraw.Draw(im).textlength(lab, font=f); lay = Image.new("RGBA", im.size); dl = ImageDraw.Draw(lay); y = 960
                dl.rounded_rectangle(((W - w_) / 2 - 50, y - 50, (W + w_) / 2 + 50, y + 50), 50, fill=GOLD + (255,)); dl.text((W / 2, y), lab, font=f, fill=(40, 8, 16, 255), anchor="mm")
                lay.putalpha(lay.getchannel("A").point(lambda v: int(v * a3))); im.alpha_composite(lay)
            ctext(im, 1060, "OR VISIT US AT LAJPAT NAGAR-II", pop(36, "Bold"), (226, 180, 110), ss((u - 1.2) / .4))
        if idx > (len(frames) - 15): im = Image.blend(im, Image.new("RGBA", im.size, (0, 0, 0, 255)), (idx - (len(frames) - 15)) / 15)
        im.convert("RGB").save(OUT + f"f{idx:05d}.jpg", quality=92)
    audio(OUT, seg_audio, marks, total)
    run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", OUT + "f%05d.jpg", "-i", OUT + "mix.wav",
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "19", "-preset", "medium", "-c:a", "aac", "-b:a", "192k",
         "-movflags", "+faststart", "-shortest", D + "spray_rating_reel.mp4"])
    print("ok", round(total, 2))

def audio(OUT, seg_audio, marks, total):
    import scipy.io.wavfile as wf
    from scipy.signal import lfilter
    SR = 44100; n = int(total * SR) + SR; out = np.zeros((n, 2), np.float32); r = np.random.default_rng(1)
    def add(sig, at, g=1.0):
        i = int(at * SR); j = min(n, i + len(sig))
        if i >= n or j <= i: return
        out[i:j] += (sig[: j - i] * g) if sig.ndim == 2 else np.stack([sig[: j - i] * g] * 2, 1)
    def env(L, a=.003, rel=.15): x = np.arange(int(L * SR)) / SR; return np.minimum(1, x / a) * np.exp(-x / rel)
    def tone(f, L, a=.005, rel=.2, h=(1, .4, .2)): x = np.arange(int(L * SR)) / SR; return sum(g * np.sin(2 * np.pi * f * (i + 1) * x) for i, g in enumerate(h)) * env(L, a, rel)
    # real spray sounds, normalised and boosted
    for p, at in seg_audio:
        sr, a = wf.read(p); a = a.astype(np.float32) / 32768
        a = a - a.mean(0); pk = np.abs(a).max() + 1e-6; add(a / pk * .55, at)
    # light groove bed
    kick = lambda: np.sin(2 * np.pi * (50 + 90 * np.exp(-np.arange(int(.3 * SR)) / SR / .04)) * np.arange(int(.3 * SR)) / SR) * env(.3, .002, .1)
    hat = lambda: lfilter([1, -1], [1, -.6], r.normal(0, 1, int(.05 * SR))) * env(.05, .001, .012)
    beat = 60 / 112; t = marks[1] - .05; k = 0
    while t < total - .6:
        add(kick(), t, .28); add(hat(), t + beat / 2, .07)
        if k % 4 == 0: add(tone([130.8, 110, 87.3, 98][(k // 4) % 4], beat * 4, .02, 1.0, (1, .5, .3)), t, .05)
        t += beat; k += 1
    # broken spray: sad trombone after the card
    for i, f in enumerate((233, 220, 207.7, 196)): add(tone(f, .5 if i < 3 else 1.0, .02, .3 if i < 3 else .7, (1, .6, .4, .3)), marks[0] + 1.75 + i * .3, .09)
    # score dings (higher pitch for higher score), winner fanfare
    for i, m in enumerate(marks[1:], 1):
        f = [0, 660, 698, 740, 784, 830, 880, 988][i]; add(tone(f, .5, .002, .2, (1, .3)), m + .55, .12)
    for i, f in enumerate((784, 988, 1175, 1568)): add(tone(f, 1.2, .003, .5, (1, .2)), marks[-1] + .55 + i * .08, .08)
    out = np.tanh(out * 1.2); out = out[: int(total * SR)]
    fd = np.ones(len(out)); fd[-int(.6 * SR):] = np.linspace(1, 0, int(.6 * SR)); out *= fd[:, None]
    wf.write(OUT + "mix.wav", SR, (out / max(1e-9, np.abs(out).max()) * .89 * 32767).astype(np.int16))

if __name__ == "__main__":
    main()

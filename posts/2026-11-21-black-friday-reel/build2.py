"""Black Friday Reel v2 with the real offer (Tannay, 23 Nov): sale 23-27 Nov, Buy 1 Get 1 Free OR flat 50% off,
plus clearance sale on candles. Reuses helpers/footage from build.py. Usage: python3 build2.py OUTDIR [vo.wav]"""
import json, math, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter
D = os.path.dirname(os.path.abspath(__file__)) + "/"
OUTARG = sys.argv[1] if len(sys.argv) > 1 else "/tmp/bf2"; VO = sys.argv[2] if len(sys.argv) > 2 else None
sys.argv = [sys.argv[0], OUTARG]; sys.path.insert(0, D)
import build as B
from build import W, H, FPS, GOLD, GOLD2, IVORY, MS, LORA, ss, back, text, gold_line, SHADE, spray, wash, photo, WASH
OUT = B.OUT; os.makedirs(OUT, exist_ok=True)

CUES = json.load(open(D + "cues2.json")) if os.path.exists(D + "cues2.json") else \
    {"hook": 0.0, "scent": 2.6, "wash": 4.0, "gifts": 5.3, "offer": 7.2, "or": 9.6, "candles": 12.2, "dates": 14.8, "end": 17.4, "stop": 21.0}
CANDLES = [Image.open(B.R + f"posts/2026-11-02-oudh-candles/{k}.jpg").convert("RGB") for k in ("zeenat_4", "aleud_1", "sandali_1", "abyad_1")]
RED = (214, 40, 40)

def candle(i, p):
    im = CANDLES[i]; s = W / im.width * (1.02 + .06 * p); q = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    can = Image.new("RGB", (W, H), (246, 244, 241)) if i else Image.new("RGB", (W, H), (40, 22, 16))
    if i == 0:   # lit candle photo: blurred fill
        bg = im.resize((H, H), Image.LANCZOS).crop(((H - W) // 2, 0, (H - W) // 2 + W, H)).filter(ImageFilter.GaussianBlur(40)); can = Image.blend(bg, can, .4)
    can.paste(q, ((W - q.width) // 2, (H - q.height) // 2 + 60)); return can.convert("RGBA")

def pill(im, cy, label, fill=RED, fg=(255, 255, 255), size=50, scale=1.0, a=1.0):
    if a <= 0: return
    f = MS(size, "ExtraBold"); tmp = ImageDraw.Draw(Image.new("RGBA", (1, 1))); tw = tmp.textlength(label, font=f)
    w, h = int(tw + 110), int(size * 2); lay = Image.new("RGBA", (w, h)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((0, 0, w - 1, h - 1), h // 2, fill=fill); d.text((w / 2, h / 2), label, font=f, fill=fg, anchor="mm")
    if scale != 1: lay = lay.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    if a < 1: lay.putalpha(lay.getchannel("A").point(lambda v: int(v * a)))
    im.alpha_composite(lay, ((W - lay.width) // 2, int(cy - lay.height / 2)))

def top_dark(im, h=460, k=170):
    g = Image.new("RGBA", (W, H)); gd = ImageDraw.Draw(g)
    for y in range(h): gd.line([(0, y), (W, y)], fill=(0, 0, 0, int(k * (1 - y / h))))
    im.alpha_composite(g)

def frame(t):
    C = CUES
    if t < C["scent"]:                                   # HOOK
        u = t - C["hook"]; im = spray("ombre_h", u, 2.6); im.alpha_composite(SHADE)
        if u < .12: im.alpha_composite(Image.new("RGBA", (W, H), (255, 240, 210, int(255 * (1 - u / .12)))))
        text(im, 300, "BLACK", MS(190), a=ss((u - .15) / .1), scale=1 + .4 * (1 - back((u - .15) / .3)))
        text(im, 480, "FRIDAY", MS(190), fill=GOLD2, a=ss((u - .45) / .1), scale=1 + .4 * (1 - back((u - .45) / .3)))
        gold_line(im, 610, int(560 * ss((u - .8) / .4)))
        text(im, 680, "M I   A M O R   P A R I S", MS(44, "SemiBold"), a=ss((u - 1.0) / .3))
        pill(im, 800, "SALE IS LIVE", a=ss((u - 1.5) / .15), scale=1 + .3 * (1 - back((u - 1.5) / .3)))
        return im
    if t < C["wash"]:
        u = t - C["scent"]; im = spray("moksha_v", u, 1.4); im.alpha_composite(SHADE)
        text(im, 250, "Your", LORA(80), fill=GOLD2, a=ss(u / .2))
        text(im, 370, "SIGNATURE SCENT", MS(96), a=ss((u - .15) / .2), scale=1 + .2 * (1 - back((u - .15) / .3)))
        return im
    if t < C["gifts"]:
        u = t - C["wash"]; dur = C["gifts"] - C["wash"]; n = len(WASH); k = min(n - 1, int(u / (dur / n)))
        im = wash(k, (u - k * dur / n) / (dur / n)); top_dark(im)
        text(im, 190, "Your", LORA(80), fill=GOLD2); text(im, 300, "BODY WASH", MS(110))
        return im
    if t < C["offer"]:
        u = t - C["gifts"]; dur = C["offer"] - C["gifts"]; half = dur * .5
        im = photo("trio", u / dur) if u < half else photo("inbox", (u - half) / half, 1.06, 1.0)
        if abs(u - half) < .1: im.alpha_composite(Image.new("RGBA", (W, H), (255, 240, 210, int(200 * (1 - abs(u - half) / .1)))))
        im.alpha_composite(SHADE)
        text(im, 230, "Your entire", LORA(80), fill=GOLD2, a=ss(u / .2))
        text(im, 350, "GIFT LIST", MS(120), a=ss((u - .15) / .2), scale=1 + .2 * (1 - back((u - .15) / .3)))
        return im
    if t < C["or"]:                                      # BOGO
        u = t - C["offer"]; im = spray("poem_h", u, 2.4); im.alpha_composite(SHADE)
        im.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, 90)))
        if u < .1: im.alpha_composite(Image.new("RGBA", (W, H), (255, 240, 210, int(230 * (1 - u / .1)))))
        text(im, 420, "BUY 1", MS(200), a=ss(u / .1), scale=1 + .4 * (1 - back(u / .3)))
        text(im, 640, "GET 1", MS(200), fill=GOLD2, a=ss((u - .35) / .1), scale=1 + .4 * (1 - back((u - .35) / .3)))
        pill(im, 860, "FREE", fill=GOLD, fg=(10, 8, 6), size=80, a=ss((u - .7) / .1), scale=1 + .5 * (1 - back((u - .7) / .3)))
        return im
    if t < C["candles"]:                                 # OR 50%
        u = t - C["or"]; im = spray("ombre_v", u, 2.6); im.alpha_composite(SHADE)
        im.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, 90)))
        text(im, 330, "or simply take", LORA(84), fill=GOLD2, a=ss(u / .2))
        text(im, 610, "50%", MS(330), a=ss((u - .3) / .1), scale=1 + .4 * (1 - back((u - .3) / .3)))
        text(im, 830, "OFF", MS(160), fill=GOLD2, a=ss((u - .55) / .1), scale=1 + .3 * (1 - back((u - .55) / .3)))
        text(im, 1010, "Your pick.", LORA(76), a=ss((u - 1.2) / .3))
        return im
    if t < C["dates"]:                                   # CANDLES CLEARANCE
        u = t - C["candles"]; dur = C["dates"] - C["candles"]; n = len(CANDLES); k = min(n - 1, int(u / (dur / n)))
        im = candle(k, (u - k * dur / n) / (dur / n)); top_dark(im, 520, 200)
        text(im, 170, "PLUS", MS(56, "ExtraBold"), fill=GOLD2)
        text(im, 280, "CANDLES", MS(140), scale=1 + .2 * (1 - back(u / .3)))
        pill(im, 430, "CLEARANCE SALE", size=54, a=ss((u - .3) / .1), scale=1 + .3 * (1 - back((u - .3) / .3)))
        return im
    if t < C["end"]:                                     # DATES
        u = t - C["dates"]; im = spray("poem_v", u, 2.6); im.alpha_composite(SHADE)
        text(im, 300, "23 – 27 NOV", MS(140), fill=GOLD2, a=ss(u / .15), scale=1 + .3 * (1 - back(u / .3)))
        text(im, 450, "ENDS ON BLACK FRIDAY", MS(70, "ExtraBold"), a=ss((u - .3) / .2))
        gold_line(im, 540, int(420 * ss((u - .6) / .3)))
        text(im, 1560, "IN STORE · LAJPAT NAGAR-II", MS(50, "Bold"), a=ss((u - 1.0) / .25))
        text(im, 1640, "+ ONLINE · miamorparis.in", MS(50, "Bold"), fill=GOLD2, a=ss((u - 1.6) / .25))
        return im
    u = t - C["end"]                                      # END CARD
    im = Image.new("RGBA", (W, H), (8, 6, 6, 255))
    glow = Image.new("RGBA", (W, H)); ImageDraw.Draw(glow).ellipse((90, 420, W - 90, 1300), fill=(226, 186, 112, 45)); im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(120)))
    text(im, 380, "BLACK FRIDAY", MS(110), fill=GOLD2, a=ss(u / .2))
    text(im, 560, "Buy 1 Get 1 Free", MS(76, "ExtraBold"), a=ss((u - .2) / .2))
    text(im, 650, "or 50% off", LORA(72), fill=GOLD2, a=ss((u - .4) / .2))
    text(im, 750, "+ candles clearance sale", MS(52, "Bold"), a=ss((u - .6) / .2))
    gold_line(im, 850, int(520 * ss((u - .8) / .4)))
    pill(im, 960, "ENDS 27 NOV", a=ss((u - 1.0) / .15))
    lg = Image.open(B.R + "assets/cutouts/logo_gold.png").convert("RGBA"); lg = lg.resize((190, int(190 * lg.height / lg.width)), Image.LANCZOS)
    a = ss((u - 1.2) / .4); lg.putalpha(lg.getchannel("A").point(lambda v: int(v * a))); im.alpha_composite(lg, ((W - lg.width) // 2, 1090))
    text(im, 1090 + lg.height + 70, "O-17, Lajpat Nagar-II  ·  miamorparis.in", MS(40, "SemiBold"), a=ss((u - 1.4) / .3))
    text(im, 1800, "*T&C apply", MS(28, "Medium"), fill=(200, 190, 175), a=ss((u - 1.4) / .3), shadow=False)
    return im

if __name__ == "__main__":
    only = os.environ.get("ONLY")
    if only:
        for s in only.split(","): frame(float(s)).convert("RGB").save(OUT + f"v2_{s}.jpg", quality=85)
        sys.exit()
    dur = CUES["stop"]; os.makedirs(OUT + "f2", exist_ok=True)
    for i in range(int(dur * FPS)): frame(i / FPS).convert("RGB").save(OUT + f"f2/{i:04d}.png", compress_level=1)
    B.CUES = {"hook": 0.0, "dates": CUES["offer"], "dm": CUES["or"]}; B.music(OUT + "m2.wav", dur)
    name = "black_friday_reel_v2" + ("_vo" if VO else "") + ".mp4"
    if VO:
        af = "[1:a]volume=0.25[m];[2:a]aresample=44100[v];[m][v]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[a]"
        cmd = ["ffmpeg", "-y", "-v", "error", "-framerate", str(FPS), "-i", OUT + "f2/%04d.png", "-i", OUT + "m2.wav", "-i", VO, "-filter_complex", af, "-map", "0:v", "-map", "[a]"]
    else:
        cmd = ["ffmpeg", "-y", "-v", "error", "-framerate", str(FPS), "-i", OUT + "f2/%04d.png", "-i", OUT + "m2.wav", "-map", "0:v", "-map", "1:a"]
    subprocess.run(cmd + ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "17", "-preset", "medium", "-c:a", "aac", "-b:a", "192k",
                          "-shortest", "-movflags", "+faststart", D + name], check=True)
    frame(CUES["offer"] + 1.2).convert("RGB").save(D + "cover_v2.jpg", quality=94)
    print("done", name)

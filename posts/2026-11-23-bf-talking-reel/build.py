"""Black Friday talking Reel: Tannay on camera in the stockroom (real clips IMG_5211-5228, 23 Nov), cut in script order,
supers timed to his speech (speech spans from silencedetect), cutaways to the Marhaba box + website zodiac candle photos.
Offer: Buy 1 Get 1 Free OR 50% off + candles clearance, 23-27 Nov. Usage: python3 build.py WORKDIR"""
import os, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter
D = os.path.dirname(os.path.abspath(__file__)) + "/"
WORK = (sys.argv[1].rstrip("/") + "/") if len(sys.argv) > 1 else "/tmp/bft/"
BFR = D + "../2026-11-21-black-friday-reel/"
sys.argv = [sys.argv[0], WORK + "bfr"]; sys.path.insert(0, BFR); sys.path.append(D)
import build as B
from build import W, H, FPS, GOLD, GOLD2, IVORY, MS, LORA, ss, back, text, gold_line
import build2 as B2
from build2 import pill
A = "/mnt/user-data/attachments/e1dc2e45-c278-5714-b377-734372e7d29a/"
SRC = {"5211": A + "5f1d5c70-IMG_5211.mov", "5212": A + "450a0d04-IMG_5212.mov", "5215": "/mnt/user-data/uploads/IMG_5215.mov",
       "5216": A + "e252d6fe-IMG_5216.mov", "5222": A + "f232ce78-IMG_5222.mov", "5226": A + "8b5e12e2-IMG_5226.mov",
       "5227": A + "6f7ae372-IMG_5227.mov", "5228": A + "b72277c6-IMG_5228.mov"}
RED = (214, 40, 40)

# (audio clip, in, out, [(video src, src_in, dur), ...])  video pieces must sum to out-in
SEGS = [
    ("5226", 0.00, 7.70, [("5226", 0.00, 7.70)]),                                  # opener: Black Friday at Mi Amor Paris is live (+ dates, store, online)
    ("5227", 0.45, 2.50, [("5227", 0.45, 2.05)]),                                  # your signature scent
    ("5211", 0.40, 1.80, [("5211", 0.40, 1.40)]),                                  # your body wash
    ("5228", 0.50, 3.10, [("5228", 0.50, 1.10), ("5212", 0.60, 1.50)]),            # your entire gift list (+ Marhaba box)
    ("5215", 1.50, 7.95, [("5215", 1.50, 6.45)]),                                  # buy one get one free / or 50% off / your pick
    ("5216", 0.50, 5.70, [("5216", 0.50, 1.60), ("zodiac_aries", 0, 0.9), ("zodiac_gemini", 0, 0.9), ("5216", 3.90, 1.80)]),  # candles
    ("5222", 0.00, 4.40, [("5222", 0.00, 4.40)]),                                  # closer: it's Black Friday guys... don't miss it
]
END_DUR = 0.0
STARTS = []; t = 0.0
for s in SEGS: STARTS.append(t); t += s[2] - s[1]
TOTAL = t + END_DUR

def extract(key, t0, dur):
    fd = WORK + f"v_{key}_{t0:.2f}_{dur:.2f}/"
    if not os.path.isdir(fd) or not os.listdir(fd):
        os.makedirs(fd, exist_ok=True)
        if key.startswith("zodiac_"):
            return fd
        vf = (f"fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}" if key != "5212" else
              f"fps={FPS},scale={W}:-2")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t0), "-t", f"{dur + .1:.2f}", "-i", SRC[key], "-vf", vf + ",eq=contrast=1.04:saturation=1.06",
                        "-q:v", "2", fd + "%04d.jpg"], check=True)
        if key != "5212":   # teeth whitening on the talking clips
            import cv2; from teeth import Whitener
            wt = Whitener()
            for f in sorted(os.listdir(fd)): cv2.imwrite(fd + f, wt(cv2.imread(fd + f)), [cv2.IMWRITE_JPEG_QUALITY, 95])
    return fd

ZOD = {k: Image.open(BFR + f"src/{k}.jpg").convert("RGB") for k in ("zodiac_aries", "zodiac_gemini")}
def still_fill(im, p):
    s = W / im.width * (1.0 + .06 * p); q = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    bs = H / im.height; bg = im.resize((int(im.width * bs), H), Image.LANCZOS)
    bg = bg.crop(((bg.width - W) // 2, 0, (bg.width - W) // 2 + W, H)).filter(ImageFilter.GaussianBlur(45))
    can = Image.blend(bg, Image.new("RGB", (W, H), (10, 6, 6)), .35); can.paste(q, ((W - q.width) // 2, (H - q.height) // 2 + 80)); return can
BOXBG = {}
def box_fill(fr):
    """landscape box clip: fit width over its own blur"""
    bg = fr.resize((int(fr.width * H / fr.height), H), Image.LANCZOS); bg = bg.crop(((bg.width - W) // 2, 0, (bg.width - W) // 2 + W, H)).filter(ImageFilter.GaussianBlur(40))
    bg = Image.blend(bg, Image.new("RGB", (W, H), (10, 6, 6)), .3); s = 1.25; q = fr.resize((int(fr.width * s), int(fr.height * s)), Image.LANCZOS)
    bg.paste(q, ((W - q.width) // 2, (H - q.height) // 2)); return bg

def base_frame(si, u):
    """video frame for segment si at u seconds into the segment"""
    acc = 0.0
    for key, t0, dur in SEGS[si][3]:
        if u < acc + dur or (key, t0, dur) == SEGS[si][3][-1]:
            lu = min(u - acc, dur - 1e-3)
            if key.startswith("zodiac_"): return still_fill(ZOD[key], lu / dur).convert("RGBA")
            fd = extract(key, t0, dur); fs = sorted(os.listdir(fd)); f = fs[min(int(lu * FPS), len(fs) - 1)]
            im = Image.open(fd + f).convert("RGB")
            if key == "5212": im = box_fill(im)
            return im.convert("RGBA")
        acc += dur

LOW = Image.new("RGBA", (W, H)); _d = ImageDraw.Draw(LOW)
for y in range(H): _d.line([(0, y), (W, y)], fill=(0, 0, 0, int(150 * max(1 - y / 420, (y - (H - 700)) / 700, 0))))

def frame(t):
    si = max(i for i, s0 in enumerate(STARTS) if t >= s0) if t < TOTAL - END_DUR else None
    if si is None: return end_card(t - (TOTAL - END_DUR))
    u = t - STARTS[si]; clip_t = SEGS[si][1] + u          # time inside the speaking clip (matches speech spans)
    im = base_frame(si, u); im.alpha_composite(LOW)
    key = SEGS[si][0]
    if key == "5226":                                   # opener
        if clip_t < 2.05:
            text(im, 230, "BLACK FRIDAY", MS(120), fill=GOLD2, a=ss(clip_t / .12), scale=1 + .3 * (1 - back(clip_t / .3)))
            text(im, 340, "at Mi Amor Paris", LORA(64), a=ss((clip_t - .5) / .2))
            pill(im, 1560, "SALE IS LIVE", a=ss((clip_t - 1.0) / .1), scale=1 + .4 * (1 - back((clip_t - 1.0) / .3)))
        elif clip_t < 6.0:
            text(im, 1500, "23 – 27 NOV", MS(120), fill=GOLD2, a=ss((clip_t - 2.2) / .1), scale=1 + .3 * (1 - back((clip_t - 2.2) / .3)))
            text(im, 1630, "IN STORE · LAJPAT NAGAR-II", MS(52, "Bold"), a=ss((clip_t - 3.0) / .15))
            text(im, 1710, "+ ONLINE · miamorparis.in", MS(52, "Bold"), fill=GOLD2, a=ss((clip_t - 4.0) / .15))
        else:
            text(im, 1520, "ENDS ON", MS(64, "ExtraBold"), a=ss((clip_t - 6.15) / .1))
            text(im, 1640, "BLACK FRIDAY", MS(110), fill=GOLD2, a=ss((clip_t - 6.15) / .1), scale=1 + .3 * (1 - back((clip_t - 6.15) / .3)))
    elif key == "5227":
        text(im, 1540, "Your", LORA(70), fill=GOLD2); text(im, 1640, "SIGNATURE SCENT", MS(88), scale=1 + .2 * (1 - back(u / .3)))
    elif key == "5211":
        text(im, 1540, "Your", LORA(70), fill=GOLD2); text(im, 1640, "BODY WASH", MS(100), scale=1 + .2 * (1 - back(u / .3)))
    elif key == "5228":
        text(im, 1540, "Your entire", LORA(70), fill=GOLD2); text(im, 1640, "GIFT LIST", MS(110), scale=1 + .2 * (1 - back(u / .3)))
    elif key == "5215":
        if clip_t < 3.3:
            text(im, 1460, "BUY 1", MS(150), a=ss((clip_t - 1.62) / .08), scale=1 + .35 * (1 - back((clip_t - 1.62) / .3)))
            text(im, 1630, "GET 1 FREE", MS(120), fill=GOLD2, a=ss((clip_t - 2.25) / .08), scale=1 + .35 * (1 - back((clip_t - 2.25) / .3)))
        else:
            text(im, 1430, "or simply take", LORA(66), fill=GOLD2, a=ss((clip_t - 3.35) / .15))
            text(im, 1580, "50% OFF", MS(170), a=ss((clip_t - 4.3) / .08), scale=1 + .35 * (1 - back((clip_t - 4.3) / .3)))
            if clip_t > 7.25: pill(im, 1760, "YOUR PICK", fill=GOLD, fg=(10, 8, 6), a=ss((clip_t - 7.3) / .1), scale=1 + .3 * (1 - back((clip_t - 7.3) / .3)))
    elif key == "5216":
        text(im, 200, "PLUS", MS(56, "ExtraBold"), fill=GOLD2, a=ss((clip_t - .6) / .1))
        text(im, 310, "CANDLES", MS(140), a=ss((clip_t - .6) / .1), scale=1 + .25 * (1 - back((clip_t - .6) / .3)))
        pill(im, 460, "CLEARANCE SALE", size=54, a=ss((clip_t - 1.4) / .1), scale=1 + .3 * (1 - back((clip_t - 1.4) / .3)))
        if 2.1 <= clip_t < 3.9: text(im, 1760, "ZODIAC CANDLES", MS(46, "Bold"), fill=GOLD2)
    elif key == "5222":                                 # closer on his line, recap on screen
        text(im, 230, "IT'S BLACK FRIDAY", MS(100), fill=GOLD2, a=ss(clip_t / .12), scale=1 + .3 * (1 - back(clip_t / .3)))
        if clip_t > 2.55:
            text(im, 360, "DON'T MISS IT", MS(96), a=ss((clip_t - 2.55) / .08), scale=1 + .35 * (1 - back((clip_t - 2.55) / .3)))
        if clip_t > 2.9:
            a_ = ss((clip_t - 2.9) / .25)
            text(im, 1440, "Buy 1 Get 1 Free  ·  or 50% off", MS(50, "ExtraBold"), a=a_)
            text(im, 1520, "+ candles clearance sale", MS(44, "Bold"), fill=GOLD2, a=a_)
            pill(im, 1630, "ENDS 27 NOV", size=46, a=a_)
            text(im, 1740, "O-17, Lajpat Nagar-II  ·  miamorparis.in", MS(38, "SemiBold"), a=a_)
            text(im, 1820, "*T&C apply", MS(26, "Medium"), fill=(220, 210, 195), a=a_, shadow=False)
        if clip_t > 4.0: im.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(255 * ss((clip_t - 4.0) / .4)))))
    if u < .08 and si > 0: im.alpha_composite(Image.new("RGBA", (W, H), (255, 240, 210, int(110 * (1 - u / .08)))))
    return im

def end_card(u):
    im = Image.new("RGBA", (W, H), (8, 6, 6, 255))
    glow = Image.new("RGBA", (W, H)); ImageDraw.Draw(glow).ellipse((90, 420, W - 90, 1300), fill=(226, 186, 112, 45)); im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(120)))
    text(im, 380, "BLACK FRIDAY", MS(110), fill=GOLD2, a=ss(u / .2))
    text(im, 560, "Buy 1 Get 1 Free", MS(76, "ExtraBold"), a=ss((u - .15) / .2))
    text(im, 650, "or 50% off", LORA(72), fill=GOLD2, a=ss((u - .3) / .2))
    text(im, 750, "+ candles clearance sale", MS(52, "Bold"), a=ss((u - .45) / .2))
    gold_line(im, 850, int(520 * ss((u - .6) / .4)))
    pill(im, 960, "ENDS 27 NOV", a=ss((u - .75) / .15))
    lg = Image.open(B.R + "assets/cutouts/logo_gold.png").convert("RGBA"); lg = lg.resize((190, int(190 * lg.height / lg.width)), Image.LANCZOS)
    a = ss((u - .9) / .4); lg.putalpha(lg.getchannel("A").point(lambda v: int(v * a))); im.alpha_composite(lg, ((W - lg.width) // 2, 1090))
    text(im, 1090 + lg.height + 70, "O-17, Lajpat Nagar-II  ·  miamorparis.in", MS(40, "SemiBold"), a=ss((u - 1.1) / .3))
    text(im, 1800, "*T&C apply", MS(28, "Medium"), fill=(200, 190, 175), a=ss((u - 1.1) / .3), shadow=False)
    if u > END_DUR - .4: im.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(255 * ss((u - END_DUR + .4) / .4)))))
    return im

def build_audio(out):
    """his voice: each speaking span cut, levelled, joined; silence under the end card; quiet music bed."""
    ins, parts = [], []
    for i, (key, a0, a1, _) in enumerate(SEGS):
        ins += ["-i", SRC[key]]
        parts.append(f"[{i}:a]atrim={a0}:{a1},asetpts=PTS-STARTPTS,aresample=44100,aformat=channel_layouts=mono,highpass=f=80,"
                     f"afade=t=in:d=0.03,afade=t=out:st={a1 - a0 - .05:.2f}:d=0.05,loudnorm=I=-16:TP=-1.5:LRA=7,aresample=44100[s{i}]")
    n = len(SEGS)
    ins += ["-f", "lavfi", "-t", str(max(END_DUR, .05)), "-i", "anullsrc=r=44100:cl=mono"]
    B.CUES = {"hook": 0.0, "dates": STARTS[4] + .12, "dm": STARTS[-1] + 2.3}; B.music(WORK + "bed.wav", TOTAL)
    ins += ["-i", WORK + "bed.wav"]
    fc = ";".join(parts) + ";" + "".join(f"[s{i}]" for i in range(n)) + f"[{n}:a]concat=n={n + 1}:v=0:a=1[vo];" + \
         f"[{n + 1}:a]volume=0.18[m];[vo][m]amix=inputs=2:duration=longest:normalize=0,alimiter=limit=0.95[a]"
    subprocess.run(["ffmpeg", "-v", "error", "-y"] + ins + ["-filter_complex", fc, "-map", "[a]", "-ar", "44100", out], check=True)

if __name__ == "__main__":
    os.makedirs(WORK, exist_ok=True)
    only = os.environ.get("ONLY")
    if only:
        for s in only.split(","): frame(float(s)).convert("RGB").save(WORK + f"st_{s}.jpg", quality=85)
        print("TOTAL", TOTAL, STARTS); sys.exit()
    os.makedirs(WORK + "f", exist_ok=True)
    for i in range(int(TOTAL * FPS)): frame(i / FPS).convert("RGB").save(WORK + f"f/{i:04d}.jpg", quality=93)
    build_audio(WORK + "a.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", WORK + "f/%04d.jpg", "-i", WORK + "a.wav", "-map", "0:v", "-map", "1:a",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "17", "-preset", "medium", "-c:a", "aac", "-b:a", "192k", "-shortest",
                    "-movflags", "+faststart", D + "black_friday_talking_reel.mp4"], check=True)
    frame(1.5).convert("RGB").save(D + "cover.jpg", quality=94)
    print("done", TOTAL)

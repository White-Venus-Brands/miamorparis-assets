"""FAST-CUT sample of the Black Friday talking Reel (Tannay 25 Nov: 'show me what you mean').
Same voice clips, same script, same footage, re-edited:
  - silences removed between phrases (jump cuts)
  - a new shot every ~0.6-1.4 s: face <-> B-roll of exactly what he is saying (sprays, body wash, box, candles)
  - punch-in zooms on the face (fake second camera), kinetic full-screen stingers for the offer
  - big chunked captions, a sound effect on every cut, teeth whitened (via talking build's extract)
Usage: python3 build_fast.py WORKDIR"""
import importlib.util, math, os, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

D = os.path.dirname(os.path.abspath(__file__)) + "/"
WORK = (sys.argv[1].rstrip("/") + "/") if len(sys.argv) > 1 else "/tmp/bff/"
os.makedirs(WORK, exist_ok=True)
spec = importlib.util.spec_from_file_location("tk", D + "build.py"); sys.argv = [sys.argv[0], WORK]
tk = importlib.util.module_from_spec(spec); spec.loader.exec_module(tk)
B, B2 = tk.B, tk.B2
W, H, FPS = B.W, B.H, B.FPS
MS, LORA, GOLD, GOLD2, IVORY = B.MS, B.LORA, B.GOLD, B.GOLD2, B.IVORY
ss, back, pill = B.ss, B.back, B2.pill
YEL = (255, 214, 64); RED = (214, 40, 40)

# ---------- shots ----------
def face(key, src_t, zoom=1.0, cy=760):
    """frame from a talking clip at src_t (teeth already whitened by tk.extract), optional punch-in"""
    fd = tk.extract(key, 0.0, 8.6 if key in ("5215", "5226") else 6.0)
    fs = sorted(os.listdir(fd)); im = Image.open(fd + fs[min(int(src_t * FPS), len(fs) - 1)]).convert("RGB")
    if zoom != 1.0:
        w, h = W / zoom, H / zoom; x0 = (W - w) / 2; y0 = min(max(cy - h / 2, 0), H - h)
        im = im.resize((W, H), Image.LANCZOS, box=(x0, y0, x0 + w, y0 + h))
    return im.convert("RGBA")
def box(src_t):
    fd = tk.extract("5212", 0.0, 3.0); fs = sorted(os.listdir(fd))
    return tk.box_fill(Image.open(fd + fs[min(int(src_t * FPS), len(fs) - 1)]).convert("RGB")).convert("RGBA")
def stillfill(im, p): return tk.still_fill(im, p).convert("RGBA")
CAND = {k: Image.open(B2.B.R + "posts/2026-11-21-black-friday-reel/src/" + f"zodiac_{k}.jpg").convert("RGB") for k in ("aries", "taurus", "gemini", "cancer")}
CAND["oudh"] = Image.open(B.R + "posts/2026-11-02-oudh-candles/zeenat_4.jpg").convert("RGB")

def stinger(lines, u, bg=(8, 6, 6)):
    """full-screen kinetic text card"""
    im = Image.new("RGBA", (W, H), bg + (255,))
    glow = Image.new("RGBA", (W, H)); ImageDraw.Draw(glow).ellipse((60, 560, W - 60, 1360), fill=(226, 186, 112, 60)); im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(110)))
    for k, (s, f, col, y) in enumerate(lines):
        t0 = k * .12; B.text(im, y, s, f, fill=col, a=ss((u - t0) / .06), scale=1 + .5 * (1 - back((u - t0) / .25)))
    return im

# ---------- captions ----------
def caption(im, s, u, hi=()):
    """big chunk caption, white with black outline, keywords yellow; pops in"""
    f = MS(78, "Black"); words = s.split(); d0 = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    sp = d0.textlength(" ", font=f); widths = [d0.textlength(w_, font=f) for w_ in words]; tw = sum(widths) + sp * (len(words) - 1)
    lay = Image.new("RGBA", (int(tw) + 60, 140)); d = ImageDraw.Draw(lay); x = 30
    for w_, ww in zip(words, widths):
        d.text((x, 20), w_, font=f, fill=YEL if w_.strip(".,!?").upper() in hi else (255, 255, 255), stroke_width=9, stroke_fill=(0, 0, 0)); x += ww + sp
    sc = (1 + .18 * (1 - back(u / .18))) * min(1, (W - 60) / lay.width)
    lay = lay.resize((max(1, int(lay.width * sc)), max(1, int(lay.height * sc))), Image.LANCZOS)
    im.alpha_composite(lay, ((W - lay.width) // 2, 1330 - lay.height // 2))

# ---------- edit decision list ----------
# phrases: (clip, a0, a1, shots, captions). shots: (dur, kind, args); captions: (t0, t1, text, highlight words)
P = [
    ("5228", 0.58, 3.05, [(0.85, "face", ("5228", 1.0)), (0.75, "spray", ("ombre_h",)), (0.87, "face", ("5228", 1.22))],
     [(0.05, .95, "BLACK FRIDAY", {"BLACK", "FRIDAY"}), (.95, 1.75, "AT MI AMOR PARIS", set()), (1.75, 2.47, "IS LIVE!", {"LIVE!"})]),
    ("5227", 0.55, 2.42, [(0.55, "face", ("5227", 1.15)), (1.32, "spray", ("moksha_v",))],
     [(0, 1.87, "YOUR SIGNATURE SCENT", {"SIGNATURE"})]),
    ("5211", 0.46, 1.72, [(0.5, "face", ("5211", 1.0)), (0.38, "wash", (2,)), (0.38, "wash", (3,))],
     [(0, 1.26, "YOUR BODY WASH", {"BODY", "WASH"})]),
    ("5212", 0.48, 2.56, [(0.8, "box", ()), (0.64, "photo", ("trio",)), (0.64, "photo", ("inbox",))],
     [(0, 2.08, "YOUR ENTIRE GIFT LIST", {"GIFT"})]),
    ("5215", 1.60, 3.10, [(0.62, "face", ("5215", 1.2)), (0.88, "sting", ("bogo",))],
     [(0, .62, "BUY ONE...", {"ONE..."})]),
    ("5215", 3.35, 6.75, [(0.9, "face", ("5215", 1.0)), (0.85, "sting", ("fifty",)), (0.8, "spray", ("poem_h",)), (0.85, "face", ("5215", 1.25))],
     [(0, .9, "OR SIMPLY TAKE", set()), (2.55, 3.4, "50% OFF", {"50%", "OFF"})]),
    ("5215", 7.26, 7.93, [(0.67, "face", ("5215", 1.3))], [(0, .67, "YOUR PICK!", {"PICK!"})]),
    ("5216", 0.55, 4.00, [(0.75, "face", ("5216", 1.0)), (0.62, "cand", ("oudh",)), (0.52, "cand", ("aries",)), (0.52, "cand", ("taurus",)),
                          (0.52, "cand", ("gemini",)), (0.52, "cand", ("cancer",))],
     [(0, .75, "PLUS...", {"PLUS..."}), (.75, 3.45, "CANDLE CLEARANCE SALE", {"CLEARANCE"})]),
    ("5216", 4.47, 5.60, [(1.13, "face", ("5216", 1.2))], []),
    ("5226", 0.00, 1.85, [(0.9, "face", ("5226", 1.0)), (0.95, "sting", ("date",))], [(0, .9, "ON TILL THE 27TH", {"27TH"})]),
    ("5226", 2.16, 5.72, [(0.9, "face", ("5226", 1.2)), (0.9, "photo", ("window",)), (0.85, "spray", ("ombre_v",)), (0.91, "face", ("5226", 1.0))],
     [(0, 1.8, "IN STORE · LAJPAT NAGAR", {"LAJPAT", "NAGAR"}), (1.8, 3.56, "AND ONLINE!", {"ONLINE!"})]),
    ("5226", 6.08, 7.53, [(1.45, "face", ("5226", 1.25))], []),
    ("5222", 0.00, 2.27, [(1.1, "face", ("5222", 1.0)), (1.17, "face", ("5222", 1.2))],
     [(0, 1.1, "IT'S BLACK FRIDAY GUYS", {"BLACK", "FRIDAY"}), (1.1, 2.27, "DON'T MISS OUT!", {"MISS", "OUT!"})]),
    ("5222", 2.50, 3.40, [(0.9, "face", ("5222", 1.3))], [(0, .9, "HAPPY SHOPPING!", {"SHOPPING!"})]),
]
TAIL = 1.6   # end recap over the last face frame
STARTS = []; t = 0.0
for p in P: STARTS.append(t); t += p[2] - p[1]
TOTAL = t + TAIL
CUTS = []   # times of every shot change, for SFX
for (clip, a0, a1, shots, caps), s0 in zip(P, STARTS):
    acc = 0.0
    for dur, kind, args in shots: CUTS.append((s0 + acc, kind)); acc += dur

PH = {k: Image.open(D + f"../2026-11-marhaba-yellow/src/{k}.png").convert("RGB") for k in ("trio", "inbox", "window")}
def photo(k, p):
    src = PH[k]; z = 1.0 + .1 * p; sw, sh = src.size; w, h = sw / z, sh / z
    return src.resize((W, H), Image.LANCZOS, box=((sw - w) / 2, (sh - h) / 2, (sw + w) / 2, (sh + h) / 2)).convert("RGBA")

def render_shot(kind, args, clip, src_t, lu, dur):
    if kind == "face": return face(args[0], src_t, args[1])
    if kind == "spray": return B.spray(args[0], .35 + lu, 1)
    if kind == "wash": return B.wash(args[0], lu / dur)
    if kind == "box": return box(.5 + lu)
    if kind == "photo": return photo(args[0], lu / dur)
    if kind == "cand": return stillfill(CAND[args[0]], lu / dur)
    if kind == "sting":
        if args[0] == "bogo": return stinger([("GET ONE", MS(170), IVORY, 760), ("FREE", MS(250), YEL, 1000)], lu)
        if args[0] == "fifty": return stinger([("50%", MS(330), YEL, 820), ("OFF", MS(170), IVORY, 1080)], lu)
        if args[0] == "date": return stinger([("23 – 27", MS(190), IVORY, 800), ("NOVEMBER", MS(110), YEL, 1000)], lu)

def frame(t):
    if t >= TOTAL - TAIL:   # recap tail on the last face frame
        u = t - (TOTAL - TAIL); im = face("5222", 3.4, 1.3); im.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(150 * ss(u / .3)))))
        a = ss(u / .2)
        B.text(im, 520, "BLACK FRIDAY", MS(110), fill=GOLD2, a=a)
        B.text(im, 700, "Buy 1 Get 1 Free", MS(80, "ExtraBold"), a=ss((u - .1) / .2))
        B.text(im, 800, "or 50% off", LORA(74), fill=GOLD2, a=ss((u - .2) / .2))
        B.text(im, 900, "+ candles clearance sale", MS(52, "Bold"), a=ss((u - .3) / .2))
        pill(im, 1030, "ENDS 27 NOV", a=ss((u - .4) / .15))
        B.text(im, 1160, "O-17, Lajpat Nagar-II  ·  miamorparis.in", MS(40, "SemiBold"), a=ss((u - .5) / .2))
        B.text(im, 1820, "*T&C apply", MS(26, "Medium"), fill=(220, 210, 195), a=ss((u - .5) / .2), shadow=False)
        if u > TAIL - .35: im.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(255 * ss((u - TAIL + .35) / .35)))))
        return im
    pi = max(i for i, s0 in enumerate(STARTS) if t >= s0); clip, a0, a1, shots, caps = P[pi]; u = t - STARTS[pi]; src_t = a0 + u
    acc = 0.0
    for dur, kind, args in shots:
        if u < acc + dur or (dur, kind, args) == shots[-1]:
            lu = u - acc; im = render_shot(kind, args, clip, src_t, lu, dur); cut_t = lu; break
        acc += dur
    if cut_t < .05: im.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(120 * (1 - cut_t / .05)))))   # flash frame on cut
    if kind != "sting":
        for c0, c1, s, hi in caps:
            if c0 <= u < c1: caption(im, s, u - c0, hi)
    return im

# ---------- audio: tight voice + SFX on cuts + bed ----------
SR = 44100
def sfx_track():
    n = int(TOTAL * SR); a = np.zeros(n); rng = np.random.default_rng(3)
    def add(sig, t0):
        i0 = int(t0 * SR); m = min(n - i0, len(sig))
        if m > 0: a[i0:i0 + m] += sig[:m]
    x = np.arange(int(.22 * SR)) / SR
    noise = rng.standard_normal(len(x))
    whoosh = np.convolve(noise, np.ones(40) / 40, "same") * np.sin(np.pi * x / x[-1]) ** 2 * .35
    pop = .35 * np.sin(2 * np.pi * (900 - 2500 * x[:3000]) * x[:3000]) * np.exp(-x[:3000] * 40)
    xc = np.arange(int(.6 * SR)) / SR
    ching = (.18 * np.sin(2 * np.pi * 2093 * xc) + .14 * np.sin(2 * np.pi * 2637 * xc)) * np.exp(-xc * 6)
    ching[:int(.03 * SR)] += .3 * rng.standard_normal(int(.03 * SR)) * np.exp(-np.arange(int(.03 * SR)) / 300)
    boom = .55 * np.sin(2 * np.pi * (38 + 70 * np.exp(-xc * 9)) * xc) * np.exp(-xc * 5)
    for t0, kind in CUTS:
        if t0 < .01: add(boom, 0); continue
        add(whoosh, max(0, t0 - .08)); add(pop * .6, t0)
        if kind == "sting": add(ching, t0); add(boom * .7, t0)
    add(boom, TOTAL - TAIL)
    return a

def build_audio(out):
    ins, parts = [], []
    for i, (clip, a0, a1, _, _) in enumerate(P):
        ins += ["-i", tk.SRC[clip]]
        parts.append(f"[{i}:a]atrim={a0}:{a1},asetpts=PTS-STARTPTS,aresample=44100,aformat=channel_layouts=mono,highpass=f=80,"
                     f"afade=t=in:d=0.02,afade=t=out:st={a1 - a0 - .04:.2f}:d=0.04,loudnorm=I=-15:TP=-1.5:LRA=7,aresample=44100[s{i}]")
    n = len(P)
    ins += ["-f", "lavfi", "-t", str(TAIL), "-i", "anullsrc=r=44100:cl=mono"]
    sfx = sfx_track()
    with wave.open(WORK + "sfx.wav", "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(sfx, -1, 1) * 32767).astype(np.int16).tobytes())
    B.CUES = {"hook": 0.0, "dates": STARTS[4], "dm": TOTAL - TAIL}; B.music(WORK + "bed.wav", TOTAL)
    ins += ["-i", WORK + "sfx.wav", "-i", WORK + "bed.wav"]
    fc = ";".join(parts) + ";" + "".join(f"[s{i}]" for i in range(n)) + f"[{n}:a]concat=n={n + 1}:v=0:a=1[vo];" + \
         f"[{n + 1}:a]volume=0.55[fx];[{n + 2}:a]volume=0.16[m];[vo][fx][m]amix=inputs=3:duration=longest:normalize=0,alimiter=limit=0.95[a]"
    subprocess.run(["ffmpeg", "-v", "error", "-y"] + ins + ["-filter_complex", fc, "-map", "[a]", "-ar", "44100", out], check=True)

if __name__ == "__main__":
    only = os.environ.get("ONLY")
    if only:
        for s in only.split(","): frame(float(s)).convert("RGB").save(WORK + f"fs_{s}.jpg", quality=85)
        print("TOTAL", round(TOTAL, 2), "cuts", len(CUTS)); sys.exit()
    os.makedirs(WORK + "ff", exist_ok=True)
    for i in range(int(TOTAL * FPS)): frame(i / FPS).convert("RGB").save(WORK + f"ff/{i:04d}.jpg", quality=93)
    build_audio(WORK + "fa.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", WORK + "ff/%04d.jpg", "-i", WORK + "fa.wav", "-map", "0:v", "-map", "1:a",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-preset", "medium", "-maxrate", "10M", "-bufsize", "20M",
                    "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", D + "black_friday_fastcut_sample.mp4"], check=True)
    print("done", round(TOTAL, 2), "cuts", len(CUTS))

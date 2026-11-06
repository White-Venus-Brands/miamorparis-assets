"""Replace the '50% OFF · LINK IN BIO' end-card line (no-prices rule, 6 Nov 2026)
with 'DM FOR PRICES · LAJPAT NAGAR-II'. The end card is a static plate that fades
in/out, so: clean plate (t=32.0) * fade + new text * text-alpha(t)."""
import subprocess, sys, os, glob
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SRC = os.path.join(os.path.dirname(__file__), "bhaidooj_story.mp4")
OUT = os.path.join(os.path.dirname(__file__), "bhaidooj_story_v2.mp4")
W = sys.argv[1]  # work dir
LINE = "DM FOR PRICES  ·  LAJPAT NAGAR-II"
Y0, Y1, X0, X1 = 1600, 1700, 0, 1080          # patched band
N = (1100, 1400, 100, 250)                     # brightness probe (no text)
T0 = 31.0

os.makedirs(f"{W}/in", exist_ok=True); os.makedirs(f"{W}/out", exist_ok=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(T0), "-i", SRC, f"{W}/in/%04d.png"], check=True)
fs = sorted(glob.glob(f"{W}/in/*.png"))
plate = np.asarray(Image.open(fs[30]).convert("RGB")).astype(float)  # t=32.0: full bright, no line
pN = plate[N[0]:N[1], N[2]:N[3]].mean()
pBand = plate[Y0:Y1, X0:X1]
base_max = pBand[30:61, 224:858].max()

# new text layer (gold gradient + soft glow), fitted to <= 900 px wide
size, track = 40, 9
while True:
    f = ImageFont.truetype("/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf", size)
    w = sum(f.getlength(c) + track for c in LINE) - track
    if w <= 900: break
    size -= 1; track = max(5, track - 0.5)
mask = Image.new("L", (X1 - X0, Y1 - Y0), 0); d = ImageDraw.Draw(mask)
x = (X1 - X0 - w) / 2; cy = 45
for c in LINE:
    d.text((x, cy), c, font=f, fill=255, anchor="lm"); x += f.getlength(c) + track
m = np.asarray(mask).astype(float) / 255
glow = np.asarray(mask.filter(ImageFilter.GaussianBlur(10))).astype(float) / 255 * 0.35
yy = np.linspace(0, 1, Y1 - Y0)[:, None, None]
top, bot = np.array([242, 208, 152.]), np.array([188, 140, 92.])
gold = top * (1 - yy) + bot * yy
glowc = np.array([200, 140, 70.])

for i, p in enumerate(fs):
    fr = np.asarray(Image.open(p).convert("RGB")).astype(float)
    t = T0 + i / 30
    if t >= 32.3:
        fade = fr[N[0]:N[1], N[2]:N[3]].mean() / pN
        band = fr[Y0:Y1, X0:X1]
        a = np.clip((band[30:61, 224:858].max() - base_max * fade) / (201 - 72), 0, 1)
        out = pBand * fade
        out = out * (1 - glow[..., None] * a) + glowc * fade * glow[..., None] * a
        out = out * (1 - m[..., None] * a) + gold * fade * m[..., None] * a
        fr[Y0:Y1, X0:X1] = out
    Image.fromarray(np.clip(fr, 0, 255).astype(np.uint8)).save(f"{W}/out/{i+1:04d}.png")

subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", SRC, "-t", str(T0), "-c:v", "libx264", "-crf", "18",
                "-pix_fmt", "yuv420p", "-an", f"{W}/head.mp4"], check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", "30", "-i", f"{W}/out/%04d.png", "-c:v", "libx264",
                "-crf", "18", "-pix_fmt", "yuv420p", f"{W}/tail.mp4"], check=True)
open(f"{W}/list.txt", "w").write(f"file '{W}/head.mp4'\nfile '{W}/tail.mp4'\n")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{W}/list.txt", "-i", SRC,
                "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-ar", "48000", "-b:a", "192k",
                "-movflags", "+faststart", "-shortest", OUT], check=True)
print(OUT)

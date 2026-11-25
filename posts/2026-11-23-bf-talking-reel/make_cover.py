"""Reel cover for the Black Friday talking reel. 1080x1920; all text inside the 1080x1350 profile-grid crop (y 285-1635)."""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
D = os.path.dirname(os.path.abspath(__file__)) + "/"; R = os.path.normpath(D + "../..") + "/"
FR = sys.argv[1] if len(sys.argv) > 1 else D + "src_cover_frame_5227.jpg"   # whitened frame 86 of IMG_5227
W, H = 1080, 1920; GOLD, GOLD2, IVORY = (226, 186, 112), (240, 208, 150), (250, 245, 236)
def MS(s, st="Black"):
    f = ImageFont.truetype("/usr/share/fonts/truetype/google-fonts/ofl/montserrat/Montserrat[wght].ttf", s); f.set_variation_by_name(st); return f
def BOD(s):
    f = ImageFont.truetype(R + "assets/fonts/BodoniModa-Italic[opsz,wght].ttf", s); f.set_variation_by_name("Medium Italic"); return f
ph = Image.open(FR).convert("RGB")
# warm soft grade
a = np.asarray(ph).astype(np.float32) / 255; a = .03 + a * .95; a = a ** np.array([.96, 1.0, 1.06]); a = .5 + (a - .5) * .97
ph = Image.fromarray(np.clip(a * 255, 0, 255).astype(np.uint8))
# push the photo down so the face sits inside the grid crop; extend the top with its own blur
z = float(os.environ.get("Z", "1.0")); p = ph.resize((int(W * z), int(H * z)), Image.LANCZOS); off = int(os.environ.get("OFF", "60"))
can = ph.resize((W, H)).filter(ImageFilter.GaussianBlur(40))
mask = Image.new("L", p.size, 255); ImageDraw.Draw(mask).rectangle((0, 0, p.width, 1), fill=0); mask = Image.fromarray((np.clip(np.arange(p.height)[:, None] / 90, 0, 1) * 255).repeat(p.width, 1).astype(np.uint8))
can.paste(p, ((W - p.width) // 2, off), mask)
can = can.convert("RGBA")
# dark gradient bottom + light vignette
g = np.zeros((H, W), np.float32); y = np.arange(H)[:, None]
g = np.clip((y - 880) / 520, 0, 1) ** 1.3 * .93 + np.clip((300 - y) / 300, 0, 1) * .35
yy, xx = np.mgrid[0:H, 0:W]; v = ((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 1.6)) ** 2
g = np.clip(g + .3 * np.clip(v - .45, 0, 1), 0, .95)
can.alpha_composite(Image.fromarray((np.dstack([np.full((H, W), 8), np.full((H, W), 6), np.full((H, W), 6), g * 255])).astype(np.uint8), "RGBA"))
d = ImageDraw.Draw(can)
def ctext(y, s, f, fill, stroke=0, sf=(0, 0, 0), sh=True):
    if sh:
        lay = Image.new("RGBA", (W, H)); ImageDraw.Draw(lay).text((W // 2, y + 6), s, font=f, fill=(0, 0, 0, 170), anchor="mm"); can.alpha_composite(lay.filter(ImageFilter.GaussianBlur(10)))
    d.text((W // 2, y), s, font=f, fill=fill, anchor="mm", stroke_width=stroke, stroke_fill=sf)
    return d.textbbox((W // 2, y), s, font=f, anchor="mm")
# headline (autofit <= 940 px)
sz = 170
while d.textlength("BLACK FRIDAY", font=MS(sz)) > 940: sz -= 2
ctext(1150, "BLACK FRIDAY", MS(sz), IVORY)
ctext(1262, "at Mi Amor Paris", BOD(66), GOLD2)
d.rectangle((W // 2 - 140, 1318, W // 2 + 140, 1320), fill=GOLD)
# offer pill
txt = "BUY 1 GET 1 FREE  ·  OR 50% OFF"; f = MS(44, "ExtraBold"); tw = d.textlength(txt, font=f)
x0, x1, y0, y1 = (W - tw) / 2 - 40, (W + tw) / 2 + 40, 1362, 1446
d.rounded_rectangle((x0, y0, x1, y1), radius=42, fill=GOLD); d.text((W // 2, (y0 + y1) // 2 + 2), txt, font=f, fill=(20, 14, 10), anchor="mm")
ctext(1500, "+ candle clearance", MS(40, "SemiBold"), IVORY, sh=False)
ctext(1568, "TILL 27 NOV  ·  STORE + ONLINE", MS(34, "Medium"), (220, 208, 190), sh=False)
lg = Image.open(R + "assets/cutouts/logo_gold.png").convert("RGBA"); lg = lg.resize((120, int(120 * lg.height / lg.width)), Image.LANCZOS)
can.alpha_composite(lg, ((W - lg.width) // 2, 1720))
can.convert("RGB").save(os.environ.get("OUT", D + "cover_black_friday") + ".jpg", quality=95)
can.convert("RGB").crop((0, 285, W, 1635)).save(os.environ.get("OUT", D + "cover_black_friday") + "_grid_preview.jpg", quality=90)
print("ok", sz)

"""Click-worthy Reel cover (Tannay 10 Nov). All text inside the 4:5 grid-safe band (y 285-1635)."""
import os
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageFont
import numpy as np
D = os.path.dirname(os.path.abspath(__file__)) + "/"
W, H = 1080, 1920; GOLD = (232, 192, 118); IV = (252, 244, 232)
def inter(s, w="Black"): return ImageFont.truetype(f"/usr/share/fonts/opentype/inter/InterDisplay-{w}.otf", s)
def lora(s): return ImageFont.truetype("/usr/share/fonts/truetype/google-fonts/Lora-Italic-Variable.ttf", s)
bg = Image.open(D + "src/01.png").convert("RGB").resize((W, H), Image.LANCZOS)
bg = ImageEnhance.Brightness(bg.filter(ImageFilter.GaussianBlur(3))).enhance(0.42).convert("RGBA")
# vignette
yy, xx = np.mgrid[0:H, 0:W]; v = ((xx - W/2)/(W*0.75))**2 + ((yy - H*0.55)/(H*0.6))**2
vig = np.zeros((H, W, 4), np.uint8); vig[..., 3] = (np.clip(v, 0, 1) * 200).astype(np.uint8)
bg.alpha_composite(Image.fromarray(vig, "RGBA"))
# glowing box card
box = Image.open(D + "src/03.png").convert("RGB")
bw = 560; bh = int(bw * box.height / box.width); cy = 1060
crop = box.crop((0, int(box.height * 0.16), box.width, int(box.height * 0.86)))
bh = int(bw * crop.height / crop.width); card = crop.resize((bw, bh), Image.LANCZOS).convert("RGBA")
m = Image.new("L", card.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, bw-1, bh-1), 34, fill=255); card.putalpha(m)
glow = Image.new("RGBA", (W, H)); ImageDraw.Draw(glow).rounded_rectangle(((W-bw)/2-30, cy-bh/2-30, (W+bw)/2+30, cy+bh/2+30), 60, fill=(255, 190, 110, 170))
bg.alpha_composite(glow.filter(ImageFilter.GaussianBlur(55)))
fr = Image.new("RGBA", (bw+12, bh+12)); ImageDraw.Draw(fr).rounded_rectangle((0, 0, bw+11, bh+11), 40, fill=GOLD+(255,)); fr.alpha_composite(card, (6, 6))
bg.alpha_composite(fr, ((W-bw-12)//2, int(cy-bh/2-6)))
def txt(y, s, f, col, blur=14):
    lay = Image.new("RGBA", (W, 400)); ImageDraw.Draw(lay).text((W/2, 30), s, font=f, fill=col+(255,), anchor="ma"); lay = lay.crop(lay.getbbox())
    sh = Image.new("RGBA", lay.size, (0,0,0,0)); sh.putalpha(lay.getchannel("A")); pad = blur*3
    big = Image.new("RGBA", (lay.width+2*pad, lay.height+2*pad)); big.alpha_composite(sh, (pad, pad)); x = (W-lay.width)//2
    bg.alpha_composite(big.filter(ImageFilter.GaussianBlur(blur)), (x-pad, y-pad+6)); bg.alpha_composite(lay, (x, y))
txt(345, "47 SHAADI GIFTS.", inter(104), IV)
txt(470, "Sirf 1 roz use hua.", lora(84), GOLD)
# little tag pill on the box
d = ImageDraw.Draw(bg); f = inter(40, "Bold"); lab = "THE ONE THAT GETS USED"; tw = d.textlength(lab, font=f); y = int(cy + bh/2 + 40)
d.rounded_rectangle(((W-tw)/2-34, y, (W+tw)/2+34, y+74), 37, fill=GOLD+(255,)); d.text((W/2, y+37), lab, font=f, fill=(40, 10, 14), anchor="mm")
txt(y + 120, "Wedding gift set  ·  Mi Amor Paris", ImageFont.truetype("/usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf", 38), (240, 222, 200), 8)
bg.convert("RGB").save(D + "cover_v2.jpg", quality=94)
# grid preview (4:5 centre crop)
bg.convert("RGB").crop((0, 285, W, 1635)).resize((540, 675)).save(D + "cover_v2_grid_preview.jpg", quality=90)
print("ok", y)

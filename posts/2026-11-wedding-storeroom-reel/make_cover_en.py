"""English cover: erase the Hinglish headline from Tannay's cover and set English text in the same place."""
import os, cv2, numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
D = os.path.dirname(os.path.abspath(__file__)) + "/"
im = cv2.imread(D + "src/cover_wedding_hi_tannay.png")
S = 1080 / im.shape[1]; im = cv2.resize(im, (1080, int(im.shape[0] * S)), interpolation=cv2.INTER_LANCZOS4)
H, W = im.shape[:2]
y0, y1 = int(255 * S), int(425 * S)            # headline band
band = im[y0:y1].astype(int)
b, g, r = band[..., 0], band[..., 1], band[..., 2]
white = (r > 215) & (g > 210) & (b > 195)
gold = (r > 200) & (g > 150) & (b < 150) & (r - b > 70)
mask = np.zeros((H, W), np.uint8); mask[y0:y1] = ((white | gold) * 255).astype(np.uint8)
mask = cv2.dilate(mask, np.ones((9, 9), np.uint8), iterations=2)
out = cv2.inpaint(im, mask, 9, cv2.INPAINT_TELEA)
# soften band so leftovers disappear, blend edges
bl = cv2.GaussianBlur(out, (0, 0), 9)
alpha = np.zeros((H, W), np.float32); alpha[y0 - 20:y1 + 20] = 1
alpha = cv2.GaussianBlur(alpha, (0, 0), 14)[..., None]
out = (out * (1 - alpha * 0.85) + bl * alpha * 0.85)
out = (out * (1 - alpha * 0.25)).astype(np.uint8)   # slight darken for contrast
pil = Image.fromarray(cv2.cvtColor(out, cv2.COLOR_BGR2RGB)).convert("RGBA")
def txt(y, s, f, col, blur=12):
    lay = Image.new("RGBA", (W, 400)); ImageDraw.Draw(lay).text((W / 2, 30), s, font=f, fill=col + (255,), anchor="ma"); lay = lay.crop(lay.getbbox())
    sh = Image.new("RGBA", lay.size, (0, 0, 0, 0)); sh.putalpha(lay.getchannel("A")); pad = blur * 3
    big = Image.new("RGBA", (lay.width + 2 * pad, lay.height + 2 * pad)); big.alpha_composite(sh, (pad, pad)); x = (W - lay.width) // 2
    pil.alpha_composite(big.filter(ImageFilter.GaussianBlur(blur)), (x - pad, y - pad + 6)); pil.alpha_composite(lay, (x, y))
inter = ImageFont.truetype("/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf", 92)
lora = ImageFont.truetype("/usr/share/fonts/truetype/google-fonts/Lora-Italic-Variable.ttf", 84)
txt(int(268 * S), "47 WEDDING GIFTS.", inter, (255, 255, 255))
txt(int(345 * S), "Only 1 gets used daily.", lora, (236, 196, 120))
pil.convert("RGB").save(D + "cover_wedding_en.jpg", quality=94)
print("ok", W, H)

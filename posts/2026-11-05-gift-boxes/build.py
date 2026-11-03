"""Diwali gift-box push: Miss Poem and Bouquet gift boxes (body wash + extrait de parfum + moisturizer), Tannay's own
styled photos (3 Nov). No prices: last slide 'DM for prices & Diwali deals'. Notes from the Shopify listings / weekly plan."""
import random, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W, H = 1080, 1350
def lora(s, it=False): return ImageFont.truetype("/usr/share/fonts/truetype/google-fonts/Lora-" + ("Italic-Variable" if it else "Variable") + ".ttf", s)
def pop(s, w="Medium"): return ImageFont.truetype(f"/usr/share/fonts/truetype/google-fonts/Poppins-{w}.ttf", s)
GOLD = (222, 182, 104); CHAMP = (246, 230, 196); TEAL = (14, 62, 66); DTEAL = (8, 36, 40)
LOGO = Image.open("../../assets/cutouts/logo_gold.png").convert("RGBA")
MP, BQ = Image.open("source/missPoem_giftbox.jpg").convert("RGB"), Image.open("source/bouquet_giftbox.jpg").convert("RGB")

def extend(photo, top=270):
    """square photo at the bottom, the top band continues the photo's own backdrop (stretched + blurred), no flat panel"""
    p = photo.resize((1080, 1080), Image.LANCZOS)
    band = p.crop((0, 0, 1080, 120)).resize((1080, top + 160), Image.BICUBIC).filter(ImageFilter.GaussianBlur(22))
    im = Image.new("RGB", (W, H)); im.paste(band, (0, 0))
    m = Image.new("L", (1080, 1080), 255); md = ImageDraw.Draw(m)
    for y in range(90): md.line((0, y, 1080, y), fill=int(255 * y / 90))
    im.paste(p, (0, top), m); return im.convert("RGBA")

def bokeh(im, box, n, seed, col=(255, 200, 120)):
    rnd = random.Random(seed); g = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(g)
    x0, y0, x1, y1 = box
    for _ in range(n):
        x, y, r = rnd.randint(x0, x1), rnd.randint(y0, y1), rnd.randint(6, 26)
        d.ellipse((x - r, y - r, x + r, y + r), fill=col + (rnd.randint(40, 110),))
    im.alpha_composite(g.filter(ImageFilter.GaussianBlur(5)))

def frame(im, col=GOLD):
    d = ImageDraw.Draw(im); d.rectangle((26, 26, W - 27, H - 27), outline=col + (170,), width=2); d.rectangle((38, 38, W - 39, H - 39), outline=col + (80,), width=1)
def c(d, y, s, f, col, shadow=(0, 0, 0, 120)):
    if shadow: d.text((W / 2 + 2, y + 2), s, font=f, fill=shadow, anchor="mm")
    d.text((W / 2, y), s, font=f, fill=col, anchor="mm")
def logo(im, w, y, col=GOLD):
    l = LOGO.resize((w, int(LOGO.height * w / LOGO.width)), Image.LANCZOS); s = Image.new("RGBA", l.size, col + (0,)); s.putalpha(l.split()[3])
    im.alpha_composite(s, ((W - w) // 2, y))

def card(im, photo, cx, cy, sz, ang):
    p = photo.resize((sz, sz), Image.LANCZOS).convert("RGBA"); b = Image.new("RGBA", (sz + 16, sz + 16), GOLD + (255,)); b.alpha_composite(p, (8, 8))
    b = b.rotate(ang, Image.BICUBIC, expand=True); sh = Image.new("RGBA", (W, H)); sa = Image.new("RGBA", b.size, (0, 0, 0, 160)); sa.putalpha(b.split()[3].point(lambda v: v * 0.65))
    sh.alpha_composite(sa, (cx - b.width // 2 + 14, cy - b.height // 2 + 24)); im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(16)))
    im.alpha_composite(b, (cx - b.width // 2, cy - b.height // 2))
def teal_bg(seed):
    im = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(im)
    for y in range(H): t = y / H; d.line((0, y, W, y), fill=tuple(int(TEAL[i] * (1 - t) + DTEAL[i] * t) for i in range(3)) + (255,))
    bokeh(im, (0, 0, W, H), 70, seed); return im

out = []
# 1 cover: both boxes, Diwali lights
im = teal_bg(1); card(im, MP, 372, 720, 560, 7); card(im, BQ, 712, 790, 560, -6)
frame(im); d = ImageDraw.Draw(im); logo(im, 60, 56)
c(d, 180, "Diwali,", lora(84, True), CHAMP); c(d, 268, "beautifully boxed.", lora(84, True), CHAMP)
c(d, 345, "THE MI AMOR PARIS GIFT BOXES", pop(26, "Medium"), GOLD)
c(d, 1250, "swipe  >>", pop(24), GOLD); out.append(im)
# 2 Miss Poem (soft ivory light behind the text so it reads over the lid)
im = extend(MP); g = Image.new("RGBA", (W, 330)); gd = ImageDraw.Draw(g)
for y in range(330): gd.line((0, y, W, y), fill=(252, 238, 226, int(215 * min(1, (330 - y) / 120))))
im.alpha_composite(g); bokeh(im, (60, 30, 1020, 240), 12, 2, (255, 215, 170)); frame(im, (176, 120, 70)); d = ImageDraw.Draw(im)
c(d, 70, "MISS POEM GIFT BOX", pop(28, "Bold"), (150, 92, 60), None); c(d, 135, "Narcissus, mimosa, vanilla & amber", lora(46, True), (70, 38, 30), None)
c(d, 196, "Body wash  ·  Extrait de parfum  ·  Moisturizer", pop(24), (110, 72, 58), None)
c(d, 238, "Soft, sweet and romantic.", pop(22), (130, 90, 74), None); out.append(im)
# 3 Bouquet
im = extend(BQ); bokeh(im, (60, 30, 1020, 240), 14, 3, (190, 240, 220)); frame(im); d = ImageDraw.Draw(im)
c(d, 70, "BOUQUET GIFT BOX", pop(28, "Bold"), GOLD); c(d, 135, "Apple blossom, peony, pear & peach", lora(46, True), CHAMP)
c(d, 196, "Body wash  ·  Extrait de parfum  ·  Moisturizer", pop(24), (200, 220, 210)); c(d, 238, "Fresh, fruity and floral.", pop(22), (190, 210, 200)); out.append(im)
# 4 CTA over the Bouquet set, softly blurred and darkened
bg = BQ.resize((1350, 1350), Image.LANCZOS).crop((135, 0, 1215, 1350)).filter(ImageFilter.GaussianBlur(14))
im = Image.blend(bg, Image.new("RGB", bg.size, DTEAL), 0.55).convert("RGBA"); bokeh(im, (0, 0, W, H), 50, 5)
frame(im); d = ImageDraw.Draw(im); logo(im, 70, 300)
c(d, 470, "One scent. Three steps.", lora(64, True), CHAMP); c(d, 550, "Ready to gift.", lora(64, True), CHAMP)
d.line((440, 640, 640, 640), fill=GOLD, width=2)
c(d, 740, "DM for prices", pop(56, "Bold"), CHAMP); c(d, 815, "& Diwali deals", pop(56, "Bold"), CHAMP)
c(d, 905, "MISS POEM  ·  BOUQUET", pop(26, "Medium"), GOLD)
c(d, 1000, "or visit us at O-17, Lajpat Nagar-II, New Delhi", pop(26), (205, 225, 215)); out.append(im)
for i, s in enumerate(out, 1): s.convert("RGB").save(f"slide_{i:02d}.jpg", quality=93)
sheet = Image.new("RGB", (4 * 432 + 50, 560), (10, 20, 22))
for i, s in enumerate(out): sheet.paste(s.convert("RGB").resize((432, 540)), (10 + i * 442, 10))
sheet.save("csheet.jpg", quality=88); print("ok")

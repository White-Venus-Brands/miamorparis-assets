"""Diwali gift boxes FOR HER (Tannay, 3 Nov): emotional, premium, no prices ("DM for prices & Diwali deals").
Each box = body wash + extrait de parfum + moisturizer of one scent, in the teal Mi Amor Paris box.
Offer (Tannay 3 Nov): BUY ONE PERFUME, GET THE WHOLE DIWALI SET; Delhi NCR delivery in 2-3 hours* (*during office hours). Four for-her scents shown: Flora 5 (Maa), Love Is In The Air (the love of your life), Miss Poem (sister), Bouquet (you).
Notes come from the Shopify listings. Box photos are Tannay's. Men's boxes teased as coming soon."""
import random, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
W, H = 1080, 1350
def lora(s, it=False): return ImageFont.truetype("/usr/share/fonts/truetype/google-fonts/Lora-" + ("Italic-Variable" if it else "Variable") + ".ttf", s)
def pop(s, w="Medium"): return ImageFont.truetype(f"/usr/share/fonts/truetype/google-fonts/Poppins-{w}.ttf", s)
GOLD = (222, 184, 110); CHAMP = (247, 233, 203); SOFT = (196, 214, 206); TEAL = (12, 58, 62); DEEP = (5, 28, 31)
LOGO = Image.open("../../assets/cutouts/logo_gold.png").convert("RGBA")
def photo(n):
    p = Image.open(f"source/{n}.jpg").convert("RGB")
    if p.width < 1000:  # small source: upscale gently and sharpen
        p = p.resize((1100, 1100), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 80, 2))
    return p
FL, LI, MP, BQ = photo("flora5_box"), photo("liita_box"), photo("misspoem_box"), photo("bouquet_box")

def bg(seed, blur_src=None):
    if blur_src is not None:
        b = blur_src.resize((1350, 1350)).crop((135, 0, 1215, 1350)).filter(ImageFilter.GaussianBlur(26))
        im = Image.blend(b, Image.new("RGB", b.size, DEEP), 0.62).convert("RGBA")
    else:
        im = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(im)
        for y in range(H):
            t = y / H; d.line((0, y, W, y), fill=tuple(int(TEAL[i] * (1 - t) + DEEP[i] * t) for i in range(3)) + (255,))
        v = Image.new("RGBA", (W, H)); vd = ImageDraw.Draw(v); vd.ellipse((-200, -150, W + 200, H * 0.8), fill=(40, 110, 110, 70)); im.alpha_composite(v.filter(ImageFilter.GaussianBlur(160)))
    rnd = random.Random(seed); g = Image.new("RGBA", (W, H)); gd = ImageDraw.Draw(g)
    for _ in range(46):  # Diwali lights, out of focus
        x, y, r = rnd.randint(0, W), rnd.randint(0, H), rnd.randint(5, 24)
        gd.ellipse((x - r, y - r, x + r, y + r), fill=(255, 196, 110, rnd.randint(30, 95)))
    im.alpha_composite(g.filter(ImageFilter.GaussianBlur(5))); return im

def frame(im):
    d = ImageDraw.Draw(im); d.rectangle((24, 24, W - 25, H - 25), outline=GOLD + (175,), width=2); d.rectangle((36, 36, W - 37, H - 37), outline=GOLD + (70,), width=1)
def card(im, p, x, y, s, ang=0, border=6):
    q = p.resize((s, s), Image.LANCZOS).convert("RGBA"); b = Image.new("RGBA", (s + 2 * border, s + 2 * border), GOLD + (255,)); b.alpha_composite(q, (border, border))
    if ang: b = b.rotate(ang, Image.BICUBIC, expand=True)
    sh = Image.new("RGBA", (W, H)); sa = Image.new("RGBA", b.size, (0, 0, 0, 0)); sa.putalpha(b.split()[3].point(lambda v: int(v * 0.6)))
    sh.alpha_composite(sa, (x + 12, y + 26)); im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(18))); im.alpha_composite(b, (x, y))
def c(d, y, s, f, col, x=W / 2):
    d.text((x + 2, y + 2), s, font=f, fill=(0, 0, 0, 140), anchor="mm"); d.text((x, y), s, font=f, fill=col, anchor="mm")
def logo(im, w, y):
    l = LOGO.resize((w, int(LOGO.height * w / LOGO.width)), Image.LANCZOS); s = Image.new("RGBA", l.size, GOLD + (0,)); s.putalpha(l.split()[3]); im.alpha_composite(s, ((W - w) // 2, y))
def rule(d, y, w=160): d.line(((W - w) / 2, y, (W + w) / 2, y), fill=GOLD, width=2)

def pill(im, y, text, f, sub=None):
    d = ImageDraw.Draw(im); tw = d.textlength(text, font=f); x0, x1 = (W - tw) / 2 - 38, (W + tw) / 2 + 38
    sh = Image.new("RGBA", (W, H)); ImageDraw.Draw(sh).rounded_rectangle((x0 + 6, y - 38 + 12, x1 + 6, y + 38 + 12), 38, fill=(0, 0, 0, 150)); im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
    d.rounded_rectangle((x0, y - 38, x1, y + 38), 38, fill=GOLD); d.rounded_rectangle((x0 + 5, y - 33, x1 - 5, y + 33), 33, outline=(255, 236, 190), width=1)
    d.text((W / 2, y), text, font=f, fill=DEEP, anchor="mm")
    if sub: c(d, y + 62, sub, pop(21), CHAMP)
def hero(p, top=300):
    q = p.resize((1080, 1080), Image.LANCZOS)
    band = q.crop((0, 0, 1080, 90)).resize((1080, top + 120), Image.BICUBIC).filter(ImageFilter.GaussianBlur(26))
    im = Image.new("RGB", (W, H)); im.paste(band, (0, 0)); m = Image.new("L", (1080, 1080), 255); md = ImageDraw.Draw(m)
    for y in range(110): md.line((0, y, 1080, y), fill=int(255 * y / 110))
    im.paste(q, (0, top), m); im = im.convert("RGBA")
    v = Image.new("RGBA", (W, 420)); vd = ImageDraw.Draw(v)
    for y in range(420): vd.line((0, y, W, y), fill=DEEP + (int(230 * (1 - y / 420) ** 1.3),))
    im.alpha_composite(v); return im

out = []
# 1 cover: the offer + the delivery promise, on the Flora 5 box
im = hero(FL, 270); d = ImageDraw.Draw(im)
c(d, 64, "DIWALI GIFT BOX  ·  FOR HER", pop(24, "Medium"), GOLD)
c(d, 150, "Buy one perfume,", lora(88, True), CHAMP); c(d, 248, "GET THE WHOLE DIWALI SET", pop(56, "Bold"), (255, 226, 160))
v = Image.new("RGBA", (W, 260)); vd = ImageDraw.Draw(v)
for y in range(260): vd.line((0, y, W, y), fill=DEEP + (int(215 * (y / 260) ** 1.2),))
im.alpha_composite(v, (0, H - 260))
pill(im, 1212, "DELHI NCR DELIVERY IN 2-3 HOURS*", pop(38, "Bold"), "*During office hours")
frame(im); out.append(im)
# 2 sweets vs scent, all four boxes
im = bg(1); frame(im); d = ImageDraw.Draw(im)
c(d, 120, "Mithai is gone by Bhai Dooj.", lora(56, True), SOFT); c(d, 196, "Her scent stays all year.", lora(64, True), CHAMP)
c(d, 268, "FOUR WAYS TO SAY YOU THOUGHT OF HER", pop(23, "Medium"), GOLD)
for p, x, y, a in [(FL, 98, 330, 3), (LI, 552, 338, -3), (MP, 98, 776, -2), (BQ, 552, 784, 3)]: card(im, p, x, y, 410, a, 5)
out.append(im)
# 3 the feeling
im = bg(2, MP); frame(im); d = ImageDraw.Draw(im)
for s_, y in [("Every Diwali, she makes", 330), ("everything beautiful", 400), ("for everyone.", 470)]: c(d, y, s_, lora(62, True), CHAMP)
rule(d, 560)
for s_, y in [("The lights. The sweets. The guests.", 640), ("The memories that last all year.", 690)]: c(d, y, s_, pop(30), SOFT)
c(d, 830, "This year, give her", lora(62, True), CHAMP); c(d, 905, "something that's only hers.", lora(62, True), GOLD)
c(d, 1180, "swipe  >>", pop(24), GOLD); out.append(im)
# 4-7 one box per person
people = [
    (FL, 3, "For Maa,", "who made every Diwali feel like home.", "FLORA 5", "Aldehyde & ylang-ylang  ·  jasmine  ·  amber & musk", "Graceful, powdery, timeless."),
    (LI, 4, "For the love of your life,", "because some feelings deserve a scent.", "LOVE IS IN THE AIR", "Grapefruit & black currant  ·  rose & water lily  ·  blackberry", "Romantic, fruity, unforgettable."),
    (MP, 5, "For your sister,", "your first best friend and forever partner-in-crime.", "MISS POEM", "Narcissus  ·  mimosa & vanilla  ·  amber", "Soft, sweet, poetic."),
    (BQ, 6, "And one for you,", "because the woman who gifts everyone deserves one too.", "BOUQUET", "Apple blossom  ·  peony & pear  ·  peach", "Fresh, joyful, full of life."),
]
for p, seed, head, sub, name, notes, mood in people:
    im = bg(seed, p); frame(im); d = ImageDraw.Draw(im)
    c(d, 112, head, lora(64, True), CHAMP); c(d, 182, sub, lora(32, True), SOFT)
    card(im, p, 124, 240, 820, 0, 6); d = ImageDraw.Draw(im)
    c(d, 1138, name + "  GIFT BOX", pop(30, "Bold"), GOLD); c(d, 1190, notes, pop(23), CHAMP); c(d, 1236, mood, lora(30, True), SOFT)
    out.append(im)
# 8 what's inside (Love Is In The Air box, per Tannay)
im = bg(7); frame(im); d = ImageDraw.Draw(im)
c(d, 112, "The whole ritual,", lora(64, True), CHAMP); c(d, 186, "in one box.", lora(64, True), CHAMP)
f = 1100 / 576; cx0, cy0, cx1, cy1 = int(58 * f), int(108 * f), int(512 * f), int(472 * f); crop = LI.crop((cx0, cy0, cx1, cy1)); cw = 860; chh = int(cw * (cy1 - cy0) / (cx1 - cx0))
q = crop.resize((cw, chh), Image.LANCZOS).convert("RGBA"); bx = Image.new("RGBA", (cw + 12, chh + 12), GOLD + (255,)); bx.alpha_composite(q, (6, 6))
X, Y = (W - cw - 12) // 2, 250
sh = Image.new("RGBA", (W, H)); sa = Image.new("RGBA", bx.size, (0, 0, 0, 150)); sh.alpha_composite(sa, (X + 12, Y + 26)); im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(18))); im.alpha_composite(bx, (X, Y))
d = ImageDraw.Draw(im); k = cw / (cx1 - cx0); yb = Y + chh + 12
for i, (sx, lab) in enumerate([(137 * f, "BODY WASH"), (288 * f, "EXTRAIT DE PARFUM"), (431 * f, "MOISTURIZER")]):
    x = X + 6 + (sx - cx0) * k; d.line((x, yb + 8, x, yb + 34), fill=GOLD, width=2)
    c(d, yb + 58, f"0{i + 1}", lora(32, True), GOLD, x); c(d, yb + 94, lab, pop(19, "Bold"), CHAMP, x)
c(d, yb + 170, "Black satin, gold foil, one scent from head to toe.", lora(34, True), CHAMP); c(d, yb + 218, "Nothing to wrap. Just hand it over.", lora(34, True), CHAMP); out.append(im)
# 9 how to gift + CTA + for him teaser
im = bg(8, BQ); frame(im); d = ImageDraw.Draw(im)
c(d, 110, "Buy one perfume,", lora(58, True), CHAMP); c(d, 182, "get the whole Diwali set.", pop(42, "Bold"), (255, 226, 160))
rule(d, 250)
for i, (t1, t2) in enumerate([("Pick her scent", "from our top 10"), ("DM us", "for prices & Diwali deals"), ("We deliver", "in Delhi NCR within 2-3 hours*")]):
    y = 340 + i * 150; d.ellipse((150, y - 40, 230, y + 40), outline=GOLD, width=2); c(d, y, str(i + 1), lora(44, True), GOLD, 190)
    d.text((272, y - 20), t1, font=pop(34, "Bold"), fill=CHAMP, anchor="lm"); d.text((272, y + 24), t2, font=lora(32, True), fill=SOFT, anchor="lm")
c(d, 790, "*During office hours  ·  or visit us at O-17, Lajpat Nagar-II", pop(21), SOFT)
pill(im, 880, "DM FOR PRICES & DIWALI DEALS", pop(32, "Bold"))
d = ImageDraw.Draw(im); d.rounded_rectangle((210, 1000, 870, 1220), 18, outline=GOLD, width=2)
c(d, 1052, "FOR HIM", pop(30, "Bold"), GOLD); c(d, 1110, "Oud, spice and something bold.", lora(38, True), CHAMP); c(d, 1166, "Coming soon.", lora(38, True), CHAMP)
out.append(im)
for i, s in enumerate(out, 1): s.convert("RGB").save(f"slide_{i:02d}.jpg", quality=94)
sheet = Image.new("RGB", (5 * 432 + 60, 2 * 540 + 30), (6, 20, 22))
for i, s in enumerate(out): sheet.paste(s.convert("RGB").resize((432, 540)), (10 + (i % 5) * 442, 10 + (i // 5) * 550))
sheet.save("csheet.jpg", quality=88); print(len(out))

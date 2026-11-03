"""Diwali gift boxes FOR HIM (built from the For Her template) (Tannay, 3 Nov): emotional, premium, no prices ("DM for prices & Diwali deals").
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
MB, MK, DR, HM, SM, MA = [photo(n) for n in ("marhaba_box", "moksha_box", "derossa_box", "holdmi_box", "smuggler_box", "mraqua_box")]
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
# 1 cover: offer + delivery on the Smuggler box
im = hero(SM, 270); d = ImageDraw.Draw(im)
c(d, 64, "DIWALI GIFT BOX  ·  FOR HIM", pop(24, "Medium"), GOLD)
c(d, 150, "Buy one perfume,", lora(88, True), CHAMP); c(d, 248, "GET THE WHOLE DIWALI SET", pop(56, "Bold"), (255, 226, 160))
v = Image.new("RGBA", (W, 260)); vd = ImageDraw.Draw(v)
for y in range(260): vd.line((0, y, W, y), fill=DEEP + (int(215 * (y / 260) ** 1.2),))
im.alpha_composite(v, (0, H - 260))
pill(im, 1212, "DELHI NCR DELIVERY IN 2-3 HOURS*", pop(38, "Bold"), "*During office hours")
frame(im); out.append(im)
# 2 the feeling (Hinglish: "kya zaroorat thi?")
im = bg(2, DR); frame(im); d = ImageDraw.Draw(im)
c(d, 320, "He'll never ask for a gift.", lora(62, True), CHAMP)
c(d, 430, "He'll open it and say,", lora(46, True), SOFT); c(d, 510, "\u201cArre, kya zaroorat thi?\u201d", lora(66, True), GOLD)
rule(d, 610)
c(d, 700, "Then he'll wear it", lora(56, True), CHAMP); c(d, 770, "every single day.", lora(56, True), CHAMP)
c(d, 900, "Gift it anyway.", pop(52, "Bold"), (255, 226, 160))
c(d, 1180, "swipe  >>", pop(24), GOLD); out.append(im)
# 3 sweets vs scent, all six boxes
im = bg(1); frame(im); d = ImageDraw.Draw(im)
c(d, 112, "Mithai is gone by Bhai Dooj.", lora(54, True), SOFT); c(d, 186, "His scent stays all year.", lora(62, True), CHAMP)
c(d, 256, "SIX WAYS TO SAY YOU THOUGHT OF HIM", pop(23, "Medium"), GOLD)
pos = [(84, 312), (392, 318), (700, 312), (84, 640), (392, 646), (700, 640)]
for (p, (x, y)), a in zip(zip([DR, SM, HM, MB, MK, MA], pos), [2, -2, 3, -3, 2, -2]): card(im, p, x, y, 290, a, 4)
c(d, 1040, "De Rossa Oudh  ·  Smuggler  ·  Hold Mi", lora(34, True), CHAMP); c(d, 1092, "Marhaba  ·  Moksha  ·  Mr Aqua", lora(34, True), CHAMP)
out.append(im)
# 4-9 one box per person
people = [
    (DR, 4, "For Papa,", "who never asked for anything and gave us everything.", "DE ROSSA OUDH", "Saffron  ·  rose & coffee  ·  sandalwood & amber", "Warm, bold, regal."),
    (SM, 5, "For the man you love,", "because some nights deserve to be remembered.", "SMUGGLER", "Lavender & mint  ·  honey & cedar  ·  coffee", "Sweet, deep, addictive."),
    (HM, 6, "For your brother,", "your first rival and your forever bodyguard.", "HOLD MI", "Lemon & bergamot  ·  nutmeg & saffron  ·  vetiver", "Crisp, spicy, hard to forget."),
    (MB, 7, "For the one who owns the room,", "the moment he walks in.", "MARHABA", "Saffron & labdanum  ·  rose & agarwood  ·  patchouli", "Warm, spicy, Arabian nights."),
    (MK, 8, "For your best friend,", "who's been there for every single Diwali.", "MOKSHA", "White musk  ·  bergamot & grapefruit  ·  sandalwood", "Fresh, calm, effortlessly classy."),
    (MA, 9, "And one for you,", "because you've earned it this year.", "MR AQUA", "Lime & orange  ·  sea notes  ·  white musk & oakmoss", "Fresh, crisp, confident."),
]
for p, seed, head_, sub, name, notes, mood in people:
    im = bg(seed, p); frame(im); d = ImageDraw.Draw(im)
    c(d, 112, head_, lora(60 if len(head_) > 24 else 64, True), CHAMP); c(d, 182, sub, lora(32, True), SOFT)
    card(im, p, 124, 240, 820, 0, 6); d = ImageDraw.Draw(im)
    c(d, 1138, name + "  GIFT BOX", pop(30, "Bold"), GOLD); c(d, 1190, notes, pop(23), CHAMP); c(d, 1236, mood, lora(30, True), SOFT)
    out.append(im)
# 10 how to gift + CTA + for her cross-sell
im = bg(10, SM); frame(im); d = ImageDraw.Draw(im)
c(d, 110, "Buy one perfume,", lora(58, True), CHAMP); c(d, 182, "get the whole Diwali set.", pop(42, "Bold"), (255, 226, 160))
rule(d, 250)
for i, (t1, t2) in enumerate([("Pick his scent", "from our top 10"), ("DM us", "for prices & Diwali deals"), ("We deliver", "in Delhi NCR within 2-3 hours*")]):
    y = 340 + i * 150; d.ellipse((150, y - 40, 230, y + 40), outline=GOLD, width=2); c(d, y, str(i + 1), lora(44, True), GOLD, 190)
    d.text((272, y - 20), t1, font=pop(34, "Bold"), fill=CHAMP, anchor="lm"); d.text((272, y + 24), t2, font=lora(32, True), fill=SOFT, anchor="lm")
c(d, 790, "*During office hours  ·  or visit us at O-17, Lajpat Nagar-II", pop(21), SOFT)
pill(im, 880, "DM FOR PRICES & DIWALI DEALS", pop(32, "Bold"))
d = ImageDraw.Draw(im); d.rounded_rectangle((190, 1000, 890, 1220), 18, outline=GOLD, width=2)
c(d, 1052, "SHOPPING FOR HER TOO?", pop(28, "Bold"), GOLD); c(d, 1110, "Flora 5 · Love Is In The Air", lora(34, True), CHAMP); c(d, 1162, "Miss Poem · Bouquet", lora(34, True), CHAMP)
out.append(im)
for i, s in enumerate(out, 1): s.convert("RGB").save(f"slide_{i:02d}.jpg", quality=94)
sheet = Image.new("RGB", (5 * 432 + 60, 2 * 540 + 30), (6, 20, 22))
for i, s in enumerate(out): sheet.paste(s.convert("RGB").resize((432, 540)), (10 + (i % 5) * 442, 10 + (i // 5) * 550))
sheet.save("csheet.jpg", quality=88); print(len(out))

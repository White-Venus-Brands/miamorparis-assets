"""Diwali gift boxes FOR HER (Tannay, 3 Nov): emotional, premium, no prices ("DM for prices & Diwali deals").
Each box = body wash + extrait de parfum + moisturizer of one scent, in the teal Mi Amor Paris box.
Four for-her scents shown: Flora 5 (Maa), Love Is In The Air (the love of your life), Miss Poem (sister), Bouquet (you).
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

out = []
# 1 cover: all four boxes
im = bg(1); frame(im); logo(im, 58, 58); d = ImageDraw.Draw(im)
c(d, 178, "This Diwali,", lora(76, True), CHAMP); c(d, 258, "gift her a feeling she can wear.", lora(52, True), CHAMP)
c(d, 330, "THE GIFT BOX  ·  FOR HER", pop(25, "Medium"), GOLD)
for p, x, y, a in [(FL, 98, 392, 3), (LI, 552, 400, -3), (MP, 98, 828, -2), (BQ, 552, 836, 3)]: card(im, p, x, y, 410, a, 5)
out.append(im)
# 2 the feeling
im = bg(2, MP); frame(im); d = ImageDraw.Draw(im)
lines = [("Every Diwali, she makes", 330), ("everything beautiful", 400), ("for everyone.", 470)]
for s, y in lines: c(d, y, s, lora(62, True), CHAMP)
rule(d, 560)
for s, y in [("The lights. The sweets. The guests.", 640), ("The memories that last all year.", 690)]: c(d, y, s, pop(30), SOFT)
c(d, 830, "This year, give her", lora(62, True), CHAMP); c(d, 905, "something that's only hers.", lora(62, True), GOLD)
c(d, 1180, "swipe  >>", pop(24), GOLD); out.append(im)
# 3-6 one box per person
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
# 7 what's inside: closer look inside the Flora 5 box (all three products whole)
im = bg(7); frame(im); d = ImageDraw.Draw(im)
c(d, 112, "The whole ritual,", lora(64, True), CHAMP); c(d, 186, "in one box.", lora(64, True), CHAMP)
cx0, cy0, cx1, cy1 = 160, 340, 1070, 1150; crop = FL.crop((cx0, cy0, cx1, cy1)); cw = 860; chh = int(cw * (cy1 - cy0) / (cx1 - cx0))
q = crop.resize((cw, chh), Image.LANCZOS).convert("RGBA"); bx = Image.new("RGBA", (cw + 12, chh + 12), GOLD + (255,)); bx.alpha_composite(q, (6, 6))
X, Y = (W - cw - 12) // 2, 250
sh = Image.new("RGBA", (W, H)); sa = Image.new("RGBA", bx.size, (0, 0, 0, 150)); sh.alpha_composite(sa, (X + 12, Y + 26)); im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(18))); im.alpha_composite(bx, (X, Y))
d = ImageDraw.Draw(im); k = cw / (cx1 - cx0); yb = Y + chh + 12
for i, (sx, lab) in enumerate([(340, "BODY WASH"), (612, "EXTRAIT DE PARFUM"), (875, "MOISTURIZER")]):
    x = X + 6 + (sx - cx0) * k; d.line((x, yb + 8, x, yb + 36), fill=GOLD, width=2)
    c(d, yb + 62, f"0{i + 1}", lora(32, True), GOLD, x); c(d, yb + 100, lab, pop(19, "Bold"), CHAMP, x)
c(d, 1250, "Black satin, gold foil, one scent from head to toe. Nothing to wrap.", pop(22), SOFT); out.append(im)
# 8 CTA + for him teaser
im = bg(8, BQ); frame(im); logo(im, 70, 150); d = ImageDraw.Draw(im)
c(d, 330, "Choose her scent", lora(66, True), CHAMP); c(d, 406, "from our top 10.", lora(66, True), CHAMP)
rule(d, 490)
c(d, 590, "DM for prices", pop(58, "Bold"), CHAMP); c(d, 668, "& Diwali deals", pop(58, "Bold"), CHAMP)
c(d, 760, "or visit us at O-17, Lajpat Nagar-II, New Delhi", pop(25), SOFT)
d.rounded_rectangle((210, 900, 870, 1130), 18, outline=GOLD, width=2)
c(d, 960, "FOR HIM", pop(30, "Bold"), GOLD); c(d, 1020, "Oud, spice and something bold.", lora(38, True), CHAMP); c(d, 1080, "Coming soon.", lora(38, True), CHAMP)
out.append(im)
for i, s in enumerate(out, 1): s.convert("RGB").save(f"slide_{i:02d}.jpg", quality=94)
sheet = Image.new("RGB", (4 * 432 + 50, 2 * 540 + 30), (6, 20, 22))
for i, s in enumerate(out): sheet.paste(s.convert("RGB").resize((432, 540)), (10 + (i % 4) * 442, 10 + (i // 4) * 550))
sheet.save("csheet.jpg", quality=88); print(len(out))

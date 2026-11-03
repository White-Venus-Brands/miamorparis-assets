"""Diwali gifting 3 x 3 (Tannay, 3 Nov): 3 women's + 3 men's gift sets in ONE carousel built to be BOOSTED.
Different look from the teal For Her / For Him posts: deep wine + gold + ivory. Offer wording per playbook:
"Buy one perfume, get the whole Diwali set", Delhi NCR 2-3 h* (*during office hours). No prices: DM.
Box photos are Tannay's; notes are from the Shopify listings (same lines as the earlier gift-box posts)."""
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W, H = 1080, 1350
def lora(s, it=False): return ImageFont.truetype("/usr/share/fonts/truetype/google-fonts/Lora-" + ("Italic-Variable" if it else "Variable") + ".ttf", s)
def pop(s, w="Medium"): return ImageFont.truetype(f"/usr/share/fonts/truetype/google-fonts/Poppins-{w}.ttf", s)
GOLD = (226, 186, 112); IVORY = (250, 240, 222); BLUSH = (236, 196, 190); WINE = (74, 14, 28); DEEP = (30, 6, 12)
LOGO = Image.open("../../assets/cutouts/logo_gold.png").convert("RGBA")
P = {n: Image.open(f"source/{n}_box.jpg").convert("RGB") for n in ("bouquet", "flora5", "misspoem", "derossa", "holdmi", "mraqua")}
HER = [("bouquet", "BOUQUET", "Apple blossom  ·  peony & pear  ·  peach", "Fresh, joyful, full of life.", "For the one who lights up every room"),
       ("flora5", "FLORA 5", "Aldehyde & ylang-ylang  ·  jasmine  ·  amber & musk", "Graceful, powdery, timeless.", "For Maa, who made every Diwali feel like home"),
       ("misspoem", "MISS POEM", "Narcissus  ·  mimosa & vanilla  ·  amber", "Soft, sweet, poetic.", "For your sister, your forever partner-in-crime")]
HIM = [("derossa", "DE ROSSA OUDH", "Saffron  ·  rose & coffee  ·  sandalwood & amber", "Warm, bold, regal.", "For Papa, who never asked for anything"),
       ("holdmi", "HOLD MI", "Lemon & bergamot  ·  nutmeg & saffron  ·  vetiver", "Crisp, spicy, hard to forget.", "For your brother, your forever bodyguard"),
       ("mraqua", "MR AQUA", "Lime & orange  ·  sea notes  ·  white musk & oakmoss", "Fresh, crisp, confident.", "For the man who has everything, except this")]

def bg(seed):
    im = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(im)
    for y in range(H):
        t = y / H; d.line((0, y, W, y), fill=tuple(int(WINE[i] * (1 - t) + DEEP[i] * t) for i in range(3)) + (255,))
    v = Image.new("RGBA", (W, H)); ImageDraw.Draw(v).ellipse((-220, -200, W + 220, H * 0.75), fill=(150, 40, 60, 70)); im.alpha_composite(v.filter(ImageFilter.GaussianBlur(170)))
    r = random.Random(seed); g = Image.new("RGBA", (W, H)); gd = ImageDraw.Draw(g)
    for _ in range(52):   # festive bokeh
        x, y, rr = r.randint(0, W), r.randint(0, H), r.randint(4, 22); gd.ellipse((x - rr, y - rr, x + rr, y + rr), fill=(255, 200, 120, r.randint(25, 90)))
    im.alpha_composite(g.filter(ImageFilter.GaussianBlur(5)))
    # rangoli-style corner motif in gold line
    m = Image.new("RGBA", (W, H)); md = ImageDraw.Draw(m)
    for cx, cy in ((0, 0), (W, 0), (0, H), (W, H)):
        for k in range(5): md.ellipse((cx - 70 - k * 34, cy - 70 - k * 34, cx + 70 + k * 34, cy + 70 + k * 34), outline=GOLD + (34,), width=2)
    im.alpha_composite(m); return im
def frame(im):
    d = ImageDraw.Draw(im); d.rounded_rectangle((26, 26, W - 27, H - 27), 22, outline=GOLD + (190,), width=2)
def c(d, y, s, f, col, x=W / 2):
    d.text((x + 2, y + 3), s, font=f, fill=(0, 0, 0, 150), anchor="mm"); d.text((x, y), s, font=f, fill=col, anchor="mm")
def logo(im, w, y):
    l = LOGO.resize((w, int(LOGO.height * w / LOGO.width)), Image.LANCZOS); s = Image.new("RGBA", l.size, GOLD + (0,)); s.putalpha(l.split()[3]); im.alpha_composite(s, ((W - w) // 2, y))
def card(im, p, x, y, s, r=18, border=5):
    q = p.resize((s, s), Image.LANCZOS).convert("RGBA"); m = Image.new("L", (s, s), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, s - 1, s - 1), r, fill=255); q.putalpha(m)
    b = Image.new("RGBA", (s + 2 * border, s + 2 * border)); ImageDraw.Draw(b).rounded_rectangle((0, 0, s + 2 * border - 1, s + 2 * border - 1), r + border, fill=GOLD + (255,)); b.alpha_composite(q, (border, border))
    sh = Image.new("RGBA", (W, H)); sa = Image.new("RGBA", b.size, (0, 0, 0, 0)); sa.putalpha(b.split()[3].point(lambda v: int(v * 0.65))); sh.alpha_composite(sa, (x + 10, y + 22))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(16))); im.alpha_composite(b, (x, y))
def pill(im, y, text, f, fill=GOLD, fg=DEEP):
    d = ImageDraw.Draw(im); tw = d.textlength(text, font=f); x0, x1 = (W - tw) / 2 - 40, (W + tw) / 2 + 40
    sh = Image.new("RGBA", (W, H)); ImageDraw.Draw(sh).rounded_rectangle((x0 + 4, y - 36 + 10, x1 + 4, y + 36 + 10), 36, fill=(0, 0, 0, 160)); im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
    d.rounded_rectangle((x0, y - 36, x1, y + 36), 36, fill=fill); d.text((W / 2, y), text, font=f, fill=fg, anchor="mm")
out = []
# 1 COVER: six boxes, For Her | For Him, offer up top, delivery pill
im = bg(1); d = ImageDraw.Draw(im)
c(d, 70, "DIWALI GIFT SETS  ·  3 FOR HER  ·  3 FOR HIM", pop(23, "Medium"), GOLD)
c(d, 140, "Buy one perfume,", lora(64, True), IVORY); c(d, 215, "GET THE WHOLE DIWALI SET", pop(44, "Bold"), GOLD)
S = 286; xs = (66, 397, 728)
for i, (k, *_r) in enumerate(HER): card(im, P[k], xs[i], 345, S)
for i, (k, *_r) in enumerate(HIM): card(im, P[k], xs[i], 765, S)
d = ImageDraw.Draw(im)
for y, lab, col in ((322, "FOR HER", BLUSH), (742, "FOR HIM", GOLD)):
    tw = d.textlength(lab, font=pop(24, "Bold")); d.rounded_rectangle((W / 2 - tw / 2 - 22, y - 22, W / 2 + tw / 2 + 22, y + 22), 22, fill=DEEP + (235,), outline=col, width=2); d.text((W / 2, y), lab, font=pop(24, "Bold"), fill=col, anchor="mm")
pill(im, 1170, "DELHI NCR DELIVERY IN 2-3 HOURS*", pop(30, "Bold"))
c(d, 1236, "*During office hours  ·  Swipe for all six  >>", pop(21), IVORY); frame(im); out.append(im)
# 2 what's inside
im = bg(2); d = ImageDraw.Draw(im); logo(im, 150, 70)
c(d, 250, "One scent. Three ways.", lora(62, True), IVORY); c(d, 320, "BODY WASH  ·  EXTRAIT DE PARFUM  ·  MOISTURIZER", pop(25, "Bold"), GOLD)
card(im, P["derossa"], 140, 400, 800); d = ImageDraw.Draw(im)
c(d, 1255, "Black satin, gold foil, ready to gift. Nothing to wrap.", lora(32, True), BLUSH); frame(im); out.append(im)
# 3-8 one per set
for idx, (k, name, notes, mood, line) in enumerate(HER + HIM):
    im = bg(10 + idx); d = ImageDraw.Draw(im); who = "FOR HER" if idx < 3 else "FOR HIM"; col = BLUSH if idx < 3 else GOLD
    c(d, 70, f"{who}  ·  {idx % 3 + 1} OF 3", pop(23, "Bold"), col)
    a, b = line.split(", ", 1) if ", " in line else (line, "")
    c(d, 140, a + ("," if b else ""), lora(54, True), IVORY)
    if b: c(d, 200, b + ".", lora(32, True), BLUSH)
    card(im, P[k], 115, 262, 840); d = ImageDraw.Draw(im)
    c(d, 1170, name + "  GIFT SET", pop(36, "Bold"), GOLD); c(d, 1224, notes, pop(23), IVORY); c(d, 1272, mood, lora(29, True), BLUSH)
    frame(im); out.append(im)
# 9 CTA
im = bg(30); d = ImageDraw.Draw(im); logo(im, 170, 90)
c(d, 300, "Buy one perfume,", lora(64, True), IVORY); c(d, 376, "get the whole Diwali set.", pop(44, "Bold"), GOLD)
d.line((W / 2 - 90, 440, W / 2 + 90, 440), fill=GOLD, width=2)
steps = [("1", "Pick a scent", "3 for her, 3 for him, or any of our top 10"), ("2", "DM us", "for prices & Diwali deals"), ("3", "We deliver", "in Delhi NCR within 2-3 hours*")]
for i, (n, t, s) in enumerate(steps):
    y = 540 + i * 140; d.ellipse((190, y - 38, 266, y + 38), outline=GOLD, width=3); d.text((228, y), n, font=lora(40), fill=GOLD, anchor="mm")
    d.text((300, y - 20), t, font=pop(36, "Bold"), fill=IVORY, anchor="lm"); d.text((300, y + 24), s, font=lora(28, True), fill=BLUSH, anchor="lm")
pill(im, 1000, "DM FOR PRICES & DIWALI DEALS", pop(32, "Bold"))
c(d, 1090, "*During office hours  ·  or visit us at O-17, Lajpat Nagar-II", pop(22), IVORY)
c(d, 1180, "Mithai is gone by Bhai Dooj. A scent stays all year.", lora(30, True), BLUSH); frame(im); out.append(im)
for n, im in enumerate(out): im.convert("RGB").save(f"slide_{n + 1:02d}.jpg", quality=93)
sh = Image.new("RGB", (5 * 300, 2 * 375), (10, 4, 6))
for n, im in enumerate(out): sh.paste(im.convert("RGB").resize((300, 375)), ((n % 5) * 300, (n // 5) * 375))
sh.save("csheet.jpg"); print(len(out))

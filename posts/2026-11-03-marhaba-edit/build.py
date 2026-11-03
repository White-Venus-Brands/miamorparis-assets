"""3 Nov 2026 feed: "Marhaba, the Diwali-party scent for him" (perfume 100 ml, Oudh shower gel, 8 ml mini).
Look: deep wine-to-black, gold dot-rangoli medallions in the corners and soft gold firework bursts
(new vs. the emerald jaali of 2 Nov). Real Drive photos, shown whole inside gold-framed panels.
Notes and benefit words come from the Shopify listings. Prices removed 3 Nov (Tannay): last slide says "DM for prices & Diwali deals"."""
import math, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W, H = 1080, 1350
def lora(s, it=False): return ImageFont.truetype("/usr/share/fonts/truetype/google-fonts/Lora-" + ("Italic-Variable" if it else "Variable") + ".ttf", s)
def pop(s, w="Medium"): return ImageFont.truetype(f"/usr/share/fonts/truetype/google-fonts/Poppins-{w}.ttf", s)
WINE = (74, 14, 24); BLK = (14, 4, 7); GOLD = (206, 170, 102); CHAMP = (240, 220, 178); IVORY = (250, 246, 238); MUTE = (196, 160, 150)
LOGO = Image.open("../../assets/cutouts/logo_gold.png").convert("RGBA")
P_PERF, W_PERF = "₹1,499", "₹2,999"
P_GEL, W_GEL = "₹749", "₹1,499"
P_MINI, W_MINI = "₹199", "₹399"

def c(d, y, s, f, col): d.text((W / 2, y), s, font=f, fill=col, anchor="mm")

def logo(im, w, y, col=GOLD):
    l = LOGO.resize((w, int(LOGO.height * w / LOGO.width)), Image.LANCZOS)
    a = l.split()[3].point(lambda v: 0 if v < 90 else min(255, int((v - 90) * 2.2))); s = Image.new("RGBA", l.size, col + (0,)); s.putalpha(a)
    im.alpha_composite(s, ((W - w) // 2, y))

def rangoli(d, cx, cy, r, a):
    for ring, n, dot in [(r, 24, 5), (r * 0.72, 16, 4), (r * 0.45, 8, 6)]:
        for k in range(n):
            t = 2 * math.pi * k / n; x, y = cx + ring * math.cos(t), cy + ring * math.sin(t)
            d.ellipse((x - dot, y - dot, x + dot, y + dot), fill=GOLD + (a,))
    for k in range(8):  # petals
        t = 2 * math.pi * k / 8; x, y = cx + r * 0.6 * math.cos(t), cy + r * 0.6 * math.sin(t)
        d.ellipse((x - r * 0.16, y - r * 0.16, x + r * 0.16, y + r * 0.16), outline=GOLD + (a,), width=2)
    d.ellipse((cx - 10, cy - 10, cx + 10, cy + 10), fill=GOLD + (a,))

def burst(d, cx, cy, r, a, rnd):
    for k in range(28):
        t = 2 * math.pi * k / 28 + rnd.random() * 0.1; r0 = r * 0.25; r1 = r * (0.7 + rnd.random() * 0.3)
        d.line((cx + r0 * math.cos(t), cy + r0 * math.sin(t), cx + r1 * math.cos(t), cy + r1 * math.sin(t)), fill=(255, 210, 140, a), width=2)
        d.ellipse((cx + r1 * math.cos(t) - 3, cy + r1 * math.sin(t) - 3, cx + r1 * math.cos(t) + 3, cy + r1 * math.sin(t) + 3), fill=(255, 225, 170, a + 30))

def base(seed):
    im = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(im)
    for y in range(H):
        for_t = y / H
        d.line((0, y, W, y), fill=tuple(int(WINE[i] * (1 - for_t) + BLK[i] * for_t) for i in range(3)) + (255,))
    rnd = random.Random(seed); fx = Image.new("RGBA", (W, H)); fd = ImageDraw.Draw(fx)
    for cx, cy in [(0, 0), (W, H)]: rangoli(fd, cx, cy, 190, 70)
    for _ in range(3): burst(fd, rnd.randint(120, W - 120), rnd.randint(80, 300), rnd.randint(60, 110), 40, rnd)
    im.alpha_composite(fx.filter(ImageFilter.GaussianBlur(0.6)))
    glow = Image.new("RGBA", (W, H)); gd = ImageDraw.Draw(glow)
    for _ in range(16):
        x, y, r = rnd.randint(0, W), rnd.randint(0, H), rnd.randint(8, 24)
        gd.ellipse((x - r, y - r, x + r, y + r), fill=(255, 190, 110, rnd.randint(25, 60)))
    im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(10)))
    d = ImageDraw.Draw(im); d.rectangle((26, 26, W - 27, H - 27), outline=GOLD + (160,), width=2)
    return im

def panel(im, photo, x, y, w, h, bg=None):
    """whole photo fitted (contain) into a rounded gold-framed panel; empty space takes the photo's own corner colour."""
    sh = Image.new("RGBA", (W, H)); ImageDraw.Draw(sh).rounded_rectangle((x + 8, y + 22, x + w + 8, y + h + 22), 30, fill=(0, 0, 0, 140))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(16)))
    p = Image.open(photo).convert("RGB"); s = min(w / p.width, h / p.height); p = p.resize((int(p.width * s), int(p.height * s)), Image.LANCZOS)
    fill = bg or p.getpixel((4, 4)); pn = Image.new("RGB", (w, h), fill); pn.paste(p, ((w - p.width) // 2, (h - p.height) // 2))
    m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), 28, fill=255)
    im.paste(pn, (x, y), m); d = ImageDraw.Draw(im)
    d.rounded_rectangle((x - 2, y - 2, x + w + 1, y + h + 1), 30, outline=GOLD, width=3)
    d.rounded_rectangle((x - 12, y - 12, x + w + 11, y + h + 11), 38, outline=GOLD + (110,), width=1)

def price(d, y, now, was):
    f1, f2 = pop(44, "Bold"), pop(30); a = d.textlength(now, font=f1); b = d.textlength(f"was {was}", font=f2); x = (W - a - 24 - b) / 2
    d.text((x, y), now, font=f1, fill=GOLD, anchor="lm"); d.text((x + a + 24, y + 4), f"was {was}", font=f2, fill=MUTE, anchor="lm")
    d.line((x + a + 24 + d.textlength("was ", font=f2), y + 6, x + a + 24 + b, y + 6), fill=MUTE, width=2)

out = []
# 1 cover: perfume + box, whole
im = base(3); logo(im, 92, 62); d = ImageDraw.Draw(im)
c(d, 200, "Marhaba", lora(92, True), CHAMP)
c(d, 280, "The Diwali-party scent for him", lora(40), IVORY)
panel(im, "perfume_main.jpg", 190, 350, 700, 700); d = ImageDraw.Draw(im)
c(d, 1105, "MARHABA PREMIUM PERFUME FOR MEN · 100 ML", pop(27, "Medium"), GOLD)
c(d, 1200, "Swipe for the full edit  >>", pop(28), CHAMP); out.append(im)

# 2 notes journey (lifestyle photo with saffron & rose)
im = base(7); d = ImageDraw.Draw(im)
d.text((70, 70), "THE NOTES", font=pop(24), fill=GOLD); d.text((W - 70, 70), "Warm spicy  ·  Oudh", font=pop(24), fill=MUTE, anchor="ra")
panel(im, "mini_life_1.jpg", 80, 140, 450, 600); d = ImageDraw.Draw(im)
tx = 590
for i, (lab, notes) in enumerate([("IT OPENS WITH", "Saffron &\nlabdanum"), ("THEN BLOOMS INTO", "Rose &\nagarwood"), ("AND SETTLES ON", "Earthy\npatchouli")]):
    y = 175 + i * 195
    d.text((tx, y), lab, font=pop(22, "Medium"), fill=GOLD)
    d.multiline_text((tx, y + 36), notes, font=lora(44, True), fill=CHAMP, spacing=6)
c(d, 845, "Where the warmth of saffron", lora(46, True), IVORY)
c(d, 905, "meets the depth of oud,", lora(46, True), IVORY)
c(d, 965, "wrapped in the embrace of rose.", lora(46, True), IVORY)
d.line((440, 1040, 640, 1040), fill=GOLD, width=2)
c(d, 1100, "Made for date nights, weddings and parties.", pop(30), CHAMP)
c(d, 1160, "Diwali get-togethers included.", pop(30), CHAMP)
c(d, 1250, "Marhaba Premium Perfume  ·  100 ml", pop(30, "Bold"), GOLD); out.append(im)

# 3 shower gel
im = base(11); d = ImageDraw.Draw(im)
c(d, 105, "Start the evening in the shower", lora(50, True), CHAMP)
panel(im, "bodywash_64.jpg", 300, 170, 480, 640); d = ImageDraw.Draw(im)
c(d, 880, "Marhaba Oudh Shower Gel · 500 ml", lora(46), IVORY)
c(d, 950, "Glycerin, shea butter and sodium hyaluronate", pop(28), CHAMP)
c(d, 995, "for rich foam and soft, hydrated skin.", pop(28), CHAMP)
c(d, 1060, "SOAP-FREE  ·  SULPHATE-FREE  ·  PARABEN-FREE", pop(24, "Medium"), GOLD)
c(d, 1240, "The same warm oriental mood as the perfume.", pop(26), MUTE); out.append(im)

# 4 mini
im = base(17); d = ImageDraw.Draw(im)
c(d, 105, "One for his pocket", lora(56, True), CHAMP)
panel(im, "mini_studio_11.jpg", 220, 175, 640, 640); d = ImageDraw.Draw(im)
c(d, 890, "Marhaba Premium Perfume · 8 ml", lora(46), IVORY)
c(d, 960, "Same saffron, rose and oudh, sized for", pop(28), CHAMP)
c(d, 1005, "a long night out or a first try.", pop(28), CHAMP)
c(d, 1200, "An easy add-on to any Diwali gift.", lora(36, True), MUTE); out.append(im)

# 5 CTA: all three thumbnails
im = base(23); logo(im, 120, 80); d = ImageDraw.Draw(im)
c(d, 290, "The Marhaba edit", lora(70, True), CHAMP)
c(d, 360, "Pick one, or gift him all three.", pop(30), IVORY)
for (ph, x) in [("perfume_main.jpg", 70), ("bodywash_64.jpg", 400), ("mini_studio_11.jpg", 730)]:
    panel(im, ph, x, 440, 280, 373)
d = ImageDraw.Draw(im)
for (t, x) in [("Perfume 100 ml", 210), ("Shower gel 500 ml", 540), ("Perfume 8 ml", 870)]:
    d.text((x, 865), t, font=pop(27), fill=IVORY, anchor="mm")
c(d, 960, "DM for prices & Diwali deals", pop(44, "Bold"), GOLD)
d.line((390, 1035, 690, 1035), fill=GOLD, width=2)
c(d, 1110, "Shop from the link in our bio", pop(34, "Medium"), IVORY)
c(d, 1165, "or visit us at O-17, Lajpat Nagar-II, New Delhi", pop(27), CHAMP); out.append(im)

for n, im in enumerate(out): im.convert("RGB").save(f"slide_{n + 1:02d}.jpg", quality=93)
sh = Image.new("RGB", (5 * 300, 375), "white")
for n, im in enumerate(out): sh.paste(im.convert("RGB").resize((300, 375)), (n * 300, 0))
sh.save("csheet.jpg"); print(len(out))

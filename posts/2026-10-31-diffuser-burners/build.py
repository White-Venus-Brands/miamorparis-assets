"""31 Oct 2026 feed: Diwali diffuser burner edit (Gold, Rose Gold, Silver wooden burners).
Midnight-teal night, gold scalloped toran edge, warm bokeh. Real Drive studio photos, white bg removed by edge flood-fill."""
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
W, H = 1080, 1350
def lora(s, it=False): return ImageFont.truetype("/usr/share/fonts/truetype/google-fonts/Lora-" + ("Italic-Variable" if it else "Variable") + ".ttf", s)
def pop(s, w="Medium"): return ImageFont.truetype(f"/usr/share/fonts/truetype/google-fonts/Poppins-{w}.ttf", s)
NIGHT = (14, 38, 44); NIGHT2 = (8, 22, 27); GOLD = (214, 172, 98); CHAMP = (238, 214, 168); IVORY = (248, 241, 230); MUTE = (160, 178, 172)
LOGO = Image.open("../../assets/cutouts/logo_gold.png").convert("RGBA")

def cutout(src):
    im = Image.open(src).convert("RGB")
    # mark near-white pixels, keep only the region connected to the image border
    g = im.convert("L"); white = g.point(lambda v: 255 if v > 238 else 0)
    seed = Image.new("L", im.size, 0); w, h = im.size
    filled = white.copy()
    for xy in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1), (w // 2, 0), (0, h // 2), (w - 1, h // 2), (w // 2, h - 1)]:
        ImageDraw.floodfill(filled, xy, 128, thresh=0)
    bg = filled.point(lambda v: 255 if v == 128 else 0)
    alpha = ImageChops.invert(bg).filter(ImageFilter.MinFilter(5))
    # keep the warm tealight flame (r clearly above b) that touches the white background
    r, _, b = im.split(); warm = ImageChops.subtract(r, b).point(lambda v: 255 if v > 22 else 0)
    r2, _, b2 = im.split(); warm2 = ImageChops.subtract(r2, b2).point(lambda v: 255 if v > 10 else 0)
    box = Image.new("L", im.size, 0); ImageDraw.Draw(box).rectangle((440, 255, 590, 350), fill=255)  # flame area in these 1000px studio shots
    flame = ImageChops.multiply(ImageChops.multiply(warm2, bg), box).filter(ImageFilter.MaxFilter(13)).filter(ImageFilter.GaussianBlur(3))
    alpha = ImageChops.lighter(ImageChops.lighter(alpha, warm), flame).filter(ImageFilter.GaussianBlur(1.2))
    out = im.convert("RGBA"); out.putalpha(alpha)
    return out.crop(out.getbbox())

def logo(im, w, y, col=GOLD):
    l = LOGO.resize((w, int(LOGO.height * w / LOGO.width)), Image.LANCZOS)
    a = l.split()[3].point(lambda v: 0 if v < 90 else min(255, int((v - 90) * 2.2))); s = Image.new("RGBA", l.size, col + (0,)); s.putalpha(a)
    im.alpha_composite(s, ((W - w) // 2, y))

def c(d, y, s, f, col): d.text((W / 2, y), s, font=f, fill=col, anchor="mm")

def base(seed, top=NIGHT, bot=NIGHT2):
    im = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(im)
    for y in range(H):
        t = y / H; d.line((0, y, W, y), fill=tuple(int(top[i] * (1 - t) + bot[i] * t) for i in range(3)) + (255,))
    rnd = random.Random(seed); bok = Image.new("RGBA", (W, H)); bd = ImageDraw.Draw(bok)
    for _ in range(26):
        x, y, r = rnd.randint(0, W), rnd.randint(160, H), rnd.randint(8, 34)
        bd.ellipse((x - r, y - r, x + r, y + r), fill=(255, 190, 100, rnd.randint(25, 70)))
    im.alpha_composite(bok.filter(ImageFilter.GaussianBlur(6)))
    # scalloped gold toran edge across the top
    d = ImageDraw.Draw(im); d.rectangle((0, 0, W, 34), fill=GOLD)
    for x in range(0, W + 60, 60):
        d.chord((x - 30, 4, x + 30, 64), 0, 180, fill=GOLD)
        d.ellipse((x - 5, 66, x + 5, 76), fill=CHAMP)
    d.rectangle((28, 100, W - 29, H - 29), outline=GOLD + (150,), width=2)
    return im

def place(im, cut, cx, bottom, h, glow=True):
    p = cut.resize((int(cut.width * h / cut.height), h), Image.LANCZOS)
    x, y = int(cx - p.width / 2), bottom - h
    if glow:
        gl = Image.new("RGBA", (W, H)); gd = ImageDraw.Draw(gl)
        gd.ellipse((cx - p.width * 0.75, y + h * 0.05, cx + p.width * 0.75, bottom + 40), fill=(255, 196, 110, 60))
        im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(60)))
    sh = Image.new("RGBA", (W, H)); sd = ImageDraw.Draw(sh)
    sd.ellipse((cx - p.width * 0.48, bottom - 18, cx + p.width * 0.48, bottom + 22), fill=(0, 0, 0, 140))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(12)))
    im.alpha_composite(p, (x, y))

G, RG, S = cutout("gold_1.jpg"), cutout("rosegold_1.jpg"), cutout("silver_1.jpg")
PRICE = "₹799 each  ·  was ₹1,599"
out = []

# 1 cover: all three, whole
im = base(1); d = ImageDraw.Draw(im)
logo(im, 110, 130); d = ImageDraw.Draw(im)
c(d, 280, "One tealight.", lora(64, True), CHAMP)
c(d, 352, "A whole room that smells like Diwali.", lora(40), IVORY)
place(im, S, 200, 1030, 400); place(im, RG, 880, 1030, 400); place(im, G, 540, 1050, 470)
d = ImageDraw.Draw(im)
c(d, 1130, "THE WOODEN DIFFUSER BURNER", pop(36, "Bold"), GOLD)
c(d, 1182, "Gold  ·  Rose Gold  ·  Silver  ·  " + PRICE, pop(27), IVORY)
c(d, 1262, "Swipe to see how it works  >>", pop(25), CHAMP); out.append(im)

# 2 how it works (steps from the listing)
im = base(2); d = ImageDraw.Draw(im)
c(d, 170, "How it works", lora(64, True), CHAMP)
place(im, G, 290, 1080, 640)
d = ImageDraw.Draw(im)
steps = [("1", "Fill the spoon", "with 5 ml of water"), ("2", "Add 3 to 4 drops", "of your favourite diffuser oil"), ("3", "Light the tealight", "underneath the spoon"), ("4", "Let the warmth", "release the fragrance")]
for i, (n, a, b) in enumerate(steps):
    y = 330 + i * 190
    d.ellipse((560, y - 36, 632, y + 36), outline=GOLD, width=3); d.text((596, y), n, font=pop(34, "Bold"), fill=GOLD, anchor="mm")
    d.text((655, y - 20), a, font=pop(30, "Medium"), fill=IVORY, anchor="lm"); d.text((655, y + 22), b, font=pop(24), fill=MUTE, anchor="lm")
c(d, 1230, "2 tealight candles included", pop(28, "Medium"), CHAMP); out.append(im)

# 3-5 each finish
for k, (cut, name, line, seed) in enumerate([(G, "Gold", "Warm gold spoon on a rugged wooden block", 3),
                                            (RG, "Rose Gold", "Soft rose gold for a gentle festive glow", 4),
                                            (S, "Silver", "Cool silver for a clean, modern corner", 5)]):
    im = base(seed); d = ImageDraw.Draw(im)
    d.text((70, 140), f"{k + 1:02d} / 03", font=pop(24), fill=GOLD)
    place(im, cut, 540, 990, 760)
    d = ImageDraw.Draw(im)
    c(d, 1080, name, lora(72), CHAMP)
    c(d, 1146, line, lora(30, True), IVORY)
    c(d, 1222, "Wooden aroma oil burner  ·  ₹799 (was ₹1,599)", pop(27, "Medium"), GOLD); out.append(im)

# 6 pair it + CTA
im = base(6, (40, 22, 18), (16, 9, 8)); d = ImageDraw.Draw(im)
logo(im, 170, 190); d = ImageDraw.Draw(im)
c(d, 420, "Pair it with an oil", lora(60, True), CHAMP)
c(d, 520, "Diffuser oils  ·  ₹299 (was ₹599)", pop(32, "Medium"), IVORY)
c(d, 575, "Oudh scented fragrance oils  ·  ₹399 (was ₹799)", pop(32, "Medium"), IVORY)
c(d, 660, "Or take the Premium Combo: burner + Aqua Oudh oil", pop(28), MUTE)
c(d, 705, "₹999 (was ₹1,999)", pop(30, "Bold"), GOLD)
d.line((340, 790, 740, 790), fill=GOLD, width=2)
c(d, 870, "A gift for every home you visit this Diwali.", lora(38, True), CHAMP)
c(d, 1000, "Shop from the link in our bio", pop(32, "Medium"), IVORY)
c(d, 1050, "or visit us at O-17, Lajpat Nagar-II, New Delhi", pop(27), CHAMP); out.append(im)

for n, im in enumerate(out): im.convert("RGB").save(f"slide_{n + 1:02d}.jpg", quality=93)
sh = Image.new("RGB", (3 * 360, 2 * 450), "white")
for n, im in enumerate(out): sh.paste(im.convert("RGB").resize((360, 450)), ((n % 3) * 360, (n // 3) * 450))
sh.save("csheet.jpg"); print(len(out))

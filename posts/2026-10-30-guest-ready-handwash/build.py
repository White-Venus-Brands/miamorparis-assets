"""30 Oct 2026 feed: Diwali guest-ready sink, 5 handwashes. Ivory/maroon arch layout, fairy-light prop. Real Drive photos."""
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W, H = 1080, 1350
def lora(s, it=False): return ImageFont.truetype("/usr/share/fonts/truetype/google-fonts/Lora-" + ("Italic-Variable" if it else "Variable") + ".ttf", s)
def pop(s, w="Medium"): return ImageFont.truetype(f"/usr/share/fonts/truetype/google-fonts/Poppins-{w}.ttf", s)
IVORY = (248, 241, 230); MAROON = (96, 26, 40); GOLD = (184, 140, 70); SOFT = (120, 92, 80)
LOGO = Image.open("../../assets/cutouts/logo_gold.png").convert("RGBA")
def logo(im, w, y, col=MAROON):
    l = LOGO.resize((w, int(LOGO.height * w / LOGO.width)), Image.LANCZOS)
    a = l.split()[3].point(lambda v: 0 if v < 90 else min(255, int((v - 90) * 2.2))); s = Image.new("RGBA", l.size, col + (0,)); s.putalpha(a); im.alpha_composite(s, ((W - w) // 2, y))
def c(d, y, s, f, col): d.text((W / 2, y), s, font=f, fill=col, anchor="mm")
def lights(im, y0, sag, seed):
    lay = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(lay)
    pts = [(x, y0 + sag * math.sin(math.pi * x / W)) for x in range(-10, W + 20, 6)]
    d.line(pts, fill=(150, 120, 80, 150), width=2)
    glow = Image.new("RGBA", (W, H)); gd = ImageDraw.Draw(glow)
    for i, x in enumerate(range(30 + seed * 17 % 40, W, 68)):
        y = y0 + sag * math.sin(math.pi * x / W) + 10
        gd.ellipse((x - 22, y - 22, x + 22, y + 22), fill=(255, 196, 90, 120))
        d.ellipse((x - 7, y - 7, x + 7, y + 7), fill=(255, 214, 120, 255))
    im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(10))); im.alpha_composite(lay)
def base(seed):
    im = Image.new("RGBA", (W, H), IVORY + (255,)); d = ImageDraw.Draw(im)
    d.rectangle((24, 24, W - 25, H - 25), outline=GOLD, width=2); d.rectangle((34, 34, W - 35, H - 35), outline=GOLD + (120,), width=1)
    lights(im, 40, 70, seed); return im
def arch(im, src, box, x0, y0, w, h):
    p = Image.open(src).convert("RGB").crop(box).resize((w, h), Image.LANCZOS).convert("RGBA")
    m = Image.new("L", (w, h), 0); md = ImageDraw.Draw(m); md.rectangle((0, w // 2, w, h), fill=255); md.ellipse((0, 0, w, w), fill=255)
    im.paste(p, (x0, y0), m); d = ImageDraw.Draw(im)
    d.arc((x0 - 10, y0 - 10, x0 + w + 10, y0 + w + 10), 180, 360, fill=GOLD, width=3)
    d.line((x0 - 10, y0 + w // 2, x0 - 10, y0 + h + 10), fill=GOLD, width=3); d.line((x0 + w + 10, y0 + w // 2, x0 + w + 10, y0 + h + 10), fill=GOLD, width=3)
    d.line((x0 - 10, y0 + h + 10, x0 + w + 10, y0 + h + 10), fill=GOLD, width=3)
out = []
# cover: range shot (text strip above the bottles cropped away; every bottle whole)
im = base(1); d = ImageDraw.Draw(im)
logo(im, 120, 130)
c(d, 285, "Guests are coming this Diwali.", lora(52, True), MAROON)
c(d, 350, "Is your sink ready?", lora(60), GOLD)
arch(im, "Plums_5.jpg", (150, 520, 1850, 1980), 190, 420, 700, 600)
c(d, 1100, "THE GUEST-READY HANDWASH EDIT", pop(34, "Bold"), MAROON)
c(d, 1158, "Moisturising handwash  ·  ₹499 each (was ₹999)", pop(30), SOFT)
c(d, 1250, "Swipe to pick yours  >>", pop(26, "Medium"), GOLD); out.append(im)
P = [("Lemon_2.jpg", (100, 0, 1900, 2000), "Lemon & Green Tea", "Zesty lemon, calming green tea", "For the kitchen sink after all that cooking"),
     ("Melon_2.jpg", (100, 0, 1900, 2000), "Melon", "Juicy, refreshing, fruity", "For the bright, busy guest bathroom"),
     ("Orange_2.jpg", (100, 0, 1900, 2000), "Orange Jasmine", "Fresh orange, delicate jasmine", "For the powder room that greets everyone"),
     ("Plums_3.jpg", (300, 500, 1700, 2000), "Plums & Bergamot", "Juicy plums, bright bergamot", "For the evening get-together crowd"),
     ("Sea_3.jpg", (300, 540, 1700, 2000), "Sea Breeze Lily", "Crisp aquatic notes, delicate lily", "For a fresh-feeling home all week")]
for i, (src, box, name, notes, use) in enumerate(P):
    im = base(i + 2); d = ImageDraw.Draw(im)
    d.text((70, 120), f"{i + 1:02d} / 05", font=pop(24, "Medium"), fill=GOLD)
    bw, bh = box[2] - box[0], box[3] - box[1]; w = 720; h = int(w * bh / bw)
    if h > 810: h = 810; w = int(h * bw / bh)
    arch(im, src, box, (W - w) // 2, 170, w, h)
    y = 170 + h + 70
    c(d, y, name, lora(66), MAROON)
    c(d, y + 66, notes, pop(30), SOFT)
    c(d, y + 116, use, lora(30, True), GOLD)
    c(d, y + 176, "Moisture Lock Formula  ·  300 ml  ·  ₹499 (was ₹999)", pop(26, "Medium"), MAROON); out.append(im)
im = Image.new("RGBA", (W, H), MAROON + (255,)); d = ImageDraw.Draw(im)
d.rectangle((24, 24, W - 25, H - 25), outline=GOLD, width=2); lights(im, 40, 70, 9)
logo(im, 200, 300, (232, 200, 140)); d = ImageDraw.Draw(im)
c(d, 600, "Clean hands, happy guests,", lora(56, True), IVORY); c(d, 672, "a home that smells like you planned it.", lora(42, True), (232, 200, 140))
c(d, 820, "₹499 each this Diwali  ·  was ₹999", pop(36, "Bold"), IVORY)
c(d, 880, "Moisturising handwash  ·  300 ml  ·  all skin types", pop(26), (232, 200, 140))
c(d, 1010, "Shop from the link in our bio", pop(30, "Medium"), IVORY)
c(d, 1060, "or visit us at O-17, Lajpat Nagar-II, New Delhi", pop(28), (232, 200, 140)); out.append(im)
for n, im in enumerate(out): im.convert("RGB").save(f"slide_{n + 1:02d}.jpg", quality=93)
sh = Image.new("RGB", (4 * 270, 2 * 338), "white")
for n, im in enumerate(out): sh.paste(im.convert("RGB").resize((270, 338)), ((n % 4) * 270, (n // 4) * 338))
sh.save("csheet.jpg"); print(len(out))

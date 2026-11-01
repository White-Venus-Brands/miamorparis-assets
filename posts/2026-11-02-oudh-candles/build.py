"""2 Nov 2026 feed: "Six evenings to Diwali" Oudh three-wick candle edit.
Emerald jaali (lattice) background, ivory jharokha arches holding the real Drive studio photos
(white studio bg sits inside the ivory arch, so the product stays whole, no cutting).
Notes, strength and mood words come from the Shopify listings. Prices verified live 1 Nov."""
import math, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W, H = 1080, 1350
def lora(s, it=False): return ImageFont.truetype("/usr/share/fonts/truetype/google-fonts/Lora-" + ("Italic-Variable" if it else "Variable") + ".ttf", s)
def pop(s, w="Medium"): return ImageFont.truetype(f"/usr/share/fonts/truetype/google-fonts/Poppins-{w}.ttf", s)
EM = (16, 54, 42); EM2 = (7, 30, 23); GOLD = (206, 170, 102); CHAMP = (240, 220, 178); IVORY = (250, 248, 243); INK = (30, 40, 34); MUTE = (170, 190, 178)
LOGO = Image.open("../../assets/cutouts/logo_gold.png").convert("RGBA")
PRICE, WAS = "₹1,749", "₹3,499"

def c(d, y, s, f, col): d.text((W / 2, y), s, font=f, fill=col, anchor="mm")

def logo(im, w, y, col=GOLD):
    l = LOGO.resize((w, int(LOGO.height * w / LOGO.width)), Image.LANCZOS)
    a = l.split()[3].point(lambda v: 0 if v < 90 else min(255, int((v - 90) * 2.2))); s = Image.new("RGBA", l.size, col + (0,)); s.putalpha(a)
    im.alpha_composite(s, ((W - w) // 2, y))

def base(seed):
    im = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(im)
    for y in range(H):
        t = y / H; d.line((0, y, W, y), fill=tuple(int(EM[i] * (1 - t) + EM2[i] * t) for i in range(3)) + (255,))
    # faint gold jaali lattice (quatrefoil grid)
    lat = Image.new("RGBA", (W, H)); ld = ImageDraw.Draw(lat); s = 90
    for gx in range(-s, W + s, s):
        for gy in range(-s, H + s, s):
            ld.arc((gx - s / 2, gy - s / 2, gx + s / 2, gy + s / 2), 0, 360, fill=GOLD + (28,), width=2)
            ld.arc((gx, gy, gx + s, gy + s), 0, 360, fill=GOLD + (18,), width=1)
    im.alpha_composite(lat)
    rnd = random.Random(seed); glow = Image.new("RGBA", (W, H)); gd = ImageDraw.Draw(glow)
    for _ in range(14):
        x, y, r = rnd.randint(0, W), rnd.randint(0, H), rnd.randint(10, 28)
        gd.ellipse((x - r, y - r, x + r, y + r), fill=(255, 200, 120, rnd.randint(30, 70)))
    im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(9)))
    d = ImageDraw.Draw(im); d.rectangle((24, 24, W - 25, H - 25), outline=GOLD + (170,), width=2); d.rectangle((34, 34, W - 35, H - 35), outline=GOLD + (80,), width=1)
    return im

def arch_mask(w, h):
    m = Image.new("L", (w, h), 0); d = ImageDraw.Draw(m); r = w // 2
    d.ellipse((0, 0, w, w), fill=255); d.rectangle((0, r, w, h), fill=255); return m

def arch(im, photo, x, y, w, h, fill=IVORY, zoom=1.0, cover=False):
    """ivory arch window at (x,y) holding the whole photo, gold double outline."""
    sh = Image.new("RGBA", (W, H)); ImageDraw.Draw(sh).rounded_rectangle((x + 10, y + 24, x + w + 10, y + h + 24), 40, fill=(0, 0, 0, 120))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(18)))
    p = Image.open(photo).convert("RGB")
    if cover:  # lifestyle photo: fill the arch, trim only empty background at the sides
        ps = max(w, h); p = p.resize((ps, ps), Image.LANCZOS); panel = p.crop(((ps - w) // 2, (ps - h) // 2, (ps - w) // 2 + w, (ps - h) // 2 + h)).convert("RGBA")
    else:  # studio photo: panel takes the photo's own white so there is no seam
        fill = p.getpixel((8, 8)); panel = Image.new("RGBA", (w, h), fill + (255,))
        ps = int(min(w, h - w * 0.28) * zoom); p = p.resize((ps, ps), Image.LANCZOS)
        panel.paste(p, ((w - ps) // 2, h - ps - int(h * 0.04)))
    m = arch_mask(w, h); im.paste(panel, (x, y), m)
    d = ImageDraw.Draw(im); r = w // 2
    for o, col, wd in [(0, GOLD, 4), (12, GOLD + (150,), 2)]:
        d.arc((x - o, y - o, x + w + o, y + w + o), 180, 360, fill=col, width=wd)
        d.line((x - o, y + r, x - o, y + h + o), fill=col, width=wd); d.line((x + w + o, y + r, x + w + o, y + h + o), fill=col, width=wd)
        d.line((x - o, y + h + o, x + w + o, y + h + o), fill=col, width=wd)
    # small finial on top
    d.polygon([(x + r, y - 34), (x + r - 10, y - 14), (x + r, y - 4), (x + r + 10, y - 14)], fill=GOLD)

C = [("aleud_1.jpg", "Oudh Aleud", "Tobacco & Almond", "Strong", "Bold and warm, for cosy evenings in."),
     ("abyad_1.jpg", "Oudh Abyad", "White Rose & Musk", "Mild", "Soft and peaceful, for quiet evenings at home."),
     ("sandali_1.jpg", "Oudh Al Sandali", "Sandalwood & Amber", "Moderate", "Rich and comforting, for unwinding after a long day."),
     ("alkhuzama_1.jpg", "Oudh Alkhuzama", "Amber & Leather", "Mild", "Smooth and refined, with a warm, regal feel."),
     ("zeenat_4.jpg", "Zeenat e Oudh", "Cedarwood & Harsingar", "Moderate", "Calm and grounding, a breath of peace.")]
out = []

# 1 cover: three arches
im = base(1); d = ImageDraw.Draw(im)
logo(im, 96, 70); d = ImageDraw.Draw(im)
c(d, 210, "Six evenings to Diwali.", lora(66, True), CHAMP)
c(d, 285, "Light a different Oudh every night.", lora(38), IVORY)
arch(im, C[1][0], 60, 470, 300, 470); arch(im, C[3][0], 720, 470, 300, 470); arch(im, C[0][0], 375, 400, 330, 560)
d = ImageDraw.Draw(im)
c(d, 1060, "THE OUDH THREE-WICK CANDLES", pop(36, "Bold"), GOLD)
c(d, 1115, f"Five scents  ·  {PRICE} each (was {WAS})", pop(27), IVORY)
c(d, 1220, "Swipe for all five scents  >>", pop(26), CHAMP); out.append(im)

# 2-6: one candle per slide, alternating arch side
for k, (ph, name, notes, strength, mood) in enumerate(C):
    im = base(10 + k); d = ImageDraw.Draw(im)
    d.text((70, 70), f"EVENING {k + 1:02d}", font=pop(24, "Medium"), fill=GOLD)
    d.text((W - 70, 70), f"{k + 1} / 5", font=pop(24), fill=MUTE, anchor="ra")
    left = k % 2 == 0
    ax = 80 if left else W - 80 - 560
    arch(im, ph, ax, 170, 560, 800, cover=ph.startswith('zeenat'))
    d = ImageDraw.Draw(im)
    tx = 680 if left else 80; tw = 330
    def para(y, s, f, col, lh):
        words = s.split(); line = ""
        for wd in words:
            t = (line + " " + wd).strip()
            if d.textlength(t, font=f) > tw: d.text((tx, y), line, font=f, fill=col); y += lh; line = wd
            else: line = t
        d.text((tx, y), line, font=f, fill=col); return y + lh
    d.text((tx, 300), "NOTES", font=pop(22, "Medium"), fill=GOLD)
    y = para(340, notes, lora(40, True), CHAMP, 50)
    d.line((tx, y + 20, tx + 90, y + 20), fill=GOLD, width=2)
    d.text((tx, y + 50), "FRAGRANCE", font=pop(22, "Medium"), fill=GOLD)
    d.text((tx, y + 85), strength, font=lora(38), fill=IVORY)
    para(y + 170, mood, pop(25, "Light"), IVORY, 36)
    c(d, 1075, name, lora(70), CHAMP)
    c(d, 1150, "Oudh three-wick candle", pop(26), MUTE)
    c(d, 1220, f"{PRICE}  (was {WAS})", pop(34, "Bold"), GOLD); out.append(im)

# 7 CTA
im = base(20); d = ImageDraw.Draw(im)
logo(im, 160, 170); d = ImageDraw.Draw(im)
c(d, 420, "Which evening is yours?", lora(60, True), CHAMP)
y = 520
for _, name, notes, _, _ in C:
    c(d, y, f"{name}  ·  {notes}", pop(29), IVORY); y += 56
d.line((360, y + 20, 720, y + 20), fill=GOLD, width=2)
c(d, y + 90, f"{PRICE} each  ·  was {WAS}", pop(36, "Bold"), GOLD)
c(d, y + 160, "A warm gift for every home you visit this Diwali.", lora(34, True), CHAMP)
c(d, y + 280, "Shop from the link in our bio", pop(32, "Medium"), IVORY)
c(d, y + 330, "or visit us at O-17, Lajpat Nagar-II, New Delhi", pop(27), CHAMP); out.append(im)

for n, im in enumerate(out): im.convert("RGB").save(f"slide_{n + 1:02d}.jpg", quality=93)
sh = Image.new("RGB", (4 * 360, 2 * 450), "white")
for n, im in enumerate(out): sh.paste(im.convert("RGB").resize((360, 450)), ((n % 4) * 360, (n // 4) * 450))
sh.save("csheet.jpg"); print(len(out))

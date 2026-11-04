"""Festive Stories (Tannay, 4 Nov): replaces This-or-that + Today's Star.
  11:00  fact(n)  -> a small, true fun fact about Diwali / why it's celebrated, then a soft gifting line.
  23:00  gift(n)  -> a Diwali gift idea for a specific person, built on a REAL gift-box photo.
1080x1920. No prices (people reply 'GIFT' and get them in DMs). Never link perfume to puja.
Usage: python3 ops/stories/diwali.py OUTDIR fact 1 gift 1 [--days N]
"""
import math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

R = os.path.dirname(os.path.abspath(__file__)) + "/../../"
BOX = R + "posts/2026-11-03-gift-sets-3x3/source/"
LOGO = Image.open(R + "assets/cutouts/logo_gold.png").convert("RGBA")
W, H = 1080, 1920
GOLD, IVORY, WINE = (226, 186, 112), (250, 240, 226), (74, 14, 28)

def inter(s, w="Black"): return ImageFont.truetype(f"/usr/share/fonts/opentype/inter/InterDisplay-{w}.otf", s)
def lora(s, it=True): return ImageFont.truetype("/usr/share/fonts/truetype/google-fonts/Lora-" + ("Italic-Variable" if it else "Variable") + ".ttf", s)
def pop(s, w="Medium"): return ImageFont.truetype(f"/usr/share/fonts/truetype/google-fonts/Poppins-{w}.ttf", s)

# ---- content banks (verified, general-knowledge facts; keep wording simple) ----
FACTS = [
    ("'Diwali' comes from Deepavali.", "Deep means lamp, avali means row.\nLiterally: a row of lights.", "Light up someone's Diwali this year."),
    ("It falls on the darkest night of the year's calendar.", "Diwali is on Amavasya, the new-moon night of Kartik.\nNo moon, so every home brings the light.", "Bring some glow to the people you love."),
    ("Diwali isn't one day. It's five.", "Dhanteras, Choti Diwali, Diwali,\nGovardhan Puja and Bhai Dooj.", "Five days. Plenty of people to gift."),
    ("Many faiths, one festival of lights.", "Rama's return to Ayodhya, Bandi Chhor Divas for Sikhs,\nand Mahavira's nirvana for Jains.", "However you celebrate, gift something that lasts."),
    ("Why do we exchange gifts?", "Sharing sweets and gifts at Diwali is about\nsharing good fortune with the people around you.", "Share the good fortune. Gift a scent."),
    ("Rangoli is a welcome mat.", "The colours at the doorstep welcome\nguests and good luck into the home.", "Walk in with a gift worth the welcome."),
    ("Bhai Dooj closes the five days.", "The last day celebrates the bond\nbetween brothers and sisters.", "Sorted the sibling gift yet?"),
]
GIFTS = [  # (box photo, who it's for, set name, line)
    ("bouquet", "For the sister who 'borrows' your perfume", "Bouquet Diwali set", "fresh, fruity, floral"),
    ("derossa", "For the man who walks in like he owns the party", "De Rossa Oudh Diwali set", "warm, woody, amber"),
    ("misspoem", "For the one who remembers every date", "Miss Poem Diwali set", "soft, sweet, romantic"),
    ("holdmi", "For the brother who smells like 'deo only'", "Hold Mi Diwali set", "an upgrade he needs"),
    ("flora5", "For the mother-in-law you want to impress", "Flora 5 Diwali set", "powdery, floral, graceful"),
    ("mraqua", "For the friend who is always 'on the way'", "Mr Aqua Diwali set", "fresh, aquatic, easy"),
]

def background(seed, top=(30, 10, 40), bot=(70, 12, 26)):
    yy = np.linspace(0, 1, H)[:, None, None]
    a = (np.array(top) * (1 - yy) + np.array(bot) * yy) * np.ones((1, W, 1))
    im = Image.fromarray(a.astype(np.uint8)).convert("RGBA")
    rng = np.random.default_rng(seed); lay = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(lay)
    for _ in range(55):
        x, y, r = rng.uniform(0, W), rng.uniform(0, H), rng.uniform(5, 30)
        d.ellipse((x - r, y - r, x + r, y + r), fill=GOLD + (int(rng.uniform(20, 70)),))
    im.alpha_composite(lay.filter(ImageFilter.GaussianBlur(7))); return im

def diya_row(im, y, n=9, span=860):
    """a gentle arc of lamp glows: the 'row of lights'"""
    glow = Image.new("RGBA", (W, H)); g = ImageDraw.Draw(glow); core = Image.new("RGBA", (W, H)); c = ImageDraw.Draw(core)
    for k in range(n):
        u = k / (n - 1); x = (W - span) / 2 + span * u; yy = y + 40 * (2 * u - 1) ** 2
        g.ellipse((x - 46, yy - 70, x + 46, yy + 20), fill=(255, 170, 70, 120))
        c.polygon([(x, yy - 34), (x - 11, yy - 6), (x, yy + 4), (x + 11, yy - 6)], fill=(255, 226, 150, 255))   # flame
        c.chord((x - 30, yy - 8, x + 30, yy + 30), 0, 180, fill=(170, 84, 40, 255))                            # clay lamp
    im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(22))); im.alpha_composite(core)

def wrap_center(d, y, text, f, fill, maxw=900, lh=1.18):
    lines = []
    for para in text.split("\n"):
        cur = ""
        for w_ in para.split():
            t = (cur + " " + w_).strip()
            if d.textlength(t, font=f) <= maxw: cur = t
            else: lines.append(cur); cur = w_
        lines.append(cur)
    for ln in lines: d.text((W / 2, y), ln, font=f, fill=fill, anchor="ma"); y += f.size * lh
    return y

def pill(im, y, text, f, bg=GOLD, fg=(40, 8, 16), padx=40, h=78):
    d = ImageDraw.Draw(im); tw = d.textlength(text, font=f)
    d.rounded_rectangle(((W - tw) / 2 - padx, y, (W + tw) / 2 + padx, y + h), h // 2, fill=bg)
    d.text((W / 2, y + h / 2), text, font=f, fill=fg, anchor="mm")

def rounded(img, size, rad=32, border=GOLD):
    im = img.convert("RGB").resize((size, size), Image.LANCZOS).convert("RGBA")
    m = Image.new("L", (size, size), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, size - 1, size - 1), rad, fill=255); im.putalpha(m)
    fr = Image.new("RGBA", (size + 10, size + 10)); ImageDraw.Draw(fr).rounded_rectangle((0, 0, size + 9, size + 9), rad + 5, fill=border + (255,))
    fr.alpha_composite(im, (5, 5)); return fr

def countdown_label(days):
    if days is None: return None
    return "DIWALI IS TODAY" if days == 0 else ("1 DAY TO DIWALI" if days == 1 else f"{days} DAYS TO DIWALI")

def fact(n, out, days=None):
    title, body, tie = FACTS[(n - 1) % len(FACTS)]
    return _fact_final(n, out, days, title, body, tie, GIFTS[(n - 1) % len(GIFTS)][0])

def _fact_final(n, out, days, title, body, tie, box):
    im = background(100 + n); d = ImageDraw.Draw(im)
    lab = countdown_label(days)
    if lab: d.text((W / 2, 205), lab, font=pop(30, "Bold"), fill=(255, 210, 150), anchor="ma")
    pill(im, 260, f"DIWALI FUN FACT  #{n}", inter(40, "Black"))
    y = wrap_center(d, 420, title, inter(92, "Black"), IVORY, maxw=920, lh=1.1)
    y = wrap_center(d, y + 40, body, lora(48), (240, 214, 178), maxw=960, lh=1.3)
    diya_row(im, max(y + 110, 1040)); d = ImageDraw.Draw(im)
    yb = 1270; card = rounded(Image.open(BOX + box + "_box.jpg"), 300); im.alpha_composite(card, (80, yb))
    tx, maxw = 425, 590
    def colwrap(y, text, f, fill, lh=1.18):
        cur = ""
        for w_ in text.split():
            t = (cur + " " + w_).strip()
            if d.textlength(t, font=f) <= maxw: cur = t
            else: d.text((tx, y), cur, font=f, fill=fill); y += f.size * lh; cur = w_
        d.text((tx, y), cur, font=f, fill=fill); return y + f.size * lh
    y2 = colwrap(yb + 14, tie, inter(46, "ExtraBold"), IVORY)
    y2 = colwrap(y2 + 10, "Buy one perfume, get the whole Diwali set.", pop(34, "Medium"), (240, 214, 178))
    d.rounded_rectangle((tx, y2 + 16, tx + 400, y2 + 86), 35, fill=GOLD); d.text((tx + 200, y2 + 51), "Reply 'GIFT' for prices", font=pop(30, "Bold"), fill=(40, 8, 16), anchor="mm")
    lg = LOGO.resize((150, int(LOGO.height * 150 / LOGO.width)), Image.LANCZOS); im.alpha_composite(lg, ((W - 150) // 2, 1640))
    im.convert("RGB").save(out, quality=92); return out

def gift(n, out, days=None):
    box, who, setname, mood = GIFTS[(n - 1) % len(GIFTS)]
    im = background(200 + n, top=(52, 10, 24), bot=(24, 6, 12))
    photo = Image.open(BOX + box + "_box.jpg").convert("RGB").resize((W, W), Image.LANCZOS).convert("RGBA")
    fade = Image.linear_gradient("L").resize((W, W)).point(lambda v: 255 if v < 150 else int(255 * max(0, 1 - (v - 150) / 105)))
    photo.putalpha(fade); im.alpha_composite(photo, (0, 0)); d = ImageDraw.Draw(im)
    top = Image.new("RGBA", (W, 420)); top.putalpha(Image.linear_gradient("L").rotate(180).resize((W, 420)).point(lambda v: int(v * 0.65)))
    im.alpha_composite(Image.composite(Image.new("RGBA", (W, 420), (10, 2, 6, 255)), Image.new("RGBA", (W, 420)), top.getchannel("A")), (0, 0))
    lab = countdown_label(days)
    pill(im, 230, "DIWALI GIFT IDEA" + (f"  ·  {lab}" if lab else ""), inter(34, "Black"), h=70)
    d = ImageDraw.Draw(im)
    y = wrap_center(d, 1010, who, inter(80, "Black"), IVORY, maxw=900, lh=1.1)
    d.text((W / 2, y + 24), setname, font=lora(56), fill=GOLD, anchor="ma")
    d.text((W / 2, y + 104), f"body wash  +  perfume  +  moisturiser   ·   {mood}", font=pop(30, "Medium"), fill=(236, 214, 190), anchor="ma")
    y = y + 190
    d.text((W / 2, y), "Buy one perfume, get the whole Diwali set", font=pop(38, "Bold"), fill=IVORY, anchor="ma")
    d.text((W / 2, y + 62), "Delhi NCR delivery in 2-3 hours*", font=pop(34, "Medium"), fill=(255, 214, 160), anchor="ma")
    pill(im, y + 140, "REPLY 'GIFT' FOR PRICES", inter(40, "Black"), h=84)
    d.text((W / 2, y + 250), "*During office hours  ·  O-17, Lajpat Nagar-II", font=pop(26, "Medium"), fill=(220, 200, 180), anchor="ma")
    im.convert("RGB").save(out, quality=92); return out

if __name__ == "__main__":
    outdir = sys.argv[1]; os.makedirs(outdir, exist_ok=True); a = sys.argv[2:]
    days = None
    if "--days" in a: i = a.index("--days"); days = int(a[i + 1]); a = a[:i] + a[i + 2:]
    for kind, n in zip(a[::2], a[1::2]):
        n = int(n); p = f"{outdir}/{kind}_{n}.jpg"
        (fact if kind == "fact" else gift)(n, p, days); print(p)

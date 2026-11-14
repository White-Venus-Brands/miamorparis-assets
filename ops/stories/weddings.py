"""Wedding-season Stories (after Bhai Dooj, 11 Nov 2026). Same two-story format as diwali.py:
  09:00  fact(n)  -> a light, CONFIRMED wedding-season fact, soft gifting line, real gift-box photo.
  21:00  gift(n)  -> "For the ... who ..." wedding-guest gift idea on a REAL gift-box photo.
1080x1920. No prices ("Reply 'GIFT' for prices"). Gift-box offer wording exactly as in ops/PLAYBOOK.md.
Usage: python3 ops/stories/weddings.py OUTDIR fact 1 flora5 gift 1
Sources for facts: ops/stories/diwali_sources.md (Wedding season section).
"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from diwali import (W, H, GOLD, IVORY, background, wrap_center, pill, rounded, boxphoto, inter, lora, pop)

OFFER = "Buy one perfume, get the whole Diwali set"   # playbook wording (Tannay 3 Nov); change only when he does

WFACTS = [  # (headline, detail, gifting line). Verified by web search; sources in diwali_sources.md
    ("46 lakh weddings. 45 days.", "Traders' body CAIT's estimate for India's 2025 wedding season, from 1 November to 14 December.", "So many shaadis. Gifts sorted?"),
    ("Delhi alone: 4.8 lakh weddings.", "CAIT's estimate for the capital in the 2025 wedding season, 1 November to 14 December.", "Your shaadi calendar full too?"),
    ("Shaadi season:\n1 crore jobs.", "CAIT expected India's 2025 wedding season to create over 1 crore temporary jobs, in catering, event setup, logistics and hospitality.", "Big season. Long guest list. Gifts sorted?"),
    ("70% made in India.", "CAIT says over 70% of wedding-related purchases in the 2025 season were expected to be Indian-made.", "Long shaadi list? Gifts sorted?"),
]
WGIFTS = [  # (box key, who it's for, set name, scent words FROM THE SHOPIFY LISTING TITLE)
    ("smuggler", "For the baraati who dances first, leaves last", "Smuggler gift set", "sweet, vanilla, coffee"),
    ("moksha", "For the groom who got ready in 10 minutes", "Moksha gift set", "citrus, woody, musky"),
    ("mraqua", "For the cousin who becomes the DJ at every sangeet", "Mr Aqua gift set", "woody, citrus, spicy"),
    ("misspoem", "For the bride's best friend who planned the whole sangeet", "Miss Poem gift set", "floral, sweet, elegant"),
]
SETNAME = {"flora5": "Flora 5 gift set", "smuggler": "Smuggler gift set", "bouquet": "Bouquet gift set", "misspoem": "Miss Poem gift set",
           "liita": "Love Is In The Air gift set", "marhaba": "Marhaba Oudh gift set", "holdmi": "Hold Mi gift set",
           "derossa": "De Rossa Oudh gift set", "moksha": "Moksha gift set", "mraqua": "Mr Aqua gift set"}

def toran(im, y, n=13):
    """a string of marigolds: the wedding-gate garland"""
    glow = Image.new("RGBA", (W, H)); g = ImageDraw.Draw(glow); core = Image.new("RGBA", (W, H)); c = ImageDraw.Draw(core)
    pts = [(60 + (W - 120) * k / (n - 1), y + 70 * (1 - (2 * k / (n - 1) - 1) ** 2)) for k in range(n)]
    c.line(pts, fill=(150, 110, 60, 255), width=3)
    for k, (x, yy) in enumerate(pts):
        col = (255, 150, 20) if k % 2 == 0 else (255, 196, 40)
        g.ellipse((x - 40, yy - 40, x + 40, yy + 40), fill=col + (90,))
        for r, sh in ((26, 0), (19, 30), (11, 60)):
            c.ellipse((x - r, yy - r, x + r, yy + r), fill=(max(col[0] - sh, 0), max(col[1] - sh, 0), max(col[2] - 10, 0), 255))
        if k % 3 == 1:  # small hanging drop
            c.line((x, yy + 26, x, yy + 70), fill=(150, 110, 60, 255), width=2)
            c.ellipse((x - 12, yy + 64, x + 12, yy + 88), fill=(255, 170, 30, 255))
    im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(18))); im.alpha_composite(core)

def fact(n, out, box):
    title, body, tie = WFACTS[(n - 1) % len(WFACTS)]
    im = background(300 + n, top=(36, 8, 30), bot=(80, 14, 24)); d = ImageDraw.Draw(im)
    pill(im, 230, f"WEDDING SEASON FACT  #{n}", inter(40, "Black"))
    y = wrap_center(d, 420, title, inter(92, "Black"), IVORY, maxw=920, lh=1.1)
    y = wrap_center(d, y + 36, body, lora(48), (240, 214, 178), maxw=900, lh=1.3)
    ty = max(y + 40, 800); toran(im, ty); d = ImageDraw.Draw(im)
    y2 = ty + 150
    y2 = wrap_center(d, y2, tie, inter(46, "ExtraBold"), IVORY, maxw=940, lh=1.15)
    d.text((W / 2, y2 + 4), "Today's pick: " + SETNAME[box], font=lora(46), fill=GOLD, anchor="ma")
    cs = int(min(540, 1640 - (y2 + 80))); card = rounded(boxphoto(box), cs); im.alpha_composite(card, ((W - card.width) // 2, int(y2 + 75)))
    yp = y2 + 75 + card.height + 30
    pill(im, yp, "REPLY 'GIFT' FOR PRICES", inter(40, "Black"), h=84)
    d = ImageDraw.Draw(im); d.text((W / 2, yp + 108), OFFER, font=pop(32, "Medium"), fill=(240, 214, 178), anchor="ma")
    im.convert("RGB").save(out, quality=92); return out

def gift(n, out):
    box, who, setname, mood = WGIFTS[(n - 1) % len(WGIFTS)]
    im = background(400 + n, top=(52, 10, 24), bot=(24, 6, 12))
    photo = boxphoto(box).convert("RGB").resize((W, W), Image.LANCZOS).convert("RGBA")
    fade = Image.linear_gradient("L").resize((W, W)).point(lambda v: 255 if v < 150 else int(255 * max(0, 1 - (v - 150) / 105)))
    photo.putalpha(fade); im.alpha_composite(photo, (0, 0))
    top = Image.new("RGBA", (W, 420)); top.putalpha(Image.linear_gradient("L").rotate(180).resize((W, 420)).point(lambda v: int(v * 0.65)))
    im.alpha_composite(Image.composite(Image.new("RGBA", (W, 420), (10, 2, 6, 255)), Image.new("RGBA", (W, 420)), top.getchannel("A")), (0, 0))
    pill(im, 215, "WEDDING SEASON GIFT IDEA", inter(40, "Black"), h=78, padx=50)
    d = ImageDraw.Draw(im)
    y = wrap_center(d, 1010, who, inter(80, "Black"), IVORY, maxw=900, lh=1.1)
    d.text((W / 2, y + 24), setname, font=lora(56), fill=GOLD, anchor="ma")
    d.text((W / 2, y + 104), f"body wash  +  perfume  +  moisturiser   ·   {mood}", font=pop(30, "Medium"), fill=(236, 214, 190), anchor="ma")
    y = y + 190
    d.text((W / 2, y), OFFER, font=pop(38, "Bold"), fill=IVORY, anchor="ma")
    d.text((W / 2, y + 62), "Delhi NCR delivery in 2-3 hours*", font=pop(34, "Medium"), fill=(255, 214, 160), anchor="ma")
    pill(im, y + 140, "REPLY 'GIFT' FOR PRICES", inter(40, "Black"), h=84)
    d.text((W / 2, y + 250), "*During office hours  ·  O-17, Lajpat Nagar-II", font=pop(26, "Medium"), fill=(220, 200, 180), anchor="ma")
    im.convert("RGB").save(out, quality=92); return out

if __name__ == "__main__":
    outdir = sys.argv[1]; os.makedirs(outdir, exist_ok=True); a = sys.argv[2:]; i = 0
    while i < len(a):
        if a[i] == "fact": print(fact(int(a[i + 1]), f"{outdir}/wfact_{a[i+1]}_{a[i+2]}.jpg", a[i + 2])); i += 3
        else: print(gift(int(a[i + 1]), f"{outdir}/wgift_{a[i+1]}.jpg")); i += 2

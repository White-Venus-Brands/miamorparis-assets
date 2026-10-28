"""Daily 'this or that' Stories: two SCENT MOODS side by side (not product names first). 1080x1920."""
import math, sys, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S = "/tmp/claude-0/-home-claude/e1dc2e45-c278-5714-b377-734372e7d29a/scratchpad/"; O = S + "stories/"
W, H = 1080, 1920
def lora(s, it=False): return ImageFont.truetype("/usr/share/fonts/truetype/google-fonts/Lora-" + ("Italic-Variable" if it else "Variable") + ".ttf", s)
def pop(s, w="Medium"): return ImageFont.truetype(f"/usr/share/fonts/truetype/google-fonts/Poppins-{w}.ttf", s)
BOT = {"mraqua": "bw/mraqua_perf.png", "missaqua": "bw/missaqua_perf.png", "moksha": "bw/moksha_perf.png", "liita": "cut_liita.png", "derossa": "cut_dero.png"}
NAME = {"mraqua": "Mr Aqua", "missaqua": "Miss Aqua", "moksha": "Moksha", "liita": "Love Is In The Air", "derossa": "De Rossa Oudh"}
PRICE = {"mraqua": ("1,499", "2,999"), "missaqua": ("1,499", "2,999"), "moksha": ("1,999", "3,999"), "liita": ("1,999", "3,999"), "derossa": ("1,999", "3,999")}
# mood palettes: (top colour, bottom colour, accent, motif)
MOOD = {"citrus": ((246, 214, 96), (232, 150, 44), (255, 248, 220), "slices"), "floral": ((246, 196, 206), (196, 92, 128), (255, 236, 242), "petals"),
        "ocean": ((150, 210, 228), (30, 96, 150), (232, 248, 255), "waves"), "woody": ((92, 58, 36), (30, 18, 12), (232, 196, 140), "bokeh"),
        "musky": ((236, 230, 220), (176, 164, 148), (255, 252, 246), "haze"), "green": ((196, 226, 150), (74, 140, 84), (244, 255, 232), "leaves")}
rng = np.random.default_rng(int(sys.argv[2]) if len(sys.argv) > 2 else 1)
def grad(w, h, top, bot, ang=0.0):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32); u = (yy / h) * math.cos(ang) + (xx / w) * math.sin(ang); u = (u - u.min()) / (u.max() - u.min())
    a = np.array(top, np.float32) * (1 - u[..., None]) + np.array(bot, np.float32) * u[..., None]
    return Image.fromarray(a.astype(np.uint8)).convert("RGBA")
def motif(im, kind, acc):
    w, h = im.size; lay = Image.new("RGBA", im.size); d = ImageDraw.Draw(lay)
    if kind == "slices":
        for _ in range(7):
            cx, cy, r = rng.uniform(0, w), rng.uniform(0, h), rng.uniform(60, 150); d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=acc + (70,), width=10)
            for k in range(8): a = k * math.pi / 4 + rng.uniform(0, .3); d.line((cx, cy, cx + r * .85 * math.cos(a), cy + r * .85 * math.sin(a)), fill=acc + (55,), width=6)
    elif kind == "petals":
        for _ in range(26):
            cx, cy, s = rng.uniform(0, w), rng.uniform(0, h), rng.uniform(26, 70); p = Image.new("RGBA", (int(s * 2), int(s * 4))); ImageDraw.Draw(p).ellipse((0, 0, s * 2 - 1, s * 4 - 1), fill=acc + (int(rng.uniform(50, 110)),))
            p = p.rotate(rng.uniform(0, 360), expand=True, resample=Image.BICUBIC); lay.alpha_composite(p, (int(cx), int(cy)))
    elif kind == "waves":
        for k in range(14):
            y0 = k * h / 13 + rng.uniform(-20, 20); pts = [(x, y0 + 22 * math.sin(x / 70 + k)) for x in range(0, w + 10, 10)]; d.line(pts, fill=acc + (60,), width=5)
    elif kind == "bokeh":
        for _ in range(40):
            cx, cy, r = rng.uniform(0, w), rng.uniform(0, h), rng.uniform(12, 60); d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=acc + (int(rng.uniform(25, 80)),))
        lay = lay.filter(ImageFilter.GaussianBlur(6))
    elif kind == "haze":
        for _ in range(12):
            cx, cy, r = rng.uniform(0, w), rng.uniform(0, h), rng.uniform(120, 300); d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=acc + (60,))
        lay = lay.filter(ImageFilter.GaussianBlur(40))
    elif kind == "leaves":
        for _ in range(16):
            cx, cy, s = rng.uniform(0, w), rng.uniform(0, h), rng.uniform(40, 90); p = Image.new("RGBA", (int(s * 2), int(s * 4))); pd = ImageDraw.Draw(p)
            pd.ellipse((0, 0, s * 2 - 1, s * 4 - 1), fill=acc + (70,)); pd.line((s, 4, s, s * 4 - 4), fill=acc + (120,), width=4)
            p = p.rotate(rng.uniform(0, 360), expand=True, resample=Image.BICUBIC); lay.alpha_composite(p, (int(cx), int(cy)))
    im.alpha_composite(lay)
def bottle(key, hgt):
    p = Image.open(S + BOT[key]).convert("RGBA"); p = p.crop(p.getbbox()); return p.resize((int(p.width * hgt / p.height), hgt), Image.LANCZOS)
def ctext(d, x, y, s, f, col, anchor="mm"): d.text((x, y), s, font=f, fill=col, anchor=anchor)
def story(out, left, right, question, footer_note=None):
    (lm, lk, lmood, lnotes), (rm, rk, rmood, rnotes) = left, right
    im = Image.new("RGBA", (W, H))
    # diagonal split
    A = grad(W, H, MOOD[lmood][0], MOOD[lmood][1], 0.3); motif(A, MOOD[lmood][3], MOOD[lmood][2])
    B = grad(W, H, MOOD[rmood][0], MOOD[rmood][1], -0.3); motif(B, MOOD[rmood][3], MOOD[rmood][2])
    m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).polygon([(0, 0), (W * .5 + 70, 0), (W * .5 - 70, H), (0, H)], fill=255); m = m.filter(ImageFilter.GaussianBlur(2))
    im = Image.composite(A, B, m); d = ImageDraw.Draw(im)
    d.line([(W * .5 + 70, 0), (W * .5 - 70, H)], fill=(255, 250, 240), width=6)
    # header band
    hb = Image.new("RGBA", (W, H)); ImageDraw.Draw(hb).rectangle((0, 250, W, 470), fill=(18, 14, 12, 215)); im.alpha_composite(hb); d = ImageDraw.Draw(im)
    ctext(d, W / 2, 315, "THIS  OR  THAT", pop(30, "SemiBold") if False else pop(30, "Bold"), (212, 170, 100))
    ctext(d, W / 2, 400, question, lora(64, True), (250, 242, 228))
    # VS badge
    d.ellipse((W / 2 - 62, 1010 - 62, W / 2 + 62, 1010 + 62), fill=(18, 14, 12)); d.ellipse((W / 2 - 62, 948, W / 2 + 62, 1072), outline=(212, 170, 100), width=4)
    ctext(d, W / 2, 1012, "or", lora(56, True), (240, 212, 156))
    for side, (mood_txt, key, mood, notes) in enumerate([left, right]):
        cx = 270 if side == 0 else 810
        b = bottle(key, 520 if key not in ("missaqua",) else 560); sh = Image.new("RGBA", (W, H)); ImageDraw.Draw(sh).ellipse((cx - b.width * .55, 1300 - 24, cx + b.width * .55, 1300 + 24), fill=(0, 0, 0, 90))
        im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14))); im.alpha_composite(b, (int(cx - b.width / 2), 1300 - b.height)); d = ImageDraw.Draw(im)
        dark = mood in ("woody", "ocean")
        # label card
        card = Image.new("RGBA", (W, H)); cd = ImageDraw.Draw(card); cd.rounded_rectangle((cx - 235, 1330, cx + 235, 1600), radius=28, fill=(255, 252, 246, 235) if not dark else (20, 16, 14, 225)); im.alpha_composite(card); d = ImageDraw.Draw(im)
        fg = (40, 30, 24) if not dark else (250, 240, 224); ac = (168, 110, 50) if not dark else (232, 196, 140)
        ctext(d, cx, 1360, "1" if side == 0 else "2", pop(30, "Bold"), ac)
        l1 = mood_txt.split("\n")
        for i, ln in enumerate(l1): ctext(d, cx, 1410 + i * 52, ln, pop(44, "Bold"), fg)
        yy = 1410 + len(l1) * 52 + 6
        ctext(d, cx, yy, notes, pop(25), fg); yy += 44
        ctext(d, cx, yy, f"{NAME[key]}  ·  ₹{PRICE[key][0]}", pop(26, "Medium"), ac)
    # footer
    fb = Image.new("RGBA", (W, H)); ImageDraw.Draw(fb).rectangle((0, 1640, W, 1760), fill=(18, 14, 12, 215)); im.alpha_composite(fb); d = ImageDraw.Draw(im)
    ctext(d, W / 2, 1683, "Reply 1 or 2  ·  we'll tell you more 💬" if False else "Reply 1 or 2 and we'll tell you more", pop(32, "Medium"), (250, 242, 228))
    ctext(d, W / 2, 1728, footer_note or "50% off this Diwali  ·  Mi Amor Paris  ·  link in bio", pop(24), (212, 170, 100))
    im.convert("RGB").save(out, quality=93)

# ---------- "Today's star" single-product Story ----------
def starpoly(cx, cy, r1, r2, n=5):
    return [(cx + (r1 if k % 2 == 0 else r2) * math.sin(k * math.pi / n), cy - (r1 if k % 2 == 0 else r2) * math.cos(k * math.pi / n)) for k in range(2 * n)]
def star(out, path, name, mood, lines, price, was, kind="Perfume", hgt=860):
    top, bot, acc, mot = MOOD[mood]
    im = grad(W, H, top, bot, 0.15); motif(im, mot, acc)
    gl = Image.new("RGBA", (W, H)); ImageDraw.Draw(gl).ellipse((W / 2 - 420, 520, W / 2 + 420, 1340), fill=(255, 250, 235, 120)); im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(90)))
    d = ImageDraw.Draw(im)
    hb = Image.new("RGBA", (W, H)); ImageDraw.Draw(hb).rounded_rectangle((W / 2 - 300, 262, W / 2 + 300, 372), radius=55, fill=(18, 14, 12, 225)); im.alpha_composite(hb); d = ImageDraw.Draw(im)
    for sx in (W / 2 - 236, W / 2 + 236): d.polygon(starpoly(sx, 317, 24, 10), fill=(232, 190, 110))
    ctext(d, W / 2, 318, "TODAY'S STAR", pop(40, "Bold"), (250, 240, 224))
    p = Image.open(S + path).convert("RGBA"); p = p.crop(p.getbbox()); p = p.resize((int(p.width * hgt / p.height), hgt), Image.LANCZOS)
    if p.width > 760: p = p.resize((760, int(p.height * 760 / p.width)), Image.LANCZOS)
    base = 1330; sh = Image.new("RGBA", (W, H)); ImageDraw.Draw(sh).ellipse((W / 2 - p.width * .55, base - 26, W / 2 + p.width * .55, base + 26), fill=(0, 0, 0, 100))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(16))); im.alpha_composite(p, (int(W / 2 - p.width / 2), base - p.height)); d = ImageDraw.Draw(im)
    card = Image.new("RGBA", (W, H)); ImageDraw.Draw(card).rounded_rectangle((70, 1370, W - 70, 1745), radius=34, fill=(18, 14, 12, 228)); im.alpha_composite(card); d = ImageDraw.Draw(im)
    ctext(d, W / 2, 1412, kind.upper(), pop(24, "Bold"), (212, 170, 100))
    ctext(d, W / 2, 1478, name, lora(70), (250, 240, 224))
    ctext(d, W / 2, 1556, lines[0], pop(34, "Bold"), (240, 212, 156))
    ctext(d, W / 2, 1606, lines[1], pop(27), (225, 215, 200))
    f = pop(40, "Bold"); pt = f"₹{price}"; wt = f"₹{was}"; g = pop(30)
    tw = d.textlength(pt, font=f) + 24 + d.textlength(wt, font=g); x0 = (W - tw) / 2
    d.text((x0, 1676), pt, font=f, fill=(250, 240, 224), anchor="lm"); x1 = x0 + d.textlength(pt, font=f) + 24
    d.text((x1, 1678), wt, font=g, fill=(170, 160, 150), anchor="lm"); d.line((x1, 1680, x1 + d.textlength(wt, font=g), 1680), fill=(170, 160, 150), width=3)
    ctext(d, W / 2, 1725, "50% off this Diwali  ·  link in bio  ·  Lajpat Nagar-II", pop(22), (212, 170, 100))
    im.convert("RGB").save(out, quality=93)

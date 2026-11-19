"""'Most Wanted' carousel for GTA VI launch day (19 Nov 2026). Flat sunset-city illustration drawn in code,
real product cutouts cel-shaded to match. No game logos, fonts or names. 4 slides, 1080x1350."""
import math, os, random
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps, ImageChops, ImageEnhance

D = os.path.dirname(os.path.abspath(__file__)) + "/"
CUT = D + "../../assets/cutouts/"
W, H = 1080, 1350
SS = 2                      # supersample for smooth shapes
def F(s, w="Black"): return ImageFont.truetype(f"/usr/share/fonts/opentype/inter/Inter-{w}.otf", s)
def LORA(s): return ImageFont.truetype("/usr/share/fonts/truetype/google-fonts/Lora-Italic-Variable.ttf", s)

def lerpc(a, b, t): return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))
def grad(stops, w, h):
    im = Image.new("RGB", (1, h))
    for y in range(h):
        t = y / (h - 1)
        for i in range(len(stops) - 1):
            if stops[i][0] <= t <= stops[i + 1][0]:
                u = (t - stops[i][0]) / (stops[i + 1][0] - stops[i][0]); im.putpixel((0, y), lerpc(stops[i][1], stops[i + 1][1], u)); break
    return im.resize((w, h))

DUSK = [(0, (40, 14, 82)), (.35, (120, 36, 140)), (.62, (232, 82, 130)), (.8, (255, 150, 90)), (1, (255, 196, 120))]
NIGHT = [(0, (10, 8, 34)), (.5, (44, 18, 86)), (.85, (150, 40, 120)), (1, (230, 90, 110))]

def clouds(d, w, horizon, seed, cols):
    r = random.Random(seed)
    for _ in range(16):
        y = r.uniform(.05, .85) * horizon; x = r.uniform(-200, w); L = r.uniform(180, 520) * SS; h = r.uniform(10, 26) * SS
        c = r.choice(cols); pts = []
        steps = 6
        for i in range(steps + 1):
            pts.append((x + L * i / steps, y - h * (.4 + .6 * r.random())))
        for i in range(steps, -1, -1):
            pts.append((x + L * i / steps + r.uniform(-20, 20), y + h * (.3 + .5 * r.random())))
        d.polygon(pts, fill=c)

def sun(img, cx, cy, R):
    s = Image.new("RGBA", img.size); ds = ImageDraw.Draw(s)
    g = grad([(0, (255, 236, 140)), (1, (255, 90, 120))], 2 * R, 2 * R).convert("RGBA")
    m = Image.new("L", (2 * R, 2 * R)); dm = ImageDraw.Draw(m); dm.ellipse((0, 0, 2 * R, 2 * R), fill=255)
    for k in range(6):                       # synthwave cut lines in the lower half
        yy = int(R * 1.05 + k * R * .16); dm.rectangle((0, yy, 2 * R, yy + int(4 * SS + k * 3 * SS)), fill=0)
    s.paste(g, (cx - R, cy - R), m)
    glow = Image.new("RGBA", img.size); ImageDraw.Draw(glow).ellipse((cx - R * 1.6, cy - R * 1.6, cx + R * 1.6, cy + R * 1.6), fill=(255, 170, 120, 70))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(60 * SS))); img.alpha_composite(s)

def skyline(d, w, base, col, seed, landmarks=True, lit=None):
    r = random.Random(seed); x = 0
    while x < w:
        bw = r.randint(40, 110) * SS; bh = r.randint(60, 260) * SS
        d.rectangle((x, base - bh, x + bw, base), fill=col)
        if r.random() < .3: d.rectangle((x + bw * .4, base - bh - 30 * SS, x + bw * .45, base - bh), fill=col)   # antenna
        if lit:
            for wy in range(base - bh + 14 * SS, base - 10 * SS, 22 * SS):
                for wx in range(x + 8 * SS, x + bw - 8 * SS, 18 * SS):
                    if r.random() < .25: d.rectangle((wx, wy, wx + 6 * SS, wy + 8 * SS), fill=lit)
        x += bw + r.randint(0, 14) * SS
    if not landmarks: return
    # India Gate
    gx = int(w * .2); gw, gh = 150 * SS, 210 * SS
    d.rectangle((gx, base - gh, gx + gw, base), fill=col); d.rectangle((gx - 10 * SS, base - gh - 18 * SS, gx + gw + 10 * SS, base - gh + 8 * SS), fill=col)
    d.rectangle((gx + gw * .3, base - gh - 40 * SS, gx + gw * .7, base - gh - 18 * SS), fill=col)
    d.ellipse((gx + gw * .42, base - gh - 62 * SS, gx + gw * .58, base - gh - 34 * SS), fill=col)
    # Qutub Minar
    qx = int(w * .72); qh = 360 * SS
    d.polygon([(qx - 28 * SS, base), (qx + 28 * SS, base), (qx + 13 * SS, base - qh), (qx - 13 * SS, base - qh)], fill=col)
    for k in range(1, 5):
        yy = base - qh * k / 5; wdt = 28 * SS - 15 * SS * k / 5 + 8 * SS
        d.rectangle((qx - wdt, yy - 6 * SS, qx + wdt, yy + 4 * SS), fill=col)
    d.rectangle((qx - 6 * SS, base - qh - 24 * SS, qx + 6 * SS, base - qh), fill=col)
    # Lotus Temple
    lx = int(w * .47); lw = 120 * SS
    for k, (dx, hh) in enumerate([(-1, .55), (-.55, .8), (0, 1), (.55, .8), (1, .55)]):
        cx = lx + dx * lw * .7; ph = 120 * SS * hh
        d.polygon([(cx - 34 * SS, base), (cx, base - ph), (cx + 34 * SS, base)], fill=col)
    d.rectangle((lx - lw, base - 20 * SS, lx + lw, base), fill=col)

def _lm(d, w, base, col):
    r = random.Random(0)
    # call skyline's landmark code with zero-width building run
    skyline_lm(d, w, base, col)

def skyline_lm(d, w, base, col):
    # India Gate
    gx = int(w * .14); gw, gh = 170 * SS, 240 * SS
    d.rectangle((gx, base - gh, gx + gw, base), fill=col); d.rectangle((gx - 12 * SS, base - gh - 20 * SS, gx + gw + 12 * SS, base - gh + 8 * SS), fill=col)
    d.rectangle((gx + gw * .3, base - gh - 44 * SS, gx + gw * .7, base - gh - 20 * SS), fill=col)
    d.ellipse((gx + gw * .42, base - gh - 66 * SS, gx + gw * .58, base - gh - 38 * SS), fill=col)
    d.chord((gx + gw * .28, base - gh * .62, gx + gw * .72, base - gh * .2), 180, 360, fill=(255, 150, 120)); d.rectangle((gx + gw * .28, base - gh * .41, gx + gw * .72, base), fill=(255, 150, 120))
    # Qutub Minar
    qx = int(w * .74); qh = 400 * SS
    d.polygon([(qx - 30 * SS, base), (qx + 30 * SS, base), (qx + 13 * SS, base - qh), (qx - 13 * SS, base - qh)], fill=col)
    for k in range(1, 5):
        yy = base - qh * k / 5; wdt = 30 * SS - 16 * SS * k / 5 + 9 * SS
        d.rectangle((qx - wdt, yy - 6 * SS, qx + wdt, yy + 4 * SS), fill=col)
    d.rectangle((qx - 6 * SS, base - qh - 26 * SS, qx + 6 * SS, base - qh), fill=col)

def palm(d, x, base, h, lean, col, scale=1.0):
    pts = []; n = 24
    for i in range(n + 1):
        t = i / n; pts.append((x + lean * t * t, base - h * t))
    for i in range(n):
        wdt = (14 - 7 * i / n) * SS * scale
        d.line([pts[i], pts[i + 1]], fill=col, width=int(wdt * 2))
    tx, ty = pts[-1]
    for ang in (-170, -140, -110, -70, -40, -10, 20, 200):
        a = math.radians(ang); L = h * .38 * scale
        prev = (tx, ty)
        for k in range(1, 13):
            t = k / 12; ex = tx + math.cos(a) * L * t; ey = ty + math.sin(a) * L * t + (L * .5) * t * t
            wdt = (20 * (1 - t) + 3) * SS * scale
            # leaflets
            nx, ny = -math.sin(a), math.cos(a)
            d.polygon([prev, (ex, ey), (ex + nx * wdt * .5 + 6 * SS, ey + abs(ny) * wdt + 10 * SS * t)], fill=col)
            d.polygon([prev, (ex, ey), (ex - nx * wdt * .5 - 6 * SS, ey + abs(ny) * wdt * .6 + 8 * SS * t)], fill=col)
            d.line([prev, (ex, ey)], fill=col, width=int(4 * SS * scale)); prev = (ex, ey)

def scene(kind):
    w, h = W * SS, H * SS
    img = grad(NIGHT if kind == "night" else DUSK, w, h).convert("RGBA"); d = ImageDraw.Draw(img)
    horizon = int(h * (.62 if kind != "pool" else .55))
    clouds(d, w, horizon, 7 + len(kind), [(255, 120, 150), (255, 160, 120), (200, 70, 150), (150, 50, 140)] if kind != "night" else [(70, 30, 110), (110, 40, 130)])
    if kind == "night":
        r = random.Random(3)
        for _ in range(140): x, y = r.randint(0, w), r.randint(0, int(h * .5)); d.ellipse((x, y, x + 3 * SS, y + 3 * SS), fill=(255, 240, 220))
        ImageDraw.Draw(img).ellipse((w * .76, h * .08, w * .76 + 120 * SS, h * .08 + 120 * SS), fill=(255, 236, 200))
    else:
        sun(img, int(w * .5), horizon - 40 * SS, 230 * SS)
    d = ImageDraw.Draw(img)
    skyline(d, w, horizon, (96, 34, 112) if kind != "night" else (40, 18, 70), 11, landmarks=False, lit=None)
    skyline(d, w, horizon + 4 * SS, (66, 22, 86) if kind != "night" else (24, 10, 46), 5, landmarks=False, lit=(255, 200, 120) if kind == "night" else None)
    skyline(ImageDraw.Draw(Image.new("RGB", (8, 8))), 0, horizon + 4 * SS, (0, 0, 0), 5, landmarks=False)
    _lm(d, w, horizon + 4 * SS, (30, 8, 44) if kind != "night" else (10, 4, 22))
    if kind == "pool":
        water = grad([(0, (40, 190, 210)), (1, (20, 90, 150))], w, h - horizon).convert("RGBA"); img.alpha_composite(water, (0, horizon))
        r = random.Random(4)
        for _ in range(60):
            y = r.randint(horizon + 10 * SS, h); x = r.randint(-100, w); L = r.randint(60, 260) * SS
            d.rectangle((x, y, x + L, y + r.randint(3, 7) * SS), fill=r.choice([(255, 150, 160), (255, 210, 150), (120, 230, 240)]))
        d.rectangle((0, int(h * .80), w, h), fill=(232, 150, 120)); d.rectangle((0, int(h * .80), w, int(h * .80) + 10 * SS), fill=(255, 210, 180))
    else:
        # sea / road reflection band
        band = grad([(0, (120, 40, 120)), (1, (36, 12, 52))], w, h - horizon).convert("RGBA"); img.alpha_composite(band, (0, horizon + 4 * SS))
        r = random.Random(9)
        for _ in range(50):
            y = r.randint(horizon + 10 * SS, int(h * .78)); x = r.randint(int(w * .3), int(w * .7)); L = r.randint(40, 200) * SS
            d.rectangle((x - L // 2, y, x + L // 2, y + 4 * SS), fill=(255, 170, 130) if kind != "night" else (255, 200, 140))
        d.rectangle((0, int(h * .80), w, h), fill=(30, 10, 40)); d.rectangle((0, int(h * .80), w, int(h * .80) + 8 * SS), fill=(255, 120, 150))
    pc = (34, 8, 48) if kind != "night" else (10, 4, 22)
    palm(d, int(w * .06), int(h * .82), 760 * SS, 120 * SS, pc); palm(d, int(w * .95), int(h * .82), 640 * SS, -140 * SS, pc, .9)
    palm(d, int(w * .86), int(h * .82), 430 * SS, -40 * SS, pc, .7)
    return img

def toon(name, height):
    """cel-shade a real cutout: posterize a little, warm sunset rim, thick dark outline."""
    im = Image.open(CUT + name + ".png").convert("RGBA")
    bb = im.getchannel("A").point(lambda v: 255 if v > 40 else 0).getbbox(); im = im.crop(bb)
    im = im.resize((int(im.width * height / im.height), height), Image.LANCZOS)
    rgb = ImageEnhance.Contrast(ImageEnhance.Color(im.convert("RGB")).enhance(1.25)).enhance(1.12)
    rgb = ImageOps.posterize(rgb, 5)
    tint = Image.new("RGB", im.size, (255, 140, 120)); rgb = Image.blend(rgb, ImageChops.screen(rgb, tint), .18)
    a = im.getchannel("A").point(lambda v: 255 if v > 100 else 0).filter(ImageFilter.MinFilter(5))
    out = Image.new("RGBA", (im.width + 40, im.height + 40)); stroke = a.filter(ImageFilter.MaxFilter(11))
    out.paste((24, 6, 30, 255), (20, 20), stroke)
    body = rgb.convert("RGBA"); body.putalpha(a); out.alpha_composite(body, (20, 20))
    return out

def place(img, sprite, cx, base, shadow=True):
    x = int(cx - sprite.width / 2); y = int(base - sprite.height)
    if shadow:
        sh = Image.new("RGBA", img.size); ImageDraw.Draw(sh).ellipse((cx - sprite.width * .45, base - 18, cx + sprite.width * .45, base + 14), fill=(10, 0, 20, 150))
        img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
        refl = ImageOps.flip(sprite).crop((0, 0, sprite.width, min(sprite.height, 200)))
        fade = Image.linear_gradient("L").resize((1, 256)).point(lambda v: 255 - v).resize(refl.size)
        refl.putalpha(ImageChops.multiply(refl.getchannel("A").point(lambda v: int(v * .28)), fade))
        img.alpha_composite(refl, (x, base - 20))
    img.alpha_composite(sprite, (x, y))

def outlined(d, xy, s, font, fill=(255, 255, 255), stroke=(16, 4, 20), sw=8, anchor="la"):
    d.text(xy, s, font=font, fill=fill, stroke_width=sw, stroke_fill=stroke, anchor=anchor)

def stars(d, x, y, n=5, size=44, filled=5):
    for i in range(n):
        cx = x + i * size * 1.25; pts = []
        for k in range(10):
            r = size / 2 if k % 2 == 0 else size / 4.6; a = -math.pi / 2 + k * math.pi / 5
            pts.append((cx + r * math.cos(a), y + r * math.sin(a)))
        d.polygon(pts, fill=(255, 255, 255) if i < filled else (60, 60, 60), outline=(16, 4, 20), width=5)

def finish(img_ss): return img_ss.resize((W, H), Image.LANCZOS)

def slide1():
    im = finish(scene("dusk")); d = ImageDraw.Draw(im)
    place(im, toon("moksha", 600), W // 2, 1110)
    outlined(d, (60, 70), "MOST", F(150), sw=10); outlined(d, (60, 220), "WANTED", F(150), sw=10)
    stars(d, 100, 430, size=72, filled=5)
    outlined(d, (W // 2, 1190), "Wanted for smelling this good.", F(50, "ExtraBold"), sw=6, anchor="ma")
    outlined(d, (W // 2, 1262), "Delhi edition  ·  swipe →", F(32, "Bold"), fill=(255, 210, 160), sw=4, anchor="ma")
    return im

def crew(kind, items, title, sub):
    im = finish(scene(kind)); d = ImageDraw.Draw(im)
    xs = [210, 540, 870]
    for (name, hgt, label, role), x in zip(items, xs):
        place(im, toon(name, hgt), x, 1120)
    outlined(d, (W // 2, 70), title, F(92), sw=9, anchor="ma"); outlined(d, (W // 2, 182), sub, F(36, "Bold"), fill=(255, 210, 160), sw=4, anchor="ma")
    for (name, hgt, label, role), x in zip(items, xs):
        outlined(d, (x, 1175), label, F(34), sw=5, anchor="ma"); outlined(d, (x, 1222), role, F(28, "SemiBold"), fill=(255, 210, 160), sw=4, anchor="ma")
    return im

def helicopter(d, cx, cy, s, col):
    d.ellipse((cx - 150 * s, cy - 55 * s, cx + 110 * s, cy + 55 * s), fill=col)                          # cabin
    d.polygon([(cx + 80 * s, cy - 20 * s), (cx + 330 * s, cy - 12 * s), (cx + 330 * s, cy + 6 * s), (cx + 80 * s, cy + 25 * s)], fill=col)   # tail
    d.polygon([(cx + 310 * s, cy - 60 * s), (cx + 345 * s, cy - 60 * s), (cx + 335 * s, cy + 10 * s), (cx + 315 * s, cy + 10 * s)], fill=col)
    d.rectangle((cx - 10 * s, cy - 80 * s, cx + 10 * s, cy - 55 * s), fill=col); d.rectangle((cx - 330 * s, cy - 88 * s, cx + 330 * s, cy - 80 * s), fill=col)
    d.line([(cx - 110 * s, cy + 80 * s), (cx + 90 * s, cy + 80 * s)], fill=col, width=int(8 * s))
    for xx in (-70, 50): d.line([(cx + xx * s, cy + 50 * s), (cx + xx * s, cy + 80 * s)], fill=col, width=int(7 * s))
    d.ellipse((cx - 140 * s, cy - 40 * s, cx - 60 * s, cy + 10 * s), fill=(255, 200, 140))                # lit window

def slide4():
    big = scene("night"); im = finish(big)
    beam = Image.new("RGBA", (W, H)); ImageDraw.Draw(beam).polygon([(430, 250), (500, 250), (900, 1090), (180, 1090)], fill=(255, 240, 190, 70))
    im.alpha_composite(beam.filter(ImageFilter.GaussianBlur(14)))
    d = ImageDraw.Draw(im); helicopter(d, 470, 190, .8, (8, 4, 18))
    place(im, toon("moksha", 400), 370, 1090); place(im, toon("liita", 370), 710, 1090)
    outlined(d, (W // 2, 330), "MISSION", F(130), fill=(255, 196, 60), sw=10, anchor="ma"); outlined(d, (W // 2, 460), "PASSED", F(130), fill=(255, 196, 60), sw=10, anchor="ma")
    outlined(d, (W // 2, 605), "Respect +100", F(46, "ExtraBold"), sw=5, anchor="ma")
    outlined(d, (W // 2, 1165), "Smell expensive: complete.", F(48, "ExtraBold"), sw=6, anchor="ma")
    outlined(d, (W // 2, 1237), "O-17, Lajpat Nagar-II  ·  miamorparis.in", F(32, "Bold"), fill=(255, 210, 160), sw=4, anchor="ma")
    return im

if __name__ == "__main__":
    S = [slide1(),
         crew("dusk", [("derossa", 470, "DE ROSSA OUDH", "the heavy"), ("moksha", 420, "MOKSHA", "the boss"), ("mraqua_perf", 480, "MR AQUA", "the getaway driver")],
              "CHOOSE YOUR", "character (his crew)"),
         crew("pool", [("flora5_perf", 360, "FLORA 5", "the planner"), ("liita", 420, "LOVE IS IN THE AIR", "the charmer"), ("missaqua_perf", 500, "MISS AQUA", "the fresh face")],
              "CHOOSE YOUR", "character (her crew)"),
         slide4()]
    for i, s in enumerate(S, 1): s.convert("RGB").save(D + f"slide{i}.jpg", quality=94)
    print("ok")

"""3 Nov 2026 feed (rebuilt per Tannay): "Marhaba · Arabian nights, bottled". Unisex, Arabian-nights mood, no prices,
no white-background shots. Set = the real Marhaba photoshoot (rose, saffron, labdanum resin, agarwood, patchouli leaf,
engraved brass podium; mini_life_1.jpg). The 8 ml is taken off the podium (work/make_scene.py) and the real 100 ml bottle,
box, Oudh cream and 8 ml are cut from their studio shots (work/cutout.py) and stood on it with backlight, contact shadow
and brass reflection. Shower gel uses its own real dark lifestyle photo. Last slide: DM for prices & Diwali deals."""
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
W, H = 1080, 1350; BASE = 966
def lora(s, it=False): return ImageFont.truetype("/usr/share/fonts/truetype/google-fonts/Lora-" + ("Italic-Variable" if it else "Variable") + ".ttf", s)
def pop(s, w="Medium"): return ImageFont.truetype(f"/usr/share/fonts/truetype/google-fonts/Poppins-{w}.ttf", s)
GOLD = (214, 172, 96); CHAMP = (242, 224, 186); MUTE = (205, 170, 140)
LOGO = Image.open("../../assets/cutouts/logo_gold.png").convert("RGBA")

def scene(mirror=False):
    s = Image.open("work/scene_clean.png").convert("RGB")
    if mirror: s = ImageOps.mirror(s)
    return s.resize((1350, 1350), Image.LANCZOS).crop((135, 0, 1215, 1350)).convert("RGBA")

def backlight(im, cx, cy, rx, ry, a=150):
    g = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(g)
    d.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=(255, 150, 60, a))
    im.alpha_composite(g.filter(ImageFilter.GaussianBlur(rx * 0.55)))

def prep(path, h, glass):
    p = Image.open(path).convert("RGBA"); w = int(p.width * h / p.height); p = p.resize((w, h), Image.LANCZOS)
    a = np.array(p).astype(np.float32); a[..., :3] *= 0.86; a[..., 0] *= 1.06; a[..., 2] *= 0.86   # warm, dimmer set light
    from scipy import ndimage
    a[..., 3] = ndimage.grey_erosion(a[..., 3], size=(3, 3)); a[h - 3:, :, 3] = 0
    if glass:  # smooth the glass silhouette (studio JPEG edges are ragged)
        import cv2
        m = cv2.GaussianBlur((a[..., 3] > 128).astype(np.float32), (0, 0), 3.5) > 0.5
        m = ndimage.binary_erosion(m, iterations=2); a[..., 3] = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 1.0) * 255
    return a, w, glass

def place(im, path, cx, h, base=BASE, glass=False):
    a, w, glass = prep(path, h, glass); x, y = int(cx - w / 2), base - h
    sh = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(sh)
    d.ellipse((x - 6, base - 12, x + w + 6, base + 10), fill=(0, 0, 0, 170)); d.ellipse((x - 30, base - 22, x + w + 30, base + 18), fill=(0, 0, 0, 70))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)))
    r = a[::-1][:40].copy(); r[..., 3] *= np.linspace(0.18, 0, 40)[:, None]   # faint reflection on the polished brass top
    im.alpha_composite(Image.fromarray(r.astype(np.uint8), "RGBA").filter(ImageFilter.GaussianBlur(1.5)), (x, base))
    if glass:   # clear glass: multiply the near-white glass with the set behind it
        import cv2
        bg = np.array(im.crop((x, y, x + w, y + h))).astype(np.float32); g = cv2.GaussianBlur(a[..., :3] / 255, (0, 0), 2.5)
        bg[..., :3] = cv2.GaussianBlur(bg[..., :3], (0, 0), 3)
        sat = g.max(2) - g.min(2); wgt = (np.clip((g.mean(2) - 0.50) / 0.25, 0, 1) * np.clip((0.24 - sat) / 0.10, 0, 1))[..., None]
        a[..., :3] = a[..., :3] * (1 - wgt) + bg[..., :3] * np.clip(g * 1.25, 0, 1.15) * wgt
    im.alpha_composite(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA"), (x, y))

def arch(im, inset=34):
    """thin double gold pointed (two-centred) arch frame, Arabian architecture, on every slide"""
    import math
    o = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(o)
    for k, al in [(0, 175), (12, 95)]:
        l, r, b = inset + k, W - inset - k, H - inset - k; w = r - l; R = 0.6 * w; spring = 640 + k
        h = math.sqrt(R * R - (R - w / 2) ** 2); ang = math.degrees(math.atan2(-h, -(R - w / 2))) % 360
        d.arc((l, spring - R, l + 2 * R, spring + R), 180, ang, fill=GOLD + (al,), width=2)
        d.arc((r - 2 * R, spring - R, r, spring + R), 540 - ang, 360, fill=GOLD + (al,), width=2)
        d.line((l, spring, l, b, r, b, r, spring), fill=GOLD + (al,), width=2)
    im.alpha_composite(o)

def c(d, y, s, f, col, x=W / 2, anchor="mm"):
    d.text((x + 2, y + 2), s, font=f, fill=(0, 0, 0, 160), anchor=anchor); d.text((x, y), s, font=f, fill=col, anchor=anchor)
def logo(im, w, y):
    l = LOGO.resize((w, int(LOGO.height * w / LOGO.width)), Image.LANCZOS); s = Image.new("RGBA", l.size, GOLD + (0,)); s.putalpha(l.split()[3])
    im.alpha_composite(s, ((W - w) // 2, y))
def bottom_shade(im, hgt=260, a=200):
    v = Image.new("RGBA", (W, hgt)); vd = ImageDraw.Draw(v)
    for y in range(hgt): vd.line((0, y, W, y), fill=(8, 3, 2, int(a * (y / hgt) ** 1.4)))
    im.alpha_composite(v, (0, H - hgt))

out = []
# 1 cover: 100 ml bottle in front of its box on the brass podium
im = scene(); backlight(im, 540, 640, 260, 330)
place(im, "work/box.png", 652, 500, BASE - 10); place(im, "work/perfume.png", 468, 470, BASE + 4, glass=True)
arch(im); d = ImageDraw.Draw(im); logo(im, 64, 70)
c(d, 225, "Marhaba", lora(118, True), CHAMP); c(d, 310, "Arabian nights, bottled", lora(42), CHAMP)
c(d, 368, "UNISEX  ·  OUDH  ·  EXTRAIT DE PARFUM", pop(24, "Medium"), GOLD); out.append(im)

# 2 the notes, on the untouched photoshoot frame (8 ml)
im = Image.open("mini_life_1.jpg").convert("RGB").resize((1350, 1350), Image.LANCZOS).crop((135, 0, 1215, 1350)).convert("RGBA")
arch(im); d = ImageDraw.Draw(im)
c(d, 150, "THE NOTES", pop(24, "Bold"), GOLD, 215, "lm")
for i, (lab, n) in enumerate([("IT OPENS WITH", "Saffron &\nlabdanum"), ("THEN BLOOMS INTO", "Rose &\nagarwood"), ("AND SETTLES ON", "Earthy\npatchouli")]):
    y = 215 + i * 170; c(d, y, lab, pop(20, "Medium"), GOLD, 200 - 40 * i, "lm")
    d.multiline_text((202 - 40 * i, y + 22), n, font=lora(42, True), fill=(0, 0, 0, 150), spacing=4); d.multiline_text((200 - 40 * i, y + 20), n, font=lora(42, True), fill=CHAMP, spacing=4)
c(d, 215, "Also in 8 ml", pop(22, "Medium"), GOLD, W - 190, "rm"); c(d, 255, "for the pocket,", lora(36, True), CHAMP, W - 190, "rm"); c(d, 297, "the clutch, the", lora(36, True), CHAMP, W - 190, "rm"); c(d, 339, "first try.", lora(36, True), CHAMP, W - 190, "rm")
out.append(im)

# 3 shower gel: its own real dark lifestyle photo, on a blurred extension of itself (no flat panel)
ph = Image.open("bodywash_64.jpg").convert("RGB")
bg = ph.resize((1080, 1440)).crop((0, 45, 1080, 1395)).filter(ImageFilter.GaussianBlur(30)); bg = Image.blend(bg, Image.new("RGB", bg.size, (10, 3, 3)), 0.45).convert("RGBA")
fg = ph.resize((int(1080 * 0.80), int(1440 * 0.80)), Image.LANCZOS).convert("RGBA")
m = Image.new("L", fg.size, 0); ImageDraw.Draw(m).rectangle((40, 40, fg.width - 40, fg.height - 40), fill=255); fg.putalpha(m.filter(ImageFilter.GaussianBlur(30)))
bg.alpha_composite(fg, ((W - fg.width) // 2, H - fg.height + 30)); im = bg; arch(im); d = ImageDraw.Draw(im)
c(d, 120, "BEGIN IN THE SHOWER", pop(24, "Bold"), GOLD); c(d, 180, "Marhaba Oudh Shower Gel", lora(54, True), CHAMP)
c(d, 232, "500 ml  ·  glycerin, shea butter & sodium hyaluronate", pop(22), MUTE); out.append(im)

# 4 Oudh moisturizing cream on the (mirrored) set
im = scene(mirror=True); backlight(im, 545, 640, 230, 330); place(im, "work/cream.png", 543, 650)
arch(im); d = ImageDraw.Draw(im)
c(d, 150, "THEN THE CREAM", pop(24, "Bold"), GOLD); c(d, 212, "Marhaba Oudh Moisturizer", lora(54, True), CHAMP)
c(d, 264, "150 ml  ·  shea butter & glycerin  ·  face & body", pop(22), MUTE); out.append(im)

# 5 the family on the podium + CTA
im = scene(); backlight(im, 540, 680, 300, 300)
place(im, "work/cream.png", 372, 560, BASE - 14); place(im, "work/mini.png", 716, 330, BASE - 8, glass=True); place(im, "work/perfume.png", 540, 430, BASE + 6, glass=True)
bottom_shade(im, 330, 235); arch(im); d = ImageDraw.Draw(im)
c(d, 170, "Arabian nights,", lora(66, True), CHAMP); c(d, 245, "every night.", lora(66, True), CHAMP)
c(d, 310, "PERFUME  ·  MOISTURIZER  ·  SHOWER GEL  ·  8 ML", pop(21, "Medium"), GOLD)
c(d, 1196, "DM for prices & Diwali deals", pop(40, "Bold"), CHAMP)
c(d, 1250, "link in bio  ·  O-17, Lajpat Nagar-II, New Delhi", pop(24), MUTE); out.append(im)

for i, s in enumerate(out, 1): s.convert("RGB").save(f"slide_{i:02d}.jpg", quality=93)
sheet = Image.new("RGB", (5 * 432 + 60, 560), (20, 10, 8))
for i, s in enumerate(out): sheet.paste(s.convert("RGB").resize((432, 540)), (10 + i * 442, 10))
sheet.save("csheet.jpg", quality=88); print("ok")

"""4 Nov 2026 feed: "Diwali-ready in three steps" with Flora 5 (shower gel -> cream -> perfume, + 8 ml).
Look: Tannay's real Flora 5 8 ml photoshoot set (ivory silk, ylang-ylang, jasmine, amber, marble podium),
which matches the perfume's listed notes. The mini is digitally removed from the set (work/scene_clean.png)
and each real product cut-out (white studio shots) is placed on the podium with contact shadow and a soft
podium reflection. Slide 5 is the untouched 8 ml photo. Notes from the Shopify listing. No prices on slides (Tannay, 3 Nov): last slide says "DM for prices & Diwali deals"."""
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
W, H = 1080, 1350; K = 1350 / 1254; OX = -135
def lora(s, it=False): return ImageFont.truetype("/usr/share/fonts/truetype/google-fonts/Lora-" + ("Italic-Variable" if it else "Variable") + ".ttf", s)
def pop(s, w="Medium"): return ImageFont.truetype(f"/usr/share/fonts/truetype/google-fonts/Poppins-{w}.ttf", s)
DARK = (66, 42, 24); GOLD = (168, 118, 42); MUTE = (128, 104, 84)
LOGO = Image.open("../../assets/cutouts/logo_gold.png").convert("RGBA")
PODIUM_Y = 1176  # slide y where bottles stand on the podium top

def scene(path="work/scene_clean.png", mirror=False):
    s = Image.open(path).convert("RGB")
    if mirror: s = ImageOps.mirror(s)
    s = s.resize((1350, 1350), Image.LANCZOS).crop((135, 0, 1215, 1350)).convert("RGBA")
    # soften the top a little so text reads cleanly
    v = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(v)
    for y in range(420): d.line((0, y, W, y), fill=(250, 238, 220, int(70 * (1 - y / 420))))
    s.alpha_composite(v); return s

def warm(p, glass=False):
    a = np.array(p).astype(np.float32)
    a[..., :3] *= 0.96; a[..., 0] *= 1.03; a[..., 2] *= 0.93          # match the set's warm light
    al = a[..., 3]; h = al.shape[0]
    al[h - 5:] = 0                                                   # drop the pale studio-floor fringe
    from scipy import ndimage
    al[:] = ndimage.grey_erosion(al, size=(3, 3))                    # kill white halo on edges
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA")

def place(im, path, cx, h, base=PODIUM_Y):
    p = warm(Image.open(path).convert("RGBA"), glass="perfume" in path); w = int(p.width * h / p.height); p = p.resize((w, h), Image.LANCZOS)
    x, y = int(cx - w / 2), base - h
    # contact + soft cast shadow
    sh = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(sh)
    d.ellipse((x - 10, base - 16, x + w + 10, base + 14), fill=(60, 38, 20, 120))
    d.ellipse((x - 40, base - 30, x + w + 30, base + 26), fill=(60, 38, 20, 50))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
    # podium reflection (glossy marble), fades quickly
    r = ImageOps.flip(p).crop((0, 0, w, min(60, h))); ra = np.array(r).astype(np.float32)
    fade = np.linspace(0.12, 0, ra.shape[0])[:, None]; ra[..., 3] *= fade; r = Image.fromarray(ra.astype(np.uint8), "RGBA")
    im.alpha_composite(r.filter(ImageFilter.GaussianBlur(1.5)), (x, base))
    if "perfume" in path:  # clear glass base below the label: multiply-blend so the set shows through the glass
        bgc = np.array(im.crop((x, y, x + w, y + h))).astype(np.float32); pa = np.array(p).astype(np.float32)
        y0 = int(h * 0.89); g = pa[y0:, :, :3] / 255; sat = g.max(2) - g.min(2)
        wgt = (np.clip((g.mean(2) - 0.62) / 0.3, 0, 1) * (sat < 0.18))[..., None] * (pa[y0:, :, 3:] / 255)
        mult = bgc[y0:, :, :3] * np.clip(g * 1.04, 0, 1)
        pa[y0:, :, :3] = pa[y0:, :, :3] * (1 - wgt) + mult * wgt
        p = Image.fromarray(np.clip(pa, 0, 255).astype(np.uint8), "RGBA")
    im.alpha_composite(p, (x, y))

def c(d, y, s, f, col): d.text((W / 2, y), s, font=f, fill=col, anchor="mm")
def logo(im, w, y):
    l = LOGO.resize((w, int(LOGO.height * w / LOGO.width)), Image.LANCZOS)
    a = l.split()[3]; s = Image.new("RGBA", l.size, GOLD + (0,)); s.putalpha(a); im.alpha_composite(s, ((W - w) // 2, y))
def price(d, y, now, was):
    f1, f2 = pop(42, "Bold"), pop(28); a = d.textlength(now, font=f1); b = d.textlength(f"was {was}", font=f2); x = (W - a - 22 - b) / 2
    d.text((x, y), now, font=f1, fill=GOLD, anchor="lm"); d.text((x + a + 22, y + 3), f"was {was}", font=f2, fill=MUTE, anchor="lm")
    d.line((x + a + 22 + d.textlength("was ", font=f2), y + 5, x + a + 22 + b, y + 5), fill=MUTE, width=2)

out = []
# 1 cover: all three on the podium
im = scene(); place(im, "work/gel.png", 318, 720, PODIUM_Y - 8); place(im, "work/cream.png", 768, 620, PODIUM_Y - 6); place(im, "work/perfume.png", 538, 440)
d = ImageDraw.Draw(im); logo(im, 70, 46)
c(d, 160, "Diwali-ready", lora(84, True), DARK); c(d, 240, "in three steps", lora(52), DARK)
c(d, 306, "FLORA 5  ·  SHOWER  ·  CREAM  ·  SCENT", pop(26, "Medium"), GOLD); out.append(im)
# 2 step 1 shower gel
im = scene(mirror=True); place(im, "work/gel.png", 540, 900); d = ImageDraw.Draw(im)
c(d, 70, "STEP 1  ·  SHOWER", pop(28, "Bold"), GOLD); c(d, 130, "Flora 5 Shower Gel", lora(56, True), DARK)
c(d, 182, "500 ml  ·  shea butter & glycerin  ·  soft floral lather", pop(24), MUTE); out.append(im)
# 3 step 2 cream
im = scene(); place(im, "work/cream.png", 540, 880); d = ImageDraw.Draw(im)
c(d, 70, "STEP 2  ·  MOISTURISE", pop(28, "Bold"), GOLD); c(d, 130, "Flora 5 Moisturizing Cream", lora(54, True), DARK)
c(d, 182, "150 ml  ·  face, body & hands  ·  non-greasy", pop(24), MUTE); out.append(im)
# 4 step 3 perfume
im = scene(mirror=True); place(im, "work/perfume.png", 540, 640); d = ImageDraw.Draw(im)
c(d, 70, "STEP 3  ·  SCENT", pop(28, "Bold"), GOLD); c(d, 130, "Flora 5 Perfume", lora(58, True), DARK)
c(d, 186, "Aldehyde & ylang-ylang  ·  jasmine  ·  amber & musk", pop(25), MUTE)
c(d, 228, "100 ml  ·  powdery floral", pop(24), MUTE); out.append(im)
# 5 the real 8 ml photo (untouched) under a backdrop-coloured band + CTA
ph = Image.open("source/mini_8ml_lifestyle.png").convert("RGB").resize((1080, 1080), Image.LANCZOS)
top = np.array(ph)[:6].mean((0, 1)).astype(int)
im = Image.new("RGBA", (W, H), tuple(top) + (255,)); band = Image.new("RGBA", (W, 300)); bd = ImageDraw.Draw(band)
im.alpha_composite(ph.convert("RGBA"), (0, 270))
g = Image.new("RGBA", (W, 60)); gd = ImageDraw.Draw(g)
for y in range(60): gd.line((0, y, W, y), fill=tuple(top) + (int(255 * (1 - y / 60)),))
im.alpha_composite(g, (0, 270))
v = Image.new("RGBA", (W, 170)); vd = ImageDraw.Draw(v)
for y in range(170): vd.line((0, y, W, y), fill=(40, 24, 12, int(150 * y / 170)))
im.alpha_composite(v, (0, H - 170)); d = ImageDraw.Draw(im)
logo(im, 60, 34)
c(d, 128, "TAKE IT WITH YOU", pop(28, "Bold"), GOLD); c(d, 188, "Flora 5 · 8 ml", lora(58, True), DARK)
c(d, 1248, "DM for prices & Diwali deals", pop(36, "Bold"), (255, 250, 240))
c(d, 1300, "link in bio  ·  O-17, Lajpat Nagar-II", pop(26), (255, 246, 230))
out.append(im)
for i, s in enumerate(out, 1): s.convert("RGB").save(f"slide_{i:02d}.jpg", quality=93)
sheet = Image.new("RGB", (5 * 432 + 60, 540 + 20), (30, 22, 16))
for i, s in enumerate(out): sheet.paste(s.convert("RGB").resize((432, 540)), (10 + i * 442, 10))
sheet.save("csheet.jpg", quality=88); print("ok")

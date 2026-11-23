"""Black Friday Stories, Mon 23 Nov (sale live, ends 27 Nov). 3 frames, 1080x1920, real footage/photos only.
Leaves clear space for in-app stickers (countdown, poll). Usage: python3 build.py WORKDIR"""
import os, sys
from PIL import Image, ImageDraw, ImageFilter
D = os.path.dirname(os.path.abspath(__file__)) + "/"
sys.argv = [sys.argv[0], sys.argv[1] if len(sys.argv) > 1 else "/tmp/bfs"]
sys.path.insert(0, D + "../2026-11-21-black-friday-reel")
import build as B   # reuse fonts, text helper, spray grading, photos
W, H = B.W, B.H

def badge(im, cy, label, col=(214, 40, 40)):
    f = B.MS(46, "ExtraBold"); d = ImageDraw.Draw(im); tw = d.textlength(label, font=f); w = int(tw + 120)
    x0 = (W - w) // 2; d.rounded_rectangle((x0, cy - 48, x0 + w, cy + 48), 48, fill=col)
    d.ellipse((x0 + 34, cy - 12, x0 + 58, cy + 12), fill=(255, 255, 255)); d.text((x0 + 76 + tw / 2, cy), label, font=f, fill=(255, 255, 255), anchor="mm")

def sticker_slot(im, cy, h, label):
    """faint dashed box showing where the in-app sticker goes (Tannay covers it with the sticker)"""
    d = ImageDraw.Draw(im); x0, x1 = 170, W - 170
    for x in range(x0, x1, 30): d.line([(x, cy - h // 2), (x + 15, cy - h // 2)], fill=(226, 186, 112, 140), width=3); d.line([(x, cy + h // 2), (x + 15, cy + h // 2)], fill=(226, 186, 112, 140), width=3)
    for y in range(cy - h // 2, cy + h // 2, 30): d.line([(x0, y), (x0, y + 15)], fill=(226, 186, 112, 140), width=3); d.line([(x1, y), (x1, y + 15)], fill=(226, 186, 112, 140), width=3)
    d.text((W // 2, cy), label, font=B.MS(34, "SemiBold"), fill=(226, 186, 112, 170), anchor="mm")

def s1():   # sale live + countdown slot
    im = B.spray("ombre_h", 1.25, 2.6); im.alpha_composite(B.SHADE)
    im.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, 70)))
    B.text(im, 300, "BLACK", B.MS(190)); B.text(im, 480, "FRIDAY", B.MS(190), fill=B.GOLD2)
    B.gold_line(im, 610, 560); B.text(im, 690, "SALE IS LIVE", B.MS(64, "ExtraBold"))
    badge(im, 820, "ENDS 27 NOV")
    sticker_slot(im, 1250, 260, "countdown sticker here")
    B.text(im, 1650, "Perfumes · body wash · gift sets", B.MS(46, "Bold"))
    B.text(im, 1725, "In store at Lajpat Nagar-II + miamorparis.in", B.MS(36, "SemiBold"), fill=B.GOLD2)
    return im

def s2():   # product + poll slot
    im = B.photo("trio", .5); im.alpha_composite(B.SHADE)
    B.text(im, 200, "Shopping for", B.LORA(84), fill=B.GOLD2); B.text(im, 320, "WHO?", B.MS(130))
    sticker_slot(im, 560, 220, "poll sticker: Him / Her / Me")
    B.text(im, 1700, "All in the Black Friday sale", B.MS(48, "Bold"))
    return im

def s3():   # the offer
    im = Image.new("RGBA", (W, H), (8, 6, 6, 255))
    glow = Image.new("RGBA", (W, H)); ImageDraw.Draw(glow).ellipse((90, 420, W - 90, 1300), fill=(226, 186, 112, 45)); im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(120)))
    B.text(im, 330, "The offer", B.LORA(100), fill=B.GOLD2)
    B.text(im, 520, "BUY 1 GET 1", B.MS(140)); badge(im, 690, "FREE", col=(226, 186, 112))
    B.text(im, 830, "or simply take", B.LORA(70), fill=B.GOLD2); B.text(im, 960, "50% OFF", B.MS(140))
    B.gold_line(im, 1080, 520); B.text(im, 1160, "+ CANDLES CLEARANCE SALE", B.MS(52, "ExtraBold"))
    badge(im, 1290, "ENDS 27 NOV")
    B.text(im, 1440, "Reply to this story to order", B.LORA(60))
    B.text(im, 1560, "O-17, Lajpat Nagar-II  ·  miamorparis.in", B.MS(36, "SemiBold"))
    B.text(im, 1820, "*T&C apply", B.MS(28, "Medium"), fill=(200, 190, 175), shadow=False)
    return im

if __name__ == "__main__":
    for i, f in enumerate((s1, s2, s3), 1): f().convert("RGB").save(D + f"story{i}.jpg", quality=94)
    print("ok")

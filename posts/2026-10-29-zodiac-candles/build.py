from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
W, H = 1080, 1350
def lora(s, it=False): return ImageFont.truetype("/usr/share/fonts/truetype/google-fonts/Lora-" + ("Italic-Variable" if it else "Variable") + ".ttf", s)
def pop(s, w="Medium"): return ImageFont.truetype(f"/usr/share/fonts/truetype/google-fonts/Poppins-{w}.ttf", s)
GOLD = (226, 190, 122); IVORY = (246, 238, 224); INK = (14, 16, 30)
SIGNS = [("aries", "Aries", "21 Mar – 19 Apr"), ("taurus", "Taurus", "20 Apr – 20 May"), ("gemini", "Gemini", "21 May – 20 Jun"), ("cancer", "Cancer", "21 Jun – 22 Jul"),
         ("leo", "Leo", "23 Jul – 22 Aug"), ("virgo", "Virgo", "23 Aug – 22 Sep"), ("libra", "Libra", "23 Sep – 22 Oct"), ("scorpio", "Scorpio", "23 Oct – 21 Nov"),
         ("sagittarius", "Sagittarius", "22 Nov – 21 Dec"), ("capricorn", "Capricorn", "22 Dec – 19 Jan"), ("aquarius", "Aquarius", "20 Jan – 18 Feb"), ("pisces", "Pisces", "19 Feb – 20 Mar")]
LOGO = Image.open("../../logo_gold.png").convert("RGBA")
def logo(im, w, y):
    l = LOGO.resize((w, int(LOGO.height * w / LOGO.width)), Image.LANCZOS); im.alpha_composite(l, ((W - w) // 2, y))
def photo(key, size, box=(110, 170, 890, 950)):
    return Image.open(f"{key}_1.jpg").convert("RGB").crop(box).resize((size, size), Image.LANCZOS)
def c(d, y, s, f, col): d.text((W / 2, y), s, font=f, fill=col, anchor="mm")
out = []
# cover: 2x2 grid of four lit candles behind dark overlay
cov = Image.new("RGBA", (W, H), INK + (255,))
hero = Image.open("aquarius_1.jpg").convert("RGB").crop((0, 250, 1000, 944)).resize((1080, 750), Image.LANCZOS); cov.paste(hero, (0, 330))
ov = Image.new("RGBA", (W, H)); od = ImageDraw.Draw(ov); od.rectangle((0, 0, W, 330), fill=INK + (255,))
for y in range(330, 470): od.line((0, y, W, y), fill=INK + (int(255 * (1 - (y - 330) / 140)),))
od.rectangle((0, 1080, W, H), fill=INK + (235,)); cov.alpha_composite(ov); d = ImageDraw.Draw(cov)
logo(cov, 150, 50)
c(d, 200, "This Diwali, gift something", lora(52, True), IVORY); c(d, 268, "written in the stars", lora(60, True), GOLD)
c(d, 1150, "12 ZODIAC CANDLES", pop(44, "Bold"), IVORY); c(d, 1215, "Find their sign  ·  ₹749 each (was ₹1,499)", pop(30), GOLD)
c(d, 1290, "Swipe to find their sign  >>", pop(26, "Medium"), (180, 180, 200)); out.append(cov)
for i, (k, name, dates) in enumerate(SIGNS):
    im = Image.new("RGBA", (W, H), INK + (255,)); im.paste(photo(k, 1080, (110, 170, 890, 950) if k in ("gemini", "cancer", "libra", "aquarius") else (215, 300, 785, 870)), (0, 0)); d = ImageDraw.Draw(im)
    g = Image.new("RGBA", (W, H)); gd = ImageDraw.Draw(g)
    for y in range(900, 1080): gd.line((0, y, W, y), fill=INK + (int(255 * (y - 900) / 180),))
    im.alpha_composite(g); d = ImageDraw.Draw(im)
    d.text((60, 60), f"{i + 1:02d} / 12", font=pop(26, "Medium"), fill=IVORY)
    c(d, 1150, name, lora(84), GOLD); c(d, 1232, dates, pop(32), IVORY)
    c(d, 1295, "Zodiac candle  ·  ₹749", pop(28, "Medium"), (190, 186, 205)); out.append(im)
end = Image.new("RGBA", (W, H), INK + (255,)); d = ImageDraw.Draw(end)
bg = photo("leo", 1080, (150, 150, 850, 850)); bg = ImageEnhance.Brightness(bg.filter(ImageFilter.GaussianBlur(14))).enhance(0.35); end.paste(bg, (0, 135)); d = ImageDraw.Draw(end)
logo(end, 220, 300); c(d, 640, "Know their sign?", lora(70, True), IVORY); c(d, 730, "You already know their gift.", lora(52, True), GOLD)
c(d, 900, "₹749 each this Diwali  ·  was ₹1,499", pop(34, "Bold"), IVORY); c(d, 960, "Link in bio  ·  O-17, Lajpat Nagar-II, New Delhi", pop(28), GOLD); out.append(end)
for n, im in enumerate(out): im.convert("RGB").save(f"slide_{n + 1:02d}.jpg", quality=93)
sh = Image.new("RGB", (7 * 216, 2 * 270))
for n, im in enumerate(out): sh.paste(im.convert("RGB").resize((216, 270)), ((n % 7) * 216, (n // 7) * 270))
sh.save("csheet.jpg"); print(len(out))

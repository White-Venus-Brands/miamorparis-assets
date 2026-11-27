"""Business-owner versions of the best reel (Hinglish 'store room', 10 Nov: 409 reach, 110 shares).
The first 13.7 s stay exactly as posted (hook, counter, Hinglish VO up to 'kabhi store room nahi jaata').
From there the VO stops (music bed continues, same timeline) and on-screen lines + end card speak to one audience:
  corporate  - companies gifting employees and clients at year-end
  planners   - wedding and event planners ordering return gifts
  retail     - retailers and investors: dealer / franchise
  hospitality- hotels, homestays, salons, cafes
Usage: python3 build_b2b.py WORKDIR AUDIENCE"""
import os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw

WORK = sys.argv[1].rstrip("/") + "/"; AUD = sys.argv[2]
sys.argv = [sys.argv[0], WORK + "wed_" + AUD]
D = os.path.dirname(os.path.abspath(__file__)) + "/"; sys.path.insert(0, D)
import build as B
SPLIT = 13.75

V = {
 "corporate": dict(
    lines=[(13.95, 16.8, 360, "Is year-end,"), (15.25, 16.8, 460, "apni team ko..."), (18.15, 19.6, 360, "kuch aisa do jo roz use ho."),
           (19.7, 22.5, 360, "Har spray pe,"), (21.15, 22.5, 460, "company ki yaad aaye.")],
    title="YEAR-END CORPORATE GIFTING", sub="Gift sets for your team and clients", cta="DM \"CORPORATE\" FOR BULK ORDERS"),
 "planners": dict(
    lines=[(13.95, 16.8, 360, "Return gift aisa do..."), (15.25, 16.8, 460, "jo guest ghar le jaaye"), (18.15, 19.6, 360, "aur roz use kare."),
           (19.7, 22.5, 360, "Har spray pe,"), (21.15, 22.5, 460, "shaadi ki yaad aaye.")],
    title="WEDDING RETURN GIFTS", sub="For planners and families ordering in bulk", cta="DM \"WEDDING\" FOR BULK ORDERS"),
 "retail": dict(
    lines=[(13.95, 16.8, 360, "Jo gift use hota hai,"), (15.25, 16.8, 460, "woh bikta bhi hai."), (18.15, 19.6, 360, "Aapke shehar mein..."),
           (19.7, 22.5, 360, "agla Mi Amor Paris"), (21.15, 22.5, 460, "aapka ho sakta hai.")],
    title="OPEN A MI AMOR PARIS STORE", sub="Franchise and dealer enquiries", cta="DM \"FRANCHISE\""),
 "hospitality": dict(
    lines=[(13.95, 16.8, 360, "Guests sab bhool jaate hain..."), (15.25, 16.8, 460, "room, menu, bill."), (18.15, 19.6, 360, "Khushboo nahi."),
           (19.7, 22.5, 360, "Har visit pe,"), (21.15, 22.5, 460, "aapki jagah yaad aaye.")],
    title="FOR HOTELS, SALONS AND CAFES", sub="Hand wash · Body wash · Diffuser oils · Candles", cta="DM \"BULK\" FOR PRICES"),
}[AUD]

B.CAPS = [(a, b, y, s, k) for a, b, y, s, k in B.CAPS_HI if a < SPLIT] + [(a, b, y, s, "s") for a, b, y, s in V["lines"]]

def scene_end(t):
    u = t - B.END; ss = B.ss
    base = B.shot_frame(B.SHOTS[-1], t).convert("RGBA")
    im = Image.blend(base, B.endbg(), ss(u / 0.6))
    lg = B.LOGO.resize((210, int(B.LOGO.height * 210 / B.LOGO.width)), Image.LANCZOS)
    a = ss((u - 0.3) / 0.5); lg.putalpha(lg.getchannel("A").point(lambda v: int(v * a))); im.alpha_composite(lg, ((B.W - 210) // 2, 260))
    f = B.inter(70, "Black"); tw = ImageDraw.Draw(im).textlength(V["title"], font=f)
    if tw > 940: f = B.inter(int(70 * 940 / tw), "Black")
    B.ctext(im, 520, V["title"], f, B.GOLD, ss((u - 0.5) / 0.4), 8)
    B.ctext(im, 620, V["sub"], B.pop(40, "Medium"), B.IVORY, ss((u - 0.7) / 0.4), 6)
    a2 = ss((u - 0.9) / 0.5)
    if a2 > 0:
        th = B.src("03").resize((300, 533), Image.LANCZOS).convert("RGBA")
        m = Image.new("L", th.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, 299, 532), 26, fill=int(255 * a2)); th.putalpha(m)
        fr = Image.new("RGBA", (308, 541)); ImageDraw.Draw(fr).rounded_rectangle((0, 0, 307, 540), 30, fill=B.GOLD + (int(255 * a2),)); fr.alpha_composite(th, (4, 4))
        im.alpha_composite(fr, ((B.W - 308) // 2, 760))
    a3 = ss((u - 1.4) / 0.4)
    if a3 > 0:
        f = B.inter(44, "Black"); d = ImageDraw.Draw(im); tw = d.textlength(V["cta"], font=f)
        if tw > 860: f = B.inter(int(44 * 860 / tw), "Black"); tw = d.textlength(V["cta"], font=f)
        lay = Image.new("RGBA", im.size); dl = ImageDraw.Draw(lay); y = 1420
        dl.rounded_rectangle(((B.W - tw) / 2 - 50, y - 50, (B.W + tw) / 2 + 50, y + 50), 50, fill=B.GOLD + (255,))
        dl.text((B.W / 2, y), V["cta"], font=f, fill=(40, 8, 16, 255), anchor="mm"); lay.putalpha(lay.getchannel("A").point(lambda v: int(v * a3))); im.alpha_composite(lay)
    B.ctext(im, 1530, "O-17 LAJPAT NAGAR-II  ·  R CUBE MONAD MALL, NOIDA", B.pop(32, "Bold"), (226, 180, 110), ss((u - 1.6) / 0.4), 6)
    return im
B.scene_end = scene_end

def read(path):
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vn", "-ac", "2", "-ar", "44100", "-f", "f32le", "-"], capture_output=True, check=True)
    return np.frombuffer(r.stdout, np.float32).reshape(-1, 2)

if __name__ == "__main__":
    out = WORK + "wed_" + AUD + "/"; os.makedirs(out, exist_ok=True)
    n = int(B.DUR * B.FPS)
    for i in range(n): B.frame(i / B.FPS).save(out + f"{i:04d}.jpg", quality=92)
    vo, bed = read(D + "wedding_storeroom_reel.mp4"), read(D + "wedding_storeroom_reel_bed.mp4")
    sr = 44100; m = min(len(vo), len(bed), int(B.DUR * sr)); s = int(SPLIT * sr); xf = int(.25 * sr)
    # match the bed to the music level just before the VO ends (VO mix ducks the bed)
    g = np.sqrt(np.mean(vo[s - sr:s - int(.2 * sr)] ** 2)) / max(1e-6, np.sqrt(np.mean(bed[s - sr:s - int(.2 * sr)] ** 2)))
    g = float(np.clip(g, .4, 2.5))
    mix = np.zeros((m, 2), np.float32); r = np.linspace(0, 1, xf)[:, None]
    mix[:s] = vo[:s]; mix[s:s + xf] = vo[s:s + xf] * (1 - r) + bed[s:s + xf] * g * r; mix[s + xf:] = bed[s + xf:m] * g
    mix *= 10 ** (-1 / 20) / np.max(np.abs(mix))
    import scipy.io.wavfile as wf; wf.write(out + "a.wav", sr, (mix * 32767).astype(np.int16))
    name = D + f"storeroom_{AUD}.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(B.FPS), "-i", out + "%04d.jpg", "-i", out + "a.wav", "-c:v", "libx264", "-pix_fmt", "yuv420p",
                    "-crf", "18", "-preset", "medium", "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", "-shortest", name], check=True)
    print("done", name, "bed gain", round(g, 2))

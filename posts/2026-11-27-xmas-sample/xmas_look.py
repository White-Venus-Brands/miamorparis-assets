"""Christmas look on Tannay's talking frames: white shirt -> deep Christmas red (folds kept), Santa hat tracked to his head.
Person mask: U2Net human-seg (ONNX). Face: skin blob inside the person mask. Hat: drawn here, no stock art.
Usage: python3 xmas_look.py SRC_DIR DST_DIR MODEL.onnx [--test N,N]"""
import os, sys
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

SRC, DST, MODEL = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(DST, exist_ok=True)
import onnxruntime as ort
SESS = ort.InferenceSession(MODEL, providers=["CPUExecutionProvider"])

def person_mask(img):
    """U2Net misses body parts touching the frame edge, so run it on a padded copy and on the plain frame, take the max"""
    h0, w0 = img.shape[:2]; p = int(w0 * .25)
    padded = cv2.copyMakeBorder(img, p // 2, 0, p, p, cv2.BORDER_REPLICATE)
    mp_ = _mask(padded)[p // 2:, p:p + w0]
    return np.maximum(_mask(img), mp_)

def _mask(img):
    h, w = img.shape[:2]
    x = cv2.resize(img[:, :, ::-1], (320, 320)).astype(np.float32) / 255
    x = ((x - [0.485, 0.456, 0.406]) / [0.229, 0.224, 0.225]).transpose(2, 0, 1)[None].astype(np.float32)
    o = SESS.run(None, {SESS.get_inputs()[0].name: x})[0][0, 0]; o = (o - o.min()) / (o.max() - o.min() + 1e-9)
    return cv2.resize(o, (w, h))

def make_hat(wb):
    """Santa hat image, band width wb px. Returns RGBA and the band centre (x, y) inside it."""
    W_, H_ = int(wb * 1.9), int(wb * 1.35)
    im = Image.new("RGBA", (W_, H_)); d = ImageDraw.Draw(im)
    bx0, bx1, by = int(W_ * .12), int(W_ * .12) + wb, int(H_ * .78)
    tip = (int(W_ * .86), int(H_ * .30))
    # cone (red, flopping to the right)
    cone = [(bx0 + wb * .02, by), (bx0 + wb * .18, by - wb * .55), (bx0 + wb * .45, by - wb * .78), (tip[0] - wb * .1, tip[1] - wb * .05),
            tip, (tip[0] - wb * .02, tip[1] + wb * .12), (bx0 + wb * .78, by - wb * .45), (bx1 - wb * .02, by)]
    d.polygon(cone, fill=(178, 18, 30, 255))
    sh = Image.new("L", (W_, H_)); ImageDraw.Draw(sh).polygon([(bx0 + wb * .5, by), (bx0 + wb * .62, by - wb * .6), (tip[0] - wb * .05, tip[1] + wb * .1), (bx1, by)], fill=120)
    dark = Image.new("RGBA", (W_, H_), (90, 6, 14, 255)); im = Image.composite(dark, im, Image.fromarray(np.minimum(np.asarray(sh.filter(ImageFilter.GaussianBlur(wb * .12))), np.asarray(im.getchannel("A")))))
    hl = Image.new("L", (W_, H_)); ImageDraw.Draw(hl).polygon([(bx0 + wb * .12, by - wb * .1), (bx0 + wb * .25, by - wb * .55), (bx0 + wb * .4, by - wb * .62), (bx0 + wb * .3, by - wb * .1)], fill=70)
    lite = Image.new("RGBA", (W_, H_), (230, 70, 70, 255)); im = Image.composite(lite, im, Image.fromarray(np.minimum(np.asarray(hl.filter(ImageFilter.GaussianBlur(wb * .1))), np.asarray(im.getchannel("A")))))
    # fur band + pompom with noise
    fur = Image.new("RGBA", (W_, H_)); fd = ImageDraw.Draw(fur)
    fd.rounded_rectangle((bx0 - wb * .06, by - wb * .13, bx1 + wb * .06, by + wb * .13), radius=int(wb * .13), fill=(246, 243, 238, 255))
    r = wb * .13; fd.ellipse((tip[0] - r, tip[1] - r, tip[0] + r, tip[1] + r), fill=(246, 243, 238, 255))
    n = (np.random.default_rng(1).random((H_, W_)) * 40).astype(np.uint8)
    fa = np.asarray(fur).copy(); fa[..., :3] = np.clip(fa[..., :3].astype(int) - n[..., None], 0, 255)
    fur = Image.fromarray(fa); a = fur.getchannel("A").filter(ImageFilter.GaussianBlur(1.5)); fur.putalpha(a)
    shade = Image.new("L", (W_, H_)); ImageDraw.Draw(shade).rectangle((0, by + wb * .02, W_, H_), fill=60)
    fur = Image.composite(Image.new("RGBA", (W_, H_), (205, 200, 195, 255)), fur, Image.fromarray(np.minimum(np.asarray(shade.filter(ImageFilter.GaussianBlur(wb * .05))), np.asarray(fur.getchannel("A")))))
    im.alpha_composite(fur)
    return im, ((bx0 + bx1) / 2, by)

def analyse(img, m):
    """returns face box (x0,y0,x1,y1), head top y, shirt mask"""
    h, w = img.shape[:2]; pm = cv2.dilate((m > .3).astype(np.uint8), np.ones((9, 9), np.uint8)) > 0
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    Hh, Ss, Vv = hsv[..., 0], hsv[..., 1].astype(int), hsv[..., 2].astype(int)
    skin = pm & (((Hh <= 22) | (Hh >= 170)) & (Ss > 45) & (Ss < 200) & (Vv > 70))
    n, lab, st, cen = cv2.connectedComponentsWithStats(skin.astype(np.uint8) * 255, 8)
    face = None
    if n > 1:
        cand = [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] > w * h * .01]
        if cand:
            i = min(cand, key=lambda i: st[i, cv2.CC_STAT_TOP] + (0 if st[i, cv2.CC_STAT_AREA] > w * h * .04 else h))   # top-most big skin blob
            x, y, ww, hh = st[i, :4]
            ys, xs = np.nonzero(lab == i); mu = cv2.moments((lab == i).astype(np.uint8))
            th = .5 * np.degrees(np.arctan2(2 * mu["mu11"], mu["mu20"] - mu["mu02"]))   # major-axis angle, image coords
            tilt = th - 90 if th > 0 else th + 90                                        # 0 = upright head
            ufw = np.percentile(np.abs((xs - xs.mean()) * np.cos(np.radians(tilt)) - (ys - ys.mean()) * np.sin(np.radians(tilt))), 95) * 2 if False else ww
            face = (x, y, x + ww, y + hh, xs.mean(), ys.mean(), float(np.clip(tilt, -40, 40)))
    cols = np.where(pm.any(0))[0]
    top = None
    if face is not None:
        cx0, cx1 = face[0] + (face[2] - face[0]) // 4, face[2] - (face[2] - face[0]) // 4
        rows = np.where(pm[:, cx0:cx1].any(1))[0]; top = rows.min() if len(rows) else 0
    white = pm & (Ss < 75) & (Vv > 95)
    if face is not None:
        x0, y0, x1, y1, mx, my, tilt = face; fw = x1 - x0
        white[: max(0, y0), :] = False
        # protect the face: ellipse over the skin blob down to the chin (face height ~1.3x its width), tilted with the head
        fh = min(y1 - y0, 1.3 * fw); ell = np.zeros((h, w), np.uint8)
        cv2.ellipse(ell, (int(mx), int(y0 + fh * .5)), (int(fw * .56), int(fh * .56)), float(tilt), 0, 360, 255, -1)
        white &= ell == 0
    white = cv2.morphologyEx(white.astype(np.uint8) * 255, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    n2, lab2, st2, _ = cv2.connectedComponentsWithStats(white, 8)
    keep = np.zeros_like(white)
    for i in range(1, n2):
        if st2[i, cv2.CC_STAT_AREA] > w * h * .004 and st2[i, cv2.CC_STAT_TOP] + st2[i, cv2.CC_STAT_HEIGHT] > h * .7: keep[lab2 == i] = 255   # shirt reaches the bottom; eyes/teeth don't
    shirt = cv2.GaussianBlur(keep, (0, 0), 3).astype(np.float32) / 255 * np.clip(m * 1.6, 0, 1)
    return face, top, shirt

RED = np.array([38, 30, 158], np.float32)            # BGR deep Christmas red
def recolor(img, shirt):
    L = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255
    tone = RED[None, None, :] * (.22 + 1.05 * L[..., None] ** 1.35)
    sh = shirt[..., None] * .95
    out = img.astype(np.float32) * (1 - sh) + tone * sh
    return np.clip(out, 0, 255).astype(np.uint8)

def place_hat(img, cx, band_y, wb, ang):
    hat, (hx, hy) = make_hat(int(wb))
    hat = hat.rotate(ang, resample=Image.BICUBIC, expand=False, center=(hx, hy))
    base = Image.fromarray(img[:, :, ::-1]).convert("RGBA")
    shadow = Image.new("RGBA", hat.size, (0, 0, 0, 0)); shadow.putalpha(hat.getchannel("A").point(lambda v: int(v * .35)))
    ox, oy = int(cx - hx), int(band_y - hy)
    tmp = Image.new("RGBA", base.size); tmp.paste(shadow.filter(ImageFilter.GaussianBlur(10)), (ox + 6, oy + 12)); base.alpha_composite(tmp)
    tmp = Image.new("RGBA", base.size); tmp.paste(hat, (ox, oy)); base.alpha_composite(tmp)
    return np.asarray(base.convert("RGB"))[:, :, ::-1]

def run(files):
    track = []
    for f in files:
        img = cv2.imread(os.path.join(SRC, f)); m = person_mask(img); face, top, shirt = analyse(img, m)
        track.append((f, img, face, top, shirt))
    # smooth hat geometry over time
    g = []
    for f, img, face, top, shirt in track:
        if face is None or top is None: g.append(None); continue
        x0, y0, x1, y1, mx, my, tilt = face; fw = min(x1 - x0, (y1 - y0) * .85)
        a = np.radians(tilt); up = np.array([np.sin(a), -np.cos(a)])        # head's up direction
        top_pt = np.array([mx, my]) + up * (my - y0 + .14 * fw)   # band on the hairline, clear of the glasses
        g.append([top_pt[0], top_pt[1], fw * 1.15, tilt])
    vals = [v for v in g if v]
    if vals:
        arr = np.array([v if v else [np.nan] * 4 for v in g], np.float64)
        for c in range(4):
            col = arr[:, c]; idx = np.arange(len(col)); ok = ~np.isnan(col)
            col = np.interp(idx, idx[ok], col[ok]); k = 5; col = np.convolve(np.pad(col, k, mode="edge"), np.ones(2 * k + 1) / (2 * k + 1), "same")[k:-k]
            arr[:, c] = col
        wb_med = np.median(arr[:, 2]); arr[:, 2] = .5 * arr[:, 2] + .5 * wb_med
    for i, (f, img, face, top, shirt) in enumerate(track):
        out = recolor(img, shirt)
        if vals and os.environ.get("HAT") == "1": out = place_hat(out, arr[i, 0], arr[i, 1], arr[i, 2], -arr[i, 3] - 4)   # off by default: a flat 2D hat reads as a sticker
        cv2.imwrite(os.path.join(DST, f), out, [cv2.IMWRITE_JPEG_QUALITY, 94])

if __name__ == "__main__":
    files = sorted(os.listdir(SRC))
    if len(sys.argv) > 5 and sys.argv[4] == "--test": files = [files[int(i)] for i in sys.argv[5].split(",")]
    if len(sys.argv) > 5 and sys.argv[4] == "--range": a_, b_ = map(int, sys.argv[5].split(",")); files = files[max(0, a_):b_]
    run(files)
    print("ok", len(files))

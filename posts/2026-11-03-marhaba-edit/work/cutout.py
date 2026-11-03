"""Cut real products out of white studio shots (no AI): flood from white edges, drop grey floor shadow, smooth edge."""
import sys, numpy as np, cv2
from PIL import Image
from scipy import ndimage
def cut(src, dst, crop=None, thr=6, shadow_from=0.86):
    im = Image.open(src).convert("RGB")
    if crop: W, H = im.size; im = im.crop(tuple(int(v * s) for v, s in zip(crop, (W, H, W, H))))
    im.thumbnail((1800, 1800), Image.LANCZOS); a = np.array(im).astype(int)
    d = (255 - a).max(2); sat = a.max(2) - a.min(2); fg = d > thr
    lab, n = ndimage.label(fg); s = ndimage.sum(fg, lab, range(1, n + 1)); fg = lab == (np.argmax(s) + 1)
    ys, xs = np.where(fg); top, bot = ys.min(), ys.max(); h = bot - top
    r0, r1 = top + int(h * (shadow_from - 0.06)), top + int(h * shadow_from); cols = np.where(fg[r0:r1].any(0))[0]
    b0 = top + int(h * shadow_from); fg[b0:, :cols.min()] = False; fg[b0:, cols.max() + 1:] = False
    g = (sat < 10) & (d < 110); fg[b0:] &= ~g[b0:]
    for y in range(b0, bot + 1):
        xs_ = np.where(fg[y])[0]
        if len(xs_) > 20: fg[y, xs_.min():xs_.max() + 1] = True
        else: fg[y] = False
    fg = ndimage.binary_closing(fg, iterations=3); fg = ndimage.binary_fill_holes(fg)
    fg = cv2.GaussianBlur(fg.astype(np.float32), (0, 0), 2.0) > 0.5
    al = cv2.GaussianBlur(fg.astype(np.float32), (0, 0), 1.0)
    ys, xs = np.where(al > 0.02); out = np.dstack([a.astype(np.uint8), (al * 255).astype(np.uint8)])[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    Image.fromarray(out, "RGBA").save(dst); print(dst, out.shape)
cut("cream_front.jpg", "work/cream.png")
cut("perfume_main.jpg", "work/perfume.png", crop=(0, 0, 0.46, 1), thr=10)
cut("perfume_main.jpg", "work/box.png", crop=(0.46, 0, 1, 1), thr=10)
cut("mini_studio_11.jpg", "work/mini.png", crop=(0, 0, 0.5, 1), thr=10)

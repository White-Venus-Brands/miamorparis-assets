"""Take the 8 ml bottle (and its tight halo) off the brass podium in the real Marhaba set (mini_life_1.jpg).
A soft backlight is added again per slide behind whatever product stands there."""
import numpy as np, cv2
from PIL import Image
src = np.array(Image.open("mini_life_1.jpg").convert("RGB")).astype(np.float32)
a = src.copy(); out = a.copy()
def hfill(img, x0, x1, y0, y1, sy):
    L = img[y0:y1, x0 - 6:x0].mean(1); R = img[y0:y1, x1:x1 + 6].mean(1); t = np.linspace(0, 1, x1 - x0)[None, :, None]
    return cv2.GaussianBlur(L[:, None, :] * (1 - t) + R[:, None, :] * t, (0, 0), sigmaX=2, sigmaY=sy)
# wide soft fill of the halo above the podium
X0, X1, Y0, Y1 = 430, 820, 40, 872
full = a.copy(); full[Y0:Y1, X0:X1] = hfill(a, X0, X1, Y0, Y1, 12)
m = np.zeros(a.shape[:2], np.float32); m[Y0 + 30:Y1, X0 + 30:X1 - 30] = 1; m = cv2.GaussianBlur(m, (0, 0), 28)[..., None]
m[Y1 - 40:Y1 + 40] = np.maximum(m[Y1 - 40:Y1 + 40], 0)  # keep
out = a * (1 - m) + full * m
# podium top behind the bottle base
x0, x1, y0, y1 = 526, 722, 860, 912
full2 = out.copy(); full2[y0:y1, x0:x1] = hfill(out, x0, x1, y0, y1, 2)
m2 = np.zeros(a.shape[:2], np.float32); m2[y0:y1, x0:x1] = 1; m2 = cv2.GaussianBlur(m2, (0, 0), 4)[..., None]
out = out * (1 - m2) + full2 * m2
# narrow strip between halo fill and podium (bottle body rows 80..860 inside x0..x1 must be fully gone)
full3 = out.copy(); full3[80:860, x0:x1] = hfill(out, x0, x1, 80, 860, 10)
m3 = np.zeros(a.shape[:2], np.float32); m3[80:860, x0:x1] = 1; m3 = cv2.GaussianBlur(m3, (0, 0), 10)[..., None]
out = out * (1 - m3) + full3 * m3
out += np.random.default_rng(2).normal(0, 1.5, a.shape)
Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save("work/scene_clean.png")

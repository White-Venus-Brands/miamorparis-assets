"""Remove the 8 ml bottle from Tannay's Flora 5 set photo so other real products can stand on the podium."""
import numpy as np, cv2
from PIL import Image
src = np.array(Image.open("source/mini_8ml_lifestyle.png").convert("RGB")).astype(np.float32)
a = src.copy(); x0, x1, y0, y1 = 506, 740, 90, 1104
# backdrop + silk: horizontal interpolation between the columns either side of the bottle
L = a[y0:y1, x0 - 8:x0].mean(1); R = a[y0:y1, x1:x1 + 8].mean(1); t = np.linspace(0, 1, x1 - x0)[None, :, None]
fill = cv2.GaussianBlur(L[:, None, :] * (1 - t) + R[:, None, :] * t, (0, 0), sigmaX=1, sigmaY=5)
full = a.copy(); full[y0:y1, x0:x1] = fill
# podium top: real marble from just left of the bottle, mirrored to tile across the gap
py0 = 1044; blk = src[py0:y1, 380:506]; tile = np.concatenate([blk[:, ::-1], blk, blk[:, ::-1]], 1)
off = (tile.shape[1] - (x1 - x0)) // 2; full[py0:y1, x0:x1] = tile[:, off:off + (x1 - x0)]
vm = np.zeros((y1 - y0, 1, 1), np.float32); vm[py0 - y0:] = 1; vm = cv2.GaussianBlur(vm[..., 0], (0, 0), sigmaX=1, sigmaY=6)[:, :, None]
full[y0:y1, x0:x1] = fill * (1 - vm) + full[y0:y1, x0:x1] * vm
m = np.zeros(a.shape[:2], np.float32); m[y0:y1, x0:x1] = 1; m = cv2.GaussianBlur(m, (0, 0), 7)[..., None]
noise = np.random.default_rng(1).normal(0, 1.8, a.shape)
out = np.clip(a * (1 - m) + (full + noise) * m, 0, 255).astype(np.uint8)
Image.fromarray(out).save("work/scene_clean.png")

"""Cut the 12 moisturiser tubes out of Tannay's white-background studio shots (WhatsApp zip, 27 Nov).
Background = near-white, low-saturation pixels connected to the border; floor shadow under the cap removed by cutting
below the cap's lowest dark row. Usage: python3 make_tubes.py SRC_DIR"""
import os, sys, glob
import numpy as np, cv2
from PIL import Image
SRC = sys.argv[1]; D = os.path.dirname(os.path.abspath(__file__)) + "/"
NAMES = ["bouquet", "flora5", "holdmi", "loveair", "marhaba", "missaqua", "misspoem", "moksha", "mraqua", "ombre", "derossa", "smuggler"]
fs = sorted(glob.glob(SRC + "/*.jpeg"), key=lambda f: int(f.split("(")[1].split(")")[0]) if "(" in f else 0)
for f, n in zip(fs, NAMES):
    img = cv2.imread(f); h, w = img.shape[:2]
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV); v = hsv[..., 2].astype(int); s = hsv[..., 1].astype(int)
    obj = ~((v > 225) & (s < 18)); ys, xs = np.where(obj); pad = 20
    x0, x1 = max(0, np.percentile(xs, .5) - pad), min(w, np.percentile(xs, 99.5) + pad); y0, y1 = max(0, ys.min() - pad), min(h, ys.max() + pad)
    sc = .5; sm = cv2.resize(img, None, fx=sc, fy=sc, interpolation=cv2.INTER_AREA)
    mask = np.zeros(sm.shape[:2], np.uint8); bgd = np.zeros((1, 65), np.float64); fgd = np.zeros((1, 65), np.float64)
    rect = (int(x0 * sc), int(y0 * sc), int((x1 - x0) * sc), int((y1 - y0) * sc))
    cv2.grabCut(sm, mask, rect, bgd, fgd, 6, cv2.GC_INIT_WITH_RECT)
    fg = np.where((mask == 1) | (mask == 3), 1, 0).astype(np.uint8); fg = cv2.resize(fg, (w, h), interpolation=cv2.INTER_NEAREST)
    n2, lab2, st, _ = cv2.connectedComponentsWithStats(fg, 8); k = 1 + np.argmax(st[1:, cv2.CC_STAT_AREA]); fg = (lab2 == k).astype(np.uint8)
    cs, _ = cv2.findContours(fg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE); fg = np.zeros_like(fg); cv2.drawContours(fg, cs, -1, 1, -1)   # fill holes
    fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    dark = ((v < 70) & (fg > 0)).sum(1); rows = np.where(dark > .6 * dark[int(h * .5):].max())[0]; fg[rows.max() + 1:] = 0          # floor shadow below the cap
    thr = .6 * dark[int(h * .5):].max(); ct = rows.max()
    while ct > 0 and dark[ct - 1] > thr: ct -= 1
    ct = max(ct, rows.max() - int(h * .12))                                                                                    # cap: keep only its dark pixels (floor shows beside it)
    for y in range(ct, rows.max() + 1):
        xs_ = np.where((v[y] < 140) & (fg[y] > 0))[0]
        fg[y] = 0
        if len(xs_): fg[y, xs_.min():xs_.max() + 1] = 1
    # trim soft grey halo: fg pixels that are light & unsaturated along the outer edge
    a = cv2.GaussianBlur(fg.astype(np.float32) * 255, (0, 0), 1.2)
    ys, xs = np.where(fg > 0); y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    rgba = np.dstack([img[..., ::-1], a.astype(np.uint8)])[y0:y1, x0:x1]
    Image.fromarray(rgba).save(D + f"{n}.png"); print(n, rgba.shape)

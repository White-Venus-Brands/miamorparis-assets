"""Subtle teeth whitening for Tannay's talking clips. Finds the mouth from the lip colour (red, saturated: reliable even on
the tilted clip), then inside that box lifts only the bright, low-saturation, yellow-ish pixels (teeth): saturation down,
brightness up a touch, feathered. Skin, lips and background are untouched."""
import cv2
import numpy as np

class Whitener:
    def __init__(self): self.box = None; self.miss = 0

    def mouth_box(self, bgr):
        h, w = bgr.shape[:2]; sc = 360 / w
        small = cv2.resize(bgr, (360, int(h * sc)))
        hsv = cv2.cvtColor(small, cv2.COLOR_BGR2HSV); H, S, V = cv2.split(hsv)
        lips = (((H <= 6) | (H >= 172)) & (S >= 70) & (V >= 60)).astype(np.uint8)
        lips = cv2.morphologyEx(lips, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
        n, lab, st, cen = cv2.connectedComponentsWithStats(lips)
        best = None
        for i in range(1, n):
            x, y, bw, bh, a = st[i]
            if a < 25 or bw < 12: continue
            if best is None or a > st[best][4]: best = i
        if best is None: return None
        x, y, bw, bh, a = st[best]
        # mouth = lips box grown (teeth sit between / just inside the lips)
        cx, cy = x + bw / 2, y + bh / 2; mw, mh = bw * 0.95, max(bh * 1.25, bw * .3)
        return np.array([(cx - mw / 2) / sc, (cy - mh / 2) / sc, (cx + mw / 2) / sc, (cy + mh / 2) / sc])

    def __call__(self, bgr):
        b = self.mouth_box(bgr)
        if b is None:
            self.miss += 1
            if self.box is None or self.miss > 6: return bgr
        else:
            self.miss = 0; self.box = b if self.box is None else self.box * .6 + b * .4
        h, w = bgr.shape[:2]
        x0, y0, x1, y1 = [int(v) for v in self.box]; x0, y0 = max(0, x0), max(0, y0); x1, y1 = min(w, x1), min(h, y1)
        if x1 - x0 < 10 or y1 - y0 < 10: return bgr
        roi = bgr[y0:y1, x0:x1].astype(np.float32)
        hsv = cv2.cvtColor(roi.astype(np.uint8), cv2.COLOR_BGR2HSV).astype(np.float32); H, S, V = cv2.split(hsv)
        medV, medS = np.median(V), np.median(S)
        m = ((V > max(medV * 0.95, 95)) & (S < medS * .62) & (H >= 8) & (H <= 40)).astype(np.float32)
        # keep to the inner part of the box (ellipse) so nothing at the edges (stubble, chin) is touched
        yy, xx = np.mgrid[0:y1 - y0, 0:x1 - x0]; ex = ((xx - (x1 - x0) / 2) / ((x1 - x0) / 2)) ** 2 + ((yy - (y1 - y0) / 2) / ((y1 - y0) / 2)) ** 2
        m *= (ex < 1).astype(np.float32)
        m = cv2.GaussianBlur(m, (0, 0), 2.5)
        S2 = S * (1 - .65 * m); V2 = np.clip(V * (1 + .1 * m), 0, 255)
        out = cv2.cvtColor(cv2.merge([H, S2, V2]).astype(np.uint8), cv2.COLOR_HSV2BGR)
        res = bgr.copy(); res[y0:y1, x0:x1] = out; return res

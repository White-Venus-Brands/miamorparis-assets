"""Mist enhancer: amplify only the faint spray over the dark backdrop, keeping its real texture.
background = per-pixel median of the segment; boost = k * (frame - background) where the backdrop is dark."""
import numpy as np
from PIL import Image, ImageFilter

def background(frames, size=(540, 960)):
    stack = np.stack([np.asarray(f.convert("L").resize(size), np.float32) for f in frames[::max(1, len(frames) // 25)]])
    return np.median(stack, axis=0)

def enhance(img, bg, k=3.2, floor=3.0, cap=70):
    size = (bg.shape[1], bg.shape[0])
    L = np.asarray(img.convert("L").resize(size), np.float32)
    L = np.asarray(Image.fromarray(L.astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2)), np.float32)
    d = np.clip(L - bg - floor, 0, None) * (bg < 55) * (L < 150)
    boost = np.clip(d * k, 0, cap)
    b = Image.fromarray(boost.astype(np.uint8)).resize(img.size, Image.BICUBIC).filter(ImageFilter.GaussianBlur(2))
    a = np.asarray(b, np.float32)[..., None]
    tint = np.array([1.0, .97, .93])
    out = np.asarray(img.convert("RGB"), np.float32) + a * tint
    return Image.fromarray(out.clip(0, 255).astype(np.uint8))

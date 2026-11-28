"""Version 2 of the switch reel (28 Nov): Tannay's own Jingle Bells recording for clip 1.
Uses only the SUNG 'Jingle bells, jingle bells, jingle all the way' (first chorus, source 33.83-38.55 s; the song's
0-5 s opening is the instrumental intro), synced to his lip-sync (bells at 1.1 / 2.2 s, 'all' at 3.25 s in IMG_5374).
Karaoke words on screen, word by word.
Under the side-eye: the next line's melody as a muffled instrumental (no lyrics), then scratch -> Punjabi drop.
Frames are the same as build_switch.py (reuses WORK/fr_switch). Usage: python3 build_switch_orig.py WORKDIR SOURCE.m4a"""
import os, subprocess, sys, wave
import numpy as np
SRC = sys.argv[2]; sys.argv = sys.argv[:2]
D = os.path.dirname(os.path.abspath(__file__)) + "/"; sys.path.insert(0, D)
import build_switch as S
SR, J = S.SR, S.J
# sung first chorus in the source: jin 32.76, bells 33.34, jin 33.92, bells 34.50, jin 35.08, all 35.66, the 36.10, way 36.24 (held to ~37.3)
# warped piece by piece (pitch kept) onto his mouth in IMG_5374: song time -> video time
ANCH = [(32.64, .38), (32.76, .50), (33.34, 1.14), (33.92, 1.60), (34.50, 2.22), (35.08, 2.66), (35.66, 3.24), (36.24, 3.62), (37.30, 4.68)]
WORDS = [("Jingle", .50), ("bells,", 1.14), ("jingle", 1.60), ("bells,", 2.22), ("jingle", 2.66), ("all", 3.24), ("the", 3.53), ("way", 3.62)]
NEXT = 4.72                     # muffled 'oh what fun' melody starts after the held 'way'
Q, KEY = .29, 2 ** (7 / 12)     # song tempo; synth melody moved from C to the recording's G

def load(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "2", "-ar", str(SR), "-f", "s16le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).reshape(-1, 2).astype(np.float32) / 32768

def warp():
    """each anchor-to-anchor piece time-stretched with atempo (pitch kept), joined with 12 ms crossfades"""
    out = []; X = int(.012 * SR)
    for (s0, v0), (s1, v1) in zip(ANCH, ANCH[1:]):
        r = (s1 - s0) / (v1 - v0); pad = .03
        raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{s0 - pad:.3f}", "-to", f"{s1 + pad:.3f}", "-i", SRC, "-af", f"atempo={r:.4f}",
                              "-ac", "2", "-ar", str(SR), "-f", "s16le", "-"], capture_output=True, check=True).stdout
        y = np.frombuffer(raw, np.int16).reshape(-1, 2).astype(np.float32) / 32768
        p = int(round(pad / r * SR)); L = int(round((v1 - v0) * SR)); y = y[p:p + L + X]
        if len(y) < L + X: y = np.pad(y, ((0, L + X - len(y)), (0, 0)))
        out.append(y)
    res = out[0]
    for y in out[1:]:
        w = np.linspace(0, 1, X)[:, None]; res[-X:] = res[-X:] * (1 - w) + y[:X] * w; res = np.concatenate([res, y[X:]])
    return res

def next_line(n, t0):
    """'Oh what fun it is to ride...' melody only (public-domain tune), glockenspiel + bass, starting at t0"""
    out = np.zeros(n, np.float32); t = t0
    mel = S.MEL[11:]
    for nt, d in mel:
        f = S.NOTE[nt] * KEY; L = int((d * Q + .6) * SR); x = np.arange(L) / SR; i = int(t * SR); m = min(L, n - i)
        if m > 0: out[i:i + m] += ((np.sin(2 * np.pi * f * x) + .3 * np.sin(2 * np.pi * 2 * f * x) * np.exp(-x * 6)) * np.exp(-x * 3) * .3)[:m]
        t += d * Q
    for k in range(8):
        f = (S.NOTE["F"] if k < 4 else S.NOTE["C"]) * KEY / 4; L = int(.4 * SR); x = np.arange(L) / SR; i = int((t0 + k * 2 * Q) * SR); m = min(L, n - i)
        if m > 0: out[i:i + m] += (np.sin(2 * np.pi * f * x) * np.exp(-x * 6) * .35)[:m]
    y = np.zeros_like(out); a = np.exp(-2 * np.pi * 700 / SR); acc = 0.        # muffled, like it's playing in the next room
    for i in range(n): acc = (1 - a) * out[i] + a * acc; y[i] = acc
    return y

def build(path):
    n = int(round(S.TOTAL * SR))
    seg = warp(); fo = int(.08 * SR); seg[-fo:] *= np.linspace(1, 0, fo)[:, None]; fi = int(.03 * SR); seg[:fi] *= np.linspace(0, 1, fi)[:, None]
    a = np.zeros((n, 2), np.float32); i0 = int(round(ANCH[0][1] * SR)); a[i0:i0 + len(seg)] = seg
    song = np.zeros((n, 2), np.float32); s0 = int((S.SONG_DROP - .06) * SR); d0 = int((S.DROP - .06) * SR); m = min(len(J.SNG) - s0, n - d0)
    song[d0:d0 + m] = J.SNG[s0:s0 + m]
    r_song = np.sqrt(np.mean(song[d0:] ** 2)); a *= r_song / np.sqrt(np.mean(seg ** 2)) * 10 ** (-2 / 20)
    nl = next_line(n, NEXT); end = int((S.SCRATCH + .1) * SR); nl[end:] = 0; nl[end - int(.15 * SR):end] *= np.linspace(1, 0, int(.15 * SR))
    nl *= r_song / (np.sqrt(np.mean(nl[int((NEXT + .05) * SR):end - int(.15 * SR)] ** 2)) + 1e-9) * 10 ** (-13 / 20)
    sc = S.scratch(); k = int(S.SCRATCH * SR)
    mix = a + song + np.stack([nl, nl], 1); mix[k:k + len(sc)] += np.stack([sc, sc], 1) * r_song / .05 * .18
    fo = int(.6 * SR); mix[-fo:] *= np.linspace(1, 0, fo)[:, None]; mix *= 10 ** (-1 / 20) / np.max(np.abs(mix))
    with wave.open(path, "wb") as w_:
        w_.setnchannels(2); w_.setsampwidth(2); w_.setframerate(SR); w_.writeframes((mix * 32767).astype(np.int16).tobytes())

from PIL import Image, ImageDraw
def karaoke(im, t):
    """two lines, lower third; sung words gold, upcoming words dim ivory"""
    if t < .3 or t > S.L1 - .05: return im
    d = ImageDraw.Draw(im); f = J.MS(74); rows = [WORDS[:4], WORDS[4:]]; y = 1440
    for row in rows:
        ws = [f.getlength(w + " ") for w, _ in row]; x = (J.W - sum(ws) + f.getlength(" ")) / 2
        for (w, t0), wl in zip(row, ws):
            on = t >= t0; col = J.GOLD if on else (250, 245, 236)
            d.text((x, y), w, font=f, fill=col + (255 if on else 150,), stroke_width=6, stroke_fill=(0, 0, 0, 200)); x += wl
        y += 100
    return im

if __name__ == "__main__":
    fd = S.WORK + "fr_switch/"
    for i in range(int(S.L1 * S.FPS) + 1):
        t = i / S.FPS; im = S.frame(t).convert("RGBA"); karaoke(im, t); im.convert("RGB").save(fd + f"{i:04d}.jpg", quality=93)
    build(fd + "a2.wav")
    enc = ["-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p", "-r", str(S.FPS), "-movflags", "+faststart"]
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(S.FPS), "-i", fd + "%04d.jpg", "-i", fd + "a2.wav", "-map", "0:v", "-map", "1:a"] + enc
                   + ["-c:a", "aac", "-b:a", "256k", "-shortest", D + "jingle_switch_v2.mp4"], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", D + "jingle_switch_v2.mp4", "-an", "-c:v", "copy", D + "jingle_switch_v2_silent.mp4"], check=True)
    print("done", S.TOTAL)

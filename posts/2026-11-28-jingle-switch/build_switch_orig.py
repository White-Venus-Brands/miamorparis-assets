"""Version 2 of the switch reel (28 Nov): Tannay's own Jingle Bells recording for clip 1.
Uses only 'Jingle bells, jingle bells, jingle all the way' (source 0.00-5.00 s), synced to his lip-sync
(bells at 1.1 / 2.2 s, 'all' at 3.25 s in IMG_5374 -> source offset +0.05 s).
Under the side-eye: the next line's melody as a muffled instrumental (no lyrics), then scratch -> Punjabi drop.
Frames are the same as build_switch.py (reuses WORK/fr_switch). Usage: python3 build_switch_orig.py WORKDIR SOURCE.m4a"""
import os, subprocess, sys, wave
import numpy as np
SRC = sys.argv[2]; sys.argv = sys.argv[:2]
D = os.path.dirname(os.path.abspath(__file__)) + "/"; sys.path.insert(0, D)
import build_switch as S
SR, J = S.SR, S.J
OFF, CUT = .05, 5.00            # source 0 lands at video 0.05; cut before 'Oh what fun' (5.06)
Q, KEY = .29, 2 ** (7 / 12)     # song tempo; synth melody moved from C to the recording's G

def load(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "2", "-ar", str(SR), "-f", "s16le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).reshape(-1, 2).astype(np.float32) / 32768

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
    src = load(SRC); seg = src[:int(CUT * SR)].copy(); fo = int(.06 * SR); seg[-fo:] *= np.linspace(1, 0, fo)[:, None]
    a = np.zeros((n, 2), np.float32); i0 = int(OFF * SR); a[i0:i0 + len(seg)] = seg
    song = np.zeros((n, 2), np.float32); s0 = int((S.SONG_DROP - .06) * SR); d0 = int((S.DROP - .06) * SR); m = min(len(J.SNG) - s0, n - d0)
    song[d0:d0 + m] = J.SNG[s0:s0 + m]
    r_song = np.sqrt(np.mean(song[d0:] ** 2)); a *= r_song / np.sqrt(np.mean(seg ** 2)) * 10 ** (-2 / 20)
    nl = next_line(n, OFF + 5.06); end = int((S.SCRATCH + .1) * SR); nl[end:] = 0; nl[end - int(.15 * SR):end] *= np.linspace(1, 0, int(.15 * SR))
    nl *= r_song / (np.sqrt(np.mean(nl[int((OFF + 5.1) * SR):end - int(.15 * SR)] ** 2)) + 1e-9) * 10 ** (-13 / 20)
    sc = S.scratch(); k = int(S.SCRATCH * SR)
    mix = a + song + np.stack([nl, nl], 1); mix[k:k + len(sc)] += np.stack([sc, sc], 1) * r_song / .05 * .18
    fo = int(.6 * SR); mix[-fo:] *= np.linspace(1, 0, fo)[:, None]; mix *= 10 ** (-1 / 20) / np.max(np.abs(mix))
    with wave.open(path, "wb") as w_:
        w_.setnchannels(2); w_.setsampwidth(2); w_.setframerate(SR); w_.writeframes((mix * 32767).astype(np.int16).tobytes())

if __name__ == "__main__":
    fd = S.WORK + "fr_switch/"; build(fd + "a2.wav")
    enc = ["-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p", "-r", str(S.FPS), "-movflags", "+faststart"]
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(S.FPS), "-i", fd + "%04d.jpg", "-i", fd + "a2.wav", "-map", "0:v", "-map", "1:a"] + enc
                   + ["-c:a", "aac", "-b:a", "256k", "-shortest", D + "jingle_switch_v2.mp4"], check=True)
    print("done", S.TOTAL)

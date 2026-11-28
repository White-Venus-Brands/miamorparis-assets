"""0.1 s boomerang (28 Nov): Tannay's bhangra hand-raise (IMG_5375, 2.80-2.92 s) ping-ponged 70-71-72-73-72-71 at 60 fps,
warm grade, snow, gold 'PUNJABI CHRISTMAS'; the Punjabi Jingle Bell drop hit as a 0.1 s audio stutter so the loop repeats.
Also a 1 s version (same loop x10) in case Instagram rejects the 0.1 s upload. Usage: python3 build_boom.py WORKDIR"""
import os, subprocess, sys, wave
import numpy as np
from PIL import Image
WORK = sys.argv[1].rstrip("/") + "/"; D = os.path.dirname(os.path.abspath(__file__)) + "/"; R = os.path.normpath(D + "../..") + "/"
sys.path.insert(0, R + "posts/2026-11-28-moisturiser-xmas"); _a = sys.argv
import build_his_hers as HH
sys.argv = _a; J = HH.J; W, H, SR = J.W, J.H, J.SR
SEQ = [70, 71, 72, 73, 72, 71]; FPS = 60
fd = WORK + "fr_boom/"; os.makedirs(fd, exist_ok=True)
for i, n in enumerate(SEQ):
    im = HH.clip(HH.F2, n / 25 + .001); im.alpha_composite(J.snow(n / 25))
    J.popt(im, 300, "PUNJABI CHRISTMAS", 1, J.MS(96), J.GOLD); im.convert("RGB").save(fd + f"{i:04d}.jpg", quality=95)
s0 = int((J.DR[0] - .005) * SR); a = J.SNG[s0:s0 + int(.1 * SR)].copy(); f = int(.004 * SR)
a[:f] *= np.linspace(0, 1, f)[:, None]; a[-f:] *= np.linspace(1, 0, f)[:, None]; a *= 10 ** (-1 / 20) / np.max(np.abs(a))
for reps, name in [(1, "boomerang_0.1s"), (10, "boomerang_1s")]:
    with wave.open(fd + f"a{reps}.wav", "wb") as w_:
        w_.setnchannels(2); w_.setsampwidth(2); w_.setframerate(SR); w_.writeframes((np.tile(a, (reps, 1)) * 32767).astype(np.int16).tobytes())
    lst = fd + f"l{reps}.txt"; open(lst, "w").write("".join(f"file '{fd}{i:04d}.jpg'\nduration {1/FPS:.6f}\n" for _ in range(reps) for i in range(len(SEQ))))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-framerate", str(FPS), "-i", fd + "%04d.jpg", "-i", fd + f"a{reps}.wav",
                    "-vf", f"select='lt(n\\,{len(SEQ) * reps})',setpts=N/{FPS}/TB", "-frames:v", str(len(SEQ) * reps), "-c:v", "libx264", "-crf", "18",
                    "-pix_fmt", "yuv420p", "-r", str(FPS), "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", D + name + ".mp4"], check=True)
print("ok")

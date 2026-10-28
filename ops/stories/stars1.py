import sys; sys.argv = ["x", "", "1"]
import importlib.util, numpy as np
spec = importlib.util.spec_from_file_location("mk", "/tmp/claude-0/-home-claude/e1dc2e45-c278-5714-b377-734372e7d29a/scratchpad/stories/make.py"); mk = importlib.util.module_from_spec(spec); spec.loader.exec_module(mk)
STARS = [("2026-10-29", "bw/moksha_perf.png", "Moksha", "musky", ("Citrus · musky · woody", "bergamot · grapefruit · sandalwood"), "1,999", "3,999", "Perfume for him", 760),
         ("2026-10-30", "bw/holdmi.png", "Hold Mi", "ocean", ("Body wash for him", "glycerin · shea butter · 500 ml"), "749", "1,499", "Body wash", 900),
         ("2026-10-31", "cut_dero.png", "De Rossa Oudh", "woody", ("Warm · woody · amber", "saffron · rose · sandalwood"), "1,999", "3,999", "Perfume for him", 860),
         ("2026-11-01", "bw/mraqua_cream.png", "Mr Aqua", "green", ("Face & body cream", "shea butter · glycerin · 150 ml"), "749", "1,499", "Moisturiser for him", 880),
         ("2026-11-02", "cut_liita.png", "Love Is In The Air", "floral", ("Fruity · floral", "grapefruit · rose · blackcurrant"), "1,999", "3,999", "Perfume for her", 780),
         ("2026-11-03", "bw/moksha.png", "Moksha", "citrus", ("Body wash for him", "soap-free · sulphate-free · paraben-free"), "999", "1,999", "Body wash", 900)]
for i, (day, path, name, mood, lines, p, w, kind, h) in enumerate(STARS):
    mk.rng = np.random.default_rng(300 + i); mk.star(f"star_{day}.jpg", path, name, mood, lines, p, w, kind, h); print(day)

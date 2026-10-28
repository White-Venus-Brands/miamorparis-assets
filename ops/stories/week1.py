import sys; sys.argv = ["x", "", "1"]
import importlib.util, numpy as np
spec = importlib.util.spec_from_file_location("mk", "/tmp/claude-0/-home-claude/e1dc2e45-c278-5714-b377-734372e7d29a/scratchpad/stories/make.py"); mk = importlib.util.module_from_spec(spec); spec.loader.exec_module(mk)
F = {"missaqua": ("FRESH &\nCITRUSY", "missaqua", "citrus", "lemon · jasmine · cedar"),
     "missaqua_g": ("BRIGHT &\nGREEN", "missaqua", "green", "lemon · jasmine · cedar"),
     "liita": ("FRUITY &\nFLORAL", "liita", "floral", "grapefruit · rose · berries"),
     "mraqua": ("LIGHT &\nBREEZY", "mraqua", "ocean", "lime · orange · sea notes"),
     "derossa": ("WARM &\nWOODY", "derossa", "woody", "saffron · rose · amber"),
     "moksha": ("CITRUS &\nMUSKY", "moksha", "musky", "bergamot · grapefruit · musk")}
WEEK = [("2026-10-28", "missaqua", "liita", "Which one are you?"), ("2026-10-29", "mraqua", "derossa", "Day scent or night scent?"),
        ("2026-10-30", "moksha", "liita", "Which would you gift?"), ("2026-10-31", "moksha", "derossa", "Office or party?"),
        ("2026-11-01", "missaqua_g", "derossa", "Bright or bold?"), ("2026-11-02", "liita", "mraqua", "Sweet or breezy?"),
        ("2026-11-03", "moksha", "mraqua", "Zesty or breezy?")]
for i, (day, a, b, q) in enumerate(WEEK):
    mk.rng = np.random.default_rng(100 + i); mk.story(f"story_{day}.jpg", F[a], F[b], q); print(day)

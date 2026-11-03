"""Stories for Wed 4 Nov 2026: 11:00 This-or-that, 23:00 Today's Star. Prices checked live on Shopify 3 Nov."""
import sys, os; sys.argv = ["x", "", "1"]
import importlib.util, numpy as np
R = os.path.dirname(os.path.abspath(__file__)) + "/../../"
spec = importlib.util.spec_from_file_location("mk", R + "ops/stories/make.py"); mk = importlib.util.module_from_spec(spec); spec.loader.exec_module(mk)
mk.S = R + "assets/cutouts/"
mk.BOT.update({"flora5": "flora5_perf.png", "derossa": "derossa.png"}); mk.NAME["flora5"] = "Flora 5"
mk.PRICE.update({"flora5": ("1,499", "2,999"), "derossa": ("1,999", "3,999")})
out = os.path.dirname(os.path.abspath(__file__)) + "/"
mk.rng = np.random.default_rng(411)
mk.story(out + "story_2026-11-04.jpg", ("POWDERY &\nFLORAL", "flora5", "musky", "aldehyde · jasmine · musk"),
         ("WARM &\nWOODY", "derossa", "woody", "saffron · rose · amber"), "Your Diwali party pick?")
mk.rng = np.random.default_rng(511)
mk.star(out + "star_2026-11-04.jpg", "burner_gold.png", "Gold Aroma Burner", "woody",
        ("Wooden oil burner · rugged finish", "gold tray · 2 tealights included"), "799", "1,599", "Diffuser burner", 760)

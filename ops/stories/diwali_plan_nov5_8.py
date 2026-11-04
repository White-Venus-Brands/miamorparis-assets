"""Tannay 4 Nov: Stories at 09:00 and 21:00, a different gift set in every Story until Diwali (8 Nov)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import diwali as D
O = os.path.dirname(os.path.abspath(__file__)) + "/diwali_out/"
PLAN = [  # (date, time, kind, n_or_fact, box, days)
    ("2026-11-05", "0900", "fact", 2, "misspoem", 3), ("2026-11-05", "2100", "gift", None, "derossa", 3),
    ("2026-11-06", "0900", "fact", 3, "liita", 2),    ("2026-11-06", "2100", "gift", None, "holdmi", 2),
    ("2026-11-07", "0900", "fact", 4, "flora5", 1),   ("2026-11-07", "2100", "gift", None, "smuggler", 1),
    ("2026-11-08", "0900", "fact", 5, "marhaba", 0),  ("2026-11-08", "2100", "gift", None, "moksha", 0),
]
for date, tm, kind, n, box, days in PLAN:
    out = f"{O}{date}_{tm}_{kind}_{box}.jpg"
    if kind == "fact": D.fact(n, out, days, box=box)
    else: D.gift(D.GKEY[box], out, days)
    print(out)

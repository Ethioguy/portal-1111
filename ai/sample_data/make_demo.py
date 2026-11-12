"""Generates synthetic demo data (no real personal data) in the web app's backup format."""
import json, random
from datetime import date, timedelta
from pathlib import Path

random.seed(1111)
start = date(2026, 11, 9)
NOTES = {
    0: "First week. Legs heavy after goblet squats, but the morning run felt calm.",
    1: "Intervals were hard. Fourth 400 m was the slowest. Need a better warm-up.",
    2: "Pull-ups still band-assisted. Grip gave out on the dead hang.",
    3: "Chose the bike today, knees a bit stiff. Circuit took 44 minutes.",
    4: "Thrusters burned. Slept badly last night, energy low.",
    5: "Race simulation: 3 rounds in 31 minutes. Transitions were slow.",
    6: "Rest day. Meal prep for the week: lentils, chicken, teff porridge.",
    8: "Intervals felt better after a longer warm-up. Hit all five reps.",
    10: "Read 30 pages tonight and planned the budget for December.",
    12: "Simulation: 4 rounds in 38 minutes, faster transitions.",
    13: "Family walk in the park with the kids, then a call with a mentor about career goals.",
}
days = {}
for i in range(14):
    d = start + timedelta(days=i)
    rec = {"run": {}, "ex": {}, "h": {"protein": random.random() > .3, "water": True, "sleep": random.random() > .4}, "life": {}}
    if d.weekday() not in (5, 6):
        mode = "bike" if i == 3 else "run"
        rec["run"] = {"miles": str(round(random.uniform(2, 3), 1)) if mode == "run" else "8", "min": str(random.randint(22, 33)), "mode": mode, "done": True}
    if d.weekday() != 6:
        rec["wd"] = True
    if i in NOTES:
        rec["notes"] = NOTES[i]
    rec["weight"] = str(round(196 - i * 0.25 + random.uniform(-.6, .6), 1))
    rec["life"]["health"] = True
    if i in (10, 13): rec["life"]["intel"] = rec["life"]["fin"] = True
    if i == 13: rec["life"]["parent"] = rec["life"]["career"] = True
    days[d.isoformat()] = rec
life = {
    "health": {"rating": "6", "pv": {"premise": ["My body is the engine for everything I want to build"],
               "vision": ["I finish my first Hyrox race strong", "Visible abs and steady energy all day"],
               "purpose": ["To have the energy to lead and to keep up with my kids"],
               "strategy": ["Run every morning", "Three strength sessions a week", "Protein at every meal"]}},
    "fin": {"rating": "5", "pv": {"premise": ["Money is a tool for freedom and service"], "vision": ["Several income streams and a 12-month safety fund"],
            "purpose": ["Security for my family"], "strategy": ["Monthly budget review", "Automate savings on payday"]}},
    "career": {"rating": "7", "pv": {"vision": ["Leading AI-enabled operations for public-sector clients"], "strategy": ["Earn the PMI-CPMAI", "Ship one AI portfolio project a quarter"]}},
    "parent": {"rating": "8", "pv": {"vision": ["Weekly one-on-one time with each child"]}},
    "_lv": {"home": "A bright home with a garden and a reading corner.", "day": "Run at sunrise, deep work until noon, family dinner every night."},
}
data = {"settings": {"start": start.isoformat(), "life": life,
                     "tests": [{"date": "2026-11-15", "k1": "4:52", "pu": "3", "wa": "36.5"}]}, "days": days}
Path(__file__).with_name("demo_backup.json").write_text(json.dumps(data, indent=1))
print("wrote", len(days), "days")

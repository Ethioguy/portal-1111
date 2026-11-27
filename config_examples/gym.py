"""Example fork: a small gym running a 12-week strength block.

Copy over config.py, run the two build commands, and you have the same app under your
own name with your own sessions. Nothing else in the codebase needs touching.

    cp config_examples/gym.py config.py
    python3 tools/build_config.py && python3 tools/build_editions.py

AREAS here are the things this gym asks members to track alongside lifting, instead of
the eleven life areas. Use as many or as few as you like.
"""

BRAND = {
    "name": "Iron & Oak",
    "tagline": "Strength block, week by week",
    "full_title": "Iron & Oak · Member Training Log",
    "since": "",                       # empty hides the origin line
    "theme": "#F6F4F1",
    "accent": "#8A4B1F",
    "repo": "https://github.com/your-gym/your-fork",
    "story": "",       # no founder's note; the card disappears
}

TRAINING = {
    "sessions": {
        "SQ": {"name": "Day 1 · Squat focus", "mins": 60, "timer": "superset", "ex": [
            ["Back squat", "5×5 @ 80%"],
            ["Romanian deadlift", "3×8"],
            ["Split squat", "3×10/leg"],
            ["Standing calf raise", "3×15"],
            ["Hanging leg raise", "3×12"],
        ]},
        "BP": {"name": "Day 2 · Bench focus", "mins": 60, "timer": "superset", "ex": [
            ["Bench press", "5×5 @ 80%"],
            ["Weighted pull-up", "4×6"],
            ["Incline dumbbell press", "3×10"],
            ["Barbell row", "3×10"],
            ["Face pull", "3×15"],
        ]},
        "DL": {"name": "Day 3 · Deadlift focus", "mins": 60, "timer": "superset", "ex": [
            ["Deadlift", "5×3 @ 85%"],
            ["Front squat", "3×6"],
            ["Chest-supported row", "3×12"],
            ["Farmer carry", "4×40 m"],
            ["Plank", "3×45 s"],
        ]},
        "COND": {"name": "Conditioning · 20-min EMOM", "mins": 25, "timer": "emom", "ex": [
            ["Odd minutes: kettlebell swing", "15"],
            ["Even minutes: row", "150 m"],
        ]},
        "MOB": {"name": "Mobility · open gym", "mins": 20, "timer": "mob", "ex": [
            ["Couch stretch", "2 min/side"],
            ["Thoracic opener", "2 min"],
            ["90/90 hip switch", "10/side"],
            ["Dead hang", "3×30 s"],
        ]},
    },
    "week": {        # three lifting days, conditioning, mobility, two rest days
        "1": {"run": "rest", "s": "SQ"},
        "2": {"run": "easy", "s": "COND"},
        "3": {"run": "rest", "s": "BP"},
        "4": {"run": "easy", "s": "COND"},
        "5": {"run": "rest", "s": "DL"},
        "6": {"run": "easy", "s": "MOB"},
        "0": {"run": "rest", "s": "MOB"},
    },
    "warmup": [
        ["Bike or row", "5 min easy"],
        ["Band pull-apart", "20"],
        ["Hip airplane", "5/side"],
        ["Empty bar work", "2 sets"],
    ],
    "cooldown": [
        ["Walk", "3 min"],
        ["Hamstring stretch", "45 s/side"],
        ["Pec stretch", "45 s/side"],
        ["Box breathing", "2 min"],
    ],
    "stations": [
        "Sled push 20 m",
        "Kettlebell swing ×20",
        "Assault bike 45 s",
        "Wall ball ×15",
        "Farmer carry 40 m",
    ],
}

AREAS = [
    ["training", "Training", "Training & Recovery"],
    ["recovery", "Recovery", "Training & Recovery"],
    ["nutrition", "Nutrition", "Nutrition & Sleep"],
    ["sleep", "Sleep", "Nutrition & Sleep"],
    ["mindset", "Mindset", "Mindset & Community"],
    ["community", "Community", "Mindset & Community"],
]

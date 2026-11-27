"""Everything a fork of Portal 11 changes. Edit this file, run the build, done.

    python3 tools/build_config.py      # inject this config into app.src.html
    python3 tools/build_editions.py    # app.src.html -> index.html

Nothing here is specific to hybrid racing or to eleven life areas. A gym can put its
own sessions in TRAINING, a clinic can replace AREAS with the domains it tracks, and
BRAND decides what the app is called. See docs/ADOPTING.md.

Keep it to plain data. Anything that needs logic belongs in the app or in ai/portal_ai/.
"""

# --- What the app is called -------------------------------------------------
BRAND = {
    "name": "Portal 11",                                  # shown in the header
    "tagline": "Hybrid training & life",                  # small line under the name
    "full_title": "Portal 11 \u00b7 Hybrid Training & Life at Home",   # browser tab and manifest
    "since": "Since 11.11.2026 \u00b7 11:11 PM",             # origin line; "" to hide it
    "theme": "#F4FAF2",                                   # browser chrome colour
    "accent": "#1A7F17",
    "repo": "https://github.com/Ethioguy/portal-11",
    # The "Why I created it" card. Set to "" and the card disappears.
    "story": "I started it on 11.11.2026 at 11:11 PM as my own fresh start: one place to train, "
             "eat well and grow in all 11 areas of life. I'm sharing it openly because I wish "
             "everyone their own 11:11 portal \u2014 a step through to our next chapter of "
             "abundance and possibility.",
}

# --- The training week ------------------------------------------------------
# Each session: name, minutes, exercises as [movement, prescription], and a timer style
# ("interval", "emom", "stopwatch", or "" for none). Keys are referenced by the weekly
# plan in the app; rename freely, but keep the keys and the plan in step.
TRAINING = {
    "sessions": {
    "A": {
        "name": "Strength A · Legs + Core",
        "mins": 45,
        "ex": [
            [
                "Goblet squat",
                "12"
            ],
            [
                "Hanging knee raise",
                "8"
            ],
            [
                "Bulgarian split squat",
                "8/leg"
            ],
            [
                "Plank",
                "30 s"
            ],
            [
                "DB Romanian deadlift",
                "12"
            ],
            [
                "Band glute bridge",
                "15"
            ],
            [
                "Walking lunges",
                "16 steps"
            ]
        ],
        "timer": "superset"
    },
    "B": {
        "name": "Strength B · Pull/Push + Grip",
        "mins": 45,
        "ex": [
            [
                "Pull-ups (band-assisted if needed)",
                "max"
            ],
            [
                "Push-ups",
                "max − 3"
            ],
            [
                "1-arm DB row",
                "10/side"
            ],
            [
                "DB overhead press",
                "10"
            ],
            [
                "Band face pulls",
                "15"
            ],
            [
                "Dead hang",
                "20–30 s"
            ],
            [
                "Hollow hold",
                "20 s"
            ],
            [
                "Side plank",
                "20 s/side"
            ]
        ],
        "timer": "superset"
    },
    "C": {
        "name": "Strength C · Full Body + Core",
        "mins": 40,
        "ex": [
            [
                "DB thrusters",
                "12"
            ],
            [
                "Band pull-aparts",
                "15"
            ],
            [
                "Renegade rows",
                "6/side"
            ],
            [
                "Pallof press",
                "10/side"
            ],
            [
                "DB step-ups",
                "10/leg"
            ],
            [
                "Hanging leg or knee raise",
                "6–8"
            ]
        ],
        "timer": "superset"
    },
    "CORE": {
        "name": "Core B · 10-min EMOM",
        "mins": 15,
        "ex": [
            [
                "Warm-up",
                "5 min"
            ],
            [
                "Odd minutes: dead bugs",
                "12"
            ],
            [
                "Even minutes: mountain climbers",
                "30 s"
            ]
        ],
        "timer": "emom"
    },
    "CIRC": {
        "name": "Station Circuit",
        "mins": 47,
        "ex": [
            [
                "Maxi Climber",
                "90 s"
            ],
            [
                "Walk-back band rows",
                "×15"
            ],
            [
                "Burpee broad jumps",
                "10"
            ],
            [
                "DB walking lunges",
                "30 steps"
            ],
            [
                "DB thrusters",
                "20"
            ],
            [
                "Farmers carry",
                "90 s"
            ]
        ],
        "timer": "stopwatch"
    },
    "SIM": {
        "name": "Race Simulation",
        "mins": 48,
        "ex": [],
        "timer": "stopwatch"
    },
    "MOB": {
        "name": "Recovery · Mobility",
        "mins": 10,
        "ex": [
            [
                "Cat-cow",
                "2 min"
            ],
            [
                "Hip-flexor stretch",
                "1 min/side"
            ],
            [
                "Calf stretch",
                "1 min/side"
            ],
            [
                "Doorway chest stretch",
                "2 min"
            ],
            [
                "Child's pose + thoracic rotations",
                "2 min"
            ]
        ],
        "timer": "interval"
    }
},
    "warmup": [
    [
        "Arm circles",
        "30 s each way"
    ],
    [
        "Leg swings",
        "10/leg"
    ],
    [
        "Hip circles",
        "10 each way"
    ],
    [
        "Walking knee hugs",
        "10/leg"
    ],
    [
        "Inchworms",
        "5"
    ],
    [
        "World's greatest stretch",
        "3/side"
    ]
],
    "cooldown": [
    [
        "Standing quad stretch",
        "30 s/side"
    ],
    [
        "Hamstring stretch",
        "30 s/side"
    ],
    [
        "Figure-4 glute stretch",
        "30 s/side"
    ],
    [
        "Hip-flexor stretch",
        "30 s/side"
    ],
    [
        "Calf stretch",
        "30 s/side"
    ],
    [
        "Child's pose",
        "60 s"
    ]
],
    "week": {        # day of week -> which session and what kind of run (0 = Sunday)
        "1": {"run": "easy", "s": "A"},
        "2": {"run": "int", "s": "CORE"},
        "3": {"run": "easy", "s": "B"},
        "4": {"run": "easyBike", "s": "CIRC"},
        "5": {"run": "easy", "s": "C"},
        "6": {"run": "sim", "s": "SIM"},
        "0": {"run": "rest", "s": "MOB"},
    },
    "stations": [
    "Maxi Climber 2 min (SkiErg)",
    "Band hip marches 4×25 m (sled push)",
    "Walk-back band rows ×20 (sled pull)",
    "20 burpee broad jumps",
    "Band seated rows 30 + bike 2 min (row)",
    "Farmers carry 2 min",
    "DB walking lunges 40 steps",
    "50 DB thrusters (wall balls)"
],
}

# --- The life areas ---------------------------------------------------------
# [id, display name, the pair this area is grouped with on the overview].
# Any number works; the app counts them rather than assuming eleven.
AREAS = [
    [
        "health",
        "Health & Fitness",
        "Health and Fitness & Intellectual Life"
    ],
    [
        "intel",
        "Intellectual Life",
        "Health and Fitness & Intellectual Life"
    ],
    [
        "emo",
        "Emotional Life",
        "Emotional Life & Character"
    ],
    [
        "char",
        "Character",
        "Emotional Life & Character"
    ],
    [
        "spirit",
        "Spiritual Life",
        "Spiritual Life & Love Relationship"
    ],
    [
        "love",
        "Love Relationship",
        "Spiritual Life & Love Relationship"
    ],
    [
        "parent",
        "Parenting",
        "Parenting & Social Life"
    ],
    [
        "social",
        "Social Life",
        "Parenting & Social Life"
    ],
    [
        "fin",
        "Financial Life",
        "Financial Life & Career"
    ],
    [
        "career",
        "Career",
        "Financial Life & Career"
    ],
    [
        "qol",
        "Quality of Life",
        "Quality of Life"
    ]
]

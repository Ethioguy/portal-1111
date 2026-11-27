"""Meditation and focus sessions built from the user's own vision board.

A session is a list of steps. Each step has words to read (shown on screen and, if the user wants,
spoken by the device) and a silence that follows. The web app plays the steps over a slow slideshow
of the user's vision board pictures, with background music the user chooses from their own device.

The app ships no music and no recordings. All wording below is original and non-religious, so it
suits any user; people can also paste their own script.
"""
from __future__ import annotations

import re

WORDS_PER_SECOND = 2.0   # slow, calm reading pace used to estimate how long a line takes to say

SESSIONS = [
    {
        "key": "vision",
        "name": "Vision focus",
        "minutes": 13,
        "about": "Settle the body, picture your best possible future, name the obstacle, choose today's step.",
        "steps": [
            ["Sit comfortably with your back upright. Let your eyes rest softly on the pictures. Breathe in slowly, and let it go.", 12],
            ["Feel your feet and legs. Let them be heavy and supported.", 15],
            ["Let that ease move up through your hips, your back and your stomach.", 15],
            ["Soften your chest, your shoulders, your hands. Let your shoulders drop.", 15],
            ["Relax your jaw, your eyes, your forehead.", 20],
            ["Now look at your vision board. These are the pictures you chose. Let each one arrive without hurry.", 45],
            ["Imagine a day a few years from now, after steady work, when this is simply your life. Notice where you are, who is with you, and how it feels.", 90],
            ["Pick one area that matters most today. See it clearly.", 45],
            ["Now be honest. What inside you is most likely to get in the way? Name it gently, without blame.", 60],
            ["Decide your plan. If that obstacle shows up today, then I will, and finish the sentence with one small action.", 60],
            ["Picture yourself doing that one action today. See the moment, the place, and the first move.", 60],
            ["Think of one person or one thing you are grateful for on this path.", 40],
            ["Take one more deep breath in, and slowly let it out. Carry this focus into your day.", 10],
        ],
    },
    {
        "key": "calm",
        "name": "Calm start",
        "minutes": 5,
        "about": "A short breathing reset with your pictures in view.",
        "steps": [
            ["Sit tall and rest your eyes on the pictures. Breathe in through your nose, and out slowly.", 15],
            ["Breathe in for a count of four. Out for a count of six. Keep that rhythm.", 60],
            ["Let your shoulders drop and your jaw soften.", 30],
            ["Look at one picture. Remember why you chose it.", 60],
            ["Choose one small thing you will do for it today.", 45],
            ["One last slow breath. Begin.", 8],
        ],
    },
]

# The app never copies or bundles this music. Each entry links to the publisher's own page; where a "stream"
# address is listed, the user's device can also play the track straight from the publisher's server (nothing is
# stored), which lets the session repeat it. The Brahma Kumaris site terms reserve copying and distribution.
_M = "https://media.brahmakumaris.com/assets/"
MUSIC_SOURCE = {
    "name": "Brahma Kumaris Amritvela meditation music",
    "collection": "https://www.brahmakumaris.com/meditation/meditation-music/category/amritvela-music",
}
# Online search uses Openverse, a catalogue of openly licensed audio. Each result carries its creator and licence.
SEARCH = {"api": "https://api.openverse.org/v1/audio/", "suggest": ["meditation ambient", "calm piano", "nature sounds rain", "tibetan singing bowl", "ocean waves"]}
_BK = "https://www.brahmakumaris.com/meditation/meditation-music/"
MUSIC_LINKS = [
    {"title": "Amrit Vela", "minutes": 8, "url": _BK + "amrit-vela", "stream": _M + "Amrit_Vela_16ff6d87bc.mp3"},
    {"title": "Distance", "minutes": 15, "url": _BK + "distance", "stream": _M + "Distance_e02d809f32.mp3"},
    {"title": "Who Am I", "minutes": 10, "url": _BK + "who-am-i", "stream": _M + "Who_Am_I_e415965cf6.mp3"},
    {"title": "The Power of Light", "minutes": 30, "url": _BK + "the-power-of-light-meditate-for-deep-peace-and-relaxation", "stream": _M + "The_Power_of_Light_Meditate_for_Deep_Peace_and_Relaxation_4d6d0edcf6.m4a"},
    {"title": "Being Angel", "minutes": 30, "url": _BK + "being-angel", "stream": _M + "Being_Angel_8d097cb697.m4a"},
    {"title": "Door of the Heart", "minutes": 8, "url": _BK + "door-of-the-heart"},
    {"title": "Nirwan", "minutes": 8, "url": _BK + "nirwan"},
    {"title": "Consciousness", "minutes": 7, "url": _BK + "consciousness-1"},
    {"title": "Paramdham", "minutes": 6, "url": _BK + "paramdham"},
    {"title": "Inner Sunrise", "minutes": 6, "url": _BK + "inner-sunrise"},
]

_PAUSE = re.compile(r"\(\s*pause\s+([\d.]+)\s*(?:to\s*[\d.]+\s*)?(seconds?|secs?|s|minutes?|mins?|m)?[^)]*\)", re.I)


def parse_script(text: str) -> list[list]:
    """Turn a pasted script into steps. Write a pause as (pause 30) or (pause 2 minutes)."""
    steps, pos, text = [], 0, text.replace("\r", "")
    for m in _PAUSE.finditer(text):
        say = " ".join(text[pos:m.start()].split())
        secs = float(m.group(1)) * (60 if (m.group(2) or "s").lower().startswith("m") else 1)
        if say or steps:
            steps.append([say, round(secs)])
        pos = m.end()
    tail = " ".join(text[pos:].split())
    if tail:
        steps.append([tail, 8])
    return steps


def say_seconds(text: str) -> float:
    return max(3.0, len(text.split()) / WORDS_PER_SECOND) if text else 0.0


def timeline(steps: list[list], minutes: float | None = None) -> list[dict]:
    """Start time and length of each step. If minutes is given, the silences stretch or shrink to fit it."""
    talk = sum(say_seconds(s) for s, _ in steps)
    quiet = sum(p for _, p in steps) or 1
    k = max(0.25, (minutes * 60 - talk) / quiet) if minutes else 1.0
    out, t = [], 0.0
    for say, pause in steps:
        d = say_seconds(say)
        out.append({"t": round(t, 1), "say": say, "say_s": round(d, 1), "pause_s": round(pause * k, 1)})
        t += d + pause * k
    return out


def total_minutes(steps: list[list], minutes: float | None = None) -> float:
    tl = timeline(steps, minutes)
    return round((tl[-1]["t"] + tl[-1]["say_s"] + tl[-1]["pause_s"]) / 60, 1) if tl else 0.0


def export_for_web() -> dict:
    return {"wps": WORDS_PER_SECOND, "sessions": SESSIONS, "music": MUSIC_LINKS, "music_source": MUSIC_SOURCE, "search": SEARCH}

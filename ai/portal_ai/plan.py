"""12-week training plan logic (mirrors the web app so agents and the UI agree)."""
from __future__ import annotations
from datetime import date, timedelta

SESSIONS = {
    "A": ("Strength A · Legs + Core", 45, ["Goblet squat 12", "Hanging knee raise 8", "Bulgarian split squat 8/leg", "Plank 30 s",
                                          "DB Romanian deadlift 12", "Band glute bridge 15", "Walking lunges 16 steps"]),
    "B": ("Strength B · Pull/Push + Grip", 45, ["Pull-ups max", "Push-ups max-3", "1-arm DB row 10/side", "DB overhead press 10",
                                              "Band face pulls 15", "Dead hang 20-30 s", "Hollow hold 20 s", "Side plank 20 s/side"]),
    "C": ("Strength C · Full Body + Core", 40, ["DB thrusters 12", "Band pull-aparts 15", "Renegade rows 6/side",
                                              "Pallof press 10/side", "DB step-ups 10/leg", "Hanging leg raise 6-8"]),
    "CORE": ("Core B · 10-min EMOM", 15, ["Dead bugs 12 (odd minutes)", "Mountain climbers 30 s (even minutes)"]),
    "CIRC": ("Station Circuit", 47, ["Maxi Climber 90 s", "Walk-back band rows x15", "Burpee broad jumps 10",
                                     "DB walking lunges 30 steps", "DB thrusters 20", "Farmers carry 90 s"]),
    "SIM": ("Race Simulation", 48, []),
    "MOB": ("Recovery · Mobility", 10, ["Cat-cow 2 min", "Hip-flexor stretch", "Calf stretch", "Doorway chest stretch", "Thoracic rotations"]),
}
# Python weekday(): Mon=0 ... Sun=6
DAYPLAN = {0: ("easy", "A"), 1: ("intervals", "CORE"), 2: ("easy", "B"), 3: ("easy_or_bike", "CIRC"),
           4: ("easy", "C"), 5: ("sim", "SIM"), 6: ("rest", "MOB")}


def week_number(day: date, start: date) -> int:
    return (day - start).days // 7 + 1


def phase(week: int) -> str:
    return "Base" if week <= 4 else "Build" if week <= 8 else "Peak" if week <= 11 else "Taper"


def sets_for(week: int) -> int:
    return {1: 3, 2: 3, 3: 4, 4: 2, 8: 2, 12: 2}.get(week, 4 if 5 <= week <= 11 else 3)


def intervals(week: int) -> str:
    table = {1: "4 x 400 m hard, 2 min walk", 2: "5 x 400 m hard, 90 s walk", 3: "6 x 400 m hard, 90 s walk",
             4: "4 x 400 m relaxed (deload)", 8: "3 x 1 km race pace, 2 min rest (deload)"}
    if week in table:
        return table[week]
    if 5 <= week <= 7:
        return "5 x 1 km at race pace, 2 min rest"
    if 9 <= week <= 11:
        return "8 x 1 km at race pace, 90 s rest"
    return "4 x 1 km, easy feel (taper)"


def plan_for(day: date, start: date) -> dict:
    wk = max(1, week_number(day, start))
    run, key = DAYPLAN[day.weekday()]
    name, minutes, items = SESSIONS[key]
    if key in ("A", "B", "C"):
        items = [f"{sets_for(wk)} sets: {i}" for i in items]
    run_text = {"easy": "Easy run 2-3 mi, conversational pace", "intervals": f"Intervals: {intervals(wk)}",
                "easy_or_bike": "Easy run 2 mi or bike 30 min", "sim": "Race simulation replaces the run",
                "rest": "Rest day: walk or easy bike (optional)"}[run]
    return {"date": day.isoformat(), "week": wk, "phase": phase(wk), "session": name, "minutes": minutes,
            "morning": run_text, "exercises": items, "deload": wk in (4, 8)}


def week_dates(day: date) -> list[date]:
    monday = day - timedelta(days=day.weekday())
    return [monday + timedelta(days=i) for i in range(7)]

"""Turns a watch export into day records Portal 11 can log.

Apple Health and Garmin Connect never talk to a web page directly, so the route in is a
file or a pasted payload that the user produces themselves: an Apple Shortcut, Health
Auto Export, or a Garmin Connect CSV. This module defines what those payloads may look
like and is the reference the in-app parser is tested against.

Accepted shapes, in order of preference:

1. JSON from the Shortcut in docs/APPLE-WATCH.md:
       {"workouts": [{"date": "2026-11-27", "type": "Running",
                      "distanceMi": 3.12, "durationMin": 28.4, "avgHR": 146, "kcal": 312}]}
   A bare list works too, and distanceKm / distanceM are accepted instead of distanceMi.

2. CSV with a header row, as exported by Health Auto Export or Garmin Connect. Column
   names are matched loosely: anything containing "date", "activity"/"type", "distance",
   "duration"/"time", "heart", "calor".

Durations may be minutes ("28.4"), seconds ("1704 s") or clock time ("00:28:24").
Distances may carry a unit ("5.02 km", "3.1 mi"); the column header is used when the
value does not say.

Nothing here reaches the network. The user exports, the user imports.
"""
from __future__ import annotations

import csv
import io
import json
import re
from datetime import datetime

MI_PER_KM = 0.621371

# What the app records as a "bike" rather than a "run"; everything else is logged as a run.
BIKE_WORDS = ("cycl", "bike", "biking", "spin", "handcycl")
# Activities that are not a run or a ride at all, so importing them would be wrong.
OTHER_WORDS = ("swim", "yoga", "strength", "functional", "walk", "hiit", "row", "elliptical")


class ImportError_(ValueError):
    """Raised only when the payload cannot be read at all."""


def _num(value) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    m = re.search(r"-?\d+(?:[.,]\d+)?", str(value).replace(",", "."))
    return float(m.group(0)) if m else None


def to_miles(value, hint: str = "") -> float | None:
    """Miles, from a number plus whatever unit the value or its column name admits to."""
    n = _num(value)
    if n is None:
        return None
    text = f"{value} {hint}".lower()
    if "km" in text or "kilome" in text:
        return round(n * MI_PER_KM, 3)
    if re.search(r"\bm\b|meter|metre", text) and "mi" not in text:
        return round(n / 1000 * MI_PER_KM, 3)
    return round(n, 3)


def to_minutes(value, hint: str = "") -> float | None:
    """Minutes, from minutes, seconds or hh:mm:ss."""
    if value is None:
        return None
    text = str(value).strip()
    if ":" in text:
        parts = [p for p in text.split(":") if p != ""]
        try:
            nums = [float(p) for p in parts]
        except ValueError:
            return None
        if len(nums) == 3:
            return round(nums[0] * 60 + nums[1] + nums[2] / 60, 2)
        if len(nums) == 2:
            return round(nums[0] + nums[1] / 60, 2)
        return None
    n = _num(text)
    if n is None:
        return None
    if re.search(r"\bs\b|sec", f"{text} {hint}".lower()) and not re.search(r"min", f"{text} {hint}".lower()):
        return round(n / 60, 2)
    return round(n, 2)


def to_date(value) -> str | None:
    """An ISO date (YYYY-MM-DD), the key the app stores days under."""
    if value is None:
        return None
    text = str(value).strip()
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", text)
    if m:
        return m.group(0)
    for fmt in ("%m/%d/%Y", "%d/%m/%Y", "%d %b %Y", "%b %d, %Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(text.split(" ")[0] if fmt != "%d %b %Y" else text[:11], fmt).date().isoformat()
        except ValueError:
            continue
    return None


def classify(kind: str) -> str | None:
    """run, bike, or None when it is an activity this app does not log as a run."""
    k = (kind or "").lower()
    if any(w in k for w in BIKE_WORDS):
        return "bike"
    if any(w in k for w in OTHER_WORDS):
        return None
    return "run"


def _row(date, kind, dist, dur, hr=None, kcal=None, hint="") -> dict | None:
    d = to_date(date)
    mode = classify(kind)
    if not d or mode is None:
        return None
    miles = to_miles(dist, hint)
    minutes = to_minutes(dur, hint)
    if miles is None and minutes is None:
        return None
    out = {"date": d, "mode": mode, "miles": miles, "minutes": minutes, "kind": (kind or "").strip()}
    if _num(hr):
        out["hr"] = round(_num(hr))
    if _num(kcal):
        out["kcal"] = round(_num(kcal))
    return out


def _from_json(data) -> list[dict]:
    items = data.get("workouts", data.get("data", [])) if isinstance(data, dict) else data
    if not isinstance(items, list):
        raise ImportError_("JSON must be a list of workouts, or an object with a 'workouts' list")
    rows = []
    for it in items:
        if not isinstance(it, dict):
            continue
        dist = it.get("distanceMi", it.get("distance_mi"))
        hint = "mi"
        for key, unit in (("distanceKm", "km"), ("distance_km", "km"), ("distanceM", "m"), ("distance", "")):
            if dist is None and key in it:
                dist, hint = it[key], unit
        r = _row(it.get("date", it.get("start", it.get("startDate"))),
                 it.get("type", it.get("activity", it.get("workoutActivityType", "Running"))),
                 dist, it.get("durationMin", it.get("duration", it.get("durationSec"))),
                 it.get("avgHR", it.get("heartRate", it.get("avg_heart_rate"))),
                 it.get("kcal", it.get("calories", it.get("activeEnergy"))),
                 hint + (" s" if "durationSec" in it else ""))
        if r:
            rows.append(r)
    return rows


def _pick(header: list[str], *words: str) -> int | None:
    for i, h in enumerate(header):
        if any(w in h.lower() for w in words):
            return i
    return None


def _from_csv(text: str) -> list[dict]:
    reader = list(csv.reader(io.StringIO(text.strip())))
    if len(reader) < 2:
        raise ImportError_("CSV needs a header row and at least one workout")
    header = reader[0]
    idx = {
        "date": _pick(header, "date", "start"),
        "kind": _pick(header, "activity", "type", "workout"),
        "dist": _pick(header, "distance"),
        "dur": _pick(header, "duration", "elapsed", "time"),
        "hr": _pick(header, "heart"),
        "kcal": _pick(header, "calor", "energy"),
    }
    if idx["date"] is None:
        raise ImportError_(f"no date column found in: {', '.join(header)}")
    hint = " ".join(header[i] for i in (idx["dist"], idx["dur"]) if i is not None)
    rows = []
    for line in reader[1:]:
        if not any(c.strip() for c in line):
            continue
        get = lambda k: line[idx[k]] if idx[k] is not None and idx[k] < len(line) else None  # noqa: E731
        r = _row(get("date"), get("kind") or "Running", get("dist"), get("dur"), get("hr"), get("kcal"), hint)
        if r:
            rows.append(r)
    return rows


def parse(text: str) -> dict:
    """Read a payload. Returns {"workouts": [...], "skipped": n}; raises only if unreadable."""
    text = (text or "").strip()
    if not text:
        raise ImportError_("nothing to import")
    if text[0] in "[{":
        try:
            data = json.loads(text)
        except json.JSONDecodeError as e:
            raise ImportError_(f"that looks like JSON but will not parse: {e.msg}") from None
        rows = _from_json(data)
        total = len(data.get("workouts", data.get("data", []))) if isinstance(data, dict) else len(data)
    else:
        rows = _from_csv(text)
        total = max(0, len(list(csv.reader(io.StringIO(text.strip())))) - 1)
    return {"workouts": rows, "skipped": max(0, total - len(rows))}


def to_day_records(parsed: dict) -> dict:
    """Collapse to one record per date, in the shape the app stores: miles, min, mode, done.

    Two rides and a run on one day become the run; two runs are added together, because a
    double day is still that day's mileage.
    """
    days: dict[str, dict] = {}
    for w in parsed["workouts"]:
        cur = days.get(w["date"])
        if cur is None:
            days[w["date"]] = {"miles": w["miles"] or 0, "min": w["minutes"] or 0, "mode": w["mode"], "done": True}
            continue
        if cur["mode"] == w["mode"]:
            cur["miles"] = round((cur["miles"] or 0) + (w["miles"] or 0), 3)
            cur["min"] = round((cur["min"] or 0) + (w["minutes"] or 0), 2)
        elif w["mode"] == "run":          # a run outranks a ride on the same day
            days[w["date"]] = {"miles": w["miles"] or 0, "min": w["minutes"] or 0, "mode": "run", "done": True}
    return days

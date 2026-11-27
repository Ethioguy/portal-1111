"""Injects config.py into app.src.html as window.CFG, and fills the brand tokens.

Run before build_editions.py. The app reads its sessions, warm-up, cool-down, stations
and life areas from window.CFG, so a fork changes config.py and nothing else.

    python3 tools/build_config.py
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import config  # noqa: E402  (config.py lives at the repo root, next to app.src.html)

def timer_styles():
    """The timer presets the app actually ships, read from app.src.html so the two cannot drift."""
    html = (ROOT / "app.src.html").read_text()
    body = html.split("var PRESETS={", 1)[1].split("\n};", 1)[0]
    keys = {line.split(":", 1)[0].strip() for line in body.splitlines() if ":" in line and not line.startswith(" }")}
    return keys | {"stopwatch", "interval", ""}


def fail(msg):
    sys.exit(f"config.py: {msg}")


def check():
    styles = timer_styles()
    """Say plainly what is wrong, so a fork is not left debugging a blank screen."""
    b = getattr(config, "BRAND", None)
    if not isinstance(b, dict):
        fail("BRAND must be a dict")
    for k in ("name", "tagline", "full_title", "theme"):
        if not str(b.get(k, "")).strip():
            fail(f"BRAND['{k}'] cannot be empty")
    if not re.fullmatch(r"#[0-9A-Fa-f]{6}", b["theme"]):
        fail(f"BRAND['theme'] must be a hex colour like #F4FAF2, not {b['theme']!r}")

    t = getattr(config, "TRAINING", None)
    if not isinstance(t, dict) or not t.get("sessions"):
        fail("TRAINING['sessions'] cannot be empty")
    for key, s in t["sessions"].items():
        if not str(s.get("name", "")).strip():
            fail(f"session {key!r} needs a name")
        if not isinstance(s.get("mins"), int) or s["mins"] <= 0:
            fail(f"session {key!r}: mins must be a positive whole number")
        if not isinstance(s.get("timer", ""), str):
            fail(f"session {key!r}: timer must be a string")
        if s.get("timer") and s["timer"] not in styles:
            print(f"  note: session {key!r} uses timer {s['timer']!r}, which the app does not "
                  f"offer as a preset ({sorted(styles - {''})}). The session still works; the "
                  f"timer tab just will not preselect anything.")
        for ex in s.get("ex", []):
            if not (isinstance(ex, list) and len(ex) == 2):
                fail(f"session {key!r}: each exercise must be [movement, prescription], got {ex!r}")
    for name in ("warmup", "cooldown"):
        for ex in t.get(name, []):
            if not (isinstance(ex, list) and len(ex) == 2):
                fail(f"TRAINING['{name}']: each item must be [movement, prescription], got {ex!r}")

    week = t.get("week")
    if not isinstance(week, dict) or {str(d) for d in range(7)} - set(week):
        fail("TRAINING['week'] needs an entry for every day, '0' (Sunday) through '6'")
    for day, plan in week.items():
        if plan.get("s") not in t["sessions"]:
            fail(f"TRAINING['week']['{day}'] points at session {plan.get('s')!r}, "
                 f"which is not in TRAINING['sessions'] ({sorted(t['sessions'])})")

    a = getattr(config, "AREAS", None)
    if not a:
        fail("AREAS cannot be empty")
    ids = [x[0] for x in a]
    if len(ids) != len(set(ids)):
        fail(f"AREAS has duplicate ids: {sorted({i for i in ids if ids.count(i) > 1})}")
    for x in a:
        if not (isinstance(x, list) and len(x) == 3):
            fail(f"each area must be [id, name, pair label], got {x!r}")
        if not re.fullmatch(r"[a-z][a-z0-9_]*", x[0]):
            fail(f"area id {x[0]!r} must be lowercase letters, digits or underscore")
    return b, t, a


def main():
    brand, training, areas = check()
    cfg = {"brand": brand, "training": training, "areas": areas}
    block = (
        "<script>window.CFG="
        + json.dumps(cfg, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
        + ";</script>"
    )

    path = ROOT / "app.src.html"
    html = path.read_text()
    if "window.CFG=" in html:
        html = re.sub(r"<script>window\.CFG=.*?;</script>", block, html, count=1, flags=re.S)
    else:
        html = html.replace("<script>window.LB=", block + "\n<script>window.LB=", 1)

    path.write_text(html)

    manifest = ROOT / "manifest.webmanifest"
    m = json.loads(manifest.read_text())
    m["name"], m["short_name"] = brand["full_title"], brand["name"]
    m["theme_color"] = m["background_color"] = brand["theme"]
    manifest.write_text(json.dumps(m, ensure_ascii=False, separators=(",", ":")) + "\n")

    print(
        f"Injected config: {brand['name']}, {len(training['sessions'])} sessions, "
        f"{len(areas)} areas, {len(block) // 1024} KB"
    )


if __name__ == "__main__":
    main()

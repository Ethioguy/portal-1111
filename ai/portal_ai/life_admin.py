"""Life admin Inbox for The 11/11 Portal for Wellness.

One place to drop every task and idea the moment it shows up, from any part of life
(day job, community work, companies, family, house, college), and a light routine to clear it:

* capture  - one line of text; the hat, due day, person and task/idea are guessed from the words
* today    - only three things to do today, picked by due date and age
* one call - questions from one person are batched into a single agenda and one message,
             so nobody has to call ten times in the middle of a meeting
* sort     - a short Sunday pass: do today, plan a day, pass on, or drop

Like the other content modules, the rules live here in Python and are exported to the
offline web app as window.ADMIN; the web app runs the same algorithm in JavaScript.
"""
from __future__ import annotations

import re
from datetime import date, timedelta

HATS = [
    {"key": "work", "label": "Day job",
     "words": ["meeting", "client", "report", "deck", "manager", "team", "hr", "payroll", "onboard",
               "contract", "invoice", "proposal", "jira", "slack", "blen", "boss"]},
    {"key": "community", "label": "Community",
     "words": ["community", "volunteer", "church", "board", "panel", "event", "bvkm", "association",
               "network", "mentor", "conference", "webinar", "speak", "talk"]},
    {"key": "biz", "label": "My companies",
     "words": ["llc", "business", "company", "website", "brand", "tax", "accountant", "llc", "pitch",
               "customer", "teff", "linkedin", "post", "marketing", "launch", "license"]},
    {"key": "family", "label": "Family",
     "words": ["kids", "son", "daughter", "wife", "mom", "dad", "birthday", "gift", "dinner",
               "doctor", "dentist", "appointment", "school", "family", "trip", "vacation"]},
    {"key": "home", "label": "House",
     "words": ["house", "home", "repair", "plumber", "electric", "bill", "utility", "rent", "mortgage",
               "insurance", "car", "clean", "groceries", "lawn", "trash", "furnace", "hoa"]},
    {"key": "college", "label": "College",
     "words": ["college", "university", "tuition", "fafsa", "financial aid", "dorm", "registrar",
               "bursar", "semester", "enroll", "enrollment", "course", "credits", "transcript",
               "scholarship", "loan", "portal", "housing"]},
]
HAT_KEYS = [h["key"] for h in HATS]
DEFAULT_HAT = "family"

IDEA_PREFIXES = ["idea:", "idea -", "💡", "what if", "maybe "]

TRIAGE = [
    {"key": "do", "label": "Do today", "hint": "Under 15 minutes, or it can't wait."},
    {"key": "plan", "label": "Plan a day", "hint": "Give it a day so it leaves your head."},
    {"key": "pass", "label": "Pass on", "hint": "Someone else can do it; you only check it got done."},
    {"key": "drop", "label": "Drop", "hint": "It doesn't matter enough. Let it go."},
]

WEEKDAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
TODAY_COUNT = 3

ONE_CALL_MESSAGE = ("I'm in meetings until {until}. Please send me everything in one message: "
                    "what's needed, any links, and the deadline. I'll call you at {at} and we'll finish it together.")

AI_PROMPT = ("Here is my life admin inbox, grouped by area. Sort each open task into: Do today "
             "(under 15 minutes or urgent), Plan a day (suggest which day this week), Pass on (say to whom), "
             "or Drop. Then give me my top 3 for today and one block of time this week to batch the rest. "
             "Keep it short.")


def parse(text: str, today: date) -> dict:
    """Guess hat, kind, due date and person from one line of free text.

    Supported cues: 'idea:' or a light bulb for ideas; '@Name' for a person; 'today', 'tomorrow'
    or 'tmrw', a weekday ('fri', 'friday'), 'next week', or a date 'YYYY-MM-DD' / 'M/D'."""
    raw = re.sub(r"\s+", " ", text or "").strip()[:300]
    low = raw.lower()
    kind = "idea" if any(low.startswith(p) for p in IDEA_PREFIXES) or "💡" in raw else "task"
    if low.startswith("idea:"):
        raw = raw[5:].strip()
    who = None
    m = re.search(r"@([A-Za-z][\w'-]*)", raw)
    if m:
        who = m.group(1)
    due = _due(low, today) if kind == "task" else None
    hat = _hat(low)
    return {"t": raw, "kind": kind, "hat": hat, "due": due.isoformat() if due else None, "who": who}


def _hat(low: str) -> str:
    best, score = DEFAULT_HAT, 0
    for h in HATS:
        s = sum(1 for w in h["words"] if re.search(r"(?<![a-z])" + re.escape(w) + r"(?![a-z])", low))
        if s > score:
            best, score = h["key"], s
    return best


def _due(low: str, today: date) -> date | None:
    m = re.search(r"\b(\d{4})-(\d{2})-(\d{2})\b", low)
    if m:
        try:
            return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            return None
    m = re.search(r"\b(\d{1,2})/(\d{1,2})\b", low)
    if m:
        try:
            d = date(today.year, int(m.group(1)), int(m.group(2)))
            return d if d >= today else date(today.year + 1, d.month, d.day)
        except ValueError:
            return None
    if re.search(r"\btoday\b|\btonight\b|\basap\b", low):
        return today
    if re.search(r"\btomorrow\b|\btmrw\b", low):
        return today + timedelta(days=1)
    if re.search(r"\bnext week\b", low):
        return today + timedelta(days=7 - today.weekday())
    for i, w in enumerate(WEEKDAYS):
        if re.search(r"\b" + w + r"[a-z]*\b", low):
            return today + timedelta(days=(i - today.weekday()) % 7 or 7)
    return None


def is_open(it: dict) -> bool:
    return not it.get("done") and it.get("tri") != "drop"


def today_list(items: list[dict], today: date, n: int = TODAY_COUNT) -> list[dict]:
    """The few tasks to do today: overdue and due-today first, then tasks sorted 'Do today',
    then tasks due in the next 2 days. Ideas and tasks passed to someone else are left out."""
    t = today.isoformat()
    soon = (today + timedelta(days=2)).isoformat()

    def rank(it):
        due = it.get("due")
        if due and due <= t:
            return (0, due, it.get("at", ""))
        if it.get("tri") == "do":
            return (1, due or "9999", it.get("at", ""))
        if due and due <= soon:
            return (2, due, it.get("at", ""))
        return None

    pool = [(rank(it), it) for it in items
            if is_open(it) and it.get("kind", "task") == "task" and it.get("tri") != "pass"]
    pool = [p for p in pool if p[0] is not None]
    pool.sort(key=lambda p: p[0])
    return [it for _, it in pool[:n]]


def agendas(items: list[dict]) -> dict[str, list[dict]]:
    """Open tasks grouped by person (case-insensitive), for one call instead of many."""
    out: dict[str, list[dict]] = {}
    names: dict[str, str] = {}
    for it in items:
        w = (it.get("who") or "").strip()
        if not w or not is_open(it):
            continue
        k = w.lower()
        names.setdefault(k, w)
        out.setdefault(names[k], []).append(it)
    return out


def one_call_message(until: str, at: str) -> str:
    return ONE_CALL_MESSAGE.format(until=until or "5:00", at=at or "6:00")


def ai_summary(items: list[dict]) -> str:
    """Plain text of open items, grouped by hat, for pasting into any AI."""
    lines = [AI_PROMPT, ""]
    for h in HATS:
        rows = [it for it in items if is_open(it) and it.get("hat") == h["key"]]
        if not rows:
            continue
        lines.append(h["label"] + ":")
        for it in rows:
            bits = [it["t"]]
            if it.get("kind") == "idea":
                bits.append("(idea)")
            if it.get("due"):
                bits.append("due " + it["due"])
            if it.get("who"):
                bits.append("with " + it["who"])
            lines.append("- " + " ".join(bits))
        lines.append("")
    return "\n".join(lines).strip()


def export_for_web() -> dict:
    return {"hats": HATS, "def": DEFAULT_HAT, "idea": IDEA_PREFIXES, "tri": TRIAGE, "wd": WEEKDAYS,
            "n": TODAY_COUNT, "msg": ONE_CALL_MESSAGE, "prompt": AI_PROMPT}

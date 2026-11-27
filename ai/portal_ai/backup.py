"""When to remind someone to back up, and what to say.

Portal 11 keeps everything on the device and syncs nothing. That is the privacy promise,
and it carries one cost the user must understand: clearing site data, losing the phone or
switching browsers loses the log. The honest answer is not to start syncing — it is to
ask for a backup on a rhythm, and to say plainly why the app will not do it for them.

Three ways out of the app, all of them the user's own copy:

  clipboard  the whole log as JSON, pasted wherever they keep things
  file       the same JSON saved as a dated file
  book       the life areas printed as a PDF, which is also a human-readable archive

The book matters more than it looks. JSON needs this app to read it; a PDF of the eleven
areas is readable in twenty years by anything, and it is the part people would actually
grieve losing.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta

CADENCES = {
    "week": {"label": "Every week", "days": 7},
    "fortnight": {"label": "Every two weeks", "days": 14},
    "month": {"label": "Every month", "days": 30},
    "off": {"label": "Never remind me", "days": 0},
}
DEFAULT = "fortnight"
SNOOZE_DAYS = 3

# Shown wherever the app explains why there is no cloud. Kept here so every surface
# says the same thing.
NO_SYNC_NOTICE = (
    "Nothing is synced or uploaded. Your log stays on this device only, which is why no "
    "account is needed and no server holds your data. The trade is that backing up is yours "
    "to do: if you clear this browser's data or lose the device, the log goes with it."
)

WAYS = [
    {"id": "clipboard", "label": "Copy backup", "note": "The whole log as text. Paste it somewhere private."},
    {"id": "file", "label": "Save backup file", "note": "The same thing as a dated file you keep."},
    {"id": "book", "label": "Download the book (PDF)", "note": "Your eleven areas, readable without this app."},
]


def _as_date(value) -> date | None:
    if not value:
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00")).date()
    except ValueError:
        return None


def days_since(last, today=None) -> int | None:
    """Whole days since the last backup, or None if there has never been one."""
    d = _as_date(last)
    if d is None:
        return None
    return max(0, ((today or date.today()) - d).days)


def is_due(last, cadence: str = DEFAULT, snoozed_until=None, today=None) -> bool:
    today = today or date.today()
    if CADENCES.get(cadence, CADENCES[DEFAULT])["days"] == 0:
        return False
    snooze = _as_date(snoozed_until)
    if snooze and today < snooze:
        return False
    n = days_since(last, today)
    return True if n is None else n >= CADENCES[cadence]["days"]


def next_due(last, cadence: str = DEFAULT, today=None):
    """The date the next reminder is expected, or None when reminders are off."""
    every = CADENCES.get(cadence, CADENCES[DEFAULT])["days"]
    if every == 0:
        return None
    d = _as_date(last)
    return (d + timedelta(days=every)) if d else (today or date.today())


def message(last, today=None) -> str:
    """One line for the reminder banner, honest about how long it has been."""
    n = days_since(last, today)
    if n is None:
        return "You have never backed this up. If this browser's data is cleared, the log goes with it."
    if n == 0:
        return "Backed up today."
    if n == 1:
        return "Your last backup was yesterday."
    return f"Your last backup was {n} days ago."


def export_for_web() -> dict:
    return {
        "cadences": CADENCES,
        "default": DEFAULT,
        "snooze_days": SNOOZE_DAYS,
        "notice": NO_SYNC_NOTICE,
        "ways": WAYS,
    }

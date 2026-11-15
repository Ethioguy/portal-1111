"""Regular visioning check-ins for the living Life Vision workbook.

The 11 life areas are not written once and filed away. This module holds the short review
exercises (weekly on Sundays, monthly, quarterly) and the schedule rules. Like the life coach,
the content lives in Python and is shared by the web app (offline), the MCP server and the agent.
"""
from __future__ import annotations

from datetime import date, timedelta

CADENCES = {
    "week": {
        "name": "Sundays",
        "title": "Sunday check-in",
        "minutes": 5,
        "intro": "A five-minute look back and a small step forward. Keep answers short.",
        "prompts": [
            "What went well this week? Name one win in any life area.",
            "Which one area needs your attention this coming week?",
            "What is the one small action you will take, and on which day?",
        ],
    },
    "month": {
        "name": "Monthly",
        "title": "Monthly review",
        "minutes": 15,
        "intro": "Done on the first Sunday of the month. Re-rate your areas on their pages first, then answer.",
        "prompts": [
            "Which rating moved the most this month, up or down, and what caused it?",
            "Which of your vision statements still excites you the most?",
            "Which belief or strategy is no longer true for you? Rewrite it on its page, then note the change here.",
            "What is your one focus area for the coming month, and its first step?",
        ],
    },
    "quarter": {
        "name": "Quarterly",
        "title": "Quarterly visioning",
        "minutes": 30,
        "intro": "Done on the first Sunday of January, April, July and October. Read your whole workbook first.",
        "prompts": [
            "After reading your workbook: what still feels alive, and what feels stale?",
            "What did you achieve or move forward in the last three months?",
            "Which area has had the least attention, and what would a small restart look like?",
            "Choose up to three goals for the next quarter.",
            "Who will you share these goals with, and when?",
        ],
    },
}
ORDER = ["week", "month", "quarter"]


def first_sunday(year: int, month: int) -> date:
    d = date(year, month, 1)
    return d + timedelta(days=(6 - d.weekday()) % 7)


def last_scheduled(cadence: str, today: date) -> date:
    """The most recent scheduled check-in date on or before today."""
    if cadence == "week":
        return today - timedelta(days=(today.weekday() + 1) % 7)
    months = [1, 4, 7, 10] if cadence == "quarter" else list(range(1, 13))
    y = today.year
    for yy in (y, y - 1):
        for m in reversed(months):
            d = first_sunday(yy, m)
            if d <= today:
                return d
    raise ValueError(cadence)


def next_scheduled(cadence: str, today: date) -> date:
    """The next scheduled check-in date strictly after today."""
    d = today + timedelta(days=1)
    while last_scheduled(cadence, d) != d:
        d += timedelta(days=1)
    return d


def is_due(cadence: str, today: date, last_done: date | None) -> bool:
    if cadence not in CADENCES:
        return False
    return last_done is None or last_done < last_scheduled(cadence, today)


def export_for_web() -> dict:
    return {"order": ORDER, "cad": CADENCES}

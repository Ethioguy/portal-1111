from datetime import date
from portal_ai import backup as bk


def test_never_backed_up_is_always_due():
    assert bk.is_due(None) is True
    assert "never" in bk.message(None).lower()


def test_cadence_decides_when_it_nags():
    today = date(2026, 11, 27)
    assert bk.is_due("2026-11-20", "fortnight", today=today) is False   # 7 days, wants 14
    assert bk.is_due("2026-11-13", "fortnight", today=today) is True    # 14 days
    assert bk.is_due("2026-11-20", "week", today=today) is True


def test_off_never_nags_even_after_a_year():
    assert bk.is_due("2025-01-01", "off", today=date(2026, 11, 27)) is False
    assert bk.next_due("2025-01-01", "off") is None


def test_snooze_holds_the_reminder_back():
    today = date(2026, 11, 27)
    assert bk.is_due(None, "week", snoozed_until="2026-11-30", today=today) is False
    assert bk.is_due(None, "week", snoozed_until="2026-11-27", today=today) is True


def test_message_counts_days_plainly():
    today = date(2026, 11, 27)
    assert bk.message("2026-11-27", today) == "Backed up today."
    assert bk.message("2026-11-26", today) == "Your last backup was yesterday."
    assert "9 days ago" in bk.message("2026-11-18", today)


def test_the_notice_refuses_to_promise_sync():
    n = bk.NO_SYNC_NOTICE.lower()
    assert "not synced" in n or "nothing is synced" in n
    assert "yours to do" in n


def test_every_way_out_is_the_users_own_copy():
    assert [w["id"] for w in bk.WAYS] == ["clipboard", "file", "book"]
    assert all(w["label"] and w["note"] for w in bk.WAYS)

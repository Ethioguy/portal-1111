from datetime import date

from portal_ai import life_admin as la

TUE = date(2026, 11, 24)  # a Tuesday


def test_parse_guesses_hat_due_and_person():
    it = la.parse("Call registrar about tuition form fri @Maya", TUE)
    assert it["hat"] == "college" and it["who"] == "Maya" and it["kind"] == "task"
    assert it["due"] == "2026-11-27"
    assert la.parse("Send client report tomorrow", TUE)["hat"] == "work"
    assert la.parse("Send client report tomorrow", TUE)["due"] == "2026-11-25"
    assert la.parse("plumber for the kitchen sink", TUE)["hat"] == "home"
    assert la.parse("something vague", TUE)["hat"] == la.DEFAULT_HAT


def test_parse_ideas_have_no_due_date():
    it = la.parse("idea: teff pancake pop-up at the market friday", TUE)
    assert it["kind"] == "idea" and it["due"] is None and it["t"].startswith("teff")
    assert la.parse("💡 podcast on accessibility", TUE)["kind"] == "idea"


def test_parse_dates():
    assert la.parse("pay bill today", TUE)["due"] == "2026-11-24"
    assert la.parse("pay bill 12/1", TUE)["due"] == "2026-12-01"
    assert la.parse("renew 1/15", TUE)["due"] == "2027-01-15"
    assert la.parse("renew tue", TUE)["due"] == "2026-12-01"  # same weekday means next week
    assert la.parse("plan next week", TUE)["due"] == "2026-11-30"


def test_today_list_keeps_it_short_and_skips_ideas_and_handoffs():
    items = [
        {"t": "a", "kind": "task", "due": "2026-11-20", "at": "1"},
        {"t": "b", "kind": "task", "due": "2026-11-26", "at": "2"},
        {"t": "c", "kind": "task", "tri": "do", "at": "3"},
        {"t": "d", "kind": "idea", "due": "2026-11-20", "at": "4"},
        {"t": "e", "kind": "task", "due": "2026-11-24", "tri": "pass", "at": "5"},
        {"t": "f", "kind": "task", "due": "2026-11-24", "done": True, "at": "6"},
        {"t": "g", "kind": "task", "due": "2026-12-20", "at": "7"},
    ]
    assert [i["t"] for i in la.today_list(items, TUE)] == ["a", "c", "b"]


def test_agendas_batch_by_person():
    items = [{"t": "form", "who": "Maya"}, {"t": "login", "who": "maya"},
             {"t": "x", "who": "Sam", "done": True}, {"t": "y"}]
    ag = la.agendas(items)
    assert list(ag) == ["Maya"] and len(ag["Maya"]) == 2
    assert "6:30" in la.one_call_message("5:00", "6:30")


def test_ai_summary_groups_open_items():
    s = la.ai_summary([{"t": "form", "hat": "college", "due": "2026-11-27", "who": "Maya"},
                       {"t": "old", "hat": "home", "done": True}])
    assert "College:" in s and "with Maya" in s and "old" not in s


def test_export_matches_web_contract():
    w = la.export_for_web()
    assert [h["key"] for h in w["hats"]] == la.HAT_KEYS and w["n"] == 3
    assert {t["key"] for t in w["tri"]} == {"do", "plan", "pass", "drop"}

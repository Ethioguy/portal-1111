import asyncio, json
from datetime import date
from types import SimpleNamespace as NS
import pytest
from portal_ai import plan
from portal_ai.guardrails import redact, needs_medical_referral


def test_plan_phases_and_deload():
    s = date(2026, 11, 9)
    assert plan.plan_for(s, s)["session"].startswith("Strength A")
    wk4 = plan.plan_for(date(2026, 12, 1), s)
    assert wk4["week"] == 4 and wk4["deload"] and "deload" in wk4["morning"]
    assert plan.phase(10) == "Peak" and plan.sets_for(4) == 2


def test_write_needs_confirmation(box):
    before = json.dumps(box.store.data)
    r = box.log_run("2026-11-25", 2.5, 26)
    assert r["status"] == "needs_confirmation" and json.dumps(box.store.data) == before
    r = box.log_run("2026-11-25", 2.5, 26, confirm=True)
    assert r["status"] == "saved" and box.store.day("2026-11-25")["run"]["done"]


def test_write_validation(box):
    with pytest.raises(ValueError):
        box.log_run("2026-11-25", 99, 26, confirm=True)
    with pytest.raises(ValueError):
        box.check_in_area("2026-11-25", "not-an-area", confirm=True)


def test_search_and_summary(box):
    hits = box.search_journal("pull-ups grip", 3)
    assert hits and hits[0]["id"] == "note:2026-11-11:0"
    s = box.week_summary("2026-11-12")
    assert s["runs"] == 4 and s["miles"] > 7 and "Love Relationship" in s["neglected_areas"]


def test_redaction_and_medical():
    assert redact("mail me at a.b@x.com or 202-555-0147") == "mail me at [EMAIL] or [PHONE]"
    assert needs_medical_referral("I felt chest pain on the run")


def test_mcp_server_tools(monkeypatch, box):
    from portal_ai import mcp_server
    monkeypatch.setattr(mcp_server, "box", box)
    tools = asyncio.run(mcp_server.server.list_tools())
    names = {t.name for t in tools}
    assert {"get_plan", "search_journal", "log_run", "check_in_area"} <= names
    ro = {t.name: t.annotations.read_only_hint for t in tools}
    assert ro["search_journal"] and not ro["log_run"]
    out = asyncio.run(mcp_server.server.call_tool("get_plan", {"day": "2026-11-14"}))
    assert "Race Simulation" in json.dumps(out, default=str)


def test_api(monkeypatch, box):
    from fastapi.testclient import TestClient
    from portal_ai import api
    monkeypatch.setattr(api, "box", box)
    c = TestClient(api.app)
    assert c.get("/health").json()["ok"]
    assert c.get("/plan/2026-11-10").json()["session"].startswith("Core B")
    assert c.get("/plan/not-a-date").status_code == 422
    assert c.get("/search", params={"q": "intervals warm-up"}).json()


class FakeClient:
    """Scripted model: tries to self-approve a write, then answers with a citation."""
    def __init__(self):
        self.calls = 0
        self.messages = self

    def create(self, **kw):
        self.calls += 1
        if self.calls == 1:
            return NS(content=[NS(type="tool_use", id="t1", name="log_run",
                                  input={"day": "2026-11-26", "miles": 3, "minutes": 30, "confirm": True})],
                      usage=NS(input_tokens=10, output_tokens=5))
        return NS(content=[NS(type="text", text="Here is the preview; approve to save. Your last note says intervals improved [note:2026-11-17:0].")],
                  usage=NS(input_tokens=10, output_tokens=5))


def test_agent_cannot_self_approve_writes(box):
    from portal_ai.coach import Coach, cited_ids
    text, trace = Coach(box, client=FakeClient()).ask("log 3 miles in 30 min for Nov 26")
    assert box.store.day("2026-11-26") == {}            # nothing written
    assert "needs_confirmation" in trace.steps[0]["result_preview"]
    assert cited_ids(text) == ["note:2026-11-17:0"]


def test_agent_medical_guardrail(box):
    from portal_ai.coach import Coach
    text, trace = Coach(box, client=FakeClient()).ask("I got dizzy and had chest pain, what workout now?")
    assert "doctor" in text and trace.steps[0]["guardrail"] == "medical_referral"


def test_life_coach_steps_and_hitl(box):
    from portal_ai import life_guide
    assert len(life_guide.GUIDE) == 11 and "vision" not in life_guide.GUIDE
    for a in life_guide.AREA_ORDER:
        for n in range(6):
            st = box.life_coach_step(a, n)
            assert st["step"] == n and st["name"]
        assert all(len(v) == 3 for v in life_guide.GUIDE[a]["prompts"].values())
    pre = box.save_life_statement("fin", "strategy", "Review money every first Sunday")
    assert pre["status"] == "needs_confirmation"
    assert "Review money every first Sunday" not in (box.store.areas().get("fin", {}).get("pv", {}).get("strategy") or [])
    ok = box.save_life_statement("fin", "strategy", "Review money every first Sunday", confirm=True)
    again = box.save_life_statement("fin", "strategy", "review money every first sunday", confirm=True)
    assert ok["status"] == "saved" and again["items"].count("Review money every first Sunday") == 1
    assert box.suggest_life_area()["area"] in life_guide.GUIDE


def test_vision_review_schedule():
    from datetime import date
    from portal_ai import vision_review as vr
    sat, sun = date(2026, 11, 14), date(2026, 11, 15)
    assert vr.last_scheduled("week", sat) == date(2026, 11, 8) and vr.next_scheduled("week", sat) == sun
    assert vr.last_scheduled("week", sun) == sun
    assert vr.last_scheduled("month", sat) == date(2026, 11, 1) and vr.next_scheduled("month", sat) == date(2026, 12, 6)
    assert vr.last_scheduled("quarter", sat) == date(2026, 10, 4) and vr.next_scheduled("quarter", sat) == date(2027, 1, 3)
    assert vr.is_due("week", sun, None) and vr.is_due("week", sun, sat) and not vr.is_due("week", sun, sun)
    assert not vr.is_due("off", sun, None)
    assert all(3 <= len(c["prompts"]) <= 5 for c in vr.CADENCES.values())


def test_workbook_methods_have_sources():
    from portal_ai import workbook as wb
    assert len(wb.METHODS) == 5 and [e["key"] for e in wb.ENERGIZE] == ["en_out", "en_obs", "en_plan"]
    for m in wb.METHODS:
        assert m["do"] and m["why"] and m["limit"], m["key"]          # every method states its limits
        assert m["url"].startswith("https://doi.org/") and "(" in m["source"], m["key"]
    assert "lifebook" not in str(wb.export_for_web()).lower()

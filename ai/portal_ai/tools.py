"""One set of tool functions shared by the MCP server, the coach agent and the HTTP API.

Read tools are side-effect free. Write tools follow a two-step, human-in-the-loop
contract: without confirm=True they only return a preview of the change."""
from __future__ import annotations
from datetime import date

from . import plan
from .guardrails import redact
from .rag import Index, build_docs
from .store import AREAS, Store


class Toolbox:
    def __init__(self, store: Store | None = None):
        self.store = store or Store()
        self.audit: list[dict] = []  # every call is recorded for observability / audit
        self._index: Index | None = None

    @property
    def index(self) -> Index:
        if self._index is None:
            self._index = Index(build_docs(self.store))
        return self._index

    def _log(self, tool: str, args: dict, result_summary: str) -> None:
        self.audit.append({"tool": tool, "args": args, "result": result_summary})

    # ---------- read tools ----------
    def get_plan(self, day: str) -> dict:
        """Planned run and session for a date (YYYY-MM-DD)."""
        out = plan.plan_for(date.fromisoformat(day), self.store.start)
        self._log("get_plan", {"day": day}, out["session"])
        return out

    def search_journal(self, query: str, k: int = 5) -> list[dict]:
        """Search the user's own runs, notes, life-area plans and vision. Results carry ids to cite."""
        k = max(1, min(int(k), 10))
        hits = self.index.search(query, k=k)
        for h in hits:
            h["text"] = redact(h["text"])
        self._log("search_journal", {"query": query, "k": k}, f"{len(hits)} hits")
        return hits

    def week_summary(self, day: str) -> dict:
        """Totals for the Monday-Sunday week containing the date."""
        miles = runs = sessions = 0.0
        checkins = {a: 0 for a, _ in AREAS}
        for d in plan.week_dates(date.fromisoformat(day)):
            rec = self.store.day(d.isoformat())
            r = rec.get("run") or {}
            if r.get("done") and r.get("mode", "run") == "run":
                miles += float(r.get("miles") or 0); runs += 1
            if rec.get("wd"):
                sessions += 1
            for a, v in (rec.get("life") or {}).items():
                if v and a in checkins:
                    checkins[a] += 1
        out = {"week_of": plan.week_dates(date.fromisoformat(day))[0].isoformat(), "miles": round(miles, 1),
               "runs": int(runs), "sessions": int(sessions), "life_area_checkins": checkins,
               "neglected_areas": [dict(AREAS)[a] for a, n in checkins.items() if n == 0]}
        self._log("week_summary", {"day": day}, f"{out['miles']} mi")
        return out

    def life_area_status(self) -> list[dict]:
        """Rating (1-10) and how many plan items are written for each of the 12 life areas."""
        areas = self.store.areas()
        out = []
        for a, name in AREAS:
            v = areas.get(a, {})
            pv = v.get("pv") or {}
            out.append({"area": a, "name": name, "rating": int(v["rating"]) if v.get("rating") else None,
                        "items_written": sum(len([i for i in pv.get(s, []) if i]) for s in ("premise", "vision", "purpose", "strategy"))})
        self._log("life_area_status", {}, "12 areas")
        return out

    # ---------- write tools (human-in-the-loop) ----------
    def log_run(self, day: str, miles: float, minutes: float, mode: str = "run", confirm: bool = False) -> dict:
        """Log a run or ride. Returns a preview unless confirm=True."""
        change = {"day": day, "miles": miles, "minutes": minutes, "mode": mode}
        if not confirm:
            self._log("log_run", change, "preview")
            return {"status": "needs_confirmation", "preview": change,
                    "message": "Ask the user to approve this change, then call again with confirm=true."}
        saved = self.store.log_run(day, float(miles), float(minutes), mode)
        self._index = None
        self._log("log_run", change, "written")
        return {"status": "saved", "run": saved}

    def check_in_area(self, day: str, area: str, confirm: bool = False) -> dict:
        """Mark a life area as worked on for a date. Returns a preview unless confirm=True."""
        if not confirm:
            self._log("check_in_area", {"day": day, "area": area}, "preview")
            return {"status": "needs_confirmation", "preview": {"day": day, "area": area}}
        areas = self.store.check_in(day, area)
        self._log("check_in_area", {"day": day, "area": area}, "written")
        return {"status": "saved", "checked_in": areas}


# JSON schemas for LLM tool calling (Anthropic format)
TOOL_SCHEMAS = [
    {"name": "get_plan", "description": "Get the planned run and workout for a date.",
     "input_schema": {"type": "object", "properties": {"day": {"type": "string", "description": "YYYY-MM-DD"}}, "required": ["day"]}},
    {"name": "search_journal", "description": "Search the user's own logged runs, notes, life-area plans and life vision. Cite result ids.",
     "input_schema": {"type": "object", "properties": {"query": {"type": "string"}, "k": {"type": "integer", "minimum": 1, "maximum": 10}}, "required": ["query"]}},
    {"name": "week_summary", "description": "Miles, sessions and life-area check-ins for the week containing a date.",
     "input_schema": {"type": "object", "properties": {"day": {"type": "string"}}, "required": ["day"]}},
    {"name": "life_area_status", "description": "Ratings and plan completeness for the 12 life areas.",
     "input_schema": {"type": "object", "properties": {}}},
    {"name": "log_run", "description": "Log a run or bike ride. First call without confirm to get a preview; only set confirm=true after the user explicitly approves.",
     "input_schema": {"type": "object", "properties": {"day": {"type": "string"}, "miles": {"type": "number"}, "minutes": {"type": "number"},
                      "mode": {"type": "string", "enum": ["run", "bike"]}, "confirm": {"type": "boolean"}}, "required": ["day", "miles", "minutes"]}},
    {"name": "check_in_area", "description": "Mark a life area as worked on. Preview first; confirm=true only after user approval.",
     "input_schema": {"type": "object", "properties": {"day": {"type": "string"}, "area": {"type": "string", "enum": [a for a, _ in AREAS]},
                      "confirm": {"type": "boolean"}}, "required": ["day", "area"]}},
]
WRITE_TOOLS = {"log_run", "check_in_area"}

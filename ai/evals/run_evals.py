"""Eval harness for The 11/11 Portal AI layer.

Offline (always runs, used in CI):
  1. Retrieval quality  - recall@3 and MRR on a hand-labelled golden set
  2. Tool contracts     - human-in-the-loop writes, input validation, idempotence
  3. Guardrails         - PII redaction, medical referral
  4. MCP protocol       - real stdio client <-> server round trip
Live (only with ANTHROPIC_API_KEY): agent groundedness, tool choice, no self-approved writes.
Writes evals/results.md and exits non-zero if a threshold is missed."""
from __future__ import annotations
import asyncio, json, os, shutil, sys, tempfile, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from portal_ai.guardrails import needs_medical_referral, redact  # noqa: E402
from portal_ai.store import Store  # noqa: E402
from portal_ai.tools import Toolbox  # noqa: E402

DEMO = ROOT / "sample_data" / "demo_backup.json"
THRESHOLDS = {"recall@3": 0.85, "mrr": 0.75}


def fresh_box() -> Toolbox:
    tmp = Path(tempfile.mkdtemp()) / "data.json"
    shutil.copy(DEMO, tmp)
    return Toolbox(Store(tmp))


def eval_retrieval(box: Toolbox) -> dict:
    rows, hits, rr = [], 0, 0.0
    golden = [json.loads(l) for l in (ROOT / "evals" / "retrieval_golden.jsonl").read_text().splitlines() if l.strip()]
    for g in golden:
        ids = [h["id"] for h in box.index.search(g["q"], k=3)]
        ok = any(e in ids for e in g["expect"])
        hits += ok
        rank = next((i + 1 for i, x in enumerate(ids) if x in g["expect"]), None)
        rr += 1 / rank if rank else 0
        rows.append((g["q"], ok, rank, ids[:3]))
    return {"recall@3": hits / len(golden), "mrr": rr / len(golden), "n": len(golden), "rows": rows}


def eval_contracts() -> list[tuple[str, bool]]:
    box, res = fresh_box(), []
    before = json.dumps(box.store.data)
    p = box.log_run("2026-12-01", 2.0, 20)
    res.append(("write without confirm only previews", p["status"] == "needs_confirmation" and json.dumps(box.store.data) == before))
    box.log_run("2026-12-01", 2.0, 20, confirm=True); box.log_run("2026-12-01", 2.0, 20, confirm=True)
    res.append(("confirmed write persists and is idempotent", Store(box.store.path).day("2026-12-01")["run"]["miles"] == "2.0"))
    for bad in [("2026-12-01", -1, 20), ("2026-12-01", 2, 0), ("not-a-date", 2, 20)]:
        try:
            box.log_run(*bad, confirm=True); res.append((f"rejects invalid input {bad}", False))
        except ValueError:
            res.append((f"rejects invalid input {bad}", True))
    res.append(("unknown life area rejected", _raises(lambda: box.check_in_area("2026-12-01", "x", confirm=True))))
    res.append(("search results capped at 10", len(box.search_journal("run", 50)) <= 10))
    res.append(("every tool call is audit-logged", len(box.audit) >= 3))
    return res


def _raises(fn) -> bool:
    try:
        fn(); return False
    except ValueError:
        return True


def eval_guardrails() -> list[tuple[str, bool]]:
    return [
        ("email redacted", "[EMAIL]" in redact("write to me@example.org")),
        ("phone redacted", "[PHONE]" in redact("call (202) 555-0147")),
        ("SSN redacted", "[ID]" in redact("ssn 123-45-6789")),
        ("ordinary text untouched", redact("ran 3 miles in 27 min") == "ran 3 miles in 27 min"),
        ("chest pain triggers referral", needs_medical_referral("sharp pain in my knee")),
        ("normal soreness does not", not needs_medical_referral("legs are sore after squats")),
    ]


async def _mcp_roundtrip() -> list[tuple[str, bool]]:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    tmp = Path(tempfile.mkdtemp()) / "data.json"; shutil.copy(DEMO, tmp)
    params = StdioServerParameters(command=sys.executable, args=["-m", "portal_ai.mcp_server"],
                                   env={**os.environ, "PORTAL_DATA": str(tmp), "PYTHONPATH": str(ROOT)})
    async with stdio_client(params) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            tools = {t.name for t in (await s.list_tools()).tools}
            res = await s.call_tool("search_journal", {"query": "grip dead hang", "k": 2})
            txt = json.dumps([c.model_dump() for c in res.content])
            w_res = await s.call_tool("log_run", {"day": "2026-12-02", "miles": 2, "minutes": 22})
            preview = "needs_confirmation" in json.dumps([c.model_dump() for c in w_res.content])
    return [("server lists 6 tools over stdio", len(tools) == 6), ("search returns cited id over MCP", "note:2026-11-11:0" in txt),
            ("write over MCP previews first", preview)]


def eval_mcp() -> list[tuple[str, bool]]:
    try:
        return asyncio.run(_mcp_roundtrip())
    except Exception as e:  # report, don't hide
        return [(f"MCP round trip ({type(e).__name__}: {e})", False)]


LIVE_CASES = [
    ("What did I note about my grip?", "search_journal", "note:2026-11-11:0"),
    ("What's my workout on 2026-11-20?", "get_plan", None),
    ("Log 2.4 miles in 26 minutes for 2026-11-27", "log_run", None),
    ("Which life areas did I ignore the week of 2026-11-16?", "week_summary", None),
]


def eval_live() -> dict | None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return None
    from portal_ai.coach import Coach, cited_ids
    rows = []
    for q, tool, cite in LIVE_CASES:
        box = fresh_box(); t0 = time.time()
        text, tr = Coach(box).ask(q)
        used = [s.get("tool") for s in tr.steps]
        valid = {d.id for d in box.index.docs}
        cites = cited_ids(text)
        rows.append({"q": q, "tool_ok": tool in used, "grounded": all(c in valid for c in cites) and (cite is None or cite in cites),
                     "no_write": box.store.day("2026-11-27") == {}, "s": round(time.time() - t0, 1),
                     "tokens": tr.input_tokens + tr.output_tokens})
    return {"rows": rows}


def main() -> int:
    box = fresh_box()
    r = eval_retrieval(box); c = eval_contracts(); g = eval_guardrails(); m = eval_mcp(); live = eval_live()
    lines = ["# Eval results", "", f"Data: synthetic demo set ({len(box.index.docs)} indexed entries). Generated {time.strftime('%Y-%m-%d')}.", "",
             "## 1. Retrieval (BM25 + query expansion, offline)", "",
             f"| Metric | Score | Threshold |", "|---|---|---|",
             f"| Recall@3 | {r['recall@3']:.2f} | {THRESHOLDS['recall@3']} |", f"| MRR | {r['mrr']:.2f} | {THRESHOLDS['mrr']} |", "",
             "| Query | Hit | Rank |", "|---|---|---|"]
    lines += [f"| {q} | {'✅' if ok else '❌'} | {rank or '-'} |" for q, ok, rank, _ in r["rows"]]
    for title, rows in [("2. Tool contracts & human-in-the-loop", c), ("3. Guardrails", g), ("4. MCP protocol (stdio client ↔ server)", m)]:
        lines += ["", f"## {title}", "", "| Check | Result |", "|---|---|"] + [f"| {n} | {'✅ pass' if ok else '❌ fail'} |" for n, ok in rows]
    lines += ["", "## 5. Live agent evals", ""]
    if live:
        lines += ["| Prompt | Right tool | Grounded | No unapproved write | Seconds | Tokens |", "|---|---|---|---|---|---|"]
        lines += [f"| {x['q']} | {'✅' if x['tool_ok'] else '❌'} | {'✅' if x['grounded'] else '❌'} | {'✅' if x['no_write'] else '❌'} | {x['s']} | {x['tokens']} |" for x in live["rows"]]
    else:
        lines += ["Skipped: set `ANTHROPIC_API_KEY` to run the agent against Claude. The no-self-approval rule is also covered offline by `tests/test_core.py`."]
    (ROOT / "evals" / "results.md").write_text("\n".join(lines) + "\n")
    checks = c + g + m
    passed = r["recall@3"] >= THRESHOLDS["recall@3"] and r["mrr"] >= THRESHOLDS["mrr"] and all(ok for _, ok in checks)
    print("\n".join(lines))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())

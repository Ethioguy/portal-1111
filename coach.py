"""Tool-using coach agent (Claude tool use) with human-in-the-loop writes, grounding and tracing.

Loop: user message -> model plans -> calls tools -> observes results -> answers with citations.
Write tools never run with confirm=true unless the caller passes approve_writes=True
(i.e. the user clicked Approve in the UI)."""
from __future__ import annotations
import json, os, re, time
from dataclasses import dataclass, field
from datetime import date

from .guardrails import MEDICAL_NOTE, needs_medical_referral, redact
from .tools import TOOL_SCHEMAS, WRITE_TOOLS, Toolbox

MODEL = os.environ.get("PORTAL_MODEL", "claude-sonnet-5-5")
SYSTEM = """You are the coach inside The 11/11 Portal for Wellness, a personal life and Hyrox-style training tracker.
Today is {today}. Rules:
- Ground every claim about the user's history in tool results and cite the result id in square brackets, e.g. [run:2026-11-10].
- If the tools return nothing relevant, say so; never invent entries.
- Write tools (log_run, check_in_area, save_life_statement) must be called WITHOUT confirm first. Show the preview and ask the user to approve.
- Life coaching: teach one step at a time with life_coach_step (learn, premise, vision, purpose, strategy, commit). Ask that step's prompts, let the user answer in their own words, then offer to save each statement. Never write statements for the user without their approval. If they don't pick an area, use suggest_life_area.
- You give general fitness guidance, not medical advice. Refer pain, injury or dizziness to a doctor.
- Be brief and practical."""


@dataclass
class Trace:
    steps: list[dict] = field(default_factory=list)
    input_tokens: int = 0
    output_tokens: int = 0
    latency_s: float = 0.0


class Coach:
    def __init__(self, box: Toolbox | None = None, client=None, max_steps: int = 6):
        self.box = box or Toolbox()
        self.max_steps = max_steps
        if client is None:
            import anthropic  # optional dependency
            client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY
        self.client = client

    def _run_tool(self, name: str, args: dict, approve_writes: bool) -> dict | list:
        if name in WRITE_TOOLS and not approve_writes:
            args = {**args, "confirm": False}  # hard guardrail: the model cannot self-approve
        fn = getattr(self.box, name, None)
        if fn is None:
            return {"error": f"unknown tool {name}"}
        try:
            return fn(**args)
        except (TypeError, ValueError) as e:
            return {"error": str(e)}

    def ask(self, message: str, approve_writes: bool = False, history: list | None = None) -> tuple[str, Trace]:
        trace, t0 = Trace(), time.time()
        if needs_medical_referral(message):
            trace.steps.append({"guardrail": "medical_referral"})
            return MEDICAL_NOTE, trace
        msgs = list(history or []) + [{"role": "user", "content": redact(message)}]
        for _ in range(self.max_steps):
            resp = self.client.messages.create(model=MODEL, max_tokens=1024, tools=TOOL_SCHEMAS,
                                               system=SYSTEM.format(today=date.today().isoformat()), messages=msgs)
            u = getattr(resp, "usage", None)
            if u:
                trace.input_tokens += u.input_tokens; trace.output_tokens += u.output_tokens
            msgs.append({"role": "assistant", "content": resp.content})
            calls = [b for b in resp.content if b.type == "tool_use"]
            if not calls:
                text = "".join(b.text for b in resp.content if b.type == "text")
                trace.latency_s = round(time.time() - t0, 2)
                return text, trace
            results = []
            for c in calls:
                out = self._run_tool(c.name, dict(c.input), approve_writes)
                trace.steps.append({"tool": c.name, "args": c.input, "result_preview": json.dumps(out)[:200]})
                results.append({"type": "tool_result", "tool_use_id": c.id, "content": json.dumps(out)})
            msgs.append({"role": "user", "content": results})
        trace.latency_s = round(time.time() - t0, 2)
        return "I couldn't finish that within my step limit. Try a narrower question.", trace


def cited_ids(text: str) -> list[str]:
    return re.findall(r"\[([a-z_]+:[^\]\s]+)\]", text)

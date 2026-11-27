# Case Study: Portal 11

**An agent-ready, local-first life and training tracker, delivered with the PMI-CPMAI six-phase methodology**

Author: Fitsum Habtemariam · Started: 11 November 2026, 11:11 PM · License: MIT
Live app: https://ethioguy.github.io/portal-1111/ · Code: https://github.com/Ethioguy/portal-1111

---

## Summary

Portal 11 began as a personal tool: a 12-week, home-equipment training plan plus a daily check-in across 12 life areas. I then ran it as an AI project using the six CPMAI phases. The result adds four production-style AI pieces on top of the app:

1. An **MCP server** that lets any MCP client (Claude Desktop, Claude Code, IDEs) read the plan and journal, and log activity safely.
2. A **retrieval (RAG) pipeline** that grounds answers in the user's own entries and returns citable ids.
3. A **tool-using coach agent** with human-in-the-loop approval, guardrails and tracing.
4. An **eval harness** that runs in CI on every push.

| Result | Value |
|---|---|
| Retrieval recall@3 (golden set, 12 queries) | **0.92** (threshold 0.85) |
| Retrieval MRR | **0.88** (threshold 0.75) |
| Tool-contract, guardrail and MCP protocol checks | **17 / 17 pass** |
| Unit tests | **9 / 9 pass** |
| Data leaving the device for search | **None** (BM25 runs locally) |

Full, regenerated results: [`ai/evals/results.md`](../ai/evals/results.md).

---

## Phase 1 — Business Understanding

**Problem.** Training plans, journals and life goals live in separate places. People lose the thread between "what I planned", "what I did" and "why it matters".

**AI question.** Can an assistant answer questions about my own progress and log activity *without* inventing facts or changing data I didn't approve?

**Which AI pattern.** Conversational assistant + goal-driven system (an agent that uses tools). Not prediction, not recommendation from other users' data.

**Go / no-go criteria set before building:**
- Answers about history must cite a real entry (groundedness).
- No write without explicit user approval.
- Works with zero cloud dependency for search; a hosted model is optional.
- Retrieval recall@3 ≥ 0.85 on a labelled set.

**Is AI even needed?** Plan lookups and weekly totals are deterministic, so they are plain functions. AI is used only where language matters: understanding free-text questions and summarising the user's own notes.

## Phase 2 — Data Understanding

| Source | Shape | Notes |
|---|---|---|
| Daily records | date → run (miles, minutes, mode), workout done, habits, weight, notes | Sparse; notes are short free text |
| 12 life areas | Premise / Vision / Purpose / Strategy bullet lists, 1–10 rating, notes | Highly personal |
| Life vision | 13 short essays (home, ideal day, health, career, …) | Present-tense, personal |
| Tests | 1 km time, pull-ups, waist every 4 weeks | Small numeric series |

**Findings.** The corpus is small (tens to hundreds of entries), so a vector database would be over-engineering. Text is personal, so the default must keep it on the device. Some fields contain health data, so they need careful handling.

## Phase 3 — Data Preparation

- **One export format.** The web app's backup JSON is the single source of truth; the Python store reads and writes it atomically.
- **Document building.** Each run, note, life-area bullet, vision answer and test becomes a document with a stable id (`note:2026-11-11:0`, `area:fin:strategy:1`) so answers can cite it.
- **Chunking.** 80-word windows with 15-word overlap for long notes.
- **Normalisation.** Lower-casing, stop-word removal and light stemming.
- **Synthetic data for development and CI.** `sample_data/make_demo.py` generates two weeks of realistic but fictional data, so no personal data is ever committed.

## Phase 4 — Model Development

**Retrieval.** BM25 with query expansion (e.g. *money → financial, savings*), plus an optional embedding rerank hook for semantic matching. I chose BM25 first because it is explainable, free, fast, and runs offline.

**Agent.** Claude tool use with six typed tools. One tool layer serves three surfaces: the MCP server, the FastAPI API and the agent.

```
user ─► coach agent ──tool calls──► Toolbox ──► local JSON store
            ▲                         ▲
            │ MCP (stdio)             │ HTTP (FastAPI)
      Claude Desktop / IDE       web / mobile client
```

**Controls built into the design (not added afterwards):**
- Write tools return a **preview** unless `confirm=true`; the agent code forces `confirm=false` unless the human approved, so the model cannot approve itself.
- MCP tool **annotations** mark read-only vs write tools for the client.
- **Guardrails:** emails, phone numbers and ID numbers are redacted before text reaches a hosted model, and pain or injury questions get a referral to a doctor in place of a workout.
- **Step limit**, plus a **trace** of every tool call, token count and latency.
- **Audit log** of every tool call.

## Phase 5 — Model Evaluation

The evals are in `ai/evals/run_evals.py` and run in GitHub Actions on every push.

| Suite | What it proves |
|---|---|
| Retrieval | Recall@3 = 0.92, MRR = 0.88 on 12 hand-labelled queries |
| Tool contracts | Previews don't write; confirmed writes persist and are idempotent; bad input is rejected |
| Guardrails | Redaction works; normal soreness does **not** trigger a false medical referral |
| MCP protocol | A real stdio client lists the tools, gets cited search results and receives a preview for writes |
| Live agent (with API key) | Right tool chosen, every citation exists, no unapproved write, plus latency and tokens |

**Failure analysis (kept visible on purpose).** *"Why does fitness matter to me?"* misses at k=3. The user's Purpose entry says *"energy to lead and keep up with my kids"*, which shares no words with the question. This is the classic weakness of keyword search. **Next step:** turn on the embedding rerank and add a "why → purpose" expansion, then re-run the same golden set to show the change. Regressions are blocked by the CI thresholds.

## Phase 6 — Model Operationalization

**Multi-user without holding anyone's data.** Many people can use the hosted app, but each person's data lives only in their own browser. AI is "bring your own", split into two editions built from one source. The **public** edition offers only (1) copying a redacted summary into any assistant; its build step strips all AI-connection code, removes third-party fonts and adds a strict Content-Security-Policy, so the page cannot send data anywhere. The **personal** edition, kept off GitHub, adds (2) a personal Anthropic key so the browser calls Claude directly, using client-side tools (plan, journal search, week summary, run log). The model can only *propose* a write; the user taps Approve. This keeps the project outside the role of a health-data custodian, which would otherwise bring breach-notification duties (FTC Health Breach Notification Rule) and state consumer-health-data laws (e.g. Washington's My Health My Data Act) into scope.


- **Delivery.** The web app is on GitHub Pages and installable offline. The Python layer installs with `pip install -e ai`. The MCP server runs with one config block in Claude Desktop.
- **Cost and latency.** Search costs $0 and runs locally. The coach model is configurable (`PORTAL_MODEL`), so you can pick it on quality, latency and cost; token counts are traced per request.
- **Monitoring.** Traces and the audit log show which tools ran and why. The eval thresholds act as the regression gate.
- **Iteration.** Each CPMAI cycle is kept small: the next cycle adds embeddings, then streaming answers in the web app.

---

## Trustworthy AI

| Concern | How it's handled |
|---|---|
| Privacy | No project server or accounts; bring-your-own AI with user-chosen sharing; local-first storage; search never leaves the device; redaction before any hosted-model call; personal data and licensed materials are excluded by `.gitignore` |
| Human oversight | Two-step writes; the model cannot self-approve |
| Transparency | Answers cite entry ids; tool calls are traced and audit-logged |
| Safety | General fitness guidance only; pain or injury goes to a doctor |
| Accountability | Evals in CI; failures are documented, not hidden |

These map to the Govern, Map, Measure and Manage functions of the NIST AI Risk Management Framework.

---

## How this maps to the BLEN AI Engineer role

| Job requirement | Where it is in this repo |
|---|---|
| Design and build agentic systems with human-in-the-loop checkpoints | `ai/portal_ai/coach.py`, preview/confirm writes |
| Build MCP servers to expose data and tools securely and auditably | `ai/portal_ai/mcp_server.py`, tool annotations, audit log |
| Design and maintain RAG pipelines (chunking, retrieval, reranking, grounding) | `ai/portal_ai/rag.py`, cited ids |
| Integrate model APIs; choose the model on quality, latency and cost | `PORTAL_MODEL` setting, token and latency tracing |
| Develop evals and observability | `ai/evals/`, CI workflow, traces |
| Prompt engineering, structured outputs, tool calling, guardrails | Tool JSON schemas, system prompt rules, `guardrails.py` |
| Production Python backends and APIs | `ai/portal_ai/api.py` (FastAPI, validated inputs) |
| Responsible AI: privacy, security, auditability, human oversight | Trustworthy AI section above |
| Git, code review, modern workflows | GitHub repo, Actions CI, MIT license |
| Explain AI trade-offs to non-technical stakeholders | This case study (e.g. "Is AI even needed?", BM25 vs embeddings) |

---

*Built with AI pair-programming assistance (Claude). The life-area structure is inspired by common life-planning frameworks. The name comes from the "11/11 portal" fresh-start tradition.*

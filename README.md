# The 11/11 Portal

**A local-first life and training tracker with an agent-ready AI layer: an MCP server, RAG, a tool-using coach and CI evals.**

Started on 11.11.2026 at 11:11 PM, the "11/11 portal" fresh-start date. Delivered with the six-phase PMI-CPMAI methodology. Read the [case study](docs/CASE_STUDY.md).

[Open the app](https://ethioguy.github.io/portal-1111/) · [Case study](docs/CASE_STUDY.md) · [Eval results](ai/evals/results.md) · [AI layer](ai/README.md)

## What's inside

| Layer | Highlights |
|---|---|
| **Web app** (`index.html`) | 12-week home training plan, daily run log with pace, timers (supersets, EMOM, intervals, race stopwatch), 12 life areas with Premise / Vision / Purpose / Strategy pages and photos, progress charts. Installable, works offline, data stays in your browser |
| **Coach (bring your own AI)** | Public edition: copy a privacy-cleaned summary into any AI. Personal edition: the owner's own Claude key, called directly from the device with 4 client-side tools and approve-before-save writes. Nothing passes through a project server |
| **Guide** | A first-run guided tour, a Guide tab with how-to steps for every feature, and a 24/7 offline guide bot behind the ? button on every screen. It answers from built-in help, so nothing leaves the device |
| **MCP server** (`ai/portal_ai/mcp_server.py`) | 6 tools + 1 resource, read-only/write annotations, preview-then-confirm writes |
| **RAG** (`ai/portal_ai/rag.py`) | Chunking, BM25 + query expansion, optional embedding rerank, citable ids, runs offline |
| **Coach agent** (`ai/portal_ai/coach.py`) | Claude tool use, human-in-the-loop, guardrails, step limit, token/latency traces |
| **API** (`ai/portal_ai/api.py`) | FastAPI with validated inputs |
| **Evals** (`ai/evals/`) | Recall@3 0.92 · MRR 0.88 · 17/17 contract, guardrail and MCP checks, run in GitHub Actions |

## Two editions
| Edition | File | AI |
|---|---|---|
| **Public** (GitHub Pages) | `index.html` | Option 1: copy a redacted summary into any AI. Contains no AI-connection code, no outside requests, and a strict CSP |
| **Personal** (owner's device only, never committed) | `private/PERSONAL-portal.html` | Option 1 plus Option 2: your own Claude key, direct from your device, approve-before-save |

Both are built from `app.src.html` with `python tools/build_editions.py`. See [PRIVACY.md](PRIVACY.md).

## Run it
```bash
cd ai && pip install -e ".[dev,coach]"
pytest -q tests && python evals/run_evals.py
uvicorn portal_ai.api:app
```

## Privacy (local-first by design)
Sync between your own devices uses an end-to-end encrypted file (AES-256-GCM + PBKDF2) that you carry via iCloud Drive or AirDrop. No sync server.
There is no project server and no account. Each person's entries stay in their own browser; the AI runs on *their* terms: they pick what to share, contact details are redacted, keys are kept only if they choose, and every write needs their tap. Your entries stay on your device. Sample data is synthetic. Personal exports and any licensed course materials are excluded by `.gitignore`.

General fitness guidance, not medical advice. MIT License.

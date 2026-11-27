# portal-ai — the AI layer of Portal 11

Python package that turns the tracker into an agent-ready system.

| Component | File | What it does |
|---|---|---|
| Tool layer | `portal_ai/tools.py` | One set of typed tools shared by every surface; read tools are side-effect free, write tools preview first and only commit with `confirm=true`; every call is audit-logged |
| MCP server | `portal_ai/mcp_server.py` | Exposes 6 tools + 1 resource over the Model Context Protocol, with read-only / write annotations |
| RAG | `portal_ai/rag.py` | Builds documents from your entries, chunks them, BM25 retrieval with query expansion, optional embedding rerank; runs fully offline |
| Coach agent | `portal_ai/coach.py` | Claude tool-use loop: plan → call tools → observe → answer with citations; step limit, token/latency trace, model can't approve its own writes |
| Guardrails | `portal_ai/guardrails.py` | Redacts emails, phone and ID numbers before anything reaches a hosted model; refers pain/injury questions to a doctor |
| API | `portal_ai/api.py` | FastAPI: `/health`, `/plan/{day}`, `/search`, `/summary/{day}`, `/areas`, `/coach` |
| Evals | `evals/run_evals.py` | Retrieval recall@3 / MRR, tool contracts, guardrails, a real MCP stdio round trip, and live agent evals when a key is set |

## Quick start
```bash
cd ai
pip install -e ".[dev,coach]"
pytest -q tests                  # unit tests
python evals/run_evals.py        # writes evals/results.md
uvicorn portal_ai.api:app        # http://127.0.0.1:8000/docs
```

Your own data: in the web app open **Setup → Copy backup**, save it as JSON and point `PORTAL_DATA` at it. The demo data in `sample_data/` is synthetic.

## Use it from Claude Desktop (MCP)
Add to `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "the-11-11-portal": {
      "command": "python",
      "args": ["-m", "portal_ai.mcp_server"],
      "cwd": "/path/to/portal-1111/ai",
      "env": { "PORTAL_DATA": "/path/to/my-backup.json" }
    }
  }
}
```
Then ask: *"What did I write about my grip, and what's my workout tomorrow?"*

## Coach agent
```bash
export ANTHROPIC_API_KEY=...            # optional; everything else runs offline
export PORTAL_MODEL=claude-sonnet-5-5   # pick the model by quality, latency and cost
python -c "from portal_ai.coach import Coach; print(Coach().ask('How was my week?')[0])"
```

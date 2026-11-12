# Eval results

Data: synthetic demo set (54 indexed entries). Generated 2026-11-12.

## 1. Retrieval (BM25 + query expansion, offline)

| Metric | Score | Threshold |
|---|---|---|
| Recall@3 | 0.92 | 0.85 |
| MRR | 0.88 | 0.75 |

| Query | Hit | Rank |
|---|---|---|
| Why did my grip fail? | ✅ | 1 |
| How did the intervals go after a longer warm-up? | ✅ | 1 |
| race simulation time and transitions | ✅ | 1 |
| what did I meal prep | ✅ | 1 |
| When did I ride the bike instead of running? | ✅ | 1 |
| my money goals and savings plan | ✅ | 1 |
| What is my vision for my career? | ✅ | 1 |
| time with my kids | ✅ | 1 |
| Why does fitness matter to me? | ❌ | - |
| describe my ideal day | ✅ | 2 |
| 1 km test result and pull-ups | ✅ | 1 |
| sleep and low energy | ✅ | 1 |

## 2. Tool contracts & human-in-the-loop

| Check | Result |
|---|---|
| write without confirm only previews | ✅ pass |
| confirmed write persists and is idempotent | ✅ pass |
| rejects invalid input ('2026-12-01', -1, 20) | ✅ pass |
| rejects invalid input ('2026-12-01', 2, 0) | ✅ pass |
| rejects invalid input ('not-a-date', 2, 20) | ✅ pass |
| unknown life area rejected | ✅ pass |
| search results capped at 10 | ✅ pass |
| every tool call is audit-logged | ✅ pass |

## 3. Guardrails

| Check | Result |
|---|---|
| email redacted | ✅ pass |
| phone redacted | ✅ pass |
| SSN redacted | ✅ pass |
| ordinary text untouched | ✅ pass |
| chest pain triggers referral | ✅ pass |
| normal soreness does not | ✅ pass |

## 4. MCP protocol (stdio client ↔ server)

| Check | Result |
|---|---|
| server lists 6 tools over stdio | ✅ pass |
| search returns cited id over MCP | ✅ pass |
| write over MCP previews first | ✅ pass |

## 5. Live agent evals

Skipped: set `ANTHROPIC_API_KEY` to run the agent against Claude. The no-self-approval rule is also covered offline by `tests/test_core.py`.

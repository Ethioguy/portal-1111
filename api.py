"""FastAPI backend exposing the toolbox and coach to web/mobile clients.

Run:  uvicorn portal_ai.api:app --reload"""
from __future__ import annotations
import os
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from .tools import Toolbox

app = FastAPI(title="The 11/11 Portal for Wellness API", version="0.1.0")
box = Toolbox()


class CoachRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    approve_writes: bool = False


@app.get("/health")
def health() -> dict:
    return {"ok": True, "entries_indexed": len(box.index.docs)}


@app.get("/plan/{day}")
def get_plan(day: str) -> dict:
    try:
        return box.get_plan(day)
    except ValueError:
        raise HTTPException(422, "day must be YYYY-MM-DD")


@app.get("/search")
def search(q: str = Query(min_length=2, max_length=200), k: int = Query(5, ge=1, le=10)) -> list[dict]:
    return box.search_journal(q, k)


@app.get("/summary/{day}")
def summary(day: str) -> dict:
    return box.week_summary(day)


@app.get("/areas")
def areas() -> list[dict]:
    return box.life_area_status()


@app.post("/coach")
def coach(req: CoachRequest) -> dict:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise HTTPException(503, "Coach needs ANTHROPIC_API_KEY; all other endpoints work offline.")
    from .coach import Coach
    text, trace = Coach(box).ask(req.message, approve_writes=req.approve_writes)
    return {"answer": text, "trace": trace.__dict__}

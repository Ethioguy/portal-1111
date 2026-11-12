"""Retrieval over the user's own entries.

Pipeline: build documents -> chunk -> BM25 index -> retrieve -> rerank.
BM25 runs fully offline (no data leaves the device). An optional embedding
function can be passed in to rerank the BM25 shortlist semantically."""
from __future__ import annotations
import math, re
from collections import Counter
from dataclasses import dataclass, field
from typing import Callable, Iterable

from .store import AREAS, Store

_TOKEN = re.compile(r"[a-z0-9]+")
_STOP = set("a an the and or of to in on for with my i me is am are was be at it this that as by from your you we our".split())
_SYN = {"run": ["running", "miles", "jog"], "money": ["financial", "income", "savings", "invest"],
        "kids": ["children", "parenting", "family"], "job": ["career", "work"], "sleep": ["rest", "recovery"]}


def tokenize(text: str) -> list[str]:
    toks = [t for t in _TOKEN.findall(text.lower()) if t not in _STOP]
    return [t[:-1] if len(t) > 4 and t.endswith("s") else t for t in toks]  # light stemming


@dataclass
class Doc:
    id: str
    text: str
    source: str
    date: str | None = None
    area: str | None = None
    tokens: list[str] = field(default_factory=list)


def chunk(text: str, max_words: int = 80, overlap: int = 15) -> list[str]:
    words = text.split()
    if len(words) <= max_words:
        return [text]
    out, i = [], 0
    while i < len(words):
        out.append(" ".join(words[i:i + max_words]))
        i += max_words - overlap
    return out


def build_docs(store: Store) -> list[Doc]:
    docs: list[Doc] = []
    names = dict(AREAS)
    for d, day in sorted(store.data["days"].items()):
        run = day.get("run") or {}
        if run.get("done"):
            docs.append(Doc(f"run:{d}", f"{d} logged {run.get('mode','run')} {run.get('miles')} miles in {run.get('min')} minutes", "run", d))
        if day.get("notes"):
            for j, c in enumerate(chunk(day["notes"])):
                docs.append(Doc(f"note:{d}:{j}", f"{d} journal: {c}", "note", d))
        if day.get("weight"):
            docs.append(Doc(f"weight:{d}", f"{d} morning weight {day['weight']}", "weight", d))
    for area, v in store.areas().items():
        if area.startswith("_") or not isinstance(v, dict):
            continue
        for sec, items in (v.get("pv") or {}).items():
            for j, item in enumerate(i for i in items if i):
                docs.append(Doc(f"area:{area}:{sec}:{j}", f"{names.get(area, area)} {sec}: {item}", "life_area", area=area))
        if v.get("notes"):
            docs.append(Doc(f"area:{area}:notes", f"{names.get(area, area)} notes: {v['notes']}", "life_area", area=area))
    for key, text in (store.areas().get("_lv") or {}).items():
        if text:
            docs.append(Doc(f"vision:{key}", f"Life vision ({key}): {text}", "vision", area="vision"))
    for t in store.data["settings"].get("tests", []):
        docs.append(Doc(f"test:{t['date']}", f"{t['date']} test: 1 km {t.get('k1') or '-'}, pull-ups {t.get('pu') or '-'}, waist {t.get('wa') or '-'}", "test", t["date"]))
    for doc in docs:
        doc.tokens = tokenize(doc.text)
    return docs


class Index:
    def __init__(self, docs: Iterable[Doc], k1: float = 1.4, b: float = 0.75):
        self.docs = list(docs)
        self.k1, self.b = k1, b
        self.df = Counter(t for d in self.docs for t in set(d.tokens))
        self.avg = sum(len(d.tokens) for d in self.docs) / max(1, len(self.docs))
        self.tf = [Counter(d.tokens) for d in self.docs]

    def _bm25(self, q: list[str], i: int) -> float:
        n, s, dl = len(self.docs), 0.0, len(self.docs[i].tokens)
        for t in q:
            f = self.tf[i].get(t, 0)
            if not f:
                continue
            idf = math.log(1 + (n - self.df[t] + 0.5) / (self.df[t] + 0.5))
            s += idf * f * (self.k1 + 1) / (f + self.k1 * (1 - self.b + self.b * dl / self.avg))
        return s

    def search(self, query: str, k: int = 5, source: str | None = None, area: str | None = None,
               embed: Callable[[list[str]], list[list[float]]] | None = None) -> list[dict]:
        q = tokenize(query)
        q += [s for t in list(q) for s in _SYN.get(t, [])]  # query expansion
        scored = [(self._bm25(q, i), i) for i, d in enumerate(self.docs)
                  if (source is None or d.source == source) and (area is None or d.area == area)]
        short = [x for x in sorted(scored, reverse=True)[: max(k * 4, 10)] if x[0] > 0]
        if embed and short:  # optional semantic rerank of the shortlist
            vecs = embed([query] + [self.docs[i].text for _, i in short])
            qv = vecs[0]
            cos = lambda a, b: sum(x * y for x, y in zip(a, b)) / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)) or 1)
            short = sorted(((0.5 * s / short[0][0] + 0.5 * cos(qv, v), i) for (s, i), v in zip(short, vecs[1:])), reverse=True)
        return [{"id": self.docs[i].id, "text": self.docs[i].text, "source": self.docs[i].source,
                 "date": self.docs[i].date, "score": round(s, 3)} for s, i in short[:k]]

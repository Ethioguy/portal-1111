"""Local-first data store. Reads and writes the same JSON the web app exports from Setup > Copy backup."""
from __future__ import annotations
import json, os, tempfile
from datetime import date
from pathlib import Path

AREAS = [("health", "Health & Fitness"), ("intel", "Intellectual Life"), ("emo", "Emotional Life"), ("char", "Character"),
         ("spirit", "Spiritual Life"), ("love", "Love Relationship"), ("parent", "Parenting"), ("social", "Social Life"),
         ("fin", "Financial Life"), ("career", "Career"), ("qol", "Quality of Life"), ("vision", "Life Vision")]
AREA_IDS = {a for a, _ in AREAS}
DEFAULT_PATH = Path(__file__).resolve().parent.parent / "sample_data" / "demo_backup.json"


class Store:
    def __init__(self, path: str | os.PathLike | None = None):
        self.path = Path(path or os.environ.get("PORTAL_DATA", DEFAULT_PATH))
        self.data = json.loads(self.path.read_text()) if self.path.exists() else {"settings": {"start": date.today().isoformat()}, "days": {}}
        self.data.setdefault("days", {})
        self.data.setdefault("settings", {})

    # ---- reads ----
    @property
    def start(self) -> date:
        return date.fromisoformat(self.data["settings"].get("start", "2026-11-09"))

    def day(self, d: str) -> dict:
        return self.data["days"].get(d, {})

    def areas(self) -> dict:
        return self.data["settings"].get("life", {})

    # ---- writes (atomic) ----
    def _save(self) -> None:
        fd, tmp = tempfile.mkstemp(dir=self.path.parent, suffix=".json")
        with os.fdopen(fd, "w") as f:
            json.dump(self.data, f, indent=1)
        os.replace(tmp, self.path)

    def _ensure_day(self, d: str) -> dict:
        date.fromisoformat(d)  # validates format
        return self.data["days"].setdefault(d, {"run": {}, "ex": {}, "h": {}})

    def log_run(self, d: str, miles: float, minutes: float, mode: str = "run") -> dict:
        if not (0 < miles <= 30) or not (0 < minutes <= 300):
            raise ValueError("miles must be 0-30 and minutes 0-300")
        if mode not in ("run", "bike"):
            raise ValueError("mode must be 'run' or 'bike'")
        day = self._ensure_day(d)
        day["run"] = {"miles": str(miles), "min": str(minutes), "mode": mode, "done": True}
        self._save()
        return day["run"]

    def check_in(self, d: str, area: str) -> list[str]:
        if area not in AREA_IDS:
            raise ValueError(f"unknown life area '{area}'")
        day = self._ensure_day(d)
        day.setdefault("life", {})[area] = True
        self._save()
        return sorted(k for k, v in day["life"].items() if v)

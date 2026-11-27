"""Injects the step-by-step life coach content (ai/portal_ai/life_guide.py) into app.src.html as window.LCOACH.

The coaching content lives in Python so the web app, the MCP server and the coach agent share one source.
Usage: python tools/build_life_coach.py [app.src.html]"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "ai"))
from portal_ai.life_guide import export_for_web  # noqa: E402

src = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "app.src.html"
html = src.read_text()
block = "<script>window.LCOACH=" + json.dumps(export_for_web(), ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/") + ";</script>\n"
if "window.LCOACH=" in html:
    html = re.sub(r"<script>window\.LCOACH=.*?;</script>\n", lambda m: block, html, count=1, flags=re.S)
else:
    html = html.replace("<script>window.LB=", block + "<script>window.LB=", 1)
src.write_text(html)
print(f"Injected life coach: {len(export_for_web()['areas'])} areas, {len(block) // 1024} KB")

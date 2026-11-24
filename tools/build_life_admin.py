"""Injects the Inbox rules (ai/portal_ai/life_admin.py) into app.src.html as window.ADMIN.

Usage: python tools/build_life_admin.py [app.src.html]"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "ai"))
from portal_ai.life_admin import export_for_web  # noqa: E402

src = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "app.src.html"
html = src.read_text()
block = "<script>window.ADMIN=" + json.dumps(export_for_web(), ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/") + ";</script>\n"
if "window.ADMIN=" in html:
    html = re.sub(r"<script>window\.ADMIN=.*?;</script>\n", lambda m: block, html, count=1, flags=re.S)
else:
    html = html.replace("<script>window.LB=", block + "<script>window.LB=", 1)
src.write_text(html)
print(f"Injected Inbox rules: {len(export_for_web()['hats'])} areas")

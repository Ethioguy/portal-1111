"""Injects the visioning check-ins (ai/portal_ai/vision_review.py) into app.src.html as window.VREV.

Usage: python tools/build_vision_review.py [app.src.html]"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "ai"))
from portal_ai.vision_review import export_for_web  # noqa: E402

src = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "app.src.html"
html = src.read_text()
block = "<script>window.VREV=" + json.dumps(export_for_web(), ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/") + ";</script>\n"
if "window.VREV=" in html:
    html = re.sub(r"<script>window\.VREV=.*?;</script>\n", lambda m: block, html, count=1, flags=re.S)
else:
    html = html.replace("<script>window.LB=", block + "<script>window.LB=", 1)
src.write_text(html)
print(f"Injected visioning check-ins: {len(export_for_web()['order'])} cadences")

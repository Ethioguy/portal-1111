"""Injects the backup reminder policy (ai/portal_ai/backup.py) into app.src.html as window.BK."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "ai"))
from portal_ai.backup import export_for_web  # noqa: E402

block = ("<script>window.BK=" + json.dumps(export_for_web(), ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/") + ";</script>")
path = ROOT / "app.src.html"
html = path.read_text()
if "window.BK=" in html:
    import re
    html = re.sub(r"<script>window\.BK=.*?;</script>", block, html, count=1, flags=re.S)
else:
    html = html.replace("<script>window.LB=", block + "\n<script>window.LB=", 1)
path.write_text(html)
print(f"Injected backup policy: {len(export_for_web()['cadences'])} cadences, {len(block)//1024} KB")

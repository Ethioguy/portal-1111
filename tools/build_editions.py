"""Builds the two editions of Portal 11 from app.src.html.

public   -> index.html                        Option 1 only. No AI connection code, no third-party
                                              requests (system fonts), strict Content-Security-Policy.
personal -> private/PERSONAL-portal.html      Adds Option 2 (your own Claude key). Keep it off GitHub.

Usage: python tools/build_editions.py [--no-csp]   (--no-csp for hosts that inject their own runtime)"""
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
src = (ROOT / "app.src.html").read_text()
no_csp = "--no-csp" in sys.argv

def strip(html, tag):
    return re.sub(r"/\*@" + tag + r"\*/.*?/\*@/" + tag + r"\*/\n?", "", html, flags=re.S)

def unmark(html, tag):
    return html.replace("/*@" + tag + "*/\n", "").replace("/*@/" + tag + "*/\n", "").replace("/*@" + tag + "*/", "").replace("/*@/" + tag + "*/", "")

FONTS = re.compile(r'<link rel="preconnect" href="https://fonts.googleapis.com">\n?<link href="https://fonts.googleapis.com/css2[^"]*" rel="stylesheet">\n?')
CSP_PUBLIC = ("default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob: https://api.openverse.org; "
              "font-src 'self'; connect-src 'self' https://api.openverse.org; worker-src 'self'; manifest-src 'self'; media-src 'self' blob: https:; base-uri 'none'; form-action 'none'; object-src 'none'")
CSP_PERSONAL = ("default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
                "img-src 'self' data: blob: https://api.openverse.org; font-src https://fonts.gstatic.com; connect-src https://api.anthropic.com https://api.openverse.org; "
                "frame-src https://www.youtube-nocookie.com; media-src 'self' blob: https:; "
                "base-uri 'none'; form-action 'none'; object-src 'none'")

def head_extra(csp):
    tags = '<meta name="referrer" content="no-referrer">\n'
    if not no_csp:
        tags = f'<meta http-equiv="Content-Security-Policy" content="{csp}">\n' + tags
    return tags

def label(html, text):
    return html.replace('<section class="card"><h3>About</h3>', f'<section class="card"><h3>About</h3><p class="tiny" style="margin:4px 0 0">{text}</p>', 1)

base = strip(src, "CLOUD")

import sys as _sys
_sys.path.insert(0, str(ROOT))
import config as _cfg                      # the fork's own name, from config.py

def brandify(html):
    """Fill the {{BRAND_*}} tokens, then prove none are left in a shipped file."""
    b = _cfg.BRAND
    for token, value in (("{{BRAND_TITLE}}", b["full_title"]), ("{{BRAND_NAME}}", b["name"]),
                         ("{{BRAND_TAGLINE}}", b["tagline"]), ("{{BRAND_SINCE}}", b.get("since", "")),
                         ("{{BRAND_REPO}}", b.get("repo", ""))):
        html = html.replace(token, value.replace("&", "&amp;"))
    html = html.replace('content="#F4FAF2"', f'content="{b["theme"]}"')
    assert "{{BRAND_" not in html, "a brand token was left unfilled; add it to brandify()"
    return html

public = FONTS.sub("", strip(base, "P2"))
public = public.replace("<meta charset=\"utf-8\">\n", "<meta charset=\"utf-8\">\n" + head_extra(CSP_PUBLIC), 1)
public = brandify(public)
public = label(public, "Public edition. Your data never leaves this device.")
for banned in ("api.anthropic.com", "x-api-key", "fonts.googleapis.com", "claude.use(", "youtube-nocookie", "VIDS=", "/*@AMRITVELA@*/"):
    assert banned not in public, f"public edition must not contain {banned}"
_priv = ROOT / "private" / "amritvela.js"      # personal text: never let a line of it reach the public build
if _priv.exists():
    for line in (l.strip() for l in _priv.read_text().splitlines()):
        assert not (len(line) > 25 and line in public), "public edition must not contain personal session text"
(ROOT / "index.html").write_text(public)

personal = unmark(base, "P2")
_amv = ROOT / "private" / "amritvela.js"
if _amv.exists():                       # personal-only text, kept out of the shared source and out of GitHub
    personal = personal.replace("/*@AMRITVELA@*/", _amv.read_text())
else:
    print("note: private/amritvela.js not found; personal edition built without that session")
personal = personal.replace("<meta charset=\"utf-8\">\n", "<meta charset=\"utf-8\">\n" + head_extra(CSP_PERSONAL), 1)
personal = personal.replace("<title>Portal 11", "<title>[Personal] Portal 11", 1)
personal = brandify(personal)
personal = label(personal, "Personal edition. For your own device only; do not upload or share this file.")
(ROOT / "private").mkdir(exist_ok=True)
(ROOT / "private" / "PERSONAL-portal.html").write_text(personal)
print(f"public: {len(public)//1024} KB, no AI connection code | personal: {len(personal)//1024} KB")

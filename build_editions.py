"""Builds the two editions of The 11/11 Portal for Wellness from app.src.html.

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
              "font-src 'self'; connect-src 'self' https://api.openverse.org; worker-src 'self'; manifest-src 'self'; base-uri 'none'; form-action 'none'; object-src 'none'")
CSP_PERSONAL = ("default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
                "img-src 'self' data: blob: https://api.openverse.org; font-src https://fonts.gstatic.com; connect-src https://api.anthropic.com https://api.openverse.org; "
                "frame-src https://www.youtube-nocookie.com; "
                "base-uri 'none'; form-action 'none'; object-src 'none'")

def head_extra(csp):
    tags = '<meta name="referrer" content="no-referrer">\n'
    if not no_csp:
        tags = f'<meta http-equiv="Content-Security-Policy" content="{csp}">\n' + tags
    return tags

def label(html, text):
    return html.replace('<section class="card"><h3>About</h3>', f'<section class="card"><h3>About</h3><p class="tiny" style="margin:4px 0 0">{text}</p>', 1)

base = strip(src, "CLOUD")

public = FONTS.sub("", strip(base, "P2"))
public = public.replace("<meta charset=\"utf-8\">\n", "<meta charset=\"utf-8\">\n" + head_extra(CSP_PUBLIC), 1)
public = label(public, "Public edition. Your data never leaves this device.")
for banned in ("api.anthropic.com", "x-api-key", "fonts.googleapis.com", "claude.use(", "youtube-nocookie", "VIDS="):
    assert banned not in public, f"public edition must not contain {banned}"
(ROOT / "index.html").write_text(public)

personal = unmark(base, "P2")
personal = personal.replace("<meta charset=\"utf-8\">\n", "<meta charset=\"utf-8\">\n" + head_extra(CSP_PERSONAL), 1)
personal = personal.replace("<title>The 11/11 Portal for Wellness", "<title>[Personal] The 11/11 Portal for Wellness", 1)
personal = label(personal, "Personal edition. For your own device only; do not upload or share this file.")
(ROOT / "private").mkdir(exist_ok=True)
(ROOT / "private" / "PERSONAL-portal.html").write_text(personal)
print(f"public: {len(public)//1024} KB, no AI connection code | personal: {len(personal)//1024} KB")

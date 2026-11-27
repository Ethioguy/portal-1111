"""Builds the 'My Portal' life-area pages for Portal 11.
Generates category data, hexagon icons and banner art, then injects them into index.html."""
import json, math, re, sys

CATS = [
 ("health","Health & Fitness","M14 4.5a1.8 1.8 0 1 0 0 .01M8.5 21l2.5-5.5 3 2.5v4.5M11 15.5l1.2-5.2 3.3 2 3-1M12.2 10.3l-3.9.9-2.1 3"),
 ("intel","Intellectual Life","M9.5 18h5M10.5 21h3M12 3a6 6 0 0 0-3.8 10.6c.6.6.8 1.3.8 2.4h6c0-1.1.2-1.8.8-2.4A6 6 0 0 0 12 3z"),
 ("emo","Emotional Life","M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18zM8 14.5s1.5 2 4 2 4-2 4-2M9 9.5h.01M15 9.5h.01"),
 ("char","Character","M13 2 4.5 13.5H11L10 22l8.5-11.5H12z"),
 ("spirit","Spiritual Life","M12 20c-4 0-7-2-8.5-5.5 3.5 0 6 1.5 8.5 5.5zm0 0c4 0 7-2 8.5-5.5-3.5 0-6 1.5-8.5 5.5zm0 0c-2.3-3.2-2.3-7.8 0-12 2.3 4.2 2.3 8.8 0 12z"),
 ("love","Love Relationship","M12 20s-7.5-4.6-7.5-10.2A4.2 4.2 0 0 1 12 7.3a4.2 4.2 0 0 1 7.5 2.5C19.5 15.4 12 20 12 20z"),
 ("parent","Parenting","M8 7.5a2 2 0 1 0 0-.01M16 7.5a2 2 0 1 0 0-.01M5 21v-6.5a3 3 0 0 1 6 0V21M13 21v-6.5a3 3 0 0 1 6 0V21"),
 ("social","Social Life","M6 12a2.4 2.4 0 1 0 0-.01M18 6a2.4 2.4 0 1 0 0-.01M18 18a2.4 2.4 0 1 0 0-.01M8.2 10.9l7.6-3.8M8.2 13.1l7.6 3.8"),
 ("fin","Financial Life","M12 2.5v19M16.5 6.5H10a3.3 3.3 0 0 0 0 6.6h4a3.3 3.3 0 0 1 0 6.6H7"),
 ("career","Career","M4 20.5V11M10 20.5V5M16 20.5V13M2.5 20.5h19M19 9l2-2 2 2"),
 ("qol","Quality of Life","M3.5 11 12 3.5l8.5 7.5M5.5 9.5V20h13V9.5M10 20v-5.5h4V20"),
 ("vision","Life Vision","M2.5 12S6 5.5 12 5.5 21.5 12 21.5 12 18 18.5 12 18.5 2.5 12 2.5 12zM12 9a3 3 0 1 0 0 6 3 3 0 0 0 0-6z"),
]

# Short guidance written for this app
GUIDE = {
 "premise":  "The beliefs you hold about this area. Keep the ones that move you forward, and rewrite the ones that hold you back.",
 "vision":   "Your ideal picture of this area. How does it look and feel, and what are you doing in it day to day?",
 "purpose":  "Your reasons. Why does this area matter to you, and what will it make possible?",
 "strategy": "Your plan. The habits, actions and next steps that turn your vision into reality.",
}

DESCRIBE = [
 ("home","My dream home","Where do I live, what is my home like, and how does it feel to be there?"),
 ("day","My ideal day","How do I spend a great day from morning to night, and who is in it with me?"),
 ("health","My health & fitness","How strong, fit and energetic am I? How do I train, eat and recover?"),
 ("intel","My learning","What am I reading, studying and exploring? How am I growing my mind?"),
 ("emo","My everyday emotions","Which feelings fill most of my days, and what keeps them there?"),
 ("char","My character","Which traits have I turned into habits, and how have they changed my life?"),
 ("spirit","My spiritual practice","What do I do regularly that keeps me grounded and connected?"),
 ("love","My love relationship","What is our partnership like, and what have I done to build it?"),
 ("parent","My family life","What is life like with my children, and what am I proudest of as a parent?"),
 ("social","My friendships","Who are the people around me, and how do we lift each other up?"),
 ("fin","My financial life","What does financial freedom look like for me: income, savings and investments?"),
 ("career","My work","What am I leading or building, who with, and what impact am I having?"),
 ("qol","My lifestyle","What experiences, travel and adventures fill my life?"),
]

def hexagon(cx, cy, r):
    return " ".join(f"{cx + r*math.cos(math.radians(60*k-90)):.1f},{cy + r*math.sin(math.radians(60*k-90)):.1f}" for k in range(6))

def icon_svg(path, size=48, fill="#22a11e", stroke="#06210A"):
    return (f'<svg viewBox="0 0 48 52" width="{size}" height="{int(size*52/48)}" aria-hidden="true">'
            f'<polygon points="{hexagon(24,26,24)}" fill="{fill}"/>'
            f'<g transform="translate(12,14)" fill="none" stroke="{stroke}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="{path}"/></g></svg>')

def banner_svg(i, cid, name, path):
    hue = 98 + i * 4
    W, H = 640, 200
    waves = []
    for k in range(9):           # flowing light ribbons, generated mathematically
        amp = 18 + k * 4; y0 = 40 + k * 17; ph = k * 0.7 + i * 0.4
        pts = [f"{x},{y0 + amp*math.sin(x/95 + ph) + 10*math.sin(x/37 + ph*2):.1f}" for x in range(0, W+20, 20)]
        op = 0.05 + 0.025 * (k % 4)
        waves.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="#FFFFFF" stroke-opacity="{op:.3f}" stroke-width="{1.5+k%3}"/>')
    gid = f"g{cid}"
    return (f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{name}">'
            f'<defs><linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="1">'
            f'<stop offset="0" stop-color="hsl({hue} 70% 26%)"/><stop offset=".5" stop-color="#22a11e"/>'
            f'<stop offset="1" stop-color="#9FE38C"/></linearGradient></defs>'
            f'<rect width="{W}" height="{H}" fill="url(#{gid})"/>' + "".join(waves) +
            f'<g transform="translate(36,52)"><polygon points="{hexagon(42,48,46)}" fill="#22a11e" stroke="#FFFFFF" stroke-opacity=".35" stroke-width="2"/>'
            f'<g transform="translate(20,26) scale(1.85)" fill="none" stroke="#06210A" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="{path}"/></g></g>'
            f'<text x="148" y="92" fill="#E8F8E3" font-size="16" font-family="Sora,Inter,sans-serif" letter-spacing="2">CATEGORY {i+1}</text>'
            f'<text x="148" y="130" fill="#FFFFFF" font-size="36" font-weight="700" font-family="Sora,Inter,sans-serif">{name.replace("&","&amp;")}</text>'
            f'</svg>')

data = {
 "cats": [{"id": c, "name": n, "icon": icon_svg(p), "iconOff": icon_svg(p, fill="#E3EEE0", stroke="#55665A"),
           "banner": banner_svg(i, c, n, p)} for i, (c, n, p) in enumerate(CATS)],
 "guide": GUIDE,
 "describe": [{"key": k, "title": t, "prompt": q} for k, t, q in DESCRIBE],
}

src = sys.argv[1]
html = open(src).read()
block = "<script>window.LB=" + json.dumps(data, ensure_ascii=False).replace("</", "<\\/") + ";</script>"
html = re.sub(r"<script>window\.LB=.*?;</script>\n?", "", html, flags=re.S)
html = html.replace("<script>\n(function(){", block + "\n<script>\n(function(){", 1)
open(src, "w").write(html)
print(f"Injected {len(data['cats'])} categories, {len(data['describe'])} Life Vision prompts, {len(block)//1024} KB of art")

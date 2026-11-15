"""Draws original illustrations for every workout move (two frames + form cues) and injects
window.EXART into app.src.html. People vary in skin tone, hair, headwear and build, cycling
through a worldwide set so the app shows many kinds of people training.

Usage: python tools/build_exercise_art.py [--preview out.html]"""
import json, math, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GROUND = 182
# Body proportions follow the Drillis & Contini segment model (as tabulated in Winter, "Biomechanics and Motor
# Control of Human Movement"): with standing height H, knee height 0.285 H, hip 0.530 H, shoulder 0.818 H,
# chin 0.870 H, upper arm 0.186 H, forearm 0.146 H, hand 0.108 H. Here H = 150 drawing units.
# T = hip to base of neck (shoulder joint sits 4 below it), TH = thigh, SH = knee to floor,
# UA = upper arm, FA = elbow to the middle of the grip (forearm plus half a hand).
SEG = dict(T=47, TH=37, SH=43, UA=28, FA=30)
FOOT = 14                    # ankle to toe tip (foot length is 0.152 H; the heel is not drawn)
HEAD_D, HEAD_R = 14, 10.5   # neck base to head centre, head radius (drawn about 8% large so the smile reads)

SKIN = ["#F1C9A5", "#8D5524", "#E0AC69", "#3B2219", "#C68642", "#5C3A21", "#D9A07B", "#A86B3C"]
PEOPLE = [  # hair/headwear, top colour, bottom colour, build (limb width)
    dict(hair="short", top="#22a11e", bot="#10221A", w=10),
    dict(hair="bun", top="#157A12", bot="#2E2D2D", w=9),
    dict(hair="locs", top="#10221A", bot="#157A12", w=10),
    dict(hair="hijab", top="#157A12", bot="#10221A", w=9),
    dict(hair="afro", top="#22a11e", bot="#2E2D2D", w=11),
    dict(hair="bald", top="#10221A", bot="#22a11e", w=11),
    dict(hair="ponytail", top="#22a11e", bot="#10221A", w=9),
    dict(hair="wrap", top="#157A12", bot="#2E2D2D", w=10),
    dict(hair="turban", top="#10221A", bot="#157A12", w=10),
    dict(hair="curly", top="#22a11e", bot="#10221A", w=10),
]

def P(x, y): return (round(x), round(y))
def go(p, ang, L): a = math.radians(ang); return P(p[0] + L * math.cos(a), p[1] + L * math.sin(a))

def pose(t=-90, l1=(90, 90), l2=(90, 90), a1=(95, 95), a2=(95, 95), bend=0):
    """t: torso angle hip->neck. l=(thigh, shin) angles. a=(upper arm, forearm). 1 = near side, 2 = far side.
    bend: spine curve (+ rounds the back away from the face side)."""
    return dict(t=t, l1=l1, l2=l2, a1=a1, a2=a2, bend=bend, ft1=0, ft2=0)

def solve(ps, hip=(0, 0)):
    h = P(*hip); n = go(h, ps["t"], SEG["T"])
    k1 = go(h, ps["l1"][0], SEG["TH"]); f1 = go(k1, ps["l1"][1], SEG["SH"])
    k2 = go(h, ps["l2"][0], SEG["TH"]); f2 = go(k2, ps["l2"][1], SEG["SH"])
    sh = go(h, ps["t"], SEG["T"] - 4)
    e1 = go(sh, ps["a1"][0], SEG["UA"]); w1 = go(e1, ps["a1"][1], SEG["FA"])
    e2 = go(sh, ps["a2"][0], SEG["UA"]); w2 = go(e2, ps["a2"][1], SEG["FA"])
    hd = go(n, ps["t"], HEAD_D)
    # toes: the foot points to the face side, square to the shin when ft = 0; ft > 0 points the toes (plantarflexion)
    def toe(ankle, shin_ang, ft):
        d = math.radians(shin_ang - 90 + ft); return P(ankle[0] + FOOT * math.cos(d), ankle[1] + FOOT * math.sin(d))
    return dict(hip=h, neck=n, sh=sh, k1=k1, f1=f1, k2=k2, f2=f2, e1=e1, w1=w1, e2=e2, w2=w2, head=hd,
                t1=toe(f1, ps["l1"][1], ps.get("ft1", 0)), t2=toe(f2, ps["l2"][1], ps.get("ft2", 0)))

def place(pts, anchor, target, cx):
    """Shift so anchor point(s) sit on target y (max of anchors), and the figure is centred on cx."""
    names = anchor if isinstance(anchor, list) else [anchor]
    dy = target - max(pts[a][1] for a in names)
    xs = [p[0] for p in pts.values()]
    dx = cx - (min(xs) + max(xs)) / 2
    return {k: P(v[0] + dx, v[1] + dy) for k, v in pts.items()}

def line(a, b, c, w, op=1):
    return f'<line x1="{a[0]}" y1="{a[1]}" x2="{b[0]}" y2="{b[1]}" stroke="{c}" stroke-width="{w}" {"" if op == 1 else f" opacity=\"{op}\""}/>'

def poly(pts, c, w, op=1):
    d = " ".join(f"{p[0]},{p[1]}" for p in pts)
    return f'<polyline points="{d}" fill="none" stroke="{c}" stroke-width="{w}" {"" if op == 1 else f" opacity=\"{op}\""}/>'

def torso(p, ps, c, w):
    h, n = p["hip"], p["neck"]
    if not ps["bend"]:
        return line(h, n, c, w + 6)
    mx, my = (h[0] + n[0]) / 2, (h[1] + n[1]) / 2
    a = math.radians(ps["t"] - 90)  # away from face side
    cx, cy = mx + ps["bend"] * math.cos(a), my + ps["bend"] * math.sin(a)
    return f'<path d="M{h[0]},{h[1]} Q{round(cx,1)},{round(cy,1)} {n[0]},{n[1]}" fill="none" stroke="{c}" stroke-width="{w + 6}" stroke-linecap="round"/>'

def _path(pts, close=True):
    d = "M" + " L".join(f"{x:g},{y:g}" for x, y in pts)
    return d + (" Z" if close else "")

# Profile head in local units: +x towards the face, +y downwards; origin at the head's centre.
PROFILE = [(-7.5, -2), (-7, -7), (-3.5, -10.5), (1.5, -11), (5.5, -8.5), (7, -4.5), (7, -2.5), (9.6, 0.6), (9.2, 1.4),
           (7.2, 2.2), (7.6, 3.6), (7, 4.6), (7.2, 5.6), (6, 8.2), (3, 9.6), (0.5, 9.4), (-1, 12), (-5.5, 12), (-6.5, 7), (-8, 3)]
FRONT = [(-7.5, -3), (-6.5, -8), (-3, -10.8), (3, -10.8), (6.5, -8), (7.5, -3), (7, 3), (4.5, 8), (0, 10), (-4.5, 8), (-7, 3)]
HAIR = {
    "short": [(-7.8, -1), (-7.6, -7.4), (-3.6, -11.2), (1.8, -11.6), (6, -8.8), (6.6, -6.6), (2.5, -8), (-1, -7.4), (-3.6, -5), (-4.8, -1.5)],
    "bun": [(-7.8, -1), (-7.6, -7.4), (-3.6, -11.2), (1.8, -11.6), (6, -8.8), (6.4, -6.8), (1, -8.2), (-3, -6.2), (-5, -2)],
    "ponytail": [(-7.8, -1), (-7.6, -7.4), (-3.6, -11.2), (1.8, -11.6), (6, -8.8), (6.4, -6.8), (1, -8.2), (-3, -6.2), (-5, -2)],
    "locs": [(-8.2, 2), (-7.8, -7.6), (-3.6, -11.6), (1.8, -12), (6.2, -9), (6.6, -6.6), (1, -8.6), (-3, -6.6), (-4.6, 0)],
}

def head(p, ps, who, skin, front=False):
    hx, hy = p["head"]; t = math.radians(ps["t"])
    up = (math.cos(t), math.sin(t)); face = (-up[1], up[0])
    k = 1.08  # head scale
    m = f"matrix({face[0] * k:.3f},{face[1] * k:.3f},{-up[0] * k:.3f},{-up[1] * k:.3f},{hx},{hy})"
    kind = who["hair"]; ink = INK; back, top = [], []
    st = f'stroke="{ink}" stroke-width="1.7" stroke-linejoin="round" stroke-linecap="round"'
    if kind == "afro":
        back.append(f'<path d="M-9,4 C-15,-2 -12,-15 -2,-15.5 C8,-16 11,-9 8,-5 C5,-8 0,-8 -3,-5 C-5,-2 -5,2 -9,4 Z" fill="{ink}"/>')
    if kind == "curly":
        for cx, cy, r in ((-6, -8, 4.5), (-1, -11, 4.5), (4, -9.5, 4), (-8.5, -2.5, 3.6)):
            back.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{ink}"/>')
    if kind == "ponytail":
        back.append(f'<path d="M-6,-6 C-12,-4 -14,4 -12,12 C-10,6 -9,1 -5,-1 Z" fill="{ink}"/>')
    if kind == "bun":
        back.append(f'<circle cx="-7" cy="-9.5" r="4" fill="{ink}"/>')
    if kind == "locs":
        for x0 in (-7.5, -5.5, -3.5):
            back.append(f'<path d="M{x0},-4 C{x0 - 3},3 {x0 - 2},8 {x0 - 4},13" fill="none" stroke="{ink}" stroke-width="2.4" stroke-linecap="round"/>')
    shape = FRONT if front else PROFILE
    face_d = f'<path d="{_path(shape)}" fill="{skin}" {st}/>'
    if kind == "hijab":
        # scarf covers hair, ears and neck, leaving the face open
        cov = [(-9, 13), (-10, 0), (-8.5, -8), (-3.5, -12.6), (2.5, -12.8), (7.2, -9.4), (8.4, -5), (5.6, -6), (4.6, -2), (4.8, 4), (3.5, 8.6), (6, 12.5)]
        return f'<g transform="{m}">{face_d}<path d="{_path(cov)}" fill="#7E8C87" {st}/></g>'
    if kind in HAIR:
        top.append(f'<path d="{_path(HAIR[kind])}" fill="{ink}"/>')
    if kind == "turban":
        top.append(f'<path d="M-8,-3 C-10,-10 -5,-14.5 1,-14.5 C6,-14.5 8.5,-11 7.2,-6.2 C3,-8.6 -2,-8.4 -8,-3 Z" fill="#FFFFFF" {st}/>'
                   f'<path d="M-6.5,-9 C-2,-12 3,-12 6.5,-9.4" fill="none" stroke="{ink}" stroke-width="1.2"/>')
    if kind == "wrap":
        top.append(f'<path d="M-8.4,-1.5 C-11,-9 -6,-15 1,-14.6 C6.5,-14.2 8.6,-10 6.6,-6.4 C2,-8.6 -3,-7.6 -8.4,-1.5 Z" fill="#9AA6A2" {st}/>'
                   f'<path d="M-5,-12.5 C-3,-9.5 1,-9 4.5,-11.5" fill="none" stroke="{ink}" stroke-width="1.1"/>')
    if kind == "bald":
        top.append(f'<path d="M1.5,6.6 C3.6,8.4 6.4,7.4 7.1,4.8 L7.4,6.6 C6.6,9.6 2.4,10.4 0.6,8.6 Z" fill="{ink}"/>')
    feats = "" if front else (f'<path d="M3.6,-2.6 L5.6,-2.4" stroke="{ink}" stroke-width="1.4" stroke-linecap="round"/>'
                              f'<path d="M-2.4,-1 C-0.6,-2 0.4,0.6 -1.6,1.8" fill="none" stroke="{ink}" stroke-width="1.2" stroke-linecap="round"/>')
    if front:
        feats = (f'<path d="M-3.6,-1.5 L-1.8,-1.5 M1.8,-1.5 L3.6,-1.5 M0,0 L0.6,2.8 L-0.4,3 M-2,5.6 C-0.6,6.6 0.8,6.6 2,5.6" fill="none" '
                 f'stroke="{ink}" stroke-width="1.2" stroke-linecap="round"/>')
    return f'<g transform="{m}">{"".join(back)}{face_d}{"".join(top)}{feats}</g>'

INK = "#2B2B2B"
def gray(c):
    c = c.lstrip("#"); r, g, b = (int(c[i:i + 2], 16) for i in (0, 2, 4)); v = round((.3 * r + .59 * g + .11 * b) * .55 + 255 * .45)
    return "#%02X%02X%02X" % (v, v, v - 4)

def tint(c, k=.62):
    c = c.lstrip("#"); r, g, b = (int(c[i:i + 2], 16) for i in (0, 2, 4))
    return "#%02X%02X%02X" % tuple(round(v + (255 - v) * k) for v in (r, g, b))

WASH = ["#D5DCD9", "#C3CCC8", "#AEB9B5", "#99A6A1"]  # light to deep grey-green washes, varied per person

def _q(h, c, n, k=6):
    """Points along a quadratic curve (for a bent spine)."""
    return [P((1 - t) ** 2 * h[0] + 2 * (1 - t) * t * c[0] + t * t * n[0], (1 - t) ** 2 * h[1] + 2 * (1 - t) * t * c[1] + t * t * n[1]) for t in [i / k for i in range(k + 1)]]

def contour(pts, w, far=False, heavy=2.3, light=1.3):
    """Loose ink contour: two side strokes per segment, ends left open, one side heavier like a brush pen."""
    out = []; op = .55 if far else 1
    for a, b in zip(pts, pts[1:]):
        dx, dy = b[0] - a[0], b[1] - a[1]; L = math.hypot(dx, dy) or 1
        ux, uy = dx / L, dy / L; nx, ny = -uy * w / 2, ux * w / 2
        a2, b2 = (a[0] + ux * 2, a[1] + uy * 2), (b[0] - ux * 1.5, b[1] - uy * 1.5)
        out.append(line(P(a2[0] + nx, a2[1] + ny), P(b2[0] + nx, b2[1] + ny), INK, heavy, op))
        out.append(line(P(a2[0] - nx, a2[1] - ny), P(b2[0] - nx, b2[1] - ny), INK, light, op))
    return "".join(out)

def _n(a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]; L = math.hypot(dx, dy) or 1
    return dx / L, dy / L, -dy / L, dx / L  # unit along, unit normal

def _pts(pp): return " ".join(f"{round(x)},{round(y)}" for x, y in pp)

def brush(a, b, wmax, shift=0.0, op=1.0):
    """Tapered brush-pen stroke from a to b (a thin lens shape), optionally pushed sideways."""
    ux, uy, nx, ny = _n(a, b)
    a, b = (a[0] + nx * shift, a[1] + ny * shift), (b[0] + nx * shift, b[1] + ny * shift)
    m1 = (a[0] + (b[0] - a[0]) * .35, a[1] + (b[1] - a[1]) * .35); m2 = (a[0] + (b[0] - a[0]) * .7, a[1] + (b[1] - a[1]) * .7)
    h = wmax / 2
    pts = [a, (m1[0] + nx * h, m1[1] + ny * h), (m2[0] + nx * h * .8, m2[1] + ny * h * .8), b, (m2[0] - nx * h * .8, m2[1] - ny * h * .8), (m1[0] - nx * h, m1[1] - ny * h)]
    return f'<polygon points="{_pts(pts)}" fill="{INK}"{"" if op == 1 else f" opacity=\"{op}\""}/>'

def seg_shape(a, b, wa, wb):
    """Tapered limb segment as a filled quad, plus round joints."""
    ux, uy, nx, ny = _n(a, b)
    q = [(a[0] + nx * wa / 2, a[1] + ny * wa / 2), (b[0] + nx * wb / 2, b[1] + ny * wb / 2), (b[0] - nx * wb / 2, b[1] - ny * wb / 2), (a[0] - nx * wa / 2, a[1] - ny * wa / 2)]
    return q

def silhouette_limb(pts, widths, fill, op=1.0):
    out = []
    for (a, b), (wa, wb) in zip(zip(pts, pts[1:]), zip(widths, widths[1:])):
        out.append(f'<polygon points="{_pts(seg_shape(a, b, wa, wb))}" fill="{fill}"/>')
    for pt, w in zip(pts, widths):
        out.append(f'<circle cx="{round(pt[0])}" cy="{round(pt[1])}" r="{round(w / 2, 1)}" fill="{fill}"/>')
    g = "".join(out)
    return g if op == 1 else f'<g opacity="{op}">{g}</g>'

def outline_limb(pts, widths, side, op=1.0, heavy=2.6):
    """Contour on both sides; the lit side is a full brush line, the other side broken and lighter."""
    out = []
    for k, ((a, b), (wa, wb)) in enumerate(zip(zip(pts, pts[1:]), zip(widths, widths[1:]))):
        ux, uy, nx, ny = _n(a, b); w = (wa + wb) / 4 + .6
        a1, b1 = (a[0] + ux * 1.5, a[1] + uy * 1.5), (b[0] - ux * 1.5, b[1] - uy * 1.5)
        out.append(brush(a1, b1, heavy, side * w, op))
        mid = (a1[0] + (b1[0] - a1[0]) * .55, a1[1] + (b1[1] - a1[1]) * .55)
        out.append(brush(a1 if k % 2 else mid, mid if k % 2 else b1, heavy * .6, -side * w, op))
    return "".join(out)

def figure(p, ps, who, skin, front=False):
    bw = who["w"] / 10
    wash = WASH[SKIN.index(skin) % len(WASH)] if skin in SKIN else WASH[1]
    t = math.radians(ps["t"]); up = (math.cos(t), math.sin(t)); face = (-up[1], up[0])
    # spine samples with widths: hips, waist, chest, shoulders, neck
    h, n = p["hip"], p["neck"]
    if ps["bend"]:
        a = math.radians(ps["t"] - 90); c = ((h[0] + n[0]) / 2 + ps["bend"] * math.cos(a), (h[1] + n[1]) / 2 + ps["bend"] * math.sin(a))
        spine = _q(h, c, n, 4)
    else:
        spine = [P(h[0] + (n[0] - h[0]) * f, h[1] + (n[1] - h[1]) * f) for f in (0, .3, .62, .86, 1)]
    tw = [x * bw for x in (19, 15, 20, 19, 7)]
    def foot(knee, ankle):
        sx, sy = ankle[0] - knee[0], ankle[1] - knee[1]; L = math.hypot(sx, sy) or 1; sx, sy = sx / L, sy / L
        c1, c2 = (-sy, sx), (sy, -sx); d = c1 if c1[0] * face[0] + c1[1] * face[1] > 0 else c2
        return P(ankle[0] + d[0] * 11 * bw, ankle[1] + d[1] * 11 * bw)
    legs = {k: ([p["hip"], p["k" + k], p["f" + k], foot(p["k" + k], p["f" + k])], [x * bw for x in (14, 10, 6.5, 3.5)]) for k in ("1", "2")}
    arms = {k: ([p["sh"], p["e" + k], p["w" + k]], [x * bw for x in (8, 6.5, 5)]) for k in ("1", "2")}
    g = []
    # far side first, then torso, then near side: wash silhouettes with brush contours
    for part, side, op in ((arms["2"], 1, .75), (legs["2"], 1, .75)):
        g.append(silhouette_limb(part[0], part[1], wash, op)); g.append(outline_limb(part[0], part[1], side, .7, 2.2))
    g.append(silhouette_limb(spine, tw, wash)); g.append(outline_limb(spine, tw, -1))
    for part, side in ((legs["1"], 1), (arms["1"], -1)):
        g.append(silhouette_limb(part[0], part[1], wash)); g.append(outline_limb(part[0], part[1], side))
    hd = head(p, ps, who, wash, front)
    hd = hd.replace(f'fill="{wash}"/>', f'fill="{wash}" stroke="{INK}" stroke-width="2"/>')
    g.insert(len(g) - 2, hd)
    xs = [v[0] for v in p.values()]; base = max(v[1] for v in p.values())
    if base > GROUND - 8:
        x0, x1 = min(xs) - 14, max(xs) + 18
        g.insert(0, f'<path d="M{round(x0)},{GROUND + 6} L{round(x1)},{GROUND + 1} L{round(x1) + 8},{GROUND + 7} L{round(x0) + 6},{GROUND + 11} Z" fill="{WASH[1]}" opacity=".9"/>')
    return "".join(g)

# ---------- clean line figure: one even outline, white body, no face detail, no black fills, no shadows ----------
LINE = "#2B2B2B"; FAR = "#DDE4E1"; HAIRW = ["#B4BFBB", "#C9D1CE", "#A3AFAB"]; GHOST = "#E3E9E6"

def limb(pts, w, c):
    d = " ".join(f"{x},{y}" for x, y in pts)
    return f'<polyline points="{d}" fill="none" stroke="{c}" stroke-width="{round(w, 1)}" stroke-linecap="round" stroke-linejoin="round"/>'

def outlined(shapes, fill, mono=None, o=1.6):
    """Draw shapes as one merged silhouette: an ink pass slightly wider, then the fill pass on top."""
    if mono:
        return "".join(limb(pts, w, mono) for pts, w in shapes)
    return "".join(limb(pts, w + 2 * o, LINE) for pts, w in shapes) + "".join(limb(pts, w, fill) for pts, w in shapes)

def simple_head(p, ps, who, front, idx=0, mono=None):
    hx, hy = p["head"]; t = math.radians(ps["t"])
    up = (math.cos(t), math.sin(t)); face = (-up[1], up[0]); k = 1.05
    m = f"matrix({face[0] * k:.3f},{face[1] * k:.3f},{-up[0] * k:.3f},{-up[1] * k:.3f},{hx},{hy})"
    d = _path(FRONT if front else PROFILE)
    if mono:
        return f'<g transform="{m}"><path d="{d}" fill="{mono}"/></g>'
    hw = HAIRW[idx % len(HAIRW)]; kind = who["hair"]; st = f'stroke="{LINE}" stroke-width="1.3" stroke-linejoin="round"'
    back, top = [], []
    def two(shape_fmt):  # merged outline for overlapping hair pieces
        return shape_fmt.format(a=f'fill="{LINE}" stroke="{LINE}" stroke-width="2.6"') + shape_fmt.format(a=f'fill="{hw}"')
    if kind == "afro": back.append(f'<path d="M-9,4 C-15,-2 -12,-15 -2,-15.5 C8,-16 11,-9 8,-5 C5,-8 0,-8 -3,-5 C-5,-2 -5,2 -9,4 Z" fill="{hw}" {st}/>')
    if kind == "curly":
        cs = ((-6, -8, 4.5), (-1, -11, 4.5), (4, -9.5, 4), (-8.5, -2.5, 3.6))
        back.append("".join(f'<circle cx="{x}" cy="{y}" r="{r + 1.3}" fill="{LINE}"/>' for x, y, r in cs) + "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{hw}"/>' for x, y, r in cs))
    if kind == "ponytail": back.append(f'<path d="M-6,-6 C-12,-4 -14,4 -12,12 C-10,6 -9,1 -5,-1 Z" fill="{hw}" {st}/>')
    if kind == "bun": back.append(f'<circle cx="-7" cy="-9.5" r="4" fill="{hw}" {st}/>')
    if kind == "locs":
        back += [f'<path d="M{x0},-4 C{x0 - 3},3 {x0 - 2},8 {x0 - 4},13" fill="none" stroke="#8C9995" stroke-width="2.4" stroke-linecap="round"/>' for x0 in (-7.5, -5.5, -3.5)]
    face_d = f'<path d="{d}" fill="#FFFFFF" {st}/>'
    if kind == "hijab":
        cov = [(-9, 13), (-10, 0), (-8.5, -8), (-3.5, -12.6), (2.5, -12.8), (7.2, -9.4), (8.4, -5), (5.6, -6), (4.6, -2), (4.8, 4), (3.5, 8.6), (6, 12.5)]
        return f'<g transform="{m}">{face_d}<path d="{_path(cov)}" fill="{hw}" {st}/></g>'
    if kind in HAIR: top.append(f'<path d="{_path(HAIR[kind])}" fill="{hw}" {st}/>')
    if kind == "turban": top.append(f'<path d="M-8,-3 C-10,-10 -5,-14.5 1,-14.5 C6,-14.5 8.5,-11 7.2,-6.2 C3,-8.6 -2,-8.4 -8,-3 Z" fill="#FFFFFF" {st}/>')
    if kind == "wrap": top.append(f'<path d="M-8.4,-1.5 C-11,-9 -6,-15 1,-14.6 C6.5,-14.2 8.6,-10 6.6,-6.4 C2,-8.6 -3,-7.6 -8.4,-1.5 Z" fill="{hw}" {st}/>')
    return f'<g transform="{m}">{"".join(back)}{face_d}{"".join(top)}</g>'

def figure_flat(p, ps, who, skin, front=False, shirt=None, mono=None, idx=0):
    bw = who["w"] / 10
    t = math.radians(ps["t"]); up = (math.cos(t), math.sin(t)); face = (-up[1], up[0])
    h, n = p["hip"], p["neck"]
    if ps["bend"]:
        a = math.radians(ps["t"] - 90); c = ((h[0] + n[0]) / 2 + ps["bend"] * math.cos(a), (h[1] + n[1]) / 2 + ps["bend"] * math.sin(a))
        spine = _q(h, c, n, 4)
    else:
        spine = [h, n]
    def foot(knee, ankle):
        sx, sy = ankle[0] - knee[0], ankle[1] - knee[1]; L = math.hypot(sx, sy) or 1; sx, sy = sx / L, sy / L
        c1, c2 = (-sy, sx), (sy, -sx); d = c1 if c1[0] * face[0] + c1[1] * face[1] > 0 else c2
        return P(ankle[0] + d[0] * 9, ankle[1] + d[1] * 9)
    def leg(k): return [([p["hip"], p["k" + k]], 11.5 * bw), ([p["k" + k], p["f" + k]], 9 * bw), ([p["f" + k], foot(p["k" + k], p["f" + k])], 5)]
    def arm(k): return [([p["sh"], p["e" + k]], 7 * bw), ([p["e" + k], p["w" + k]], 6 * bw)]
    body = [(spine, 16 * bw), ([n, p["head"]], 5.5)] + leg("1")
    return (outlined(arm("2"), FAR, mono) + outlined(leg("2"), FAR, mono) + outlined(body, "#FFFFFF", mono)
            + simple_head(p, ps, who, front, idx, mono) + outlined(arm("1"), "#FFFFFF", mono))

def motion_arrow(a, b, c="#E8590C"):
    dx, dy = b[0] - a[0], b[1] - a[1]; L = math.hypot(dx, dy) or 1; ux, uy = dx / L, dy / L
    a2, b2 = (a[0] + ux * 7, a[1] + uy * 7), (b[0] - ux * 9, b[1] - uy * 9)
    cx, cy = (a2[0] + b2[0]) / 2 - uy * L * .18, (a2[1] + b2[1]) / 2 + ux * L * .18
    ang = math.atan2(b2[1] - cy, b2[0] - cx)
    h1 = (b2[0] - 8 * math.cos(ang - .45), b2[1] - 8 * math.sin(ang - .45)); h2 = (b2[0] - 8 * math.cos(ang + .45), b2[1] - 8 * math.sin(ang + .45))
    return (f'<path d="M{a2[0]:.0f},{a2[1]:.0f} Q{cx:.0f},{cy:.0f} {b2[0]:.0f},{b2[1]:.0f}" fill="none" stroke="{c}" stroke-width="2.6" stroke-linecap="round" stroke-dasharray="5 4"/>'
            f'<path d="M{h1[0]:.0f},{h1[1]:.0f} L{b2[0]:.0f},{b2[1]:.0f} L{h2[0]:.0f},{h2[1]:.0f}" fill="none" stroke="{c}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>')

# ---------- props: equipment in bold brand green so it stands out from the grey figures ----------
GR = "#1A7F17"; EQ = "#1A7F17"; EQD = "#0E4F0C"; BAND = "#22a11e"; EQL = "#BFE8B5"
def db(c, ang=0):
    a = math.radians(ang); dx, dy = 13 * math.cos(a), 13 * math.sin(a)
    p1, p2 = P(c[0] - dx, c[1] - dy), P(c[0] + dx, c[1] + dy)
    px, py = -math.sin(a) * 9, math.cos(a) * 9
    def plate(q):
        return (line(P(q[0] - px, q[1] - py), P(q[0] + px, q[1] + py), EQD, 11) + line(P(q[0] - px * .78, q[1] - py * .78), P(q[0] + px * .78, q[1] + py * .78), "#5DBB4E", 6.5))
    return "<g data-front=\"1\">" + line(p1, p2, EQD, 4.5) + plate(p1) + plate(p2) + "</g>"
def bar(x0, x1, y):
    return (line((x0, y + 4), (x0, GROUND + 1), EQ, 4.5) + line((x1, y + 4), (x1, GROUND + 1), EQ, 4.5)
            + line((x0 - 7, GROUND + 1), (x0 + 7, GROUND + 1), EQD, 5) + line((x1 - 7, GROUND + 1), (x1 + 7, GROUND + 1), EQD, 5)
            + line((x0 - 5, y), (x1 + 5, y), EQD, 8) + line((x0 - 5, y), (x1 + 5, y), "#5DBB4E", 4))
def box(x, w, h):
    return (f'<rect x="{x}" y="{GROUND - h}" width="{w}" height="{h}" rx="3" fill="{EQL}" stroke="{EQD}" stroke-width="3"/>'
            + "".join(line((x + k, GROUND - 3), (x + k + 9, GROUND - h + 4), EQ, 1.3, .7) for k in range(5, int(w) - 8, 8)))
def mat(x0, x1): return f'<rect x="{x0}" y="{GROUND + 2.5}" width="{x1 - x0}" height="5" rx="2.5" fill="{EQL}" stroke="{EQD}" stroke-width="2"/>'
def band(a, b): return line(a, b, EQD, 6.5) + line(a, b, "#5DBB4E", 3.5)
def wall(x):
    return (f'<rect x="{x}" y="10" width="10" height="{GROUND - 10}" fill="none" stroke="#2B2B2B" stroke-width="2"/>'
            + "".join(line((x, y), (x + 10, y - 8), "#8A8A8A", 1) for y in range(24, GROUND, 14)))
def climber(top, foot):
    """Vertical climber: tall rail, handles at the top, pedals near the bottom, wide base."""
    tx, bx = top[0] + 14, foot[0] + 28
    return (line((tx, 14), (bx, GROUND), EQD, 10) + line((tx, 14), (bx, GROUND), "#5DBB4E", 5.5)
            + line((tx - 13, 22), (tx + 5, 22), EQD, 6) + line((bx - 24, GROUND - 22), (bx - 4, GROUND - 22), EQD, 6)
            + line((bx - 42, GROUND), (bx + 36, GROUND), EQD, 8) + line((bx - 42, GROUND), (bx + 36, GROUND), "#5DBB4E", 4))
def arrow(a, b):
    ang = math.atan2(b[1] - a[1], b[0] - a[0]); h1 = P(b[0] - 8 * math.cos(ang - .5), b[1] - 8 * math.sin(ang - .5)); h2 = P(b[0] - 8 * math.cos(ang + .5), b[1] - 8 * math.sin(ang + .5))
    return line(a, b, "#2B2B2B", 2) + poly([h1, b, h2], "#2B2B2B", 2)

# ---------- the moves ----------
STAND = pose()
def M(key, cues, frames, labels=("Start", "Finish")):
    return dict(key=key, cues=cues, frames=frames, labels=labels)

def F(ps, anchor="f1", target=GROUND, props=None, front=False, hip=(0, 0)):
    return dict(ps=ps, anchor=anchor, target=target, props=props, front=front)

SQ_ARMS = dict(a1=(100, -50), a2=(95, -45))
MOVES = [
 M("goblet-squat", ["Hold one dumbbell upright at your chest, elbows tucked.", "Sit hips back and down between your heels; chest stays tall.", "Knees track over toes. Drive up through the whole foot."],
   [F(pose(**SQ_ARMS), props=lambda p: db(p["w1"], 90)),
    F(pose(t=-62, l1=(12, 104), l2=(18, 108), a1=(110, -40), a2=(105, -35)), anchor=["f1", "f2"], props=lambda p: db(p["w1"], 90))]),
 M("hanging-knee-raise", ["Hang with straight arms and shoulders pulled down.", "Curl your knees up toward your chest without swinging.", "Lower slowly, control the whole way."],
   [F(pose(a1=(-80, -84), a2=(-100, -96)), anchor="w1", target=22, props=lambda p: bar(p["w1"][0] - 50, p["w1"][0] + 50, p["w1"][1])),
    F(pose(t=-95, l1=(-15, 95), l2=(-8, 100), a1=(-80, -84), a2=(-100, -96)), anchor="w1", target=22, props=lambda p: bar(p["w1"][0] - 50, p["w1"][0] + 50, p["w1"][1]))]),
 M("bulgarian-split-squat", ["Back foot laces-down on a step or couch.", "Drop the back knee straight down; front shin stays fairly upright.", "Push through the front heel to stand."],
   [F(pose(t=-88, l1=(80, 92), l2=(118, 192), a1=(92, 90), a2=(88, 90)), props=lambda p: box(p["f2"][0] - 26, 32, GROUND - p["f2"][1] - 2.5) + db(p["w1"], 90)),
    F(pose(t=-82, l1=(10, 96), l2=(100, 205), a1=(92, 90), a2=(88, 90)), props=lambda p: box(p["f2"][0] - 26, 32, GROUND - p["f2"][1] - 2.5) + db(p["w1"], 90))]),
 M("plank", ["Forearms under shoulders, body in one straight line.", "Squeeze glutes and brace like someone may poke your belly.", "Breathe slowly. Stop before your hips sag."],
   [F(pose(t=-4, l1=(176, 178), l2=(178, 180), a1=(92, 2), a2=(90, 0)), anchor=["f1", "w1"], props=lambda p: mat(p["f1"][0] - 10, p["w1"][0] + 10)),
    F(pose(t=-14, l1=(170, 210), l2=(172, 205), a1=(92, 2), a2=(90, 0)), anchor=["k1", "w1"], props=lambda p: mat(p["f1"][0] - 10, p["w1"][0] + 10))], ("Hold", "Easier: knees down")),
 M("romanian-deadlift", ["Soft knees, dumbbells close to your legs.", "Push hips back until you feel the hamstrings; back stays flat.", "Stand tall by driving hips forward."],
   [F(pose(a1=(90, 90), a2=(88, 88)), props=lambda p: db(p["w1"])),
    F(pose(t=-18, l1=(98, 84), l2=(96, 82), a1=(88, 88), a2=(86, 86)), anchor=["f1", "f2"], props=lambda p: db(p["w1"]))]),
 M("glute-bridge", ["Band just above your knees; feet flat, hip-width.", "Press knees out against the band and lift hips.", "Pause at the top, ribs down, then lower."],
   [F(pose(t=180, l1=(-50, 75), l2=(-46, 78), a1=(2, 0), a2=(0, 0)), anchor=["neck", "f1"], props=lambda p: mat(p["head"][0] - 14, p["f1"][0] + 12) + f'<ellipse cx="{p["k1"][0]}" cy="{p["k1"][1]+2}" rx="6" ry="10" fill="none" stroke="{BAND}" stroke-width="4.5"/>'),
    F(pose(t=160, l1=(-12, 92), l2=(-8, 94), a1=(25, 0), a2=(22, 0)), anchor=["f1", "neck"], props=lambda p: mat(p["head"][0] - 14, p["f1"][0] + 12) + f'<ellipse cx="{p["k1"][0]}" cy="{p["k1"][1]+2}" rx="6" ry="10" fill="none" stroke="{BAND}" stroke-width="4.5"/>')]),
 M("walking-lunge", ["Long step forward, torso tall.", "Lower until the back knee nearly touches the floor.", "Push off the front foot into the next step."],
   [F(pose(l1=(80, 92), l2=(100, 92), a1=(95, 95), a2=(85, 85))),
    F(pose(t=-88, l1=(8, 94), l2=(112, 170), a1=(100, 90), a2=(80, 90)), anchor=["f1"])]),
 M("db-walking-lunge", ["Hold dumbbells at your sides, shoulders back.", "Long step, back knee toward the floor.", "Stay tall; don't let the weights pull you forward."],
   [F(pose(l1=(80, 92), l2=(100, 92), a1=(90, 90), a2=(88, 88)), props=lambda p: db(p["w1"])),
    F(pose(t=-88, l1=(8, 94), l2=(112, 170), a1=(90, 90), a2=(88, 88)), props=lambda p: db(p["w1"]))]),
 M("pull-up", ["Hands just wider than shoulders; start from a dead hang.", "Pull elbows down toward your ribs until chin clears the bar.", "Use a band under your knee if you need help."],
   [F(pose(l1=(95, 115), l2=(92, 112), a1=(-100, -95), a2=(-80, -85)), anchor="w1", target=22, props=lambda p: bar(p["w1"][0] - 55, p["w1"][0] + 55, p["w1"][1])),
    F(pose(l1=(95, 120), l2=(92, 118), a1=(120, -75), a2=(60, -105)), anchor="w1", target=22, props=lambda p: bar(p["w1"][0] - 55, p["w1"][0] + 55, p["w1"][1]))]),
 M("push-up", ["Hands under shoulders, body straight from head to heels.", "Lower your chest to a fist's height from the floor, elbows about 45°.", "Press away; elevate hands on a couch to make it easier."],
   [F(pose(t=-14, l1=(172, 176), l2=(174, 178), a1=(88, 90), a2=(90, 92)), anchor=["f1", "w1"], props=lambda p: mat(p["f1"][0] - 10, p["w1"][0] + 14)),
    F(pose(t=-3, l1=(178, 179), l2=(179, 180), a1=(200, 62), a2=(202, 64)), anchor=["f1", "w1"], props=lambda p: mat(p["f1"][0] - 10, p["w1"][0] + 14))]),
 M("db-row", ["Hinge forward with a flat back; free hand on your front knee.", "Row the dumbbell toward your hip, elbow close.", "Lower with control; don't twist."],
   [F(pose(t=-30, l1=(45, 100), l2=(118, 108), a1=(90, 90), a2=(70, 55)), anchor=["f1", "f2"], props=lambda p: db(p["w1"])),
    F(pose(t=-30, l1=(45, 100), l2=(118, 108), a1=(150, 80), a2=(70, 55)), anchor=["f1", "f2"], props=lambda p: db(p["w1"]))]),
 M("overhead-press", ["Dumbbells at shoulder height, ribs down.", "Press straight up until arms are locked overhead.", "Don't lean back; squeeze glutes."],
   [F(pose(a1=(55, -85), a2=(50, -82)), props=lambda p: db(p["w1"])),
    F(pose(a1=(-92, -92), a2=(-88, -88)), props=lambda p: db(p["w1"]))]),
 M("face-pull", ["Band anchored at head height; arms straight to start.", "Pull toward your face, elbows high and wide.", "Squeeze shoulder blades, then return slowly."],
   [F(pose(a1=(-5, -5), a2=(-3, -3)), props=lambda p: band(p["w1"], (p["w1"][0] + 40, p["w1"][1])) + wall(p["w1"][0] + 40)),
    F(pose(a1=(-170, -20), a2=(-165, -15)), props=lambda p: band(p["w1"], (p["w1"][0] + 80, p["w1"][1])) + wall(p["w1"][0] + 80))]),
 M("dead-hang", ["Grip the bar, arms straight, feet off the floor.", "Relax, then gently pull shoulders away from your ears.", "Breathe; build up the time week by week."],
   [F(pose(a1=(-92, -92), a2=(-88, -88)), anchor="w1", target=22, props=lambda p: bar(p["w1"][0] - 50, p["w1"][0] + 50, p["w1"][1])),
    F(pose(l1=(80, 100), l2=(84, 104), a1=(-92, -92), a2=(-88, -88)), anchor="w1", target=22, props=lambda p: bar(p["w1"][0] - 50, p["w1"][0] + 50, p["w1"][1]))], ("Hold", "Active shoulders")),
 M("hollow-hold", ["Low back pressed into the floor.", "Arms overhead, legs long and low, shoulders lifted.", "Bend knees or bring arms in to make it easier."],
   [F(pose(t=192, l1=(-12, -10), l2=(-10, -8), a1=(196, 196), a2=(194, 194)), anchor="hip", props=lambda p: mat(p["w1"][0] - 8, p["f1"][0] + 8)),
    F(pose(t=192, l1=(-60, 30), l2=(-58, 32), a1=(-30, 40), a2=(-28, 40)), anchor="hip", props=lambda p: mat(p["head"][0] - 14, p["f1"][0] + 10))], ("Hold", "Easier: tuck")),
 M("side-plank", ["Elbow under shoulder, body in a straight line.", "Lift hips; don't let them sag toward the floor.", "Drop the bottom knee to make it easier."],
   [F(pose(t=-20, l1=(162, 162), l2=(164, 164), a1=(92, -2), a2=(-92, -92)), anchor=["f1", "w1"], props=lambda p: mat(p["f1"][0] - 10, p["w1"][0] + 10)),
    F(pose(t=-32, l1=(155, 215), l2=(157, 215), a1=(92, -2), a2=(-92, -92)), anchor=["k1", "w1"], props=lambda p: mat(p["f1"][0] - 10, p["w1"][0] + 10))], ("Hold", "Easier: knees")),
 M("thruster", ["Dumbbells at shoulders; squat down with chest up.", "Drive up and use that power to press overhead.", "Lower the weights back to shoulders as you squat again."],
   [F(pose(t=-62, l1=(12, 104), l2=(18, 108), a1=(55, -85), a2=(50, -82)), anchor=["f1", "f2"], props=lambda p: db(p["w1"])),
    F(pose(a1=(-92, -92), a2=(-88, -88)), props=lambda p: db(p["w1"]))]),
 M("band-pull-apart", ["Hold the band at chest height, arms straight.", "Pull it apart until it touches your chest.", "Squeeze shoulder blades; return slowly."],
   [F(pose(l1=(84, 88), l2=(96, 92), a1=(25, 160), a2=(155, 20)), front=True, props=lambda p: band(p["w1"], p["w2"])),
    F(pose(l1=(84, 88), l2=(96, 92), a1=(-4, -4), a2=(184, 184)), front=True, props=lambda p: band(p["w1"], p["w2"]))]),
 M("renegade-row", ["High plank on dumbbells, feet wide.", "Row one dumbbell to your ribs without rotating your hips.", "Place it down softly and switch sides."],
   [F(pose(t=-14, l1=(170, 176), l2=(176, 178), a1=(88, 90), a2=(90, 92)), anchor=["f1", "w1"], props=lambda p: db(p["w1"]) + db(p["w2"])),
    F(pose(t=-14, l1=(170, 176), l2=(176, 178), a1=(-175, 92), a2=(90, 92)), anchor=["f1", "w2"], props=lambda p: db(p["w1"]) + db(p["w2"]))]),
 M("pallof-press", ["Band anchored to your side at chest height.", "Press hands straight out from your chest.", "Resist the band twisting you; hold 2 seconds, return."],
   [F(pose(a1=(100, -40), a2=(95, -38)), props=lambda p: band(p["w1"], (p["w1"][0] - 90, p["w1"][1] - 2)) + wall(p["w1"][0] - 100)),
    F(pose(a1=(-2, -2), a2=(0, 0)), props=lambda p: band(p["w1"], (p["w1"][0] - 130, p["w1"][1])) + wall(p["w1"][0] - 140))]),
 M("step-up", ["Whole foot on a sturdy step or bench.", "Drive through that heel to stand tall on top.", "Step down under control; switch legs."],
   [F(pose(l1=(-5, 92), l2=(95, 90), a1=(90, 90), a2=(88, 88)), anchor="f2", props=lambda p: box(p["f1"][0] - 22, 56, GROUND - p["f1"][1] - 2.5) + db(p["w1"])),
    F(pose(l1=(90, 90), l2=(-20, 90), a1=(90, 90), a2=(88, 88)), anchor="f1", target=GROUND - 42, props=lambda p: box(p["f1"][0] - 26, 56, 39.5) + db(p["w1"]))]),
 M("hanging-leg-raise", ["Hang with shoulders active, no swinging.", "Lift legs (or knees) to hip height or higher.", "Lower slowly."],
   [F(pose(t=-95, l1=(-15, 95), l2=(-8, 100), a1=(-80, -84), a2=(-100, -96)), anchor="w1", target=22, props=lambda p: bar(p["w1"][0] - 50, p["w1"][0] + 50, p["w1"][1])),
    F(pose(t=-100, l1=(-8, -6), l2=(-4, -2), a1=(-80, -84), a2=(-100, -96)), anchor="w1", target=22, props=lambda p: bar(p["w1"][0] - 50, p["w1"][0] + 50, p["w1"][1]))], ("Knees", "Straight legs")),
 M("warm-up", ["Easy jog in place or on the Maxi Climber for 3 minutes.", "Then arm circles, leg swings and a few bodyweight squats.", "Finish slightly warm, not tired."],
   [F(pose(t=-85, l1=(40, 110), l2=(120, 150), a1=(60, -60), a2=(140, 100)), anchor="f2"),
    F(pose(a1=(-60, -40), a2=(-120, -140)))], ("Jog", "Arm circles")),
 M("dead-bug", ["On your back, arms to the ceiling, knees bent at 90°.", "Lower the opposite arm and leg toward the floor, low back stays down.", "Return and switch sides."],
   [F(pose(t=180, l1=(-90, 0), l2=(-92, 2), a1=(-90, -90), a2=(-92, -92)), anchor=["hip"], props=lambda p: mat(p["head"][0] - 14, p["f1"][0] + 12)),
    F(pose(t=180, l1=(-12, -6), l2=(-92, 2), a1=(-90, -90), a2=(192, 190)), anchor=["hip"], props=lambda p: mat(p["w2"][0] - 8, p["f1"][0] + 12))]),
 M("mountain-climber", ["High plank, hands under shoulders.", "Drive one knee toward your chest, then switch quickly.", "Keep hips low and steady."],
   [F(pose(t=-16, l1=(40, 125), l2=(172, 178), a1=(88, 90), a2=(90, 92)), anchor=["f2", "w1"], props=lambda p: mat(p["f2"][0] - 10, p["w1"][0] + 12)),
    F(pose(t=-16, l1=(172, 178), l2=(40, 125), a1=(88, 90), a2=(90, 92)), anchor=["f1", "w1"], props=lambda p: mat(p["f1"][0] - 10, p["w1"][0] + 12))]),
 M("maxi-climber", ["Hold the handles, feet in the pedals, body upright.", "Push opposite arm and leg (right hand with left foot).", "Short fast strokes for cardio, long strokes for strength."],
   [F(pose(t=-80, l1=(30, 100), l2=(95, 90), a1=(-75, -80), a2=(-60, -10)), anchor="f2", props=lambda p: climber(p["w1"], p["f2"])),
    F(pose(t=-80, l1=(95, 90), l2=(30, 100), a1=(-60, -10), a2=(-75, -80)), anchor="f1", props=lambda p: climber(p["w2"], p["f1"]))]),
 M("band-row-walkback", ["Band anchored low in front of you.", "Row hands to your waist, lean back slightly.", "Take small steps back while keeping tension, like a sled pull."],
   [F(pose(t=-95, l1=(80, 95), l2=(110, 90), a1=(10, 10), a2=(12, 12)), anchor=["f1", "f2"], props=lambda p: band(p["w1"], (p["w1"][0] + 60, GROUND - 20)) + wall(p["w1"][0] + 60)),
    F(pose(t=-102, l1=(70, 100), l2=(120, 95), a1=(150, -10), a2=(152, -8)), anchor=["f1", "f2"], props=lambda p: band(p["w1"], (p["w1"][0] + 90, GROUND - 20)) + wall(p["w1"][0] + 90) + arrow((p["hip"][0] - 10, GROUND - 6), (p["hip"][0] - 40, GROUND - 6)))]),
 M("burpee-broad-jump", ["Hands down, jump feet back, chest and thighs touch the floor.", "Push up, bring feet in, stand.", "Jump forward with both feet; land soft and repeat."],
   [F(pose(t=-6, l1=(179, 181), l2=(180, 182), a1=(200, 60), a2=(202, 62)), anchor=["f1", "w1"], props=lambda p: mat(p["f1"][0] - 10, p["head"][0] + 14)),
    F(pose(t=-60, l1=(150, 60), l2=(155, 65), a1=(-30, -25), a2=(-35, -30)), anchor="f1", target=GROUND - 30, props=lambda p: arrow((p["hip"][0] - 60, GROUND - 2), (p["hip"][0] + 40, GROUND - 2)))], ("Chest down", "Jump forward")),
 M("farmers-carry", ["Heavy dumbbells at your sides, shoulders back and down.", "Walk tall with short, quick steps.", "Grip hard; don't let the weights swing."],
   [F(pose(l1=(70, 100), l2=(108, 95), a1=(90, 90), a2=(88, 88)), anchor=["f1", "f2"], props=lambda p: db(p["w1"]) + db(p["w2"])),
    F(pose(l1=(108, 95), l2=(70, 100), a1=(90, 90), a2=(88, 88)), anchor=["f1", "f2"], props=lambda p: db(p["w1"]) + db(p["w2"]))], ("Step", "Step")),
 M("cat-cow", ["On hands and knees, hands under shoulders.", "Cat: round your back up and tuck your chin.", "Cow: drop your belly, lift chest and tailbone. Move with your breath."],
   [F(pose(t=0, l1=(90, 180), l2=(92, 182), a1=(90, 90), a2=(92, 92), bend=16), anchor=["k1", "w1"], props=lambda p: mat(p["f1"][0] - 30, p["w1"][0] + 12)),
    F(pose(t=-4, l1=(90, 180), l2=(92, 182), a1=(90, 90), a2=(92, 92), bend=-20), anchor=["k1", "w1"], props=lambda p: mat(p["f1"][0] - 30, p["w1"][0] + 12))], ("Cat", "Cow")),
 M("hip-flexor-stretch", ["Half-kneel, back knee on a cushion.", "Squeeze the back-side glute and tuck your pelvis.", "Shift forward gently; reach the same-side arm up."],
   [F(pose(l1=(0, 90), l2=(95, 180), a1=(100, 30), a2=(95, 30)), anchor=["f1"], props=lambda p: mat(p["f2"][0] - 12, p["f1"][0] + 12)),
    F(pose(t=-95, l1=(-8, 98), l2=(105, 182), a1=(-100, -100), a2=(95, 30)), anchor=["f1"], props=lambda p: mat(p["f2"][0] - 12, p["f1"][0] + 12))], ("Set up", "Shift and reach")),
 M("calf-stretch", ["Hands on a wall, back leg straight, heel down.", "Lean in until you feel the calf; hold.", "Bend the back knee slightly to stretch lower down."],
   [F(pose(t=-60, l1=(70, 92), l2=(122, 122), a1=(-25, -10), a2=(-22, -8)), anchor=["f1", "f2"], props=lambda p: wall(p["w1"][0] + 2)),
    F(pose(t=-60, l1=(70, 92), l2=(115, 100), a1=(-25, -10), a2=(-22, -8)), anchor=["f1", "f2"], props=lambda p: wall(p["w1"][0] + 2))], ("Straight knee", "Bent knee")),
 M("doorway-chest-stretch", ["Forearm on the door frame, elbow at shoulder height.", "Step through with the same-side foot.", "Turn chest away gently until you feel a stretch; hold."],
   [F(pose(a1=(180, -90), a2=(95, 95)), props=lambda p: line((p["e1"][0] - 6, 18), (p["e1"][0] - 6, GROUND), "#8A8A8A", 3)),
    F(pose(t=-80, l1=(75, 95), l2=(105, 92), a1=(185, -95), a2=(95, 95)), anchor=["f1", "f2"], props=lambda p: line((p["e1"][0] - 6, 18), (p["e1"][0] - 6, GROUND), "#8A8A8A", 3))]),
 M("childs-pose", ["Kneel, sit hips back toward your heels.", "Walk hands forward and rest your forehead down.", "Then on all fours, reach one arm under and then up to the ceiling."],
   [F(pose(t=24, l1=(40, 180), l2=(42, 182), a1=(10, 0), a2=(12, 2)), anchor=["k1", "f1", "w1"], props=lambda p: mat(p["f1"][0] - 10, p["w1"][0] + 10)),
    F(pose(t=0, l1=(90, 180), l2=(92, 182), a1=(-90, -90), a2=(92, 92)), anchor=["k1", "w2"], props=lambda p: mat(p["f1"][0] - 30, p["w2"][0] + 12))], ("Child's pose", "Rotation")),
 # ---- warm-up (moving) and cool-down (held) stretches ----
 M("arm-circles", ["Stand tall, arms out to the sides at shoulder height.", "Draw small circles, growing bigger, for 30 seconds.", "Reverse direction for another 30 seconds."],
   [F(pose(a1=(-5, -5), a2=(-8, -8))), F(pose(a1=(-80, -80), a2=(-100, -100)), props=lambda p: arrow((p["w1"][0] + 18, p["w1"][1] + 30), (p["w1"][0] + 8, p["w1"][1] + 2)))], ("Arms out", "Big circles")),
 M("leg-swing", ["Hold a wall for balance, stand tall on one leg.", "Swing the other leg forward and back, letting the range grow.", "Keep your trunk still; switch legs after 10."],
   [F(pose(l2=(-25, -15), a1=(-10, -5), a2=(-12, -8)), anchor="f1", props=lambda p: wall(p["w1"][0] + 2)), F(pose(l2=(145, 135), a1=(-10, -5), a2=(-12, -8)), anchor="f1", props=lambda p: wall(p["w1"][0] + 2))], ("Swing forward", "Swing back")),
 M("hip-circles", ["Hands on hips, feet hip-width apart.", "Draw big slow circles with your hips.", "10 one way, then 10 the other way."],
   [F(pose(t=-78, l1=(84, 92), l2=(96, 90), a1=(120, 30), a2=(115, 28))), F(pose(t=-102, l1=(84, 92), l2=(96, 90), a1=(120, 30), a2=(115, 28)))], ("Hips one way", "Then the other")),
 M("knee-hug", ["Step forward and pull one knee to your chest.", "Rise onto the toes of the standing foot.", "Release, step and switch legs."],
   [F(pose(l1=(80, 92), l2=(100, 92), a1=(95, 95), a2=(85, 85))), F(pose(l1=(-45, 90), a1=(40, -20), a2=(45, -15)), anchor="f2")], ("Step", "Hug the knee")),
 M("inchworm", ["Fold forward and put your hands on the floor (bend your knees if you need to).", "Walk your hands out to a high plank.", "Walk the hands back and stand up slowly."],
   [F(pose(t=68, l1=(92, 90), l2=(94, 92), a1=(95, 95), a2=(93, 93)), anchor=["f1", "w1"], props=lambda p: mat(p["f1"][0] - 14, p["w1"][0] + 20)),
    F(pose(t=-14, l1=(172, 176), l2=(174, 178), a1=(88, 90), a2=(90, 92)), anchor=["f1", "w1"], props=lambda p: mat(p["f1"][0] - 10, p["w1"][0] + 14))], ("Fold", "Walk out to plank")),
 M("worlds-greatest-stretch", ["Step into a long lunge, back knee lifted.", "Put the same-side hand on the floor inside your front foot.", "Rotate and reach the other arm to the ceiling; switch sides."],
   [F(pose(t=-35, l1=(5, 92), l2=(160, 175), a1=(95, 92), a2=(100, 95)), anchor=["f1", "w1"], props=lambda p: mat(p["f2"][0] - 10, p["f1"][0] + 14)),
    F(pose(t=-35, l1=(5, 92), l2=(160, 175), a1=(95, 92), a2=(-95, -95)), anchor=["f1", "w1"], props=lambda p: mat(p["f2"][0] - 10, p["f1"][0] + 14))], ("Lunge, hand down", "Rotate, reach up")),
 M("quad-stretch", ["Stand tall and hold a wall for balance.", "Bend one knee and hold the ankle behind you.", "Knees together, hips gently forward; hold 30 seconds."],
   [F(pose(a2=(-10, -5)), anchor="f2", props=lambda p: wall(p["w2"][0] + 2)),
    F(pose(t=-92, l1=(98, -115), a1=(125, 72), a2=(-10, -5)), anchor="f2", props=lambda p: wall(p["w2"][0] + 2))], ("Stand tall", "Hold the ankle, hips forward")),
 M("hamstring-stretch", ["Sit with one leg straight, the other foot against the inner thigh.", "Sit tall first, then hinge forward from the hips.", "Reach toward your foot until you feel the stretch; hold."],
   [F(pose(t=-82, l1=(0, 0), l2=(4, 176), a1=(70, 40), a2=(72, 42)), anchor=["hip", "f1"], props=lambda p: mat(p["hip"][0] - 24, p["f1"][0] + 12)),
    F(pose(t=-32, l1=(0, 0), l2=(4, 176), a1=(18, 8), a2=(20, 10)), anchor=["hip", "f1"], props=lambda p: mat(p["hip"][0] - 24, p["f1"][0] + 12))], ("Sit tall", "Hinge forward")),
 M("figure-four", ["Lie on your back, cross one ankle over the other knee.", "Lift the bottom leg and hold behind that thigh.", "Pull gently toward your chest; hold 30 seconds each side."],
   [F(pose(t=180, l1=(-30, 5), l2=(-50, 75), a1=(2, 0), a2=(0, 0)), anchor=["neck", "f2"], props=lambda p: mat(p["head"][0] - 14, p["f2"][0] + 12)),
    F(pose(t=180, l1=(-60, 10), l2=(-85, -10), a1=(-40, 5), a2=(-38, 8)), anchor=["neck", "hip"], props=lambda p: mat(p["head"][0] - 14, p["f2"][0] + 30))], ("Cross the ankle", "Pull in")),
]

EQUIP = {"goblet-squat": "1 dumbbell", "hanging-knee-raise": "Pull-up bar", "bulgarian-split-squat": "2 dumbbells, a step or couch",
 "plank": "Mat", "romanian-deadlift": "2 dumbbells", "glute-bridge": "Mini band or resistance band, mat", "walking-lunge": "Bodyweight",
 "db-walking-lunge": "2 dumbbells", "pull-up": "Pull-up bar, band for assistance", "push-up": "Mat", "db-row": "1 dumbbell",
 "overhead-press": "2 dumbbells", "face-pull": "Resistance band, door anchor", "dead-hang": "Pull-up bar", "hollow-hold": "Mat",
 "side-plank": "Mat", "thruster": "2 dumbbells", "band-pull-apart": "Resistance band", "renegade-row": "2 dumbbells, mat",
 "pallof-press": "Resistance band, door anchor", "step-up": "2 dumbbells, a sturdy step or bench", "hanging-leg-raise": "Pull-up bar",
 "warm-up": "Bodyweight or Maxi Climber", "dead-bug": "Mat", "mountain-climber": "Mat", "maxi-climber": "Maxi Climber",
 "band-row-walkback": "Resistance band, low anchor", "burpee-broad-jump": "Open floor space", "farmers-carry": "2 dumbbells (heaviest)",
 "cat-cow": "Mat", "hip-flexor-stretch": "Mat or cushion", "calf-stretch": "Wall", "doorway-chest-stretch": "Doorway", "childs-pose": "Mat", "arm-circles": "Bodyweight", "leg-swing": "Wall for balance", "hip-circles": "Bodyweight", "knee-hug": "Bodyweight", "inchworm": "Mat", "worlds-greatest-stretch": "Mat", "quad-stretch": "Wall for balance", "hamstring-stretch": "Mat", "figure-four": "Mat"}

NAMES = {  # exercise names in the plan -> drawing key
 "Goblet squat": "goblet-squat", "Hanging knee raise": "hanging-knee-raise", "Bulgarian split squat": "bulgarian-split-squat",
 "Plank": "plank", "DB Romanian deadlift": "romanian-deadlift", "Band glute bridge": "glute-bridge", "Walking lunges": "walking-lunge",
 "Pull-ups (band-assisted if needed)": "pull-up", "Push-ups": "push-up", "1-arm DB row": "db-row", "DB overhead press": "overhead-press",
 "Band face pulls": "face-pull", "Dead hang": "dead-hang", "Hollow hold": "hollow-hold", "Side plank": "side-plank", "DB thrusters": "thruster",
 "Band pull-aparts": "band-pull-apart", "Renegade rows": "renegade-row", "Pallof press": "pallof-press", "DB step-ups": "step-up",
 "Hanging leg or knee raise": "hanging-leg-raise", "Warm-up": "warm-up", "dead bugs": "dead-bug", "mountain climbers": "mountain-climber",
 "Maxi Climber": "maxi-climber", "Walk-back band rows": "band-row-walkback", "Burpee broad jumps": "burpee-broad-jump",
 "DB walking lunges": "db-walking-lunge", "Farmers carry": "farmers-carry", "Cat-cow": "cat-cow", "Hip-flexor stretch": "hip-flexor-stretch",
 "Calf stretch": "calf-stretch", "Child's pose": "childs-pose", "Arm circles": "arm-circles", "Leg swings": "leg-swing", "Hip circles": "hip-circles", "Walking knee hugs": "knee-hug", "Inchworms": "inchworm", "World's greatest stretch": "worlds-greatest-stretch", "Standing quad stretch": "quad-stretch", "Hamstring stretch": "hamstring-stretch", "Figure-4 glute stretch": "figure-four", "Doorway chest stretch": "doorway-chest-stretch", "Child's pose + thoracic rotations": "childs-pose",
}

# ---------- animated line figure (original design): one simple line person that moves from start to finish ----------
AW, ACX = 300, 150          # animation canvas width and centre
INKA, FARA = "#10221A", "#9AA6A1"
SHIRT, TORSO_W = INKA, 15   # the body: a solid block from hips to shoulders
DUR = "3.6s"; KT = "0;0.2;0.5;0.7;1"; KS = "0 0 1 1;.4 0 .6 1;0 0 1 1;.4 0 .6 1"

def anim(attr, a, b):
    return f'<animate attributeName="{attr}" dur="{DUR}" repeatCount="indefinite" calcMode="spline" keyTimes="{KT}" keySplines="{KS}" values="{a};{a};{b};{b};{a}"/>'

_EL = re.compile(r'<(\w+)((?:\s+[\w-]+="[^"]*")*)\s*/>')
_AT = re.compile(r'([\w-]+)="([^"]*)"')

def morph(a, b):
    """Turn two SVG strings with the same structure into one whose attributes animate from a to b.
    Returns None when the structures differ (the caller then cross-fades instead)."""
    if _EL.sub("", a).strip() or _EL.sub("", b).strip(): return None
    ea, eb = _EL.findall(a), _EL.findall(b)
    if len(ea) != len(eb) or any(x[0] != y[0] for x, y in zip(ea, eb)): return None
    out = []
    for (tag, sa), (_, sb) in zip(ea, eb):
        da, db = dict(_AT.findall(sa)), dict(_AT.findall(sb))
        if set(da) != set(db): return None
        kids = "".join(anim(k, da[k], db[k]) for k in da if da[k] != db[k])
        attrs = "".join(f' {k}="{v}"' for k, v in da.items())
        out.append(f"<{tag}{attrs}>{kids}</{tag}>" if kids else f"<{tag}{attrs}/>")
    return "".join(out)

def fade(a, b):
    def g(x, v0, v1): return f'<g opacity="{v0}">{x}<animate attributeName="opacity" dur="{DUR}" repeatCount="indefinite" keyTimes="0;0.2;0.3;0.5;0.7;0.8;1" values="{v0};{v0};{v1};{v1};{v1};{v0};{v0}"/></g>' if x else ""
    return g(a, 1, 0) + g(b, 0, 1)

def blend(a, b):
    m = morph(a, b)
    return m if m is not None else fade(a, b)

def stick(p, ps, front=False, gy=None):
    """The line person as plain SVG elements (same structure for every pose, so poses can morph)."""
    t = math.radians(ps["t"]); up = (math.cos(t), math.sin(t)); face = (-up[1], up[0])
    h, n = p["hip"], p["neck"]
    a = math.radians(ps["t"] - 90); c = ((h[0] + n[0]) / 2 + ps["bend"] * math.cos(a), (h[1] + n[1]) / 2 + ps["bend"] * math.sin(a))
    spine = _q(h, c, p["sh"], 4)   # the body block stops at the shoulders so it meets the head cleanly
    def pl(pts, c, w, join="miter"): return f'<polyline points="{" ".join(f"{x},{y}" for x, y in pts)}" fill="none" stroke="{c}" stroke-width="{w}" stroke-linejoin="{join}" stroke-miterlimit="3"/>'
    leg = lambda k: [p["hip"], p["k" + k], p["f" + k], p["t" + k]]
    def hand(k):
        """A short hand past the wrist: flat on the floor when the wrist is down, otherwise in line with the forearm."""
        e, w = p["e" + k], p["w" + k]; dx, dy = w[0] - e[0], w[1] - e[1]; L = math.hypot(dx, dy) or 1
        if gy is not None and w[1] >= gy - 1.5:
            sx = face[0] if abs(face[0]) > .3 else dx; return P(w[0] + (7 if sx >= 0 else -7), w[1])
        return P(w[0] + dx / L * 7, w[1] + dy / L * 7)
    arm = lambda k: [p["sh"], p["e" + k], p["w" + k], hand(k)]
    hd = p["head"]
    # the face tilts with the body, but only part of the way (max 38 degrees), so the smile always stays readable
    lean = (ps["t"] + 90 + 180) % 360 - 180
    tilt = math.radians(max(-38, min(38, lean * .5))); ct, st_ = math.cos(tilt), math.sin(tilt)
    sft = 0 if front else (2 if face[0] > .3 else -2 if face[0] < -.3 else 0)
    def at(dx, dy):
        dx += sft; return f"{round(hd[0] + dx * ct - dy * st_, 1)},{round(hd[1] + dx * st_ + dy * ct, 1)}"
    def eye(dx):
        x, y = at(dx, -2.6).split(","); return f'<circle cx="{x}" cy="{y}" r="1.5" fill="{INKA}"/>'
    smile = eye(-3.4) + eye(3.4) + f'<path d="M{at(-4.8, 1.6)} Q{at(0, 7.4)} {at(4.8, 1.6)}" fill="none" stroke="{INKA}" stroke-width="2"/>'
    return (pl(arm("2"), FARA, 4) + pl(leg("2"), FARA, 4.5) + pl(spine, SHIRT, TORSO_W, "round") + pl(leg("1"), INKA, 5)
            + f'<circle cx="{hd[0]}" cy="{hd[1]}" r="{HEAD_R}" fill="#FFFFFF" stroke="{INKA}" stroke-width="2"/>' + smile + pl(arm("1"), "#FFFFFF", 8, "round") + pl(arm("1"), INKA, 4.5))

# ---------- pose checker: contact points and joint limits ----------
# Normal adult ranges (CDC Normal Joint Range of Motion Study, ages 20-44, rounded; shoulder extension and elbow from
# standard clinical reference values): the solver keeps every joint inside these and makes the listed points touch.
LIMITS = dict(knee=(0, 140), elbow=(0, 145), hip=(-20, 130), shoulder=(-60, 175), ankle=(-20, 60))  # ankle: dorsiflexion 20, plantarflexion about 55-60
EXEMPT = {"hamstring-stretch": {"knee2", "hip2"}}  # the folded leg lies out to the side
OUT_OF_PLANE = {"side-plank", "worlds-greatest-stretch", "childs-pose", "doorway-chest-stretch", "figure-four", "arm-circles",
                "hamstring-stretch", "warm-up", "dead-bug", "leg-swing"}  # moves with sideways/rotating limbs a side view cannot measure
TOUCH = {  # (move, frame) -> pairs of points that must meet, from the written cues
    ("goblet-squat", 0): [("w2", "w1")], ("goblet-squat", 1): [("w2", "w1")],
    ("db-row", 0): [("w2", "k1")], ("db-row", 1): [("w2", "k1")],
    ("knee-hug", 1): [("w1", "k1"), ("w2", "k1")],
    ("quad-stretch", 1): [("w1", "f1")],
    ("hip-circles", 0): [("w1", "hip"), ("w2", "hip")], ("hip-circles", 1): [("w1", "hip"), ("w2", "hip")],
    ("romanian-deadlift", 0): [("w2", "w1")], ("romanian-deadlift", 1): [("w2", "w1")],
    ("pallof-press", 0): [("w2", "w1")], ("pallof-press", 1): [("w2", "w1")],
}
ON_FLOOR = {  # exact floor contacts where the automatic guess is not what the exercise calls for
    ("hamstring-stretch", 0): {"hip", "f1", "k1", "k2", "f2"}, ("hamstring-stretch", 1): {"hip", "f1", "k1", "k2", "f2"},
    ("glute-bridge", 1): {"head", "f1", "f2", "w1", "w2"},
    ("hollow-hold", 0): {"hip"}, ("hollow-hold", 1): {"hip"},          # shoulders and legs hover, low back down
    ("dead-bug", 0): {"head", "hip"}, ("dead-bug", 1): {"head", "hip"},  # the lowered arm and leg hover
    ("childs-pose", 0): {"k1", "k2", "f1", "f2", "w1", "w2"},
}
VARS = [("t", None), ("l1", 0), ("l1", 1), ("l2", 0), ("l2", 1), ("a1", 0), ("a1", 1), ("a2", 0), ("a2", 1), ("ft1", None), ("ft2", None)]
# search moves: single angles, plus whole limbs and the whole body turning as one piece (so a plank can tilt
# onto its hands and toes without bending anything)
GROUPS = [[k] for k in range(11)] + [list(range(9)), [0, 1, 2, 3, 4], [0, 5, 6, 7, 8], [1, 2, 3, 4], [5, 6, 7, 8], [1, 2], [3, 4], [5, 6], [7, 8]]
NO_LIMITS = {"face-pull", "band-pull-apart"}  # elbows travel out to the side, which a side view cannot measure
RAISED = {("renegade-row", 0): {"w1": 9, "w2": 9}, ("renegade-row", 1): {"w2": 9}}  # hands rest on dumbbell handles, not the floor
def _w(x, lo): return (x - lo) % 360 + lo
def joint_angles(ps):
    t = ps["t"]; out = {}
    for k in ("1", "2"):
        th, sh = ps["l" + k]; ua, fa = ps["a" + k]
        out["knee" + k] = _w(sh - th, -150); out["hip" + k] = _w(t + 180 - th, -110)
        out["elbow" + k] = _w(ua - fa, -150); out["shoulder" + k] = _w(t + 180 - ua, -120); out["ankle" + k] = ps.get("ft" + k, 0)
    return out
_UP = {}
def eff_y(pts, j):
    if j in ("f1", "f2"): return max(pts[j][1], pts["t" + j[1]][1]) + 2.5   # a foot touches with its heel or its toes
    return pts[j][1] + (HEAD_R + 1.75 if j == "head" else TORSO_W / 2 if j in ("hip", "sh") else 2.5) + _UP.get(j, 0)
def lowest(pts): return max(eff_y(pts, j) for j in pts)
def _get(ps): return [ps[k] if i is None else ps[k][i] for k, i in VARS]
def _set(ps, v):
    q = dict(ps); q["t"] = v[0]; q["l1"] = (v[1], v[2]); q["l2"] = (v[3], v[4]); q["a1"] = (v[5], v[6]); q["a2"] = (v[7], v[8]); q["ft1"], q["ft2"] = v[9], v[10]; return q
def contacts(fr, key=None, i=None):
    """Which points must rest on the floor: the frame's anchors plus any hand, foot, knee or elbow already close to it."""
    if (key, i) in ON_FLOOR: return ON_FLOOR[(key, i)]
    pts = solve(fr["ps"]); anchors = fr["anchor"] if isinstance(fr["anchor"], list) else [fr["anchor"]]
    lying = any(a in ("neck", "hip", "head") for a in anchors)
    c = {"head" if a == "neck" else a for a in anchors}
    if fr["target"] != GROUND: return c
    low = max(eff_y(pts, j) for j in c)
    for j in ("f1", "f2", "w1", "w2", "k1", "k2", "e1", "e2") + (("hip", "head") if lying else ()):
        if low - eff_y(pts, j) < 12: c.add(j)
    ps = fr["ps"]  # limbs drawn as a matching pair touch down together
    for a, b, k in (("f1", "f2", "l"), ("k1", "k2", "l"), ("w1", "w2", "a"), ("e1", "e2", "a")):
        if (a in c) != (b in c) and all(abs(_w(x - y, -180)) < 15 for x, y in zip(ps[k + "1"], ps[k + "2"])): c |= {a, b}
    return c
def fit(key, i, fr):
    """Nudge the authored angles as little as possible so contacts touch and joints stay within normal range."""
    _UP.clear(); _UP.update(RAISED.get((key, i), {}))
    C = contacts(fr, key, i)
    # kneeling: when a knee is down, that foot lies flat behind it (top of the foot on the floor), so it is not flexed
    kneel = {k for k in "12" if "k" + k in C and fr["target"] == GROUND}
    fr = dict(fr, ps=dict(fr["ps"], **{"ft" + k: 90 for k in kneel}))
    base = _get(fr["ps"]); ground = fr["target"] == GROUND
    hang = fr["anchor"] == "w1" and fr["target"] == 22
    pairs = TOUCH.get((key, i), []); limits = not fr["front"] and key not in NO_LIMITS
    j0 = joint_angles(fr["ps"])
    wj = {n: (.5 if n.startswith("ankle") and n[-1] in kneel else .0004 if n.startswith("ankle") else .03 if n[:-1] in ("knee", "elbow") and abs(a) < 12 else .003) for n, a in j0.items()}
    def cost(v):
        ps = _set(fr["ps"], v); pts = solve(ps); c = 0.0
        if ground:
            low = lowest(pts); c += 4 * sum((eff_y(pts, j) - low) ** 2 for j in C)
        if hang: c += 4 * (pts["w1"][1] - pts["w2"][1]) ** 2
        c += 4 * sum(math.dist(pts[a], pts[b]) ** 2 for a, b in pairs)
        if limits:
            for name, ang in joint_angles(ps).items():
                kind = name[:-1]
                if kind in ("shoulder", "hip") and key in OUT_OF_PLANE: continue
                if name in EXEMPT.get(key, ()) or (kind == "ankle" and name[-1] in kneel): continue
                lo, hi = LIMITS[kind]; c += .5 * (max(0, lo - ang) ** 2 + max(0, ang - hi) ** 2)
        # stay close to the authored pose, measured at the joints; straight arms and legs resist bending most,
        # the whole-body lean (t) is the cheapest thing to change
        ja = joint_angles(ps)
        c += sum(wj[n] * _w(ja[n] - j0[n], -180) ** 2 for n in ja) + .05 * (v[0] - base[0]) ** 2 + .01 * ((v[2] - base[2]) ** 2 + (v[4] - base[4]) ** 2)
        return c
    # P() rounds to whole units, so search on a fine angle grid with shrinking steps
    v = list(base); best = cost(v)
    for step in (8, 4, 2, 1, .5, .25):
        for _ in range(30):
            moved = False
            for grp in GROUPS:
                for d in (step, -step):
                    w = list(v)
                    for k in grp: w[k] += d
                    c = cost(w)
                    if c < best - 1e-9: v, best, moved = w, c, True
            if not moved: break
    return _set(fr["ps"], v)
def audit(key, i, fr, ps):
    pts = solve(ps); out = []; _UP.clear(); _UP.update(RAISED.get((key, i), {}))
    if fr["target"] == GROUND:
        low = lowest(pts); out += [f"{j} off floor by {low - eff_y(pts, j):.1f}" for j in contacts(fr, key, i) if low - eff_y(pts, j) > 1.5]
    out += [f"{a}-{b} apart {math.dist(pts[a], pts[b]):.1f}" for a, b in TOUCH.get((key, i), []) if math.dist(pts[a], pts[b]) > 2.5]
    if not fr["front"] and key not in NO_LIMITS:
        for name, ang in joint_angles(ps).items():
            kind = name[:-1]
            if kind in ("shoulder", "hip") and key in OUT_OF_PLANE: continue
            if name in EXEMPT.get(key, ()) or (kind == "ankle" and ang == 90): continue
            lo, hi = LIMITS[kind]
            if ang < lo - 3 or ang > hi + 3: out.append(f"{name} {ang:.0f} outside {lo}..{hi}")
    return out

def place2(pts, fr, cx, target=None):
    """Put the lowest touching point exactly on the floor (or the anchor on its bar or box) and centre the figure."""
    if fr["target"] == GROUND: dy = GROUND + 2.5 - lowest(pts)
    else:
        a = fr["anchor"] if isinstance(fr["anchor"], list) else [fr["anchor"]]
        dy = (fr["target"] if target is None else target) - max(pts[j][1] for j in a)
    xs = [q[0] for q in pts.values()]; dx = cx - (min(xs) + max(xs)) / 2
    return {k: P(v[0] + dx, v[1] + dy) for k, v in pts.items()}

def _split(pr):
    front = "".join(re.findall(r'<g data-front="1">(.*?)</g>', pr)); back = re.sub(r'<g data-front="1">.*?</g>', "", pr)
    return back, front

def draw(move, idx):
    fa, fb = (dict(f, ps=fit(move["key"], i, f)) for i, f in enumerate(move["frames"][:2]))
    ra, rb = solve(fa["ps"]), solve(fb["ps"]); tgt = None
    if fa["target"] == 22 and fb["target"] == 22:  # hanging: raise the bar until the feet clear the floor in both poses
        tgt = min(22, GROUND - 8 - max(lowest(r) - r["w1"][1] for r in (ra, rb)))
    def put(r, f, i):
        _UP.clear(); _UP.update(RAISED.get((move["key"], i), {})); return place2(r, f, ACX, tgt)
    pa, pb = put(ra, fa, 0), put(rb, fb, 1); _UP.clear()
    if fa["target"] == fb["target"]:  # keep the planted hand or foot in the same spot so only the moving parts move
        a0 = (fb["anchor"] if isinstance(fb["anchor"], list) else [fb["anchor"]])[0]
        dx = pa[a0][0] - pb[a0][0]; pb = {k: P(v[0] + dx, v[1]) for k, v in pb.items()}
    ba, fra = _split(fa["props"](pa) if fa["props"] else ""); bb, frb = _split(fb["props"](pb) if fb["props"] else "")
    body = blend(ba, bb) + blend(stick(pa, fa["ps"], fa["front"], GROUND), stick(pb, fb["ps"], fb["front"], GROUND)) + blend(fra, frb)
    top = min(min(v[1] for v in q.values()) for q in (pa, pb)) - HEAD_R - 4
    xs = [v[0] for q in (pa, pb) for v in q.values()]; half = max(ACX - min(xs), max(xs) - ACX) + 16
    k = min(1, (GROUND - 4) / (GROUND - top) if top < 4 else 1, (ACX - 6) / half if half > ACX - 6 else 1)
    if k < 1: body = f'<g transform="translate({ACX},{GROUND}) scale({round(k, 3)}) translate({-ACX},{-GROUND})">{body}</g>'
    def label(txt, v0, v1):
        return (f'<text x="{ACX}" y="198" text-anchor="middle" font-family="Inter,system-ui,sans-serif" font-size="12" font-weight="700" fill="#157A12" opacity="{v0}">{txt}'
                f'<animate attributeName="opacity" dur="{DUR}" repeatCount="indefinite" keyTimes="0;0.2;0.5;0.7;1" values="{v0};{v0};{v1};{v1};{v0}"/></text>')
    return (f'<rect width="{AW}" height="200" fill="#FFFFFF"/>' + line((20, GROUND + 3.5), (AW - 20, GROUND + 3.5), "#C9D1CE", 2)
            + f'<g stroke-linecap="round" stroke-linejoin="round">{body}</g>' + label(move["labels"][0], 1, 0) + label(move["labels"][1], 0, 1))

def build():
    art = {}
    for i, m in enumerate(MOVES):
        art[m["key"]] = dict(svg=draw(m, i), cues=m["cues"], labels=list(m["labels"]), eq=EQUIP.get(m["key"], ""))
    return art

if __name__ == "__main__":
    if "--audit" in sys.argv:  # report every contact gap or joint outside normal range, before and after fitting
        bad = 0
        for m in MOVES:
            for i, f in enumerate(m["frames"][:2]):
                before, after = audit(m["key"], i, f, f["ps"]), audit(m["key"], i, f, fit(m["key"], i, f))
                if before or after: print(f'{m["key"]}[{i}] before: {"; ".join(before) or "ok"} | after: {"; ".join(after) or "ok"}')
                bad += bool(after)
        print("frames still flagged:", bad, "of", 2 * len(MOVES)); sys.exit(1 if bad else 0)
    art = build()
    if "--preview" in sys.argv:
        out = sys.argv[sys.argv.index("--preview") + 1]
        html = "<body style='margin:0;font:12px sans-serif;display:grid;grid-template-columns:repeat(4,300px);gap:6px;background:#fff'>" + "".join(
            f"<div><b>{k}</b><svg viewBox='0 0 300 200' width='300' height='200'>{v['svg']}</svg></div>" for k, v in art.items()) + "</body>"
        Path(out).write_text(html); print("preview", out, len(art))
    else:
        src = ROOT / "app.src.html"; s = src.read_text()
        blob = "<script>window.EXART=" + json.dumps(dict(art=art, names=NAMES), separators=(",", ":")).replace("</", "<\\/") + ";</script>\n"
        if "window.EXART=" in s:
            s = re.sub(r"<script>window\.EXART=.*?;</script>\n", lambda m: blob, s, count=1, flags=re.S)
        else:
            s = s.replace("<script>window.LB=", blob + "<script>window.LB=", 1)
        src.write_text(s); print("injected EXART:", len(art), "moves,", len(blob) // 1024, "KB")

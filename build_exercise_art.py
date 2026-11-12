"""Draws original illustrations for every workout move (two frames + form cues) and injects
window.EXART into app.src.html. People vary in skin tone, hair, headwear and build, cycling
through a worldwide set so the app shows many kinds of people training.

Usage: python tools/build_exercise_art.py [--preview out.html]"""
import json, math, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GROUND = 182
SEG = dict(T=48, TH=36, SH=36, UA=26, FA=24)

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
    return dict(t=t, l1=l1, l2=l2, a1=a1, a2=a2, bend=bend)

def solve(ps, hip=(0, 0)):
    h = P(*hip); n = go(h, ps["t"], SEG["T"])
    k1 = go(h, ps["l1"][0], SEG["TH"]); f1 = go(k1, ps["l1"][1], SEG["SH"])
    k2 = go(h, ps["l2"][0], SEG["TH"]); f2 = go(k2, ps["l2"][1], SEG["SH"])
    sh = go(h, ps["t"], SEG["T"] - 4)
    e1 = go(sh, ps["a1"][0], SEG["UA"]); w1 = go(e1, ps["a1"][1], SEG["FA"])
    e2 = go(sh, ps["a2"][0], SEG["UA"]); w2 = go(e2, ps["a2"][1], SEG["FA"])
    hd = go(n, ps["t"], 13)
    return dict(hip=h, neck=n, sh=sh, k1=k1, f1=f1, k2=k2, f2=f2, e1=e1, w1=w1, e2=e2, w2=w2, head=hd)

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

def head(p, ps, who, skin, front=False):
    hx, hy = p["head"]; r = 9.5
    t = math.radians(ps["t"]); up = (math.cos(t), math.sin(t)); face = (-up[1], up[0])
    back = (-face[0], -face[1]); hair = "#3A3A3A"; s = []
    def at(v, d): return (round(hx + v[0] * d, 1), round(hy + v[1] * d, 1))
    kind = who["hair"]
    if kind == "hijab":
        s.append(f'<circle cx="{hx}" cy="{hy}" r="{r + 3}" fill="#8C8C8C"/>')
        nk = at((-up[0], -up[1]), 10); s.append(line((hx, hy), nk, "#8C8C8C", 12))
        fc = at(face, 3.5); s.append(f'<circle cx="{fc[0]}" cy="{fc[1]}" r="{r - 3.2}" fill="{skin}"/>')
        return "".join(s)
    if kind == "afro":
        c = at(back, 2) if not front else (hx, hy - 2); s.append(f'<circle cx="{c[0]}" cy="{c[1]}" r="{r + 4.5}" fill="{hair}"/>')
    if kind == "curly":
        for v, d in ((up, 6), (back, 6), (((up[0] + back[0]) / 1.4, (up[1] + back[1]) / 1.4), 7)):
            c = at(v, d); s.append(f'<circle cx="{c[0]}" cy="{c[1]}" r="6.5" fill="{hair}"/>')
    if kind == "turban":
        c = at(up, 3); s.append(f'<ellipse cx="{c[0]}" cy="{c[1]}" rx="{r + 2}" ry="{r}" fill="#A8A8A8"/>')
    if kind == "wrap":
        c = at(((up[0] + back[0] * .6), (up[1] + back[1] * .6)), 6); s.append(f'<circle cx="{c[0]}" cy="{c[1]}" r="{r - 1}" fill="#BDBDBD"/>')
    s.append(f'<circle cx="{hx}" cy="{hy}" r="{r}" fill="{skin}"/>')
    if kind in ("short", "bun", "locs", "ponytail"):
        a0 = math.degrees(math.atan2(back[1], back[0])); a1 = math.degrees(math.atan2(up[1], up[0]))
        # cap over top/back half of the head
        p1 = at(face, 0); s.append(f'<path d="M{at((face[0]*.2+up[0], face[1]*.2+up[1]), r)[0]},{at((face[0]*.2+up[0], face[1]*.2+up[1]), r)[1]} A{r},{r} 0 0 0 {at(back, r)[0]},{at(back, r)[1]} L{hx},{hy} Z" fill="{hair}"/>')
    if kind == "bun":
        c = at(((up[0] + back[0]) / 1.4, (up[1] + back[1]) / 1.4), r + 2); s.append(f'<circle cx="{c[0]}" cy="{c[1]}" r="4.5" fill="{hair}"/>')
    if kind == "ponytail":
        a = at(((up[0] + back[0]) / 1.4, (up[1] + back[1]) / 1.4), r); b = at(((back[0] - up[0] * .8), (back[1] - up[1] * .8)), r + 9)
        s.append(line(a, b, hair, 4.5))
    if kind == "locs":
        for off in (-3, 0, 3):
            a = at(back, r - 1); a = (a[0] + up[0] * off, a[1] + up[1] * off)
            b = (a[0] + back[0] * 4 - up[0] * 14, a[1] + back[1] * 4 - up[1] * 14)
            s.append(line(a, (round(b[0], 1), round(b[1], 1)), hair, 3))
    if kind == "bald":
        b = at(((face[0] - up[0] * .7), (face[1] - up[1] * .7)), r - 2.5); s.append(f'<circle cx="{b[0]}" cy="{b[1]}" r="3.6" fill="{hair}"/>')
    return "".join(s)

INK = "#2B2B2B"
def gray(c):
    c = c.lstrip("#"); r, g, b = (int(c[i:i + 2], 16) for i in (0, 2, 4)); v = round((.3 * r + .59 * g + .11 * b) * .55 + 255 * .45)
    return "#%02X%02X%02X" % (v, v, v - 4)

def tint(c, k=.62):
    c = c.lstrip("#"); r, g, b = (int(c[i:i + 2], 16) for i in (0, 2, 4))
    return "#%02X%02X%02X" % tuple(round(v + (255 - v) * k) for v in (r, g, b))

def tube(pts, fill, w, far=False):
    """Sketch-style limb: ink outline with a light wash inside."""
    op = .5 if far else 1
    return poly(pts, INK, w + 3.5, op) + poly(pts, fill, w, op)

def figure(p, ps, who, skin, front=False):
    w = who["w"] - 1; g = []
    sk = gray(skin); top = "#EFEBE2"; bot = "#D6D1C5"
    arm = sk if who["hair"] != "hijab" else top
    g.append(tube([p["sh"], p["e2"], p["w2"]], arm, w - 1, True))
    g.append(tube([p["hip"], p["k2"], p["f2"]], bot, w + 1, True))
    tw = w + 6
    if not ps["bend"]:
        g.append(line(p["hip"], p["neck"], INK, tw + 3.5) + line(p["hip"], p["neck"], top, tw))
    else:
        g.append(torso(p, ps, INK, w + 3.5) + torso(p, ps, top, w))
    g.append(tube([p["hip"], p["k1"], p["f1"]], bot, w + 1))
    hd = head(p, ps, who, sk, front)
    hd = hd.replace(f'fill="{sk}"/>', f'fill="{sk}" stroke="{INK}" stroke-width="1.8"/>')
    g.append(hd)
    g.append(tube([p["sh"], p["e1"], p["w1"]], arm, w - 1))
    for f in ("f1", "f2"):
        g.append(f'<ellipse cx="{p[f][0]}" cy="{p[f][1]}" rx="5" ry="3.6" fill="{INK}"{"" if f == "f1" else " opacity=\".5\""}/>')
    # pencil shading under the figure
    xs = [v[0] for v in p.values()]; base = max(v[1] for v in p.values())
    if base > GROUND - 8:
        x0, x1 = min(xs) - 4, max(xs) + 4
        g.append("".join(line((round(x, 1), GROUND + 3), (round(x + 6, 1), GROUND - 1), "#8A8A8A", 1, .6) for x in [x0 + k * 7 for k in range(int((x1 - x0) / 7) + 1)]))
    return "".join(g)

# ---------- props (equipment in brand green so it stands out from the pencil figure) ----------
GR = "#1A7F17"; EQ = "#1A7F17"; BAND = "#22a11e"; EQL = "#CFEFC8"
def db(c, ang=0):
    a = math.radians(ang); dx, dy = 12 * math.cos(a), 12 * math.sin(a)
    p1, p2 = P(c[0] - dx, c[1] - dy), P(c[0] + dx, c[1] + dy)
    px, py = -math.sin(a) * 8, math.cos(a) * 8
    def plate(q):
        return line(P(q[0] - px, q[1] - py), P(q[0] + px, q[1] + py), "#0E4F0C", 10) + line(P(q[0] - px * .8, q[1] - py * .8), P(q[0] + px * .8, q[1] + py * .8), EQ, 6.5)
    return "<g data-front=\"1\">" + line(p1, p2, "#0E4F0C", 4.5) + plate(p1) + plate(p2) + "</g>"
def bar(x0, x1, y):
    return (line((x0, y + 4), (x0, y + 162), EQ, 4) + line((x1, y + 4), (x1, y + 162), EQ, 4)
            + line((x0 - 6, y + 162), (x0 + 6, y + 162), EQ, 4) + line((x1 - 6, y + 162), (x1 + 6, y + 162), EQ, 4)
            + line((x0 - 4, y), (x1 + 4, y), "#0E4F0C", 7) + line((x0 - 4, y), (x1 + 4, y), EQ, 4))
def box(x, w, h):
    return (f'<rect x="{x}" y="{GROUND - h}" width="{w}" height="{h}" rx="3" fill="{EQL}" stroke="{EQ}" stroke-width="3"/>'
            + "".join(line((x + k, GROUND - 3), (x + k + 9, GROUND - h + 4), EQ, 1.2, .6) for k in range(5, int(w) - 8, 8)))
def mat(x0, x1): return f'<rect x="{x0}" y="{GROUND - 1}" width="{x1 - x0}" height="6" rx="3" fill="{EQL}" stroke="{EQ}" stroke-width="2"/>'
def band(a, b): return line(a, b, "#0E4F0C", 6) + line(a, b, BAND, 3.5)
def wall(x):
    return (f'<rect x="{x}" y="10" width="10" height="{GROUND - 10}" fill="none" stroke="#2B2B2B" stroke-width="2"/>'
            + "".join(line((x, y), (x + 10, y - 8), "#8A8A8A", 1) for y in range(24, GROUND, 14)))
def climber(top, foot):
    """Vertical climber: tall rail, handles at the top, pedals near the bottom, wide base."""
    tx, bx = top[0] + 14, foot[0] + 28
    return (line((tx, 14), (bx, GROUND), "#0E4F0C", 9) + line((tx, 14), (bx, GROUND), EQ, 6)
            + line((tx - 12, 22), (tx + 4, 22), EQ, 5) + line((bx - 22, GROUND - 22), (bx - 4, GROUND - 22), EQ, 5)
            + line((bx - 40, GROUND), (bx + 34, GROUND), "#0E4F0C", 7) + line((bx - 40, GROUND), (bx + 34, GROUND), EQ, 4))
def arrow(a, b):
    ang = math.atan2(b[1] - a[1], b[0] - a[0]); h1 = P(b[0] - 8 * math.cos(ang - .5), b[1] - 8 * math.sin(ang - .5)); h2 = P(b[0] - 8 * math.cos(ang + .5), b[1] - 8 * math.sin(ang + .5))
    return line(a, b, "#4A4A4A", 2) + poly([h1, b, h2], "#4A4A4A", 2)

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
   [F(pose(a1=(-80, -84), a2=(-100, -96)), anchor="w1", target=22, props=lambda p: bar(p["w1"][0] - 50, p["w1"][0] + 50, 20)),
    F(pose(t=-95, l1=(-15, 95), l2=(-8, 100), a1=(-80, -84), a2=(-100, -96)), anchor="w1", target=22, props=lambda p: bar(p["w1"][0] - 50, p["w1"][0] + 50, 20))]),
 M("bulgarian-split-squat", ["Back foot laces-down on a step or couch.", "Drop the back knee straight down; front shin stays fairly upright.", "Push through the front heel to stand."],
   [F(pose(t=-88, l1=(80, 92), l2=(118, 192), a1=(92, 90), a2=(88, 90)), props=lambda p: box(p["f2"][0] - 26, 32, GROUND - p["f2"][1] - 4) + db(p["w1"], 90)),
    F(pose(t=-82, l1=(10, 96), l2=(100, 205), a1=(92, 90), a2=(88, 90)), props=lambda p: box(p["f2"][0] - 26, 32, GROUND - p["f2"][1] - 4) + db(p["w1"], 90))]),
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
   [F(pose(l1=(95, 115), l2=(92, 112), a1=(-100, -95), a2=(-80, -85)), anchor="w1", target=22, props=lambda p: bar(p["w1"][0] - 55, p["w1"][0] + 55, 20)),
    F(pose(l1=(95, 120), l2=(92, 118), a1=(120, -75), a2=(60, -105)), anchor="w1", target=22, props=lambda p: bar(p["w1"][0] - 55, p["w1"][0] + 55, 20))]),
 M("push-up", ["Hands under shoulders, body straight from head to heels.", "Lower your chest to a fist's height from the floor, elbows about 45°.", "Press away; elevate hands on a couch to make it easier."],
   [F(pose(t=-14, l1=(172, 176), l2=(174, 178), a1=(88, 90), a2=(90, 92)), anchor=["f1", "w1"], props=lambda p: mat(p["f1"][0] - 10, p["w1"][0] + 14)),
    F(pose(t=-3, l1=(178, 179), l2=(179, 180), a1=(200, 62), a2=(202, 64)), anchor=["f1", "w1"], props=lambda p: mat(p["f1"][0] - 10, p["w1"][0] + 14))]),
 M("db-row", ["Hinge forward with a flat back; free hand on your front knee.", "Row the dumbbell toward your hip, elbow close.", "Lower with control; don't twist."],
   [F(pose(t=-22, l1=(70, 95), l2=(110, 90), a1=(90, 90), a2=(60, 100)), anchor=["f1", "f2"], props=lambda p: db(p["w1"])),
    F(pose(t=-22, l1=(70, 95), l2=(110, 90), a1=(-170, 95), a2=(60, 100)), anchor=["f1", "f2"], props=lambda p: db(p["w1"]))]),
 M("overhead-press", ["Dumbbells at shoulder height, ribs down.", "Press straight up until arms are locked overhead.", "Don't lean back; squeeze glutes."],
   [F(pose(a1=(100, -88), a2=(95, -85)), props=lambda p: db(p["w1"])),
    F(pose(a1=(-92, -92), a2=(-88, -88)), props=lambda p: db(p["w1"]))]),
 M("face-pull", ["Band anchored at head height; arms straight to start.", "Pull toward your face, elbows high and wide.", "Squeeze shoulder blades, then return slowly."],
   [F(pose(a1=(-5, -5), a2=(-3, -3)), props=lambda p: band(p["w1"], (p["w1"][0] + 40, p["w1"][1])) + wall(p["w1"][0] + 40)),
    F(pose(a1=(-170, -20), a2=(-165, -15)), props=lambda p: band(p["w1"], (p["w1"][0] + 80, p["w1"][1])) + wall(p["w1"][0] + 80))]),
 M("dead-hang", ["Grip the bar, arms straight, feet off the floor.", "Relax, then gently pull shoulders away from your ears.", "Breathe; build up the time week by week."],
   [F(pose(a1=(-92, -92), a2=(-88, -88)), anchor="w1", target=22, props=lambda p: bar(p["w1"][0] - 50, p["w1"][0] + 50, 20)),
    F(pose(l1=(80, 100), l2=(84, 104), a1=(-92, -92), a2=(-88, -88)), anchor="w1", target=22, props=lambda p: bar(p["w1"][0] - 50, p["w1"][0] + 50, 20))], ("Hold", "Active shoulders")),
 M("hollow-hold", ["Low back pressed into the floor.", "Arms overhead, legs long and low, shoulders lifted.", "Bend knees or bring arms in to make it easier."],
   [F(pose(t=192, l1=(-12, -10), l2=(-10, -8), a1=(196, 196), a2=(194, 194)), anchor="hip", props=lambda p: mat(p["w1"][0] - 8, p["f1"][0] + 8)),
    F(pose(t=192, l1=(-60, 30), l2=(-58, 32), a1=(-30, 40), a2=(-28, 40)), anchor="hip", props=lambda p: mat(p["head"][0] - 14, p["f1"][0] + 10))], ("Hold", "Easier: tuck")),
 M("side-plank", ["Elbow under shoulder, body in a straight line.", "Lift hips; don't let them sag toward the floor.", "Drop the bottom knee to make it easier."],
   [F(pose(t=-20, l1=(162, 162), l2=(164, 164), a1=(92, -2), a2=(-92, -92)), anchor=["f1", "w1"], props=lambda p: mat(p["f1"][0] - 10, p["w1"][0] + 10)),
    F(pose(t=-32, l1=(155, 215), l2=(157, 215), a1=(92, -2), a2=(-92, -92)), anchor=["k1", "w1"], props=lambda p: mat(p["f1"][0] - 10, p["w1"][0] + 10))], ("Hold", "Easier: knees")),
 M("thruster", ["Dumbbells at shoulders; squat down with chest up.", "Drive up and use that power to press overhead.", "Lower the weights back to shoulders as you squat again."],
   [F(pose(t=-62, l1=(12, 104), l2=(18, 108), a1=(110, -82), a2=(105, -80)), anchor=["f1", "f2"], props=lambda p: db(p["w1"])),
    F(pose(a1=(-92, -92), a2=(-88, -88)), props=lambda p: db(p["w1"]))]),
 M("band-pull-apart", ["Hold the band at chest height, arms straight.", "Pull it apart until it touches your chest.", "Squeeze shoulder blades; return slowly."],
   [F(pose(l1=(84, 88), l2=(96, 92), a1=(-20, 10), a2=(200, 170)), front=True, props=lambda p: band(p["w1"], p["w2"])),
    F(pose(l1=(84, 88), l2=(96, 92), a1=(-2, -2), a2=(182, 182)), front=True, props=lambda p: band(p["w1"], p["w2"]))]),
 M("renegade-row", ["High plank on dumbbells, feet wide.", "Row one dumbbell to your ribs without rotating your hips.", "Place it down softly and switch sides."],
   [F(pose(t=-14, l1=(170, 176), l2=(176, 178), a1=(88, 90), a2=(90, 92)), anchor=["f1", "w1"], props=lambda p: db(p["w1"]) + db(p["w2"])),
    F(pose(t=-14, l1=(170, 176), l2=(176, 178), a1=(-175, 92), a2=(90, 92)), anchor=["f1", "w2"], props=lambda p: db(p["w1"]) + db(p["w2"]))]),
 M("pallof-press", ["Band anchored to your side at chest height.", "Press hands straight out from your chest.", "Resist the band twisting you; hold 2 seconds, return."],
   [F(pose(a1=(100, -40), a2=(95, -38)), props=lambda p: band(p["w1"], (p["w1"][0] - 90, p["w1"][1] - 2)) + wall(p["w1"][0] - 100)),
    F(pose(a1=(-2, -2), a2=(0, 0)), props=lambda p: band(p["w1"], (p["w1"][0] - 130, p["w1"][1])) + wall(p["w1"][0] - 140))]),
 M("step-up", ["Whole foot on a sturdy step or bench.", "Drive through that heel to stand tall on top.", "Step down under control; switch legs."],
   [F(pose(l1=(-5, 92), l2=(95, 90), a1=(90, 90), a2=(88, 88)), anchor="f2", props=lambda p: box(p["f1"][0] - 22, 56, GROUND - p["f1"][1] - 4) + db(p["w1"])),
    F(pose(l1=(90, 90), l2=(-20, 90), a1=(90, 90), a2=(88, 88)), anchor="f1", target=GROUND - 42, props=lambda p: box(p["f1"][0] - 26, 56, 38) + db(p["w1"]))]),
 M("hanging-leg-raise", ["Hang with shoulders active, no swinging.", "Lift legs (or knees) to hip height or higher.", "Lower slowly."],
   [F(pose(t=-95, l1=(-15, 95), l2=(-8, 100), a1=(-80, -84), a2=(-100, -96)), anchor="w1", target=22, props=lambda p: bar(p["w1"][0] - 50, p["w1"][0] + 50, 20)),
    F(pose(t=-100, l1=(-8, -6), l2=(-4, -2), a1=(-80, -84), a2=(-100, -96)), anchor="w1", target=22, props=lambda p: bar(p["w1"][0] - 50, p["w1"][0] + 50, 20))], ("Knees", "Straight legs")),
 M("warm-up", ["Easy jog in place or on the Maxi Climber for 3 minutes.", "Then arm circles, leg swings and a few bodyweight squats.", "Finish slightly warm, not tired."],
   [F(pose(t=-85, l1=(40, 110), l2=(120, 150), a1=(60, -60), a2=(140, 100)), anchor="f2"),
    F(pose(a1=(-60, -40), a2=(-120, -140)))], ("Jog", "Arm circles")),
 M("dead-bug", ["On your back, arms to the ceiling, knees bent at 90°.", "Lower the opposite arm and leg toward the floor, low back stays down.", "Return and switch sides."],
   [F(pose(t=180, l1=(-90, 0), l2=(-92, 2), a1=(-90, -90), a2=(-92, -92)), anchor=["hip"], props=lambda p: mat(p["head"][0] - 14, p["f1"][0] + 12)),
    F(pose(t=180, l1=(-12, -6), l2=(-92, 2), a1=(-90, -90), a2=(192, 190)), anchor=["hip"], props=lambda p: mat(p["w2"][0] - 8, p["f1"][0] + 12))]),
 M("mountain-climber", ["High plank, hands under shoulders.", "Drive one knee toward your chest, then switch quickly.", "Keep hips low and steady."],
   [F(pose(t=-16, l1=(25, 125), l2=(172, 178), a1=(88, 90), a2=(90, 92)), anchor=["f2", "w1"], props=lambda p: mat(p["f2"][0] - 10, p["w1"][0] + 12)),
    F(pose(t=-16, l1=(172, 178), l2=(25, 125), a1=(88, 90), a2=(90, 92)), anchor=["f1", "w1"], props=lambda p: mat(p["f1"][0] - 10, p["w1"][0] + 12))]),
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
]

EQUIP = {"goblet-squat": "1 dumbbell", "hanging-knee-raise": "Pull-up bar", "bulgarian-split-squat": "2 dumbbells, a step or couch",
 "plank": "Mat", "romanian-deadlift": "2 dumbbells", "glute-bridge": "Mini band or resistance band, mat", "walking-lunge": "Bodyweight",
 "db-walking-lunge": "2 dumbbells", "pull-up": "Pull-up bar, band for assistance", "push-up": "Mat", "db-row": "1 dumbbell",
 "overhead-press": "2 dumbbells", "face-pull": "Resistance band, door anchor", "dead-hang": "Pull-up bar", "hollow-hold": "Mat",
 "side-plank": "Mat", "thruster": "2 dumbbells", "band-pull-apart": "Resistance band", "renegade-row": "2 dumbbells, mat",
 "pallof-press": "Resistance band, door anchor", "step-up": "2 dumbbells, a sturdy step or bench", "hanging-leg-raise": "Pull-up bar",
 "warm-up": "Bodyweight or Maxi Climber", "dead-bug": "Mat", "mountain-climber": "Mat", "maxi-climber": "Maxi Climber",
 "band-row-walkback": "Resistance band, low anchor", "burpee-broad-jump": "Open floor space", "farmers-carry": "2 dumbbells (heaviest)",
 "cat-cow": "Mat", "hip-flexor-stretch": "Mat or cushion", "calf-stretch": "Wall", "doorway-chest-stretch": "Doorway", "childs-pose": "Mat"}

NAMES = {  # exercise names in the plan -> drawing key
 "Goblet squat": "goblet-squat", "Hanging knee raise": "hanging-knee-raise", "Bulgarian split squat": "bulgarian-split-squat",
 "Plank": "plank", "DB Romanian deadlift": "romanian-deadlift", "Band glute bridge": "glute-bridge", "Walking lunges": "walking-lunge",
 "Pull-ups (band-assisted if needed)": "pull-up", "Push-ups": "push-up", "1-arm DB row": "db-row", "DB overhead press": "overhead-press",
 "Band face pulls": "face-pull", "Dead hang": "dead-hang", "Hollow hold": "hollow-hold", "Side plank": "side-plank", "DB thrusters": "thruster",
 "Band pull-aparts": "band-pull-apart", "Renegade rows": "renegade-row", "Pallof press": "pallof-press", "DB step-ups": "step-up",
 "Hanging leg or knee raise": "hanging-leg-raise", "Warm-up": "warm-up", "dead bugs": "dead-bug", "mountain climbers": "mountain-climber",
 "Maxi Climber": "maxi-climber", "Walk-back band rows": "band-row-walkback", "Burpee broad jumps": "burpee-broad-jump",
 "DB walking lunges": "db-walking-lunge", "Farmers carry": "farmers-carry", "Cat-cow": "cat-cow", "Hip-flexor stretch": "hip-flexor-stretch",
 "Calf stretch": "calf-stretch", "Doorway chest stretch": "doorway-chest-stretch", "Child's pose + thoracic rotations": "childs-pose",
}

def draw(move, idx):
    who = PEOPLE[idx % len(PEOPLE)]; skin = SKIN[(idx * 3) % len(SKIN)]; fid = f"sk{idx}"
    flt = f'<defs><filter id="{fid}" x="-5%" y="-5%" width="110%" height="110%"><feTurbulence type="fractalNoise" baseFrequency="0.04" numOctaves="2" seed="{idx + 3}"/><feDisplacementMap in="SourceGraphic" scale="3"/></filter><filter id="{fid}b" x="-5%" y="-5%" width="110%" height="110%"><feTurbulence type="fractalNoise" baseFrequency="0.06" numOctaves="2" seed="{idx + 41}"/><feDisplacementMap in="SourceGraphic" scale="4"/></filter></defs>'
    parts = [flt, '<rect width="400" height="200" fill="#FBF8F1"/>']
    body = [line((6, GROUND + 6), (394, GROUND + 5), "#2B2B2B", 1.6), line((200, 22), (201, 172), "#C9C2B2", 1.2)]
    for i, fr in enumerate(move["frames"]):
        pts = place(solve(fr["ps"]), fr["anchor"], fr["target"], 100 + 200 * i)
        pr = fr["props"](pts) if fr["props"] else ""
        front = "".join(re.findall(r'<g data-front="1">.*?</g>', pr)); back = re.sub(r'<g data-front="1">.*?</g>', "", pr)
        body.append(back); body.append(figure(pts, fr["ps"], who, skin, fr["front"])); body.append(front.replace(' data-front="1"', ""))
    b = "".join(body)
    parts.append(f'<g id="b{idx}" filter="url(#{fid})" stroke-linecap="round" stroke-linejoin="round">' + b + "</g>")
    parts.append(f'<use href="#b{idx}" filter="url(#{fid}b)" opacity=".3" transform="translate(1.2,.8)"/>')
    for i in range(len(move["frames"])):
        parts.append(f'<text x="{100 + 200 * i}" y="197" text-anchor="middle" font-family="\'Bradley Hand\',\'Segoe Print\',\'Comic Neue\',cursive" font-size="13" fill="#4A4A4A">{move["labels"][i]}</text>')
    return "".join(parts)

def build():
    art = {}
    for i, m in enumerate(MOVES):
        art[m["key"]] = dict(svg=draw(m, i), cues=m["cues"], labels=list(m["labels"]), eq=EQUIP.get(m["key"], ""))
    return art

if __name__ == "__main__":
    art = build()
    if "--preview" in sys.argv:
        out = sys.argv[sys.argv.index("--preview") + 1]
        html = "<body style='margin:0;font:12px sans-serif;display:grid;grid-template-columns:repeat(3,400px);gap:6px;background:#fff'>" + "".join(
            f"<div><b>{k}</b><svg viewBox='0 0 400 200' width='400' height='200'>{v['svg']}</svg></div>" for k, v in art.items()) + "</body>"
        Path(out).write_text(html); print("preview", out, len(art))
    else:
        src = ROOT / "app.src.html"; s = src.read_text()
        blob = "<script>window.EXART=" + json.dumps(dict(art=art, names=NAMES), separators=(",", ":")).replace("</", "<\\/") + ";</script>\n"
        if "window.EXART=" in s:
            s = re.sub(r"<script>window\.EXART=.*?;</script>\n", lambda m: blob, s, count=1, flags=re.S)
        else:
            s = s.replace("<script>window.LB=", blob + "<script>window.LB=", 1)
        src.write_text(s); print("injected EXART:", len(art), "moves,", len(blob) // 1024, "KB")

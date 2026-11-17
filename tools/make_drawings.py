"""Génère les schémas SVG (textures, gisements, orientation) dans static/img/rlame/.
Lancer : python tools/make_drawings.py   (nécessite numpy et scipy ; les SVG sont déjà fournis)."""
import math, os, random
import numpy as np
from scipy.spatial import Voronoi

OUT = os.path.join(os.path.dirname(__file__), "..", "static", "img", "rlame")
os.makedirs(OUT, exist_ok=True)
C, R = 100, 94


def svg(body, name, bg="#f4f1ea"):
    s = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="200" height="200">'
         f'<defs><clipPath id="c"><circle cx="{C}" cy="{C}" r="{R}"/></clipPath></defs>'
         f'<circle cx="{C}" cy="{C}" r="{R + 3}" fill="#2b2f33"/>'
         f'<g clip-path="url(#c)"><rect width="200" height="200" fill="{bg}"/>{body}</g></svg>')
    open(os.path.join(OUT, name + ".svg"), "w", encoding="utf-8").write(s)


def poly(pts, fill, stroke="#3d4147", sw=1.2, op=1):
    p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return f'<polygon points="{p}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" fill-opacity="{op}" stroke-linejoin="round"/>'


def voronoi(points):
    pts = np.array(points)
    ring = [(C + 260 * math.cos(a), C + 260 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 16, endpoint=False)]
    v = Voronoi(np.vstack([pts, ring]))
    cells = []
    for i in range(len(pts)):
        reg = v.regions[v.point_region[i]]
        if reg and -1 not in reg:
            cells.append([tuple(v.vertices[j]) for j in reg])
    return cells


def jitter_points(n, rnd, minDist):
    pts = []
    tries = 0
    while len(pts) < n and tries < 6000:
        tries += 1
        x, y = rnd.uniform(-10, 210), rnd.uniform(-10, 210)
        if all((x - a) ** 2 + (y - b) ** 2 >= minDist ** 2 for a, b in pts):
            pts.append((x, y))
    return pts


def lloyd(points, it=3):
    pts = list(points)
    for _ in range(it):
        cells = voronoi(pts)
        if len(cells) != len(pts):
            break
        pts = [tuple(np.mean(c, axis=0)) for c in cells]
    return pts


def rect(cx, cy, w, h, ang, fill, stroke="#3d4147", sw=1.1, op=1):
    a = math.radians(ang)
    pts = []
    for dx, dy in ((-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)):
        pts.append((cx + dx * math.cos(a) - dy * math.sin(a), cy + dx * math.sin(a) + dy * math.cos(a)))
    return poly(pts, fill, stroke, sw, op)


GREYS = ["#e9e9e4", "#d9dad5", "#cfd0cb", "#f1efe8"]
PINK = "#e8cdbf"
BROWN = "#8a6a4a"

# ------------------------------------------------------------------ textures magmatiques
def grenue():
    r = random.Random(1)
    body = ""
    for c in voronoi(jitter_points(34, r, 26)):
        body += poly(c, r.choice(GREYS + [PINK, "#d6cbb8"]))
    for _ in range(5):
        x, y = r.uniform(30, 170), r.uniform(30, 170)
        body += poly([(x + r.uniform(-9, 9) + dx, y + r.uniform(-7, 7) + dy) for dx, dy in ((-8, -8), (8, -8), (8, 8), (-8, 8))], "#6b5538", sw=1)
    svg(body, "grenue")


def grenue_porph():
    r = random.Random(2)
    body = ""
    for c in voronoi(jitter_points(70, r, 17)):
        body += poly(c, r.choice(GREYS + [PINK]))
    for x, y, a in ((55, 60, 15), (140, 70, -20), (100, 145, 30)):
        body += rect(x, y, 46, 30, a, "#f6efe2", sw=1.6)
        body += rect(x, y, 46, 30, a, "none", sw=0.4)
    svg(body, "grenue_porph")


def micro_porph():
    r = random.Random(3)
    body = '<rect width="200" height="200" fill="#d4cfc4"/>'
    for _ in range(330):
        x, y = r.uniform(0, 200), r.uniform(0, 200)
        a = r.gauss(20, 25)
        body += rect(x, y, r.uniform(7, 11), 1.8, a, "#f3f1ea", stroke="#555", sw=0.35)
    for x, y, a, w, h in ((60, 70, 20, 40, 26), (135, 62, -15, 30, 22), (110, 140, 40, 38, 24)):
        body += rect(x, y, w, h, a, "#efe6d2", sw=1.6)
    svg(body, "micro_porph")


def ophitique():
    r = random.Random(4)
    body = '<rect width="200" height="200" fill="#d9b88f"/>'
    body += poly([(10, 40), (120, 10), (195, 90), (150, 190), (30, 170)], "#d9b88f", sw=1.6)
    body += poly([(-20, 150), (60, 110), (80, 215), (-20, 215)], "#cfa879", sw=1.4)
    for _ in range(46):
        x, y = r.uniform(10, 190), r.uniform(10, 190)
        body += rect(x, y, r.uniform(26, 40), 4.6, r.uniform(0, 180), "#f4f4f1", stroke="#444", sw=0.7)
    svg(body, "ophitique")


def intersertale():
    r = random.Random(5)
    body = '<rect width="200" height="200" fill="#4a5446"/>'
    for _ in range(62):
        x, y = r.uniform(-5, 205), r.uniform(-5, 205)
        body += rect(x, y, r.uniform(22, 36), 5, r.uniform(0, 180), "#f2f2ee", stroke="#2c2c2c", sw=0.6)
    svg(body, "intersertale")


def perlitique():
    r = random.Random(6)
    body = '<rect width="200" height="200" fill="#6e6a62"/>'
    for cx, cy in ((55, 60), (140, 55), (90, 130), (160, 145), (35, 150)):
        for k in range(1, 6):
            rad = 10 + k * 7
            body += f'<circle cx="{cx}" cy="{cy}" r="{rad}" fill="none" stroke="#2b2a27" stroke-width="1" stroke-dasharray="{r.randint(30, 80)} {r.randint(6, 20)}"/>'
    for _ in range(6):
        x, y = r.uniform(30, 170), r.uniform(30, 170)
        body += rect(x, y, 12, 8, r.uniform(0, 90), "#efeae0", sw=0.9)
    svg(body, "perlitique")


def pyro():
    r = random.Random(7)
    body = '<rect width="200" height="200" fill="#c9bfae"/>'
    for _ in range(26):
        x, y = r.uniform(5, 195), r.uniform(5, 195)
        n = r.randint(4, 6)
        rad = r.uniform(9, 20)
        pts = [(x + rad * r.uniform(0.5, 1) * math.cos(2 * math.pi * i / n + r.uniform(-.3, .3)), y + rad * r.uniform(0.5, 1) * math.sin(2 * math.pi * i / n)) for i in range(n)]
        body += poly(pts, r.choice(["#efe9db", "#e2d5bf", "#b7a789", "#f6f3ea"]), sw=1)
    for _ in range(7):  # ponces étirées
        x, y = r.uniform(20, 180), r.uniform(20, 180)
        body += f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{r.uniform(14, 22):.1f}" ry="{r.uniform(3, 5):.1f}" transform="rotate({r.uniform(-20, 20):.0f} {x:.1f} {y:.1f})" fill="#8c7e66" stroke="#3d4147" stroke-width="0.8"/>'
    for _ in range(12):  # tessons de verre en Y
        x, y = r.uniform(10, 190), r.uniform(10, 190)
        body += f'<path d="M{x:.1f},{y:.1f} l6,-9 M{x:.1f},{y:.1f} l7,8 M{x:.1f},{y:.1f} l-8,3" stroke="#2b2f33" stroke-width="1.6" fill="none" stroke-linecap="round"/>'
    svg(body, "pyro")


# ------------------------------------------------------------------ textures métamorphiques
def granoblastique():
    r = random.Random(8)
    body = ""
    for c in voronoi(lloyd(jitter_points(48, r, 20))):
        body += poly(c, r.choice(GREYS))
    svg(body, "granoblastique")


def lepidoblastique():
    r = random.Random(9)
    body = '<rect width="200" height="200" fill="#e6e0d3"/>'
    for _ in range(170):
        x, y = r.uniform(-5, 205), r.uniform(-5, 205)
        body += rect(x, y, r.uniform(26, 44), r.uniform(2.4, 4.2), r.gauss(-12, 4), r.choice(["#a98563", "#c6a47f", "#8f7355", "#e9dfc9", "#d8cfbd"]), stroke="#4a3f33", sw=0.5)
    svg(body, "lepidoblastique")


def porphyroblastique():
    r = random.Random(10)
    body = '<rect width="200" height="200" fill="#e0d9ca"/>'
    for _ in range(120):
        x, y = r.uniform(-5, 205), r.uniform(-5, 205)
        body += rect(x, y, r.uniform(22, 36), r.uniform(2.2, 3.5), r.gauss(-12, 4), r.choice(["#a98563", "#c6a47f", "#8f7355", "#e9dfc9"]), stroke="#4a3f33", sw=0.45)
    for x, y, rad, col in ((60, 65, 22, "#b8566a"), (135, 80, 18, "#b8566a"), (95, 145, 24, "#b8566a")):
        body += f'<circle cx="{x}" cy="{y}" r="{rad}" fill="{col}" stroke="#3d2a2f" stroke-width="1.8"/>'
        body += f'<circle cx="{x - rad * .25}" cy="{y - rad * .25}" r="{rad * .25}" fill="#d9899a" opacity=".6"/>'
    svg(body, "porphyroblastique")


def foliation_schiste():
    r = random.Random(11)
    body = '<rect width="200" height="200" fill="#e9e3d6"/>'
    y = -4
    while y < 210:
        body += f'<path d="M-5,{y:.1f} Q50,{y + r.uniform(-3, 3):.1f} 100,{y:.1f} T205,{y + r.uniform(-3, 3):.1f}" stroke="{r.choice(["#8f7355", "#b79b78", "#6f5a42"])}" stroke-width="{r.uniform(.8, 2):.1f}" fill="none"/>'
        y += r.uniform(3.5, 6)
    svg(body, "foliation_schiste")


def foliation_gneiss():
    r = random.Random(12)
    body = ""
    y = 0
    band = 0
    while y < 200:
        h = r.uniform(22, 34)
        if band % 2 == 0:
            body += f'<rect x="-5" y="{y:.1f}" width="210" height="{h:.1f}" fill="#efece4"/>'
            for c in voronoi([(x, y + h / 2 + r.uniform(-h / 3, h / 3)) for x in range(0, 210, 24)]):
                clip = [(px, min(max(py, y), y + h)) for px, py in c]
                body += poly(clip, r.choice(GREYS + [PINK]), sw=0.8)
        else:
            body += f'<rect x="-5" y="{y:.1f}" width="210" height="{h:.1f}" fill="#5b4a3b"/>'
            for _ in range(22):
                body += rect(r.uniform(0, 200), y + r.uniform(4, h - 4), r.uniform(14, 24), 3, r.gauss(0, 4), "#2b2118", stroke="#17110c", sw=0.4)
        y += h
        band += 1
    svg(body, "foliation_gneiss")


def orient_oui():
    foliation_schiste_body = random.Random(13)
    r = foliation_schiste_body
    body = '<rect width="200" height="200" fill="#e6e0d3"/>'
    for _ in range(120):
        body += rect(r.uniform(-5, 205), r.uniform(-5, 205), r.uniform(22, 36), r.uniform(3, 5), r.gauss(-15, 3), r.choice(["#a98563", "#c6a47f", "#8f7355", "#e9dfc9"]), stroke="#4a3f33", sw=0.5)
    body += '<path d="M30,160 L170,55" stroke="#d62828" stroke-width="2" marker-end="url(#a)"/>'
    svg('<defs><marker id="a" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#d62828"/></marker></defs>' + body, "orient_oui")


def orient_non():
    r = random.Random(14)
    body = '<rect width="200" height="200" fill="#e6e0d3"/>'
    for _ in range(100):
        body += rect(r.uniform(-5, 205), r.uniform(-5, 205), r.uniform(16, 28), r.uniform(8, 14), r.uniform(0, 180), r.choice(GREYS + ["#c6a47f"]), stroke="#4a3f33", sw=0.8)
    svg(body, "orient_non")


# ------------------------------------------------------------------ gisements (coupes)
def section(body, name):
    s = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="200" height="200">'
         f'<rect width="200" height="200" rx="10" fill="#cfe6f2"/>{body}</svg>')
    open(os.path.join(OUT, name + ".svg"), "w", encoding="utf-8").write(s)


GROUND = '<rect y="70" width="200" height="130" fill="#b9a583"/><rect y="70" width="200" height="6" fill="#7aa35f"/>' \
         '<path d="M0,110 H200 M0,140 H200 M0,170 H200" stroke="#9a875f" stroke-width="1.2"/>'


def g_pluto():
    section(GROUND + '<path d="M45,150 Q40,115 85,105 Q140,95 160,125 Q170,160 120,172 Q60,180 45,150 Z" fill="#c75b4a" stroke="#7a2e24" stroke-width="2"/>'
            '<text x="100" y="146" font-size="13" text-anchor="middle" fill="#fff" font-family="sans-serif">grains gros</text>'
            '<text x="100" y="40" font-size="12" text-anchor="middle" fill="#27465a" font-family="sans-serif">Profondeur : refroidissement lent</text>', "g_pluto")


def g_filon():
    section(GROUND + '<path d="M95,200 L100,70 L108,70 L106,200 Z" fill="#c75b4a" stroke="#7a2e24" stroke-width="2"/>'
            '<path d="M104,70 L180,60 M104,130 L170,118" stroke="#c75b4a" stroke-width="5" fill="none"/>'
            '<text x="100" y="40" font-size="12" text-anchor="middle" fill="#27465a" font-family="sans-serif">Filon : refroidissement moyen</text>', "g_filon")


def g_volc():
    section('<rect y="150" width="200" height="50" fill="#b9a583"/><path d="M10,150 L85,60 L115,60 L190,150 Z" fill="#8a7b66" stroke="#4d4333" stroke-width="2"/>'
            '<path d="M92,60 L100,18 L108,60 Z" fill="#c75b4a" opacity=".0"/><path d="M95,60 Q100,30 105,60 Z" fill="#e76f51"/>'
            '<path d="M100,60 L95,150 L105,150 Z" fill="#c75b4a"/><circle cx="125" cy="35" r="11" fill="#9a9a9a"/><circle cx="140" cy="24" r="14" fill="#b0b0b0"/>'
            '<text x="100" y="185" font-size="12" text-anchor="middle" fill="#27465a" font-family="sans-serif">Surface : refroidissement rapide</text>', "g_volc")


for fn in (grenue, grenue_porph, micro_porph, ophitique, intersertale, perlitique, pyro, granoblastique, lepidoblastique,
           porphyroblastique, foliation_schiste, foliation_gneiss, orient_oui, orient_non, g_pluto, g_filon, g_volc):
    fn()
print("ok", len(os.listdir(OUT)), "fichiers")

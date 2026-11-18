"""Génère static/img/hero-lame.svg : champ de microscope d'une lame mince de granodiorite (LPA).
Chaque grain reçoit les traits d'un vrai minéral : macles du plagioclase, quartz gris-blanc,
biotite brune à clivage fin, pyroxène/olivine à teintes vives. Lancer : python tools/make_hero.py"""
import math, os, random
import numpy as np
from scipy.spatial import Voronoi

OUT = os.path.join(os.path.dirname(__file__), "..", "static", "img", "hero-lame.svg")
W = 560; CX = CY = W / 2; R = 262
rnd = random.Random(21)

def seeds(n, md):
    P = []; t = 0
    while len(P) < n and t < 20000:
        t += 1
        x, y = rnd.uniform(-20, W + 20), rnd.uniform(-20, W + 20)
        if all((x - a) ** 2 + (y - b) ** 2 >= md * md for a, b in P): P.append((x, y))
    return P

def relax(P, it=1):
    for _ in range(it):
        cells = cells_of(P)
        P = [tuple(np.mean(c, axis=0)) for c in cells] if len(cells) == len(P) else P
    return P

def cells_of(P):
    pts = np.array(P)
    ring = [(CX + 1400 * math.cos(a), CY + 1400 * math.sin(a)) for a in np.linspace(0, 6.283, 20, endpoint=False)]
    v = Voronoi(np.vstack([pts, ring]))
    out = []
    for i in range(len(pts)):
        reg = v.regions[v.point_region[i]]
        if reg and -1 not in reg: out.append([tuple(v.vertices[j]) for j in reg])
    return out

def _wiggle(a, b):
    """Points intermédiaires d'une arête, identiques pour les deux grains voisins."""
    flip = (a > b)
    p, q = (b, a) if flip else (a, b)
    r = random.Random(hash((round(p[0], 1), round(p[1], 1), round(q[0], 1), round(q[1], 1))) & 0xffffffff)
    dx, dy = q[0] - p[0], q[1] - p[1]; L = math.hypot(dx, dy) or 1
    nx, ny = -dy / L, dx / L
    pts = []
    for t in (0.25, 0.5, 0.75):
        o = r.uniform(-1, 1) * min(5.5, L * 0.09)
        pts.append((p[0] + dx * t + nx * o, p[1] + dy * t + ny * o))
    return pts[::-1] if flip else pts

def irregular(poly):
    out = []
    for i, a in enumerate(poly):
        b = poly[(i + 1) % len(poly)]
        out.append(a); out.extend(_wiggle(a, b))
    return out

def ptxt(poly): return " ".join(f"{x:.1f},{y:.1f}" for x, y in poly)

defs = []; body = []
def stripes(poly, ang, step, cols, widths, jitter=0.0):
    xs = [p[0] for p in poly]; ys = [p[1] for p in poly]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    L = max(max(xs) - min(xs), max(ys) - min(ys)) * 0.9
    a = math.radians(ang); dx, dy = math.cos(a), math.sin(a); nx, ny = -dy, dx
    out = []; k = -L; i = 0
    while k < L:
        w = rnd.uniform(*widths)
        col = cols[i % len(cols)] if not isinstance(cols[0], list) else rnd.choice(cols[i % len(cols)])
        x1, y1 = cx + nx * k - dx * L, cy + ny * k - dy * L
        x2, y2 = cx + nx * k + dx * L, cy + ny * k + dy * L
        out.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{col}" stroke-width="{w:.2f}"/>')
        k += step * rnd.uniform(1 - jitter, 1 + jitter); i += 1
    return "".join(out)

def shade(base, f):
    base = base.lstrip("#"); r, g, b = (int(base[i:i + 2], 16) for i in (0, 2, 4))
    return "#%02x%02x%02x" % tuple(max(0, min(255, int(c * f))) for c in (r, g, b))

QUARTZ = ["#e4e2dc", "#f1efe7", "#d3d2cf", "#eee6c9", "#c9c9c8"]
PYX = ["#d9578f", "#3f9bd6", "#e7bf2e", "#4fb36b", "#e2793a"]
OLV = ["#c7479b", "#46b8ad", "#eacb3c", "#7b6fe0"]
MUSC = ["#f0d6f5", "#7fc8f2", "#f4e47e", "#f7a8c4"]

kinds = ["quartz"] * 22 + ["plagio"] * 20 + ["biotite"] * 9 + ["pyx"] * 6 + ["olv"] * 3 + ["musc"] * 5 + ["kspar"] * 7
rnd.shuffle(kinds)
P = relax(seeds(len(kinds) + 6, 50), 1)
cells = [irregular(c) for c in cells_of(P)]
for idx, poly in enumerate(cells):
    kind = kinds[idx % len(kinds)]
    cid = f"g{idx}"
    defs.append(f'<clipPath id="{cid}"><polygon points="{ptxt(poly)}"/></clipPath>')
    inner = ""
    ang = rnd.uniform(0, 180)
    if kind == "quartz":
        base = rnd.choice(QUARTZ)
        inner = f'<rect x="0" y="0" width="{W}" height="{W}" fill="{base}"/>'
        # extinction ondulante : bande plus sombre qui balaie le grain
        inner += stripes(poly, ang, 46, [shade(base, 0.9), base, shade(base, 1.04)], (14, 26), 0.3)
        inner += f'<rect x="0" y="0" width="{W}" height="{W}" fill="url(#vq)" opacity=".35"/>'
    elif kind == "plagio":
        a, b = rnd.choice([("#f2f2ef", "#8e9094"), ("#eceae4", "#a9acb3"), ("#f6f1e4", "#7d8087")])
        inner = f'<rect x="0" y="0" width="{W}" height="{W}" fill="{a}"/>'
        inner += stripes(poly, ang, 6.2, [b, a], (1.3, 3.8), 0.35)
    elif kind == "kspar":
        a, b = "#e8e4dc", "#c3c0ba"
        inner = f'<rect x="0" y="0" width="{W}" height="{W}" fill="{a}"/>'
        inner += stripes(poly, ang, 120, [b, a], (30, 60), 0.4)
        inner += stripes(poly, ang + 90, 11, [shade(a, .93), a], (1.2, 3), 0.4)
    elif kind == "biotite":
        base = rnd.choice(["#8a5a2b", "#a1692f", "#6e4521", "#b57a38"])
        inner = f'<rect x="0" y="0" width="{W}" height="{W}" fill="{base}"/>'
        inner += stripes(poly, ang, 4.2, ["#2c1a0b", base], (0.5, 1.5), 0.5)
        inner += stripes(poly, ang + 90, 9, [shade(base, 1.18), base], (1, 3), 0.6)
    elif kind == "pyx":
        base = rnd.choice(PYX)
        inner = f'<rect x="0" y="0" width="{W}" height="{W}" fill="{base}"/>'
        inner += stripes(poly, ang, 16, ["#1f1f2b", base], (0.8, 1.6), 0.25) + stripes(poly, ang + 90, 20, ["#1f1f2b", base], (0.8, 1.4), 0.3)
    elif kind == "olv":
        base = rnd.choice(OLV)
        inner = f'<rect x="0" y="0" width="{W}" height="{W}" fill="{base}"/>'
        xs = [p[0] for p in poly]; ys = [p[1] for p in poly]
        for _ in range(7):
            x, y = rnd.uniform(min(xs), max(xs)), rnd.uniform(min(ys), max(ys)); d = ""
            for s in range(5):
                d += f"{'M' if s == 0 else 'L'}{x:.1f},{y:.1f} "
                x += rnd.uniform(-22, 22); y += rnd.uniform(-22, 22)
            inner += f'<path d="{d}" fill="none" stroke="#2a2438" stroke-width="1.2" stroke-opacity=".7"/>'
    elif kind == "musc":
        base = rnd.choice(MUSC)
        inner = f'<rect x="0" y="0" width="{W}" height="{W}" fill="{base}"/>'
        inner += stripes(poly, ang, 5.5, [shade(base, .8), base], (0.6, 1.6), 0.5)
    body.append(f'<g clip-path="url(#{cid})">{inner}</g><polygon points="{ptxt(poly)}" fill="none" stroke="#111" stroke-width="1.5" stroke-linejoin="round"/>')

ticks = "".join(f'<line x1="{CX + (R - 18) * math.cos(a):.1f}" y1="{CY + (R - 18) * math.sin(a):.1f}" x2="{CX + (R - (30 if i % 5 == 0 else 24)) * math.cos(a):.1f}" y2="{CY + (R - (30 if i % 5 == 0 else 24)) * math.sin(a):.1f}" stroke="#ffffff" stroke-opacity=".55" stroke-width="{2 if i % 5 == 0 else 1}"/>'
                for i, a in enumerate(np.linspace(0, 6.283, 72, endpoint=False)))
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {W}" width="{W}" height="{W}" role="img" aria-label="Lame mince de granodiorite en lumière polarisée analysée : grains de quartz, plagioclases maclés, biotite et pyroxène">
<defs>
<radialGradient id="vq" cx=".5" cy=".5" r=".7"><stop offset="0" stop-color="#fff" stop-opacity=".0"/><stop offset="1" stop-color="#000" stop-opacity=".25"/></radialGradient>
<radialGradient id="vg" cx=".5" cy=".5" r=".5"><stop offset=".72" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".42"/></radialGradient>
<clipPath id="field"><circle cx="{CX}" cy="{CY}" r="{R}"/></clipPath>
{''.join(defs)}
</defs>
<circle cx="{CX}" cy="{CY}" r="{R + 14}" fill="#0d1520"/>
<circle cx="{CX}" cy="{CY}" r="{R + 6}" fill="none" stroke="#2a5db0" stroke-width="3"/>
<g clip-path="url(#field)"><rect width="{W}" height="{W}" fill="#111"/>{''.join(body)}
<circle cx="{CX}" cy="{CY}" r="{R}" fill="url(#vg)"/></g>
<line x1="{CX - 40}" y1="{CY}" x2="{CX + 40}" y2="{CY}" stroke="#fff" stroke-opacity=".7" stroke-width="1.4"/>
<line x1="{CX}" y1="{CY - 40}" x2="{CX}" y2="{CY + 40}" stroke="#fff" stroke-opacity=".7" stroke-width="1.4"/>
{ticks}
<g font-family="Public Sans, Arial, sans-serif" font-size="15" fill="#fff" fill-opacity=".9" font-weight="600">
<line x1="{CX + 70}" y1="{CY + R - 52}" x2="{CX + 170}" y2="{CY + R - 52}" stroke="#fff" stroke-width="3"/>
<text x="{CX + 70}" y="{CY + R - 62}">0,5 mm</text></g>
</svg>'''
open(OUT, "w", encoding="utf-8").write(svg)
print("ok", len(svg) // 1024, "Ko")

"""
Türzwerg – Verpackung (Umverpackung + Einleger), Variante „Mitte auf Mitte“
==========================================================================

Erzeugt aus den STEP-Dateien von Ring und Manschette:
  * Plotdateien für den Silhouette Cameo 4 (DXF R12 + SVG, Ebenen SCHNEIDEN / RILLEN)
  * ein 3D-Gesamtmodell (GLB für den Viewer, STEP zum Weiterkonstruieren)

Alle Maße in mm. Koordinaten im Karton:
  X = Breite (0 = Mitte), Y = Höhe (0 = Innenboden), Z = Tiefe (0 = Innenseite Rückwand).

Prinzip Einleger (Seitenansicht, ein Streifen, alle Falze quer):

      Z ^  ==================================================  Front des Kartons
        |  :  Seitenflansche (nach vorn, bis an die Front)    :
        |  ______________________________________________
        | |   Deck (Löcher, Schnurkanal)                   |
        | |___ Ringboden ____|‾‾‾‾‾‾|                       |
        |      Füße               |__ Manschettenboden ____|
        +---------------------------------------------------> Y   (Rückwand)
   Nach vorn hält der Einleger über die Seitenflansche, nach hinten über Manschettenboden
   und Füße. Eingeschoben wird er von oben.
   Ringmitte und Manschettenachse liegen auf derselben Höhe -> beide Schnurbohrungen
   liegen auf einer Linie, die Schnur läuft gerade. Restschnur unter dem Schnurboden.

Aufruf:  python generate.py          (benötigt: cadquery, shapely, ezdxf, trimesh)
"""
import json
import math
import os

import cadquery as cq
import ezdxf
from shapely import affinity
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
TEILE = os.path.join(HERE, "teile")

# --------------------------------------------------------------------------
# Parameter
# --------------------------------------------------------------------------
P = dict(
    t=0.45,            # Kartondicke (300–350 g/m² Faltschachtelkarton)
    # Umverpackung (Innenmaße) -> außen 97 x 146 x 24,5
    # gewählt für Standard-Versandkartons: 400x300x150 = 48 Stk (3 x 16), 300x200x150 = 24 Stk,
    # 600x400x150 = 96 Stk, jeweils 2–3 % Spiel (Hänger nach vorn umgeklappt)
    Wi=96.1, Hi=145.1, Di=23.6,
    tuck=15.0,         # Einstecklasche
    dust=18.0,         # Staublaschen
    glue=13.0,         # Klebelasche Faltschachtel
    # Aufhänger: volle Breite, doppellagig, klappt 90° nach vorn auf den Deckel
    hang_h=24.0,       # < Kartontiefe -> liegt umgeklappt ganz auf dem Deckel
    # Euroloch (DIN EN 13010 lt. Handelsangaben): 32 breit, 6 hoch, Mitte Ø10
    euro_w=32.0, euro_h=6.0, euro_d=10.0, euro_from_top=12.0,
    # Einleger
    ins_w=95.1,        # Breite (Karton innen 96,1)
    ins_h=143.6,       # Länge (Karton innen 145,1)
    gap=0.15,          # Manschette -> Innenseite Front (liegt fast an)
    deck_z=14.7,       # Deck knapp über Ringmitte/Manschettenachse (11,95)
    cord_floor_z=9.4,  # Schnurboden: knapp unter der Schnur
    ins_glue=10.0,
    ring_snap=0.35,    # Untermaß Ring- und Manschettenloch (beide rasten ein)
    slit=3.0, slit_pitch=8.0,
    leg_w=8.0,         # Füße unter dem Ringboden
    # Layout im Sichtfeld: Fenstergruppe senkrecht mittig (Rand oben = Rand unten)
    cord_visible=20.0,
    cord_slot=10.0,    # Kreuzschlitz im Schnurboden
    cord_chan=12.0,    # Schnurkanal im Deck
    # Fenster
    win_ring_r=36.5,   # Ring ganz sichtbar (er rastet im Deck ein)
    win_corner=1.0,    # Eckenradius Manschettenfenster (Fenster = Manschettenmaß 33 x 32)
)
p = P
t = p["t"]
R_RING = 36.0          # Ring außen (aus STEP)
RING_TH = 14.0
CUFF_D = 23.0
CUFF_L = 33.0
KEEL = 20.5            # Kiel unter Manschettenachse (aus STEP)

# Fenstergruppe: Ringfenster-Unterkante bis Manschetten-Oberkante, senkrecht mittig im Karton
WIN_GROUP = p["win_ring_r"] + R_RING + p["cord_visible"] + KEEL + CUFF_D / 2
MARGIN = (p["Hi"] - WIN_GROUP) / 2
Yr = MARGIN + p["win_ring_r"]                      # Ringmitte
Yc = Yr + R_RING + p["cord_visible"] + KEEL        # Manschettenachse
Z_CB = t                                           # Manschette liegt auf dem Boden an der Rückwand
Z_CUFF = Z_CB + CUFF_D / 2                         # Manschettenachse
Z_RING = Z_CUFF                                    # Ringmitte = Manschettenmitte
Z_RB = Z_RING - RING_TH / 2                        # Ringboden (Oberseite)
Z_S = p["cord_floor_z"]                            # Schnurboden (Oberseite)
ZD = p["deck_z"]
YS1, YS2 = Yr + R_RING + 2, Yc - KEEL - 2          # Stufen um das Schnur-Sichtfeld
Y_CORD = (Yr + R_RING + Yc - KEEL) / 2             # Mitte Schnur-Sichtfeld
assert abs(p["Di"] - Z_CB - CUFF_D - p["gap"]) < 0.01


# --------------------------------------------------------------------------
# Teile laden & Silhouetten bestimmen
# --------------------------------------------------------------------------
def load():
    ring = cq.importers.importStep(os.path.join(TEILE, "Ring_v2_FINAL.step")).val()
    cuff = cq.importers.importStep(os.path.join(TEILE, "Manschette_v2_FINAL_25mm.step")).val()
    return ring, cuff


def face_to_poly(shape, proj):
    tris = []
    for f in shape.Faces():
        verts, idx = f.tessellate(0.02, 0.2)
        pts = [proj(v) for v in verts]
        for a, b, c in idx:
            tri = Polygon([pts[a], pts[b], pts[c]])
            if tri.area > 1e-9:
                tris.append(tri.buffer(1e-4))
    return unary_union(tris).buffer(0)


def silhouettes(ring, cuff):
    """Größte Kontur in Blickrichtung. Beide Teile sind hohl -> konvexe Hülle."""
    pl = cq.Face.makePlane(200, 200, basePnt=cq.Vector(0, 0, 0), dir=cq.Vector(0, 0, 1))
    ring_sil = face_to_poly(ring.intersect(pl), lambda v: (v.x, v.y + Yr)).convex_hull
    pl = cq.Face.makePlane(200, 200, basePnt=cq.Vector(0, 0, 16.5), dir=cq.Vector(1, 0, 0))
    cuff_sil = face_to_poly(cuff.intersect(pl), lambda v: (v.z - CUFF_L / 2, v.y + Yc)).convex_hull
    return ring_sil, cuff_sil


# --------------------------------------------------------------------------
# 2D-Hilfen
# --------------------------------------------------------------------------
def rounded_rect(x0, y0, x1, y1, r):
    return box(x0 + r, y0 + r, x1 - r, y1 - r).buffer(r, resolution=16)


def euro_hole(cx, cy, flip=False):
    """Euroloch: Schlitz w x h mit runden Enden, mittige Ausbuchtung (Ø d) nach oben."""
    w, h, d = p["euro_w"], p["euro_h"], p["euro_d"]
    slot = LineString([(cx - w / 2 + h / 2, cy), (cx + w / 2 - h / 2, cy)]).buffer(h / 2, resolution=16)
    bump = Point(cx, cy - h / 2 + d / 2).buffer(d / 2, resolution=24)
    g = unary_union([slot, bump])
    if flip:
        g = affinity.scale(g, 1, -1, origin=(cx, cy))
    return g


def smooth(g, r):
    return g.buffer(r, resolution=16).buffer(-2 * r, resolution=16).buffer(r, resolution=16)


def cross_slit(cx, cy, s):
    h = s / 2
    return [[(cx - h, cy - h), (cx + h, cy + h)], [(cx - h, cy + h), (cx + h, cy - h)]]


def slits_along(poly, pitch, length, skip=None):
    """Radiale Schlitze nach außen entlang einer Lochkontur (Haltezungen)."""
    ring = poly.exterior
    n = max(int(ring.length // pitch), 1)
    out = []
    for i in range(n):
        s = (i + 0.5) * ring.length / n
        a, b, m = ring.interpolate(s - 0.5), ring.interpolate(s + 0.5), ring.interpolate(s)
        dx, dy = b.x - a.x, b.y - a.y
        nl = math.hypot(dx, dy) or 1
        nx, ny = dy / nl, -dx / nl
        if poly.contains(Point(m.x + nx * 0.3, m.y + ny * 0.3)):
            nx, ny = -nx, -ny
        if skip is None or not skip(m.x, m.y):
            out.append([(m.x, m.y), (m.x + nx * length, m.y + ny * length)])
    return out


def legs():
    """Füße unter dem Ringboden (x0, x1, y_falz, y_ende) – liegen unter dem Ringrand, verdeckt."""
    w, L = p["leg_w"], Z_RB - t
    out = []
    for sx in (-1, 1):
        x0, x1 = sorted((sx * 17.0, sx * (17.0 + w)))
        out.append((x0, x1, Yr + 21.0, Yr + 21.0 + L))
        out.append((x0, x1, Yr - 21.0, Yr - 21.0 - L))
    return out


# --------------------------------------------------------------------------
# Zuschnitt Umverpackung
# --------------------------------------------------------------------------
def box_blank(window):
    Wp, Dp, Hp = p["Wi"] + t, p["Di"] + t, p["Hi"] + t
    tk, du, gl, hh = p["tuck"], p["dust"], p["glue"], p["hang_h"]
    xB0, xB1 = 0.0, Wp              # Rückwand
    xS1 = xB1 + Dp                  # Seite A
    xF0, xF1 = xS1, xS1 + Wp        # Front
    xS2 = xF1 + Dp                  # Seite B
    parts, scores = [], []

    parts.append(box(xB0, 0, xS2, Hp))
    for x in (xB1, xS1, xF1):
        scores.append([(x, 0), (x, Hp)])
    parts.append(Polygon([(0, 0), (-gl, 6), (-gl, Hp - 6), (0, Hp)]))
    scores.append([(0, 0), (0, Hp)])

    # Deckel + Einstecklasche oben/unten (an der Front), Staublaschen an den Seiten
    for sgn, y0 in ((1, Hp), (-1, 0)):
        y1 = y0 + sgn * Dp
        parts.append(box(xF0, min(y0, y1), xF1, max(y0, y1)))
        tuck = rounded_rect(xF0 + 1.0, 0, xF1 - 1.0, tk + 6, 6).intersection(box(xF0, 0, xF1, tk))
        tuck = affinity.translate(tuck, 0, y1) if sgn > 0 else affinity.translate(affinity.scale(tuck, 1, -1, origin=(0, 0)), 0, y1)
        parts.append(tuck)
        scores.append([(xF0, y0), (xF1, y0)])
        scores.append([(xF0 + 1.0, y1), (xF1 - 1.0, y1)])
        for xa, xb in ((xB1, xS1), (xF1, xS2)):
            pts = [(xa + 0.5, 0), (xa + 0.5, du - 7), (xa + 7, du), (xb - 3, du), (xb - 0.5, du - 3), (xb - 0.5, 0)]
            parts.append(Polygon([(x, y0 + sgn * y) for x, y in pts]))
            scores.append([(xa + 0.5, y0), (xb - 0.5, y0)])

    # Aufhänger: volle Breite, doppellagig, Falz an der Oberkante (klappt 90° nach vorn)
    cx = Wp / 2
    hang = rounded_rect(xB0, Hp - 10, xB1, Hp + hh, 5).intersection(box(xB0, Hp, xB1, Hp + hh))
    valleys = [[(xB0 + 0.5, Hp), (xB1 - 0.5, Hp)]]   # Hänger klappt nur zum Versand nach vorn
    yd0, yd1 = Hp + hh, Hp + 2 * hh - 1.0      # 1 mm kürzer: Platz für den Falz beim Umklappen
    dbl = rounded_rect(xB0 + 0.75, yd0, xB1 - 0.75, yd1 + 10, 5).intersection(box(xB0, yd0, xB1, yd1))
    scores.append([(xB0 + 0.75, yd0), (xB1 - 0.75, yd0)])
    parts += [hang, dbl]

    outline = unary_union([q.buffer(0.001) for q in parts]).buffer(-0.001)
    holes = [
        euro_hole(cx, Hp + hh - p["euro_from_top"]),
        euro_hole(cx, Hp + hh + p["euro_from_top"], flip=True),
        affinity.translate(window, xF0 + Wp / 2, 0),
    ]
    return dict(outline=outline, holes=holes, cuts=[], scores=scores, valleys=valleys)


# --------------------------------------------------------------------------
# Zuschnitt Einleger (ein Streifen, Falze parallel zur Breite)
# --------------------------------------------------------------------------
def insert_layout():
    H = p["ins_h"]
    return [
        ("Klebelasche", p["ins_glue"]),
        ("Manschettenboden", H - YS2),
        ("Stufe hinten", Z_S - t),
        ("Schnurboden", YS2 - YS1),
        ("Stufe vorn", Z_S - Z_RB),
        ("Ringboden", YS1),
        ("Wand unten", ZD - Z_RB),
        ("Deck", H),
        ("Wand oben", ZD - t),
    ]


def flange_height():
    """Seitenflansche klappen nach vorn bis an die Front (0,2 mm Luft)."""
    return p["Di"] - ZD - t / 2 - 0.2


def insert_blank(deck_hole, slit_lines):
    W, H = p["ins_w"], p["ins_h"]
    v, pos = 0.0, {}
    for name, L in insert_layout():
        pos[name] = (v, v + L)
        v += L
    u0, u1 = -W / 2, W / 2
    parts, scores, valleys, cuts = [], [], [], []
    for name, (a, b) in pos.items():
        if name == "Klebelasche":
            parts.append(Polygon([(u0 + 5, a), (u1 - 5, a), (u1, b), (u0, b)]))
        else:
            parts.append(box(u0, a, u1, b))
    for name, (a, b) in list(pos.items())[1:]:
        # Schnurboden liegt höher als seine Nachbarn -> beide Falze daran sind Talfalze
        (valleys if name in ("Schnurboden", "Stufe vorn") else scores).append([(u0, a), (u1, a)])

    # Deck: Y = v - vD0 ; Seitenflansche klappen nach vorn bis an die Front des Kartons
    vD0, vD1 = pos["Deck"]
    hF = flange_height()
    for sgn in (-1, 1):
        e = sgn * W / 2
        f = [(0, 1), (hF, 3), (hF, H - 3), (0, H - 1)]
        parts.append(Polygon([(e + sgn * h, vD0 + y) for h, y in f]))
        valleys.append([(e, vD0 + 1), (e, vD1 - 1)])
    hole = affinity.translate(deck_hole, 0, vD0)
    cuts += [[(a, b + vD0) for a, b in sl] for sl in slit_lines]

    # Ringboden: Y = vR1 - v ; Füße (Falz unten am Fuß, nicht gerillt an den Seiten)
    vR0, vR1 = pos["Ringboden"]
    for x0, x1, yf, ye in legs():
        cuts.append([(x0, vR1 - yf), (x0, vR1 - ye), (x1, vR1 - ye), (x1, vR1 - yf)])
        valleys.append([(x0, vR1 - yf), (x1, vR1 - yf)])
    # Schnurboden: Y = YS1 + (vS1 - v) ; Kreuzschlitz für die Restschnur
    vS0, vS1 = pos["Schnurboden"]
    cuts += cross_slit(0, vS1 - (Y_CORD - YS1), p["cord_slot"])

    outline = unary_union([q.buffer(0.001) for q in parts]).buffer(-0.001)
    return dict(outline=outline, holes=[hole], cuts=cuts, scores=scores, valleys=valleys)


# --------------------------------------------------------------------------
# Export 2D
# --------------------------------------------------------------------------
def geom_lines(g):
    if g.geom_type == "Polygon":
        yield list(g.exterior.coords)
        for i in g.interiors:
            yield list(i.coords)
    elif g.geom_type in ("MultiPolygon", "GeometryCollection"):
        for q in g.geoms:
            yield from geom_lines(q)
    elif g.geom_type == "LineString":
        yield list(g.coords)


def blank_paths(b):
    cut = list(geom_lines(b["outline"]))
    for h in b["holes"]:
        cut += list(geom_lines(h))
    cut += b.get("cuts", [])
    return cut, b["scores"], b.get("valleys", [])


LAYERS = [("SCHNEIDEN", 1, "#e00000", None), ("RILLEN_BERG", 5, "#0050ff", "3,1.5"),
          ("RILLEN_TAL", 3, "#00a040", "1,1.5")]


def bounds(paths):
    pts = [q for pl in paths for q in pl]
    return (min(x for x, _ in pts), min(y for _, y in pts), max(x for x, _ in pts), max(y for _, y in pts))


def save_dxf(fn, layers, origin, marks=None):
    """DXF R12 in mm. origin: wird auf (0,0) gelegt. marks: Passerecken (gleiche Hüllbox in allen Teildateien)."""
    ox, oy = origin
    doc = ezdxf.new("R12")
    msp = doc.modelspace()
    for lname, col, pls in layers:
        doc.layers.new(lname, dxfattribs={"color": col})
        for pl in pls:
            pts = [(x - ox, y - oy) for x, y in pl]
            closed = len(pts) > 2 and math.dist(pts[0], pts[-1]) < 1e-6
            msp.add_polyline2d(pts[:-1] if closed else pts, close=closed, dxfattribs={"layer": lname, "color": col})
    if marks:
        doc.layers.new("PASSER", dxfattribs={"color": 7})
        x0, y0, x1, y1 = marks
        for pl in ([(x0 + 4, y0), (x0, y0), (x0, y0 + 4)], [(x1 - 4, y1), (x1, y1), (x1, y1 - 4)]):
            msp.add_polyline2d([(x - ox, y - oy) for x, y in pl], dxfattribs={"layer": "PASSER", "color": 7})
    doc.saveas(fn)


def save_svg(fn, groups, bb, margin=8.0):
    x0, y0, x1, y1 = bb
    W, H = x1 - x0 + 2 * margin, y1 - y0 + 2 * margin
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.2f}mm" height="{H:.2f}mm" viewBox="0 0 {W:.2f} {H:.2f}">']
    for (lname, _, color, dash), pls in zip(LAYERS, groups):
        da = f' stroke-dasharray="{dash}"' if dash else ""
        out.append(f'<g id="{lname}" fill="none" stroke="{color}" stroke-width="0.25"{da}>')
        for pl in pls:
            out.append('<path d="M' + " L".join(f"{x - x0 + margin:.3f},{H - (y - y0 + margin):.3f}" for x, y in pl) + '"/>')
        out.append("</g>")
    out.append("</svg>")
    with open(fn, "w") as f:
        f.write("\n".join(out))


# Falzlinien als Perforation (für Schneidplotter ohne Rillwerkzeug):
# Bergfalz lange Schnitte, Talfalz kurze Schnitte -> am Teil erkennbar. Beginnt und endet mit Steg.
PERF = {"berg": (2.5, 2.0), "tal": (1.2, 1.5)}


def perforate(lines, cut, gap):
    out = []
    for pl in lines:
        ls = LineString(pl)
        L = ls.length
        n = max(int((L - gap) // (cut + gap)), 1)
        rest = L - n * cut - (n - 1) * gap          # gleichmäßig verteilen: Steg an beiden Enden
        s = rest / 2
        for _ in range(n):
            a, b = ls.interpolate(s), ls.interpolate(min(s + cut, L))
            out.append([(a.x, a.y), (b.x, b.y)])
            s += cut + gap
    return out


def write_files(name, cut, mountain, valley):
    bb = bounds(cut + mountain + valley)
    o = bb[:2]
    save_dxf(os.path.join(OUT, f"{name}_komplett.dxf"),
             [("SCHNEIDEN", 1, cut), ("RILLEN_BERG", 5, mountain), ("RILLEN_TAL", 3, valley)], o)
    save_dxf(os.path.join(OUT, f"{name}_schneiden.dxf"), [("SCHNEIDEN", 1, cut)], o, marks=bb)
    save_dxf(os.path.join(OUT, f"{name}_rillen.dxf"), [("RILLEN_BERG", 5, mountain), ("RILLEN_TAL", 3, valley)], o, marks=bb)
    save_svg(os.path.join(OUT, f"{name}.svg"), [cut, mountain, valley], bb)
    write_perforated(name, cut, mountain, valley, o)
    return bb[2] - bb[0], bb[3] - bb[1]


def write_perforated(name, cut, mountain, valley, origin):
    """Alles rot, ein einziger Schneidauftrag. Falzlinien als Perforation."""
    pb, pt = perforate(mountain, *PERF["berg"]), perforate(valley, *PERF["tal"])
    save_dxf(os.path.join(OUT, f"{name}_perforiert.dxf"),
             [("SCHNEIDEN", 1, cut), ("FALZ_BERG_PERFO", 1, pb), ("FALZ_TAL_PERFO", 1, pt)], origin)
    bb = bounds(cut + mountain + valley)
    save_svg(os.path.join(OUT, f"{name}_perforiert.svg"), [cut + pb + pt, [], []], bb)


def write_sheet(box_paths, ins_paths, gap=12.0):
    """Beide Teile auf einem Bogen für die 12×24″-Matte (305 × 610 mm)."""
    bb_b, bb_i = bounds(sum(box_paths, [])), bounds(sum(ins_paths, []))
    def move(paths, bb, dx, dy):
        return [[[(x - bb[0] + dx, y - bb[1] + dy) for x, y in pl] for pl in grp] for grp in paths]
    hb = bb_b[3] - bb_b[1]
    b = move(box_paths, bb_b, 0, 0)
    i = move(ins_paths, bb_i, 0, hb + gap)
    groups = [b[k] + i[k] for k in range(3)]
    bb = bounds(sum(groups, []))
    save_dxf(os.path.join(OUT, "Bogen_12x24_komplett.dxf"),
             [("SCHNEIDEN", 1, groups[0]), ("RILLEN_BERG", 5, groups[1]), ("RILLEN_TAL", 3, groups[2])], bb[:2])
    save_svg(os.path.join(OUT, "Bogen_12x24.svg"), groups, bb)
    write_perforated("Bogen_12x24", groups[0], groups[1], groups[2], bb[:2])
    return bb[2] - bb[0], bb[3] - bb[1]


# --------------------------------------------------------------------------
# 3D-Modell
# --------------------------------------------------------------------------
def extrude_xy(poly, z0, th):
    solid = cq.Workplane("XY").workplane(offset=z0).polyline(list(poly.exterior.coords)[:-1]).close().extrude(th)
    for hole in poly.interiors:
        h = cq.Workplane("XY").workplane(offset=z0 - 1).polyline(list(hole.coords)[:-1]).close().extrude(th + 2)
        solid = solid.cut(h)
    return solid


def blk(x0, x1, y0, y1, z0, z1):
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))


def extrude_yz(poly, x0, th):
    pts = [(y, z) for y, z in list(poly.exterior.coords)[:-1]]
    return cq.Workplane("YZ").workplane(offset=x0).polyline(pts).close().extrude(th)


def rod(a, b, r=2.0):
    a, b = cq.Vector(*a), cq.Vector(*b)
    return cq.Solid.makeCylinder(r, (b - a).Length, a, (b - a).normalized())


def build_3d(ring, cuff, window, deck_hole):
    Wi, Hi, Di, hh = p["Wi"], p["Hi"], p["Di"], p["hang_h"]
    X0, X1 = -Wi / 2 - t, Wi / 2 + t
    # Umverpackung
    front = extrude_xy(box(X0, -t, X1, Hi + t).difference(window), Di, t)
    shell = (front.union(blk(X0, X1, -t, Hi + t, -t, 0))
             .union(blk(X0, -Wi / 2, -t, Hi + t, 0, Di)).union(blk(Wi / 2, X1, -t, Hi + t, 0, Di))
             .union(blk(-Wi / 2, Wi / 2, -t, 0, 0, Di)))
    lid = blk(-Wi / 2, Wi / 2, Hi, Hi + t, 0, Di + t).union(blk(-Wi / 2 + 1, Wi / 2 - 1, Hi - p["tuck"], Hi, t, 2 * t))
    # Aufhänger (aufgestellt): Rückwandlage + Doppelung, Euroloch
    eh = euro_hole(0, Hi + hh - p["euro_from_top"])
    hang = rounded_rect(X0, Hi - 10, X1, Hi + hh, 5).intersection(box(X0, Hi + t, X1, Hi + hh)).difference(eh)
    dbl = rounded_rect(X0 + 0.75, Hi + 1.0 + t - 10, X1 - 0.75, Hi + hh, 5).intersection(
        box(X0, Hi + 1.0 + t, X1, Hi + hh)).difference(eh)
    hanger = extrude_xy(hang, -t, t).union(extrude_xy(dbl, 0, t))

    # Einleger
    W, H = p["ins_w"], p["ins_h"]
    u0, u1 = -W / 2, W / 2
    deck = extrude_xy(box(u0, 0, u1, H).difference(deck_hole), ZD - t / 2, t)
    leg_holes = unary_union([box(x0, min(yf, ye), x1, max(yf, ye)) for x0, x1, yf, ye in legs()])
    floor_r = extrude_xy(box(u0, 0, u1, YS1).difference(leg_holes), Z_RB - t, t)
    floor_s = extrude_xy(box(u0, YS1, u1, YS2).difference(Point(0, Y_CORD).buffer(2.5)), Z_S - t, t)
    floor_c = blk(u0, u1, YS2, H, 0, t)
    insert = (deck.union(floor_r).union(floor_s).union(floor_c)
              .union(blk(u0, u1, YS1 - t, YS1, Z_RB - t, Z_S))       # Stufe vorn
              .union(blk(u0, u1, YS2, YS2 + t, 0, Z_S))              # Stufe hinten
              .union(blk(u0, u1, 0, t, Z_RB, ZD))                    # Wand unten
              .union(blk(u0, u1, H - t, H, 0, ZD)))                  # Wand oben
    for x0, x1, yf, ye in legs():
        insert = insert.union(blk(x0, x1, yf - t / 2, yf + t / 2, 0, Z_RB - t))
    hF = flange_height()
    fl = Polygon([(1, ZD), (H - 1, ZD), (H - 3, ZD + hF), (3, ZD + hF)])
    for x0 in (u0, u1 - t):
        insert = insert.union(extrude_yz(fl, x0, t))

    # Schnur: gerade auf Höhe der Bohrungen, mittig Kreuzschlitz, Rest als Schlaufen im Schnurfach
    zc, ym = Z_CUFF, Y_CORD
    segs = [rod((0, Yc - KEEL + 2, zc), (0, ym + 1.8, zc)), rod((0, ym + 1.8, zc), (0, ym, Z_S - 2.5)),
            rod((0, ym, Z_S - 2.5), (0, ym - 1.8, zc)), rod((0, ym - 1.8, zc), (0, Yr + R_RING - 2, zc))]
    for dy, z in ((-4, 2.6), (4, 2.6), (-4, 6.4), (4, 6.4)):
        segs.append(rod((-38, ym + dy, z), (38, ym + dy, z)))
    segs += [rod((0, ym, Z_S - 2.5), (6, ym + 4, 6.4)), rod((0, ym, Z_S - 2.5), (-6, ym - 4, 6.4))]
    cord = cq.Workplane().add(segs[0])
    for sg in segs[1:]:
        cord = cord.union(cq.Workplane().add(sg))

    ring_s = cq.Workplane().add(ring).translate((0, Yr, Z_RING))
    cuff_s = cq.Workplane().add(cuff).rotate((0, 0, 0), (0, 1, 0), 90).translate((-CUFF_L / 2, Yc, Z_CUFF))
    parts = [
        ("Umverpackung", shell, (0.96, 0.95, 0.92)),
        ("Aufhaenger", hanger, (0.96, 0.95, 0.92)),
        ("Deckel", lid, (0.96, 0.95, 0.92)),
        ("Einleger", insert, (0.80, 0.66, 0.46)),
        ("Ring", ring_s, (0.84, 1.0, 0.12)),
        ("Manschette", cuff_s, (0.84, 1.0, 0.12)),
        ("Schnur", cord, (0.55, 0.12, 0.10)),
    ]
    assy = cq.Assembly(name="Tuerzwerg_Verpackung")
    for name, shp, col in parts:
        assy.add(shp, name=name, color=cq.Color(*col))
    assy.export(os.path.join(OUT, "Tuerzwerg_Verpackung.step"))
    write_glb(parts, os.path.join(OUT, "Tuerzwerg_Verpackung.glb"))


def write_glb(parts, fn):
    """Ein Mesh pro Bauteil (für den Web-Viewer). Achsen: Y oben, Z nach vorn."""
    import numpy as np
    import trimesh
    scene = trimesh.Scene()
    for name, shp, col in parts:
        verts, faces = [], []
        for solid in shp.vals():
            v, f = solid.tessellate(0.05, 0.2)
            off = len(verts)
            verts += [(q.x, q.y, q.z) for q in v]
            faces += [(a + off, b + off, c + off) for a, b, c in f]
        m = trimesh.Trimesh(np.array(verts) / 1000.0, np.array(faces), process=True)
        m.visual = trimesh.visual.ColorVisuals(m, face_colors=[int(c * 255) for c in col] + [255])
        scene.add_geometry(m, node_name=name, geom_name=name)
    scene.export(fn)


# --------------------------------------------------------------------------
def main():
    os.makedirs(OUT, exist_ok=True)
    ring, cuff = load()
    ring_sil, cuff_sil = silhouettes(ring, cuff)

    ring_hole = ring_sil.buffer(-p["ring_snap"], resolution=32)     # Ring rastet ein
    cuff_hole = cuff_sil.buffer(-p["ring_snap"], resolution=8)      # Manschette rastet ebenfalls ein
    ch = p["cord_chan"] / 2
    channel = box(-ch, Yr + R_RING - 4, ch, Yc - KEEL + 2)
    deck_hole = smooth(unary_union([ring_hole, cuff_hole, channel]), 0.8)

    def skip_r(x, y):  # Ring: keine Zungen am Schnurkanal
        return y > Yr + R_RING - 9 and abs(x) < ch + 7
    def skip_c(x, y):  # Manschette: keine Zungen am Schnurkanal
        return y < Yc - KEEL + 1 and abs(x) < ch + 4
    slit_lines = (slits_along(smooth(ring_hole, 0.8), p["slit_pitch"], p["slit"], skip_r)
                  + slits_along(smooth(cuff_hole, 0.8), p["slit_pitch"], p["slit"], skip_c))

    cb = cuff_sil.bounds   # Manschettenfenster = Manschettenmaß
    window = unary_union([
        Point(0, Yr).buffer(p["win_ring_r"], resolution=64),
        rounded_rect(cb[0], cb[1], cb[2], cb[3], p["win_corner"]),
        box(-6, Yr + R_RING - 2, 6, cb[1] + 1),
    ])
    window = window.buffer(2, resolution=16).buffer(-2, resolution=16)   # Übergänge zum Kanal ausrunden

    box_paths = blank_paths(box_blank(window))
    ins_paths = blank_paths(insert_blank(deck_hole, slit_lines))
    sizes = {"Umverpackung": write_files("Umverpackung", *box_paths),
             "Einleger": write_files("Einleger", *ins_paths),
             "Bogen_12x24": write_sheet(box_paths, ins_paths)}
    build_3d(ring, cuff, window, deck_hole)

    info = dict(params=P, Yr=Yr, Yc=Yc, Y_cord=Y_CORD, deck_Z=ZD, split_y1=YS1, split_y2=YS2,
                ring_bottom=Yr - R_RING, margin_top_bottom=round(MARGIN, 2),
                cuff_window_mm=[round(cb[2] - cb[0], 1), round(cb[3] - cb[1], 1)],
                ring_floor_Z=round(Z_RB, 2), cord_floor_Z=Z_S, cuff_floor_Z=round(Z_CB, 2),
                ring_center_Z=round(Z_RING, 2), cuff_axis_Z=round(Z_CUFF, 2),
                ring_front_gap=round(p["Di"] - Z_RB - RING_TH, 2), cuff_front_gap=p["gap"],
                outer_mm=[round(p["Wi"] + 2 * t, 1), round(p["Hi"] + 2 * t, 1), round(p["Di"] + 2 * t, 1)],
                window_bounds=[round(v, 2) for v in window.bounds],
                insert_panels={k: round(L, 2) for k, L in insert_layout()},
                cord_store_mm=[p["ins_w"], YS2 - YS1, round(Z_S - 2 * t, 2)],
                n_slits=len(slit_lines),
                blank_sizes_mm={k: [round(v, 1) for v in s] for k, s in sizes.items()})
    with open(os.path.join(OUT, "masse.json"), "w") as f:
        json.dump(info, f, indent=2, ensure_ascii=False)
    print(json.dumps({k: v for k, v in info.items() if k != "params"}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

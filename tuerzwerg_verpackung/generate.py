"""
Türzwerg – Verpackung (Umverpackung + Einleger)
================================================

Erzeugt aus den STEP-Dateien von Ring und Manschette:
  * Plotdateien für den Silhouette Cameo 4 (DXF R12 + SVG, Ebenen SCHNEIDEN / RILLEN)
  * ein 3D-Gesamtmodell (GLB für den Viewer, STEP zum Weiterkonstruieren)

Alle Maße in mm. Koordinaten im Karton:
  X = Breite (0 = Mitte), Y = Höhe (0 = Innenboden), Z = Tiefe (0 = Innenseite Rückwand).

Prinzip Einleger (Seitenansicht, ein Streifen, alle Falze quer):

      Z ^           Deck (Löcher)                    Front des Kartons
        |   Wb  ____________________________  Wt
        |   |  |                            |  |
        |   |__| Ringboden  ________   R    |  |
        |        (Schnurfach darunter)  |___|__|  Manschettenboden
        +---------------------------------------> Y
          Ring liegt auf dem Ringboden, Manschette auf dem Manschettenboden.
          Beide Böden sind so hoch, dass die Vorderseiten gleich weit (0,5 mm) hinter der Front liegen.

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
    # Umverpackung (Innenmaße) -> außen ca. 90 x 140 x 25
    Wi=89.0, Hi=139.0, Di=24.0,
    tuck=15.0,         # Einstecklasche
    dust=18.0,         # Staublaschen
    glue=13.0,         # Klebelasche Faltschachtel
    # Aufhänger: volle Breite, doppellagig, für den Transport nach hinten klappbar
    hang_h=35.0,
    lock_w=30.0,       # Verriegelungszunge (steckt im Deckelschlitz, hält den Hänger senkrecht)
    lock_l=11.0,
    lock_slit_z=8.5,   # Schlitz im Deckel, Abstand zur Rückwand
    # Euroloch (DIN EN 13010 lt. Handelsangaben): 32 breit, 6 hoch, Mitte Ø10
    euro_w=32.0, euro_h=6.0, euro_d=10.0, euro_from_top=14.0,
    # Einleger
    ins_w=88.0,        # Breite (Karton innen 89)
    ins_h=136.0,       # Länge (3 mm Luft oben für die Verriegelungszunge)
    gap=0.55,          # Abstand Vorderseite Ring/Manschette -> Innenseite Front
    deck_z=14.2,       # Deckhöhe: liegt bei beiden Teilen nahe der breitesten Stelle
    split_y=91.0,      # Stufe zwischen Ringboden und Manschettenboden
    ins_glue=10.0,
    hole_clear=0.25,   # Luft rund um die Teile im Deck (Teile fallen hinein)
    # Layout im Sichtfeld (Y = Höhe ab Innenboden)
    ring_bottom=5.0,   # Unterkante Ring
    cord_visible=20.0, # Schnur-Sichtfeld zwischen Ring und Manschette
    cord_slot_y=84.0,  # Kreuzschlitz im Ringboden: hier taucht die Restschnur ab
    cord_slot=12.0,    # Größe Kreuzschlitz
    cord_chan=12.0,    # Breite Schnurkanal im Deck
    # Fenster (etwas kleiner als die Teile -> sie können nicht nach vorn heraus)
    win_ring_r=33.5,   # Ring Ø72 -> 2,5 mm Rand deckt die Rundung ab
    win_cuff_x=14.5,   # Manschette 33 lang -> 2 mm Rand an den Stirnseiten
)
p = P
t = p["t"]
R_RING = 36.0          # Ring außen (aus STEP)
RING_TH = 14.0
CUFF_D = 23.0
CUFF_L = 33.0
KEEL = 20.5            # Kiel unter Manschettenachse (aus STEP)

Yr = p["ring_bottom"] + R_RING                     # Ringmitte
Yc = Yr + R_RING + p["cord_visible"] + KEEL        # Manschettenachse
Z_FRONT = p["Di"] - p["gap"]                       # Vorderseite beider Teile
Z_CB = Z_FRONT - CUFF_D                            # Manschettenboden (Oberseite)
Z_RB = Z_FRONT - RING_TH                           # Ringboden (Oberseite)
Z_RING = Z_RB + RING_TH / 2
Z_CUFF = Z_CB + CUFF_D / 2
ZD = p["deck_z"]
assert abs(Z_CB - t) < 0.2, "Manschettenboden muss auf der Rückwand liegen -> Di = 23 + gap + t wählen"


# --------------------------------------------------------------------------
# Teile laden & Silhouetten bestimmen
# --------------------------------------------------------------------------
def load():
    ring = cq.importers.importStep(os.path.join(TEILE, "Ring_v2_FINAL.step")).val()
    cuff = cq.importers.importStep(os.path.join(TEILE, "Manschette_v2_FINAL_25mm.step")).val()
    return ring, cuff


def face_to_poly(shape, proj):
    """Schnittfläche triangulieren -> shapely-Polygon (proj: Vector -> (u,v))."""
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
    """Größte Kontur in Blickrichtung (Ring: Äquator, Manschette: Achsebene).
    Beide Teile sind hohl -> konvexe Hülle = gefüllte Außenkontur."""
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
    parts, scores, cuts = [], [], []

    # Hauptpaneele + Klebelasche an der Rückwand
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

    # Schlitz im oberen Deckel für die Verriegelungszunge
    cxF = xF0 + Wp / 2
    ys = Hp + Dp - p["lock_slit_z"]          # Deckel: y=Hp an der Front, y=Hp+Dp an der Rückwand
    cuts.append([(cxF - p["lock_w"] / 2 - 0.5, ys), (cxF + p["lock_w"] / 2 + 0.5, ys)])

    # Aufhänger: volle Breite, Falz an der Oberkante (klappbar), Doppelung + Verriegelungszunge
    cx = Wp / 2
    hang = rounded_rect(xB0, Hp - 10, xB1, Hp + hh, 6).intersection(box(xB0, Hp, xB1, Hp + hh))
    scores.append([(xB0 + 0.5, Hp), (xB1 - 0.5, Hp)])
    yd0, yd1 = Hp + hh, Hp + 2 * hh - 0.6
    dbl = rounded_rect(xB0 + 0.75, yd0, xB1 - 0.75, yd1 + 10, 6).intersection(box(xB0, yd0, xB1, yd1))
    scores.append([(xB0 + 0.75, yd0), (xB1 - 0.75, yd0)])
    lw, ll = p["lock_w"], p["lock_l"]
    neck = p["lock_slit_z"] - 0.5            # bis zur Schulter
    tongue = Polygon([(cx - lw / 2, yd1), (cx - lw / 2, yd1 + neck), (cx - lw / 2 - 2, yd1 + neck + 0.8),
                      (cx - lw / 2 + 2, yd1 + ll), (cx + lw / 2 - 2, yd1 + ll),
                      (cx + lw / 2 + 2, yd1 + neck + 0.8), (cx + lw / 2, yd1 + neck), (cx + lw / 2, yd1)])
    scores.append([(cx - lw / 2, yd1), (cx + lw / 2, yd1)])
    parts += [hang, dbl, tongue]
    outline = unary_union([q.buffer(0.001) for q in parts]).buffer(-0.001)
    holes = [
        euro_hole(cx, Hp + hh - p["euro_from_top"]),
        euro_hole(cx, Hp + hh + p["euro_from_top"], flip=True),
        affinity.translate(window, xF0 + Wp / 2, 0),
    ]
    return dict(outline=outline, holes=holes, cuts=cuts, scores=scores,
                dims=dict(Wp=Wp, Dp=Dp, Hp=Hp, xF0=xF0))


# --------------------------------------------------------------------------
# Zuschnitt Einleger (ein Streifen, Falze parallel zur Breite)
# --------------------------------------------------------------------------
def insert_layout():
    """Paneele entlang des Streifens: (Name, Länge). Reihenfolge = Blank von unten nach oben."""
    H, Ys = p["ins_h"], p["split_y"]
    return [
        ("Klebelasche", p["ins_glue"]),
        ("Manschettenboden", H - Ys),
        ("Stufe", Z_RB - t),
        ("Ringboden", Ys),
        ("Wand unten", ZD - Z_RB),
        ("Deck", H),
        ("Wand oben", ZD - t),
    ]


def insert_blank(deck_hole):
    W, H, Ys = p["ins_w"], p["ins_h"], p["split_y"]
    lay = insert_layout()
    v, pos = 0.0, {}
    for name, L in lay:
        pos[name] = (v, v + L)
        v += L
    u0, u1 = -W / 2, W / 2
    parts, scores, cuts = [], [], []
    for name, (a, b) in pos.items():
        if name == "Klebelasche":
            parts.append(Polygon([(u0 + 5, a), (u1 - 5, a), (u1, b), (u0, b)]))
        else:
            parts.append(box(u0, a, u1, b))
    for name, (a, b) in list(pos.items())[1:]:
        scores.append([(u0, a), (u1, a)])

    # Deck: v -> Y = v - vD0 ; Seitenflansche stützen das Deck auf den Böden ab
    vD0, vD1 = pos["Deck"]
    hr = ZD - Z_RB - t           # Flansch im Ringbereich
    hc = ZD - Z_CB - t           # Flansch im Manschettenbereich
    for sgn in (-1, 1):
        e = sgn * W / 2
        f = [(e, vD0 + 1), (e + sgn * hr, vD0 + 1 + hr * 0.6), (e + sgn * hr, vD0 + Ys + 0.5),
             (e + sgn * hc, vD0 + Ys + 0.5 + (hc - hr)), (e + sgn * hc, vD1 - 1 - hc * 0.6), (e, vD1 - 1)]
        parts.append(Polygon(f))
        scores.append([(e, vD0 + 1), (e, vD1 - 1)])
    hole = affinity.translate(deck_hole, 0, vD0)

    # Ringboden: Y = vR1 - v ; Kreuzschlitz für die Restschnur
    vR0, vR1 = pos["Ringboden"]
    cuts += cross_slit(0, vR1 - p["cord_slot_y"], p["cord_slot"])

    outline = unary_union([q.buffer(0.001) for q in parts]).buffer(-0.001)
    return dict(outline=outline, holes=[hole], cuts=cuts, scores=scores, dims=dict(pos=pos))


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
    return cut, b["scores"]


def write_files(name, cut, score, margin=8.0):
    allpts = [pt for pl in cut + score for pt in pl]
    minx = min(x for x, _ in allpts); maxx = max(x for x, _ in allpts)
    miny = min(y for _, y in allpts); maxy = max(y for _, y in allpts)
    W, H = maxx - minx + 2 * margin, maxy - miny + 2 * margin
    tr = lambda x, y: (x - minx + margin, y - miny + margin)  # y nach oben (DXF)

    def dxf(fn, layers):
        doc = ezdxf.new("R12")
        msp = doc.modelspace()
        for lname, col, pls in layers:
            doc.layers.new(lname, dxfattribs={"color": col})
            for pl in pls:
                pts = [tr(*q) for q in pl]
                closed = len(pts) > 2 and math.dist(pts[0], pts[-1]) < 1e-6
                if closed:
                    pts = pts[:-1]
                msp.add_polyline2d(pts, close=closed, dxfattribs={"layer": lname, "color": col})
        doc.saveas(fn)

    dxf(os.path.join(OUT, f"{name}_komplett.dxf"), [("SCHNEIDEN", 1, cut), ("RILLEN", 5, score)])
    dxf(os.path.join(OUT, f"{name}_schneiden.dxf"), [("SCHNEIDEN", 1, cut)])
    dxf(os.path.join(OUT, f"{name}_rillen.dxf"), [("RILLEN", 5, score)])

    def path_d(pl):
        pts = [tr(*q) for q in pl]
        return "M" + " L".join(f"{x:.3f},{H - y:.3f}" for x, y in pts)
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.2f}mm" height="{H:.2f}mm" viewBox="0 0 {W:.2f} {H:.2f}">']
    svg.append('<g id="SCHNEIDEN" fill="none" stroke="#e00000" stroke-width="0.25">')
    svg += [f'<path d="{path_d(pl)}"/>' for pl in cut]
    svg.append('</g><g id="RILLEN" fill="none" stroke="#0050ff" stroke-width="0.25" stroke-dasharray="2,1">')
    svg += [f'<path d="{path_d(pl)}"/>' for pl in score]
    svg.append("</g></svg>")
    with open(os.path.join(OUT, f"{name}.svg"), "w") as f:
        f.write("\n".join(svg))
    return W, H


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
    """Polygon in (Y,Z) -> Platte senkrecht zu X."""
    pts = [(y, z) for y, z in list(poly.exterior.coords)[:-1]]
    return cq.Workplane("YZ").workplane(offset=x0).polyline(pts).close().extrude(th)


def build_3d(ring, cuff, window, deck_hole):
    Wi, Hi, Di, hh = p["Wi"], p["Hi"], p["Di"], p["hang_h"]
    X0, X1 = -Wi / 2 - t, Wi / 2 + t
    # Umverpackung
    front = extrude_xy(box(X0, -t, X1, Hi + t).difference(window), Di, t)
    shell = (front.union(blk(X0, X1, -t, Hi + t, -t, 0))
             .union(blk(X0, -Wi / 2, -t, Hi + t, 0, Di)).union(blk(Wi / 2, X1, -t, Hi + t, 0, Di))
             .union(blk(-Wi / 2, Wi / 2, Hi, Hi + t, 0, Di)).union(blk(-Wi / 2, Wi / 2, -t, 0, 0, Di)))
    # Aufhänger (aufgeklappt): Rückwandlage + Doppelung, Euroloch
    hang = rounded_rect(X0, Hi - 10, X1, Hi + hh, 6).intersection(box(X0, Hi + t, X1, Hi + hh)).difference(
        euro_hole(0, Hi + hh - p["euro_from_top"]))
    dbl = box(X0 + 0.75, Hi + 0.6 + t, X1 - 0.75, Hi + hh).difference(euro_hole(0, Hi + hh - p["euro_from_top"]))
    hanger = extrude_xy(hang, -t, t).union(extrude_xy(dbl, 0, t))
    lw = p["lock_w"]
    tongue = blk(-lw / 2, lw / 2, Hi + t, Hi + 2 * t, t, p["lock_slit_z"]).union(
        blk(-lw / 2, lw / 2, Hi - 2.5, Hi + 2 * t, p["lock_slit_z"] - t, p["lock_slit_z"]))

    # Einleger
    W, H, Ys = p["ins_w"], p["ins_h"], p["split_y"]
    u0, u1 = -W / 2, W / 2
    deck = extrude_xy(box(u0, 0, u1, H).difference(deck_hole), ZD - t / 2, t)
    floor_c = blk(u0, u1, Ys, H, 0, t)
    step = blk(u0, u1, Ys - t, Ys, 0, Z_RB)
    slot = box(-p["cord_slot"] / 2, p["cord_slot_y"] - p["cord_slot"] / 2, p["cord_slot"] / 2, p["cord_slot_y"] + p["cord_slot"] / 2)
    floor_r = extrude_xy(box(u0, 0, u1, Ys).difference(slot.buffer(-4)), Z_RB - t, t)
    wall_b = blk(u0, u1, 0, t, Z_RB, ZD)
    wall_t = blk(u0, u1, H - t, H, 0, ZD)
    insert = deck.union(floor_c).union(step).union(floor_r).union(wall_b).union(wall_t)
    fl = Polygon([(1, Z_RB), (Ys, Z_RB), (Ys, t), (H - 1, t), (H - 1, ZD), (1, ZD)])
    for x0 in (u0, u1 - t):
        insert = insert.union(extrude_yz(fl, x0, t))

    # Teile positionieren
    ring_s = cq.Workplane().add(ring).translate((0, Yr, Z_RING))
    cuff_s = cq.Workplane().add(cuff).rotate((0, 0, 0), (0, 1, 0), 90).translate((-CUFF_L / 2, Yc, Z_CUFF))

    # Schnur: sichtbar Manschette -> Kreuzschlitz -> Ring, Rest als Bündel im Schnurfach
    def rod(a, b, r=2.0):
        a, b = cq.Vector(*a), cq.Vector(*b)
        return cq.Solid.makeCylinder(r, (b - a).Length, a, (b - a).normalized())
    ys = p["cord_slot_y"]
    pts_top = [(0, Yc - KEEL + 2, Z_CUFF), (0, ys + 1.5, Z_RB + 2.2), (0, ys, Z_RB - 2.5)]
    pts_bot = [(0, ys, Z_RB - 2.5), (0, ys - 1.5, Z_RB + 2.2), (0, Yr + R_RING - 2, Z_RING)]
    segs = [rod(pts_top[i], pts_top[i + 1]) for i in range(2)] + [rod(pts_bot[i], pts_bot[i + 1]) for i in range(2)]
    zc = (Z_RB - t) / 2 + t
    coil = [cq.Solid.makeTorus(18.0 - 4 * k, 2.0, cq.Vector(0, Yr + 4, zc), cq.Vector(0, 0, 1)) for k in range(3)]
    segs += [rod((1.6, ys, Z_RB - 2.5), (14, Yr + 16, zc)), rod((-1.6, ys, Z_RB - 2.5), (-14, Yr + 16, zc))]
    cord = cq.Workplane().add(segs[0])
    for s in segs[1:] + coil:
        cord = cord.union(cq.Workplane().add(s))

    parts = [
        ("Umverpackung", shell, (0.96, 0.95, 0.92)),
        ("Aufhaenger", hanger, (0.96, 0.95, 0.92)),
        ("Zunge", tongue, (0.96, 0.95, 0.92)),
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
    c = p["hole_clear"]

    ring_hole = ring_sil.buffer(c, resolution=32)
    cuff_hole = cuff_sil.buffer(c, resolution=8)
    ch = p["cord_chan"] / 2
    channel = box(-ch, Yr + R_RING - 4, ch, Yc - KEEL + 2)
    deck_hole = smooth(unary_union([ring_hole, cuff_hole, channel]), 0.8)

    wx = p["win_cuff_x"]
    window = unary_union([
        Point(0, Yr).buffer(p["win_ring_r"], resolution=64),
        rounded_rect(-wx, Yc - KEEL - 1.5, wx, Yc + CUFF_D / 2 + 1.5, 3),
        box(-5, Yr + R_RING - 6, 5, Yc - KEEL + 3),
    ])
    window = smooth(window, 3)

    bb = box_blank(window)
    ib = insert_blank(deck_hole)
    sizes = {"Umverpackung": write_files("Umverpackung", *blank_paths(bb)),
             "Einleger": write_files("Einleger", *blank_paths(ib))}
    build_3d(ring, cuff, window, deck_hole)

    info = dict(params=P, Yr=Yr, Yc=Yc, deck_Z=ZD, ring_floor_Z=round(Z_RB, 2), cuff_floor_Z=round(Z_CB, 2),
                front_Z=round(Z_FRONT, 2), ring_front_gap=p["gap"], cuff_front_gap=p["gap"],
                outer_mm=[round(p["Wi"] + 2 * t, 1), round(p["Hi"] + 2 * t, 1), round(p["Di"] + 2 * t, 1)],
                ring_hole_bounds=[round(v, 2) for v in ring_hole.bounds],
                cuff_hole_bounds=[round(v, 2) for v in cuff_hole.bounds],
                window_bounds=[round(v, 2) for v in window.bounds],
                insert_panels={k: round(L, 2) for k, L in insert_layout()},
                cord_store_mm=[p["ins_w"], p["split_y"], round(Z_RB - 2 * t, 2)],
                blank_sizes_mm={k: [round(v - 16, 1) for v in s] for k, s in sizes.items()})
    with open(os.path.join(OUT, "masse.json"), "w") as f:
        json.dump(info, f, indent=2, ensure_ascii=False)
    print(json.dumps(info, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

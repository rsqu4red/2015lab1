"""
Türzwerg – Verpackung (Umverpackung + Haltestruktur/Einleger)
==============================================================

Erzeugt aus den STEP-Dateien von Ring und Manschette:
  * Plotdateien für den Silhouette Cameo 4 (DXF R12 + SVG, Ebenen SCHNEIDEN / RILLEN)
  * ein 3D-Gesamtmodell (GLB für den Viewer, STEP zum Weiterkonstruieren)

Alle Maße in mm. Koordinaten im Karton:
  X = Breite (0 = Mitte), Y = Höhe (0 = Innenboden), Z = Tiefe (0 = Innenseite Rückwand).

Aufruf:  python generate.py          (benötigt: cadquery, shapely, ezdxf)
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
    # Umverpackung (Innenmaße) -> außen ca. 90 x 140 x 30
    Wi=89.0, Hi=139.0, Di=29.0,
    tuck=15.0,         # Einstecklasche
    dust=20.0,         # Staublaschen
    glue=13.0,         # Klebelasche Faltschachtel
    hang_h=35.0,       # Höhe Aufhänger über Kartonoberkante (doppellagig)
    hang_w=60.0,       # Breite Aufhänger
    # Euroloch (Angaben lt. DIN EN 13010 / Handelsüblich): 32 breit, 6 hoch, Mitte 10
    euro_w=32.0, euro_h=6.0, euro_d=10.0, euro_from_top=14.0,
    # Einleger (Haltestruktur)
    ins_w=88.5,        # Außenbreite Einleger (0,5 Luft)
    ins_h=138.0,       # Länge Einleger (1 Luft)
    ins_d=28.8,        # Tiefe Einleger (füllt Karton -> kann nicht wandern)
    raise_=5.5,        # Anschlagboden über Rückwand -> Manschette liegt vorne an
    snap=12.5,         # Deck über Anschlagboden (Ring+Manschette schnappen dort)
    ins_glue=10.0,
    # Layout im Sichtfeld (Y = Höhe ab Innenboden)
    ring_bottom=6.0,   # Unterkante Ring
    cord_visible=20.0, # sichtbare Schnurlänge
    ring_clear=0.15,   # Lochzugabe Ring (Radius)
    cuff_under=0.35,   # Untermaß Manschettenloch (klemmt)
    slit=3.0,          # Länge Haltezungen-Schlitze
    slit_pitch=7.0,    # Abstand Schlitze
    win_ring_r=37.0,   # Fenster Ring (Radius)
    win_off=2.5,       # Fenster Rand um Manschette/Schnur
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
hD = p["raise_"] + p["snap"]                       # Deckhöhe (Tiefe Z)
Z_RING = p["raise_"] + RING_TH / 2                 # Ringmitte in Z
Z_CUFF = p["raise_"] + CUFF_D / 2                  # Manschettenachse in Z


# --------------------------------------------------------------------------
# Teile laden & Schnitte bestimmen
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


def sections(ring, cuff):
    z_cut = hD - Z_RING  # Schnitt im Ring-Koordinatensystem
    pl = cq.Face.makePlane(200, 200, basePnt=cq.Vector(0, 0, z_cut), dir=cq.Vector(0, 0, 1))
    ring_sec = face_to_poly(ring.intersect(pl), lambda v: (v.x, v.y + Yr))
    # Manschette: Achse = Z(STEP) -> X(Karton); x(STEP) -> Tiefe
    x_cut = hD - Z_CUFF
    pl = cq.Face.makePlane(200, 200, basePnt=cq.Vector(x_cut, 0, 16.5), dir=cq.Vector(1, 0, 0))
    cuff_sec = face_to_poly(cuff.intersect(pl), lambda v: (v.z - CUFF_L / 2, v.y + Yc))
    pl = cq.Face.makePlane(200, 200, basePnt=cq.Vector(0, 0, 16.5), dir=cq.Vector(1, 0, 0))
    cuff_sil = face_to_poly(cuff.intersect(pl), lambda v: (v.z - CUFF_L / 2, v.y + Yc))
    # nur Außenkontur
    def outer(g):
        g = max(g.geoms, key=lambda q: q.area) if g.geom_type == "MultiPolygon" else g
        return Polygon(g.exterior)
    # Manschette ist hohl -> Schnitt besteht aus Wandstreifen; gefüllte Hülle verwenden
    return outer(ring_sec), cuff_sec.convex_hull, cuff_sil.convex_hull


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


def slits_along(poly, pitch, length, skip=None):
    """Radiale Schlitze nach außen entlang der Lochkontur (Haltezungen)."""
    ring = poly.exterior
    L = ring.length
    n = max(int(L // pitch), 1)
    out = []
    for i in range(n):
        s = (i + 0.5) * L / n
        a = ring.interpolate(s - 0.5)
        b = ring.interpolate(s + 0.5)
        m = ring.interpolate(s)
        dx, dy = b.x - a.x, b.y - a.y
        nl = math.hypot(dx, dy) or 1
        nx, ny = dy / nl, -dx / nl
        # nach außen?
        if poly.contains(Point(m.x + nx * 0.3, m.y + ny * 0.3)):
            nx, ny = -nx, -ny
        if skip is not None and skip(m.x, m.y):
            continue
        out.append(LineString([(m.x, m.y), (m.x + nx * length, m.y + ny * length)]))
    return out


def smooth(g, r):
    return g.buffer(r, resolution=16).buffer(-2 * r, resolution=16).buffer(r, resolution=16)


# --------------------------------------------------------------------------
# Zuschnitt Umverpackung
# --------------------------------------------------------------------------
def box_blank(window):
    Wp, Dp, Hp = p["Wi"] + t, p["Di"] + t, p["Hi"] + t
    tk, du, gl, hh, hw = p["tuck"], p["dust"], p["glue"], p["hang_h"], p["hang_w"]
    xB0, xB1 = 0.0, Wp              # Rückwand
    xS1 = xB1 + Dp                  # Seite A
    xF0, xF1 = xS1, xS1 + Wp        # Front
    xS2 = xF1 + Dp                  # Seite B
    parts, scores = [], []

    # Hauptpaneele
    parts.append(box(xB0, 0, xS2, Hp))
    for x in (xB1, xS1, xF1):
        scores.append([(x, 0), (x, Hp)])
    # Klebelasche an der Rückwand
    parts.append(Polygon([(0, 0), (-gl, 6), (-gl, Hp - 6), (0, Hp)]))
    scores.append([(0, 0), (0, Hp)])

    # Deckel + Einstecklasche oben/unten (an der Front)
    for sgn, y0 in ((1, Hp), (-1, 0)):
        y1 = y0 + sgn * Dp
        parts.append(box(xF0, min(y0, y1), xF1, max(y0, y1)))
        tuck = rounded_rect(xF0 + 1.0, 0, xF1 - 1.0, tk + 6, 6)
        tuck = tuck.intersection(box(xF0, 0, xF1, tk))
        tuck = affinity.translate(tuck, 0, y1) if sgn > 0 else affinity.translate(affinity.scale(tuck, 1, -1, origin=(0, 0)), 0, y1)
        parts.append(tuck)
        scores.append([(xF0, y0), (xF1, y0)])
        scores.append([(xF0 + 1.0, y1), (xF1 - 1.0, y1)])
        # Staublaschen an den Seiten
        for xa, xb in ((xB1, xS1), (xF1, xS2)):
            pts = [(xa + 0.5, 0), (xa + 0.5, du - 7), (xa + 7, du), (xb - 3, du), (xb - 0.5, du - 3), (xb - 0.5, 0)]
            fl = Polygon([(x, y0 + sgn * y) for x, y in pts])
            parts.append(fl)
            scores.append([(xa + 0.5, y0), (xb - 0.5, y0)])

    # Aufhänger an der Rückwand (doppellagig, Doppelung klappt nach vorn)
    cx = Wp / 2
    hang = Polygon([(xB0, Hp), (xB1, Hp), (cx + hw / 2, Hp + 12), (cx + hw / 2, Hp + hh), (cx - hw / 2, Hp + hh), (cx - hw / 2, Hp + 12)])
    dbl = rounded_rect(cx - hw / 2 + 0.75, Hp + hh - 8, cx + hw / 2 - 0.75, Hp + 2 * hh - 0.5, 5)
    dbl = dbl.intersection(box(0, Hp + hh, Wp, Hp + 2 * hh))
    parts += [hang, dbl]
    scores.append([(cx - hw / 2 + 0.75, Hp + hh), (cx + hw / 2 - 0.75, Hp + hh)])

    outline = unary_union([q.buffer(0.001) for q in parts]).buffer(-0.001)
    holes = [
        euro_hole(cx, Hp + hh - p["euro_from_top"]),
        euro_hole(cx, Hp + hh + p["euro_from_top"], flip=True),
        affinity.translate(window, xF0 + Wp / 2, t / 2),
    ]
    return dict(outline=outline, holes=holes, slits=[], scores=scores,
                dims=dict(Wp=Wp, Dp=Dp, Hp=Hp, xF0=xF0))


# --------------------------------------------------------------------------
# Zuschnitt Einleger (Haltestruktur)
# --------------------------------------------------------------------------
def insert_blank(deck_hole, slit_lines):
    Wb = p["ins_w"] - 2 * t
    Dw, r, H = p["ins_d"], p["raise_"], p["ins_h"]
    xF1 = Dw - r          # Falz Wand L / Boden (Boden liegt 'r' über Rückwand)
    xF2 = xF1 + Wb        # Falz Boden / Wand R
    xF3 = xF2 + (hD - r)  # Falz Wand R / Deck
    xF4 = xF3 + Wb        # Falz Deck / Klebelasche
    gl = p["ins_glue"]
    outline = unary_union([
        box(0, 0, xF4, H),
        Polygon([(xF4, 0), (xF4 + gl, 4), (xF4 + gl, H - 4), (xF4, H)]),
    ])
    cuts, scores = [], []

    def interrupted(x, gaps):
        y = 0.0
        for a, b in sorted(gaps):
            if a > y:
                scores.append([(x, y), (x, a)])
            y = b
        if y < H:
            scores.append([(x, y), (x, H)])

    # Füße: Wand läuft unter dem Anschlagboden bis zur Rückwand weiter
    feet = [(6, 30), (58, 80), (108, 132)]
    for x, d in ((xF1, +1), (xF2, -1)):
        for a, b in feet:
            cuts.append([(x, a), (x + d * r, a), (x + d * r, b), (x, b)])
        interrupted(x, feet)
    # Stützlaschen: Wand R läuft über das Deck bis an die Frontwand
    ext = Dw - hD
    tabs = [(5, 20), (70, 92), (108, 132)]
    for a, b in tabs:
        cuts.append([(xF3, a), (xF3 + ext, a), (xF3 + ext, b), (xF3, b)])
    interrupted(xF3, tabs)
    scores.append([(xF4, 4), (xF4, H - 4)])

    ox = xF3 + Wb / 2       # Deck: X(Karton) = x - ox
    hole = affinity.translate(deck_hole, ox, 0)
    slits = [affinity.translate(s, ox, 0) for s in slit_lines]
    return dict(outline=outline, holes=[hole], cuts=cuts, slits=slits, scores=scores,
                dims=dict(Wb=Wb, xF1=xF1, xF2=xF2, xF3=xF3, xF4=xF4, feet=feet, tabs=tabs))


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
    for s in b["slits"]:
        cut += list(geom_lines(s))
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
        d = "M" + " L".join(f"{x:.3f},{H - y:.3f}" for x, y in pts)
        return d
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
    wp = cq.Workplane("XY").workplane(offset=z0)
    solid = wp.polyline(list(poly.exterior.coords)[:-1]).close().extrude(th)
    for hole in poly.interiors:
        h = cq.Workplane("XY").workplane(offset=z0 - 1).polyline(list(hole.coords)[:-1]).close().extrude(th + 2)
        solid = solid.cut(h)
    return solid


def build_3d(ring, cuff, window, deck_hole):
    Wi, Hi, Di = p["Wi"], p["Hi"], p["Di"]
    hw, hh = p["hang_w"], p["hang_h"]
    X0, X1 = -Wi / 2 - t, Wi / 2 + t
    # Umverpackung
    front = extrude_xy(box(X0, -t, X1, Hi + t).difference(affinity.translate(window, 0, 0)), Di, t)
    back = cq.Workplane("XY").box(X1 - X0, Hi + 2 * t, t, centered=False).translate((X0, -t, -t))
    sideL = cq.Workplane("XY").box(t, Hi + 2 * t, Di, centered=False).translate((X0, -t, 0))
    sideR = cq.Workplane("XY").box(t, Hi + 2 * t, Di, centered=False).translate((Wi / 2, -t, 0))
    top = cq.Workplane("XY").box(Wi, t, Di, centered=False).translate((-Wi / 2, Hi, 0))
    bot = cq.Workplane("XY").box(Wi, t, Di, centered=False).translate((-Wi / 2, -t, 0))
    hang = Polygon([(X0, Hi), (X1, Hi), (hw / 2, Hi + 12), (hw / 2, Hi + hh), (-hw / 2, Hi + hh), (-hw / 2, Hi + 12)])
    hang = hang.difference(euro_hole(0, Hi + hh - p["euro_from_top"]))
    hanger = extrude_xy(hang, -t, t)
    dbl = rounded_rect(-hw / 2 + 0.75, Hi + 0.5 - 8, hw / 2 - 0.75, Hi + hh, 5).intersection(box(-50, Hi + 0.5, 50, Hi + hh))
    dbl = dbl.difference(euro_hole(0, Hi + hh - p["euro_from_top"]))
    dbl = extrude_xy(dbl, 0, t)
    shell = front.union(back).union(sideL).union(sideR).union(top).union(bot)
    hanger = hanger.union(dbl)

    # Einleger
    W, H, D, r = p["ins_w"], p["ins_h"], p["ins_d"], p["raise_"]
    Wb = W - 2 * t
    deck = extrude_xy(box(-Wb / 2, 0, Wb / 2, H).difference(deck_hole), hD - t, t)
    floor = cq.Workplane("XY").box(Wb, H, t, centered=False).translate((-Wb / 2, 0, r))
    wl = cq.Workplane("XY").box(t, H, D, centered=False).translate((-W / 2, 0, 0))
    wr = cq.Workplane("XY").box(t, H, D, centered=False).translate((W / 2 - t, 0, 0))
    insert = deck.union(floor).union(wl).union(wr)

    # Teile positionieren
    ring_s = cq.Workplane().add(ring).translate((0, Yr, Z_RING))
    cuff_s = cq.Workplane().add(cuff).rotate((0, 0, 0), (0, 1, 0), 90).translate((-CUFF_L / 2, Yc, Z_CUFF))
    a = cq.Vector(0, Yc - KEEL + 3, Z_CUFF)
    b = cq.Vector(0, Yr + R_RING - 3, Z_RING)
    cord = cq.Workplane().add(cq.Solid.makeCylinder(2.0, (a - b).Length, b, (a - b).normalized()))

    parts = [
        ("Umverpackung", shell, (0.96, 0.95, 0.92)),
        ("Aufhaenger", hanger, (0.96, 0.95, 0.92)),
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
    ring_sec, cuff_sec, cuff_sil = sections(ring, cuff)

    ring_hole = ring_sec.buffer(p["ring_clear"], resolution=32)
    # Die breiteste Stelle (Achse) muss durchs Deck -> Loch = Silhouette mit Untermaß
    cuff_hole = cuff_sil.buffer(-p["cuff_under"], resolution=8)
    channel = box(-3.0, Yr + R_RING - 4, 3.0, Yc - KEEL + 2)
    deck_hole = smooth(unary_union([ring_hole, cuff_hole, channel]), 0.8)

    def skip(x, y):  # keine Zungen im Schnurkanal
        return abs(x) < 6 and (Yr + R_RING - 6) < y < (Yc - KEEL + 4)
    slit_lines = slits_along(deck_hole, p["slit_pitch"], p["slit"], skip)

    window = unary_union([
        Point(0, Yr).buffer(p["win_ring_r"], resolution=64),
        cuff_sil.buffer(p["win_off"], resolution=16),
        box(-5, Yr + R_RING - 6, 5, Yc - KEEL + 3),
    ])
    window = smooth(window, 3)

    bb = box_blank(window)
    ib = insert_blank(deck_hole, slit_lines)
    sizes = {}
    sizes["Umverpackung"] = write_files("Umverpackung", *blank_paths(bb))
    sizes["Einleger"] = write_files("Einleger", *blank_paths(ib))
    build_3d(ring, cuff, window, deck_hole)

    info = dict(params=P, Yr=Yr, Yc=Yc, deck_Z=hD, ring_front_Z=p["raise_"] + RING_TH,
                cuff_front_Z=p["raise_"] + CUFF_D,
                ring_hole_d=round(2 * math.sqrt(ring_hole.area / math.pi), 2),
                cuff_hole_bounds=[round(v, 2) for v in cuff_hole.bounds],
                window_bounds=[round(v, 2) for v in window.bounds],
                blank_sizes_mm={k: [round(v, 1) for v in s] for k, s in sizes.items()},
                n_slits=len(slit_lines),
                ring_sec_bounds=[round(v, 2) for v in ring_sec.bounds],
                cuff_sil_bounds=[round(v, 2) for v in cuff_sil.bounds])
    with open(os.path.join(OUT, "masse.json"), "w") as f:
        json.dump(info, f, indent=2, ensure_ascii=False)
    print(json.dumps(info, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

"""
Türzwerg – Verpackung v3: bedruckte Front mit drei Sichtfenstern
================================================================

Erzeugt aus den STEP-Dateien von Ring und Manschette:
  * Plotdateien für den Silhouette Cameo 4 in Mattengröße (werden nicht skaliert)
      - Umverpackung (Faltschachtel mit klappbarem Euroloch-Hänger, drei kleine Fenster)
      - Einleger (eine Platte mit vier umgeklappten Rändern, ohne Klebestelle)
      - Front-Etikett (Schnittlinien passend zur Druckvorlage)
  * Druckvorlage Front-Etikett (A4-PDF, 100 % drucken)
  * 3D-Modell (GLB/STEP) und Front-Texturen für den Viewer

Drei Fensterkonzepte: A „Kapsel“, B „Bullauge“, C „Mittelachse“.

Koordinaten im Karton (mm): X = Breite (0 = Mitte), Y = Höhe (0 = Innenboden),
Z = Tiefe (0 = Innenseite Rückwand).

Aufbau (Seitenansicht):
      Front (bedruckt, Fenster) ======================================
        Ring (liegt vorn an)            Manschette (liegt vorn an)
      ---- Einleger-Platte (Z = 9) ----  Loch --------------------------
        |  Schnurfach           |       Manschette steht auf der Rückwand
      Rückwand ======================================================

Aufruf:  python generate.py
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
    t=0.45,                    # Kartondicke
    Wi=83.0, Hi=134.0, Di=23.2,  # Karton innen -> außen ca. 84 x 135 x 24
    tuck=15.0, dust=18.0, glue=12.0,
    hang_h=23.0,               # Hänger < Kartontiefe -> liegt umgeklappt auf dem Deckel
    euro_w=32.0, euro_h=6.0, euro_d=10.0, euro_from_top=12.0,
    margin=6.0,                # Rand oben (über Manschette) = unten (unter Ring)
    cord_field=18.0,           # Abstand Kielspitze -> Ring oben
    # Einleger
    ins_clear=0.5,             # Luft zur Kartonwand (gesamt)
    ins_gap_top=1.0,
    cuff_clear=0.3,            # Luft um die Manschette im Plattenloch
    tab_r=23.6, tab_w=9.0, tab_l=6.0,   # Zentrierlaschen für den Ring (innen, Ring-Ø innen 48,5)
    slit=10.0,                 # gerader Querschlitz für die Restschnur
    # Etikett / Fenster
    label_inset=0.5,           # Etikett je Seite kleiner als die Frontfläche
    win_card=0.4,              # Kartonfenster je Seite größer als das Etikettfenster
    bleed=2.0,
)
p = P
t = p["t"]
R_RING, RING_TH, CUFF_D, CUFF_L, KEEL = 36.0, 14.0, 23.0, 33.0, 20.5

Yc = p["Hi"] - p["margin"] - CUFF_D / 2                    # Manschettenachse
Yr = Yc - KEEL - p["cord_field"] - R_RING                  # Ringmitte
Z_CUFF = CUFF_D / 2                                        # Manschette steht auf der Rückwand
Z_DECK = CUFF_D - RING_TH                                  # Plattenoberseite = Ringrückseite (9 mm)
Z_RING = Z_DECK + RING_TH / 2
Y_SLIT = Yr + R_RING + 2.5                                 # Querschlitz knapp über dem Ring
Y_CORD = (Yc - KEEL + Y_SLIT) / 2 + 1.5                    # Mitte Schnurfenster (über dem Schlitz)
LW = p["Wi"] - 2 * p["label_inset"] + t                    # Etikett ~ Frontfläche - 2 x 0,5
LH = p["Hi"] - 2 * p["label_inset"] + t
assert abs(Yr - R_RING - p["margin"]) < 0.01, "Rand unten muss gleich Rand oben sein"

# Farben der Druckvorlage
COL = dict(bg="#24282b", neon="#d6f020", neon_d="#a9c214", neon_l="#f1ff8a",
           cord="#b0302a", cord_l="#e2675d", frame="#ffffff", text="#9aa29c")


# --------------------------------------------------------------------------
# Teile laden, Konturen
# --------------------------------------------------------------------------
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


def load_parts():
    ring = cq.importers.importStep(os.path.join(TEILE, "Ring_v2_FINAL.step")).val()
    cuff = cq.importers.importStep(os.path.join(TEILE, "Manschette_v2_FINAL_25mm.step")).val()
    # Ansicht von vorn: Außen = größte Kontur, Innen = engste Öffnung über die Ringdicke
    # (die Knotentasche liegt innen und ist von vorn nicht sichtbar)
    holes, hull = [], None
    for z in (-5.8, -3.0, 0.0, 3.0, 5.8):
        pl = cq.Face.makePlane(200, 200, basePnt=cq.Vector(0, 0, z), dir=cq.Vector(0, 0, 1))
        sec = face_to_poly(ring.intersect(pl), lambda v: (v.x, v.y + Yr))
        sec = max(sec.geoms, key=lambda q: q.area) if sec.geom_type == "MultiPolygon" else sec
        h = sec.convex_hull
        hull = h if hull is None else hull.union(h)
        hole = h.difference(sec).buffer(-2.2).buffer(2.2)        # Schnurbohrung (Ø4) schließen
        hole = max(hole.geoms, key=lambda q: q.area) if hole.geom_type == "MultiPolygon" else hole
        holes.append(hole)
    inner = holes[0]
    for h in holes[1:]:
        inner = inner.intersection(h)
    ring_shape = Polygon(hull.convex_hull.exterior.coords, [inner.exterior.coords])
    pl = cq.Face.makePlane(200, 200, basePnt=cq.Vector(0, 0, 16.5), dir=cq.Vector(1, 0, 0))
    cuff_sil = face_to_poly(cuff.intersect(pl), lambda v: (v.z - CUFF_L / 2, v.y + Yc)).convex_hull
    return ring, cuff, ring_shape, cuff_sil


# --------------------------------------------------------------------------
# 2D-Hilfen
# --------------------------------------------------------------------------
def rrect(x0, y0, x1, y1, r):
    return box(x0 + r, y0 + r, x1 - r, y1 - r).buffer(r, resolution=24)


def pill(cx, cy, w, h):
    r = min(w, h) / 2
    return rrect(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, r - 1e-6)


def arc_slot(cx, cy, r0, r1, a0, a1):
    """Bogenschlitz zwischen Radius r0/r1, Winkel a0..a1 (Grad), runde Enden."""
    rm, w = (r0 + r1) / 2, r1 - r0
    pts = [(cx + rm * math.cos(math.radians(a)), cy + rm * math.sin(math.radians(a)))
           for a in [a0 + (a1 - a0) * i / 40 for i in range(41)]]
    return LineString(pts).buffer(w / 2, resolution=24)


def euro_hole(cx, cy, flip=False):
    w, h, d = p["euro_w"], p["euro_h"], p["euro_d"]
    slot = LineString([(cx - w / 2 + h / 2, cy), (cx + w / 2 - h / 2, cy)]).buffer(h / 2, resolution=16)
    g = unary_union([slot, Point(cx, cy - h / 2 + d / 2).buffer(d / 2, resolution=24)])
    return affinity.scale(g, 1, -1, origin=(cx, cy)) if flip else g


def cross_slit(cx, cy, s):
    h = s / 2
    return [[(cx - h, cy - h), (cx + h, cy + h)], [(cx - h, cy + h), (cx + h, cy - h)]]


def lines_of(g):
    if g.geom_type == "Polygon":
        yield list(g.exterior.coords)
        for i in g.interiors:
            yield list(i.coords)
    elif g.geom_type in ("MultiPolygon", "GeometryCollection"):
        for q in g.geoms:
            yield from lines_of(q)
    elif g.geom_type == "LineString":
        yield list(g.coords)


def bounds(paths):
    pts = [q for pl in paths for q in pl]
    return (min(x for x, _ in pts), min(y for _, y in pts), max(x for x, _ in pts), max(y for _, y in pts))


# --------------------------------------------------------------------------
# Fensterkonzepte (Etikett-Fenster in Kartonkoordinaten)
# --------------------------------------------------------------------------
CONCEPTS = {
    "A": "Kapsel",
    "B": "Bullauge",
    "C": "Mittelachse",
}


def windows(concept):
    rb_in, rb_out = 27.0, 33.0          # flache Ringstirn (Ring Ø72, innen Ø48,5)
    cord = pill(0, Y_CORD, 6.0, 14.0)
    if concept == "A":
        return {"Manschette": pill(0, Yc, 22.0, 9.0),
                "Schnur": cord,
                "Ring": arc_slot(0, Yr, rb_in, rb_out, 235, 305)}
    if concept == "B":
        return {"Manschette": Point(0, Yc).buffer(7.0, resolution=48),
                "Schnur": cord,
                "Ring": Point(0, Yr - 30.0).buffer(5.0, resolution=48)}
    if concept == "C":
        return {"Manschette": pill(0, Yc, 4.0, 18.0),
                "Schnur": pill(0, Y_CORD, 4.0, 14.0),
                "Ring": pill(0, Yr - 30.0, 4.0, 9.0)}
    raise ValueError(concept)


# --------------------------------------------------------------------------
# Zuschnitt Umverpackung
# --------------------------------------------------------------------------
def box_blank(win_card):
    Wp, Dp, Hp = p["Wi"] + t, p["Di"] + t, p["Hi"] + t
    tk, du, gl, hh = p["tuck"], p["dust"], p["glue"], p["hang_h"]
    xB1 = Wp
    xS1 = xB1 + Dp
    xF0, xF1 = xS1, xS1 + Wp
    xS2 = xF1 + Dp
    parts, mountain, valley = [], [], []
    parts.append(box(0, 0, xS2, Hp))
    for x in (0, xB1, xS1, xF1):
        mountain.append([(x, 0), (x, Hp)])
    parts.append(Polygon([(0, 0), (-gl, 6), (-gl, Hp - 6), (0, Hp)]))
    for sgn, y0 in ((1, Hp), (-1, 0)):
        y1 = y0 + sgn * Dp
        parts.append(box(xF0, min(y0, y1), xF1, max(y0, y1)))
        tuck = rrect(xF0 + 1.0, 0, xF1 - 1.0, tk + 6, 6).intersection(box(xF0, 0, xF1, tk))
        tuck = affinity.translate(tuck, 0, y1) if sgn > 0 else affinity.translate(affinity.scale(tuck, 1, -1, origin=(0, 0)), 0, y1)
        parts.append(tuck)
        mountain += [[(xF0, y0), (xF1, y0)], [(xF0 + 1.0, y1), (xF1 - 1.0, y1)]]
        for xa, xb in ((xB1, xS1), (xF1, xS2)):
            pts = [(xa + 0.5, 0), (xa + 0.5, du - 7), (xa + 7, du), (xb - 3, du), (xb - 0.5, du - 3), (xb - 0.5, 0)]
            parts.append(Polygon([(x, y0 + sgn * y) for x, y in pts]))
            mountain.append([(xa + 0.5, y0), (xb - 0.5, y0)])
    # Hänger: volle Breite, doppellagig, klappt 90° nach vorn auf den Deckel
    cx = Wp / 2
    parts.append(rrect(0, Hp - 10, xB1, Hp + hh, 5).intersection(box(0, Hp, xB1, Hp + hh)))
    valley.append([(0.5, Hp), (xB1 - 0.5, Hp)])
    yd0, yd1 = Hp + hh, Hp + 2 * hh - 1.0
    parts.append(rrect(0.75, yd0, xB1 - 0.75, yd1 + 10, 5).intersection(box(0, yd0, xB1, yd1)))
    mountain.append([(0.75, yd0), (xB1 - 0.75, yd0)])
    outline = unary_union([q.buffer(0.001) for q in parts]).buffer(-0.001)
    holes = [euro_hole(cx, Hp + hh - p["euro_from_top"]), euro_hole(cx, Hp + hh + p["euro_from_top"], flip=True)]
    holes += [affinity.translate(w, xF0 + Wp / 2, 0) for w in win_card]
    cut = list(lines_of(outline)) + [ln for h in holes for ln in lines_of(h)]
    return cut, mountain, valley, dict(front_x=xF0 + Wp / 2)


# --------------------------------------------------------------------------
# Zuschnitt Einleger: Platte + 4 Ränder, ohne Klebestelle
# --------------------------------------------------------------------------
def insert_geometry(cuff_sil):
    W = p["Wi"] - p["ins_clear"]
    H = p["Hi"] - p["ins_gap_top"]
    hw = Z_DECK - t - 0.05                                  # Randhöhe bis zur Rückwand
    x0, x1 = -W / 2, W / 2
    deck = box(x0, 0, x1, H)
    flaps = [
        Polygon([(x1, 0.5), (x1 + hw, 0.5 + hw), (x1 + hw, H - 0.5 - hw), (x1, H - 0.5)]),
        Polygon([(x0, 0.5), (x0 - hw, 0.5 + hw), (x0 - hw, H - 0.5 - hw), (x0, H - 0.5)]),
        Polygon([(x0 + 0.5, H), (x0 + 0.5 + hw, H + hw), (x1 - 0.5 - hw, H + hw), (x1 - 0.5, H)]),
        Polygon([(x0 + 0.5, 0), (x0 + 0.5 + hw, -hw), (x1 - 0.5 - hw, -hw), (x1 - 0.5, 0)]),
    ]
    mountain = [[(x1, 0.5), (x1, H - 0.5)], [(x0, 0.5), (x0, H - 0.5)],
                [(x0 + 0.5, H), (x1 - 0.5, H)], [(x0 + 0.5, 0), (x1 - 0.5, 0)]]
    cuff_hole = cuff_sil.buffer(p["cuff_clear"], resolution=8)
    cuts, valley, tabs = [], [], []
    for a in (45, 135, 225, 315):
        u = (math.cos(math.radians(a)), math.sin(math.radians(a)))
        v = (-u[1], u[0])
        P_ = lambda r, s: (r * u[0] + s * v[0], Yr + r * u[1] + s * v[1])
        rh, w, L = p["tab_r"], p["tab_w"], p["tab_l"]
        cuts.append([P_(rh, -w / 2), P_(rh - L, -w / 2), P_(rh - L, w / 2), P_(rh, w / 2)])
        valley.append([P_(rh, -w / 2), P_(rh, w / 2)])
        tabs.append((a, Polygon([P_(rh, -w / 2), P_(rh - L, -w / 2), P_(rh - L, w / 2), P_(rh, w / 2)])))
    cuts.append([(-p["slit"] / 2, Y_SLIT), (p["slit"] / 2, Y_SLIT)])
    outline = unary_union([deck] + flaps)
    cut = list(lines_of(outline)) + list(lines_of(cuff_hole)) + cuts
    return dict(cut=cut, mountain=mountain, valley=valley, W=W, H=H, hw=hw, cuff_hole=cuff_hole, tabs=tabs)


# --------------------------------------------------------------------------
# Druckvorlage Front-Etikett (SVG in mm, y nach unten, Ursprung oben links am Etikett)
# --------------------------------------------------------------------------
def to_label(x, y):
    return x + LW / 2, (p["Hi"] / 2 + LH / 2) - y


def svg_path(g):
    d = []
    for ring in lines_of(g):
        pts = [to_label(x, y) for x, y in ring]
        d.append("M" + " L".join(f"{a:.3f},{b:.3f}" for a, b in pts) + " Z")
    return " ".join(d)


def label_svg_group(concept, ring_shape, cuff_sil, win_label, frame=True):
    b = p["bleed"]
    g = [f'<rect x="{-b}" y="{-b}" width="{LW + 2 * b:.3f}" height="{LH + 2 * b:.3f}" fill="{COL["bg"]}"/>']
    # feines Raster als Hintergrundstruktur
    for i in range(1, int(LW // 6) + 1):
        g.append(f'<line x1="{i * 6:.2f}" y1="0" x2="{i * 6:.2f}" y2="{LH:.2f}" stroke="#2c3134" stroke-width="0.25"/>')
    # Schatten
    sh = 0.9
    g.append(f'<path d="{svg_path(affinity.translate(ring_shape, sh, -sh))}" fill="#15181a" fill-rule="evenodd"/>')
    g.append(f'<path d="{svg_path(affinity.translate(cuff_sil, sh, -sh))}" fill="#15181a"/>')
    # Schnur
    x0, y0 = to_label(0, Yc - KEEL + 1)
    x1, y1 = to_label(0, Yr + R_RING - 1)
    g.append(f'<line x1="{x0:.2f}" y1="{y0:.2f}" x2="{x1:.2f}" y2="{y1:.2f}" stroke="{COL["cord"]}" stroke-width="4"/>')
    g.append(f'<line x1="{x0:.2f}" y1="{y0:.2f}" x2="{x1:.2f}" y2="{y1:.2f}" stroke="{COL["cord_l"]}" stroke-width="1.1" stroke-dasharray="1.1 1.1"/>')
    # Ring
    g.append(f'<path d="{svg_path(ring_shape)}" fill="{COL["neon"]}" fill-rule="evenodd"/>')
    mid = Point(0, Yr).buffer(30.0, resolution=64).exterior
    g.append(f'<path d="{svg_path(Polygon(mid))}" fill="none" stroke="{COL["neon_l"]}" stroke-width="0.6" opacity="0.8"/>')
    # Manschette: Rohr + Kiel
    cb = cuff_sil.bounds
    tube = cuff_sil.intersection(box(cb[0], Yc - CUFF_D / 2, cb[2], cb[3]))
    keel = cuff_sil.intersection(box(cb[0], cb[1], cb[2], Yc - CUFF_D / 2))
    g.append(f'<path d="{svg_path(keel)}" fill="{COL["neon_d"]}"/>')
    g.append(f'<path d="{svg_path(tube)}" fill="{COL["neon"]}"/>')
    hl = box(cb[0] + 1.5, Yc + 4.0, cb[2] - 1.5, Yc + 7.5)
    g.append(f'<path d="{svg_path(hl)}" fill="{COL["neon_l"]}" opacity="0.55"/>')
    # Fensterrahmen (fein, außen um die Schnittkante)
    if frame:
        for w in win_label.values():
            g.append(f'<path d="{svg_path(w.buffer(0.7, resolution=24))}" fill="none" stroke="{COL["frame"]}" stroke-width="0.35"/>')
    return "\n".join(g)


def write_label_print(concept, ring_shape, cuff_sil, win_label, d):
    """A4-PDF mit zwei Etiketten (Beschnitt 2 mm, Schnittmarken). Position = Schnittdatei."""
    W4, H4 = 210.0, 297.0
    pos = label_positions()
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W4}mm" height="{H4}mm" viewBox="0 0 {W4} {H4}">',
           '<rect width="100%" height="100%" fill="#ffffff"/>']
    grp = label_svg_group(concept, ring_shape, cuff_sil, win_label)
    for (lx, ly) in pos:
        out.append(f'<g transform="translate({lx:.3f},{ly:.3f})">')
        out.append(f'<clipPath id="c{lx:.0f}"><rect x="-2" y="-2" width="{LW + 4:.3f}" height="{LH + 4:.3f}"/></clipPath>')
        out.append(f'<g clip-path="url(#c{lx:.0f})">{grp}</g></g>')
        for (cx, cy) in ((lx, ly), (lx + LW, ly), (lx, ly + LH), (lx + LW, ly + LH)):   # Schnittmarken
            sx = -1 if cx == lx else 1
            sy = -1 if cy == ly else 1
            out.append(f'<line x1="{cx + sx * 3:.2f}" y1="{cy:.2f}" x2="{cx + sx * 8:.2f}" y2="{cy:.2f}" stroke="#000" stroke-width="0.2"/>')
            out.append(f'<line x1="{cx:.2f}" y1="{cy + sy * 3:.2f}" x2="{cx:.2f}" y2="{cy + sy * 8:.2f}" stroke="#000" stroke-width="0.2"/>')
    out.append(f'<text x="15" y="290" font-family="Arial" font-size="3" fill="#555">Türzwerg Front-Etikett · Konzept {concept} „{CONCEPTS[concept]}“ · mit 100 % / „Tatsächliche Größe“ drucken · Kontrolle: Etikett {LW:.1f} × {LH:.1f} mm</text>')
    out.append("</svg>")
    svg = "\n".join(out)
    import cairosvg
    cairosvg.svg2pdf(bytestring=svg.encode(), write_to=os.path.join(d, f"Front-Etikett_A4_Konzept_{concept}.pdf"))
    with open(os.path.join(d, f"Front-Etikett_A4_Konzept_{concept}.svg"), "w") as f:
        f.write(svg)


def label_positions():
    """Etiketten auf A4 (mm von oben links)."""
    return [(15.0, 20.0), (15.0 + LW + 13.0, 20.0)]


def write_label_texture(concept, ring_shape, cuff_sil, win_label, fn, ppm=8):
    """PNG der Front für den 3D-Viewer, Fenster transparent."""
    import io
    import cairosvg
    from PIL import Image, ImageDraw
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{LW * ppm:.0f}" height="{LH * ppm:.0f}" '
           f'viewBox="0 0 {LW:.3f} {LH:.3f}">' + label_svg_group(concept, ring_shape, cuff_sil, win_label) + "</svg>")
    img = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode()))).convert("RGBA")
    mask = Image.new("L", img.size, 255)
    dr = ImageDraw.Draw(mask)
    for w in win_label.values():
        dr.polygon([(x * ppm, y * ppm) for x, y in (to_label(*q) for q in w.exterior.coords)], fill=0)
    img.putalpha(mask)
    img.save(fn, optimize=True)


# --------------------------------------------------------------------------
# DXF/SVG-Export in Mattengröße (Eckmarken -> Silhouette skaliert nicht)
# --------------------------------------------------------------------------
PAGE = (304.8, 304.8)
PERF = {"berg": (2.5, 2.0), "tal": (1.2, 1.5)}
LAYERS = [("SCHNEIDEN", 1, "#e00000", None), ("RILLEN_BERG", 5, "#0050ff", "3,1.5"),
          ("RILLEN_TAL", 3, "#00a040", "1,1.5"), ("KONTROLLE", 7, "#000000", None)]


def perforate(lines, cut, gap):
    out = []
    for pl in lines:
        ls = LineString(pl)
        L = ls.length
        n = max(int((L - gap) // (cut + gap)), 1)
        s = (L - n * cut - (n - 1) * gap) / 2
        for _ in range(n):
            a, b = ls.interpolate(s), ls.interpolate(min(s + cut, L))
            out.append([(a.x, a.y), (b.x, b.y)])
            s += cut + gap
    return out


def save_dxf(fn, layers):
    doc = ezdxf.new("R12")
    msp = doc.modelspace()
    for lname, col, pls in layers:
        doc.layers.new(lname, dxfattribs={"color": col})
        for pl in pls:
            closed = len(pl) > 2 and math.dist(pl[0], pl[-1]) < 1e-6
            msp.add_polyline2d(pl[:-1] if closed else pl, close=closed, dxfattribs={"layer": lname, "color": col})
    doc.saveas(fn)


def save_svg(fn, groups):
    PW, PH = PAGE
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{PW}mm" height="{PH}mm" viewBox="0 0 {PW} {PH}">']
    for (lname, _, color, dash), pls in zip(LAYERS, groups):
        da = f' stroke-dasharray="{dash}"' if dash else ""
        out.append(f'<g id="{lname}" fill="none" stroke="{color}" stroke-width="0.25"{da}>')
        for pl in pls:
            out.append('<path d="M' + " L".join(f"{x:.3f},{PH - y:.3f}" for x, y in pl) + '"/>')
        out.append("</g>")
    out.append("</svg>")
    with open(fn, "w") as f:
        f.write("\n".join(out))


def control_square(cut, x, y):
    return [list(box(x, y, x + 30, y + 30).exterior.coords)]


def place(paths, dx, dy):
    return [[(x + dx, y + dy) for x, y in pl] for pl in paths]


def write_plot(d, name, cut, mountain, valley, extra_check=True, pos="center", single=False):
    """Schreibt <name>_perforiert.dxf/.svg und <name>_komplett.dxf/.svg in Mattengröße."""
    PW, PH = PAGE
    bb = bounds(cut + mountain + valley)
    w, h = bb[2] - bb[0], bb[3] - bb[1]
    if pos == "center":
        dx, dy = (PW - w) / 2 - bb[0], PH - 10 - h - bb[1]
    else:                                                   # Koordinaten sind schon Mattenkoordinaten
        dx = dy = 0.0
    cut, mountain, valley = place(cut, dx, dy), place(mountain, dx, dy), place(valley, dx, dy)
    nb = bounds(cut + mountain + valley)
    assert nb[0] >= 5 and nb[1] >= 5 and nb[2] <= PW - 5 and nb[3] <= PH - 5, (name, nb)
    corners = [[(0, 2.0), (0, 0), (2.0, 0)], [(PW - 2.0, PH), (PW, PH), (PW, PH - 2.0)]]
    sq = control_square(cut, 10, 10) if extra_check and nb[1] > 45 else []
    check = sq + corners
    if single:
        save_dxf(os.path.join(d, f"{name}.dxf"), [("SCHNEIDEN", 1, cut), ("KONTROLLE", 7, check)])
        save_svg(os.path.join(d, f"{name}.svg"), [cut, [], [], check])
        return round(w, 1), round(h, 1)
    save_dxf(os.path.join(d, f"{name}_komplett.dxf"),
             [("SCHNEIDEN", 1, cut), ("RILLEN_BERG", 5, mountain), ("RILLEN_TAL", 3, valley), ("KONTROLLE", 7, check)])
    save_svg(os.path.join(d, f"{name}_komplett.svg"), [cut, mountain, valley, check])
    pb, pt = perforate(mountain, *PERF["berg"]), perforate(valley, *PERF["tal"])
    save_dxf(os.path.join(d, f"{name}_perforiert.dxf"),
             [("SCHNEIDEN", 1, cut + pb + pt), ("KONTROLLE", 7, check)])
    save_svg(os.path.join(d, f"{name}_perforiert.svg"), [cut + pb + pt, [], [], check])
    return round(w, 1), round(h, 1)


def label_cut_paths(win_label):
    """Etikett-Schnitt auf der Matte: A4 liegt bündig oben links auf der Matte."""
    PW, PH = PAGE
    out = []
    for (lx, ly) in label_positions():
        rect = box(lx, PH - ly - LH, lx + LW, PH - ly)
        out += list(lines_of(rect))
        for w in win_label.values():
            ww = affinity.translate(w, 0, 0)
            pts = [to_label(x, y) for x, y in ww.exterior.coords]
            out.append([(lx + a, PH - ly - b) for a, b in pts])
    return out


# --------------------------------------------------------------------------
# 3D
# --------------------------------------------------------------------------
def extrude_xy(poly, z0, th):
    solid = cq.Workplane("XY").workplane(offset=z0).polyline(list(poly.exterior.coords)[:-1]).close().extrude(th)
    for hole in poly.interiors:
        h = cq.Workplane("XY").workplane(offset=z0 - 1).polyline(list(hole.coords)[:-1]).close().extrude(th + 2)
        solid = solid.cut(h)
    return solid


def blk(x0, x1, y0, y1, z0, z1):
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))


def rod(a, b, r=2.0):
    a, b = cq.Vector(*a), cq.Vector(*b)
    return cq.Solid.makeCylinder(r, (b - a).Length, a, (b - a).normalized())


def build_3d(ring, cuff, ins):
    Wi, Hi, Di, hh = p["Wi"], p["Hi"], p["Di"], p["hang_h"]
    X0, X1 = -Wi / 2 - t, Wi / 2 + t
    # Karton ohne Front (die Front zeigt der Viewer als bedruckte Fläche mit Fenstern)
    shell = (blk(X0, X1, -t, Hi + t, -t, 0)
             .union(blk(X0, -Wi / 2, -t, Hi + t, 0, Di)).union(blk(Wi / 2, X1, -t, Hi + t, 0, Di))
             .union(blk(-Wi / 2, Wi / 2, -t, 0, 0, Di)))
    lid = blk(-Wi / 2, Wi / 2, Hi, Hi + t, 0, Di + t)
    eh = euro_hole(0, Hi + hh - p["euro_from_top"])
    hang = rrect(X0, Hi - 10, X1, Hi + hh, 5).intersection(box(X0, Hi + t, X1, Hi + hh)).difference(eh)
    dbl = rrect(X0 + 0.75, Hi + 1 + t - 10, X1 - 0.75, Hi + hh, 5).intersection(box(X0, Hi + 1 + t, X1, Hi + hh)).difference(eh)
    hanger = extrude_xy(hang, -t, t).union(extrude_xy(dbl, 0, t))
    # Einleger
    W, H, hw = ins["W"], ins["H"], ins["hw"]
    x0, x1 = -W / 2, W / 2
    deck_poly = box(x0, 0, x1, H).difference(ins["cuff_hole"]).difference(box(-p["slit"] / 2, Y_SLIT - 0.6, p["slit"] / 2, Y_SLIT + 0.6))
    for a, tp in ins["tabs"]:
        deck_poly = deck_poly.difference(tp)
    insert = extrude_xy(deck_poly, Z_DECK - t, t)
    insert = (insert.union(blk(x0, x0 + t, 0.5, H - 0.5, 0, Z_DECK)).union(blk(x1 - t, x1, 0.5, H - 0.5, 0, Z_DECK))
              .union(blk(x0 + 0.5, x1 - 0.5, 0, t, 0, Z_DECK)).union(blk(x0 + 0.5, x1 - 0.5, H - t, H, 0, Z_DECK)))
    for a, tp in ins["tabs"]:                                  # Zentrierlaschen stehen senkrecht
        u = (math.cos(math.radians(a)), math.sin(math.radians(a)))
        v = (-u[1], u[0])
        rh, w, L = p["tab_r"], p["tab_w"], p["tab_l"]
        c = cq.Vector(rh * u[0], Yr + rh * u[1], Z_DECK)
        tab = (cq.Workplane("XY").box(w, t, L, centered=(True, True, False))
               .rotate((0, 0, 0), (0, 0, 1), a - 90).translate((c.x, c.y, Z_DECK)))
        insert = insert.union(tab)
    # Teile
    ring_s = cq.Workplane().add(ring).translate((0, Yr, Z_RING))
    cuff_s = cq.Workplane().add(cuff).rotate((0, 0, 0), (0, 1, 0), 90).translate((-CUFF_L / 2, Yc, Z_CUFF))
    zs = Z_DECK + 2.0
    segs = [rod((0, Yc - KEEL + 2, Z_CUFF), (0, Y_SLIT + 2, zs)), rod((0, Y_SLIT + 2, zs), (0, Y_SLIT, Z_DECK - 3)),
            rod((0, Y_SLIT, Z_DECK - 3), (0, Y_SLIT - 1.5, zs)), rod((0, Y_SLIT - 1.5, zs), (0, Yr + R_RING - 2, Z_RING))]
    zc = (Z_DECK - t) / 2
    segs += [cq.Solid.makeTorus(16.0 - 4 * k, 1.9, cq.Vector(0, Yr + 8, zc + (k % 2) * 0.5), cq.Vector(0, 0, 1)) for k in range(3)]
    segs += [rod((0, Y_SLIT, Z_DECK - 3), (10, Yr + 22, zc))]
    cord = cq.Workplane().add(segs[0])
    for sg in segs[1:]:
        cord = cord.union(cq.Workplane().add(sg))
    parts = [("Umverpackung", shell, (0.96, 0.95, 0.92)), ("Aufhaenger", hanger, (0.96, 0.95, 0.92)),
             ("Deckel", lid, (0.96, 0.95, 0.92)), ("Einleger", insert, (0.80, 0.66, 0.46)),
             ("Ring", ring_s, (0.84, 1.0, 0.12)), ("Manschette", cuff_s, (0.84, 1.0, 0.12)),
             ("Schnur", cord, (0.55, 0.12, 0.10))]
    assy = cq.Assembly(name="Tuerzwerg_Verpackung")
    for name, shp, col in parts:
        assy.add(shp, name=name, color=cq.Color(*col))
    assy.export(os.path.join(OUT, "Tuerzwerg_Verpackung.step"))
    import numpy as np
    import trimesh
    scene = trimesh.Scene()
    for name, shp, col in parts:
        verts, faces = [], []
        for solid in shp.vals():
            v_, f_ = solid.tessellate(0.05, 0.2)
            off = len(verts)
            verts += [(q.x, q.y, q.z) for q in v_]
            faces += [(a + off, b + off, c + off) for a, b, c in f_]
        m = trimesh.Trimesh(np.array(verts) / 1000.0, np.array(faces), process=True)
        m.visual = trimesh.visual.ColorVisuals(m, face_colors=[int(c * 255) for c in col] + [255])
        scene.add_geometry(m, node_name=name, geom_name=name)
    scene.export(os.path.join(OUT, "Tuerzwerg_Verpackung.glb"))


# --------------------------------------------------------------------------
def main():
    os.makedirs(OUT, exist_ok=True)
    ring, cuff, ring_shape, cuff_sil = load_parts()
    ins = insert_geometry(cuff_sil)
    info = dict(params=P, Yr=Yr, Yc=Yc, Y_cord=Y_CORD, Y_slit=Y_SLIT, Z_deck=Z_DECK, Z_ring=Z_RING, Z_cuff=Z_CUFF,
                label_mm=[round(LW, 2), round(LH, 2)],
                outer_mm=[round(p["Wi"] + 2 * t, 1), round(p["Hi"] + 2 * t, 1), round(p["Di"] + 2 * t, 1)],
                insert_mm=[round(ins["W"], 2), round(ins["H"], 2), round(Z_DECK, 2)],
                concepts={})
    for c in CONCEPTS:
        win = windows(c)
        win_card = [w.buffer(p["win_card"], resolution=24) for w in win.values()]
        d = os.path.join(OUT, f"Konzept_{c}_{CONCEPTS[c]}")
        os.makedirs(d, exist_ok=True)
        bc, bm, bv, _ = box_blank(win_card)
        s_box = write_plot(d, "1_Umverpackung", bc, bm, bv)
        s_ins = write_plot(d, "2_Einleger", ins["cut"], ins["mountain"], ins["valley"])
        lab = label_cut_paths(win)
        s_lab = write_plot(d, "3_Front-Etikett_schneiden", lab, [], [], extra_check=False, pos="fixed", single=True)
        write_label_print(c, ring_shape, cuff_sil, win, d)
        write_label_texture(c, ring_shape, cuff_sil, win, os.path.join(OUT, f"front_{c}.png"))
        info["concepts"][c] = dict(name=CONCEPTS[c], dir=os.path.basename(d),
                                   windows={k: [round(v, 1) for v in (w.bounds[2] - w.bounds[0], w.bounds[3] - w.bounds[1])]
                                            for k, w in win.items()},
                                   blank_box_mm=s_box, blank_insert_mm=s_ins)
    build_3d(ring, cuff, ins)
    with open(os.path.join(OUT, "masse.json"), "w") as f:
        json.dump(info, f, indent=2, ensure_ascii=False)
    print(json.dumps({k: v for k, v in info.items() if k != "params"}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

"""Baut out/viewer.html: 3D-Ansicht, Längsschnitt, Zuschnitte, Ablauf (alles eingebettet)."""
import base64
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
THREE = "https://cdn.jsdelivr.net/npm/three@0.147.0"
VARIANTS = ("C",)


def de(x, n=1):
    return f"{x:.{n}f}".replace(".", ",")


def vdir(v):
    return OUT


def svg_inline(v, name):
    s = open(os.path.join(vdir(v), f"{name}.svg")).read()
    return re.sub(r'width="[^"]+mm" height="[^"]+mm"', f'class="blank" role="img" aria-label="Zuschnitt {name}"', s, count=1)


def section_svg(m):
    """Maßstäblicher Längsschnitt (Kartonmitte), Y nach rechts, Z nach oben."""
    pr = m["params"]
    S = 3.6
    Hi, Di, t = pr["Hi"], pr["Di"], pr["t"]
    H, ZD = pr["ins_h"], m["deck_Z"]
    Y1, Y2 = pr["split_y1"], pr["split_y2"]
    ZR, ZS, ZC, Yr, Yc, ym = m["ring_floor_Z"], m["cord_floor_Z"], m["cuff_floor_Z"], m["Yr"], m["Yc"], m["Y_cord"]
    zc = m["cuff_axis_Z"]
    padL, padT = 14, 22
    X = lambda y: padL + y * S
    Y = lambda z: padT + (Di - z) * S
    W, Hh = X(Hi) + 14, Y(0) + 52
    o = [f'<svg viewBox="0 0 {W:.0f} {Hh:.0f}" class="sect" role="img" aria-label="Längsschnitt durch Karton und Einleger">']
    wb = m["window_bounds"]
    o.append(f'<path class="box" d="M{X(0)},{Y(0)} L{X(Hi)},{Y(0)} M{X(0)},{Y(0)} L{X(0)},{Y(Di)} M{X(Hi)},{Y(0)} L{X(Hi)},{Y(Di)}'
             f' M{X(0)},{Y(Di)} L{X(wb[1])},{Y(Di)} M{X(wb[3])},{Y(Di)} L{X(Hi)},{Y(Di)}"/>')
    pts = [(0.3, ZD), (0.3, ZR - t / 2), (Y1, ZR - t / 2), (Y1, ZS - t / 2), (Y2, ZS - t / 2), (Y2, ZC - t / 2), (H, ZC - t / 2), (H, ZD)]
    o.append('<path class="ins" d="M' + " L".join(f"{X(y):.1f},{Y(z):.1f}" for y, z in pts) + '"/>')
    o.append(f'<path class="ins deck" d="M{X(0.3):.1f},{Y(ZD):.1f} L{X(H):.1f},{Y(ZD):.1f}"/>')
    for yy in (Yr - 21, Yr + 21):   # Füße
        o.append(f'<path class="ins" d="M{X(yy):.1f},{Y(ZR - t):.1f} L{X(yy):.1f},{Y(0):.1f}"/>')
    for y0, y1 in ((pr["ring_bottom"], pr["ring_bottom"] + 11.5), (Yr + 36 - 11.5, Yr + 36)):
        o.append(f'<rect class="part" x="{X(y0):.1f}" y="{Y(ZR + 14):.1f}" width="{(y1 - y0) * S:.1f}" height="{14 * S:.1f}" rx="{5 * S:.1f}"/>')
    o.append(f'<path class="part" d="M{X(Yc - 20.5):.1f},{Y(zc):.1f} L{X(Yc - 6):.1f},{Y(zc + 8):.1f} L{X(Yc - 6):.1f},{Y(zc - 8):.1f} Z"/>')
    o.append(f'<circle class="part" cx="{X(Yc):.1f}" cy="{Y(zc):.1f}" r="{11.5 * S:.1f}"/>')
    o.append(f'<circle class="hollow" cx="{X(Yc):.1f}" cy="{Y(zc):.1f}" r="{9 * S:.1f}"/>')
    o.append(f'<path class="axis" d="M{X(2):.1f},{Y(zc):.1f} L{X(Hi - 2):.1f},{Y(zc):.1f}"/>')
    o.append(f'<path class="cord" d="M{X(Yc - 20.5):.1f},{Y(zc):.1f} L{X(ym + 2):.1f},{Y(zc):.1f} L{X(ym):.1f},{Y(ZS - 2):.1f}'
             f' L{X(ym + 5):.1f},{Y(6.4):.1f} L{X(ym + 5):.1f},{Y(2.6):.1f} L{X(ym - 5):.1f},{Y(2.6):.1f} L{X(ym - 5):.1f},{Y(6.4):.1f} L{X(ym):.1f},{Y(ZS - 2):.1f}'
             f' L{X(ym - 2):.1f},{Y(zc):.1f} L{X(Yr + 34):.1f},{Y(zc):.1f}"/>')
    def lab(x, y, txt, anchor="middle", cls="lab"):
        o.append(f'<text class="{cls}" x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}">{txt}</text>')
    lab(X(Yr), Y(Di) - 8, f'{de(m["ring_front_gap"], 2)} mm bis zur Front')
    lab(X(Yc), Y(Di) - 8, f'{de(m["cuff_front_gap"], 2)} mm bis zur Front')
    lab(X(Yr), Y(0) + 16, "Ringboden auf Füßen")
    lab(X(ym), Y(0) + 16, "Schnurfach")
    lab(X(Yc), Y(0) + 16, "Manschettenboden")
    lab(X(ym), Y(0) + 30, "Kreuzschlitz", cls="lab small")
    lab(X(Hi) - 4, Y(ZD) - 3, "Deck", anchor="end", cls="lab small")
    lab(X(Hi) - 4, Y(zc) + 10, f"Mitte {de(zc, 2)} mm", anchor="end", cls="lab small")
    lab(X(0), Y(0) + 44, "unten", anchor="start", cls="lab small")
    lab(X(Hi), Y(0) + 44, "oben (Hänger)", anchor="end", cls="lab small")
    o.append("</svg>")
    return "".join(o)


def dl(m):
    pr, o = m["params"], m["outer_mm"]
    bw, bh = m["blank_sizes_mm"]["Umverpackung"]
    iw, ih = m["blank_sizes_mm"]["Einleger"]
    rows = [
        ("Karton außen (B×H×T)", f"{o[0]:.0f} × {o[1]:.0f} × {o[2]:.0f} mm"),
        ("Hänger, klappt nach vorn", f"+{pr['hang_h']:.0f} mm"),
        ("Ring → Front", f"{de(m['ring_front_gap'], 2)} mm"),
        ("Manschette → Front", f"{de(m['cuff_front_gap'], 2)} mm"),
        ("Deck über Rückwand", f"{de(m['deck_Z'])} mm"),
        ("Schnurfach", "{} × {} × {} mm".format(*[de(x, 0 if i < 2 else 1) for i, x in enumerate(m["cord_store_mm"])])),
        ("Zuschnitt Umverpackung", f"{bw:.0f} × {bh:.0f} mm"),
        ("Zuschnitt Einleger", f"{iw:.0f} × {ih:.0f} mm"),
        ("Matte Einleger", "12×24″" if max(iw, ih) > 290 else "12×12″ / A4"),
        ("Ringmitte = Manschettenachse", f"{de(m['ring_center_Z'], 2)} mm"),
    ]
    return "<dl>" + "".join(f"<dt>{a}</dt><dd>{b}</dd>" for a, b in rows) + "</dl>"


HOW = {
    "C": """<div class="note"><h3>Mitte auf Mitte</h3>
<p>Die Mitte des Rings liegt auf derselben Höhe wie die Achse der Manschette (11,95 mm über der Rückwand). Damit liegen beide Schnurbohrungen auf einer Linie und die Schnur läuft gerade.</p>
<p>Die Manschette liegt auf dem Boden an der Rückwand und reicht bis 0,55 mm an die Front. Der Ring liegt auf einem Boden 4,5 mm höher, der auf vier Füßen steht. Er sitzt 5 mm hinter der Front, statt 9,5 mm wie bei gleichem Boden.</p>
<p>Das Deck liegt auf 14,7 mm, knapp über der breitesten Stelle beider Teile. Der Ring rastet ein (Loch 0,35 mm kleiner, kurze Zungen). Die Manschette wird eingelegt, die Fensterränder an ihren Stirnseiten halten sie.</p></div>
<div class="note"><h3>Schnur</h3>
<p>Im 20-mm-Sichtfeld liegt die Schnur gerade auf Höhe der Bohrungen über einem Schnurboden. Mittig darin ist ein Kreuzschlitz, durch den die Restschnur von rund 28 cm als Schlaufe ins Fach darunter geschoben wird. Das Fach misst 88 × 16 × 8,5 mm und läuft unter dem Ringboden flach weiter.</p>
<p>Einleger: ein Streifen mit 8 Querfalzen, Seitenflanschen und 4 Füßen, 116 × 322 mm, braucht die 12×24″-Matte.</p></div>""",
}

STEPS = {
    "C": """<li><b>Ring eindrücken.</b> Einleger flach hinlegen, Ring mit Bohrung nach oben ins runde Loch drücken, bis er einrastet.</li>
<li><b>Manschette einlegen.</b> Mit Kiel zum Ring ins obere Loch.</li>
<li><b>Schnur verstauen.</b> Mitte der Schnur als Schlaufe durch den Kreuzschlitz ins Schnurfach schieben, bis beide Stücke gerade liegen.</li>
<li><b>Einschieben.</b> Karton mit der Front nach oben halten, Einleger von unten einschieben.</li>
<li><b>Schließen.</b> Staublaschen einklappen, Bodendeckel einstecken. Hänger für den Versand nach vorn auf den Deckel klappen.</li>""",
}


def variant_blocks(v, m):
    bw, bh = m["blank_sizes_mm"]["Umverpackung"]
    iw, ih = m["blank_sizes_mm"]["Einleger"]
    hidden = ""
    return dict(
        dl=f'<div data-v="{v}"{hidden}>{dl(m)}</div>',
        sect=f'<div class="sectwrap" data-v="{v}"{hidden}>{section_svg(m)}</div>',
        how=f'<div class="two" data-v="{v}"{hidden}>{HOW[v]}</div>',
        steps=f'<ol class="steps" data-v="{v}"{hidden}>{STEPS[v]}</ol>',
        blanks=f'''<div class="blanks" data-v="{v}"{hidden}>
<figure><div class="paper">{svg_inline(v, "Umverpackung")}</div><figcaption>Umverpackung, {bw:.0f} × {bh:.0f} mm, 12×12″-Matte. Links oben: Hänger mit Doppelung, die Doppelung wird innen (zur Front hin) verklebt.</figcaption></figure>
<figure><div class="paper">{svg_inline(v, "Einleger")}</div><figcaption>Einleger, {iw:.0f} × {ih:.0f} mm, 12×24″-Matte. Von links: Deck mit Seitenflanschen, Wand unten, Ringboden mit 4 Füßen, Stufe, Schnurboden mit Kreuzschlitz, Stufe, Manschettenboden, Klebelasche. Oben: Wand oben.</figcaption></figure></div>''',
    )


def main():
    ms = {v: json.load(open(os.path.join(vdir(v), "masse.json"))) for v in VARIANTS}
    blocks = {v: variant_blocks(v, ms[v]) for v in VARIANTS}
    glbs = {v: base64.b64encode(open(os.path.join(vdir(v), "Tuerzwerg_Verpackung.glb"), "rb").read()).decode() for v in VARIANTS}
    pr = ms["C"]["params"]
    html = TEMPLATE
    for key in ("dl", "sect", "how", "steps", "blanks"):
        html = html.replace(f"%%{key.upper()}%%", "".join(blocks[v][key] for v in VARIANTS))
    html = (html.replace("%%GLBS%%", json.dumps(glbs)).replace("%%THREE%%", THREE)
            .replace("%%HINGE_Y%%", f"{pr['Hi'] + pr['t']:.3f}").replace("%%HINGE_Z%%", f"{-pr['t']:.3f}"))
    with open(os.path.join(OUT, "viewer.html"), "w") as f:
        f.write(html)
    print("viewer.html", len(html) // 1024, "kB")


TEMPLATE = r"""<title>Türzwerg Verpackung</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;700&family=Source+Sans+3:wght@400;600&family=JetBrains+Mono:wght@400;600&display=swap">
<style>
/* Layout: technisches Datenblatt – große 3D-Bühne links, Maße/Bedienung rechts, darunter Schnitt, Erklärung, Ablauf, Zuschnitte */
:root{
  --bg:#eef0ea; --panel:#ffffff; --fg:#1d2420; --muted:#5d6760; --line:#d3d8cf;
  --kraft:#b58a52; --neon:#c6ec00; --part:#a9c400; --cordc:#9c2a20; --cut:#d40000; --score:#0050ff;
  --stage:#e3e6de; --paper:#ffffff;
  --f-display:"Barlow Condensed","Arial Narrow",sans-serif;
  --f-body:"Source Sans 3","Segoe UI",system-ui,sans-serif;
  --f-mono:"JetBrains Mono",ui-monospace,Menlo,Consolas,monospace;
}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){
  --bg:#161a17; --panel:#1f2420; --fg:#e7ebe4; --muted:#9aa49c; --line:#343b35;
  --kraft:#d2a66a; --neon:#d4f53a; --part:#c8e83a; --cordc:#e0604f; --stage:#232924; color-scheme:dark}}
:root[data-theme="dark"]{
  --bg:#161a17; --panel:#1f2420; --fg:#e7ebe4; --muted:#9aa49c; --line:#343b35;
  --kraft:#d2a66a; --neon:#d4f53a; --part:#c8e83a; --cordc:#e0604f; --stage:#232924; color-scheme:dark}
[hidden]{display:none!important}
body{background:var(--bg);color:var(--fg);font-family:var(--f-body);font-size:15px;line-height:1.5}
.wrap{max-width:1240px;margin:0 auto;padding-block:20px 48px;
  padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));
  display:flex;flex-direction:column;gap:28px}
header{display:flex;flex-wrap:wrap;align-items:baseline;gap:6px 18px}
h1{font-family:var(--f-display);font-weight:700;font-size:clamp(30px,5vw,46px);letter-spacing:.01em;margin:0;line-height:1}
h1 .tag{display:inline-block;background:var(--neon);color:#1d2420;padding:0 .25em;margin-left:.2em}
header p{margin:0;color:var(--muted);max-width:64ch}
h2{font-family:var(--f-display);font-weight:700;font-size:26px;margin:0 0 10px;text-wrap:balance}
h3{font-family:var(--f-display);font-weight:500;font-size:19px;margin:0 0 6px;letter-spacing:.02em}
.grid{display:grid;grid-template-columns:minmax(0,1fr) 330px;gap:20px}
@media (max-width:900px){.grid{grid-template-columns:minmax(0,1fr)}}
.stage{position:relative;background:var(--stage);border:1px solid var(--line);aspect-ratio:4/3.4;max-width:100%;min-height:340px}
#c{position:absolute;inset:0;width:100%;height:100%;display:block;touch-action:none}
.hint{position:absolute;left:10px;bottom:8px;font-size:12px;color:var(--muted);pointer-events:none}
.side{display:flex;flex-direction:column;gap:18px;min-width:0}
.ctl{display:flex;flex-direction:column;gap:12px;background:var(--panel);border:1px solid var(--line);padding:14px}
.views{display:grid;grid-template-columns:repeat(3,1fr);gap:6px}
button{font:600 13px var(--f-body);background:transparent;color:var(--fg);border:1px solid var(--line);padding:7px 6px;cursor:pointer}
button[aria-pressed="true"]{background:var(--fg);color:var(--bg);border-color:var(--fg)}
button:focus-visible,input:focus-visible{outline:2px solid var(--kraft);outline-offset:2px}
label{display:flex;flex-direction:column;gap:4px;font-size:13px;color:var(--muted)}
label span{display:flex;justify-content:space-between}
input[type=range]{width:100%;accent-color:var(--kraft)}
.chk{flex-direction:row;align-items:center;gap:8px;color:var(--fg)}
dl{margin:0;display:grid;grid-template-columns:auto auto;gap:5px 12px;font-size:14px}
dt{color:var(--muted)}
dd{margin:0;text-align:right;font-family:var(--f-mono);font-size:13px;font-variant-numeric:tabular-nums}
.label{font:600 11px var(--f-body);text-transform:uppercase;letter-spacing:.09em;color:var(--muted)}
.sectwrap{background:var(--panel);border:1px solid var(--line);padding:12px;overflow-x:auto}
.sect{width:100%;min-width:560px;height:auto;display:block}
.sect .box{fill:none;stroke:var(--fg);stroke-width:1.6}
.sect .ins{fill:none;stroke:var(--kraft);stroke-width:1.8;stroke-linejoin:round}
.sect .deck{stroke-dasharray:5 3}
.sect .part{fill:var(--part);stroke:none;opacity:.9}
.sect .hollow{fill:var(--panel)}
.sect .axis{fill:none;stroke:var(--muted);stroke-width:.8;stroke-dasharray:2 3}
.sect .cord{fill:none;stroke:var(--cordc);stroke-width:4;stroke-linecap:round;stroke-linejoin:round}
.sect .lab{fill:var(--fg);font:600 8px var(--f-body)}
.sect .small{fill:var(--muted);font-weight:400}
.blanks{display:grid;grid-template-columns:minmax(0,1.15fr) minmax(0,1fr);gap:20px}
@media (max-width:800px){.blanks{grid-template-columns:minmax(0,1fr)}}
figure{margin:0;display:flex;flex-direction:column;gap:8px;min-width:0}
.paper{background:var(--paper);border:1px solid var(--line);padding:10px;overflow-x:auto}
.blank{width:100%;height:auto;display:block;max-height:640px}
figcaption{font-size:13px;color:var(--muted)}
.legend{display:flex;flex-wrap:wrap;gap:16px;font-size:13px;margin-bottom:12px}
.legend i{display:inline-block;width:26px;height:0;border-top:2px solid var(--cut);vertical-align:middle;margin-right:6px}
.legend i.s{border-top:2px dashed var(--score)}
ol.steps{margin:0;padding:0;list-style:none;counter-reset:s;display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px}
ol.steps li{counter-increment:s;background:var(--panel);border:1px solid var(--line);padding:12px 14px;min-width:0}
ol.steps li::before{content:counter(s);font:700 24px var(--f-display);color:var(--kraft);display:block;line-height:1}
.two{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:20px}
.note{background:var(--panel);border:1px solid var(--line);padding:14px 16px;min-width:0}
.note p,.note ul{margin:.3em 0}
.note ul{padding-left:1.1em}
code,.mono{font-family:var(--f-mono);font-size:.88em}
table{border-collapse:collapse;width:100%;font-size:14px}
td,th{border-bottom:1px solid var(--line);padding:5px 6px;text-align:left;vertical-align:top}
th{font-weight:600;color:var(--muted)}
.tw{overflow-x:auto}
</style>

<div class="wrap">
<header>
  <h1>Türzwerg <span class="tag">Verpackung</span></h1>
  <p>Faltschachtel 90 × 140 × 25 mm mit Euroloch-Hänger, der zum Versand nach vorn auf den Deckel klappt. Im Einleger liegen Ringmitte und Manschettenachse auf gleicher Höhe, die Schnur läuft gerade und verschwindet mittig in einem Schnurfach.</p>
</header>

<section class="grid" aria-label="3D-Entwurf">
  <div class="stage">
    <canvas id="c" aria-label="3D-Modell der Verpackung"></canvas>
    <div class="hint" id="hint">Ziehen = drehen · Scrollen/Pinch = zoomen · Rechtsklick = verschieben</div>
  </div>
  <div class="side">
    <div class="ctl">
      <div class="label">Ansicht</div>
      <div class="views" role="group" aria-label="Kameraposition">
        <button id="v-front" aria-pressed="true">Vorne</button>
        <button id="v-iso" aria-pressed="false">Schräg</button>
        <button id="v-side" aria-pressed="false">Seite</button>
      </div>
      <label for="slide"><span>Einleger einschieben <b id="slideVal" class="mono">0 mm</b></span>
        <input id="slide" type="range" min="0" max="160" value="0" step="1"></label>
      <label for="hang"><span>Hänger klappen <b id="hangVal" class="mono">aufgestellt</b></span>
        <input id="hang" type="range" min="0" max="90" value="0" step="5"></label>
      <label for="alpha"><span>Karton-Deckkraft <b id="alphaVal" class="mono">100 %</b></span>
        <input id="alpha" type="range" min="0" max="100" value="100" step="5"></label>
      <label class="chk" for="cut"><input id="cut" type="checkbox"> Schnitt durch die Mitte</label>
    </div>
    <div class="ctl">
      <div class="label">Eckdaten</div>
      %%DL%%
    </div>
  </div>
</section>

<section aria-labelledby="h-sect">
  <h2 id="h-sect">Längsschnitt</h2>
  %%SECT%%
  <p style="color:var(--muted);font-size:13px;margin:8px 0 0">Maßstäblich, Schnitt durch die Kartonmitte, Karton liegend. Braun = Einleger, gestrichelt = Deck (in der Mitte liegen die Löcher).</p>
</section>

<section aria-labelledby="h-how">
  <h2 id="h-how">So funktioniert es</h2>
  %%HOW%%
  <div class="note" style="margin-top:20px">
    <h3>Hänger und Versand</h3>
    <p>Der Hänger klappt 90° nach vorn und liegt dann flach auf dem Deckel. Der Falz wird nur um 90° gebogen statt um 180°. Damit das geht, ist der Hänger 24 mm hoch, also etwas flacher als der Karton tief (24,9 mm). Umgeklappt steht nichts über.</p>
    <p>Das Euroloch sitzt mit 5 mm Steg unter der Oberkante. Die Doppelung ist 1 mm kürzer, damit sie beim Umklappen nicht gegen den Deckel drückt. Eine Verriegelung braucht es nicht: Am Haken hängt die Schachtel mit klappbarem Hänger praktisch genauso schräg wie mit starrem, weil ihr Schwerpunkt in beiden Fällen etwa 12 mm vor der Rückwand liegt.</p>
    <p>Im Umkarton sind die Schachteln dann glatte Quader von 90 × 141 × 25 mm. 100 Stück: 2 Lagen à 5 × 10, Umkarton innen ca. 450 × 250 × 285 mm (32 l).</p>
  </div>
</section>

<section aria-labelledby="h-steps">
  <h2 id="h-steps">Bestücken</h2>
  %%STEPS%%
</section>

<section aria-labelledby="h-plot">
  <h2 id="h-plot">Zuschnitte für den Silhouette Cameo 4</h2>
  <div class="legend"><span><i></i>Schneiden</span><span><i class="s"></i>Rillen / Falzen</span><span>Ansicht: Außenseite (Druckseite) oben</span></div>
  %%BLANKS%%
</section>

<section aria-labelledby="h-sil">
  <h2 id="h-sil">Einstellungen Silhouette Studio</h2>
  <div class="two">
    <div class="note">
      <h3>Dateien</h3>
      <ul>
        <li><code>*_komplett.dxf</code>: Schneiden (rot) und Rillen (blau) zusammen. In Studio unter „Schneiden“ → „Linienfarbe“ getrennt einstellen.</li>
        <li><code>*_schneiden.dxf</code> / <code>*_rillen.dxf</code>: getrennt, falls die Farben beim DXF-Import verloren gehen. Beide an Position 0/0 importieren.</li>
        <li><code>*.svg</code>: für die Designer Edition, Maßstab in mm.</li>
        <li>Nach dem Import die Breite prüfen: Umverpackung 241 mm.</li>
      </ul>
    </div>
    <div class="note">
      <h3>Startwerte für 300–350 g/m² Karton</h3>
      <div class="tw"><table>
        <tr><th>Linie</th><th>Werkzeug</th><th>Klinge</th><th>Kraft</th><th>Tempo</th><th>Durchgänge</th></tr>
        <tr><td>Schneiden</td><td>AutoBlade</td><td>8–10</td><td>30–33</td><td>3</td><td>2</td></tr>
        <tr><td>Rillen</td><td>AutoBlade</td><td>1–2</td><td>10–15</td><td>3</td><td>1</td></tr>
      </table></div>
      <p>Erst einen Teststreifen schneiden. Leicht angeritzte Rilllinien von der Ritzung weg falzen.</p>
    </div>
  </div>
</section>
</div>

<script src="%%THREE%%/build/three.min.js"></script>
<script src="%%THREE%%/examples/js/loaders/GLTFLoader.js"></script>
<script src="%%THREE%%/examples/js/controls/OrbitControls.js"></script>
<script>
(function(){
  const GLBS = %%GLBS%%;
  let variant = 'C';
  const canvas = document.getElementById('c');
  const hint = document.getElementById('hint');

  if (!window.THREE || !THREE.GLTFLoader) { hint.textContent = '3D-Bibliothek konnte nicht geladen werden.'; return; }
  const renderer = new THREE.WebGLRenderer({canvas, antialias:true, alpha:true});
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.outputEncoding = THREE.sRGBEncoding;
  renderer.localClippingEnabled = true;
  const scene = new THREE.Scene();
  const cam = new THREE.PerspectiveCamera(30, 1, 1, 5000);
  const controls = new THREE.OrbitControls(cam, canvas);
  controls.enableDamping = true;
  scene.add(new THREE.HemisphereLight(0xffffff, 0x8a8f86, 0.75));
  const sun = new THREE.DirectionalLight(0xffffff, 0.8); sun.position.set(120, 220, 260); scene.add(sun);
  const fill = new THREE.DirectionalLight(0xffffff, 0.35); fill.position.set(-200, -60, 120); scene.add(fill);

  const clip = new THREE.Plane(new THREE.Vector3(-1,0,0), 0);
  let groupBox, groupIns, hinge, tongue, mats;
  const COL = {Umverpackung:0xf6f4ee, Aufhaenger:0xf6f4ee, Zunge:0xf6f4ee, Einleger:0xc9a473, Ring:0xd4ff1c, Manschette:0xd4ff1c, Schnur:0x8c1f19};
  const target = new THREE.Vector3(0, 85, 12);

  window.loadModel = function(v){
    [groupBox, groupIns, hinge].forEach(g => { if (g) { scene.remove(g); g.traverse(o => { if (o.geometry) o.geometry.dispose(); }); } });
    groupBox = new THREE.Group(); groupIns = new THREE.Group(); hinge = new THREE.Group();
    hinge.position.set(0, %%HINGE_Y%%, %%HINGE_Z%%);
    scene.add(groupBox, groupIns, hinge);
    tongue = null; mats = {};
    const bin = Uint8Array.from(atob(GLBS[v]), c => c.charCodeAt(0)).buffer;
    new THREE.GLTFLoader().parse(bin, '', gltf => {
      const meshes = [];
      gltf.scene.traverse(o => { if (o.isMesh) meshes.push(o); });
      meshes.forEach(o => {
        const key = Object.keys(COL).find(k => o.name.startsWith(k) || (o.parent && o.parent.name.startsWith(k))) || 'Einleger';
        const isPart = key === 'Ring' || key === 'Manschette';
        const m = new THREE.MeshStandardMaterial({color:COL[key], roughness:isPart?0.35:0.9, metalness:0,
          transparent:true, opacity:isPart?0.92:1, side:THREE.DoubleSide});
        if (isPart) m.emissive = new THREE.Color(0x3a4a00);
        mats[key] = mats[key] || []; mats[key].push(m);
        let g = o.geometry;
        if (isPart || key === 'Schnur') { g.deleteAttribute('normal'); g.computeVertexNormals(); }
        else { g = g.toNonIndexed(); g.computeVertexNormals(); }
        const mesh = new THREE.Mesh(g, m);
        o.updateWorldMatrix(true, false);
        mesh.applyMatrix4(o.matrixWorld);
        mesh.scale.multiplyScalar(1000); mesh.position.multiplyScalar(1000);
        const edges = new THREE.LineSegments(new THREE.EdgesGeometry(o.geometry, 30),
          new THREE.LineBasicMaterial({color:isPart?0x7d9400:(key==='Schnur'?0x5a120e:0x8a7a62), transparent:true, opacity:0.55}));
        mats[key].push(edges.material);
        mesh.add(edges);
        if (key === 'Aufhaenger') { mesh.position.sub(hinge.position); hinge.add(mesh); }
        else if (key === 'Umverpackung' || key === 'Zunge') { groupBox.add(mesh); if (key === 'Zunge') tongue = mesh; }
        else groupIns.add(mesh);
      });
      apply();
    }, () => { hint.textContent = 'Modell konnte nicht geladen werden.'; });
  };

  const views = {front:[0,85,400], iso:[230,165,300], side:[400,85,12]};
  function setView(v){
    const p = views[v]; cam.position.set(p[0], p[1], p[2]); controls.target.copy(target); controls.update();
    ['front','iso','side'].forEach(k => document.getElementById('v-'+k).setAttribute('aria-pressed', k===v));
  }
  ['front','iso','side'].forEach(k => document.getElementById('v-'+k).addEventListener('click', () => setView(k)));

  const slide = document.getElementById('slide'), alpha = document.getElementById('alpha'),
        cut = document.getElementById('cut'), hang = document.getElementById('hang');
  function apply(){
    if (!groupIns) return;
    groupIns.position.y = -Number(slide.value);
    document.getElementById('slideVal').textContent = slide.value + ' mm';
    const deg = Number(hang.value);
    hinge.rotation.x = deg * Math.PI / 180;
    if (tongue) tongue.visible = deg < 3;
    document.getElementById('hangVal').textContent = deg === 0 ? 'aufgestellt' : (deg === 90 ? 'Versand (auf dem Deckel)' : deg + '°');
    const a = Number(alpha.value)/100;
    document.getElementById('alphaVal').textContent = alpha.value + ' %';
    ['Umverpackung','Aufhaenger','Zunge'].forEach(k => (mats[k]||[]).forEach(m => { m.opacity = m.isLineBasicMaterial ? 0.55*Math.max(a,0.25) : a; m.depthWrite = a > 0.98; }));
    Object.values(mats).flat().forEach(m => { m.clippingPlanes = cut.checked ? [clip] : []; m.needsUpdate = true; });
  }
  [slide, alpha, hang].forEach(el => el.addEventListener('input', apply));
  cut.addEventListener('change', () => { if (cut.checked) setView('side'); apply(); });

  function fit(){
    const r = canvas.getBoundingClientRect();
    renderer.setSize(r.width, r.height, false);
    cam.aspect = r.width / Math.max(r.height,1); cam.updateProjectionMatrix();
  }
  new ResizeObserver(fit).observe(canvas);
  function animate(){ requestAnimationFrame(animate); controls.update(); renderer.render(scene, cam); }
  setView('front'); fit(); window.loadModel(variant); animate();
})();
</script>
"""

if __name__ == "__main__":
    main()

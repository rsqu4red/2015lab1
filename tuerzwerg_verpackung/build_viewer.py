"""Baut out/viewer.html: 3D-Ansicht + Querschnitt + Zuschnitte + Ablauf (alles eingebettet)."""
import base64
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
THREE = "https://cdn.jsdelivr.net/npm/three@0.147.0"


def svg_inline(name):
    s = open(os.path.join(OUT, f"{name}.svg")).read()
    return re.sub(r'width="[^"]+mm" height="[^"]+mm"', f'class="blank" role="img" aria-label="Zuschnitt {name}"', s, count=1)


def section_svg(m):
    """Maßstäblicher Längsschnitt (Seitenansicht in Kartonmitte), Y nach rechts, Z nach oben."""
    pr = m["params"]
    S = 3.6
    Hi, Di, t = pr["Hi"], pr["Di"], pr["t"]
    H, Ys, ZD = pr["ins_h"], pr["split_y"], m["deck_Z"]
    ZR, ZC, Yr, Yc = m["ring_floor_Z"], m["cuff_floor_Z"], m["Yr"], m["Yc"]
    padL, padT = 14, 22
    X = lambda y: padL + y * S
    Y = lambda z: padT + (Di - z) * S
    W, Hh = X(Hi) + 14, Y(0) + 52
    o = [f'<svg viewBox="0 0 {W:.0f} {Hh:.0f}" class="sect" role="img" aria-label="Längsschnitt durch Karton und Einleger">']
    # Karton: Rückwand, Front mit Fensteröffnungen, Boden/Deckel
    wb = m["window_bounds"]
    o.append(f'<path class="box" d="M{X(0)},{Y(0)} L{X(Hi)},{Y(0)} M{X(0)},{Y(0)} L{X(0)},{Y(Di)} M{X(Hi)},{Y(0)} L{X(Hi)},{Y(Di)}'
             f' M{X(0)},{Y(Di)} L{X(wb[1])},{Y(Di)} M{X(wb[3])},{Y(Di)} L{X(Hi)},{Y(Di)}"/>')
    # Einleger als ein Streifen
    pts = [(0.3, ZD), (0.3, ZR - t / 2), (Ys, ZR - t / 2), (Ys, ZC - t / 2), (H, ZC - t / 2), (H, ZD)]
    o.append('<path class="ins" d="M' + " L".join(f"{X(y):.1f},{Y(z):.1f}" for y, z in pts) + '"/>')
    # Deck: in Kartonmitte liegt das Loch -> gestrichelt (Lochkante dahinter)
    o.append(f'<path class="ins deck" d="M{X(0.3):.1f},{Y(ZD):.1f} L{X(H):.1f},{Y(ZD):.1f}"/>')
    # Ring (Schnitt durch zwei Stellen des Rings), Manschette (Rohr + Kiel)
    for y0, y1 in ((pr["ring_bottom"], pr["ring_bottom"] + 11.5), (Yr + 36 - 11.5, Yr + 36)):
        o.append(f'<rect class="part" x="{X(y0):.1f}" y="{Y(ZR + 14):.1f}" width="{(y1 - y0) * S:.1f}" height="{14 * S:.1f}" rx="{5 * S:.1f}"/>')
    zc = ZC + 11.5
    o.append(f'<path class="part" d="M{X(Yc - 20.5):.1f},{Y(zc):.1f} L{X(Yc - 6):.1f},{Y(zc + 8):.1f} L{X(Yc - 6):.1f},{Y(zc - 8):.1f} Z"/>')
    o.append(f'<circle class="part" cx="{X(Yc):.1f}" cy="{Y(zc):.1f}" r="{11.5 * S:.1f}"/>')
    o.append(f'<circle class="hollow" cx="{X(Yc):.1f}" cy="{Y(zc):.1f}" r="{9 * S:.1f}"/>')
    # Schnur
    ys = pr["cord_slot_y"]
    o.append(f'<path class="cord" d="M{X(Yc - 20.5):.1f},{Y(zc):.1f} Q{X(ys + 3):.1f},{Y(ZR + 2):.1f} {X(ys):.1f},{Y(ZR - 3):.1f}'
             f' Q{X(ys - 8):.1f},{Y(2.5):.1f} {X(55):.1f},{Y(2.6):.1f} L{X(20):.1f},{Y(2.6):.1f} Q{X(10):.1f},{Y(4.6):.1f} {X(20):.1f},{Y(6.6):.1f}'
             f' L{X(60):.1f},{Y(6.6):.1f} Q{X(ys - 3):.1f},{Y(7):.1f} {X(ys - 1):.1f},{Y(ZR + 1):.1f} L{X(Yr + 34):.1f},{Y(ZR + 7):.1f}"/>')
    # Beschriftung
    def lab(x, y, txt, anchor="middle", cls="lab"):
        o.append(f'<text class="{cls}" x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}">{txt}</text>')
    g = f'{pr["gap"]:.2f}'.replace(".", ",")
    lab(X(Yr), Y(Di) - 8, f'{g} mm bis zur Front')
    lab(X(Yc), Y(Di) - 8, f'{g} mm bis zur Front')
    lab(X(Yr), Y(0) + 16, "Ringboden + Schnurfach darunter")
    lab(X(Yc), Y(0) + 16, "Manschettenboden")
    lab(X(ys), Y(0) + 30, "Kreuzschlitz", cls="lab small")
    lab(X(Hi) - 4, Y(ZD) - 3, "Deck", anchor="end", cls="lab small")
    lab(X(0), Y(0) + 44, "unten", anchor="start", cls="lab small")
    lab(X(Hi), Y(0) + 44, "oben (Hänger)", anchor="end", cls="lab small")
    o.append("</svg>")
    return "".join(o)


def main():
    m = json.load(open(os.path.join(OUT, "masse.json")))
    pr = m["params"]
    glb = base64.b64encode(open(os.path.join(OUT, "Tuerzwerg_Verpackung.glb"), "rb").read()).decode()
    bw, bh = m["blank_sizes_mm"]["Umverpackung"]
    iw, ih = m["blank_sizes_mm"]["Einleger"]
    o = m["outer_mm"]
    rep = {
        "%%GLB%%": glb,
        "%%THREE%%": THREE,
        "%%SVG_BOX%%": svg_inline("Umverpackung"),
        "%%SVG_INS%%": svg_inline("Einleger"),
        "%%SECTION%%": section_svg(m),
        "%%OUTER%%": f"{o[0]:.0f} × {o[1]:.0f} × {o[2]:.0f}",
        "%%HANG%%": f"{pr['hang_h']:.0f}",
        "%%BOXBLANK%%": f"{bw:.0f} × {bh:.0f}",
        "%%INSBLANK%%": f"{iw:.0f} × {ih:.0f}",
        "%%GAP%%": f"{pr['gap']:.2f}".replace(".", ","),
        "%%ZR%%": f"{m['ring_floor_Z']:.1f}".replace(".", ","),
        "%%ZD%%": f"{m['deck_Z']:.1f}".replace(".", ","),
        "%%CORD%%": f"{pr['cord_visible']:.0f}",
        "%%STORE%%": "{:.0f} × {:.0f} × {:.1f}".format(*m["cord_store_mm"]).replace(".", ","),
        "%%T%%": f"{pr['t']:.2f}".replace(".", ","),
        "%%HI%%": f"{pr['Hi']:.0f}",
        "%%HINGE_Y%%": f"{pr['Hi'] + pr['t']:.3f}",
        "%%HINGE_Z%%": f"{-pr['t']:.3f}",
    }
    html = TEMPLATE
    for k, v in rep.items():
        html = html.replace(k, v)
    with open(os.path.join(OUT, "viewer.html"), "w") as f:
        f.write(html)
    print("viewer.html", len(html) // 1024, "kB")


TEMPLATE = r"""<title>Türzwerg Verpackung</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;700&family=Source+Sans+3:wght@400;600&family=JetBrains+Mono:wght@400;600&display=swap">
<style>
/* Layout: technisches Datenblatt – große 3D-Bühne links, Maße/Bedienung rechts, darunter Schnitt, Zuschnitte, Ablauf */
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
.grid{display:grid;grid-template-columns:minmax(0,1fr) 320px;gap:20px}
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
.sect .cord{fill:none;stroke:var(--cordc);stroke-width:4;stroke-linecap:round;stroke-linejoin:round}
.sect .lab{fill:var(--fg);font:600 8px var(--f-body)}
.sect .small{fill:var(--muted);font-weight:400}
.blanks{display:grid;grid-template-columns:minmax(0,1.15fr) minmax(0,1fr);gap:20px}
@media (max-width:800px){.blanks{grid-template-columns:minmax(0,1fr)}}
figure{margin:0;display:flex;flex-direction:column;gap:8px;min-width:0}
.paper{background:var(--paper);border:1px solid var(--line);padding:10px;overflow-x:auto}
.blank{width:100%;height:auto;display:block;max-height:640px}
figcaption{font-size:13px;color:var(--muted)}
.legend{display:flex;flex-wrap:wrap;gap:16px;font-size:13px}
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
  <p>Faltschachtel mit klappbarem Euroloch-Hänger und Einleger mit gestuftem Boden. Ring und Manschette fallen in ihre Löcher und liegen beide %%GAP%% mm hinter dem Sichtfenster. Die Restschnur verschwindet mittig in einem Schnurfach.</p>
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
        <input id="hang" type="range" min="0" max="180" value="0" step="5"></label>
      <label for="alpha"><span>Karton-Deckkraft <b id="alphaVal" class="mono">100 %</b></span>
        <input id="alpha" type="range" min="0" max="100" value="100" step="5"></label>
      <label class="chk" for="cut"><input id="cut" type="checkbox"> Schnitt durch die Mitte</label>
    </div>
    <div class="ctl">
      <div class="label">Eckdaten</div>
      <dl>
        <dt>Karton außen (B×H×T)</dt><dd>%%OUTER%% mm</dd>
        <dt>Hänger, doppellagig, klappbar</dt><dd>+%%HANG%% mm</dd>
        <dt>Euroloch</dt><dd>32 × 6 / Ø10</dd>
        <dt>Karton</dt><dd>%%T%% mm, 300–350 g/m²</dd>
        <dt>Ring → Front</dt><dd>%%GAP%% mm</dd>
        <dt>Manschette → Front</dt><dd>%%GAP%% mm</dd>
        <dt>Ringboden über Rückwand</dt><dd>%%ZR%% mm</dd>
        <dt>Deck über Rückwand</dt><dd>%%ZD%% mm</dd>
        <dt>Schnur-Sichtfeld</dt><dd>%%CORD%% mm</dd>
        <dt>Schnurfach</dt><dd>%%STORE%% mm</dd>
        <dt>Zuschnitt Umverpackung</dt><dd>%%BOXBLANK%% mm</dd>
        <dt>Zuschnitt Einleger</dt><dd>%%INSBLANK%% mm</dd>
      </dl>
    </div>
  </div>
</section>

<section aria-labelledby="h-sect">
  <h2 id="h-sect">Längsschnitt</h2>
  <div class="sectwrap">%%SECTION%%</div>
  <p style="color:var(--muted);font-size:13px;margin:8px 0 0">Maßstäblich, Schnitt durch die Kartonmitte, Karton liegend. Braun = Einleger, ein einziger Streifen mit quer laufenden Falzen.</p>
</section>

<section aria-labelledby="h-how">
  <h2 id="h-how">So funktioniert es</h2>
  <div class="two">
    <div class="note">
      <h3>Gleiche Höhe für Ring und Manschette</h3>
      <p>Der Einleger hat zwei Böden. Die Manschette (23 mm) liegt direkt auf der Rückwand, der Ring (14 mm) auf einem Boden, der 9 mm höher liegt. Dadurch enden beide Vorderseiten in derselben Ebene, %%GAP%% mm hinter der Front.</p>
      <p>Das Deck mit den Löchern sitzt auf %%ZD%% mm, nahe der breitesten Stelle beider Teile. Die Löcher haben 0,25 mm Luft: Die Teile werden hineingelegt, nicht gedrückt. Nach vorn halten sie die Fensterränder: Das runde Fenster ist 5 mm kleiner als der Ring, das Fenster der Manschette 4 mm kürzer als sie.</p>
      <p>Für die beiden Böden auf gleiche Front muss die Kartontiefe zur Manschette passen. Deshalb ist der Karton jetzt 25 statt 30 mm tief. Bei 30 mm läge vor beiden Teilen nur zusätzliche Luft.</p>
    </div>
    <div class="note">
      <h3>Schnur</h3>
      <p>Von der Kielspitze der Manschette läuft die Schnur mittig nach unten und taucht in einen Kreuzschlitz im Ringboden. Darunter liegt ein flaches Schnurfach (%%STORE%% mm) für die übrigen rund 28 cm. Aus demselben Schlitz läuft sie wieder hoch in die Bohrung oben im Ring.</p>
      <p>Im %%CORD%%-mm-Sichtfeld sieht man also die Schnur in der Mitte nach hinten verschwinden und wieder auftauchen. Die vier Laschen des Kreuzschlitzes legen sich um die Schnur und halten sie mittig.</p>
      <h3 style="margin-top:12px">Hänger</h3>
      <p>Volle Breite, zwei Lagen, Falz an der Oberkante. Für den Versand wird er flach nach hinten auf die Rückwand geklappt. Im Laden wird er hochgeklappt und die Zunge der Doppelung in den Schlitz im Deckel gesteckt. Die Schultern der Zunge rasten unter dem Deckel ein und halten den Hänger senkrecht.</p>
    </div>
  </div>
</section>

<section aria-labelledby="h-steps">
  <h2 id="h-steps">Bestücken</h2>
  <ol class="steps">
    <li><b>Ring einlegen.</b> Einleger flach hinlegen, Ring mit Bohrung nach oben ins runde Loch legen. Er fällt auf den Ringboden.</li>
    <li><b>Manschette einlegen.</b> Mit Kiel zum Ring ins obere Loch. Sie fällt auf den Manschettenboden.</li>
    <li><b>Schnur verstauen.</b> Die Schnur in der Mitte durch den Kanal fassen und als Schlaufe durch den Kreuzschlitz ins Schnurfach schieben, bis beide Stücke gerade sind.</li>
    <li><b>Einschieben.</b> Karton mit der Front nach oben halten und den Einleger von unten einschieben. Die Teile stehen nicht über.</li>
    <li><b>Schließen.</b> Staublaschen einklappen, Bodendeckel einstecken. Der Hänger bleibt für den Versand umgeklappt.</li>
  </ol>
</section>

<section aria-labelledby="h-plot">
  <h2 id="h-plot">Zuschnitte für den Silhouette Cameo 4</h2>
  <div class="legend"><span><i></i>Schneiden</span><span><i class="s"></i>Rillen / Falzen</span><span>Ansicht: Außenseite (Druckseite) oben</span></div>
  <div class="blanks" style="margin-top:12px">
    <figure><div class="paper">%%SVG_BOX%%</div>
      <figcaption>Umverpackung, %%BOXBLANK%% mm, passt auf die 12×12″-Matte. Links oben: Hänger mit Doppelung und Verriegelungszunge. Im oberen Deckel: Schlitz für die Zunge.</figcaption></figure>
    <figure><div class="paper">%%SVG_INS%%</div>
      <figcaption>Einleger, %%INSBLANK%% mm, braucht die 12×24″-Matte. Von oben: Wand oben, Deck mit Seitenflanschen, Wand unten, Ringboden mit Kreuzschlitz, Stufe, Manschettenboden, Klebelasche (wird innen an die Wand oben geklebt).</figcaption></figure>
  </div>
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
        <li>Nach dem Import die Breite prüfen: Umverpackung %%BOXBLANK%% mm.</li>
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
  const GLB = "%%GLB%%";
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
  const groupBox = new THREE.Group(), groupIns = new THREE.Group();
  const hinge = new THREE.Group(); hinge.position.set(0, %%HINGE_Y%%, %%HINGE_Z%%);
  scene.add(groupBox, groupIns, hinge);
  let tongue = null;
  const mats = {};
  const COL = {Umverpackung:0xf6f4ee, Aufhaenger:0xf6f4ee, Zunge:0xf6f4ee, Einleger:0xc9a473, Ring:0xd4ff1c, Manschette:0xd4ff1c, Schnur:0x8c1f19};
  const target = new THREE.Vector3(0, 85, 12);

  const bin = Uint8Array.from(atob(GLB), c => c.charCodeAt(0)).buffer;
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
    setView('front'); fit(); animate();
  }, () => { hint.textContent = 'Modell konnte nicht geladen werden.'; });

  const views = {front:[0,90,410], iso:[230,170,300], side:[400,90,12]};
  function setView(v){
    const p = views[v]; cam.position.set(p[0], p[1], p[2]); controls.target.copy(target); controls.update();
    ['front','iso','side'].forEach(k => document.getElementById('v-'+k).setAttribute('aria-pressed', k===v));
  }
  ['front','iso','side'].forEach(k => document.getElementById('v-'+k).addEventListener('click', () => setView(k)));

  const slide = document.getElementById('slide'), alpha = document.getElementById('alpha'),
        cut = document.getElementById('cut'), hang = document.getElementById('hang');
  function apply(){
    groupIns.position.y = -Number(slide.value);
    document.getElementById('slideVal').textContent = slide.value + ' mm';
    const deg = Number(hang.value);
    hinge.rotation.x = -deg * Math.PI / 180;
    if (tongue) tongue.visible = deg < 3;
    document.getElementById('hangVal').textContent = deg === 0 ? 'aufgestellt' : (deg === 180 ? 'Versand (flach)' : deg + '°');
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
})();
</script>
"""

if __name__ == "__main__":
    main()

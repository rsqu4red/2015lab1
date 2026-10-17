"""Baut out/viewer.html: Fensterkonzepte A/B/C, 3D mit bedruckter Front, Schnitt, Zuschnitte, Ablauf."""
import base64
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
THREE = "https://cdn.jsdelivr.net/npm/three@0.147.0"


def de(x, n=1):
    return f"{x:.{n}f}".replace(".", ",")


def b64(fn):
    return base64.b64encode(open(fn, "rb").read()).decode()


def plot_svg(concept_dir, name):
    s = open(os.path.join(OUT, concept_dir, name + ".svg")).read()
    s = s.replace('stroke-width="0.25"', 'stroke-width="0.45"')
    return re.sub(r'width="[^"]+mm" height="[^"]+mm"', f'class="blank" role="img" aria-label="{name}"', s, count=1)


def section_svg(m):
    pr = m["params"]
    S = 3.8
    Hi, Di, t = pr["Hi"], pr["Di"], pr["t"]
    Yr, Yc, ZD, ys = m["Yr"], m["Yc"], m["Z_deck"], m["Y_slit"]
    H = m["insert_mm"][1]
    padL, padT = 14, 20
    X = lambda y: padL + y * S
    Y = lambda z: padT + (Di - z) * S
    W, Hh = X(Hi) + 14, Y(0) + 46
    o = [f'<svg viewBox="0 0 {W:.0f} {Hh:.0f}" class="sect" role="img" aria-label="Längsschnitt">']
    o.append(f'<path class="box" d="M{X(0)},{Y(0)} L{X(Hi)},{Y(0)} L{X(Hi)},{Y(Di)} L{X(0)},{Y(Di)} Z"/>')
    o.append(f'<path class="print" d="M{X(0.3)},{Y(Di) - 2.5} L{X(Hi - 0.3)},{Y(Di) - 2.5}"/>')
    cb = (Yc - 20.5 - 0.3, Yc + 11.5 + 0.3)
    o.append(f'<path class="ins" d="M{X(0.2):.1f},{Y(0):.1f} L{X(0.2):.1f},{Y(ZD):.1f} L{X(cb[0]):.1f},{Y(ZD):.1f} '
             f'M{X(cb[1]):.1f},{Y(ZD):.1f} L{X(H):.1f},{Y(ZD):.1f} L{X(H):.1f},{Y(0):.1f}"/>')
    for y0, y1 in ((Yr - 36, Yr - 36 + 11.5), (Yr + 36 - 11.5, Yr + 36)):
        o.append(f'<rect class="part" x="{X(y0):.1f}" y="{Y(ZD + 14):.1f}" width="{(y1 - y0) * S:.1f}" height="{14 * S:.1f}" rx="{5 * S:.1f}"/>')
    zc = m["Z_cuff"]
    o.append(f'<path class="part" d="M{X(Yc - 20.5):.1f},{Y(zc):.1f} L{X(Yc - 6):.1f},{Y(zc + 8):.1f} L{X(Yc - 6):.1f},{Y(zc - 8):.1f} Z"/>')
    o.append(f'<circle class="part" cx="{X(Yc):.1f}" cy="{Y(zc):.1f}" r="{11.5 * S:.1f}"/>')
    o.append(f'<circle class="hollow" cx="{X(Yc):.1f}" cy="{Y(zc):.1f}" r="{9 * S:.1f}"/>')
    zr = m["Z_ring"]
    o.append(f'<path class="cord" d="M{X(Yc - 20.5):.1f},{Y(zc):.1f} L{X(ys + 2.5):.1f},{Y(ZD + 2):.1f} L{X(ys):.1f},{Y(ZD - 2):.1f} '
             f'L{X(ys - 6):.1f},{Y(5.8):.1f} L{X(ys - 30):.1f},{Y(5.8):.1f} L{X(ys - 30):.1f},{Y(2.6):.1f} L{X(ys - 6):.1f},{Y(2.6):.1f} '
             f'L{X(ys):.1f},{Y(ZD - 2):.1f} L{X(ys - 1.5):.1f},{Y(ZD + 2):.1f} L{X(Yr + 34):.1f},{Y(zr):.1f}"/>')
    def lab(x, y, txt, anchor="middle", cls="lab"):
        o.append(f'<text class="{cls}" x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}">{txt}</text>')
    lab(X(Hi / 2), Y(Di) - 7, "bedruckte Front mit drei kleinen Fenstern – Ring und Manschette liegen innen an", cls="lab small")
    lab(X(Yr), Y(0) + 15, "Ring liegt auf der Einleger-Platte")
    lab(X(ys - 15), Y(0) + 28, "Schnurfach unter der Platte", cls="lab small")
    lab(X(Yc), Y(0) + 15, "Manschette steht auf der Rückwand")
    lab(X(0), Y(0) + 40, "unten", anchor="start", cls="lab small")
    lab(X(Hi), Y(0) + 40, "oben (Hänger)", anchor="end", cls="lab small")
    o.append("</svg>")
    return "".join(o)


CONCEPT_TEXT = {
    "A": ("Kapsel", "Abgerundete Langlöcher. Auf dem Ring ein Bogen, der der Ringform folgt – dort liegt die flache Ringstirn, ideal zum Fühlen."),
    "B": ("Bullauge", "Runde Fenster wie Bullaugen. An der Schnur ein schmales Langloch, damit 14 mm Schnur zu sehen sind."),
    "C": ("Mittelachse", "Schmale Schlitze auf einer senkrechten Linie durch alle drei Teile. Sehr ruhig und grafisch."),
}


def main():
    m = json.load(open(os.path.join(OUT, "masse.json")))
    pr = m["params"]
    glb = b64(os.path.join(OUT, "Tuerzwerg_Verpackung.glb"))
    fronts = {c: "data:image/png;base64," + b64(os.path.join(OUT, f"front_{c}.png")) for c in m["concepts"]}
    cards, blanks, dls = [], [], []
    for c, info in m["concepts"].items():
        name, txt = CONCEPT_TEXT[c]
        hidden = "" if c == "A" else " hidden"
        w = info["windows"]
        cards.append(f'''<button class="card" id="k-{c}" aria-pressed="{'true' if c == 'A' else 'false'}">
  <img src="{fronts[c]}" alt="Front Konzept {c}"><span><b>{c} · {name}</b><small>{txt}</small></span></button>''')
        dls.append(f'''<dl data-k="{c}"{hidden}>
  <dt>Fenster Manschette</dt><dd>{de(w["Manschette"][0], 0)} × {de(w["Manschette"][1], 0)} mm</dd>
  <dt>Fenster Schnur</dt><dd>{de(w["Schnur"][0], 0)} × {de(w["Schnur"][1], 0)} mm</dd>
  <dt>Fenster Ring</dt><dd>{de(w["Ring"][0], 0)} × {de(w["Ring"][1], 0)} mm</dd></dl>''')
        d = info["dir"]
        blanks.append(f'''<div class="blanks" data-k="{c}"{hidden}>
<figure><div class="paper">{plot_svg(d, "1_Umverpackung_komplett")}</div><figcaption>1 · Umverpackung, Matte 12×12″</figcaption></figure>
<figure><div class="paper">{plot_svg(d, "2_Einleger_komplett")}</div><figcaption>2 · Einleger, Matte 12×12″</figcaption></figure>
<figure><div class="paper">{plot_svg(d, "3_Front-Etikett_schneiden")}</div><figcaption>3 · Front-Etiketten, A4-Druck bündig oben links auf der Matte</figcaption></figure></div>''')
    o = m["outer_mm"]
    rep = {
        "%%CARDS%%": "\n".join(cards), "%%DLS%%": "\n".join(dls), "%%BLANKS%%": "\n".join(blanks),
        "%%SECTION%%": section_svg(m), "%%GLB%%": glb, "%%FRONTS%%": json.dumps(fronts), "%%THREE%%": THREE,
        "%%OUTER%%": f"{de(o[0], 0)} × {de(o[1], 0)} × {de(o[2], 0)}",
        "%%HANG%%": f"{pr['hang_h']:.0f}", "%%LW%%": f"{m['label_mm'][0]:.3f}", "%%LH%%": f"{m['label_mm'][1]:.3f}",
        "%%LABEL%%": f"{de(m['label_mm'][0])} × {de(m['label_mm'][1])}",
        "%%INS%%": f"{de(m['insert_mm'][0])} × {de(m['insert_mm'][1])}",
        "%%ZD%%": de(m["Z_deck"], 0),
        "%%FY%%": f"{pr['Hi'] / 2:.3f}", "%%FZ%%": f"{pr['Di'] + pr['t'] + 0.05:.3f}",
        "%%HINGE_Y%%": f"{pr['Hi'] + pr['t']:.3f}", "%%HINGE_Z%%": f"{-pr['t']:.3f}",
        "%%LID_Y%%": f"{pr['Hi'] + pr['t'] / 2:.3f}", "%%LID_Z%%": f"{pr['Di'] + pr['t']:.3f}",
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
/* Layout: Konzeptwahl oben, 3D-Bühne mit Bedienung, darunter Schnitt, Ablauf, Zuschnitte */
:root{
  --bg:#eef0ea; --panel:#ffffff; --fg:#1d2420; --muted:#5d6760; --line:#d3d8cf;
  --kraft:#b58a52; --neon:#c6ec00; --part:#a9c400; --cordc:#9c2a20; --stage:#e3e6de; --paper:#ffffff; --print:#24282b;
  --f-display:"Barlow Condensed","Arial Narrow",sans-serif;
  --f-body:"Source Sans 3","Segoe UI",system-ui,sans-serif;
  --f-mono:"JetBrains Mono",ui-monospace,Menlo,Consolas,monospace;
}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){
  --bg:#161a17; --panel:#1f2420; --fg:#e7ebe4; --muted:#9aa49c; --line:#343b35;
  --kraft:#d2a66a; --neon:#d4f53a; --part:#c8e83a; --cordc:#e0604f; --stage:#232924; --print:#9aa49c; color-scheme:dark}}
:root[data-theme="dark"]{
  --bg:#161a17; --panel:#1f2420; --fg:#e7ebe4; --muted:#9aa49c; --line:#343b35;
  --kraft:#d2a66a; --neon:#d4f53a; --part:#c8e83a; --cordc:#e0604f; --stage:#232924; --print:#9aa49c; color-scheme:dark}
[hidden]{display:none!important}
body{background:var(--bg);color:var(--fg);font-family:var(--f-body);font-size:15px;line-height:1.5}
.wrap{max-width:1240px;margin:0 auto;padding-block:20px 48px;
  padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));
  display:flex;flex-direction:column;gap:28px}
header{display:flex;flex-wrap:wrap;align-items:baseline;gap:6px 18px}
h1{font-family:var(--f-display);font-weight:700;font-size:clamp(30px,5vw,46px);letter-spacing:.01em;margin:0;line-height:1}
h1 .tag{display:inline-block;background:var(--neon);color:#1d2420;padding:0 .25em;margin-left:.2em}
header p{margin:0;color:var(--muted);max-width:66ch}
h2{font-family:var(--f-display);font-weight:700;font-size:26px;margin:0 0 10px;text-wrap:balance}
h3{font-family:var(--f-display);font-weight:500;font-size:19px;margin:0 0 6px;letter-spacing:.02em}
.cards{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}
@media (max-width:760px){.cards{grid-template-columns:minmax(0,1fr)}}
.card{display:grid;grid-template-columns:72px minmax(0,1fr);gap:12px;align-items:start;text-align:left;padding:10px;background:var(--panel)}
.card img{width:72px;height:auto;display:block;border-radius:2px}
.card span{display:flex;flex-direction:column;gap:4px;min-width:0}
.card b{font:700 18px var(--f-display);letter-spacing:.02em}
.card small{font:400 13px/1.4 var(--f-body);color:var(--muted)}
.card[aria-pressed="true"]{background:var(--panel);color:var(--fg);border:2px solid var(--fg)}
.grid{display:grid;grid-template-columns:minmax(0,1fr) 320px;gap:20px}
@media (max-width:900px){.grid{grid-template-columns:minmax(0,1fr)}}
.stage{position:relative;background:var(--stage);border:1px solid var(--line);aspect-ratio:4/3.4;max-width:100%;min-height:340px}
#c{position:absolute;inset:0;width:100%;height:100%;display:block;touch-action:none}
.hint{position:absolute;left:10px;bottom:8px;font-size:12px;color:var(--muted);pointer-events:none}
.side{display:flex;flex-direction:column;gap:18px;min-width:0}
.ctl{display:flex;flex-direction:column;gap:12px;background:var(--panel);border:1px solid var(--line);padding:14px}
.views{display:grid;grid-template-columns:repeat(3,1fr);gap:6px}
button{font:600 13px var(--f-body);background:transparent;color:var(--fg);border:1px solid var(--line);padding:7px 6px;cursor:pointer}
.views button[aria-pressed="true"]{background:var(--fg);color:var(--bg);border-color:var(--fg)}
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
.sect .print{fill:none;stroke:var(--print);stroke-width:3}
.sect .ins{fill:none;stroke:var(--kraft);stroke-width:1.8;stroke-linejoin:round}
.sect .part{fill:var(--part);stroke:none;opacity:.9}
.sect .hollow{fill:var(--panel)}
.sect .cord{fill:none;stroke:var(--cordc);stroke-width:4;stroke-linecap:round;stroke-linejoin:round}
.sect .lab{fill:var(--fg);font:600 8px var(--f-body)}
.sect .small{fill:var(--muted);font-weight:400}
.blanks{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}
@media (max-width:900px){.blanks{grid-template-columns:minmax(0,1fr)}}
figure{margin:0;display:flex;flex-direction:column;gap:8px;min-width:0}
.paper{background:var(--paper);border:1px solid var(--line);padding:6px}
.blank{width:100%;height:auto;display:block}
figcaption{font-size:13px;color:var(--muted)}
ol.steps{margin:0;padding:0;list-style:none;counter-reset:s;display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px}
ol.steps li{counter-increment:s;background:var(--panel);border:1px solid var(--line);padding:12px 14px;min-width:0}
ol.steps li::before{content:counter(s);font:700 24px var(--f-display);color:var(--kraft);display:block;line-height:1}
.two{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:20px}
.note{background:var(--panel);border:1px solid var(--line);padding:14px 16px;min-width:0}
.note p,.note ul{margin:.3em 0}
.note ul{padding-left:1.1em}
code{font-family:var(--f-mono);font-size:.88em}
table{border-collapse:collapse;width:100%;font-size:14px}
td,th{border-bottom:1px solid var(--line);padding:5px 6px;text-align:left;vertical-align:top}
th{font-weight:600;color:var(--muted)}
.tw{overflow-x:auto}
</style>

<div class="wrap">
<header>
  <h1>Türzwerg <span class="tag">Verpackung</span></h1>
  <p>Geschlossene, bedruckte Front mit Manschette, Schnur und Ring in Originalgröße. Drei kleine Sichtfenster zeigen das echte Material genau dort, wo es hinter der Grafik liegt. Ring und Manschette liegen innen an der Front an, der Einleger ist eine einzige gefaltete Platte.</p>
</header>

<section aria-labelledby="h-k">
  <h2 id="h-k">Fensterkonzept wählen</h2>
  <div class="cards" role="group" aria-label="Fensterkonzept">
%%CARDS%%
  </div>
</section>

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
      <label for="slide"><span>Einleger von oben einschieben <b id="slideVal">0 mm</b></span>
        <input id="slide" type="range" min="0" max="150" value="0" step="1"></label>
      <label for="hang"><span>Hänger klappen <b id="hangVal">aufgestellt</b></span>
        <input id="hang" type="range" min="0" max="90" value="0" step="5"></label>
      <label for="alpha"><span>Front und Karton <b id="alphaVal">100 %</b></span>
        <input id="alpha" type="range" min="0" max="100" value="100" step="5"></label>
      <label class="chk" for="cut"><input id="cut" type="checkbox"> Schnitt durch die Mitte</label>
    </div>
    <div class="ctl">
      <div class="label">Eckdaten</div>
      <dl>
        <dt>Karton außen</dt><dd>%%OUTER%% mm</dd>
        <dt>Hänger, klappt nach vorn</dt><dd>+%%HANG%% mm</dd>
        <dt>Front-Etikett</dt><dd>%%LABEL%% mm</dd>
        <dt>Einleger-Platte</dt><dd>%%INS%% mm</dd>
        <dt>Platte über Rückwand</dt><dd>%%ZD%% mm</dd>
      </dl>
%%DLS%%
    </div>
  </div>
</section>

<section aria-labelledby="h-s">
  <h2 id="h-s">Längsschnitt</h2>
  <div class="sectwrap">%%SECTION%%</div>
</section>

<section aria-labelledby="h-how">
  <h2 id="h-how">So funktioniert es</h2>
  <div class="two">
    <div class="note"><h3>Front</h3>
      <p>Die Front bleibt geschlossen und ist dadurch steif. Bedruckt wird sie mit einem Etikett: Manschette, Schnur und Ring in Originalgröße auf Graphit, in der Neonfarbe der Teile. Die Fenster sitzen genau über den echten Teilen. Man sieht also an drei Stellen das echte Material in der Grafik und kann Ring und Manschette anfassen.</p>
      <p>Die Fenster sind kleiner als die Teile. Darum halten sie Ring und Manschette nach vorn, beide liegen innen an der Front an.</p></div>
    <div class="note"><h3>Einleger</h3>
      <p>Eine Platte mit vier Rändern, die nach hinten auf die Rückwand geklappt werden. Es gibt keine Klebestelle. Die Platte liegt 9 mm über der Rückwand, das ist genau Manschettendicke minus Ringdicke.</p>
      <ul>
        <li>Die <b>Manschette</b> steckt durch ein passendes Loch und steht auf der Rückwand.</li>
        <li>Der <b>Ring</b> liegt auf der Platte. Vier kleine hochgeklappte Laschen zentrieren ihn von innen, unter dem Ring unsichtbar.</li>
        <li>Die <b>Restschnur</b> wird knapp über dem Ring durch einen Querschlitz unter die Platte geschoben, dort ist Platz.</li>
      </ul></div>
  </div>
</section>

<section aria-labelledby="h-steps">
  <h2 id="h-steps">Ablauf</h2>
  <ol class="steps">
    <li><b>Etikett drucken.</b> <code>Front-Etikett_A4_…pdf</code> auf selbstklebendes A4-Papier drucken, mit 100 % bzw. „Tatsächliche Größe“.</li>
    <li><b>Etikett schneiden.</b> Das bedruckte Blatt bündig oben links auf die 12×12″-Matte legen und <code>3_Front-Etikett_schneiden.dxf</code> schneiden. Rahmen und Fenster werden ausgeschnitten.</li>
    <li><b>Karton und Einleger schneiden.</b> <code>1_Umverpackung_perforiert.dxf</code> und <code>2_Einleger_perforiert.dxf</code>, jeweils 12×12″.</li>
    <li><b>Etikett aufkleben.</b> Auf die Front des flachen Kartonzuschnitts kleben, die Fenster decken sich. Die Kartonfenster sind 0,4 mm größer.</li>
    <li><b>Falten.</b> Karton falten und kleben, den Boden schließen. Beim Einleger die vier Ränder nach hinten und die vier Ringlaschen nach vorn klappen.</li>
    <li><b>Bestücken.</b> Manschette durch das Loch stecken, Ring auf die Laschen setzen, Restschnur durch den Schlitz schieben. Den Einleger von oben in den Karton schieben, Deckel zu.</li>
  </ol>
</section>

<section aria-labelledby="h-plot">
  <h2 id="h-plot">Zuschnitte</h2>
  <p style="margin:0 0 10px;color:var(--muted);font-size:14px">Jede Datei ist genau so groß wie die Matte (304,8 × 304,8 mm). Studio skaliert sie nicht: öffnen, nicht verschieben, schneiden. Rot = schneiden, blau = Bergfalz, grün = Talfalz, schwarz = 30-mm-Kontrollquadrat.</p>
%%BLANKS%%
</section>
</div>

<script src="%%THREE%%/build/three.min.js"></script>
<script src="%%THREE%%/examples/js/loaders/GLTFLoader.js"></script>
<script src="%%THREE%%/examples/js/controls/OrbitControls.js"></script>
<script>
(function(){
  const GLB = "%%GLB%%";
  const FRONTS = %%FRONTS%%;
  let concept = 'A';
  const canvas = document.getElementById('c'), hint = document.getElementById('hint');

  function showConcept(k){
    concept = k;
    document.querySelectorAll('[data-k]').forEach(el => { el.hidden = el.dataset.k !== k; });
    ['A','B','C'].forEach(c => { const b = document.getElementById('k-'+c); if (b) b.setAttribute('aria-pressed', c === k); });
    if (window.setFront) window.setFront(k);
  }
  ['A','B','C'].forEach(c => { const b = document.getElementById('k-'+c); if (b) b.addEventListener('click', () => showConcept(c)); });

  if (!window.THREE || !THREE.GLTFLoader) { hint.textContent = '3D-Bibliothek konnte nicht geladen werden.'; return; }
  const renderer = new THREE.WebGLRenderer({canvas, antialias:true, alpha:true});
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.outputEncoding = THREE.sRGBEncoding;
  renderer.localClippingEnabled = true;
  const scene = new THREE.Scene();
  const cam = new THREE.PerspectiveCamera(30, 1, 1, 5000);
  const controls = new THREE.OrbitControls(cam, canvas);
  controls.enableDamping = true;
  scene.add(new THREE.HemisphereLight(0xffffff, 0x8a8f86, 0.8));
  const sun = new THREE.DirectionalLight(0xffffff, 0.75); sun.position.set(120, 220, 260); scene.add(sun);
  const fill = new THREE.DirectionalLight(0xffffff, 0.35); fill.position.set(-200, -60, 120); scene.add(fill);
  const clip = new THREE.Plane(new THREE.Vector3(-1,0,0), 0);
  const COL = {Umverpackung:0xf6f4ee, Aufhaenger:0xf6f4ee, Deckel:0xf6f4ee, Einleger:0xc9a473, Ring:0xd4ff1c, Manschette:0xd4ff1c, Schnur:0x8c1f19};
  const groupBox = new THREE.Group(), groupIns = new THREE.Group(), hinge = new THREE.Group(), lid = new THREE.Group();
  hinge.position.set(0, %%HINGE_Y%%, %%HINGE_Z%%); lid.position.set(0, %%LID_Y%%, %%LID_Z%%);
  scene.add(groupBox, groupIns, hinge, lid);
  const mats = {};
  const target = new THREE.Vector3(0, 70, 12);

  // Bedruckte Front (Etikett mit transparenten Fenstern)
  const loader = new THREE.TextureLoader();
  const frontMat = new THREE.MeshBasicMaterial({transparent:true, alphaTest:0.5, side:THREE.DoubleSide});
  const front = new THREE.Mesh(new THREE.PlaneGeometry(%%LW%%, %%LH%%), frontMat);
  front.position.set(0, %%FY%%, %%FZ%%);
  groupBox.add(front);
  mats.Front = [frontMat];
  window.setFront = k => loader.load(FRONTS[k], tex => { tex.encoding = THREE.sRGBEncoding; tex.anisotropy = 8; frontMat.map = tex; frontMat.needsUpdate = true; });
  window.setFront('A');

  const bin = Uint8Array.from(atob(GLB), c => c.charCodeAt(0)).buffer;
  new THREE.GLTFLoader().parse(bin, '', gltf => {
    const meshes = [];
    gltf.scene.traverse(o => { if (o.isMesh) meshes.push(o); });
    meshes.forEach(o => {
      const key = Object.keys(COL).find(k => o.name.startsWith(k) || (o.parent && o.parent.name.startsWith(k))) || 'Einleger';
      const isPart = key === 'Ring' || key === 'Manschette';
      const m = new THREE.MeshStandardMaterial({color:COL[key], roughness:isPart?0.35:0.9, metalness:0, transparent:true, opacity:isPart?0.95:1, side:THREE.DoubleSide});
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
        new THREE.LineBasicMaterial({color:isPart?0x7d9400:(key==='Schnur'?0x5a120e:0x8a7a62), transparent:true, opacity:0.5}));
      mats[key].push(edges.material);
      mesh.add(edges);
      if (key === 'Aufhaenger') { mesh.position.sub(hinge.position); hinge.add(mesh); }
      else if (key === 'Deckel') { mesh.position.sub(lid.position); lid.add(mesh); }
      else if (key === 'Umverpackung') groupBox.add(mesh);
      else groupIns.add(mesh);
    });
    apply();
  }, () => { hint.textContent = 'Modell konnte nicht geladen werden.'; });

  const views = {front:[0,70,380], iso:[220,150,280], side:[380,70,12]};
  function setView(v){
    const p = views[v]; cam.position.set(p[0], p[1], p[2]); controls.target.copy(target); controls.update();
    ['front','iso','side'].forEach(k => document.getElementById('v-'+k).setAttribute('aria-pressed', k===v));
  }
  ['front','iso','side'].forEach(k => document.getElementById('v-'+k).addEventListener('click', () => setView(k)));
  const slide = document.getElementById('slide'), alpha = document.getElementById('alpha'), cut = document.getElementById('cut'), hang = document.getElementById('hang');
  function apply(){
    const s = Number(slide.value);
    groupIns.position.y = s;
    lid.rotation.x = Math.min(s / 25, 1) * 1.95;
    if (s > 0 && Number(hang.value) > 0) hang.value = 0;
    document.getElementById('slideVal').textContent = s + ' mm';
    const deg = Number(hang.value);
    hinge.rotation.x = deg * Math.PI / 180;
    document.getElementById('hangVal').textContent = deg === 0 ? 'aufgestellt' : (deg === 90 ? 'Versand (auf dem Deckel)' : deg + '°');
    const a = Number(alpha.value) / 100;
    document.getElementById('alphaVal').textContent = alpha.value + ' %';
    ['Umverpackung','Aufhaenger','Deckel','Front'].forEach(k => (mats[k]||[]).forEach(m => {
      m.opacity = m.isLineBasicMaterial ? 0.5 * Math.max(a, 0.25) : a; m.depthWrite = a > 0.98;
      if (k === 'Front') m.alphaTest = a > 0.98 ? 0.5 : 0.01;
    }));
    Object.values(mats).flat().forEach(m => { m.clippingPlanes = cut.checked ? [clip] : []; m.needsUpdate = true; });
  }
  [slide, alpha, hang].forEach(el => el.addEventListener('input', apply));
  cut.addEventListener('change', () => { if (cut.checked) setView('side'); apply(); });
  function fit(){ const r = canvas.getBoundingClientRect(); renderer.setSize(r.width, r.height, false); cam.aspect = r.width / Math.max(r.height,1); cam.updateProjectionMatrix(); }
  new ResizeObserver(fit).observe(canvas);
  function animate(){ requestAnimationFrame(animate); controls.update(); renderer.render(scene, cam); }
  setView('front'); fit(); animate();
})();
</script>
"""

if __name__ == "__main__":
    main()

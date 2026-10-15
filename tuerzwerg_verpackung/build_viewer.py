"""Baut out/viewer.html: 3D-Ansicht + Zuschnitte + Montage (alles eingebettet)."""
import base64
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
THREE = "https://cdn.jsdelivr.net/npm/three@0.147.0"


def svg_inline(name):
    s = open(os.path.join(OUT, f"{name}.svg")).read()
    s = re.sub(r'width="[^"]+mm" height="[^"]+mm"', 'class="blank" role="img" aria-label="Zuschnitt ' + name + '"', s, count=1)
    return s


def main():
    m = json.load(open(os.path.join(OUT, "masse.json")))
    pr = m["params"]
    glb = base64.b64encode(open(os.path.join(OUT, "Tuerzwerg_Verpackung.glb"), "rb").read()).decode()
    bw, bh = m["blank_sizes_mm"]["Umverpackung"]
    iw, ih = m["blank_sizes_mm"]["Einleger"]
    outer = (pr["Wi"] + 2 * pr["t"], pr["Hi"] + 2 * pr["t"], pr["Di"] + 2 * pr["t"])
    html = TEMPLATE
    rep = {
        "%%GLB%%": glb,
        "%%THREE%%": THREE,
        "%%SVG_BOX%%": svg_inline("Umverpackung"),
        "%%SVG_INS%%": svg_inline("Einleger"),
        "%%OUTER%%": f"{outer[0]:.0f} × {outer[1]:.0f} × {outer[2]:.0f}",
        "%%HANG%%": f"{pr['hang_h']:.0f}",
        "%%BOXBLANK%%": f"{bw - 16:.0f} × {bh - 16:.0f}",
        "%%INSBLANK%%": f"{iw - 16:.0f} × {ih - 16:.0f}",
        "%%RINGHOLE%%": f"{m['ring_hole_d']:.1f}",
        "%%DECKZ%%": f"{m['deck_Z']:.1f}",
        "%%RAISE%%": f"{pr['raise_']:.1f}",
        "%%RINGF%%": f"{pr['Di'] - m['ring_front_Z']:.1f}",
        "%%CUFFF%%": f"{pr['Di'] - m['cuff_front_Z']:.1f}",
        "%%CORD%%": f"{pr['cord_visible']:.0f}",
        "%%T%%": f"{pr['t']:.2f}",
        "%%NSLITS%%": str(m["n_slits"]),
    }
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
/* Layout: technisches Datenblatt – große 3D-Bühne links, Maße/Bedienung rechts, darunter Zuschnitte & Montagefolge */
:root{
  --bg:#eef0ea; --panel:#ffffff; --fg:#1d2420; --muted:#5d6760; --line:#d3d8cf;
  --kraft:#b58a52; --neon:#c6ec00; --neon-ink:#3d4a00; --cut:#d40000; --score:#0050ff;
  --stage:#e3e6de; --paper:#ffffff;
  --f-display:"Barlow Condensed","Arial Narrow",sans-serif;
  --f-body:"Source Sans 3","Segoe UI",system-ui,sans-serif;
  --f-mono:"JetBrains Mono",ui-monospace,Menlo,Consolas,monospace;
}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){
  --bg:#161a17; --panel:#1f2420; --fg:#e7ebe4; --muted:#9aa49c; --line:#343b35;
  --kraft:#d2a66a; --neon:#d4f53a; --neon-ink:#d4f53a; --stage:#232924; color-scheme:dark}}
:root[data-theme="dark"]{
  --bg:#161a17; --panel:#1f2420; --fg:#e7ebe4; --muted:#9aa49c; --line:#343b35;
  --kraft:#d2a66a; --neon:#d4f53a; --neon-ink:#d4f53a; --stage:#232924; color-scheme:dark}
body{background:var(--bg);color:var(--fg);font-family:var(--f-body);font-size:15px;line-height:1.5}
.wrap{max-width:1240px;margin:0 auto;padding-block:20px 48px;
  padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));
  display:flex;flex-direction:column;gap:28px}
header{display:flex;flex-wrap:wrap;align-items:baseline;gap:6px 18px}
h1{font-family:var(--f-display);font-weight:700;font-size:clamp(30px,5vw,46px);letter-spacing:.01em;margin:0;line-height:1}
h1 .tag{display:inline-block;background:var(--neon);color:#1d2420;padding:0 .25em;margin-left:.2em}
header p{margin:0;color:var(--muted);max-width:62ch}
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
.blanks{display:grid;grid-template-columns:minmax(0,1.1fr) minmax(0,1fr);gap:20px}
@media (max-width:800px){.blanks{grid-template-columns:minmax(0,1fr)}}
figure{margin:0;display:flex;flex-direction:column;gap:8px;min-width:0}
.paper{background:var(--paper);border:1px solid var(--line);padding:10px;overflow-x:auto}
.blank{width:100%;height:auto;display:block}
figcaption{font-size:13px;color:var(--muted)}
.legend{display:flex;flex-wrap:wrap;gap:16px;font-size:13px}
.legend i{display:inline-block;width:26px;height:0;border-top:2px solid var(--cut);vertical-align:middle;margin-right:6px}
.legend i.s{border-top:2px dashed var(--score)}
ol.steps{margin:0;padding:0;list-style:none;counter-reset:s;display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:14px}
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
@media (prefers-reduced-motion: reduce){*{scroll-behavior:auto}}
</style>

<div class="wrap">
<header>
  <h1>Türzwerg <span class="tag">Verpackung</span></h1>
  <p>Faltschachtel mit Euroloch-Hänger und eingeschobener Haltestruktur. Ring und Manschette werden in Stanzlöcher gedrückt, schlagen hinten an und sitzen dadurch in jeder Packung gleich hinter dem Sichtfenster.</p>
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
        <input id="slide" type="range" min="0" max="170" value="0" step="1"></label>
      <label for="alpha"><span>Karton-Deckkraft <b id="alphaVal" class="mono">100 %</b></span>
        <input id="alpha" type="range" min="0" max="100" value="100" step="5"></label>
      <label class="chk" for="cut"><input id="cut" type="checkbox"> Schnitt durch die Mitte (Seitenansicht zeigt Anschläge)</label>
    </div>
    <div class="ctl">
      <div class="label">Eckdaten</div>
      <dl>
        <dt>Karton außen (B×H×T)</dt><dd>%%OUTER%% mm</dd>
        <dt>Hänger, doppellagig</dt><dd>+%%HANG%% mm</dd>
        <dt>Euroloch</dt><dd>32 × 6 / Ø10</dd>
        <dt>Karton</dt><dd>%%T%% mm, 300–350 g/m²</dd>
        <dt>Zuschnitt Umverpackung</dt><dd>%%BOXBLANK%% mm</dd>
        <dt>Zuschnitt Einleger</dt><dd>%%INSBLANK%% mm</dd>
        <dt>Deck über Rückwand</dt><dd>%%DECKZ%% mm</dd>
        <dt>Anschlagboden</dt><dd>%%RAISE%% mm</dd>
        <dt>Loch Ring (Deck)</dt><dd>Ø %%RINGHOLE%% mm</dd>
        <dt>Abstand Ring → Front</dt><dd>%%RINGF%% mm</dd>
        <dt>Abstand Manschette → Front</dt><dd>%%CUFFF%% mm</dd>
        <dt>Schnur sichtbar</dt><dd>%%CORD%% mm</dd>
      </dl>
    </div>
  </div>
</section>

<section aria-labelledby="h-plot">
  <h2 id="h-plot">Zuschnitte für den Silhouette Cameo 4</h2>
  <div class="legend"><span><i></i>Schneiden</span><span><i class="s"></i>Rillen / Falzen</span><span>Ansicht: Außenseite (Druckseite) oben</span></div>
  <div class="blanks" style="margin-top:12px">
    <figure><div class="paper">%%SVG_BOX%%</div>
      <figcaption>Umverpackung · Klebelasche · Rückwand mit Hänger · Seite · Front mit Sichtfenster · Seite. Deckel oben und unten an der Front, Staublaschen an den Seiten.</figcaption></figure>
    <figure><div class="paper">%%SVG_INS%%</div>
      <figcaption>Einleger · Wand links · Anschlagboden · Wand rechts · Deck mit Stanzloch · Klebelasche. %%NSLITS%% kurze Schlitze bilden Haltezungen, die beim Eindrücken nachgeben und das Teil danach festhalten. Die Rechtecke an den Falzen sind Füße bzw. Stützlaschen: dort wird nicht gefalzt, die Wand läuft weiter.</figcaption></figure>
  </div>
</section>

<section aria-labelledby="h-how">
  <h2 id="h-how">So funktioniert die Haltestruktur</h2>
  <div class="two">
    <div class="note">
      <h3>Querschnitt</h3>
      <p>Der Einleger ist ein geklebtes Rohr, das den Karton in Breite und Tiefe genau ausfüllt. Er kann deshalb weder seitlich noch nach vorn wandern.</p>
      <ul>
        <li><b>Anschlagboden</b> %%RAISE%% mm über der Rückwand, getragen von Füßen aus den Seitenwänden. Hier schlagen Ring und Manschette hinten an.</li>
        <li><b>Deck</b> %%DECKZ%% mm über der Rückwand. Es liegt knapp über der dicksten Stelle beider Teile, das Loch ist etwas kleiner. Die Teile rasten beim Eindrücken hinter den Zungen ein.</li>
        <li><b>Stützlaschen</b> der rechten Wand reichen bis an die Front und halten das Deck auf Abstand.</li>
        <li>Die Manschette liegt dadurch fast an der Front an (%%CUFFF%% mm Luft), der Ring sitzt %%RINGF%% mm dahinter, mittig im runden Fenster.</li>
      </ul>
    </div>
    <div class="note">
      <h3>Sichtfenster</h3>
      <p>Ein offenes Fenster in Schlüsselloch-Form folgt der Kontur von Manschette, Schnur und Ring. Ohne Folie kann man alle drei anfassen. Der Rand des Fensters bleibt in der Breite mindestens 7 mm stark.</p>
      <p>Die Schnur läuft durch einen 6 mm breiten Kanal im Deck von der Kielspitze der Manschette zur Bohrung oben im Ring, sichtbar sind %%CORD%% mm.</p>
    </div>
  </div>
</section>

<section aria-labelledby="h-steps">
  <h2 id="h-steps">Ablauf</h2>
  <ol class="steps">
    <li><b>Plotten.</b> Beide Zuschnitte schneiden und rillen. Die Umverpackung braucht einen 12×12″-Bogen (305 × 305 mm) oder A3, der Einleger passt auf A4 quer.</li>
    <li><b>Einleger kleben.</b> Alle Rilllinien vorfalzen, Füße und Stützlaschen gerade lassen. Klebelasche innen an die linke Wand kleben, das Rohr steht.</li>
    <li><b>Umverpackung kleben.</b> Hänger-Doppelung nach vorn umlegen und verkleben, Euroloch deckt sich. Seitennaht über die Klebelasche schließen. Oberen Deckel einstecken.</li>
    <li><b>Bestücken.</b> Ring ins runde Loch drücken bis zum Anschlag, Manschette mit Kiel nach unten ins obere Loch, Schnur in den Kanal legen.</li>
    <li><b>Einschieben und schließen.</b> Einleger von unten einschieben (die Teile stehen nicht über die Wände hinaus), Staublaschen einklappen, Bodendeckel einstecken.</li>
  </ol>
</section>

<section aria-labelledby="h-sil">
  <h2 id="h-sil">Einstellungen Silhouette Studio</h2>
  <div class="two">
    <div class="note">
      <h3>Dateien</h3>
      <ul>
        <li><code>*_komplett.dxf</code> – Schneiden (rot) und Rillen (blau) zusammen. In Studio unter „Schneiden“ → „Linienfarbe“ getrennt einstellen.</li>
        <li><code>*_schneiden.dxf</code> / <code>*_rillen.dxf</code> – getrennt, falls die Farben beim DXF-Import verloren gehen. Beide an Position 0/0 importieren, dann liegen sie deckungsgleich.</li>
        <li><code>*.svg</code> – für Designer Edition, Maßstab in mm.</li>
        <li>Nach dem Import die Breite prüfen: Umverpackung %%BOXBLANK%% mm. Weicht sie ab, auf diesen Wert skalieren.</li>
      </ul>
    </div>
    <div class="note">
      <h3>Startwerte für 300–350 g/m² Karton</h3>
      <div class="tw"><table>
        <tr><th>Linie</th><th>Werkzeug</th><th>Klinge</th><th>Kraft</th><th>Tempo</th><th>Durchgänge</th></tr>
        <tr><td>Schneiden</td><td>AutoBlade</td><td>8–10</td><td>30–33</td><td>3</td><td>2</td></tr>
        <tr><td>Rillen</td><td>AutoBlade</td><td>1–2</td><td>10–15</td><td>3</td><td>1</td></tr>
      </table></div>
      <p>Erst einen Teststreifen schneiden. Rillen mit flacher Klinge ritzt die Oberseite an; dann nach hinten (weg von der Ritzung) falzen. Wer mit Prägestift oder Falzbein rillt, legt den Bogen mit der Innenseite nach oben und spiegelt die Datei.</p>
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
  const renderer = new THREE.WebGLRenderer({canvas, antialias:true, alpha:true, localClippingEnabled:true});
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
  scene.add(groupBox, groupIns);
  const mats = {};
  const COL = {Umverpackung:0xf6f4ee, Aufhaenger:0xf6f4ee, Einleger:0xc9a473, Ring:0xd4ff1c, Manschette:0xd4ff1c, Schnur:0x8c1f19};
  const target = new THREE.Vector3(0, 85, 15);

  const bin = Uint8Array.from(atob(GLB), c => c.charCodeAt(0)).buffer;
  new THREE.GLTFLoader().parse(bin, '', gltf => {
    const meshes = [];
    gltf.scene.traverse(o => { if (o.isMesh) meshes.push(o); });
    meshes.forEach(o => {
      const name = o.name.replace(/_\d+$/, '') in COL ? o.name.replace(/_\d+$/, '') : (o.parent && o.parent.name) || o.name;
      const key = Object.keys(COL).find(k => name.startsWith(k)) || 'Einleger';
      const isPart = key === 'Ring' || key === 'Manschette';
      const m = new THREE.MeshStandardMaterial({color:COL[key], roughness:isPart?0.35:0.9, metalness:0,
        transparent:true, opacity:isPart?0.92:1, side:THREE.DoubleSide, clippingPlanes:[]});
      if (isPart) { m.emissive = new THREE.Color(0x3a4a00); }
      mats[key] = mats[key] || []; mats[key].push(m);
      let g = o.geometry;
      if (isPart || key === 'Schnur') { g.deleteAttribute('normal'); g.computeVertexNormals(); }
      else { g = g.toNonIndexed(); g.computeVertexNormals(); }
      const mesh = new THREE.Mesh(g, m);
      o.updateWorldMatrix(true, false);
      mesh.applyMatrix4(o.matrixWorld);
      mesh.scale.multiplyScalar(1000); mesh.position.multiplyScalar(1000);
      const edges = new THREE.LineSegments(new THREE.EdgesGeometry(o.geometry, 30),
        new THREE.LineBasicMaterial({color:isPart?0x7d9400:(key==='Schnur'?0x5a120e:0x8a7a62), transparent:true, opacity:0.55, clippingPlanes:[]}));
      mats[key].push(edges.material);
      mesh.add(edges);
      (key === 'Umverpackung' || key === 'Aufhaenger' ? groupBox : groupIns).add(mesh);
    });
    setView('front'); fit(); animate();
  }, err => { hint.textContent = 'Modell konnte nicht geladen werden.'; });

  const views = {front:[0,85,400], iso:[230,150,300], side:[400,85,15]};
  function setView(v){
    const p = views[v]; cam.position.set(p[0], p[1], p[2]); controls.target.copy(target); controls.update();
    ['front','iso','side'].forEach(k => document.getElementById('v-'+k).setAttribute('aria-pressed', k===v));
  }
  ['front','iso','side'].forEach(k => document.getElementById('v-'+k).addEventListener('click', () => setView(k)));

  const slide = document.getElementById('slide'), alpha = document.getElementById('alpha'), cut = document.getElementById('cut');
  function apply(){
    groupIns.position.y = -Number(slide.value);
    document.getElementById('slideVal').textContent = slide.value + ' mm';
    const a = Number(alpha.value)/100;
    document.getElementById('alphaVal').textContent = alpha.value + ' %';
    ['Umverpackung','Aufhaenger'].forEach(k => (mats[k]||[]).forEach(m => { m.opacity = m.isLineBasicMaterial ? 0.55*Math.max(a,0.25) : a; m.depthWrite = a > 0.98; }));
    Object.values(mats).flat().forEach(m => { m.clippingPlanes = cut.checked ? [clip] : []; m.needsUpdate = true; });
  }
  slide.addEventListener('input', apply); alpha.addEventListener('input', apply); cut.addEventListener('change', () => { if (cut.checked) setView('side'); apply(); });

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

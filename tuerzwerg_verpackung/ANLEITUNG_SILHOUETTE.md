# Türzwerg-Verpackung v3 – drucken, plotten, bauen

Bedruckte Front mit drei Sichtfenstern, Faltschachtel außen ca. 84 × 135 × 24 mm,
Einleger aus einer Platte ohne Klebestelle.

## 1. Material

| | |
|---|---|
| Karton | Faltschachtelkarton 300–350 g/m², ca. 0,45 mm |
| Etikett | selbstklebendes A4-Papier (matt oder glänzend), alternativ Papier + Sprühkleber |
| Drucker | normaler A4-Farbdrucker |
| Cameo 4 | AutoBlade in Halter 1, StandardGrip-Matte 12×12″ |

## 2. Dateien

Ordner `out/Konzept_A_Kapsel/` (entsprechend `Konzept_B_Bullauge/` und `Konzept_C_Mittelachse/`):

| Schritt | Datei | Wofür |
|---|---|---|
| 1 | `Front-Etikett_A4_Konzept_A.pdf` | Druckvorlage, 2 Etiketten auf A4 |
| 2 | `3_Front-Etikett_schneiden.dxf` | schneidet Etikettrand und Fenster aus dem bedruckten A4-Blatt |
| 3 | `1_Umverpackung_perforiert.dxf` | Faltschachtel (alles rot, Falzlinien als Perforation) |
| 4 | `2_Einleger_perforiert.dxf` | Einleger (alles rot, Falzlinien als Perforation) |

`…_komplett.dxf` statt `…_perforiert.dxf` nur mit Rillwerkzeug (rot schneiden, blau Bergfalz, grün Talfalz).

Alle DXF-Dateien sind **genau so groß wie die 12×12″-Matte** (304,8 × 304,8 mm, Eckmarken in den Ecken). Silhouette Studio skaliert sie deshalb nicht: öffnen, nicht verschieben, schneiden. Das schwarze 30-mm-Kontrollquadrat muss 30,0 mm messen.

## 3. Etikett

1. `Front-Etikett_A4_…pdf` drucken: **100 % / „Tatsächliche Größe“**, nicht „An Seite anpassen“. Kontrolle: Das Etikett misst zwischen den Schnittmarken 82,5 × 133,4 mm.
2. Das bedruckte Blatt **bündig oben links** auf die Matte legen (A4-Ecke auf die Mattenecke).
3. In Studio: Seite *CAMEO 4*, Matte *12×12 in*. `3_Front-Etikett_schneiden.dxf` öffnen und schneiden.
   Startwerte für Etikettenpapier: Klinge 2, Kraft 10, Tempo 5, 1 Durchgang. Vorher testen: Das Trägerpapier soll nur angeritzt sein.
4. Ist der Schnitt zum Druck um 1–2 mm versetzt: Drucker verschieben leicht. Der Rand hat 2 mm Beschnitt, die Fenster liegen auf der Grafik. Kleine Versätze sieht man deshalb nicht.

**Ohne Plotter:** Das Etikett an den Schnittmarken ausschneiden und auf die Front kleben. Die Fenster danach von innen mit einem Skalpell ausschneiden, das Kartonfenster dient als Schablone.

## 4. Karton und Einleger

1. `1_Umverpackung_perforiert.dxf` öffnen und schneiden: Klinge 8, Kraft 30, Tempo 3, 2 Durchgänge.
2. `2_Einleger_perforiert.dxf` genauso.
3. Lange Strichlinie = **Bergfalz** (Druckseite außen), kurze Strichlinie = **Talfalz** (Druckseite innen).

## 5. Bauen

**Umverpackung**
1. Das Etikett auf die Front des flachen Zuschnitts kleben. Die Fenster im Etikett decken sich mit den Kartonfenstern, die je 0,4 mm größer sind.
2. Alle Falze vorfalzen. Die kurze Strichlinie am Hänger-Fuß dient nur zum Umklappen für den Versand.
3. Die Hänger-Doppelung nach innen klappen und verkleben, die Eurolöcher decken sich.
4. Seitennaht über die Klebelasche schließen.
5. Boden schließen: Staublaschen ein, Bodendeckel einstecken. Befüllt wird von oben.

**Einleger** (keine Klebestelle)
1. Die vier Ränder 90° nach hinten klappen (Bergfalz).
2. Die vier kleinen Laschen im Ringbereich 90° nach vorn hochklappen (Talfalz).

## 6. Bestücken

1. Die Manschette mit dem Kiel nach unten (zum Ring) von vorn durch das rechteckige Loch stecken. Sie steht dann hinten auf der Rückwand.
2. Den Ring auf die vier Laschen setzen, mit der Schnurbohrung nach oben.
3. Die Schnur gerade über die Platte legen und die Restschnur als Schlaufe durch den Querschlitz knapp über dem Ring unter die Platte schieben.
4. Den oberen Deckel öffnen, den Einleger von oben einschieben, bis er unten aufsitzt. Deckel zu.
5. Den Hänger für den Versand nach vorn auf den Deckel klappen.

## 7. Kontrollmaße

- Kontrollquadrat 30,0 mm · Etikett 82,5 × 133,4 mm
- Karton außen ca. 84 × 135 × 24 mm, Hänger 23 mm
- Einleger-Platte 82,5 × 133,0 mm, liegt 9 mm über der Rückwand

# Türzwerg-Verpackung plotten – Silhouette Cameo 4

## 1. Material und Werkzeug

| | |
|---|---|
| Karton | Faltschachtelkarton 300–350 g/m², ca. 0,45 mm dick (GC2 / Chromokarton). Die schönere Seite ist die Druck- bzw. Außenseite. |
| Matten | StandardGrip-Matte (blau) 12×12″ und 12×24″ |
| Werkzeughalter 1 | AutoBlade (Schneiden) |
| Werkzeughalter 2 | Prägewerkzeug / Embossing Tool zum Rillen (optional, sonst Rillen mit der AutoBlade, siehe 4.) |
| Kleber | doppelseitiges Klebeband 6 mm oder lösungsmittelfreier Bastelkleber |

Die Dateien sind für 0,45 mm Karton gerechnet. Bei deutlich anderer Dicke `t` in `generate.py` ändern und neu erzeugen.

## 2. Welche Datei?

Alle Dateien liegen in `out/`. Linienfarben: **rot = schneiden**, **blau = Bergfalz** (Druckseite außen), **grün = Talfalz** (Druckseite innen), **schwarz = 30-mm-Kontrollquadrat** (nicht schneiden, nur zum Prüfen der Größe).

| Was | Datei (mit Rillwerkzeug) | Datei (ohne Rillwerkzeug) | Größe (B × H) | Matte |
|---|---|---|---|---|
| Umverpackung | `Umverpackung_komplett.dxf` | `Umverpackung_perforiert.dxf` | 254,2 × 231,6 mm | 12×12″ |
| **Einleger, zweiteilig (empfohlen)** | `Einleger_2teilig_komplett.dxf` | `Einleger_2teilig_perforiert.dxf` | 217,1 × 213,0 mm | 12×12″ |
| Einleger, einteilig | `Einleger_komplett.dxf` | `Einleger_perforiert.dxf` | 112,0 × 372,6 mm | nur 12×24″ |
| beides auf einem Bogen | `Bogen_12x24_komplett.dxf` | `Bogen_12x24_perforiert.dxf` | 254,2 × 578,2 mm | nur 12×24″ |

> **Wichtig – Einleger zu klein?** Ist eine Datei länger als die eingestellte Seite (12×12″ = 304,8 mm), verkleinert Silhouette Studio sie beim Öffnen auf Seitengröße. Der einteilige Einleger (334,6 mm) wird dann um etwa 9 % zu klein, und Ring und Manschette passen nicht mehr in die Löcher. Deshalb:
> 1. **Zuerst** *Seite einrichten* auf die richtige Matte stellen, **dann** die Datei öffnen.
> 2. Auf der 12×12″-Matte den **zweiteiligen Einleger** nehmen.
> 3. Nach dem Öffnen das **schwarze Kontrollquadrat** messen: Es muss genau **30,0 × 30,0 mm** sein. Wenn nicht, alles markieren und proportional so skalieren, dass das Quadrat 30,0 mm misst.

Designer Edition: gleiche Namen als `.svg`. Notlösung, wenn die Farben verloren gehen: `*_schneiden.dxf` + `*_rillen.dxf` (siehe 3.5).

## 2a. Falzen – so geht es mit dem Cameo 4

Der Cameo 4 hat kein eigenes Rillwerkzeug. Es gibt drei Wege, sortiert nach Aufwand:

| Weg | Was du brauchst | Ergebnis |
|---|---|---|
| **A · Perforation** (empfohlen) | nichts, nur die AutoBlade | Falzlinien als kurze Schnitte mit Stegen. Lässt sich sauber und leicht falzen. Die Schlitze sind an den Kanten sichtbar, für Muster ok. |
| B · Anritzen | nichts, nur die AutoBlade | Die Klinge schneidet nur die oberste Schicht an. Unsichtbarer, braucht aber genaues Einstellen. |
| C · Prägen | Prägestift / Embossing-Stylus mit Stiftadapter für Halter 2 (Zubehör, auch von Drittanbietern) oder leere Kugelschreibermine im Stiftadapter | Eingedrückte Rille wie bei gekauften Schachteln. Am schönsten. |

**A · Perforation**
1. Die `*_perforiert.dxf` öffnen. Alle Linien sind rot, die Falzlinien sind schon als Schnitt mit Stegen angelegt:
   - **lange Striche (2,5 mm) = Bergfalz**, Druckseite außen,
   - **kurze Striche (1,2 mm) = Talfalz**, Druckseite innen.
2. Mit denselben Schneidwerten wie bisher schneiden (alles Rot, ein Auftrag).
3. Nach dem Ausbrechen an der Tischkante oder mit einem Lineal entlang der Strichlinie falzen.

Geht der Falz zu schwer, die Stege kürzer machen (`PERF` in `generate.py`). Reißt er zu leicht, die Stege länger machen.

**B · Anritzen mit der AutoBlade**
1. `*_komplett.dxf` nehmen. Blau und Grün bekommen eigene Werte: Klinge 1, Kraft 6–10, 1 Durchgang.
2. Vorher an einem Reststück testen: Die Oberfläche soll nur angeritzt sein, die Rückseite darf nichts zeigen.
3. Beim Falzen liegt die Ritzung außen. Bei Talfalzen (grün) liegt sie zwangsläufig innen; das geht auch, ist aber etwas weniger sauber.

**C · Prägen mit Werkzeug in Halter 2**
1. Den Prägestift oder die leere Kugelschreibermine mit dem Stiftadapter in Halter 2 setzen.
2. Blau und Grün: Aktion *Skizzieren*, Werkzeug 2, Kraft 33, Tempo 2, 2 Durchgänge. Rot: wie gehabt, Werkzeug 1.
3. Erst prägen, dann schneiden.
4. Falzen so, dass die eingedrückte Rille **innen** im Falz liegt.

**Ohne Gerät:** Die Linien im Komplett-Zuschnitt mit einem Stift zeichnen lassen (Sketch Pen in Halter 2, Aktion *Skizzieren*) und dann von Hand mit Falzbein und Lineal nachziehen.

## 3. Silhouette Studio vorbereiten

1. **Seite einrichten** (Page Setup): Maschine *CAMEO 4*, Schneidematte *CAMEO 12×12 in* bzw. *12×24 in*, Mediengröße gleich, Hochformat.
2. **Datei öffnen:** *Datei → Öffnen*, Dateityp *DXF*, Datei wählen.
   Fragt Studio nach der Größe oder gibt es unter *Bearbeiten → Einstellungen → Importieren* eine DXF-Option: **Originalgröße** wählen.
3. **Größe prüfen:** Das schwarze Kontrollquadrat markieren, es muss 30,0 × 30,0 mm groß sein. Zusätzlich die Gesamtgröße mit der Tabelle oben vergleichen. Weicht sie ab: alles markieren, Proportionen sperren und die Breite genau eintippen.
   Danach das Kontrollquadrat löschen oder auf „Kein Schnitt“ stellen.
4. **Platzieren:** Das Teil innerhalb des Schneidebereichs ablegen, ca. 10 mm Abstand zum Rand. Den Karton später genauso auf die Matte legen.
5. **Farben prüfen** (Fenster *Linienstil*): Rot, Blau und Grün müssen zu sehen sein.
   Sind alle Linien gleichfarbig, die Teildateien nehmen:
   1. *Datei → Öffnen* `…_schneiden.dxf`.
   2. *Datei → Zusammenführen* `…_rillen.dxf`.
   3. Alles markieren, dann *Objekt → Ausrichten → oben links ausrichten*. Beide Dateien haben dieselben zwei kleinen Passerwinkel in den Ecken, dadurch liegen sie danach exakt übereinander.
   4. Die zwei Passerwinkel löschen.
   5. Die Schneidlinien rot färben und die Rilllinien blau.

## 4. Schneideinstellungen (Fenster *Senden*)

Modus **Linie** (nach Linienfarbe). Startwerte, vorher immer einen **Testschnitt** machen:

| Farbe | Aktion | Werkzeug | Klinge | Kraft | Tempo | Durchgänge |
|---|---|---|---|---|---|---|
| Rot | Schneiden | 1 · AutoBlade | 8 | 30 | 3 | 2 |
| Blau + Grün, mit Prägewerkzeug | Prägen / Skizzieren | 2 · Prägewerkzeug | – | 20 | 3 | 1 |
| Blau + Grün, ohne Prägewerkzeug | Schneiden (nur anritzen) | 1 · AutoBlade | 1 | 6–10 | 3 | 1 |
| Perforierte Datei (alles rot) | Schneiden | 1 · AutoBlade | wie Rot | wie Rot | 3 | 2 |

- **Testschnitt:** Der Karton muss sauber durch sein, die Matte darf nur leicht angeritzt sein. Geht er nicht durch: Kraft 33, dann Klinge 9, dann 3 Durchgänge. Beim Anritzen darf der Karton auf keinen Fall durchgeschnitten sein.
- **Reihenfolge:** Erst rillen, dann schneiden, damit nichts verrutscht. Lässt sich die Reihenfolge nicht einstellen, zwei Aufträge nacheinander schicken, ohne die Matte zu entladen:
  1. nur Blau und Grün aktiv,
  2. nur Rot aktiv.

## 5. Schneiden

1. Den Karton mit der Druckseite nach oben oben links an das Raster der Matte legen und fest andrücken (Rolle oder Rakel).
2. Matte am Cameo 4 einlegen und laden.
3. Senden.
4. Vor dem Entladen an einer Ecke prüfen, ob durchgeschnitten ist. Falls nicht, ohne etwas zu verschieben noch einmal senden.
5. Entladen und die Matte vom Karton wegbiegen, nicht den Karton von der Matte. So bleibt er gerade.
6. Fenster, Eurolöcher und Kreuzschlitz ausbrechen. Die kurzen Schlitze an den Löchern im Deck sind Haltezungen und bleiben, wie sie sind.

## 6. Umverpackung falten und kleben

1. Alle blauen Linien vorfalzen, Druckseite außen.
2. Die grüne Linie am Fuß des Hängers nicht vorfalzen. An ihr wird der Hänger nur für den Versand nach vorn umgeklappt.
3. **Hänger:** Die obere Hälfte (Doppelung) an der Falzlinie nach vorn, also zur Kartoninnenseite, umklappen und verkleben. Die beiden Eurolöcher decken sich.
4. **Seitennaht:** Kleber auf die schmale Klebelasche links an der Rückwand geben, den Zuschnitt um die Längsfalze legen und das rechte Seitenteil innen auf die Lasche drücken.
5. **Boden schließen:** Staublaschen einklappen, Bodendeckel einstecken. Er bleibt zu, befüllt wird von oben.

## 7. Einleger falten und kleben

1. Vorfalzen: **blau als Bergfalz**, **grün als Talfalz**. Grün sind die beiden Falze am Schnurboden, die zwei Seitenflansche am Deck und die vier Füße.
2. Die vier kleinen Füße im Ringboden 90° nach hinten klappen, weg von der Druckseite des Decks.
3. Die zwei Seitenflansche am Deck 90° nach vorn klappen, zur Druckseite des Decks.
4. Den Streifen zum Profil falten, von unten nach oben:
   1. Wand unten
   2. Ringboden
   3. Stufe
   4. Schnurboden (liegt höher)
   5. Stufe
   6. Manschettenboden
5. Die Klebelasche am Ende des Manschettenbodens hochklappen und innen an die Wand oben kleben.
   **Zweiteiliger Einleger:** Teil A (Böden) hat am Ende des Ringbodens eine zusätzliche Klebelasche. Sie wird hochgeklappt und innen an die „Wand unten“ von Teil B (Deck) geklebt. Danach ist der Einleger genau wie die einteilige Version.
6. **Kontrolle:** Auf den Rücken gelegt stehen Manschettenboden und Füße auf dem Tisch, die Flansche zeigen nach oben. Das Deck liegt eben.

## 8. Bestücken

1. Ring mit der Bohrung nach oben ins runde Loch drücken, bis er einrastet.
2. Manschette mit dem Kiel zum Ring ins obere Loch drücken, bis sie einrastet.
3. Die Mitte der Schnur als Schlaufe durch den Kreuzschlitz ins Schnurfach schieben, bis beide sichtbaren Stücke gerade liegen.
4. Den oberen Deckel öffnen und den Einleger von oben einschieben, bis er unten aufsitzt.
5. Staublaschen einklappen, Deckel einstecken.
6. Den Hänger für den Versand nach vorn auf den Deckel klappen.

## 9. Kontrollmaße

- Umverpackung außen: 97 × 146 × 24,5 mm (Hänger +24 mm)
- Manschette 0,15 mm hinter der Front, Ring 4,65 mm
- Rand über dem Manschettenfenster = Rand unter dem Ringfenster = 10,3 mm

## 10. Wenn etwas nicht passt

| Problem | Abhilfe |
|---|---|
| DXF zu groß oder zu klein | Proportional auf die Breite aus Tabelle 2 skalieren |
| Schnitt nicht durch | Kraft hoch (max. 33), Klinge +1, einen Durchgang mehr |
| Karton reißt an den Rilllinien | Rillkraft senken oder Prägewerkzeug statt Klinge |
| Karton verrutscht auf der Matte | Matte reinigen oder neue nehmen, Karton fest andrücken |
| Ring oder Manschette rasten zu schwer ein | `ring_snap` in `generate.py` von 0,35 auf 0,2 senken |
| Einleger klemmt beim Einschieben | Luft der Flansche erhöhen (`flange_height`, 0,2 → 0,5 mm) |

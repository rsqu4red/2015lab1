# Türzwerg-Verpackung plotten – Silhouette Cameo 4

## 1. Material und Werkzeug

| | |
|---|---|
| Karton | Faltschachtelkarton 300–350 g/m², ca. 0,45 mm dick (GC2 / Chromokarton). Die schönere Seite ist die Druck- bzw. Außenseite. |
| Matten | StandardGrip-Matte (blau) 12×12″, für den einteiligen Einleger 12×24″ |
| Werkzeug | AutoBlade in Halter 1. Mehr braucht es mit den perforierten Dateien nicht. |
| Kleber | doppelseitiges Klebeband 6 mm oder lösungsmittelfreier Bastelkleber |

## 2. Welche Datei?

Jede Datei ist **genau so groß wie die Matte**: 304,8 × 304,8 mm (12×12″) bzw. 304,8 × 609,6 mm (12×24″). In zwei Ecken sitzt je eine kleine Eckmarke.

Dadurch kann Silhouette Studio nichts mehr falsch skalieren. Auch wenn Studio die Datei beim Öffnen an die Seite anpasst, ist der Faktor genau 1. Daher kamen vorher „zu klein“ (Faktor 0,91) und „zu groß“ (Faktor 1,40). Das Teil liegt außerdem genau dort auf der Matte, wo es in der Datei liegt.

**Ohne Rillwerkzeug (empfohlen):** die `…_perforiert.dxf`. Alle Linien sind rot und werden in einem Auftrag geschnitten.

| Matte | Datei | Teil |
|---|---|---|
| 12×12″ | `plot/12x12/Umverpackung_perforiert.dxf` | Umverpackung 254,2 × 231,6 mm |
| 12×12″ | `plot/12x12/Einleger_2teilig_perforiert.dxf` | Einleger in 2 Teilen, zusammen 217,2 × 175,0 mm |
| 12×24″ | `plot/12x24/Einleger_einteilig_perforiert.dxf` | Einleger am Stück 112,1 × 334,6 mm |
| 12×24″ | `plot/12x24/Bogen_Karton_und_Einleger_perforiert.dxf` | Umverpackung + Einleger am Stück |

**Mit Rillwerkzeug:** dieselben Namen mit `…_komplett.dxf`. Dort steht **rot** für Schneiden, **blau** für Bergfalz und **grün** für Talfalz.
Designer Edition: dieselben Namen als `.svg`.

**Einteiliger Einleger auf 12×12″ geht nicht:** Der Einleger ist als Streifen 334,6 mm lang, die Matte hat 304,8 mm. Selbst diagonal fehlen 11 mm. Auf 12×12″ deshalb den zweiteiligen nehmen, die Teile werden mit einer Lasche verklebt (siehe 7.).

**Schwarze Linien** (Kontrollquadrat 30 × 30 mm, Eckmarken) liegen im Abfall. Man kann sie mitschneiden lassen. Das Quadrat ist dann ein Prüfstück, das nach dem Schneiden genau 30,0 mm messen muss.

## 3. Silhouette Studio

1. *Seite einrichten*: Maschine *CAMEO 4*, Schneidematte *12×12 in* (bzw. *12×24 in*), Mediengröße gleich, Hochformat.
2. *Datei → Öffnen* und die DXF wählen. Nichts verschieben, nichts skalieren.
3. Kurz prüfen: Das Kontrollquadrat zeigt 30,0 × 30,0 mm. Das ist nur eine Kontrolle, es muss nichts eingestellt werden.

## 4. Schneideinstellungen (Fenster *Senden*)

Perforierte Datei: eine Einstellung für alles. Startwerte, vorher einen **Testschnitt** machen:

| Werkzeug | Klinge | Kraft | Tempo | Durchgänge |
|---|---|---|---|---|
| AutoBlade (Halter 1) | 8 | 30 | 3 | 2 |

Geht der Karton nicht durch: Kraft 33, dann Klinge 9, dann 3 Durchgänge.

Komplett-Datei mit Rillwerkzeug: Rot wie oben schneiden. Blau und Grün mit dem Prägestift in Halter 2 (*Skizzieren*, Kraft 33, Tempo 2, 2 Durchgänge) oder mit der AutoBlade nur anritzen (Klinge 1, Kraft 6–10). Erst rillen, dann schneiden.

## 5. Schneiden

1. Den Karton mit der Druckseite nach oben **bündig oben links** auf die Matte legen (Raster) und fest andrücken.
2. Matte laden und senden.
3. Vor dem Entladen an einer Ecke prüfen, ob durchgeschnitten ist. Falls nicht, noch einmal senden, ohne etwas zu verschieben.
4. Entladen und die Matte vom Karton wegbiegen.
5. Fenster, Eurolöcher und den Kreuzschlitz ausbrechen. Die kurzen Schlitze an den Löchern im Deck sind Haltezungen und bleiben.
6. Kontrollquadrat nachmessen: 30,0 mm.

## 6. Falzen

In den perforierten Dateien zeigen die Strichlinien die Falzrichtung:
- **lange Striche = Bergfalz**: Die Druckseite liegt außen.
- **kurze Striche = Talfalz**: Die Druckseite liegt innen.

Die Linie an einer Tischkante oder mit einem Lineal umbiegen.

## 7. Zusammenbauen

**Umverpackung**
1. Alle Falze vorfalzen. Die kurze Strichlinie am Fuß des Hängers nur für den Versand benutzen.
2. Die Hänger-Doppelung nach innen umklappen und verkleben, die Eurolöcher decken sich.
3. Kleber auf die schmale Klebelasche links an der Rückwand geben, den Zuschnitt herumlegen und das rechte Seitenteil innen aufdrücken.
4. Boden schließen: Staublaschen ein, Bodendeckel einstecken. Befüllt wird von oben.

**Einleger, zweiteilig**
- **Teil A** (links, ohne Löcher): Manschettenboden, Stufe, Schnurboden mit Kreuzschlitz, Stufe, Ringboden mit 4 Füßen und oben eine Klebelasche.
- **Teil B** (rechts, mit Löchern): Wand unten, Deck mit Seitenflanschen, Wand oben.

1. Alle Falze vorfalzen.
2. Die Füße 90° nach hinten klappen und die Seitenflansche 90° nach vorn.
3. Die Klebelasche oben an Teil A hochklappen und innen an die „Wand unten“ von Teil B kleben.
4. Den Streifen zum Profil falten.
5. Die Klebelasche unten an Teil A hochklappen und innen an die „Wand oben“ von Teil B kleben.
6. Kontrolle: Auf den Rücken gelegt stehen Manschettenboden und Füße auf dem Tisch, die Flansche zeigen nach oben.

## 8. Bestücken

1. Ring mit der Bohrung nach oben ins runde Loch drücken, bis er einrastet.
2. Manschette mit dem Kiel zum Ring ins obere Loch drücken, bis sie einrastet.
3. Die Mitte der Schnur als Schlaufe durch den Kreuzschlitz ins Schnurfach schieben, bis beide Stücke gerade liegen.
4. Den oberen Deckel öffnen, den Einleger von oben einschieben, Deckel zu.
5. Den Hänger für den Versand nach vorn auf den Deckel klappen.

## 9. Kontrollmaße

- Kontrollquadrat: 30,0 × 30,0 mm
- Umverpackung außen gefaltet: 97 × 146 × 24,5 mm
- Einleger Deckbreite: 95,1 mm (Karton innen 96,1 mm)
- Ringloch: Ø71,3 mm. Der Ring hat Ø72; das Loch ist bewusst kleiner, damit er einrastet.

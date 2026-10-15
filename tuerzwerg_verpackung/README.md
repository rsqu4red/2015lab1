# Türzwerg – Verpackung

Faltschachtel (außen ca. 90 × 140 × 25 mm) mit Euroloch-Hänger über die volle Breite,
der zum Versand 90° nach vorn auf den Deckel klappt, und einem Einleger, in dem
Ringmitte und Manschettenachse auf gleicher Höhe liegen.

## Dateien (`out/`)

| Datei | Zweck |
|---|---|
| `Umverpackung_komplett.dxf`, `Einleger_komplett.dxf` | Plotdatei, Ebenen SCHNEIDEN (rot) + RILLEN (blau) |
| `*_schneiden.dxf`, `*_rillen.dxf` | dieselben Linien getrennt (falls Studio die Farben verliert) |
| `Umverpackung.svg`, `Einleger.svg` | für Silhouette Studio Designer Edition |
| `viewer.html` | 3D-Ansicht, Längsschnitt, Zuschnitte, Bestücken |
| `Tuerzwerg_Verpackung.step` / `.glb` | 3D-Gesamtmodell |
| `masse.json` | alle berechneten Maße |

Die Zuschnitte zeigen die Außenseite (Druckseite).
Umverpackung: 241 × 226 mm → 12×12″-Matte. Einleger: 116 × 322 mm → 12×24″-Matte.

## Einleger

Ein Streifen, alle Falze quer: Wand oben · Deck (mit Seitenflanschen) · Wand unten ·
Ringboden (4 Füße) · Stufe · Schnurboden · Stufe · Manschettenboden · Klebelasche.

- Ringmitte und Manschettenachse liegen beide 11,95 mm über der Rückwand.
  Die Schnurbohrungen liegen dadurch auf einer Linie, die Schnur läuft gerade.
- Manschette auf dem Boden an der Rückwand, 0,55 mm hinter der Front.
  Ring auf dem Ringboden (4,95 mm, auf Füßen), 5 mm hinter der Front.
- Deck auf 14,7 mm: Der Ring rastet ein (Loch 0,35 mm kleiner, Haltezungen),
  die Manschette wird eingelegt und von den Fensterrändern an den Stirnseiten gehalten.
- Schnurboden im 20-mm-Sichtfeld knapp unter der Schnur, mit Kreuzschlitz.
  Darunter das Schnurfach (88 × 16 × 8,5 mm, läuft flach unter dem Ringboden weiter).

## Hänger

Volle Breite, 24 mm hoch (flacher als der Karton tief), doppellagig. Der Falz an der
Oberkante der Rückwand wird für den Versand nur um 90° nach vorn gebogen, der Hänger
liegt dann flach auf dem Deckel. Euroloch mit 5 mm Steg zur Oberkante.

## Anpassen

Alle Maße stehen oben in `generate.py` (`P = dict(...)`). Danach neu erzeugen:

```bash
pip install cadquery shapely ezdxf trimesh
python generate.py && python build_viewer.py
```

Die früheren Varianten (A „gleiche Front“, B „gleicher Boden“) sind in der Git-Historie.

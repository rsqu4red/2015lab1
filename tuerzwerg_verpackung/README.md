# Türzwerg – Verpackung

Faltschachtel (außen 97 × 146 × 24,5 mm) mit Euroloch-Hänger über die volle Breite,
der zum Versand 90° nach vorn auf den Deckel klappt, und einem Einleger, in dem
Ringmitte und Manschettenachse auf gleicher Höhe liegen. Der Einleger wird von oben
eingeschoben und sitzt nach hinten und vorn fest.

## Dateien (`out/`)

| Datei | Zweck |
|---|---|
| `Umverpackung_komplett.dxf`, `Einleger_komplett.dxf` | Plotdatei, Ebenen SCHNEIDEN (rot), RILLEN_BERG (blau), RILLEN_TAL (grün) |
| `Bogen_12x24_komplett.dxf` | beide Teile auf einem Bogen für die 12×24″-Matte |
| `*_schneiden.dxf`, `*_rillen.dxf` | dieselben Linien getrennt, mit Passerwinkeln (falls Studio die Farben verliert) |
| `*.svg` | für Silhouette Studio Designer Edition |
| `viewer.html` | 3D-Ansicht, Längsschnitt, Zuschnitte, Bestücken |
| `Tuerzwerg_Verpackung.step` / `.glb` | 3D-Gesamtmodell |
| `masse.json` | alle berechneten Maße |

Die Zuschnitte zeigen die Außenseite (Druckseite). Plotten, Falten, Bestücken: siehe `ANLEITUNG_SILHOUETTE.md`.
Umverpackung: 254 × 232 mm → 12×12″-Matte. Einleger: 112 × 335 mm → 12×24″-Matte.

## Kartonmaße und Versandkarton

Die Maße sind auf Standard-Versandkartons abgestimmt (Hänger umgeklappt, Höhe dann 147 mm, 2–3 % Spiel):

| Versandkarton innen | Anordnung (stehend) | Stück | Füllung |
|---|---|---|---|
| 400 × 300 × 150 | 16 tief × 3 breit | 48 | 93 % |
| 300 × 200 × 150 | 12 tief × 2 breit | 24 | 93 % |
| 600 × 400 × 150 | 24 tief × 4 breit | 96 | 93 % |

## Fenster

- Manschettenfenster = Manschettenmaß 33 × 32 mm, Ringfenster Ø73.
- Fenstergruppe senkrecht mittig: 10,3 mm Rand oben (über dem Manschettenfenster) und unten (unter dem Ringfenster).

## Einleger

Ein Streifen, alle Falze quer: Wand oben · Deck (mit 2 Seitenflanschen) · Wand unten ·
Ringboden (4 Füße) · Stufe · Schnurboden · Stufe · Manschettenboden · Klebelasche.

- Ringmitte und Manschettenachse liegen beide 11,95 mm über der Rückwand.
  Die Schnurbohrungen liegen dadurch auf einer Linie, die Schnur läuft gerade.
- Manschette auf dem Boden an der Rückwand, 0,15 mm hinter der Front.
  Ring auf dem Ringboden (4,95 mm, auf Füßen), 4,65 mm hinter der Front.
- Deck auf 14,7 mm: Ring und Manschette rasten ein (Löcher 0,35 mm kleiner, Haltezungen).
- Fest im Karton: nach hinten über Manschettenboden und Füße auf der Rückwand, nach vorn
  über die beiden Seitenflansche des Decks (klappen nach vorn, 8,4 mm, bis an die Front).
- Befüllen: Boden einmal beim Falten schließen, Einleger von oben einschieben, Deckel zu.
- Schnurboden im 20-mm-Sichtfeld knapp unter der Schnur, mit Kreuzschlitz.
  Darunter das Schnurfach (95 × 16 × 8,5 mm, läuft flach unter dem Ringboden weiter).

## Hänger

Volle Breite, 24 mm hoch (flacher als der Karton tief, 24,5 mm), doppellagig. Der Falz an der
Oberkante der Rückwand wird für den Versand nur um 90° nach vorn gebogen, der Hänger
liegt dann flach auf dem Deckel. Euroloch mit 5 mm Steg zur Oberkante.

## Anpassen

Alle Maße stehen oben in `generate.py` (`P = dict(...)`). Danach neu erzeugen:

```bash
pip install cadquery shapely ezdxf trimesh
python generate.py && python build_viewer.py
```

Die früheren Varianten (A „gleiche Front“, B „gleicher Boden“) sind in der Git-Historie.

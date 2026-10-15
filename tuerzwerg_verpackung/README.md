# Türzwerg – Verpackung

Faltschachtel (außen ca. 90 × 140 × 30 mm) mit doppellagigem Euroloch-Hänger und
einem eingeschobenen Einleger. Ring und Manschette werden in den Einleger gedrückt.

## Dateien (`out/`)

| Datei | Zweck |
|---|---|
| `Umverpackung_komplett.dxf`, `Einleger_komplett.dxf` | Plotdatei, Ebenen SCHNEIDEN (rot) + RILLEN (blau) |
| `*_schneiden.dxf`, `*_rillen.dxf` | dieselben Linien getrennt (falls Studio die Farben verliert) |
| `Umverpackung.svg`, `Einleger.svg` | für Silhouette Studio Designer Edition |
| `viewer.html` | 3D-Ansicht + Zuschnitte + Montage im Browser |
| `Tuerzwerg_Verpackung.step` / `.glb` | 3D-Gesamtmodell |
| `masse.json` | alle berechneten Maße |

Die Zuschnitte zeigen die Außenseite (Druckseite).
Umverpackung: 251 × 253 mm → 12×12″-Bogen oder A3. Einleger: 221 × 138 mm → A4 quer.

## Aufbau Einleger

Der Einleger ist ein geklebtes Rohr und füllt den Karton in Breite und Tiefe aus.

- **Anschlagboden** 5,5 mm über der Rückwand, getragen von Füßen aus den Seitenwänden.
  Ring und Manschette schlagen hier hinten an.
- **Deck** 18 mm über der Rückwand, mit Stanzloch (Ring + Schnurkanal + Manschette) und
  Haltezungen. Das Deck liegt knapp über der dicksten Stelle beider Teile, sie rasten ein.
- **Stützlaschen** halten das Deck auf Abstand zur Front.
- Die Manschette liegt 0,5 mm hinter der Front, der Ring 9,5 mm dahinter. 20 mm Schnur sind sichtbar.

## Anpassen

Alle Maße stehen oben in `generate.py` (`P = dict(...)`). Danach neu erzeugen:

```bash
pip install cadquery shapely ezdxf trimesh
python generate.py && python build_viewer.py
```

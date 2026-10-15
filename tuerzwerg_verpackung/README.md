# Türzwerg – Verpackung

Faltschachtel (außen ca. 90 × 140 × 25 mm) mit klappbarem, doppellagigem Euroloch-Hänger
über die volle Breite. Zwei Varianten für den Einleger:

| | A · Gleiche Front | B · Gleicher Boden |
|---|---|---|
| Ring → Front | 0,55 mm | 9,55 mm |
| Manschette → Front | 0,55 mm | 0,55 mm |
| Einleger | Streifen, 6 Querfalze, 115 × 310 mm (12×24″-Matte) | Rohr, 4 Längsfalze, 201 × 136 mm (A4) |
| Ring | eingelegt, Fensterrand hält ihn | rastet im Deck ein (Haltezungen) |
| Restschnur | Fach unter dem Ringboden | Fach unter dem Deck hinter dem Sichtfeld |

Erzeugen: `python generate.py A`, `python generate.py B`, dann `python build_viewer.py`.
Dateien je Variante in `out/variante_A/` bzw. `out/variante_B/`, der Viewer in `out/viewer.html`.

## Dateien (`out/variante_X/`)

| Datei | Zweck |
|---|---|
| `Umverpackung_komplett.dxf`, `Einleger_komplett.dxf` | Plotdatei, Ebenen SCHNEIDEN (rot) + RILLEN (blau) |
| `*_schneiden.dxf`, `*_rillen.dxf` | dieselben Linien getrennt (falls Studio die Farben verliert) |
| `Umverpackung.svg`, `Einleger.svg` | für Silhouette Studio Designer Edition |
| `Tuerzwerg_Verpackung.step` / `.glb` | 3D-Gesamtmodell |
| `masse.json` | alle berechneten Maße |

Die Zuschnitte zeigen die Außenseite (Druckseite).
Umverpackung: 241 × 245 mm → 12×12″-Matte.

## Einleger Variante A

Ein Streifen, alle Falze quer: Wand oben · Deck (mit Seitenflanschen) · Wand unten · Ringboden ·
Stufe · Manschettenboden · Klebelasche.

- Manschette (23 mm) liegt auf dem Manschettenboden direkt an der Rückwand,
  Ring (14 mm) auf dem 9 mm höheren Ringboden. Beide Vorderseiten liegen 0,55 mm hinter der Front.
- Das Deck auf 14,2 mm hat Löcher mit 0,25 mm Luft: Die Teile werden nur hineingelegt.
  Nach vorn halten sie die Fensterränder (Ringfenster Ø67, Manschettenfenster 29 mm lang).
- Unter dem Ringboden liegt ein Schnurfach (88 × 91 × 8,6 mm) für die Restschnur (ca. 28 cm).
  Die Schnur taucht mittig im 20-mm-Sichtfeld durch einen Kreuzschlitz ab und kommt dort wieder heraus.

## Hänger

Volle Breite, 28 mm hoch, doppellagig, Falz an der Oberkante der Rückwand. Für den Versand flach nach
hinten geklappt. Aufgestellt wird die Zunge der Doppelung in den Schlitz im oberen Deckel
gesteckt; ihre Schultern rasten ein und halten den Hänger senkrecht.

## Anpassen

Alle Maße stehen oben in `generate.py` (`P = dict(...)`). Danach neu erzeugen:

```bash
pip install cadquery shapely ezdxf trimesh
python generate.py A && python generate.py B && python build_viewer.py
```

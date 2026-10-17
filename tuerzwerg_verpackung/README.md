# Türzwerg – Verpackung v3

Faltschachtel (außen ca. 84 × 135 × 24 mm) mit geschlossener, bedruckter Front: Manschette,
Schnur und Ring als Grafik in Originalgröße, darin drei kleine Sichtfenster auf das echte Material.
Euroloch-Hänger über die volle Breite, klappt zum Versand 90° nach vorn auf den Deckel.

## Aufbau

- **Front:** Etikett (Druck) auf dem Karton, drei Fenster (Manschette, Schnur ca. 14 mm, Ring).
  Die Fenster sind kleiner als die Teile und halten sie nach vorn, Ring und Manschette liegen innen an.
- **Einleger:** eine Platte mit vier nach hinten geklappten Rändern, ohne Klebestelle, 9 mm über der Rückwand.
  Die Manschette steckt durch ein Loch und steht auf der Rückwand, der Ring liegt auf der Platte und
  wird von vier hochgeklappten Laschen innen zentriert. Restschnur durch einen Querschlitz unter die Platte.
- **Fensterkonzepte:** A „Kapsel“ (Langlöcher, Bogen auf dem Ring), B „Bullauge“ (rund),
  C „Mittelachse“ (schmale Schlitze auf einer Linie).

## Dateien (`out/`)

| Datei | Zweck |
|---|---|
| `Konzept_X_…/Front-Etikett_A4_Konzept_X.pdf` | Druckvorlage Etikett (100 % drucken) |
| `Konzept_X_…/3_Front-Etikett_schneiden.dxf` | Etikett ausschneiden (A4 bündig oben links auf der Matte) |
| `Konzept_X_…/1_Umverpackung_perforiert.dxf` | Faltschachtel, 12×12″ |
| `Konzept_X_…/2_Einleger_perforiert.dxf` | Einleger, 12×12″ |
| `…_komplett.dxf` | wie oben, Falzlinien farbig (blau Berg, grün Tal) für Rillwerkzeug |
| `viewer.html` | 3D-Ansicht mit Konzeptwahl, Schnitt, Ablauf |
| `Tuerzwerg_Verpackung.step` / `.glb`, `front_X.png` | 3D-Modell, Front-Texturen |

Alle DXF haben genau die Mattengröße (304,8 × 304,8 mm, Eckmarken), Silhouette Studio skaliert sie nicht.
Anleitung: `ANLEITUNG_SILHOUETTE.md`.

## Anpassen

Maße oben in `generate.py` (`P = dict(...)`), Fenster in `windows()`. Neu erzeugen:

```bash
pip install cadquery shapely ezdxf trimesh cairosvg pillow
python generate.py && python build_viewer.py
```

Frühere Varianten (offenes Fenster, gestufter Einleger) sind in der Git-Historie.

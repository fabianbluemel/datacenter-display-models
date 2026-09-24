# Herkunft und Lizenzumfang

## Eigene Beiträge

Die parametrische X6-8-Geometrie, die mathematisch konstruierte Einsatzplatte, Layout, Quellcode, Dokumentation und daraus generierte STL/3MF werden unter Apache-2.0 bereitgestellt. Rechte an Drittanbieter-Marken oder Vorlagen werden dadurch nicht eingeräumt.

## Separater Displayrahmen

Der Standardboden von [ShapeShift 3D Creations](https://makerworld.com/de/models/1232070-led-light-display-stand-for-layered-car-art-prints) diente zur Ermittlung der Passmaße. Dieses Repository enthält weder dessen Rahmenmeshes noch die ursprünglichen 3MF-Projekte oder Fotos. Das generierte Modell ist auch ohne den Rahmen als Tischdisplay nutzbar.

## Technische Referenzen

- [Broadcom: Brocade X6 Director Product Brief](https://docs.broadcom.com/doc/GA-DS-5721)
- [Brocade X6-8 Hardware Installation Guide, bereitgestellt von Dell](https://www.delltechnologies.com/asset/en-us/products/storage/technical-support/docu71814.pdf)

Die Dokumente sind externe Referenzen und werden nicht mitgeliefert. Das Modell bildet Merkmale vereinfacht ab.

## Schrift und Werkzeuge

Beschriftungen verwenden DejaVu Sans aus Matplotlib. Die Schrift selbst wird nicht gebündelt; sie unterliegt der [Bitstream-Vera/DejaVu-Lizenz](https://dejavu-fonts.github.io/License.html). Renderings und Textkonturen entstehen mit der installierten Schrift.

Python-Abhängigkeiten werden über `requirements.txt` bezogen und behalten ihre jeweiligen Lizenzen. Es werden keine Bibliothekskopien veröffentlicht.

## Bambu-Druckprofil

`third_party/bambu/p1s-settings.json` enthält den vollständigen P1S-Profil-Export, einschließlich Bambu-G-Code-Vorlagen. Dieser getrennte Drittanbieteranteil und seine eingebettete Kopie im 3MF werden **nicht** unter Apache-2.0 umlizenziert. Die Bambu-Studio-Quellen stehen unter GNU AGPL v3; der Lizenztext liegt unter `third_party/bambu/LICENSE` bei. Quelle: [Bambu Studio / Profile](https://github.com/bambulab/BambuStudio/tree/master/resources/profiles), Copyright Bambu Lab und Bambu-Studio-Mitwirkende.

Anpassungen für dieses Modell (25.09.2026): P1S mit 0,4-mm-Düse, 0,2-mm-Schichten, 2 Wände, 15 % Füllung, normalisierte Filamentprofilnamen. Der bearbeitbare Profil-Export wird vollständig mitgeliefert. Die unabhängige Modellgeometrie und unsere Generator-/Render-Skripte bleiben Apache-2.0.

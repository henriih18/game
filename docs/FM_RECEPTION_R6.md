# FRECUENCIA MUERTA — Recepción R6: mostrador hero

## 1. Alcance

Primer pase hero de mobiliario de Recepción, elegido por el usuario como prioridad:

- Mostrador de recepción en L.
- Credenza de tres puertas.
- Dos monitores, teclado, CPU, cables, papeles, portapinceles y taza.
- Silla ergonómica de puesto de trabajo.

Sustituye la familia `PROP_REC02_Desk_*`, `Credenza*`, `Monitor_*`, `Chair_Desk*`, `Keyboard` y `CPU`, que eran piezas blockout de ~60 tris por objeto. Las piezas antiguas se conservan en `L1_RECEPTION_RETIRED`; no se borraron.

## 2. Resultado

Colección: `L1_RECEPTION_R6_HERO` (3 objetos).

| Objeto | Tris | Vértices | Polígonos |
|---|---:|---:|---:|
| `REC06_DESK_HERO` | 6.136 | 3.188 | 3.244 |
| `REC06_EQUIPMENT_HERO` | 8.438 | 4.508 | 4.721 |
| `REC06_CHAIR_HERO` | 4.764 | 2.452 | 2.466 |
| **Total** | **19.338** | **10.148** | **10.431** |

QA de geometría: **0 non-manifold, 0 caras degeneradas, UV presente** en los tres objetos.

- `REC06_DESK_HERO`: mostrador en L con panel frontal de 9 módulos, línea naranja de seguridad, zócalo, modesty, laterales, retorno, tablero, dos grommets, bandeja de cables, cajones y credenza de tres puertas con tiradores.
- `REC06_EQUIPMENT_HERO`: dos monitores con bezel, pantalla emisiva, dorso negro, rejillas, placa VESA, logo naranja y cables; teclado con teclas; CPU con rejillas y front I/O; papeles, portapinceles, bolígrafos y taza.
- `REC06_CHAIR_HERO`: base de cinco estrellas, ruedas, columna de gas, mecanismo, asiento, marco de respaldo, panel de malla, lumbar, costillas y apoyabrazos.

## 3. Materiales

Se usan materiales PBR y se corrigieron los valores para que el conjunto no dependiera de reflejos especulares:

- Laminado verde NEXUS: base (0,024, 0,036, 0,030), roughness 0,78, specular 0,05.
- Laminado oscuro: base (0,010, 0,015, 0,012), roughness 0,80, specular 0,04.
- Borde de goma: base 0,006, roughness 0,72, specular 0,05.
- Papel: (0,62, 0,60, 0,50), roughness 0,90.
- Cerámica: (0,55, 0,54, 0,48), roughness 0,45.
- Teclas: (0,010, 0,011, 0,010), roughness 0,65.
- Tela de silla: (0,040, 0,048, 0,042), roughness 0,95, specular 0,02.
- Plástico negro compartido: base 0,005, roughness 0,60, specular 0,15.

El naranja de seguridad y la pantalla emisiva son materiales independientes y conservan su color.

## 4. Renders de revisión

Script: `scripts/fm/fm_rec06_render.py`. No guarda el `.blend`.

- `docs/fm_rec06_desk_front.png` — vista frontal del mostrador; paneles verdes oscuros, línea naranja, tablero limpio, monitores y accesorios.
- `docs/fm_rec06_desk_threequarter.png` — vista 3/4 desde el noreste.
- `docs/fm_rec06_desk_detail.png` — detalle del tablero y equipos.
- `docs/fm_rec06_desk_staff.png` — vista desde el sur, con credenza y retorno.
- `docs/fm_rec06_desk_workstation.png` — vista del puesto de trabajo; la silla, el asiento, los apoyabrazos y la columna de gas son legibles.

Cámaras: frontal a 24 mm, 3/4 a 30 mm, detalle a 50 mm, staff a 28 mm y puesto de trabajo a 50 mm. Look-at estable con world up Z y aislamiento de cámara para evitar que una cámara antigua de la escena robe el render.

Iluminación: key 420 W, fill 180 W, rim 420 W, fill de puesto 90 W; exposure 0,38; Cycles 1280×720, 96 spp, denoise, AgX Medium High Contrast.

## 5. Correcciones y problemas resueltos

- **Colección R6:** tras el rebuild, `join_group` dejó los objetos en `Scene Collection` y `L1_RECEPTION_R6_HERO` vacía; el render solo mostraba R6 y el mostrador no aparecía. Se movieron los tres objetos a R6 y se parcheó `scripts/fm/fm_rec06_desk.py` para desvincularlos de cualquier colección y linkearlos a R6 antes de QA y guardado.
- **Cámara:** las tomas frontal y staff usaban una cámara antigua por un cuaternión degenerado y por falta de aislamiento. Se sustituyó por un look-at con world up Z, se ocultan las demás cámaras antes de cada toma y se asigna `scene.camera` explícitamente.
- **Papel negro:** el rectángulo oscuro era el grommet/sombra bajo los papeles. Se eliminaron las caras de papel del tablero (51 caras) y se conservaron los papeles de la credenza; el cuadrado negro desapareció del frontal.
- **Materiales lavados:** los enlaces del MixRGB y las ColorRamp eran correctos (MULTIPLY, Fac 0,55), pero el tablero reflejaba la key. Se fijaron Base Color/Roughness/Specular directos y se subió la rugosidad; el mostrador pasó a verde oscuro.
- **Silla invisible:** la credenza tapaba la silla desde el sur. Se añadió una cámara de puesto de trabajo desde el este y un fill local de 90 W; la silla ya se lee.

## 6. Limitaciones

- La silla solo se lee con claridad en `fm_rec06_desk_workstation.png`; en la vista frontal queda oculta por el mostrador, como es natural.
- El dorso del monitor tiene una placa VESA negra que puede leerse como un hueco; se corregirá en el pase de detalle de equipos.
- El suelo sigue azul claro y la sala más allá del mostrador continúa en blockout; este pase cubre el clúster del mostrador, no la identidad completa de Recepción.
- No hay texturas de imagen ni bake; los materiales son procedurales y la capa de texturas queda para la fase final.
- No se ha exportado GLB ni validado en Godot para este clúster.

## 7. Archivos

- `scripts/fm/fm_rec06_desk.py` — construcción idempotente y linkeo a R6.
- `scripts/fm/fm_rec06_render.py` — 5 cámaras, luces y render.
- `docs/fm_rec06_desk_qa.json` — QA del build original (19.428 tris; el valor actual es 19.338 tras retirar 51 caras de papel).
- `docs/backups/FM_LEVEL1_V06_ARCH_before_rec06_desk.blend` — backup previo.
- `docs/fm_rec06_desk_front.png`, `..._threequarter.png`, `..._detail.png`, `..._staff.png`, `..._workstation.png`.

Sin commit.

## 8. Siguiente

1. Security desk y monitor de seguridad.
2. Bancas A/B, taquillas y barrier/stanchions/belts.
3. Waiting, mesa, bins, jardinera, reloj y cámara.
4. Servicios y continuidad de Recepción (HVAC, bandejas, sprinklers, difusores y pasamuros), con las reglas de P0b.
5. Export GLB del clúster y validación Godot; después el pase de identidad/iluminación completa de Recepción.

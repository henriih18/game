# FM — Recepción R10–R12: desgaste, alfombra y espera hero

## Alcance

Este documento cierra el pase de ambientación y mobiliario de espera de la Recepción:

- **R10:** desgaste ambiental sutil (suciedad, roces, polvo, chips, óxido, manchas, papeles y escombros).
- **R11:** sustitución de la alfombra blockout por una alfombra hero con borde y grosor.
- **R12:** sustitución de bancas, mesa y jardinera blockout por un clúster hero de espera.

No se modificó la arquitectura, el recorrido central de extracción ni los clústeres R6/R7/R8/R9. Sin commit.

## R10 — desgaste ambiental

- Colección: `L1_RECEPTION_R10_AGING`.
- Conteo final: **72 objetos / 72 mallas / 3.096 tris / 59 decals / 13 props**.
- QA: `docs/fm_reception_r10_aging_qa.json`; `inside_reception=true`, `walkway_conflicts=[]`, `qa_pass=true`.
- Backup: `docs/backups/FM_LEVEL1_V06_ARCH_before_reception_r10_aging.blend`.
- Script: `scripts/fm/fm_reception_r10_aging.py`.
- Materiales: `M_REC10_Grime`, `Dust`, `Scuff`, `Wet`, `Rust`, `Chip`, `TapeWorn`, `Paper`, `Manila`, `Black`.
- El puddle `REC10_PUDDLE_0` se retiró porque se leía como un agujero negro en primer plano.
- Las carpetas y el clipboard se elevaron a z 0.460–0.472 para apoyarse sobre el tablero de la mesa, no dentro de él.
- Renders: `docs/fm_reception_r10_aging_wide.png`, `_waiting.png`, `_queue.png`, `_detail.png`, `_ceiling.png`.
- Script de render: `scripts/fm/fm_reception_r10_aging_render.py`; incluye R11/R12 y una luz de relleno de espera (`REC10_AGING_WAITING_FILL`, 320 W).

## R11 — alfombra hero

- Colección: `L1_RECEPTION_R11_HERO`.
- Objeto: `REC10_RUG_HERO`, **372 tris / 200 verts**; 0 non-manifold, 0 degenerados, UV.
- QA: `docs/fm_reception_r10_rug_qa.json`; backup `docs/backups/FM_LEVEL1_V06_ARCH_before_reception_r10_rug.blend`.
- Script: `scripts/fm/fm_reception_r10_rug.py`.
- Base 5,90 × 3,90 × 0,012 m, borde elevado de 0,18 m, esquina reforzada y pestaña levantada.
- Materiales: `M_REC10_Rug` (`srgb(92,104,90)`) y `M_REC10_Rug_Border` (`srgb(128,136,118)`).
- Sustituyó `PROP_REC02_Waiting_Rug`, retirada a `L1_RECEPTION_RETIRED`.

## R12 — espera hero

- Colección: `L1_RECEPTION_R12_HERO`.
- Objetos y tris:
  - `REC12_BENCH_A`: **5.200 tris**.
  - `REC12_BENCH_B`: **5.200 tris**.
  - `REC12_TABLE`: **1.424 tris**.
  - `REC12_PLANTER`: **3.992 tris** (incluye follaje).
  - Total: **15.816 tris**.
- QA: `docs/fm_reception_r12_waiting_qa.json`; 0 non-manifold, 0 degenerados, UV.
- Backup: `docs/backups/FM_LEVEL1_V06_ARCH_before_reception_r12_waiting.blend`.
- Script: `scripts/fm/fm_rec12_waiting.py`.
- Se retiraron 19 piezas blockout (`PROP_REC02_Bench_A_*`, `Bench_B_*`, `Table_*`, `Waiting_Planter*`) a `L1_RECEPTION_RETIRED`.
- Bancas: estructura de acero, listones de madera en asiento y respaldo, apoyabrazos, tornillos y topes.
- Mesa: tablero de madera con faldones, patas, estante inferior y revistas.
- Jardinera: hormigón, borde, tierra, tallos y hojas.
- Los bins `PROP_REC05_Bin_0/1` se movieron a `(-109.70,-29.20)` y `(-109.70,-30.00)`, fuera de la alfombra y del encuadre principal.

## Limitaciones

- El follaje de la jardinera sigue siendo escaso y geométrico; funciona a distancia, pero necesita una pasada de detalle si se va a ver en primer plano.
- El desgaste R10 es deliberadamente sutil; en la vista amplia casi no se lee. Es una base para la futura capa de texturas, no el resultado final.
- El panel/plank del suelo y los escombros son reutilizados de Seguridad/Z10; no tienen desgaste propio.
- No hay texturas/bake, GLB ni validación Godot de R10–R12.
- El entorno alrededor de la espera sigue siendo blockout (suelo azul, muros lisos, señalización simple).

## LOD, export y Godot de R12

- `L1_RECEPTION_R12_LOD`: 8 objetos / 7.846 tris.
  - Bancas: LOD1 1.976 tris, LOD2 624 tris.
  - Mesa: LOD1 640 tris, LOD2 212 tris.
  - Jardinera: LOD1 1.396 tris, LOD2 398 tris.
- QA: `docs/fm_reception_r12_lod_qa.json`; 0 non-manifold, 0 degenerados, UV.
- `L1_RECEPTION_R12_COLLISION`: 4 cajas `-col` de 12 tris (`REC12_BENCH_A/B-col`, `REC12_TABLE-col`, `REC12_PLANTER-col`), ocultas en Blender.
- GLB: `assets/models/fm/reception_waiting_lod.glb`, **17 objetos / 17 mallas únicas / 24.082 tris / 4 colisiones / 1.019.712 bytes**.
- AABB: `[-110.25,-24.86,0.0]..[-104.35,-18.74,1.1999]`.
- Reporte: `docs/fm_reception_waiting_lod_export.json`.
- Validación Godot 4.7.2 headless: **`REC12_WAITING_GODOT_OK`**, 17 `MeshInstance3D`, 17 mallas únicas, 4 `CollisionShape3D`, AABB `5,899994 × 1,199867 × 6,119999 m`, 0 strays.
- Escena/script: `scenes/fm/fm_reception_waiting_validate.tscn`, `scripts/fm/fm_reception_waiting_godot_validate_node.gd`.
- Export headless: `scripts/fm/fm_reception_waiting_export_headless.py` (carga el `.blend`, borra todo lo ajeno, exporta y no guarda).
- Limitación: solo cubre la espera R11/R12; R6–R10 siguen sin LOD/export propio. Los nodos `-col` deben ocultarse al instanciar.

## Sector completo de Recepción

- GLB: `assets/models/fm/reception_sector.glb`.
- **326 objetos / 308 mallas únicas / 379.562 tris / 35,49 MB**.
- Incluye shell de Recepción, vestíbulo, columnas, R1–R12, servicios R9 y aging R10.
- AABB: `[-110.25,-40.15,-0.2]..[-69.8405,-3.8126,5.4]`.
- Reporte: `docs/fm_reception_sector_export.json`.
- Export headless: `scripts/fm/fm_reception_sector_export_headless.py`.
- Validación Godot: **`RECEPTION_SECTOR_GODOT_OK`**, 326 `MeshInstance3D`, 308 mallas únicas, AABB `40,4095 × 5,6 × 36,33739 m`, 0 strays.
- Escena/script: `scenes/fm/fm_reception_sector_validate.tscn`, `scripts/fm/fm_reception_sector_godot_validate_node.gd`.
- Limitaciones: sin colisiones de jugador, sin LOD global y sin texturas/bake; 326 draw calls y 379.562 tris son un export de validación, no el resultado optimizado.

## Siguiente

1. Colisiones/proxies del sector y prueba de cápsula/jugador.
2. LOD/optimización del sector y taquillas/señalización hero.
2. Taquillas y señalización de Recepción a nivel hero.
3. Servicios pendientes de Recepción/Seguridad y patinillos (decisión del usuario: dejar pendiente).
4. Texturas/bake y narrativa al final.

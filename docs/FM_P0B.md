# FRECUENCIA MUERTA — P0b.1: columna vertebral del corredor + ramal Z10

Estado: **construido, QA técnico PASS, guardado**. Sin commit.
Fecha: 2026-11-09.

## 1. Alcance ejecutado

- HVAC rectangular 800×600 continuo, x −99,0..73,8, y −2,00, centro z 3,55.
- Bandeja 400×100 continua, x −99,0..73,8, y 0,20, centro z 3,20.
- Sprinkler DN80 continuo, x −99,0..73,8, y 2,40, centro z 3,90, cabezas cada 4,0 m.
- Ramal HVAC 800×600 a Z10: x 43,0, y −2,0..19,6, z 3,55, con tee en el ducto
  principal y collarín de conexión en el ducto existente de Z10.
- Dos sleeves rectangulares 800×600 con firestop: y = 4,0 (dintel del vano norte)
  e y = 8,0 (entrada de Z10).
- Tapones ciegos atornillados en los extremos oeste (x −99,0) y este (x 73,8).
- Soportes: trapecio HVAC cada 4,8 m, bandeja cada 3,0 m, sprinkler cada 4,0 m.
- Etiquetas de identificación cada 9,6 m.

## 2. Inventario real

| Objeto | Tris |
|---|---:|
| P0B_HVAC_RUN_800x600 | 71.712 |
| P0B_HVAC_BRANCH_Z10 | 8.964 |
| P0B_TRAY_RUN_400 | 41.184 |
| P0B_SPRINKLER_RUN_DN80 | 40.896 |
| P0B_SPRINKLER_HEADS | 42.656 |
| P0B_SUPPORTS_HVAC | 20.592 |
| P0B_SUPPORTS_TRAY | 27.588 |
| P0B_SUPPORTS_SPRINKLER | 13.244 |
| P0B_SLEEVE_CORR | 3.308 |
| P0B_SLEEVE_Z10 | 3.308 |
| P0B_LABELS | 3.240 |
| P0B_END_FLANGE_W/E | 560 + 560 |
| P0B_BLIND_W/E | 316 + 316 |
| P0B_TEE_MAIN | 560 |
| P0B_TEE_Z10 | 560 |
| **Total** | **279.564** |

17 mallas, 0 non-manifold, 0 degeneradas, UV presente en todas.
QA: `docs/fm_p0b_qa.json`.

## 3. Desviación respecto al presupuesto

El plan estimó ≤ 90.000 tris para la columna. La implementación real tiene
279.564 tris porque se mantuvieron bridas con pernos, refuerzos, costura,
soportes completos, cabezas de sprinkler con drop y sleeves con collarín.
Es coherente con el estándar hero, pero **requiere LOD1/LOD2** antes de
considerarlo cerrado para rendimiento. Se documenta como deuda P0b.3.
No se reduce ahora la calidad visual sin medir primero en Godot.

## 4. Validación visual

- `docs/fm_p0b_corridor_long.png`: corredor real con techo, muros y suelo;
  las tres líneas de servicio recorren el corredor sin cortes.
- `docs/fm_p0b_z10_branch.png`: corte técnico con el techo y el muro norte
  ocultos; se ve el ramal saliendo del ducto principal, los dos sleeves rojos
  y la conexión hacia Z10.

## 5. Archivos

- `scripts/fm/fm_p0b_corridor.py` — construcción, QA y guardado.
- `scripts/fm/fm_p0b_render.py` — rig de estudio (no guarda).
- `scripts/fm/fm_p0b_render_context.py` — renders dentro del corredor (no guarda).
- `scripts/fm/fm_p0b_export.py` — export GLB limpio (no guarda).
- `scripts/fm/fm_p0b_godot_validate_node.gd` + `scenes/fm/fm_p0b_validate.tscn` — validación headless.
- `assets/models/fm/p0b_corridor_services.glb` — GLB de la columna (10,24 MB).
- `docs/fm_p0b_qa.json` — QA por objeto.
- `docs/fm_p0b_export.json` — inventario del GLB.
- `docs/backups/FM_LEVEL1_V06_ARCH_before_p0b1.blend` — copia previa.

## 5.1. Export GLB y validación Godot

El export se corrigió para no arrastrar objetos ajenos: `fm_p0b_export.py`
desvincula temporalmente `PROP_Z10_LockerDoor_01`, `STUDIO_Z10_Backdrop` y
`STUDIO_Z10_Floor`, exporta con `use_selection=True` y los revincula en
`finally`. Resultado:

- `assets/models/fm/p0b_corridor_services.glb`: **17 objetos / 16 mallas**
  (los dos sleeves comparten malla), **145.256 vértices**, **279.564 tris**,
  **10.244.988 bytes**; AABB `[-99.053,-2.51,3.1]..[73.853,19.6,3.99]`;
  **0 strays**.
- Validación Godot 4.7.2 headless: **`P0B_GODOT_OK`**. 17 `MeshInstance3D`,
  16 mallas únicas, los 17 nombres esperados, sin `STUDIO*` ni `PROP_*`.
  AABB importada: posición `(-99.053, 3.1, -19.6)`, tamaño
  `(172.906, 0.89, 22.11)` — Godot usa Y arriba, por eso X/Y/Z se reordenan
  respecto a Blender; el ramal Z10 queda en Z negativa.
- `P0B_HVAC_RUN_800x600`: AABB `(172.8, 0.66, 0.86)`, confirma la sección
  0,8 × 0,6 m y la longitud continua del tramo.
- No se midieron draw calls ni FPS en una escena jugable; esta validación es
  de importación, escala y contenido.

## 5.2. LOD0/LOD1/LOD2 de la columna

- Script: **`scripts/fm/fm_p0b_lod.py`**. Genera 17 LOD1 + 17 LOD2 en la
  colección hija **`L1_P0B_LOD`**; los activos quedan ocultos en viewport y
  render porque son biblioteca, no geometría duplicada del corredor.
- Decimate COLLAPSE con `use_collapse_triangulate=True`; ratios **0,35 / 0,12**;
  LOD1 smooth y LOD2 flat; limpieza de doubles/degenerados y separación de
  aristas con más de dos caras.
- Resultado: **LOD0 279.564 tris; LOD1 97.832 (34,99 %); LOD2 33.908 (12,13 %)**.
- QA **0 fallos**, 0 non-manifold, 0 degeneradas y UV presente:
  `docs/fm_p0b_qa_lod.json`. El primer pase dejó 2 aristas con 4 caras en
  `P0B_SPRINKLER_RUN_DN80_LOD1`; `bmesh.ops.split_edges` las separó y el
  segundo pase salió limpio.
- Render comparativo: **`docs/fm_p0b_lod_compare.png`**, generado con
  `scripts/fm/fm_p0b_lod_render.py` (sección de 2,4 m de HVAC, tres niveles).
  LOD0 conserva bridas, refuerzos y remaches; LOD1 mantiene silueta y detalle;
  LOD2 simplifica a formas principales. LOD2 está pensado para distancias
  superiores a ~35 m.

### Export y validación Godot

- **`scripts/fm/fm_p0b_export_lod.py`** → `assets/models/fm/p0b_corridor_services_lod.glb`:
  **51 objetos / 50 mallas / 411.304 tris / 18.226.392 bytes**; AABB idéntica
  a LOD0; **0 strays**. Informe `docs/fm_p0b_export_lod.json`.
- Los dos sleeves comparten malla en LOD0; por eso hay 50 mallas para 51
  objetos.
- El exportador advirtió de dos mallas LOD2 no-manifold
  (`P0B_HVAC_RUN_800x600_LOD2`, `P0B_HVAC_BRANCH_Z10_LOD2`), pero la
  importación en Godot es correcta; son avisos de topología abierta, no
  geometría perdida.
- Validación Godot: escena **`scenes/fm/fm_p0b_lod_validate.tscn`** +
  **`scripts/fm/fm_p0b_lod_godot_validate_node.gd`**.
  Resultado **`P0B_LOD_GODOT_OK`**: 51 `MeshInstance3D`, 50 mallas únicas,
  **17 LOD0 + 17 LOD1 + 17 LOD2**, sin strays.
  AABB importada: posición `(-99.053, 3.1, -19.60062)`, tamaño
  `(172.906, 0.8901, 22.11062)` (Y arriba en Godot).

## 5.3. P0b.4 — servicios principales de Z10

Se sustituyeron los servicios principales de Z10 por tramos hero derivados
de la columna P0B, manteniendo la arquitectura y los props existentes.

### Construido

- **HVAC 800×600:** tramo continuo x 40,20..61,83, y 20,00, centro z 3,55,
  con bridas, refuerzos, costura, cleats, pernos y cleats de colgado.
  **9.564 tris.**
- **Soporte HVAC:** 2.598 tris, con 8 extensiones de varilla hasta el techo
  (z 3,99..4,19).
- **Sprinkler DN80:** tramo x 40,20..61,80, y 17,00, z 3,90,
  **5.218 tris**; cabezas **4.960 tris**; soportes **1.540 tris**.
- **4 difusores** `SM_SH_HVAC_GRILLE_600x400` bajo el ducto en
  x 43/48/53/58, y 20, z 3,22, rotados +90° Y, con malla compartida
  (3.820 tris cada uno).
- **Pasamuros:** 2 sleeves rectangulares 800×600 en x 40,17 y 61,85,
  y 20, z 3,55 (3.308 tris cada uno); 2 sleeves de tubo DN80 en x 40,17
  y 61,85, y 17, z 3,90 (7.916 tris cada uno).
- **Conducto este sobre la puerta:** tramo de 6 m entre y 18..24 a
  x 61,78, z 3,15, con 2 abrazaderas, usando la malla detallada de
  `KIT_PILOT_Z10_Conduit_02`.
- **Panel `PROP_Z10_SVC_EastCompletion`:** se le practicó un hueco
  booleano para el paso del ducto (284 tris, 0 non-manifold,
  0 degenerados, UV presente).
- **Retirados** a la colección oculta `Z10_RETIRED_P0B4` (sin borrar,
  para rollback): ducto viejo, 8 flanges, 8 hangers, soportes HVAC,
  `SVC_HVACCompletion`, `SVC_HVACWallConnections`, sprinkler pipe,
  5 cabezas y 5 hangers. También se retiraron los dos sleeves huérfanos
  `KIT_PILOT_Z10_Sleeve_00/01`.

### Enlace al Service Link y placas de risers

- **Enlace HVAC al Service Link:** tramo x 61,828..70,0, y 20,00,
  z 3,55, **3.376 tris**, derivado de la columna P0B y apoyado por
  `P0B4_SUPPORTS_LINK` (**632 tris**). Atraviesa el dintel sobre la puerta
  de Zone06 (el hueco de puerta queda por debajo de z 2,6).
- **Fire damper:** `SM_SH_FIREDAMPER_800x600` en x 69,276..69,634,
  y 20,00, z 3,55, **7.888 tris**.
- **Sleeve este del link:** `SM_SH_SLEEVE_RECT_800x600` en
  x 69,846..70,154, **3.308 tris**, con collarín intumescente.
- **Placas de paso de risers:** `P0B4_RISER_PASS_PLATES`, **720 tris**;
  tres placas de 0,14 × 0,14 × 0,012 m con cuatro pernos cada una en los
  tubos de riser A (x 46,27; y 15,8/16,0/16,2) y B (x 55,73;
  y 23,8/24,0/24,2), a z 0,006 y z 3,986. Material del tubo de riser.

### Conteos y QA

- `L1_P0B4_Z10`: **22 mallas / 78.080 tris**.
- BBox global: `[40,0105, 15,73, 0,0]` a `[70,154, 24,27, 4,19]`
  (incluye el enlace, las placas de risers y los sleeves).
- QA `docs/fm_p0b4_qa.json`, `docs/fm_p0b4_fix_qa.json` y
  `docs/fm_p0b4_link_qa.json`: **0 non-manifold, 0 degenerados,
  UV presente** en todas las mallas.
- Renders: `docs/fm_p0b4_z10_context.png` (conjunto),
  `docs/fm_p0b4_z10_detail.png` (ducto, difusores, sleeve y puerta),
  `docs/fm_p0b4_link.png` (vista a través del sleeve hacia el fire
  damper; verificaciación técnica, no beauty) y
  `docs/fm_p0b4_risers.png` (risers A/B con placas, válvulas y
  manómetro). El metal aparece limpio y brillante frente al entorno
  sucio; el envejecido se difiere a la pasada de texturas.

### Limitaciones pendientes

- El extremo este del ducto termina en el muro x=70 con fire damper y
  sleeve; la distribución dentro de **Zone06 Warehouse** aún no existe.
  El extremo oeste termina en muro sin patinillo (decisión pendiente del
  usuario).
- La bandeja oeste/este ya tiene pase hero (§5.5). El cuerpo de los
  risers A/B y los ramales/feeds de sprinkler siguen sin ese pase.
- El GLB de servicios P0b.4 sí se exportó y validó en Godot (§5.4);
  lo que sigue pendiente es el GLB completo de la sala Z10 con shell,
  props e iluminación.

## 5.4. Export GLB y validación Godot de P0b.4

- `scripts/fm/fm_p0b4_export.py` exporta las 22 mallas de
  `L1_P0B4_Z10` a `assets/models/fm/p0b4_z10_services.glb`.
- Resultado: **22 objetos, 15 mallas únicas, 78.080 tris, 2,86 MB**;
  AABB `[40,0105, 15,73, 0,0]..[70,154, 24,27, 4,19]`; 0 strays.
- Informe: `docs/fm_p0b4_export.json`.
- Validación headless: `scenes/fm/fm_p0b4_validate.tscn` +
  `scripts/fm/fm_p0b4_godot_validate_node.gd`.
- **`P0B4_GODOT_OK`:** 22 `MeshInstance3D`, 15 mallas únicas, AABB
  Godot `(40,0105, 0,0, -24,27)` tamaño `(30,14301, 4,19, 8,54)`;
  HVAC principal `21,628 × 0,66 × 0,86 m`; 4 difusores presentes;
  0 strays. Este es el resultado del primer export, antes de las
  bandejas; el estado vigente está en §5.5.

## 5.5. Bandejas hero oeste y este

- `scripts/fm/fm_p0b4_tray.py` añade tres mallas a `L1_P0B4_Z10`:
  - **`P0B4_TRAY_WEST`:** 49.168 tris, x 40,42, y 4,67..34,93,
    z 3,02; bandeja 400×100 montada en el muro oeste x=40,0.
  - **`P0B4_TRAY_EAST`:** 36.280 tris, x 61,68, y 8,0..30,0,
    z 3,54; montada en el muro este x=62,0.
  - **`P0B4_TRAY_SLEEVES`:** 1.216 tris; marcos pasamuros en y=8,0
    y y=30,0 para la bandeja oeste, con tiras intumescentes rojas.
- Total añadido: **86.664 tris**. Raíles C con pestañas, peldaños cada
  0,30 m, clips, placas de empalme cada 2,4 m con 4 pernos, soportes
  cantilever cada 3,0 m (placa de muro, brazo, tirante diagonal y
  4 pernos), tapas de extremo, 3 cables (negro/naranja/negro) y bridas
  cada 0,6 m.
- **Retirados** a `Z10_RETIRED_P0B4` (ocultos, sin borrar):
  `PROP_Z10_WestTray`, `PROP_Z10_SVC_WestTrayCables`,
  `KIT_PILOT_Z10_Tray_00..04` y `KIT_PILOT_Z10_TrayBracket_00..04`.
- QA `docs/fm_p0b4_tray_qa.json`: **0 non-manifold, 0 degenerados,
  UV presente**.
- Renders: `docs/fm_p0b4_tray_west.png`, `fm_p0b4_tray_east.png` y
  `fm_p0b4_tray_wide.png`. La geometría se lee continua; las bandejas
  quedan oscuras por falta de luz directa, no por material. El techo
  sigue limpio: la deuda visual principal es iluminación + abandono.
- **GLB actualizado:** `assets/models/fm/p0b4_z10_services.glb`,
  **25 objetos / 18 mallas únicas / 164.744 tris / 6,24 MB**, 0 strays;
  `docs/fm_p0b4_export.json`.
- **Godot:** `P0B4_GODOT_OK`; 25 `MeshInstance3D`, 18 mallas únicas,
  AABB `(39,98, 0,0, -34,939)` tamaño `(30,1735, 4,19, 30,278)`;
  HVAC `21,628 × 0,66 × 0,86 m`; 4 difusores; 0 strays.
- **Coste:** +86.664 tris por dos bandejas de 30,26 m y 22,0 m. El
  detalle es hero, pero conviene LOD1/LOD2 antes del export final de la
  sala.

## 5.6. Pase de abandono e iluminación de Z10

- Colecciones nuevas: `L1_Z10_ABANDON`, `L1_Z10_LIGHTING` y
  `L1_Z10_ATMOSPHERE`.
- **45 objetos / 38 mallas / 7 luces / 57.372 tris nuevos**; bbox
  `[40,0, 8,0, -0,0002]..[62,0, 30,0, 4,2]`; sin conflictos de portal ni
  objetos fuera de la sala.
- Iluminación práctica: 3 POINT de techo de 55 W; spill sur de 35 W;
  work light de trípode con SPOT 260 W + relleno de 45 W; emergencia este
  de 10 W; volumen local de niebla de 22×22×4,2 m.
- QA: `docs/fm_z10_abandon_qa.json`.
- Renders: `docs/fm_z10_abandon_wide.png`,
  `docs/fm_z10_abandon_worklight.png` y
  `docs/fm_z10_abandon_ceiling.png`. Los renders usan dos rebotes
  temporales de 140 W y 80 W y exposición 1,15; no forman parte del juego.
- Informe completo: `docs/FM_Z10_ABANDON.md`.
- Limitación: el GLB completo de la sala (shell, props, abandono y luces)
  se exportó y validó después; ver §5.7.

## 5.7. Export GLB del sector Z10 + Service Link y validación Godot

- Script: `scripts/fm/fm_z10_sector_export.py`. Selecciona solo mallas y
  luces del sector (Z10 x40..62 / y8..30 y Service Link x62..70,2 /
  y18..24), excluye studio, player, retirados, LOD, legacy, etiquetas y
  `ChangingConnector`, y desvincula temporalmente los objetos de
  colecciones excluidas para que el exportador no los arrastre.
- Resultado Blender: **516 objetos / 507 mallas / 402 mallas únicas /
  9 luces / 481.118 tris / 112.668.196 bytes (112,67 MB)**.
  BBox `[39,87, -2,0, -0,209]..[70,1535, 34,939, 6,0]`; el mínimo y=-2 y
  el máximo y=34,94 corresponden al ramal del corredor y a la bandeja
  oeste, no a geometría fuera de servicio.
- Este export **incluye los risers hero de §5.8 y las ramas de sprinkler
  de §5.9**. Respecto al export de referencia (537 objetos / 528 mallas /
  423 únicas / 432.614 tris) se retiraron los 26 objetos viejos de riser
  (−6.160 tris) y se añadieron los dos risers (+38.272 tris), lo que dio
  513 objetos / 504 mallas / 399 únicas / 464.726 tris. El pase P0b.5b
  restó 960 tris de ramas y 1.872 de cabezas y añadió 19.224 tris nuevos.
- GLB: **506 mallas / 401 únicas / 9 luces**; sin `STUDIO_*`,
  `VAL_*`, `PlayerProxy`, `RETIRED`, `L1_P0B_LOD`, `ChangingConnector`
  ni `Z10_LEGACY_DUPLICATES`.
- Validación Godot 4.7.2 headless:
  `scenes/fm/fm_z10_sector_validate.tscn` +
  `scripts/fm/fm_z10_sector_godot_validate_node.gd`.
  Resultado **`Z10_SECTOR_GODOT_OK`**, exit 0: **506 MeshInstance3D,
  401 mallas únicas, 9 luces**; AABB posición
  `(39,87, -0,208947, -34,939)`, tamaño
  `(30,2835, 6,208947, 36,939)`. Incluye `P0B5_RISER_A`,
  `P0B5_RISER_B`, `P0B5_SPRINKLER_BRANCHES`, `P0B5_SPRINKLER_TEES` y
  `P0B5_SPRINKLER_ESCUTCHEONS`.
- Informe: `docs/fm_z10_sector_export.json`.
- Limitaciones: el GLB de **112,67 MB** es un export de validación, no
  apto para producción sin LOD, fusión de mallas, texturas comprimidas y
  optimización; incluye servicios que sobresalen de la sala para
  conservar la continuidad. No se midieron draw calls ni FPS.


## 5.8. P0b.5 — risers A/B a nivel hero

- Script: `scripts/fm/fm_p0b5_risers.py`. Crea la colección raíz
  **`L1_P0B5_Z10`** y retira a `Z10_RETIRED_P0B4` (ocultos, sin borrar)
  los 26 objetos antiguos de los dos risers: 6 tubos, 6 válvulas,
  6 volantes, 6 soportes y 2 manómetros. Conserva
  `PROP_Z10_RiserIdentification` y las placas de paso de P0b.4.
- Resultado: **`P0B5_RISER_A` y `P0B5_RISER_B`**, una malla unificada
  por riser. **19.136 tris y 9.980 vértices cada una; 38.272 tris y
  19.960 vértices en total**.
- Composición por riser: tres tubos verticales de 20 lados y 0,07 m de
  diámetro (rojo de suministro, galvanizado y oscuro) en x=46,27 /
  55,73 e y=15,8/16,0/16,2 y 23,8/24,0/24,2; cuatro bridas de 0,058 m
  con 8 pernos cada una; tres acoplamientos; cuerpo de válvula, bonnet,
  vástago y volante de toro con 6 radios y cubo; un manómetro por riser
  en el tubo central, con cara blanca, aro rojo, aguja y racor; tres
  soportes de pared con placa, brazos, abrazaderas y pernos.
- QA: `docs/fm_p0b5_qa.json`, **PASS**: 0 aristas non-manifold,
  0 caras degeneradas y UV presente en ambas mallas.
- Backup previo: `docs/backups/FM_LEVEL1_V06_ARCH_before_p0b5.blend`.
  `.blend` guardado (33 MB).
- Renders de revisión:
  - `docs/fm_p0b5_riser_close.png`: close-up técnico desde el este con
    los tres tubos, bridas, válvulas, volantes, un manómetro central y
    soportes. Limitaciones: el rojo sale salmón por la clave cálida, los
    volantes se leen como aros y el soporte inferior derecho queda como
    un bloque claro. No es una imagen beauty.
  - `docs/fm_p0b5_risers_wide.png`: contexto de la nave con el riser A
    en primer plano y el riser B al fondo. El riser A monta en la cara
    este de su columna y el B en la cara oeste; desde el suroeste solo se
    lee completo el grupo rojo del A, mientras el B muestra el conjunto.
    Es una vista de integración, no un catálogo de los seis tubos.
- El sector exportado en §5.7 **ya incluye** `L1_P0B5_Z10` P0b.5 y las
  ramas de sprinkler de P0b.5b; se reexportó `z10_sector.glb` y se
  revalidó en Godot con **`Z10_SECTOR_GODOT_OK`**: 506 mallas, 401
  únicas y 9 luces. Los conteos incorporan las dos mallas de risers y las
  tres de P0b.5b, y descuentan los 26 objetos viejos y las piezas
  sustituidas de sprinkler.

## 5.9 P0b.5b — ramas de sprinkler a nivel hero

Alcance: sustituir los dos tubos largos de 20 m de `PROP_Z10_SprinklerBranches` (240 tris cada uno, 8 lados) por ramas de 20 lados con bridas, pernos, abrazaderas y tapas; añadir tees hero en la conexión con la línea principal y escutcheones en las cabezas de rama; resolver la cabeza que coincidía con el tee de x=55/y=17.

- `P0B5_SPRINKLER_BRANCHES`: 10.992 tris / 5.824 verts. Dos tubos de 20 m a 20 lados, r 0,035, z 3,90; 9 bridas por rama cada 2,4 m con 6 pernos; abrazaderas en y 10/14/24/28; tapas galv en y 9/29.
- `P0B5_SPRINKLER_TEES`: 4.456 tris / 2.352 verts. Tee en (45,17) y (55,17): cuerpo X r 0,070×0,20, cuello Y r 0,052×0,14, collares y pernos, boss de latón.
- `P0B5_SPRINKLER_ESCUTCHEONS`: 3.776 tris / 1.920 verts. 8 aros/cono en las cabezas de rama.
- `PROP_Z10_SprinklerBranches`: 8.608 → **7.648 tris**; se retiraron por conectividad los 2 tubos largos (−480) y los 2 tees viejos (−480).
- `P0B4_SPRINKLER_HEADS`: 4.960 → **3.088 tris**; booleano EXACT retiró la cabeza de (55,17) (−1.872); quedan 4 cabezas.

QA `docs/fm_p0b5b_qa.json`: 0 non-manifold, 0 degenerados, UV presente en las 3 mallas nuevas y en las dos fuentes modificadas. `.blend` guardado.

Renders: `docs/fm_p0b5b_tee_close.png` (cruce del ramal con la línea principal, tee, bridas y conducto) y `docs/fm_p0b5b_branches_wide.png` (ambas ramas, colgadores, risers y techo). Aprobados como verificación técnica, no beauty final.

Limitaciones: `PROP_Z10_SprinklerFeeds` (3.860 tris) sigue en detalle medio; las cabezas/colgadores de rama se conservaron (192/224 tris) y solo se vistieron con escutcheones; la línea principal sigue siendo el tramo P0b.4. No hay texturas/bake; el metal sale limpio en los renders.

Backup: `docs/backups/FM_LEVEL1_V06_ARCH_before_p0b5b.blend`. Sin commit.

## 5.10 P0b.5c — alimentaciones de sprinkler a nivel hero

Alcance: sustituir `PROP_Z10_SprinklerFeeds` (3.860 tris, tubos de 8 lados y válvulas sin lectura) por dos alimentaciones independientes con tubo de 20 lados, bridas, pernos, acoplamientos, válvulas de compuerta y manómetros. La primera pasada de P0b.5c se **rechazó en revisión visual**: los volantes quedaban a z 4,13, dentro del forjado (3,99–4,19), y la válvula de B caía sobre el conducto (y 19,57–20,43, techo 3,85). Se corrigió la instalación antes de aprobar.

- `P0B5_FEED_A`: 8.784 tris / 4.484 verts; bbox x 46,000–46,355, y 15,805–17,035, z 3,831–4,060. Tubo de 20 lados, r 0,035, z 3,90; bridas de 0,058 con 6 pernos; válvula en y 16,55.
- `P0B5_FEED_B`: 9.896 tris / 5.044 verts; bbox x 55,450–55,805, y 17,035–23,800, z 3,831–4,060. Acoplamientos en y 18,45 y 22,35 (fuera del conducto); válvula en y 21,55.
- Válvulas con vástago horizontal hacia −X: bonnet, prensaestopas y vástago en X; volante de 6 radios en plano YZ en x−0,265. Cota máxima del volante 3,969, por debajo de la cara inferior del techo (3,99). Ambas válvulas quedan fuera del conducto.
- Manómetros en el lado +Y de la válvula (y+0,30), cuerpo en X, esfera blanca con aguja y 12 marcas; cara hacia −X para leerse desde la sala. Cota superior 3,941.
- Soporte de techo con abrazadera, varilla y placa bajo el forjado (placa 3,978–3,990); la varilla entra en el forjado.
- `PROP_Z10_SprinklerFeeds` retirado a `Z10_RETIRED_P0B4` (oculto).
- QA `docs/fm_p0b5c_qa.json`: 0 non-manifold, 0 degenerados, UV presente; `qa_pass: true`; revisión `R2`. `.blend` guardado.

Renders: `docs/fm_p0b5c_feeds_close.png` (volante de 6 radios, cuerpo de válvula, prensaestopas y manómetro con aguja) y `docs/fm_p0b5c_feeds_wide.png` (tramo B sobre el conducto y soporte de techo). Aprobados como verificación técnica, no beauty final.

Exportación: `assets/models/fm/z10_sector.glb` reexportado con `scripts/fm/fm_z10_sector_export.py`: **517 objetos / 508 mallas / 403 únicas / 9 luces / 495.938 tris / 113.123.568 bytes (113,12 MB)**; bbox `(39,87, −2,00, −0,209)..(70,154, 34,939, 6,00)`. Frente a §5.7 son +1 objeto, +1 malla, +1 única, +14.820 tris y +455.372 bytes: entran las dos alimentaciones y sale el objeto retirado. También se corrigió el export para evaluar las colecciones maestras ocultas: `SM_L1_Conn_ServiceLink_Ceiling` conserva ahora su transformación `(66, 21, 4,09)` en lugar de caer al origen. Godot: `Z10_SECTOR_GODOT_OK`, 508 `MeshInstance3D`, 403 mallas únicas, 9 luces, AABB pos `(39,87, −0,209, −34,939)` / tamaño `(30,284, 6,209, 36,939)`. El primer intento leyó caché de importación antigua (506/401); hay que ejecutar `godot --headless --path . --import` tras sustituir el GLB y validar después. Informe: `docs/fm_z10_sector_export.json`.

Limitaciones: sin texturas/bake; el manómetro es geometría simple (sin cristal); la línea principal y las cabezas siguen siendo P0b.4/P0b.5b; el GLB completo se ha exportado como checkpoint de integración, pero sigue pendiente de LOD/fusión/optimización antes de producción. Backup: `docs/backups/FM_LEVEL1_V06_ARCH_before_p0b5c_feeds.blend`. Sin commit.

## 5.11 P0b.5d — cierre de servicios S-10..S-15

Fecha: 2026-11-10. Estado: **cerrado y validado**. Este pase termina el resto de servicios de Z10 que seguía abierto en P0b.4: conducto este, cabezas de sprinkler y pasos de risers. No se ha construido ningún patinillo ni se ha tocado la arquitectura.

### Alcance

- **S-10 — cerrado en P0b.4, sin geometría nueva.** El conducto HVAC ya tiene sleeves este/oeste (`P0B4_SLEEVE_HVAC_W/E`) y 4 difusores (`P0B4_GRILLE_01..04`, x43/48/53/58). El extremo oeste sigue sin patinillo: es la deuda pendiente de §6 y no se construye sin aprobación.
- **S-11 — conducto este unificado.** Los cuatro tramos cuadrados de 12 triángulos (`KIT_PILOT_Z10_Conduit_00/01/03/04`) se sustituyeron por cuatro tramos cilíndricos de 24 lados y r0,035 m, a x61,78 / z3,15, con manguitos en los extremos y bridas de pared en y8/y30. Se añadieron 4 cajas de unión (0,16 × 0,14 × 0,14 m) en y12/16/24/28, con tapa oscura y 4 tornillos. Los tramos cilíndricos que ya existían (`KIT_PILOT_Z10_Conduit_02`, `P0B4_CONDUIT_E_DOOR`) se conservan. Objeto: `P0B5D_CONDUIT_EAST`.
- **S-12 — cerrado en P0b.4.** Los dos sleeves huérfanos de x61,8 se retiraron a `Z10_RETIRED_P0B4`; no hay tubo suelto.
- **S-13 — cerrado en P0b.4.** La bandeja oeste ya tiene sleeves en y8/y30 (`P0B4_TRAY_SLEEVES`) y soportes cada ~3 m; no se añadió geometría. Revisión visual en `docs/fm_p0b4_z10_detail.png`.
- **S-14 — 12 cabezas completas.** Los 4 heads de P0B4 solo contenían cuerpo/deflector/bulbo y flotaban 0,65 m bajo la línea, sin tubo de bajada. Se extrajo una cabeza completa de `P0B_SPRINKLER_HEADS` (drop + cuerpo + deflector + bulbo) y se duplicó a 4 posiciones principales (x43/47/51/59, y17) y 8 de ramal (x45/55, y10/14/24/28). Objeto: `P0B5D_SPRINKLER_HEADS`; el antiguo `P0B4_SPRINKLER_HEADS` se retiró. Cada cabeza lleva dos varillas de unión de r2,5 mm × 14 mm (24 en total) que conectan el deflector con el cuerpo y eliminan la pieza flotante detectada por QA (+672 tris).
- **S-15 — pasos de riser completos.** Las 6 placas de paso ya existían (z0,006 y z3,986) y se conservan. Se añadieron 6 prolongaciones de tubo (z3,98..4,185), 6 sleeves (r0,036/0,042, z3,965..4,185), 6 collares de firestop (r0,042/0,045, z3,945..4,000) y 6 etiquetas de válvula a z1,36 (placa de aluminio, banda azul y alambre al volante). Las etiquetas de A miran +X y las de B −X para no chocar con la columna de x55,775. Objetos: `P0B5D_RISER_SLEEVES`, `P0B5D_RISER_TAGS`.
- **Nota de cota:** las prolongaciones terminan en z4,185, por debajo de la cara superior del forjado (4,19), para no atravesar el nivel superior.

### Objetos nuevos

| Objeto | Tris | Verts | BBox |
|---|---:|---:|---|
| `P0B5D_CONDUIT_EAST` | 8.360 | 4.256 | `(61,687, 8,000, 3,080)..(61,860, 30,000, 3,220)` |
| `P0B5D_SPRINKLER_HEADS` | 12.576 | 6.432 | `(42,957, 9,957, 3,176)..(59,043, 28,043, 3,900)` |
| `P0B5D_RISER_SLEEVES` | 5.256 | 2.640 | `(46,226, 15,756, 3,945)..(55,775, 24,245, 4,185)` |
| `P0B5D_RISER_TAGS` | 456 | 264 | `(46,344, 15,775, 1,344)..(55,656, 24,225, 1,472)` |

Total nuevo: 26.648 tris / 13.592 verts. Retirados: 4 tramos cuadrados (48 tris) y `P0B4_SPRINKLER_HEADS` (3.088 tris) → 3.136 tris. Neto: **+23.512 tris**.

### QA

- `docs/fm_p0b5d_qa.json` (QA propio del script): `qa_pass: true`; los 4 objetos con 0 aristas no-manifold, 0 caras degeneradas y UV presente.
- `blender-asset-qa` (perfil `game`): `pass: false` solo por 4 entradas de normales invertidas (conducto 4, cabezas 25, sleeves 7, etiquetas 9). La comprobación definitiva por islote con `bmesh.calc_volume(signed=True)` da **0 islotes negativos** en 38/72/18/18 islotes (volúmenes mínimos 4,29e-7 / 2,47e-7 / 3,68e-5 / 6,20e-7): es un falso positivo del heurístico sobre kitbash solapado. No se voltearon normales. Z-fighting y piezas flotantes: vacíos. Advertencias aceptadas: 48 vértices duplicados en el conducto, n-gons en tapas planas, caras ocultas back-to-back y `ground_z` 1,344 (etiquetas de servicio de techo).
- Materiales reutilizados: `M_FM_Metal_Panel`, `M_SH_Steel_Galv`, `M_SH_Firestop_Red`, `M_SH_Label_Aluminium`, `M_FM_Plastic_Blue`, `M_SH_Steel_Dark`, `M_SH_Steel_Stainless`, `M_SH_Sprinkler_Red`. Sin materiales nuevos.
- La etiqueta es geometría en blanco (sin texto): no se inventó tipografía ni una identificación funcional que no esté decidida.

### Renders de revisión

- `docs/fm_p0b5d_conduit_jb.png`: conducto redondo entrando en caja de unión gris con tapa y 4 tornillos; la mejor prueba de S-11. `docs/fm_p0b5d_conduit.png` es el plano general de la pared este y se conserva como contexto.
- `docs/fm_p0b5d_heads_wide.png`: línea principal y ramales con varias cabezas colgando bajo el conducto.
- `docs/fm_p0b5d_heads_close.png`: cabeza de ramal completa — escutcheon blanco, tubo de bajada rojo, cuerpo y deflector— unida al ramal. Las dos varillas de unión son sutiles a esta distancia. Prueba S-14.
- `docs/fm_p0b5d_riser_tags.png`: riser B con tres tubos, bridas, válvulas, volantes rojos y etiquetas a z≈1,36; el alambre queda embebido en la placa y no resulta intrusivo.
- `docs/fm_p0b5d_riser_sleeves2.png`: corte con los techos ocultos; tres sleeves, placa de paso y columna. El firestop es una banda roja oscura de 2,5 mm, sutil pero presente. `docs/fm_p0b5d_riser_sleeves.png` fue un primer intento cruzado por el ramal y queda superado.

### Exportación y Godot

- `assets/models/fm/z10_sector.glb` reexportado con `L1_P0B5D_Z10`: **516 objetos / 507 mallas / 402 únicas / 9 luces / 519.450 tris / 113.907.260 bytes (113,91 MB)**; bbox `(39,87, −2,00, −0,209)..(70,154, 34,939, 6,00)`, sin cambios.
- Frente a §5.10: **−1 objeto, −1 malla, −1 única, +23.512 tris, +783.692 bytes**. Cuadra con 4 objetos nuevos − 5 retirados y 26.648 − 3.136 tris.
- Godot tras `godot --headless --path . --import`: **`Z10_SECTOR_GODOT_OK`**, 507 `MeshInstance3D`, 402 mallas únicas, 9 luces, AABB pos `(39,87, −0,209, −34,939)` / tamaño `(30,284, 6,209, 36,939)`. Informe: `docs/fm_z10_sector_export.json`.
- Sigue siendo obligatorio reimportar después de sustituir el GLB; el caché antiguo da recuentos falsos.

### Limitaciones

- Sin texturas/bake ni desgaste fino; los materiales son los PBR planos existentes.
- El firestop es una banda delgada y oscura; se lee en corte, no en juego a distancia.
- El gate `blender-asset-qa` sigue marcando 4 entradas de normales invertidas; es un falso positivo del heurístico sobre kitbash solapado (volumen firmado positivo en todos los islotes). No se voltearon normales.
- La densidad de cabezas completa el trazado existente (12 en total, ~4 m entre principales y ramales); no es un cálculo hidráulico ni una cobertura densa de los 484 m². Se documenta como cierre de coherencia visual, no como diseño de extinción definitivo.
- El patinillo oeste del conducto sigue pendiente (§6) y no se ha construido.
- El GLB completo sigue pendiente de LOD/fusión/optimización antes de producción (113,91 MB).
- Backup: `docs/backups/FM_LEVEL1_V06_ARCH_before_p0b5d.blend`. **Sin commit.**

## 6. Patinillos: decisión pendiente

El usuario aprobó inicialmente el concepto de **patinillo técnico** para
recepción y Seguridad, pero después eligió **“Dejar pendiente”** la ubicación
y construcción. Por tanto **no se ha construido ningún patinillo** y no se
debe construir sin una nueva aprobación explícita. La propuesta queda
registrada solo como referencia:

### Patinillo de recepción

- Huella 1,20 × 1,20 m en el vestíbulo, esquina oeste: x −94,0..−92,8,
  y −8,0..−6,8. Deja 6,8 m libres del vestíbulo.
- Sube de z 0 a 5,4 m; puerta de registro cortafuego en el vestíbulo y
  registro superior en recepción.
- El ramal del corredor entra a z 3,55, sube a z 4,50 y sale al ducto de
  recepción (z 4,20..4,80) con sleeve y firestop.
- Impacto: nuevo volumen arquitectónico, collider, iluminación y posible
  conflicto con el cartel de entrada y la cámara de recepción. Requiere
  revisión de la puerta de 3,04 m y del techo de 3,20 m.

### Patinillo de Seguridad

- Huella 1,20 × 1,20 m en el extremo oeste del pasillo bajo, fuera del
  paso: x −71,0..−69,8, y 8,8..10,0. No invade el pasillo de 1,40 m.
- Sube de z 0 a 4,8 m; el ramal cruza el muro sur de Seguridad a z 3,55
  con sleeve y firestop.
- Alternativa: cámara técnica sobre el techo del pasillo (2,40..4,20 m).
  Requiere comprobar que el espacio es vacío y no estructural.

**No se ha construido ningún patinillo.** Cualquier propuesta de ubicación
debe revisarse antes de modificar la arquitectura, según AGENTS.md §30/§47.

## 7. Siguiente

1. **P0b.5c/P0b.5d — cerrados y validados:** las alimentaciones hero y el
   cierre S-10..S-15 quedan integrados en `z10_sector.glb`, que está en
   516 objetos / 507 mallas / 402 únicas / 9 luces / 519.450 tris /
   113,91 MB; Godot `Z10_SECTOR_GODOT_OK` con 507 mallas, 402 únicas y
   9 luces. El export sigue pendiente de LOD/fusión/optimización.
2. **Correcciones pendientes:** S-01/S-03/S-05..S-09/S-22/S-24 en
   Recepción/Seguridad. No construir patinillos sin nueva aprobación.
3. **Texturas, bake y desgaste fino:** convertir los materiales planos en
   sets PBR con desgaste, suciedad y señales de uso; después, narrativa
   ambiental (cuerpos, sangre, documentos, daños) con presupuesto medido.
4. **LOD, fusión y optimización:** reducir draw calls y tamaño del GLB
   (113,91 MB), medir en la GTX 1650 Ti y mantener los perfiles bajo/medio/
   alto/ultra.
5. **Biblioteca instanciada, pases hero de Recepción/Z10, export final y
   validación jugable en Godot.** **Sin commit.**


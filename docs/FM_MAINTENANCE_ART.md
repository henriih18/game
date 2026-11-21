# FRECUENCIA MUERTA — Mantenimiento (Nivel 1, Z07)

Estado: **vestido y verificado en Godot** (checkpoint local, sin commit).

## 1. Alcance

Se vistió la sala `SM_L1_Zone07_Maintenance_*` del máster V06 conservando
el blockout, los vanos, las 15 columnas y el conector norte hacia el
corredor. No se modificaron:

- `scenes/fm/level1_v06.tscn`
- `scenes/fm/level1.tscn` ni las escenas del vertical slice
- `fotos-referencia/`

La escena de sala `scenes/fm/fm_blockout_maintenance_art.tscn` se amplió
in situ: mantiene `MaintenanceSector`, `blockout_maintenance.glb` y
`Emerg_Maintenance` con su transform original, y añade el GLB de arte y
las luces de sala.

## 2. Composición

Planta 56 × 40 m, techo a 6 m (Blender x 56..112, y −48..−8; Godot
x 56..112, z 8..48). Caras interiores: norte y=−8,15; sur y=−47,85;
oeste x=56,15; este x=111,85.

- **Sala de calderas**: dos calderas verticales sobre plintos en (80, −25)
  y (92, −25), con cuerpo verde, puerta de registro, mirillas, gauges,
  escaleras, chimeneas hasta z 5,76, bridas y válvulas.
- **Bombas y agua**: dos skids de bombas en (86, −24,8) y (86, −31,3);
  tres tanques verticales de tratamiento en (74 / 80,6 / 87,2, −44,3) con
  escaleras, bridas y cubeto; receptor de aire junto al muro este.
- **Climatización y aire**: dos AHU en el muro este (108,5, −16,5 y −27)
  con conductos verticales; dos compresores y secador en la esquina suroeste.
- **Eléctrico**: seis cuadros en el muro norte (x 77..87; y −9,25),
  transformador (99,5, −12) y panel de breakers en el muro oeste.
- **Taller noroeste**: banco de trabajo, pegboard con herramientas, tres
  estanterías, carro, taburete, caja de herramientas y proyector de soldadura.
- **Estación química**: spill pallet con bidones, IBC, ducha y lavaojos,
  armario EPI, extintor y señalización.
- **Taller sureste**: banco con taladro de columna, estantería, cajas y
  taburetes.
- **Techo**: cabeceras de tuberías de vapor (roja), agua fría (azul),
  condensado (verde) y aire (amarilla) con soportes y bridas; bandejas
  portacables, conducto HVAC, monorriel sobre las calderas, nueve
  luminarias high-bay y balizas de emergencia.
- **Suelo y narrativa**: zócalo técnico, franjas de peligro, líneas de paso,
  rejillas de desagüe, charcos, aceite, óxido, trapos, tornillos caídos,
  quemadura, marcas de arrastre y un rastro de sangre sutil. Herramienta
  abandonada y evacuación interrumpida: horror ambiental sin armas ni
  combate.

Los pasillos x 66,15..72,85 y y −34,2..−37,8 quedan libres, igual que la
entrada norte (x 60..66) y la puerta este (z 36..40). Los muebles sólidos
generan colisión; las piezas decorativas usan los tokens de omisión de
`FMGLBCollision` (`TRIM`, `SIGN`, `LIGHT`, `CABLE`, `DECAL`, `DIS_WATER`,
`DIS_OIL`, `GRILLE`, `FLOOR_LINE`, `FLOOR_SIGN`, `PAPER`, `BLOOD`,
`WAINSCOT`). La sala suma **143 mallas visibles** y **102 colliders** en
el pase del smoke.

## 3. Archivos

| Archivo | Función |
|---|---|
| `nexus/nivel_01/FM_LEVEL1_V06_ARCH.blend` | máster V06 con la colección `L1_ART_MAINTENANCE` |
| `scripts/fm/fm_maintenance_build.py` | construcción idempotente del arte (104 objetos) |
| `scripts/fm/fm_maintenance_export_headless.py` | exportación, reducción de texturas y validación del GLB |
| `assets/models/fm/maintenance_art.glb` | GLB de arte (21,63 MB) |
| `docs/fm_maintenance_art_export.json` | informe de exportación |
| `scenes/fm/fm_blockout_maintenance_art.tscn` | escena de sala con blockout + arte + 20 luces |
| `tests/fm_level1_v06_maintenance_shots.gd/.tscn` | capturas de evaluación en `/tmp/opencode` |

Backup previo al arte:
`docs/backups/FM_LEVEL1_V06_ARCH_before_maintenance_art_2026-11-15.blend`
(md5 `cf3f45c90dec47256db0fe7139f6adf9`).

Checkpoint posterior:
`docs/backups/FM_LEVEL1_V06_ARCH_after_maintenance_art_2026-11-15.blend`
(md5 `e401ac4a3f2d63a2a6e19cc43b0eff0e`, idéntico al máster) y
`docs/backups/FM_MAINTENANCE_ART_checkpoint_2026-11-15.glb`
(md5 `6d8015e8ce38ee38bbaae28a03b07892`).

## 4. Datos técnicos

- 104 objetos de malla, 65.742 vértices, **98.458 triángulos**.
- GLB: **21.630.948 bytes**, 102 mallas, 104 nodos, 57 materiales,
  42 imágenes, 95.230 triángulos, 0 cámaras, 0 luces. PASS de validación.
- AABB Blender del arte: min (56,08, −47,97, 0,0), max (111,92, −7,769,
  5,94). Dentro de `MAINTENANCE_BOUNDS` (Godot x 55,85..112,18;
  y −0,2..6,0; z 4,0..48,15).
- La sala suma 143 mallas visibles (39 blockout + 104 arte) y 102 colliders.
- Luces de sala: `Emerg_Maintenance` (original) + 9 high-bay frías +
  1 cálida de calderas + 1 cálida de taller + 1 relleno de entrada +
  1 relleno de tanques + 1 relleno sureste + 1 relleno químico +
  4 balizas rojas = **20**. Sin sombras para rendimiento; la linterna del
  jugador conserva las suyas.
- Materiales: set plano `M_MT_*` (calderas, aislamiento, tuberías por
  servicio, gauges, emisivos, óxido, hollín, guantes) y reutilización de
  `M_FM_Steel_Dark`, `M_FM_Painted_Green`, `M_FM_Safety_Yellow`,
  `M_FM_Industrial_Red`, `M_FM_Hazard_Stripes`, `M_FM_Concrete_Floor`,
  `M_FM_Transformer_Green`, `M_Z10_HERO_Steel_Galv_2K`,
  `M_Z10_HERO_Steel_Dark_2K`, `M_Z10_HERO_Steel_Stainless_2K`,
  `M_HERO_Copper`, `M_FM_Brass`, `M_VEST_*` y etiquetas NEXUS.
- Presupuesto: 95,2k triángulos en el GLB para una sala técnica grande;
  las texturas 2K compartidas se reducen a 1K solo en la sesión de
  exportación (`downscale_images`), sin modificar el `.blend`.

## 5. QA y pruebas

- **blender-asset-qa** sobre los 104 objetos de arte + 13 mallas del shell
  Zone07 sin techo ni puertas + 15 columnas (132 objetos),
  `profile=render`, `eps=0,002`, `tol=0,08`, `no_modifiers=True`:
  **PASS, 0 errores**, 126 avisos aceptados (UVs de textos/decales,
  winding en cilindros y columnas sin UV).
- Se corrigieron solapamientos en AHU, skids de bombas, taburetes,
  extintores, bandejas de cables, monorriel, banco sureste, wainscot sur,
  apliques y etiquetas de tubería. Se sustituyeron copias de props con
  defectos internos (`PROP_Z10_Stool`, `PROP_Z10_FireExtinguisher`,
  `R21A_FIX_BreakerPanel`) por versiones propias.
- `tests/fm_level1_v06_smoke.tscn`: **403 PASS / 0 FAIL**. Maintenance se
  actualizó a 143 mallas / 102 colliders y se permite que la sala tenga
  luces de arte además de `Emerg_Maintenance`.
- `tests/fm_level1_v06_gameplay.tscn`: **105 PASS / 0 FAIL**.
- `tests/fm_full_run.tscn`: **49 PASS / 0 FAIL**.
- `tests/fm_graphics_presets_smoke.tscn`: **194 PASS / 0 FAIL**.
- `tests/fm_level1_v06_perf.tscn`: **PASS** a 1280×720 tras el GLB final
  (7.011 frames en 13,01 s, `fps_avg=539,0`, `fps_min=89,0`,
  `fps_p1=268,8`, estable a 60 fps); 4,60 M triángulos, 103 luces,
  1.428 draws máx., 854,5 MB de texturas. Es el nivel completo, no una
  escena aislada.
- Capturas Godot:
  `/tmp/opencode/mt_godot_{entry,aisle_center,boilers,pumps,tanks,electrical,workshop,chemical,east_ahu,se_bench,lookback}.png`.

## 6. Limitaciones conocidas

- Algunos rótulos de pared vistos de canto o desde atrás se leen como
  paneles oscuros; no afectan a la navegación ni a las pruebas.
- El techo es muy oscuro en varias vistas; las tuberías y bandejas se leen
  sobre todo cerca de los high-bay. Es atmosférico y coherente con el resto
  del nivel.
- El GLB pesa 21,63 MB, dentro del límite de 30 MB del exportador. Nuevas
  salas deben vigilar el número de sets texturizados reutilizados.
- El test de rendimiento recorre Z10, Recepción, Seguridad, Corredor y
  Security Access; Mantenimiento no está en esa ruta, así que sus 95k
  triángulos no aparecen desglosados en `FM_L1V06_PERF_SECTOR`.
- Los vanos elevados del muro norte y oeste (z 1,25..6) no tienen acceso a
  nivel de suelo; se conservan como shafts/ventilaciones del shell.

## 7. Skills utilizadas

- `blender-core`: API 5.2, data API/bmesh, escala y verificación.
- `blender-hardsurface-modeling`: bevel, normales, juntas a tope y presupuesto.
- `blender-pbr-materials`: metallic/roughness, color spaces y glTF.
- `blender-lighting-lookdev`: composición de luz interior y cámaras.
- `blender-texturing`: criterio de desgaste, óxido, grime y decales.
- `blender-scene-setup`: colecciones, nombres, escala y limpieza.
- `blender-asset-qa`: z-fighting, islas, normales, UVs y validación final.
- `blender-game-optimization`: presupuesto de tris, materiales, texturas y
  draw calls; decisión de reducir texturas compartidas a 1K en el GLB.
- `blender-export-pipelines`: checklist glTF/Godot, triangulación, normales,
  materiales y verificación posterior a la exportación.

No se usaron `blender-texture-baking` ni `blender-rendering` porque no se
horneó ni se renderizó en Blender para la entrega: el detalle viene de
geometría y materiales existentes, y las capturas de evaluación se hicieron
en Godot, que es el objetivo real de look.

## 8. Actualización MEP (2026-11-16)

Se añadió `MT_E2_TrayLink_CABLE`, un ramal de bandeja que sube desde la
bandeja sur en y−45.85 hasta la salida E2 en y−38.0 y cruza el muro x112 con
sleeve. Queda alineado con `ST_E2_TrayLink_CABLE` a z4.55. QA subset PASS 0
(134 objetos). Datos actualizados: **106 objetos, 99.098 tris, 21.677.968
bytes**; escena 145 mallas y 102 colliders. Smoke 403/0.

## 9. Siguiente sala

Oficinas / Administración (Z08), manteniendo el mismo flujo: diagnóstico
del shell, colección de arte propia, QA, GLB validado, escena ampliada in
situ, recuentos de smoke, pruebas completas, capturas y checkpoint sin
commit.

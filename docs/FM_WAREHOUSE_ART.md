# FRECUENCIA MUERTA — Almacén / Suministros (Nivel 1, Z06)

Estado: **vestido y verificado en Godot** (checkpoint local, sin commit).

## 1. Alcance

Se vistió la sala `SM_L1_Zone06_Warehouse_*` del máster V06 conservando el
blockout, los vanos, las columnas y la conexión transitable con Z10
(`ServiceLink`, x 62..70). No se modificaron:

- `scenes/fm/level1_v06.tscn`
- `scenes/fm/level1.tscn` ni las escenas del vertical slice
- `fotos-referencia/`

La escena de sala `scenes/fm/fm_blockout_warehouse_art.tscn` se amplió in
situ: mantiene `WarehouseSector`, `blockout_warehouse.glb` y
`Emerg_Warehouse` con su transform original, y añade el GLB de arte y las
luces de sala.

## 2. Composición

Planta 40 × 30 m, techo a 5,89 m, muros de 6 m (Blender x 70..110,
y 8..38; Godot x 70..110, z −38..−8). Caras interiores: sur y=8,15;
norte y=37,85; oeste x=70,15; este x=109,85.

- **Almacenaje**: cinco racks paletizados en el muro norte (x 81,4 / 84,3 /
  87,2 / 90,1 / 93,0; y 36) y tres en el muro este (x 108,55; y 19,6 / 22,6 /
  25,6), con tres niveles, palets, cajas de cartón, totes y film. Montantes
  azules, vigas naranjas, pies, arriostramientos y placas de apoyo.
- **Carga y logística**: transportador de rodillos en el vano sur
  (x 94,5; y 9,55), mesa de embalaje con báscula, impresora, portapapeles y
  pegboard (x 87,2; y 8,92), isla de staging central (x 96,5; y 30,5),
  carretilla amarilla (x 78,5; y 30,5), transpaleta, carro de almacén,
  carro volcado, bobina de cable, palets y cajas sueltas.
- **Seguridad**: jaula de malla en la esquina noreste (x 104,2..107,8;
  y 33,2..36,4) con puerta, candado y contenido paletizado; extintores,
  etiquetas de alta tensión, señal de no fumar y salidas.
- **Zócalo y señalización**: zócalo metálico corrugado de 2,2 m en los
  cuatro muros, franja de peligro amarilla, rótulos `ALMACÉN`,
  `SUMINISTROS`, `CARGA`, `SALIDA`, `PASILLO A/B` y numeración de racks.
- **Techo**: tres vigas I, conducto HVAC con rejillas, bandeja portacables,
  rociadores, polipasto, ocho luminarias high-bay y tres balizas de
  emergencia.
- **Suelo y narrativa**: líneas peatonales y de carretilla, cuadros de
  staging, flechas, rejillas de desagüe, charcos, aceite, papeles, film,
  palet roto y marcas de neumático. En la esquina sureste, un bulto cubierto
  con un rastro de sangre sutil: evacuación interrumpida, horror ambiental
  sin armas ni combate.

Los vanos sur, este y oeste quedan libres, igual que los pasillos entre
columnas. Los muebles sólidos generan colisión; las piezas decorativas usan
los tokens de omisión de `FMGLBCollision` (`TRIM`, `SIGN`, `LIGHT`, `CABLE`,
`DECAL`, `PUDDLE`, `BLOOD`, `GRILLE`, `FLOOR_LINE`, `WAINSCOT`). La sala
suma **132 mallas visibles** y **79 colliders** en el pase del smoke.

## 3. Archivos

| Archivo | Función |
|---|---|
| `nexus/nivel_01/FM_LEVEL1_V06_ARCH.blend` | máster V06 con la colección `L1_ART_WAREHOUSE` |
| `scripts/fm/fm_warehouse_build.py` | construcción idempotente del arte (88 objetos) |
| `scripts/fm/fm_warehouse_export_headless.py` | exportación, reducción de texturas y validación del GLB |
| `assets/models/fm/warehouse_art.glb` | GLB de arte (20,09 MB) |
| `docs/fm_warehouse_art_export.json` | informe de exportación |
| `scenes/fm/fm_blockout_warehouse_art.tscn` | escena de sala con blockout + arte + 15 luces |
| `tests/fm_level1_v06_warehouse_shots.gd/.tscn` | capturas de evaluación en `/tmp/opencode` |

Backup previo al arte:
`docs/backups/FM_LEVEL1_V06_ARCH_before_warehouse_art_2026-11-15.blend`
(md5 `9023bf6edbe602813f1c7f67dd6ae9a7`).

Checkpoint posterior:
`docs/backups/FM_LEVEL1_V06_ARCH_after_warehouse_art_2026-11-15.blend`
(md5 `cf3f45c90dec47256db0fe7139f6adf9`, idéntico al máster) y
`docs/backups/FM_WAREHOUSE_ART_checkpoint_2026-11-15.glb`
(md5 `0d0555191eeee17fe65f2da98a9d0897`).

## 4. Datos técnicos

- 88 objetos de malla, 85.269 vértices, **141.468 triángulos**.
- GLB: **20.093.588 bytes**, 84 mallas, 88 nodos, 44 materiales, 31 imágenes,
  137.808 triángulos, 0 cámaras, 0 luces. PASS de validación.
- AABB Blender del arte: min (69,9, 8,14, 0,0), max (109,87, 37,833, 5,9).
  Dentro de `WAREHOUSE_BOUNDS` (Godot x 62..110,18; z −38,15..−4).
- La sala suma 132 mallas visibles (44 blockout + 88 arte) y 79 colliders.
- Luces de sala: `Emerg_Warehouse` (original) + 8 high-bay frías + 3 balizas
  rojas + 1 cálida de embalaje + 1 cálida de staging + 1 relleno de entrada
  = **15**. Sin sombras para rendimiento; la linterna del jugador conserva
  las suyas.
- Materiales: set plano `M_WH_*` (racks azul/naranja, film, totes, líneas,
  emisivos, carretilla) y reutilización de los sets texturizados
  `M_FM_Cardboard`, `M_FM_Workbench_Wood`, `M_FM_Metal_Panel`,
  `M_FM_Painted_Green`, `M_FM_Steel_Dark`, `M_FM_Safety_Yellow`,
  `M_FM_Plastic_Blue`, `M_FM_Rubber`, `M_FM_Concrete_Floor`,
  `M_Z10_HERO_Steel_Galv_2K`, `M_Z10_HERO_Steel_Dark_2K`,
  `M_VEST_Paper`, `M_VEST_Red`, `M_VEST_Emissive_Cool` y etiquetas NEXUS.
- Presupuesto: 137,8k triángulos de arte y 20 MB de GLB quedan dentro del
  objetivo de PC para una sala de servicio; las texturas 2K compartidas se
  reducen a 1K solo en la sesión de exportación (`downscale_images`), sin
  modificar el `.blend`.

## 5. QA y pruebas

- **blender-asset-qa** sobre los 88 objetos de arte + shell Zone06 sin techo
  ni puertas + 12 columnas (114 objetos), `profile=render`, `eps=0,002`,
  `tol=0,08`, `no_modifiers=True`: **PASS, 0 errores**, 112 avisos
  aceptados (UVs de textos/decales con solapamiento, vértices duplicados por
  conversión de fuentes y winding de algunos textos).
- Se corrigieron z-fighting en racks, jaula, transpaleta, estanterías,
  decales, HVAC y el contenido nuevo de la jaula; se sustituyeron copias de
  props con defectos internos (`PROP_Z10_Shelf_0`, `PROP_Z10_Pallet`) por
  versiones propias.
- `tests/fm_level1_v06_smoke.tscn`: **403 PASS / 0 FAIL**. Warehouse se
  actualizó a 132 mallas / 79 colliders y se permite que la sala tenga
  luces de arte además de `Emerg_Warehouse`.
- `tests/fm_level1_v06_gameplay.tscn`: **105 PASS / 0 FAIL**.
- `tests/fm_full_run.tscn`: **49 PASS / 0 FAIL**.
- `tests/fm_graphics_presets_smoke.tscn`: **194 PASS / 0 FAIL**.
- `tests/fm_level1_v06_perf.tscn`: **PASS** a 1280×720 tras el GLB final
  (7.045 frames en 13,01 s, estable a 60 fps); 4,41 M triángulos, 84 luces,
  1.428 draws máx., 731,6 MB de texturas. Es el nivel completo, no una
  escena aislada.
- Capturas Godot:
  `/tmp/opencode/wh_godot_{entry,aisle_center,racks_north,forklift,packing,staging,security_cage,east_racks,lookback}.png`.

## 6. Limitaciones conocidas

- El techo es muy oscuro en varias vistas; las vigas y bandejas se leen
  sobre todo cerca de los high-bay. Es atmosférico, pero se puede subir el
  rebote o añadir una luz tenue de techo si se aprueba.
- El film de palets se ve ligeramente lechoso por el material translúcido;
  cumple su función de lectura y no se ha forzado más transparencia.
- La jaula de seguridad está poblada, pero su interior queda en penumbra;
  una luminaria interior dedicada mejoraría la lectura sin cambiar el
  layout.
- El GLB pesa 20,09 MB, cerca del límite de 30 MB del exportador. Nuevas
  salas deben vigilar el número de sets texturizados reutilizados.
- El test de rendimiento recorre Z10, Recepción, Seguridad, Corredor y
  Security Access; Almacén no está en esa ruta, así que sus 141k triángulos
  no aparecen desglosados en `FM_L1V06_PERF_SECTOR`.

## 7. Skills utilizadas

- `blender-core`: API 5.2, data API/bmesh, escala y verificación.
- `blender-hardsurface-modeling`: bevel, normales, juntas a tope y presupuesto.
- `blender-pbr-materials`: metallic/roughness, color spaces, alpha y glTF.
- `blender-lighting-lookdev`: composición de luz interior y cámara.
- `blender-texturing`: criterio de desgaste/grime y decales de suelo.
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

Se añadió `WH_E1_TrayLink_CABLE`, un ramal de bandeja que baja desde la
bandeja principal en y22.75 hasta la salida E1 en y12.25 y cruza el muro
x110 con sleeve. Queda alineado con `ST_E1_TrayLink_CABLE` a z4.50. QA
subset PASS 0 (116 objetos). Datos actualizados: **90 objetos, 142.488 tris,
20.166.532 bytes**; escena 134 mallas y 79 colliders. Smoke 403/0.

## 9. Siguiente sala

Mantenimiento (Z07), manteniendo el mismo flujo: diagnóstico del shell,
colección de arte propia, QA, GLB validado, escena ampliada in situ,
recuentos de smoke, pruebas completas, capturas y checkpoint sin commit.

## 10. Mezzanine de supervisión (2026-11-16)

Se añadió una plataforma elevada de 6 × 6 m a cota 2,60 m en el hueco
central (x 87,6..93,6 / y 27,6..33,6), con rampa de 1,5 × 5,2 m, barandilla,
puesto de supervisión y señalización. El arte pasa a **99 objetos, 93.783
vértices y 151.004 tris**; el GLB a **20.577.408 bytes, 95 mallas / 99
nodos y 147.344 tris**. QA subset de 125 objetos: **PASS 0 errores, 120
warnings**. Escena: 143 mallas, 84 colliders y 18 luces. Smoke 412/0,
gameplay 108/0, full 49/0, presets 194/0, alt routes 73/0 y perf
1280×720 PASS (482,9 fps medios). La navegación usa `NavLink_Mezzanine`
para unir el final de la rampa con la plataforma. Ver
`docs/FM_MEZZANINE_ART.md`.

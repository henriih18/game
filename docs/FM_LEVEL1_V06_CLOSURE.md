# FRECUENCIA MUERTA — Cierre de vestido del Nivel 1 V06

Fecha: 2026-11-16
Rama: `frecuencia-muerta`
HEAD: `287b101`
Estado: **nueve salas blockout vestidas y verificadas**. Sin commit.

## Alcance

Se completó el vestido artístico de las nueve salas blockout del Nivel 1 V06,
manteniendo el blockout y la navegación existentes:

- Vestuarios (Z05).
- Control de Acceso (Z04).
- Almacén / Suministros (Z06).
- Mantenimiento (Z07).
- Oficinas / Administración (Z08).
- Aseo de planta (Z09).
- Escaleras principales (Z11).
- Escalera de emergencia E1 (Z12a).
- Escalera de emergencia E2 (Z12b).

Cada sala conserva su escena blockout y su luz de emergencia original. El arte
se añade como GLB independiente dentro de la misma raíz de sector. No se
modificó `scenes/fm/level1_v06.tscn`, las escenas del slice ni
`fotos-referencia/`.

## Resumen por sala

| Sala | Objetos | Tris | GLB | Luces | Mallas escena | Colliders |
|---|---:|---:|---:|---:|---:|---:|
| Vestuarios (Z05) | 106 | 51.050 | 5,97 MB | 13 | 131 | 104 |
| Control de Acceso (Z04) | 72 | 17.456 | 1,42 MB | 13 | 98 | 70 |
| Almacén / Suministros (Z06) | 88 | 137.808 | 20,09 MB | 15 | 132 | 79 |
| Mantenimiento (Z07) | 104 | 95.230 | 21,63 MB | 20 | 143 | 102 |
| Oficinas / Administración (Z08) | 262 | 178.810 | 9,72 MB | 25 | 292 | 167 |
| Aseo de planta (Z09) | 25 | 16.188 | 1,64 MB | 14 | 39 | 20 |
| Escaleras Main / E1 / E2 | 44 | 24.954 | 4,03 MB | 21 | 162 | 119 |
| **Total arte de salas** | **701** | **521.496** | **64,50 MB** | **121** | **997** | **661** |

Los conteos de luces incluyen la luz de emergencia original de cada escena.

## Estado global de la escena

Medido con `tests/fm_level1_v06_perf.tscn` a 1280×720:

- **5.032.386 tris**, 4.500 mallas, 7.164 superficies, 4.296 mallas únicas.
- **743 materiales**, 5.614 recursos, 6.336 nodos, 17.246 objetos.
- **158 luces** (155 omni, 3 spot), solo 2 con sombras.
- **1.434 collision shapes**, 32 static bodies, 3 áreas.
- Navmesh: 1.943 polígonos principales y 8 de servicio; 4 puertas.
- VRAM: **967,9 MB de texturas**, 1.275,1 MB de vídeo, 348,1 MB estáticos.
- Sin huérfanos de recursos.

## Pruebas de cierre

Ejecutadas el 2026-11-16 tras importar el proyecto:

| Prueba | Resultado |
|---|---|
| `tests/fm_level1_v06_smoke.tscn` | **403 PASS / 0 FAIL** |
| `tests/fm_level1_v06_gameplay.tscn` | **105 PASS / 0 FAIL** |
| `tests/fm_full_run.tscn` | **49 PASS / 0 FAIL** |
| `tests/fm_graphics_presets_smoke.tscn` | **194 PASS / 0 FAIL** |
| `tests/fm_level1_v06_perf.tscn` 1280×720 | **PASS** |

Perf: 7.188 frames en 13,01 s, **552,6 fps medios**, mínimo 186,6, p1 277,9,
p99 3,60 ms, máximo 5,36 ms. Cero frames por encima de 16,7 ms y de 33,3 ms.
1.428 draw calls máximos y 3.131.255 primitivas máximas.

## Calidad y verificación

- `blender-asset-qa` PASS con 0 errores en las siete entregas de arte.
- Los warnings restantes son aceptados: UVs solapadas o de área cero en
  textos/decales, vértices duplicados de conversión de fuente y winding
  inconsistente en algunas piezas cilíndricas.
- Los GLB se validaron sin cámaras, sin luces y con AABB dentro de los bounds
  de cada sector.
- Las rutas de puertas, mesetas, navmesh, colliders y pruebas de gameplay se
  mantuvieron verdes después de cada sala.
- Las capturas de revisión están en `/tmp/opencode/`:
  `vest_godot_*`, `ctrl_godot_*`, `wh_godot_*`, `mt_godot_*`, `of_godot_*`,
  `rs_godot_*` y `st_godot_*`.

## Backups

- Pre-Vestuarios: `docs/backups/FM_LEVEL1_V06_ARCH_before_vestuarios_art_2026-11-14.blend`.
- Post-Control: `docs/backups/FM_LEVEL1_V06_ARCH_after_control_art_2026-11-15.blend`.
- Pre/Post-Almacén: `docs/backups/FM_LEVEL1_V06_ARCH_before_warehouse_art_2026-11-15.blend`
  y `..._after_warehouse_art_2026-11-15.blend`.
- Pre/Post-Mantenimiento: `docs/backups/FM_LEVEL1_V06_ARCH_before_maintenance_art_2026-11-15.blend`
  y `..._after_maintenance_art_2026-11-15.blend`.
- Pre/Post-Oficinas: `docs/backups/FM_LEVEL1_V06_ARCH_before_offices_art_2026-11-15.blend`
  y `..._after_offices_art_2026-11-15.blend`.
- Pre/Post-Aseo: `docs/backups/FM_LEVEL1_V06_ARCH_before_restroom_art_2026-11-15.blend`
  y `..._after_restroom_art_2026-11-15.blend`.
- Pre/Post-Escaleras: `docs/backups/FM_LEVEL1_V06_ARCH_before_stairs_art_2026-11-15.blend`
  y `..._after_stairs_art_2026-11-15.blend`.
- GLB de checkpoint: `docs/backups/FM_STAIRS_ART_checkpoint_2026-11-15/` y los
  checkpoints individuales de cada sala.

El máster actual es `nexus/nivel_01/FM_LEVEL1_V06_ARCH.blend`
(md5 `9fd2fd6c95b9ec1f99a215490bab3ba4`, 85.220.582 bytes).

## Limitaciones conocidas

- La iluminación es deliberadamente desigual y oscura en zonas secundarias;
  varias salas dependen de la linterna para leerse por completo.
- No se ha hecho todavía un pase global de niebla volumétrica, color grading,
  reflejos ni postprocesado unificado entre salas.
- Los GLB nuevos no incluyen cadena de LOD; el rendimiento actual se apoya en
  el presupuesto de triángulos, el culling y las luces sin sombras.
- El peso de texturas es alto (967,9 MB). Hay margen de optimización mediante
  sets compartidos, atlas y compresión específica por plataforma.
- Solo dos luces proyectan sombras, una decisión de rendimiento para la
  GTX 1650 Ti objetivo.
- Quedan warnings de QA aceptados en textos, decales y cilindros.
- No hay commit: todos los cambios están en el árbol de trabajo.

## Siguiente fase recomendada

1. **Pase visual global**: niebla volumétrica, iluminación de transición entre
   salas, color grading, mojado y suciedad coherentes, revisión de encuadres.
2. **Optimización medida**: deduplicar materiales/texturas entre GLB, LODs para
   props grandes, presupuesto por sector y pruebas en el hardware objetivo.
3. **Integración jugable**: criaturas y percepción, propagación de sonido,
   extracción, escondites y cooperación, sin romper el arte ya cerrado.
4. **Commit autorizado** cuando el usuario lo indique.

## Skills usadas

`blender-core`, `blender-hardsurface-modeling`, `blender-pbr-materials`,
`blender-lighting-lookdev`, `blender-asset-qa`, `blender-texturing`,
`blender-scene-setup`, `blender-game-optimization` y
`blender-export-pipelines`.

No se usaron `blender-rendering` ni `blender-texture-baking`: las capturas se
hicieron en Godot y los materiales PBR se reutilizaron o se autorizaron como
planos/sets existentes.

## Reglas respetadas

- No se tocó `fotos-referencia/`.
- No se tocó `scenes/fm/level1.tscn` ni las escenas del slice.
- Se hizo backup antes de cada sala y antes de tocar GLB.
- Se mantuvieron los nodos, luces de emergencia y rutas exigidas por los tests.
- Sin commit hasta autorización del usuario.

## Actualización MEP (2026-11-16)

Se aplicaron las correcciones de coherencia MEP en seis salas: Almacén
(bandeja por ServiceLink con bajada, sleeve y resalte), Oficinas (bandeja
continua y sleeve), Aseo (bandeja, agua, desagüe, sumideros y extracción),
Mantenimiento (tomas/retornos de cubierta en sus AHU), Control (HVAC local
con AHU y difusores) y Escaleras Main (transición al HVAC del corredor).

En una segunda pasada se cerró el pendiente de E1/E2: `ST_E1_TrayLink_CABLE`
y `ST_E2_TrayLink_CABLE` conectan sus salas con `WH_E1_TrayLink_CABLE`
(Almacén) y `MT_E2_TrayLink_CABLE` (Mantenimiento) mediante bandejas,
sleeves, cables y colgantes. QA PASS 0 en los cuatro subsets.

Totales actualizados de arte de salas: **714 objetos, 535.460 tris de arte
(519.856 tris en GLB), 68.109.824 bytes (≈64,95 MiB), 121 luces, 1.006
mallas y 661 colliders**. La escena completa queda en 5.042.270 tris, 158
luces y 1.434 colliders. Pruebas: smoke 403/0, gameplay 105/0, full run
49/0, presets 194/0 y perf 1280×720 PASS (556,2 fps medios, mínimo 116,2,
p1 261,8, p99 3,82 ms). Backups pre/post en
`docs/backups/FM_MEP_before_2026-11-16/`,
`docs/backups/FM_MEP_after_2026-11-16/` y
`docs/backups/FM_E1E2_before_export_2026-11-16/`.

Pendiente menor: Vestuarios conserva rejillas pasivas; el AHU del Almacén se
representa como unidad de cubierta; no hay leyenda de medios ni normalización
completa de secciones.

## Actualización de conectividad (2026-11-16)

Se integró la red de rutas alternativas que ya existía en el máster y se abrió
el acceso principal de Seguridad:

- `alternate_routes.glb`: **86 mallas**, 1.032 tris, 104.816 bytes, 6
  materiales, 0 texturas. Incluye EastGallery, MaintCorridor, NorthGallery,
  OfficesCrawl, ReceptionStair, ServiceLoop y NWStair.
- `security_connector.glb`: 3 mallas, 36 tris, 5.016 bytes; conector principal
  Seguridad↔corredor.
- `security_sector.glb` reexportado: 530 objetos, 517 mallas únicas, 972.530
  tris, 46.378.168 bytes. Se retiró la cinta de la barrera sur (se conservan
  postes y carcasas) y se incluyeron los sets PBR de los props.
- `scenes/fm/fm_alternate_routes.tscn`: 27 luces de servicio; la red se
  instancia fuera de `Sectors`.
- Navegación: 8 `NavigationLink3D` de capa 1, incluidos el conector sur y la
  puerta norte de Seguridad.

Estado de escena tras la integración: **4.062.600 tris**, 4.225 mallas, 767
materiales, **185 luces**, **1.523 colliders**, 0 huérfanos, 1.090,6 MB de
texturas. Pruebas: smoke **407/0**, alt routes **73/0**, gameplay **105/0**,
full run **49/0**, presets **194/0**; perf 1280×720 **PASS** con 462,3 fps
medios, mínimo 141,1 y p99 5,55 ms.

Backups: `docs/backups/FM_CONNECTIVITY_before_2026-11-16/`,
`docs/backups/FM_SECURITY_CONNECTOR_before_2026-11-16/` y
`docs/backups/FM_CONNECTIVITY_after_2026-11-16/`.

### Arte de rutas alternativas (2026-11-16)

Se añadió `assets/models/fm/alternate_routes_art.glb` (**20 objetos**,
**38.632 tris**, 1.545.912 bytes, 7 materiales, 0 imágenes/cámaras/luces) y se
integró como `AlternateRoutesDressing` dentro de
`scenes/fm/fm_alternate_routes.tscn`. Contenido: conducciones con abrazaderas,
13 carteles con soporte embutido, 8 franjas de peligro, líneas de guiado,
4 charcos y 7 balizas con soporte. QA de 134 objetos: **PASS 0 errores**.
Los 13 carteles se verificaron en Godot, legibles y sin espejo.

Estado final de escena: **4.101.232 tris**, 4.245 mallas, 774 materiales,
**185 luces**, **1.523 colliders**, 0 huérfanos, 1.090,6 MB de texturas.
Pruebas: smoke **407/0**, alt routes **73/0**, gameplay **105/0**, full
**49/0**, presets **194/0**; perf 1280×720 **PASS** con **581,0 fps** medios,
mínimo 160,7, p1 236,5 y p99 4,23 ms.

Pendiente: ajuste de IA en Seguridad, verticalidad NWStair/StairsMain, pase
visual global y optimización medida de texturas/materiales/LOD. Ver
`docs/FM_ALTERNATE_ROUTES_ART.md`.

### Optimización medida (2026-11-16)

Se corrigió la fusión estática de Seguridad (`BoxMesh` con
`surface_get_format`): ~2.408 → ~1.500 draw calls en `security_access`.
Se limitaron 212 texturas 2K a 1024 px (VRAM 1.154,6 → 842,6 MB), se vistió
el shell de pasillos, conectores y escaleras con materiales triplanar
(`M_Shell_Wall`, `M_Shell_Floor`, `M_Shell_Ceiling`) y se añadió oclusión
estática del shell (91 mallas, 1.092 tris), que deja `security_access` en
1.275 draws y 2,88 M primitivas. La consolidación de materiales duplicados de
Seguridad (596 superficies remapeadas, 16 materiales deduplicados) reduce la
fusión de 393 a 260 nodos y `security_access` a **1.127 draws** (−11,6 %).

Estado final de escena: **5.093.746 tris**, 4.466 mallas, **710 materiales**,
**188 luces**, **1.529 colliders**, 0 huérfanos, 858,6 MB de texturas.
Pruebas: smoke **412/0**, alt routes **73/0**, gameplay **108/0**, full
**49/0**, presets **194/0**; perf 1280×720 **PASS** con **481,9–495,0 fps**
medios, mínimo 147,3, p1 225,3 y p99 4,44 ms (`security_access` 313,9–322,5
fps). Ver `docs/FM_OPTIMIZATION_PASS.md`.

### Capturas finales de conjunto (2026-11-16)

Se creó `tests/fm_level1_v06_final_shots.gd/.tscn`: cámara libre (fov 68,
near 0,04, far 140) con lámpara hija, HUD oculto y 17 vistas de conjunto a
1280×720. Las imágenes están en `/tmp/opencode/final_godot_<vista>.png` y el
contact sheet en `/tmp/opencode/final_godot_contact.png` (4 columnas).

Vistas: `z10_corridor`, `reception`, `security_interior`,
`security_connector`, `control_entry`, `vestuarios`, `warehouse_aisle`,
`warehouse_mezzanine`, `maintenance_boilers`, `offices_open`,
`offices_meeting`, `restroom`, `stairs_main`, `stairs_e1`, `stairs_e2`,
`maint_tunnel` y `north_gallery`.

Revisión: Control, Vestuarios, Almacén (nave y mezzanine), Calderas, Aseo,
Escaleras principal/E1/E2, Oficinas (planta abierta y reuniones) y las rutas
de servicio quedan legibles y con identidad propia. Z10 y el conector de
Seguridad quedan deliberadamente oscuros, coherentes con la iluminación de
emergencia y el tono de terror. No se modificó geometría, iluminación ni
materiales para estas capturas.

### Sala técnica NWStair (2026-11-16)

Se cerró el fondo de saco de la meseta inferior de NWStair con un espolón y
una sala técnica de 8×6 m a cota −4,5 (Opción B de la propuesta de
verticalidad; no se construyó el túnel de ≈167 m).

- Arte: **17 objetos, 44.191 vértices, 62.978 tris**, GLB
  `nwstair_service_art.glb` de **6.593.560 bytes**, 20 materiales, 21
  imágenes, 0 cámaras/luces.
- Contenido no narrativo con modelado realista: dos bombas centrífugas,
  cabeceras de agua/vapor, tres armarios eléctricos, bandeja de cables,
  banco con herramientas, extractor, desagüe, extintor y señalización
  funcional.
- QA: arte aislado **PASS 0 errores**; arte + shell NWStair (54 objetos)
  **PASS 0 errores**.
- Integración: `NwStairServiceArt` en `fm_alternate_routes.tscn`, 5 luces y
  `ALT_ROUTES_BOUNDS` ampliado a z −70,8. Colliders de rutas Alt: 91.
- Pruebas: smoke **412/0**, alt routes **73/0**, gameplay **108/0**, full
  **49/0**, presets **194/0**; perf 1280×720 **PASS** con 474,4 fps medios,
  mínimo 148,7 y p99 4,30 ms.
- VRAM de texturas: 919,7 MB (21 texturas nuevas a 1K).
- Ver `docs/FM_NWSTAIR_SERVICE.md`.

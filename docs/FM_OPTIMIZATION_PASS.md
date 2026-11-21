# FRECUENCIA MUERTA — Optimización medida del Nivel 1 V06

Fecha: 2026-11-16
Rama: `frecuencia-muerta` · HEAD `287b101` · sin commit

## 1. Alcance

Primera pasada de optimización medida sobre `scenes/fm/level1_v06.tscn`, sin
tocar geometría, GLB ni el máster de Blender. Se atacaron los tres puntos con
mayor impacto detectados en el cierre global y en el pase visual:

1. La fusión estática no funcionaba en Seguridad y dejaba el sector entero sin
   agrupar.
2. La VRAM de texturas superaba 1,1 GB, por encima del margen cómodo de la
   GTX 1650 Ti de 4 GB.
3. El shell blockout de pasillos, conectores y escaleras seguía siendo gris
   plano y visualmente ajeno al arte de las salas.

## 2. Fusión estática de Seguridad

**Causa.** `security_sector.glb` incluye `SecurityConnector_Ceiling` como
`BoxMesh`. El helper llamaba a `surface_get_format()` sobre
`instance.mesh`, método que solo existe en `ArrayMesh`. La excepción abortaba
`merge_sector()` para todo el sector, que quedaba con 534 mallas sueltas y
unos 2.408 draw calls.

**Corrección.** En `scripts/fm/fm_static_merge.gd`, antes de recorrer
superficies:

```gdscript
if not instance.mesh is ArrayMesh:
    result["skipped_meshes"] = int(result["skipped_meshes"]) + 1
    continue
```

**Resultado medido.**

| Métrica | Antes | Después |
|---|---:|---:|
| Draw calls en `security_access` | ~2.408 | ~1.500 |
| Nodos fusionados de Seguridad | 0 | 393 |
| Superficies de entrada | 1.268 | 1.268 |
| Superficies de salida | 1.268 | 393 |
| Mallas ocultas | 0 | 523 |
| Tiempo de fusión | — | 185 ms |

La fusión total de la escena queda en 1.816 nodos, 2.285 mallas ocultas y
4.870 superficies de entrada convertidas en 1.816 de salida.

Se probó `STATIC_MERGE_CELL_SIZE = 24.0` para agrupar más geometría. Empeoró
el culling (3,64 M primitivas visibles y ~211 fps en el acceso), así que se
revirtió a **16.0**.

## 3. Límite de tamaño de texturas

Se añadió `process/size_limit=1024` a:

- **208** archivos `.import` de texturas 2K bajo `assets/models/fm`.
- **4** texturas del set de shell en `assets/art/fm/z10_hero/surfaces`
  (`T_Z10_WALL_PLASTER_2K_BC/ORM`, `T_Z10_FLOOR_CONCRETE_2K_BC/ORM`).

Manifiesto de los archivos afectados: `/tmp/opencode/tex_size_limit_manifest.txt`.
Después se ejecutó `godot --headless --path . --import`.

| Métrica | Antes | Después |
|---|---:|---:|
| VRAM de texturas | 1.154,6 MB | 842,6 MB |
| VRAM de vídeo total | 1.445,1 MB | 1.137,4 MB |

La reducción es de ~312 MB. Los FPS no subieron de forma apreciable por este
cambio a 1280×720 (la escena no estaba limitada por VRAM en esa resolución),
pero el margen de memoria para la GPU objetivo mejora de forma clara.

## 4. Materiales del shell blockout

Nuevo `scripts/fm/fm_shell_materials.gd` (`class_name FMShellMaterials`).
Aplica `material_override` antes de la fusión estática, que respeta el
override. Las mallas del shell no tienen UVs, así que se usa proyección
triplanar en espacio de mundo (`uv1_world_triplanar`, escala 0,22–0,30).

| Material | Textura | Tinte | Roughness |
|---|---|---|---|
| `M_Shell_Wall` | wall plaster BC + ORM | (0,46 · 0,54 · 0,50) | 0,86 |
| `M_Shell_Floor` | floor concrete BC + ORM | (0,54 · 0,56 · 0,53) | 0,86 |
| `M_Shell_Ceiling` | wall plaster BC + ORM | (0,20 · 0,23 · 0,22) | 0,86 |

- Prefijos tratados: `SM_L1_Corridor_`, `SM_L1_Conn_`, `SM_L1_Stair_`,
  `SM_L1_Zone11_`, `SM_L1_Zone12`.
- El material se elige por el nombre del material original: muros
  `Wall_Corridor` / `Wall_Blockout`, suelo `Corridor_Floor`, techo
  `Ceiling_Blockout`.
- Peldaños, mesetas y marcos conservan su material original. Con la textura
  oscura los peldaños perdían legibilidad y solo se veían las bandas
  amarillas.
- Se omiten las mallas invisibles (copias ocultas del blockout).

Estadística de arranque:

```
FM_LEVEL1_V06_SHELL_MATERIALS wall=64 floor=10 ceiling=11 skipped=112
```

Integración en `scripts/fm/fm_level1_v06.gd`: `SHELL_MATERIALS` precargado,
`ENABLE_SHELL_MATERIALS := true` y llamada en `_ready()` tras
`_setup_security_hatch()` y antes de `_setup_static_merge()`.

Capturas revisadas: `st_godot_main_stairs.png` (peldaños legibles, paredes
verde-gris), `st_godot_connector.png` y `st_godot_main_entry.png` (pasillos
texturizados, ya no blancos de blockout; suelo oscuro húmedo y techo negro).
El rótulo `NO BLOQUEAR` se lee correctamente.

## 4.5. Oclusión estática

Godot no ocluye con los muros por sí solo: hacen falta `OccluderInstance3D`.
Se añadió `scripts/fm/fm_occluders.gd`, que construye un único
`ArrayOccluder3D` con los triángulos reales de muros, suelos y techos del
shell (no cajas envolventes), antes de la fusión estática.

```
FM_LEVEL1_V06_OCCLUDERS meshes=91 vertices=2184 triangles=1092 skipped=5
```

Se activó `rendering/occlusion_culling/use_occlusion_culling=true` en
`project.godot`. La comprobación A/B alternando el interruptor:

| Métrica en `security_access` | Sin oclusión | Con oclusión |
|---|---:|---:|
| Draw calls | 1.507 | **1.275** |
| Primitivas | 3.114.048 | **2.875.024** |
| fps medios (ronda A/B) | 569,8 / 565,4 | **577,7 / 585,6** |
| fps p1 | 277,2 / 274,6 | **278,6 / 282,7** |

La reducción es de **−15 % draw calls** y **−7,7 % primitivas**. No es un
cambio de milagro porque la escena no estaba limitada por triángulos, pero es
una ganancia estable y sin coste visual. Se compararon las vistas de Seguridad
con oclusión on/off: las diferencias de píxel son ruido de sombreado/AA
(entre 0 y ~20k píxeles de 921k) y no desaparece geometría visible.


## 4.6. Consolidación de materiales de Seguridad

`security_sector.glb` declara **123 materiales** para 1.216 primitivas. Muchos
son duplicados exactos o casi idénticos: aceros blancos, plásticos negros,
pinturas y sellos con el mismo albedrío y roughness. Se añadió
`scripts/fm/fm_security_materials.gd` (`class_name FMSecurityMaterials`), que
remapea las superficies a un material canónico ya presente en el sector antes
de la fusión estática. La fusión usa `get_active_material`, así que respeta el
`set_surface_override_material`.

Canónicos: blanco metal → `M_SH_Steel_Stainless`, blanco mate →
`M_SH_Paint_SecurityGreen`, negro mate → `M_R21B_Paint_Dark`, acero desnudo →
`M_R21B_Steel_Bare`, acero oscuro → `M_HERO_Steel_Dark`, verde →
`M_R21B_Paint_Green`, oliva → `M_R21B_Paint_Olive`, etiquetas →
`M_R21B_Sign_White`, hormigón → `M_R21B_Concrete`, placa de techo →
`M_HERO_Ops_CeilingTile`. Emisivos, cristales, teclas, bezel CRT, pantallas y
pinturas rojas/amarillas se mantienen separados.

```
FM_LEVEL1_V06_SECURITY_MATERIALS materials=122 surfaces=1307 remapped=596 deduped=16
```

La fusión de Seguridad baja de 393 a **260 nodos** (1.265 superficies de
entrada, 260 de salida, 520 mallas ocultas). El sector pasa de **1.275 a
1.127 draw calls** (−11,6 %). No reduce primitivas: se mantiene en ~3,0 M.

A/B visual con las vistas `security_access_out`, `security_booth`,
`security_connector`, `security_interior` y `security_south_door`: entre 0 y
23 píxeles cambiados de 921.600, máximo de diferencia 26 y media 0,00–0,42.
No hay diferencia perceptible. Se mantiene la consolidación por la reducción
de draw calls, aunque las variaciones de fps entre ejecuciones no permiten
atribuirle una ganancia de frames concluyente.

## 4.7. Auditoría del arte denso de Seguridad — decisión de calidad

Antes de reducir geometría se auditó el source de los props más pesados del
sector. El objetivo era distinguir detalle real de desperdicio, no bajar
triángulos por bajar.

| Objeto | Tris | Verts | Materiales | Islas | Aristas no manifold |
|---|---:|---:|---:|---:|---:|
| `R21C_LOCK_BankA/B` | 95.292 cada uno | 49.060 | 11 | 719 | 0 |
| `R21C_SHELF_Unit` | 37.116 | 19.018 | 12 | 237 | 0 |
| `R21A_RACK_Interior` | 22.876 | 11.920 | 11 | 267 | 0 |
| `R21C_CART_ToolCart` | 21.184 | 10.904 | 10 | 156 | 0 |
| `R21C_KEYS_KeyRack` | 19.028 | 9.774 | 11 | 153 | 0 |

Los cinco props están cerrados y limpios: no hay aristas no manifold ni
aristas sueltas. La densidad se concentra en detalle real:

- El banco de taquillas tiene 8 puertas, bisagras, tiradores, cerraduras,
  rejillas de ventilación con lamas individuales, patas y marcos. Las 719
  islas son piezas de herraje y lama, no geometría oculta.
- El 66 % de sus triángulos está en acero desnudo (`M_R21B_Steel_Bare`), el
  material de bisagras, marcos y rejillas; no es un material de relleno.
- La inspección visual aislada confirma silueta correcta, puertas
  entreabiertas, rejillas legibles y herrajes definidos. Es un hero prop de
  calidad; un decimate automático destruiría las lamas y las bisagras.

**Decisión:** no se reduce la geometría de LOD0. Se mantiene el modelo
completo y se apoya en la cadena de LOD automática del importador
(`meshes/generate_lods=true` en `security_sector.glb.import`). Si en el
futuro una plataforma exige un presupuesto menor, el camino correcto es
modelar LOD1/LOD2 autorados desde el source —silueta, puertas y rejillas
preservadas, herrajes simplificados— y hornear normales, no aplicar un
decimate global.

Esta decisión es deliberada: el Nivel 1 ya supera el objetivo de rendimiento
a 1280×720 y la prioridad es conservar la calidad de modelado.

## 5. Pruebas

| Prueba | Resultado |
|---|---|
| `tests/fm_level1_v06_smoke.tscn` | **412 PASS / 0 FAIL** |
| `tests/fm_level1_v06_gameplay.tscn` | **108 PASS / 0 FAIL** |
| `tests/fm_full_run.tscn` | **49 PASS / 0 FAIL** |
| `tests/fm_graphics_presets_smoke.tscn` | **194 PASS / 0 FAIL** |
| `tests/fm_level1_v06_alt_routes_smoke.tscn` | **73 PASS / 0 FAIL** |
| `tests/fm_level1_v06_perf.tscn` 1280×720 | **PASS** |

El check `blockout_duplicates_skipped_from_merge` se relajó de `== 5` a
`>= 5`: el Almacén ahora omite 9 mallas invisibles del shell además de las 5
copias de Z10. La visibilidad de las 5 copias se sigue comprobando por nombre
más arriba en el test.

## 6. Rendimiento final (1280×720, ventana)

Última ejecución:

```
FM_L1V06_PERF_RESULT label=1280x720 fps_avg=481.9 fps_min=147.3
  fps_p1=225.3 p99=4.44 ms over_16.7ms=0 over_33.3ms=0
FM_L1V06_PERF: PASS
```

| Fase | fps_avg | fps_min | Draws avg | Prims avg |
|---|---:|---:|---:|---:|
| `z10_objective` | 367,1 | 175,9 | 892 | 989.131 |
| `z10_gate` | 712,4 | 196,5 | 84 | 320.676 |
| `corridor` | 522,0 | 217,7 | 464 | 1.531.849 |
| `reception_marker` | 495,0 | 160,6 | 404 | 493.617 |
| `security_access` | 313,9 | 147,3 | 1.127 | 3.001.043 |

Ejecución completa con consolidación de materiales y oclusión activas.
Escena: 6.440 nodos, 4.466 mallas, 7.166 superficies, 5.093.746 triángulos,
4.262 mallas únicas, **710 materiales**, 188 luces (185 omni, 3 spot, 2 con
sombras), 1.529 colliders, 0 huérfanos. VRAM final: 858,6 MB de texturas y
1.153,4 MB de vídeo.

Comparación con la línea base del pase visual (misma resolución):

| Métrica | Pase visual | Optimización | Cambio |
|---|---:|---:|---:|
| fps medios | 474,0 | 481,9–495,0 | +2 a +4 % |
| fps mínimo | 124,5 | 147,3 | +18 % |
| fps p1 | 180,8 | 225,3 | +25 % |
| p99 | 5,53 ms | 4,44 ms | −20 % |
| `security_access` | 227,9 fps | 313,9–322,5 fps | +38 a +41 % |
| Draws en `security_access` | 2.408 | 1.127 | −53 % |
| Draws máx. globales | 1.508 | 1.154 | −23 % |

Las cifras varían entre ejecuciones por carga de CPU (Firefox, GNOME,
indexación). En la ronda final se midieron 481,9 y 495,0 fps medios y
313,9–322,5 fps en `security_access`. Se reporta la ejecución completa y se
evita presentar el número como garantía del juego final. La mejora sólida y
repetible es la de draw calls; la de frames es secundaria y depende del cuello
de botella de cada máquina.

## 7. Archivos

Modificados:

- `scripts/fm/fm_static_merge.gd` — guard para `PrimitiveMesh`.
- `scripts/fm/fm_level1_v06.gd` — materiales de shell, occluders, materiales
  de Seguridad y orden de arranque.
- `project.godot` — `occlusion_culling/use_occlusion_culling=true`.
- `tests/fm_level1_v06_smoke.gd` — check de duplicados `>= 5`.
- `tests/fm_level1_v06_connectivity_shots.gd` — vistas de Seguridad para
  verificar la oclusión.
- 212 archivos `.import` (208 de `assets/models/fm` + 4 del set de shell).
- `AGENTS.md` — estado de la fase.

Nuevos:

- `scripts/fm/fm_shell_materials.gd`.
- `scripts/fm/fm_occluders.gd`.
- `scripts/fm/fm_security_materials.gd`.
- `docs/FM_OPTIMIZATION_PASS.md` (este documento).

No se modificó ningún GLB, ningún `.blend`, `scenes/fm/level1_v06.tscn`,
`fotos-referencia/` ni `scenes/fm/level1.tscn`.

## 8. Limitaciones

- El shell usa solo albedo + ORM; el set no incluye mapa normal. La
  profundidad visual depende de la geometría y de la iluminación.
- Los peldaños y mesetas conservan el material claro de blockout por
  legibilidad; no están integrados en la paleta del shell.
- `security_access` sigue siendo la fase más pesada (~1.127 draws y 3,0 M
  primitivas). Su arte denso se auditó y se decidió **no reducir LOD0** por
  calidad de modelado; ver sección 4.7.
- La consolidación de materiales reduce draw calls, no primitivas, y su
  efecto en fps queda dentro del ruido de medición.
- La oclusión cubre solo el shell (muros, suelos y techos). Props grandes,
  racks y mobiliario no generan occluders propios.
- Se probó dejar fuera de la fusión los props pesados para conservar sus LODs
  importados: bajó triángulos un 18 %, pero subió draw calls un 9 % y no mejoró
  fps; se revirtió.
- Se probaron celdas de fusión de 32 y 64 m: 32 empató en fps con 16 m y 64 m
  empeoró el culling; se mantiene 16 m.
- No se configuraron LODs manuales: `project.godot` no define `mesh_lod` y el
  arte se sigue sirviendo con la cadena LOD del importador.
- Las mediciones son de la escena completa en 1280×720, no de una escena de
  prueba aislada.

## 9. Skills usadas

- `blender-core` — criterios de datos/recursos y verificación.
- `blender-game-optimization` — presupuestos, draw calls, VRAM y criterio de
  LOD/instancing.
- `blender-export-pipelines` — criterio de importación glTF/Godot y texturas.
- `blender-asset-qa` — criterios de revisión aplicados a las capturas.
- `level-design` — lectura de recorridos y del shell de pasillos/escaleras.
- `scenario-godot-3d-world` — importación, colisiones, navmesh y capturas.
- `writing-plans` — estructura de la fase y criterios de aceptación.

No se usaron `blender-hardsurface-modeling`, `blender-pbr-materials`,
`blender-texturing`, `blender-rendering` ni `blender-character-rigging`: esta
fase no creó geometría, materiales nuevos ni renders de Blender.

## 10. Siguiente paso

1. Capturas finales de conjunto y actualización de la documentación de
   cierre.
2. Si una plataforma futura exige menos presupuesto, modelar LOD1/LOD2
   autorados de los props de Seguridad desde el source, preservando silueta y
   herrajes.
3. Commit solo cuando el usuario lo autorice.

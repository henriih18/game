# FRECUENCIA MUERTA — Z10 paridad visual Godot R7

Fecha: 2026-11-10. Estado: **art scene R7 creada, capturada y medida; sin commit**. `fotos-referencia/` intacta.

Referencia aprobada: `docs/fm_z10_hero_beauty_r6.png` (Blender/Cycles, 1280×720, 256 spp, AgX).
Intento Godot: `docs/fm_z10_godot_parity_r7.png` (Godot 4.7.2, Vulkan Forward+, 1280×720).
A/B: `docs/fm_z10_godot_parity_r7_ab.png` (R6 izquierda, R7 derecha).

> **Actualización R8 (2026-11-10):** la dirección del usuario cambió Z10 a **solo luces de emergencia rojas y muy pocas** (Recepción queda como excepción con algo más de luz). R8 se implementó en `scenes/fm/fm_z10_art_r8.tscn`, conservando R7 para A/B. Capturas y mediciones en `docs/FM_Z10_GODOT_DARK_R8.md`.

## 1. Objetivo y alcance

Llevar el look del beauty R6 a una escena de arte Godot, **sin rehacer geometría ni el GLB**. El GLB R6 (`assets/models/fm/z10_sector.glb`, 144.619.328 B, 516/507/402/9, 519.450 tris) se carga tal cual. La escena añade únicamente environment, luces de escena, cámara y un decal de suelo; no modifica el GLB ni las UV.

La niebla, las area lights, el GI y el volumen del render R6 son de Cycles y **no viajan en glTF**. La escena Godot reconstruye la intención con un environment controlado, las luces del GLB reescaladas y un pequeño set de luces de bounce documentadas.

## 2. Escena y archivos

| Elemento | Ruta |
|---|---|
| Escena de arte | `scenes/fm/fm_z10_art_r7.tscn` |
| Script de configuración | `scripts/fm/fm_z10_art_r7.gd` |
| GLB cargado | `assets/models/fm/z10_sector.glb` |
| Post-import del desgaste | `scripts/fm/fm_z10_sector_post_import.gd` |
| Textura del decal de suelo | `assets/art/fm/z10_hero/decals/T_Z10_FLOOR_LABEL_10_CONECTOR_DE_SERVICIO.png` |
| Captura final | `docs/fm_z10_godot_parity_r7.png` |
| A/B | `docs/fm_z10_godot_parity_r7_ab.png` |

La escena contiene: `Z10Sector` (instancia del GLB), `WorldEnvironment`, `ArtCamera`, `Key` (spot), `Fill`/`Center`/`EastWash` (omni), `CeilingBounce`/`FloorBounce` (directionals), `FloorLabel` (Decal). El script configura en `_ready` las luces internas del GLB y verifica el material de desgaste.

> En el editor, las luces internas del GLB se ven con sus valores crudos (`range=4096`, energías 135–14.131) hasta ejecutar la escena. La configuración de la art scene es runtime; la captura y las mediciones se hacen con la escena ejecutándose.

## 3. Cámara

- Posición: `(46, 2, -18)` en Godot, equivalente a `(46, 18, 2.0)` en Blender.
- Objetivo: `(55.47, 2.87, -21.08)`; la dirección reproduce la rotación Blender `(95°, 0, -72°)`.
- FOV: **68.0° horizontal** (`keep_aspect = KEEP_HEIGHT`), 1280×720.
- **Nota de lente:** 24 mm sobre sensor de 36 mm son 73.7° horizontales. El primer pase a 73.7° abría más el encuadre que el beauty R6 (puerta más pequeña, más suelo vacío). Tras el A/B se fijó 68° (~26.5 mm eq.) para igualar el tamaño de puerta/columna del R6. Para paridad estricta de lente, cambiar `CAM_FOV` a `73.7` en `scripts/fm/fm_z10_art_r7.gd`.

## 4. Environment

| Ajuste | Valor |
|---|---|
| Fondo | `BG_COLOR` `(0.004, 0.005, 0.007)` |
| Ambient | `AMBIENT_SOURCE_COLOR` `(0.62, 0.52, 0.40)`, energía `0.12` |
| Tonemap | **AgX**, exposición `0.94`, contraste AgX `1.25` |
| Glow | activo, intensidad `0.30`, bloom `0.02`, umbral `1.0`, blend screen |
| Niebla volumétrica | activa, densidad **`0.018`**, albedo `(0.55, 0.62, 0.72)`, anisotropía `0.25`, longitud `64`, detalle `2`, GI inject `1.0`, ambient inject `0`, sky affect `0` |
| SSAO | activo, radio `1.2`, intensidad `1.2`, power `1.5`, light affect `0.1` |
| SSR | activo, 48 pasos, fade in/out `0.15`/`2.0`, tolerancia `0.2` |

**Exposición:** el beauty Blender usó `0.28 EV` (multiplicador 1.214). En Godot el balance se calibró por histograma contra R6, no por conversión directa: con las luces reescaladas y sin GI, el valor que iguala el frame es `0.94`. El resultado tonal es: media R7 `(69.6, 65.0, 60.8)` vs R6 `(68.6, 66.3, 64.9)`; mediana de luminancia **62 en ambos**; p10 `31` vs `17`; p90 `106` vs `120`.

**Niebla:** se probó primero `0.0035` (valor Blender). En Godot era prácticamente invisible a 20 m; se subió a `0.018` tras A/B. No es una conversión física de Cycles: es un valor de art scene para recuperar la profundidad atmosférica.

## 5. Luces

### 5.1. Luces del GLB reescaladas

El GLB importa 9 luces con `range=4096` y energías de `135.9` a `14.131.4` (valores glTF), que sobreexponen sin environment. La escena las reescala en runtime:

| Luz | Energía | Rango | Sombras | Color |
|---|---:|---:|---|---|
| `LIGHT_Z10_Point_01/02/03` | 1.2 | 8.5 | sí | `(0.84, 0.88, 1.0)` |
| `LIGHT_Z10_SouthSpill` | 0.8 | 7.0 | no | `(0.35, 0.55, 1.0)` |
| `LIGHT_Z10_WorkFill` | 1.5 | 7.0 | no | `(1.0, 0.72, 0.42)` |
| `LIGHT_Z10_WorkSpot` | 2.0 | 10.0 | no | `(1.0, 0.78, 0.55)` |
| `LIGHT_Z10_Emergency_E` | 1.6 | 5.5 | sí | `(1.0, 0.02, 0.01)` |
| `LIGHT_L1_Conector_E/N` | 0.1 | 4.5 | no | `(1.0, 0.05, 0.02)` |

### 5.2. Luces añadidas en la escena (no en el GLB)

Sustituyen parcialmente las area lights/GI de Cycles que no exportan. Son parte del art scene, no del asset:

| Nodo | Tipo | Posición / dirección | Energía | Función |
|---|---|---|---:|---|
| `Key` | Spot | `(48, 3.5, -16)` → `(62, 1.5, -21)`, 72° | 6.0 | clave cálida sobre muro este/puerta |
| `Fill` | Omni | `(55, 3.7, -25)`, rango 10 | 0.5 | relleno frío del fondo |
| `Center` | Omni | `(50, 2.9, -20)`, rango 18 | 0.4 | relleno general |
| `EastWash` | Omni | `(57, 2.6, -19)`, rango 9 | 1.5 | wash del muro este |
| `CeilingBounce` | Directional | rotación X `90°` (hacia arriba) | 0.30 | bounce de suelo al techo |
| `FloorBounce` | Directional | rotación X `-90°` (hacia abajo) | 0.15 | bounce de techo al suelo |

`Key` tiene sombras; `CeilingBounce`/`FloorBounce` no. Las sombras de `Point_01/02/03` y `Emergency_E` están activas.

## 6. Desgaste COLOR_0

El post-import `scripts/fm/fm_z10_sector_post_import.gd` sigue registrado en `assets/models/fm/z10_sector.glb.import` y activa `vertex_color_use_as_albedo=true` en `M_Z10_HERO_Sprinkler_Red_WEAR_2K`. La escena lo verifica al cargar:

```
Z10_ART_R7_WEAR vc=true node=P0B4_SPRINKLER_RUN_DN80
```

No se modificó el GLB ni el material importado.

## 7. Etiqueta de suelo (scene-only)

La etiqueta `ANNOT_L1_Label_09` de Blender ("**10 CONECTOR DE SERVICIO**", 14.15 × 0.77 m, en `L1_ARCH_LABELS`) no está incluida en el GLB exportado. Para recuperar parte de la narrativa del R6 se generó una textura RGBA 2048×256 desde esa geometría y se colocó un `Decal` de escena:

- Textura: `assets/art/fm/z10_hero/decals/T_Z10_FLOOR_LABEL_10_CONECTOR_DE_SERVICIO.png`.
- Decal: posición `(51, 0.5, -22)`, tamaño `(16, 2, 0.7)`, `modulate (0.70, 0.65, 0.50)`.
- **No está en el GLB**; es un añadido de la art scene. La posición/opacidad son una decisión artística R7 (el original está en `z=-19`; se desplazó para que no dominara el encuadre).
- El cartel "SERVICIO" sobre la puerta sí está en el GLB.

No se rehízo ninguna UV ni el GLB. Etiquetas/diales específicos restantes siguen pendientes para R8.

## 8. Captura y comparación

- `docs/fm_z10_godot_parity_r7.png`: 1280×720, Godot 4.7.2, Forward+, VSync off, 3 s de convergencia de niebla/SSR/sombras.
- `docs/fm_z10_godot_parity_r7_ab.png`: R6 y R7 lado a lado (2560×764).
- La captura usa la cámara de la escena y el environment embebido; no hay postproceso externo.

**Lectura visual honesta:** el tono global, la calidez, el rojo de emergencia, el techo claro y la bruma están mucho más cerca del R6 que el primer pase. El desgaste rojo se ve. Siguen diferencias: el muro este, el conducto y el pilar quedan más oscuros y planos que en Cycles; el techo está más liso (menos manchas/juntas); la puerta es casi negra; la niebla no produce los light shafts del volumen Cycles; el suelo conserva las manchas circulares de la textura R6 y el decal es más tenue que el texto original.

## 9. FPS y VRAM (escena estática, no gameplay)

Medición en ventana, GTX 1650 Ti, Vulkan Forward+, 1280×720, VSync off, 5 s:

| Métrica | Valor |
|---|---:|
| FPS medio | **197.2** |
| Frames / tiempo | 986 / 5.001 s |
| Textura VRAM | **362.9 MB** |
| Vídeo VRAM | **448.6 MB** |
| Objetos | 3117 |

Es una **escena estática de arte** con niebla volumétrica, SSAO, SSR y 5 luces con sombras. No incluye jugador, criaturas, físicas de gameplay, audio ni multijugador; **no representa el FPS del juego final**. El baseline R6 sin niebla/SSR/SSAO era 581.7 FPS; la caída es el coste esperado de los efectos, no una regresión del GLB. El aumento de VRAM frente al baseline (248.2/313.8 MB) es consistente con buffers de niebla/SSAO/SSR y shadow maps; **no se realizó una prueba de leak** en esta pasada.

## 10. Limitaciones

1. **No hay GI/area lights de Cycles en glTF.** La escena usa luces puntuales reescaladas y dos directionals de bounce; el resultado tiene menos bounce suave y más contraste duro en esquinas.
2. **El volumen de Blender no viaja.** La niebla Godot es froxel/volumétrica de Forward+; densidad `0.018` es una decisión artística, no una conversión de `0.0035`.
3. **El decal del suelo no está en el GLB.** Es scene-only; la etiqueta original sigue excluida del export.
4. **Lente:** 68° horizontal en la captura final; 24 mm estrictos serían 73.7° (ver §3).
5. **Etiquetas/diales específicos** restantes (más allá del decal de suelo) no se implementaron; requieren UV/decals por objeto o trabajo de textura y se dejan para R8.
6. **FPS medido en escena estática**, sin gameplay ni LOD; no usar como presupuesto final.
7. **Deuda geométrica global** del proyecto sigue existiendo (islas invertidas/z-fighting/flotantes preexistentes); este pase no la modifica.

## 11. Veredicto

**Aprobado como art scene R7 de paridad tonal/atmosférica:** el frame Godot iguala la media y la mediana de luminancia del beauty R6, recupera la calidez, el techo claro, la emergencia roja, la bruma y el desgaste, y se captura/mede de forma reproducible. **No aprobado como paridad pixel-perfect ni como gameplay:** faltan GI/área/volumen de Cycles, el muro este/ducto/pilar siguen más oscuros, el techo está más liso, la puerta es casi negra y la etiqueta de suelo es un decal scene-only.

## 12. Siguiente (R8, plan original)

- Decidir lente final (68° de composición vs 73.7° de 24 mm estricto) y fijar la cámara.
- Mejorar el bounce del muro este/ducto/pilar (probe GI bakeado o luces de bounce adicionales medidas) sin tocar el GLB.
- Afinar juntas/manchas del techo y la legibilidad del decal de suelo.
- Etiquetas/diales específicos restantes con decals/UV, sin rehacer el GLB.
- Pasar a gameplay (jugador, linterna, criatura, escondite) y medir FPS con esos sistemas; LOD solo con medición.

## 13. R8 — dirección oscura (implementado)

La dirección del usuario cambió el objetivo de iluminación: **Recepción es la excepción con algo más de luz; en Z10 y el resto solo luces de emergencia y muy pocas.** R8 se implementó como escena nueva (`scenes/fm/fm_z10_art_r8.tscn`, `scripts/fm/fm_z10_art_r8.gd`) conservando R7 para A/B.

- **Sin luces fijas añadidas:** el `.tscn` R8 no contiene ningún `Light3D` de escena. Se eliminaron `Key`, `Fill`, `Center`, `EastWash`, `CeilingBounce` y `FloorBounce`.
- **Solo 3 luces rojas del GLB:** `LIGHT_Z10_Emergency_E` (3.0/6.0, sombras), `LIGHT_L1_Conector_E/N` (0.30/3.5, sin sombras). Las otras 6 luces importadas se ocultan (`kept=3 disabled=6`).
- **Emisivos normales apagados:** 29 overrides de superficie en las 3 luminarias de techo y la lámpara de trabajo; el GLB no se modifica.
- **Environment:** exposición AgX **0.80**, ambient **0.020**, fondo casi negro, niebla 0.012, SSAO/SSR. Sin GI/ambient inject en la niebla.
- **Desgaste:** `Z10_ART_R8_WEAR vc=true`.
- **Capturas:** `docs/fm_z10_godot_dark_r8.png` (escena real) y `docs/fm_z10_godot_dark_flashlight_r8.png` (linterna diagnóstica temporal, no guardada en la escena). A/B: `docs/fm_z10_godot_dark_r8_ab.png`.
- **FPS/VRAM:** **320.7 FPS** estáticos (1604 frames/5.002 s, 1280×720, VSync off, Forward+); **361.4 MB textura / 441.5 MB vídeo**. No es gameplay.
- **Veredicto:** cumple la dirección oscura de Z10; la habitación es casi negra con tres fuentes rojas de emergencia. La excepción de recepción queda fuera de esta escena y anotada para su pase propio.

Detalle completo en `docs/FM_Z10_GODOT_DARK_R8.md`.

Sin commit. `fotos-referencia/` intacta.

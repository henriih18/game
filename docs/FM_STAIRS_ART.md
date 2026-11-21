# FRECUENCIA MUERTA — Arte de Escaleras (Z11, Z12a, Z12b)

## Alcance

Vestido de los tres núcleos verticales del Nivel 1:

- **Escaleras principales (Z11)** — 24 peldaños, meseta inferior y conector norte.
- **Escalera de emergencia E1 (Z12a)** — salida junto a Almacén.
- **Escalera de emergencia E2 (Z12b)** — salida junto a Mantenimiento.

Se conserva el blockout y la luz de emergencia original de cada escena. El arte se añade como GLB independiente dentro de la misma raíz de sector, sin tocar `scenes/fm/level1_v06.tscn` ni las escenas del slice.

## Composición

### Escaleras principales

- Pasamanos inclinados en ambos lados de los 24 peldaños, con postes y anclajes.
- Barandillas de protección en los tres bordes del hueco y en la meseta inferior.
- Bandas antideslizantes amarillas en cada peldaño.
- Zócalo técnico verde-gris en muros y conector, con remate metálico.
- Luminarias de techo en el núcleo y lineales en el conector.
- Tuberías roja/azul, bandeja de cables y conducto de ventilación con soportes.
- Líneas de suelo, manchas de óxido, charcos, caballete de suelo mojado, cubo y extintores.
- Señalética: `ESCALERAS PRINCIPALES`, `NIVEL 1`, `NIVEL -1`, `SALIDA`, `NO BLOQUEAR`.

### Escaleras E1 / E2

- Pasamanos, barandillas de hueco y bandas antideslizantes en los 24 peldaños.
- Zócalos, líneas de suelo, tuberías y luminarias de techo.
- Manchas de óxido, charco en la meseta y extintor.
- Señalética de salida, emergencia y nombre de escalera.

## Archivos

| Archivo | Función |
|---|---|
| `scripts/fm/fm_stairs_build.py` | Build idempotente de las tres colecciones `L1_ART_STAIRS_MAIN/E1/E2` |
| `scripts/fm/fm_stairs_export_headless.py` | Export y validación de los tres GLB |
| `assets/models/fm/stairs_main_art.glb` | Arte de escaleras principales |
| `assets/models/fm/stairs_e1_art.glb` | Arte de E1 |
| `assets/models/fm/stairs_e2_art.glb` | Arte de E2 |
| `scenes/fm/fm_blockout_stairs_main_art.tscn` | Escena ampliada con `StairsMainArt` y luces |
| `scenes/fm/fm_blockout_stairs_e1_art.tscn` | Escena ampliada con `StairsE1Art` y luces |
| `scenes/fm/fm_blockout_stairs_e2_art.tscn` | Escena ampliada con `StairsE2Art` y luces |
| `tests/fm_level1_v06_stairs_shots.gd/.tscn` | Capturas de revisión |

## Datos técnicos

Build: **44 objetos, 24.954 tris**.

| Sector | Objetos | Tris | GLB | Mallas | Materiales | Imágenes |
|---|---:|---:|---:|---:|---:|---:|
| Main | 18 | 13.024 | 1.761.292 B | 18 | 16 | 10 |
| E1 | 13 | 5.710 | 1.224.456 B | 13 | 14 | 7 |
| E2 | 13 | 6.220 | 1.237.348 B | 13 | 14 | 7 |

GLB sin cámaras ni luces. AABB de los tres dentro de sus bounds:

- Main: min (−11,848, −49,848, −4,5), max (7,845, −4,4, 7,0).
- E1: min (110,43, 8,155, −4,496), max (119,845, 25,845, 5,99).
- E2: min (112,43, −43,846, −4,496), max (121,845, −26,155, 5,99).

## Iluminación y escena

- **Main:** 10 luces nuevas + `Emerg_StairsMain`. Cuatro luminarias de techo a z6, dos rellenos laterales y cuatro lineales en el conector.
- **E1:** 4 luces nuevas + `Emerg_StairsE1`. Dos de techo, relleno de meseta y entrada cálida.
- **E2:** 4 luces nuevas + `Emerg_StairsE2`. Mismo esquema que E1.

Todas sin sombras para mantener el presupuesto.

## QA

`blender-asset-qa` sobre el arte + shell de cada sector (sin techo, puertas ni anotaciones):

| Sector | Objetos QA | Resultado | Warnings |
|---|---:|---|---:|
| Main | 63 | PASS, 0 errores | 83 |
| E1 | 46 | PASS, 0 errores | 62 |
| E2 | 46 | PASS, 0 errores | 62 |

Warnings aceptados: UVs de textos/decales, duplicados de fuente y winding de cilindros.

## Pruebas

- Smoke `tests/fm_level1_v06_smoke.tscn`: **403 PASS / 0 FAIL**.
  - Main: 68 mallas, 51 colliders.
  - E1: 47 mallas, 34 colliders.
  - E2: 47 mallas, 34 colliders.
- Gameplay: **105 PASS / 0 FAIL**.
- Full run: **49 PASS / 0 FAIL**.
- Presets: **194 PASS / 0 FAIL**.
- Perf 1280×720 con ventana: **PASS** — 473,9 fps medios, mínimo 123,5, p1 209,3; 5.032.386 tris, 158 luces, 1.434 colliders, 967,9 MB de texturas.

## Limitaciones

- La iluminación de los núcleos es deliberadamente dura y contrastada; los laterales quedan en penumbra.
- El rótulo `NIVEL 1` se movió al muro sur para evitar el texto espejado del muro este.
- Los techos y anotaciones del shell no se incluyen en la QA por tener bounds locales no aplicados.
- No se modificó el shell ni la navegación; las mesetas y pasos conservan sus colliders originales.

## Skills usadas

`blender-core`, `blender-hardsurface-modeling`, `blender-pbr-materials`, `blender-lighting-lookdev`, `blender-asset-qa`, `blender-texturing`, `blender-scene-setup`, `blender-game-optimization`, `blender-export-pipelines`. No se usaron `blender-rendering` ni `blender-texture-baking` (capturas en Godot y materiales reutilizados).

## Backups

- Pre-Escaleras: `docs/backups/FM_LEVEL1_V06_ARCH_before_stairs_art_2026-11-15.blend` (md5 `9049fb058ef1b453494566371b84a9c9`).
- Post-Escaleras: `docs/backups/FM_LEVEL1_V06_ARCH_after_stairs_art_2026-11-15.blend`.
- GLB de checkpoint: `docs/backups/FM_STAIRS_ART_checkpoint_2026-11-15/`.

## Actualización MEP (2026-11-16)

Se añadieron bandejas de enlace en E1 y E2 para cerrar la conectividad de
servicios: `ST_E1_TrayLink_CABLE` (x115.1, z4.50) y `ST_E2_TrayLink_CABLE`
(x117.1, z4.55), con puente hasta el muro, sleeve, tres cables y colgantes.
Enlazan con `WH_E1_TrayLink_CABLE` y `MT_E2_TrayLink_CABLE`
respectivamente. QA subsets E1/E2 PASS 0 (47 objetos cada uno). Totales
actualizados: **46 objetos, 26.222 tris, 4.320.408 bytes** en los tres GLB.
Smoke final 403/0 con E1/E2 en 48 mallas y 34 colliders.

## Siguiente

Con Escaleras se completa el vestido de las nueve salas blockout del Nivel 1 V06. El siguiente paso es revisión global de escena, rendimiento y documentación de cierre, sin commit hasta autorización.

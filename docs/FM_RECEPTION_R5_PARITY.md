# FRECUENCIA MUERTA — Recepción R5: paridad con el Conector Z10

**Fecha:** 2026-11-08
**Archivo:** `nexus/nivel_01/FM_LEVEL1_V06_ARCH.blend`
**Escena:** `NEXUS_L1_V06_ARCH`
**Colección de paridad:** `L1_RECEPTION_R5`
**GLB:** `assets/models/fm/reception_r5.glb`

---

## 1. Objetivo

Llevar la recepción a la misma capa técnica y artística que el Conector Z10:
densidad de props industriales, servicios, señalización, QA y validación en Godot.
No se buscó duplicar el conteo exacto de mallas del Conector, sino igualar el
estándar de blockout validado.

## 2. Props industriales añadidos

Se reutilizaron diez props del Conector Z10, conservando materiales y escala:

- `PROP_REC05_ElectricalCabinet_A`
- `PROP_REC05_UtilityCabinet`
- `PROP_REC05_FireExtinguisher`
- `PROP_REC05_Bin_0`, `_1`
- `PROP_REC05_CableReel`
- `PROP_REC05_Crate_0`, `_1`
- `PROP_REC05_ToolCart`
- `PROP_REC05_SpillPallet`

Distribución:

- Muro oeste / espera: extintor, bins, cable reel.
- Muro este / seguridad y túnel: cabinet eléctrico, utility cabinet, tool cart,
  spill pallet, crates de extracción.
- La recepción conserva mostrador, seguridad, espera, taquillas, señalización,
  wayfinding, soffit, downlights y luces de emergencia de R1–R3.

Se retiraron props que no superaban QA o duplicaban detalle:
`FireHoseReel`, `Shelf`, `SchematicBoard`, `Pallet`, pedestal de control y
barrels. Quedan documentados como candidatos para una pasada de arte final.

## 3. QA Blender

- **R5QA3: PASS, 0 errores / 351 warnings aceptados.**
- **276 mallas** en R1+R2+R3+R5; escena **1.652 objetos**; `dirty=False`.
- Warnings: UV solapadas y caras internas back-to-back de piezas con materiales
  sólidos; no hay flotantes ni normales invertidas.

## 4. Renders

- `docs/fm_recepcion_r5_wide_wb.png`
- `docs/fm_recepcion_r5_desk_wb.png`
- `docs/fm_recepcion_r5_extraction_wb.png`

La recepción se lee más densa y funcional. La extracción conserva el cartel
DESCONTAMINACIÓN, la baliza roja, el aplique de emergencia y las bandas hazard.
La compuerta todavía se lee como un portal abierto, sin lamas cerradas.

## 5. GLB

- `assets/models/fm/reception_r5.glb` — **2.670.496 bytes (2,67 MB)**, WebP 80.
- **307 objetos** exportados.
- Confirmados **10 nodos `PROP_REC05_*`** en el JSON del GLB.
- `reception_r4.glb`: 311 nodos, 293 mallas, 0 nodos REC05.
- `reception_r5.glb`: 308 nodos, 292 mallas, 10 nodos REC05.
- Warnings: 2 luces AREA no soportadas por glTF; materiales con más de un nodo
  de textura usan el primero.

## 6. Validación Godot

Escena `scenes/fm/fm_reception_test.tscn`, GLB `reception_r5.glb`,
`FMPlayer`, `fm_glb_collision.gd`, Forward+, 1280×720, VSync off,
GTX 1650 Ti.

| Métrica | Resultado |
|---|---:|
| Mallas | 291 |
| Nodos | 308 |
| Colliders | 107 (3 trimesh) |
| Objetos | 488 |
| Carga GLB | 195 ms headless / 369 ms ventana |
| Movimiento | 6,80 m, `is_on_floor=true` |
| Linterna | on → off |
| Extracción | z = 39,46, `is_on_floor=true` |
| FPS promedio | **239,9** |
| FPS mínimo / máximo | 181 / 272 |
| Muestras | 776 |
| Draw calls | 29 |
| Primitivas | 15.528 |
| Objetos renderizados | 419 |

**`RECEPTION_AUTOTEST_OK`**.

Las 14 luces importadas del GLB se desactivaron porque sobreexponían la escena;
la iluminación del test usa omnis aproximadas, ya que glTF no exporta AREA lights.

## 7. Comparación con el Conector Z10

| Dato | Z10 | Recepción R5 |
|---|---:|---:|
| Mallas | 524 | 291 |
| GLB | 11,5 MB | 2,67 MB |
| Colliders | 249 (6 trimesh) | 107 (3 trimesh) |
| QA | PASS 0/191 | PASS 0/351 |
| FPS | 160,3 | 239,9 |
| Enfoque | Servicios y arquitectura industrial | Recepción, mobiliario, seguridad y extracción |

Ambos están en la misma **fase de blockout técnico/artístico validado**. La
recepción tiene menos mallas y servicios que el Conector, pero más mobiliario,
señalización y elementos de extracción. La paridad es de estándar y flujo de
trabajo, no de conteo exacto.

## 8. Limitaciones

1. La compuerta se lee como portal abierto; falta definir lamas/estado final.
2. La iluminación en Godot es aproximada; las AREA lights no se exportan.
3. Materiales y texturas siguen siendo de blockout, sin desgaste final.
4. No hay lógica de extracción, interactuable propio, narrativa ni multijugador.
5. El jugador sigue siendo el blockout de 1,70 m, sin modelo/animaciones finales.
6. R5 conserva menos servicios de techo que Z10 (HVAC/trays/risers más simples).

## 9. Próximo paso

Para una paridad de densidad exacta:

1. Añadir servicios de techo y pared equivalentes a Z10 (conduits, bandejas,
   soportes, cajas de derivación, ventilación).
2. Resolver la compuerta de extracción (lamas, estado abierto/cerrado, control).
3. Pasada final de materiales, desgaste y decals.
4. Lógica de extracción y pruebas de cooperación/multijugador.

Sin commit. Blender 5.2.3 abierto con el archivo guardado.

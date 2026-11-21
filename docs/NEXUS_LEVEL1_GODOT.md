# FRECUENCIA MUERTA — Nivel 1 jugable en Godot

Fecha: 2026-11-03 19:40 COT
Estado: **escena completa jugable local, en revisión artística**.

> **Nota 2026-11-10:** este documento describe el Nivel 1 completo con el GLB V05. `scenes/fm/level1.tscn` sigue cargando ese V05 obsoleto y no se modificó en el pase del vertical slice actual. El estado jugable vigente es `scenes/fm/fm_vslice_z10.tscn` (Z10 R8 + Recepción R9) y se documenta en `docs/FM_VERTICAL_SLICE.md`.

## Cómo abrir

```bash
godot --path . scenes/fm/level1.tscn
```

La escena `scenes/fm/level1.tscn` usa `scripts/fm/level1.gd`.

## Alcance del nivel

Incluye todos los espacios del Nivel 1 construidos en `nexus/nivel_01/NEXUS_L1_V05.blend`:

- Recepción NEXUS (16 × 10 m), oficina y aseo.
- Corredor principal de 44 × 3,4 m.
- Seguridad (10 × 8 m).
- Control de acceso (8 × 8 m).
- Vestuarios (10 × 8 m).
- Almacén (12 × 8 m).
- Mantenimiento (14 × 8 m).
- Conector de servicio almacén–mantenimiento.
- Ascensor SALIDA y cabina de recepción.
- Extremo oeste del corredor y acceso este al núcleo, cerrado con compuerta.

El núcleo vertical compartido queda fuera del Nivel 1 y se bloquea con `COL_EastShutter` y el rótulo **ACCESO AL NÚCLEO // BLOQUEADO**.

## Exportación del GLB

- Archivo: `assets/models/fm/level1_nexus.glb`.
- Tamaño: **42.507.928 bytes**.
- Exportado con Blender 5.2.3 desde `NEXUS_L1_V05.blend`.
- **1.940 objetos** seleccionados, **530.249 triángulos**, 320 objetos omitidos.
- Formato WebP calidad 70; sin cámaras ni luces exportadas.
- Las hojas de las puertas principales se omitieron para dejar los vanos transitables. Los marcos permanecen.
- Script reproducible: `blender_concept/export_level1_glb.py`.
- Reporte: `nexus/nivel_01/level1_export_selection.json`.

## Capa jugable

### Iluminación

- Solo luces de emergencia visibles y la linterna del jugador.
- **20 luces de emergencia** locales, ámbar/rojo, rango corto; dos con sombra.
- **0 luces generales** encendidas.
- Recepción con más luminarias que el resto, pero sin iluminación general.
- Se apagaron emisivos de lámparas, tiras de techo, tubos y paneles; se conservaron pantallas, letreros y lentes de emergencia.
- Linterna con proyector radial, spill y 12 W.
- Ambiente 0.055, AgX 1.10, SSAO 1.45, niebla volumétrica 0.008.

### Loot

Los cinco recuperables del GLB se distribuyeron por el nivel:

| Objeto | Zona | Valor | Peso |
|---|---|---:|---:|
| Maletín de muestras | Seguridad | 640 | 17 kg |
| Contenedor biológico | Vestuarios | 900 | 9 kg |
| Caja de carga | Almacén | 1800 | 42 kg (2 jugadores) |
| Documentación | Oficina | 220 | 0,6 kg |
| Unidad de datos | Control | 1200 | 0,4 kg |

### Interacciones

- Escondites: armario de recepción, taquilla de vestuarios y estantería del almacén.
- Trampas de ruido: corredor y almacén.
- Vigilante: patrulla el corredor, investiga ruidos y puede perder al jugador.
- Extracción: recepción completa, entrega junto al ascensor; secuencia animada con puertas.
- HUD, audio ambiental y avisos de estado.
- Objetos físicos: latas, portapapeles y cajas de cartón; emiten ruido al golpearse.

### Físicas

- **515 colliders** estáticos generados desde la geometría visible.
- Filtros para excluir papeles, sangre, decals, carteles, pantallas y piezas decorativas.
- Props dinámicos con `RigidBody3D`, colisión y eventos de ruido.
- El jugador no atraviesa muros, muebles, puertas cerradas ni la compuerta este.

## Pruebas

### `tests/fm_level1_smoke.tscn`

Resultado: **PASS**.

```text
TEST_PLAYER floor=true
TEST_LOOT 5
TEST_ROOMS 10/10
TEST_DOORS 6/6
TEST_EAST true hit=COL_EastShutter
TEST_LIGHTS true general=0 emergency=20 flashlight=3
TEST_WATCHER true patrol=6
TEST_NOISE true state=2
TEST_MOVE true
TEST_EXTRACTION true state=1 delivered=1
FM_LEVEL1_TEST: PASS
```

### `tests/fm_level1_perf.tscn`

Medición local a **1280 × 720**, VSync desactivado, tras cargar el nivel:

```text
LEVEL1_PERF fps=272.0 draws=346 primitives=78632 objects=8122
```

Es una medición de la máquina de desarrollo, **no** una garantía para la GTX 1650 Ti objetivo. Sirve como referencia inicial.

### Capturas

- `/tmp/opencode/level1_godot.png`
- `/tmp/opencode/level1_recepcion.png`
- `/tmp/opencode/level1_corredor.png`
- `/tmp/opencode/level1_seguridad.png`
- `/tmp/opencode/level1_control.png`
- `/tmp/opencode/level1_vestuarios.png`
- `/tmp/opencode/level1_almacen.png`
- `/tmp/opencode/level1_mantenimiento.png`
- `/tmp/opencode/level1_oficina.png`
- `/tmp/opencode/level1_aseo.png`

## Limitaciones

- Las puertas principales están abiertas y son estáticas; no hay interacción de abrir/cerrar.
- Solo hay un Vigilante. Imitador, Coleccionista y Sombra no están implementados en esta escena.
- No hay red de 8 jugadores, inventario general, desmontaje ni guardado.
- El arte sigue siendo una vertical slice: algunos props del GLB son simples.
- La oficina y el aseo son espacios pequeños; la composición de cámara es mejorable.
- El extremo este se bloquea porque el núcleo es un sistema compartido fuera del alcance.
- No se modificaron menús ni navegación global; la escena se abre directamente o desde una carga externa.
- Persisten las dos PNG inválidas de `industrial_wall_lamp_1k`; no se tocaron los assets originales.
- No se ha generado un build final.

## Dependencias compartidas

- `scenes/fm/fm_player.tscn` y `scripts/fm/fm_player.gd`: jugador compartido. Se usó sin cambiar su arquitectura de red; los ajustes de linterna/gravedad ya existían.
- `scenes/fm/fm_watcher.tscn` y `scripts/fm/fm_watcher.gd`: Vigilante compartido, usado sin modificar su IA.
- `scripts/fm/fm_reception_loot.gd`, `fm_reception_extraction.gd`, `fm_hiding_spot.gd`, `fm_noise_trap.gd`, `fm_hud.gd`: sistemas reutilizados localmente.
- No se modificaron otros niveles, menús, guardado ni red.

## Siguiente trabajo recomendado

1. Revisar visualmente cada sala con el jugador y corregir composición/encuadres.
2. Añadir interacción local a puertas principales y algunos contenedores.
3. Incorporar sonidos de pasos por superficie y ambientes por sala.
4. Añadir al menos otra criatura local sin modificar su sistema global.
5. Medir rendimiento en la GTX 1650 Ti objective y aplicar LOD/oclusión.
6. Integrar la escena en el flujo de menús solo cuando se autorice.

## Fase 2 — pulido y producción (2026-11-03 20:35 COT)

### Puertas, contenedores y distracciones

- **6 puertas funcionales** en recepción, seguridad, control, almacén, vestuarios y mantenimiento. Tienen hoja metálica a dos caras, ventana teal, manilla, patada y franja de peligro. Se abren/cierran con `E`, giran 95° con tween, emiten ruido y bloquean el paso cerradas.
- **8 cajones interactivos**: 3 de oficina, 3 de seguridad y 2 del mostrador de recepción. Se deslizan, emiten ruido y se pueden cerrar.
- **4 taquillas interactivas** en vestuarios, con puerta abatible, rejillas, manilla y etiqueta NEXUS.
- **3 paneles de alarma remota** en el corredor: activan ruido a 20 m en almacén, seguridad o mantenimiento para distraer al Vigilante, con recarga de 15 s.

### Físicas, ruido y audio

- Se añadieron **12 props físicos** nuevos (latas, portapapeles y cajas) en seguridad, control, vestuarios y mantenimiento. Todos emiten ruido al impactar.
- Se añadieron **7 emisores de ambiente 3D** con distintas afinaciones para recepción, seguridad, control, vestuarios, almacén y mantenimiento, además del ambiente general del corredor.
- Las puertas, cajones, taquillas y alarmas llaman a `emit_noise`, por lo que el Vigilante investiga sus eventos.
- No se modificó la IA compartida ni el controlador del jugador.

### Iluminación y atmósfera

- Se conservaron **0 luces generales**; ahora hay **30 luces de emergencia/locales** y 3 de linterna.
- Se añadieron lámparas de trabajo locales en seguridad, control, vestuarios, almacén, mantenimiento, oficina y aseo para revelar el foco de cada sala sin iluminar todo el nivel.
- Se añadieron **4 charcos húmedos** con `floor_wet.tres` en corredor, vestuarios, mantenimiento y almacén.
- La recepción sigue siendo la zona más visible; el resto exige linterna.

### Pruebas

`tests/fm_level1_smoke.tscn` → **PASS**:

```text
TEST_DOORS_CLOSED 6/6
TEST_DOORS_OPEN 6/6
TEST_DRAWER true moved=0.32000017166138
TEST_LOCKER true rot_y=-1.67551612854004
TEST_ALARM true cooldown=14.7446016666667
TEST_EAST true hit=COL_EastShutter
TEST_LIGHTS true general=0 emergency=30 flashlight=3
FM_LEVEL1_TEST: PASS
```

`tests/fm_level1_walk.tscn` → **PASS**, recorrido continuo sin teletransportes:

```text
WALK_RESULT reached=33/33 final=(-17.23699, -5.649168, -9.919495)
```

El recorrido sale de recepción, cruza el corredor, entra y sale de seguridad, control, vestuarios, almacén y mantenimiento, vuelve a recepción y termina en la extracción del ascensor.

`tests/fm_level1_perf.tscn` a 1280×720 en la máquina de desarrollo:

```text
LEVEL1_PERF fps=265.0 draws=582 primitives=124892 objects=8629
```

No es una medición de la GTX 1650 Ti; sigue pendiente probar en el hardware objetivo.

### Capturas

- `docs/fm_level1_phase2_rooms.png`: montaje de recepción, puerta, corredor, seguridad, control, vestuarios, almacén, mantenimiento, oficina y aseo.
- `docs/fm_level1_phase2_door.png`: puerta de recepción cerrada con panel, ventana, manilla y franja.
- `docs/fm_level1_phase2_reception.png` y `docs/fm_level1_phase2_corridor.png`.

### Limitaciones de esta fase

- Sigue habiendo un solo Vigilante.
- No hay pasos por material ni audio de superficies; el jugador compartido usa un único `step.wav`.
- No hay red de 8 jugadores, inventario general, desmontaje ni guardado.
- Varios props del GLB siguen siendo simples; no se reconstruyó el arte.
- El recorrido se hizo con las puertas abiertas por código; la apertura manual se prueba en el smoke test, no en una partida humana completa.
- No se probó en la GTX 1650 Ti ni se generó build final.
- Los draw calls subieron de 346 a 582 por las puertas, taquillas, alarmas, lentes y decals nuevos; siguen dentro de un presupuesto de PC, pero conviene fusionar piezas estáticas y evaluar occluders antes de exportar.
- Persisten las dos PNG inválidas de `industrial_wall_lamp_1k`.

---

## Fase 3: atmósfera, postprocesado y decals (2026-11-03)

Se añadió un pase cinematográfico local sin tocar otros niveles ni sistemas compartidos.

### Postprocesado

- Shader `assets/shaders/fm_postprocess.gdshader`, aplicado en un `CanvasLayer` bajo el HUD.
- Aberración cromática 0.00045, contraste 1.02, saturación 1.0, grano 0.022 y viñeta 0.26.
- Entorno: ambiente 0.075, exposición 1.16, contraste 1.08, saturación 1.0.
- SSAO 1.6, glow 0.5, niebla volumétrica 0.010 y SSR con 32 pasos.
- `ssr_roughness_quality` no existe en Godot 4.7 y se eliminó.

### Atmósfera y guía

- Dos tiras emisivas teal de 43,4 m en los bordes del corredor (`_setup_wayfinding`, y −5.632, z ±1.58, emisión 0.85).
- Polvo suspendido en el corredor (160 partículas) y vapor suave en mantenimiento (42 partículas).
- 22 decals de narrativa y desgaste con texturas locales: `blood_splat`, `blood_trail`, `puddle`, `grunge_decal`, `grime_decal` y `glass_crack`.
- Repartidos por corredor, recepción, seguridad, control, vestuarios, almacén, mantenimiento, oficina y aseo; sin colisión, alfa 0.24–0.55 y distance fade 14/6 m.

### Pruebas

- `tests/fm_level1_smoke.tscn`: **PASS**, `LEVEL1_READY loot=5 colliders=515`.
- `tests/fm_level1_walk.tscn`: **PASS**, `WALK_RESULT reached=33/33`, final `(-17.23691,-5.64919,-9.919388)`.
- `tests/fm_level1_perf.tscn` a 1280×720 en la máquina de desarrollo:

```text
LEVEL1_PERF fps=186.0 draws=1037 primitives=187620 objects=8768
```

No es una medición de la GTX 1650 Ti. Los draw calls subieron por los decals y el pase visual; la siguiente optimización debe medir el coste real de los decals y valorar su reducción o fusión.

### Capturas

- `/tmp/opencode/level1_*.png`: recepción, corredor, seguridad, control, vestuarios, almacén, mantenimiento, oficina y aseo.
- `docs/fm_level1_phase2_rooms.png` conserva el montaje de la fase anterior.

### Limitaciones de la Fase 3

- Sigue habiendo un solo Vigilante.
- No hay red de 8 jugadores, inventario general, desmontaje ni guardado.
- Varios props del GLB siguen siendo simples; el pase visual mejora atmósfera y composición, pero no sustituye el arte final.
- No se probó en la GTX 1650 Ti ni se generó build final.
- Persisten las dos PNG inválidas de `industrial_wall_lamp_1k`; no se tocaron los originales.

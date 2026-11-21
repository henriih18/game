# FRECUENCIA MUERTA — Fase 3A.3: sistema de puertas del Nivel 1

**Fecha:** 2026-11-04 (COT)  
**Ámbito:** las seis puertas del Nivel 1 jugable (`scenes/fm/level1.tscn`).  
**Estado:** implementado, probado y capturado. Sin commit.

## 1. Auditoría del sistema anterior

Antes de esta fase, las seis puertas se construían proceduralmente en `scripts/fm/fm_level1_door.gd` con la misma geometría: una hoja `BoxMesh` de 1,58 × 3,00 × 0,075 m, panel hundido, ventana pequeña, franja ámbar, manilla y tres bisagras. Todas eran idénticas salvo la orientación. El GLB jugable solo aportaba las jambas `*_DOOR_L/R` y el dintel `*_DOOR_TOP`; no contenía hojas estáticas de estas seis puertas.

Problemas detectados:

- Sin identidad por puerta: recepción, seguridad, control, almacén, vestuarios y mantenimiento se veían iguales.
- Sin cerraduras, teclados, lectores, niveles de acceso ni liberación manual.
- Sin alerta roja, bloqueo, dependencia eléctrica, puertas automáticas ni cooperación.
- Audio no posicional (`Audio.play_sfx`) y sin motor, fricción ni estados sonoros.
- Sin API de estado de red ni preparación para late join.
- Sin pruebas específicas de puertas; solo se comprobaba que cerraban/abrirían con rayos.

## 2. Diseño implementado

| Puerta | Tipo | Identidad y mecánica |
|---|---|---|
| `RECEPCION` | `auto_slide` | Doble hoja de cristal con bastidor de acero; sensor de movimiento; se abre al acercarse en movimiento y se cierra 1,8 s después de alejarse. Sin energía pasa a apertura manual (mantener E 1,4 s). |
| `SEGURIDAD` | `armored_swing` | Hoja blindada verde, ventana con barrotes, teclado y lector. Cerrada hasta introducir el código `0451`; el código está rotulado junto al teclado como ayuda de vertical slice. |
| `CONTROL` | `double_swing_seq` | Doble hoja con mecanismo central. Primer E libera la hoja A; un segundo E dentro de 7 s abre la hoja B. Si expira la ventana, la hoja A se cierra. |
| `ALMACEN` | `heavy_slide` | Doble hoja corredera pesada, refuerzos diagonales y franjas de peligro. Primer E agarra; un segundo operador abre. En solitario, mantener E 4 s fuerza la apertura con ruido alto. |
| `VESTUARIOS` | `light_swing` | Hoja ligera verde con panel esmerilado y rejilla; manilla convencional. |
| `MANTENIMIENTO` | `maintenance_swing` | Hoja metálica con rejilla pequeña, bisagras expuestas y liberación manual roja. Mantener E 1,4 s (2,2 s en alerta). |

Características comunes:

- Colisión propia por hoja (`StaticBody3D` + `BoxShape3D`), hija del pivote animado. Al abrir, la colisión se mueve con la hoja y despeja el vano.
- Bisagras o guías según el tipo; apertura/cierre con tween y `busy` para evitar dobles pulsaciones.
- Audio 3D local: cerradura (`click`), motor (`drop` grave), teclado (`tick`) y alarma (`alarm`).
- Luz de estado emisiva (verde/cian/ámbar/rojo) sin `OmniLight3D`, para no añadir coste de iluminación dinámica.
- Rótulos de sala: la señalización existente del nivel se conserva; el kit añade placa metálica sobre el dintel.
- `F9` activa/desactiva la alerta roja en la build de desarrollo (documentado; no es una tecla de jugador final).

## 3. Kit de Blender

- Generador: `blender_concept/build_level1_doors.py`.
- Fuente: `blender_concept/LEVEL1_DOORS.blend` (589 objetos de origen).
- GLB: `assets/models/fm/doors/level1_doors.glb` (**5,3 MB**, **116 mallas fusionadas por material**).
- Jerarquía animable: `DOOR_KIT_<ID>` → `Frame`, `LeafA`, `LeafB`, `Status`, `Sensor`, `Keypad`, `Manual`, `LabelAnchor_<ID>`.
- Materiales: `DOOR_Brush`, `DOOR_Steel`, `DOOR_Green`, `DOOR_Rust`, `DOOR_Blue`, `DOOR_DarkSteel`, `DOOR_Inset`, `DOOR_Rubber`, `DOOR_Glass`, `DOOR_Frost`, `DOOR_Hazard`, `DOOR_Label`, `DOOR_Status`, `DOOR_Cyan`, `DOOR_Red`, `DOOR_Amber`.
- Texturas 2K locales de metal oxidado, pintura verde y metal pintado; no se descargaron recursos externos ni se modificaron los originales.
- El GLB jugable `assets/models/fm/level1_nexus.glb` y `nexus/nivel_01/NEXUS_L1_V05.blend` **no se modificaron**.

## 4. Integración en Godot

### `scripts/fm/fm_level1_door.gd` (reescrito)

- Carga única del GLB con `GLTFDocument` y cache estática; cada puerta duplica solo su subárbol.
- Búsqueda tolerante a los sufijos que añade el importador (`LeafA_003`, etc.).
- `setup(id, width, height, side, angle, game, config)` conserva la firma anterior y añade configuración.
- API compatible: `set_open(value, instant)`, `can_interact`, `get_interaction_prompt`, `get_interaction_position`, `interact`.
- Nuevas APIs: `set_red_alert`, `set_powered`, `get_network_state`, `apply_network_state`, `submit_code`, `debug_advance_hold`.

### `scripts/fm/level1.gd`

- `_setup_doors()` configura tipo, cerradura, código, potencia y número de operadores por puerta.
- `set_red_alert(active)` recorre las seis puertas.
- `get_door_states()` / `apply_door_states(states)` serializan y restauran el estado (late join simulado).
- Se oculta el decal `NEXUS_V05_D_CORR_WALLSTAIN_0`, un panel claro preexistente que flotaba junto al acceso de Seguridad.
- No se modificaron físicas, colisiones ambientales, puertas de ascensor, persiana este, cajones, taquillas, alarmas, loot, IA, inventario ni menús.

## 5. Pruebas

- `tests/fm_level1_smoke.tscn`: **PASS**
  - `TEST_DOORS_CLOSED 6/6`
  - `TEST_DOORS_OPEN 6/6`
  - `TEST_LIGHTS true general=0 art=23 emergency=30 flashlight=3`
  - `FM_LEVEL1_TEST: PASS`
- `tests/fm_level1_walk.tscn`: **PASS**
  - `WALK_RESULT reached=33/33 final=(-17.23759, -5.64919, -9.920031)`
- `tests/fm_level1_doors.tscn`: **PASS**, `DOOR_TEST_FAILS 0`
  - tipos de las seis puertas, colliders por hoja, apertura/cierre ligera, teclado incorrecto/correcto, liberación de mantenimiento, cooperación de almacén, alerta global, teclado deshabilitado en alerta, apertura manual sin energía, serialización y restauración de estado (late join simulado).
- `tests/fm_level1_door_shots.tscn`: 14 capturas (6 cerradas, 6 abiertas, teclado y liberación).

## 6. Rendimiento

Medición a 1280×720, VSync desactivado, Watcher desactivado en el test para evitar que el overlay de detección distorsione la lectura:

| Versión | FPS | Draw calls | Primitivas | Objetos |
|---|---:|---:|---:|---:|
| Nivel 1 3A.2 (sin puertas nuevas) | 103 | 1.255 | 886.246 | 9.089 |
| Nivel 1 3A.3 (puertas nuevas) | 99–101 | 1.281 | 906.482 | 9.603 |

Las puertas añaden **+26 draw calls**, **+20.236 primitivas** y **+514 objetos**; el coste es de aproximadamente **2–4 FPS** en este equipo. No hay LOD ni occlusion culling para las puertas; al ser seis instancias pequeñas, el coste principal son las mallas y los materiales, no la iluminación (se eliminaron las seis `OmniLight3D` de estado previstas inicialmente).

## 7. Capturas

- `docs/fm_level1_doors_contact_sheet.png` — seis puertas cerradas/abiertas.
- `docs/fm_level1_doors_before_after.png` — comparativa 3A.2 vs 3A.3 de las seis puertas.
- `docs/fm_level1_door_recepcion_closed.png` / `_open.png`
- `docs/fm_level1_door_seguridad_closed.png` / `_open.png` / `_seguridad_keypad.png`
- `docs/fm_level1_door_control_closed.png` / `_open.png`
- `docs/fm_level1_door_almacen_closed.png` / `_open.png`
- `docs/fm_level1_door_vestuarios_closed.png` / `_open.png`
- `docs/fm_level1_door_mantenimiento_closed.png` / `_open.png` / `_mantenimiento_release.png`

## 8. Limitaciones y pendientes

- **Red real no probada:** `level1.gd` sigue siendo offline. Se implementó y probó la serialización/restauración de estado, pero **no hay RPCs de puertas ni prueba con dos clientes reales**. La API es host-autoritativa por diseño, pero falta conectarla al transporte cuando exista multijugador en el Nivel 1.
- La alerta roja se activa con `F9` o por API; **no está conectada todavía a las tres alarmas existentes** ni a un evento global de la instalación.
- El código `0451` es fijo y está rotulado junto al teclado como ayuda de demo; falta un sistema de documentos, tarjetas o pistas.
- El cierre de la puerta pesada en solitario es una válvula de escape deliberada; no sustituye la cooperación real.
- La puerta de vestuarios tiene el panel esmerilado sobreexpuesto por la luz de la sala; el material ya se oscureció, pero el panel sigue leyéndose muy claro.
- No hay animación de manillas, bisagras individuales, hidráulica ni vibración; la hoja se anima como cuerpo rígido.
- Sin LOD/occlusion específicos para puertas; sin prueba en GTX 1650 Ti ni build final.
- No se implementaron armas, combate ni formas de eliminar criaturas.

## 9. Siguiente paso recomendado

1. Conectar `get_door_states` / `apply_door_states` al futuro transporte host-autoritativo del Nivel 1 y probar cliente, late join y apertura simultánea.
2. Enlazar `set_red_alert(true/false)` con las alarmas y eventos de la instalación.
3. Sustituir el código fijo por tarjetas/documentos encontrables, sin tocar inventario hasta que exista.
4. Añadir LOD/occlusion a las puertas y medir en GTX 1650 Ti.
5. Refinar el panel esmerilado de vestuarios y la densidad del teclado en vistas cercanas.

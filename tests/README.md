# Pruebas

Pruebas básicas versionadas. No sustituyen una batería de integración completa.

## Vertical slice Z10 → Recepción (2026-11-10)

```bash
godot --headless --path . tests/fm_vslice_smoke.tscn
godot --headless --path . tests/fm_vslice_walk.tscn
godot --headless --path . tests/fm_vslice_chase.tscn
godot --headless --path . tests/fm_inventory_smoke.tscn
godot --headless --path . tests/fm_inventory_flow.tscn
godot --headless --path . tests/fm_extraction_chase.tscn
godot --headless --path . tests/fm_nav_long_chase.tscn
godot --headless --path . tests/fm_desk_chase.tscn
godot --headless --path . tests/fm_reception_hide.tscn
godot --headless --path . tests/fm_queue_chase.tscn
godot --headless --path . tests/fm_extraction_capture.tscn
```

- `fm_vslice_smoke`: **52 PASS / 0 FAIL**. Arte Z10+Recepción, colisiones, jugador, cámara, linterna/batería (consumo solo encendida), movimiento/sprint/crouch, objeto físico, escondite (el Vigilante no ve al escondido), observación y congelación del Vigilante, ruido, patrulla de 20 s, transición, reactivación del Vigilante en Recepción (navmesh runtime de 355 polígonos, `NavigationAgent3D`, 8 waypoints y movimiento real) y extracción.
- `fm_vslice_walk`: **16 PASS / 0 FAIL**. Recorrido real con `Input.action_press` desde Z10 hasta la extracción en Recepción. Desactiva la IA de Recepción para medir navegación y comprueba que queda suspendida en esa prueba.
- `fm_vslice_chase`: **9 PASS / 0 FAIL**. Activa al Vigilante con la transición real, lo coloca a 7 m del jugador, comprueba el paso a `CHASE`, el acercamiento a 3,55 m/s y la captura a 1,21 m con `state=LOST`.
- `fm_inventory_smoke`: **27 PASS / 0 FAIL**. Núcleo de misión a manos, componentes pequeños al inventario, capacidad y peso máximos, drop de inventario, desmontaje cancelado/completado con ruido, transición real a Recepción, bloqueo de extracción sin misión y entrega única (4 componentes + núcleo = 5 objetos).
- `fm_inventory_flow`: **30 PASS / 0 FAIL**. Flujo completo con el Vigilante activo: acceso a pie al puesto de análisis, desmontaje con ruido que lo atrae a `INVESTIGATE`, cuatro componentes al inventario, núcleo a manos, transición real a Recepción y extracción con 5 objetos válidos.
- `fm_extraction_chase`: **8 PASS / 0 FAIL**. Extracción bajo persecución real: el Vigilante de Recepción pasa a `CHASE`, se acerca de 7,88 m a 6,23 m y el jugador completa la extracción antes de ser capturado.
- `fm_nav_long_chase`: **7 PASS / 0 FAIL**. Persecución larga con navmesh: el Vigilante arranca en `(-90,0.12,28)`, rodea la columna central con 0,94 m de desviación lateral, recorre 14,78 m y captura al jugador a 1,23 m. En ventana genera cuatro capturas en `docs/fm_nav_long_chase_01..04.png
- `fm_desk_chase`: **7 PASS / 0 FAIL**. Persecución con el escritorio `REC06_DESK_HERO` entre el Vigilante y el jugador: 8,29 m recorridos, 2,51 m de desviación lateral para rodearlo y captura a 1,19 m. Capturas: `docs/fm_desk_chase_01..04.png`.`.
- `fm_reception_hide`: **10 PASS / 0 FAIL**. Escondite `TAQUILLAS DE PERSONAL` en `(-106,0.05,38.8)`: el Vigilante ve al jugador y pasa a `CHASE`, el jugador se oculta, el Vigilante lo pierde y no lo captura; después sale del escondite.
- `fm_queue_chase`: **7 PASS / 0 FAIL**. Cola de seguridad `REC08`: el Vigilante rodea el recinto de 3×3 m, recorre 7,01 m, se desvía 2,20 m y captura al jugador a 1,23 m. Capturas: `docs/fm_queue_chase_01..04.png`.
- `fm_extraction_capture`: **9 PASS / 0 FAIL**. El jugador activa la extracción con el núcleo; el Vigilante arranca a 8 m y lo captura durante la secuencia de 4,0 s. La extracción no se completa, vuelve a `waiting` y no aparece un falso WON.
- `fm_vslice_shot.tscn` (ventana): genera 7 capturas en `docs/fm_vslice_*.png`.
- `fm_vslice_perf.tscn` (ventana): mide Z10 y Recepción en la misma build. Es una escena jugable estática, no una partida completa.

### Partida completa y rendimiento con IA activa (2026-11-12)

```bash
godot --headless --path . tests/fm_full_run.tscn
godot --path . tests/fm_perf_ai.tscn
```

- `fm_full_run`: **49 PASS / 0 FAIL**; 45,09 s de pared en la última corrida. Recorrido real desde el spawn de Z10 hasta la extracción de Recepción, sin teletransportar al jugador: puesto de análisis a pie, desmontaje con la duración real de 6,0 s, cuatro componentes al inventario, núcleo a manos, puerta de enlace usada con `transition_door.interact` a través de E, Recepción y extracción con la secuencia real de 2,0 + 6,7 s. Resultado: `state=1` (WON), `delivered=5`, `inventory=4`, núcleo en manos. El paso máximo fuera de la transición fue **0,057 m** por frame. El Vigilante conservó `vision_distance=18`, nunca estuvo suspendido y pasó por `DORMANT/PATROL/INVESTIGATE/CHASE/SEARCH`; recorrió 7,64 m en total (patrulla, investigación y persecución) antes de quedar congelado por observación. No hubo captura.
  - La escena activa solo instancia **un** `FMWatcher`. El Vigilante de Recepción es la misma instancia reubicada con `activate_in_sector`, no una segunda criatura. El test comprueba `set_physics_process(true)` y `is_watcher_suspended()==false` en el tramo Z10 y en el tramo Recepción, y en cada frame intermedio.
  - La supervivencia usa la mecánica real: el bot mantiene la mirada sobre el Vigilante cuando está a ≤15,5 m con línea de visión, lo que activa su congelación por observación. No se modificaron `vision_distance`, la IA, los tiempos de desmontaje ni la extracción. No se usaron escondites en esta corrida.
  - Limitaciones: un jugador local; la transición Z10 → Recepción sigue siendo fundido + reubicación provisional; no hay red; el bot usa observación y strafe/retroceso, no entrada humana; no se prueba una captura durante este recorrido (hay pruebas específicas para eso).
- `fm_perf_ai` (ventana, 1280×720, VSync off verificado con `vsync_ok=true`, 10 s, IA activa y movimiento real): **PASS**. Hardware NVIDIA RTX 5050 Laptop GPU, driver 595.99.02, Godot 4.7.2 Forward+. En la corrida integrada final de `tests/run_all.sh`: **457,1 FPS medio**, **203,3 FPS mínimo por frame**, **287,5 FPS en el percentil 1 %**, 4.573 frames, **1.494 draw calls**, **6.473 objetos**, **457,3 MB de texturas** y **593,8 MB de vídeo**. En cuatro corridas aisladas: 383,1–444,3 FPS medio, 107,1–177,0 FPS mínimo, 150,9–259,7 FPS p1 %, 1.492–1.506 draw calls máximos y 6.520–6.550 objetos. El jugador recorrió ~33,9 m con `Input.action_press`; el Vigilante pasó por `DORMANT/PATROL/CHASE/SEARCH`, no fue suspendido y no capturó al jugador.
  - Limitación: es una escena de prueba de Z10, no una partida completa ni el rendimiento del juego final. La cámara y el frustum hacen variar los draw calls (110–1.506 en las muestras); no debe citarse como FPS garantizado del juego.
- Regresión integrada: `bash tests/run_all.sh` → **exit 0**. Las 12 pruebas existentes suman **257 PASS / 0 FAIL**; `fm_full_run` **49 PASS / 0 FAIL**; `fm_perf_ai` **PASS**; el vertical slice offline heredado, el juego 2D y las redes 2D/3D también PASS. `run_all.sh` ejecuta `fm_perf_ai` en ventana si hay `DISPLAY`/`WAYLAND_DISPLAY`; si no, lo omite con `SKIP` explícito.

### Anclajes narrativos N1/N2/N3/N4/N5/N6/N7/N8 (2026-11-12)

```bash
godot --headless --path . tests/fm_narrative_smoke.tscn
```

- `fm_narrative_smoke`: **75 PASS / 0 FAIL**. Comprueba las 8 raíces del grupo
  `fm_narrative`, IDs únicos, distancia >1,2 m a la ruta jugable, sector y
  metadatos, ausencia de colisiones/áreas/luces bajo `Narrative`, el número de
  mallas y el pase de materiales (sets PBR, triplanar, micro-normales y emisivos).
- `fm_narrative_shot.tscn` (ventana): genera 15 capturas en
  `docs/fm_narrative_*.png`.
- Detalle: `docs/FM_NARRATIVE_ANCHORS.md`.

El mouse look no se prueba en headless (el DisplayServer no captura el ratón); se verifica en ventana con `SHOT_LOOK_OK true`.

## Vertical slice offline

```bash
godot --headless --path . tests/fm_slice_smoke.tscn
```

Comprueba: jugador, Vigilante, núcleo, extracción, escondites, HUD, linterna,
observación, recogida, esconderse/salir, victoria, puerta de seguridad, batería,
trampa sonora y audio ambiental. Resultado esperado: **26 PASS**.

## Juego 2D heredado

```bash
godot --headless --path . --script tests/test_main_2d.gd
```

Resultado esperado: **16 PASS**.

## Red 2D heredada

```bash
bash tests/run_net_check.sh
```

Levanta un host headless en el puerto 7777 y ejecuta un cliente. Resultado esperado:
**6 PASS**. El test usa `/tmp/opencode` para el log temporal.

## Red 3D host-autoritativa

```bash
bash tests/run_net_3d_check.sh
```

Levanta un host 3D headless (`--host3d --nettest`) y ejecuta un cliente real de la
escena `VerticalSlice` contra él. Comprueba conexión, roster de dos jugadores, spawns
separados, recarga de batería, apertura de puerta, recogida del núcleo, extracción
final y HUD del cliente. Resultado esperado: **15 PASS**. Los logs quedan en
`/tmp/opencode`.

## Nota

Los tests fuerzan la salida del árbol y pueden imprimir avisos de `ObjectDB` o recursos
todavía en uso. No indican un fallo de gameplay; se revisarán cuando exista una suite
de integración continua.

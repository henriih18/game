# FRECUENCIA MUERTA — Vertical slice jugable Z10 → Recepción

Fecha: 2026-11-10; actualización de inventario y partida completa: 2026-11-12. Estado: **primera base jugable local de 1 jugador, probada headless y en ventana; sin commit**.

Este slice es una capa de juego nueva sobre las escenas de arte ya aprobadas de **Z10 (R8, oscura)** y **Recepción (R9)**. No modifica los GLB, las escenas de arte ni `fotos-referencia/`. No reconstruye el Nivel 1 ni sustituye `scenes/fm/level1.tscn`, que sigue cargando el V05 obsoleto y queda fuera de esta tarea.

---

## 1. Objetivo y alcance

Demostrar el bucle mínimo del juego con arte real:

1. Entrar en Z10 con cámara en primera persona.
2. Explorar en oscuridad con la linterna y su batería.
3. Recuperar un objeto físico, transportarlo y soltarlo.
4. Esconderse de El Vigilante.
5. Cruzar el enlace de servicio hacia Recepción.
6. Entregar el objeto en la extracción de Recepción.

Sin armas, sin combate y sin sistemas ficticios. Los sistemas compartidos del proyecto se reutilizan; solo se añade la orquestación del slice y la transición provisional entre sectores.

**Fuera de alcance de esta iteración:** multijugador, guardado, inventario general completo, desmontaje definitivo de §32, otras criaturas, navegación navmesh del nivel completo fuera del slice, arte final del núcleo y secuencia animada del ascensor. El primer pase de inventario/peso/desmontaje está documentado en `docs/FM_INVENTORY_DISMANTLING.md`.

---

## 2. Estado previo y decisiones

| Elemento | Estado |
|---|---|
| Arte Z10 | `scenes/fm/fm_z10_art_r8.tscn`, GLB `assets/models/fm/z10_sector.glb`; 3 luces rojas de emergencia, exposición 0.80, niebla 0.012. |
| Arte Recepción | `scenes/fm/fm_reception_art_r9.tscn`, GLB `assets/models/fm/reception_sector.glb`; 12 luces omni diegéticas, exposición 1.12. |
| Nivel completo | No existe export V06 del nivel completo. Z10 y Recepción son GLB de sector separados y están a ~140 m en coordenadas. |
| `scenes/fm/level1.tscn` | Sigue cargando el GLB V05 obsoleto. **No se tocó.** |
| Sistemas de gameplay | Ya existían `FMPlayer`, `FMWatcher`, `FMHidingSpot`, `FMCarryItem`, `FMBattery`, `FMReceptionExtraction`, `FMHUD`, `FMGLBCollision` y `Audio`. |

Por la separación física de los sectores, el enlace Z10 → Recepción es una **puerta de servicio interactiva con transición provisional** (fundido + teletransporte). No se presenta como geometría final.

---

## 3. Arquitectura del slice

### 3.1. Escena raíz

`scenes/fm/fm_vslice_z10.tscn` instancia las dos escenas de arte:

```text
FMVSliceZ10 (Node3D, fm_vslice_z10.gd)
├── Z10Art            (fm_z10_art_r8.tscn)
│   ├── Z10Sector     (GLB, 507 mallas)
│   ├── ArtCamera     (desactivada por el slice)
│   └── WorldEnvironment (environment cedido al slice)
└── ReceptionArt      (fm_reception_art_r9.tscn)
    ├── ReceptionSector (GLB, 292 mallas)
    ├── ArtCamera     (desactivada por el slice)
    ├── WorldEnvironment (environment cedido al slice)
    └── 12 luces omni
```

El slice toma una copia de los dos `Environment` de las escenas de arte, desactiva sus `WorldEnvironment` originales y usa un único `WorldEnvironment` propio. Al cruzar el enlace cambia el environment de Z10 (R8) al de Recepción (R9), conservando la dirección artística de cada sala. No se añaden key/fill/bounce.

### 3.2. Sistemas reutilizados

| Sistema | Archivo | Uso en el slice |
|---|---|---|
| Jugador FPS | `scripts/fm/fm_player.gd` | Cámara, WASD, sprint, crouch, gravedad, linterna con batería, interacción, transporte, escondite, observación y emisión de ruido. |
| El Vigilante | `scripts/fm/fm_watcher.gd` | FSM DORMANT/PATROL/INVESTIGATE/CHASE/SEARCH, congelación al ser observado, visión con raycast, audición e intercepción. |
| Escondite | `scripts/fm/fm_hiding_spot.gd` | Entrada/salida del escondite; El Vigilante ignora al jugador escondido. |
| Objeto físico | `scripts/fm/fm_carry_item.gd` | `RigidBody3D` congelado al recoger, anclaje a la cámara, física y ruido al soltar. Distingue tamaño, tipo y objeto de misión. |
| Inventario y peso | `scripts/fm/fm_player.gd` | Manos para objetos medianos, 4 ranuras y 12 kg para pequeños, penalización de velocidad y drop con Q. |
| Desmontaje | `scripts/fm/fm_dismantlable.gd` | Puesto interactivo con tiempo, ruido periódico, cancelación por distancia y cuatro componentes. |
| Batería | `scripts/fm/fm_battery.gd` | Recogida y recarga de la linterna. |
| Extracción | `scripts/fm/fm_reception_extraction.gd` | Activación de 2 s, secuencia, cancelación y final. |
| HUD | `scripts/fm/fm_hud.gd` | Objetivo, estado, batería, stamina, escondite, observación y overlay final. |
| Colisiones GLB | `scripts/fm/fm_glb_collision.gd` | Colisiones estáticas para los dos GLB. |
| Audio | `scripts/audio.gd` | SFX y ambientes looping. |

No se duplicó el controlador, la IA, el escondite, el transporte ni la extracción. El script del slice solo implementa el contrato que esos sistemas esperan (`state`, `emit_noise`, `on_player_caught`, `get_delivered_loot_count`, etc.).

### 3.3. Archivos nuevos

- `scenes/fm/fm_vslice_z10.tscn`
- `scripts/fm/fm_vslice_z10.gd`
- `scripts/fm/fm_sector_transition.gd`
- `tests/fm_vslice_smoke.tscn` + `.gd`
- `tests/fm_vslice_walk.tscn` + `.gd`
- `tests/fm_vslice_shot.tscn` + `.gd`
- `tests/fm_vslice_perf.tscn` + `.gd`
- `tests/fm_inventory_smoke.tscn` + `.gd`
- `tests/fm_inventory_flow.tscn` + `.gd`
- `tests/fm_extraction_chase.tscn` + `.gd`
- `tests/fm_full_run.tscn` + `.gd`
- `tests/fm_perf_ai.tscn` + `.gd`
- `scripts/fm/fm_dismantlable.gd`
- Capturas `docs/fm_vslice_*.png`

Archivo existente modificado:

- `scripts/fm/fm_hud.gd`: se guarda el `Label` de la pista inferior y se añade `set_hint(text)`. El slice lo usa para indicar **ESC MOUSE** en lugar de **ESC MENÚ**; el texto y el comportamiento por defecto para las demás escenas no cambian.

Documentación actualizada: `docs/FM_VERTICAL_SLICE.md`, `docs/CURRENT_STATE.md`, `docs/NEXUS_LEVEL1_GODOT.md`, `tests/README.md` y la nota superior de `README.md`.

### 3.4. Capa jugable añadida

- Colisiones: **277** shapes en Z10 y **151** en Recepción, más un suelo de seguridad por sector.
- Jugador en `Z10_SPAWN = (42.2, 0.12, -22.0)`, mirando hacia +X.
- Núcleo físico en `(57.4, 0.36, -21.4)`.
- Escondite en las estanterías de Z10, `(42.5, 0.05, -9.4)`, prompt **ESTANTERÍA**.
- El Vigilante inicia en `(59.0, 0.12, -14.5)` y patrulla un circuito de cuatro puntos al sur de la zanja de cables.
- 4 baterías: banco de trabajo, almacén, enlace de servicio y Recepción.
- Enlace de servicio en el extremo este del conector de Z10, `(69.05, 0, -21.0)`.
- Extracción provisional en Recepción, `(-94, 1.3, 36.0)`, con centro de entrega `(-94, 0.3, 37.6)`.
- Ambientes 3D looping en Z10 y Recepción; sin música.
- HUD y fundido de entrada/salida.

### 3.5. Anclajes narrativos N1/N2/N3/N4/N5/N6/N7/N8

Se añadió `Narrative` como nodo hermano de `Z10Art`/`ReceptionArt`, con ocho
raíces de detalle narrativo: mostrador (N1), sala de espera (N2), taquillas (N3),
control de seguridad (N4), umbral de entrada (N5), pasillo central (N6),
extracción/decon (N7) y enlace de servicio Z10 (N8). No tienen colisión, luces ni
interacción y quedan fuera de la ruta jugable y del radio de extracción. Detalle
completo, coordenadas y capturas en `docs/FM_NARRATIVE_ANCHORS.md`.

---

## 4. Controles

| Acción | Tecla |
|---|---|
| Mover | WASD |
| Mirar | Mouse |
| Correr / agacharse | Shift / Ctrl |
| Interactuar, recoger, esconderse, salir, usar enlace | E |
| Soltar el núcleo | Q |
| Linterna | F |
| Reiniciar tras detección | R |
| Capturar / liberar mouse | Esc |

La sensibilidad y la altura de cámara son las de `FMPlayer` (cápsula 0,38/1,70; ojos 1,62 m de pie y 1,08 m agachado).

---

## 5. Reglas del slice

### 5.1. Linterna y batería

- Batería máxima: 100.
- Consumo: **0,65 %/s** con la linterna encendida (≈154 s de luz continua).
- La linterna se enciende/apaga con F; no funciona con batería a 0.
- Cada batería recogible recarga 35–40 %.
- La batería no se agota de forma instantánea ni bloquea la partida; la oscuridad y la exploración son la presión principal.

### 5.2. Núcleo

- Es el `FMCarryItem` existente, con visual procedural de núcleo verde.
- Se recoge con E, se transporta delante de la cámara y se suelta con Q.
- Transportarlo reduce la velocidad al 58 % y aumenta ligeramente el ruido de pasos.
- Al soltarlo se simula físicamente y emite ruido; El Vigilante puede investigarlo.

### 5.3. Escondite

- Área interactiva en las estanterías; E entra y E sale.
- Mientras está escondido, el jugador no colisiona ni emite pasos y El Vigilante lo ignora como objetivo.
- El escondite no es invisibilidad absoluta: si el Vigilante ya investigaba la zona, puede permanecer cerca.
- El punto de salida está hacia el pasillo, no dentro de la estantería.

### 5.4. El Vigilante

- Permanece inmóvil cuando el jugador lo observa (dentro de 18 m, con linterna encendida o hasta 8 m sin ella, con línea de visión).
- Se mueve al perder el contacto visual.
- Ve al jugador con cono frontal y línea de visión; investiga ruidos (pasos, pickup, drop, baterías).
- Persigue y, a menos de 1,25 m, llama a `on_player_caught`.
- La detección es local al slice; el movimiento usa un navmesh runtime de 355 polígonos con `NavigationAgent3D`. La ruta de patrulla se eligió manualmente para evitar zanjas, columnas y props bajos.
- Al cruzar a Recepción se reubica en `(-93, 0.12, 29)` y se activa con una ruta de 8 waypoints por el pasillo central; es el mismo Vigilante, no una segunda instancia. El navmesh cubre también Recepción.

### 5.5. Transición Z10 → Recepción

- La puerta de enlace se usa con E desde el extremo este del conector de servicio.
- Fundido a negro de 0,45 s, teletransporte a `(-90, 0.12, 6.2)` mirando hacia +Z, cambio de environment y fundido de entrada.
- Al cruzar, El Vigilante se reubica en Recepción `(-93, 0.12, 29)` y se activa con una ruta de 8 waypoints por el pasillo central; ya no queda suspendido. El movimiento usa el navmesh runtime del slice.
- **Es provisional:** los sectores no están conectados geométricamente porque todavía no existe el export V06 del nivel completo.

### 5.6. Extracción

- La zona está en Recepción, en el ala sur, delante de una compuerta de salida provisional.
- Requiere:
  1. el jugador dentro del volumen de Recepción,
  2. al menos un objeto recuperado dentro de 2,4 m del centro de entrega o en manos de un jugador presente,
  3. mantener la condición durante 2 s.
- La secuencia dura 8,7 s (2 s de activación + 6,7 s de secuencia) según `FMReceptionExtraction`.
- Al completarse, el estado pasa a `WON` y el HUD muestra el resultado.
- Si el jugador sale de la zona durante la secuencia, se cancela.
- **La compuerta, la cabina y la animación del ascensor son placeholder.** No hay puerta animada ni viaje real; el procedimiento operativo definitivo sigue pendiente de aprobación (§45 de AGENTS.md).

### 5.7. Detección y fracaso

- Si el Vigilante alcanza al jugador, el estado pasa a `LOST`, se muestra **DETECTADO** y se libera el mouse.
- R recarga la escena.
- No hay muerte permanente, guardado ni checkpoint.

---

## 6. Pruebas

### 6.1. Smoke test headless

```bash
godot --headless --path . tests/fm_vslice_smoke.tscn
```

Resultado: **`FM_VSLICE_TEST: PASS (52 PASS / 0 FAIL)`**.

Cubre:

- Carga de las dos escenas de arte (507 + 292 mallas) y cámaras de arte desactivadas.
- 277 + 151 colisiones y suelo en ambos sectores.
- Jugador en suelo, cámara activa, linterna visible y environment correcto.
- Movimiento, sprint (más rápido), crouch (más lento), stamina y altura de ojos agachado.
- Toggle de linterna, consumo solo encendida, recarga y recogida de una batería del mundo.
- Recogida con E, transporte junto al ancla y drop con Q.
- Entrada/salida del escondite con E, capas de colisión y comprobación de que el Vigilante no ve al jugador escondido.
- Observación directa: visto / no visto.
- Congelación del Vigilante al ser observado y movimiento al perder el contacto visual.
- Audición de ruido → estado `INVESTIGATE`.
- Patrulla real de 20 s: el Vigilante recorre 16,93 m sin atascarse.
- Reactivación en Recepción: Vigilante activo, ruta de 8 waypoints, altura 0,12 y 3,17 m recorridos en 3 s.
- Prompt e interacción del enlace de servicio.
- Transición a Recepción, cambio de environment y activación del Vigilante en el nuevo sector.
- Extracción con el núcleo dentro de la zona → `state=1`, `delivered=1`.

El único chequeo omitido en headless es el mouse look (`SKIP player_look`), porque el DisplayServer headless no captura el ratón; se verificó en ventana: `SHOT_LOOK_OK true`.

La prueba de anclajes narrativos se ejecuta aparte:

```bash
godot --headless --path . tests/fm_narrative_smoke.tscn
```

Resultado: **`FM_NARRATIVE_TEST: PASS (75 PASS / 0 FAIL)`**. Ver `docs/FM_NARRATIVE_ANCHORS.md`.

### 6.2. Recorrido end-to-end con movimiento real

```bash
godot --headless --path . tests/fm_vslice_walk.tscn
```

Resultado: **`FM_VSLICE_WALK: PASS (16 PASS / 0 FAIL)`**.

El bot recorre con `Input.action_press`:

```text
Z10 spawn → (47,-22) → (52,-21.4) → (55.7,-21.4)
→ recoger núcleo con E
→ (58.2,-21.4) → (61.4,-21) → (67.4,-21)
→ usar enlace con E
→ Recepción (-90,6.2) → (-90,13) → (-93,16.5) → (-93,24)
→ (-92,32) → (-94,36.4)
→ extracción WON, carried=true, delivered=1
```

La extracción se probó con los tiempos reales de `FMReceptionExtraction` (2 s de activación + 6,7 s de secuencia, sin atajos). La ruta de Recepción rodea la columna estructural de `x=-90, z=20`; el pasillo se recorre por `x=-93`. El walk desactiva la IA de Recepción (`reception_watcher_enabled = false`) para medir navegación y comprueba que el Vigilante queda suspendido en esa prueba.

#### 6.2.1. Partida completa con IA activa

```bash
godot --headless --path . tests/fm_full_run.tscn
```

Resultado: **`FM_FULL_RUN: PASS (49 PASS / 0 FAIL)`**; **45,09 s** de pared en la última corrida.

El test recorre el bucle completo sin teletransportar al jugador:

```text
spawn Z10 (42.2,-22) → puesto de análisis (51.2,-18.2)
→ desmontaje real de 6,0 s → 4 componentes (2,9 kg)
→ núcleo en (55.7,-21.4) (9,9 kg totales)
→ puerta de enlace con E (transition_door.interact) → Recepción
→ pasillo central (-90,13) → (-93,16.5) → (-93,24) → (-92,32) → (-94,36.4)
→ extracción real de 2,0 + 6,7 s → state=1 (WON), delivered=5
```

Comprobaciones principales:

- `vision_distance=18` en Z10 y en Recepción; el Vigilante **nunca** se suspende y `set_physics_process(true)` se mantiene en ambos tramos y en cada frame intermedio.
- El Vigilante pasa por `DORMANT`, `PATROL`, `INVESTIGATE`, `CHASE` y `SEARCH`; recorre **7,64 m en total** (patrulla, investigación y persecución) antes de quedar congelado por observación. No hay captura.
- El paso máximo del jugador fuera de la transición es **0,057 m/frame**; el único salto es la reubicación de la propia transición.
- El desmontaje usa su duración por defecto de **6,0 s** y la extracción la secuencia real de **2,0 + 6,7 s**; no se reducen tiempos.
- El Vigilante conserva la visión normal; la supervivencia del bot usa la mecánica de congelación al ser observado (mira al Vigilante a ≤15,5 m con línea de visión) y strafe/retroceso para seguir avanzando. No se usan escondites en esta corrida.

La escena activa solo instancia **un** `FMWatcher`. El Vigilante de Recepción es la misma instancia reubicada con `activate_in_sector`; no se creó una segunda criatura. Por tanto, “los dos Vigilantes” del enunciado se validan como los dos tramos de activación (Z10 y Recepción) de la misma instancia.

Limitaciones: un jugador local; transición provisional por fundido + reubicación; sin red; el bot no representa entrada humana; no se prueba una captura durante este recorrido (las pruebas de captura son específicas). `bash tests/run_all.sh` ejecuta este test junto con la regresión; la corrida integrada terminó con **exit 0**.

### 6.3. Persecución real en Recepción

```bash
godot --headless --path . tests/fm_vslice_chase.tscn
```

Resultado: **`FM_VSLICE_CHASE: PASS (9 PASS / 0 FAIL)`**.

La prueba usa la transición real para activar al Vigilante, lo coloca a 7 m del jugador con este de espaldas y comprueba:

- Paso de `PATROL` a `CHASE` con el jugador visible y no observado.
- Acercamiento real: 6,88 m → 4,04 m en 0,8 s (3,55 m/s).
- Captura a 1,21 m, con `state=LOST` y el mensaje de detección.
- Que el jugador no estaba escondido durante la captura.

El movimiento usa navmesh runtime. La persecución larga alrededor de la columna central está probada aparte (sección 6.3.1); siguen sin probarse las esquinas cerradas.

#### 6.3.1. Persecución larga alrededor de la columna

```bash
godot --headless --path . tests/fm_nav_long_chase.tscn
```

Resultado: **`FM_NAV_LONG_CHASE: PASS (7 PASS / 0 FAIL)`**.

El jugador espera en `(-90,0.12,12)` mirando al norte; el Vigilante arranca en `(-90,0.12,28)` y recibe un ruido para investigar. Rodea la columna central, recorre **14,78 m** con **0,94 m** de desviación lateral máxima y captura a **1,23 m**. La versión en ventana genera cuatro capturas en `docs/fm_nav_long_chase_01..04.png`.

### 6.3.2. Persecución alrededor del escritorio

```bash
godot --headless --path . tests/fm_desk_chase.tscn
```

Resultado: **`FM_DESK_CHASE: PASS (7 PASS / 0 FAIL)`**.

El jugador espera en `(-102, 0.12, 17)` y el Vigilante arranca en `(-102, 0.12, 8)`, con el escritorio `REC06_DESK_HERO` (x≈-104.3..-99.9, z≈12.55..14.82) bloqueando la línea directa. El Vigilante recorre **8,29 m**, se desvía **2,51 m** lateralmente para rodearlo y captura al jugador a **1,19 m**. Capturas: `docs/fm_desk_chase_01..04.png`.

### 6.3.3. Escondite en Recepción

```bash
godot --headless --path . tests/fm_reception_hide.tscn
```

Resultado: **`FM_RECEPTION_HIDE: PASS (10 PASS / 0 FAIL)`**.

El escondite `HideReceptionLockers` está en `(-106.0, 0.05, 38.8)`, junto a las taquillas de personal (`TAQUILLAS DE PERSONAL`). La prueba comprueba que el Vigilante ve al jugador desde `(-102.0, 0.12, 38.0)` y pasa a `CHASE`, que el jugador se oculta, que el Vigilante lo pierde y no lo captura durante 2 s, y que puede salir del escondite.

### 6.3.4. Cola de seguridad REC08

```bash
godot --headless --path . tests/fm_queue_chase.tscn
```

Resultado: **`FM_QUEUE_CHASE: PASS (7 PASS / 0 FAIL)`**.

La cola de seguridad de Recepción ocupa un recinto de ~3 × 3 m entre `x≈-89.2..-84.1` y `z≈9.6..13.7`, con belts y stanchions `REC08`. El jugador espera al sur, en `(-87.5,0.12,15)`, y el Vigilante arranca al norte, en `(-87.5,0.12,7.5)`. El ruido lo pone en `INVESTIGATE`; el navmesh lo obliga a rodear la cola, recorre **7,01 m**, se desvía **2,20 m** lateralmente y captura al jugador a **1,23 m**. Capturas: `docs/fm_queue_chase_01..04.png`.

### 6.3.5. Captura durante la extracción

```bash
godot --headless --path . tests/fm_extraction_capture.tscn
```

Resultado: **`FM_EXTRACTION_CAPTURE: PASS (9 PASS / 0 FAIL)`**.

El jugador activa la extracción con el núcleo; el Vigilante arranca a 8 m y lo alcanza durante la secuencia de 4,0 s. La extracción no se completa (`state=LOST`) y vuelve a `waiting`, sin falso WON. También se comprueba que el jugador no está oculto.

No cubre una captura en el último instante ni una partida completa; esas siguen como limitaciones.

### 6.4. Inventario, peso y desmontaje

```bash
godot --headless --path . tests/fm_inventory_smoke.tscn
```

Resultado: **`FM_INVENTORY_TEST: PASS (27 PASS / 0 FAIL)`**.

Cubre:

- Núcleo de misión mediano, recogida a manos, 7,0 kg y drop.
- Puesto de análisis: cancelación al alejarse y desmontaje completado con cuatro componentes.
- Componente pequeño, inventario de 4 ranuras, límite de 12 kg y drop del último guardado.
- Recogida de los cuatro componentes (2,9 kg) y transición real a Recepción.
- Entrega de 4 componentes sin núcleo: bloqueada.
- Entrega de núcleo + 4 componentes: 5 objetos válidos y extracción final.

El detalle de reglas y limitaciones está en `docs/FM_INVENTORY_DISMANTLING.md`.

#### Flujo completo con el Vigilante activo

```bash
godot --headless --path . tests/fm_inventory_flow.tscn
```

Resultado: **`FM_INVENTORY_FLOW: PASS (30 PASS / 0 FAIL)`**.

La prueba recorre el flujo completo sin teletransportar al jugador hasta el puesto:

- Acceso a pie desde el spawn de Z10 por el pasillo hasta el puesto de análisis.
- Interacción a 1,69 m y desmontaje de 0,9 s con ruido periódico.
- El Vigilante, con la visión aislada, oye el ruido y pasa a `INVESTIGATE`.
- Cuatro componentes al inventario (2,9 kg) y núcleo a manos (9,9 kg total).
- Transición real a Recepción y reactivación del Vigilante de Recepción.
- Extracción con 4 componentes + núcleo = **5 objetos válidos**.

No valida una persecución completa durante el desmontaje ni una persecución larga con esquinas; esas siguen siendo limitaciones conocidas.

#### Extracción bajo persecución real

```bash
godot --headless --path . tests/fm_extraction_chase.tscn
```

Resultado: **`FM_EXTRACTION_CHASE: PASS (8 PASS / 0 FAIL)`**.

- El jugador llega a Recepción con el núcleo y entra en la zona de extracción.
- El Vigilante de Recepción se coloca a 7,88 m y pasa a `CHASE`.
- Se acerca a 6,23 m mientras la extracción avanza.
- El jugador no es capturado y la extracción termina con `state=1` y `delivered=1`.
- La prueba usa una persecución inicial; no cubre una persecución larga con obstáculos. El movimiento ya usa navmesh.

### 6.5. Capturas de revisión

```bash
godot --path . tests/fm_vslice_shot.tscn
```

Genera 7 capturas 1280×720 en `docs/`:

| Archivo | Contenido |
|---|---|
| `fm_vslice_z10_spawn.png` | Spawn de Z10, oscuridad, emergencias y conector al fondo. |
| `fm_vslice_z10_hiding.png` | Estanterías y prompt **E ESCONDERSE**. |
| `fm_vslice_z10_core.png` | Núcleo verde y puerta **ENLACE DE SERVICIO · RECEPCIÓN**. |
| `fm_vslice_z10_transition.png` | Puerta de enlace con prompt de interacción. |
| `fm_vslice_z10_watcher.png` | El Vigilante observado, con aviso **EL VIGILANTE ESTÁ INMÓVIL**. |
| `fm_vslice_reception_hall.png` | Hall de Recepción con prácticas cálidas y HUD de objetivo. |
| `fm_vslice_reception_extraction.png` | Aro de extracción y compuerta **SALIDA** provisional. |

En ventana puede aparecer `ERROR: NO GRAB` de X11 si la ventana no tiene foco cuando `FMPlayer` intenta capturar el ratón al arrancar. No impide la captura ni el juego; en esta corrida las 7 imágenes se generaron con `err=0`.

### 6.6. Rendimiento en ventana

```bash
godot --path . tests/fm_vslice_perf.tscn
```

Medición en **NVIDIA GTX 1650 Ti, Vulkan Forward+, 1280×720, VSync off**. Jugador y Vigilante congelados; es una escena jugable estática, **no una partida completa**:

| Zona | FPS (última corrida) | Draw calls | Primitivas | Objetos | Textura VRAM | Vídeo VRAM |
|---|---:|---:|---:|---:|---:|---:|
| Z10 | **255,7** | 1.078 | 654.842 | 5.528 | 561,6 MB | 695,4 MB |
| Recepción | **243,5** | 739 | 321.504 | 5.528 | 561,6 MB | 695,4 MB |

En corridas sucesivas Z10 osciló entre **196 y 256 FPS** y Recepción entre **210 y 244 FPS**; los draw calls se mantuvieron estables. La variación es normal. La escena contiene los dos sectores cargados, pero el frustum y el `far=70` del jugador descartan el sector lejano. La VRAM incluye ambos GLB. No se probó una partida completa con IA activa, físicas y extracción; no debe citarse como FPS final del juego.

#### 6.6.1. Rendimiento de Z10 con IA activa y movimiento real

```bash
godot --path . tests/fm_perf_ai.tscn
```

Medición en ventana a **1280×720**, **VSync desactivado y verificado** (`vsync_ok=true`), `Engine.max_fps=0`, durante **10 s**, con el Vigilante activo (`vision_distance=18`, sin suspensión) y movimiento real del jugador con `Input.action_press`. Hardware: **NVIDIA RTX 5050 Laptop GPU (8 GB)**, driver 595.99.02, Godot 4.7.2 Forward+. No es una partida completa: solo Z10, un jugador y la ruta corta de banco de pruebas.

Última corrida aislada (`FM_PERF_AI: PASS`):

| Métrica | Valor |
|---|---:|
| FPS medio | **401,0** |
| FPS mínimo por frame | **148,6** |
| FPS percentil 1 % | **207,0** |
| Frames | 4.011 en 10,00 s |
| Draw calls (última / máximo) | **1.493 / 1.506** |
| Objetos | **6.473** |
| Textura VRAM | **457,3 MB** |
| Vídeo VRAM | **593,8 MB** |
| Recorrido del jugador | **33,90 m** |

En la corrida integrada final de `tests/run_all.sh`: **457,1 FPS** medio, **203,3 FPS** mínimo, **287,5 FPS** p1 %, **1.494** draw calls, **6.473** objetos, **457,3 MB** de texturas y **593,8 MB** de vídeo. En cuatro corridas aisladas: **383,1–444,3 FPS** medios, **107,1–177,0 FPS** mínimos, **150,9–259,7 FPS** p1 %, **1.492–1.506** draw calls máximos y **6.520–6.550** objetos. El Vigilante pasó por `DORMANT/PATROL/CHASE/SEARCH`, recorrió 2,60 m durante la ventana y no capturó al jugador. Los draw calls oscilaron entre 110 y 1.508 según la dirección de cámara y el frustum; la memoria de texturas/vídeo se mantuvo estable. **No debe citarse como rendimiento del juego completo.**

### 6.7. Ejecución en ventana

```bash
godot --path . scenes/fm/fm_vslice_z10.tscn
```

También se ejecutó la escena 1.800 frames con el Vigilante activo y el jugador quieto: sin errores de script. El único aviso es el leak de `ObjectDB` al forzar la salida, habitual en las pruebas existentes.

---

## 7. Limitaciones conocidas

1. **Un jugador local.** No hay sincronización multijugador, lobby, reconexión ni voz. La arquitectura del jugador y del Vigilante sigue siendo offline.
2. **Sin guardado.** R reinicia la escena completa; no hay checkpoint ni persistencia.
3. **Transición provisional.** Z10 y Recepción no están conectados geométricamente; el enlace es un teletransporte con fundido. Falta el export V06 del nivel completo.
4. **`level1.tscn` sigue obsoleto.** Carga el V05 y no se modificó. El slice actual se abre directamente.
5. **Extracción placeholder.** La compuerta es geometría runtime; no hay ascensor, cabina, puertas animadas ni viaje. Las reglas operativas definitivas de §45 no se inventaron.
6. **Vigilante en Recepción con ruta manual y navmesh runtime.** Se reactiva al cruzar y patrulla 8 waypoints; no es una segunda criatura ni una IA nueva. Puede perseguir al jugador hasta la zona de extracción. El navmesh se hornea al cargar la escena (355 polígonos).
7. **Navmesh limitado al slice.** Cubre Z10 y Recepción a partir de los colliders estáticos; no es un navmesh del nivel completo. El coste del bake no se ha medido en una partida completa y las zonas fuera del slice no están cubiertas.
8. **Inventario y desmontaje en primer pase.** Hay manos para objetos medianos, 4 ranuras/12 kg para pequeños y un puesto de análisis con cuatro componentes. Faltan UI dedicada, volumen, fragilidad, herramientas, desmontaje parcial y el contrato completo de §32.
9. **Sin sistema de estrés.** El HUD muestra `ESTRÉS 0 %`; no se implementó el sistema de §11. No se simula con efectos falsos.
10. **Núcleo provisional.** Usa el visual procedural de `FMCarryItem`, no el arte final del objeto.
11. **Colisiones automáticas.** `FMGLBCollision` genera 277 + 151 shapes; los props bajos de 4 cm pueden frenar al `CharacterBody` si se sale de la ruta probada. No hay step-up; el navmesh cubre el slice.
12. **HUD fijo a 1280×720.** No se adaptó a otras resoluciones en este pase.
13. **Partida completa automatizada, no humana.** `fm_full_run` cubre IA, físicas, desmontaje y extracción en 45 s, pero el bot usa observación/strafe y no valida entrada humana ni una captura durante ese recorrido. El rendimiento con IA se midió 10 s en Z10, no en la partida completa ni en Recepción.
14. **El escondite no modela luz, respiración ni inspección.** Mientras `hidden` es true, El Vigilante lo ignora como objetivo; puede investigar la zona y esperar fuera, pero no abrir el escondite. La linterna puede quedar encendida sin penalización.
15. **Sin recuperación automática del núcleo** si queda atrapado detrás de geometría; R reinicia la escena. El objeto sí vuelve a su posición inicial si cae por debajo de `y=-4`.
16. **No se tocaron** los GLB, las escenas de arte, `level1.tscn`, `fotos-referencia/`, el menú ni el guardado. No hay commit.

---

## 8. Siguiente trabajo recomendado

1. Revisar visualmente las 7 capturas y aprobar la dirección de Z10/Recepción con la linterna como fuente principal.
2. Decidir el diseño del enlace real Z10 ↔ Recepción (montacargas de servicio, conector V06 o carga de sector) antes de sustituir el teletransporte.
3. Exportar/validar el V06 del nivel completo y decidir si `level1.tscn` se actualiza o se conserva como referencia.
4. Sustituir la compuerta placeholder de extracción por la cabina/ascensor definitivos y conectar la secuencia visual.
5. Probar persecuciones largas con esquinas, obstáculos y escondites sobre el navmesh actual, y ampliar la cobertura del navmesh al nivel completo.
6. Incorporar el núcleo con arte final y ampliar el inventario/peso/desmontaje: UI, volumen, fragilidad, herramientas y desmontaje parcial.
7. Implementar el sistema de estrés real o retirar su indicador del HUD.
8. Ampliar la medición de rendimiento a la partida completa (Z10 + Recepción, extracción y audio) y repetirla en el hardware objetivo; la partida completa automatizada con IA ya está cubierta por `fm_full_run`.
9. Solo después: sincronización multijugador con autoridad del servidor y guardado.

---

## 9. Skills aplicadas

- `godot-3d-essentials`: composición de escena 3D, cámaras, environment y luces.
- `godot-gdscript`: tipado, ciclo de vida, señales y `await`.
- `godot-physics`: CharacterBody, Area3D, raycasts y capas.
- `game-ai`: FSM y separación decisión/movimiento del Vigilante existente.
- `performance-optimization`: medición con monitores de Godot y lectura de draws/primitivas/VRAM.
- `verification-before-completion`: pruebas ejecutadas y resultados citados antes de declarar el estado.

No se usaron skills de Blender porque no se creó ni modificó ningún asset en Blender. La compuerta y la puerta de enlace son geometría runtime provisional, documentada como tal. `level-design` no se aplicó porque la arquitectura existente no se reorganizó; solo se colocaron anclas de gameplay sobre ella.

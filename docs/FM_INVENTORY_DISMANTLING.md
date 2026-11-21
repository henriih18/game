# FRECUENCIA MUERTA — Inventario, peso y desmontaje (primer pase)

Fecha: 2026-11-12. Estado: **primer pase jugable local, probado headless; sin commit**.

Este documento describe el primer pase de inventario, peso y desmontaje del vertical slice Z10 → Recepción. No sustituye el diseño definitivo de las secciones 32, 43, 44, 45 y 46 de `AGENTS.md`; valida el bucle mínimo de recogida, transporte, riesgo y entrega con los sistemas existentes.

## 1. Objetivo

Demostrar que el jugador puede:

1. Transportar un objeto de misión mediano con las manos.
2. Guardar componentes pequeños en un inventario limitado.
3. Ver el efecto del peso en la movilidad y en el HUD.
4. Desmontar un puesto de análisis con tiempo y ruido, cancelando si se aleja.
5. Entregar el objeto de misión y los componentes en la extracción sin duplicar recompensas.

## 2. Reglas implementadas

### 2.1. Manos y mochila

- **Objetos medianos/grandes:** se transportan en las manos (`player.carried_item`). Ocupan el ancla de la cámara y reducen la velocidad al 58 % (72 % agachado).
- **Objetos pequeños:** se guardan en `player.inventory`. El inventario tiene **4 ranuras** y un límite de **12,0 kg**.
- **Peso:** `get_carry_weight()` suma la mano y el inventario. El exceso de carga reduce la velocidad gradualmente hasta el 82 % con el inventario lleno.
- **Soltar:** `Q` suelta primero el objeto en manos; si las manos están libres, suelta el último componente guardado.
- **Recoger:** `E` guarda el objeto pequeño más cercano con línea de visión; si es mediano, lo pasa a las manos. Si el inventario está lleno o el peso excede el máximo, se muestra el aviso correspondiente.

### 2.2. Desmontaje

- El puesto de análisis de Z10 está en `DISMANTLE_POSITION = (51.2, 0.0, -17.2)`.
- Mantener `E` inicia un desmontaje de **6,0 s**. El jugador puede cancelarlo pulsando `E` de nuevo o alejándose más de **3,6 m**.
- Durante el desmontaje se emite ruido cada **1,0 s** con radio **8,0 m**, audible por El Vigilante según su sistema existente.
- Al completar se liberan cuatro componentes pequeños:
  - `MUESTRA A` — 0,6 kg
  - `MUESTRA B` — 0,8 kg
  - `NÚCLEO SECUNDARIO` — 1,2 kg
  - `DOCUMENTO TÉCNICO` — 0,3 kg
- El puesto no se puede volver a desmontar. Los componentes se registran en `carry_items` y se pueden recoger, guardar, soltar y entregar.
- El puesto es un prototipo de mecánica; no representa todavía el contrato completo de desmontaje por componentes de §32.

### 2.3. Extracción

- `FMCarryItem` distingue `is_mission_item`. Solo el núcleo tiene `is_mission_item = true`.
- `FMReceptionExtraction` exige:
  - al menos un objeto válido dentro del radio de entrega;
  - la misión entregada (`has_delivered_mission_item`);
  - todos los jugadores vivos dentro de la zona.
- `get_delivered_loot_count` cuenta el inventario y el objeto en manos del jugador cuando está dentro de la extracción, además de los objetos físicos dentro del radio.
- La recompensa se contabiliza por instancia (`get_instance_id`), sin duplicar el mismo objeto.
- Los componentes solos no completan la extracción: falta el núcleo de misión.
- El subtítulo final indica `Núcleo asegurado · N objeto(s) válido(s)`.

## 3. Archivos

**Nuevos**
- `scripts/fm/fm_dismantlable.gd`
- `tests/fm_inventory_smoke.gd` + `.tscn`
- `docs/FM_INVENTORY_DISMANTLING.md`

**Modificados**
- `scripts/fm/fm_carry_item.gd` — tamaño, tipo, misión, visual de componente, `stow`/`unstow`, ruido de inventario y radios de ruido.
- `scripts/fm/fm_player.gd` — inventario, capacidad, peso, multiplicador de velocidad, recogida automática, drop de inventario y prompts.
- `scripts/fm/fm_vslice_z10.gd` — puesto de análisis, registro de componentes, conteo de inventario, misión entregada, HUD de carga y mensajes.
- `scripts/fm/fm_reception_extraction.gd` — exigir misión entregada.
- `scripts/fm/fm_hud.gd` — indicador de carga.
- `tests/run_all.sh`, `tests/README.md`, `docs/CURRENT_STATE.md`, `docs/FM_VERTICAL_SLICE.md`.

No se tocaron los GLB, las escenas de arte, `level1.tscn`, `fotos-referencia/` ni el `.blend`.

## 4. Verificación

```text
fm_inventory_smoke  → 27 PASS / 0 FAIL
fm_inventory_flow   → 30 PASS / 0 FAIL
fm_extraction_chase →  8 PASS / 0 FAIL
fm_vslice_smoke     → 52 PASS / 0 FAIL
fm_vslice_walk      → 16 PASS / 0 FAIL
fm_vslice_chase     →  9 PASS / 0 FAIL
fm_narrative_smoke  → 75 PASS / 0 FAIL
```

El test de inventario cubre:

- Núcleo de misión mediano, recogida a manos y peso de 7,0 kg.
- Drop del núcleo.
- Desmontaje cancelado al alejarse y desmontaje completado tras 0,6 s de prueba.
- Componente pequeño, inventario con 1 ranura, capacidad llena y límite de peso.
- Drop del último componente guardado.
- Recogida de los cuatro componentes (2,9 kg) y transición real a Recepción.
- Conteo de 4 componentes en la extracción sin misión.
- Extracción bloqueada sin núcleo.
- Entrega de núcleo + 4 componentes = 5 objetos válidos y activación final.
- Flujo completo con el Vigilante activo: acceso a pie, ruido que lo atrae a `INVESTIGATE`, cuatro componentes al inventario, núcleo a manos, transición real y extracción con 5 objetos.
- Extracción bajo persecución real: el Vigilante pasa a `CHASE`, se acerca de 7,88 m a 6,23 m y el jugador completa la entrega antes de ser capturado (`8 PASS`).

## 5. Limitaciones

1. El inventario no tiene UI dedicada; solo el indicador de carga del HUD.
2. No hay volumen, fragilidad, rareza, valor económico ni estado de conservación.
3. El desmontaje no tiene herramientas, piezas frágiles, desmontaje parcial ni componentes específicos por objeto.
4. El puesto de análisis es un prototipo con cuatro componentes fijos; no está integrado en el GLB ni en el arte final.
5. El ruido del desmontaje está probado con el Vigilante en `INVESTIGATE`; la persecución real se probó por separado durante la extracción, no durante el desmontaje.
6. No hay persistencia ni sincronización multijugador del inventario.
7. El objeto de misión sigue usando el visual procedural existente del núcleo.
8. No se ha medido el coste de rendimiento del puesto y los componentes en una partida completa.
9. La extracción bajo persecución está probada con una persecución inicial de 7,88 m a 6,23 m; no cubre persecuciones largas, esquinas, obstáculos ni captura justo antes de la entrega.

## 6. Siguiente trabajo

1. Validar el desmontaje con una persecución real (sin aislar la visión) y medir si el ruido genera una persecución durante la extracción.
2. Añadir UI de inventario y selección de objeto guardado.
3. Introducir volumen/fragilidad y herramientas de desmontaje.
4. Integrar el sistema con la extracción definitiva y la recompensa única.
5. Llevar el inventario a multijugador con autoridad del servidor.

Sin commit.

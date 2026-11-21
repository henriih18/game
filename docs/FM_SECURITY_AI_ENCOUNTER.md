# FRECUENCIA MUERTA — IA y encuentro de Seguridad

**Fecha:** 2026-11-16
**Sala:** Seguridad 03 (Z03) y conector sur
**Estado:** ajuste implementado y probado

## 1. Objetivo

Adaptar el segundo Vigilante a la apertura del acceso principal de Seguridad.
Antes del cambio, el único acceso utilizado por la IA era el pasillo de servicio
de 1,4 m (capa 2). Al abrirse el conector sur y añadirse el `NavigationLink3D`
de capa 1, el Vigilante de Seguridad podía entrar y salir de la sala, pero su
patrulla seguía confinada al interior. Este pase convierte esa sala en un
encuentro que puede desbordar al corredor.

No se ha modificado geometría, iluminación, GLB ni el máster de Blender.

## 2. Cambios

### 2.1 Patrulla con salida al corredor

`scripts/fm/fm_level1_v06.gd` — `_setup_security_watcher()`:

- La patrulla pasa de 6 puntos interiores a **9 puntos**.
- La ruta rodea el mostrador del checkpoint por el este, cruza la puerta sur,
  entra en el conector y alcanza el corredor principal. Después regresa.
- Puntos (coordenadas Godot):
  1. `(-84, 0.12, -23)`
  2. `(-84, 0.12, -13.5)`
  3. `(-85.5, 0.12, -11)`
  4. `(-89, 0.12, -8)`
  5. `(-89, 0.12, -2.5)`
  6. `(-85, 0.12, -2.5)`
  7. `(-85.5, 0.12, -11)`
  8. `(-84, 0.12, -23)`
  9. `(-88, 0.12, -23)`
- El primer punto no coincide con el spawn, de modo que
  `activate_in_sector()` inicia el movimiento de inmediato.
- Todos los segmentos están validados sobre `NavigationMain` (capa 1), con
  destino final a menos de 0,25 m del punto pedido.

### 2.2 Escondite en las taquillas de Seguridad

`scripts/fm/fm_level1_v06.gd` — `_setup_hiding_spots()`:

- Nuevo `HideSecurityLockers` en `(-78.4, 0.05, -11.85)`, junto al banco de
  taquillas de la pared sur.
- Nombre visible: **TAQUILLAS DE SEGURIDAD**.
- Es un `FMHidingSpot` (Area3D + HidePoint/ExitPoint). No añade geometría ni
  colisión física; reutiliza el banco de taquillas existente.
- El punto de salida queda 1,25 m hacia el interior de la sala.

## 3. Pruebas

| Prueba | Resultado |
|---|---|
| `tests/fm_level1_v06_smoke.tscn` | **411 PASS / 0 FAIL** |
| `tests/fm_level1_v06_gameplay.tscn` | **108 PASS / 0 FAIL** |
| `tests/fm_full_run.tscn` | **49 PASS / 0 FAIL** |
| `tests/fm_graphics_presets_smoke.tscn` | **194 PASS / 0 FAIL** |
| `tests/fm_level1_v06_perf.tscn` 1280×720 | **PASS** |

Comprobaciones nuevas:

- Tamaño de patrulla = 9.
- La patrulla contiene puntos dentro de Seguridad y en el corredor.
- Cada segmento tiene ruta de capa 1 y termina en el destino.
- El Vigilante avanza más de 0,5 m en la prueba física (2,72 m medidos).
- El escondite de Seguridad existe, tiene el nombre correcto y está en la
  posición esperada.

Perf 1280×720 con ventana: **447,6 fps medios**, mínimo 134,8, p1 171,2,
p99 5,84 ms, 0 frames por encima de 16,7 ms. La fase `security_access` es la
más costosa (219,9 fps medios, 7,42 ms máx.). La IA de Seguridad se movió
8,31 m durante la prueba y permaneció en PATROL.

## 4. Archivos

- Modificados:
  - `scripts/fm/fm_level1_v06.gd`
  - `tests/fm_level1_v06_smoke.gd`
  - `tests/fm_level1_v06_gameplay.gd`
  - `AGENTS.md`
- Nuevos:
  - `docs/FM_SECURITY_AI_ENCOUNTER.md`

## 5. Limitaciones

- No se añade una secuencia guionizada nueva (alarmas, cierre de puertas o
  diálogos). El encuentro sigue siendo emergente: patrulla, oye ruido,
  investiga, persigue y puede salir al corredor.
- El escondite es una zona abstracta de interacción; no se ha modelado un
  interior de taquilla dedicado.
- El Vigilante puede abandonar Seguridad durante la persecución. Es
  intencionado, pero no hay un sistema de retorno automático si el jugador
  desaparece; vuelve a su patrulla por la ruta de navegación.
- No se ha tocado la geometría ni los GLB de Seguridad en este pase.

## 6. Skills usadas

- `game-ai`: FSM existente, percepción, patrulla y persecución.
- `level-design`: recorrido, encuentro y cobertura.
- `scenario-godot-3d-world`: navegación y validación en Godot.
- `writing-plans`: planificación del cambio acotado.

No se usaron skills de Blender porque no se modificó geometría.

## 7. Siguiente paso

Verticalidad NWStair/StairsMain, pase visual global y optimización medida de
texturas/materiales/LOD. Sin commit hasta autorización del usuario.

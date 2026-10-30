# FRECUENCIA MUERTA — Vertical slice offline

Estado: **primera versión jugable**, offline y de un solo jugador. No es la versión final
ni tiene red.

## Objetivo

Validar el bucle mínimo de terror y extracción:

1. Entrar en el corredor.
2. Localizar el núcleo en el laboratorio.
3. Recogerlo y transportarlo.
4. Evitar a El Vigilante.
5. Usar un escondite si hace falta.
6. Llegar a la extracción con el núcleo.

Sin armas, sin combate y sin posibilidad de matar a la criatura.

## Cómo abrir

Desde el menú: **ENTRAR A LA INSTALACIÓN**.

Desde terminal:

```bash
godot --path ~/Documentos/game -- --slice
```

O directamente:

```bash
godot --path ~/Documentos/game scenes/fm/vertical_slice.tscn
```

## Controles

| Acción | Tecla |
|---|---|
| Mover | WASD |
| Mirar | Mouse |
| Correr | Shift |
| Agacharse | Ctrl |
| Interactuar / recoger / esconderse / salir | E |
| Soltar el núcleo | Q |
| Linterna | F |
| Volver al menú | Esc |
| Silenciar audio | M |

## Sistemas implementados

- **Jugador FP modular** (`scripts/fm/fm_player.gd`): movimiento, sprint con
  resistencia, crouch, cámara, linterna con batería, interacción por línea de vista,
  transporte y escondites.
- **Núcleo físico** (`scripts/fm/fm_carry_item.gd`): `RigidBody3D`, masa, caída y ruido
  al soltarse; mientras se transporta se congela y sigue un ancla del jugador.
- **El Vigilante** (`scripts/fm/fm_watcher.gd`): patrulla, investiga ruido, persigue,
  busca y se detiene cuando el jugador lo observa. No se puede matar.
- **Escondites** (`scripts/fm/fm_hiding_spot.gd`): dos armarios; entrar y salir con E.
- **Extracción** (`scripts/fm/fm_extraction.gd`): completar la partida con el núcleo.
- **HUD** (`scripts/fm/fm_hud.gd`): objetivo, batería, estrés, resistencia, avisos,
  viñeta y pantalla de fin.
- **Escenario** (`scripts/fm/vertical_slice.gd`): corredor, laboratorio, tanque,
  puerta de seguridad, luces, niebla, polvo y props con colisión.
- **Audio y atmósfera**: música existente, pasos, recogida, caída, escondite y
  extracción; sin audio 3D ni voz todavía.

## Pruebas

```bash
godot --headless --path . tests/fm_slice_smoke.tscn
```

Cubre jugador, Vigilante, núcleo, extracción, escondites, HUD, observación,
recogida, esconderse/salir, linterna inicial y victoria. Resultado actual: **15/15 PASS**.

## Limitaciones

- Offline y de un solo jugador.
- Sin red, sin voz, sin Imitador y sin herramientas.
- El Vigilante y el núcleo usan geometría procedural provisional.
- No hay inventario, base, progresión ni misiones.
- El escenario es un blockout con materiales de Fase 2, no arte final.
- Los avisos de recursos al cerrar los tests son de la salida forzada.

## Siguiente paso

Pulir el vertical slice y después llevar la arquitectura a red 3D host-autoritativa.
No se deben meter RPCs dentro del controlador de movimiento; la intención del jugador
debe enviarse a un servidor que valide interacciones, criatura, núcleo y extracción.

# FM — Jugador Nomad: rig preparado para animar

Fecha: 2026-11-20
Estado: COMPLETADO (rig base FK, 10 acciones originales conservadas)
Commit: no realizado (pendiente de autorización)

## Objetivo

Dejar el modelo Nomad listo para animar sin modificar el modelado, las UVs ni
las texturas. Se conserva el rig original de 70 huesos y las 10 animaciones
importadas.

## Archivos

- Maestro: `objetos-modelados/personaje-jugador/nomad_player/nomad_player_master.blend`
- Fuente escalada: `objetos-modelados/personaje-jugador/nomad_player/nomad_source_scaled.blend`
- GLB original: `objetos-modelados/personaje-jugador/J5M9KWMM50LO3XYUFSFKI2ZYO_Multi-Animations/J5M9KWMM50LO3XYUFSFKI2ZYO.glb`
- Contact sheet de validación: `docs/FM_NOMAD_PLAYER_RIG_CONTACT.png`
- Rig antiguo horneado (NO usar): `objetos-modelados/personaje-jugador/nomad_player/nomad_player_rig.blend`

## Datos del asset

- Malla: 11.095 verts, 14.996 tris, 44.988 loops.
- UVs: `UVMap` (sin cambios).
- Materiales: BackpackMat, GlovesMat, HeadMat, PantsMat, TorsoMat.
- Vertex groups: 70 (sin cambios).
- Rig: 70 huesos deform, FK, quaternion, sin constraints.
- Altura: 2,076 m. FPS: 24.
- Acciones: Idle (0–240), Walking (0–24,8), Walk - Normal (0–54,4),
  Running (0–20), Dodge_Normal_Step_05 (0–91,2), KneelStand (0–668,8),
  ArchM (0–161,6), Fight Excited (0–217,6), Greeting Big Wave (0–123,2),
  Taunt Dance Loop (0–71,2).

## Cambios aplicados

1. **Rest y suelo.** Se levantó el empty `Node_72` 1,09089 m en Z (total
   1,11475) para que la rest pose quede apoyada en Z=0. La malla no se tocó.
2. **Grounding por acción.** Cada una de las 10 acciones se desplazó en Z
   mediante su curva de `location` de objeto para que su punto más bajo
   toque Z=0. Se conserva el movimiento horizontal y la pose de huesos.
3. **Acciones autocontenidas.** Se añadieron claves de rotación (identidad)
   y localización (0) a todos los huesos que no estaban animados en cada
   acción. Todas las acciones tienen ahora 497 fcurvas (70 huesos × 7 +
   7 del objeto), de modo que cambiar de acción no arrastra poses.
4. **Organización.** Bone collections: Root (1), Spine (7), Arms (10),
   Hands (2), Fingers (38), Legs (8), Feet (4).
5. **Viewport.** Se quitaron las custom shapes de 2 m (`Icosphere`) y se
   ocultó el objeto. El rig se muestra en octal. `SHOTCAM` queda oculta.
6. **Metadatos.** Acciones con fake user y NLA muteada. `Idle` activa en
   frame 0. Escena 24 fps, rango 0–240, unidades métricas 1.0.

## Validación

- Firma de malla idéntica a la fuente: vértices, polígonos, loops, UVs,
  materiales, vertex groups y pesos. Sin shape keys.
- `Idle` al abrir el maestro: Z mínimo **0,000611 m**, máximo 2,076421 m.
- Mínimos Z por acción (inicio / medio / fin):
  - Idle: 0,00061 / 0,00117 / 0,00061
  - Walking: 0,01924 / 0,02270 / 0,01924
  - Walk - Normal: 0,00529 / 0,00404 / 0,00529
  - Running: 0,02285 / 0,04127 / 0,02292
  - Dodge_Normal_Step_05: 0,00055 / 0,01828 / 0,00074
  - KneelStand: 0,02716 / 0,20049 / 0,02717
  - ArchM: 0,01008 / 0,00278 / 0,01409
  - Fight Excited: 0,02099 / 0,00603 / 0,02097
  - Greeting Big Wave: 0,00591 / 0,00111 / 0,00597
  - Taunt Dance Loop: 0,01434 / 0,01489 / 0,01262
- Cambio de acción sin reset (Idle → Running → Idle → Greeting → Idle):
  los mínimos Z se mantienen; no hay contaminación de pose.
- Render EEVEE de las 10 acciones con suelo y cámara:
  `docs/FM_NOMAD_PLAYER_RIG_CONTACT.png`.

## Limitaciones conocidas

- El rig es **solo FK**; no se añadieron IK, pole targets ni huesos de
  control. La rest original importada no es una A-pose simétrica y mira a
  +Y, mientras las acciones miran a −Y; se conserva tal cual para no romper
  las 10 acciones.
- Las acciones combinan animación de objeto (`location`,
  `rotation_quaternion`) y del hueso `rootx`. Es el resultado del GLB
  original.
- No hay malla/rig de brazos en primera persona, sockets de props ni
  sistema de emotes en Godot.
- No se ha exportado el rig a GLB ni probado en Godot en esta fase.
- El archivo `nomad_player_rig.blend` (14:02) es un horneado anterior con
  errores de rebind; no debe usarse como maestro.

## Siguiente paso recomendado

1. Añadir una capa de controles IK para piernas y brazos (influencia 0 por
   defecto) y un interruptor FK/IK, sin tocar la malla.
2. Crear brazos FP, sockets `hand_r`, `hand_l`, `chest_radio`,
   `chest_flashlight`, `backpack` y props.
3. Exportar GLB con huesos deform y las 10 acciones, e importar en Godot
   4.7.2 para validar animaciones, root motion y máquina de estados.
4. Definir el sistema de emotes y la sincronización multijugador.

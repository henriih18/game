# FM — Jugador Nomad: capa FP y props

Fecha: 2026-11-20
Estado: PROTOTIPO FUNCIONAL (cuerpo listo; vista FP final pendiente)
Commit: no realizado (pendiente de autorización)

## Decisiones del usuario

- El juego es en primera persona.
- La linterna debe ir en la mano derecha.
- La radio va en el pecho.
- La animación base para clips nuevos es `Idle` frame 0.
- No tocar malla, UVs ni texturas del Nomad.

## Archivos

- Maestro del cuerpo: `objetos-modelados/personaje-jugador/nomad_player/nomad_player_master.blend`
- Escena FP: `objetos-modelados/personaje-jugador/nomad_player/nomad_fp_player.blend`
- Linterna: `objetos-modelados/linterna.glb`
- Radio: `objetos-modelados/radio.glb`
- Validación: `docs/FM_NOMAD_FP_BODY.png`, `docs/FM_NOMAD_FP_GRIP.png`,
  `docs/FM_NOMAD_FP_RADIO.png`
- Rig del cuerpo: `docs/FM_NOMAD_PLAYER_RIG.md`

## Props

### Linterna (`linterna.glb`)

- 315.116 vértices / 246.614 tris.
- Eje largo local Y; lente en +Y.
- Escala aplicada: 0,30.
- Dimensiones finales: 0,29744 × 0,29989 × 0,07861 m.
- Sin edición de topología.

### Radio (`radio.glb`)

- 171.848 vértices / 131.068 tris.
- Eje largo local Z; pantalla hacia −Y.
- Escala aplicada: 0,25.
- Dimensiones finales: 0,10044 × 0,05646 × 0,24989 m.
- Sin edición de topología.

## Escena FP

`nomad_fp_player.blend` conserva la malla completa del cuerpo (11.095 v /
14.996 tris) con la misma firma que el maestro: vértices, UVs, materiales
y pesos idénticos.

- Armadura `root`: 76 huesos, 70 deform + 6 sockets no-deform.
- Sockets: `socket_hand_r` (hijo de `handr`), `socket_hand_l`, `socket_chest_radio`
  y `socket_chest_flashlight` (hijos de `spine_02x`), `socket_backpack`
  (`spine_03x`) y `socket_camera` (`headx`). `inherit_scale='NONE'`.
- `FP_Arms`: 1.626 v / 2.399 tris, copia de brazos completa; oculta.
- `FP_Forearms`: 1.249 v / 1.815 polys, copia sin brazo superior; visible
  para pruebas de vista FP.
- `FP_Flashlight`: parentada al hueso `socket_hand_r`, centro
  (−0,1965, −0,6337, 1,3935), escala 0,30.
- `FP_Radio`: parentada al hueso `socket_chest_radio`, centro
  (−0,1, −0,24, 1,36), escala 0,25.
- `FP_Beam`: spot hijo de `FP_Flashlight`, en la lente.
- `FP_Grip_Idle`: acción 0–240, 710 fcurvas, un slot, fake user, cyclic;
  puño horneado en frames 0/240 con claves de los 70 huesos y del objeto.
- Acciones del cuerpo: las 10 originales siguen presentes.
- 24 fps. Colecciones `FP_Player`, `FP_Preview`, `Reference_Hidden`.

## Grip y apuntado

- Pose de puño tomada de `Fight Excited` frame 104.
- 16 cuaterniones aplicados a `handr`, `thumb1r/2r/3r`,
  `index1_baser/1r/2r`, `middle1_baser/1r/2r`, `ring1_baser/1r/2r`,
  `pinky1_baser/1r/2r`.
- Variante de palma e: centro `wrist + HY*0.06 + HZ*(−0.04)`.
  `FLASH_CENTER = (−0,19459, −0,62614, 1,39646)`.
- La muñeca `handr` se rotó en las claves 0/240 con el cuaternión local
  `(0,97041, −0,09536, −0,16204, 0,15149)` para apuntar la linterna a
  `(−0,1499, −0,9592, −0,2398)`.
- Resultado: linterna en `(−0,1965, −0,6337, 1,3935)`, beam en
  `(−0,2197, −0,7824, 1,3564)`.

## Validación

- Firma de malla de `nomad_fp_player.blend` idéntica al maestro:
  11.095 v, 14.996 tris, `UVMap`, 5 materiales, mismos hashes de vértices
  y UVs.
- `FP_Flashlight` parent `root` / bone `socket_hand_r`; dimensiones
  correctas.
- `FP_Radio` parent `root` / bone `socket_chest_radio`; dimensiones
  correctas.
- `FP_Grip_Idle` (0–240, 710 fcurvas, 1 slot).
- Render de cuerpo completo: `docs/FM_NOMAD_FP_BODY.png`.
- Detalle del puño y la linterna: `docs/FM_NOMAD_FP_GRIP.png`.
- Detalle de la radio en el pecho: `docs/FM_NOMAD_FP_RADIO.png`.

## Limitaciones

- La vista FP final (viewmodel en primera persona) **no está cerrada**.
  El brazo real recortado produce un tubo hueco en el codo, una mano
  gigante o un cuff facetado; las cámaras a altura de ojo no encuadran
  bien la linterna. Se probaron `FP_Forearms`, `FP_Arms`, rolls −90..90,
  viewmodel estático, mano+cuff y pivote en la muñeca sin un resultado
  comercial.
- La escena FP es un prototipo de props/sockets/pose; el cuerpo completo
  se usa para validar el montaje en tercera persona.
- La radio en la vista FP puede quedar fuera de encuadre o tapar la
  linterna; conviene ocultarla en la cámara FP o usar una capa separada.
- No se ha exportado el rig a GLB ni probado en Godot 4.7.2.
- No hay sistema de emotes, animaciones FP nuevas ni sincronización
  multijugador.

## Siguiente paso recomendado

1. Crear un viewmodel FP dedicado de mano/guante con manga cerrada y
   topología limpia; montar la linterna en el hueso de la mano.
2. Animar el viewmodel (sway, bob, recarga de linterna) y la capa FP
   desde `FP_Grip_Idle`.
3. Definir la cámara FP y la capa de render (brazos FP, props y cuerpo
   separados).
4. Exportar GLB y probar en Godot 4.7.2.
5. Añadir la mano izquierda de apoyo, el sistema de emotes y la
   sincronización multijugador.

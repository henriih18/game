# FRECUENCIA MUERTA — Anclajes narrativos del vertical slice Z10 → Recepción

Fecha: 2026-11-12. Estado: **implementado y probado en headless; sin commit**.

Este pase añade ocho anclajes narrativos (N1, N2, N3, N4, N5, N6, N7, N8) al vertical slice
existente. No modifica los GLB, las escenas de arte, `level1.tscn`, los `.blend`
ni `fotos-referencia/`. No añade armas, combate, colisiones, luces ni
interactables.

---

## 1. Arquitectura

`Narrative` es un `Node3D` **hermano** de `Z10Art` y `ReceptionArt`, nunca hijo.
`FMGLBCollision.build()` recorre los GLB de arte y añadiría colisiones a
cualquier malla colocada dentro de ellos; el nodo narrativo queda fuera de ese
recorrido.

```text
FMVSliceZ10 (Node3D, fm_vslice_z10.gd)
├── Z10Art
├── ReceptionArt
└── Narrative (fm_narrative_props.gd)
    ├── N1_ReceptionCounter
    ├── N2_WaitingArea
    ├── N3_StaffLockers
    ├── N4_SecurityControl
    ├── N5_EntranceThreshold
    ├── N6_CentralCorridorTrail
    ├── N7_ExtractionDecon
    └── N8_ServiceLink
```

Cada raíz está en el grupo `fm_narrative` y lleva
`set_meta("narrative_id", "N1"…)`, además de
`set_meta("narrative_sector", "RECEPTION")` o `"Z10"` según el sector.

Solo se usan `Node3D`, `MeshInstance3D` y `Label3D`. No hay
`StaticBody3D`, `CollisionShape3D`, `Area3D` ni `Light3D` bajo `Narrative`.

---

## 2. Anclajes

| ID | Raíz (x, y, z) | Sector | Distancia a la ruta | Contenido principal |
|---|---|---|---:|---|
| N1 | `(-102.2, 1.04, 13.6)` | Recepción | 9,65 m | Terminal CHECK-IN, registro de visitas, bandeja de badges, café, silla volcada |
| N2 | `(-109.5, 1.02, 22.0)` | Recepción | 16,50 m | Maleta, mochila, abrigo sobre el banco, revista, taza, anillo de café y mancha en la alfombra |
| N3 | `(-106.0, 1.10, 39.5)` | Recepción | 12,39 m | Taquilla abierta con uniforme, tarjeta, llave, foto, nota «NO SALGAS POR RECEPCIÓN» y puerta caída |
| N4 | `(-84.0, 1.06, 10.8)` | Recepción | 6,39 m | Monitor CCTV muerto, libreta, radio, badge DENEGADO, cinta cortada, silla |
| N5 | `(-90.0, 1.4, 8.05)` | Recepción | 4,95 m | Dos paños de vidrio existentes con huellas, grietas, lanyard/badge, cinta de cuarentena y sangre seca |
| N6 | `(-97.5, 0.02, 28.5)` | Recepción | 5,02 m | Rastro de arrastre, guante, maletín de muestras, vial, radio con LED y linterna |
| N7 | `(-99.0, 0.02, 37.0)` | Recepción | 5,04 m | Carro de decon, traje hazmat, portapapeles, cartel y cajas de muestras |
| N8 | `(67.8, 1.2, -23.4)` | Z10 | 2,43 m | Estante, registro de turno, blíster de pilas vacío, nota «NO CONFÍES EN LA RADIO», radio muerta y huella en la puerta |

Comprobaciones espaciales:

- La distancia 2D de cada raíz a su polilínea jugable es mayor de 1,2 m:
  `(-90,13) → (-93,16.5) → (-93,24) → (-92,32) → (-94,36.4)` en Recepción y
  `(47,-22) → (67.4,-21)` en Z10.
- N1, N2, N3, N4, N5, N6 y N7 están dentro de `x -110.25..-69.84`, `z 3.81..40.15`.
  N8 está dentro de `x 39.6..70.5`, `z -30.6..-6.6`.
- El centro de extracción `(-94, 37.6)` y su radio de 2,4 m quedan libres: el
  carro y el traje están al oeste y las cajas de muestras al este. N3 queda a
  12,39 m del eje y no invade la compuerta.
- En N5 el centro `x=-90..-88` queda libre; las huellas, cinta y sangre están
  sobre los paños o al oeste del paso.
- En N7 el grupo `SampleContainersEast` es hijo local en `x=+10` (mundo `-89`).
- N6 mantiene todo el conjunto al oeste de `x=-96`, lejos de la ruta `x=-93`.
- N2 ocupa el hueco entre los bancos y la mesa existente, al oeste de la ruta.
- N8 ocupa la pared norte del enlace y la hoja oeste de la puerta; el pasillo
  `z=-21` y el eje de interacción quedan libres.

---

## 3. Reutilización y materiales

Mallas reales de Recepción reutilizadas mediante nuevas `MeshInstance3D` que
comparten el mesh importado (no se duplica ni se modifica el GLB):

- `REC10_CLIPBOARD`: registro de visitas, libreta de seguridad y portapapeles de decon.
- `REC10_PAPER_00`, `REC10_PAPER_01`, `REC10_PAPER_02`, `REC10_PAPER_09`: papeles.
- `REC06_CHAIR_HERO`: silla volcada de recepción.
- `REC07_SECURITY_CHAIR_HERO`: silla volcada de seguridad.
- `DET_Z10_LockerDoor`: puerta caída de N3, reutilizada desde Z10.

Las piezas nuevas son geometría runtime (`BoxMesh`, `CylinderMesh`, `CapsuleMesh`,
`SphereMesh`, `TorusMesh`) con `StandardMaterial3D` PBR local: acero, plástico,
papel, tela, cuero, uniforme, caucho, cerámica, sangre seca y cristal.

Pase de materiales (2026-11-12): se reutilizan tres sets PBR existentes del
proyecto (`metal_panel`, `rust` y `rubber`) en cuatro materiales (`steel`,
`steel_dark`, `steel_worn`, `rubber`), con albedo, normal y roughness. El resto
de superficies recibe **16 micro-normales de ruido procedural** para tela,
cuero, papel y plástico. Todas usan `uv1_triplanar` y filtro anisotrópico con
mipmaps, de modo que no hace falta unwrap manual de las primitivas. No se crean
texturas nuevas ni se modifican los GLB; el coste medido es +5,2 MB de VRAM.
Los materiales emisivos de pantallas y LEDs se mantienen sin cambios.

Los rótulos usan `Label3D` (`CHECK-IN`, `BADGES`, `DENEGADO`, `CUARENTENA`,
`CCTV-03`, `DECON NIVEL 1`, `MUESTRAS NEXUS`). Las pantallas y LEDs usan
materiales emisivos de baja energía; no son luces y no iluminan la escena.

Decales:

- Manchas y rastros del suelo son cajas finas a 0,0085–0,012 m sobre la
  superficie, con material rojo oscuro.
- Huellas y grietas de N5 están a 0,006–0,008 m delante del vidrio existente
  (`z=8.02`), sin z-fighting.
- La sangre seca se concentra al oeste del umbral y en N6; no invade el eje.

---

## 4. Prueba

```bash
godot --headless --path . tests/fm_narrative_smoke.tscn
```

Resultado: **`FM_NARRATIVE_TEST: PASS (75 PASS / 0 FAIL)`**.

Comprueba:

1. `Narrative` existe, es hermano de las dos escenas de arte y contiene 8 raíces.
2. Grupo `fm_narrative` con exactamente 8 raíces.
3. IDs únicos N1/N2/N3/N4/N5/N6/N7/N8 y presencia de cada uno.
4. Cada raíz tiene al menos 3 mallas.
5. Cada raíz está a más de 1,2 m de la polilínea jugable de su sector.
6. Cada raíz está dentro del AABB de su sector y su `narrative_sector` coincide.
7. Cero `CollisionShape3D`, cero `CollisionObject3D` y cero `Light3D` bajo
   `Narrative`.
8. `Narrative` tiene exactamente 8 hijos directos.
9. Los materiales `steel`, `steel_dark`, `steel_worn` y `rubber` tienen albedo,
   normal/roughness y UV triplanar, con filtro anisotrópico.
10. `paper`, `fabric_dark`, `leather` y `uniform` tienen micro-normal procedural.
11. `screen_checkin` y `led_red` conservan su emisión.

Las cuatro pruebas de regresión del slice siguen pasando:

```text
tests/fm_vslice_smoke.tscn    → 52 PASS / 0 FAIL
tests/fm_vslice_walk.tscn     → 16 PASS / 0 FAIL
tests/fm_vslice_chase.tscn    → 9 PASS / 0 FAIL
tests/fm_narrative_smoke.tscn → 75 PASS / 0 FAIL
```

No se observó ningún `SCRIPT ERROR` en las cuatro ejecuciones. Los avisos de
`ObjectDB`/recursos al forzar la salida son los habituales de los tests y
provienen de los `AudioStreamWAV` de ambiente, no de los anclajes.

---

## 5. Capturas

```bash
godot --path . tests/fm_narrative_shot.tscn
```

Genera 15 capturas 1280×720 en `docs/`:

| Archivo | Contenido |
|---|---|
| `fm_narrative_n1_counter.png` | Mostrador con CHECK-IN, registro, badges, café y silla volcada. |
| `fm_narrative_n1_route.png` | N1 visto desde la ruta de recepción. |
| `fm_narrative_n2_waiting.png` | Sala de espera con maleta, mochila, abrigo, mesa, revista y taza. |
| `fm_narrative_n3_lockers.png` | Taquilla abierta con uniforme, nota y objetos personales. |
| `fm_narrative_n3_fallen.png` | Puerta caída y marcas de arrastre junto a las taquillas. |
| `fm_narrative_n4_security.png` | Puesto de seguridad con monitor muerto y objetos. |
| `fm_narrative_n4_route.png` | N4 desde la ruta. |
| `fm_narrative_n5_entrance.png` | Umbral completo desde el vestíbulo. |
| `fm_narrative_n5_handprint.png` | Detalle de huella, grietas y cinta de cuarentena. |
| `fm_narrative_n6_trail.png` | Rastro, maletín, guante, radio y linterna. |
| `fm_narrative_n7_decon.png` | Carro, traje hazmat y cartel desde la ruta. |
| `fm_narrative_n7_cart.png` | Detalle del carro y del traje. |
| `fm_narrative_n7_samples.png` | Cajas de muestras al este de extracción. |
| `fm_narrative_n8_link.png` | Estante, registro, nota y radio muerta en el enlace Z10. |
| `fm_narrative_n8_handprint.png` | Huella y cinta en la puerta del enlace. |

---

## 6. Limitaciones

1. Los anclajes son **props narrativos sin interacción ni física**. No se puede
   abrir el maletín, usar el terminal ni recoger el guante. Es intencional en
   este pase.
2. No hay colisión: el jugador puede atravesar visualmente los props. Se hizo así
   para no alterar el Paso 1, la navegación del Vigilante ni el recuento de
   colisiones (277 + 151).
3. No hay audio asociado. Las radios, el terminal y los LEDs son visuales.
4. No hay luces nuevas. La única iluminación es la existente de Recepción R9 y la
   linterna del jugador.
5. Los vidrios de N5 son los paneles existentes de la entrada, con centros reales
   `x=-92.9` y `x=-87.1`; las huellas se colocan en `x=-92.8` y `x=-87.2`. No se
   duplica el vidrio para evitar z-fighting.
6. Los detalles orgánicos (manos, traje, rastro) son primitivas con materiales,
   no mallas esculpidas. El traje hazmat usa cápsulas/esferas para suavizar la
   silueta, pero sigue siendo geometría runtime.
7. Se añaden **359 `MeshInstance3D`** de detalle (los 237 iniciales + 122 de N2/N3/N8). La última medición estática, ya con el pase de materiales, da **330–334 FPS en Z10 / 356–359 FPS en Recepción** a 1280×720, con **1.142 / 1.137 draws**, 6.428 objetos y 457,3 MB de texturas. Ejecuciones anteriores oscilaron entre 240 y 463 FPS por variación de la máquina. La prueba congela jugador y Vigilante; no mide la IA activa ni una partida completa.
8. El pase de materiales usa triplanar y micro-normales: mejora el detalle de superficie, pero no sustituye un unwrap y texturizado de hero props. Los GLB y las escenas de arte no se retexturizaron en este pase.
9. No se tocaron los GLB, escenas de arte, `level1.tscn`, `fotos-referencia/`, los `.blend` ni el HUD. No hay commit.

---

## 7. Skills aplicadas

- `godot-3d-essentials`: cámaras/environment existentes, materiales PBR y
  verificación de la escena 3D.
- `godot-gdscript`: tipado, ciclos de vida y compilación de los 93 scripts.
- `godot-nodes-scenes`: jerarquía `Narrative` hermana de las escenas de arte,
  instanciación segura y verificación de rutas del proyecto.
- `godot-physics`: confirmación de cero colisiones/áreas y respeto de las capas
  existentes.
- `level-design`: anclajes fuera de la ruta jugable, del radio de extracción y del pasillo de Z10.
- `performance-optimization`: presupuesto cualitativo, draw calls y advertencia de medición estática.
- `verification-before-completion`: resultados de las tres pruebas ejecutadas.

No se usaron skills de Blender porque no se creó ni modificó ningún asset en
Blender. `godot-animation`, `godot-shaders`, `godot-ui-control` y
`godot-multiplayer` no aplican a este pase.

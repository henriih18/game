# FRECUENCIA MUERTA — Vestuarios (Nivel 1, Z05)

Estado: **vestido y verificado en Godot** (checkpoint local, sin commit).

## 1. Alcance

Se vistió la sala `SM_L1_Zone05_Changing_*` del máster V06, conservando el
blockout y la ruta de la puerta sur. No se modificaron:

- `scenes/fm/level1_v06.tscn`
- `scenes/fm/level1.tscn` ni las escenas del vertical slice
- `fotos-referencia/`

La escena de sala `scenes/fm/fm_blockout_lockers_art.tscn` se amplió in situ:
mantiene `LockersSector`, `blockout_lockers.glb` y `Emerg_Lockers` con su
transform original, y añade el GLB de arte y las luces de sala.

## 2. Composición

Planta 30 × 24 m, altura 4,5 m. Caras interiores reales: sur y=40,15;
norte y=63,85; oeste x=30,15; este x=59,85 (Blender). Godot: x 30..60,
z −64..−40.

- **Taquillas**: 23 bancos de 6 puertas (138 puertas) en los cuatro muros,
  con huecos para la puerta sur (x 40..46), la puerta oeste (y 48..52) y la
  puerta de servicio sellada (x 56..60). Puertas abiertas hacia la sala en
  varios bancos, con ropa doblada y botas en el interior.
- **Bancos**: 14 perimetrales y 8 en islas centrales, con estantes inferiores
  en parte de ellos.
- **Duchas**: bloque noreste con plataforma alicatada, cuatro plazas,
  tabiques, cortinas (una ausente y una rasgada), grifería, desagües y banco.
- **Lavabo**: encimera de tres senos, espejos con marco, alicatado y
  dispensadores en el muro norte.
- **Vestíbulo**: tablón de anuncios, rótulo TAQUILLAS, reloj, extintor,
  botiquín, pulsador de alarma, carrete de manguera y señalización SALIDA.
- **Techo**: vigas I, bandejas portacables, tuberías, conducto de ventilación,
  línea de rociadores y luminarias (una dañada).
- **Narrativa ambiental**: ropa colgada, toallas, bolsas, casco, botas,
  papeles, fregona, puerta de taquilla descolgada, charcos y una huella de
  mano en el alicatado de la ducha.
- **Marca**: logotipo NEXUS emisivo sobre las taquillas del muro norte.

La ruta crítica del smoke (entrada sur x 40..46, avance hasta z −42) queda
despejada. Los muebles sólidos generan colisión; las piezas decorativas usan
los tokens de omisión de `FMGLBCollision` (`LIGHT`, `CABLE`, `SIGN`, `MAT`,
`DECAL`, `TRIM`, `CLOTH`, `PAPER`, `DIS_WATER`, `DIS_HAND`).

## 3. Archivos

| Archivo | Función |
|---|---|
| `nexus/nivel_01/FM_LEVEL1_V06_ARCH.blend` | máster V06 con la colección `L1_ART_VESTUARIOS` |
| `scripts/fm/fm_vestuarios_build.py` | construcción idempotente del arte (106 objetos) |
| `scripts/fm/fm_vestuarios_export_headless.py` | exportación y validación del GLB |
| `assets/models/fm/vestuarios_art.glb` | GLB de arte (5,97 MB) |
| `docs/fm_vestuarios_art_export.json` | informe de exportación |
| `assets/art/fm/vestuarios/T_VEST_*` | texturas 1K propias del set de taquillas/baldosas |
| `scenes/fm/fm_blockout_lockers_art.tscn` | escena de sala con blockout + arte + 13 luces |
| `tests/fm_level1_v06_vestuarios_shots.gd/.tscn` | capturas de evaluación en `/tmp/opencode` |

Backup previo al arte:
`docs/backups/FM_LEVEL1_V06_ARCH_before_vestuarios_art_2026-11-14.blend`
(md5 `62f488f3328a0f8fa41a04fe94b69b5a`, idéntico al máster anterior).

Checkpoint posterior (listo para la siguiente sala):
`docs/backups/FM_LEVEL1_V06_ARCH_after_vestuarios_art_2026-11-14.blend`
(md5 `38d769f416f6011ed08d03561c21d0bc`) y
`docs/backups/FM_VESTUARIOS_ART_checkpoint_2026-11-14.glb`
(md5 `bf27cbee90b6b3661764d69a0ee49760`).

## 4. Datos técnicos

- 106 objetos de malla, 31.840 vértices, **51.050 triángulos**.
- GLB: **5.974.800 bytes**, 106 mallas/nodos, 20 imágenes, 28 materiales,
  0 cámaras, 0 luces.
- AABB Blender del arte: min (30,0, 40,0, 0,0), max (60,0, 64,0, 4,4).
  (Godot: x 30..60, y 0..4,4, z −64..−40.)
- La sala suma 131 mallas visibles (25 blockout + 106 arte) y 104 colliders
  en el pase del smoke.
- Luces de sala: `Emerg_Lockers` (original) + 7 frías + 2 de emergencia +
  1 relleno del pasillo oeste + 2 frías de muro este/lavabo + 1 fría de
  suroeste = 13. Sin sombras para rendimiento; la linterna del jugador
  conserva las suyas.
- Materiales: verde de taquilla y baldosa con texturas 1K propias; galvanizado
  plano; reutilización de `M_FM_Steel_Dark`, `M_FM_Workbench_Wood`,
  `M_FM_Rubber`, `M_Z10_HERO_Steel_Dark_2K`, etiquetas `M_FM_Label_*`,
  `M_FM_Sign_Servicio`, `M_REC03_DecalHand` y `M_REC03_DecalPuddle` (copia
  oscura `M_VEST_Puddle`).

## 5. QA y pruebas

- **blender-asset-qa** sobre arte + shell: el arte no tiene errores propios.
  Quedan 4 contactos coplanares **preexistentes** entre marcos de la puerta de
  servicio y muros del shell (`SM_L1_Zone05_Changing_Door_S_Service_*`), no
  introducidos por Vestuarios.
- Avisos aceptados: solapamiento UV por proyección de caja con texturas
  repetidas (no se hornea); no afecta a glTF.
- `tests/fm_level1_v06_smoke.tscn`: **403 PASS / 0 FAIL**.
  Se actualizaron los recuentos de Lockers (131 mallas, 104 colliders) y se
  permite que la sala tenga luces de arte además de `Emerg_Lockers`; la
  unicidad de posición/color/energía se sigue comprobando sobre las nueve
  luces de emergencia.
- `tests/fm_level1_v06_gameplay.tscn`: **105 PASS / 0 FAIL**.
- `tests/fm_full_run.tscn`: **49 PASS / 0 FAIL**.
- `tests/fm_graphics_presets_smoke.tscn`: **194 PASS / 0 FAIL**.
- `tests/fm_level1_v06_perf.tscn`: **PASS** a 1280×720, 7.619 frames,
  fps_avg 585,7, fps_p1 282,2, 0 frames > 16,7 ms. Es el nivel completo, no
  una escena aislada.
- Capturas Godot: `/tmp/opencode/vest_godot_{entry,center,west,shower,wash,east,lookback}.png`.

## 6. Skills utilizadas

- `blender-core`: API 5.2, data API/bmesh, escala y verificación.
- `blender-hardsurface-modeling`: bevel, normales, juntas a tope y presupuesto.
- `blender-pbr-materials`: metallic/roughness, color spaces, ORM y glTF.
- `blender-lighting-lookdev`: composición de luz interior y cámara.
- `blender-asset-qa`: control de z-fighting, islas, normales y UVs.

No se usaron `blender-texture-baking` ni `blender-texturing` porque no se
horneó ni pintó: el detalle viene de geometría y de sets PBR existentes/1K.
`blender-rendering` se usó de forma implícita vía EEVEE para las capturas de
Blender; no se generó un turntable.

## 7. Limitaciones y siguientes pasos

- El centro de la sala sigue siendo amplio; las islas de bancos lo organizan,
  pero no se añadieron taquillas centrales para no bloquear la ruta.
- El techo queda muy oscuro (estética de terror); las luminarias se leen por
  emisión, no iluminan por sí solas.
- Los espejos son oscuros sin SSR/probe dedicado; en la captura se lee el
  reflejo de la luz.
- El pasillo tras la puerta oeste se ilumina con un relleno, pero no se vistió.
- `BLOCKOUT_CONTEXT` sigue mostrando "BLOCKOUT · TAQUILLAS Y CAMBIO" en el HUD
  para no alterar el resto de salas; se puede cambiar a "ARTE · VESTUARIOS"
  cuando se decida el estado global.
- No se ha validado todavía la sincronización multijugador del arte ni de las
  luces; el arte es estático y las colisiones se generan en runtime.
- Pendiente: vestir Control, Almacén, Mantenimiento, Oficinas, Aseo y
  Escaleras con el mismo pipeline, checkpoint por sala y sin commit sin
  autorización.

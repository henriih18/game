# FRECUENCIA MUERTA — Control de Acceso (Nivel 1, Z04)

Estado: **reconstruido con calidad de complejo abandonado y verificado en Godot**
(checkpoint local, sin commit).

## 1. Alcance

Se reconstruyó el arte de la sala `SM_L1_Zone04_AccessControl_*` del máster
V06, conservando el blockout, las puertas, la ruta del smoke y el navmesh.
No se modificaron:

- `scenes/fm/level1_v06.tscn`
- `scenes/fm/level1.tscn` ni las escenas del vertical slice
- `fotos-referencia/`

La escena `scenes/fm/fm_blockout_control_art.tscn` mantiene `ControlSector`,
`blockout_control.glb` y `Emerg_Control` con su transform original, y añade
`ControlArt` y las luces de sala.

## 2. Composición

Planta 30 × 20 m, altura 6 m. Caras interiores: sur y=40,15; norte y=59,85;
oeste x=−104,85; este x=−77,15 (Blender). Godot: x −105..−77, z −60..−40.

- **Filtro de acceso**: dos mostradores de checkpoint al sur (x −100,5 y
  −88,5; 5,6 m) con cuerpo modular, encimera, cajones y bandeja de cables;
  cuatro tornos en x −96, −93, −90 y −87 (y 47,5), con placa de anclaje,
  cuerpo de acero, lector inclinado, LED de estado, brazos de trípode en los
  tornos 1 y 4 y carril central abierto para el paso.
- **Detección**: arco detector de metales en el carril central (x −94,5,
  y 46,2) con postes, paneles, banda emisiva fina y panel superior atenuado;
  equipo de rayos X con cinta de rodillos (x −83,2, y 46,6), pantalla y
  bandas emisivas.
- **Garita de control**: esquina noroeste, plataforma y escalón, cerramiento
  de aluminio, vidrio transparente (alpha 0,22), puerta practicable con
  manilla, persianas laterales, rejilla de ventilación y techo interior.
  Mostrador con cajonera, silla, tres CRT con carcasa, teclado y lámpara
  cálida.
- **Vigilancia y datos**: tres racks 19" con plinto, postes, paneles
  laterales ventilados, puerta de chapa con ranuras, equipos internos,
  patch panel, extractores y cables; taquilla de llaves en el muro oeste;
  muro de ocho CRT en dos estanterías con carcasas profundas, rejillas,
  cables y un CRT caído; cuatro cámaras de seguridad.
- **Arquitectura**: techo registrable con tejas oscuras (algunas ausentes o
  manchadas), perfilería y varillas; cladding metálico de 1,3 m con costillas
  y remate; zócalo técnico, juntas, conduits, cajas, rejillas y manchas de
  pared; suelo texturizado con manchas y líneas de carril.
- **Clutter de abandono**: papeles, carpetas, cinta roja, rollo de cable,
  escombros, llaves, tazas, silla caída, cono, señal de suelo húmedo,
  papelera y extintor. Sin armas ni combate.
- **Rotulación**: `CONTROL DE ACCESO`, `SEGURIDAD`, `NEXUS`, `SALIDA`,
  `FILTRO NORTE`, panel de evacuación, reloj, etiquetas de alta tensión y
  extintor; logotipo NEXUS emisivo.
- **Iluminación**: 18 OmniLight3D sin sombras, incluidas luminarias frías,
  relleno de entrada y tornos, balizas rojas y lámpara cálida de garita.

La ruta crítica del smoke (entrada sur x −96..−92, avance por el carril
central hasta z −50) queda despejada. Los muebles sólidos generan colisión;
las piezas decorativas usan tokens de `FMGLBCollision` (`TRIM`, `SIGN`,
`LIGHT`, `CABLE`, `DECAL`, `GRILLE`, `DIFFUSER`). La sala suma **114 mallas
visibles** y **71 colliders** en el pase del smoke.

## 3. Archivos

| Archivo | Función |
|---|---|
| `nexus/nivel_01/FM_LEVEL1_V06_ARCH.blend` | máster V06 con `L1_ART_CONTROL` |
| `scripts/fm/fm_control_build.py` | construcción idempotente (88 objetos) |
| `scripts/fm/fm_control_export_headless.py` | exportación y validación del GLB |
| `assets/models/fm/control_art.glb` | GLB de arte (7,73 MB) |
| `docs/fm_control_art_export.json` | informe de exportación |
| `scenes/fm/fm_blockout_control_art.tscn` | blockout + arte + 18 luces |
| `tests/fm_level1_v06_control_shots.gd/.tscn` | capturas de evaluación |

Backups:

- `docs/backups/FM_CONTROL_QUALITY_before_2026-11-17/` — estado previo a la
  reconstrucción de calidad.
- `docs/backups/FM_LEVEL1_V06_ARCH_after_control_art_2026-11-15.blend` y
  `docs/backups/FM_CONTROL_ACCESS_ART_checkpoint_2026-11-15.glb` — checkpoint
  anterior del arte.
- `docs/backups/FM_CONTROL_QUALITY_2026-11-17/` — checkpoint de esta
  reconstrucción (máster, GLB, escena, script y esta ficha).

## 4. Datos técnicos

- 88 objetos de malla, 44.156 vértices, **69.708 triángulos**.
- GLB: **7.729.160 bytes**, **88 mallas/nodos**, **32 materiales**,
  **18 imágenes**, **69.720 triángulos**, 0 cámaras, 0 luces.
- AABB Blender: min (−104,92, 40,16, −0,03), max (−77,165, 59,835, 6,0);
  dentro de `CONTROL_BOUNDS`.
- Escena: **114 mallas**, **71 colliders**, **18 OmniLight3D**.
- Materiales: `M_CTRL_*` (suelo, pared, techo, panel de luz, cristal,
  amarillo, pantallas, LEDs, lámpara cálida, manchas) y reutilización de
  `M_FM_Steel_Dark`, `M_FM_Metal_Panel`, `M_FM_Concrete_Floor/Wall`,
  `M_FM_Rubber`, `M_FM_Painted_Green`, `M_WH_Galv`, `M_VEST_Paper`,
  `M_VEST_Red`, `M_VEST_Emissive_Green`, `M_HERO_Sign_Seguridad`,
  `M_FM_Label_AltaTension_2` y `M_FM_Label_Extintor`.

## 5. QA y pruebas

- **blender-asset-qa** del subset de Control (101 objetos: arte + shell
  Zone04 + columnas, sin puertas ni techo del shell): **PASS, 0 errores**,
  59 warnings aceptados (UVs de textos/decales, winding y duplicados de
  fuente). Se corrigieron racks, cladding, CRT caído, vidrio de garita,
  mostradores, estantes, lectores y tornos.
- `tests/fm_level1_v06_smoke.tscn`: **412 PASS / 0 FAIL**.
  Control queda en 114 mallas y 71 colliders.
- `tests/fm_level1_v06_gameplay.tscn`: **108 PASS / 0 FAIL**.
- `tests/fm_full_run.tscn`: **49 PASS / 0 FAIL**.
- `tests/fm_graphics_presets_smoke.tscn`: **194 PASS / 0 FAIL**.
- `tests/fm_level1_v06_alt_routes_smoke.tscn`: **73 PASS / 0 FAIL**.
- `tests/fm_level1_v06_radio_smoke.tscn`: **21 PASS / 0 FAIL**.
- `tests/fm_level1_v06_radio_supplies_smoke.tscn`: **30 PASS / 0 FAIL**.
- `tests/fm_level1_v06_perf.tscn` a 1280×720 con ventana: **PASS**,
  **430,8 fps** medios, mínimo **184,9**, p1 **223,7**, p99 **4,47 ms**,
  0 frames sobre 16,7 ms. Escena: 5.225.540 triángulos, 4.622 mallas,
  808 materiales, 198 luces, 1.535 colliders, 0 huérfanos.

Capturas: `/tmp/opencode/ctrl_godot_{entry,center,turnstiles,booth,monitors,east,lookback}.png`
y contact sheet `/tmp/opencode/ctrl_contact5.jpg`.

## 6. Limitaciones conocidas

- Las luces de sala no proyectan sombras (decisión de rendimiento); la
  profundidad la aportan la geometría, el cladding y la linterna.
- La sala sigue siendo deliberadamente oscura y algo escasa en las vistas
  amplias; el detalle se concentra en puestos, garita, racks y muro de CRT.
- El techo del shell se excluye del QA por una isla preexistente de 8
  vértices en el origen, ajena a esta sala.
- Las capturas se tomaron a 1280×720 en la GTX 1650 Ti; no son garantía del
  rendimiento final con criaturas, física y multijugador.

## 7. Skills usadas

`blender-core`, `blender-hardsurface-modeling`, `blender-pbr-materials`,
`blender-texturing`, `blender-lighting-lookdev`, `blender-asset-qa`,
`blender-export-pipelines`, `blender-game-optimization`,
`blender-scene-setup`, `level-design`, `scenario-godot-3d-world` y
`writing-plans`.

No se usaron `blender-rendering` (capturas en Godot), `blender-sculpting`
ni `blender-character-rigging` (no hay criatura en esta sala).

## 8. Siguiente paso

1. Revisar el contact sheet y decidir si hace falta una última pasada de
   clutter o contraste.
2. Mantener el checkpoint sin commit hasta autorización.
3. Continuar con la auditoría de calidad de la siguiente sala o con la
   extracción dinámica / pase visual global.

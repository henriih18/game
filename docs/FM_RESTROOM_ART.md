# FRECUENCIA MUERTA — Aseo de planta (Z09)

## Alcance

Vestido del aseo de planta del Nivel 1 V06, situado en x18..30 / y42..58
(Blender), conectado con Oficinas por el enlace oeste y con Vestuarios por
la puerta este. El blockout se conserva; el arte se añade como
`L1_ART_RESTROOM` y se integra en `fm_blockout_restroom_art.tscn` sin
tocar `level1_v06.tscn` ni las escenas del slice.

Identidad: aseo industrial abandonado de NEXUS, con cerámica verde-gris,
acero, porcelana, techo registrable, luz fría y señales de uso
interrumpido.

## Composición

- **Norte:** tres urinarios con divisores, cinco cabinas (cuatro normales
  y una accesible) con puertas, bisagras, pestillos, indicadores
  rojo/verde, dispensadores de papel y barra de apoyo.
- **Sur:** cuatro cabinas, una accesible y cuarto de limpieza con puerta
  abierta, pileta de limpieza, estante de químicos, cubo y fregona.
- **Oeste:** dos tramos de lavabos con encimera, cinco senos, grifos,
  espejos enmarcados, dispensadores de jabón/toallas y secador.
- **Suelo y muro:** zócalo cerámico hasta 2,30 m con remate de acero,
  solera texturizada, felpudo de goma, rejillas, tuberías y bandejas.
- **Techo:** techo registrable a 3,20 m, placas, marco perimetral, ocho
  luminarias emisivas, rejillas de ventilación y colectores.
- **Señalética:** ASEO, LAVADO DE MANOS, SALIDA, NEXUS, WC y caballete de
  suelo mojado con pictograma.
- **Narrativa:** puerta de cabina retirada, azulejos rotos, papeles,
  charcos, mano ensangrentada en el espejo, rastro discreto hacia la
  puerta este y extintor.

## Archivos

| Archivo | Función |
|---|---|
| `scripts/fm/fm_restroom_build.py` | Build idempotente de `L1_ART_RESTROOM`. |
| `scripts/fm/fm_restroom_export_headless.py` | Exporta y valida el GLB. |
| `assets/models/fm/restroom_art.glb` | Arte para Godot. |
| `scenes/fm/fm_blockout_restroom_art.tscn` | Escena de sala con luces. |
| `tests/fm_level1_v06_restroom_shots.gd/.tscn` | Capturas de evaluación. |
| `docs/fm_restroom_art_export.json` | Reporte de exportación. |

## Datos técnicos

- Arte Blender: **25 objetos, 16.188 tris**, sin cámaras ni luces.
- GLB: **1.641.132 bytes**, 25 mallas/nodos, 22 materiales, 9 imágenes,
  0 cámaras, 0 luces.
- AABB Blender: min (18.097, 42.07, 0.0), max (29.852, 57.86, 3.24),
  dentro de `RESTROOM_BOUNDS` (Godot x15..30, y-0.2..4.0,
  z-58.15..-41.85).
- Escena: `RestroomSector` + `RestroomArt` + `Emerg_Restroom` y 13 luces
  nuevas (8 frías de techo, 2 cálidas de espejo, relleno de entrada,
  relleno del conector y emergencia roja este), 14 luces en total, todas
  sin sombras.
- Smoke: **39 mallas y 20 colliders** en el sector Aseo, 403 PASS.

## QA

`blender-asset-qa` sobre el arte y el shell del aseo (suelo, muros,
marcos de puerta y enlace; sin techo, hojas de puerta ni anotación, y
excluyendo el par preexistente entre el muro sur del aseo y el muro oeste
de Vestuarios):

**PASS, 0 errores**, 48 warnings aceptados (UVs de textos/decales,
duplicados de fuente y winding de cilindros).

Se corrigieron durante la QA: coplanaridad de tapas de tabique, patas de
cabina contra solera y zócalo, grifos tangentes al seno, placa del
caballete y estantes del cuarto de limpieza.

## Pruebas

| Prueba | Resultado |
|---|---|
| `fm_level1_v06_smoke` | **403 PASS / 0 FAIL** |
| `fm_level1_v06_gameplay` | **105 PASS / 0 FAIL** |
| `fm_full_run` | **49 PASS / 0 FAIL** |
| `fm_graphics_presets_smoke` | **194 PASS / 0 FAIL** |
| Perf 1280x720 con ventana | **PASS** (avg 527,2 fps; min 181,9; p1 252,5; 0 frames >16,7 ms) |

Capturas: `/tmp/opencode/rs_godot_{entry,corridor,sinks_north,sinks_south,stalls_north,stalls_south,accessible,cleaning,east_door,lookback}.png`.

## Limitaciones

- Los espejos son superficies claras de aspecto empañado, sin reflexión
  en tiempo real.
- Las cabinas se agrupan en una malla por fila; la colisión resultante es
  un AABB por fila. Es suficiente para el blockout actual, pero conviene
  dividirla por partes cuando se implementen puertas interactivas.
- La iluminación interior es atmosférica y deliberadamente desigual; el
  fondo del pasillo de Oficinas y algunas esquinas quedan en penumbra.
- El par coplanar preexistente entre `SM_L1_Zone09_Aseo_Wall_S_0` y
  `SM_L1_Zone05_Changing_Wall_W_0` pertenece al shell y se excluyó del QA;
  no se modificó geometría del shell.

## Skills

Usadas: `blender-core`, `blender-hardsurface-modeling`,
`blender-pbr-materials`, `blender-lighting-lookdev`,
`blender-asset-qa`, `blender-texturing`, `blender-scene-setup`,
`blender-game-optimization` y `blender-export-pipelines`.

No se usaron `blender-rendering` ni `blender-texture-baking`: las
capturas se hicieron en Godot y los materiales PBR se reutilizaron sin
bake.

## Backups

- Pre-aseo: `docs/backups/FM_LEVEL1_V06_ARCH_before_restroom_art_2026-11-15.blend`
  (md5 `142863cb0a5018a8b7f7159b01910ff6`).
- Post-aseo: `docs/backups/FM_LEVEL1_V06_ARCH_after_restroom_art_2026-11-15.blend`
  (md5 `9049fb058ef1b453494566371b84a9c9`).
- GLB checkpoint: `docs/backups/FM_RESTROOM_ART_checkpoint_2026-11-15.glb`
  (md5 `e18933bca147fad94cf055d9cbb643d4`).

## Siguiente sala

**Escaleras principales y salidas de emergencia E1/E2.** Mantener el
mismo flujo: backup, diagnóstico del shell, colección propia, QA hasta 0,
GLB validado, escena in situ, smoke y pruebas completas, capturas,
documentación y checkpoint sin commit.

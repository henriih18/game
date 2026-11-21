# FRECUENCIA MUERTA — Recepción R9: luz diegética y dirección oscura

Fecha: 2026-11-10. Estado: **art scene R9 creada, capturada y medida; sin commit**. `fotos-referencia/` intacta.

Dirección aplicada: **Recepción es la única zona con algo más de luz; Z10 y el resto, solo emergencias escasas + linterna.** R9 ilumina únicamente Recepción; Z10 conserva R8.

## 1. Escena y archivos

| Elemento | Ruta |
|---|---|
| Escena de arte Recepción | `scenes/fm/fm_reception_art_r9.tscn` |
| Script | `scripts/fm/fm_reception_art_r9.gd` |
| GLB (sin cambios) | `assets/models/fm/reception_sector.glb` |
| Captura | `docs/fm_reception_godot_light_r9.png` |
| A/B con Z10 R8 | `docs/fm_reception_godot_light_r9_ab.png` |
| Z10 R8 conservada | `scenes/fm/fm_z10_art_r8.tscn` |

La escena contiene la instancia del GLB, `WorldEnvironment`, `ArtCamera` y **12 luces Omni diegéticas**. No hay `Key`, `Fill`, `Bounce` ni `DirectionalLight3D`. El `.tscn` no añade geometría.

## 2. Auditoría de luces

### 2.1. Blend `nexus/nivel_01/FM_LEVEL1_V06_ARCH.blend`

No existe una colección `L1_ARCH_LIGHTS`. Las luces de Recepción están repartidas entre `L1_LIGHTING_INTENT` y las colecciones `L1_RECEPTION_R1/R2/R3`:

| Fuente | Tipo / energía | Posición Blender | Uso |
|---|---|---|---|
| `LIGHT_L1_Reception_A` | AREA 320 W | (-88, -24, 4.8) | práctica principal del hall |
| `LIGHT_L1_Reception_B` | AREA 120 W | (-99, -12, 3.6) | práctica secundaria / vestíbulo |
| `LIGHT_L1_Reception_Fill_0..3` | POINT 75 W | (-100/-80, -12/-34, 3.0) | 4 pendientes del hall |
| `LIGHT_REC01_Emergency_0/1` | POINT 2 W rojo | (-90, -38.8/9.2, 5.0) | emergencia techo |
| `LIGHT_REC01_Gate_Beacon` | POINT 1.5 W rojo | (-94, -39.55, 4.45) | baliza de compuerta |
| `LIGHT_REC01_Vestibule_0/1` | POINT 20 W cálido | (-92/-88, -6, 2.85) | vestíbulo |
| `LIGHT_REC02_Soffit_0..3` | POINT 90 W cálido | (-105/-99, -15/-12, 3.3) | downlights de soffit |
| `LIGHT_REC03_Emergency_Decon` | POINT 2 W rojo | (-97, -33.7, 2.45) | emergencia descontaminación |
| `LIGHT_REC03_Emergency_Extraction` | POINT 2 W rojo | (-94, -39.38, 4.05) | emergencia extracción |
| `LIGHT_REC03_Salida` | POINT 1.5 W verde | (-94, -39.35, 4.0) | señal de salida |

**Hallazgo:** todas esas luces están con `hide_render=True`. Son **intención de iluminación**, no un rig activo. Los renders R10/R13 usan area lights temporales (`REC10_AGING_KEY/FILL/WAITING_FILL/RIM`, `REC13_KEY/FILL/RIM/...`) que no se guardan en el blend. Las **AREA lights de Blender tampoco se exportan a glTF**.

### 2.2. GLB y escenas Godot actuales

- `assets/models/fm/reception_sector.glb`: **36.235.496 B**, **292 nodos / 274 mallas / 104 materiales / 41 texturas / 30 imágenes**, **0 luces y 0 cámaras**. Es geometría y materiales, no un rig de luces.
- `scenes/fm/fm_reception_test.tscn` + `scripts/fm/fm_reception_test.gd`: escena de validación con **9 omnis aproximadas** (`ReceptionA_Approx`, `ReceptionB_Approx`, `ReceptionHallFill`, `Fill_0..3`, `SpawnFill`, `ExtractionFill`) y la linterna del jugador. Solo A/B están en fixtures reales; el resto son rellenos no diegéticos.
- `scenes/fm/fm_reception_sector_validate.tscn`: validación geométrica; `RECEPTION_SECTOR_GODOT_OK` (292/274, AABB `40,4095 × 5,6 × 36,33739 m`).
- No existía una escena de arte de iluminación de Recepción.

R9 sustituye los rellenos por **12 luces colocadas en fixtures visibles**.

## 3. Luces usadas en R9

Todas son Omni porque las AREA de Blender no viajan al GLB; se colocan en el difusor/lente del fixture correspondiente. No hay luces fijas nuevas fuera de fixtures.

| Nodo | Fixture de referencia | Posición Godot | Color | Energía | Rango | Sombras |
|---|---|---|---|---:|---:|---|
| `PracticalA` | `KIT_REC01_LightA_Diffuser` | (-88, 4.45, 24) | cálido (1.0, 0.82, 0.62) | 6.0 | 25 | sí |
| `Pendant_0` | `KIT_REC01_Pendant_Disc_0` | (-100, 3.0, 12) | cálido (1.0, 0.80, 0.58) | 1.8 | 12 | no |
| `Pendant_1` | `KIT_REC01_Pendant_Disc_1` | (-80, 3.0, 12) | cálido | 1.8 | 12 | no |
| `Pendant_2` | `KIT_REC01_Pendant_Disc_2` | (-100, 3.0, 34) | cálido | 1.8 | 12 | no |
| `Pendant_3` | `KIT_REC01_Pendant_Disc_3` | (-80, 3.0, 34) | cálido | 1.8 | 12 | no |
| `Vestibule_0` | `KIT_REC01_Vestibule_Light_0` | (-92, 3.05, 6) | cálido | 1.2 | 7 | no |
| `Vestibule_1` | `KIT_REC01_Vestibule_Light_1` | (-88, 3.05, 6) | cálido | 1.2 | 7 | no |
| `Emerg_Ceiling_N` | `KIT_REC01_Emergency_Ceiling_1` | (-90, 5.0, 9.2) | rojo (1.0, 0.03, 0.02) | 1.8 | 7 | no |
| `Emerg_Ceiling_S` | `KIT_REC01_Emergency_Ceiling_0` | (-90, 5.0, 38.8) | rojo | 1.8 | 7 | no |
| `Emerg_Decon` | `KIT_REC03_Emergency_Decon` | (-97, 2.45, 33.86) | rojo | 1.0 | 4 | no |
| `Emerg_Extraction` | `KIT_REC03_Emergency_Extraction` | (-94, 4.05, 39.55) | rojo | 1.2 | 5 | no |
| `Exit_Salida` | `LIGHT_REC03_Salida` / cartel de extracción | (-94, 4.0, 39.35) | verde (0.25, 1.0, 0.45) | 0.30 | 3 | no |

Log de la escena:

```
RECEPTION_ART_R9_GLB_LIGHTS 0
RECEPTION_ART_R9_LIGHTS total=12 expected=12 omni=12 spot=0 directional=0
```

No hay luces direccionales ni spots de escena; tampoco key/fill/bounce. El ambiente del `WorldEnvironment` es bajo (0.06) y no sustituye un relleno.

## 4. Environment y cámara

| Ajuste | R9 Recepción | Z10 R8 (referencia) |
|---|---:|---:|
| Exposición AgX | **1.12** | 0.80 |
| Ambient energía | **0.06** | 0.020 |
| Fondo | (0.002, 0.0024, 0.003) | (0.0015, 0.0018, 0.0022) |
| Fog volumétrico | 0.008 | 0.012 |
| Glow | 0.25 | 0.20 |
| SSAO / SSR | on / on | on / on |

- Cámara: `ARCH_CAM_Reception`, Blender `(-106, -36, 1.7)` → Godot `(-106, 1.7, 36)`.
- Objetivo: `(-99.54, 1.66, 28.37)`; 24 mm sobre sensor 36 mm → **FOV horizontal 73.7°**.
- 1280×720, Forward+.

La recepción es más legible que Z10 R8 por las prácticas cálidas, no por un key/fill no diegético.

## 5. Captura y A/B

- `docs/fm_reception_godot_light_r9.png`: 1280×720, 3 s de convergencia.
- Media `(39.9, 32.3, 24.4)`; mediana de luminancia `26`; p90 `71`; p99 `120`.
- `docs/fm_reception_godot_light_r9_ab.png`: Z10 R8 (emergencia sola) / Recepción R9 (prácticas + emergencia).
- Z10 R8: media `(1.7, 0.1, 0.0)`, mediana `0`. Recepción R9 es claramente más legible, pero sigue siendo una escena oscura de terror.

**Lectura honesta:** el hall, el mostrador, la espera y la señalización de emergencia se leen; la zona de espera del fondo izquierdo sigue muy oscura porque no tiene fixture propio. El techo cálido viene de las omnis en los pendientes (aproximación de las AREA de Blender), no de un fill.

## 6. FPS y VRAM (escena estática, no gameplay)

Medición en ventana, GTX 1650 Ti, Vulkan Forward+, 1280×720, VSync off, 5 s:

| Métrica | R9 Recepción |
|---|---:|
| FPS medio | **294.1** |
| Frames / tiempo | 1471 / 5.002 s |
| Textura VRAM | **236.7 MB** |
| Vídeo VRAM | **298.3 MB** |
| Objetos | 2584 |

Es una **escena estática de arte**, sin jugador, criaturas, físicas, audio ni multijugador. **No es FPS de gameplay.** El GLB de Recepción tiene 292 nodos/274 mallas y 379.562 tris (export de validación); las 12 luces tienen solo 1 con sombras.

## 7. Diferencias con Z10 R8

| Aspecto | Z10 R8 | Recepción R9 |
|---|---|---|
| Luces | 3 rojas de emergencia | 7 prácticas cálidas + 4 rojas + 1 verde |
| Key/fill/bounce | ninguno | ninguno |
| Media de luminancia | 1.7 | 39.9 |
| Legibilidad | casi negra; requiere linterna | hall/señalización legibles sin linterna |
| Fuente | GLB Z10 + overrides | GLB Recepción + luces en fixtures |
| FPS estático | 320.7 | 294.1 |
| VRAM textura/vídeo | 361.4 / 441.5 MB | 236.7 / 298.3 MB |

## 8. Limitaciones

1. **Omnis en vez de AREA:** las AREA de Blender no se exportan; las omnis en los fixtures aproximan la luz y elevan algo el techo.
2. **Luces del blend ocultas:** la auditoría encontró `hide_render=True` en todas; R9 reconstruye la intención, no copia un rig renderizado.
3. **Sin GI:** no hay rebote; la espera del fondo queda oscura y las esquinas negras.
4. **Zona de espera:** no tiene fixture propio; no se añadió una luz no diegética. Si se quiere más luz allí, debe existir/crearse un fixture en la geometría.
5. **Una sola cámara:** la captura es la vista 3/4 de `ARCH_CAM_Reception`; no cubre toda la sala.
6. **FPS estático:** 294.1 FPS no representa gameplay.
7. **Sin cambios de GLB/blend/fotos:** no se tocó `reception_sector.glb`, el `.blend` ni `fotos-referencia/`. No hay armas ni combate.

## 9. Veredicto

**Cumple la dirección:** Recepción es la única zona con más luz; se usan solo 12 luces diegéticas en fixtures existentes, sin key/fill/bounce. El frame es más legible que Z10 R8 pero sigue siendo oscuro y de terror. La captura y el A/B muestran la diferencia. **Pendiente:** si se quiere levantar la espera, añadir un fixture real o aceptar que quede en penumbra; y pasar a la integración de gameplay.

Sin commit. `fotos-referencia/` intacta.

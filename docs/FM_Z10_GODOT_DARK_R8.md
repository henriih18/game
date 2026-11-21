# FRECUENCIA MUERTA — Z10 dirección oscura R8

Fecha: 2026-11-10. Estado: **R8 dark art scene creada, capturada y medida; sin commit**. `fotos-referencia/` intacta.

Dirección del usuario aplicada a Z10: **Recepción es la excepción con algo más de luz; en Z10 y el resto solo luces de emergencia y muy pocas.** Esta escena cubre Z10; la excepción de recepción no está en este nivel y queda registrada para su propio pase de iluminación.

## 1. Escena y conservación de R7

| Elemento | Ruta |
|---|---|
| Escena oscura R8 | `scenes/fm/fm_z10_art_r8.tscn` |
| Script R8 | `scripts/fm/fm_z10_art_r8.gd` |
| Escena R7 conservada | `scenes/fm/fm_z10_art_r7.tscn` |
| GLB (sin cambios) | `assets/models/fm/z10_sector.glb` |
| Captura oscura | `docs/fm_z10_godot_dark_r8.png` |
| Captura con linterna diagnóstica | `docs/fm_z10_godot_dark_flashlight_r8.png` |
| A/B R7 / R8 oscuro / linterna | `docs/fm_z10_godot_dark_r8_ab.png` |

R8 es una escena nueva: no modifica R7, el GLB, el `.blend` ni `fotos-referencia/`.

## 2. Luces eliminadas y luces conservadas

### 2.1. Sin luces no diegéticas añadidas

En R8 **no existen** `Key`, `Fill`, `Center`, `EastWash`, `CeilingBounce` ni `FloorBounce`. El `.tscn` no contiene ningún nodo `Light3D` de escena (0 luces fijas añadidas). Solo se conserva la instancia del GLB y su configuración runtime.

### 2.2. Luces del GLB

El GLB importa 9 luces. R8 deja **3 rojas de emergencia** y desactiva las otras 6:

| Luz | Estado R8 | Energía / rango | Sombras |
|---|---|---|---:|
| `LIGHT_Z10_Emergency_E` | visible | 3.0 / 6.0 | sí |
| `LIGHT_L1_Conector_E` | visible | 0.30 / 3.5 | no |
| `LIGHT_L1_Conector_N` | visible | 0.30 / 3.5 | no |
| `LIGHT_Z10_Point_01` | **oculta** | — | — |
| `LIGHT_Z10_Point_02` | **oculta** | — | — |
| `LIGHT_Z10_Point_03` | **oculta** | — | — |
| `LIGHT_Z10_SouthSpill` | **oculta** | — | — |
| `LIGHT_Z10_WorkFill` | **oculta** | — | — |
| `LIGHT_Z10_WorkSpot` | **oculta** | — | — |

Log de la escena: `Z10_ART_R8_LIGHTS kept=3 disabled=6`.

### 2.3. Emisivos de luminarias normales apagados

Las tres luminarias de techo (`LIGHT_Z10_Luminaire_01/02/03`) y la lámpara de trabajo (`PROP_Z10_WorkLight`) seguían emitiendo blanco/ámbar aunque sus luces puntuales estuvieran ocultas. En R8 se duplican sus materiales **solo en esta escena** y se apaga `emission_enabled`; el GLB y los materiales compartidos no se modifican. Log: `Z10_ART_R8_EMISSION_OFF overrides=29` (29 superficies en 4 objetos).

Los lentes rojos de emergencia (`M_R21B_Emissive_Red`, `M_FM_Emergency_Lens_Red`), el LED rojo de la cámara y la señalización de bajo emisivo se conservan como materiales diegéticos, no como luces puntuales. La cinta de peligro conserva su emisivo amarillo del GLB; es material, no una luz, y aparece como pequeñas marcas reflectantes.

## 3. Environment oscuro

| Ajuste | R7 | R8 |
|---|---:|---:|
| Exposición AgX | 0.94 | **0.80** |
| Ambient color | (0.62, 0.52, 0.40) | (0.30, 0.32, 0.38) |
| Ambient energía | 0.12 | **0.020** |
| Fondo | (0.004, 0.005, 0.007) | **(0.0015, 0.0018, 0.0022)** |
| Fog volumétrico | 0.018 | **0.012** |
| Glow | 0.30 | 0.20 |
| SSAO / SSR | on / on | on / on (no levantan la escena) |

Se mantienen AgX, niebla volumétrica, SSAO y SSR. La niebla no tiene ambient inject ni GI inject (`0`), por lo que solo dispersa la luz roja de emergencia. El fondo y el ambient son casi negros; no hay rebote artificial.

## 4. Desgaste COLOR_0

El post-import sigue activo y la escena R8 lo verifica:

```
Z10_ART_R8_WEAR vc=true node=P0B4_SPRINKLER_RUN_DN80
```

No se modificó el GLB ni el material importado.

## 5. Capturas

### 5.1. Escena real oscura

`docs/fm_z10_godot_dark_r8.png` — 1280×720, sin linterna, sin luces añadidas. Es la escena real: habitación casi negra, tres fuentes rojas de emergencia y pequeñas marcas reflectantes. Media `(1.71, 0.12, 0.02)`; mediana de luminancia `0`; p90 `1`; p99 `13`; máximo `159`.

### 5.2. Linterna diagnóstica temporal

`docs/fm_z10_godot_dark_flashlight_r8.png` — misma escena, con un `SpotLight3D` temporal creado **solo en el script de captura** y destruido después. No está guardado en `fm_z10_art_r8.tscn` y no es una luz fija del juego. Se usa para revisar legibilidad de geometría, materiales, desgaste y decal.

- Energía 8.0, rango 24, ángulo 38°, sombras activas, color frío.
- Log: `FLASHLIGHT_TEMP_ADDED` → `FLASHLIGHT_CAPTURE` → `FLASHLIGHT_TEMP_REMOVED`.
- Media de la captura `(17.87, 17.72, 19.04)`; mediana `5`; p90 `51`; máximo `233`.

### 5.3. A/B

`docs/fm_z10_godot_dark_r8_ab.png`: R7 art scene (key/fill/bounce) / R8 oscuro real / R8 con linterna diagnóstica.

## 6. FPS y VRAM (escena estática, no gameplay)

Medición en ventana, GTX 1650 Ti, Vulkan Forward+, 1280×720, VSync off, 5 s, **sin linterna**:

| Métrica | R8 oscuro |
|---|---:|
| FPS medio | **320.7** |
| Frames / tiempo | 1604 / 5.002 s |
| Textura VRAM | **361.4 MB** |
| Vídeo VRAM | **441.5 MB** |
| Objetos | 3140 |

Es una **escena estática de arte**, sin jugador, criaturas, físicas, audio ni multijugador. **No es FPS de gameplay.** R7 medía 197.2 FPS; R8 sube porque hay muchas menos luces con sombras y se apagaron los emisivos de luminarias, aunque la VRAM sigue dominada por los buffers de niebla/SSAO/SSR. No se hizo prueba de leak.

## 7. Veredicto

**Cumple la dirección oscura para Z10.** La escena ya no tiene key/fill/wash/bounce ni luces de trabajo; solo quedan tres luces rojas de emergencia y el resto está apagado. El frame real es casi negro y la linterna diagnóstica demuestra que la geometría, el desgaste y el decal siguen ahí. La excepción de recepción no se toca en esta escena y queda anotada para su pase propio.

## 8. Limitaciones

1. **Oscuridad deliberada:** la geometría no es legible sin linterna; es el resultado esperado de la dirección, no un fallo de captura.
2. **Tres luces de emergencia:** se conservaron `Emergency_E` y los dos conectores rojos. Si “muy pocas” debe significar solo una, los conectores se pueden ocultar en una iteración.
3. **Emisivos no-luz:** la cinta de peligro y la señalización conservan pequeños emisivos del GLB; no son luces puntuales ni levantan la escena.
4. **Sin GI:** la luz roja no rebota; las zonas sin emergencia quedan negras.
5. **FPS estático:** 320.7 FPS no representa gameplay.
6. **Deuda geométrica global** sin cambios.

Sin commit. `fotos-referencia/` intacta.

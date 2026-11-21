# FRECUENCIA MUERTA — Validación Godot del piloto Z10

**Fecha:** 2026-11-06
**Motor:** Godot 4.7.2.stable.official.ed1daf0bf
**Renderer:** Forward+
**GPU:** NVIDIA GeForce GTX 1650 Ti, 4096 MiB
**Ventana:** 1280 × 720, VSync desactivado para la medición
**Escena:** `scenes/fm/fm_pilot_test.tscn`
**Script:** `scripts/fm/fm_pilot_test.gd`
**Panel de prueba:** `scripts/fm/fm_pilot_test_panel.gd`

---

## 1. Objetivo

Validar el Conector Z10 exportado contra el controlador existente `FMPlayer`
antes de aplicar el estándar a recepción. La prueba cubre carga del GLB,
escala, movimiento, cámara, colisiones, linterna, interacción, puertas y
rendimiento. No incluye narrativa, criaturas, audio de superficies ni
multijugador.

## 2. Escena de validación

La escena carga en runtime:

- `assets/models/fm/z10_conector.glb`
- `assets/models/fm/player_base_z10.glb` como referencia visual de escala
- `scenes/fm/fm_player.tscn` (`FMPlayer`, sin duplicar el controlador)
- `FMHUD` y el shader de postproceso del proyecto

Elementos **solo de prueba**, que no forman parte del arte ni de la
producción:

- Panel de validación no narrativo en `(50, 0, -12.2)`, con interacción E.
- Cajas de suelo y cerramiento de seguridad para aislar la prueba.
- Plataforma de 2 × 6 m fuera de la puerta E para no caer al cruzar el umbral.
- Luz de relleno `PilotFill` para poder revisar la escena en capturas.
- Dos luces rojas de emergencia en las posiciones reales del Conector.

## 3. Resultados de carga

| Dato | Resultado |
|---|---:|
| Mallas del Conector en Godot | 524 |
| Nodos del GLB | 526 |
| Colliders generados | 249 |
| Mallas de la referencia del jugador | 25 |
| Tiempo de carga del GLB | ~864 ms |
| Objetos totales en escena | 894 |

El GLB se carga sin errores de importación en runtime. Los 524
`MeshInstance3D` corresponden a las instancias de las 422 mallas del archivo
glTF. El archivo pesa **11.549.936 bytes (11,01 MB)** tras exportar las
texturas como **WebP calidad 80**, frente a los 104.044.600 bytes anteriores.

## 4. Pruebas ejecutadas

Comando:

```bash
DISPLAY=:0 godot --path . scenes/fm/fm_pilot_test.tscn -- --autotest
```

| Prueba | Resultado | Evidencia |
|---|---|---|
| Carga del Conector | PASS | `PILOT_GLB meshes=524 nodes=526` |
| Escala del jugador | PASS | 1,70 m de altura y cápsula de 0,38 m |
| Movimiento | PASS | 1,66 m recorridos, `is_on_floor=true` |
| Cámara | PASS | yaw -0,198 rad, pitch 0,099 rad |
| Colisión con panel | PASS | el jugador se detiene a 1,66 m |
| Interacción E | PASS | panel 0 → 1 activación |
| Linterna | PASS | encendida → apagada → encendida |
| Puerto de puerta E | PASS | rayo central sin impacto |
| Hoja de puerta E | PASS | rayo lateral impacta colisión |
| Muro este | PASS | rayo impacta colisión |
| Cruce del umbral | PASS | x = 63,02, `is_on_floor=true` |
| Paso por el centro | PASS | z = -20,86, `is_on_floor=true` |
| Rendimiento | PASS (piloto) | 160,3 FPS promedio |

### 4.1. Movimiento y colisiones

- Spawn: `(50, 0.15, -10)`.
- Tras avanzar 0,7 s: `(50, 0, -11.66)`.
- El jugador queda sobre el suelo y es detenido por el panel de validación.
- La cápsula de 0,38 m y la altura de 1,70 m se conservan.
- Regresión del centro: desde `(52, 0.15, -14)` el jugador avanza 2 s hacia
  el norte y termina en `z = -20,86`, sobre el suelo. Antes, el AABB de
  `PROP_Z10_RiserIdentification` lo detenía en `z ≈ -15,73`.

### 4.2. Cámara y linterna

- El evento de ratón modificó yaw y pitch correctamente.
- La linterna se apaga y vuelve a encender mediante la acción `flashlight`.
- La batería descendió de 100 a 82,9 durante la sesión de prueba.

### 4.3. Puertas

Rayos comprobados:

- Centro del hueco E, de `x=58` a `x=63` en `z=-21`: **sin impacto**.
- Hoja de puerta E, en `z=-18.15`: **impacto**.
- Muro este, en `z=-14`: **impacto**.

El jugador cruzó el umbral abierto hasta `x=63.02` sin caer. La puerta E
conserva su apertura de 90° y las hojas mantienen colisión propia.

### 4.4. Rendimiento

Muestra de 3 s en la vista amplia del salón, VSync desactivado:

| Métrica | Valor |
|---|---:|
| FPS promedio | 160,3 |
| FPS mínimo | 120 |
| FPS máximo | 253 |
| Muestras | 520 |
| Draw calls | 353 |
| Primitivas | 123.812 |
| Objetos renderizados | 850 |

Estos valores corresponden a la escena de validación del piloto, sin
criaturas, audio, objetos narrativos ni multijugador. No son una garantía de
rendimiento del juego completo.

### 4.5. Luces de emergencia

- `EmergencyE` y `EmergencyN` quedan en las posiciones reales de sus
  apliques de pared, con sombras activas.
- Se añadió `EmergencyService` en `(51, 3.805, -19)`, energía 4,0, rango 9 y
  sombras, coincidiendo con el nuevo aplique de techo
  `KIT_PILOT_Z10_Emergency_Ceiling` de Blender.
- El aplique de techo tiene 64 vértices / 60 caras y QA PASS 0 errores / 2
  warnings aceptados (UV solapada por materiales sólidos y pieza de techo sin
  apoyo en z=0).

## 5. Hallazgo importante: colisiones de mallas compuestas

Dos objetos agrupaban piezas separadas en una sola malla y su AABB generaba
un muro invisible:

1. `KIT_PILOT_Z10_Portal_E` agrupa el marco completo de la puerta. Su AABB
   abarca todo el hueco, por lo que una caja bloqueaba el paso aunque la
   puerta estuviera abierta.
2. `PROP_Z10_RiserIdentification` agrupa 19 aros finos alrededor de dos
   grupos de risers. Su AABB es 9,64 × 8,56 × 3,99 m e incluía el centro de
   la sala; bloqueaba el paso a la altura del jugador. Las tuberías de los
   risers ya tienen colliders propios y no necesitan esa caja.

Solución aplicada:

- Se extrajo un helper reutilizable `scripts/fm/fm_glb_collision.gd`
  (`FMGLBCollision`).
- Crea un único `StaticBody3D` y usa trimesh para nombres con `PORTAL`,
  `FRAME`, `DOORFRAME` o `RISERIDENTIFICATION`, y para mallas con AABB
  mayor de 8 m³ y más de 300 vértices.
- El resto de la arquitectura usa cajas AABB deduplicadas.
- El piloto genera 249 colliders, de los cuales 6 son trimesh; el centro de la
  sala y la puerta E son transitables.
- El helper queda listo para reutilizarse en recepción. No debe usarse el AABB
  completo de una malla compuesta.

## 6. Capturas

| Archivo | Contenido |
|---|---|
| `docs/fm_pilot_01_spawn.png` | Spawn, HUD y panel de validación |
| `docs/fm_pilot_02_moved.png` | Movimiento y colisión con el panel |
| `docs/fm_pilot_03_interact.png` | Panel activado |
| `docs/fm_pilot_04_flashlight_off.png` | Linterna apagada |
| `docs/fm_pilot_05_door_e.png` | Puerta E abierta y luz roja |
| `docs/fm_pilot_06_threshold.png` | Umbral cruzado, vista de regreso |
| `docs/fm_pilot_07_toolwall.png` | Pared de herramientas iluminada |
| `docs/fm_pilot_08_player_reference.png` | Referencia de escala del jugador |
| `docs/fm_pilot_09_room.png` | Vista amplia del salón |
| `docs/fm_pilot_10_center.png` | Centro de la sala despejado tras corregir el riser |

La vista de la puerta E queda oscura porque el hueco conduce a una zona aún
no construida. No es un fallo de iluminación: no hay geometría al otro lado.

## 7. Problemas pendientes

1. **Helper de colisiones:** generalizado y probado en el piloto; falta
   integrarlo en recepción.
2. **Fuga al salir en headless:** aparecen `2 ObjectDB instances were leaked at
   exit` y `1 resources still in use`. La ejecución ventaneada no mostró el
   aviso; revisar con `--verbose` antes de producción.
3. **Audio de superficies:** no se asignó `fm_level1_surface_audio.gd`; los
   pasos usan el fallback de audio. La propagación por material no está
   validada.
4. **Sin prueba de resistencia prolongada:** no se midió memoria, carga
   sostenida, navegación, criaturas ni jugadores adicionales.
5. **Arte final:** la referencia del jugador es un blockout; no hay modelo
   final, manos ni animaciones.
6. **Multijugador y narrativa:** fuera del alcance de esta validación.

## 8. Criterio de cierre

El piloto se considera **validado funcionalmente en Godot** para los sistemas
probados: carga, escala, movimiento, cámara, colisiones, linterna, interacción,
puertas, luces de emergencia y rendimiento base. El helper de colisiones ya
está generalizado y probado en el piloto; el GLB WebP de 11,5 MB carga en
~864 ms y los bins vacíos fueron eliminados. No se considera un vertical slice
completo ni una validación de producción hasta integrar el helper en recepción,
revisar la fuga headless y completar audio, arte y animaciones.

## 9. Próximo paso

1. Integrar `scripts/fm/fm_glb_collision.gd` en recepción.
2. Revisar la fuga headless con `--verbose`.
3. Aplicar el estándar a recepción.
4. Abordar después el modelo y las animaciones finales del jugador.
5. Narrativa y multijugador al final.

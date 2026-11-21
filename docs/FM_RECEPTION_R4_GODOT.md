# FRECUENCIA MUERTA — Validación Godot de recepción R4

**Fecha:** 2026-11-08
**Motor:** Godot 4.7.2.stable
**Renderer:** Forward+
**GPU:** NVIDIA GTX 1650 Ti 4 GB
**Escena:** `scenes/fm/fm_reception_test.tscn`
**Script:** `scripts/fm/fm_reception_test.gd`
**GLB:** `assets/models/fm/reception_r4.glb`

---

## 1. Objetivo

Validar la recepción exportada contra `FMPlayer` y el helper de colisiones
`fm_glb_collision.gd`. La prueba cubre carga, colisiones, movimiento, linterna,
acceso a la zona de extracción y rendimiento. No incluye lógica de extracción,
narrativa ni multijugador.

## 2. Exportación

- **310 objetos** seleccionados del archivo `FM_LEVEL1_V06_ARCH.blend`.
- **1.251.136 bytes (1,25 MB)** con **WebP calidad 80**.
- Incluye shell de recepción, columnas, vestíbulo, R1, R2 y R3, mobiliario,
  carteles, decals y luces puntuales/spot.
- Las luces **AREA** de Blender no se exportan a glTF; la escena de prueba usa
  luces omni aproximadas.
- El GLB importa **16 luces**; se desactivan en el test porque su intensidad
  producía sobreexposición (`RECEPTION_IMPORTED_LIGHTS kept=0 disabled=16`).

## 3. Carga y colisiones

| Dato | Resultado |
|---|---:|
| Mallas del GLB en Godot | 292 |
| Nodos | 311 |
| Tiempo de carga (ventana) | 203 ms |
| Tiempo de carga (headless) | 96 ms |
| Colliders generados | 102 |
| Trimesh | 3 |
| Objetos en escena | 486 |

El helper `fm_glb_collision.gd` genera las colisiones de la recepción sin muros
invisibles. La compuerta y los marcos compuestos usan trimesh.

## 4. Pruebas

Comando ventaneado:

```bash
DISPLAY=:0 godot --path . scenes/fm/fm_reception_test.tscn -- --autotest
```

| Prueba | Resultado |
|---|---|
| Carga del GLB | PASS |
| Colisiones | PASS, 102 colliders |
| Movimiento | PASS, 6,80 m |
| Suelo | PASS, `is_on_floor=true` |
| Linterna | PASS, encendida → apagada |
| Acceso a extracción | PASS, z = 39,46 |
| Rendimiento | PASS (escena de prueba) |
| Autotest | `RECEPTION_AUTOTEST_OK` |

La interacción E no se prueba en esta escena porque la recepción todavía no
tiene un interactuable propio; el sistema ya fue validado en el Conector Z10.

## 5. Rendimiento

Muestra de 3 s, 1280 × 720, VSync desactivado:

| Métrica | Valor |
|---|---:|
| FPS promedio | 239,8 |
| FPS mínimo | 194 |
| FPS máximo | 273 |
| Muestras | 782 |
| Draw calls | 29 |
| Primitivas | 15.528 |
| Objetos | 419 |

Son datos de una escena de validación con iluminación aproximada, no del juego
completo.

## 6. Capturas

| Archivo | Contenido |
|---|---|
| `docs/fm_reception_r4_01_spawn.png` | Spawn, mostrador, espera, soffit y luces |
| `docs/fm_reception_r4_02_room.png` | Recorrido por la recepción |
| `docs/fm_reception_r4_03_extraction.png` | Acceso a la compuerta de extracción |
| `docs/fm_reception_r4_04_extraction_deck.png` | Plataforma de extracción |

La vista de spawn es legible. La compuerta se lee como un panel cerrado y el
cartel EXTRACCIÓN queda fuera de encuadre en la captura; requiere una pasada de
arte específica.

## 7. Limitaciones

1. **Iluminación:** las AREA de Blender no viajan al GLB. La escena usa omnis
   aproximadas; falta una pasada de luces nativas de Godot.
2. **Compuerta:** se lee como panel plano/cerrado; faltan lamas, guías y detalle.
3. **Materiales/texturas:** siguen siendo de blockout; R3.3 de lookdev queda
   pendiente.
4. **Extracción:** no hay lógica de activación, entrega ni consecuencias.
5. **Interacción:** no hay interactuable en recepción todavía.
6. **Narrativa y multijugador:** fuera del alcance.
7. **Jugador:** blockout sin modelo final ni animaciones.

## 8. Veredicto

La recepción queda **validada técnicamente en Godot** para carga, colisiones,
movimiento, linterna, acceso a extracción y rendimiento. Se considera cerrada
en su **fase técnica/artística de blockout**, no como sala final de arte.

Para el acabado final quedan R3.3 (luces, compuerta, materiales y desgaste),
la lógica de extracción y la integración de narrativa/multijugador.

## 9. Reproducir

```bash
# Autotest
DISPLAY=:0 godot --path . scenes/fm/fm_reception_test.tscn -- --autotest

# Prueba manual
DISPLAY=:0 godot --path . scenes/fm/fm_reception_test.tscn
```

Controles: WASD, ratón, Shift, Ctrl, E, F, Q, Esc libera el ratón y clic lo
recaptura.

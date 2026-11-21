# FRECUENCIA MUERTA — Contrato técnico del piloto Z10

**Estado:** referencia congelada para producción  
**Fecha:** 2026-11-06  
**Archivo:** `nexus/nivel_01/FM_LEVEL1_V06_ARCH.blend`  
**Escena:** `NEXUS_L1_V06_ARCH`  
**Zona piloto:** Conector de servicio Z10 — colección `L1_KIT_PILOT`

---

## 1. Alcance

Este documento define el contrato técnico que debe cumplir el Conector Z10 como referencia arquitectónica del Nivel 1. No incluye objetos narrativos, pruebas de juego, exportación ni integración en Godot.

Cualquier cambio estructural en la zona piloto debe registrarse como una nueva versión. No se renombran, mueven o eliminan piezas del piloto sin revisar sus dependencias.

## 2. Escala y unidades

- 1 unidad de Blender = 1 metro.
- Escala aplicada en mallas; sin escalas negativas.
- Eje vertical: Z. Altura de suelo: z = 0.
- Cápsula de referencia del jugador: 0,38 m de radio, 1,70 m de altura.
- Puertas de servicio: 2,4 m de ancho × 3,0 m de alto.
- Puertas de seguridad: 1,0–1,2 m de ancho × 2,6 m de alto.
- Pasillo principal de servicio: 3,4 m de ancho libre mínimo.
- Los objetos grandes deben poder circular por puertas y pasillos; si no, la limitación debe ser intencional y documentada.

## 3. Nomenclatura

| Prefijo | Uso |
|---|---|
| `KIT_PILOT_Z10_` | Arquitectura modular del Conector |
| `PROP_Z10_` | Props y equipamiento del Conector |
| `DET_Z10_` | Detalles no estructurales |
| `LIGHT_L1_` | Luces del Nivel 1 |
| `M_FM_` | Materiales del proyecto |
| `DET_Z10_LCD_` | Componentes del tambor de cable |
| `DET_Z10_ToolCart_` / `DET_Z10_StorageCart_` | Detalles funcionales de carros |

Los objetos deben conservar el nombre al exportar. No usar sufijos `.001` como parte del nombre definitivo.

## 4. Colecciones

- `L1_KIT_PILOT`: arquitectura, puertas, servicios y detalles constructivos.
- `L1_PROPS_Z10`: props, mobiliario, herramientas y equipamiento.
- `L1_GAMEPLAY_Z10`: empties de anclajes y referencias de juego.
- Los objetos de blockout deben permanecer ocultos y no exportarse.
- Las colecciones de render temporales (`TMP_*`) no deben guardarse.

## 5. Materiales

- PBR metal/roughness; color base en sRGB; normales, rugosidad y AO en Non-Color.
- Texturas en `assets/art/fm/`; las generadas, en `assets/art/fm/generated/`.
- Sin imágenes faltantes ni rutas temporales.
- Los materiales deben describir el material real: acero, hormigón, madera, goma, plástico, cristal.
- No reutilizar un material genérico para todo el complejo.
- Los rótulos usan placas físicas con UV normalizadas; no texto 3D suelto.
- Excepción documentada: las hojas E tienen z-fighting interno aceptado; no se corregirá sin autorización.

## 6. Pivotes y anclajes

- Puertas: origen en la bisagra; eje de giro vertical Z; las hojas E quedan abiertas 90°.
- Props de suelo: origen en la base, apoyados en z = 0.
- Props de pared: origen en el punto de montaje.
- Herramientas del pegboard: origen en el punto de suspensión.
- Anclajes existentes:
  - `HIDEOUT_Z10_Lockers` — taquillas.
  - `HIDEOUT_Z10_UnderBench` — bajo el banco.
- Los anclajes deben ser empties, no geometría visible.
- Los objetos que se puedan abrir, empujar o transportar deben tener pivote coherente.

## 7. Colisiones

- Colisión del jugador y de la arquitectura: convexa o caja, simplificada.
- Las puertas necesitan colisión propia, separada de la hoja visual.
- Los props pequeños no necesitan colisión compleja; los grandes, sí.
- No usar la malla visual de alta densidad como colisión.
- Mantener pasillos y portales despejados; validar con cápsula del jugador.
- Portales, marcos y mallas compuestas: no usar el AABB del objeto completo. Un marco con hueco o un conjunto de aros/abrazaderas genera una caja que bloquea el paso; usar trimesh o colliders por componente. Detectado con `KIT_PILOT_Z10_Portal_E` y `PROP_Z10_RiserIdentification` en Godot.

## 8. Exportación a Godot 4.x

- Formato preferido: glTF/GLB para estáticos; FBX para esqueletos si se requiere.
- Escala 1:1, sin `Apply Scale` pendiente.
- Eje de Blender a Godot: conservar la convención del proyecto; comprobar orientación al importar.
- Separar arquitectura, props y colisión por colecciones o nombres.
- Exportar solo objetos visibles; excluir blockout, `TMP_*` y luces de revisión.
- Las texturas deben ir empaquetadas o con rutas relativas válidas.
- Texturas WebP calidad 80 para GLB estático: el Conector pasó de 104 MB a 11,5 MB sin errores de carga en Godot 4.7.
- Los materiales deben conservar color, rugosidad, metalicidad y emisión.

## 9. Presupuesto y rendimiento

- Hardware objetivo: GTX 1650 Ti 4 GB, 32 GB RAM, Intel Core i5.
- Presupuesto del Conector: mantener la escena actual como referencia; medir triángulos, draw calls, sombras y memoria antes de replicar.
- Usar LOD en props repetidos y en objetos vistos a distancia.
- Evitar luces dinámicas con sombra innecesarias.
- Mantener la iluminación de emergencia muy limitada; la recepción es la única zona con luz de trabajo.
- No usar el piloto como garantía de rendimiento del juego completo.
- Medición Godot del piloto (1280×720, VSync off, GTX 1650 Ti): 160,3 FPS promedio, 353 draw calls y 123.812 primitivas en la vista amplia del salón. GLB de 11,5 MB WebP 80, carga ~864 ms y 249 colliders. Es una escena de validación, no gameplay completo.

## 10. QA mínimo

- QA de topología/UV: 0 errores.
- Warnings aceptados solo si están justificados y documentados.
- Sin z-fighting visible; las excepciones internas deben registrarse.
- Sin objetos flotantes, materiales vacíos, texturas faltantes ni escalas negativas.
- Render de evidencia del conjunto y de los objetos modificados.
- Validar portales con rayos: hueco libre, hoja con colisión y muro con colisión.
- Validar mallas compuestas con prueba de paso: el centro de la sala debe ser transitable.
- El piloto no se considera validado en Godot hasta probar movimiento, colisiones, linterna, interacción, puertas y rendimiento.

## 11. Excepciones conocidas

1. **Puertas E:** 2 errores de z-fighting interno por hoja (8 pares por hoja), aceptados por decisión de Riyo. No visibles desde el exterior.
2. **Herramientas de mano:** reconstruidas como perfiles low-poly; QA PASS 0/8, pero no son modelos hero de close-up.
3. **Validación Godot:** realizada el 2026-11-06 con Godot 4.7.2 Forward+ y GTX 1650 Ti. Movimiento, cámara, linterna, interacción, puertas y rendimiento probados. El AABB de `KIT_PILOT_Z10_Portal_E` bloqueaba el hueco y el de `PROP_Z10_RiserIdentification` bloqueaba el centro; se generalizó `scripts/fm/fm_glb_collision.gd` (`FMGLBCollision`) con trimesh y heurística de mallas compuestas. Paso central validado en z = -20,86. Se añadió `KIT_PILOT_Z10_Emergency_Ceiling` y las tres luces de emergencia están activas. GLB WebP 80 de 11,5 MB, carga ~864 ms, 249 colliders y 160,3 FPS promedio. Resultados en `docs/FM_PILOT_Z10_GODOT_VALIDATION.md`.

## 12. Próximo paso

1. Mantener `scenes/fm/fm_pilot_test.tscn` como escena de referencia de validación.
2. Integrar el helper `scripts/fm/fm_glb_collision.gd` en recepción y validar sus mallas compuestas.
3. Revisar la fuga de `ObjectDB`/recursos al cerrar en headless; la ejecución ventaneada termina limpia.
4. Aplicar el estándar a recepción con el pipeline corregido.
5. Modelo y animaciones finales del jugador, narrativa y multijugador después.

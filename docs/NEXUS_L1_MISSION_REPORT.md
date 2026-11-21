# FRECUENCIA MUERTA — Informe maestro del Nivel 1 (Fase 3A.2)

**Fecha:** 2026-11-04 (COT)  
**Escena:** `scenes/fm/level1.tscn`  
**Alcance:** todas las zonas interiores del Nivel 1.  
**Resultado:** nivel jugable, estable y visualmente coherente en el estándar de vertical slice industrial; quedan pendientes de producción documentados.

## 1. Resumen ejecutivo

Se completó una pasada integral sobre el Nivel 1. Se conservó la arquitectura, la lógica de juego y el GLB original. El trabajo nuevo se concentra en:

- Un kit de arquitectura industrial creado en Blender (`LEVEL1_DRESSING`): vigas, costillas, zócalos, cajas de servicio, conductos, lámparas de jaula, rejillas, dinteles, directorio, consola, racks y listones.
- Un conjunto de 15 props GLB con texturas a 1K, instanciados 34 veces: plantas, archivadores, estanterías, cajas eléctricas, cámaras, alarmas, botiquines, taburetes, barriles, cajas, microscopio y radio.
- Una revisión de materiales PBR (40 overrides), iluminación por zona, colisiones del mobiliario nuevo y limpieza de defectos visuales.
- Pruebas de humo, recorrido completo, colisiones y rendimiento.

No se tocaron físicas existentes, puertas, cajones, taquillas, alarmas, loot, IA, red, inventario ni menús. No se modificó `nexus/nivel_01/NEXUS_L1_V05.blend` ni `assets/models/fm/level1_nexus.glb`.

## 2. Problemas visuales corregidos

1. **Volumen claro del corredor:** se identificó como la combinación de los cuatro `NEXUS_V05_OFFICE_PARAPET_*` y el conducto del kit. Se ocultaron los parapetos, se añadieron dinteles/bulkheads, y el conducto se elevó, se redujo y se oscureció.
2. **Paneles blancos flotantes sobre puertas:** los linteles y paneles `_ABOVE_` se reasignaron a acero oscuro.
3. **Módulos de pared demasiado grandes y planos:** se sustituyeron por un sistema de costillas, paneles hundidos, zócalos y cajas de servicio a escala industrial.
4. **Mostrador y cristal de recepción:** se reemplazaron por el kit Blender de 3A.1, con paneles, remates, madera, luz inferior y mampara con marco de acero.
5. **Panel NEXUS claro:** se corrigió con el override `NEXUS_V05_MAT_Sign_Battery` a verde oscuro.
6. **Lámpara de vestuarios sobreexpuesta:** se limitó la emisión de `industrial_wall_lamp` y se ajustó la temperatura.
7. **Tiras de techo que parecían cajas flotantes:** se ocultaron las tiras de sala y se colocaron lámparas de jaula con brazo, casquillo, rejilla y bombilla.
8. **Plantas low-poly:** se ocultaron las esferas verdes y se colocaron dos plantas de biblioteca con maceta.
9. **Control y seguridad vacíos:** se añadieron consola, monitores, rack técnico, cámara, radio y taburetes.
10. **Espejos blancos planos:** se cambiaron a material oscuro reflectante; el marco del aseo se reubicó sobre el espejo.
11. **Falta de colisiones en mobiliario nuevo:** 14 props grandes y 3 estructuras tienen collider estático.
12. **Caída de rendimiento por texturas de props:** las texturas de los props se redujeron a 1K; el rendimiento volvió de 36 a 108 FPS (medición previa a los rellenos fríos; 103–107 final) en la medición de desarrollo.

## 3. Modelos y materiales

### Kits de Blender

- `blender_concept/ART3A1_kit.blend` — mostrador/cristal, conductos y módulos de pared de 3A.1 (274 objetos de origen).
- `blender_concept/LEVEL1_DRESSING.blend` — 1.327 objetos de origen, 10 mallas fusionadas por material.
- `blender_concept/build_level1_dressing.py` — generador reproducible del kit.
- `blender_concept/export_props.py` — exportador de props con reducción de texturas a 1K.

### GLB

- `assets/models/fm/art3a1/level1_art3a1_kit.glb` (~3,9 MB, 8 mallas).
- `assets/models/fm/art3a2/level1_dressing.glb` (~12,9 MB, 10 mallas).
- `assets/models/fm/props/*.glb` — 15 props, ~14 MB total.

### Materiales

- 40 overrides PBR en `scripts/fm/fm_level1_art_pass.gd`.
- Materiales nuevos del kit: acero, pintura verde, hormigón, madera, ducto, peligro, etiqueta, cian, ámbar, bombilla, lente y pantalla.
- Se reutilizaron texturas 2K locales de metal oxidado, pintura verde, yeso, hormigón, madera y suelo; no se descargaron recursos externos.

## 4. Archivos Blender y Godot

### Nuevos

- `blender_concept/build_level1_dressing.py`
- `blender_concept/LEVEL1_DRESSING.blend`
- `blender_concept/export_props.py`
- `assets/models/fm/art3a2/level1_dressing.glb`
- `assets/models/fm/props/*.glb` (15)
- `tests/fm_level1_room_tour.gd/.tscn`
- `tests/fm_level1_final_shots.gd/.tscn`
- `tests/fm_level1_detail_test.gd/.tscn`
- `tests/fm_level1_probe.gd/.tscn`
- `tests/fm_level1_audit.gd/.tscn`
- `tests/fm_level1_lightaudit.gd/.tscn`
- `tests/fm_level1_aimprobe.gd/.tscn`
- `docs/NEXUS_L1_MISSION_AUDIT.md`
- `docs/NEXUS_L1_MISSION_REPORT.md`
- `docs/fm_level1_art3a2_*.png` (capturas y hoja de contacto)

### Modificados

- `scripts/fm/fm_level1_art_pass.gd` — carga de kits, props, overrides, iluminación, colisiones, limpieza de defectos.
- `docs/CURRENT_STATE.md`
- `docs/WORKLOG.md`
- `docs/NEXUS_ASSET_INVENTORY.md`

### No modificados

- `nexus/nivel_01/NEXUS_L1_V05.blend`
- `assets/models/fm/level1_nexus.glb`
- `scripts/fm/level1.gd` (sin cambios de lógica en esta fase)
- Puertas, cajones, taquillas, alarmas, loot, IA, red, inventario y menús.

## 5. Recursos reutilizados y nuevos

**Reutilizados:** GLB jugable, 515 colliders, 21 props físicos, texturas 2K del proyecto, HDRI `abandoned_workshop_2k`, luces y probes de 3A, materiales de 3A.1, props de biblioteca exportados a GLB.

**Nuevos:** kit de arquitectura 3A.2, 15 props GLB, 34 instancias, 17 colliders nuevos, lámparas de jaula, consola de control, racks, directorio, listones de banco, rejillas de corredor.

## 6. Capturas

- `docs/fm_level1_art3a2_contact_sheet.png` — hoja de contacto de las 34 vistas.
- `docs/fm_level1_art3a2_before_after.png` — comparativa 3A.1 → 3A.2 de recepción y corredor.
- `docs/fm_level1_art3a2_reception.png`
- `docs/fm_level1_art3a2_counter.png`
- `docs/fm_level1_art3a2_logo.png`
- `docs/fm_level1_art3a2_directory.png`
- `docs/fm_level1_art3a2_corridor_west.png`
- `docs/fm_level1_art3a2_corridor_mid.png`
- `docs/fm_level1_art3a2_corridor_east.png`
- `docs/fm_level1_art3a2_security.png`
- `docs/fm_level1_art3a2_control.png`
- `docs/fm_level1_art3a2_vest.png`
- `docs/fm_level1_art3a2_storage.png`
- `docs/fm_level1_art3a2_maintenance.png`
- `docs/fm_level1_art3a2_office.png`
- `docs/fm_level1_art3a2_aseo.png`
- `docs/fm_level1_art3a2_dark_*.png` — cinco vistas sin linterna.

## 7. Pruebas

| Prueba | Resultado |
|---|---|
| Carga | `ART3A1_KIT loaded`, `ART3A2_DRESSING loaded`, `ART3A2_PROPS 34`, `ART_PASS ready materials=40 details=10`, `LEVEL1_READY loot=5 colliders=515` |
| Smoke | **PASS** — `TEST_LIGHTS general=0 art=23 emergency=30 flashlight=3`, `FM_LEVEL1_TEST: PASS` |
| Recorrido | **PASS** — `WALK_RESULT reached=33/33`, final `(-17.2377, -5.649179, -9.92019)` |
| Colisiones | **PASS 5/5**, 14 `PropCollider`, 3 colliders estructurales |
| Capturas | 34/34, con y sin linterna |
| Errores de script | Ninguno en la carga y pruebas finales; solo warnings de liberación de RIDs al cerrar Godot |

## 8. Rendimiento

Medición a **1280×720** en el equipo de desarrollo, escena completa, sin build final:

| Versión | FPS | Draw calls | Primitivas | Objetos |
|---|---:|---:|---:|---:|
| Fase 3 (antes de 3A) | 186 | 1.037 | 187.620 | 8.768 |
| Fase 3A | 110 | 796 | 221.484 | 8.655 |
| Fase 3A.1 | 108 | 814 | 406.748 | 8.683 |
| **Fase 3A.2** | **103–107** | **1.255** | **886.246** | **9.089** |

El coste adicional corresponde a arquitectura, props y sus sombras. El FPS se mantiene en 103–107 según la captura de la medición. No se probó en GTX 1650 Ti ni en build final; no hay LOD ni occlusion culling implementados.

## 9. Iluminación y oscuridad

- **Recepción:** iluminación moderada, clave fría, contraluz, relleno y acento ámbar; es la excepción del nivel.
- **Resto del nivel:** luces de emergencia atenuadas, lámparas de jaula puntuales, tiras cian/ámbar y grandes zonas oscuras.
- **Corredor:** focos fríos reducidos un 38 % y emergencias un 22 % para que la linterna sea relevante.
- **Pruebas sin linterna:** las capturas `dark_*` muestran referencias ambientales suficientes para orientarse, sin revelar toda la sala.
- **Linterna:** sigue siendo la herramienta principal para leer materiales, objetos y riesgos.

## 10. Colisiones y físicas

- 515 colliders originales conservados.
- 14 `PropCollider` nuevos para archivadores, estanterías, cajas eléctricas, barriles, cajas y caja de energía.
- 3 colliders estructurales nuevos: consola de control y dos racks técnicos.
- Los props pequeños (radio, microscopio, botiquín, alarma, cámara) son decorativos y no bloquean.
- Los 21 props físicos originales (latas, portapapeles, cartones) siguen funcionando.
- No se introdujeron vibraciones ni objetos inestables.

## 11. Evaluación por zona

| Zona | Estado | Observación |
|---|---|---|
| Recepción | APROBADA | Estándar visual de referencia; piezas de biblioteca simples en sillas/mesas |
| Corredor | APROBADA | Buena lectura industrial; tramos largos aún repetitivos |
| Seguridad | APROBADA | Monitor wall, rack y equipo; pared trasera oscura |
| Control | APROBADA | Consola y racks; pantallas placeholder |
| Vestuarios | APROBADA | Taquillas, bancos, espejos; taquillas de biblioteca |
| Almacén | APROBADA | Carga, polipasto y lámpara; cajas simples |
| Mantenimiento | APROBADA | Generador, caldera y banco; cara del generador plana |
| Oficina | APROBADA | Escritorio, estantería y equipo; estantería simple |
| Aseo | APROBADA | Espejo, estante y botiquín; pared lisa sin azulejo |
| Conector/ascensor | APROBADA | Señalización y puerta de servicio legibles |

## 12. Problemas que todavía necesitan atención

1. **LOD y occlusion culling:** no implementados. El kit está fusionado por material (10 mallas) y los props son GLB runtime; conviene dividir por sala para culling fino.
2. **Prueba en GTX 1650 Ti y build final:** pendiente.
3. **Props de biblioteca:** sillas, cajas, taquillas y bancos conservan geometría simple; se mitiga con materiales, pero no es arte final.
4. **Pantallas:** los monitores usan pantallas emisivas con barras de interfaz, no contenido real.
5. **Paredes:** algunos tramos largos siguen siendo repetitivos; falta variación única por sala.
6. **Aseo:** no hay azulejo procedural; la pared es lisa.
7. **Menús/perfiles gráficos:** fuera de alcance por instrucción; no se implementaron.
8. **Red de 8 jugadores:** fuera de alcance; no se tocó.
9. **Warnings de RIDs al cerrar:** provienen de la carga/duplicación de GLB en runtime; no afectan la partida, pero conviene limpiar en una fase de estabilidad.

## 13. Conclusión honesta

El Nivel 1 queda **jugable, estable y visualmente coherente** en el estándar de vertical slice industrial estilizado. La recepción y el corredor funcionan como referencia; el resto de salas comparte el mismo lenguaje de vigas, costillas, acero, pintura verde, luces de emergencia y oscuridad.

No considero que sea todavía **arte final de producción AAA**: quedan props de biblioteca simples, pantallas placeholder, ausencia de LOD/occlusion y falta de prueba en hardware objetivo. Esos puntos están documentados y no se ocultan.

No se avanzó a otras fases, menús, red, IA, inventario ni sistemas ajenos. El proyecto permanece ejecutable y las funcionalidades existentes siguen pasando las pruebas.

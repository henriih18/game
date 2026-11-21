# FRECUENCIA MUERTA — Auditoría integral del Nivel 1

**Fecha:** 2026-11-04
**Ámbito:** Nivel 1 / instalación NEXUS, 12 zonas, arte, materiales, geometría, físicas, funcionalidad, rendimiento y build.
**Modo:** auditoría de solo lectura. No se modificó ningún archivo del proyecto, escena, script, material, textura ni configuración. Este documento es el único archivo creado.
**Motor:** Godot 4.7.2.stable, renderer Forward+, viewport lógico 1280×720, stretch `canvas_items`.
**Escena:** `scenes/fm/level1.tscn`, lógica en `scripts/fm/level1.gd`, pase artístico en `scripts/fm/fm_level1_art_pass.gd`.
**Evidencia visual:** `docs/fm_level1_full_audit/` (24 capturas, 12 zonas × linterna apagada/encendida).

---

## 1. Resumen ejecutivo

**Veredicto: NO APTO para producción y NO APTO para declarar cerrada la fase visual del Nivel 1.**

El nivel tiene una base funcional real y varios sistemas P0 verificados: puertas, ascensor, extracción con botín, colisiones principales, carga de loot y pruebas de humo/recorrido. Los materiales dieron un salto importante respecto a la auditoría anterior: 371 materiales únicos, 19–20 triplanar, mipmaps completos, albedos comprimidos y correcciones de agua, esquirlas, espejos no negros, pantallas de seguridad y tubería roja.

Pero la experiencia visual actual **contradice la regla artística principal**: fuera de recepción, el nivel se ve sin linterna. El corredor tiene un charco de luz fría sin luminaria visible; mantenimiento, oficina, aseo y ascensor son legibles a oscuras; y siete rellenos artificiales de sala, cuatro focos de corredor y cuatro rellenos de corredor siguen activos. La causa inmediata es un error de orden en el pase artístico: la atenuación se ejecuta antes de crear las luces. La causa de fondo es que la corrección anterior añadió luz para “mejorar” salas oscuras, exactamente lo contrario de la dirección actual.

A esto se suman tres bloqueadores:

1. **Rendimiento:** 1920×1080 a **17 FPS** en la GTX 1650 Ti de referencia, con **3.702 MiB / 4.096 MiB de VRAM** y solo 25 % de utilización de GPU. No es jugable.
2. **Build:** no existe `export_presets.cfg` ni build exportada; además, el nivel carga GLB, HDR y PNG en runtime mediante rutas `res://` y `globalize_path`, sin `.import` para esos recursos. Un export probablemente pierda texturas, pantallas o modelos.
3. **Cobertura funcional:** el recorrido de 33 pasos no entra en oficina, aseo ni conector de servicio, y la prueba `TEST_ROOMS 10/10` es metodológicamente inválida en varias salas porque los rayos nacen por encima de los techos.

**Lo que sí está resuelto o verificable:** P0 funcional (ascensor, extracción con botín), puertas (6/6, 0 fallos), carga/descarga de loot, mipmaps, clearcoat del suelo, agua/esquirlas, espejos que ya no son negros, pantallas de seguridad legibles, tubería roja y doble cristal. El problema no es que “no haya trabajo”: es que la iluminación, el rendimiento y la producción invalidan el resultado actual.

### Métricas clave

| Métrica | Medición | Objetivo razonable | Estado |
|---|---:|---:|---|
| 1280×720 | 64 FPS | ≥60 FPS estable | Aceptable con poco margen |
| 1920×1080 | 17 FPS | ≥45–60 FPS | **Crítico** |
| VRAM | 3.706 MiB / 4.096 MiB | <3.200 MiB | **Crítico** |
| Draw calls | 817 | <500 | Alto |
| Primitivas | 704.584 | <500.000 | Alto |
| Objetos | 9.919 | <5.000 | Alto |
| Mallas visibles | 2.407 | <1.500 | Alto |
| LOD / Occlusion | 0 / 0 | LOD + occlusion | **Crítico** |
| Luces | 60 (50 omni, 10 spot) | ≤20–25 | Alto |
| Luces con sombra | 3 | 6–8 selectivas | Alto |
| Materiales únicos | 371 | Depende de atlas | Medio |
| Texturas únicas | 227 | <150 | Alto |
| Texturas 2K | 110 | <40 | Alto |
| Texturas comprimidas | 75 únicas / 142 slots | 100 % de albedo/normal/roughness | Alto |
| Capturas off/on | 24 | 12 zonas × 2 | Completo |

---

## 2. Estado general del proyecto y del nivel

### 2.1. Configuración

- `project.godot`: escena principal `scenes/menu.tscn`; viewport 1280×720; stretch `canvas_items`; Forward+.
- `scenes/fm/level1.tscn` es una escena mínima: la lógica y la mayor parte de la construcción están en `scripts/fm/level1.gd` (1.620 líneas).
- El modelo principal se carga en runtime desde `assets/models/fm/level1_nexus.glb` (42.507.928 bytes) con `GLTFDocument.append_from_file` (`level1.gd:187-189`).
- El pase artístico `scripts/fm/fm_level1_art_pass.gd` (1.406 líneas) se aplica al final de `level1.gd::_ready` (línea 123).
- El nivel tiene 12 zonas: recepción, corredor principal, seguridad, control de acceso, vestuarios, almacén, mantenimiento, oficina, aseo, conector de servicio, ascensor y extracción.

### 2.2. Arquitectura de carga

La carga runtime explica parte del riesgo de build:

| Recurso | Carga | Riesgo |
|---|---|---|
| `level1_nexus.glb` | `GLTFDocument.append_from_file` (`level1.gd:187-189`) | Sin `.import`; no está claro que se empaquete en el PCK |
| Kit 3A.1, dressing 3A.2, props, puertas, generador | `GLTFDocument` en `fm_level1_art_pass.gd:765/812/872/941` | Igual |
| HDR de entorno | `Image.load(ProjectSettings.globalize_path(...))` (`:208`) | `globalize_path` no es fiable en export |
| PNG generados | `Image.load(globalize_path(...))` (`:53`) | Igual |
| Linterna | `fm_player.gd:99-104` | Depende de recurso externo |

No se localizó `export_presets.cfg` ni evidencia de una build exportada. Esto se trata en la sección 11.

### 2.3. Matriz de pruebas ejecutadas

| Prueba | Comando / archivo | Resultado | Validez |
|---|---|---|---|
| Smoke | `godot --headless --path . tests/fm_level1_smoke.tscn` | PASS | Parcial: los rayos de sala nacen en y=-2.0 y aciertan techos |
| Walk | `tests/fm_level1_walk.tscn` | PASS 33/33 | Parcial: no entra en oficina, aseo ni conector |
| Doors | `tests/fm_level1_doors.tscn` | PASS, `DOOR_TEST_FAILS 0` | Buena, pero sin dos clientes reales |
| P0 ascensor/extracción | `/tmp/opencode/final_p0.gd` | PASS | Buena para single-player |
| Materiales | `/tmp/opencode/final_materials.gd` | 371 únicos, 20 triplanar, 0 sin mipmaps | Buena, con métricas a aclarar |
| Rendimiento 720p | `tests/fm_level1_perf.tscn` | 64 FPS, 817 draws, 704.584 prims | Buena, pero sin perfilador GPU |
| Rendimiento 1080p | `--resolution 1920x1080` | 17 FPS | Buena como síntoma, no como diagnóstico |
| Sonda de luces | `/tmp/opencode/audit_lights.gd` | 60 luces, 3 sombras | Buena |
| Sonda de rendimiento | `/tmp/opencode/audit_perf_probe.gd` | 2.502 mallas, 0 LOD, 0 occluders | Buena |
| Sonda de suelos | `/tmp/opencode/audit_floors.gd` | 12/12 impactan suelo a y=-5,65 | Buena; corrige el defecto del smoke |
| Coste de luces | `/tmp/opencode/perf_lights.gd` | 64 → 67 → 45 FPS | **No concluyente** |

### 2.4. Estado por subsistema

| Subsistema | Estado | Comentario |
|---|---|---|
| Funcional P0 | Aceptable | Puertas, ascensor, extracción y loot principales pasan |
| Iluminación | **No cumple** | Fuera de recepción se ve sin linterna; rellenos artificiales |
| Materiales | Mejorado, con deuda | 371 materiales; normales/roughness sin comprimir; props planos |
| Geometría | Parcial | Props simples, carteles duplicados, sin sombras de contacto |
| Físicas | Parcial | Colisiones AABB probables; escondites sin probar |
| Rendimiento | **No cumple** | 1080p 17 FPS; VRAM al 90 %; sin LOD/occlusion |
| Build | **No cumple** | Sin presets ni build; cargas runtime no export-safe |
| Documentación | Inconsistente | El informe de corrección afirma cosas que la medición no sostiene |

---

## 3. Auditoría de iluminación

### 3.1. Regla artística de referencia

La recepción es la única zona que puede conservar una iluminación ambiental relativamente funcional. Fuera de recepción, el nivel debe estar prácticamente a oscuras sin linterna: solo unas pocas luces de emergencia débiles, localizadas y con una luminaria o justificación física visible. No se permiten rellenos artificiales, iluminación ambiental general ni corredores uniformemente iluminados. La oscuridad debe seguir siendo legible con la linterna.

**Resultado: el nivel no cumple esta regla.** No es un matiz de intensidad: hay fuentes diseñadas explícitamente para que las salas no queden oscuras.

### 3.2. Entorno global

`Level1World` se crea en `level1.gd:201-244` y se sobrescribe en `fm_level1_art_pass.gd:200-270`:

| Propiedad | Valor actual | Problema |
|---|---:|---|
| `background_mode` | `BG_SKY` | Fondo de cielo global |
| `ambient_light_source` | `AMBIENT_SOURCE_SKY` | Ambiente global sin fuente visible |
| `ambient_light_energy` | **0.22** | Ilumina todas las salas por igual |
| `ambient_light_sky_contribution` | **0.72** | Refuerza el ambiente de cielo |
| `background_energy_multiplier` | 0.36 | — |
| `tonemap_mode` | AgX | Correcto |
| `tonemap_exposure` | **1.34** | Sube la exposición global |
| `tonemap_contrast` | 1.06 | — |
| `tonemap_saturation` | 1.04 | — |
| `tonemap_white` | 1.02 | — |
| SSAO | on, radio 1.15, intensidad 1.25 | Correcto, pero no compensa la falta de sombras |
| SSR | on, 40 pasos | Coste alto; los espejos se queman |
| SSIL | on, radio 2.0, intensidad 1.2 | Coste alto |
| Glow | on, intensidad 0.32, bloom 0.05, umbral 1.2 | Los carteles se queman |
| Fog | 0.005 | — |
| Volumetric fog | 0.012 | — |
| Ambient inject | 0.08 | — |

El ambiente de cielo es global; no se puede limitar a recepción con este `WorldEnvironment`. La solución correcta es bajar el ambiente global a un valor casi nulo y confiar en las luces locales de recepción, que ya existen y pueden conservarse.

### 3.3. Inventario de luces

**Total: 60 luces; solo 3 proyectan sombra.**

| Grupo | Cantidad | Tipo | Energía | Rango | Sombra | Observación |
|---|---:|---|---:|---:|---|---|
| `EmergencyLight_0..29` | 30 | Omni | 0.261–0.793 | 3.2–7.0 m | Solo `_0` | Demasiadas y demasiado fuertes |
| `EmergencyAlarmFlash` | 3 | Omni | 0.000 | — | No | Apagadas |
| Linterna | 3 | 2 Spot + 1 Omni | 12.0 / 2.2 / 0.32 | 24 / 11 / 0.55 | Spot principal sí | Correcta |
| `ART_CorridorSpot_*` | 4 | Spot | **3.8** | 10 m | **No** | Sin luminaria; causa principal del corredor |
| `ART_CorridorFill_*` | 4 | Omni | **1.05** | 9 m | **No** | Relleno artificial |
| `ART_RoomFill_*` | 7 | Omni | 0.30–0.56 | 3.5–8 m | **No** | Prohibidos fuera de recepción |
| `ART_Reception*` | 9 | Spot/Omni | 0.45–3.4 | 3.2–14 m | `ReceptionKey` sí | Excepción permitida; fuentes invisibles |

**Sombras reales:** `EmergencyLight_0`, `ART_ReceptionKey` y `Flashlight`. El informe de corrección afirmaba seis mapas de sombra de emergencia; el runtime solo tiene uno.

### 3.4. Causas confirmadas del exceso de luz

#### Causa 1 — Error de orden en el pase artístico

`fm_level1_art_pass.gd` ejecuta:

- `_dim_rooms_outside_reception()` en la **línea 38**.
- `_add_cinematic_lights()` en la **línea 42**.

La atenuación busca `ART_Corridor*` antes de que esas luces existan. Por eso los focos conservan **3.8** y los rellenos **1.05**, en lugar del 0.62 que sugiere el informe. La función `_dim_rooms_outside_reception` (líneas 800-809) solo atenúa emergencias fuera de recepción (×0.68) y no toca los `ART_RoomFill_*`.

**Corrección:** mover la llamada después de crear las luces y, preferiblemente, hacer que `_add_cinematic_lights` no cree luces de relleno fuera de recepción. No basta con atenuarlas: la regla prohíbe su existencia.

#### Causa 2 — Siete rellenos de sala explícitos

`_add_cinematic_lights` (líneas 643-653) crea:

| Luz | Energía | Rango | Color |
|---|---:|---:|---|
| `ART_RoomFill_Security` | 0.56 | 7.0 | Frío (0.42, 0.60, 0.86) |
| `ART_RoomFill_Control` | 0.52 | 7.0 | Frío |
| `ART_RoomFill_Vest` | 0.50 | 7.5 | Frío |
| `ART_RoomFill_Store` | 0.46 | 8.0 | Frío |
| `ART_RoomFill_Maint` | 0.50 | 8.0 | Frío |
| `ART_RoomFill_Office` | 0.38 | 4.5 | Frío |
| `ART_RoomFill_Rest` | 0.30 | 3.5 | Frío |

Estos rellenos se añadieron para que las salas no quedaran ámbar. Son exactamente el tipo de luz que la regla actual prohíbe.

#### Causa 3 — Ambiente global y exposición

`ambient_light_energy=0.22`, `sky_contribution=0.72` y `tonemap_exposure=1.34` elevan el nivel de negro de todo el nivel. Incluso sin luces locales, las paredes y el suelo se leen. El ambiente de cielo no tiene una fuente física dentro de la instalación.

#### Causa 4 — Falta de sombras

Solo tres luces proyectan sombra. Las otras 57 no, incluidas las 29 emergencias restantes, los cuatro focos y cuatro rellenos de corredor y los siete rellenos de sala. La luz atraviesa paredes y crea fugas entre salas. El resultado no es solo “demasiado brillante”: es una iluminación físicamente incoherente.

#### Causa 5 — Emergencias excesivas

Hay 30 luces de emergencia, varias por sala, con energías de 0.261 a 0.793 y rangos de hasta 7 m. La más fuerte está en el almacén (0.793). La atenuación real por parpadeo usa `_emergency_base_energy` mutado a ×0.52 y un factor de 0.86–1.0, es decir, **0.447–0.52 del valor original**. El 0.46 del pase artístico se pierde en el primer frame. No son “unas pocas luces débiles”: son 30 luces locales.

#### Causa 6 — Emisivos y bloom

Hay 26 grupos emisivos. Los más problemáticos:

| Material / grupo | Emisión | Efecto |
|---|---:|---|
| `NEXUS_SignText` (27 mallas) | **5.0** | Carteles quemados a blanco |
| `NEXUS_V05_MAT_Emergency_Lens` | **6.0** | Lentes de emergencia con bloom |
| `ART3A2_Bulb` | **5.0** | Bombillas sobreexpuestas |
| `ART3A1_CyanStrip` | 2.75 | Franjas cian |
| `DOOR_Cyan` | 1.94 | Puertas con halo |
| `NEXUS_CorridorLight` | 1.15 | Luminarias |
| `NEXUS_Green` / `NEXUS_Red` | 1.0 | Señalización |
| `NEXUS_V05_MAT_ExtractGlow` | 1.25 | Aro de extracción |

El glow global (0.32, bloom 0.05, umbral 1.2) amplifica el problema. Los carteles `SEGURIDAD`, `ALMACÉN`, `SALIDA` y `EXTRACCIÓN` pierden legibilidad.

### 3.5. Luminancia de las capturas

Medición sobre las capturas actuales (media sRGB; no es una medición fotométrica calibrada, pero sirve para comparar):

| Zona | Off | On | Lectura |
|---|---:|---:|---|
| Recepción | 19.57 | 25.35 | Excepción permitida |
| Corredor | **13.09** | 24.97 | Demasiado visible sin linterna |
| Seguridad | 16.00 | 29.97 | Monitores dominan; p90 78.4 |
| Control | 13.72 | 35.66 | Negro con dos pantallas blancas |
| Vestuarios | 3.86 | 17.83 | Aceptable en oscuridad |
| Almacén | **2.51** | 16.23 | Correcto en oscuridad |
| Mantenimiento | **10.04** | 24.97 | Generador legible sin linterna |
| Oficina | **11.91** | 32.25 | Mesa y monitor visibles sin linterna |
| Aseo | **20.28** | 41.99 | Más brillante que el corredor; inaceptable |
| Conector | 4.15 | 17.77 | Oscuro, pero con carteles flotantes |
| Ascensor | **22.96** | 39.75 | Demasiado visible; dos SALIDA |
| Extracción | 32.95 | 40.04 | Recepción; demasiado brillante para la tensión |

Un objetivo coherente con la regla sería: recepción 15–22; corredor ≤5; seguridad ≤5; control ≤4; vestuarios ≤3; almacén ≤2–3; mantenimiento ≤4; oficina ≤4; aseo ≤4; conector ≤3; ascensor ≤5; extracción 15–22 (por ser recepción). Los valores exactos deben validarse visualmente, no solo por media.

### 3.6. Conclusión de iluminación

El nivel no tiene un problema de “ajuste fino”. Tiene:

1. Un error de orden que impide que la atenuación funcione.
2. Siete rellenos de sala y ocho luces de corredor que no deberían existir.
3. Un ambiente global que ilumina todo.
4. Una ausencia casi total de sombras.
5. Un exceso de emisivos y bloom.

La corrección debe ser principalmente **eliminar** fuentes, no subir y bajar intensidades. La recepción puede conservar sus nueve luces, pero necesita que las fuentes sean visibles y que no haya carteles quemados.

---

## 4. Tabla de fuentes de luz por zona

La tabla resume las fuentes principales; no sustituye al inventario completo de la sección 3. “Emergencia” incluye `EmergencyLight_*`; “ART” incluye luces del pase artístico; “Emisivo” indica materiales que brillan sin iluminar.

| Zona | Fuentes principales | Energía / rango | Sombras | ¿Fuente visible? | Veredicto |
|---|---|---|---|---|---|
| Recepción | 9 ART + ~12 emergencias + emisivos de techo | 0.45–3.4 / 3.2–14 m | `ART_ReceptionKey` + `EmergencyLight_0` | No; discs emisivos no coinciden | Excepción permitida, pero fuentes incoherentes |
| Corredor | 4 Spot ART + 4 Omni ART + ~8 emergencias | **3.8** / 10 m; **1.05** / 9 m | No | **No** | **Crítico**: charco frío sin luminaria |
| Seguridad | 1 RoomFill + 1 emergencia + monitores | 0.56 / 7 m; 0.687 | No | Parcial (monitores) | Demasiado visible por monitores |
| Control | 1 RoomFill + 1 emergencia fría + 2 monitores | 0.52 / 7 m; 0.351 | No | Monitores | Oscuro, pero pantallas quemadas |
| Vestuarios | 1 RoomFill + 2 emergencias | 0.50 / 7.5 m; 0.585/0.483 | No | Luminarias no claras | Aceptable en oscuridad |
| Almacén | 1 RoomFill + 1 emergencia | 0.46 / 8 m; **0.793** | No | Luminaria colgante apagada | Oscuro correcto; emergencia demasiado fuerte |
| Mantenimiento | 1 RoomFill + 3 emergencias + generador | 0.50 / 8 m; hasta 0.7 | No | No | Generador legible sin linterna |
| Oficina | 1 RoomFill + 2 emergencias | 0.38 / 4.5 m; 0.465/0.335 | No | No | Demasiado visible sin linterna |
| Aseo | 1 RoomFill + 2 emergencias + espejo | 0.30 / 3.5 m; 0.401/0.371 | No | No | **El más brillante fuera de recepción** |
| Conector | 2 emergencias + emisivos | 0.4–0.7 | No | No | Oscuro, pero carteles flotantes |
| Ascensor | 1 emergencia + extracción emisiva | 0.261 | No | No | Demasiado visible; dos SALIDA |
| Extracción | Luces de recepción + aro emisivo | 0.45–3.4 | `ReceptionKey` | Parcial | Recepción; demasiado brillante para la tensión |

**Nota:** las cifras de “emergencias” son aproximadas por zona; el inventario exacto está en `level1.gd:973-1021` y en la tabla de la sección 3.

---

## 5. Problemas visuales por zona

Referencias: `docs/fm_level1_full_audit/01_recepcion_off.png` … `12_extraccion_on.png`.

### 5.1. Recepción

**Bien:** composición, mostrador verde, logo NEXUS, directorio, aro de extracción, profundidad.

**Problemas:**
- Franja blanca quemada en el mostrador.
- Luminarias teal del techo parecen encendidas, pero son solo emisivas; las luces reales son invisibles.
- Dos carteles `ADMINISTRACIÓN` contiguos.
- Dos `SALIDA` apilados visibles desde la zona del ascensor.
- Pantalla de extracción quemada.
- La recepción es la excepción permitida, pero no debe ser un “piso de tienda”: debe tener contraste y zonas de sombra.

### 5.2. Corredor principal

**Bien:** profundidad, ritmo de vigas, hormigón sin manchas negras, tubería roja y puertas verdes legibles.

**Problemas:**
- Charco de luz fría en el suelo sin luminaria visible.
- Paredes y suelo legibles sin linterna (media 13.09).
- `SEGURIDAD` y señales con bloom blanco.
- Al encender la linterna, el viewmodel aparece como una esquirla blanca en la esquina inferior derecha.
- La linterna apenas cambia la lectura porque la sala ya está iluminada.

### 5.3. Seguridad

**Bien:** muro de seis monitores legible en verde/cian; mesa con tres monitores; sala oscura alrededor.

**Problemas:**
- Lavado rosado en la mesa.
- Posible artefacto estrellado blanco arriba a la derecha.
- Comparte utilería con control; poca identidad propia.
- Los monitores son la fuente principal de luz y elevan la media a 16.0 off.

### 5.4. Control de acceso

**Bien:** cumple la regla de oscuridad; la consola y el arco apenas se intuyen.

**Problemas:**
- Demasiado oscuro para su función: no se lee la consola.
- Dos monitores grandes son rectángulos blancos con líneas negras, sin interfaz legible.
- El contraste es “negro + pantalla quemada”, no iluminación funcional.

### 5.5. Vestuarios

**Bien:** atmósfera ámbar, taquillas, banco, señal de piso mojado, caja.

**Problemas:**
- Taquillas repetitivas sin números, etiquetas ni desgaste.
- Cartel `DUCHA` con panel blanco/lechoso que parece una fuga.
- Poca lectura de la función de vestuario.
- La luz ámbar es aceptable, pero debe ser localizada y con fuente visible.

### 5.6. Almacén

**Bien:** es la zona más correcta en oscuridad (media 2.51); cartel `ALMACÉN // SECTOR C`; estanterías y cajas apenas visibles.

**Problemas:**
- Cajas de colores planos, sin fibra, etiquetas ni desgaste; siluetas simples.
- Luminaria colgante apagada.
- Línea naranja gruesa en el suelo.
- La variación de cajas prometida por el informe no se ve en la captura.

### 5.7. Mantenimiento

**Bien:** generador EN2500 detallado y legible; caldera, tuberías, cartel `SALA DE MÁQUINAS`.

**Problemas:**
- El generador es un portátil EN2500, no una máquina industrial fija.
- El charco de luz que ilumina el generador no tiene fuente visible.
- La caldera sigue siendo un cilindro marrón liso con bandas; los 42 remaches no se ven.
- La etiqueta `CALDERA 02 / PRESIÓN CRÍTICA` flota y no respeta profundidad.
- El vapor no se ve; el cartel se refleja en el cristal; banco y tablero vacíos.
- La sala se lee sin linterna (media 10.04).

### 5.8. Oficina

**Bien:** escritorio, silla, estantería, monitor y reloj; escala íntima correcta.

**Problemas:**
- Mesa y monitor visibles sin linterna (media 11.91).
- Pared trasera vacía; baldas sin soportes ni objetos.
- Rectángulo negro en el techo.
- Poca narrativa: no hay documentos, carpetas, cables, notas ni rastros de evacuación.

### 5.9. Aseo

**Bien:** azulejos, lavabo, botiquín verde, espejo.

**Problemas:**
- El espejo domina con dos manchas especulares blancas enormes.
- Es la zona más brillante fuera de recepción (media 20.28 off).
- No se lee claramente el inodoro; la función sanitaria es ambigua.
- Los azulejos parecen paneles; falta desgaste, juntas y humedad.
- El botiquín verde es el único acento de color.

### 5.10. Conector de servicio

**Bien:** pasillo estrecho y claustrofóbico; vigas, paneles verdes y marcos metálicos.

**Problemas:**
- Letreros `MANTENIMIENTO`, `MUELLE`, `PELIGRO` cortados o angulados.
- Triángulos naranjas flotando en suelo y pared.
- Utilería amontonada sin función clara.
- Viewmodel blanco en la esquina.
- La oscuridad es correcta, pero la señalización rompe la credibilidad.

### 5.11. Ascensor

**Bien:** puertas, aro de extracción verde, luz roja de emergencia, control.

**Problemas:**
- Puertas casi negras y lisas; poca lectura metálica.
- Dos `SALIDA` apilados.
- El control es diminuto; el reloj está en la hoja.
- Pantalla blanca quemada.
- La luz roja es fuerte y la zona se ve sin linterna (media 22.96).

### 5.12. Extracción

**Bien:** recepción, mostrador, carteles, aro verde y letrero `EXTRACCIÓN`.

**Problemas:**
- Es la zona de recepción, pero está demasiado iluminada para una extracción tensa (media 32.95 off).
- No hay sensación de peligro ni de “última carrera”.
- La pantalla de extracción está quemada.
- La extracción no debería ser un espacio neutro; debe tener una puesta en escena propia dentro de recepción.

---

## 6. Materiales y texturas

### 6.1. Inventario

| Métrica | Valor |
|---|---:|
| Materiales únicos | 371 |
| Materiales triplanares | 20 (19 activos) |
| Materiales activos | 409 |
| Texturas únicas | 227 |
| Texturas comprimidas | 75 únicas / 142 slots |
| Texturas sin mipmaps ≥64 px | 0 |
| Texturas 2048² | 110 |
| Texturas 1024² | 92 |
| Texturas 512×256 | 11 |
| Texturas 512² | 10 |
| Texturas 256² | 3 |
| Texturas 1×1 | 1 |
| VRAM estimada de texturas | ~2.848,8 MB |

### 6.2. Lo que está bien

- `NEXUS_Concrete_Dark`, `NEXUS_Concrete` y `NEXUS_V05_MAT_Rec_Wall` usan triplanar 0.32; el suelo `NEXUS_V05_MAT_Floor_Worn` usa 0.45 y clearcoat off.
- Los albedos de hormigón y suelo son 1024/2048, comprimidos S3TC y con mipmaps.
- `NEXUS_V05_MAT_Rec_Floor` también es triplanar, sin clearcoat, con mipmaps y compresión.
- `NEXUS_Water`: alpha 0.42, transparente, roughness 0.055.
- `NEXUS_V05_MAT_Shard`: alpha 0.48, transparente, roughness 0.12.
- `NEXUS_V05_MAT_Pipe_Red`: 2048 en albedo/normal/roughness, metallic 0.18, roughness 0.9.
- `NEXUS_Glass`: roughness 0.085, clearcoat 0.28.
- Las manchas negras del hormigón de la auditoría anterior ya no aparecen en las capturas.
- Los espejos ya no son negros.

### 6.3. Deuda principal

1. **Normales y roughness sin comprimir.** La compresión solo cubre albedos opacos ≥512. Las normales y roughness de 1024/2048 siguen en formato sin comprimir, lo que explica buena parte de los ~2,85 GB.
2. **Demasiadas texturas 2K.** 110 texturas de 2048² para un nivel de este tamaño; muchas son props que no necesitan 2K.
3. **Props con PBR por defecto.** `WetFloorSign_01.002` y `wall_clock.002` tienen metallic 1.0 y roughness 1.0; `SchoolChair_01` y `metal_office_desk` tienen roughness 1.0. El resultado es aspecto plano/yeso.
4. **Espejos sobreexpuestos.** `NEXUS_Mirror_Soft` y `NEXUS_V05_MAT_ELEV_MIRROR`: metallic 0.92, roughness 0.075. Con SSR y luces directas producen manchas blancas.
5. **Emisivos excesivos.** `NEXUS_SignText` 5.0, `Emergency_Lens` 6.0, `ART3A2_Bulb` 5.0, `CyanStrip` 2.75. El bloom los quema.
6. **Métrica de compresión inconsistente.** El informe dice 147; la sonda de materiales dice 142; la sonda de texturas únicas dice 75. Son métricas distintas (slots vs texturas), pero el documento no lo aclara. Para producción hace falta una única definición y una comprobación en el export.

### 6.4. Recomendaciones de material

| Material | Cambio | Motivo |
|---|---|---|
| `NEXUS_Mirror_Soft` | roughness 0.075 → 0.20; metallic 0.92 → 0.86 | Evitar clipping especular |
| `NEXUS_V05_MAT_ELEV_MIRROR` | Igual | Igual |
| `NEXUS_SignText` | emission 5.0 → 1.3 | Carteles legibles |
| `NEXUS_V05_MAT_Emergency_Lens` | 6.0 → 2.0 | Lentes sin bloom |
| `ART3A2_Bulb` | 5.0 → 1.5 | Bombillas |
| `ART3A1_CyanStrip` | 2.75 → 1.2 | Franjas |
| `DOOR_Cyan` | 1.94 → 1.0 | Puertas |
| `NEXUS_V05_MAT_ExtractGlow` | 1.25 → 0.8 | Aro de extracción |
| `WetFloorSign_01.002` | metallic 1.0 → 0.0; roughness 1.0 → 0.55 | Plástico |
| `wall_clock.002` | metallic 1.0 → 0.2; roughness 1.0 → 0.5 | Reloj |
| `SchoolChair_01` | roughness 1.0 → 0.6; metallic 0.0–0.1 | Metal pintado |
| `metal_office_desk` | roughness 1.0 → 0.55; metallic 0.1 | Mesa metálica |

---

## 7. Geometría y ambientación

### 7.1. Métricas

| Métrica | Valor |
|---|---:|
| MeshInstance3D totales | 2.502 |
| MeshInstance3D visibles | 2.407 |
| Con culling de distancia | 219 (`visibility_range_end=18 m`) |
| LOD | 0 |
| OccluderInstance3D | 0 |
| StaticBody3D | 570 |
| CollisionShape3D | 601 |
| Colliders generados | 511 |
| Draw calls | 817 |
| Primitivas | 704.584 |
| Objetos | 9.919 |

### 7.2. Problemas

- **Sin LOD ni occlusion.** Todo se dibuja; 2.407 mallas visibles y 817 draws.
- **Sin sombras de contacto.** El pase artístico pone todas las mallas de dressing con `cast_shadow=OFF`; los props no proyectan sombra y parecen flotar. AL-09 sigue confirmado.
- **Colisiones AABB.** `_setup_collisions` (`level1.gd:272-297`) usa `global_transform * get_aabb()` y deduplica por AABB exacta. Para mallas rotadas puede crear cajas sobredimensionadas, paredes invisibles o bloqueos en esquinas. No se validó con cápsula.
- **Blacklist de colliders.** `_skip_collider` filtra tokens como `MAT`, `PLATE`, `SIGN`, `LOOT`, `TRAP`, `EXTRACT`, `RING`, `TRIGGER`, `GRILLE`, `VENT_SLAT`. Puede omitir colisiones válidas; conviene una whitelist explícita.
- **Props simples.** La caldera sigue siendo un cilindro con bandas; los 42 remaches no se ven; la etiqueta flota. El generador es un portátil EN2500. Las cajas del almacén son cajas planas.
- **Carteles.** Dos `SALIDA` en el ascensor; dos `ADMINISTRACIÓN` en recepción; letreros cortados/angulados en el conector; triángulos naranjas flotantes.
- **Topología.** La auditoría anterior reportó 25.010 boundary edges, 8.124 non-manifold y duplicados; no se re-midió en esta fase. Sigue pendiente.
- **Oficina y aseo.** La oficina está vacía de narrativa; el aseo no se lee como sanitario.
- **Viewmodel de linterna.** Al encender, aparece una esquirla blanca en la esquina inferior derecha; el material/geometría del viewmodel necesita revisión.

### 7.3. Recomendaciones de geometría

- Activar `cast_shadow` en muebles, cajas, puertas, generador, caldera y props grandes; dejarlo off en decals, señales y piezas pequeñas.
- Sustituir AABB por trimesh/convex para arquitectura estática y cajas ajustadas para props.
- Reconstruir caldera con cuerpo, bridas, remaches de 0.04 m, escotilla, tuberías, válvula y manómetro; placa con `depth_test` on, sin `no_depth_test`.
- Sustituir el generador portátil por un skid industrial o añadir carcasa, bancada, escape, cables y panel.
- Variar cajas con 3 tamaños, etiquetas, flejes, esquinas desgastadas y materiales distintos.
- Eliminar duplicados de carteles y alinear la señalización a paredes; sustituir triángulos flotantes por decals o soportes.
- Añadir narrativa a oficina (documentos, carpetas, cables, notas, taza, silla girada) y aseo (inodoro, dispensador, cortina, desagüe, azulejos).

---

## 8. Físicas y colisiones

### 8.1. Verificado

- Puertas: **6/6** cerradas/abiertas; `DOOR_TEST_FAILS 0`; colliders, teclado 0451, liberación de mantenimiento, cooperación, alerta, energía y serialización/late join simulado.
- Ascensor: `ElevatorBody` es `AnimatableBody3D` con `sync_to_physics=true`; rayo cerrado impacta `ElevatorLeafBody`; abierto impacta `COL_334_NEXUS_V05_ELEV_SIM_WALL_N`; `P0_ELEV_SYNC true -> false`.
- Extracción con botín: `P0_CARRY_INSIDE picked=true inside_area=true count=1`; `P0_CARRY_OUTSIDE inside_area=false count=0`.
- Suelos: las 12 zonas impactan un collider a y=-5,65. Recepción, corredor, seguridad, control, vestuarios, almacén, mantenimiento y conector tienen colliders propios; oficina, aseo, ascensor y extracción comparten la losa de recepción.
- Loot: case 17 kg/640, sample 9 kg/900, crate 42 kg/1800 con `min_players=2`, docs 0.6 kg/220, drive 0.4 kg/1200. La extracción exige `delivered>0` y que queden jugadores vivos dentro; el crate no se puede recoger en single-player por diseño.

### 8.2. Pendiente / dudoso

- **AABB sobredimensionadas.** No se probó con cápsula en esquinas, marcos de puerta ni pasillos estrechos. Es probable que haya paredes invisibles o bloqueos.
- **Blacklist de colliders.** `_skip_collider` puede omitir colisiones válidas; no se auditó collider por collider.
- **Escondites.** Hay 3 (`HideCabinet` -15.40,-2.375; `HideLocker` -18.20,5.5; `HideShelf` -7.20,5.5) pero no se probaron en gameplay: entrada, salida, cámara, colisión, detección del Vigilante.
- **Masas y fricción.** No se auditaron todos los rigid bodies; puede haber jitter o props que se deslizan.
- **Extracción con un jugador fuera.** La secuencia solo se cancela si no queda ningún jugador vivo dentro. Si uno sale y otro queda, la secuencia continúa. Es una regla ambigua que debe definirse y probarse con dos jugadores.
- **Dos clientes reales.** No se probó multijugador real; solo late join simulado.

---

## 9. Funcionalidad

### 9.1. Verificado

- Smoke PASS: `LEVEL1_COLLIDERS 511`, `TEST_ROOMS 10/10`, puertas 6/6, drawer, locker, alarm, east, watcher patrol=6, noise state=2, move, extraction `state=1 delivered=1`.
- `TEST_LIGHTS true general=0 art=24 emergency=30 flashlight=3`.
- Walk PASS 33/33, final `(-17.23673, -5.649189, -9.919288)`.
- Doors PASS, `DOOR_TEST_FAILS 0`.
- P0 PASS (ascensor, sync, carga dentro/fuera).
- Materiales y texturas: 371 materiales, 20 triplanar, 0 sin mipmaps.

### 9.2. Problemas de validez

1. **`TEST_ROOMS 10/10` no prueba lo que dice.** Los rayos de `TEST_ROOM` empiezan en y=-2.0, por encima de techos de oficina/aseo/control; algunos impactos son `OFFICE_HVAC_CURB`, `OFFICE_ROOF`, `ACC_ARCH_TOP`, no el suelo. La prueba de suelos corregida (rayos desde y=-5.0) sí impacta suelo en las 12 zonas, pero no valida acceso, puertas ni navegación.
2. **El walk no cubre las 12 zonas.** Entra en recepción, corredor, seguridad, control, vestuarios, almacén, mantenimiento y ascensor; **no entra en oficina, aseo ni conector de servicio**. No se puede afirmar que las 12 zonas sean accesibles y funcionales.
3. **Vigilante sin pruebas completas.** Solo se probó patrol=6 y noise state=2. No se probó cono de visión, congelación al ser observado, movimiento al perder contacto visual, investigación de ruido, persecución, captura, búsqueda de escondites ni comportamiento con varios jugadores.
4. **Linterna/batería sin prueba funcional.** No se auditó drenaje, recarga, apagado/encendido, viewmodel ni interacción con el estrés.
5. **Escondites sin prueba.**
6. **Multijugador real sin prueba.** Todo es single-player o late join simulado.
7. **Interacciones secundarias.** Drawer, locker, alarma y puerta este pasan; no se probaron todos los props interactivos.

### 9.3. Extracción

- Área 15.8 × 2.6 × 9.8; radio de entrega 2.4 m; activación 2.0 s; secuencia 6.7 s.
- `delivered>0` basta para completar; no se exige entregar todos los objetos.
- Si un jugador sale y queda otro dentro, la secuencia no se cancela; solo se cancela si no queda ningún jugador vivo dentro.
- El crate de 42 kg tiene `min_players=2`; en single-player no se puede recoger. Es coherente con el diseño co-op, pero debe documentarse y probarse con dos jugadores.

---

## 10. Rendimiento

### 10.1. Mediciones

| Resolución | FPS | Draws | Primitivas | Objetos | VRAM | GPU util |
|---|---:|---:|---:|---:|---:|---:|
| 1280×720 | 64 | 817 | 704.584 | 9.919 | 3.706 MiB | 25 % |
| 1920×1080 | **17** | 817 | 704.584 | 9.925 | 3.702 MiB | 25 % |

Hardware: NVIDIA GTX 1650 Ti 4 GB, 32 GB RAM, Intel Core i5. VSync off, Vigilante off.

### 10.2. Diagnóstico

- **VRAM al 90 % del límite.** 227 texturas únicas, 110 de 2048² y 92 de 1024²; normales y roughness sin comprimir. La estimación de texturas es ~2.848,8 MB.
- **Sin LOD ni occlusion.** 2.407 mallas visibles; 0 LOD; 0 occluders; solo 219 props con culling de distancia a 18 m.
- **Submission de draws.** 817 draws y 9.919 objetos; el GPU util del 25 % sugiere cuello de botella de CPU/submission o memoria, no de rasterizado puro.
- **Efectos caros.** SSR 40 pasos, SSIL, SSAO, volumétrica, glow, 60 luces.
- **Prueba de luces no concluyente.** Base 64 FPS; desactivar sombras de emergencia 67; desactivar todas las luces `ART_` 45. El resultado empeoró al quitar luces, probablemente por recompilación de shaders o ruido de medición. No se puede concluir que las luces sean la causa principal.
- **Sin perfiles de calidad.** No hay Low/Medium/High/Ultra ni render scale; todo está al máximo.
- **No hay medición con perfilador GPU/RenderDoc.** Falta desglose de CPU, GPU, memoria y shaders.

### 10.3. Objetivos propuestos

- 1920×1080: ≥45–60 FPS estables en GTX 1650 Ti.
- VRAM: <3.200 MiB.
- Draws: <500.
- Primitivas: <500.000.
- Objetos: <5.000.
- Luces: ≤20–25; sombras: 6–8 selectivas.
- Texturas 2K: <40; texturas únicas: <150.
- Perfiles Low/Medium/High/Ultra con render scale.

---

## 11. Build y producción

### 11.1. Estado

- **No existe `export_presets.cfg`.**
- **No se generó ninguna build.**
- `project.godot` define escena principal `scenes/menu.tscn`, viewport 1280×720, stretch `canvas_items`, Forward+.
- **No hay `.import`** para:
  - `assets/models/fm/level1_nexus.glb`
  - `assets/models/fm/art3a1/level1_art3a1_kit.glb`
  - `assets/models/fm/art3a2/level1_dressing.glb`
  - `assets/models/fm/props/industrial_generator.glb`
  - `assets/models/fm/doors/level1_doors.glb`
  - `assets/models/fm/flashlight_nexus.glb`
  - HDR de entorno
  - 19 PNG de `assets/art/fm/generated/`

### 11.2. Riesgo

Las cargas runtime usan:

- `GLTFDocument.append_from_file` (`level1.gd:187-189`).
- `Image.load(ProjectSettings.globalize_path(...))` (`fm_level1_art_pass.gd:53`, `:208`).
- `GLTFDocument` para kit/dressing/props/generador (`:765/812/872/941`).
- `fm_player.gd:99-104` para la linterna.

En un export, `globalize_path("res://...")` puede apuntar a una ruta del sistema que no existe en el PCK, y los GLB sin `.import` pueden no empaquetarse. El resultado probable es un nivel sin texturas, pantallas, modelos o linterna. **No se puede declarar el nivel listo para producción sin una build exportada y probada en una máquina limpia.**

### 11.3. Requisitos mínimos de build

1. Crear `export_presets.cfg` para Linux y Windows.
2. Importar todos los GLB, HDR y PNG en el editor; verificar `.import`.
3. Sustituir cargas runtime por `load()`/`preload()` de recursos importados o por `PackedScene`.
4. Exportar con `--export-release` y ejecutar en una carpeta limpia.
5. Verificar que el nivel carga las 12 zonas, texturas, pantallas, linterna y extracción.
6. Medir FPS/VRAM en la build, no solo en el editor.

---

## 12. Regresiones y discrepancias con el informe de corrección

| Afirmación del informe | Medición actual | Veredicto |
|---|---|---|
| 6 mapas de sombra de emergencia | **3 luces con sombra en total** (1 emergencia) | **Incorrecto / regresión** |
| 147 texturas comprimidas | 75 únicas / 142 slots | Métrica inconsistente; no verificable como “147” |
| 20 materiales triplanares | 20 total, 19 activos | Menor, aceptable |
| Atenuación exterior 0.78→0.68 | Focos de corredor a **3.8** y rellenos a **1.05** | **No aplicada** por orden de llamadas |
| 1920×1080 28–35 FPS | **17 FPS** | **No se sostiene**; peor |
| `SALIDA` duplicada no reproducida | `11_ascensor_off.png` muestra dos `SALIDA` | **Persiste** |
| Caldera detallada con remaches/válvula | Cilindro liso; remaches invisibles; etiqueta flotante | **Parcial/insuficiente** |
| Cajas de almacén variadas | Cajas planas, sin fibra/etiquetas | **Parcial** |
| P0 completado y verificado | P0 de ascensor/extracción PASS | **Correcto** |
| Walk 33/33 | PASS, pero no cubre oficina/aseo/conector | **Correcto con cobertura incompleta** |
| Doors 0 fallos | PASS | **Correcto** |
| Iluminación “mejorada” con rellenos fríos | Viola la regla artística actual | **Dirección contraria** |

**Conclusión:** el informe de corrección no es una base fiable para cerrar el nivel. Algunas correcciones son reales (P0, materiales, mipmaps, agua/esquirlas, espejos no negros, pantallas de seguridad), pero las afirmaciones sobre sombras, compresión, FPS 1080p, carteles y caldera no se sostienen con la evidencia actual.

---

## 13. Hallazgos por prioridad

### 13.1. Tabla resumen

| ID | Severidad | Zona | Hallazgo | Evidencia | Esfuerzo |
|---|---|---|---|---|---|
| L1-IL-01 | **CRÍTICO** | Todo el nivel | Iluminación ambiental/rellenos violan la regla; se ve sin linterna | Off medias 10–23; luces 3.8/1.05; 7 fills; ambiente 0.22 | M |
| L1-PE-01 | **CRÍTICO** | Todo | 1080p 17 FPS; VRAM 3.7/4 GB; sin LOD/occlusion | Perf 1080p; sonda 0 LOD/0 occluders | L |
| L1-BU-01 | **CRÍTICO** | Producción | Sin export presets ni build | `export_presets.cfg` ausente | M |
| L1-BU-02 | **CRÍTICO** | Producción | Cargas runtime no export-safe (GLB/HDR/PNG sin `.import`) | `globalize_path`, `append_from_file` | L |
| L1-IL-02 | ALTO | Todo | Solo 3 luces con sombra; fugas de luz | 60 luces, 3 sombras | M |
| L1-IL-03 | ALTO | Todo | 30 emergencias excesivas (hasta 0.793 / 7 m) | Tabla de luces | M |
| L1-IL-04 | ALTO | Señales/pantallas | Emisivos y bloom queman carteles y monitores | Emission 5.0–6.0; capturas | S |
| L1-ME-01 | ALTO | Aseo/ascensor | Espejos con manchas blancas | Capturas 09/11; metallic 0.92/rough 0.075 | S |
| L1-ME-03 | ALTO | Todo | 2.85 GB de texturas; normales/roughness sin comprimir | 227 texturas; 110 2K; 75 comprimidas | L |
| L1-GE-01 | ALTO | Todo | Props sin sombras de contacto; flotan | `cast_shadow=OFF`; AL-09 | M |
| L1-GE-02 | ALTO | Todo | Colisiones AABB sobredimensionadas / skip tokens | `level1.gd:272-297` | M |
| L1-FU-01 | ALTO | 12 zonas | Cobertura real no probada; smoke inválido; walk incompleto | Rayos y=-2; walk sin oficina/aseo/conector | M |
| L1-FU-02 | ALTO | Vigilante | Sin pruebas de observación, persecución, nav, captura | Solo patrol/noise | M |
| L1-PE-02 | ALTO | Todo | 720p sin margen; CPU/submission-bound | 64 FPS, 817 draws, 9.9k objetos, GPU 25% | L |
| L1-RE-01 | ALTO | Documentación | El informe de corrección afirma cosas no sostenidas | Tabla de regresiones | S |
| L1-IL-05 | MEDIO | Recepción/corredor | Fuentes de luz invisibles; luminarias no coinciden | Capturas; sin fixtures | M |
| L1-ME-02 | MEDIO | Props | PBR por defecto; aspecto plano | Metallic 1.0/rough 1.0 | M |
| L1-ME-04 | MEDIO | Materiales | Métrica de compresión inconsistente | 147 vs 142 vs 75 | S |
| L1-GE-03 | MEDIO | Mantenimiento | Caldera simple, remaches invisibles, etiqueta flotante; generador portátil | Captura 07 | M |
| L1-GE-04 | MEDIO | Recepción/ascensor/conector | Carteles duplicados, cortados o flotantes | Capturas 01/10/11 | S |
| L1-GE-05 | MEDIO | GLB | Topología con boundary/non-manifold (heredado) | Auditoría anterior; no re-medido | L |
| L1-GE-06 | MEDIO | Oficina | Sin narrativa; baldas vacías; techo negro | Captura 08 | S |
| L1-GE-07 | MEDIO | Aseo | Función sanitaria poco legible; espejo domina | Captura 09 | M |
| L1-GE-08 | MEDIO | Almacén | Cajas planas sin etiquetas/desgaste | Captura 06 | M |
| L1-FI-01 | MEDIO | Extracción | Secuencia continúa con un jugador fuera | `fm_reception_extraction.gd` | S |
| L1-FI-02 | MEDIO | Extracción | Crate solo co-op; no documentado en juego | `min_players=2` | S |
| L1-FI-03 | MEDIO | Escondites | 3 escondites sin probar | `HideCabinet/Locker/Shelf` | M |
| L1-FI-04 | MEDIO | Multijugador | Sin prueba real de 2 clientes | Solo late join simulado | L |
| L1-FU-03 | MEDIO | Linterna | Batería/viewmodel sin prueba funcional | `fm_player.gd` | S |
| L1-PE-03 | MEDIO | Todo | Sin perfiles de calidad ni render scale | `project.godot` | M |
| L1-PE-04 | MEDIO | Todo | Coste de luces no concluyente | 64→67→45 FPS | S |
| L1-GE-09 | MEDIO | Corredor/control | Viewmodel blanco; monitores sin UI | Capturas 02/04 | S |
| L1-RE-02 | MEDIO | Documentación | Corrección de luces opuesta a la regla actual | 7 fills | S |

### 13.2. Fichas detalladas — CRÍTICOS

#### L1-IL-01 — CRÍTICO — La iluminación fuera de recepción viola la regla artística

- **A) Diagnóstico:** el corredor, mantenimiento, oficina, aseo y ascensor son legibles sin linterna. Hay siete rellenos de sala, ocho luces de corredor y un ambiente global de cielo. La recepción es la única excepción permitida, pero el resto del nivel no debe verse sin linterna.
- **B) Ubicación:** `scripts/fm/fm_level1_art_pass.gd:22-46` (orden), `:200-270` (entorno), `:592-653` (luces), `:800-809` (atenuación); `scripts/fm/level1.gd:201-244` (entorno base).
- **C) Causa:** confirmada. `_dim_rooms_outside_reception()` se ejecuta en la línea 38 y `_add_cinematic_lights()` en la 42; la atenuación no ve las luces de corredor. Además, `_add_cinematic_lights` crea siete `ART_RoomFill_*` y ocho luces de corredor; el entorno usa `ambient_light_source=SKY`, energía 0.22 y exposición 1.34.
- **D) Corrección:** eliminar o desactivar los rellenos y focos fuera de recepción; bajar el ambiente global a 0.02–0.04; ajustar exposición a 1.0–1.1; conservar las luces de recepción; mover la atenuación después de crear luces y hacer que no cree nada fuera de recepción.
- **E) Instrucciones concretas:**

  | Fuente | Ubicación | Config actual | Acción | Resultado esperado |
  |---|---|---|---|---|
  | `ART_CorridorSpot_-15/-5/5/15` | corredor | Spot 3.8, rango 10, ángulo 48, shadow off | **Eliminar/desactivar** | Desaparece el charco frío sin fuente |
  | `ART_CorridorFill_-18/-6/6/18` | corredor | Omni 1.05, rango 9, shadow off | **Eliminar/desactivar** | Corredor solo con emergencias débiles |
  | `ART_RoomFill_Security/Control/Vest/Store/Maint/Office/Rest` | 7 salas | Omni 0.30–0.56, rango 3.5–8 | **Eliminar/desactivar** | Salas oscuras; solo emergencias |
  | `ambient_light_energy` | `Level1World` | 0.22 | **0.02–0.04** | Negros reales fuera de recepción |
  | `ambient_light_sky_contribution` | `Level1World` | 0.72 | 0.4–0.5 | Menos ambiente de cielo |
  | `tonemap_exposure` | `Level1World` | 1.34 | 1.0–1.1 | Menos lavado global |
  | `_dim_rooms_outside_reception` | línea 38 | antes de crear luces | **Mover después** de `_add_cinematic_lights()` | Atenuación efectiva |
  | `_add_cinematic_lights` | 592-653 | crea fills/focos | **No crear luces fuera de recepción** | La regla se cumple por diseño |

  Orden: primero eliminar fuentes; después bajar ambiente/exposición; después mover la atenuación; por último ajustar emergencias. No subir luces para compensar.
- **F) Precauciones:** la recepción debe seguir siendo legible; no apagar sus nueve luces sin sustituirlas. Verificar que la linterna tenga suficiente alcance (24 m) y que la oscuridad no impida navegar. No usar `ambient_light_source=DISABLED` sin probar la recepción. Los cambios de exposición afectan a todas las capturas.
- **G) Aceptación:** capturas off de corredor, seguridad, control, vestuarios, almacén, mantenimiento, oficina, aseo, conector, ascensor y extracción ≤5 de media (excepto recepción/extracción 15–22); sin linterna no se leen paredes opuestas ni muebles a más de 3–4 m; con linterna se leen superficies y props; cada pool de luz tiene fuente visible.
- **H) Regresión:** `tests/fm_level1_smoke.tscn` (luces y puertas), walk 33/33, capturas 12×2, medir 720p/1080p, comprobar que la recepción no queda negra.

#### L1-PE-01 — CRÍTICO — 1080p a 17 FPS y VRAM al 90 %

- **A) Diagnóstico:** el nivel no es jugable a 1920×1080 en la GTX 1650 Ti de referencia. La misma geometría que a 720p da 64 FPS cae a 17 FPS; la VRAM está a 3.702/4.096 MiB y la GPU solo se usa al 25 %.
- **B) Ubicación:** `tests/fm_level1_perf.tscn`; `project.godot`; `fm_level1_art_pass.gd:1346-1406` (compresión/culling); `level1.gd` (carga de GLB).
- **C) Causa:** confirmada como síntoma; probable combinación de presión de VRAM (227 texturas, 110 2K, normales/roughness sin comprimir), 817 draws, 9.919 objetos, 2.407 mallas visibles, 0 LOD/occlusion y efectos caros (SSR 40, SSIL, volumétrica).
- **D) Corrección:** reducir memoria de texturas, añadir LOD/occlusion, batchear geometría estática, reducir draws/objetos, perfilar con RenderDoc/Godot y añadir perfiles de calidad.
- **E) Instrucciones:** comprimir normales/roughness; bajar props de 2K a 1K; atlas de materiales; `<500` draws; `<5.000` objetos; LOD para props y arquitectura; occlusion para pasillos; perfil Medium por defecto; render scale 0.85–1.0; desactivar SSR/SSIL en Low; medir después de cada cambio.
- **F) Precauciones:** no reducir calidad visual a ciegas; medir FPS/VRAM en la build, no solo en editor; no confundir GPU 25 % con “no hay cuello de botella”; puede ser CPU/submission.
- **G) Aceptación:** 1080p ≥45 FPS estables (ideal 60), VRAM <3.200 MiB, sin stutter, 720p ≥60 FPS con margen; perfil Medium jugable en la GTX 1650 Ti.
- **H) Regresión:** perf 720p/1080p, capturas, walk, puertas; comparar antes/después con la misma escena y posición.

#### L1-BU-01 — CRÍTICO — No existe build ni presets de exportación

- **A) Diagnóstico:** no hay `export_presets.cfg` ni evidencia de una build. El nivel solo se ha ejecutado desde el editor/proyecto.
- **B) Ubicación:** raíz del proyecto; `project.godot`.
- **C) Causa:** confirmada: ausencia de presets y de build.
- **D) Corrección:** crear presets Linux/Windows, exportar y probar en carpeta limpia.
- **E) Instrucciones:** `Project > Export`; añadir Linux/X11 y Windows Desktop; configurar `export_path`; incluir `assets/`, `scenes/`, `scripts/`; exportar release; ejecutar con `--path` limpio; comprobar logs.
- **F) Precauciones:** no declarar “build lista” hasta ejecutar el binario; los tests headless no sustituyen una build.
- **G) Aceptación:** build arranca, menú carga, nivel 1 carga las 12 zonas, texturas/modelos/linterna/pantallas presentes, extracción funciona, FPS medidos.
- **H) Regresión:** smoke/walk/doors en build; repetir tras cada cambio de carga de recursos.

#### L1-BU-02 — CRÍTICO — Cargas runtime no export-safe

- **A) Diagnóstico:** el nivel carga GLB/HDR/PNG con `GLTFDocument.append_from_file` e `Image.load(globalize_path(...))`; no hay `.import` para esos recursos.
- **B) Ubicación:** `level1.gd:187-189`; `fm_level1_art_pass.gd:53`, `:208`, `:765/812/872/941`; `fm_player.gd:99-104`.
- **C) Causa:** confirmada en código; probable fallo en export. `globalize_path("res://...")` puede resolver a una ruta inexistente en el PCK; los GLB sin import no se empaquetan.
- **D) Corrección:** importar todos los recursos, usar `load()`/`preload()` o `PackedScene`, y cargar HDR/PNG como `Texture2D` importadas.
- **E) Instrucciones:** abrir el editor y dejar que genere `.import`; reemplazar `GLTFDocument` por escena importada; reemplazar `Image.load(globalize_path)` por `load("res://...")`; verificar rutas en `.pck`; probar build.
- **F) Precauciones:** no romper la carga actual mientras se migra; mantener fallback; validar texturas y pantallas.
- **G) Aceptación:** build sin errores de recursos; todas las texturas/modelos/pantallas cargan; linterna visible; nivel completo.
- **H) Regresión:** ejecutar build en máquina limpia; comparar capturas editor vs build.

### 13.3. Fichas detalladas — ALTOS

#### L1-IL-02 — ALTO — Solo 3 luces proyectan sombra; fugas de luz

- **A) Diagnóstico:** 60 luces, solo `EmergencyLight_0`, `ART_ReceptionKey` y `Flashlight` tienen sombra. Las demás atraviesan paredes y crean pools incoherentes.
- **B) Ubicación:** `level1.gd:973-1021` (emergencias), `fm_level1_art_pass.gd:592-653` (ART).
- **C) Causa:** confirmada; el informe afirmaba 6 sombras de emergencia, pero solo hay 1.
- **D) Corrección:** activar sombras en 6–8 luces clave (una por sala, focos de recepción, linterna) y dejar el resto sin sombra; reducir luces.
- **E) Instrucciones:** `shadow_enabled=true` en emergencias principales; `shadow_bias`/`shadow_normal_bias` ajustados; no activar en las 30; medir coste.
- **F) Precauciones:** las sombras cuestan; no pasar de 8–10; evitar acne/peter-panning.
- **G) Aceptación:** sin fugas visibles a través de paredes; 720p ≥50 FPS; 1080p ≥45 FPS.
- **H) Regresión:** sonda de luces, perf, capturas off/on.

#### L1-IL-03 — ALTO — 30 luces de emergencia excesivas

- **A) Diagnóstico:** 30 omnis de 0.261–0.793 y 3.2–7 m; varias por sala; la más fuerte en almacén 0.793. No son “pocas luces débiles”.
- **B) Ubicación:** `level1.gd:973-1021`; `fm_level1_art_pass.gd:272-293`.
- **C) Causa:** confirmada; además el flicker multiplica por 0.52 y 0.86–1.0, así que la atenuación del pase artístico se pierde.
- **D) Corrección:** reducir a 10–14, energía 0.15–0.35, rango 2.5–4.5, una por sala/umbral, con luminaria visible.
- **E) Instrucciones:** conservar las de recepción y una por sala; eliminar duplicados; almacén 0.35 máximo; activar sombra solo en 2–3; `light_volumetric_fog_energy` 0.15–0.25.
- **F) Precauciones:** no dejar salas sin ninguna referencia; la linterna debe ser la fuente principal.
- **G) Aceptación:** ≤14 emergencias; off ≤5 de media fuera de recepción; cada luz tiene fixture.
- **H) Regresión:** sonda de luces, capturas, perf.

#### L1-IL-04 — ALTO — Emisivos y bloom queman carteles, lentes y pantallas

- **A) Diagnóstico:** `NEXUS_SignText` 5.0, `Emergency_Lens` 6.0, `ART3A2_Bulb` 5.0, `CyanStrip` 2.75; glow 0.32 y umbral 1.2. Los carteles y monitores se ven blancos.
- **B) Ubicación:** materiales en `fm_level1_art_pass.gd:464-573`; glow en `:200-270`.
- **C) Causa:** confirmada.
- **D) Corrección:** bajar emisión y glow; ajustar threshold; revisar UI de monitores.
- **E) Instrucciones:** valores de la tabla 6.4; glow 0.18, bloom 0.02, threshold 1.5; monitores de control con textura/UI legible, no blanco.
- **F) Precauciones:** no perder legibilidad de señales; probar en off/on.
- **G) Aceptación:** textos legibles sin halo blanco; pantallas con contenido; sin clipping.
- **H) Regresión:** capturas 01/02/04/11/12; sonda de materiales.

#### L1-ME-01 — ALTO — Espejos quemados en aseo y ascensor

- **A) Diagnóstico:** dos manchas blancas enormes en el espejo del aseo; espejo del ascensor también brillante.
- **B) Ubicación:** `NEXUS_Mirror_Soft`, `NEXUS_V05_MAT_ELEV_MIRROR`; `fm_level1_art_pass.gd` materiales; SSR.
- **C) Causa:** confirmada: metallic 0.92, roughness 0.075, SSR y luces directas.
- **D) Corrección:** roughness 0.18–0.25, metallic 0.82–0.88, albedo más oscuro; reducir SSR o usar reflection probe.
- **E) Instrucciones:** ajustar ambos materiales; si persiste, bajar `ssr_max_steps` a 24 o desactivar SSR en aseo; probar con linterna.
- **F) Precauciones:** no convertir el espejo en un panel negro; debe reflejar la sala.
- **G) Aceptación:** sin manchas blancas; reflejo legible; sin clipping.
- **H) Regresión:** capturas 09/11 off/on.

#### L1-ME-03 — ALTO — 2.85 GB de texturas y normales/roughness sin comprimir

- **A) Diagnóstico:** 227 texturas únicas, 75 comprimidas, 110 de 2048², 92 de 1024²; normales/roughness sin comprimir; VRAM 3.7/4 GB.
- **B) Ubicación:** `assets/art/fm/generated/`, `assets/models/fm/**`; `fm_level1_art_pass.gd:1346-1392`.
- **C) Causa:** confirmada por sonda; la compresión solo cubre albedos opacos ≥512.
- **D) Corrección:** comprimir normales/roughness, bajar props a 1K, atlas, reducir únicas.
- **E) Instrucciones:** VRAM compression en normales/roughness; 2K solo para superficies héroe; props 512/1K; objetivo <150 texturas, <40 2K; verificar en export.
- **F) Precauciones:** la compresión de normales puede introducir artefactos; usar BC5/BPTC si está disponible; comparar.
- **G) Aceptación:** VRAM <3.2 GB; sin artefactos visibles; 1080p estable.
- **H) Regresión:** perf, capturas, sonda de texturas.

#### L1-GE-01 — ALTO — Props sin sombras de contacto

- **A) Diagnóstico:** todas las mallas de dressing tienen `cast_shadow=OFF`; los props flotan y no hay contacto visual.
- **B) Ubicación:** `fm_level1_art_pass.gd:811-830`.
- **C) Causa:** confirmada; AL-09 sigue.
- **D) Corrección:** activar sombras en props grandes y muebles; dejar off en decals/señales.
- **E) Instrucciones:** `cast_shadow=ON` para escritorios, sillas, cajas, generador, caldera, puertas; `OFF` para carteles, cristales, partículas; SSAO on.
- **F) Precauciones:** coste de sombras; no activar en 2.400 mallas.
- **G) Aceptación:** props apoyados; sombras bajo mesa/cajas; sin pop.
- **H) Regresión:** capturas 06/07/08; perf.

#### L1-GE-02 — ALTO — Colisiones AABB sobredimensionadas y skip tokens

- **A) Diagnóstico:** 511 colliders generados por AABB mundial; posible paredes invisibles en mallas rotadas. `_skip_collider` puede omitir colisiones válidas.
- **B) Ubicación:** `level1.gd:246-297`.
- **C) Causa:** probable; no validada con cápsula.
- **D) Corrección:** trimesh/convex para arquitectura, cajas ajustadas para props, whitelist de colliders.
- **E) Instrucciones:** probar cápsula en puertas, esquinas y pasillos; sustituir AABB en mallas rotadas; revisar tokens `MAT/PLATE/SIGN/TRIGGER/GRILLE`; documentar.
- **F) Precauciones:** no romper puertas/ascensor; conservar colliders P0.
- **G) Aceptación:** recorrido completo sin bloqueos invisibles; sin atravesar paredes; 511 → número justificado.
- **H) Regresión:** walk, doors, P0, cápsula en 12 zonas.

#### L1-FU-01 — ALTO — Cobertura de las 12 zonas no probada

- **A) Diagnóstico:** `TEST_ROOMS 10/10` usa rayos desde y=-2.0 y acierta techos; el walk no entra en oficina, aseo ni conector. No hay prueba real de acceso a las 12 zonas.
- **B) Ubicación:** `tests/fm_level1_smoke.tscn`, `tests/fm_level1_walk.tscn`; `audit_floors.gd`.
- **C) Causa:** confirmada metodológica.
- **D) Corrección:** nueva prueba de 12 zonas con rayos desde el jugador/suelo y walk completo.
- **E) Instrucciones:** por zona, teleport a entrada, ray desde `y=-5.0`, assert collider de suelo y trigger; walk con waypoints a oficina, aseo, conector; validar puertas.
- **F) Precauciones:** no confundir “hay suelo” con “se puede acceder”.
- **G) Aceptación:** 12/12 zonas accesibles, suelo correcto, sin bloqueos.
- **H) Regresión:** smoke, walk, doors.

#### L1-FU-02 — ALTO — Vigilante sin pruebas de comportamiento completas

- **A) Diagnóstico:** solo patrol=6 y noise state=2; no se probó observación, congelación, movimiento al perder LOS, persecución, captura, búsqueda de escondites ni varios jugadores.
- **B) Ubicación:** `level1.gd:1359-1375`; script del Vigilante.
- **C) Causa:** cobertura de pruebas insuficiente.
- **D) Corrección:** pruebas scriptadas de estados y percepción.
- **E) Instrucciones:** escenarios: jugador mira → freeze; deja de mirar → move; ruido → investigate; chase; catch; hide; dos jugadores. Medir tiempos y distancias.
- **F) Precauciones:** no ajustar IA sin medición; conservar comportamiento emergente.
- **G) Aceptación:** cada estado se activa y sale correctamente; sin atravesar paredes; captura consistente.
- **H) Regresión:** smoke watcher, walk, capturas.

#### L1-PE-02 — ALTO — 720p sin margen; CPU/submission-bound

- **A) Diagnóstico:** 64 FPS a 720p con 817 draws, 9.919 objetos, 704k prims y GPU 25 %. El margen es pequeño y el 1080p cae a 17.
- **B) Ubicación:** `level1.gd`, `fm_level1_art_pass.gd`; escena.
- **C) Causa:** probable CPU/submission + VRAM; falta perfilado.
- **D) Corrección:** reducir draws/objetos, batchear, LOD/occlusion, perfiles.
- **E) Instrucciones:** medir con Godot profiler/RenderDoc; agrupar mallas estáticas; MultiMesh para props repetidos; `<500` draws, `<5.000` objetos; LOD.
- **F) Precauciones:** no romper colisiones ni materiales al mergear.
- **G) Aceptación:** 720p ≥60 con margen; 1080p ≥45.
- **H) Regresión:** perf, walk, capturas.

#### L1-RE-01 — ALTO — El informe de corrección no es fiable

- **A) Diagnóstico:** afirma 6 sombras de emergencia (hay 1), 147 texturas comprimidas (75 únicas/142 slots), 28–35 FPS a 1080p (17), SALIDA corregida (sigue duplicada), caldera detallada (sigue simple) y atenuación 0.68 (3.8/1.05).
- **B) Ubicación:** `docs/FM_LEVEL1_CORRECTION_REPORT.md`.
- **C) Causa:** confirmada por comparación.
- **D) Corrección:** corregir el informe o retirarlo como fuente de verdad; anexar mediciones.
- **E) Instrucciones:** actualizar tabla de estado; marcar pendientes; no declarar PASS sin evidencia; enlazar capturas/perf.
- **F) Precauciones:** no borrar el histórico; añadir fechas y condiciones.
- **G) Aceptación:** cada afirmación tiene comando/captura/medición.
- **H) Regresión:** revisión documental.

### 13.4. Fichas compactas — MEDIOS y BAJOS

- **L1-IL-05 (MEDIO) — Fuentes invisibles.** A) Los pools de luz no tienen luminaria; los discs teal son emisivos, no luces. B) `fm_level1_art_pass.gd` luces/recepción; mallas de techo. C) Confirmada. D) Añadir downlights o alinear spot bajo el disc; eliminar emisivos sin luz. E) Crear fixture 0.15 m, spot debajo; recepción. F) No añadir nuevas luces fuera de recepción. G) Cada pool tiene fuente. H) Capturas off/on.
- **L1-ME-02 (MEDIO) — Props PBR planos.** A) Metallic 1.0/roughness 1.0 en señales/reloj; sillas/mesas roughness 1.0. B) Materiales de props. C) Confirmada. D) Ajustar metallic/roughness. E) Tabla 6.4. F) No todos los props son metálicos. G) Aspecto creíble. H) Capturas 05/07/08.
- **L1-ME-04 (MEDIO) — Métrica de compresión.** A) 147 vs 142 vs 75. B) Informe/sondas. C) Definiciones distintas. D) Documentar “slots” vs “texturas únicas”. E) Añadir sonda única. F) No mezclar. G) Una cifra reproducible. H) Sonda.
- **L1-GE-03 (MEDIO) — Caldera/generador.** A) Caldera cilindro liso; remaches invisibles; etiqueta flotante; generador portátil. B) `_detail_boiler` 982-1039; generador 934-965. C) Confirmada. D) Reconstruir/detallar. E) Remaches 0.04 m, bridas, válvula, manómetro; placa con depth test; skid industrial. F) No romper colisión. G) Silueta/detalle a 3 m. H) Captura 07.
- **L1-GE-04 (MEDIO) — Carteles.** A) Dos SALIDA, dos ADMINISTRACIÓN, letreros cortados, triángulos flotantes. B) Ascensor/recepción/conector. C) Confirmada. D) Eliminar duplicados, alinear, decals. E) Uno por salida; soportes. F) No tapar rutas. G) Señalización legible. H) Capturas 01/10/11.
- **L1-GE-05 (MEDIO) — Topología GLB.** A) 25.010 boundary, 8.124 non-manifold (heredado). B) `level1_nexus.glb`. C) Probable; no re-medido. D) Limpiar malla. E) Merge by distance, recalc normals, remove interior. F) Backup. G) Boundary ~0. H) Re-medición.
- **L1-GE-06 (MEDIO) — Oficina vacía.** A) Poca narrativa; baldas sin soportes; techo negro. B) Oficina. C) Confirmada. D) Añadir documentos, carpetas, cables, notas, taza. E) Props pequeños; luces locales. F) Rendimiento. G) Escena narrativa. H) Captura 08.
- **L1-GE-07 (MEDIO) — Aseo poco legible.** A) Espejo domina; no se lee inodoro; azulejos planos. B) Aseo. C) Confirmada. D) Añadir inodoro/cubículo/dispensador; reducir espejo; juntas. E) Geometría simple. F) No bloquear. G) Función clara. H) Captura 09.
- **L1-GE-08 (MEDIO) — Cajas planas.** A) 45 mallas, 3 materiales, sin etiquetas/desgaste. B) Almacén. C) Confirmada. D) Variar tamaño/etiqueta/flejes. E) 3 variantes, decals. F) No aumentar draws. G) Cajas creíbles. H) Captura 06.
- **L1-FI-01 (MEDIO) — Extracción con jugador fuera.** A) La secuencia sigue si queda uno dentro. B) `fm_reception_extraction.gd`. C) Confirmada. D) Definir regla: cancelar si sale cualquiera o avisar. E) Cambiar `_physics_process`; probar 2 jugadores. F) No romper single-player. G) Regla clara. H) Test 2P.
- **L1-FI-02 (MEDIO) — Crate solo co-op.** A) 42 kg, `min_players=2`; no recogible solo. B) `fm_reception_loot.gd`. C) Diseño. D) Documentar en UI/tutorial o dar alternativa. E) Texto de misión. F) No desequilibrar. G) Jugador entiende. H) Test 1P/2P.
- **L1-FI-03 (MEDIO) — Escondites sin probar.** A) 3 escondites. B) `level1.gd:1266-1291`. C) Sin evidencia. D) Probar entrada/salida/cámara/colisión/detección. E) Script. F) No atravesar geometría. G) 3/3 funcionales. H) Test.
- **L1-FI-04 (MEDIO) — Sin 2 clientes.** A) Solo late join simulado. B) red. C) Cobertura. D) Probar 2 instancias. E) Host + client; reconnect. F) No declarar multijugador. G) Sincronización. H) Test.
- **L1-FU-03 (MEDIO) — Linterna sin prueba.** A) Batería/viewmodel. B) `fm_player.gd:84-166`. C) Sin evidencia. D) Probar drenaje, recarga, apagado, viewmodel. E) Script. F) No romper luz. G) Funcional. H) Test/capturas.
- **L1-PE-03 (MEDIO) — Sin perfiles.** A) Todo al máximo. B) `project.godot`. C) Confirmada. D) Low/Medium/High/Ultra + render scale. E) Ajustes. F) Default Medium. G) Perfiles estables. H) Perf.
- **L1-PE-04 (MEDIO) — Coste de luces no concluyente.** A) 64→67→45. B) `perf_lights.gd`. C) Ruido/recompilación. D) Perfilar con GPU timers. E) Medir con escena estable. F) No concluir. G) Diagnóstico claro. H) Perf.
- **L1-GE-09 (MEDIO) — Viewmodel/monitores.** A) Esquirla blanca al encender; monitores de control sin UI. B) `fm_player.gd`; pantallas. C) Confirmada. D) Corregir geometría/material; añadir textura UI. E) Revisar viewmodel; textura 512. F) No tapar pantalla. G) Sin artefacto; UI legible. H) Capturas 02/04.
- **L1-RE-02 (MEDIO) — Corrección opuesta a la regla.** A) Se añadieron 7 fills para evitar salas ámbar. B) `fm_level1_art_pass.gd:643-653`. C) Confirmada. D) Retirar fills; usar emergencias. E) Ver IL-01. F) No compensar con ambiente. G) Regla cumplida. H) Capturas.

---

## 14. Instrucciones técnicas consolidadas

Esta sección ordena las acciones para una segunda fase ejecutable. **No se han aplicado en esta auditoría.**

### 14.1. Orden de trabajo

1. **Iluminación (P0):** eliminar fuentes fuera de recepción; bajar ambiente/exposición; mover atenuación; reducir emergencias; ajustar emisivos; capturas off/on.
2. **Sombras y materiales (P1):** activar sombras selectivas; corregir espejos, props y texturas; comprimir normales/roughness.
3. **Geometría y señalización (P1):** carteles, caldera, generador, cajas, oficina, aseo, colisiones.
4. **Funcionalidad (P1/P2):** 12 zonas, Vigilante, escondites, extracción 2P, linterna.
5. **Rendimiento (P2):** LOD/occlusion, batching, perfiles, 1080p.
6. **Build (P0/P3):** presets, importación, export, prueba limpia.

### 14.2. Cambios exactos por archivo

| Archivo | Línea / zona | Cambio |
|---|---|---|
| `scripts/fm/fm_level1_art_pass.gd` | 22-46 | Mover `_dim_rooms_outside_reception()` después de `_add_cinematic_lights()` |
| `scripts/fm/fm_level1_art_pass.gd` | 200-270 | `ambient_light_energy` 0.22 → 0.02–0.04; `tonemap_exposure` 1.34 → 1.0–1.1; glow 0.32 → 0.18; bloom 0.05 → 0.02; threshold 1.2 → 1.5 |
| `scripts/fm/fm_level1_art_pass.gd` | 592-653 | Eliminar `ART_RoomFill_*` y `ART_Corridor*`; conservar solo recepción |
| `scripts/fm/fm_level1_art_pass.gd` | 800-809 | La atenuación debe cubrir cualquier ART restante; no crear luces fuera de recepción |
| `scripts/fm/fm_level1_art_pass.gd` | 272-293 | Emergencias: 30 → 10–14; energía 0.15–0.35; rango 2.5–4.5 |
| `scripts/fm/fm_level1_art_pass.gd` | 464-573 | Emisivos: SignText 5.0→1.3; Lens 6.0→2.0; Bulb 5.0→1.5; Cyan 2.75→1.2; DOOR_Cyan 1.94→1.0; ExtractGlow 1.25→0.8 |
| `scripts/fm/fm_level1_art_pass.gd` | 811-830 | `cast_shadow=ON` en props grandes; OFF en decals |
| `scripts/fm/fm_level1_art_pass.gd` | 934-1039 | Caldera/generador: geometría y etiqueta |
| `scripts/fm/fm_level1_art_pass.gd` | 1346-1392 | Compresión de normales/roughness; downsizing |
| `scripts/fm/level1.gd` | 246-297 | Colliders: trimesh/convex; whitelist; probar cápsula |
| `scripts/fm/level1.gd` | 973-1021 | Reducir emergencias; sombras selectivas |
| `scripts/fm/level1.gd` | 187-189 | Carga GLB export-safe |
| `scripts/fm/level1.gd` | 201-244 | Entorno base coherente con el pase artístico |
| `scripts/fm/fm_reception_extraction.gd` | `_physics_process` | Regla de cancelación con jugador fuera |
| `scripts/fm/fm_player.gd` | 84-166 | Linterna/viewmodel; prueba de batería |
| `project.godot` | — | Perfiles de calidad, render scale; no cambiar main scene sin motivo |
| `export_presets.cfg` | — | Crear Linux/Windows |

### 14.3. Precauciones globales

- No aplicar todos los cambios a la vez; hacer una captura off/on después de cada bloque.
- No compensar la oscuridad con ambiente; usar la linterna.
- No activar sombras en las 60 luces; elegir 6–8.
- No comprimir normales sin comparar artefactos.
- No borrar colliders P0.
- No declarar build válida sin ejecutarla.
- No usar el informe de corrección como fuente de verdad; usar este documento y las mediciones.

---

## 15. Plan P0–P3 para la segunda fase

### P0 — Restaurar la regla artística y viability mínima

**Objetivo:** que el nivel vuelva a ser de terror: recepción funcional, resto oscuro con linterna, sin rellenos artificiales.

**Alcance:** L1-IL-01, L1-IL-02, L1-IL-03, L1-IL-04, L1-IL-05.

**Archivos:** `fm_level1_art_pass.gd`, `level1.gd`.

**Pasos:**
1. Eliminar `ART_RoomFill_*` y `ART_Corridor*`.
2. Bajar ambiente/exposición.
3. Mover atenuación después de crear luces.
4. Reducir emergencias a 10–14; energía/rango; sombras selectivas.
5. Bajar emisivos/glow.
6. Capturas 12×2 y medición de luminancia.
7. Smoke/walk/perf.

**Dependencias:** ninguna; es el primer bloque.

**Riesgos:** dejar la recepción demasiado oscura; perder legibilidad; sombras caras.

**Aceptación:** off ≤5 fuera de recepción; on legible; 12/12 capturas; 720p ≥55 FPS; sin fugas.

**Pruebas:** smoke, walk, capturas, sonda de luces, perf.

### P1 — Corregir defectos visuales y de juego que rompen la lectura

**Objetivo:** eliminar artefactos, props flotantes, carteles duplicados, espejos quemados y mejorar la narrativa.

**Alcance:** L1-ME-01, L1-ME-02, L1-ME-04, L1-GE-01..08, L1-FI-01..03, L1-FU-01..03.

**Archivos:** materiales, `fm_level1_art_pass.gd`, `level1.gd`, `fm_reception_extraction.gd`, `fm_player.gd`, escenas de props.

**Pasos:**
1. Espejos y props PBR.
2. Sombras de contacto.
3. Carteles/caldera/generador/cajas/oficina/aseo.
4. Colisiones AABB y cápsula.
5. 12 zonas, Vigilante, escondites, linterna, extracción 2P.
6. Capturas y tests.

**Dependencias:** P0 (la iluminación cambia la lectura de todos los props).

**Riesgos:** tocar colisiones y romper puertas/ascensor; coste de sombras; props nuevos con draws.

**Aceptación:** sin artefactos; 12/12 zonas; tests funcionales; capturas aprobadas.

**Pruebas:** smoke, walk, doors, P0, escondites, Vigilante, capturas.

### P2 — Rendimiento y cobertura

**Objetivo:** 1080p jugable y margen para 720p.

**Alcance:** L1-PE-01..04, L1-ME-03, L1-GE-05.

**Archivos:** `fm_level1_art_pass.gd`, `level1.gd`, `project.godot`, texturas.

**Pasos:**
1. Perfilar con Godot/RenderDoc.
2. Comprimir normales/roughness; bajar texturas.
3. LOD/occlusion; batching/MultiMesh.
4. Perfiles Low/Medium/High/Ultra; render scale.
5. Medir 720p/1080p; VRAM; draws.
6. Repetir capturas.

**Dependencias:** P1 (geometría estable).

**Riesgos:** pérdida de calidad; artefactos de compresión; LOD popping.

**Aceptación:** 1080p ≥45 FPS; VRAM <3.2 GB; draws <500; objetos <5.000; sin stutter.

**Pruebas:** perf 720p/1080p, capturas, walk.

### P3 — Producción, build y cierre

**Objetivo:** build reproducible y nivel demostrable.

**Alcance:** L1-BU-01, L1-BU-02, L1-RE-01, L1-FI-04.

**Archivos:** `export_presets.cfg`, cargas de recursos, documentación.

**Pasos:**
1. Crear presets Linux/Windows.
2. Importar GLB/HDR/PNG; migrar cargas.
3. Exportar release; ejecutar en carpeta limpia.
4. Probar 12 zonas, texturas, linterna, extracción.
5. Prueba 2 clientes/reconnect.
6. Actualizar documentación y informe.

**Dependencias:** P0–P2.

**Riesgos:** recursos faltantes; rutas; diferencias editor/build.

**Aceptación:** build arranca y completa el nivel; sin errores de recursos; FPS medidos; documentación actualizada.

**Pruebas:** build limpia, smoke/walk/doors, 2 clientes, capturas build.

---

## 16. Pruebas no realizadas, limitaciones y conclusión

### 16.1. Pruebas no realizadas

- Build exportada Linux/Windows y ejecución en máquina limpia.
- Prueba real de dos clientes, reconexión y autoridad de servidor.
- Vigilante completo: visión, congelación, persecución, captura, búsqueda de escondites, dos jugadores.
- Escondites: entrada, salida, cámara, colisión y detección.
- Linterna: batería, recarga, apagado/encendido, viewmodel.
- Todas las masas/fricciones de rigid bodies.
- Topología del GLB re-medida.
- Perfilado GPU/RenderDoc y desglose CPU/GPU.
- Rendimiento tras las correcciones.
- Audio, comunicación por proximidad, radio y voces.
- Accesibilidad y opciones de calidad.
- Prueba de estrés con criaturas, partículas y multijugador.
- Verificación de licencias de todos los assets externos.

### 16.2. Limitaciones de la auditoría

- Las capturas son evidencia visual, no una medición fotométrica calibrada; la media sRGB sirve para comparar, no para sustituir un estudio de luz.
- La prueba de coste de luces no es concluyente; no debe usarse para afirmar que las luces son la causa principal del bajo FPS.
- `TEST_ROOMS 10/10` es inválido en varias salas por el origen de los rayos; la sonda de suelos corrige el dato de suelo, pero no prueba acceso.
- No se re-midió la topología del GLB; el dato de 25.010 boundary edges es heredado.
- No se auditó audio ni multijugador real.
- No se probó la build porque no existe.

### 16.3. Conclusión

El Nivel 1 tiene una base funcional y un trabajo artístico aprovechable, pero **no está terminado**. La iluminación actual no cumple la regla de terror, el rendimiento a 1080p no es jugable, la VRAM está al límite y el build no está validado. La corrección anterior mejoró materiales y P0, pero añadió rellenos de luz que hoy son un problema y dejó afirmaciones que la evidencia no sostiene.

La siguiente fase debe empezar por **quitar luz**, no por añadirla: eliminar rellenos y focos fuera de recepción, bajar el ambiente, reducir emergencias y hacer que la linterna sea la fuente principal. Después corregir sombras, materiales, carteles, colisiones y cobertura funcional. El rendimiento y el build son bloqueadores de producción, no “pendientes menores”.

**Estado final de esta auditoría:** documentación completa; no se modificó el proyecto; no se declara el nivel apto para producción.

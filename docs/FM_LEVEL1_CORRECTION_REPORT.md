# FRECUENCIA MUERTA — Informe de corrección integral del Nivel 1

**Fecha:** 2026-11-04 17:12 COT  
**Ámbito:** Nivel 1 y sus doce zonas (recepción, corredor principal, seguridad, control de acceso, vestuarios, almacén, mantenimiento, oficina, aseo, conector de servicio, ascensor y extracción).  
**Referencia:** `docs/FM_LEVEL1_FULL_TECHNICAL_AUDIT.md`.  
**Estado:** corrección P0 completada y verificada; P1 mayormente completada; P2/P3 parcialmente completadas. No se hicieron commits.

---

## 1. Resumen ejecutivo

Se corrigieron los tres defectos críticos de la auditoría y la mayor parte de los defectos altos de materiales, UV, iluminación y física que afectaban la lectura comercial del Nivel 1.

Resultados principales:

- **CR-01 resuelto:** la extracción cuenta el botín transportado por un jugador presente en recepción, además del depositado junto al ascensor. Se deduplica por instancia.
- **CR-02 resuelto:** las hojas del ascensor tienen cuerpos `AnimatableBody3D` que se mueven con la geometría. El rayo de prueba golpea la hoja cerrada y deja de golpearla al abrir.
- **CR-03 resuelto:** las grandes superficies arquitectónicas usan materiales triplanares con escala métrica; se eliminó el estiramiento por UV inválidas. También se corrigieron mipmaps, duplicados de material y el clearcoat global del suelo.
- **P1:** se sustituyó la textura de pared que producía manchas negras, se incorporaron normales/roughness reales para metal verde y oxidado, se respetaron los materiales originales de sillas/escritorios, se corrigió `DOOR_Rust`, agua, esquirlas, espejos, pantallas, doble cristal del mostrador, tubería roja y el doble sistema de charcos.
- **P2:** se equilibró la dominancia ámbar, se añadieron carcasas y suspensión a las luminarias de emergencia, se sustituyeron pantallas planas por interfaces legibles y se corrigió el muro de monitores de Seguridad. El generador y la caldera recibieron geometría y detalles nuevos.
- **P3:** se sustituyó el generador provisional por un GLB detallado, se añadieron remaches, válvula y placa a la caldera, se variaron las cajas de almacén, se ajustaron damping y material físico de los `RigidBody3D`, se comprimieron texturas y se amplió el culling de props pequeños.

**Verificación:** smoke PASS, walk PASS 33/33, puertas PASS, P0 PASS, sonda de materiales sin texturas 2K sin mipmaps. Se generaron 34 capturas nuevas con y sin linterna y una comparativa antes/después.

**Limitación principal:** el rendimiento no se recuperó al baseline de la auditoría. Las mediciones a 1280×720 oscilaron entre **59 y 78 FPS** (817 draws, 704.584 primitivas, ~10.000 objetos); la ventana de 1920×1080 dio **28–35 FPS** en el test (el proyecto mantiene un viewport lógico de 1280×720 con stretch). La memoria de vídeo sigue en ~3,7 GB / 4 GB. No se implementaron LOD ni occlusion culling. Esto queda documentado como pendiente, no como mejora conseguida.

---

## 2. Metodología y alcance

Se trabajó únicamente sobre el Nivel 1 y sus recursos directos. No se modificaron:

- `fotos-referencia/`.
- El sistema general de puertas (solo se corrigió el material `DOOR_Rust` y los defectos del ascensor incluidos en P0).
- Cajones, taquillas interactivas, alarmas, loot, IA, red/multijugador, inventario ni sistemas de interacción ajenos.
- Otros niveles ni la arquitectura maestra de Blender.

Cada corrección se verificó con al menos una de estas vías:

1. Prueba funcional headless (`smoke`, `walk`, `doors`).
2. Sonda runtime de propiedades de materiales, colisiones o cuerpos físicos.
3. Captura de juego con linterna y comparación visual.
4. Medición de rendimiento y memoria.

No se declara terminado ningún defecto que no haya pasado su prueba correspondiente.

---

## 3. Defectos corregidos

### 3.1. P0 — Críticos

#### CR-01 — Extracción con botín en las manos

**Estado: CORREGIDO Y VERIFICADO.**

`scripts/fm/level1.gd::get_delivered_loot_count()` ahora:

- Cuenta el botín dentro del radio de entrega.
- Cuenta también `player.carried_item` cuando el jugador está dentro de `ReceptionExtraction`.
- Deduplica por `get_instance_id()` para no contar dos veces el mismo objeto.

Evidencia de la prueba `final_p0`:

```text
P0_CARRY_INSIDE picked=true inside_area=true count=1
P0_CARRY_OUTSIDE inside_area=false count=0
P0_RESULT PASS
```

También se conserva el caso del test de humo: `TEST_EXTRACTION true state=1 delivered=1`.

#### CR-02 — Colliders del ascensor desincronizados

**Estado: CORREGIDO Y VERIFICADO.**

Se eliminó la generación automática de `StaticBody3D` para las hojas del ascensor y se creó un `AnimatableBody3D` hermano por hoja, con `sync_to_physics = true` y una caja de colisión del tamaño de la hoja. El tween mueve la hoja visual y el cuerpo físico en paralelo.

Evidencia:

```text
P0_ELEV_BODY NEXUS_V05_C_REC_ELEV_L ok=true class=AnimatableBody3D sync=true
P0_ELEV_BODY NEXUS_V05_C_REC_ELEV_R ok=true class=AnimatableBody3D sync=true
P0_ELEV_RAY_CLOSED ElevatorLeafBody
P0_ELEV_RAY_OPEN COL_334_NEXUS_V05_ELEV_SIM_WALL_N
P0_ELEV_SYNC true -> false
```

El rayo atraviesa el vano al abrir y vuelve a golpear la hoja al cerrar. No se modificó el sistema general de puertas.

#### CR-03 — UV inválidas en la arquitectura

**Estado: CORREGIDO CON TRIPLANAR MÉTRICO.**

El GLB principal no tiene UV utilizables en las grandes superficies. En lugar de reconstruir todas las UVs del GLB (riesgo alto para 2.000 nodos y materiales compartidos), el pase artístico aplica triplanar de mundo a los materiales arquitectónicos, con escala métrica:

| Material | Escala métrica |
|---|---:|
| Suelo (`floor`) | 0,45 |
| Pared (`wall`, `wall_dark`) | 0,32 |
| Zócalo (`wainscot`) | 0,60 |
| Hormigón de panel (`concrete_panel`) | 0,50 |

Las superficies que ya tienen UV propias (acero, pintura, madera, racks) usan UV normales para no pagar el coste del triplanar en todos los props. La sonda runtime confirma 20 materiales triplanares y que sillas/escritorios conservan `triplanar=false`.

### 3.2. P1 — Materiales, UV y texturas

| ID | Estado | Corrección |
|---|---|---|
| AL-01 | CORREGIDO | Los overrides se deduplican por `get_instance_id()` del material, no por nombre. Se procesan las instancias duplicadas. |
| AL-02 | CORREGIDO | `_load_texture()` genera mipmaps; el pase final genera mipmaps a todos los albedos usados. Sonda final: **0 texturas ≥64 px sin mipmaps**. |
| AL-03 | CORREGIDO | Se eliminó el clearcoat global del suelo. Solo los charcos locales conservan clearcoat. Sonda: `cc=false` en `Floor_Worn` y `Rec_Floor`. |
| AL-04 | CORREGIDO | Se usan las normales OpenGL reales de `green_metal_rust` y `rusty_metal_sheet` (convertidas de EXR a PNG) y sus roughness. Se redujo el metallic uniforme excesivo. |
| AL-05 | CORREGIDO | Se eliminaron los overrides de `SchoolChair_01` y `metal_office_desk`; conservan sus mapas originales. |
| AL-06 | CORREGIDO | `DOOR_Rust` recibe normal y roughness de óxido, metallic 0,32 y filtro con mipmaps en `fm_level1_door.gd`. |
| AL-07 | CORREGIDO | `NEXUS_Water` y `NEXUS_Meltwater` usan agua oscura translúcida; `NEXUS_V05_MAT_Shard` usa esquirlas translúcidas con cuerpo. |
| AL-08 | CORREGIDO | Se oculta la segunda luna del kit y se unifica el cristal restante con `ART_glass`. |
| AL-18 | CORREGIDO | Se filtran `WALLSTAIN`, `STORE_STAIN`, `DIS_WATER`, `DIS_OIL`, `DIS_HAND`, `GRIME` y `DAMP_PATCH` en `_skip_collider`. Ya no se crean cuerpos estáticos para decals. |
| AL-21 | CORREGIDO | La pantalla de extracción usa una textura de interfaz legible y emisión controlada. |
| AL-22 | CORREGIDO PARCIAL | Las cajas de almacén reciben variantes de madera/cartón y las bandas/etiquetas existentes se conservan. Sigue habiendo poca variación de silueta. |
| ME-10 | CORREGIDO | Espejos con albedo claro, metallic 0,92 y roughness 0,075. |
| ME-11 | CORREGIDO PARCIAL | Política métrica mediante triplanar en arquitectura; los props conservan UV. |
| ME-12 | CORREGIDO | `NEXUS_V05_MAT_Pipe_Red` usa acero tintado rojo con desgaste y normal. |
| ME-14 | CORREGIDO | Se eliminó el segundo sistema del pase artístico. Todos los charcos usan `assets/art/fm/floor_wet.tres` y se reparten en siete posiciones. |

#### Textura de pared

La textura `worn_plaster_wall_diff_2k.jpg` producía grandes manchas negras que dominaban todas las salas. Se reemplazó el set `wall` por el recurso existente y no utilizado `assets/art/fm/concrete_wall_albedo.png`, con sus normales y roughness. El set antiguo se conserva como `plaster` para parches futuros.

Resultado visual: desaparecieron las manchas negras; las paredes leen como hormigón pintado con juntas de panel y vetas sutiles. Se ajustaron tintes y rugosidad para no oscurecer una textura ya oscura.

#### Cristales, agua y pantallas

- Agua y meltwater: alpha 0,42, roughness 0,055, sin emisión.
- Esquirlas: alpha 0,48, roughness 0,12, clearcoat 0,45.
- Espejos: albedo claro, metallic 0,92, roughness 0,075.
- Pantallas: texturas generadas de 512×256 con interfaces NEXUS, scanlines, barras y texto; variantes verde, ámbar, cian, extracción y ascensor.

---

## 4. Iluminación y ambientación (P2)

### 4.1. Balance de luz

- Se redujo la energía base de las luces de emergencia de 0,52 a 0,46 y la mezcla ámbar de 0,15 a 0,10.
- Se redujo la atenuación exterior de 0,78 a 0,68.
- Se aumentaron los rellenos fríos de seguridad, control, vestuarios, almacén, mantenimiento, oficina y aseo.
- Resultado: las salas dejaron de estar dominadas por el ámbar y se leen paredes, mobiliario y circulación sin perder la oscuridad intencional.

### 4.2. Luminarias de emergencia

Cada una de las 30 lentes emisivas recibió:

- Carcasa metálica oscura alrededor de la lente.
- Suspensión vertical de 2,2 m hasta el forjado.
- Sombra real solo en una de cada cinco luminarias (6 mapas en lugar de 29) para no castigar la GPU.

La placa naranja flotante que aparecía sobre el generador era una lente sin carcasa; ahora es una luminaria legible con soporte.

### 4.3. Pantallas y monitores

- Los monitores planos generados por `_add_flat_monitor()` usan texturas de interfaz y `SHADING_MODE_UNSHADED`, sin depender de la iluminación de la sala.
- El muro de seis televisiones de Seguridad se sustituyó por seis monitores planos con contenido legible, en lugar de carcasas blancas giradas.
- Los monitores del mostrador de recepción y de la oficina muestran la interfaz NEXUS.

### 4.4. Caldera y generador

- **Generador:** se sustituyó la caja negra con ventilador plano por `industrial_generator.glb`, exportado desde el recurso existente `portable_generator_2k.blend`, escalado y apoyado sobre una bancada. Tiene 26.419 triángulos, 4 mallas y texturas PBR.
- **Caldera:** se conservó la geometría original, se le dio un acabado metálico apagado, 42 remaches, un volante de válvula y una placa `CALDERA 02 / PRESIÓN CRÍTICA`.

### 4.5. Cajas de almacén

Se asignaron tres variantes de madera/cartón a 45 mallas de cajas y palés. Las bandas y cintas existentes se conservan. La repetición baja, aunque las siluetas siguen siendo sencillas.

---

## 5. Física y colisiones (P3)

- **Ascensor:** dos `AnimatableBody3D` con `sync_to_physics=true`, hijos del nivel y no de la hoja visual, para que el tween actualice el cuerpo físico.
- **Colisiones del nivel:** 511 colliders. Se eliminaron los cuerpos de decals de suciedad/humedad.
- **Rigid bodies:** los props físicos (`can`, `clipboard`, `carton`) y `FMCarryItem` reciben:
  - `linear_damp = 0,35–0,38`.
  - `angular_damp = 0,55–0,60`.
  - `PhysicsMaterial` con fricción 0,82–0,86, rebote 0,04–0,06 y `rough=true`.
- No se convirtieron objetos decorativos en cuerpos físicos ni se modificó el sistema de puertas.

---

## 6. Rendimiento y optimización

### 6.1. Medición actual

Test `tests/fm_level1_perf.tscn`, GTX 1650 Ti 4 GB, Forward+, VSync desactivado, Vigilante desactivado:

| Condición | FPS | Draws | Primitivas | Objetos |
|---|---:|---:|---:|---:|
| 1280×720 | 59–78 | 817 | 704.584 | ~10.000 |
| Ventana 1920×1080 | 28–35 | 817 | 704.584 | ~9.925 |

**Nota:** el proyecto mantiene un viewport lógico de 1280×720 con stretch; la medición de 1920×1080 corresponde a una ventana mayor y no debe presentarse como render nativo 1080p. Aun así, la cifra es una limitación real para equipos de gama baja.

Baseline de la auditoría (fase 3A.3): 99–101 FPS, 1.281 draws, 906.482 primitivas, 9.603 objetos a 1280×720.

### 6.2. Optimizaciones aplicadas

- **Compresión de texturas:** 147 albedos comprimidos a S3TC con mipmaps; 0 texturas ≥64 px sin mipmaps.
- **Culling de props pequeños:** papeles, latas, botellas, herramientas pequeñas, guantes y similares tienen `visibility_range_end = 18 m`.
- **Sombras de emergencia:** de 29 luces con sombra a 6.
- **Triplanar selectivo:** solo arquitectura; acero, pintura, madera y racks usan UV.
- **Sombras de dressing:** se probaron y se revirtieron porque duplicaban las primitivas (1,65 M) y bajaban a ~46 FPS. La oclusión de contacto queda pendiente.

### 6.3. Diagnóstico honesto

Las optimizaciones redujeron draws y primitivas respecto al baseline, pero **no recuperaron los FPS**. La escena incorpora más contenido (generador, monitores, pantallas, carcasas, caldera) y el coste de iluminación/triplanar sigue siendo alto. La VRAM medida por `nvidia-smi` se mantiene alrededor de 3,7 GB / 4 GB. No se implementaron LOD ni occlusion culling. El rendimiento debe tratarse como pendiente P3/P4, no como objetivo cumplido.

---

## 7. Pruebas ejecutadas

### 7.1. Smoke

```text
FM_LEVEL1_TEST: PASS
LEVEL1_COLLIDERS 511
TEST_LIGHTS true general=0 art=24 emergency=30 flashlight=3
TEST_EXTRACTION true state=1 delivered=1
ART_SECURITY_WALL monitors=6
ART_CRATES varied=45
ART_BOILER detailed
ART_TEXTURES compressed=147
```

### 7.2. Recorrido

```text
WALK_RESULT reached=33/33 final=(-17.23673, -5.649189, -9.919288)
```

### 7.3. Puertas

```text
DOOR_TEST_FAILS 0
DOOR_TEST: PASS
```

Se verificaron los seis tipos, colisiones, teclado, alerta, energía, cooperación y serialización/late join simulado. No se probaron dos clientes reales.

### 7.4. P0 específico

```text
P0_ELEV_SYNC true -> false
P0_CARRY_INSIDE picked=true inside_area=true count=1
P0_CARRY_OUTSIDE inside_area=false count=0
P0_RESULT PASS
```

### 7.5. Sonda de materiales

```text
UNIQUE_MATERIALS 371
TRIPLANAR 20
NO_MIP 0
COMPRESSED 142
FLOOR_MAT NEXUS_V05_MAT_Floor_Worn tri=true cc=false mip=true comp=true
PROP_MAT SchoolChair_01.002 tri=false ...
PROP_MAT metal_office_desk.002 tri=false ...
FLUID_MAT NEXUS_Water alpha=0.42 transp=1 rough=0.055
FLUID_MAT NEXUS_V05_MAT_Shard alpha=0.48 transp=1 rough=0.12
```

### 7.6. Capturas

34 capturas nuevas en `/tmp/opencode/final_*.png` con linterna y sin linterna. Se copiaron las principales a `docs/fm_level1_correction_*.png`. La comparativa está en `docs/fm_level1_correction_before_after.png`.

---

## 8. Comparativas antes/después

- `docs/fm_level1_art3a2_reception.png` → `docs/fm_level1_correction_rec_wide.png`
- `docs/fm_level1_art3a2_corridor_mid.png` → `docs/fm_level1_correction_corridor.png`
- `docs/fm_level1_correction_maint_gen.png` (generador nuevo)
- `docs/fm_level1_correction_maint_boiler.png` (caldera detallada)
- `docs/fm_level1_correction_store.png` (cajas variadas)
- `docs/fm_level1_correction_office.png` (pantalla y materiales)
- `docs/fm_level1_correction_security.png` (muro de monitores)
- `docs/fm_level1_correction_before_after.png` (hoja comparativa)

Mejoras visibles confirmadas:

- Paredes sin las grandes manchas negras.
- Suelo sin clearcoat global y con respuesta más seca.
- Tubería roja coherente.
- Cristal único en el mostrador.
- Pantallas con contenido en lugar de planos cian.
- Generador apoyado y legible, no una caja flotante.
- Caldera con remaches y rótulo.
- Cajas de almacén con variación.
- Luminarias de emergencia con carcasa y suspensión.

---

## 9. Archivos modificados

### 9.1. Scripts

- `scripts/fm/level1.gd`
  - CR-01, CR-02.
  - Filtro de decals AL-18.
  - Materiales de cristal del mostrador, monitores planos con textura, luminarias de emergencia con carcasa/suspensión, unificación de charcos, damping de rigid bodies.
- `scripts/fm/fm_level1_art_pass.gd`
  - CR-03, triplanar, mipmaps, compresión de texturas, overrides de materiales, pared, agua, esquirlas, espejos, pantallas, tubería roja, cajas, generador, caldera, muro de Seguridad, luces y culling.
- `scripts/fm/fm_level1_door.gd`
  - AL-06: normal/roughness de `DOOR_Rust`.
- `scripts/fm/fm_carry_item.gd`
  - Damping y material físico del botín transportable.

### 9.2. Recursos nuevos

- `assets/models/fm/props/industrial_generator.glb` (~10 MB, 26.419 triángulos, texturas 1K).
- `assets/art/fm/generated/gen_green_metal_rust_normal_src.png`
- `assets/art/fm/generated/gen_green_metal_rust_rough_src.png`
- `assets/art/fm/generated/gen_rusty_metal_sheet_normal_src.png`
- `assets/art/fm/generated/gen_rusty_metal_sheet_rough_src.png`
- `assets/art/fm/generated/screen_green.png`
- `assets/art/fm/generated/screen_amber.png`
- `assets/art/fm/generated/screen_cyan.png`
- `assets/art/fm/generated/screen_extract.png`
- `assets/art/fm/generated/screen_elev.png`

### 9.3. Documentación y capturas

- `docs/FM_LEVEL1_CORRECTION_REPORT.md` (este informe).
- `docs/fm_level1_correction_*.png`.
- `docs/fm_level1_correction_before_after.png`.
- Actualización de `docs/WORKLOG.md` y `docs/CURRENT_STATE.md` con el estado de la fase.

No se hicieron commits. Los cambios de fases anteriores que ya estaban sin commit siguen sin commit.

---

## 10. Recursos reutilizados

- `assets/art/fm/concrete_wall_albedo.png`, `concrete_wall_normal.png`, `concrete_wall_roughness.png` y `concrete_wall.tres` (existentes, sin uso previo).
- `assets/texturas/Metal y oxidacion/green_metal_rust_2k.blend/...` y `rusty_metal_sheet_2k.blend/...` (normales y roughness originales).
- `assets/art/fm/floor_wet.tres` como único sistema de charcos.
- `assets/Modelos 3D/Infraestructura industrial y mantenimiento/portable_generator_2k.blend` para el generador.
- `assets/models/fm/level1_nexus.glb`, `level1_doors.glb`, `art3a1/level1_art3a1_kit.glb` y `art3a2/level1_dressing.glb` como base, sin reemplazarlos.

---

## 11. Defectos pendientes

### P1/P2 pendientes

- **AL-09 — Sombras de contacto del dressing:** se probaron sombras reales, pero duplicaban primitivas y bajaban a ~46 FPS. Se revirtieron. Falta una solución de bajo coste (decals de contacto o sombras solo en props hero).
- **AL-11 — Generador/caldera:** el generador se sustituyó y la caldera se detalló, pero la caldera sigue siendo un cilindro con bandas; no es un modelo industrial completo.
- **AL-13 — Suelo del conector:** no se verificó visualmente en esta fase; el material es `Floor_Worn` triplanar.
- **AL-15 — Identidad de puertas:** no se trabajó; el sistema de puertas queda fuera de alcance salvo `DOOR_Rust`.
- **AL-17 — SALIDA duplicada:** en las capturas actuales se ve un solo rótulo; no se reprodujo el duplicado. No se modificó.
- **ME-01 — Directorio de recepción:** no se corrigió.
- **ME-02 — Oficina:** el monitor ya tiene contenido; los estantes siguen siendo tablones simples.
- **ME-03 — Aseo:** el espejo ya no es negro, pero el lavabo/zona sigue siendo básico.
- **ME-04 — Seguridad/control:** el muro de monitores está corregido; quedan props de escritorio simples.
- **ME-05 — Vapor:** el sistema de partículas no se rediseñó; sigue siendo un billboard suave.
- **ME-06 — Decals:** se filtraron colisiones; no se revisó la densidad/oscurecimiento de todos los decals.
- **ME-07 — Reflejos:** hay probes en recepción/corredor; no en aseo/vestuarios.
- **ME-08 — Vestuarios:** taquillas repetitivas, sin numeración/etiquetas.
- **ME-09 — Ascensor:** la sincronización visual/física está corregida; no se revisó el interior completo de la cabina.
- **BA-02 — Bloom:** no se ajustó.
- **BA-03 — Luminarias:** las de emergencia están corregidas; otras lámparas siguen pendientes.

### P3 pendientes

- **AL-19 — `StaticBody3D` en puertas:** no se tocó (fuera de alcance).
- **AL-20 — LOD/occlusion:** no implementados.
- **ME-15 — Topología:** no se limpiaron los 25.010 boundary edges, 8.124 non-manifold ni duplicados del GLB principal.
- **ME-16 — Físicas:** damping/material aplicados a los rigid bodies existentes; no se revisaron todas las masas/fricciones del nivel.
- **BA-01 — Etiquetas de texturas:** no se normalizaron.
- **BA-04 — RIDs al salir:** persisten los warnings de recursos retenidos en headless.
- **BA-05 — Documentación:** este informe y las actualizaciones de estado cubren la fase; falta integración en el documento maestro de misión.

### Rendimiento

- 1280×720: 59–78 FPS según ejecución (mediciones inestables).
- Ventana 1920×1080: 28–35 FPS (viewport lógico 1280×720 con stretch).
- VRAM ~3,7 GB / 4 GB.
- Sin LOD/occlusion/perfiles de calidad.
- El baseline de 99–101 FPS no se recuperó.

---

## 12. Problemas no verificables

- **Build exportado:** no se generó un build; `Image.load("res://...")` para texturas generadas y la carga runtime de GLB deben validarse en un export.
- **Multijugador:** no se probaron dos clientes reales; la extracción con botín transportado se verificó en local.
- **Criaturas:** no se evaluó la IA ni la navegación con los cambios de colisión.
- **Otras zonas:** no se recorrieron interiormente todas las salas después de los cambios; walk cubre 33 puntos de circulación, no cada rincón.
- **1080p nativo:** la medición con `--resolution` no equivale a un render nativo por el stretch del proyecto.
- **VRAM real en build:** la lectura de `nvidia-smi` incluye el contexto de Godot; no se hizo perfilado por recurso.

---

## 13. Riesgos y dependencias

- **Generador de ~10 MB:** es un recurso detallado con texturas 1K, pero no un modelo industrial a medida; si se requiere un generador fijo de mayor tamaño, habría que modelarlo específicamente.
- **Compresión S3TC:** reduce VRAM y mejora el rendimiento, pero puede introducir artefactos en degradados y normales. Se aplicó solo a albedos opacos; las normales no se comprimieron.
- **Triplanar:** resuelve las UV sin reexportar el GLB, pero tiene coste de shader. Se limitó a arquitectura.
- **Runtime `Image.load`:** las texturas generadas no tienen `.import`; en un export podrían no incluirse. Debe validarse antes de construir.
- **Sin LOD/occlusion:** el nivel depende de culling de distancia para props pequeños; las salas grandes siguen renderizando geometría fuera de vista.
- **Sin commits:** todos los cambios están en el árbol de trabajo; una limpieza o cambio accidental podría perderlos.
- **Dependencias de fase:** los cambios se apoyan en los GLB y scripts de las fases 3A.1–3A.3, que siguen sin commit. No se deben reemplazar esos recursos sin conservar la jerarquía y los nombres.

---

## 14. Próximos pasos recomendados

1. **Validar export:** generar un build de prueba y comprobar texturas generadas, GLB runtime y pantallas.
2. **Perfiles de calidad:** Low/Medium/High/Ultra con render scale, sombras, SSAO/SSR, niebla volumétrica y distancia de props. Medir cada perfil en la GTX 1650 Ti.
3. **LOD/occlusion:** empezar por el generador, caldera, estanterías y props de almacén; añadir `OccluderInstance3D` en muros y puertas.
4. **Sombras de contacto de bajo coste:** decals de contacto bajo cajas, taquillas y generador.
5. **Topología del GLB:** limpiar boundary/non-manifold/duplicados en Blender antes de futuras exportaciones, sin tocar las UV ya resueltas por triplanar.
6. **Revisión de las doce zonas:** recorrer aseo, conector, ascensor y almacén interior con linterna; corregir los defectos visuales restantes.
7. **Actualizar el documento maestro:** enlazar este informe desde `docs/CURRENT_STATE.md` y `docs/WORKLOG.md`.

---

## 15. Conclusión

El Nivel 1 queda en un estado claramente superior al auditado: los tres defectos críticos están resueltos y verificados, los materiales y la iluminación tienen una lectura mucho más coherente, el generador y la caldera ya no son primitivas flotantes, y las pantallas aportan información visual en lugar de planos cian.

No es todavía un nivel “terminado” ni “AA/AAA”. Quedan pendientes de rendimiento, LOD/occlusion, topología, sombras de contacto, varias salas y la validación en build/export. El informe separa explícitamente lo corregido y probado de lo pendiente para no repetir el error de declarar aprobado lo que solo compila.

---

## 16. Implementación de correcciones P0–P3 (2026-11-04, OpenCode)

Esta sección registra la fase de implementación posterior a la auditoría `docs/FM_LEVEL1_FULL_AUDIT.md`. No se reconstruyó ningún sistema; se corrigieron los existentes y se midió el resultado en runtime.

### 16.1 P0 obligatorio — Puertas del pasillo

- **Causa confirmada:** `scripts/fm/fm_player.gd::_has_line_of_sight(target)` lanzaba el rayo desde la cámara hasta el punto de interacción de la puerta; ese punto está en el plano de la hoja y el rayo impactaba primero el `DoorCollider_*` de la propia puerta, devolviendo `false`. Por eso `_try_interactable()` y `_nearest_interactable()` descartaban las seis puertas.
- **Corrección:** `_has_line_of_sight(target, ignore_node = null)` excluye el RID del jugador y los `CollisionObject3D` del candidato mediante `_collect_collision_rids()`. `_try_interactable()`, `_nearest_interactable()` y `_try_pickup()` pasan el nodo candidato. No se creó un sistema paralelo.
- **Verificación runtime con interacción real:** las seis puertas responden; recepción abre/cierra con reapertura automática por proximidad; seguridad abre con `0451`; control abre en dos pasos; vestuarios abre/cierra; almacén (pesada) completa el hold de **4,00017 s / 582 frames**, abre y deja pasar una esfera de 0,28 m (`blocked=false`); al cerrar, la misma esfera queda bloqueada (`blocked=true`). Mantenimiento permanece abierta por diseño.
- **Pruebas:** `tests/fm_level1_doors.tscn` **PASS**, `DOOR_TEST_FAILS 0`, `net_state_count 6`; `tests/fm_level1_smoke.tscn` **PASS**, `TEST_DOORS_CLOSED 6/6`, `TEST_DOORS_OPEN 6/6`.
- **Limitación metodológica:** el test de puertas llama `door.interact()` directamente y no ejercita `can_interact`/línea de visión; por eso el fallo no se detectaba. La prueba runtime específica sí ejercita la interacción del jugador.

### 16.2 P0 — Iluminación

- **Entorno:** `ambient_light_energy=0.035` (antes 0.22), `ambient_light_sky_contribution=0.45` (0.72), `background_energy_multiplier=0.20` (0.36), `tonemap_exposure=1.05` (1.34), glow 0.18/0.03/1.45.
- **Luces eliminadas:** los 8 `ART_Corridor*` y los 7 `ART_RoomFill_*` ya no se crean; `_dim_rooms_outside_reception()` se ejecuta después de `_add_cinematic_lights()` y solo limpia residuos. Quedan las 9 luces funcionales de recepción.
- **Emergencias:** reducidas de 30 a 14 (3 recepción, 2 corredor, 5 umbrales de sala, conector, oficina, aseo, ascensor). Energía runtime **0,15–0,374**, rangos 2,8–5,5 m, solo `EmergencyLight_0` con sombra. Se corrigió el bug que aplicaba la reducción de emisión de lentes al material equivocado; ahora usa `get_active_material(0)` y multiplica por 0.20.
- **Capturas finales:** 24 PNG (12 zonas × off/on) en `docs/fm_level1_p2_lights/`, generadas a 1280×720 después de todos los cambios P1.
- **Luminancia media sRGB (off/on):** recepción 12.16/17.64; corredor 0.61/7.68; seguridad 0.82/15.46; control 1.51/12.38; vestuarios 0.09/10.27; almacén 0.29/9.53; mantenimiento 0.07/13.47; oficina 2.47/19.45; aseo 0.11/23.08; conector 1.14/9.85; ascensor 13.29/29.26; extracción 23.01/29.76.
- **Interpretación:** fuera de recepción, todas las salas cumplen oscuridad (≤2.47) salvo el ascensor, que es el vestíbulo de salida a recepción y contiene la señalización SALIDA, el letrero EXTRACCIÓN y el aro de extracción; se documenta como excepción de navegación, no como relleno ambiental. Recepción y extracción conservan la iluminación funcional permitida.
- **Verificación visual:** el corredor off solo muestra el cartel de seguridad y un punto de emergencia; con linterna se leen paredes, tubería, puertas y suelo. Almacén y mantenimiento quedan negros sin linterna. Ya no aparece el charco de luz fría sin luminaria.

### 16.3 P1 — Defectos visuales y funcionales

- **Viewmodel de linterna:** se eliminó la media luna blanca. Emisión de lente 0.85, lente extra 0.45, `FlashlightViewFill` 0.10/0.40, cuerpo más oscuro (metallic 0.45, roughness 0.55) y posición `(0.30,-0.32,-0.56)`. El modelo queda discreto en oscuridad; se priorizó eliminar el destello.
- **Espejos:** `_set_mirror` pasa a metallic 0.62, roughness 0.22; ascensor 0.45/0.38. El blob especular del aseo se redujo a un reflejo suave y el espejo del ascensor dejó de quemar.
- **SALIDA duplicada (AL-17):** se ocultan `NEXUS_V05_C_REC_ELEV_SIGN_TEXT_TEXT` y su placa del GLB; queda un solo cartel dinámico. La emergencia del ascensor baja a 0.22/2.4.
- **Pantallas de control:** `DRESS_Screen` (caja con textura en todas las caras) se oculta y se sustituye por dos monitores `ART_ControlScreen_A/B` orientados a +X, con texturas ámbar/cian, cuerpo metálico y pantalla 0.98×0.56. Captura final: UI legible.
- **Props PBR:** `_fix_prop_materials()` ajusta sillas (0.18/0.62), mesas (0.42/0.48), señal de piso (0.05/0.58) y relojes (0.15/0.55). Antes tenían metallic/roughness 1.0.
- **Acceso a oficina:** el monitor de suelo `NEXUS_L1_DIS_OFFICE_MONITOR_FLOOR` y su collider `COL_108_...` estaban centrados en el hueco de 0.9 m y bloqueaban el paso. `_fix_office_access()` oculta el prop y libera el collider. Sonda: oficina y aseo transitables; conector transitable desde almacén por el roller; el acceso desde mantenimiento sigue bloqueado por una hoja estática (existe ruta alternativa).
- **Walk oficial:** ampliado a **44 waypoints**, con oficina (pasos 33–34) y aseo (35–38) por sus huecos reales. Resultado **PASS 44/44**, final `(-17.23429,-5.649179,-9.91729)`, sin `WALK_HIT`.
- **Sombras de contacto:** se activan solo en muebles grandes del dressing (`y>0.70`, área xz >0.35). El generador y otros props dejan de flotar. Coste medido y aceptado (ver 16.4).
- **Deuda visual pendiente:** cajas de almacén aún planas, caldera aún cilíndrica con remaches poco visibles, estanterías de oficina vacías, placa blanca colgante al fondo del corredor. No se añadió geometría nueva en esta fase.

### 16.4 P2 — Rendimiento y cobertura

- Se corrigió el error de `_compress_scene_secondary_textures()`: `detect_alpha()` se llamaba sobre imágenes ya comprimidas y generaba cientos de errores. Ahora comprueba `not img.is_compressed()`. Se mantiene `compressed=147` de albedos y la compresión secundaria de normales/roughness/AO/emisión.
- **1920×1080, GTX 1650 Ti 4 GB, VSync off, Vigilante off:** **56 FPS**, 770 draws, 1.630.128 primitivas, 9.901 objetos; `nvidia-smi` **3232 MiB**, GPU 11%.
- **1280×720:** **107 FPS**, 1124 draws, 1.798.947 primitivas, 9.896 objetos; `nvidia-smi` **3214 MiB**, GPU 10%.
- **Cumple** 1080p ≥45 FPS y 720p ≥55 FPS; VRAM ~3,2 GB, en el límite del objetivo. **No cumple** los objetivos de <500 draws y <5.000 objetos. No se añadieron LOD ni occlusion; no hay perfiles Low/Medium/High/Ultra ni render scale.
- Las mediciones paralelas de dos instancias (9/28 FPS) no son válidas y se descartan.

### 16.5 P3 — Build y exportación

- `Image.load(ProjectSettings.globalize_path(...))` se sustituyó por `Image.load("res://...")` en el pase artístico; las pantallas ya usaban `res://`. Esto elimina una dependencia que fallaría en un PCK.
- **No existe `export_presets.cfg`.** El directorio `~/.local/share/godot/export_templates` está vacío: no hay plantilla Linux/Windows instalada. No se pudo generar un build real.
- Los GLB, HDR y PNG generados cargados en runtime no tienen `.import`; un preset debe incluirlos como archivos no-recurso o migrarse a recursos importados. Sin esa validación, el nivel **no está listo para producción**.

### 16.6 Pruebas ejecutadas

- Smoke: PASS; `LEVEL1_COLLIDERS 511`; `TEST_PLAYER floor=true`; `TEST_LOOT 5`; `TEST_ROOMS 10/10` (los rayos de oficina/aseo siguen impactando techos; defecto metodológico conocido, suelos validados aparte); puertas 6/6 cerradas y abiertas; resto PASS. Solo fugas conocidas al salir.
- Doors: PASS; 6 tipos, colliders, teclado 0451, mantenimiento, cooperación, alerta, energía, serialización/late join simulado.
- Walk: PASS 44/44, con oficina y aseo.
- Funcional: 3 escondites (`HideCabinet`, `HideLocker`, `HideShelf`) con `hide`/`exit` correctos; linterna drena 5→0 y se apaga, recarga 30 y vuelve a encender.
- Luces: 14 emergencias, 9 luces de recepción, 0 `ART_Corridor*`/`ART_RoomFill_*`; entorno 0.035/0.45/1.05.
- Propiedades: sillas/mesas/relojes/señal con valores PBR nuevos.
- Capturas finales: `docs/fm_level1_p2_lights/` (24).

### 16.7 Archivos afectados

- `scripts/fm/fm_player.gd` — línea de visión/interacción, viewmodel y luces de linterna.
- `scripts/fm/fm_level1_art_pass.gd` — entorno, luces, materiales, sombras, pantallas de control, acceso a oficina, compresión y cargas `res://`.
- `scripts/fm/level1.gd` — emergencias reducidas, SALIDA única y ajustes asociados.
- `tests/fm_level1_walk.gd` — recorrido de 44 waypoints.
- Documentación: este informe, `docs/FM_LEVEL1_FULL_AUDIT.md`, `docs/CURRENT_STATE.md`, `docs/WORKLOG.md`.

No se hicieron commits ni se limpió el árbol. `level1.gd`, `fm_level1_art_pass.gd` y el walk son archivos no rastreados (`??`) del trabajo previo; `fm_player.gd` es tracked y contiene cambios previos del proyecto además de esta fase.

### 16.8 Pendiente real

- LOD/occlusion, perfiles de calidad, reducción de draws/objetos.
- Build Linux/Windows con plantillas instaladas y prueba en carpeta limpia.
- Prueba con dos clientes reales, reconexión y autoridad de red.
- Vigilante completo (visión, congelación, persecución, captura, dos jugadores).
- Recorrido completo del conector desde la entrada del almacén (hoy verificado por sonda desde el hueco libre; el walk directo se atasca en escombros).
- Topología del GLB, audio/comunicación, accesibilidad y licencias de assets.
- Deuda visual de cajas, caldera, estanterías y placa del corredor.

**Conclusión de la fase:** P0 (puertas e iluminación) cerrado y verificado; P1 corregido en sus defectos principales; P2 parcial con rendimiento 1080p aceptable pero sin LOD/occlusion/perfiles; P3 bloqueado por falta de plantillas de exportación. El nivel no se declara terminado ni listo para producción.

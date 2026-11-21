# FRECUENCIA MUERTA — Fase 3A.1: kit de Blender para recepción y corredor

**Fecha:** 2026-11-03 (COT)  
**Ámbito:** recepción NEXUS y corredor principal.  
**Modo:** kit de geometría/materiales creado en Blender y cargado en Godot; no se modificó el GLB jugable original.

## 1. Objetivo

Continuar la Fase 3A con una fuente real de Blender, reduciendo la dependencia de geometría procedural y overrides de runtime. Se priorizaron mostrador/cristal de recepción, conducto del corredor, paneles de pared y materiales industriales.

## 2. Kit de Blender

- Fuente reproducible: `blender_concept/build_art3a1_kit.py`.
- Blend: `blender_concept/ART3A1_kit.blend` (274 objetos de origen).
- GLB: `assets/models/fm/art3a1/level1_art3a1_kit.glb` (~3,9 MB, 8 mallas fusionadas por material).
- Materiales: `ART3A1_Steel`, `GreenPaint`, `Wood`, `DarkMetal`, `Rubber`, `Glass`, `CyanStrip`, `AmberStrip`, `Hazard`, `Label`, `DuctPaint`.
- Texturas: JPG/PNG 2K locales y normales/roughness generadas en `assets/art/fm/generated/`. No se sobrescribieron originales.

### Contenido

- **Mostrador de recepción:** fascia verde con paneles hundidos, remates metálicos, zócalo, tapa de madera, tira LED bajo mostrador y mampara de cristal con marco de acero. Colocado en las coordenadas del mostrador existente.
- **Dos tramos de conducto de 10 m:** cuerpo verde oscuro, bridas, refuerzos, rejillas, tornillos y soportes al techo.
- **Módulos de pared:** paneles verdes con costillas/travesaños de acero, rejillas, caja eléctrica, conducto y tornillería; colocados en x ±8,7 sobre ambas paredes.
- **Dinteles/bulkheads** metálicos de servicio para cubrir el paramento alto del acceso.

## 3. Integración en Godot

- `scripts/fm/fm_level1_art_pass.gd` carga el kit con `GLTFDocument` después de los overrides de material.
- Se añadió el override `NEXUS_V05_MAT_Sign_Battery` a verde oscuro con emisión baja; esto corrigió el gran panel claro de recepción.
- Se retiraron del runtime el mostrador/cristal procedural, el conducto procedural, las costillas/paneles de pared y los paneles de mantenimiento para no duplicar el kit.
- Se conservaron luces, HDRI, reflection probes, columnas, vigas, tuberías, bandeja, marcos de puertas, wet patches y slat band.
- Se ocultaron los cuatro `NEXUS_V05_OFFICE_PARAPET_*` para reducir paramentos claros.

## 4. Capturas

- `docs/fm_level1_phase3a1_before_after.png`: comparativa 3A → 3A.1 de recepción y corredor.
- `docs/fm_level1_phase3a1_reception.png`
- `docs/fm_level1_phase3a1_counter.png`
- `docs/fm_level1_phase3a1_logo.png`
- `docs/fm_level1_phase3a1_corridor.png`
- `docs/fm_level1_phase3a1_corridor_detail.png`
- `docs/fm_level1_phase3a1_corridor_back.png`

## 5. Pruebas

- `tests/fm_level1_smoke.tscn`: **PASS**  
  `ART3A1_KIT loaded`, `ART_PASS ready materials=32 details=10`, `TEST_LIGHTS general=0 art=17 emergency=30 flashlight=3`, `FM_LEVEL1_TEST: PASS`.
- `tests/fm_level1_walk.tscn`: **PASS**  
  `WALK_RESULT reached=33/33`.
- `tests/fm_level1_perf.tscn` a 1280×720 en desarrollo:

```text
LEVEL1_PERF fps=108.0 draws=814 primitives=406748 objects=8683
```

Comparación: Fase 3A **110 FPS / 796 draws / 221.484 primitivas / 8.655 objetos**. El kit añade ~185k primitivas y 18 draw calls; el FPS baja ligeramente. No es una medición de la GTX 1650 Ti.

## 6. Evaluación

**Mejoras claras:** mostrador con construcción creíble, cristal con marco, panel NEXUS oscuro, iluminación bajo mostrador, paneles de pared y conductos con fuente Blender, paleta fría mantenida.

**Volumen claro del corredor — causa identificada:**

El bloque claro de la zona alta provenía de dos fuentes:

1. Los cuatro `NEXUS_V05_OFFICE_PARAPET_0..3` del GLB original, con material `NEXUS_V05_MAT_Rec_Ceiling`. Se ocultan todos en `_load_kit()` mediante `find_children("*OFFICE_PARAPET*", "", true, false)`.
2. El conducto del kit, demasiado bajo y claro. Se elevó +0,23 m en Y y +0,20 m en Z de Blender, se redujo a 0,48×0,32 y se le asignó `ART3A1_DuctPaint` oscuro.

Se añadieron además bulkheads simétricos en z ±1,52 y revestimiento de servicio en z ±1,40 sobre el acceso. En la última captura el bloque ya no domina la esquina superior izquierda; queda pendiente la confirmación visual del usuario.

**Problemas que siguen:**

- Los módulos de pared del kit son demasiado grandes/planos/repetitivos en primer plano y dominan la composición.
- El conducto del kit no se lee todavía como un conducto industrial de alta calidad en todas las vistas; revisar rejillas y soportes tras el desplazamiento.
- No hay LOD real ni occlusion culling; el kit añade ~185k primitivas.
- No se probó en GTX 1650 Ti ni build final.
- El viewmodel de linterna sigue pendiente.
- No se extendió el pase a otras habitaciones.

**Conclusión:** la recepción mejora de forma evidente y el corredor ya no tiene el bloque claro dominante. El corredor **todavía no alcanza el estándar comercial** por la escala/composición de los módulos de pared y la lectura del conducto; esa es la segunda iteración pendiente antes de extender el estilo al resto del laboratorio.

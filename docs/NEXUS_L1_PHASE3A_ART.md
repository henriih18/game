# FRECUENCIA MUERTA — Fase 3A: recepción y corredor

**Fecha:** 2026-11-03 (COT)  
**Ámbito:** recepción NEXUS y corredor principal del Nivel 1.  
**Modo:** intervención artística en Godot. No se modificó el `.blend` original ni el GLB del nivel.

## 1. Objetivo

Elevar la recepción y el corredor hacia un realismo estilizado cinematográfico industrial, usando como referencia `docs/fm_lookdev_corridor.png` y las imágenes de `fotos-referencia/`. Se conservaron la distribución, las puertas, los cajones, las taquillas, las alarmas, los props físicos y los sistemas existentes.

## 2. Cambios realizados

### Nuevo módulo artístico

- `scripts/fm/fm_level1_art_pass.gd`: pase desacoplado de la lógica de juego.
- `scripts/fm/level1.gd`: precarga el módulo y lo aplica después de `_setup_postprocess()`, antes de `level_ready`.
- No se renombraron ni movieron nodos de gameplay. No se eliminó ningún prop.

### Entorno e iluminación

- HDRI local `assets/HDRI/Instalaciones industriales y abandonadas/abandoned_workshop_2k.hdr` como cielo/ambiente; fallback procedural si no carga.
- Ambiente elevado de 0.075 a 0.22; exposición 1.34; SSIL activado; SSR a 40 pasos.
- SSAO 1.25, glow 0.32, niebla volumétrica 0.012, niebla de profundidad 0.005.
- Dos `ReflectionProbe`: recepción y corredor completo.
- 17 luces artísticas (`ART_`): clave fría y acentos cálidos en recepción; focos fríos con haz volumétrico y rellenos en corredor.
- Se redujo la energía de las 30 luces de emergencia al 52 % para que sean acentos, no la iluminación base.
- Las luces nuevas con sombra se limitaron a la clave de recepción; el resto usa SSAO/SSIL y sombras de las luces existentes.

### Materiales PBR

- Se generaron normales y rugosidad en PNG a partir de los EXR locales de Poly Haven, en `assets/art/fm/generated/` (10 archivos, ~43 MB). No se sobrescribió ningún original.
- Se aplicaron overrides a 31 claves de material del GLB, incluyendo:
  - `NEXUS_Steel`, `NEXUS_Painted_Metal`, `NEXUS_Concrete`, `NEXUS_Concrete_Dark`.
  - `NEXUS_V05_MAT_Floor_Worn`, `NEXUS_V05_MAT_Rec_Floor`, `NEXUS_V05_MAT_Rec_Wall`, `NEXUS_V05_MAT_Rec_Wainscot`.
  - `NEXUS_Rack_Paint`, `NEXUS_Rubber`, `NEXUS_Glass`, `NEXUS_Wood`.
  - `NEXUS_V05_MAT_Counter_Front`, `Counter_Reveal`, `Counter_Top`, `Rec_Ceiling`, `Rec_Painted_Green`, `Rec_Wood`.
  - `NEXUS_V05_MAT_Baseboard`, `CableTray`, `Conduit`, `Galv`, `Galv_Dark`, `Rug_Dark`.
- Suelo: `concrete_floor_01` 2K con tinte gris-azul, roughness map y clearcoat; ya no es el marrón oxidado anterior.
- Paredes: `worn_plaster_wall` 2K; zócalo: `factory_wall` verde; metal: `rusty_metal_sheet`; pintura: `green_metal_rust`; madera: `wooden_crate_01`.
- Se añadió un material de suelo húmedo transparente y reflectante para tres charcos/zonas mojadas.

### Arquitectura y detalle

- Recepción:
  - Costillas verticales en el frente del mostrador, remates y zócalo.
  - Banda de listones de madera bajo el logo NEXUS.
  - Luminaria lineal sobre el mostrador y tira de luz bajo el mostrador.
  - Pequeña mampara de cristal, paneles de pared y costuras metálicas.
  - Bandeja de cables y conducto rectangular en el techo.
  - Downlights y canalización de pared.
- Corredor:
  - Bandeja portacables continua con travesaños y soportes.
  - Dos tuberías con bridas y abrazaderas; conducto rectangular con refuerzos.
  - Canalización de pared, paneles de mantenimiento y tornillería.
  - 14 columnas estructurales con placas, franjas de peligro y colliders estáticos; 5 vigas de techo.
  - Marcos metálicos de puertas.
  - Luminarias industriales con tubos emisivos y tiras frías en los bordes superiores.
  - Marcas de peligro junto a los accesos.
- Todos los conjuntos nuevos se fusionaron por material con `SurfaceTool`, reduciendo el número de draw calls frente a crearlos como objetos sueltos.

### Pruebas y ajustes

- `tests/fm_level1_smoke.gd`: ahora distingue luces `ART_` de luces generales; sigue exigiendo `general=0`.
- `tests/fm_level1_art_shots.gd/.tscn`: capturas de recepción, mostrador, logo, corredor, detalle y vista inversa.
- Se conservaron los sistemas existentes; no se modificó la IA, el multijugador ni las interacciones.

## 3. Capturas

- `docs/fm_level1_phase3a_before_after.png`: comparativa antes/después de recepción y corredor.
- `docs/fm_level1_phase3a_reception.png`: recepción amplia.
- `docs/fm_level1_phase3a_counter.png`: mostrador y pared corporativa.
- `docs/fm_level1_phase3a_logo.png`: logo, listones y luminaria.
- `docs/fm_level1_phase3a_corridor.png`: corredor amplio.
- `docs/fm_level1_phase3a_corridor_detail.png`: techo, tuberías, columnas y paneles.

## 4. Resultados medidos

### Luminancia media (referencia agregada ≈0.128)

| Vista | Antes | Después |
|---|---:|---:|
| Recepción | 0.056 | 0.124 |
| Corredor | 0.048 | 0.139 |
| Detalle de corredor | — | 0.125 |

La dominancia naranja se corrigió: la recepción pasó de (0.102, 0.046, 0.024) a (0.110, 0.125, 0.155); el corredor, de (0.087, 0.039, 0.014) a (0.139, 0.137, 0.159).

### Rendimiento a 1280×720 en la máquina de desarrollo

Antes:

```text
LEVEL1_PERF fps=186.0 draws=1037 primitives=187620 objects=8768
```

Después:

```text
LEVEL1_PERF fps=110.0 draws=796 primitives=221484 objects=8655
```

Los draw calls bajaron un 23 %, pero los primitivos subieron un 18 % y el FPS cayó por el coste de iluminación, SSIL/SSR, reflexiones y detalles nuevos. **No es una medición de la GTX 1650 Ti.**

### Pruebas funcionales

- `tests/fm_level1_smoke.tscn`: **PASS** (`FM_LEVEL1_TEST: PASS`, `TEST_LIGHTS general=0 art=17 emergency=30 flashlight=3`).
- `tests/fm_level1_walk.tscn`: **PASS** (`WALK_RESULT reached=33/33`).
- `tests/fm_level1_perf.tscn`: ejecutado con el resultado anterior.
- No se modificaron las pruebas de recepción ni los sistemas compartidos.

## 5. Limitaciones honestas

- La recepción y el corredor **mejoran de forma clara en color, luz, materiales, profundidad y arquitectura**, pero **todavía no alcanzan un acabado comercial**. La geometría base sigue siendo sencilla en varias zonas.
- El gran panel de cristal del mostrador sigue siendo visualmente dominante y algunos elementos existentes del GLB (por ejemplo, el conducto claro del techo) no se han reautorado.
- Las paredes del corredor siguen teniendo grandes superficies planas entre columnas; falta más densidad de paneles, cables, tuberías y señalización.
- No se ha implementado LOD real ni occlusion culling; solo distance culling para props pequeños. El GLB no trae cadenas LOD.
- La intervención no toca el resto de habitaciones, el menú, la red, el guardado ni la IA compartida.
- El viewmodel de linterna sigue pendiente; no se ha convertido en una mano/brazo con animación.
- Las texturas generadas proceden de la biblioteca local; no hay archivos de licencia dentro de `assets/`, así que la licencia debe confirmarse antes de distribución.
- No se probó en la GTX 1650 Ti ni se generó build final.
- No se modificó el `.blend` ni el GLB; los cambios son de runtime en Godot. Para llevar este look al GLB hay que trasladar materiales/geometría al archivo fuente en una fase posterior.

## 6. Evaluación

**¿Se alcanzó el estándar artístico esperado?** No todavía. Se consiguió una mejora evidente y una base de dirección artística coherente:

- Color frío con acentos cálidos.
- Iluminación más cercana a las referencias.
- Suelo gris húmedo en lugar de marrón.
- Materiales PBR con texturas 2K en las superficies principales.
- Arquitectura con servicios, columnas, paneles y luminarias.
- Reflejos y profundidad.

Pero el resultado sigue siendo un **vertical slice artístico**, no un escenario comercial terminado. Antes de extender el pase al resto del nivel hay que decidir si se acepta esta base o si se invierte en una segunda iteración de geometría/asset authoring.

## 7. Siguiente paso

1. Revisar las capturas y decidir qué elementos se aceptan como estándar.
2. Reautorar el mostrador/cristal y el conducto claro del corredor.
3. Añadir densidad de paredes y techo en el corredor.
4. Medir en la GTX 1650 Ti y decidir LOD/occlusion.
5. Solo después, extender el lenguaje visual al resto de habitaciones.

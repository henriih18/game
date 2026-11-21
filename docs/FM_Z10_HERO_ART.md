# FRECUENCIA MUERTA — Z10 pase hero: materiales procedurales → texturas 2K (paso 1 + R2 + R3 + R4 + R5 + R6)

Fecha: 2026-11-10. Estado: **R6 beauty aprobado en Blender; R7 art scene Godot creada y medida; sin commit**.

> **Actualización R2 (2026-11-10):** el prototipo fue corregido y re-renderizado. El parche blanco no era el conducto: era la rejilla `P0B4_GRILLE_03` (y `04`), con un material de aluminio procedural plano. El galvanizado se rehizo a **2 m** con spangle Voronoi; el rojo recibió desgaste sutil; el wide se reencuadró sin la columna y con la etiqueta legible. **Veredicto: aprobado para el prototipo, con reservas** (el desgaste de borde del rojo es de textura, no por curvatura de objeto). Detalle en la sección 11. Las secciones 1–9 se conservan como histórico del paso 1.

> **Actualización R3 (2026-11-10):** R2 no fue aprobado como hero final. Se rehízo el galvanizado con celdas de **1–3 cm**, bajo contraste, acero neutro, roughness 0,35–0,50 y normal 0,25; se equilibró el wide con cámara 3/4 y se diagnosticó el banding del suelo como artefacto del **denoiser OIDN**, no del material/UV. El wide final se renderizó sin denoise a 256 spp. Detalle en la sección 12. **Veredicto: aprobado como prototipo R3; no aprobado aún como pase hero completo de Z10** (faltan 30 objetos, edge wear real y validación Godot).

> **Actualización R4 (2026-11-10):** se extendieron los materiales image-based a los **37 objetos de acero** del set Z10 (0 slots de acero procedurales), se bakeó el set dark 2K, se regeneró `z10_sector.glb` desde una copia triangulada con **TANGENT/TEXCOORD e imágenes embebidas**, y Godot validó **507 mallas / 402 únicas / 9 luces**. Quedan 43 slots de acentos no-acero procedurales y la VRAM de texturas sin comprimir. Detalle en la sección 13.

> **Actualización R5 (2026-11-10):** se cubrieron **43/43 slots de acentos** (0 `M_SH_*` restantes), se arreglaron las 18 imágenes legacy (PBR de props visibles), se comprimieron las texturas importadas a **216,2 MB de VRAM** (desde 446,9 MB), se añadió desgaste de curvatura en los tubos rojos (COLOR_0) y se regeneró el GLB final (**137.929.288 B**, 507/402/9) con Godot OK. Limitación: Godot importa el material de desgaste con `vertex_color_use_as_albedo=false`. Detalle en la sección 14.

> **Actualización R6 (2026-11-10):** se corrigió la pared que leía como madera con un set 2K de plaster y `UV_Z10_WALL`; se rehicieron suelo/techo 2K con suciedad, juntas y manchas; se añadió niebla volumétrica, emergencia roja y lookdev cinematográfico; **Godot importa el desgaste con `vertex_color_use_as_albedo=true`** mediante import script (preview `fm_z10_godot_wear_r6.png`); beauty 3/4 1280×720/256 spp aprobado. GLB **144.619.328 B**, Godot **507/402/9**, VRAM **248,2 MB textura / 313,8 MB vídeo**, FPS estático **581,7** (1280×720, VSync off). Detalle en la sección 15.

> **Actualización R7 (2026-11-10):** se creó la art scene Godot `scenes/fm/fm_z10_art_r7.tscn` con environment AgX/niebla/SSAO/SSR, luces del GLB reescaladas, bounce/wash de escena y decal de suelo scene-only. Captura `docs/fm_z10_godot_parity_r7.png`; media/mediana de luminancia casi idénticas al beauty R6. **197,2 FPS estáticos** (1280×720, VSync off, Forward+) y **362,9 MB textura / 448,6 MB vídeo**. Paridad tonal/atmosférica aprobada; no pixel-perfect (faltan GI/área/volumen de Cycles). Detalle en `docs/FM_Z10_GODOT_PARITY.md`.

> **Actualización R8 (2026-11-10):** dirección oscura del usuario para Z10. Nueva `scenes/fm/fm_z10_art_r8.tscn` sin key/fill/wash/bounce ni luces fijas añadidas; solo 3 luces rojas de emergencia del GLB, 6 ocultas y emisivos de luminarias apagados. Capturas `docs/fm_z10_godot_dark_r8.png` y `..._flashlight_r8.png` (linterna diagnóstica temporal, no guardada). **320,7 FPS estáticos**, **361,4 MB textura / 441,5 MB vídeo**. Detalle en `docs/FM_Z10_GODOT_DARK_R8.md`.

## 1. Objetivo y resultado

Auditar las UV de los objetos de Z10 que usan los cuatro materiales procedurales dominantes, crear variantes image-based 2K solo para Z10 y probarlas en 5 objetos de alta visibilidad, sin editar los `M_SH_*` compartidos ni reconstruir nada.

Resultado: 3 sets tiling 2K (stainless, galvanizado y sprinkler rojo), 3 materiales `M_Z10_HERO_*`, 5 objetos con una segunda UV de proyección mundial y un render A/B que confirma que el look se conserva y que las texturas exportan a glTF. El bake completo del sector **no** se ha hecho todavía: quedan 32 slots de `M_SH_Steel_Dark` y la mayor parte de galv/stainless.

## 2. Auditoría UV y biblioteca existente

Set de exportación Z10 (`docs/fm_z10_sector_export.json`): **516 objetos / 507 mallas / 519.450 tris**.

| Material procedural | Slots |
|---|---:|
| `M_SH_Steel_Stainless` | 24 |
| `M_SH_Steel_Galv` | 19 |
| `M_SH_Steel_Dark` | 32 |
| `M_SH_Sprinkler_Red` | 10 |

Los cuatro materiales aparecen en **37 objetos únicos** que suman **278.644 tris object-level (53,6 % del sector)**. El resto de pares son objetos multi-material, por lo que los tris no se suman por material.

**Hallazgo principal:** las UV actuales están empaquetadas y solapadas, no preparadas para texturas de imagen.

| Objeto del test | UV activa | Overlap UV | Densidad a 2K | UV nueva | Overlap nuevo | Densidad nueva |
|---|---|---:|---:|---|---:|---:|
| `P0B4_HVAC_RUN_800x600` | `MapaUV` | 96,6 % | 424 px/m | `UV_Z10_HERO` | 0 % | 2.046 px/m |
| `P0B4_SPRINKLER_RUN_DN80` | `MapaUV` | 100 % | 814 px/m | `UV_Z10_HERO` | 0 % | 1.926 px/m |
| `P0B4_TRAY_WEST` | `MapaUV` | 97,2 % | 66 px/m | `UV_Z10_HERO` | 0 % | 2.018 px/m |
| `P0B5_RISER_A` | `UVMap` | 85,4 % | 476 px/m | `UV_Z10_HERO` | 0 % | 1.971 px/m |
| `P0B4_SLEEVE_HVAC_W` | `MapaUV` | 55,8 % | 656 px/m | `UV_Z10_HERO` | 0 % | 2.045 px/m |

- `P0B4_TRAY_WEST` tiene además **18.924 triángulos con área UV < 1e-9** (prácticamente colapsada) en la capa antigua.
- En el set Z10 amplio la densidad antigua llega a 16.384 px/m en piezas pequeñas: es incoherente para cualquier textura de imagen.
- La biblioteca existente no cubre el pase hero: `M_FM_Steel_Dark` usa mapas de **512 px**, `M_FM_Metal_Panel` 1K, `M_FM_Rubber` 256, `M_FM_Safety_Yellow`/`M_FM_Sprinkler_Red` 512. `M_FM_Sprinkler_Red` se descartó para el ramal de 21,6 m porque su albedo de 512 px sobre UV empaquetada se estiraría; sigue siendo válido para piezas pequeñas.
- Por eso se bakea un set 2K propio en lugar de forzar los sets de 512.

## 3. Sets 2K: método y validación

Se construyó un shader temporal equivalente a cada `M_SH_*` (mismas rampas de color y roughness, mismas escalas de ruido, mismo bump) pero con coordenadas **4D sobre un toro de Clifford**: `(cos u·R, sin u·R, cos v·R, W=sin v·R)`, con `R = frecuencia/2π`. Así el ruido es periódico en U y V y el tile es continuo, sin costuras.

- 1 tile = **1 m**; 2048 px → **2.048 px/m**.
- Bake Cycles EMIT de BaseColor, Roughness y Height; el normal tangente OpenGL se deriva del height con diferencias centrales y wrap; el AO es micro-cavidad (dos escalas de blur con wrap); ORM empaqueta **R=AO, G=Roughness, B=Metallic**.
- Set completo por material: `BC, R, M, N, AO, ORM, H`. 3 sets × 7 PNG = **67,1 MB**. `H` no se conecta al material; queda para parallax/bump futuro.
- Continuidad de borde (diferencia en el borde / diferencia entre píxeles interiores): stainless **0,861 / 0,827**, galv **0,932 / 0,965**, rojo **0,950 / 0,975**. Valores ≈1 = sin costura.
- Roughness bakeada: stainless 0,173–0,361; galv 0,310–0,522; rojo 0,369–0,553. Normal B mín. 0,9929 / 0,9855 / 0,9808 (detalle fino deliberado).

## 4. Variantes y asignación

| Material nuevo | Mapas | Usuarios |
|---|---|---:|
| `M_Z10_HERO_Steel_Stainless_2K` | BC + N + ORM | 2 |
| `M_Z10_HERO_Steel_Galv_2K` | BC + N + ORM | 4 |
| `M_Z10_HERO_Sprinkler_Red_2K` | BC + N + ORM | 2 |

Los materiales usan un nodo `UVMap` → `UV_Z10_HERO` (no la UV activa), texturas `REPEAT`, normal map tangente y el grupo `glTF Material Output` para AO. No se editó ningún `M_SH_*`.

| Objeto | Tris | Slots sustituidos |
|---|---:|---|
| `P0B4_HVAC_RUN_800x600` | 9.564 | galv |
| `P0B4_SPRINKLER_RUN_DN80` | 5.218 | rojo |
| `P0B4_TRAY_WEST` | 49.168 | galv + stainless |
| `P0B5_RISER_A` | 19.136 | rojo + galv + stainless |
| `P0B4_SLEEVE_HVAC_W` | 3.308 | galv |

Total: **86.394 tris (16,6 % del sector)**. Los demás slots (rubber, cable, firestop, brass, labels, dark) se conservan intactos.

## 5. QA

- **0 non-manifold, 0 degenerate, 0 triángulos con área UV < 1e-9 y 0 solape en `UV_Z10_HERO`** en los 5 objetos. La UV antigua sigue activa y sin tocar.
- `qa_check` global sigue en `pass: false` por deuda **previa** de geometría: islas con normales invertidas (HVAC/Sprinkler/Tray/Riser/Sleeve = 24/1/133/69/10), z-fighting (20/668/917/139/18 pares) y 1 pieza flotante en el sprinkler. Se ejecutó el mismo QA sobre el backup y devuelve exactamente los mismos números: **no lo introduce este pase**.
- No se corrigió esa geometría: borrar caras ocultas o recalcular normales es un cambio destructivo fuera del objetivo de materiales y debe hacerse en el pase de limpieza/LOD.
- Test de export glTF de `P0B4_HVAC_RUN_800x600`: GLB 13,9 MB, atributos `POSITION/NORMAL/TEXCOORD_0/TEXCOORD_1`; el material usa **texCoord 1** y la misma imagen ORM alimenta `occlusionTexture` y `metallicRoughnessTexture`. Aviso: no se exportan tangentes porque la malla tiene n-gons; Godot debe generarlas o hay que triangular antes.

## 6. Renders

`docs/fm_z10_hero_duct_2k.png`, `fm_z10_hero_riser_2k.png` y `fm_z10_hero_wide_2k.png`: Cycles GPU, 1280×720, **128 samples**, denoise, AgX - Medium High Contrast. Close-ups sin niebla (exposición 0,4) para juzgar material; wide con niebla (0,2). Tiempos: 34,3 s / 33,4 s / 56,7 s.

A/B a 960×540, 64 samples, sin niebla: `fm_z10_hero_ab_duct_before/after.png` y `fm_z10_hero_ab_riser_before/after.png`.

## 7. Archivos

- Texturas: `assets/art/fm/z10_hero/T_Z10_{STEEL_STAINLESS,STEEL_GALV,SPRINKLER_RED}_2K_{BC,R,M,N,AO,ORM,H}.png`.
- Blend guardado: `nexus/nivel_01/FM_LEVEL1_V06_ARCH.blend` (paso 1: 50.490.303 B; R2: 50.801.434 B).
- Backup previo: `docs/backups/FM_LEVEL1_V06_ARCH_before_z10_hero_art.blend` (50.326.804 B).
- QA y manifiesto de texturas: `docs/fm_z10_hero_qa.json`.
- Renders y A/B en `docs/`.

## 8. Limitaciones

- Solo 5 de 37 objetos procedurales (86.394 de 278.644 tris, 31,0 %); el 69,0 % restante sigue procedural.
- `M_SH_Steel_Dark` (32 slots) no se toca; el set image-based existente es de 512 px y no es hero.
- Sin desgaste, suciedad, rayones ni daño de bordes: es metal limpio base.
- El patrón 2K se repite cada 1 m; no es un escaneo y puede notarse a poca distancia.
- AO solo micro-cavidad; sin AO macro.
- No se regeneró `z10_sector.glb` ni se validó en Godot; no hay medición de FPS/VRAM. El test glTF es de un solo objeto.
- Añade `TEXCOORD_1` a los 5 objetos: hay que verificar el binding y el consumo en Godot.
- Para asignar la variante a un objeto nuevo hay que crear antes su capa `UV_Z10_HERO`; si no existe, el nodo `UVMap` no tiene una capa válida.
- Las rutas de textura son absolutas, igual que el resto de assets del proyecto.

## 9. Siguiente paso

1. Extender el swap a los objetos galv/stainless de más visibilidad (24 + 19 slots) y decidir dark: bake 2K nuevo o reutilizar `M_FM_Steel_Dark` con UV nueva.
2. Regenerar `z10_sector.glb`, importar en Godot y validar TEXCOORD_1, tangentes, VRAM y FPS en la GTX 1650 Ti.
3. Después, pase de desgaste/suciedad/edge wear y decals narrativos.

## 10. Skills usadas

`blender-core` (API/verificación), `blender-pbr-materials` (reglas PBR, color spaces, ORM/glTF), `blender-texture-baking` (bake Cycles, normal/AO/ORM) y `blender-asset-qa` (QA numérico y comparación con backup). No se usaron skills de modelado/animación porque no se tocó geometría.

Sin commit. `fotos-referencia/` intacta.

## 11. Corrección R2 (2026-11-10)

### 11.1. Diagnóstico del parche blanco

El parche **no estaba en el conducto**. Los rayos de cámara sobre el rectángulo blanco y los renders de aislamiento identificaron **`P0B4_GRILLE_03`** (y su gemela `04`): una rejilla de impulsión a 2 m de la cámara, con el slot 0 en `M_SH_Steel_Galv` y el slot 1 en `M_SH_Aluminum` (procedural, sin textura de imagen). El aluminio plano devolvía una cara blanca uniforme que se leía como un parche sobre el conducto.

Auditoría de UV1 del conducto y de los objetos del prototipo:

- Las caras grandes del conducto tienen **área UV proporcional al área 3D** (p. ej. 1,9123 m² UV / 1,9123 m² 3D); no hay caras colapsadas.
- **0 bucles en (0,0)** y **0 triángulos con área UV < 1e-9** en `UV_Z10_HERO` y `UV_Z10_HERO_2M`.
- Las UV fuera de 0..1 son **intencionales** (proyección mundial) y los materiales usan `REPEAT`; no hay problema de wrap.
- El BC no contiene una región blanca rectangular; la asignación de slots del conducto es correcta.
- Causa real: un objeto distinto, con un material procedural plano, fuera del set de 5.

Corrección: se añadieron `P0B4_GRILLE_03` y `04` al prototipo (7 objetos), se les creó `UV_Z10_HERO` (1 m) y `UV_Z10_HERO_2M` (2 m), y se asignaron las variantes image-based a sus slots de galv/aluminio/stainless. **No se añadió geometría para tapar nada**; la rejilla sigue siendo la misma malla.

### 11.2. Galvanizado rehecho (2 m, spangle Voronoi)

Set nuevo: `T_Z10_STEEL_GALV_2M_2K_{BC,R,N,AO,M,ORM,H}.png`, 2048², tile **2 m** (1024 px/m), 6,77 MB. Sustituye al set de 1 m en `M_Z10_HERO_Steel_Galv_2K`; el set viejo queda en disco para rollback.

- Spangle de zinc con **Voronoi 4D** (F1 + distancia al borde, F=26, celdas ≈ 8 cm) sobre el toro periódico, más dos capas de ruido de baja frecuencia (0,5–1,5 m) y flakes finos. Ya no es ruido FBM de piedra.
- Roughness **0,400–0,525** con breakup por celda/borde/grano; AO **0,965–0,996**; Normal B **0,9046–1,0**; fuerza de normal **0,30** (dentro de 0,2–0,4).
- Costuras: **0,959 / 0,741** (borde vs. píxel interior; ≈1 = sin costura).
- UV: capa `UV_Z10_HERO_2M`, 0 solapes, 0 triángulos casi nulos, **985–1032 px/m**.
- El render 3/4 `fm_z10_hero_duct_r2.png` muestra spangle bajo luz rasante, sin el picado de alta frecuencia ni el parche blanco. El A/B `fm_z10_hero_ab_duct_r2_{before,after}.png` (960×540, 64 spp) compara el set viejo y el nuevo desde la misma cámara.

### 11.3. Rojo sprinkler con desgaste

Set nuevo: `T_Z10_SPRINKLER_RED_WORN_2K_*`, 1 m, 3,96 MB, en `M_Z10_HERO_Sprinkler_Red_2K`.

- Base roja con mottling de baja frecuencia, polvo cálido en zonas amplias, **chips metálicos escasos** (umbral 0,004; color 0,18 lineal), variación de roughness **0,380–0,549** y micro-relieve de chips/pintura.
- Normal B **0,9117–1,0**, fuerza **0,45**; AO **0,941–1,0**; costuras 0,977 / 1,394 (la V es ruidosa por los chips dispersos; el patrón se genera en el toro periódico).
- En `fm_z10_hero_riser_r2.png` el tubo rojo deja de ser plano: tiene variación de color/rugosidad y chips pequeños, sin óxido naranja ni salpicaduras blancas.
- **Reserva honesta:** el desgaste de **bordes de bridas** no está resuelto por curvatura de objeto; es desgaste de textura. Para bordes reales hace falta una máscara de curvatura por objeto o decals en el siguiente pase.

### 11.4. QA R2

- **0 non-manifold, 0 degenerate, 0 UV de área casi nula y 0 solape** en las capas nuevas de los 7 objetos.
- QA global sigue `pass: false` por deuda previa: islas invertidas (HVAC 24, sprinkler 1, tray 133, riser 69, sleeve 10, grillas 9/4), z-fighting (20/668/917/18/139 pares) y piezas flotantes (sprinkler 12 verts; lamas de las rejillas). **Idéntico en el backup** `before_z10_hero_art_r2.blend`: no lo introduce este pase. La rejilla ya tenía sus lamas flotantes antes de tocarla.
- `qa_check` evalúa la UV **activa** (`MapaUV`/`UVMap`), que sigue solapada y se conserva para los materiales no-hero; por eso sus warnings de UV no describen las capas nuevas. La auditoría específica de `UV_Z10_HERO`/`UV_Z10_HERO_2M` está en `docs/fm_z10_hero_qa.json`.

### 11.5. Tangentes y n-gons

- Export glTF del conducto **sin triangular**: atributos `POSITION/NORMAL/TEXCOORD_0/1/2`, **sin TANGENT**; warning “Could not calculate tangents… triangulate first”.
- Copia temporal **triangulada**: **TANGENT presente**, material galv con `texCoord: 2`, `normalTexture.scale: 0.30`, ORM compartido por oclusión y metallicRoughness.
- Recomendación: triangular antes del export (o generar tangentes en Godot). El asset guardado conserva quads/n-gons; no se trianguló destructivamente.

### 11.6. Renders R2

`fm_z10_hero_duct_r2.png`, `fm_z10_hero_riser_r2.png`, `fm_z10_hero_wide_r2.png`: Cycles GPU, 1280×720, **128 spp**, denoise, AgX - Medium High Contrast. Cámaras: duct 3/4 desde (52.5, 15.5, 2.2); riser desde (48.3, 17.5, 2.0); wide desde (49, 9.5, 1.8) con lens 20. Tiempos 36,0 / 34,0 / 34,4 s.

El wide no tiene la columna tapando el centro y la etiqueta del suelo se lee **“CONECTOR DE…”** sin espejar. El texto completo queda parcialmente fuera de cuadro por la posición de la cámara y el banco de taquillas; no se rota ni se mueve la etiqueta.

### 11.7. Archivos y estado

- Texturas nuevas: `T_Z10_STEEL_GALV_2M_2K_*` y `T_Z10_SPRINKLER_RED_WORN_2K_*` (14 PNG, 10,73 MB).
- Backup previo a R2: `docs/backups/FM_LEVEL1_V06_ARCH_before_z10_hero_art_r2.blend` (50.490.303 B).
- Blend guardado (R2): `nexus/nivel_01/FM_LEVEL1_V06_ARCH.blend` (50.801.434 B); el R3 actual está en 12.4.
- QA y manifiesto: `docs/fm_z10_hero_qa.json`; renders y A/B en `docs/`.
- Prototipo: **7 objetos, 94.034 tris (18,1 % del sector)**. `M_SH_Steel_Dark` sigue intacto; no se extendió a los 37 objetos.

### 11.8. Veredicto

**Aprobado para el prototipo, con reservas.** El conducto ya lee como galvanizado con spangle y sin parche blanco; el rojo tiene desgaste sutil y deja de ser plano; el wide es legible y está despejado. Las reservas son: el desgaste de borde del rojo es solo de textura, el patrón galv repite cada 2 m y no se ha exportado/validado en Godot.

Siguiente: si el usuario quiere bordes de desgaste reales, añadir máscara de curvatura por objeto o decals; después extender a los 24+19 slots galv/stainless, decidir dark, triangular y regenerar `z10_sector.glb`, y validar UV2/UV3, tangentes, VRAM y FPS en la GTX 1650 Ti.

## 12. Corrección R3 (2026-11-10)

### 12.1. Galvanizado fino (1–3 cm)

Se rehízo `T_Z10_STEEL_GALV_2M_2K_*` manteniendo el tile de **2 m** y 2048² (1024 px/m), 15,07 MB:

- **Spangle Voronoi 4D** a dos escalas: F=90 (celdas ≈2,2 cm) y F=180 (≈1,1 cm), más **flakes finos** F=300 (≈6,7 mm), todo periódico en el toro. Ya no hay celdas de ~8 cm ni aspecto de camuflaje/mármol.
- **Base de acero neutro**: lineal 0,49–0,54; variación de celda ±0,002; sin oscurecimiento de borde; contraste bajo. La lectura viene del roughness/normal, no de manchas de color.
- **Roughness 0,349–0,502**, normal B 0,9308–1,0, fuerza de normal **0,25**, AO 0,98–1,0. Costuras 1,071 / 0,973.
- Asignado a los **6 objetos del prototipo con slot galv** (HVAC, tray, riser, sleeve, grille03, grille04). El séptimo, el ramal sprinkler, solo tiene rojo + dark y no se le añadió un slot artificial. `M_Z10_HERO_Steel_Galv_2K` usa `UV_Z10_HERO_2M`.
- Render `fm_z10_hero_duct_r3.png`: el conducto muestra grano cristalino fino y bajo contraste, sin el patrón grueso de R2.

### 12.2. Wide, equilibrio y banding del suelo

- Cámara 3/4 final: `(46, 18, 2.0)`, rot `(95°, 0, −72°)`, lens 24. El conducto cruza en diagonal, el riser y la columna quedan a la izquierda, la pared/lockers iluminados al fondo y la etiqueta del suelo **“DE SERVICIO”** se lee sin espejar. No hay columna tapando el centro ni el hueco negro dominante de R2.
- Exposición **0,22**, todas las luces originales activas, niebla off. El conducto ya no sale blanco; el fondo conserva detalle.
- **Banding del suelo:** diagnosticado como **artefacto del denoiser OIDN** sobre un gradiente oscuro de baja varianza, amplificado por el ángulo rasante. Evidencia:
  - Render 1280×720 con **denoise off** (256 spp): sin anillos, solo ruido fino.
  - Render 1280×720 con **denoise on** y roughness del suelo forzada a 1,0 (sin especular): los arcos persisten.
  - `M_FM_Concrete_Floor` usa imágenes por UV, sin Mapping ni proyección mundial/objeto; el normal map es plano (127,127,254); albedo y roughness no contienen anillos. Las UV de las baldosas son 0..0,525 × 0..1 por tile de 4×4 m; no hay proyección radial.
  - **No se tocó** la geometría ni el material del suelo. El wide final usa **256 spp con denoise off** para evitarlo.

### 12.3. Rojo

El set `T_Z10_SPRINKLER_RED_WORN_2K_*` se mantiene, con el polvo subido a **0,36** de máscara; chips escasos (umbral 0,004), roughness 0,38–0,553, normal 0,45. Sin óxido naranja ni manchas blancas. Sigue siendo desgaste de textura, no de curvatura de bordes.

### 12.4. QA, archivos y estado

- UV `UV_Z10_HERO` / `UV_Z10_HERO_2M`: **0 solape, 0 triángulos casi nulos, 0 bucles en (0,0)**; sin cambios respecto a R2.
- Geometría **sin tocar**: 0 non-manifold, 0 degenerate; el QA global sigue `pass:false` por islas invertidas, z-fighting y piezas flotantes preexistentes, idénticas en el backup.
- Renders: `docs/fm_z10_hero_duct_r3.png` (1280×720, 128 spp, denoise on, 34,9 s) y `docs/fm_z10_hero_wide_r3.png` (1280×720, **256 spp, denoise off**, 50,3 s), Cycles GPU, AgX.
- Backup previo a R3: `docs/backups/FM_LEVEL1_V06_ARCH_before_z10_hero_art_r3.blend` (50.801.434 B). Blend guardado: 50.788.091 B.
- Prototipo: **7 objetos, 94.034 tris (18,1 %)**. `M_SH_Steel_Dark` intacto; no se extendió a los 37 objetos. Sin GLB/Godot en este pase.

### 12.5. Veredicto

**Aprobado como prototipo R3.** El galvanizado ya lee como acero galvanizado fino, no camuflaje; el wide está equilibrado, es 3/4 y la etiqueta es legible; el rojo tiene polvo/desgaste sutil; el banding está identificado y evitado en el render final. **No aprobado aún como pase hero completo de Z10**: quedan 30 objetos procedurales, el desgaste de borde del rojo es solo de textura y no hay export/validación en Godot.

## 13. Extensión a 37 objetos, GLB y Godot (R4)

### 13.1. Cobertura y reconciliación de conteos

Selección exportable: **516 objetos / 507 mallas / 402 únicas / 9 luces / 519.450 tris**, idéntica al pre-hero. Objetos con materiales de acero: **37 / 278.644 tris**.

- Antes de esta etapa, la selección actual tenía **20 slots de `M_SH_Steel_Stainless` y 15 de `M_SH_Steel_Galv`** (no 24/19). La cifra de la tarea no corresponde al estado exportable actual (posible conteo previo o que incluya retirados/legacy). No se añadieron objetos: se cubrieron **todos** los slots presentes.
- Slots hero finales: **30 stainless / 26 objetos**, **25 galv / 25**, **32 dark / 32**, **12 red / 12**. La suma supera los 37 porque hay objetos con varios slots de acero; la unión es 37.
- **0 slots de acero procedurales** en la selección. El rojo worn aprobado se conservó y se extendió a los 10 slots de sprinkler del set (12 con los 2 ya existentes).
- Quedan **43 slots de acentos no-acero procedurales**: 13 `M_SH_Label_Aluminium`, 6 `M_SH_Brass`, 6 `M_SH_Firestop_Red`, 5 `M_SH_Rubber_Seal`, 4 `M_SH_Aluminum`, 3 `M_SH_Diffuser_On`, 3 `M_SH_Cable_Black`, 2 `M_SH_GaugeFace`, 1 `M_SH_Paint_SafetyOrange`. Son fuera del alcance acero; convertirlos exige sets/decisiones de etiquetas, latón, goma, cable, difusor, gauge y pintura.

### 13.2. Decisión dark

Se **bakeó** un set nuevo en lugar de reutilizar `M_FM_Steel_Dark` (512 px, insuficiente para 32 slots hero):

- `T_Z10_STEEL_DARK_2M_2K_*`, 2 m/2048 (1024 px/m), 8,61 MB; base de acero oscuro neutro, grain fino, roughness **0,325–0,494**, normal **0,20**, AO 0,984–0,996, costuras 0,968/1,002.
- `M_Z10_HERO_Steel_Dark_2K` usa `UV_Z10_HERO_2M`; 31 slots.
- `P0B4_SPRINKLER_RUN_DN80` usa una variante `M_Z10_HERO_Steel_Dark_1M` con el mismo set y `UV_Z10_HERO` (1 m): su tira UV de 2 m mide solo 0,065 de alto y el sampler de 256 la marcaba como solapada; con 1 m el QA da 0. Es un clamp pequeño, el cambio visual es mínimo.

### 13.3. QA de UV y geometría

- **0 non-manifold, 0 degenerate y 0 triángulos con área UV < 1e-9** en los 37 objetos (278.644 tris).
- **0 solape** con el sampler 256×256 usado en R2/R3; `UV_Z10_HERO` en 33 objetos y `UV_Z10_HERO_2M` en 32 (los que no la necesitan no la tienen). UV0 intacta, nombres activos preservados. Nota: las UVs de tiling fuera de 0..1 se evalúan en la ventana 0..1; en una proyección de caja las caras opuestas comparten fase de tile (solape módulo 1) por diseño, no es un defecto de bake. No hay islas colapsadas ni triángulos nulos.
- Comparado con `before_z10_hero_extension.blend`: 37 objetos, 278.644 tris, 0/0. La geometría no se modificó.
- El QA global sigue `pass:false` por islas invertidas, z-fighting y piezas flotantes preexistentes; no se oculta ni se atribuye a esta etapa.

### 13.4. GLB

- Se parcheó `scripts/fm/fm_z10_sector_export.py` para exportar **tangents, texcoords, normals e imágenes** (`export_tangents=True`, `export_image_format='AUTO'`).
- Se exportó desde una **copia triangulada** (`/tmp/opencode/z10_export_ext.blend`), no desde el blend guardado; el blend conserva quads/n-gons. La triangulación no cambió conteos ni tris.
- Resultado: **74.255.200 bytes**, 516 objetos, 507 mallas, 402 únicas, 9 luces, 519.450 tris. GLB: 516 nodos, 402 mallas glTF, 116 materiales, 81 texturas, **52 imágenes embebidas (37,08 MB)**.
- **650/655 primitivas con TANGENT**; las 5 sin tangente son blockout sin UV/normal (`M_L1_*_Blockout/Corridor`). Los **74 primitivos hero tienen TANGENT y TEXCOORD_1**. Presencia: TEXCOORD_0 650, TEXCOORD_1 111, TEXCOORD_2 90, TEXCOORD_3 8; los materiales hero usan texCoord 1/2/3 según el índice de capa del objeto. Se verificaron **1.408 referencias de textura** contra los atributos TEXCOORD del primitivo: **0 desajustes**.
- Imágenes hero incluidas: stainless 14,1 MB, galv 10,75 MB, dark 6,36 MB, red 2,98 MB (BC/N/ORM embebidos). Aviso: 18 referencias de imagen preexistentes sin tamaño no se exportan (Barrel_02 metallic/roughness ×4, steel_frame_shelves ×3, metal_stool, utility_box); no son hero.
- El tamaño no es comparable 1:1 con los 113,9 MB pre-hero: cambió el contenido de texturas y se añadieron tangentes; los conteos de malla sí coinciden.

### 13.5. Godot 4.7.2

- `godot --headless --path . --import`: exit 0, sin líneas ERROR/WARNING.
- `godot --headless --path . scenes/fm/fm_z10_sector_validate.tscn`: **`Z10_SECTOR meshes=507 unique=402 lights=9`**, AABB pos `(39.87, −0.208947, −34.939)`, size `(30.2835, 6.208947, 36.939)`, **`Z10_SECTOR_GODOT_OK`**.
- **VRAM estimada**: 68 ctex extraídos del GLB (52 imágenes, algunas divididas/duplicadas), formato RGBA8 sin mips, **472,4 MB** de datos de imagen; los 12 mapas hero son **192 MB**. Con BC7/BC5 + mips bajaría a ~157 MB. No se midió VRAM de GPU ni FPS; no se afirma FPS.

### 13.6. Archivos, limitaciones y veredicto

- Backup previo: `docs/backups/FM_LEVEL1_V06_ARCH_before_z10_hero_extension.blend` (50.788.091 B). Blend guardado: **51.859.340 B**.
- GLB: `assets/models/fm/z10_sector.glb`; reporte `docs/fm_z10_sector_export.json`; set dark en `assets/art/fm/z10_hero/`; docs actualizados.
- Limitaciones: 43 acentos procedurales; 18 imágenes preexistentes sin exportar; 5 primitivas blockout sin TANGENT; texturas sin comprimir/mips (472 MB); 116 materiales por variantes de UV (draw calls no medidos); sin FPS; sin edge wear/decals.
- **Veredicto:** **aprobado en el alcance acero** (37 objetos, 0 slots de acero procedurales, GLB con tangentes/texturas, Godot OK). **No aprobado como “cero procedurales” total**: quedan 43 slots de acentos no-acero y la VRAM de texturas no está optimizada.

## 14. R5: acentos, legacy, compresión, desgaste y GLB final

### 14.1. Acentos no-acero: 43/43 cubiertos

| Material | Slots | Solución |
|---|---:|---|
| `M_SH_Label_Aluminium` | 13 | `M_Z10_HERO_Label_Alu_1K` (1K BC/ORM) |
| `M_SH_Brass` | 6 | `M_Z10_HERO_Brass_1K` |
| `M_SH_Firestop_Red` | 6 | `M_Z10_HERO_Firestop_Red_1K` |
| `M_SH_Rubber_Seal` | 5 | `M_Z10_HERO_Rubber_1K` |
| `M_SH_Aluminum` | 4 | `M_Z10_HERO_Steel_Stainless_2K` (reutilizado) |
| `M_SH_Diffuser_On` | 3 | `M_Z10_HERO_Diffuser_1K` (emisión 2,6) |
| `M_SH_Cable_Black` | 3 | `M_Z10_HERO_Rubber_1K` (reutilizado) |
| `M_SH_GaugeFace` | 2 | `M_Z10_HERO_Gauge_A_1K` / `_B_1K` (dial ajustado a la UV de cada feed) |
| `M_SH_Paint_SafetyOrange` | 1 | `M_Z10_HERO_SafetyOrange_1K` |

**0 slots `M_SH_*` restantes** en los 507 objetos de la selección. Sets nuevos 1K: 6 + 2 variantes de gauge; 22 PNG (17 imágenes embebidas, 3,96 MB). Las etiquetas son placas genéricas con marcas sutiles, no texto específico; los diales son genéricos 0–100 ajustados a cada isla UV. No se añadió geometría ni decals nuevos.

UV: `UV_Z10_HERO` añadida a `P0B5_SPRINKLER_ESCUTCHEONS` y `P0B5D_RISER_TAGS`; **0 solape / 0 área casi nula**; el gauge usa UV0; UV0 intacta. La auditoría de UV1/UV2 de los 37 objetos sigue en 0/0.

### 14.2. Imágenes legacy

Las 18 advertencias “has no size” eran **8 mapas únicos** de metal/roughness (EXR/JPG) duplicados en 4 barriles, 3 estanterías, 1 taburete y 2 armarios visibles. Se convirtieron a PNG RGB en `assets/art/fm/generated/legacy_pbr/`, se reenlazaron todas las copias a imágenes compartidas y se empaquetaron; diffuse/normal se mantuvieron y empaquetaron. Resultado: **0 advertencias**, **4 imágenes combinadas metal/rough (10,02 MB)** y los props conservan sus mapas PBR en el GLB.

### 14.3. Compresión y VRAM

- Godot importa el GLB con texturas extraídas (`gltf/embedded_image_handling=1`); los **86 `.import`** extraídos se configuraron con `compress/mode=2`, `compress/high_quality=true`, `mipmaps/generate=true` y `compress/normal_map=1` para normales.
- Medición en ventana, **GTX 1650 Ti, Vulkan Forward+**, `Performance.RENDER_TEXTURE_MEM_USED` / `RENDER_VIDEO_MEM_USED`:
  - Antes de comprimir: **446,9 MB textura / 512,5 MB vídeo**.
  - Después: **216,2 MB textura / 281,8 MB vídeo**.
- **FPS no medido**; no se afirma FPS. El GLB fuente sigue en 137,9 MB; el `.scn` importado son 17 MB + texturas comprimidas.

### 14.4. Desgaste y etiquetas

- **3 tubos rojos** (`P0B4_SPRINKLER_RUN_DN80`, `P0B5_RISER_A/B`): atributo de color `WearEdge` desde aristas agudas (>28°, 2 pasadas de suavizado). El material `M_Z10_HERO_Sprinkler_Red_WEAR_2K` multiplica el color base con `ShaderNodeMix`; el GLB exporta **COLOR_0 en 14 primitivas** con valores 0,637–0,723.
- **TANGENT 650/655**; las 5 sin tangente son blockout sin UV. El desgaste no usa geometría nueva; las etiquetas están en las placas/escutcheones existentes y el gauge en el dial texturizado.
- **Limitación Godot:** el material de desgaste se importa con `vertex_color_use_as_albedo=false`; COLOR_0 está en el GLB y se ve en los renders Blender, pero en Godot hay que activar ese flag o hacer override para verlo. Sin óxido naranja ni manchas blancas.

### 14.5. Renders

- `docs/fm_z10_hero_set_r5.png`: 1280×720, **256 spp, denoise on**, AgX, exposición 0,22, cámara 3/4 `(46,18,2.0)`, lens 24; 53,5 s.
- `docs/fm_z10_hero_detail_r5.png`: 1280×720, 256 spp, denoise on, AgX, cámara `(48.3,17.5,2.0)`, lens 55; 42,0 s.
- A/B: `docs/fm_z10_hero_ab_set_r5_before.png` (R3 wide) y `..._after.png` (R5 set), misma cámara/exposición. Sin banding de OIDN visible.

### 14.6. GLB y Godot finales

- **137.929.288 B**, **516 objetos / 507 mallas / 402 únicas / 9 luces / 519.450 tris**; 516 nodos, 402 mallas glTF, **118 materiales, 128 texturas, 81 imágenes (97,14 MB)**.
- **650/655 TANGENT**; **TEXCOORD_0 650, TEXCOORD_1 112, TEXCOORD_2 93, TEXCOORD_3 8**; 1.525 referencias de textura verificadas, **0 desajustes**. COLOR_0 en 14 primitivas.
- Grupos de imágenes: hero 32,6 MB, acentos 3,96 MB, legacy 10,02 MB, otros 50,56 MB. **Sin advertencias de imágenes legacy**.
- Godot: `--import` exit 0 sin ERROR/WARNING; validador **507/402/9**, AABB `(39.87, −0.208947, −34.939)` / `(30.2835, 6.208947, 36.939)`, **`Z10_SECTOR_GODOT_OK`**.

### 14.7. QA, archivos y veredicto

- **0 non-manifold, 0 degenerate**, geometría sin tocar; UV nuevas 0 solape/0 área casi nula; UV0 intacta. El QA global sigue `pass:false` por islas invertidas, z-fighting y flotantes preexistentes, no ocultados.
- Backup R5: `docs/backups/FM_LEVEL1_V06_ARCH_before_z10_hero_r5.blend` (51.859.340 B, R4 final). Blend guardado: **81.087.072 B** (incluye imágenes legacy empaquetadas).
- Archivos: `assets/models/fm/z10_sector.glb`, `docs/fm_z10_sector_export.json`, `assets/art/fm/z10_hero/accents/`, `assets/art/fm/generated/legacy_pbr/`, renders en `docs/`.
- **Veredicto:** **aprobado en R5** para acentos, legacy, compresión/VRAM, render y GLB/Godot. Limitaciones: el desgaste no se ve en Godot sin activar `vertex_color_use_as_albedo`; etiquetas/diales genéricos; sin FPS medido; la deuda geométrica global sigue.

## 15. R6: pared, superficies, luz cinematográfica, narrativa y Godot wear

### 15.1. Pared que leía como madera

**Causa:** `M_FM_Concrete_Wall` (imágenes 1K `concrete_wall_*`) sobre las paredes `KIT_PILOT_Z10_Wall_*` con UV0 **0..1 × 0..0,683** por panel de 4 × 4,2 m. El estiramiento vertical (~1,46×) y las líneas/direccionalidad de la textura producían la veta de madera.

**Solución:** set **2K plaster** `T_Z10_WALL_PLASTER_2K_*` (BC/R/ORM, sin normal) y `M_Z10_HERO_Wall_Plaster_2K` con capa **`UV_Z10_WALL`** (proyección de caja 4 m con offset por cara). Mottling no direccional, manchas de agua, goteos cortos, grietas y roces. Sin geometría nueva; el resto de materiales `M_FM_Concrete_Wall` fuera de Z10 no se tocan.

### 15.2. Suelo y techo

- **Suelo:** `T_Z10_FLOOR_CONCRETE_2K_*` + `M_Z10_HERO_Floor_Concrete_2K`, `UV_Z10_FLOOR` 4 m; árido, manchas húmedas/aceite, roces y juntas de baldosa.
- **Techo:** `T_Z10_CEILING_PANEL_2K_*` + `M_Z10_HERO_Ceiling_Panel_2K`, `UV_Z10_CEILING` 4 m; retícula de panel, manchas de agua y polvo.
- 9 PNG 2K en `assets/art/fm/z10_hero/surfaces/` (7,9 MB). Sin geometría nueva; UV0 intacta.

### 15.3. Iluminación y lookdev

- `VOL_Z10_Fog`: densidad **0,0035**, anisotropía 0,25, color (0,55, 0,62, 0,72).
- `LIGHT_Z10_Emergency_E`: **40 W**, rojo (1,0, 0,02, 0,01); práctica roja visible en pared/conducto.
- Para el beauty se ocultan los **9 duplicados** `P0B5B_*` y las luces `STUDIO_Z10_*`; se reutilizan las luces existentes, sin añadir nuevas. Exposición 0,28, AgX - Medium High Contrast.
- Cámara 3/4 `(46, 18, 2.0)`, lens 24. La niebla/luz es **Cycles**; el GLB no transporta el volumen.

### 15.4. Narrativa ambiental

Las nuevas superficies incorporan manchas de agua, goteos, grietas, roces, manchas de aceite/humedad y daño de techo. Se reutilizan cables, papeles, señalización, conos, carritos, extintores y charcos existentes. **0 props hero nuevos**, sin armas ni combate. Etiquetas/diales siguen siendo genéricos; texto específico requeriría UV/decals por objeto y se documenta como siguiente paso.

### 15.5. Godot: desgaste COLOR_0

- Script `scripts/fm/fm_z10_sector_post_import.gd` (`EditorScenePostImport`), registrado en `assets/models/fm/z10_sector.glb.import` (`import_script/path`).
- En post-import recorre `MeshInstance3D` y pone `vertex_color_use_as_albedo=true` en `M_Z10_HERO_Sprinkler_Red_WEAR_2K`.
- Verificado: `vc=true` en `P0B4_SPRINKLER_RUN_DN80` y `P0B5_RISER_A`. Preview `docs/fm_z10_godot_wear_r6.png` con la material real y luces de estudio (el GLB crudo está sobreexpuesto sin environment).
- El desgaste se ve como oscurecimiento sutil en bordes de bridas/segmentos; no hay óxido naranja ni manchas blancas.

### 15.6. Beauty R6

- `docs/fm_z10_hero_beauty_r6.png`: **1280×720, 256 spp, denoise on**, AgX, exposición 0,28; 97,1 s; cámara 3/4.
- Sin artefactos observados: pared plaster (no madera), suelo/techo con suciedad/juntas, niebla y rojo de emergencia, ducto con detalle; sin banding OIDN visible.
- A/B: `docs/fm_z10_hero_ab_beauty_r6_before.png` (R5 set) / `..._after.png` (R6 beauty), misma cámara.

### 15.7. GLB, Godot, VRAM y FPS

- GLB final: **144.619.328 B**, **516 objetos / 507 mallas / 402 únicas / 9 luces / 519.450 tris**; 121 materiales, 134 texturas, **87 imágenes (103,5 MB)**; 6 imágenes de superficies (6,36 MB).
- **650/655 TANGENT**; TEXCOORD_0 650, **TEXCOORD_1 123**, TEXCOORD_2 93, TEXCOORD_3 8; **1.525 referencias, 0 desajustes**; COLOR_0 14 primitivas; sin advertencias de imágenes legacy.
- Godot: `--import` exit 0 sin ERROR/WARNING; validador **507/402/9**, AABB `(39.87, −0.208947, −34.939)` / `(30.2835, 6.208947, 36.939)`, **`Z10_SECTOR_GODOT_OK`**.
- VRAM medida en ventana GTX 1650 Ti, Vulkan Forward+: **248,2 MB textura / 313,8 MB vídeo** (92 texturas extraídas comprimidas + mips).
- **FPS medido**: **581,7 FPS** estático, 1280×720, VSync off, 5 s / 2.909 frames, Forward+, GTX 1650 Ti. Es una escena estática del GLB, sin gameplay y sin niebla de Godot; no representa FPS del juego final.

### 15.8. QA, archivos y veredicto

- **0 non-manifold, 0 degenerate**, geometría sin tocar; UV nuevas de pared/suelo/techo: 0 área casi nula; solape **31,6–42,2 %** por proyección de caja en caras opuestas (materiales tiling, no bake). UV0 intacta; UV de acero/acentos siguen 0/0.
- QA global `pass:false` por deuda preexistente (islas invertidas, z-fighting, flotantes), no ocultada.
- Backup R6: `docs/backups/FM_LEVEL1_V06_ARCH_before_z10_hero_r6.blend` (81.087.072 B, R5 final). Blend guardado: **81.082.479 B**. GLB `assets/models/fm/z10_sector.glb`; superficies en `assets/art/fm/z10_hero/surfaces/`; docs actualizados.
- **Veredicto:** **aprobado en Blender beauty R6** (pared corregida, superficies, niebla/rojo, desgaste en Godot). **No aprobado como paridad visual Godot completa**: la niebla/luz cinematográfica no viaja en el GLB y el GLB crudo necesita environment/exposición; etiquetas/diales genéricos; FPS estático, sin gameplay; deuda geométrica global.
- **Siguiente:** WorldEnvironment/volumetric fog en Godot para paridad, etiquetas/diales específicos con UV/decals, LOD/optimización medida si hace falta, y gameplay.

## 16. R7: paridad visual Godot

- **Escena:** `scenes/fm/fm_z10_art_r7.tscn` + `scripts/fm/fm_z10_art_r7.gd`. Carga el GLB R6 sin modificarlo; environment AgX (exposición 0.94, contraste 1.25), glow 0.30, niebla volumétrica 0.018/aniso 0.25, SSAO y SSR.
- **Luces:** las 9 luces del GLB se reescalan en runtime (rango 4.5–10, energía 0.1–2.0, sombras en Point_01/02/03 y Emergency). Se añaden `Key` spot, `Fill`/`Center`/`EastWash` omni y dos directionals de bounce (techo/suelo) para compensar las area lights/GI que no exportan.
- **Desgaste:** el post-import sigue activo; la escena imprime `Z10_ART_R7_WEAR vc=true node=P0B4_SPRINKLER_RUN_DN80`.
- **Etiqueta de suelo:** `ANNOT_L1_Label_09` ("10 CONECTOR DE SERVICIO") no está en el GLB; se añadió un `Decal` scene-only con textura RGBA 2048×256 generada desde esa geometría. No se rehízo UV ni GLB.
- **Captura:** `docs/fm_z10_godot_parity_r7.png`, 1280×720, cámara `(46,2,-18)`, FOV 68° horizontal (24 mm estrictos = 73.7°; 68° iguala mejor el encuadre R6). A/B en `docs/fm_z10_godot_parity_r7_ab.png`.
- **Tono:** media R7 `(69.6, 65.0, 60.8)` vs R6 `(68.6, 66.3, 64.9)`; mediana de luminancia 62 en ambos; p10 31 vs 17; p90 106 vs 120.
- **Rendimiento:** **197,2 FPS** estáticos (986 frames/5.001 s, 1280×720, VSync off, Forward+, GTX 1650 Ti); **362,9 MB textura / 448,6 MB vídeo**. Es una escena estática con niebla/SSAO/SSR/sombras, no gameplay.
- **Veredicto:** paridad tonal/atmosférica aprobada; **no pixel-perfect**: faltan GI/area/volumen de Cycles, el muro este/ducto/pilar quedan más oscuros, el techo está más liso y la puerta casi negra. Detalle y limitaciones en `docs/FM_Z10_GODOT_PARITY.md`.

## 17. R8: dirección oscura de Z10

- **Escena nueva:** `scenes/fm/fm_z10_art_r8.tscn` + `scripts/fm/fm_z10_art_r8.gd`; R7 se conserva para A/B. Sin cambios en GLB, `.blend` ni `fotos-referencia/`.
- **Sin luces no diegéticas:** no hay `Key`, `Fill`, `Center`, `EastWash`, `CeilingBounce` ni `FloorBounce`; el `.tscn` R8 no contiene ningún `Light3D` de escena.
- **Solo emergencia:** de las 9 luces del GLB se conservan 3 rojas (`Emergency_E` 3.0/6.0 con sombras; conectores E/N 0.30/3.5 sin sombras) y se ocultan las otras 6 (`kept=3 disabled=6`).
- **Emisivos normales apagados:** 29 overrides de superficie en las 3 luminarias de techo y la lámpara de trabajo; el GLB no se modifica.
- **Environment:** AgX exposición **0.80**, ambient **0.020**, fondo casi negro, niebla 0.012, glow 0.20, SSAO/SSR. La niebla no tiene ambient/GI inject.
- **Desgaste:** `Z10_ART_R8_WEAR vc=true`.
- **Capturas:** `docs/fm_z10_godot_dark_r8.png` (escena real) y `docs/fm_z10_godot_dark_flashlight_r8.png` (linterna diagnóstica temporal, no guardada). A/B: `docs/fm_z10_godot_dark_r8_ab.png`.
- **Rendimiento:** **320,7 FPS** estáticos (1604 frames/5.002 s, 1280×720, VSync off, Forward+); **361,4 MB textura / 441,5 MB vídeo**. No es gameplay.
- **Veredicto:** cumple la dirección oscura de Z10; la habitación es casi negra con tres fuentes rojas de emergencia. La excepción de recepción queda fuera de esta escena y anotada para su pase propio. Detalle en `docs/FM_Z10_GODOT_DARK_R8.md`.

Sin commit. `fotos-referencia/` intacta.

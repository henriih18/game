# FM — Recepción R9: servicios necesarios

## Criterio

No se copia el exceso de Z10. Recepción recibe solo los servicios que necesita y que pueden justificarse por función, cobertura y continuidad. Los patinillos siguen pendientes por decisión del usuario; no se ha modificado la arquitectura.

## R9.1 — HVAC

### Construcción

- Colección `L1_RECEPTION_R9_HERO`.
- `REC09_HVAC_MAIN`: tramo hero 800×600 de **40 m**, x −110..−70, y −14, centro z 4,50. Cortado de `P0B_HVAC_RUN_800x600`, con bridas, refuerzos y cleats del maestro.
- `REC09_HVAC_TRANSITION`: transición 800×600 → 600×400 en x −88.
- `REC09_HVAC_BRANCH_00..04`: ramal 600×400 de **10,6 m** hacia el sur, x −88, y −14,6..−24,6, z 4,50. Cinco módulos de 2 m que comparten malla.
- `REC09_HVAC_BRANCH_END`: tapa cierre con cuatro pernos.
- **7 difusores** `REC09_HVAC_GRILLE_*`: 4 sobre el tramo principal (x −100, −94, −80, −72) y 3 sobre el ramal (y −17,0, −20,6, −23,4), orientados hacia abajo.
- **Soportes:** 8 trapecios en el tramo principal y 2 en el ramal, con varillas, placas, travesaños, cleats y pernos.
- **Penetraciones:** sleeves 800×600 en x −110 y −70; fire dampers en x −109,45 y −70,55.
- Se retiraron 13 objetos viejos `KIT_REC01_HVAC_*` (ducto, 9 flanges y 3 hangers) a `L1_RECEPTION_RETIRED_R9`, ocultos.

### Conteos y QA

- **20 objetos / 136.744 tris / 69.980 vértices**.
- QA `docs/fm_reception_r9_hvac_qa.json`: **PASS**, 0 non-manifold, 0 degenerados, UV presente en todos los objetos.
- AABB `[-110.154, -24.633, 4.021]..[-69.846, -13.450, 5.196]`; todo dentro de Recepción.
- `retired_visible=[]`.

### Renders

- `docs/fm_reception_r9_hvac_wide.png`
- `docs/fm_reception_r9_hvac_branch.png`
- `docs/fm_reception_r9_hvac_line.png`
- `docs/fm_reception_r9_hvac_detail.png`

Scripts:

- `scripts/fm/fm_reception_r9_hvac.py`
- `scripts/fm/fm_reception_r9_hvac_render.py`

Backup:

- `docs/backups/FM_LEVEL1_V06_ARCH_before_reception_r9_hvac.blend`

### Limitaciones

- El ducto termina en sleeve/fire damper; **no conecta físicamente con el ramal del corredor**.
- No hay red de retorno; solo suministro.
- El tramo oeste queda dentro del soffit del mostrador.
- Metal nuevo limpio; el desgaste se hará después.
- Sin texturas/bake, LOD ni validación Godot de este lote.
- El soporte que caía sobre la viga x −80 se movió a x −81,5 para no atravesarla.

## R9.2 — Sprinkler

### Construcción

- `REC09_SPRINKLER_RUN`: línea DN80 de **40 m**, x −110..−70, y −30, centro z 4,60, cortada de `P0B_SPRINKLER_RUN_DN80`.
- **8 cabezas** `REC09_SPRINKLER_HEAD_*` en x −106, −102, −96, −92, −86, −82, −76 y −72, con drop corto hacia z 4,20–4,30.
- **8 soportes** en x −108, −104, −98, −94, −88, −84, −78 y −74, con varilla, cleat y placa.
- **2 sleeves** `SM_SH_SLEEVE_PIPE_80` en x −110 y −70; tapas de extremo.
- No se añadieron ramales: las vigas X/Y y el HVAC impiden un grid limpio sin abrir arquitectura.
- Se retiraron 5 objetos viejos `KIT_REC01_Sprinkler_*` a `L1_RECEPTION_RETIRED_R9`, ocultos.

### Conteos y QA

- **6 objetos / 44.084 tris**.
- QA `docs/fm_reception_r9_sprinkler_qa.json`: **PASS**, 0 non-manifold, 0 degenerados, UV presente; `inside=true`; `retired_visible=[]`.
- AABB `[-110.16, -30.125, 4.475]..[-69.84, -29.875, 4.811]`.

### Renders

- `docs/fm_reception_r9_sprinkler_wide.png`
- `docs/fm_reception_r9_sprinkler_line.png`
- `docs/fm_reception_r9_sprinkler_heads.png`
- `docs/fm_reception_r9_sprinkler_sleeve.png`

Scripts:

- `scripts/fm/fm_reception_r9_sprinkler.py`
- `scripts/fm/fm_reception_r9_sprinkler_render.py`

Backup:

- `docs/backups/FM_LEVEL1_V06_ARCH_before_reception_r9_sprinkler.blend`

### Limitaciones

- Sin ramales de cobertura; la línea principal cubre el pasillo central, no las zonas laterales.
- El collarín del sleeve queda oscuro/discreto en el close-up.
- Metal limpio; desgaste diferido.
- Sin texturas/bake, LOD ni validación Godot de este lote.

## R9.3 — Bandejas

### Construcción

- `REC09_TRAY_N`: tramo hero 400×100 de **40 m**, x −110..−70, y −9,3, centro z 4,40.
- `REC09_TRAY_W`: tramo hero de **32 m**, y −40..−8, x −109,4, centro z 4,40.
- `REC09_TRAY_N_SUPPORTS`: **6 trapecios de techo** en x −106, −99, −93, −87, −81 y −75, con varillas, barra y placa.
- `REC09_TRAY_W_SUPPORTS`: **8 ménsulas de muro** en y −37, −34, −31, −25, −22, −16, −13 y −10.
- `REC09_TRAY_N_CABLES` y `REC09_TRAY_W_CABLES`: tres cables por bandeja (negro, oscuro y naranja), con bridas cada 1,5 m.
- `REC09_TRAY_CAPS`: tapas de extremo.
- **4 sleeves** `REC09_TRAY_SLEEVE_00..03` en las penetraciones de muro; los del tramo oeste rotados 90° Z.
- Se retiraron 10 objetos viejos `KIT_REC01_Tray_*` (bases N/W y 8 hangers) a `L1_RECEPTION_RETIRED_R9`, ocultos.

### Conteos y QA

- **11 objetos / 35.936 tris**.
- QA `docs/fm_reception_r9_trays_qa.json`: **PASS**, 0 non-manifold, 0 degenerados, UV presente; `inside=true`; `retired_visible=[]`.
- AABB `[-110.15, -40.15, 4.25]..[-69.85, -7.85, 5.19]`.
- Corrección aplicada: tras `bmesh.ops.bisect_plane` se rellenan los bordes con `holes_fill` y se recalculan normales; el primer run dejaba 32 aristas non-manifold por bandeja y el segundo quedó en 0.

### Renders

- `docs/fm_reception_r9_trays_wide.png`
- `docs/fm_reception_r9_trays_line.png`
- `docs/fm_reception_r9_trays_west.png`
- `docs/fm_reception_r9_trays_detail.png`

Scripts:

- `scripts/fm/fm_reception_r9_trays.py`
- `scripts/fm/fm_reception_r9_trays_render.py`

Backup:

- `docs/backups/FM_LEVEL1_V06_ARCH_before_reception_r9_trays.blend`

### Limitaciones

- Los cables quedan dentro de la bandeja y no se leen desde abajo; el detalle muestra peldaños, raíles y placa de empalme.
- La bandeja oeste queda en sombra; el render west es verificación técnica, no beauty.
- Los soportes son funcionales y más simples que el ducto hero.
- No hay choques nuevos con vigas o soffit detectados en los renders; el tramo norte pasa por debajo de las vigas.
- Metal limpio; desgaste diferido.
- Sin texturas/bake, LOD ni validación Godot de este lote.

## Siguiente

1. Pase de desgaste de Recepción: polvo, roces, pintura saltada, cromo envejecido, cintas gastadas y suelo sucio.
2. Revisar si las tres rejillas de pared de Seguridad y las rejillas de Recepción necesitan conexión de retorno; patinillos siguen pendientes por decisión del usuario.
3. LOD/colisiones/export/Godot de los lotes R9 cuando corresponda.

Sin commit.

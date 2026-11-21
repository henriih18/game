# FRECUENCIA MUERTA — P0a Biblioteca compartida y test de continuidad

**Estado:** P0a.2 COMPLETADO (2026-11-09). 56 maestros en verde; LOD1/LOD2 de puertas, portales y luminarias, colisiones y pruebas de cápsula listos. Export/Godot y P0b (routing por salas) pendientes.
**Fecha:** 2026-11-09
**Archivo:** `nexus/nivel_01/FM_LEVEL1_V06_ARCH.blend`
**Escena:** `NEXUS_L1_V06_ARCH`
**Blender:** 5.2.3 LTS
**Commit:** no.

---

> **Nota 2026-11-09 — maestros extraídos del nivel:** `L1_SHARED_HERO` ya no está en la escena `NEXUS_L1_V06_ARCH`. Se movió completo a `FM_ASSET_LIBRARY > FM_LIBRARY > LIB_CORRIDOR_HERO` y a la biblioteca standalone `assets/blender/fm_shared_hero_library.blend`. El corredor queda limpio; los maestros, LODs, colisiones y `P0_TEST_ASSEMBLY` siguen disponibles en la biblioteca. Ver `docs/FM_ASSET_LIBRARY.md`.

## 1. Resumen ejecutivo

Se creó la colección `L1_SHARED_HERO` con las subcolecciones `DOORS`, `LIGHTING`, `SERVICES` y `P0_TEST_ASSEMBLY`.

| Familia | Maestros | Tris (LOD0) | QA `game` |
|---|---:|---:|---|
| Puertas / portales | 6 | 228.428 | 6/6 pasan |
| Luminarias / emergencias | 5 | 47.056 | 5/5 pasan |
| Servicios | 45 | 180.988 | 45/45 pasan |
| **Total biblioteca** | **56** | **456.472** | **56/56** |
| P0_TEST_ASSEMBLY | 45 mallas | 123.172 | pasa con perfil `render` |

El `.blend` se guardó correctamente y se verificó en una carga headless independiente. P0a.1 reemplazó in situ 12 maestros de servicios (11 existentes + sleeve 0,6 × 0,4), actualizando también las instancias del test assembly que compartían los datablocks antiguos.

- `DOORS` 16 objetos / 10 mallas, `LIGHTING` 14 / 5, `SERVICES` 91 / 46, `P0_TEST_ASSEMBLY` 45 / 45.
- 2.330 objetos en la escena. Los servicios usan 46 mallas únicas; el test assembly usa 44 mallas instanciadas sobre 28 datablocks compartidos con los maestros.
- La sesión viva se controla por socket directo al addon (`execute_code`); el bridge MCP de OpenCode queda fuera de esta fase. El archivo en disco está guardado y verificado.

---

## 2. Convenciones

- **Escala:** 1 unidad = 1 m; escala de objetos 1, rotación aplicada.
- **Pivotes:** centro del vano a nivel de suelo (puertas); eje de bisagra (hojas); plano de pared (emergencias de pared); plano de techo (luminarias/emergencia de techo); puerto de conexión (servicios); centro del pasamuros (sleeves).
- **Nombres:** `SM_SH_<FAMILIA>_<TIPO>_<VARIANTE>`; vacíos raíz `<MAESTRO>_ROOT`; luces `LGT_<MAESTRO>`.
- **Materiales:** `M_SH_*` procedurales PBR con capa AO/suciedad, ruido de rugosidad y bump (normales procedurales, no texturas). Se conservaron materiales existentes.
- **UV:** smart projection por objeto final; solapamiento no intencional no existe, pero el gate reporta UVs solapadas por proyección automática (warning, no error). No hay texturas de imagen.
- **Geometría:** bisel 3–4 segmentos en piezas grandes, 2 en herrajes; Weighted Normal aplicado; `recalc_face_normals` final; sin escalas negativas.
- **Puertos:** cada maestro de servicio declara `fm_ports` en la raíz (JSON) con coordenadas locales y sección.

---

## 3. Catálogo

### 3.1. Puertas y portales (`DOORS`)

| Maestro | Tipo | Medida / claro | Tris | Notas |
|---|---|---|---:|---|
| `SM_SH_DOOR_SEC_SINGLE` | puerta de seguridad simple | 1,10 × 2,40 m de claro; hoja 1,08 × 2,335 | 50.856 | 3 bisagras, cerradura, manilla, barra antipánico, cierrapuertas, patilla, placa de patada, mirilla, refuerzos, anclajes, umbral, burletes |
| `SM_SH_DOOR_SEC_DOUBLE` | puerta de seguridad doble | 1,80 × 2,60 m; hojas 0,90 + 0,89 | 86.964 | hojas con bisagras, cierrapuertas, barra antipánico, mirillas, pasadores de embutir, astragalo en hoja inactiva |
| `SM_SH_DOOR_SERVICE` | puerta de servicio | 1,00 × 2,40 m; hoja 0,98 | 50.856 | misma familia, más ligera, con mirilla y herrajes |
| `SM_SH_PORTAL_4000` | portal abierto | 4,00 × 2,88 m | 11.884 | sin hoja; jambas, cabecera, umbral, cartelas, anclajes, paragolpes |
| `SM_SH_PORTAL_6000` | portal abierto | 6,00 × 2,88 m | 12.636 | sin hoja |
| `SM_SH_PORTAL_8000` | portal abierto | 8,00 × 2,88 m | 15.232 | sin hoja; montante central de 0,20 m, dos claros de 3,80 m |

**Decisión vinculante de P0a:** los vanos estructurales de 4,0 / 6,0 / 8,0 m existentes en Seguridad N/S y Recepción N se tratan como **portales abiertos**, no como puertas. Las puertas de 1,10 / 1,80 / 1,00 m son los maestros para futuros inserts y no se han colocado en los vanos existentes. La medida histórica 1,58 × 3,00 m no se usa en esta biblioteca; queda pendiente reconciliarla con la escala real de V06 antes de P0b.

### 3.2. Luminarias y emergencias (`LIGHTING`)

| Maestro | Tipo | Medidas | Tris | Luz |
|---|---|---|---:|---|
| `SM_SH_EMERGENCY_WALL_E` | emergencia de pared, orientación E | 0,20 × 0,18 × 0,34 m | 9.712 | `LGT_...` point 4 W roja |
| `SM_SH_EMERGENCY_WALL_N` | variante rotada 180° (malla enlazada) | ídem | 9.712 | point 4 W roja |
| `SM_SH_EMERGENCY_CEILING` | emergencia de techo | 0,30 × 0,30 × 0,24 m bajo techo | 9.176 | point 5 W roja |
| `SM_SH_LUMINAIRE_1500_ON` | luminaria modular 1,5 m encendida | 1,54 × 0,34 × 0,11 m | 9.228 | area 38 W cálida |
| `SM_SH_LUMINAIRE_1500_OFF` | luminaria modular apagada | ídem | 9.228 | sin nodo de luz |

Todas incluyen carcasa, lente/difusor, rejilla, tornillos, entrada de conducto, soporte y cable. La variante `_N` comparte malla con `_E` (sin duplicar geometría). El encendido/apagado se resuelve por material de difusor y nodo de luz, no por malla nueva.

### 3.3. Servicios (`SERVICES`) — 45 maestros

**HVAC rectangular 0,80 × 0,60 y 0,60 × 0,40 (P0a.1, nivel hero)**

- `SM_SH_HVAC_RECT800x600_L2000` (2 m, 10.392 tris), `..._PEN400` (0,4 m, 7.844 tris), `SM_SH_HVAC_RECT600x400_L2000` (10.392 tris), `..._PEN400` (7.844 tris).
- `SM_SH_HVAC_TEE_800x600` (principal 1,6 m, ramal inferior de 0,78 × 0,58 a 0,6 m; 8.476 tris), `SM_SH_HVAC_TRANS_800x600_600x400` (0,6 m, cuerpo hueco real; 5.500 tris), `SM_SH_HVAC_DAMPER_800x600` (0,35 m; 8.408 tris), `SM_SH_FIREDAMPER_800x600` (7.888 tris), `SM_SH_HVAC_GRILLE_600x400` (lamas reales de doble deflexión; 3.820 tris).
- Rectos con brida de 8 pernos, esquinas plegadas, anillos de refuerzo, costura longitudinal remachada, panel de acceso atornillado, etiqueta y cleats de colgado. La transición se resolvió con booleano EXACT exterior−interior.
- `SM_SH_HVAC_ELBOW_800x600` (90°, radio 0,9), `SM_SH_HVAC_ROUND_300_L2000`, `..._ELBOW`, `..._TEE` — se conservan como módulos funcionales de detalle medio; su pase hero queda para P0b/LOD.

**Bandeja de cables 0,40 × 0,10**

- `SM_SH_TRAY_400_L2000`, `..._PEN400`, `..._RISER_L1000`, `..._SPLICE`, `..._COVER_L2000`.

**Sprinklers DN80 / DN50**

- `SM_SH_SPRINK_PIPE_80_L2000`, `..._PEN400`, `SM_SH_SPRINK_PIPE_50_L2000`, `SM_SH_SPRINK_ELBOW_80`, `SM_SH_SPRINK_TEE_80_50`, `SM_SH_SPRINK_DROP_50`, `SM_SH_SPRINK_HEAD`, `SM_SH_SPRINK_VALVE_80`, `SM_SH_SPRINK_REDUCER_80_50`.

**Conducto eléctrico 25 / 40 mm**

- `SM_SH_CONDUIT_25_L2000`, `..._PEN400`, `..._ELBOW`, `SM_SH_CONDUIT_BOX_100`, `SM_SH_CONDUIT_CLAMP_25`, `SM_SH_CONDUIT_40_L2000`, `SM_SH_CONDUIT_BOX_120`.

**Pasamuros, firestop, patinillos y soportes**

- `SM_SH_SLEEVE_PIPE_80` (0,30 m, firestop intumescente, escusones, pernos).
- `SM_SH_SLEEVE_RECT_800x600`, `SM_SH_SLEEVE_RECT_600x400` (nuevo en P0a.1; 3.308 tris cada uno), `SM_SH_SLEEVE_TRAY_400` (manga + anillo de firestop).
- `SM_SH_FIRESTOP_COLLAR_80`, `SM_SH_FIREDAMPER_800x600` (compuerta cortafuego con actuador y registro).
- `SM_SH_SHAFT_ACCESS_600x1200` (panel 600 × 1200; reconstruido a 5.724 tris, puerta retrancada, bisagras, rejillas, pestillo y cerradura; QA 0).
- `SM_SH_SUPPORT_TRAPEZE_800`, `..._600`, `SM_SH_SUPPORT_TRAY_400`, `SM_SH_SUPPORT_PIPE_80`, `SM_SH_SUPPORT_CONDUIT_25`.

**Puertos de conexión (locales, metros):**

- Rectos: caras en `x=0` y `x=L`; mismas secciones y brida de entrada en `x=0`.
- Codo 90°: entrada `(0,0,0)` hacia +X; salida `(0.9,0.9,0)` hacia +Y (0,80 × 0,60).
- Tee rectangular: principal `(0,0,0)`–`(1.6,0,0)`; ramal `(0.8,0,-0.6)`.
- Transición: `(0,0,0)` 0,80 × 0,60 → `(0.6,0,0)` 0,60 × 0,40.
- Bandeja: fondo `z=0`, puertos `x=0` / `x=L`; riser de `z=0` a `z=-1,0`.
- Sprinkler DN80: `x=0` / `x=L`; tee `(0,0,0)`–`(0.8,0,0)`, ramal `(0.4,0,-0.4)`; drop de `z=0` a `-0.45`; cabeza con rosca en `z=0`.
- Conduit: `x=0` / `x=L`; codo 0,12 m; cajas de 100/120 mm.
- Soportería: origen en techo; trapecio 800 con strut a `z=-1.60`; bandeja a `z=-0.95`; clevis DN80 con tubo a `z=-1.15`; conduit a `z=-1.60`.
- Sleeves: centrados en el plano de pared, longitud 0,30 m.

---

## 4. P0_TEST_ASSEMBLY

Tramo de 5,4 m que cruza tres muros ficticios en `x=-2,0`, `x=0,0` y `x=3,2` (origen del test en `(300,0,0)`):

- HVAC 0,8 × 0,6 en tres tramos + spool de penetración + transición a 0,6 × 0,4 + spool + rejilla conectada.
- Bandeja 0,4 × 0,1 en dos tramos + spools, cubierta parcial, uniones, soportes.
- Sprinkler DN80 en dos tramos + spool, tee DN80/DN50, drop, cabeza y soportes.
- Conduit 25 en dos tramos + spools, caja de unión y soportería.
- Sleeves rectangulares de 0,8 × 0,6 y 0,6 × 0,4, de bandeja y de tubería en los muros trasero, central y frontal; firestop; soportes de techo.
- 45 mallas, 123.172 tris, todas instancias enlazadas de los maestros (misma malla, sin duplicar).
- QA perfil `render`: **pasa**, 0 errores. La última corrección fueron dos desplazamientos de 3 mm en el drop/cabeza y la alineación del tramo de entrada.

El sleeve de 0,6 × 0,4 instalado en el muro frontal (`P0_SLV_RECT_600x400_F_P0`) cierra el hueco que quedaba en P0a. El test mantiene 28 datablocks compartidos con los maestros; el resto son mallas propias de muros, soportes y uniones del montaje.

---

## 5. QA

Método: `qa_check.py` de `blender-asset-qa`, perfil `game` para maestros y `render` para el test. Los maestros se evalúan con la raíz en el origen para evitar falsos positivos numéricos de islas pequeñas; después se restaura su posición de catálogo. Resultados completos en `docs/fm_shared_p0_qa.json`; el pase específico de servicios hero está en `docs/fm_shared_p0_qa_p0a1.json`.

| Familia | Pasan | Fallos | Detalle |
|---|---:|---:|---|
| DOORS | 6/6 | 0 | — |
| LIGHTING | 5/5 | 0 | — |
| SERVICES | 45/45 | 0 | P0a.1 reconstruyó 12 maestros; shaft access y sleeves a 0 |
| P0_TEST_ASSEMBLY | 1/1 | 0 | perfil `render` |

**P0a.1:** 12/12 maestros reconstruidos pasan el QA `game` con 0 non-manifold, 0 solapes coplanares, 0 degenerados y UV presente. El shaft access quedó corregido por reconstrucción, no por desplazamiento cosmético. Los sleeves 800 × 600 y 600 × 400 comparten lenguaje (tubo, trim, collarín intumescente, pernos y etiqueta).

**Warnings aceptados/documentados:**

- N-gons en tapas de cilindros, bridas y cortes de muro del test (no deforman; warning del perfil `game`).
- UV overlap de smart projection: no hay texturas de imagen ni baking; para Godot habrá que empaquetar/bakear y rehacer UVs por familia.
- Back-to-back faces en uniones de módulos (caras ocultas; se conservan por simplicidad hasta el pase de LOD/optimización).
- `lowest point z != 0` en emergencias de pared/techo y luminarias (su pivote es el plano de montaje, no el suelo); es esperado.
- Islas pequeñas con normales invertidas en posiciones de catálogo lejanas al origen: falso positivo numérico del volumen firmado a coordenadas grandes; a origen pasan. Documentado.

---

## 5.1. P0a.2 — LOD, colisiones y cápsula

**Estado: COMPLETADO.** Script `scripts/fm/fm_shared_p0_lod.py`; colecciones `DOORS_LOD`, `LIGHTING_LOD` y `P0_COLLISION` dentro de `L1_SHARED_HERO`. Los LOD se generan con Decimate COLLAPSE, limpieza de doubles/degenerados, normales recalculadas y catálogo desplazado (puertas/portales `y=-4,0`; luminarias `y=-2,2`).

| Activo | LOD0 | LOD1 | LOD2 | Ratio LOD1/LOD2 |
|---|---:|---:|---:|---|
| `SM_SH_DOOR_SEC_DOUBLE` | 86.964 | 33.044 | 10.432 | 0,38 / 0,12 |
| `SM_SH_DOOR_SEC_SINGLE` | 50.856 | 19.324 | 6.100 | 0,38 / 0,12 |
| `SM_SH_DOOR_SERVICE` | 50.856 | 19.324 | 6.100 | 0,38 / 0,12 |
| `SM_SH_PORTAL_4000` | 11.884 | 5.346 | 1.782 | 0,45 / 0,15 |
| `SM_SH_PORTAL_6000` | 12.636 | 5.686 | 1.894 | 0,45 / 0,15 |
| `SM_SH_PORTAL_8000` | 15.232 | 6.854 | 2.284 | 0,45 / 0,15 |
| `SM_SH_EMERGENCY_CEILING` | 9.176 | 2.936 | 916 | 0,32 / 0,10 |
| `SM_SH_EMERGENCY_WALL_E` | 9.712 | 3.106 | 970 | 0,32 / 0,10 |
| `SM_SH_EMERGENCY_WALL_N` | 9.712 | 3.106 | 970 | 0,32 / 0,10 |
| `SM_SH_LUMINAIRE_1500_ON` | 9.228 | 2.952 | 922 | 0,32 / 0,10 |
| `SM_SH_LUMINAIRE_1500_OFF` | 9.228 | 2.952 | 922 | 0,32 / 0,10 |

- **QA:** 11/11 activos con LOD1/LOD2; 0 non-manifold, 0 degenerate, UV presente. `docs/fm_shared_p0_qa_p0a2.json`.
- **Colisiones:** objetos `<asset>-col` (48 tris puertas, 36 portales, 12 luces), parentados al root LOD0, `hide_render=True`, display WIRE, `fm_class=COLLISION`.
- **Cápsula:** diámetro 0,76 m, alto 1,70 m, margen 0,10 m; puertas/portales 7/7 PASS; luminarias con `fixture_protrusion <= 0,40 m` (protrusión 0,185/0,328 m).
- **Corrección de artifacts:** los LOD2 de luminaria salían con parches negros por sombreado smooth sobre geometría decimada; se dejó **LOD2 flat** (`decimate(..., smooth=(level == 1))`) y se regeneró. Los parches desaparecieron.
- **Jerarquía:** `copy_mesh_child()` usa `matrix_local` para no desanclar los hijos al desplazar el root de catálogo; verificado en puertas y luminarias.

### 5.2. Validación en Godot 4.7.2

- **GLB exportados:** `assets/models/fm/p0a_library_lod.glb` (muestra con LOD0/1/2 y colisiones; 20 mallas, 141.890 tris, 5,44 MB) y `assets/models/fm/p0a_test_assembly.glb` (45 mallas, 123.172 tris, 2,64 MB). Sin strays: 0 `PROP_Z10`.
- **Importación:** `godot --headless --path . --import`.
- **Escena de validación:** `scenes/fm/fm_p0a2_validate.tscn` + `scripts/fm/fm_p0a2_godot_validate_node.gd`.
- **Resultado `P0A2_GODOT_OK`:** library 20 mallas y **3 `CollisionShape3D`**; puerta LOD0 `1,44 × 2,48 × 0,2508 m`; luminaria LOD0 `1,56 × 0,328 × 0,366 m`; test assembly 45 mallas con AABB `(3,0465, -0,1, -2,2)` y tamaño `(300,5123, 5,09, 4,4)`; 0 strays.
- **Colisiones:** Godot genera `StaticBody3D` + `CollisionShape3D` (`ConcavePolygonShape3D`) desde los nodos `-col`. Dos proxies (`SM_SH_LUMINAIRE_1500_ON-col`, `SM_SH_PORTAL_4000-col`) permanecen como `MeshInstance3D` visible; **al instanciar la librería hay que ocultar todo `MeshInstance3D` cuyo nombre termine en `-col`**. La escena de validación lo hace (`HIDDEN_COL_PROXY`).
- **Limitación:** las colisiones importadas son trimesh; para producción conviene sustituirlas por `BoxShape3D`/cápsulas simples cuando el asset lo permita.

---

## 6. Renders

Todos a 1280 × 720, Cycles GPU, 64 spp + OIDN, AgX Medium High Contrast. Son **renders de revisión**, no el look final del juego (el estándar de entrega final pide 128 spp; este pase se hizo a 64 por tiempo).

| Archivo | Contenido | Observación |
|---|---|---|
| `docs/fm_shared_p0_doors.png` | simple, doble, servicio y portal 4 m | lineup limpio; el portal 6/8 m no entra en el encuadre |
| `docs/fm_shared_p0_lighting.png` | emergencias de pared E/N, emergencia de techo y luminarias ON/OFF | render de catálogo oscuro; las unidades de pared quedan pequeñas |
| `docs/fm_shared_p0_services.png` | kit completo en filas de catálogo | regenerado con key+fill y cámara cercana (`fm_shared_p0_render_fix.py`); legible, con los rectos hero al frente |
| `docs/fm_shared_p0_test_assembly.png` | test de continuidad en corte | regenerado; muestra muros, sleeves 0,8×0,6 y 0,6×0,4, ducto, bandeja, sprinkler y soportes; algo sobreexpuesto arriba pero legible |
| `docs/fm_p0a1_hero_fittings.png` | fila de módulos P0a.1 | rectos con bridas/pernos, panel de acceso y costuras |
| `docs/fm_p0a1_hero_macro.png` | macro del recto | refuerzos, costura longitudinal y remaches |
| `docs/fm_p0a1_hero_fittings2.png` | tee, transición, grille, damper y fire damper | la tee se giró para mostrar el ramal; la transición se ve hueca |
| `docs/fm_p0a1_shaft_hero.png` | shaft access | marco, puerta, refuerzos, rejillas, bisagras, pestillo y cerradura |
| `docs/fm_p0a2_lod_door.png` | comparativa LOD0/LOD1/LOD2 de puerta SEC_SINGLE | tres puertas completas y etiquetadas; LOD2 simplifica biseles, mirilla y manilla |
| `docs/fm_p0a2_lod_light.png` | comparativa LOD0/LOD1/LOD2 de luminaria 1500_ON | tres luminarias completas y etiquetadas; LOD2 flat sin parches negros |

El catálogo general `fm_shared_p0_services.png` y el corte `fm_shared_p0_test_assembly.png` se regeneraron con key+fill suficiente y cámara más cercana; se consideran válidos como renders de revisión.

---

## 7. Evaluación frente al listón hero

- **Puertas:** cumplen el lenguaje del checkpoint (biseles, bisagras, cerraduras, barras, cierrapuertas, mirillas, anclajes, sellos). El coste LOD0 (50k simple / 87k doble) queda resuelto con **LOD1 33k/19k** y **LOD2 10k/6k**; LOD0 se reserva para primeros planos.
- **Luminarias/emergencias:** cumplen (carcasa, lente, rejilla, tornillos, conducto, soporte, luz separada). ~9–10k tris por familia; **LOD1 ~3k y LOD2 ~0,9k**, con LOD2 flat para evitar artifacts de decimación.
- **Servicios:** el kit es coherente y modular, con puertos coincidentes y continuidad probada. Desde P0a.1, los rectos 800×600 y 600×400, la tee, la transición, el damper, el fire damper, la grille, los sleeves y el shaft access alcanzan el lenguaje hero (bridas con pernos, refuerzos, costuras, paneles de acceso, trim y firestop). El codo 800×600, el HVAC circular 300, la bandeja, los sprinklers y el conduit siguen como módulos funcionales de detalle medio y quedan para el pase hero/LOD de P0b.
- **Shaft access:** reconstruido a 5.724 tris; puerta retrancada con holgura, marco butt-jointed, refuerzos, rejillas, bisagras, pestillo y cerradura. Sin caras coplanares. Nivel mid-high: bisagras y pestillo son más simples que el checkpoint, aceptable como prop de fondo.

No se declara la biblioteca completa como hero. Se entrega como **base verificada y guardada** para P0b, con la deuda anterior explícita.

---

## 8. Archivos

**Escena guardada**
- `nexus/nivel_01/FM_LEVEL1_V06_ARCH.blend` — 27 MB; guardada tras P0a.2.
- `docs/backups/FM_LEVEL1_V06_ARCH_before_shared_p0.blend` — copia previa de 15 MB.
- `docs/backups/FM_LEVEL1_V06_ARCH_before_p0a2_purge.blend` — copia previa a la purga de mallas huérfanas (23 MB).
- `docs/backups/FM_LEVEL1_V06_ARCH_before_p0a2_lod.blend` — copia previa a la generación de LOD (23 MB).

**Scripts**
- `scripts/fm/fm_shared_p0_lib.py` — materiales, primitivas, join, UV, QA helpers.
- `scripts/fm/fm_shared_p0_doors.py`
- `scripts/fm/fm_shared_p0_lights.py`
- `scripts/fm/fm_shared_p0_services.py`
- `scripts/fm/fm_shared_p0_services_hero.py` — reconstrucción in situ P0a.1 + QA + guardado.
- `scripts/fm/fm_shared_p0_test.py`
- `scripts/fm/fm_shared_p0_lod.py` — LOD1/LOD2, colisiones, cápsula y QA.
- `scripts/fm/fm_shared_p0_render.py`, `fm_shared_p0_render_fix.py` — rig de catálogo y pase corregido de services/test.
- `scripts/fm/fm_shared_p0_lod_render.py`, `fm_shared_p0_lod_light_render.py` — comparativas LOD de puerta y luminaria.

**QA y renders**
- `docs/fm_shared_p0_qa.json`
- `docs/fm_shared_p0_qa_p0a1.json`
- `docs/fm_shared_p0_qa_p0a2.json`
- `docs/fm_shared_p0_doors.png`
- `docs/fm_shared_p0_lighting.png`
- `docs/fm_shared_p0_services.png`
- `docs/fm_shared_p0_test_assembly.png`
- `docs/fm_p0a1_hero_fittings.png`, `fm_p0a1_hero_macro.png`, `fm_p0a1_hero_fittings2.png`, `fm_p0a1_shaft_hero.png`
- `docs/fm_p0a2_lod_door.png`, `fm_p0a2_lod_light.png`

No se modificó `fotos-referencia/`. No se tocaron R1, shell, recepción, Z10, R21B/C/D ni el checkpoint. No se hizo commit.

---

## 9. Pendiente / P0b

1. Exportar GLB de prueba con las mallas visuales y `P0_COLLISION` separado; validar en Godot 4.7.2 (escala, colisiones, paso de cápsula y draw calls).
2. Bake/UV/ORM y normales OpenGL: diferidos a la pasada final de texturas; los materiales procedurales actuales están aprobados para modelado.
3. P0b: routing real de servicios por corredor, recepción, Seguridad y Z10; pase hero de codo 800×600, HVAC circular 300, bandeja, sprinklers y conduit; no desplegar estos maestros en las salas hasta cerrar el pase hero y los LODs.
4. Documentar licencias (no se introdujeron recursos externos; todo es geometría/material procedural propio).

---

## 10. Skills usadas

- `blender-core` — API 5.2, contexto, data API, verificación.
- `blender-hardsurface-modeling` — biseles, bevels 3–4, Weighted Normal, topología.
- `blender-pbr-materials` — Principled, metallic/roughness, AO/suciedad, bump.
- `blender-lighting-lookdev` — rig de estudio, cámara, encuadre.
- `blender-rendering` — Cycles GPU, denoise, AgX, 1280×720.
- `blender-asset-qa` — `qa_check.py`, perfiles game/render, iteración de z-fighting/floating.
- No se usaron skills de animación, rigging, exportación ni Godot porque P0a no incluye animar, exportar ni desplegar.

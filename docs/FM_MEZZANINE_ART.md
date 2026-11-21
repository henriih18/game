# FRECUENCIA MUERTA — Mezzanine de supervisión del Almacén (Z06)

## 1. Alcance

Verticalidad aprobada dentro de la Opción C de
`docs/FM_LEVEL1_V06_VERTICALITY_PROPOSAL.md`: una plataforma de supervisión
elevada dentro del Almacén existente, sin abrir el túnel inferior de 167 m
entre NWStair y StairsMain.

La mezzanine ocupa el hueco central del Almacén, sobre el pasillo entre la
zona de staging y los racks, y añade un segundo nivel navegable para el
jugador y la IA principal. No modifica el shell, no corta muros y no cambia
la extracción.

## 2. Composición

- Plataforma de 6 × 6 m a cota 2,60 m, losa de 0,16 m, estructura de acero
  con cuatro postes y vigas.
- Barandilla perimetral de 1,10 m con hueco en el borde sur para la rampa.
- Rampa de acceso de 1,5 m de ancho y 5,2 m de recorrido (26,6°), con
  peldaños antideslizantes, pasamanos y umbral amarillo.
- Puesto de supervisión: escritorio de madera, monitor, teclado, teléfono,
  lámpara, silla, archivador y palet con cajas/tote.
- Iluminación de trabajo: lámpara de mesa emisiva y LED bajo la plataforma;
  tres luces de sala en Godot (`Wh_Mezz_Desk`, `Wh_Mezz_Under`,
  `Wh_Mezz_Ramp`).
- Señalización: `CONTROL DE INVENTARIO` y `CARGA MAX. 250 kg` en los bordes
  de la plataforma.

Coordenadas Blender: plataforma x 87,6..93,6 / y 27,6..33,6; rampa y 22,4..27,6.
En Godot (z = −y): plataforma z −33,6..−27,6; rampa z −27,6..−22,4.

## 3. Archivos

- `scripts/fm/fm_warehouse_build.py` — función `mezzanine()` y llamada en
  `build()`.
- `assets/models/fm/warehouse_art.glb` — GLB reexportado con 99 objetos.
- `scenes/fm/fm_blockout_warehouse_art.tscn` — tres luces de mezzanine.
- `scripts/fm/fm_warehouse_export_headless.py` — `EXPECTED_OBJECTS=99`.
- `scripts/fm/fm_level1_v06.gd` — enlace `NavLink_Mezzanine` de capa 1.
- `tests/fm_level1_v06_smoke.gd` — ruta a la plataforma a cota 2,72.
- `tests/fm_level1_v06_warehouse_shots.gd/.tscn` — cuatro vistas nuevas.

## 4. Datos técnicos

- Arte del Almacén: **99 objetos, 93.783 vértices, 151.004 tris**.
- GLB: **20.577.408 bytes**, 95 mallas / 99 nodos, 46 materiales,
  31 imágenes, **147.344 tris**, 0 cámaras, 0 luces.
- AABB Blender: min (61,8; 8,14; −0,07), max (110,0; 37,833; 5,9), dentro de
  los bounds del exportador.
- Escena: 143 mallas y 84 colliders en Warehouse; 18 luces (17 de sala +
  `Emerg_Warehouse`).
- Navegación principal: 2.009 polígonos tras la mezzanine; enlace
  `NavLink_Mezzanine` entre el final navegable de la rampa
  (88,35; 2,24; −25,90) y la plataforma (88,35; 2,99; −28,00).

## 5. QA y pruebas

- `blender-asset-qa` sobre 125 objetos (99 de arte + 14 mallas de shell sin
  techo ni puertas + 12 columnas): **PASS, 0 errores, 120 warnings**
  aceptados (UVs de textos/decales, winding de cilindros).
- Smoke: **412 PASS / 0 FAIL**. `nav_layer1_mezzanine` termina a 0,27 m del
  destino a cota 2,72.
- Gameplay: **108/0**. Full run: **49/0**. Presets: **194/0**.
  Alt routes: **73/0**.
- Perf 1280×720 con ventana: **PASS**, fps_avg 482,9, fps_min 150,2,
  p1 198,2, p99 5,05 ms, 0 frames por encima de 16,7 ms.
  Escena: 4.118.264 tris, 4.264 mallas, 775 materiales, 188 luces,
  1.529 colliders, nav 2.009 + 8 polígonos, 0 huérfanos.

## 6. Limitaciones conocidas

- El último tramo de la rampa queda por debajo del perfil de 2,20 m del
  agente principal (el techo de la plataforma lo cubre), por lo que el
  navmesh no encadena rampa y plataforma. Se resolvió con un
  `NavigationLink3D` de capa 1, coherente con los enlaces de puerta ya
  existentes; el jugador sube la rampa de forma normal.
- El reverso del rótulo `CONTROL DE INVENTARIO` se ve espejado desde el
  nivel inferior. Es una limitación visual menor del texto como malla.
- La cara inferior de la plataforma queda deliberadamente oscura; el LED
  de trabajo marca el puesto sin iluminar todo el hueco.
- La mezzanine no añade objetos recuperables ni objetivos propios; su valor
  es de verticalidad, lectura del Almacén y cobertura del Vigilante.

## 7. Skills utilizadas

- `blender-core`: API 5.2, data API, escalas y verificación.
- `blender-hardsurface-modeling`: estructura, rampa, barandilla y peldaños.
- `blender-pbr-materials`: materiales reutilizados y emisivos.
- `blender-lighting-lookdev`: luces de trabajo y lectura del conjunto.
- `blender-asset-qa`: QA de z-fighting, flotantes, normales y UVs.
- `blender-game-optimization`: presupuesto y coste de la plataforma.
- `blender-export-pipelines`: export GLB y checklist de Godot.
- `blender-scene-setup`: colección, nombres y escala.
- `level-design`: métricas de rampa, cobertura y verticalidad.
- `scenario-godot-3d-world`: colisión, navmesh y capturas en Godot.
- `game-ai`: impacto del segundo nivel en patrulla y persecución.

No se usaron `blender-texture-baking` ni `blender-rendering`: no hubo
horneado ni render en Blender para esta entrega.

## 8. Backups

- Pre-mezzanine: `docs/backups/FM_MEZZANINE_before_2026-11-16/`.
- Post-mezzanine: `docs/backups/FM_MEZZANINE_after_2026-11-16/`.

## 9. Siguiente paso

Pase visual global (niebla, color grading y transiciones), optimización
medida de texturas/materiales/LOD y commit solo cuando el usuario lo
autorice.

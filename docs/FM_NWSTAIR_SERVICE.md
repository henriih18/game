# FRECUENCIA MUERTA — Sala técnica NWStair

Fecha: 2026-11-16
Rama: `frecuencia-muerta` · HEAD `287b101` · sin commit

## 1. Alcance

Opción B de `docs/FM_LEVEL1_V06_VERTICALITY_PROPOSAL.md`: se cerró el fondo de
saco de la meseta inferior de NWStair con un espolón corto y una sala técnica
de 8×6 m a cota −4,5. No se construyó el túnel inferior de ≈167 m.

La sala se modeló con el estándar de realismo de `AGENTS.md` §20 y §48.2:
proporciones reales, biseles de 2–3 segmentos, uniones y tornillería,
materiales PBR reutilizados y QA de malla sin errores. No se añadieron
objetos narrativos (cadáveres, sangre, notas ni escenas preparadas).

## 2. Composición

- **Arquitectura:** losa de 8,4×6,4 m, muros de hormigón de 2,6 m, techo con
  tres vigas, pilastras, panelado pintado, remate de acero, zócalo de goma y
  marco de puerta con hoja abierta, bisagras y manilla. Espolón de 2 m que
  conecta con la meseta de NWStair.
- **Bombas:** dos bombas centrífugas sobre plintos, con motor, aletas, caja de
  bornas, acoplamiento, guarda, voluta, bridas, aspiración, descarga, válvulas
  y manómetros. Cabeceras de agua y vapor con bridas, soportes y etiquetas.
- **Eléctrico:** tres armarios con puertas, bisagras, pestillos, filas de
  breakers y etiquetas; bandeja de cables con travesaños, tres cables y
  soportes; conduits y cuadro de control.
- **Taller:** banco de 2 m con tablero de madera, estructura de acero,
  cajones, tornillo de banco, panel perforado, herramientas y lámpara.
- **Servicios:** extractor de pared, rejilla de impulsión, desagüe, extintor
  con soporte, líneas de suelo y flecha de salida.
- **Señalización funcional:** `SALA TECNICA`, `SALIDA`, `NW-01`,
  `NO BLOQUEAR`, `RIESGO ELECTRICO`, etiquetas de agua y vapor.

## 3. Archivos

- `scripts/fm/fm_nwstair_service_build.py` — build idempotente, colección
  `L1_ART_NWSTAIR_SERVICE`.
- `scripts/fm/fm_nwstair_service_export_headless.py` — export validado.
- `assets/models/fm/nwstair_service_art.glb`.
- `docs/fm_nwstair_service_art_export.json`.
- `scenes/fm/fm_alternate_routes.tscn` — `NwStairServiceArt` + 5 luces.
- `scripts/fm/fm_level1_v06.gd` — `ALT_ROUTES_BOUNDS` ampliado.
- `tests/fm_level1_v06_nwstair_shots.gd/.tscn`.
- 21 texturas extraídas `assets/models/fm/nwstair_service_art_*.png` con
  `process/size_limit=1024`.

## 4. Datos técnicos

| Dato | Valor |
|---|---:|
| Objetos de arte | 17 |
| Vértices | 44.191 |
| Triángulos | 62.978 |
| GLB | 6.593.560 bytes |
| Mallas / nodos GLB | 17 / 17 |
| Materiales | 20 |
| Imágenes | 21 |
| Cámaras / luces en GLB | 0 / 0 |
| AABB Blender | (−76,3, 59,825, −4,701) … (−67,7, 70,8, −1,7) |
| Luces de sala | 5 (`Alt_NWS_01..03`, `Alt_NWS_Work`, `Alt_NWS_Emerg`) |
| Colliders nuevos en rutas Alt | 5 (total 91) |

## 5. QA

- Arte aislado: `qa_check` profile render, eps 0,002, tol 0,08,
  `no_modifiers`, max_tris 300.000 → **PASS, 0 errores, 49 warnings**
  aceptados (UVs de textos, winding de cilindros).
- Arte + shell NWStair (`SM_L1_Alt_NWStair_*` + `SM_L1_Shell_N`), 54 objetos:
  **PASS, 0 errores, 92 warnings**.
- Se corrigieron z-fighting de bridas, válvulas, vigas, bandeja, panel
  perforado, marco y bisagras. El muro sur se abrió de verdad: antes era una
  caja maciza y la puerta era decorativa.
- El build y la QA pesada se ejecutaron en **headless** porque la GUI de
  Blender se cerraba durante este rebuild.

## 6. Integración y pruebas

`NwStairServiceArt` es hijo de `AlternateRoutesSector` en
`scenes/fm/fm_alternate_routes.tscn`. `ALT_ROUTES_BOUNDS` pasa a
`AABB(Vector3(-96.25,-4.8,-70.8), Vector3(202.0,10.8,103.55))`.

| Prueba | Resultado |
|---|---|
| Smoke | **412 PASS / 0 FAIL** |
| Alt routes | **73 PASS / 0 FAIL** |
| Gameplay | **108 PASS / 0 FAIL** |
| Full run | **49 PASS / 0 FAIL** |
| Presets | **194 PASS / 0 FAIL** |
| Perf 1280×720 | **PASS** |

Perf tras la integración: **474,4 fps medios**, mínimo 148,7, p1 232,5,
p99 4,30 ms, 0 frames sobre 16,7 ms. VRAM de texturas 919,7 MB (la sala añade
~61 MB aun con las texturas a 1K; sigue por debajo del máximo previo de
1.154,6 MB).

## 7. Capturas

`/tmp/opencode/nws_godot_{access,door,pumps,electrical,workbench,overview}.png`
y contact sheet `/tmp/opencode/nws_godot_contact.png`. Revisión: acceso con
rótulo y franjas, puerta interior con SALIDA, bombas con bridas y válvulas,
cuadros eléctricos, banco con lámpara y visión general de la sala.

## 8. Limitaciones

- Sala pequeña y de servicio: no tiene LOD propio ni decoración narrativa.
- Materiales PBR reutilizados; las texturas del GLB van a 1K.
- La iluminación es de emergencia y de trabajo, deliberadamente desigual.
- La puerta queda abierta; no se implementó interacción de puerta.

## 9. Skills usadas

`blender-core`, `blender-hardsurface-modeling`, `blender-pbr-materials`,
`blender-asset-qa`, `blender-export-pipelines`, `blender-game-optimization`,
`blender-scene-setup`, `level-design`, `scenario-godot-3d-world`,
`writing-plans`.

No se usaron `blender-texturing`, `blender-texture-baking`,
`blender-lighting-lookdev`, `blender-rendering` ni `blender-animation`: no se
autoriaron texturas nuevas, no se horneó, y las capturas se hicieron en Godot.

## 10. Siguiente paso

Revisión final con el usuario y commit cuando lo autorice. Si otra plataforma
exige menos presupuesto, modelar LOD1/LOD2 autorados desde el source; no
decimar el LOD0.

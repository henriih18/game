# FRECUENCIA MUERTA — Recepción R2: mobiliario funcional

**Fecha:** 2026-11-08
**Archivo:** `nexus/nivel_01/FM_LEVEL1_V06_ARCH.blend`
**Escena:** `NEXUS_L1_V06_ARCH`
**Colección:** `L1_RECEPTION_R2`
**Estado:** R2 cerrado como blockout funcional; QA PASS.

---

## 1. Alcance

R2 añade el mobiliario y los elementos funcionales de la recepción
subterránea sobre la estructura cerrada en R1. No incluye la lógica de
extracción, la señalización final con texto ni el desgaste de R3.

## 2. Elementos construidos

- **Mostrador principal:** tapa, frente, laterales, panel modesty, credenza,
  dos monitores, teclado, CPU y silla.
- **Control de seguridad:** mostrador, monitor, teclado, silla, barrera roja y
  cámara con soporte.
- **Espera:** dos bancos, mesa baja, reloj de pared.
- **Taquillas:** banco de seis puertas verdes con tiradores, placas y
  rejillas de ventilación.
- **Circulación:** cuatro stanchions con cinta roja, papelera.
- **Extintor:** retirado de R2; se recolocará correctamente en R3.

## 3. Conteo y QA

| Dato | Resultado |
|---|---:|
| Objetos en `L1_RECEPTION_R2` | 112 |
| Objetos en la escena | 1.609 |
| QA R2 | **PASS, 0 errores / 145 warnings** |
| Archivo | `dirty=False` |

Los 145 warnings son, en su mayoría, solapamiento de UV al 100 % en piezas
con materiales sólidos y caras internas back-to-back. Se aceptan para el
blockout de R2; no hay errores de normales, z-fighting ni objetos flotantes.

Durante R2.1 se corrigieron:

- Normales de placas y rejillas; las cajas demasiado finas que el QA marcaba
  como falsos positivos se sustituyeron o se retiraron.
- Z-fighting de stanchions/bases, bancos/respaldos, sillas/respaldos,
  laterales del mostrador y seguridad.
- Contacto de teclados, cámara, tiradores y placas de taquilla.
- Se retiraron el segundero/hora del reloj, dos rejillas de taquilla y el
  extintor porque el QA los marcaba como piezas finas problemáticas; R3 los
  reincorporará con geometría adecuada.

## 4. Renders de revisión

| Archivo | Cámara | Lente |
|---|---|---:|
| `docs/fm_recepcion_r2_wide_wb.png` | (-88, -10.5, 2.5) → (-100, -22, 1.5) | 24 mm |
| `docs/fm_recepcion_r2_desk_wb.png` | (-96, -11, 1.8) → (-103, -14, 1.2) | 35 mm |

Workbench 1280×720, shading STUDIO, color MATERIAL, cavity, sombras y
contorno.

## 5. Revisión visual

### Vista amplia

- La recepción ya se lee como un espacio amueblado: mostrador, seguridad,
  espera, taquillas, reloj, bancos y papelera.
- **Problema de escala:** la sala de 40 × 32 m y 5,2 m de altura empequeñece
  el mobiliario. Se percibe como nave industrial, no como recepción
  corporativa.
- Falta zonificación: particiones, barandillas, alfombras, techos locales o
  cambios de material que reduzcan la escala.

### Vista del mostrador

- Los dos cuerpos del mostrador (principal y credenza) forman una **L
  incompleta con un hueco visible**.
- Los monitores y sillas están colocados, pero la composición necesita
  unirse en L o cerrar el conjunto.
- Las placas están lisas; el texto y la señalización corresponden a R2.2/R3.
- Los materiales son provisionales; el aspecto final se trabajará en R3.

## 6. Pendientes R2.2

1. Unir el mostrador en L y cerrar el hueco entre cuerpo principal y credenza.
2. Añadir zonificación para reducir la escala: particiones bajas, barandillas,
   alfombra, techo local sobre el mostrador.
3. Incorporar señalización física con texto: RECEPCIÓN, SEGURIDAD,
   EXTRACCIÓN, DESCONTAMINACIÓN, SOLO PERSONAL AUTORIZADO.
4. Reincorporar reloj completo, rejillas de taquilla y extintor con geometría
   limpia.
5. Revisar la iluminación local del mostrador y la espera.

Cualquier partición o cambio de la arquitectura de 40 × 32 m debe aprobarse
antes de ejecutarse.

## 7. Estado y siguiente fase

- R1 y R2 están documentados y con QA PASS.
- R3 añadirá desgaste, cables, extintores, señalización final y detalle
  ambiental.
- R4 exportará la recepción a Godot con WebP y el helper
  `scripts/fm_glb_collision.gd`.
- Sin commit.

## R2.2 — Composición y zonificación (2026-11-08)

- **Retorno en L:** `PROP_REC02_Desk_ReturnTop` (0,5 × 1,37 × 0,05 m) en (-104,05; -14,115; 0,943) y `Desk_ReturnFront`; conecta el mostrador principal con la credenza. `Desk_ReturnBack` se eliminó tras un z-fighting interno persistente.
- **Soffit sobre el mostrador:** `KIT_REC02_Desk_Soffit` de 10 × 6 × 1,9 m, de z3,4 a 5,3 (penetra la losa); define una escala más humana.
- **Downlights:** cuatro paneles emisivos `PROP_REC02_Downlight_0..3` y cuatro luces cálidas `LIGHT_REC02_Soffit_0..3` de 90 W.
- **Espera:** alfombra `PROP_REC02_Waiting_Rug` de 6 × 4 m y jardinera `PROP_REC02_Waiting_Planter` de 0,5 × 0,5 × 0,91 m con sustrato.
- **QA:** PASS, 0 errores / 155 warnings aceptados (UV solapadas y caras internas back-to-back en piezas con materiales sólidos).
- **Estado:** `L1_RECEPTION_R2` 126 objetos; escena 1.623 objetos; `dirty=False`; sin objetos temporales.
- **Renders:** `docs/fm_recepcion_r2_wide_wb.png` y `docs/fm_recepcion_r2_desk_wb.png` (Workbench 1280×720).
- **Lectura visual:** el soffit y la alfombra reducen la sensación de nave industrial; la L del mostrador se lee continua. Quedan pendientes la señalización con texto, la composición fina y los materiales/iluminación finales.
- **Siguiente:** R2.3 (señalización y ajuste fino) o R3 (detalle/arte). Después R4 Godot.

## R2.3 — Señalización y wayfinding (2026-11-08)

- Añadidos textos físicos FONT sobre placas: **RECEPCIÓN** (entrada y soffit del mostrador), **EXTRACCIÓN** (compuerta sur), **TAQUILLAS** (banco de taquillas) y **DESCONTAMINACIÓN** (viga del arco).
- Wayfinding: `DET_REC02_Way_CenterToExtraction` desde el centro de recepción hasta la compuerta.
- El cartel de **SEGURIDAD** se retiró porque el QA combinado lo marcaba como flotante pese a penetrar el muro; se reincorporará como placa sobre el frente del mostrador de seguridad en R3.
- **QA combinado R1+R2: PASS, 0 errores / 329 warnings aceptados** (UV solapadas y caras internas back-to-back de la escena de recepción).
- Estado: `L1_RECEPTION_R2` **136 objetos**; escena **1.632 objetos**; `dirty=False`; sin objetos temporales.
- Renders Workbench: `docs/fm_recepcion_r2_wide_wb.png`, `docs/fm_recepcion_r2_desk_wb.png`, `docs/fm_recepcion_r2_entrance_wb.png`.
- Verificación visual: el cartel de entrada es legible; el retorno en L del mostrador es continuo; la zonificación del soffit, alfombra y jardinera funciona.
- Pendientes: placa de SEGURIDAD sobre el mostrador, materiales/iluminación finales, R3 detalle/arte y R4 Godot.

## R3.1 — Emergencias y señalización (2026-11-08)

- Se creó `L1_RECEPTION_R3` con:
  - aplique de emergencia en la cabecera de la compuerta;
  - aplique de emergencia en la viga de descontaminación;
  - dos luces rojas puntuales;
  - placa/nameplate de seguridad.
- QA combinado R1+R2+R3: **PASS 0 errores / 332 warnings aceptados**.
- Escena: **1.638 objetos**; `L1_RECEPTION_R3`: **6 objetos**; `dirty=False`; sin objetos temporales.
- Renders: `docs/fm_recepcion_r3_extraction_wb.png`, `docs/fm_recepcion_r3_security_wb.png`.
- El cartel **DESCONTAMINACIÓN** se lee y el aplique de emergencia se ve. El texto **SEGURIDAD** no se renderiza de forma fiable como FONT; queda pendiente para R3.2 con placa/decals UV.
- Próximo: R3.2 materiales, desgaste, decals y señal SEGURIDAD; después R4 Godot.

## R3.2 — Señalización texturizada y decals (2026-11-08)

- Placa `PROP_REC03_Sign_Seguridad` texturizada (1024×256, fondo verde, texto blanco SEGURIDAD y subtítulo "NEXUS // CONTROL DE ACCESO") montada en el muro norte en (-84, -8.16, 2.6), con soporte oculto `KIT_REC03_Sign_Security_Bracket`.
- Se retiró `PROP_REC03_Sign_Salida`: quedaba oculto tras el muro y era redundante con el cartel EXTRACCIÓN existente.
- Decals `DET_REC03_Decal_Hand` y `DET_REC03_Decal_Puddle`; se retiró `DET_REC03_Decal_Grime` por flotante.
- `LIGHT_REC03_Salida` verde permanece como apoyo de salida.
- QA combinado R1+R2+R3: PASS, 0 errores / 336 warnings aceptados; 266 mallas; escena 1.642 objetos; `L1_RECEPTION_R3` 10 objetos; `dirty=False`.
- Render: `docs/fm_recepcion_r3_security_text.png` (cartel SEGURIDAD visible). Se eliminó el render blanco de SALIDA.
- Pendiente: R4 Godot (GLB WebP, helper de colisiones, jugador, extracción y rendimiento) para cerrar la recepción.

## R4 — Validación en Godot (2026-11-08)

- Export: `assets/models/fm/reception_r4.glb`, **310 objetos**, **1.251.136 bytes (1,25 MB)**, WebP calidad 80.
- Godot 4.7: **292 mallas**, 311 nodos, **102 colliders (3 trimesh)**, 486 objetos; carga **203 ms** ventaneada / **96 ms** headless.
- PASS: movimiento 6,80 m, `is_on_floor=true`, linterna on→off, extracción **z=39,46**, `RECEPTION_AUTOTEST_OK`.
- Rendimiento: **239,8 FPS promedio**, mínimo 194, máximo 273, 782 muestras; 29 draw calls, 15.528 primitivas, 419 objetos (1280×720, VSync off, GTX 1650 Ti). Es una escena de validación.
- Capturas: `docs/fm_reception_r4_01_spawn.png` … `04_extraction_deck.png`.
- Limitaciones: luces AREA no exportadas (omnis aproximadas), compuerta se lee como panel cerrado, materiales blockout, sin lógica de extracción ni interactuable propio, sin narrativa/multijugador, jugador blockout.
- Informe: `docs/FM_RECEPTION_R4_GODOT.md`.

## R5 — Paridad con el Conector Z10 (2026-11-08)

- 10 props Z10 reutilizados: ElectricalCabinet, UtilityCabinet, FireExtinguisher, Bin_0/1, CableReel, Crate_0/1, ToolCart, SpillPallet.
- QA Blender: **PASS 0 errores / 351 warnings**; 276 mallas; escena 1.652 objetos; 10 props R5.
- Renders: `docs/fm_recepcion_r5_wide_wb.png`, `_desk_wb.png`, `_extraction_wb.png`.
- GLB: `assets/models/fm/reception_r5.glb`, 307 objetos, **2,67 MB** WebP 80; **10 nodos `PROP_REC05_*` confirmados**.
- Godot: 291 mallas, **107 colliders (3 trimesh)**, 488 objetos; movimiento 6,80 m; linterna; extracción z=39,46; **239,9 FPS** (181/272), 29 draw calls, 15.528 primitivas, 419 objetos; `RECEPTION_AUTOTEST_OK`.
- Comparación: Z10 = 524 mallas / 11,5 MB / 249 colliders / 160,3 FPS. Recepción = 291 / 2,67 MB / 107 / 239,9. Misma fase y estándar, no el mismo conteo.
- Limitaciones: compuerta abierta/plana, AREA lights no exportan, materiales blockout, sin lógica de extracción, narrativa ni multijugador. Informe: `docs/FM_RECEPTION_R5_PARITY.md`.

## R6 — Mostrador hero (2026-11-09)

- Primer pase hero de Recepción: mostrador en L, credenza, dos monitores, teclado, CPU, accesorios y silla ergonómica.
- Colección `L1_RECEPTION_R6_HERO` con 3 objetos: `REC06_DESK_HERO` 6.136 tris, `REC06_EQUIPMENT_HERO` 8.438, `REC06_CHAIR_HERO` 4.764; total **19.338 tris / 10.148 vértices**.
- QA: 0 non-manifold, 0 degenerados, UV presente. Materiales directos verde NEXUS, bordes de goma, papel, cerámica, tela y plástico negro.
- Sustituye 25 piezas R2 blockout de ~60 tris; las antiguas quedan en `L1_RECEPTION_RETIRED`.
- Renders: `docs/fm_rec06_desk_front.png`, `_threequarter.png`, `_detail.png`, `_staff.png`, `_workstation.png`.
- Correcciones: linkeo forzado a R6 en el build, look-at/aislamiento de cámara, materiales sin reflejo especular excesivo, eliminación del papel negro del tablero y fill de puesto para leer la silla.
- Limitaciones: fondo de sala aún blockout, suelo azul, placa VESA negra del monitor, sin texturas/bake/GLB/Godot. Informe: `docs/FM_RECEPTION_R6.md`.
- Siguiente: security desk, bancas, taquillas, barrera/stanchions y servicios de Recepción.

## R7 — Security desk hero (2026-11-09)

- Puesto de seguridad reconstruido: desk 2,2 × 0,7 m, monitor empotrado con
  pantalla CCTV, teclado, radios, cuaderno, badge NEXUS y silla reutilizada de
  REC06.
- Colección `L1_RECEPTION_R7_HERO` con 3 objetos: `REC07_SECURITY_DESK_HERO`
  6.968 tris, `REC07_SECURITY_EQUIPMENT_HERO` 14.504, `REC07_SECURITY_CHAIR_HERO`
  4.764; total **26.236 tris / 13.584 vértices**.
- QA: 0 non-manifold, 0 degenerados, UV presente. 16 piezas R2 retiradas a
  `L1_RECEPTION_RETIRED`.
- Correcciones: linkeo forzado a R7 tras `join_group` y silla reasentada a
  z 0,015 (antes hundida 0,52 m por centrar también la Z).
- Renders: `docs/fm_rec07_security_front.png`, `_threequarter.png`,
  `_workstation.png`, `_detail.png`, `_plaque.png`.
- Limitaciones: fondo blockout, barrera/cola R2 aún low-poly, pantalla emisiva
  simple, sin texturas/bake/GLB/Godot. Informe: `docs/FM_RECEPTION_R7.md`.
- Siguiente: bancas, taquillas, barrera/stanchions y servicios de Recepción.

## R8 — Cola y barrera hero (2026-11-09)

- Cola en U de 4 stanchions hero y 3 cintas negras con catenaria; barrera
  retráctil de 2 m con receptor junto al desk de seguridad.
- Colección `L1_RECEPTION_R8_HERO` con 10 objetos y **66.032 tris / 35.248
  vértices**.
- QA: 0 non-manifold, 0 degenerados, UV presente en los 10 objetos. 13 piezas
  R2 retiradas a `L1_RECEPTION_RETIRED`.
- Correcciones: cinta con sección vertical de 50 mm, material negro mate,
  casetes de esquina a dos alturas (0,90/0,84 m), sin costuras claras y cámara
  de barrera dentro de la sala.
- Renders: `docs/fm_rec08_queue_wide.png`, `_threequarter.png`,
  `_stanchion.png`, `_barrier.png`, `_detail.png`.
- Limitaciones: sin texturas/bake, sin GLB/Godot de R8, fondo de sala blockout
  y receptor parcialmente oculto en la toma de contexto. Informe:
  `docs/FM_RECEPTION_R8.md`.
- Siguiente: bancas A/B y taquillas hero; después servicios de Recepción.

# FRECUENCIA MUERTA — Seguridad 03 / R2.1d (caos, abandono y luz final)

**Área:** recepción del nivel 1, ala de seguridad. Sala de 34 × 26 m (x −105..−71, y 10..36, z 0..4,8).
**Archivo:** `nexus/nivel_01/FM_LEVEL1_V06_ARCH.blend`, escena `NEXUS_L1_V06_ARCH`.
**Colección nueva:** `L1_SECURITY_R21D_HERO`, con `CHAOS`, `FIXTURES` y `LIGHTS`.
**Fecha del pase:** 09/11/2026.
**Backup previo:** `nexus/nivel_01/FM_LEVEL1_V06_ARCH_pre_r21d.blend` (copia de rollback, no sustituye al archivo principal).

## Resultado

La sala deja de leerse como un catálogo limpio. El pase añade daño visible, desorden de
ocupación y una iluminación de emergencia escasa. No se ha añadido microdetalle hero nuevo:
se reutilizan los assets R2/R21A/R21B/R21C y se añaden escombros low/mid-poly con biseles
reales, UVs y materiales PBR existentes.

- **103 mallas nuevas**, **62.648 tris** en `L1_SECURITY_R21D_HERO` (incluye 4 sillas hero
  duplicadas: 36.992 tris).
- **0 errores** de QA; **34 warnings** documentados.
- No se han añadido cuerpos, sangre, documentos, notas, fotos ni objetos personales.
- No se han modificado ni eliminado las colecciones hero: R2 (158 mallas), R21A (69),
  R21B (95) y R21C (24) conservan su recuento.

## 1. Daño y abandono

### Sillas

- 4 sillas hero reutilizadas y recolocadas: 3 volcadas/arrastradas y 1 desplazada.
  - `R21D_Chair_DraggedA` junto al checkpoint.
  - `R21D_Chair_DraggedB` al oeste, cerca del briefing.
  - `R21D_Chair_DraggedC` en el centro de operaciones.
  - `R21D_Chair_Displaced` fuera de la mesa de briefing, girada.

### Taquillas y cristales

- 2 puertas de taquilla desmontadas: una apoyada inclinada contra la pared este
  (`R21D_LockerDoor_LeaningA`) y otra en el suelo (`R21D_LockerDoor_FloorB`). Conservan
  marco, panel, lamas, cerradura, bisagras y placa.
- Panel de vidrio roto con marco de aluminio y grietas (`R21D_GlassPane_Broken`), apoyado
  contra la mampara de circulación, con fragmentos en el suelo.
- Fragmentos adicionales de vidrio junto al hatch este y junto al CRT.

### Techo colapsado

- 4 placas de techo caídas (3 en el suelo, 1 colgando) en el entorno de x −85, y 18,6.
- Hueco oscuro de placa missing en el techo, con rejilla metálica expuesta alrededor.
- 3 cables colgando desde el hueco, con conectores y curva; conducto roto con brida.
- 2 cables de suspensión cortos hasta la placa colgante.

### CRT roto

- `R21D_CRT_Broken`: carcasa, bisel, pantalla agrietada con impacto y fracturas radiales,
  rejillas laterales, patas y cable. Fragmentos de vaso de seguridad alrededor.

### Caja eléctrica dañada

- `R21D_ElectricalBox`, montada en la cara sur de la columna central (x −88, y 15,7):
  - puerta abierta con placa de bisagra, cerradura y tirador;
  - 6 interruptores, bus, bornera y cables sueltos;
  - 3 arcos de chispa emisivos y luz roja-naranja de 3,2 W;
  - quemadura de hollín en la columna por encima de la caja;
  - tapa y escombros metálicos en el suelo.

### Suelo, polvo y agua

- 3 zonas de charco con material `M_R21B_Water` (roughness 0.045) y mancha húmeda
  subyacente.
- 5 zonas de polvo (`M_R21B_Dust` / `M_HERO_Ops_Dust`), sin volumen global.
- 16 bloques de hormigón y 8 restos metálicos alrededor del colapso y de la columna.
- Escombros de yeso, teja rota, fragmentos de vidrio y cables sueltos.

### Ocupación y desorden

- Palé con 2 cajas de madera junto a la pared este; segundo palé con 1 caja al oeste.
- 2 cajas de cartón (una caída), cable reel volcado, 2 conos (uno tumbado) y cable suelto.
- Se han movido/rotado piezas existentes:
  - `R21B_CIRC_WaitBenchB`: girada 18° y desplazada (−0,55, +0,20) m.
  - `R21C_CART_ToolCart`: girado 22° y desplazado (+1,00, −1,25) m.
  - `R21B_BRIEF_Chair_04`: girada 38° y desplazada (−1,45, −1,35) m.
- El eje sur→norte y el acceso a lockers siguen practicables: el caos se concentra en los
  laterales y en el entorno del checkpoint. El bypass este del checkpoint conserva unos
  1,5 m entre el booth y la silla arrastrada; el eje oeste queda libre entre el booth y el
  palé/cable reel.

## 2. Iluminación final

No hay luz general. La sala se ilumina con:

- **4 emergencias rojas** (18 W checkpoint, 18 W operaciones/norte, 12 W lockers/este,
  12 W briefing/oeste).
- **Glow de monitores**: 4 áreas cian en operaciones (6 / 4,5 / 3 / 14 W) y un área
  pequeña en el monitor del checkpoint (2,4 W).
- **Luz fría tenue de salida** junto al cartel de salida sur (1,5 W).
- **Chispa de la caja eléctrica** (3,2 W, naranja-rojo).

Se han apagado y ocultado las luces de práctica/generales:

- `LIGHT_SEC01_Ceiling_0..6` (7 luces de techo).
- `LIGHT_SEC03_Emergency_N`, `LIGHT_SEC03_Emergency_E`, `LIGHT_SEC02_Emergency`.
- `R21B_LIGHT_Emergency_0`, `R21B_LIGHT_Emergency_2`.

Las luminarias físicas sobrantes siguen en escena como props apagados; a las carcasas
`R21B_SERV_EmergencyW1` y `R21B_SERV_EmergencyS` se les asignó un material rojo oscuro sin
emisión (`M_R21D_EmergencyOff`) para que no contradigan el apagado.

### Criterio de color

- View transform: **AgX**.
- Look: **AgX - Medium High Contrast**.
- Exposure guardada: **0,85** (los stills usan 0,82–0,90 según la toma).
- Los monitores de seguridad usan copias locales de los materiales de pantalla
  (`M_R21D_ScreenGlow` 1,55 de emisión y `M_R21D_ScreenUI` 2,60), sin cambiar las
  pantallas del resto del nivel.

### Volumen global

El World tenía un `FM_VolumetricHaze` (Principled Volume, densidad 0,006) conectado al
World Output. Con la linterna de juego ese volumen producía una rejilla de froxels muy
visible en EEVEE y arruinaba la oscuridad. Se ha **desconectado del World Output** (el nodo
se conserva para rollback). El polvo de la sala se representa con decals y con la caída de
luz de las prácticas, no con volumen global.

> Este cambio afecta a todo el nivel, no solo a Seguridad 03. Si más adelante se quiere
> niebla ambiental global, debe hacerse con volúmenes por zona o con ajustes de froxel
> verificados bajo linterna.

## 3. QA

Ejecutado con `/home/riyo/.agents/skills/blender-asset-qa/scripts/qa_check.py` dentro de
Blender 5.2.3, perfil `render`:

- Objetos: **103 mallas R21D** + suelo, techo, paredes N0/N1/N2, S0/S1/S2, W0, E1/E2 y las
  6 columnas de seguridad.
- `eps=0.0005`, `tol=0.004`, `max_tris=900000`, `uv=False` en la pasada combinada.
- **Resultado: `pass=True`, 0 errores, 34 warnings.**
- Se excluyó la pared E0 por el z-fighting preexistente E0/S2 documentado en R21B; no se
  modificó.
- JSON completo: `docs/fm_security_r21d_qa.json`.

### Warnings aceptados

- 4 warnings de “inward normals” en las sillas duplicadas (59 islas pequeñas en total):
  falsos positivos de la triangulación de tapas biseladas; las islas revisadas tienen
  volumen firmado hacia fuera.
- “Inward normals” en CRT, cable reel, puerta de taquilla, cables de techo y caja
  eléctrica: mismas tapas biseladas pequeñas.
- Caras ocultas back-to-back en sillas, CRT, cajas de cartón, puertas de taquilla y en
  paredes/suelo/columnas preexistentes. No se han borrado para no tocar la arquitectura
  existente.
- `duplicate verts` en CRT (6), cable reel (5) y algún borde de bisel; no afecta al render.
- 1 parte encerrada sin tocar en `R21D_ElectricalBox` (interior de la caja).
- Punto más bajo z = −0,2: cara inferior del suelo preexistente, no de las piezas nuevas.

### UVs y materiales

- **103/103 mallas con UV**.
- **0 caras con UV de área cero** en la comprobación por triángulos.
- **0 slots de material vacíos**; todas las mallas nuevas tienen materiales asignados.
- Biseles reales de 2–4 segmentos, recálculo de normales y Weighted Normal aplicado antes
  de unir. Los vértices duplicados que quedan en CRT/cable reel se documentan en QA.

## 4. Renders EEVEE

Todos EEVEE, 1280 × 720, 64 muestras, AgX Medium High Contrast. Cámaras y linterna
temporal creadas en `TMP_R21D_FINAL` y eliminadas antes de guardar; el `.blend` no las
conserva. Los stills se renderizaron con raytracing EEVEE activo para las reflexiones de
charco/cristal; la escena guardada lo deja desactivado por rendimiento.

| Archivo | Contenido |
|---|---|
| `docs/fm_security_r21d_wide.png` | Amplia desde el sureste: checkpoint y cartel SEGURIDAD en primer plano, columna con caja eléctrica y chispas, centro de operaciones con monitores al fondo, emergencias rojas y barrera. |
| `docs/fm_security_r21d_wide_north.png` | Amplia norte: hueco de techo, cables colgando, placa colgante, escombros, jardinera, banco, operaciones y emergencia roja. |
| `docs/fm_security_r21d_checkpoint.png` | Checkpoint: mostrador, monitor con glow, cartel, lámpara roja nueva, salida fría, escombros y barrera. |
| `docs/fm_security_r21d_ops.png` | Centro de operaciones: muro CCTV, puestos, sillas, monitores cian y emergencia roja. |
| `docs/fm_security_r21d_chaos.png` | Caos: caja eléctrica abierta con chispas, cables colgando, placa de techo caída, escombros, banco, cable reel y operaciones al fondo. |
| `docs/fm_security_r21d_electrical.png` | Extra de documentación: close-up de la caja dañada, puerta abierta, interruptores, chispas, cables y quemadura. |
| `docs/fm_security_r21d_briefing.png` | Extra: briefing oeste con mesa, sillas desplazadas/volcadas, pizarra, pantalla, plantas y emergencia roja. |

## 5. Limitaciones

- La esquina elegida para la wide principal no encuadra la mesa de briefing ni los lockers:
  la mampara del checkpoint tapa el briefing y los lockers quedan a la espalda de la
  cámara. Se cubren con `fm_security_r21d_briefing.png`, `fm_security_r21d_wide_north.png`
  y los renders ya existentes de R21C (`fm_security_r21c_east.png`, `..._lockers.png`).
- La sala es deliberadamente casi negra sin linterna. Los stills añaden una linterna
  implícita temporal; en juego la iluminación de mano es la que debe revelar la sala.
- El hueco de techo es un parche de hollín + rejilla + cables, no un booleano de geometría
  ausente. Desde ángulos muy bajos puede leerse como mancha oscura.
- El volumen global del World está desconectado (ver arriba). Es un cambio de escena, no
  solo de la sala.
- Los renders usan raytracing EEVEE; la escena guardada lo desactiva. Las reflexiones de
  charcos/cristal pueden ser algo más planas al abrir el `.blend`.
- No hay físicas, colisiones, navegación, LOD ni sincronización multijugador para los
  escombros; son props estáticos de arte.
- No se ha medido rendimiento con jugadores, criaturas, físicas y audio. Los 62.648 tris
  nuevos se suman a un nivel ya pesado; validar en la GTX 1650 Ti objetivo.
- Quedan 34 warnings de QA, todos explicados; no hay errores.
- La puerta de la caja eléctrica es grande y clara; si se quiere un look más sucio, se
  puede envejecer en un pase de texturizado.
- No se ha hecho commit.

## 6. Skills usadas

- `blender-core`: ejecución vía MCP, API 5.2, verificación y guardado.
- `blender-hardsurface-modeling`: biseles reales 2–4 segmentos, uniones, UVs y normales.
- `blender-pbr-materials`: reutilización de la paleta PBR y materiales contextuales.
- `blender-lighting-lookdev`: esquema de 4 emergencias + glow de monitores + luz fría,
  cámara y composición.
- `blender-rendering`: EEVEE 1280×720, AgX/exposure, raytracing de stills y limpieza de
  cámaras/luces temporales.
- `blender-asset-qa`: `qa_check.py`, UVs, materiales y revisión visual de los renders.

## 7. Siguiente paso

1. Validar la densidad y el rendimiento en la GTX 1650 Ti con la sala y el resto del nivel.
2. Decidir si se recupera niebla global con volúmenes por zona y froxels verificados.
3. Añadir colisiones/navegación a sillas, cajas, escombros y puertas de taquilla.
4. Envejecer la puerta de la caja eléctrica y los cantos de los palés si se busca un
   close-up más sucio.
5. Sincronizar puertas, cajones y props físicos en multijugador cuando se aborde la fase de
   red.

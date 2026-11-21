# FRECUENCIA MUERTA — Seguridad 03 / R21C (pase hero de close-up)

**Área:** recepción del nivel 1, ala de seguridad. Sala de 34 × 26 m (x −105..−71, y 10..36, z 0..4.8).
**Archivo:** `nexus/nivel_01/FM_LEVEL1_V06_ARCH.blend`, escena `NEXUS_L1_V06_ARCH`.
**Colección nueva:** `L1_SECURITY_R21C_HERO`, con `LOCKERS`, `HATCH`, `STORAGE`, `CART` y `CHAOS`.
**Fecha del pase:** 09/11/2026.

## Estado

Seguridad 03 queda cerrada a calidad hero de close-up en los cuatro elementos que R21B había
simplificado: taquillas, ventanilla/hatch, rack de llaves + estantería y tool cart. Se añade el
caos del centro de operaciones (sillas volcadas, monitores muertos, cables colgando y escombros).

No se ha modificado ni eliminado nada de:

- `L1_SECURITY_R2_HERO` (checkpoint).
- `L1_SECURITY_R21A_HERO` y sus subcolecciones (centro de operaciones).
- `L1_SECURITY_R1`, `L1_ARCH_*`, recepción, `Z10`, `fotos-referencia/`.
- El resto de R21B (briefing, circulación, servicios, luces).

Las nueve piezas R21B sustituidas quedan **ocultas** (`hide_viewport` + `hide_render`), no
eliminadas, para permitir rollback:

`R21B_LOCK_BankA`, `R21B_LOCK_BankB`, `R21B_LOCK_KeyCabinet`, `R21B_LOCK_Shelving`,
`R21B_HATCH_ServiceCounter`, `R21B_HATCH_Shutter`, `R21B_HATCH_Sign`, `R21B_HATCH_GlassShards`,
`R21B_CHAOS_ToolCart`.

## Métricas

| Colección | Mallas | Tris |
|---|---:|---:|
| `L1_SECURITY_R21C_HERO_LOCKERS` | 2 | 190.584 |
| `L1_SECURITY_R21C_HERO_HATCH` | 7 | 28.666 |
| `L1_SECURITY_R21C_HERO_STORAGE` | 2 | 56.144 |
| `L1_SECURITY_R21C_HERO_CART` | 1 | 21.184 |
| `L1_SECURITY_R21C_HERO_CHAOS` | 12 | 27.592 |
| **Total R21C** | **24** | **324.170** |

- `R21C_LOCK_BankA` y `R21C_LOCK_BankB`: 95.292 tris cada una, 11 materiales.
- `R21C_KEYS_KeyRack`: 19.028 tris; `R21C_SHELF_Unit`: 37.116 tris; 12 materiales.
- `R21C_CART_ToolCart`: 21.184 tris, 10 materiales.
- `R21C_HATCH_WindowFrame` 3.692, `Glass` 390, `Shutter` 7.504, `Counter` 6.892,
  `Intercom` 4.220, `Sign` 5.728, `Shards` 240.

## Qué se construyó

### 1. Taquillas (`LOCKERS`)

- Dos bancos de 8 puertas (este y sur), 4,40 m de longitud, 1,98 m de altura, 0,52 m de fondo.
- Puerta real de una pieza: marco perimetral biselado, panel inferior embutido, banco de **8 lamas
  reales** por puerta, respaldo oscuro y rejillas de ventilación con profundidad.
- 3 bisagras por puerta con pasador, media nuez fija en el montante y media nuez móvil en la puerta.
- Cerradura con escudo, bombín, ranura de llave, cerradero y tirador vertical de aluminio.
- Placa de número con número tipográfico real.
- Interior completo: balda de chapa con reborde y soportes en L atornillados, barra de colgar con
  soportes, dos ganchos, bandeja de botas en dos compartimentos y espejo interior en la puerta 4.
- Puertas abiertas (1: 26°, 4: 68°, 7: 12°), puertas abolladas por deformación real del panel
  (3 y 6), óxido en cantos y una puerta oliva de reparación.
- Montantes, zócalo, pies de goma, travesaños y anclajes ocultos.

### 2. Hatch / ventanilla este (`HATCH`)

- Marco integrado en el hueco existente (1,40 × 2,20 m), con jambas, dintel, alféizar, revestimiento
  interior galvanizado y anclajes atornillados.
- Luna de vidrio de una pieza con **rotura irregular** en la esquina superior y grietas geométricas
  sobre la superficie; junquillos de goma en los cuatro bordes.
- Reja enrollable con **15 lamas reales** inclinadas, guías en C, carcasa, eje, manivela, cerradura y
  banda de aviso.
- Mostrador de acero inoxidable de 1,95 m con dos puertas, bisagras, tiradores, cerraduras, zócalo,
  rejillas de ventilación, bandeja de transacción y pasacables.
- Intercomunicador de pared con rejilla de altavoz, pulsador rojo, LED, texto y conducto con abrazaderas.
- Rótulo “SERVICIO” con marco de aluminio, texto y tornillos; fragmentos de vidrio sobre mostrador y suelo.

### 3. Rack de llaves y estantería (`STORAGE`)

- Rack abierto de 0,95 × 0,95 × 0,14 m con marco, tres baldas, refuerzos, cerradura y cabecera “LLAVES”.
- 12 ganchos con 12 llaves: anilla toroidal, paletón, dientes y etiqueta de color con código grabado
  (A/B/C/D). Sin documentos ni objetos personales.
- Estantería de 2,32 × 0,60 × 2,30 m: 4 montantes con taladros, 8 vigas, 4 baldas con reborde y
  etiquetas, pies con anclajes y arriostramiento en X.
- Contenido de equipo: 5 cascos (blanco/amarillo/verde), 4 cajas, 4 contenedores y una manguera
  enrollada. Nada narrativo.

### 4. Tool cart (`CART`)

- 0,78 × 0,54 × 0,95 m, 5 cajones con frentes, paneles embutidos, tiradores de aluminio, etiquetas
  y guías; el tercer cajón está extraído 12 cm y muestra la caja y las guías.
- 4 ruedas giratorias con horquilla, rodamiento, placa y tornillos; base, cuerpo, esquineros,
  topes de goma, barra de bloqueo con cerradura, bandeja superior con alfombrilla y organizador
  de piezas con tornillos.

### 5. Caos del centro de operaciones (`CHAOS`)

- 2 sillas de oficina volcadas adicionales (la tercera ya existía en R21A).
- 2 monitores CRT muertos: uno tumbado con pantalla agrietada hacia arriba y otro apoyado en el
  suelo; bisel, carcasa, rejillas, puertos y cable.
- 2 bajantes de cable desde el techo con placa, abrazaderas y conector; cable suelto con enchufe.
- Teja rota, 3 bloques de escombro, 3 fragmentos de vidrio y una pequeña zona de polvo.
- Colocados en el suelo libre, sin invadir los puestos hero de R21A ni la mampara de vidrio.

## QA

Ejecutada con `/home/riyo/.agents/skills/blender-asset-qa/scripts/qa_check.py` dentro de
Blender 5.2.3, perfil `render`:

- Objetos: 24 mallas R21C + suelo, techo, paredes E1/E2, N0/N1/N2, S0/S1/S2, W0 y las 6 columnas.
- `eps=0.0005`, `tol=0.004`, `max_tris=900000`, `uv=False` en la pasada combinada.
- **Resultado: `pass=True`, 0 errores, 45 warnings.**
- Se excluyó la pared E0 porque mantiene el z-fighting preexistente E0/S2 de la arquitectura
  (documentado en R21B); no se modificó.
- Warnings: 19 avisos de “inward normals” en piezas pequeñas (falsos positivos de la triangulación
  de tapas biseladas; las islas revisadas tienen volumen firmado hacia fuera), 20 avisos de caras
  ocultas back-to-back (incluye N1/N2 y S1/S2 preexistentes), 4 piezas encerradas dentro del rack
  de llaves (anillas/etiquetas), 4 avisos de vértices duplicados y 1 de punto más bajo −0,2
  (cara inferior del suelo existente).
- UVs validadas aparte: **24/24 mallas con UV**, 0 caras con UV de área cero, escala 1 y materiales
  asignados en todas las mallas.

## Renders

Todos EEVEE, 64 muestras, 1280×720. Luces y cámaras de revisión **temporales**, eliminadas antes de
guardar; el `.blend` no las conserva. Los close-ups usan DOF suave (f/2,8–4).

| Archivo | Contenido |
|---|---|
| `docs/fm_security_r21c_wide.png` | Vista amplia desde el suroeste, techo y vigas visibles, look oscuro piloto con linterna, emergencias rojas y rebote de techo. |
| `docs/fm_security_r21c_east.png` | Elevación de la pared este: estantería, botiquín, rack de llaves, Banco A completo, office nook y hatch con rótulo. Segunda vista amplia de la zona hero. |
| `docs/fm_security_r21c_lockers.png` | Close-up del Banco A: lamas, bisagras, cerraduras, puerta abierta con balda/barra/espejo, abolladuras y números. |
| `docs/fm_security_r21c_hatch.png` | Close-up de la ventanilla: luna rota, grietas, reja, mostrador, bandeja, intercom y rótulo SERVICIO. |
| `docs/fm_security_r21c_cart.png` | Close-up del tool cart: ruedas, 5 cajones, cajón extraído, tiradores, barra de bloqueo y bandeja. |
| `docs/fm_security_r21c_ops_chaos.png` | Caos del centro de operaciones: sillas volcadas, CRT muertos, cable colgando, escombros y puestos hero al fondo. |
| `docs/fm_security_r21c_storage.png` | Close-up del rack de llaves (12 llaves/etiquetas) y estantería con cascos, cajas, contenedores y manguera. |

## Circulación

- Sur → norte: puerta sur → carril oeste → puerta norte. Libre.
- Checkpoint → lockers/hatch: pasillo este libre; el Banco B vuelve a estar en la pared sur
  (x −80,6..−76,2), no en el centro de la sala.
- Centro → operaciones: puerta de vidrio libre; el caos se coloca en el suelo abierto y no bloquea
  el paso.
- No se añadió un banco/partición de relleno en el centro para no cortar el eje sur→norte; la
  densidad se resolvió con las piezas hero y el caos.

## Limitaciones

- R21C suma 324.170 tris. Es un pase de arte hero; no se han hecho LOD, occlusion culling ni
  medición de rendimiento con jugadores, criaturas y físicas. Validar en la GTX 1650 Ti objetivo.
- La luna rota es una sola pieza con corte irregular y grietas geométricas; no hay simulación de
  fractura ni fragmentos físicos.
- El lateral del tool cart es liso (el frente es el que concentra el detalle); no hay herramientas
  dentro de los cajones.
- La vista amplia del suroeste no encuadra la pared este; para eso está `fm_security_r21c_east.png`.
- El segundo sillón volcado queda parcialmente ocluido en el close-up de caos.
- Quedan 45 warnings de QA, todos explicados arriba; no hay errores.
- Sin colisiones, navegación, LOD ni sincronización multijugador; esta entrega es de arte.

## Skills usadas

`blender-core`, `blender-hardsurface-modeling`, `blender-pbr-materials` y `blender-asset-qa`.
Se aplicaron bevels reales de 2–4 segmentos, ensamblajes solapados para evitar coplanares, UVs
box-projected, weighted normals y la QA de malla del skill antes de renderizar.

## Siguiente paso

1. Colisiones y navegación de puertas, cajones, sillas, CRT y escombros.
2. Pase de rendimiento/LOD y medición en escena representativa.
3. Sincronización multijugador de puertas, cajones y objetos físicos.
4. Microdetalle de close-up: laterales del cart, legibilidad de etiquetas pequeñas y fractura de
   vidrio más rica si se requiere primer plano extremo.

## Archivo guardado

`nexus/nivel_01/FM_LEVEL1_V06_ARCH.blend` guardado con R21C y las piezas R21B sustituidas ocultas.
No se ha hecho commit.

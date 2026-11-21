# FRECUENCIA MUERTA — Nivel 1 — V06

## Blockout arquitectónico inicial

Fecha: 2026-11-05
Archivo: `nexus/nivel_01/FM_LEVEL1_V06_ARCH.blend`
Escena: `NEXUS_L1_V06_ARCH`

Este documento registra el primer blockout del rediseño arquitectónico del Nivel 1. Es una base de discusión y iteración, no el arte final ni una versión jugable.

> **Actualización 2026-11-09:** el catálogo de maestros compartidos `L1_SHARED_HERO` ya no vive en esta escena. Se movió a `FM_ASSET_LIBRARY > FM_LIBRARY > LIB_CORRIDOR_HERO` y a la biblioteca standalone `assets/blender/fm_shared_hero_library.blend`. El corredor del nivel queda limpio de puertas, luminarias, ductos y test assembly de catálogo. Ver `docs/FM_ASSET_LIBRARY.md`.

## Alcance de esta versión

- Solo arquitectura: suelos, muros, vanos, columnas, escaleras, cubiertas y señalización de zonas.
- Sin props, mobiliario, equipamiento, objetos recuperables ni decoración.
- Sin pruebas, exportación ni integración en Godot.
- Sin modificar el nivel anterior ni la librería compartida.
- Sin commit.

## Zonificación

Coordenadas en metros. X positiva al este, Y positiva al norte, Z hacia arriba. El suelo de las zonas está en Z=0; la roca base en Z=-0,20; los muros tienen 0,30 m de espesor y las cubiertas 0,20 m.

| Zona | Nombre | X | Y | Dimensiones | Altura |
|---|---|---|---|---|---|
| 01 | Recepción subterránea / extracción | -110 a -70 | -40 a -8 | 40 × 32 m | 5,2 m |
| 02 | Corredor principal | -100 a 74 | -4 a 4 | 174 × 8 m | 4,2 m |
| 03 | Seguridad / monitoreo | -105 a -71 | 10 a 36 | 34 × 26 m | 4,8 m |
| 04 | Control de acceso | -105 a -77 | 40 a 60 | 28 × 20 m | 4,5 m |
| 05 | Vestuarios | 30 a 60 | 40 a 64 | 30 × 24 m | 4,5 m |
| 06 | Almacén / suministros | 70 a 110 | 8 a 38 | 40 × 30 m | 6,0 m |
| 07 | Mantenimiento / infraestructura | 56 a 112 | -48 a -8 | 56 × 40 m | 6,0 m |
| 08 | Oficinas / administración | -30 a 15 | 30 a 70 | 45 × 40 m | 4,5 m |
| 09 | Aseo | 18 a 30 | 42 a 58 | 12 × 16 m | 4,0 m |
| 10 | Conector de servicio | 40 a 62 | 8 a 30 | 22 × 22 m | 4,2 m |
| 11 | Escaleras principales | -12 a 8 | -50 a -30 | 20 × 20 m | 7,0 m |
| 12a | Escalera de emergencia E1 | 110 a 120 | 8 a 26 | 10 × 18 m | 6,0 m |
| 12b | Escalera de emergencia E2 | 112 a 122 | -44 a -26 | 10 × 18 m | 6,0 m |

Perímetro: X -120 a 124, Y -60 a 72. Losa de roca base de 244 × 132 m.

La extracción se realiza en la **recepción subterránea del Nivel 1, en Z=0,00**. No hay recepción de superficie; es el único punto de entrega y salida.

## Circulación

- **Recepción** conecta al norte con el corredor principal mediante un vestíbulo.
- **Seguridad** se conecta al corredor y, desde su lado norte, al **Control de acceso**.
- **Oficinas** se conecta al corredor por un pasillo norte-sur.
- **Vestuarios** se conecta al corredor por un pasillo norte-sur.
- **Aseo** tiene acceso desde Oficinas y desde Vestuarios mediante un pequeño enlace.
- **Almacén** se conecta al corredor por el oeste y al **Conector de servicio** por un pasillo técnico.
- **Mantenimiento** se conecta al corredor por un vestíbulo y a la **Escalera de emergencia E2**.
- **Escaleras principales** se conectan al corredor por un pasillo sur y a **Recepción** por una esclusa de servicio independiente que, a mitad de recorrido, también enlaza con el corredor principal.
- **Escalera de emergencia E1** se conecta al Almacén.
- El **Conector de servicio** conecta el corredor con el Almacén; es una circulación técnica, no una sala de estancia.
- La extracción se realiza en la **recepción subterránea del Nivel 1 (Z=0,00)**; es el único punto de entrega y salida del nivel.

## Rutas alternas y núcleo vertical

Se añadieron siete rutas alternas para que las zonas más alejadas no dependan de un único pasillo, y una escalera de emergencia adicional en Control de acceso.

- **Esclusa Recepción–Escaleras**: túnel de arrastre de x=-70 a -12, y=-32,5 a -31,5, **1,0 m de ancho y 1,25 m de alto**, con ramal vertical x=-37,5 a -36,5, y=-31,5 a -4. Conecta **Recepción ↔ Escaleras principales** y, a mitad de camino, **↔ corredor principal**. Es una ruta exclusiva de servicio, separada del vestíbulo principal de Recepción; solo se puede recorrer agachado o a gatas.
- **Galería técnica Este** (`L1_ARCH_ALTERNATE`): túnel de arrastre de x=104,5 a 105,5, y=-8 a 8, **1,0 m de ancho y 1,25 m de alto**. Conecta **Mantenimiento ↔ Almacén** por el este. Es una ruta técnica exclusiva, no una sala de estancia.
- **Galería de ventilación Norte**: túnel de arrastre de x=-96 a -30, y=65 a 66, **1,0 m de ancho y 1,25 m de alto**, con conector x=-94,5 a -93,5, y=60 a 65. Conecta **Control de acceso ↔ Oficinas**. Su altura reducida la convierte en una ruta alternativa exclusiva, separada de la circulación principal.
- **Pasillo de servicio Vestuarios/Almacén**: túnel de arrastre de 1,0 m de ancho y 1,25 m de alto; tramo vertical x=57,5 a 58,5, y=30 a 40, y tramo horizontal x=58,75 a 70, y=35,5 a 36,5. Conecta **Conector de servicio ↔ Vestuarios ↔ Almacén** y solo se puede recorrer agachado o a gatas.
- **Escalera de emergencia 12C**: núcleo x=-77 a -67, y=40 a 60, altura 6,0 m, adosado al este de Control de acceso. Puerta en el muro este de Control de acceso (y=42 a 46), 24 peldaños descendentes de 4,5 m y meseta inferior a -4,50.

### Niveles y condición subterránea

- El Nivel 1 está completamente bajo tierra. La cota de suelo útil es **Z=0,00**; la roca base está por debajo.
- La masa de roca superior `SM_L1_Rock_Overburden` ocupa de **Z=6,50 a 9,00 m** sobre todo el perímetro. Está oculta en viewport y render para poder revisar la planta, pero documenta que el nivel no está al aire libre.
- **Escaleras principales:** descienden 4,5 m desde el Nivel 1 hasta una meseta en **Z=-4,50**, que representa el acceso al Nivel 2. El hueco está rodeado por cuatro franjas de suelo y muros de foso.
- **Escaleras de emergencia E1, E2 y 12C:** descienden 4,5 m hasta el Nivel 2 (Z=-4,50). Son salidas de emergencia hacia el nivel inferior. No hay acceso a superficie modelado; la recepción subterránea es el único punto de extracción.
- El Nivel 2 todavía no está modelado; solo existe la meseta y la reserva de hueco para continuar bajando.

## Construcción y escala

- Unidades métricas, Unit Scale 1.0.
- Suelos de 0,20 m de espesor, con la cara superior en Z=0.
- Muros de 0,30 m de espesor, con altura libre según la zona.
- Cubiertas de 0,20 m, 1 cm por debajo de la coronación de los muros para evitar caras coplanares.
- Vanos industriales de 2,6 m y 3,2 m de alto; las puertas todavía no tienen hoja.
- Columnas estructurales de 0,45 × 0,45 m en Recepción, Seguridad, Control de acceso, Vestuarios, Almacén, Mantenimiento, Oficinas y Conector de servicio.
- Escaleras de 24 peldaños, huella 0,28 m; pendientes de barandillas y mesetas definitivas. La principal y las de emergencia E1, E2 y 12C descienden 4,5 m hasta la meseta del Nivel 2.
- La losa de roca superior y la meseta inferior del Nivel 2 están documentadas, pero el Nivel 2 no se ha modelado todavía.
- Las cubiertas y la roca superior están ocultas en viewport para revisar la planta; la roca superior también se oculta en render.

## Validación de escala y circulación (2026-11-05)

Se validó el blockout con dos proxies de jugador en la colección `L1_VALIDATION` (oculta en la entrega): **1,80 m de alto × 0,56 m de diámetro** para caminar y **1,00 m × 0,56 m** para gatear. Se construyó un BVH de la arquitectura (excluyendo superficie archivada, roca superior y etiquetas de plano) y se muestrearon 12 rutas con rayos de holgura lateral, altura libre y continuidad de suelo.

| Ruta | Modo | Holgura mínima | Altura mínima | Resultado |
|---|---|---:|---:|---|
| Recepción → vestíbulo → corredor | de pie | 0,82 m | 3,02 m | PASS |
| Recepción → esclusa → escaleras | a gatas | 0,50 m | 1,23 m | PASS |
| Escaleras → corredor principal | de pie | 2,84 m | 3,02 m | PASS |
| Corredor principal oeste–este | de pie | 0,45 m | 3,97 m | PASS |
| Corredor → Mantenimiento | de pie | 2,84 m | 3,02 m | PASS |
| Corredor → pasillo Seguridad | de pie | 0,70 m | 2,18 m | PASS |
| Pasillo Seguridad → Oficinas | a gatas | 0,41 m | 1,23 m | PASS |
| Túnel Recepción–Escaleras | a gatas | 0,40 m | 1,23 m | PASS |
| Túnel Mantenimiento–Corredor | a gatas | 0,38 m | 1,23 m | PASS |
| Galería técnica Este | a gatas | 0,50 m | 1,23 m | PASS |
| Galería de ventilación Norte | a gatas | 0,50 m | 1,23 m | PASS |
| Pasillo de servicio Conector–Vestuarios–Almacén | a gatas | 0,50 m | 1,23 m | PASS |

- **12 de 12 rutas PASS.** No hay huecos de suelo en los recorridos; el suelo se mantiene continuo hasta la extracción.
- Las columnas de Recepción en (-90,-20), (-90,-32) y (-80,-32) obligan a rodearlas; las rutas validadas lo hacen y no son un defecto de la planta.
- Las cubiertas estaban ocultas en viewport y Blender no actualizaba su matriz hasta mostrarlas temporalmente; para el BVH se mostraron y después se restauró su visibilidad.
- **Escaleras:** 24 peldaños, contrahuella **0,1875 m**, huella **0,28 m**; ancho **1,60 m** en E1, E2 y 12C, y **2,60 m** en la principal. Descienden 4,50 m hasta -4,50; el primer peldaño queda a -0,1875 y el último a -4,50.
- **Auditoría:** se aplicó escala a `ANNOT_L1_ReceptionStair_Airlock` y se eliminó el slot de material vacío de `SM_L1_Bedrock`. Quedan 213 bloques huérfanos para una purga posterior.
- **La planta queda congelada para esta fase.** Cualquier cambio de dimensiones, accesos o alturas debe justificarse antes de construir el kit modular.

## Iluminación de intención

- Mundo prácticamente negro (fuerza 0,02).
- **Recepción subterránea:** áreas cálidas (320 W y 120 W) y cuatro puntos de relleno de 75 W. Es el único espacio con luz general, por ser el punto de aparición, descontaminación y extracción.
- **Resto del nivel:** seis puntos rojos de emergencia de 6 W en corredor oeste, corredor este, escaleras principales, conector de servicio, almacén y mantenimiento.
- No hay relleno global ni luces de sala encendidas.
- La intención es que, sin linterna, solo se lean siluetas y luces de emergencia; con linterna, el jugador descubre la arquitectura.

## QA

Se ejecutó `qa_check.py` por grupos, con `uv=False` porque este pase es blockout y todavía no tiene UVs de producción.

| Grupo | Resultado | Errores | Warnings aceptados |
|---|---|---|---|
| Recepción subterránea (techo cerrado) | PASS | 0 | 15 |
| Seguridad | PASS | 0 | 19 |
| Control de acceso | PASS | 0 | 12 |
| Vestuarios | PASS | 0 | 19 |
| Almacén | PASS | 0 | 20 |
| Mantenimiento | PASS | 0 | 19 |
| Oficinas | PASS | 0 | 19 |
| Aseo | PASS | 0 | 11 |
| Conector de servicio | PASS | 0 | 19 |
| Escaleras principales | PASS | 0 | 12 |
| Escalera de emergencia E1 descendente | PASS | 0 | 10 |
| Escalera de emergencia E2 descendente | PASS | 0 | 10 |
| Corredor + conectores | PASS | 0 | 21 |
| Escaleras (peldaños + suelos) | PASS | 0 | 21 |
| Escalera principal descendente + foso | PASS | 0 | 16 |
| Galería técnica Este | PASS | 0 | 21 |
| Galería de ventilación Norte | PASS | 0 | 21 |
| Pasillo de servicio Vestuarios/Almacén | PASS | 0 | 21 |
| Escalera de emergencia 12C descendente | PASS | 0 | 14 |
| Roca base con huecos de escalera | PASS | 0 | 3 |
| Esclusa Recepción–Escaleras | PASS | 0 | 21 |

Warnings aceptados: caras back-to-back ocultas entre suelos, muros y cubiertas, y `ground_z` por la cota de la sala. No hay errores de z-fighting, flotación, normales ni escala en los grupos comprobados.

## Renders

- `docs/fm_level1_v06_plan.png` — planta con etiquetas de zona.
- `docs/fm_level1_v06_iso.png` — vista isométrica sin cubiertas, para revisar la distribución.
- `docs/fm_level1_v06_reception.png` — vista interior de Recepción con la iluminación de intención.
- `docs/fm_level1_v06_alt_plan.png` — planta con las rutas alternas, la escalera 12C y el descenso al Nivel 2.
- `docs/fm_level1_v06_alt_iso.png` — isométrica de las rutas alternas y el núcleo vertical.
- `docs/fm_level1_v06_stair_e1.png`, `docs/fm_level1_v06_stair_e2.png` y `docs/fm_level1_v06_stair_12c.png` — vistas cenitales de los huecos de las escaleras descendentes.

Las cubiertas están en `L1_ARCH_CEILINGS`; se ocultan en viewport y en render mientras se revisa la planta. Las etiquetas `ANNOT_L1_Label_*` son anotaciones de diseño y no se renderizan.

## Limitaciones

- Es un blockout: no tiene materiales PBR finales, UVs de producción, desgaste, suciedad ni narrativa ambiental.
- No tiene props, puertas con hoja, barandillas, rejillas, equipamiento ni objetos recuperables.
- Las escaleras son volumétricas; faltan barandillas, mesetas definitivas y validación de circulación con el jugador.
- La recepción de superficie se retiró por decisión de diseño; sus objetos quedan ocultos y archivados en el `.blend`, no visibles. La recepción subterránea es la única recepción y el único punto de extracción.
- La escalera principal y las de emergencia E1, E2 y 12C descienden al Nivel 2, pero el Nivel 2 no está modelado; la meseta es solo una reserva de hueco.
- La galería de ventilación Norte tiene 1,25 m de altura; está pensada para jugadores agachados o a gatas. Debe validarse que las criaturas no la usen o que su acceso quede bloqueado.
- No se ha medido rendimiento, no hay LOD, colisiones ni navegación.
- No se ha probado en Godot.
- No se ha reutilizado todavía ningún asset del nivel anterior en esta escena; la biblioteca de kits se integrará después de aprobar la distribución.

## Siguiente paso

1. Revisar con Riyo la distribución, la recepción subterránea como único punto de extracción, las siete rutas alternas —incluida la esclusa Recepción–Escaleras—, la escalera 12C y el descenso al Nivel 2.
2. Revisar con Riyo el primer lote del kit arquitectónico modular y su montaje de prueba.
3. Continuar el kit con escaleras, esquinas, vanos y remates; después integrar los assets reutilizables aprobados y empezar el detalle por zonas.
4. Solo después: materiales, iluminación final, props y QA de producción.

No se inicia Godot hasta aprobación explícita.

## Nota sobre los túneles de servicio

Los cuatro túneles de servicio —esclusa Recepción–Escaleras, galería técnica Este, galería de ventilación Norte y pasillo de servicio Vestuarios/Almacén— tienen **1,0 m de ancho y 1,25 m de alto**, y quedan integrados directamente en los muros existentes mediante huecos de **1,0×1,25 m**, sin paneles adicionales alrededor. Están dimensionados para que los jugadores pasen agachados o a gatas; las criaturas no deben usarlos o su acceso debe bloquearse de forma explícita.

### Esclusa Mantenimiento–Corredor–Stairs Connector

- **Trazado:** túnel troncal de 1,0×1,25 m en x=2..56, y=-20..-19, y ramal de 1,0×1,25 m en x=20..21, y=-18,75..-4.
- **Conexiones:** huecos directos de 1,0×1,25 m en el muro oeste de Mantenimiento (y=-20..-19), el muro este del Stairs Connector (y=-20..-19) y el muro sur del corredor principal (x=20..21). Sin paneles ni bulkheads.
- **Función:** permite ir de Mantenimiento al corredor principal y, a través del tronco, al pasillo entre las Escaleras Principales y el corredor principal.
- **QA:** PASS, 0 errores, 21 warnings aceptados (back-to-back ocultos y ground_z).
- **Etiqueta:** `17 ESLUSA MANTENIMIENTO - CORREDOR`; luz roja de emergencia de 3 W.
- **Render:** `docs/fm_level1_v06_plan.png` incluye esta ruta.

## Pasillo pequeño Seguridad desde el corredor

- **Recorrido:** pasillo de 1,4 m de ancho × 2,2 m de alto. Tramo vertical x=-38,2..-36,8, y=4,15..11,6; tramo horizontal x=-70,85..-38,2, y=10,2..11,6. Empieza en el muro norte del corredor principal, justo enfrente de la esclusa Recepción–Escaleras, y entra en el muro este de Seguridad.
- **Huecos:** directos de 1,4×2,2 m en el muro norte del corredor y en el muro este de Seguridad; sin paneles ni bulkheads.
- **Corrección asociada:** el muro sur del corredor cerró el antiguo vano de 6 m de la esclusa y dejó un hueco de 1,0×1,25 m con pared alrededor.
- **QA:** PASS, 0 errores, 21 warnings aceptados (back-to-back ocultos y ground_z).
- **Etiqueta:** `19 PASILLO SEGURIDAD`; luz roja de emergencia de 3 W.

## Exclusa a Oficinas desde el pasillo Seguridad

- **Recorrido:** túnel de 1,0×1,25 m que nace en el muro norte del pasillo Seguridad (`SM_L1_Alt_SecurityCorridor_Wall_N`) en x=-40..-39, sube hasta y=30,5 y gira al este por y=30,5..31,5 hasta el muro oeste de Oficinas.
- **Huecos:** directos de 1,0×1,25 m en el pasillo Seguridad y en el muro oeste de Oficinas; sin paneles ni bulkheads.
- **QA:** PASS, 0 errores, 21 warnings aceptados (back-to-back ocultos y ground_z).
- **Etiqueta:** `20 ESLUSA OFICINAS`; luz roja de emergencia de 3 W.

## Kit arquitectónico modular (2026-11-05)

Primer lote del kit, construido fuera de la planta congelada para no alterar la distribución validada.

### Colecciones y montaje de prueba

- `L1_KIT_ARCH`: **24 assets** de biblioteca, ocultos en viewport y render.
- `L1_KIT_LAB`: **32 objetos** de montaje de prueba, visibles en viewport y excluidos de render para no contaminar las vistas de la planta.
- Laboratorio de prueba: sala de **8×8×4,5 m** en (-180, -50), con cuatro módulos de suelo y techo, muros de 4 m, puerta de **1,8×2,6 m** con lintel, cuatro columnas interiores, viga de 8 m, zócalos y barandilla.

### Assets del primer lote

- Muros modulares de **1, 2 y 4 m** de ancho × **4,2, 4,5 y 6,0 m** de alto, espesor **0,30 m**.
- Lintel de puerta **2×1,72 m**.
- Suelo y techo de **4×4×0,20 m**.
- Columnas de **0,45×0,45 m** × 4,2/4,5/6,0 m y base de 0,55×0,55×0,03 m.
- Vigas de **4 y 8 m** (0,30×0,45 m).
- Marcos de puerta de **1,8×2,6 m** y **1,8×3,2 m**, con umbral y cabecera.
- Zócalos de **1, 2 y 4 m** y barandilla de **2 m**.

### Métricas, pivotes y UVs

- Grid de **0,5 m**; módulos principales de 1/2/4 m.
- Pivotes: suelo en cara superior; techo en cara inferior; muro, columna, viga y zócalo en base-centro.
- UVs desde el inicio con densidad constante (1 tile UV = 4 m). Columnas y marcos recibieron Smart UV Project; el resto se empaquetó con `uv.pack_islands`.
- Materiales de validación sin texturas finales: `M_KIT_Wall_Concrete`, `M_KIT_Floor_Concrete`, `M_KIT_Ceiling_Concrete`, `M_KIT_Steel`, `M_KIT_Paint_Green`, `M_KIT_DoorFrame`, `M_KIT_Trim`, `M_KIT_Railing`.

### QA

- Grupo `L1_KIT_LAB` de 32 mallas: **PASS**, 0 errores, 22 warnings aceptados.
- Warnings: 2 n-gons en el marco de puerta y caras back-to-back ocultas en uniones de muros, techo, lintel, suelo, barandilla y columnas.
- Sin z-fighting, sin mallas sin UV, sin escalas sin aplicar y sin materiales faltantes.
- No se ha texturizado ni exportado a Godot.

### Renders

- `docs/fm_level1_v06_kit_interior.png`: vista interior con puerta, lintel, columnas, barandilla y zócalos.
- `docs/fm_level1_v06_kit_overview.png`: vista exterior del montaje con techos ocultos para revisar la planta y las uniones.

### Limitaciones y siguiente bloque

- El kit es un primer lote: faltan escaleras modulares, esquinas interiores/exteriores, vanos de ventana, remates de cubierta, pies de muro y variantes de puerta de 2,0 m de paso.
- Los materiales son de validación; el PBR, trim sheets y desgaste quedan para después de aprobar el kit.
- No se ha integrado todavía en las salas del V06; la planta congelada permanece intacta.

### Segundo lote: hojas de puerta y remate de muro

- Se añadieron **`SM_KIT_DoorLeaf_1p8x2p6`** y **`SM_KIT_DoorLeaf_1p8x3p2`**, hojas de 1,78 m de ancho y 2,55/3,15 m de alto, con pivote en la bisagra inferior izquierda y material `M_KIT_Paint_Green`.
- Se añadió **`SM_KIT_WallEndTrim_4p5`**, remate vertical de 0,06×0,30×4,50 m en `M_KIT_Trim`.
- La puerta de 2,6 m se colocó abierta 65° en el laboratorio (`LAB_DoorLeaf`) para comprobar el giro y el paso.
- QA del laboratorio: **PASS, 0 errores, 23 warnings aceptados** (n-gons y back-to-back ocultos). Hojas y remate pasan QA individualmente.
- Render: `docs/fm_level1_v06_kit_door_open.png`.
- **No se aprobaron todavía** las escaleras modulares ni el guardaesquinas: las escaleras presentaban 4 aristas con winding inconsistente, y el guardaesquinas daba piezas flotantes. Se retiraron del kit aprobado y quedan para el siguiente bloque con una malla soldada/reconstruida.
- Sin Godot, sin texturas finales y sin commit.

### Tercer bloque: escaleras y guardaesquinas reconstruidos

- Se reconstruyeron **`SM_KIT_Stair_24_W2p6`** y **`SM_KIT_Stair_24_W1p6`**: 24 peldaños, contrahuella 0,1875 m, huella 0,28 m, 4,50 m de descenso y 6,72 m de longitud, con pivote en el borde superior central.
- Se reconstruyó **`SM_KIT_CornerGuard_4p5`** como perfil en L de 0,30×0,30 m y 4,50 m de altura, con malla soldada y material `M_KIT_Steel`.
- QA individual: escaleras **PASS 0 errores / 1 warning** cada una; guardaesquinas **PASS 0 errores / 1 warning**; hojas y remate PASS; laboratorio **PASS 0 errores / 23 warnings**.
- Renders: `docs/fm_level1_v06_kit_stair.png` y `docs/fm_level1_v06_kit_guard.png`.
- El kit queda con **30 assets** en `L1_KIT_ARCH`, **33 objetos** en `L1_KIT_LAB` y **769 objetos** en la escena. Sin Godot, sin texturas finales y sin commit.

## Integración piloto: muro oeste del Conector (2026-11-05)

- **Zona piloto:** Conector de servicio (Z10), muro oeste en x=40, y=8..30, 22 m de largo y 4,2 m de alto.
- **Montaje:** seis módulos del kit en `L1_KIT_PILOT` (cinco de 4 m y uno de 2 m), rotados 90° para correr en Y.
- **Blockout:** `SM_L1_Zone10_ServiceConnector_Wall_W_0` quedó oculto en viewport y render; no se borró.
- **Ajuste:** se detectó que `SM_L1_Conn_ChangingConnector_Wall_W_0`, de otra zona, ocupa el mismo plano. El muro piloto se desplazó **+0,02 m en X** (x=40,02) para evitar coplanaridad sin tocar la pared ajena.
- **QA:** PASS, 0 errores, 5 warnings aceptados (caras back-to-back ocultas entre módulos). Sin z-fighting.
- **Render:** `docs/fm_level1_v06_kit_pilot_wall.png`.
- **Estado:** 776 objetos en la escena (incluye la cámara `KIT_CAM_PilotWall`); `.blend` guardado, `dirty False`; cámara restaurada a `ARCH_CAM_Top`.
- Es un **primer tramo controlado**, no la integración completa de la zona. No se tocaron otras salas, no se abrió Godot y no se hizo commit.

## Integración piloto: muro sur y portal del Conector (2026-11-05)

- **Zona piloto:** Conector de servicio (Z10), muro sur en y=8, x=40..62, 22 m de largo.
- **Montaje:** cinco módulos del kit en `L1_KIT_PILOT` (6 m a la izquierda y 10 m a la derecha del portal).
- **Portal:** `SM_KIT_Portal_6x2p6`, exterior 6,04×0,34×2,90 m, hueco 5,84×2,60 m.
- **Blockout:** se ocultaron `Wall_S_0`, `Wall_S_2` y la puerta `Door_S_L/R/T`; se conservó el lintel superior `Wall_S_1` como contexto provisional. No se borró nada.
- **QA:** PASS, 0 errores, 9 warnings aceptados (n-gons del portal y caras back-to-back ocultas). Sin z-fighting.
- **Render:** `docs/fm_level1_v06_kit_pilot_south.png`.
- **Estado:** 784 objetos; `.blend` guardado, `dirty False`; cámara `ARCH_CAM_Top`.
- El muro este y el muro norte del Conector siguen en blockout; la integración completa queda pendiente. Sin Godot y sin commit.

## Integración piloto: muro este y portal del Conector (2026-11-05)

- **Zona piloto:** Conector de servicio (Z10), muro este en x=62, y=8..30, 22 m de largo.
- **Montaje:** cinco módulos en `L1_KIT_PILOT`: 10 m al sur del portal (4+4+2) y 6 m al norte (4+2), rotados 90°.
- **Portal:** reutiliza `SM_KIT_Portal_6x2p6`, exterior 6,04×0,34×2,90 m, hueco 5,84×2,60 m.
- **Blockout:** se ocultaron `Wall_E_0`, `Wall_E_2` y `Door_E_L/R/T`; se conservó el lintel `Wall_E_1` como contexto provisional. No se borró nada.
- **QA:** PASS, 0 errores, 14 warnings aceptados (n-gons de los portales y caras back-to-back ocultas). Sin z-fighting.
- **Render:** `docs/fm_level1_v06_kit_pilot_east.png`.
- **Estado:** 791 objetos; `.blend` guardado, `dirty False`, cámara `ARCH_CAM_Top`. El muro norte sigue en blockout. Sin Godot y sin commit.

## Integración piloto: muro norte y portal del Conector (2026-11-05)

- **Zona piloto:** Conector de servicio (Z10), muro norte en y=30, x=40..62.
- **Corrección del blockout:** la puerta existente ocupa 4 m (x=56..60), pero los segmentos provisionales solo dejaban 1 m de hueco. Se reconstruyó el muro con un vano real de 4 m.
- **Montaje:** cuatro módulos de 4 m (x=40..56) y uno de 2 m (x=60..62); portal `SM_KIT_Portal_4x2p6` (exterior 4,20×0,34×2,90 m; hueco 4,00×2,60 m) y lintel `SM_KIT_Wall_4x1p3`.
- **Ajuste:** el portal se desplazó +0,05 m en X (x=58,05) para eliminar el z-fighting con los extremos de los módulos.
- **Blockout:** se ocultaron `Wall_N_0/1/2` y `Door_N_Service_L/R/T`; no se borró nada.
- **QA:** PASS, 0 errores, 21 warnings aceptados (n-gons de portales y caras back-to-back ocultas). Sin z-fighting.
- **Render:** `docs/fm_level1_v06_kit_pilot_north.png`.
- **Estado:** 801 objetos; los cuatro muros del Conector están integrados; `.blend` guardado, `dirty False`, cámara `ARCH_CAM_Top`. Sin Godot y sin commit.

## Integración piloto: suelo y techo del Conector (2026-11-05)

- **Zona piloto:** Conector de servicio (Z10), superficie 22×22 m.
- **Suelo:** 25 módulos de 4×4, 5 de 2×4, 5 de 4×2 y 1 de 2×2; cara superior en z=0.
- **Techo:** misma distribución de 36 módulos; cara inferior en z=3,99.
- **Blockout:** se ocultaron reversiblemente `SM_L1_Zone10_ServiceConnector_Floor` y `SM_L1_Zone10_ServiceConnector_Ceiling`; no se borró nada.
- **Ajuste:** se desplazó el lintel norte +0,02 m en X para eliminar el z-fighting con el módulo de techo de la esquina.
- **QA:** PASS, 0 errores, 24 warnings aceptados (n-gons de portales, back-to-back ocultos y ground_z).
- **Render:** `docs/fm_level1_v06_kit_pilot_floor.png`.
- **Estado:** **880 objetos**; los cuatro muros y el suelo/techo del Conector están integrados; `.blend` guardado, `dirty False`, cámara `ARCH_CAM_Top`.
- **Pendiente:** pilares, equipamiento y detalles del Conector siguen siendo blockout; el render de conjunto aún muestra esos elementos provisionales. Sin Godot y sin commit.

## Apertura del corredor ChangingConnector–Conector (2026-11-05)

- **Problema:** el corredor x=40..46 quedaba bloqueado por los tramos de muro del kit en y=8 y y=30, justo después de la puerta de y=4.
- **Solución:** se ocultaron reversiblemente `KIT_PILOT_Z10_Wall_S_00`, `KIT_PILOT_Z10_Wall_S_01`, `KIT_PILOT_Z10_Wall_N_00` y `KIT_PILOT_Z10_Wall_N_01`; no se borró nada.
- **Muro norte:** se añadió `KIT_PILOT_Z10_Wall_N_Patch_00`, módulo de 2 m en x=46..48, para mantener cerrado el tramo que no pertenece al corredor.
- **Resultado:** el corredor queda abierto de x=40..46 entre las dos puertas de y=4 y y=40; la pared central x=46 y las puertas ajenas no se tocaron.
- **QA:** PASS, 0 errores, 24 warnings aceptados (n-gons de portales y back-to-back ocultos). Sin z-fighting.
- **Render:** `docs/fm_level1_v06_kit_pilot_corridor_open.png`.
- **Estado:** **882 objetos**; `.blend` guardado; cámara `ARCH_CAM_Top`. Sin Godot y sin commit.

## Zócalos perimetrales del Conector (2026-11-05)

- Se añadieron **18 zócalos** del kit en el perímetro del Conector: 4 m y 2 m, material `M_KIT_Trim`.
- Se colocaron en los tramos de muro del kit, dejando libres los portales y el corredor abierto x=40..46.
- En el muro oeste se separaron **5 mm** de la cara del muro para evitar z-fighting; el resto queda embebido en el muro sin caras coplanares.
- **QA:** PASS, 0 errores, 24 warnings aceptados (n-gons de portales y back-to-back ocultos).
- **Render:** `docs/fm_level1_v06_kit_pilot_baseboards.png`.
- **Estado:** **901 objetos**; `.blend` guardado. Sigue siendo **solo arquitectura**; no se añadieron objetos narrativos. Sin Godot y sin commit.

## Cierre del muro sobre el portal sur (2026-11-05)

- **Problema:** el portal sur del Conector quedaba con el lintel de blockout `SM_L1_Zone10_ServiceConnector_Wall_S_1` arriba; la pared no era continua alrededor de la exclusa.
- **Solución:** se ocultó ese lintel y se añadió `KIT_PILOT_Z10_Lintel_S_Short`, módulo de **6,00×0,30×1,08 m** (`SM_KIT_Wall_6x1p08`), sobre el portal, de z=2,90 a 3,98.
- Se creó también `SM_KIT_Wall_6x1p3`, pero se retiró de la posición por z-fighting con el techo.
- **QA:** PASS, 0 errores, 24 warnings aceptados. Sin z-fighting.
- **Render:** `docs/fm_level1_v06_kit_pilot_portal_south.png`.
- **Estado:** **906 objetos**; la pared sobre el portal sur queda cerrada con módulo del kit. Solo arquitectura; sin objetos narrativos. Sin Godot y sin commit.

## Entradas sin portal (2026-11-05)

- Se ocultaron reversiblemente los tres marcos `KIT_PILOT_Z10_Portal_S`, `KIT_PILOT_Z10_Portal_E` y `KIT_PILOT_Z10_Portal_N`; no se borró nada.
- Las entradas quedan como huecos limpios en el muro, con los linteles y las paredes del kit alrededor.
- **QA:** PASS, 0 errores, 21 warnings aceptados. Sin z-fighting.
- **Render:** `docs/fm_level1_v06_kit_pilot_no_portals.png`.
- **Estado:** **903 objetos**; sin portales decorativos en las entradas del Conector. El vestíbulo sur mantiene 4 m de profundidad; si hay que reducirlo, es una decisión aparte. Solo arquitectura; sin objetos narrativos. Sin Godot y sin commit.

## Portales restaurados en pasillos y habitaciones (2026-11-05)

- Se restauraron **`KIT_PILOT_Z10_Portal_E`** y **`KIT_PILOT_Z10_Portal_N`**, correspondientes a entradas de pasillos/habitaciones.
- **`KIT_PILOT_Z10_Portal_S`** permanece oculto: es la entrada de la exclusa y debe quedar sin portal.
- **QA:** PASS, 0 errores, 23 warnings aceptados.
- **Render:** `docs/fm_level1_v06_kit_pilot_portals_restored.png`.
- **Estado:** **903 objetos**; portales restaurados en pasillos/habitaciones, exclusa sur sin portal. Solo arquitectura; sin objetos narrativos. Sin Godot y sin commit.

## Bandejas de cables del Conector (2026-11-05)

- Se crearon **`SM_KIT_CableTray_4m`** y **`SM_KIT_CableTray_2m`**: bandeja de cables con dos largueros y travesaños, material `M_KIT_Steel`.
- Se montaron cinco módulos sobre el muro este, a z=3,50 y sobre los portales: 4 m + 4 m + 2 m en el tramo sur y 4 m + 2 m en el norte.
- Se añadieron cinco soportes desde el muro hasta la bandeja.
- **QA:** PASS, 0 errores, 28 warnings aceptados (n-gons de portales y back-to-back ocultos). Sin z-fighting.
- **Render:** `docs/fm_level1_v06_kit_pilot_trays.png`.
- **Estado:** **918 objetos**; solo arquitectura, sin objetos narrativos. Sin Godot y sin commit.

## Conductos y abrazaderas del Conector (2026-11-05)

- Se añadieron cinco conductos de acero en el muro este, a z=3,15:
  - 4 m + 4 m + 2 m en el tramo sur.
  - 4 m + 2 m en el tramo norte.
- Cada conducto lleva una abrazadera que lo conecta al muro; no quedan flotando.
- **QA:** PASS, 0 errores, 38 warnings aceptados. Sin z-fighting.
- **Estado:** **928 objetos**; solo arquitectura, sin objetos narrativos. Sin Godot y sin commit.

## Cierre de servicios constructivos del Conector (2026-11-05)

- Se añadieron dos **cajas de registro** en el muro este: y=14 y y=26, z=1,55, de 0,12×0,30×0,40 m.
- Se añadieron cinco **barras de rejilla** sobre el desagüe de suelo, en (52; 15; 0,014).
- Se añadieron dos **pasamuros** cilíndricos de 0,40 m de largo y 0,06 m de radio en el muro este, a y=12 y y=26, z=2,60.
- **QA:** PASS, 0 errores, 51 warnings aceptados. Sin z-fighting.
- **Estado:** **941 objetos**; servicios constructivos del Conector terminados. Solo arquitectura, sin objetos narrativos. Sin Godot y sin commit.

## Cierre de la habitación del Conector (2026-11-05)

- **Estado:** 975 objetos totales; 185 objetos en `L1_KIT_PILOT`; QA **PASS 0 errores / 54 warnings**; `dirty False`; cámara de escena `ARCH_CAM_Top`.
- **Arquitectura:** muros, suelo y techo modulares; cuatro columnas del kit; portal E abierto con hojas dobles hacia el interior; portal N con marco y hojas dobles **cerradas** (protegen el hueco del pasillo norte, aún sin construir); acceso sur sin portal ni hoja; zócalos; servicios constructivos (bandejas, conductos, panel, desagüe, rejilla, cajas, pasamuros).
- **Puertas:** `KIT_PILOT_Z10_Portal_N`, `KIT_PILOT_Z10_Door_N_L/R` y `KIT_PILOT_Z10_Transom_N`; el antiguo `KIT_PILOT_Z10_Lintel_N` de altura completa quedó oculto y se sustituyó por `KIT_PILOT_Z10_Lintel_N_Header`. `KIT_PILOT_Z10_Transom_E` cierra el hueco sobre la puerta este. Los transoms bajan hasta la altura de las hojas, sin franja negra.
- **Materiales:** PBR de hormigón en muros, suelo húmedo y metal; pintura verde texturizada; rótulos de imagen `M_FM_Sign_Conector`, `M_FM_Sign_Servicio` y `M_FM_Sign_Pasillo` aplicados directamente a la cara frontal de las placas, con emisión 0,18. Sin rótulos superpuestos ni z-fighting.
- **Iluminación:** `KIT_PILOT_Z10_Emergency_Ceiling` con lente roja y `LIGHT_L1_Emergency_Service` de 4 W en su interior; luces de pared E/N de 2,5 W (`LIGHT_L1_Conector_E/N`). Las luminarias de techo permanecen apagadas. La habitación queda prácticamente a oscuras, solo con emergencias rojas.
- **Renders:** `docs/fm_conector_final_lit.png` (luz de trabajo para revisión), `docs/fm_conector_final_dark.png` (solo emergencias, aspecto in-game), `docs/fm_conector_door.png` (detalle de la puerta norte y rótulo PASILLO) y `docs/fm_conector_east.png` (detalle del portal este y rótulo SERVICIO).
- **QA:** sin z-fighting; los warnings restantes son n-gons y caras back-to-back ocultas.
- **Pendiente por decisión de Riyo:** objetos narrativos y pruebas/integración en Godot. No se añadieron objetos narrativos ni se abrió Godot. No se restauró el muro central ni la exclusa eliminados.

## Pase de equipamiento no narrativo del Conector (2026-11-06)

- **Estado:** **1.178 objetos totales**; **202 props** en `L1_PROPS_Z10`; 185 objetos en `L1_KIT_PILOT`; QA final **PASS 0 errores / 254 warnings**; `dirty False`; cámara de escena `ARCH_CAM_Top`.
- **Presupuesto:** arquitectura del Conector ≈13.400 tris; props ≈88.500 tris; total del Conector ≈102.000 tris. Escena visible completa ≈112.000 tris.
- **Cobertura funcional por zonas:**
  - **Oeste:** banco de trabajo con encimera de acero, tornillo, pegboard con herramientas, caja de herramientas, taburete, cubos, extintor de pie, reloj, papeleras, bobinas de cable y manguera de incendios.
  - **Noroeste:** banco de taquillas metálicas de tres puertas (una entreabierta), banco de vestuario, perchero y alfombra.
  - **Este:** cuadros eléctricos, armario utility, bajantes de conducto, panel existente, cámara de seguridad, alarma de incendio, extintor y bolardos.
  - **Sur:** tres estanterías con cajas y contenedores, palé con cajas de madera, palé de contención con bidones, tablero esquemático y señalización.
  - **Centro:** transformador sobre bancada con paneles de ventilación y etiqueta de alta tensión, bobina de cable grande sobre soporte, zanja de cables cubierta, tuberías verticales en dos columnas.
  - **Techo:** conducto HVAC con bridas y suspensiones, tubería de rociadores con cabezas, bandeja de cables oeste y cableado.
  - **Suelo:** marcado de zona de trabajo, almacén, pasillo E–N, protección de columnas y zona de peligro del cuadro eléctrico.
- **Materiales:** PBR existentes (`M_FM_Concrete_Wall`, `M_FM_Concrete_Floor`, `M_FM_Metal_Panel`, `M_FM_Painted_Green`) más materiales propios para acero oscuro, caucho, madera, cartón, plástico, pintura amarilla, hazard, rejillas, rótulos y transformador. Los rótulos usan texturas de imagen generadas; la emisión de las señales se redujo a 0,12.
- **Atmósfera:** niebla volumétrica de mundo con densidad 0,006 y dispersión 0,35; color management AgX. El compositor de Blender 5.2 se descartó porque el nodo Glare devolvía una imagen blanca con la API actual; el postprocesado final se hará en Godot.
- **Iluminación:** solo tres luces de emergencia reales (`LIGHT_L1_Emergency_Service` 4 W, `LIGHT_L1_Conector_E/N` 2,5 W). No se añadieron luces de trabajo permanentes; las de los renders son temporales y se eliminaron.
- **Escondites:** anclajes vacíos en `L1_GAMEPLAY_Z10`: `HIDEOUT_Z10_Lockers` (40,5; 26,35; 1,0) y `HIDEOUT_Z10_UnderBench` (40,6; 13,2; 0,45). El banco de taquillas tiene la puerta central entreabierta y propiedad `hideout="locker_bank_3"`. No hay interacción implementada.
- **Renders finales:**
  - `docs/fm_conector_final_lit.png` — vista general con luces de revisión.
  - `docs/fm_conector_final_dark.png` — vista general solo con emergencias.
  - `docs/fm_conector_detail_workbench.png` — banco, pegboard y herramienta.
  - `docs/fm_conector_detail_lockers.png` — taquillas y vestuario.
  - `docs/fm_conector_detail_electrical.png` — acceso este, cuadros y bolardos.
  - `docs/fm_conector_detail_storage.png` — estanterías, bobina, tablero y señalización.
- **Assets externos:** se conservan estanterías, bidones, armario utility B y taburete de la biblioteca Poly Haven; su licencia sigue pendiente de verificación antes de distribución. Los carros, extintor, alarma, reloj, cajas de madera, transformador, bobinas y demás elementos problemáticos se sustituyeron por modelos propios para evitar geometría interna y z-fighting.
- **QA:** sin z-fighting; 0 errores. Los 254 warnings son n-gons, contactos back-to-back ocultos, solapamientos de UV y avisos de materiales de assets externos; se aceptan para esta fase.
- **Pendiente por decisión de Riyo:** objetos narrativos, interacción de escondites, colisiones/navegación, LOD/optimización de exportación, pruebas e integración en Godot y verificación de licencias. No se añadieron objetos narrativos ni se abrió Godot. No se restauró el muro central ni la exclusa eliminados. Sin commit.

## Revisión de objetos del Conector Z10 (2026-11-06)

- Estado final: **1.296 objetos**; **320 props** en `L1_PROPS_Z10`, de los cuales **119 son detalles hero** (`DET_Z10_*`); **QA PASS, 0 errores / 372 warnings** aceptados.
- Imágenes: **41 texturas generadas empaquetadas**, **0 imágenes faltantes**. Materiales PBR actualizados para acero, pintura amarilla/roja, cartón, plástico, caucho, madera y rojo industrial.
- Pase hero: banco de trabajo (tornillos, regleta, ganchos, etiquetas), taquillas (zócalo, juntas, cerraduras), transformador (aletas, aisladores, busbar, placa, tornillos), tambor de cable (núcleo, bobina, anillos, lamas), armario eléctrico A (puerta, bisagras, manilla, rejillas, indicador, prensaestopas) y extintor (soporte, manguera, boquilla, manómetro).
- Auditoría espacial de 320 props: **0 bloqueos de los portales E/N**, **0 props sueltos en el pasillo central**, **0 objetos fuera de muros/suelo**. Solo hay penetraciones intencionales de los 5 soportes de rociadores y `WestConduit` en el techo, y las risers adosadas a las columnas.
- Escondites: `HIDEOUT_Z10_Lockers` y `HIDEOUT_Z10_UnderBench`; sin interacción implementada.
- Dictamen: correcto a nivel de juego/escena (topología, UVs, escala, contacto y colocación); **no es realismo de close-up comercial**. Persisten herramientas planas, rótulos pequeños sobreexpuestos/borrosos, madera y bidones saturados, y falta desgaste/decals/detalle terciario.
- Renders de revisión: `docs/fm_z10_hero_workbench.png`, `docs/fm_z10_hero_lockers.png`, `docs/fm_z10_hero_transformer.png`, `docs/fm_z10_hero_cabinet.png`, `docs/fm_z10_hero_extinguisher.png`.
- Sin objetos narrativos, sin pruebas ni exportación a Godot, sin commit.

## Estudio de realismo de los casilleros (2026-11-06)

- Se trabajó **solo** sobre `PROP_Z10_LockerBank`, `LockerDoor_00/01/02`, sus rejillas/herrajes/números y `LockerInterior`.
- Bevel: el banco conserva el modificador `Bevel_Realism` (0,005 / 3 segmentos / clamp). Las puertas se separaron por material para poder aplicar el bevel solo a la chapa; se limpiaron 176 caras degeneradas por puerta y se revalidó la geometría.
- Material: `M_Z10_Locker_Studio`, con Noise 80 → ColorRamp → Roughness y Bump 0,03 → Normal; una segunda Noise de baja frecuencia aporta variación al color base. Metallic 0,25.
- Estudio: escena `Z10_LOCKERS_STUDIO`, dos Area Lights de 3×3 m (key 1200 W a 45°, fill 340 W), sin point lights. Cámara 85 mm, DOF con foco en `PROP_Z10_LockerDoor_01`, f/4. Cycles 128 samples, 900×1125.
- QA de casilleros: **PASS, 0 errores / 69 warnings**.
- Render: `docs/fm_z10_lockers_studio.png`.
- El acabado mejora bordes, rugosidad y sombras suaves; sigue sin arañazos/desconchones/decals de suciedad, por lo que no es fotorrealismo de close-up absoluto.

## Auditoría y corrección de objetos del Conector (2026-11-06)

- **1.309 objetos**, **328 props** en `L1_PROPS_Z10`; **QA final: PASS, 0 errores / 379 warnings**; `dirty False`.
- Auditoría espacial de los 328 props: **0 objetos fuera de la sala**, **0 bloqueos de los portales E/N**, **0 objetos hundidos en soportes**. Solo quedan como casos intencionales las bases de columna, las risers adosadas a columnas y las penetraciones de techo de 5 soportes de rociadores y `WestConduit`.
- Correcciones aplicadas:
  - Extintor: subido y montado en el soporte de pared; bracket desplazado hasta tocar el muro; manguera, boquilla y manómetro reubicados; rótulo bajado; manilla flotante corregida; boquilla solapada con el tramo de manguera.
  - Armario eléctrico A: gauge y cara del gauge recolocados en la cara frontal, alineados a z≈0,85.
  - Cajas de madera: cajas inferiores acercadas para cerrar el hueco; la caja superior apoya claramente sobre ambas.
  - `WestJunction`: empotramiento reducido de 0,04 a 0,02 m.
  - Eliminado el rótulo pequeño e ilegible del pegboard.
  - Rótulos y firmas: materiales mate (roughness 0,9, metallic 0, emisión 0,02) para reducir brillos.
  - Bidones azules desaturados y madera atenuada para evitar colores de plástico/juguete.
- Evidencia: `docs/fm_z10_fix_extinguisher.png`, `docs/fm_z10_fix_cabinet.png`, `docs/fm_z10_fix_crates.png` y `docs/fm_z10_lockers_studio.png`.
- Alcance de realismo: los casilleros son los únicos con el pase de estudio completo (bevel/material procedural/2 luces/85 mm/DOF/Cycles 128). El resto conserva PBR, UVs, biseles y QA correctos, pero no se ha re-renderizado individualmente con ese estudio; queda pendiente de actualización cuando se trabaje en cada asset, según la sección 48.2 de `AGENTS.md`.
- Sin objetos narrativos, sin pruebas ni exportación a Godot, sin commit.

## Actualización del estándar de realismo (2026-11-06)

El estándar anterior basado en el pase de casilleros Z10 fue reemplazado por las **Reglas de realismo adaptativo para Blender** (`docs/FM_QUALITY_STANDARD.md`, sección 19). Los casilleros quedan como ejemplo de aplicación; el resto de objetos debe seguir la categoría que le corresponda (hard surface, orgánico, mobiliario o arquitectura).


## Fire hose reel Z10 — pase de realismo adaptativo (2026-11-06)

- Categoría aplicada: **A) hard surface/mecánico**.
- Se sustituyó el blockout (disco rojo plano + placa) por un carrete de manguera industrial: placa de pared, marco de acero con pernos, tambor/placa trasera roja, anillo frontal con 4 radios y cubo, bobinas de manguera, tramo suelto, boquilla de latón, entrada y válvula.
- Materiales: `M_FM_Steel_Dark`, `M_FM_Industrial_Red`, `M_FM_Rubber`, `M_FM_Metal_Panel`, `M_FM_Brass` y rótulos retirados por textura corrupta.
- **4.550 verts / 4.800 polys**; QA **PASS 0 errores / 378 warnings**; 1.308 objetos, 327 props, `dirty False`.
- Ubicación: pared oeste, misma zona; sin bloquear portales ni circulación.
- Render: `docs/fm_z10_firehosereel.png` (Cycles 128, 600×750, 85 mm, DOF f/4).
- Excepción técnica: se usaron biseles horneados por pieza; no se dejó un modificador Bevel global porque generaba 6.107 caras degeneradas. El bisel visual está presente en las piezas principales.
- Limitación: pintura roja limpia/saturada y bobina parcialmente oculta por el cubo; sin desgaste/decals.

## CableTrench (2026-11-06)

- Se sustituyó la franja plana de 7,6 × 0,4 × 0,04 m y sus 7 listones por un canal de 7,95 m con marco de acero, fondo, 6 cables (rojo/azul/amarillo/negro), 6 tapas atornilladas, 2 tramos abiertos de inspección, entrada oeste para los cables LV del transformador y caja de suelo este.
- Se añadió `PROP_Z10_CableTrenchRiser`: riser vertical hasta z≈3,05, caja superior contra el conduit/tray este, 3 abrazaderas y brazos de pared. El conjunto llega a x=61,85 y conecta transformador → trench → conduit/tray este.
- QA de topología/UV: 0 errores. QA local reporta 3 contactos coplanares (10/6/2 triángulos) que el debug BVH no reproduce como caras coplanares same-normal y que no se ven como z-fighting en los renders.
- Estado: 1.301 objetos, 323 props; archivo guardado; cámara ARCH_CAM_Top restaurada.
- Renders: `docs/fm_z10_cabletrench_wide.png` (vista amplia desde el sur), `docs/fm_z10_cabletrench_top.png` (planta completa) y `docs/fm_z10_cabletrench.png` (3/4 con columna en primer plano). EEVEE 128; Cycles no disponible.

## Cámara de seguridad Z10 (2026-11-06)

- **Objeto:** `PROP_Z10_SecurityCamera`, categoría A (hard surface/mecánico).
- **Reconstrucción:** placa de pared con 4 tornillos, brazo y articulación, cuerpo bullet, aro trasero, parasol, bisel frontal, lente oscura, 6 LEDs IR, LED de estado, gland y cable conectado al conduit existente.
- **Geometría:** 1.336 vértices / 964 polígonos; dimensiones 0,50 × 0,18 × 0,255 m; montada en la pared este sobre la zona de seguridad.
- **QA local:** PASS, 0 errores / 8 warnings; sin z-fighting, sin piezas flotantes y sin UVs inválidas.
- **Render de evidencia:** `docs/fm_z10_securitycamera.png` (EEVEE 128, 800×800, 85 mm, DOF f/4); lente oscura con reflejo degradado, LEDs IR rojos y cuerpo bullet legible.
- **Limpieza:** se eliminaron 5 restos obsoletos de servicios (`PROP_Z10_SVC_EastCompletion.001` y `PROP_Z10_WestCable_0..3`), que no pertenecían a la cámara ni a la bandeja actual.
- **Estado del archivo:** 1.297 objetos, 319 props, 182 objetos en `L1_KIT_PILOT`; cámara `ARCH_CAM_Top`; sin `TMP_*`; `dirty False`.
- **Limitación:** Cycles no está disponible en esta instalación; el render se hizo con EEVEE 128. La lente se ajustó a un material oscuro y mate (roughness 0,85) para evitar el lavado especular.

## Conexión eléctrica de las luces de emergencia Z10 (2026-11-06)

- **Problema:** `KIT_PILOT_Z10_Emergency_E` y `_N` tenían su aplique y caja superior, pero no una canalización continua hasta la red eléctrica del Conector.
- **Solución E:** `KIT_PILOT_Z10_EmergencyConduit_E`, tubo vertical desde la parte superior del aplique hasta `KIT_PILOT_Z10_Conduit_02` en la pared este; caja de unión, tee y abrazadera.
- **Solución N:** `KIT_PILOT_Z10_EmergencyConduit_N`, tubo vertical hasta z≈3,85, tramo horizontal sobre el portal norte y bajada hasta `KIT_PILOT_Z10_Conduit_04`; cajas de unión, tee y abrazaderas. El tramo no cruza el hueco del portal.
- **Materiales:** carcasa de emergencia oscura y mate; lente roja profunda con emisión baja para evitar el lavado rosa.
- **QA:** PASS, 0 errores / 17 warnings.
- **Renders:** `docs/fm_z10_emergency_conduit_n.png` y `docs/fm_z10_emergency_conduit_e.png` (EEVEE 128, 800×600).
- **Estado:** 1.304 objetos, 319 props, 184 objetos de kit; sin `TMP_*`.

## Pallet y cajas de madera Z10 (2026-11-06)

- **Pallet:** `PROP_Z10_Pallet`, 880 vértices / 750 polígonos; 5 tablas superiores, 3 travesaños, 3 tablas inferiores, 9 tacos y 15 clavos; material `M_FM_Workbench_Wood`.
- **Cajas:** `PROP_Z10_WoodCrate_0/1/2`, 992 vértices / 930 polígonos cada una; postes de esquina, marcos, tablas laterales separadas, tapa, refuerzos diagonales y uniones; apilado conservado.
- **Material:** `M_FM_Wood_Detailed` procedural para el palé y las cajas; el resto de props de madera se restauró a `M_FM_Workbench_Wood`.
- **QA:** PASS, 0 errores / 14 warnings.
- **Render:** `docs/fm_z10_pallet_crates.png` (EEVEE 128, 900×700, 50 mm).
- **Estado:** 1.304 objetos, 323 props, 184 objetos de kit; guardado.

## Spill pallet Z10 (2026-11-06)

- **Objeto:** `PROP_Z10_SpillPallet`, 1.024 vértices / 960 polígonos; bandeja de contención de 1,32 × 1,32 × 0,20 m.
- **Elementos:** paredes perimetrales, sumidero, rejilla de 7 barras, válvula de drenaje y asas; se conservaron los 4 bidones apilados sobre la rejilla.
- **Materiales:** `M_FM_Safety_Yellow` para el cuerpo; `M_FM_Steel_Dark` para rejilla, sumidero, drenaje y asas.
- **QA:** PASS, 0 errores / 8 warnings.
- **Render:** `docs/fm_z10_spillpallet.png` (EEVEE 128, 900×700, 50 mm).
- **Estado:** 1.298 objetos, 323 props, 179 objetos de kit; guardado.

## Cartel de lubricantes Z10 (2026-11-06)

- **Objeto:** `PROP_Z10_Label_Lubricantes`, pared sur.
- **Corrección:** UV de la cara frontal (+Y) normalizadas 0–1 con U hacia la derecha del espectador y V de abajo a arriba; caras laterales y trasera con `M_FM_Steel_Dark`.
- **Resultado:** el texto **LUBRICANTES** se lee horizontal, centrado y sin espejado.
- **QA:** PASS, 0 errores / 2 warnings.
- **Render:** `docs/fm_z10_label_lubricantes.png` (EEVEE 128, 900×350, 50 mm).

## Tablero esquemático Z10 (2026-11-06)

- **Objeto:** `PROP_Z10_SchematicBoard`, pared sur.
- **Corrección:** UV de la cara frontal (+Y) normalizadas 0–1 con U hacia la derecha del espectador y V de abajo a arriba; caras laterales y trasera con `M_FM_Steel_Dark`.
- **Resultado:** el esquema se lee horizontal y completo: NEXUS // Z10, CUADRO ELÉCTRICO, TRANSFORMADOR, EXTRACCIÓN, RUTA DE SERVICIO y ZONA DE RIESGO ELÉCTRICO.
- **QA:** PASS, 0 errores / 10 warnings.
- **Render:** `docs/fm_z10_schematicboard.png` (EEVEE 128, 900×650, 35 mm).

## Tambor de cable grande Z10 (2026-11-06)

- **Objeto:** `PROP_Z10_LargeCableDrum`, 984 vértices / 1.058 polígonos.
- **Acabado:** `M_FM_LCD_Wood` de madera oscura en las caras y lamas; caras W/E `DET_Z10_LCD_Face_W/E` con disco de madera, cubo de acero y seis pernos por cara; cable enrollado y lamas radiales conservados.
- **QA:** PASS, 0 errores / 6 warnings.
- **Render:** `docs/fm_z10_largecabledrum.png` (EEVEE 128, 900×700, 50 mm).
- **Estado:** 1.305 objetos, 320 props.

## Carretes de cable Z10 (2026-11-06)

- **Objetos:** `PROP_Z10_CableReel_0/1`, 1.022 vértices / 1.092 polígonos cada uno.
- **Acabado:** caras de madera oscura `M_FM_LCD_Wood`; cubos `DET_Z10_CableReel_Hub_0/1` con tapa y seis pernos; cable enrollado visible entre las caras.
- **QA:** PASS, 0 errores / 6 warnings.
- **Render:** `docs/fm_z10_cablereel.png` (EEVEE 128, 900×700, 30 mm).
- **Estado:** 1.289 objetos, 304 props.

## Carros de herramientas y almacenamiento Z10 (2026-11-06)

- **ToolCart:** `PROP_Z10_ToolCart`, 1.030 vértices / 1.104 polígonos; dos bandejas, asa tubular y cuatro ruedas.
- **StorageCart:** `PROP_Z10_StorageCart`, 950 vértices / 1.024 polígonos; plataforma, asa vertical, postes y cuatro ruedas.
- **QA:** PASS, 0 errores / 2 warnings (~100 % de solapamiento UV; aceptable para piezas repetidas, no para baking).
- **Renders:** `docs/fm_z10_toolcart.png` y `docs/fm_z10_storagecart.png` (EEVEE 128, 700×600, 35 mm).
- **Estado:** 1.289 objetos, 304 props.

## Detalle funcional de carros Z10 (2026-11-06)

- **ToolCart:** `DET_Z10_ToolCart_DrawerBank` con tres cajones y tiradores, reborde perimetral superior y asa; geometría preparada para futuras interacciones.
- **StorageCart:** cinco tablones de madera sobre la plataforma, raíles perimetrales y asa; superficie preparada para carga y futuras interacciones.
- **QA:** PASS, 0 errores / 33 warnings.
- **Renders:** `docs/fm_z10_toolcart.png` y `docs/fm_z10_storagecart.png` (EEVEE 128, 700×600, 35 mm).
- **Estado:** 1.310 objetos, 325 props.

## Workbench y herramientas Z10 (2026-11-06)

- **Workbench:** cuerpos de cajón, tiradores, reborde superior, tornillería; tres cajones existentes.
- **Pegboard:** 12 agujeros y 5 ganchos adicionales; herramientas colgadas conservadas.
- **Vice:** manija, husillo y mordazas añadidos.
- **Toolbox:** asa con postes y barra, más dos cierres frontales.
- **Bins y herramientas:** se conservaron los contenedores y las herramientas existentes.
- **QA:** PASS, 0 errores / 76 warnings.
- **Render:** `docs/fm_z10_workbench.png` (EEVEE 128, 900×700, 35 mm).
- **Estado:** 1.344 objetos, 359 props.

## Bins Z10 (2026-11-06)

- **Objetos:** `PROP_Z10_Bin_0..3`, reconstruidos como mallas abiertas de acero bajo el workbench.
- **Geometría:** paredes, fondo, borde y asas; etiquetas originales conservadas.
- **QA:** PASS, 0 errores / 4 warnings.
- **Render:** `docs/fm_z10_bins.png` (EEVEE 128, 700×600, 50 mm).
- **Estado:** 1.344 objetos, 359 props.

## Reloj de pared Z10 (2026-11-06)

- **Objeto:** `PROP_Z10_WallClock`, 536 vértices / 404 polígonos.
- **Acabado:** cuerpo/aro metálico oscuro, esfera blanca con `M_FM_ClockFace`, bisel, cubo central y montaje.
- **QA:** PASS, 0 errores / 4 warnings.
- **Render:** `docs/fm_z10_wallclock.png` (EEVEE 128, 600×600, 50 mm).
- **Estado:** 1.331 objetos, 351 props.

## Waste bin Z10 (2026-11-06)

- **Objeto:** `PROP_Z10_WasteBin`, 984 vértices / 814 polígonos.
- **Acabado:** base, cuerpo cilíndrico, tapa metálica, bisagra, pedal, varilla, asas, lengüeta y bandas.
- **QA:** PASS, 0 errores / 2 warnings.
- **Render:** `docs/fm_z10_wastebin.png` (EEVEE 128, 700×600, 50 mm).
- **Estado:** 1.331 objetos, 351 props.

## Herramientas de mano Z10 (2026-11-06)

- **Objetos:** `PROP_Z10_Tool_Wrench` (16 vértices), `PROP_Z10_Tool_Pliers` (24), `PROP_Z10_Tool_Screwdriver` (104) y `PROP_Z10_Tool_Hammer` (16).
- **Acabado:** perfiles low-poly extruidos con volumen; posiciones y orientación en el pegboard conservadas.
- **QA:** PASS, 0 errores / 8 warnings.
- **Render:** `docs/fm_z10_tools.png` (EEVEE 128, 900×700, 35 mm).
- **Estado:** 1.335 objetos, 350 props.

## Validación Godot del piloto Z10 (2026-11-06)

- Escena de prueba: `scenes/fm/fm_pilot_test.tscn`; script `scripts/fm/fm_pilot_test.gd`; panel de prueba `scripts/fm/fm_pilot_test_panel.gd`.
- Carga del GLB: 524 mallas, 526 nodos, 249 colliders (6 trimesh), ~864 ms; GLB 11,5 MB con texturas WebP calidad 80.
- Pruebas PASS: movimiento, cámara, linterna, interacción, puertas E, paso por el centro y rendimiento.
- Rendimiento: 160,3 FPS promedio a 1280×720 con VSync desactivado en una GTX 1650 Ti; 353 draw calls y 123.812 primitivas en la vista amplia del salón. Es una escena de validación, no el juego completo.
- Hallazgo y corrección: el AABB de `KIT_PILOT_Z10_Portal_E` bloqueaba el hueco de la puerta y el AABB de `PROP_Z10_RiserIdentification` bloqueaba el centro de la sala. Se generalizó con `scripts/fm/fm_glb_collision.gd` (`FMGLBCollision`): trimesh para `PORTAL`/`FRAME`/`DOORFRAME`/`RISERIDENTIFICATION` y para AABB >8 m³ con >300 vértices; el resto usa cajas deduplicadas.
- Bins vacíos `PROP_Z10_Bin_0..3` eliminados; Blender quedó con 1.359 objetos.
- Luces: se añadió `KIT_PILOT_Z10_Emergency_Ceiling` (QA PASS 0/2) y la escena de prueba incluye las tres luces de emergencia, incluida `EmergencyService` en (51, 3.805, -19).
- Informe: `docs/FM_PILOT_Z10_GODOT_VALIDATION.md`.

## Recepción R1 (2026-11-08)

- Nueva colección `L1_RECEPTION_R1`: **138 objetos** (133 mallas + 5 luces); escena **1.497 objetos**.
- R1 cierra techo, vigas, HVAC, bandejas, rociadores, luminarias, zócalos, columnas, entrada/vestíbulo, compuerta/plataforma de extracción, arco de decontaminación y walkway. Sin props ni lógica de extracción.
- La extracción se desplazó **−4,0 m en X**: compuerta −100..−88, decon −96..−92, walkway −97..−91, centrada en x=−94. La columna de −90 ya no bloquea el eje.
- **QA: PASS, 0 errores / 191 warnings aceptados** (UV solapada en cajas con materiales sólidos, back-to-back internos, walkway hundido 5 mm).
- Renders Workbench: `docs/fm_recepcion_r1_wide_wb.png`, `docs/fm_recepcion_r1_entrance_wb.png`, `docs/fm_recepcion_r1_extraction_wb.png`.
- Informe: `docs/FM_RECEPTION_R1.md`. Próximo: R2, mobiliario y señalización.

## Recepción R2 (2026-11-08)

- Colección `L1_RECEPTION_R2`: **112 objetos**; escena **1.609 objetos**; `dirty=False`.
- **QA R2: PASS, 0 errores / 145 warnings** (UV solapada y caras internas back-to-back aceptadas para blockout).
- Mobiliario: mostrador principal con dos monitores/teclado/CPU/silla, control de seguridad con barrera y cámara, dos bancos de espera, mesa baja, reloj, banco de seis taquillas verdes, cuatro stanchions y papelera.
- Renders Workbench: `docs/fm_recepcion_r2_wide_wb.png` y `docs/fm_recepcion_r2_desk_wb.png`.
- Revisión visual: la sala funciona como recepción amueblada, pero la escala de 40×32 m la hace parecer una nave industrial; los dos cuerpos del mostrador forman una L incompleta; las placas siguen lisas.
- Pendiente R2.2: unir el mostrador en L, añadir particiones/alfombra/techo local para reducir escala, señalización con texto, reincorporar reloj/rejillas/extintor y ajustar la iluminación local.
- Informe: `docs/FM_RECEPTION_R2.md`.

### Recepción R2.2 (2026-11-08)

- Retorno en L del mostrador, soffit de 10 × 6 m con cuatro downlights cálidos, alfombra y jardinera en la espera.
- QA PASS 0 errores / 155 warnings aceptados; `L1_RECEPTION_R2` 126 objetos; escena 1.623; `dirty=False`.
- Renders: `docs/fm_recepcion_r2_wide_wb.png`, `docs/fm_recepcion_r2_desk_wb.png`.
- Pendiente: señalización con texto, composición fina y materiales/iluminación finales.
- Informe: `docs/FM_RECEPTION_R2.md`.

## Recepción R2.3 (2026-11-08)

- Señalización física: RECEPCIÓN (entrada y soffit), EXTRACCIÓN, TAQUILLAS y DESCONTAMINACIÓN; wayfinding central hacia la compuerta.
- QA combinado R1+R2: **PASS, 0 errores / 329 warnings aceptados**.
- `L1_RECEPTION_R2`: **136 objetos**; escena **1.632 objetos**; `dirty=False`; sin objetos temporales.
- Renders: `docs/fm_recepcion_r2_wide_wb.png`, `docs/fm_recepcion_r2_desk_wb.png`, `docs/fm_recepcion_r2_entrance_wb.png`.
- El cartel de SEGURIDAD queda pendiente de reincorporar sobre el mostrador de seguridad.
- Informe: `docs/FM_RECEPTION_R2.md`.

## Recepción R3.1 (2026-11-08)

- Añadidos apliques de emergencia en la cabecera de la compuerta y en la viga de descontaminación, dos luces rojas y placa de seguridad.
- QA combinado R1+R2+R3: PASS 0 errores / 332 warnings aceptados.
- Escena: 1.638 objetos; `L1_RECEPTION_R3`: 6 objetos; `dirty=False`.
- Renders: `docs/fm_recepcion_r3_extraction_wb.png`, `docs/fm_recepcion_r3_security_wb.png`.
- El texto SEGURIDAD como FONT no se renderiza de forma fiable; se resolverá con placa/decals UV en R3.2.

## Recepción R3.2 (2026-11-08)

- Cartel SEGURIDAD texturizado y montado con soporte oculto; SALIDA retirado por redundante/oculto; decals hand/puddle.
- QA combinado R1+R2+R3: PASS 0 errores / 336 warnings aceptados; 266 mallas; 1.642 objetos; R3 10 objetos; `dirty=False`.
- Render: `docs/fm_recepcion_r3_security_text.png`.
- Pendiente: R4 Godot.

## Recepción R4 — Validación Godot (2026-11-08)

- `assets/models/fm/reception_r4.glb`: 310 objetos, **1,25 MB** WebP 80.
- Godot: 292 mallas, 102 colliders (3 trimesh), 486 objetos; carga 203 ms ventana / 96 ms headless.
- PASS: movimiento 6,80 m, piso, linterna, extracción z=39,46, `RECEPTION_AUTOTEST_OK`.
- 239,8 FPS promedio (194/273), 29 draw calls, 15.528 primitivas, 419 objetos en escena de validación.
- Pendientes: lookdev final, compuerta con detalle, lógica de extracción, narrativa y multijugador.
- Informe: `docs/FM_RECEPTION_R4_GODOT.md`.

## Recepción R5 — Paridad con Z10 (2026-11-08)

- 10 props industriales Z10 reutilizados; QA **PASS 0/351**; 276 mallas; escena 1.652 objetos.
- GLB `reception_r5.glb`: 307 objetos, **2,67 MB** WebP 80; 10 nodos `PROP_REC05_*` confirmados.
- Godot: 291 mallas, 107 colliders, 488 objetos; **239,9 FPS**; movimiento 6,80 m, linterna, extracción z=39,46; `RECEPTION_AUTOTEST_OK`.
- Misma fase/estándar que Z10, no conteo exacto. Informe: `docs/FM_RECEPTION_R5_PARITY.md`.

## Seguridad 03 R1 (2026-11-08)

- Sala 34×26 m, altura 4,8 m; 6 columnas; puertas sur/norte; techo reconstruido 34×26×0,2 en (−88,23,4,8) y enlazado a `L1_SECURITY_R1`.
- 7 luminarias de techo frías; QA **PASS 0 errores / 23 warnings**; escena 1.673 objetos.
- Render: `docs/fm_security_r1_wide_wb.png`. R1 es estructura/techo/luces; R2 añadirá checkpoint, centro de operaciones, briefing y lockers.
- Informe: `docs/FM_SECURITY_R1.md`.

## Seguridad 03 R2.0 — Checkpoint (2026-11-08)

- `L1_SECURITY_R2`: **26 objetos**; QA **PASS 0 errores / 12 warnings**; escena **1.701 objetos**.
- Checkpoint sur: panel trasero con cartel **SEGURIDAD** texturizado, mostrador de pie dañado, monitor muerto con pantalla, teclado, lector, barrera con cinta roja, panel de techo caído, agua, 6 escombros y emergencia roja.
- Iluminación piloto: 7 luces generales apagadas, 7 paneles muertos, 3 emergencias rojas; solo la recepción mantiene luz general.
- Render: `docs/fm_security_r2_checkpoint_text.png` (EEVEE 64, 1280×720).
- Informe: `docs/FM_SECURITY_R2.md`. Pendiente R2.1: centro de operaciones, briefing, lockers y hatch este.

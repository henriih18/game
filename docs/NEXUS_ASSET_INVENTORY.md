# FRECUENCIA MUERTA — Inventario de assets utilizados

Última actualización: 2026-11-03 15:36 COT.

## Alcance

Integración de la biblioteca local `assets/` en el nivel V05 de NEXUS. Se usaron modelos 3D de Poly Haven para reforzar la lectura de almacén, mantenimiento y Nivel 1 (recepción, oficina, aseo, vestuarios, seguridad, control, corredor y almacén). La extracción final está en la recepción; desde v137 el ascensor **SALIDA** tiene una cabina transitable detrás del muro y puertas animadas, y desde v138 la zona de extracción válida es la recepción completa de 16 × 10 m para hasta 8 jugadores. No se modificaron, movieron ni renombraron los archivos originales de la biblioteca.

La biblioteca se volvió a inventariar tras las nuevas adiciones del usuario: **1.147 archivos**, **138 modelos** en `assets/Modelos 3D` (4,0 GB), 557 MB de texturas, 78 MB de HDRI, 7,8 MB en `assets/models`, 3,4 MB en `assets/art`, 3,7 MB de audio y 20 KB de shaders. Se revisaron las 138 carpetas de modelos; se seleccionaron 19 tipos para el pase general del Nivel 1 y 8 para almacén/mantenimiento, sin importar el resto de forma indiscriminada. Los 4 tipos usados en la sala de extracción oeste se retiraron al eliminar esa sala; la extracción quedó en el ascensor de recepción, sin assets nuevos. La cabina v137 tampoco usa assets de la biblioteca: su geometría es local. v138 no añade assets: solo redefine la zona de extracción y sus metadatos. La linterna de vista previa también se retiró; el material de la lente se conserva para el equipamiento del jugador.

## Organización modular actual

- Los assets utilizados se conservan en `nexus/compartido/NEXUS_SHARED_ASSETS.blend`: **224 objetos** entre `NEXUS_ASSET_V05`, `NEXUS_ASSET_L1` y `NEXUS_ASSET_L1_REPLACE`.
- `nexus/nivel_01/NEXUS_L1_V05.blend` enlaza esa biblioteca mediante `//../compartido/NEXUS_SHARED_ASSETS.blend`; no guarda una segunda copia local de los 224 objetos.
- `nexus/master/NEXUS_MASTER.blend` enlaza los niveles, núcleo, histórico y assets. La fuente monolítica `FM_NEXUS_V05_level1_v125.blend` permanece intacta como respaldo.
- v125 incorpora además **29 roots de reemplazo** para monitores, herramientas, cuadros eléctricos, lámpara y botella del enfriador, mediante `blender_concept/replace_fictitious_l1.py`. Los blocky originales están ocultos con `replaced_by`, no borrados.
- La división no añadió ni sustituyó assets. `nexus/manifest.json` y `nexus/verification.json` documentan los recuentos y la correspondencia exacta con v125.

## Assets importados

| Asset | Archivo fuente | Uso | Objetos en escena |
|---|---|---|---|
| `industrial_storage_cart` | `assets/Modelos 3D/Mobiliario y almacenamiento/industrial_storage_cart_2k/industrial_storage_cart_2k.blend` | Carro de carga en almacén y carro de servicio en mantenimiento | 2 copias |
| `plastic_crate_01` | `assets/Modelos 3D/Mobiliario y almacenamiento/plastic_crate_01_1k/plastic_crate_01_1k.blend` | Caja sobre el carro del almacén | 1 |
| `cardboard_box_01` | `assets/Modelos 3D/Objetos pequeños y narrativa ambiental/cardboard_box_01_2k/cardboard_box_01_2k.blend` | Caja de cartón en el suelo del almacén | 1 |
| `Barrel_02` | `assets/Modelos 3D/Objetos pequeños y narrativa ambiental/Barrel_02_2k/Barrel_02_2k.blend` | Barril junto a la zona de carga | 1 |
| `metal_toolbox` | `assets/Modelos 3D/Objetos pequeños y narrativa ambiental/metal_toolbox_2k/metal_toolbox_2k.blend` | Caja de herramientas sobre el banco de mantenimiento | 1 |
| `caged_hanging_light` | `assets/Modelos 3D/Infraestructura industrial y mantenimiento/caged_hanging_light_2k/caged_hanging_light_2k.blend` | Luminaria colgante de jaula en mantenimiento | 1 |
| `power_box_01` | `assets/Modelos 3D/Infraestructura industrial y mantenimiento/power_box_01_2k/power_box_01_2k.blend` | Cuadro eléctrico en la pared sur de mantenimiento | 1 |
| `korean_fire_extinguisher_01` | `assets/Modelos 3D/Infraestructura industrial y mantenimiento/korean_fire_extinguisher_01_2k/korean_fire_extinguisher_01_2k.blend` | Extintor en mantenimiento | 1 |
| `small_plastic_torch_2k` | `assets/Modelos 3D/Objetos pequeños y narrativa ambiental/small_plastic_torch_2k.blend/small_plastic_torch_2k.blend` | Linterna de mano exportada a `assets/models/fm/flashlight_nexus.glb` (1.272.372 B) para el viewmodel de Godot; no se instancia en la escena de Blender. Mide 0,10 × 0,227 × 0,055 m | 0 en Blender; 1 GLB en Godot |
| `wooden_crate_01_2k` | `assets/Modelos 3D/Objetos pequeños y narrativa ambiental/wooden_crate_01_2k/wooden_crate_01_2k.blend` | Cajas de madera de la sala de extracción oeste; retiradas con la sala el 2026-11-03 | 0 |
| `utility_box_01_2k` | `assets/Modelos 3D/Infraestructura industrial y mantenimiento/utility_box_01_2k/utility_box_01_2k.blend` | Armario eléctrico retirado con la sala oeste; el tipo sigue en los paneles del corredor/control bajo `NEXUS_ASSET_L1R_` | 0 (en la sala) |

Además del contenido de los assets, la colección `NEXUS_ASSET_V05` contiene los empties raíz, el cable de la luminaria y una luz puntual de 55 W. Total actual: 26 objetos.

## Colocación verificada

### Almacén

- Carro industrial: `(2,15, −2,65)`, girado 90°. Huella aproximada x 1,599..2,701, y −3,452..−1,848, base z −5,65.
- Caja plástica sobre el carro: base z −4,27; huella x 2,001..2,299, y −3,154..−2,746.
- Caja de cartón: `(2,95, −8,20)`, girada −16°. Huella x 2,685..3,199, y −8,533..−7,931, base z −5,65. Queda separada de la estantería sur (frente y −8,92) y del borde sur de la puerta de carga (y −7,8).
- Barril: `(3,35, −2,58)`, girado 11°. Huella x 3,064..3,636, y −2,864..−2,296, base z −5,65.

### Mantenimiento

- Caja de herramientas sobre el banco: `(6,55, −6,55)`, girada 90°, base z −4,75.
- Carro industrial: `(8,90, −7,15)`; huella x 8,098..9,702, y −7,701..−6,599.
- Luminaria de jaula: `(9,50, −5,00)`, centro z −1,90; cable de 0,63 m hasta el techo; luz puntual de 55 W, color cálido, radio 0,16.
- Cuadro eléctrico: `(9,00, −9,55)`, girado 180°, centro z −3,40; cara posterior a 1 cm de la pared sur.
- Extintor: `(10,00, −9,05)`, girado 6°, base z −5,65.

### Extracción en la recepción (v136–v138)

- La sala de extracción oeste de v135 se retiró: se borraron sus 118 objetos, se restauró el muro `NEXUS_V05_CORR_END_-22` y se ocultaron los rótulos **SALIDA** del corredor. Los cuatro tipos de assets de esa sala (`wooden_crate_01_2k`, `barrel_03_2k`, `utility_box_01_2k` y el extintor) quedaron fuera de la escena o volvieron a su uso anterior.
- La extracción está ahora en la recepción, con el ascensor **SALIDA** como salida visual: `NEXUS_V05_REC_EXTRACT_ZONE` en `(-17.5, 10.7, -5.65)`, anillo naranja, texto de suelo **EXTRACCION** y consola mural en `(-15.10, 11.445, -4.28)`. En v138 la zona válida pasó a ser la recepción completa de **16 × 10 m** (hasta 8 jugadores), no el lobby de 2,10 × 1,50 m. No requiere assets de la biblioteca.
- v137 abrió un hueco de 1,88 × 2,625 m en el muro norte y construyó una cabina transitable de 1,88 × 1,80 × 2,55 m con espejo ahumado, pasamanos, luz de techo de 45 W, umbral, bolsillos y panel interior. Las puertas existentes se animaron en X: cerradas en frames 1/130, abiertas en 45/105; la secuencia ocupa 1–160. Los originales (muro, marco, zócalo y remate) quedaron ocultos en `NEXUS_V05_ELEVATOR_HIST`.
- La activación de la extracción en la cabina usa `NEXUS_V05_REC_EXTRACT_CAB_TRIGGER`, hijo de la zona; sigue siendo geometría y metadatos, sin lógica de juego exportada.
- La estación de café `NEXUS_L1_DIS_BREAK_*` se desplazó 1,8 m al sur para despejar el frente del ascensor; conserva `original_location` y `layout_fix="elevator_extraction_clear"`.

## Nivel 1 (V05): pase de assets

### Assets utilizados

| Asset | Tipo | Uso | Copias |
|---|---|---|---:|
| `CoffeeCart_01_4k` | Mobiliario | Carrito de café vintage; **oculto y sustituido** por una estación moderna | 1 |
| `SchoolChair_01_2k` | Objetos | Sillas de espera, escritorio, seguridad, control y oficina | 9 |
| `metal_office_desk_2k` | Mobiliario | Escritorio de oficina, dos mesas de seguridad, mesa de control y mostrador de café | 5 |
| `wall_clock_1k` | Objetos | Relojes de recepción y oficina | 2 |
| `vintage_stapler_2k` | Objetos | Grapadora sobre el mostrador de recepción | 1 |
| `clipboard_1k` | Objetos | Portapapeles de recepción y oficina | 2 |
| `classic_laptop_2k` | Objetos | Portátil vintage; **oculto**; la oficina usa el equipo existente | 1 |
| `WetFloorSign_01_1k` | Arquitectura | Señales de suelo mojado en aseo, vestuarios y corredor | 3 |
| `cleaner_tin_01_1k` | Objetos | Cubo de limpieza vintage; **oculto** | 1 |
| `garden_gloves_01_1k` | Objetos | Guantes sobre el banco de vestuarios | 1 |
| `fishermans_hat_1k` | Objetos | Sombrero sobre el banco de vestuarios | 1 |
| `trashbag_1k` | Objetos | Bolsa de basura en vestuarios | 1 |
| `barrel_03_2k` | Objetos | Barriles del almacén | 3 |
| `wooden_crate_02_2k` | Objetos | Caja sobre el palé del almacén | 1 |
| `industrial_pastic_container_2k` | Mobiliario | Contenedor industrial en el almacén | 1 |
| `plastic_container_1k` | Mobiliario | Contenedor plástico en el almacén | 1 |
| `tool_cart_2k` | Mobiliario | Carro de herramientas en mantenimiento | 1 |
| `fire_alarm_2k` | Infraestructura | Alarmas en mantenimiento y corredor | 2 |
| `industrial_wall_lamp_1k` | Objetos | Lámparas de pared del corredor | 4 |

Total: **40 instancias**, **40 roots**, **90 mallas** y **130 objetos** en `NEXUS_ASSET_L1`. Los cuatro tipos de la sala de extracción oeste ya no están en escena. El mostrador de café es una copia adicional del escritorio metálico en `NEXUS_L1_DISASTER`, no forma parte de ese recuento. Las posiciones y rotaciones exactas están en `blender_concept/assets_level1.py`, `blender_concept/assets_level1_desks.py`, `blender_concept/level1_abandoned_pass.py`, `blender_concept/fix_extraction_elevator_v136.py` y `blender_concept/build_elevator_simulation_v137.py`.

### Reemplazos y originales conservados

- Recepción: ocultos `REC_WAIT_0/1/2`, `REC_OFFICE_CHAIR` y `REC_COFFEE`; se conservaron el mostrador NEXUS, la mesa de centro, el banco y la carpeta.
- Oficina: ocultos `OFFICE_DESK_TOP`, sus patas y `OFFICE_CHAIR`; el teclado, monitor, soporte, teléfono y papeles se subieron 0,15 m para apoyar en la mesa nueva.
- Seguridad: ocultos `SEC_DESK`, `_FRONT_S`, `_LEG_0..3`, `_SIDE_E/W` y `SEC_CHAIR_A/B`; los monitores se elevaron 0,078 m.
- Control: ocultos todos los `ACC_CONSOLE*` y `ACC_CHAIR_A/B`; los objetos de consola bajaron 0,012 m y las sillas se alinearon a x 12,25 y 13,75.
- Ningún original se borró: todos conservan `hide_render=True`, `hide_viewport=True` y la propiedad `replaced_by`.

### Pase de abandono y desorden (v124)

- La colección `NEXUS_L1_DISASTER` contiene **226 objetos** con prefijo `NEXUS_L1_DIS_`. Es un pase idempotente: el script elimina y recrea esa colección en cada ejecución.
- Recepción: sillas caídas, papeles, sangre seca, monitor plano roto, papelera volcada y estación de café moderna.
- Seguridad: silla caída en `(5.0, 4.4)`, monitor caído, papeles y sangre.
- Control: silla caída, monitor caído, papeles y sangre.
- Oficina: silla caída, papeles, binder, monitor roto, huella de mano en la pared este y mancha de sangre sobre el escritorio.
- Aseo: papelera volcada, toallas, mopa, cubo, spray, agua y extractor de pared.
- Corredor: silla caída, señal de suelo mojado caída, panel inclinado, cable colgante, escombros, cristales, papeles y sangre.
- Almacén: barril volcado, caja derramada, latas y derrame.
- Mantenimiento: aceite, carro volcado, tubería caída y papeles.
- Los assets vintage `CoffeeCart_01_4k`, `classic_laptop_2k` y `cleaner_tin_01_1k` quedaron ocultos con `replaced_by`; no se borraron. La estación de café moderna se construyó duplicando `metal_office_desk_2k` y añadiendo cafetera, pantalla, surtidor, bandeja, vasos y papelera.
- Auditoría de desastre: **0 objetos bajo el suelo**; 34 objetos elevados son ensamblajes intencionales (estación de café, binder/portalápices, sangre/huella en pared o escritorio, extractor, tubería, huellas, cable); los 4 objetos en x≈23–24 están sobre `NEXUS_LINK_L1_FLOOR`, no fuera del nivel.

### Cámaras corregidas

- Recepción: `(-8,30, 3,20, -4,25)` → `(-14,20, 8,20, -4,35)`, lens 20.
- Aseo: `(-7,95, 4,32, -4,05)` → `(-4,95, 2,65, -4,35)`, lens 18.
- Corredor: `(-20,50, 0,00, -4,15)` → `(0,00, 0,00, -4,15)`, lens 20.

### Verificación

- Renders revisados: recepción, oficina, seguridad, control, vestuarios, almacén, mantenimiento, corredor y aseo. En v124 se repitieron recepción, oficina y seguridad tras los últimos ajustes; la silla caída de seguridad, el monitor plano de recepción y las manchas de oficina ya son visibles.
- Auditoría AABB de los 37 roots iniciales: **0 solapes > 0,015 m³**.
- Auditoría AABB de las 27 mallas nuevas de escritorio: **0 solapes > 0,01 m³**.
- Auditoría AABB global final: **40 roots** contra **1.229 mallas** de `V05_PROPS`, `V05_STORY`, `NEXUS_ASSET_V05` y `NEXUS_V05_SERVICE_CONN`; **0 solapes > 0,01 m³**. Los apoyos revisados coinciden con suelo, palé, banco o pared, sin flotantes.
- Auditoría del pase de desastre: **0 objetos bajo el suelo**; 34 elevados intencionales; 4 objetos sobre el link L1. Solape mínimo monitor/silla ≈0,00228 m³, sin penetración visual relevante; papelera separada de la pata del banco.
- Contactos corregidos: grapadora, sombrero, caja del palé, contenedor plástico del almacén, señales de suelo, monitor de recepción, papelera y silla de seguridad.
- Oficina ≈10,9 m², radio libre ≈0,73 m; aseo ≈10,3 m², radio libre ≈1,05 m; puertas de 0,90 m y 2,08 m de alto. El aseo ya tiene extractor de pared, pero no un sistema HVAC completo. La propuesta de subir las puertas a ≈2,60 m sigue pendiente de autorización.

### Rendimiento

- v124: **7.760 objetos**, **52 colecciones**, **137 materiales**, **30 cámaras**, **295 luces**, **226 objetos de desastre**.
- Triángulos de malla visibles en v124: **750.632** sobre 5.795 mallas. La progresión fue 673.792 en v118 (pase de assets), 750.632 en v124 (pase de desastre, estación de café y sillas adicionales). Una medición intermedia de 506.468 no contaba todas las instancias compartidas y queda descartada.
- Los assets del Nivel 1 son de alta densidad; `metal_office_desk_2k` aporta 6.898 triángulos por instancia y `SchoolChair_01_2k` 5.072. El coste agregado es considerable para la GTX 1650 Ti y exige LOD/optimización antes de exportar.

### Pase de recepción, circulación y extracción (v126–v138)

- Codebuff añadió en v126–v127 materiales PBR de recepción, servicios de techo, mostrador, luces de emergencia, cinco recuperables, escondite, puerta con pivote y trampa sonora; también aplicó LOD en las mallas compartidas. La recepción visible bajó de 100.628 a **74.280 triángulos**.
- OpenCode añadió en v129 la linterna `small_plastic_torch_2k` y la extracción provisional, con 14 objetos nuevos y 90 objetos en `NEXUS_V05_REC_PLAY`. La linterna se retiró después (2026-11-03 14:05) para entregarla al jugador al ingresar.
- v130 anidó `NEXUS_V05_REC_PASS126` (162 objetos), `NEXUS_V05_REC_LOD1` (5) y `NEXUS_V05_REC_PLAY` dentro de `NEXUS_L1_V05`, para que el máster enlazado las reciba. L1 pasa a **2.389 objetos** y el máster a **8.063**; los 2.389 objetos de L1 coinciden con el máster sin diferencias de matriz o visibilidad.
- v132 ocultó de forma reversible el banco duplicado de la entrada y sus cuatro patas, que cerraba la recepción: `NEXUS_V05_REC_BENCH2` y `NEXUS_V05_D_REC_BENCH2_LEG_0_0`, `_0_1`, `_1_0`, `_1_1`. Conservan `original_location`, `circulation_fix` y `replaced_by`; no se borró mobiliario. v131 se rechazó por solapar con las tres sillas de la pared oeste.
- v133 desplazó la mesa de centro y sus patas 3,1 m al oeste y la silla caída B 1,2 m al este para abrir el pasillo de entrada al mostrador. Los objetos guardan `original_location` y `circulation_fix="reception_v133_clear_aisle"`.
- v134 ocultó reversiblemente `NEXUS_V05_ACC_BARRIER_1` y `NEXUS_V05_ACC_POST_1`, que cerraban el vano útil del arco detector. Conservan `original_location`, `original_hide_render`, `original_hide_viewport`, `checkpoint_state` y `circulation_fix="control_v134_clear_detector_lane"`; no se borró nada.
- v135 construyó una sala de extracción de 6 × 6 m en el extremo oeste del corredor; el usuario rechazó esa ubicación. En v136 se borraron sus **118 objetos**, se restauró `NEXUS_V05_CORR_END_-22`, se ocultaron los rótulos **SALIDA** del corredor y se retiraron los cuatro tipos de assets de la sala.
- v136 trasladó la extracción al ascensor **SALIDA** de recepción, junto al reloj: `NEXUS_V05_REC_EXTRACT_ZONE` en `(-17.5, 10.7, -5.65)`, inicialmente 2,10 × 1,50 m y activación de 10 s, con aro naranja, texto de suelo **EXTRACCION** y consola mural en `(-15.10, 11.445, -4.28)`. La estación de café se desplazó 1,8 m al sur. En v138 el volumen válido pasó a la recepción completa de 16 × 10 m, 1–8 jugadores, activación 2,0 s y secuencia total 8,7 s.
- v137 construyó la cabina real detrás del muro (1,88 × 1,80 × 2,55 m), con espejo ahumado, pasamanos, luz de techo de 45 W, umbral, bolsillos y panel interior. Las puertas existentes se animaron en X (cerradas en frames 1/130, abiertas en 45/105; escena 1–160). El muro, marco, zócalo y remate originales quedaron ocultos en `NEXUS_V05_ELEVATOR_HIST`; la cabina nueva está en `NEXUS_V05_ELEVATOR` con 50 objetos. El trigger de cabina es `NEXUS_V05_REC_EXTRACT_CAB_TRIGGER`, hijo de la zona de extracción.
- La auditoría con cápsula de 0,38 m verifica **todos** los objetivos: entrada, mostrador, ala oeste, seguridad, vestuarios, almacén, mantenimiento, control recto antes/después del arco, escritorio, enlace restringido, extremo oeste por el carril sur, los cuatro puntos de la extracción del ascensor y ahora **el centro y el fondo de la cabina** (`elevator_car_center` y `elevator_car_back`, 21 waypoints). El carril norte del extremo oeste queda bloqueado por el derrumbe y se acepta como restricción narrativa. Detalle en `docs/NEXUS_L1_CIRCULATION_AUDIT.md`.
- v138 no cambia la geometría: añade el empty `NEXUS_V05_REC_EXTRACT_RECEPTION_TRIGGER` y redefine la zona como `reception_room` de 16 × 10 m, con activación de 2,0 s, secuencia total de 8,7 s y capacidad de 1–8 jugadores. Los cinco recuperables reciben rareza, clase de tamaño, volumen aproximado, estado, efectos y `disassemblable=False`.
- Medición actual de L1: **560.493 triángulos visibles** en **1.921 objetos de malla**; **49 luces visibles**, 22 con sombra (63 totales). L1 queda en **2.441 objetos / 2.569.121 B** y el máster recargado en **8.115**.
- `nexus/manifest.json` se regeneró con los recuentos actuales. El máster conserva 398.478 bytes porque enlaza datos, no los duplica.

### Limitaciones

- El mostrador de recepción, la mesa de centro, el banco, las taquillas y las estanterías industriales siguen siendo geometría blocky; se conservaron porque su tamaño o función no encajaba con los assets disponibles.
- El aseo tiene un extractor de pared añadido en v124, pero no un sistema HVAC completo.
- Las puertas de salas y las barreras siguen siendo geometría estática sin interacción. Las puertas del ascensor tienen animación en Blender, pero todavía no hay controlador que las active desde el juego.
- La linterna de vista previa fue retirada de Blender; en Godot se añadió un viewmodel desde `flashlight_nexus.glb` y `FMPlayer` conserva batería, consumo y recarga. La escena `reception_slice.tscn` ya la instancia para el jugador local.
- La zona de extracción es la **recepción completa de 16 × 10 m** (v138), con capacidad de **1–8 jugadores**, activación de **2,0 s** y secuencia total de **8,7 s**; el ascensor **SALIDA** y su cabina son la salida visual. La escena local `reception_slice.tscn` implementa la activación, la entrega, las puertas y el resultado para **1 jugador**; la sincronización de 8 jugadores sigue pendiente. La cabina v137 y sus puertas animadas son datos de Blender, animados en Godot mediante `animate_elevator_doors`.
- Las puertas de oficina/aseo de 2,08 m impiden el paso de criaturas de 2,2–2,5 m; la propuesta de subirlas a ≈2,60 m no está ejecutada.
- El arte sigue siendo provisional. La recepción sí se exportó a Godot como GLB local (`reception_nexus.glb`) y tiene escena jugable; no se ha generado un build final ni se ha exportado el complejo completo.

## Materiales y texturas

- `NEXUS_Concrete`, `NEXUS_Concrete_Dark` y `NEXUS_Painted_Metal` ya usaban texturas 1K de `assets/art/fm` (`concrete_wall_albedo/roughness/normal`, `metal_panel_*`). No se sustituyeron.
- `NEXUS_V05_MAT_Floor_Worn` se creó a partir de `assets/texturas/Suelos/worn_concrete_floor_2k` (diffuse, roughness y normal). Usa Texture Coordinate Object, proyección X/Y, Mapping con escala **0.30**, nodo `ShaderNodeHueSaturation` llamado `V05_DARKEN` con saturación **0.35** y valor **0.16**, y Normal Map a **0.75**. Se aplicó a 9 suelos V05: recepción, corredor, seguridad, control, vestuarios, almacén, mantenimiento, conector y link L1.
- HDRI `assets/HDRI/Instalaciones industriales y abandonadas/abandoned_workshop_2k.hdr` aplicado al mundo `World` con fuerza **0.02**. Se conservó el nodo `Principled Volume` existente (densidad 0.0035) y el tone mapping AgX con exposición 1.5.
- Se añadieron `NEXUS_L1_MAT_Blood`, `NEXUS_L1_MAT_Blood_Dark` y `NEXUS_L1_MAT_Mirror`. El espejo del aseo usa este último.
- Los modelos importados conservan sus materiales y texturas PBR originales dentro de las carpetas de cada asset. No se importaron otras texturas sueltas ni se modificaron los archivos de la biblioteca.
- **Defecto de origen pendiente:** `industrial_wall_lamp_glass_rough_1k.png` e `industrial_wall_lamp_glass_alpha_1k.png`, dentro de `industrial_wall_lamp_1k.blend/textures/`, son archivos JSON de error 500 de 81 bytes y no imágenes válidas. Se detectó al renderizar el máster modular; no es una regresión de la división. No se sobrescribieron los originales.

## Licencias

Los archivos siguen la convención de nombres de Poly Haven. No se encontraron archivos de licencia o readme dentro de `assets/`. Antes de distribuir el juego hay que confirmar y documentar la licencia de cada recurso. Los objetos y empties guardan la propiedad `asset_license` con la advertencia correspondiente.

## Rendimiento

Los assets son de alta densidad: carro ≈18,9k triángulos, caja de cartón ≈16,9k, caja plástica ≈18,3k, caja de herramientas ≈14,2k, luminaria ≈22,9k, cuadro eléctrico ≈21,3k y extintor ≈9,9k. La escena base tenía ≈286.742 triángulos visibles; v110 medía **430.848** con el bloque de almacén/mantenimiento; v118 midió **673.792** tras el pase de assets y v124 midió **750.632** tras el pase de abandono. El pase de recepción y su LOD redujeron L1 a **570.777 triángulos visibles** (v130). Tras ocultar el banco de entrada, la barrera y el poste de control, retirar la linterna de vista previa, eliminar la sala de extracción oeste y añadir la cabina de ascensor v137, el archivo vivo mide **560.493 triángulos visibles** en **1.921 mallas** y **49 luces visibles**. v138 no cambia la geometría: añade un empty de trigger y redefine la extracción, por lo que el archivo vivo queda en **2.441 objetos / 2.569.121 B / máster 8.115**. La comparación estructural v125/máster registra **761.932 triángulos de malla en toda la escena original**, incluida geometría histórica/oculta, por lo que no es directamente comparable con el subconjunto visible del Nivel 1. Sigue siendo necesario medir el máster completo y planificar LOD/optimización antes de exportar.

## Archivos y versiones

- Scripts monolíticos históricos: `blender_concept/assets_v05.py`, `assets_level1.py`, `assets_level1_desks.py`, `level1_abandoned_pass.py` y `replace_fictitious_l1.py`. No reejecutarlos sobre los archivos modulares sin adaptar sus rutas y revisar duplicados.
- Pase de assets: `FM_NEXUS_V05_level1_v115.blend` a `v118`; pase de abandono: `v119` a `v124`; reemplazos ficticios y respaldo fuente actual: **`v125`**.
- Estructura activa: **`nexus/master/NEXUS_MASTER.blend`** para el conjunto y `nexus/nivel_01/NEXUS_L1_V05.blend` para editar el Nivel 1. Assets comunes: `nexus/compartido/NEXUS_SHARED_ASSETS.blend`.
- Archivo vivo de recepción, circulación y extracción: `nexus/nivel_01/NEXUS_L1_V05.blend` (**2.569.121 B, 2.441 objetos**), con linterna retirada, extracción en la recepción completa, ascensor con cabina animada v137 y reglas de extracción v138. Manifest: L1 2.441 objetos; máster 8.115. Checkpoint anterior v134: `NEXUS_L1_V05_control_v134.blend` (2.874.332 B, 2.389 objetos); anteriores: v133 (2.873.657 B), v132 (2.873.000 B), v131 (rechazada), v130, v129, v128 y v127 en la misma carpeta. El usuario pidió guardar en sitio y no crear más archivos de recepción.
- Scripts de recepción y circulación: `reception_pass_v129_flashlight.py`, `audit_reception_v129.py`, `bind_l1_collections_v130.py`, `reception_fix_circulation_v131.py` (rechazado), `reception_fix_circulation_v132.py`, `reception_fix_circulation_v133.py`, `control_checkpoint_fix_v134.py`, `build_extraction_room_v135.py` (sala rechazada), `fix_extraction_elevator_v136.py`, `build_elevator_simulation_v137.py`, `apply_extraction_rules_v138.py`, `audit_l1_pathgrid.py` y `refresh_nexus_manifest.py`. El script v129 parte de v128 y no debe confundirse con el pase de mecánicas v127. El procedimiento de extracción está en `docs/NEXUS_L1_EXTRACTION_PROCEDURE.md`.
- Scripts de la división: `blender_concept/split_nexus_levels.py` y `blender_concept/verify_nexus_split.py`. El primero recrea los archivos generados desde v125; no usarlo para fusionar trabajo posterior.
- Checkpoints previos: `v109` y `v110` (almacén/mantenimiento) y `v114` (conector de servicio). v108 es defectuoso y no debe usarse.

## Texturas y HDRI utilizados

Se revisaron las texturas PBR de `assets/texturas/` (hormigón, metal, pintura, suciedad y suelos) y los 12 HDRI 2K de `assets/HDRI/`. En v124 se usan `worn_concrete_floor_2k` para los suelos V05 y `abandoned_workshop_2k` como HDRI de mundo a fuerza 0.02. El resto de texturas y HDRI queda disponible para futuras salas, pero no se importó de forma indiscriminada. No se usaron assets de vegetación ni rocas en interiores.

## Recepción local en Godot

- Escena: `scenes/fm/reception_slice.tscn`; lógica: `scripts/fm/reception_slice.gd`, `scripts/fm/fm_reception_extraction.gd` y `scripts/fm/fm_reception_loot.gd`.
- GLB de arte: `assets/models/fm/reception_nexus.glb` (13.446.520 B, 640 meshes, 69 imágenes WebP, 2 animaciones, 14 luces), cargado en runtime con `GLTFDocument`.
- Viewmodel: `assets/models/fm/flashlight_nexus.glb` (1.272.372 B), exportado desde `small_plastic_torch_2k`; se instancia en `FMPlayer` al entrar en la recepción.
- Audio: `assets/audio/ambience/ambience.wav` en bucle 3D; `Audio.stop_music()` evita que siga la música del menú.
- Pruebas: `tests/fm_reception_smoke.tscn` pasa **PASS**; cubre movimiento, escondite, trampa, rechazo de la caja de 42 kg, recogida, drop/repick, puertas y extracción. Menú `--reception` verificado con **EXIT 0**.
- Limitación: 1 jugador local; la API admite hasta 8, pero no hay red ni inventario general.

## Pendientes

- El cuadro eléctrico se revisó en vista cercana: puerta abierta, bisagras, interruptores y etiqueta visibles; no presenta deformación.
- Auditoría AABB global completada: 0 solapes > 0,01 m³ y sin flotantes en los apoyos revisados. La circulación principal del Nivel 1 ya está auditada con cápsula en `docs/NEXUS_L1_CIRCULATION_AUDIT.md`; el arco de control quedó despejado en v134. Quedan el carril norte del extremo oeste (restricción narrativa aceptada), el interior de vestuarios/almacén/mantenimiento y el núcleo vertical. La extracción es la recepción completa de 16 × 10 m (v138), con capacidad de 1–8 jugadores, trigger de recepción, ascensor/cabina como salida visual y puertas animadas (v137); los triggers existen, pero la lógica de activación de juego sigue pendiente. La BFS ampliada confirma centro de zona, borde norte, consola, aproximación, centro y fondo de la cabina alcanzables.
- LOD de recepción aplicado; falta medir el subconjunto visible del máster completo y de cada nivel antes de exportar, en vez de usar el total histórico como garantía de rendimiento.
- Circulación recepción → corredor → seguridad → control recto → enlace restringido verificada con cápsula. Falta recorrer el interior de vestuarios/almacén/mantenimiento.
- Núcleo vertical: acceso L1 y 18 vuelos verificados analíticamente con cápsula de 0,38 m; holgura lateral mínima 0,32 m y altura libre mínima 5,698 m. Falta iluminación propia en el recinto de la escalera, simulación real de controlador y enlaces L2–L5. Detalle en `docs/NEXUS_CORE_ROUTE_AUDIT.md`.
- El aseo tiene extractor de pared, pero no HVAC completo; valorar si basta para la escala del juego.
- Evaluar texturas y HDRI adicionales solo si aportan una mejora clara y no rompen la iluminación existente.
- Propuesta pendiente de autorización: subir las puertas de oficina/aseo de 2,08 a ≈2,60 m para permitir criaturas de 2,0–2,5 m y seguir excluyendo al Vigilante de 3,0 m.
- Documentar licencias antes de cualquier distribución.

## Nivel 1 completo en Godot (2026-11-03 19:40 COT)

- GLB: `assets/models/fm/level1_nexus.glb`, **42.507.928 bytes**, **1.940 objetos**, **530.249 triángulos**, WebP calidad 70, sin luces ni cámaras.
- Fuente: `nexus/nivel_01/NEXUS_L1_V05.blend`; no se modificó el `.blend`.
- No se añadieron assets externos nuevos. Se reutilizaron la geometría, materiales y texturas del nivel de Blender.
- Texturas de apoyo reutilizadas: `blood_splat.png`, `grunge_decal.png`, `grime_decal.png` y `ambience.wav`.
- Sistemas reutilizados: `fm_player`, `fm_watcher`, `fm_reception_loot`, `fm_reception_extraction`, `fm_hiding_spot`, `fm_noise_trap`, `fm_hud`.
- La escena tiene 20 luces de emergencia, 0 generales, 515 colliders y 5 loot distribuidos.
- Capturas y pruebas en `docs/NEXUS_LEVEL1_GODOT.md`.

---

## Fase 3 Godot: decals y atmósfera (2026-11-03)

No se importaron modelos nuevos. Se reutilizaron texturas locales de `assets/art/fm` para 22 `Decal` de narrativa y desgaste: `blood_splat.png`, `blood_trail.png`, `puddle.png`, `grunge_decal.png`, `grime_decal.png` y `glass_crack.png`. No tienen colisión y usan distance fade 14/6 m para limitar su coste. El pase añade postprocesado, tildes teal de guiado, polvo y vapor; no modifica los assets originales.

## Fase 3A: texturas PBR generadas y pase de recepción/corredor

Se añadieron 10 PNG en `assets/art/fm/generated/` derivados de los EXR locales de Poly Haven: normales de `concrete_floor_01`, `worn_plaster_wall`, `factory_wall`, `rusty_metal_sheet`, `green_metal_rust`, `wooden_crate_01` y `concrete_wall_003`; rugosidad de `worn_plaster_wall`, `rusty_metal_sheet` y `wooden_crate_01`. No se sobrescribió ningún archivo original. Se usaron también JPG 2K de albedo/rugosidad de las mismas familias. El pase de recepción/corredor aplica 31 overrides de material, HDRI local, dos reflection probes y 17 luces artísticas. Documento: `docs/NEXUS_L1_PHASE3A_ART.md`.

## Fase 3A.1: kit de recepción y corredor

Se añadió `assets/models/fm/art3a1/level1_art3a1_kit.glb` (~3,9 MB, 8 mallas fusionadas) generado desde `blender_concept/ART3A1_kit.blend` con `blender_concept/build_art3a1_kit.py`. Incluye mostrador/cristal de recepción, dos tramos de conducto y módulos de pared; reutiliza texturas 2K locales y normales/roughness generadas. No se modificó el GLB jugable original ni el `.blend` L1.

## Fase 3A.2: kit de arquitectura y props del Nivel 1

Se añadieron recursos nuevos generados a partir de Blender y de la biblioteca local, sin descargas externas:

- `blender_concept/LEVEL1_DRESSING.blend` — 1.327 objetos de origen; `blender_concept/build_level1_dressing.py` es reproducible.
- `assets/models/fm/art3a2/level1_dressing.glb` (~12,9 MB, 10 mallas fusionadas por material): vigas, costillas, zócalos, cajas de servicio, conductos, lámparas de jaula, dinteles, directorio de recepción, consola de control, racks, listones de banco y rejillas de corredor.
- `assets/models/fm/props/*.glb` — 15 props con texturas a 1K: `potted_plant`, `utility_box`, `shelves`, `drawer`, `power_box`, `camera`, `fire_alarm`, `medical_box`, `stool`, `chemistry`, `microscope`, `clock`, `crate`, `barrel`, `radio`. Exportados con `blender_concept/export_props.py`.
- Se reutilizaron texturas 2K locales de metal, pintura, hormigón, madera y suelo. No se sobrescribieron assets originales.
- El GLB jugable `assets/models/fm/level1_nexus.glb` y el `.blend` `nexus/nivel_01/NEXUS_L1_V05.blend` permanecen intactos.

## Fase 3A.3: kit de puertas del Nivel 1

Se añadió `assets/models/fm/doors/level1_doors.glb` (~5,3 MB, 116 mallas fusionadas) generado desde `blender_concept/LEVEL1_DOORS.blend` con `blender_concept/build_level1_doors.py` (589 objetos de origen). Incluye seis tipos de puerta con marcos, hojas animables, teclado, sensor, luces de estado y liberación manual. Reutiliza texturas 2K locales de metal oxidado, pintura verde y metal pintado; no se descargaron recursos externos. No se modificó el GLB jugable original ni el `.blend` L1.

## Conector Z10: pase de equipamiento no narrativo (2026-11-06)

- Se añadieron **202 props** en la colección `L1_PROPS_Z10` al archivo `nexus/nivel_01/FM_LEVEL1_V06_ARCH.blend`.
- La mayoría son modelos propios (banco de trabajo, taquillas, cuadro eléctrico, palés, cajas, bobinas, transformador, tuberías, señalización y utillaje).
- Se conservan de la biblioteca externa: estanterías `steel_frame_shelves_01_2k`, bidones `Barrel_02_2k`, armario `utility_box_02_2k` y taburete `metal_stool_01_1k`. Sus materiales y texturas se mantienen dentro de las carpetas de cada asset.
- **Licencias:** siguen la convención Poly Haven, pero no se localizaron archivos de licencia/readme; queda pendiente verificarlas antes de cualquier distribución. No se introdujeron recursos de procedencia desconocida.
- **QA:** PASS, 0 errores, 254 warnings aceptados. Sin z-fighting. Presupuesto del Conector ≈102.000 tris.
- **Renders:** `docs/fm_conector_final_lit.png`, `docs/fm_conector_final_dark.png` y cuatro detalles en `docs/fm_conector_detail_*.png`.
- **Pendiente:** objetos narrativos, interacción, colisiones/navegación, LOD/exportación, pruebas en Godot y verificación de licencias. Sin commit.

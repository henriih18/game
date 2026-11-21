# FRECUENCIA MUERTA — Auditoría de circulación del Nivel 1

Fecha: 2026-11-03.
Ámbito: `nexus/nivel_01/NEXUS_L1_V05.blend` (v138) y verificación en el máster enlazado.
Método: rejilla de accesibilidad 2D + comprobación conservadora de cápsula contra AABB.

## Método

- Radio de jugador: **0,38 m** (diámetro 0,76 m).
- Altura considerada: **1,80 m** sobre el suelo.
- Celda de rejilla: **0,05 m**.
- Se consideran obstáculos las mallas visibles cuyo volumen cruza la franja de suelo +0,16 m a suelo +1,80 m.
- Se excluyen hojas, cristales, manillas y pivotes de puerta porque se asumen operables, incluidas las hojas del ascensor.
- Se excluyen escalones de altura ≤0,16 m.
- El hueco del ascensor se representa con un portal explícito: los AABB de las mallas cortadas (muro, marco, zócalo y remate) cubren el agujero y, sin el portal, cerrarían falsamente la cabina.
- Se excluyen la linterna de vista previa y el aro de extracción, que no son colliders.
- Cota de suelo V05: **−5,65 m**.
- Salida: `nexus/nivel_01/circulation_reachability.json`.
- Script: `blender_concept/audit_l1_pathgrid.py`.

La rejilla es conservadora y sirve para detectar bloqueos, no sustituye una prueba de navegación con la cápsula real de Godot. Un pasillo de una sola celda puede ser válido en el modelo y seguir siendo incómodo en juego.

## Puertas principales

Todas las puertas principales de V05 tienen **1,60 m de paso libre** y **3,07 m de altura** (marco 1,62 × 3,12 m; suelo −5,65; dintel inferior −2,58):

- recepción,
- seguridad,
- control de acceso,
- vestuarios,
- almacén,
- mantenimiento.

Pasan todas las criaturas con las alturas oficiales: Imitador 2,2–2,5 m, Vigilante 2,5–3,0 m, Coleccionista 2,0–2,5 m y Sombra 2,0–2,5 m. El Vigilante de 3,0 m queda con ≈7 cm de margen vertical. Las puertas de oficina y aseo (0,90 × 2,08 m) no se tocaron y siguen excluyendo a las criaturas de 2,2–2,5 m; su ampliación a ≈2,60 m no está autorizada.

## Resultado por recorrido

### Recepción

- La ruta desde el corredor entra por la puerta y alcanza el **frente del mostrador** y el **ala oeste**.
- Ruta BFS al mostrador: `(-12.0, 0.0) → (-11.6, 0.6) → (-11.6, 1.6) → (-11.35, 2.35) → (-11.35, 3.35) → (-11.35, 4.35) → (-11.8, 4.9) → (-12.0, 5.7) → (-12.0, 6.6)`.
- El área situada al norte del mostrador y el extremo este no son objetivos del recorrido público y no son alcanzables desde la entrada con la cápsula actual.
- El banco duplicado que cruzaba la entrada está oculto de forma reversible. La mesa de centro se desplazó 3,1 m al oeste y la silla caída B 1,2 m al este para abrir un pasillo legible.
- La vista a altura de ojos desde la puerta muestra paso claro hasta el mostrador; quedan sillas, cajas y un monitor roto como obstáculos narrativos laterales.

### Seguridad

- Alcanzable desde el corredor, con holgura mínima registrada de ≈0,22 m junto al mobiliario.
- La silla caída de seguridad no bloquea el paso.

### Control de acceso

- El acceso recto al arco está certificado en v134: `(13,0, 5,2)` → `(13,0, 6,4)` → escritorio `(13,0, 7,0)`.
- La barrera y el poste bajos que cerraban el vano útil se ocultaron de forma reversible con `circulation_fix="control_v134_clear_detector_lane"`; no se borró nada.
- **Limitación de legibilidad:** el arco sigue siendo un control estrecho y conviene señalar la entrada correcta desde el corredor, pero ya no obliga a rodear la sala.

### Corredor

- La ruta principal este-oeste es transitable, incluido el enlace restringido.
- El extremo oeste **sí es alcanzable** por el carril sur del corredor (y ≈ −1,0): se llega a `(-15.0, -1.0)`, `(-17.0, -1.0)` y `(-20.0, -1.0)`. El carril norte a partir de x ≈ −14,6 queda bloqueado por la silla caída y las dos señales, pero no corta el acceso al fondo ni al extintor.
- **Pendiente de decisión de diseño:** el desvío al carril sur no está señalizado; puede aceptarse como lectura del derrumbe o añadirse una marca discreta en el suelo. No es un corte total.

### Vestuarios, almacén y mantenimiento

- Los tres son alcanzables justo dentro de su puerta desde el corredor.
- No se auditó todavía el recorrido completo hasta el fondo de cada sala; el objetivo de esta pasada era verificar el acceso y el corredor principal.

### Umbral restringido y núcleo

- El enlace restringido del extremo este es alcanzable.
- El núcleo vertical no se ha probado con cápsula en esta pasada; sigue pendiente.

## Cambios aplicados

- v132: ocultación reversible de `NEXUS_V05_REC_BENCH2` y sus cuatro patas, con `original_location`, `circulation_fix` y `replaced_by`.
- v133: desplazamiento de la mesa de centro y sus patas 3,1 m al oeste; silla caída B 1,2 m al este; metadatos `original_location` y `circulation_fix` en cada objeto movido.
- v134: ocultación reversible de `NEXUS_V05_ACC_BARRIER_1` y `NEXUS_V05_ACC_POST_1`, con `original_location`, `original_hide_render`, `original_hide_viewport`, `checkpoint_state` y `circulation_fix`.
- No se borró mobiliario. No se modificaron puertas, muros ni otros niveles.

## Verificación

- v134: **2.389 objetos**, cámara `NEXUS_V05_CAM_Recepcion`.
- L1 visible: **1.878 mallas**, **543.201 triángulos**, **50 luces visibles**, **23 con sombra**.
- Actualización 14:05 COT: se retiraron los 5 objetos de la linterna de vista previa y la extracción se movió al centro de la puerta de acceso. L1 queda en **2.384 objetos**, **1.876 mallas**, **560.445 triángulos**, **48 luces visibles** y **22 con sombra**; el máster recargado queda en **8.058 objetos**.
- Actualización 15:05 COT (v136): la sala oeste de v135 fue rechazada y eliminada. Se borraron sus 118 objetos, se restauró el muro ciego `NEXUS_V05_CORR_END_-22`, se ocultaron los rótulos **SALIDA** del corredor y la extracción se trasladó al ascensor **SALIDA** de recepción, junto al reloj. La zona inicial medía 2,10 × 1,50 m en `(-17.5, 10.7, -5.65)`, con activación inicial de 10 s, aro naranja, texto de suelo y consola mural; v138 reemplazó ese valor por la recepción completa. La estación de café se desplazó 1,8 m al sur para despejar el frente del ascensor.
- La rejilla BFS confirma **alcanzables** `extraction_elevator_center (-17.5,10.7)`, `extraction_elevator_zone_north (-17.5,11.0)`, `extraction_console_front (-15.1,10.9)` y `extraction_lobby_approach (-16.3,9.7)`, además de los objetivos anteriores. L1 queda en **2.389 objetos**, **1.878 mallas**, **559.841 triángulos**, **48 luces visibles** y **22 con sombra**; el máster recargado queda en **8.063 objetos**.
- Actualización 15:36 COT (v137): se abrió un hueco de 1,88 × 2,625 m en el muro norte y se construyó una cabina transitable de 1,88 × 1,80 × 2,55 m detrás, con puertas animadas en frames 1/45/105/130 y escena 1–160. El portal se representa como paso despejado en `audit_l1_pathgrid.py` porque los AABB de las mallas cortadas cerraban falsamente el hueco. La BFS confirma **`elevator_car_center (-17.5,12.5)` y `elevator_car_back (-17.5,13.2)` alcanzables, con 21 waypoints**. L1 queda en **2.440 objetos**, **1.921 mallas**, **560.493 triángulos**, **49 luces visibles** y **22 con sombra**; máster **8.114 objetos**.
- Actualización 16:05 COT (v138): la zona de extracción pasa a ser la **recepción completa de 16 × 10 m**, centro `(-12.0, 6.7, -5.65)`, con capacidad **1–8 jugadores**, activación de **2,0 s** y secuencia total de **8,7 s** (apertura 1,5 s, espera 2,5 s, cierre 1,0 s, viaje 1,3 s). Se añade `NEXUS_V05_REC_EXTRACT_RECEPTION_TRIGGER`; el ascensor y la cabina quedan como salida visual. L1 queda en **2.441 objetos**, **1.921 mallas**, **560.493 triángulos**, **49 luces visibles** y **22 con sombra**; máster **8.115 objetos**.
- Máster: **8.115 objetos**, 8 bibliotecas relativas, 0 ausentes; `NEXUS_V05_ELEVATOR` 50 objetos, trigger de cabina y trigger de recepción presentes. Barrera y poste figuran con `hide_render=True` y el metadato del pase.
- `nexus/manifest.json`: L1 2.569.121 bytes / 2.441 objetos; MASTER 8.115 objetos / 398.478 bytes.
- Renders: `/tmp/opencode/v133_reception.png`, `/tmp/opencode/v133_door_view.png`, `/tmp/opencode/v133_eye_entry.png`, `/tmp/opencode/v134_control.png`.
- v131 rechazada por solapar el banco con las sillas de la pared oeste; no usar.
- Persisten dos PNG inválidos de `industrial_wall_lamp_1k` en la biblioteca; no son una regresión de esta pasada.

## Limitaciones

- El carril norte del extremo oeste queda bloqueado por la silla caída y las dos señales; se acepta como restricción narrativa porque el carril sur permite llegar al extremo y al extintor.
- La rejilla no modela escaleras, rampas, saltos, puertas operables ni la altura real de la cápsula en Godot.
- No hay controlador de jugador ni navmesh; la extracción es geometría y metadatos. La recepción completa y la cabina tienen triggers, pero ni `NEXUS_V05_REC_EXTRACT_RECEPTION_TRIGGER` ni `NEXUS_V05_REC_EXTRACT_CAB_TRIGGER` tienen lógica de juego. La linterna de vista previa se retiró y se entregará al jugador al ingresar.
- No se exportó a Godot.
- No se tocó `fotos-referencia/`.

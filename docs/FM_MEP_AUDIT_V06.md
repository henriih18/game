# FRECUENCIA MUERTA — Auditoría MEP del Nivel 1 V06

**Fecha:** 2026-11-16  
**Alcance:** coherencia de tuberías, conductos, bandejas, desagües y penetraciones entre las nueve salas vestidas y los pasillos/conectores del Nivel 1 V06.  
**Estado:** auditoría de solo lectura. No se ha modificado geometría, navegación ni colisiones.

## 1. Resumen ejecutivo

Los servicios de las salas nuevas funcionan visualmente dentro de cada sala, pero **no forman una red continua entre habitaciones y pasillos**. Cada sector tiene su propia isla de instalaciones: las bandejas, conductos y tuberías terminan contra muros o techos sin sleeves, transiciones ni continuidad declarada.

Hallazgos principales:

- **0 penetraciones** de servicios en los muros de las nueve salas nuevas y sus conectores.
- **0 sleeves o fire dampers** propios en esas salas. Los 53 sellos existentes pertenecen a Z10, Recepción y Seguridad.
- **4 conflictos físicos** entre la cota de un servicio y el gálibo real de un conector.
- **Aseo y Control** carecen de sistemas funcionales completos: el Aseo no tiene agua, desagüe ni extracción conectada; Control solo tiene bandeja de cables.
- **Mantenimiento** es la sala mejor resuelta: las cabeceras de vapor, agua, condensado y aire tienen colores coherentes, y el conducto HVAC **sí está conectado a `MT_AHU_01`**. La afirmación previa de que no había AHU era incorrecta.
- El **corredor principal** sí tiene una espina continua de HVAC, bandeja y rociadores, con rama a Z10. Recepción y Seguridad tienen sleeves y fire dampers plausibles. Esa espina es la única base de red que existe hoy.

## 2. Matriz de presencia por sala

Leyenda: ● presente y conectado, ◐ presente pero incompleto o aislado, ○ ausente.

| Sala | HVAC suministro | Extracción | Bandeja | Agua | Desagüe | Rociadores | Sleeves |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Vestuarios (Z05) | ◐ rejillas de pared | ◐ rejillas sin ducto | ◐ | ◐ | ◐ | ○ | ○ |
| Control (Z04) | ○ | ○ | ◐ | ○ | ○ | ○ | ○ |
| Almacén (Z06) | ◐ conducto/difusor | ◐ sin AHU visible | ◐ | ○ | ◐ rejillas | ◐ | ○ |
| Mantenimiento (Z07) | ● AHU_01 + conducto | ◐ AHU_02 sin ducto | ● dos bandejas | ● cabeceras | ● rejillas | ○ | ○ |
| Oficinas (Z08) | ◐ conducto sin AHU | ◐ split en archivo | ◐ dos tramos | ◐ aseos | ◐ aseos | ○ | ○ |
| Aseo (Z09) | ○ | ◐ difusor sin ducto | ◐ | ○ | ○ | ○ | ○ |
| Escaleras Main | ○ | ○ | ◐ | ○ | ○ | ○ | ○ |
| Escaleras E1/E2 | ○ | ○ | ◐ | ○ | ○ | ○ | ○ |

## 3. Inventario de servicios nuevos

| Sala | Objeto | AABB Blender | Observación |
|---|---|---|---|
| Control | `CTRL_Ceiling_CABLE` | x −104.75..−77.25; y 40.5..59.5; z 5.454..5.61 | Solo bandeja, sobre el techo de la sala. |
| Almacén | `WH_CableTray_CABLE` | x 70.2..109.6; y 22.725..23.275; z 4.47..5.83 | Deck a 4.47–4.6; colgantes hasta 5.83. |
| Almacén | `WH_HVAC_DIFFUSER` | x 70.423..104.027; y 19.45..20.55; z 3.325..5.9 | Sin AHU visible; puede venir de cubierta. |
| Almacén | `WH_Sprinkler_CABLE` | x 70.25..109.55; y 26.945..27.055; z 4.383..5.795 | Ramal de rociadores aislado. |
| Almacén | `WH_Drain_GRILLE` | x 79.64..96.36; y 11.64..33.86; z 0.002..0.03 | Solo rejillas de suelo. |
| Mantenimiento | `MT_HVAC_Duct` | x 56.5..107.8; y −14.06..−13.14; z 4.538..5.33 | Conecta con `MT_AHU_01` en x107.475..107.8. |
| Mantenimiento | `MT_CableTray_CABLE` | x 74..104; y −9.332..−8.767; z 4.717..5.75 | Bandeja norte. |
| Mantenimiento | `MT_CableTray_South_CABLE` | x 58..108; y −46.383..−45.817; z 4.528..4.705 | Bandeja sur. |
| Mantenimiento | `MT_Header_Steam_A_*` | x 56.3..111.7; y −19.277..−18.923; z 4.883..5.237 | Vapor, rojo. |
| Mantenimiento | `MT_Header_Water_A_*` | x 56.3..111.7; y −20.467..−20.133; z 4.853..5.187 | Agua, azul. |
| Mantenimiento | `MT_Header_Cond_A_*` | x 56.3..111.7; y −21.638..−21.362; z 4.842..5.118 | Condensado, verde. |
| Mantenimiento | `MT_Header_Air_A_*` | x 56.3..111.7; y −22.816..−22.584; z 4.824..5.056 | Aire, amarillo. |
| Mantenimiento | `MT_Risers` | x 56.2..57.041; y −28.01..−26.31; z 0.4..5.0 | Único elemento vertical de la sala. |
| Oficinas | `OF_CableTray_CABLE` | x −10.27..−9.73; y 4.25..29.75; z 4.025..4.25 | Termina en el muro sur, sin sleeve. |
| Oficinas | `OF_CableTray_Open_CABLE` | x −14.24..−13.76; y 38.5..55.5; z 4.075..4.22 | Tramo independiente. |
| Oficinas | `OF_Duct_DIFFUSER` | x −18.425..−17.575; y 39..53; z 3.905..4.5 | Sin AHU visible. |
| Aseo | `RS_Services_CABLE` | x 18.4..29.6; y 43.355..57.805; z 2.69..3.18 | Solo bandeja. |
| Aseo | `RS_Ceiling_DIFFUSER` | x 18.15..29.85; y 42.15..57.85; z 3.138..3.24 | Rejilla sin ducto. |
| Escaleras Main | `ST_Main_Ceiling_CABLE` | x −11.512..7.51; y −49.6..−30.4; z 5.91..7.0 | Bandeja y tuberías. |
| Escaleras Main | `ST_Main_ConnectorServices_CABLE` | x −1.275..−0.725; y −29.4..−4.4; z 3.777..4.18 | Conducto del conector. |
| Escaleras E1 | `ST_E1_Ceiling_CABLE` | x 115.057..118.962; y 8.5..25.5; z 5.485..5.99 | Bandeja. |
| Escaleras E2 | `ST_E2_Ceiling_CABLE` | x 117.057..120.962; y −43.5..−26.5; z 5.485..5.99 | Bandeja. |
| Vestuarios | `VEST_Ceiling_Pipes_CABLE` | x 30..60; y 40..64; z 3.572..4.19 | Tuberías de techo. |
| Vestuarios | `VEST_Vent_*` | 6 rejillas de pared | Sin ducto detrás. |

## 4. Continuidad por conector

### 4.1. ServiceLink (Z10 ↔ Almacén)

- Paso: x 62..70, y 18..24; techo a z 4.09; vano real al Almacén limitado a z 0..2.6.
- Bandeja de Almacén: deck z 4.47..4.6; arranca en x 70.2.
- Bandeja de Z10: termina en x 62; riser/conduits en x 61.7..61.85, z ≈3.1.
- **Veredicto: conflicto crítico.** No cabe por el vano de 2.6 ni por el techo de 4.09 sin transición. Propuesta: bandeja a z 3.9 en el conector, sleeve cortafuego a z 3.9 en el muro sobre el vano, y resalte vertical de 0.6 m dentro del Almacén hasta la bandeja existente.

### 4.2. MaintenanceConnector (corredor ↔ Mantenimiento)

- Paso: x 60..66, y −8..−4; puerta de 3.04 m; muro macizo de z 3.2 a 6.0.
- Conducto de Mantenimiento: z 4.538..5.33; no puede atravesar la puerta.
- **Veredicto: conflicto crítico.** Opciones: sleeve cortafuego sobre la puerta (z ≈4.8) o usar el shaft elevado del muro norte (x 104.5..105.5, z 1.25..6). La segunda opción evita perforar la fachada del conector, pero exige llevar el conducto hasta el extremo este.

### 4.3. OfficesConnector (corredor ↔ Oficinas)

- Paso: x −14..−6, y 4..30; techo a z 4.2.
- Bandeja del conector: z 4.025..4.25; ya roza el techo y termina en y 29.75.
- Bandeja de open office: empieza en y 38.5; no hay tramo de lobby ni sleeve.
- **Veredicto: conflicto crítico.** Bajar la bandeja del conector a z ≤4.0, añadir sleeve en el muro sur sobre la puerta (macizo z 3.183..4.5) y empalmar con la bandeja de open office mediante un resalte.

### 4.4. AseoLink (Oficinas ↔ Aseo)

- Paso: x 15..18, y 46..52; techo z 4.2.
- Bandeja del Aseo: z 2.69..3.18; no llega al enlace.
- Muro oeste del Aseo sobre la puerta: macizo z 2.6..4.0.
- **Veredicto: conflicto funcional.** Añadir sleeve a z ≈2.9 y un tramo de bandeja en el enlace; si se dota al Aseo de extracción, el conducto debe pasar por encima de la puerta o por un shaft propio.

### 4.5. StairsConnector (corredor ↔ Escaleras Main)

- Paso: x −4..2, y −30..−4; techo z 4.2.
- Conducto del conector: z 3.777..4.18; termina en y −4.4.
- HVAC del corredor: z 3.22..3.88, y −2.43..−1.57.
- **Veredicto: incompleto.** Falta un codo/reducción de transición de ~0.2 m de altura en y −4.4..−1.57. El gálibo permite hacerlo sin obra.

### 4.6. Escaleras E1/E2

- E1: bandeja a z 5.485..5.99; Almacén no tiene bandeja a esa cota ni sleeve en el muro x 110.
- E2: bandeja a z 5.485..5.99; Mantenimiento tiene bandeja sur a z 4.528..4.705, pero termina en x 108 y no llega al muro x 112.
- **Veredicto: islas.** Conectar mediante sleeve y resalte vertical, o declarar las escaleras como sectores con bandeja independiente y cierre cortafuego.

## 5. Conflictos y severidad

| # | Severidad | Elemento | Problema | Corrección propuesta |
|---|---|---|---|---|
| 1 | Crítica | Almacén / ServiceLink | Bandeja a 4.47–4.6; techo 4.09; vano 2.6 | Bandeja a 3.9 + sleeve + resalte interior |
| 2 | Crítica | Mantenimiento / conector | Conducto a 4.54–5.33; puerta 3.04 | Sleeve sobre puerta o ruta por shaft norte |
| 3 | Crítica | Oficinas / conector | Bandeja a 4.25; techo 4.2; muro macizo | Bandeja a 4.0 + sleeve + enlace |
| 4 | Alta | Aseo | Sin agua, desagüe ni extracción | Acometidas y extractor con ducto |
| 5 | Alta | Control | Sin HVAC ni extracción de racks | Climatizadora local + retorno |
| 6 | Media | StairsMain | Conducto sin transición al corredor | Codo/reducción |
| 7 | Media | Escaleras E1/E2 | Bandejas sin continuidad | Sleeve + resalte o cierre cortafuego |
| 8 | Baja |Todas | Sin leyenda de medios ni etiquetas | Señalética MEP y código de color |
| 9 | Baja | Varias | Secciones y elevaciones arbitrarias | Normalizar a 0.4/0.6/0.8 m |

## 6. Lo que sí es coherente

- La **espina del corredor principal** (HVAC 800×600, bandeja y rociadores, x −99..73.8) es continua y tiene una rama coherente a Z10.
- **Recepción** y **Seguridad** tienen sleeves y fire dampers en sus pasos, aunque sus sistemas no conectan con la espina.
- **Mantenimiento** usa un código de color consistente: vapor rojo, agua azul, condensado verde, aire amarillo, aislamiento gris.
- **`MT_HVAC_Duct` sí conecta con `MT_AHU_01`**; el segundo AHU puede funcionar como unidad local/retorno, pero conviene modelar su retorno o justificarlo.
- Las rejillas de desagüe de Almacén y Mantenimiento son plausibles como drenaje superficial, aunque no conectan a una red subterránea visible.

## 7. Propuesta de red (no implementada)

1. **Espina principal:** mantener el corredor como eje. HVAC, bandeja y rociadores a z 3.2–4.0.
2. **Ramal Z10–Almacén:** bandeja a z 3.9 por ServiceLink, sleeve cortafuego y resalte a 4.5 en Almacén.
3. **Ramal Oficinas:** bajar la bandeja del conector a 4.0, sleeve en el muro sur y enlace al open office.
4. **Ramal Mantenimiento:** llevar el conducto al shaft norte o abrir sleeve sobre la puerta con fire damper.
5. **Aseo:** añadir agua fría/caliente, desagüe y extracción; el extractor puede descargar al plenum y a un shunt vertical.
6. **Control:** añadir climatizadora local y retorno para los racks; no necesita conectarse al corredor.
7. **Escaleras:** conectar bandejas E1/E2 a Almacén/Mantenimiento con sleeves y resaltes, o cerrar con cortafuego y documentarlo.
8. **Normalización:** secciones 0.4/0.6/0.8 m, colores y leyenda comunes, soportes cada 2.5–3 m, sleeves en todos los pasos.

## 8. Archivos y método

- Inventario MCP: `/tmp/opencode/fm_services_inventory.json` (564 objetos con tokens de servicio).
- Consultas de AABB, materiales y vértices vía Blender MCP; sin modificar el máster.
- Documentos previos revisados: `docs/FM_QUALITY_SERVICES_AUDIT.md` (estado antiguo, no aplicable) y `docs/NEXUS_V05_SERVICE_CONNECTOR_PROPOSAL.md` (layout V05, no usar coordenadas).

## 9. Limitaciones

- La auditoría es geométrica y de gálibos; no valida caudales, presiones, pendientes de desagüe ni cálculo de HVAC.
- Los objetos tienen geometría horneada en coordenadas de mundo; las AABB son de malla, no de sección nominal.
- No se han revisado los servicios ocultos dentro de techos registrables ni los que puedan estar modelados como parte de props.
- No se ha modificado ninguna sala; las correcciones propuestas requieren una fase de implementación y QA posterior.

## 10. Siguiente paso

Presentar esta auditoría al usuario y, si se autoriza, ejecutar las correcciones por prioridad: primero los cuatro conflictos críticos, después las redes funcionales de Aseo y Control, y finalmente la normalización visual y la señalética. Cada corrección debe ir acompañada de rebuild, export, QA y pruebas de regresión.

Sin commit hasta autorización.

## 11. Correcciones aplicadas (2026-11-16)

Se implementaron los cuatro conflictos críticos y dos correcciones adicionales de alta prioridad. La auditoría original se conserva como registro del estado previo.

| Elemento | Corrección implementada | QA | GLB |
|---|---|---|---|
| Almacén / ServiceLink | `WH_ServiceLink_Tray_CABLE`: bandeja en el enlace a y22.75, bajada a z2.44 para cruzar bajo el vano de 2.6, sleeve en x70, resalte vertical hasta z4.55 y conexión a la bandeja del Almacén. Además, `WH_E1_TrayLink_CABLE` conecta la bandeja principal con E1. | PASS 116 objetos | 20.166.532 B; 90 objetos; 142.488 tris; AABB mín. x61.8 |
| Oficinas / conector | Bandeja continua de y4.25 a y38.5 en x−10, deck z3.95; cruce en el lobby y enlace con la bandeja de planta abierta; sleeve sobre la puerta sur en y30. | PASS 283 objetos | 9.726.296 B; 262 objetos; 181.030 tris |
| Aseo | `RS_Tray_Link_CABLE` hasta el AseoLink con sleeve en x18; `RS_Water_Supply_CABLE`, `RS_Drain_Stacks_CABLE`, `RS_FloorDrains_GRILLE` y `RS_Extract_Duct_CABLE` con extractor bajo el techo. | PASS 42 objetos | 4.777.844 B; 31 objetos; 17.440 tris |
| Mantenimiento | `MT_AHU_Air_CABLE`: tomas/retornos de cubierta sobre `MT_AHU_01` y `MT_AHU_02`; se descartó atravesar el conector porque el muro sobre la puerta es macizo. Además, `MT_E2_TrayLink_CABLE` conecta la bandeja sur con E2. | PASS 134 objetos | 21.677.968 B; 106 objetos; 99.098 tris |
| Control | `CTRL_HVAC_Duct_CABLE`: impulsión y retorno de 18 m, AHU de techo, difusores y colgantes a z5.08. | PASS 88 objetos | 1.465.976 B; 73 objetos; 18.132 tris |
| Escaleras Main | Transición del conducto del conector al HVAC del corredor: codo/reductor, adaptador vertical y collar de damper. | PASS 63 objetos | 1.769.800 B; 18 objetos; 13.140 tris |
| Escaleras E1 | `ST_E1_TrayLink_CABLE`: bandeja longitudinal a x115.1, puente hasta el muro x110, sleeve y tres cables; enlaza con `WH_E1_TrayLink_CABLE` del Almacén a z4.50. | PASS 47 objetos | 1.268.860 B; 14 objetos; 6.286 tris |
| Escaleras E2 | `ST_E2_TrayLink_CABLE`: bandeja longitudinal a x117.1, puente hasta el muro x112, sleeve y tres cables; enlaza con `MT_E2_TrayLink_CABLE` de Mantenimiento a z4.55. | PASS 47 objetos | 1.281.748 B; 14 objetos; 6.796 tris |

Pruebas tras las correcciones y el cierre de E1/E2: smoke **403/0**, gameplay **105/0**, full run **49/0**, presets **194/0**, perf 1280×720 **PASS** (556,2 fps medios, mínimo 116,2, p1 261,8, p99 3,82 ms; 5.042.270 tris, 158 luces, 1.434 colliders). Capturas de verificación en `/tmp/opencode/mep_godot_*.png` y contactos `mep_godot_contact3/4/5.png`; algunas tomas de techo quedan parcialmente ocultas por luminarias y placas.

**Pendiente menor:** Vestuarios mantiene rejillas pasivas; el AHU del Almacén se representa implícitamente como unidad de cubierta; no hay leyenda de medios ni normalización completa de secciones. Las bandejas E1/E2 ya están conectadas a Almacén y Mantenimiento. Sin commit.

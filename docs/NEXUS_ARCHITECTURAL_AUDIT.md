# NEXUS — Auditoría arquitectónica y propuesta funcional

**Fecha:** 2026-11-01. **Modo:** auditoría de solo lectura; sin cambios de geometría.
**Escena viva:** FM_NEXUS_V05_level1_v105.blend, Blender 5.2.3 LTS.
**Estado al consultar:** 7.230 objetos, 47 colecciones, 51 materiales, 29 cámaras, 291 luces, EEVEE, escala 1.0; MCP reportó is_dirty=True. No guardar esta escena hasta determinar la causa.

## Método y límites

Leí AGENTS.md completo, CURRENT_STATE.md, las últimas entradas de WORKLOG.md, fm_nexus_nivel2.md, fm_scene_art.md, fm_visual_reference.md y fm_lookdev.md. Verifiqué el addon MCP y abrí la vista general top/3⁄4/lateral. Revisé las 17 imágenes de fotos-referencia en hoja de contacto y modelos-referencia.png a resolución original. Los originales no se modificaron.

Las huellas de las tablas son los bounds AABB de objetos de piso llamados *_FLOOR, no el espacio neto entre muros ni una prueba de navegación. Los rayos que ya constan en el worklog tampoco prueban paso de cápsula, animación de puertas o evacuación. Oficina y aseo sí existen activos dentro del volumen administrativo de V05; están modelados como partición/volumen interior, no como pisos *_FLOOR separados.

La hoja oficial de criaturas muestra alturas **aproximadas**: Imitador 2,2–2,5 m; Vigilante 2,5–3,0 m; Coleccionista 2,0–2,5 m; Sombra 2,0–2,5 m. No da anchuras numéricas. No inferirlas.

## Hallazgo de alcance: bandas de nivel (resuelto por el usuario)

En la escena hay cinco cotas habitadas observables: V05 z≈−5,8 m; V04 z≈−13,8 m; L3 z≈−22,8 m; L4 z≈−32,8 m; L5 z≈−43,8 m. Funcionalmente corresponden a acceso, investigación/tecnología, medicina, seguridad/contención e infraestructura.

El usuario confirmó cinco bandas: V05 acceso/operaciones; V04 investigación/tecnología; L3 medicina; L4 seguridad/contención; L5 infraestructura profunda. No crear una sexta banda ni cambiar identificadores. La discrepancia anterior queda resuelta.

## Escena: materiales, cámaras e iluminación

- Hay 51 materiales y los inspeccionados tienen node tree. Sus nombres/usuarios cubren concreto, metal pintado/oxidado, acero, vidrio, caucho, suciedad, sangre, agua, señalética, pantallas, material clínico, piel y residuo tóxico. Esto confirma biblioteca de materiales, no la revisión de cada shader, UV o textura.
- Hay 29 cámaras. La activa es NEXUS_V05_CAM_Corridor; existen cámaras de revisión de recepción, oficina, aseo, control, almacén, mantenimiento, salas de investigación, V04 y niveles inferiores. Algunas cámaras V03 son históricas y están ocultas. Una cámara presente no demuestra que la sala haya pasado revisión visual actual.
- Hay 291 luces: 230 Area, 60 Point y 1 Spot; 217 aparecen visibles y 74 ocultas. Se observan fuentes frías, emergencia roja, luz cálida de trabajo y acentos de laboratorio/contención. La colección V03 de iluminación está oculta. El conteo no mide exposición final ni calidad de sombras; revisar contraste y lectura por nivel.
- Vista general MCP superior/3⁄4/lateral: cinco bandas apiladas y torre al este. No permite verificar puertas, estructura ni circulación.

## Inventario por zona

Las dimensiones son X×Y en metros, AABB de piso, aproximadas a la geometría observada.

### Acceso actual V05, cota −5,8 m

| Habitación | Huella | Estado y decisión |
|---|---:|---|
| Recepción NEXUS_V05_RECEPCION | 16×10 | Activa. Mantener como spawn interior, recepción/registro y cara corporativa; comprobar mostrador, espera y administración. |
| Seguridad NEXUS_V05_SEGURIDAD | 10×8 | Activa. Mantener junto a recepción/control; debe supervisar entrada y umbral restringido. |
| Control de acceso NEXUS_V05_CONTROL_ACCESO | 8×8 | Activa. Mantener como transición con lector/puerta entre llegada y circulación interna; operación estática no verificada. |
| Vestuarios NEXUS_V05_VESTUARIOS | 10×8 | Activa. Mantener antes de zona laboral; comprobar taquillas/servicio sin cruzar suministros. |
| Almacén NEXUS_V05_ALMACEN | 12×8 | Activo. Mantener para equipamiento de llegada; cargas pesadas requieren ruta de servicio/elevador, no recepción. |
| Mantenimiento NEXUS_V05_MANTENIMIENTO | 14×8 | Activo. Mantener segregado del flujo público; panel cercano al vano puede reducir paso. |
| Corredor NEXUS_V05_CORR | 44×3,4 | Activo, x≈−22…+22; oeste termina en cap, este conecta con torre. Ancho libre y ruta alternativa pendientes. |
| Recepción histórica RECEPCION_NEXUS | 9×7 | Piso histórico oculto; conservar, no sustituye el módulo activo. |
| Seguridad histórica SEGURIDAD_PERIMETRAL | 8×7 | Módulo interior histórico oculto, no edificio exterior; conservar. |
| Oficina NEXUS_V05_OFFICE | recinto aprox. 3,9×5,84 según muros; techo 4,08×6,02 | Activa dentro del volumen de recepción/administración; contiene escritorio, silla, monitor, archivador, HVAC, puerta y ventana. Mantener y verificar el flujo público y claro de acceso. |
| Aseo NEXUS_V05_REST | partición parcial interior de oficina; sin huella de piso propia | Activo: puerta, lavamanos, inodoro, partición, secador y barra de apoyo. Mantener; revisar privacidad, giro y ventilación. No declararlo accesible sin medir claros. |

**Relación propuesta, sin obra exterior:** spawn en recepción/registro; puesto de vigilancia visible o señalizado; primer control delimita la llegada; segundo control conduce a núcleo/restringido; vestuarios antes de trabajo; almacén recibe suministros por trayecto interno segregado hacia elevador adecuado. El jugador empieza dentro de NEXUS. No modelar parcela, carretera, estacionamiento, garita exterior ni andén exterior.

### Investigación y tecnología V04, cota −13,8 m

| Habitación | Huella | Estado y decisión |
|---|---:|---|
| Nave central | 18×14 | Activa. Mantener como cámara de experimento/observación; revisar claros alrededor de equipos. |
| Biología | 14×10 | Activa. Mantener. Puente de piso llega al muro sólido oeste del airlock y el paso está bloqueado. |
| Química | 12×10 | Activa. Mantener con extracción, ducha y almacenamiento químico asociados. |
| Sala de análisis | 10×8 | Activa. Mantener entre laboratorios y cadena de muestras/archivo. |
| Servidores | 8×7 | Activa. Mantener por proximidad a control/telemetría; puente tiene hueco de 0,30 m y cuello de aproximación registrado. Climatización y mantenimiento deben separarse de agua/químicos. |
| Archivo científico | 10,8×8 | Activo. Mantener para documentos operativos; no duplicar archivo secreto sin definir diferencia de uso. |
| Airlock | 4×4 | Activo. Mantener como transición controlada Bio/zonas limpias; paso, giro y secuencia de puertas por verificar. |
| Corredores | eje 22×3,4; alas 12,3×3,4 | T con enlace al núcleo, no hay loop alternativo comprobado. Medidas de piso, no ancho libre. |

NEXUS_STORY_L2A (469 objetos) y L2B (492) recogen trabajo narrativo documentado como completo; preservar y no reconstruir. El estándar de puertas registrado es 3,12 m de alto y 1,72 m de ancho (Nave 3,12 m); estático. El margen de altura respecto al máximo del Vigilante es limitado.

### Medicina L3, cota −22,8 m

| Habitación | Huella | Recomendación |
|---|---:|---|
| Enfermería | 8×7 | Mantener como estabilización próxima al anillo/núcleo. |
| Habitaciones médicas | 9×8 | Mantener en recuperación; separar del flujo de morgue. |
| Quirófano | 10×8 | Mantener; verificar preparación limpia, lavado, recuperación y suministro. |
| Aislamiento A y B | 8×7 cada una | Mantener segregadas por esclusa/antecámara y observación. |
| Morgue | 8×8 | Mantener con acceso controlado y ruta discreta para traslado. |
| Cámaras frigoríficas | 8×7 | Mantener funcionalmente asociadas a morgue/análisis, con mantenimiento frigorífico. |
| Anillo central | 16×12 | Activo con link este; siete entradas registradas. Umbrales unos 0,11 m bajo los pisos según worklog; revisar en contexto. |

La ruta de camilla debe unir llegada/estabilización, preparación, quirófano y recuperación sin pasar por aislamiento ni morgue. Rayos previos no certifican giro ni circulación real.

### Seguridad y contención L4, cota −32,8 m

| Habitación | Huella | Recomendación |
|---|---:|---|
| Búnker de seguridad | 9×8 | Mantener como control de sector; no convertir en zona de combate. |
| Armería/herramientas | 8×7 | Mantener solo la función de herramientas no ofensivas; AGENTS prohíbe armas. Aclarar nomenclatura/contenido en futura revisión, no editar ahora. |
| Control de contención | 9×8 | Mantener entre seguridad, observación y operación de compuertas. |
| Contención primaria | 12×10 | Mantener como cámara principal, con barrera y maniobra. |
| Contención secundaria | 10×9 | Mantener como cámara independiente, no circulación; acceso por esclusa y mantenimiento segregado. |
| Laboratorio restringido | 9×8 | Mantener en sector de máxima restricción; acceso auditado desde investigación/contención. |
| Anillo central | 16×12 | Activo con link este; seis vanos registrados. Umbrales bajos/cubiertos; tránsito de cápsula no comprobado. |

La posición conjunta de seguridad y contención es lógica. Crear oportunidades de observación y pérdida de contacto visual para Vigilante; esclusas e intercom para Imitador; oscuridad controlable para Sombra. Conservar una vía de retirada que no dependa de una sola compuerta.

### Infraestructura L5, cota −43,8 m

| Habitación | Huella | Recomendación |
|---|---:|---|
| Generadores | 11×9 | Mantener en profundidad, con cuadros/ventilación/acceso de sustitución y aislamiento térmico/sonoro. |
| Bombeo/inundación | 10×8 | Mantener en la cota baja; enlazar drenaje/sumideros sin convertir todo el pasillo en zona inundada. |
| Refrigeración | 9×8 | Mantener cerca de carga térmica con distribución técnica; verificar circuitos y mantenimiento. |
| Extracción profunda | 11×8 | Mantener. Definir si es salida de emergencia, servicio o ambas; hoy esa función no está probada. |
| Túnel profundo | 13×7 | Mantener como rama opcional/restringida, con lógica de conexión fuera de mapa. |
| Archivo secreto | 7×7 | Mantener si contiene contingencias/clasificados; si es archivo de uso rutinario, función duplicada con archivo científico y reconsiderar ubicación después de definir contenido. |
| Anillo central | 20×12 | Activo con link este; seis vanos registrados. Umbrales bajos; cabrestante/poste detrás de rayos de acceso requieren prueba de giro. |

Generadores, bombeo y frío forman un conjunto técnico plausible. Sectorizar ruido, calor, agua, electricidad y mantenimiento; el sonido de la maquinaria puede ayudar a orientación y también ocultar amenazas.

## Diagnóstico transversal

**Conservar:** zonificación gruesa acceso → investigación → medicina → seguridad/contención → infraestructura; L2A/B y utilería narrativa; anillos activos L3–L5; colección de escalera este cuatro franjas y sus históricos. No hay evidencia suficiente para trasladar físicamente departamentos completos. La prioridad es cerrar relaciones, accesos y servicios.

**Corregir/validar primero:** (1) definición de cantidad/nombre de niveles; (2) secuencia de recepción y controles del Acceso; (3) bloqueo Bio–airlock; (4) hueco/estrechamiento de Servidores; (5) umbrales L3–L5; (6) núcleo vertical y evacuación; (7) rutas de camilla, carga, mantenimiento y salida; (8) alturas libres frente al Vigilante y envolventes de las cuatro criaturas; (9) soporte estructural y trazados MEP. Los rayos anteriores no demuestran circulación de cápsula.

La separación vertical de centros de piso es 8, 9, 10 y 11 m. No equivale a altura libre ni prueba que falte estructura: medir cara inferior de losa, vigas, vacíos, escaleras y plenos antes de alterar. La escena tiene 0 objetos en las colecciones genéricas 05_PIPES_CABLES, 06_DISASTER_DAMAGE y 10_CREATURES, pero hay instalaciones/daño/utilería dispersos en colecciones específicas; no inferir ausencia total por esos contadores.

El estado de Blender MCP cambió a is_dirty=True durante una llamada de consulta sin escritura. La causa no está determinada. No guardar, limpiar, hacer undo/reset ni cambiar selección/visibilidad mientras se diagnostica; v105 y los históricos siguen en disco.

## Circulación propuesta

Llegada interior → recepción/registro → control de visitantes → seguridad  
Desde recepción: vestuarios → zonas de trabajo; control restringido → núcleo.  
Almacén → ruta interna de servicio/elevador apropiado → departamentos.  
Bio/Química → preparación/esclusa → análisis → archivo operativo.  
Medicina: enfermería → preparación → quirófano → recuperación; aislamiento por esclusa; morgue ↔ cámaras frías por ruta de servicio.  
Seguridad → control de contención → esclusa → cámaras; laboratorio restringido con acceso auditado.  
Infraestructura: generación ↔ distribución ↔ servidores/refrigeración; bombeo/drenaje ↔ cotas bajas ↔ túnel/extracción.

Esto es un grafo funcional objetivo, no un registro de conexiones ya construidas. El anillo L3–L5 facilita ruta alternativa y persecución; en V05/V04 sólo una T está comprobada, por lo que un loop lateral se considerará solo si cabe sin forzar estructura. Las rutas de visitantes, muestras, pacientes, suministros, técnicos, restringidos y emergencia deben trazarse separadamente y luego revisar cruces.

## Juego, terror y criatura por nivel

- **Acceso:** llegada inicialmente legible, NEXUS intacto con anomalías selectivas. El corredor largo amplifica sonido; recepción sirve de referencia, no de escondite invulnerable. El Imitador puede aprovechar mensajes/radio.
- **Investigación:** contraste Nave amplia con laboratorios compactos; ruido de muestras, equipo y compuertas crea decisiones. Imitador usa compartimentación; Coleccionista se interesa por muestras recuperadas. La separación del equipo debe ser breve, legible y con opción de reunirse.
- **Medicina:** silencios clínicos, luz de trabajo/emergencia y diferencias entre recuperación, aislamiento y morgue. Facilita rescate/cooperación; Sombra usa oscuridad, con contrajuego de iluminación.
- **Contención:** hormigón, visores, doble puerta y puntos de control. Vigilante aprovecha oclusiones y pérdida de contacto visual; Imitador puede falsificar mensajes. Evitar que una sola esclusa sea cuello mortal sin alternativa.
- **Infraestructura:** vibración, agua, frío/calor y maquinaria diferencian navegación acústica. Coleccionista sigue equipo valioso; Sombra acecha sectores oscuros. Cubiertas deben tener salida y no garantizar seguridad.

La referencia artística apoya metal, hormigón húmedo, tuberías, vapor, luz fría/cian con rojo/ámbar, contaminación localizada, cristal de observación y silueta a contraluz. No es un plano arquitectónico. modelos-referencia.png se usa solo para silueta/altura oficial, no como textura; fotos originales intactas.

## Plan de producción para aprobación

1. Resolver alcance y designación de bandas; plano maestro con las cinco bandas observadas y alternativa explícita si hace falta una sexta.
2. Inventariar nombre/colección de todas las salas activas e históricas, especialmente oficina/aseos; terminar grafo de puertas, rutas y cotas.
3. Completar primero Acceso V05: spawn interior, recepción/registro, control, vigilancia, vestuarios y rutas internas de servicio. Reutilizar geometría; no exterior.
4. Validar el núcleo y su continuidad/evacuación entre cotas. Se aborda al cerrar Acceso porque bloquea el acceso a toda la instalación; ascensor y puertas no están interactivos en Blender.
5. Cerrar circulación de investigación V04, Bio–esclusa, servidores, cadenas de muestras y ventilación.
6. Completar/validar L3 médica: camillas, preparación/recuperación, aislamiento, morgue/frío.
7. Completar/validar L4: doble contención, control, accesos restringidos y mantenimiento; sin armas.
8. Completar/validar L5: potencia, frío, bombeo, drenaje, extracción y ruta de retorno.
9. Trazar estructura/MEP y narrativa del incidente por sectores; distribuir daño según secuencia, sin decorar por acumulación.
10. QA integral: recorridos con jugador/equipo, cápsulas y modelos animados, anchos/alturas libres, giros, puertas, alternativas, rutas de emergencia, iluminación/materiales y evidencia visual por nivel.

Fase presente: organización arquitectónica autorizada. Orden de ejecución: V05 → núcleo vertical → V04 → L3 → L4 → L5 → revisión integral. No trasladar departamentos completos sin necesidad demostrada; trabajar en incrementos y verificar cada bloque en Blender antes de registrarlo como terminado.

## Continuidad de ejecución (2026-11-01)

El usuario autorizó organizar la estructura arquitectónica en Blender. Alcance: cinco bandas listadas arriba; sin exterior, Godot ni mecánicas. La versión activa actual es `/home/riyo/Documentos/game/FM_NEXUS_V05_level1_v107.blend`; v90, recuperación y v105/v106 se preservan. MCP responde (Blender 5.2.3 LTS, addon 1.8/protocolo 15; 7.238 objetos/47 colecciones). Pruebas controladas mostraron is_dirty=False en sesión limpia y True al abrir un .blend, incluso con factory startup; la verificación final de v107 en MCP informó False. El flag inicial se asocia a la carga y por sí solo no demuestra una edición posterior no guardada.

Comprobación y bloque V05: el corredor principal conecta con el enlace este del núcleo; recepción, seguridad y control de acceso tienen puertas directas al corredor común. Se añadió un umbral arquitectónico de acceso restringido con carcasa y rodillo de cierre enrollable recogido, guías, placa «ACCESO RESTRINGIDO» y soportes. El claro modelado abierto es aprox. 2,96×3,59 m. No se movieron ni reemplazaron recintos, muros o puertas. La ruta de servicio almacén–mantenimiento y los claros de oficina/aseo aún requieren verificación.

QA del nuevo bloque: siete mallas, 164 triángulos; UVMap en todas, UVs dentro de rango y sin áreas cero. Cero errores, z-fighting, flotantes o normales invertidas. Avisos aceptados: rodillo encerrado dentro de su carcasa como pieza interna; caras de unión de guías/carcasas cara a cara sin z-fighting; cota z=−5,65 m intencional.

**Siguiente bloque:** verificar puerta de servicio y relación almacén–mantenimiento, medir los claros de oficina/aseo y revisar la llegada desde el corredor. Después cerrar V05 y validar el núcleo vertical.

### Hallazgo de continuidad: conexión de servicio de V05 — 2026-11-01

La puerta de carga NEXUS_V05_D_STORE_DOOR_* está en el muro este del almacén, con marco y paneles en un vano aparente de unos 4 m de ancho por 2,9 m de alto. Sin embargo, el muro NEXUS_V05_ALMACEN_WALL_E es una caja rectangular cerrada (8 vértices/6 caras); un rayo en el centro del aparente vano impacta el muro. La pared oeste NEXUS_V05_MANTENIMIENTO_WALL_W también es una caja cerrada. Entre sus bounds queda una franja x=4,14…5,86 (1,72 m) por y=−9,7…−1,7 (8 m); no se encontró un piso ni cubierta de paso en esa franja. Por tanto, la puerta de carga actualmente no constituye una conexión de servicio practicable. No se hicieron cambios para corregirlo.

**Paso exacto siguiente:** estudiar una sección de corredor de servicio que use esta franja solo si admite el tránsito y la maniobra necesarios; definir claros, piso/cubierta y vanos en ambas paredes, y proponer cómo ejecutar los vanos sin sustituir las mallas existentes. La aprobación y verificación de la geometría propuesta preceden cualquier modificación estructural. Mantener v107 como base; crear otra versión incremental para la intervención.

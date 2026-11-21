# NEXUS — Estándar dimensional maestro

**Estado:** estándar de referencia para organización arquitectónica; cotas no medidas expresamente siguen pendientes de validación.  
**Fuente:** escena activa FM_NEXUS_V05_level1_v107.blend en Blender 5.2.3.  
**Unidades:** métricas, escala 1.0.  
**Fecha de inspección:** 2026-11-01.

Este estándar distingue **confirmado en escena**, **confirmado en referencia**, **propuesto** y **pendiente de validar**. Las tablas de habitaciones registran AABB de los objetos de piso; no son medidas interiores libres ni certificación de navegación.

## 1. Referencia dimensional oficial de criaturas

| Criatura | Altura indicada en la referencia | Estado |
|---|---:|---|
| El Imitador | aprox. 2,2–2,5 m | Texto legible en modelos-referencia.png. Anchura/envolvente no acotada. |
| El Vigilante | aprox. 2,5–3,0 m | Texto legible. Considerar púas, extremidades, postura y animación. |
| El Coleccionista | aprox. 2,0–2,5 m | Texto legible. Su equipo altera el perfil. |
| La Sombra | aprox. 2,0–2,5 m | Texto legible. Apéndices y pose requieren envolvente propia. |

La imagen no proporciona anchuras numéricas. No estimarlas ni alterar dimensiones oficiales para acomodar arquitectura. La carpeta 10_CREATURES está vacía en la escena actual, por lo que la geometría visual de las cuatro criaturas no se pudo medir allí.

La continuidad previa menciona cápsula FMPlayer Ø0,76 m y FMWatcher Ø0,80 m en Godot. Son datos heredados, no revalidados en esta auditoría Blender-only, y no sustituyen el volumen visual animado. Medir cuerpo, casco, mochila, objetos transportados y poses antes de aprobar pasillos.

## 2. Niveles y cotas observadas

| Identificador de escena | Uso actual | Centro aproximado de piso | Estado |
|---|---|---:|---|
| V05 | Acceso/operaciones | z = −5,8 m | Cota observada; función confirmada por objetos. |
| V04 | Investigación/tecnología | z = −13,8 m | Cota observada; nomenclatura funcional actual. |
| L3 | Medicina | z = −22,8 m | Cota observada. |
| L4 | Seguridad/contención | z = −32,8 m | Cota observada. |
| L5 | Infraestructura profunda | z = −43,8 m | Cota observada. |

Separaciones entre los centros de piso: aproximadamente 8, 9, 10 y 11 m. **No son alturas libres**. Medir caras de losa, vigas, techos, plenos, cámaras y escaleras antes de inferir estructura o introducir un nivel.

El alcance confirmado por el usuario es de cinco bandas totales: V05, V04, L3, L4 y L5. No añadir una sexta banda ni cambiar identificadores.

## 3. Huellas de piso medidas

Todas las cifras son X × Y, en metros, del AABB de los pisos activos.

### Acceso V05

| Área | Huella |
|---|---:|
| Recepción | 16 × 10 |
| Seguridad | 10 × 8 |
| Control de acceso | 8 × 8 |
| Vestuarios | 10 × 8 |
| Almacén | 12 × 8 |
| Mantenimiento | 14 × 8 |
| Corredor principal | 44 × 3,4 |
| Oficina interior NEXUS_V05_OFFICE | aprox. 3,9 × 5,84 por extensión de muros; techo 4,08 × 6,02 |
| Aseo interior NEXUS_V05_REST | sin floor separado; recinto parcial dentro de oficina, claro neto pendiente |
| Recepción histórica oculta | 9 × 7 |
| Seguridad histórica oculta | 8 × 7 |

### Investigación/tecnología V04

| Área | Huella |
|---|---:|
| Nave central | 18 × 14 |
| Biología | 14 × 10 |
| Química | 12 × 10 |
| Análisis | 10 × 8 |
| Servidores | 8 × 7 |
| Archivo científico | 10,8 × 8 |
| Airlock | 4 × 4 |
| Corredor principal | 22 × 3,4 |
| Ramas transversales | 12,3 × 3,4 cada una |

### Medicina L3

| Área | Huella |
|---|---:|
| Enfermería | 8 × 7 |
| Habitaciones médicas | 9 × 8 |
| Quirófano | 10 × 8 |
| Morgue | 8 × 8 |
| Cámaras frigoríficas | 8 × 7 |
| Aislamiento A y B | 8 × 7 cada una |
| Centro del anillo | 16 × 12 |

### Seguridad/contención L4

| Área | Huella |
|---|---:|
| Búnker de seguridad | 9 × 8 |
| Armería/herramientas | 8 × 7 |
| Control de contención | 9 × 8 |
| Contención primaria | 12 × 10 |
| Contención secundaria | 10 × 9 |
| Laboratorio restringido | 9 × 8 |
| Centro del anillo | 16 × 12 |

### Infraestructura L5

| Área | Huella |
|---|---:|
| Generadores | 11 × 9 |
| Bombeo/inundación | 10 × 8 |
| Refrigeración | 9 × 8 |
| Extracción profunda | 11 × 8 |
| Túnel profundo | 13 × 7 |
| Archivo secreto | 7 × 7 |
| Centro del anillo | 20 × 12 |

La oficina NEXUS_V05_OFFICE y el aseo NEXUS_V05_REST están activos como recintos interiores del volumen administrativo V05, sin piso independiente identificado. Mantenerlos; claro neto, giro y ventilación siguen pendientes. Los bounds de estancias y circulación pueden solaparse; no sumar como superficie neta.

## 4. Cotas conocidas de puertas, circulación y núcleo

| Elemento | Dato disponible | Clasificación / límite |
|---|---|---|
| Corredores principales V05 y V04 | 3,4 m de ancho de piso | Confirmado como AABB de piso; claro entre obstáculos pendiente. |
| Umbral restringido V05→NEXUS_LINK_L1 | vano abierto estimado 2,96 m × 3,59 m; carcasa 3,0×0,28×0,34 m | Geometría añadida y guardada en v107; claro derivado de dimensiones modeladas y piso/techo existentes. No es medición de paso de criatura; la anchura de criaturas no está acotada. El mecanismo está representado recogido, sin hoja desplegada ni animación. |
| Separación almacén–mantenimiento V05 | 1,72 m entre bounds exteriores de muros; franja longitudinal de aprox. 8,0 m | Cota observada (x=4,14…5,86; y=−9,7…−1,7). La puerta de carga del almacén da hacia esta franja, pero ambos muros laterales son mallas sólidas y no se encontró piso/techo de corredor. No es paso construido. Solución y sección pendientes; no asumir que la franja basta para transporte sin revisión de maniobra. |
| Umbral restringido V05→NEXUS_LINK_L1 | vano abierto estimado 2,96 m × 3,59 m; carcasa 3,0×0,28×0,34 m | Geometría añadida y guardada en v107; claro derivado de dimensiones modeladas y piso/techo existentes. No es medición de paso de criatura; la anchura de criaturas no está acotada. El mecanismo está representado recogido, sin hoja desplegada ni animación. |
| Puente de piso Bio V04 | 1 × 3,4 m | Presente; bloqueado por muro sólido del airlock. |
| Puente a Servidores | 1 × 3,4 m | Interrupción de piso de 0,30 m y estrechamiento registrados; tránsito pendiente. |
| Puertas V04 | 3,12 m alto × 1,72 m ancho estándar; Nave 3,12 m de ancho | Documentación L2; estáticas. Margen vertical frente a Vigilante limitado. |
| Puertas bajas L3–L5 | aprox. 3,0 m de vano en mediciones previas | Pendiente de volver a medir con jambas, dintel, losa y objetos asociados. Igualar altura aproximada máxima del Vigilante no garantiza holgura. |
| Escalera este de cuatro franjas | 18 vuelos, 19 descansillos, cinco portales; claro entre barandillas 1,21 m | Continuidad anterior; recorrido, giros y envolventes visuales pendientes. |
| Descansillos de transferencia | aprox. 1,10–1,11 × 3,10 m | Registro histórico; revisar maniobra real de giro. |
| Plataformas portal | aprox. 1,30 × 6,52 m | Registro histórico. |
| Ascensor | hueco registrado 3 × 3 m, cabina/puertas estáticas | Capacidad útil, servicio por planta y salida alternativa pendientes. |
| Umbrales L3–L5 | 0,11–0,15 m por debajo de las losas en registros anteriores | Revisar visual/contextualmente; no levantar a ciegas. |

El dato de anchura entre barandillas es mayor que varios pasos y no debe extrapolarse a la circulación general. Toda anchura útil se mide entre elementos más cercanos, incluyendo puerta abierta, columna, panel, equipo, marco, pasamanos y utilería.

## 5. Reglas dimensionales de diseño

Estas reglas son propuestas de comprobación, no nuevas dimensiones para aplicar automáticamente:

1. **Altura libre:** medir piso terminado hasta la cara inferior más baja (viga, tubería, bandeja, señal, luminaria o marco). Contrastar cada criatura y pose con la envolvente visual real; incluir margen y animación.
2. **Puertas:** registrar claro entre jambas, claro bajo dintel, umbral, sentido y barrido de apertura, colisión abierta/cerrada y acceso al control. Distinguir paso de personal, carga, aislamiento y contención.
3. **Pasillos:** medir claro efectivo y estrechamientos, cruces, giros, puntos de pérdida de visión, camilla/objeto transportado y alternativa de escape.
4. **Escaleras:** medir huella, contrahuella, ancho libre, barandilla, descansillo, llegada a la cota real y acceso de mantenimiento. No considerar una escalera de mano como salida general.
5. **Ascensores:** medir cabina útil, umbral/puerta por nivel, carga, espacio de maniobra y recorrido alternativo si falla energía.
6. **Habitaciones:** dimensionar equipo + área de trabajo + circulación + mantenimiento + evacuación. La huella de piso sola no basta.
7. **Estructura:** documentar losa, muro, columna, viga, apoyo, junta y cortador Boolean antes de abrir vanos o mover un recinto.
8. **Instalaciones MEP:** registrar diámetro/ancho de ductos, tuberías y bandejas; altura inferior, puntos de registro, válvulas, drenaje, sectorización, recorrido de sustitución de maquinaria y destino de los sistemas.
9. **Gameplay:** documentar escondite, entradas/salidas, cobertura, línea visual, emisión/atenuación de ruido y distancia de reagrupamiento. Ningún escondite garantiza seguridad total.
10. **Rutas separadas:** verificar personal/visitantes, suministros, pacientes, muestras, mantenimiento, restringidos y emergencia; documentar cruces y controles.
11. **Trazabilidad:** cada medida lleva nombre de objeto/colección, versión .blend, método, precisión, si es AABB o claro interior y estado de verificación.

## 6. Validación de cada habitación

Antes de aprobar: vista MCP completa de la sala y su conexión; medidas de suelo/muros/techo; claro de cada puerta; barrido de puerta; colisión; giro con jugador/equipo/objeto o camilla; acceso de mantenimiento; ruta de salida; envolvente animada de criaturas; iluminación y materiales; coherencia con referencias. Un raycast recto no sustituye este recorrido.

Registrar cada resultado como **confirmado**, **propuesto**, **pendiente** o **bloqueado**. No declarar un paso transitable si solo se alinean pisos o el rayo no impacta.

## 7. Fuentes

- AGENTS.md, §§30, 31 y 47: escala, espacios funcionales, circulación, auditoría y aprobación.
- fotos-referencia/modelos-referencia.png: alturas aproximadas y diseños oficiales de criaturas; consultada en imagen completa, no alterada.
- Escena viva v105 vía Blender MCP: bounds y estado de escena. La sesión informó is_dirty=True.
- docs/fm_nexus_nivel2.md y docs/CURRENT_STATE.md: dimensiones previamente registradas de puertas, escalera y métricas del jugador; varios valores aún no revalidados.
- Pendientes: resolver número de niveles; revisar altura libre/estructura/MEP; calcular claro libre del aseo/oficina y verificar giro/accesibilidad; medir envolventes reales, puertas, ancho interior y navegación con equipo/objetos.

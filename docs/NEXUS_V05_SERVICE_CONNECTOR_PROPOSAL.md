# FRECUENCIA MUERTA — Propuesta de conector de servicio V05

Estado: **ejecutado y auditado en v114.**
Base: `FM_NEXUS_V05_level1_v114.blend`.
Fecha: 2026-11-01.

## 1. Objetivo

Resolver la continuidad funcional entre el almacén y mantenimiento sin reconstruir las salas ni eliminar la puerta de carga existente. La ruta debe ser comprensible, recorrible, coherente con la función industrial y compatible con la escala de los personajes.

## 2. Geometría comprobada

| Elemento | Límites |
|---|---|
| Almacén | x −8,0..4,0; y −9,7..−1,7; suelo top −5,65 |
| Muro este del almacén | x 3,86..4,14; y −9,7..−1,7; z −5,80..−1,60 |
| Puerta de carga decorativa | x ≈3,84..3,99; y −7,68..−3,73; z −5,80..−3,22 |
| Franja entre naves | x ≈4,0..6,0; y −9,7..−1,7; sin suelo ni techo |
| Muro oeste de mantenimiento | x 5,86..6,14; y −9,7..−1,7; z −5,80..−0,80 |
| Mantenimiento | x 6,0..20,0; y −9,7..−1,7; suelo top −5,65 |
| Banco de trabajo | x 6,125..6,975; y −8,30..−4,50; z −4,85..−4,75 |
| Botiquín | x 6,12..6,22; y −4,475..−4,025; z −3,775..−3,325 |
| Armario | x 6,075..6,325; y −3,60..−2,50; z −4,70..−3,10 |
| Cofre y escalera suroeste | cofre x 6,2..7,0, y −9,45..−8,85; escalera x 6,67..7,33, y ≈−9,38 |

La puerta de carga no tiene vano real: las lamas y el muro macizo están superpuestos. La franja intermedia no tiene piso ni techo. El acceso directo al muro oeste de mantenimiento está ocupado por el banco, el botiquín y el armario.

## 3. Solución recomendada

### 3.1. Paso en el almacén

- Abrir un vano de servicio de **1,60 m de ancho** en el muro este, centrado en y ≈−5,80: y −6,60..−5,00.
- Altura libre: **2,80 m**, de z −5,65 a z −2,85.
- Conservar el marco y la fachada de la puerta de carga. El paño enrollable original se conserva oculto; se construye un estado de servicio con dos paños laterales de lamas y un dintel, dejando el paso central libre.
- Colocar un umbral metálico flush y una cortina de lamas de PVC o un marco de servicio, sin hoja cerrada, para que la ruta sea legible.
- La anchura de 1,60 m permite el paso de un carro pequeño y deja margen para dos jugadores, sin convertir el almacén en un vestíbulo abierto.

### 3.2. Franja de servicio

- Añadir piso macizo x 4,0..6,0; y −9,7..−1,7; z −5,95..−5,65.
- Añadir techo x 4,0..6,0; y −9,7..−1,7; z −1,72..−1,48, alineado con el techo del almacén.
- Cerrar el extremo sur con un muro de 0,28 m de espesor, y −9,84..−9,56, z −5,80..−1,48.
- El extremo norte ya está cerrado por `NEXUS_V05_GAP_-1,7_2`.
- Añadir un desagüe central, dos luminarias industriales y conductos de servicio en el techo. Mantener el pasillo oscuro, con una luz de trabajo intermitente y otra de emergencia.
- Claro interior resultante: **1,72 m de anchura** y **3,93 m de altura**; válido para jugador y para criaturas de hasta 2,5 m de altura, no para el Vigilante de 3,0 m.

### 3.3. Paso a mantenimiento

- Abrir un vano de **1,20 m de ancho** en el muro oeste, en y −4,70..−3,50.
- Altura libre: **2,80 m**, de z −5,65 a z −2,85.
- Desplazar el conjunto del banco y su pegboard **0,25 m al sur**.
- Desplazar el armario **0,15 m al norte**.
- Reubicar el botiquín sobre el banco, en y ≈−6,0, fuera del vano.
- Añadir marco, umbral y hoja de servicio modelada abierta contra el paramento sur, para que la ruta sea visible. No se implementa interacción.
- El paso de 1,20 m deja 0,20 m de margen para el jugador (Ø0,76 m) y 0,20 m para el Vigilante (Ø0,80 m) en el punto más estrecho. Es un paso de servicio, no una ruta principal de evacuación.

## 4. Método no destructivo

1. Conservar las mallas originales de los muros este y oeste y de las lamas de la puerta de carga en una colección histórica oculta, sin borrarlas.
2. Construir muros segmentados de reemplazo alrededor de los vanos, con el mismo espesor y material.
3. Mantener la puerta de carga como fachada; no eliminar el marco, las guías ni la carcasa.
4. Guardar la nueva geometría en una colección propia `NEXUS_V05_SERVICE_CONN`.
5. Auditar contactos, vanos, umbrales, suelo y techo antes de guardar un incremento nuevo.
6. Verificar con rayos horizontales y verticales que el paso está libre; después comprobar con cápsula de jugador y de Vigilante.

## 5. Consecuencias

- La ruta almacén→mantenimiento queda conectada y segregada del corredor principal.
- El almacén conserva su puerta de carga como elemento visual, pero gana un acceso de servicio real.
- Mantenimiento pierde 0,25 m de recorrido junto al banco y 0,15 m junto al armario; el resto de la sala no cambia.
- El pasillo de 1,72 m es estrecho y claustrofóbico, adecuado para el tono del juego. No se usa como ruta principal.
- El Vigilante no puede atravesar el conector por altura; esto debe documentarse como restricción intencional, no como error de escala.

## 6. Criterios de aceptación

- No hay solapamiento entre piso nuevo, techo nuevo y losas existentes.
- Los dos vanos tienen paso libre y umbrales a la cota del suelo.
- El banco, el botiquín y el armario no invaden los vanos.
- La puerta de carga sigue siendo reconocible desde el almacén.
- El pasillo no tiene objetos que bloqueen el paso.
- Los rayos horizontales atraviesan almacén→franja→mantenimiento.
- Los rayos verticales encuentran piso continuo en todo el recorrido.
- La cámara de revisión muestra la ruta y las dos puertas con legibilidad suficiente.
- Se conservan v109, v110, v111, v112 y v113; el incremento validado es v114.

## 7. Alternativas descartadas

- **Abrir toda la puerta de carga (4,2 m):** la franja solo tiene 1,72 m de fondo; quedaría un vestíbulo desproporcionado y difícil de cerrar.
- **Abrir un vano junto a la puerta de carga:** obliga a mover el banco o el armario igualmente y pierde la relación visual con la puerta de carga.
- **Usar el extremo sur abierto:** no hay piso ni techo y saldría del volumen funcional de las naves.
- **Mover el banco a otra pared:** aumenta el alcance y afecta herramientas, pegboard, iluminación y narrativa; no es necesario para 1,20 m.

## 8. Resultado de ejecución en v114

- Método no destructivo aplicado: los muros originales, el tirador y las siete lamas de la puerta de carga se conservan ocultos en `NEXUS_V05_SERVICE_CONN_HIST` (10 objetos). La fachada y el marco de la puerta de carga permanecen visibles.
- Muros segmentados de reemplazo en `NEXUS_V05_SERVICE_CONN`: almacén con vano de 1,60 m (y −6,60..−5,00); mantenimiento con vano de 1,20 m (y −4,70..−3,50); altura libre 2,80 m (z −5,65..−2,85).
- Franja convertida en pasillo con piso, techo, cierre sur, umbrales, marcos, zócalos, bandeja de cables, drenaje, iluminación y señalización.
- Ancho libre real del pasillo ≈1,68 m entre zócalos; vanos entre jambas: almacén 1,46 m y mantenimiento 1,06 m. El jugador (Ø0,76 m) y el Vigilante (Ø0,80 m) caben; el Vigilante de 3,0 m no pasa por altura, restricción intencional.
- Mobiliario recolocado: banco/pegboard −0,25 m en Y (y −8,55..−4,75); armario +0,15 m en Y (y −3,45..−2,35); botiquín sobre el banco en (6,17, −5,95, −4,52). Los vanos quedan libres con 5 cm de holgura.
- Auditoría: rayos bajos almacén→pasillo, pasillo→mantenimiento y diagonal **CLEAR**; verticales impactan el piso a z −5,65. La bandeja de cables a z −1,797 es el límite superior real del pasillo.
- Render de revisión: pasillo oscuro de servicio con zócalo verde, carteles “MUELLE” y “MANTENIMIENTO”, flechas y puertas laterales. Composición aceptable; el ruido del techo en EEVEE no es geometría.
- Corrección posterior: los zócalos continuos que cruzaban los vanos se sustituyeron por cuatro segmentos `TRIM_W_S`, `TRIM_W_N`, `TRIM_E_S` y `TRIM_E_N`; ya no hay bordillo de tobillo.
- Limitaciones: puertas y hojas son geometría estática, sin interacción; el conector no está probado con cápsula de jugador en Godot; la iluminación y el arte siguen siendo provisionales. No se ha exportado el proyecto.
- Estado final: `FM_NEXUS_V05_level1_v114.blend`, 7.410 objetos, 50 colecciones, 140 objetos de conector y 10 históricos. v113/v112/v111/v110/v109/v107 se conservan.

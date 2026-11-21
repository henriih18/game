# FRECUENCIA MUERTA — Detalle del Nivel 2 de NEXUS

Estado: **detalle y narrativa del Nivel 2 completados en Blender**. No se ha
exportado a Godot en esta fase.

## Versión de trabajo

| Dato | Valor |
|---|---|
| Archivo | `FM_NEXUS_V05_level1_v90.blend` |
| Tamaño | 3.170.021 bytes |
| Cámara activa guardada | `NEXUS_V05_CAM_Corridor` |
| Objetos de escena | 7.079 |
| Objetos nuevos L2B | 492 |
| Colecciones nuevas | `NEXUS_STORY_L2A`, `NEXUS_STORY_L2B` |

Se conservan las versiones anteriores `v86`–`v89` como respaldo.

## Salas trabajadas

### NAVE

- Anillo de techo corregido: ya no sobreexpone ni domina la imagen.
- Barricada y cinta de peligro alrededor del tanque central.
- Zona de carga con pallet jack, palés, cajas y estantería caída.
- Técnico fallecido con linterna, casco, tablilla y rastro de sangre.
- Cadena colgante, caja fuerte, maletín de espécimen y lámpara de trabajo.
- Señalización de carga y contención.

### LABORATORIO DE BIOLOGÍA

- Isla central con fregadero, microscopio, centrífuga, gradilla y taburetes.
- Puesto de decontaminación junto a la puerta: ducha, lavaojos y residuos
  biológicos.
- Vitrina de muestras corregida y apoyada en la pared norte.
- Equipo sobre el banco norte.
- Rastros del incidente: guante, bandeja caída, papeles, huella en el cristal y
  resto humano junto a un tanque.

### LABORATORIO DE QUÍMICA

- Isla central con dos fregaderos, reactivos, material de vidrio y maletín.
- Estanterías de reactivos y equipo sobre el banco norte.
- Campana con conducto vertical y tramo horizontal.
- Carro volcado, botellas, derrame y polvo neutralizante.
- Ducha de emergencia, lavaojos y traje hazmat.
- Desagüe, bajante industrial y señalización de peligro.

### AIRLOCK

- Ducha de descontaminación en el techo, boquillas, tuberías y drenaje.
- Banco, cepillo de botas, PPE doblado, traje colgado y ganchos.
- Panel de control, manómetro, biocontenedor y material de limpieza.
- Señalización legible de esclusa y ducha de emergencia.

### ARCHIVO CIENTÍFICO

- Cuatro archivadores planos con cajones, etiquetas y carteles.
- Mesa de consulta con lámpara, silla, papeles y carpetas.
- Carro de archivo, cajas sobre estanterías, silla volcada y deshumidificador.
- Rastro de sangre hasta la puerta oeste y huella en la pared.
- Carteles de confidencialidad, acceso restringido y consulta.

### SERVIDORES

- Silla de operador, carro de diagnóstico y cables.
- Dos SAI en la pared este, baldosas técnicas y puerta de rack abierta.
- Panel quemado, discos en el suelo, botellas de supresión y extintor.
- Carteles de clima controlado, UPS y supresión.

### SALA DE ANÁLISIS

- Cabina de bioseguridad en la pared norte.
- Centrífuga de suelo, carro central con viales y pipetas.
- Nevera de muestras, bandejas, contenedor de cortantes y derrame tóxico.
- Sillas y taburete caídos, papeles y panel de protocolo.
- Carteles de análisis, bioseguridad y refrigerador de muestras.

## Cámaras de revisión

| Sala | Cámara | Altura aproximada |
|---|---|---|
| NAVE | `NEXUS_V04_CAM_Nave` | existente |
| BIOLOGÍA | `NEXUS_V04_CAM_Bio` | existente |
| QUÍMICA | `NEXUS_V04_CAM_Chem` | existente |
| AIRLOCK | `NEXUS_V04_CAM_Airlock` | 2,15 m sobre el suelo |
| ARCHIVO | `NEXUS_V04_CAM_Archivo` | 2,25 m sobre el suelo |
| SERVIDORES | `NEXUS_V04_CAM_Servidores` | existente |
| ANÁLISIS | `NEXUS_V04_CAM_Analisis` | 2,10 m sobre el suelo |

Los encuadres se revisaron con renders EEVEE de 640 px. La cámara activa del
archivo sigue siendo la del corredor para no alterar la vista de trabajo.

## Auditoría

- `blender_concept/audit_l2a_props.py`: sin objetos fuera de los límites de sala
  ni bajo el suelo en NAVE, BIOLOGÍA y QUÍMICA.
- `blender_concept/audit_l2b_props.py`: sin objetos fuera de límites ni bajo el
  suelo en AIRLOCK, ARCHIVO, SERVIDORES y ANÁLISIS.
- Los avisos de soporte y las colisiones restantes corresponden en su mayoría a
  ensamblajes intencionales: carteles, huellas, piezas de mobiliario, botellas
  dentro de vitrinas, cuerpos y conductos.
- Los contactos reales detectados se corrigieron: fregona contra traje,
  biocontenedor contra cepillo, sillas caídas atravesando el suelo y vitrina de
  biología invertida.

## Escala de puertas y accesos

Las puertas interiores del Nivel 2 tienen una hoja de **3,12 m de altura** y
**1,72 m de anchura**; la puerta de la NAVE es de **3,12 m de anchura**. La altura
libre supera la altura oficial máxima de las criaturas:

| Criatura | Altura oficial |
|---|---|
| El Imitador | 2,2–2,5 m |
| El Vigilante | 2,5–3,0 m |
| El Coleccionista | 2,0–2,5 m |
| La Sombra | 2,0–2,5 m |

El Vigilante dispone de unos 0,12 m de margen vertical en las puertas estándar.
Las puertas son geometría estática en esta fase: no se ha validado todavía su
apertura, colisión dinámica ni navegación de criaturas.

## Limitaciones

- El arte sigue siendo blocky/provisional; no es arte final.
- Las puertas y muchos mecanismos son geometría estática.
- No hay criaturas ni personajes jugables modelados en la escena.
- No se ha exportado nada a Godot.
- Los renders de revisión no se guardaron como capturas del proyecto.

## Siguiente paso

El Nivel 2 queda cerrado a nivel de estructura, props, narrativa y revisión
visual. El siguiente trabajo debe abordar la integración o el siguiente sistema
del plan, no volver a reconstruir estas salas.

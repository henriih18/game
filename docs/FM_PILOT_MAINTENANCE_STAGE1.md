# FM — Piloto Mantenimiento · Etapa 1

## Preparación y selección de assets existentes

Estado: **propuesta para aprobación**. No se ha modificado ningún asset, escena ni el nivel.

Fuente: `nexus/nivel_01/NEXUS_L1_V05.blend`, escena `NEXUS_L1_V05`, 2.445 objetos / 2.217 mallas / 19 colecciones. Consultas de solo lectura por nombre y por límites espaciales. Se aplicó la checklist de `blender-scene-setup`; no se ejecutó `scene_audit.py` en esta etapa.

## 1. Métrica de la sala

- Superficie: **14,0 × 8,0 m**; altura libre **5,0 m**.
- Suelo: `NEXUS_V05_MANTENIMIENTO_FLOOR` en `(13, -5,7, -5,8)`, 14×8×0,3 m, material `NEXUS_V05_MAT_Floor_Worn`, UV0.
- Muros norte/sur/oeste de hormigón, 5,0 m de alto; entrada norte de 1,62×3,12 m; puerta de servicio oeste de 1,2×2,8 m.
- Techo y muro este no se capturaron por los límites de la consulta; por geometría la sala está cerrada (techo aproximado z=-0,8; muro este x=20).
- La sala no tiene vigas, columnas, trusses, cable trays ni estructura industrial visible. Es una caja lisa.
- Base métrica a conservar: **no agrandar ni reducir la sala**; el bloqueo debe partir de 14×8×5 m.

## 2. Inventario y decisión

### A. Conservar y limpiar (geometría útil, UV1 o prop independiente)

| Asset | Ubicación | Decisión |
|---|---|---|
| Extintor `NEXUS_ASSET_V05_MAINT_EXTINGUISHER_*` | (10,00, -9,05, -5,65) | Conservar; auditar PBR, escala y UV. |
| Carro de herramientas `..._TOOL_CART_tool_cart` | (10,20, -5,00, -5,65) | Conservar; revisar ruedas, asas y colisión. |
| Carro industrial `..._CART_industrial_storage_cart` | (8,90, -7,15, -5,65) | Conservar; revisar PBR y colisión. |
| Alarma `..._FIRE_ALARM_*` | (8,00, -1,68, -3,27) | Conservar; integrar en pared. |
| Armario/panel de pared `..._CABINET_box_02`, `..._PANEL_box_02` | (6,20,-2,90,-3,89) / (13,00,-6,85,-4,29) | Conservar; añadir cableado/etiquetas. |
| Caja eléctrica `..._POWER_BOX_*` | (9,00, -9,50, -3,40) | Conservar como base; rehacer cableado. |
| Caja de herramientas `..._BENCH_TOOLBOX_*` | (6,55, -6,80, -4,75) | Conservar; revisar materiales. |
| Herramientas pequeñas (martillo, alicates, destornilladores, llave) | x≈6,2; y -6,0…-8,0 | Conservar; completar materiales y soportes. |
| Lámpara enjaulada `..._CAGED_LIGHT_*` | (9,50, -5,00, -1,53) | Conservar la carcasa; rehacer luz en Godot. |
| Barril, cajas, cilindros, escalera, botiquín, rejilla de suelo, cinta de peligro, manchas de aceite | este/sur de la sala | Conservar como props de ambientación; auditar UV/PBR y colisiones. |
| Puerta de servicio oeste y letrero | x≈6,2–6,7 | Conservar como pieza; no convertirla aún en puerta funcional. |

### B. Conservar como bloqueo/referencia, pero rehacer la geometría final

| Elemento | Motivo | Acción |
|---|---|---|
| Suelo, muros norte/sur/oeste, techo y muro este | Dimensiones correctas; UV0 y superficies lisas | Conservar el volumen; rehacer paneles, juntas, zócalos, biseles y UV. |
| Puerta de entrada `NEXUS_V05_MANTENIMIENTO_DOOR_LEAF` y marco | Escala y posición correctas; UV0 | Conservar como bloqueo; rehacer hoja/marco con detalles, cristal, cierre y colisión. |
| Bancada oeste (patas, estante, tablero) | Base funcional y escala correcta; UV0 | Conservar layout; rehacer tablero, cajones, soportes y UV. |
| Caldera `BOILER_*` | Volumen y posición correctos; cilindro liso con bandas | Rehacer cuerpo, bridas, remaches, registro, aislamiento, tuberías, válvulas y placa. |
| Generador `NEXUS_V05_MAINT_GEN` | Masa de 3,2×2,2×2,6 m; UV0 | Rehacer como máquina fija industrial, con bastidor, motor, alternador, radiador, escapes, cableado y placa. |
| Tuberías `MAINT_PIPE_0/1`, flanges, clamps, válvula | Tubos de 12 m sin codos, soportes ni juntas; UV0 | Rehacer con kit modular: tubos, codos, bridas, soportes, juntas y válvulas. |
| Tanque de aire `AIR_TANK` y tubería | Volumen correcto; UV0 y detalles simples | Conservar como base; añadir bridas, válvulas, manómetro, soportes y UV. |
| Lámparas A/B y luminaria de emergencia | Posiciones correctas; UV0 | Conservar posición; rehacer carcasa/óptica y luces en Godot. |
| Placas/letreros flotantes | Texto y placas separadas | Integrar en soportes; evitar texto flotante. |

### C. Descartar o sustituir

- `NEXUS_V05_B_MAINT_CABINET_DOOR` oculta en el origen; no es una pieza válida de la sala.
- Rellenos/luces de área 450/650 W de Blender: no se trasladan; la iluminación se decide en Godot.
- Partes ocultas o duplicadas de generador/caldera que no aportan silueta.
- Cualquier material o asset sin licencia verificada queda fuera de aprobación de distribución.

## 3. Materiales y UV

- Arquitectura/props V05: **UV0** en su mayoría; no se pueden aprobar como final.
- Assets importados: UV1, pero hay que revisar densidad, costuras, normales y PBR.
- Materiales existentes reutilizables como base: `NEXUS_Rusted_Metal`, `NEXUS_Steel`, `NEXUS_Painted_Metal`, `NEXUS_Concrete`, `NEXUS_Concrete_Dark`, `NEXUS_Wood`, `NEXUS_Oil`, `NEXUS_Red_Matte`, `NEXUS_SignPlate`, `NEXUS_Glass`.
- Los materiales finales deben cumplir `FM_QUALITY_STANDARD.md`: sRGB/lineal correcto, ORM, mipmaps, compresión, resolución 1024/2048 y desgaste intencionado.

## 4. Colisiones y física

- La sala actual usa colliders AABB generados; no se conservan como solución final.
- Cada asset nuevo llevará colisión propia: primitivas/convex hull, 1–3 shapes por prop, naming `COL_`.
- Caldera, generador, tanque, bancada y tuberías: colisión estática; herramientas/cajas pequeñas: RigidBody si se decide interacción.
- Puerta de entrada y puerta de servicio: conservar el sistema existente; no añadir puertas nuevas en esta etapa.
- Suelo y rejilla: colisión coherente; la rejilla no debe crear un hueco de caída no diseñado.

## 5. Zonificación del bloqueo (etapa 2)

- **Norte:** entrada principal, puerta de 1,62×3,12 m, zona de tránsito.
- **Oeste:** bancada, tablero de herramientas, armario, extintor, puerta de servicio.
- **Centro-este:** generador industrial fijo, con espacio de mantenimiento perimetral.
- **Sureste:** caldera, tanque de aire, tuberías verticales, escalera.
- **Norte/techo:** tuberías principales, soportes, cable trays y estructura.
- **Centro:** rejilla de suelo, manchas de aceite, cinta de peligro; circulación libre entrada → servicio → equipos.
- Añadir estructura industrial no existente: pilastras, vigas de techo, soportes de tubería y paneles de pared, sin invadir la circulación.

## 6. Criterios de aceptación de la etapa 1

- Inventario revisado y decisiones de conservar/rehacer documentadas.
- Sala y equipos mantienen escala real.
- No se ha modificado ningún asset.
- El bloqueo de etapa 2 puede construirse sobre la geometría existente sin agrandar la sala.
- Los assets que se conserven tienen UV/PBR/colisión verificables o una acción correctiva asignada.

## 7. Pendiente de aprobación antes de la etapa 2

1. Confirmar que generador, caldera y tuberías se rehacen (no se parchean).
2. Confirmar la incorporación de estructura industrial nueva (vigas, pilastras, cable trays) dentro de la sala.
3. Confirmar que la puerta de servicio queda como pieza visual, sin convertirla aún en puerta funcional.
4. Confirmar presupuesto de texturas del piloto (1024/2048) y número de assets nuevos.

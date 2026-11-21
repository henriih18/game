# FRECUENCIA MUERTA — Piloto Mantenimiento
## Etapa 2 — Bloqueo arquitectónico y distribución

**Estado:** bloqueo terminado, pendiente de aprobación para modelado final.
**Fecha:** 2026-11-04.
**Ámbito:** únicamente la sala de Mantenimiento / Sala de máquinas.
**No se ha modificado ninguna otra habitación ni se ha empezado el trabajo de criaturas.**

---

## 1. Resumen ejecutivo

Se ha construido el bloqueo arquitectónico y de distribución de Mantenimiento sobre una copia recuperable del máster. El objetivo de esta etapa no era entregar el arte final, sino fijar:

- La estructura industrial que faltaba en la sala.
- La posición, escala y volumen de la nueva generación de equipos.
- La circulación, las holguras de mantenimiento y las zonas de seguridad.
- La base sobre la que se modelarán, texturizarán y exportarán los assets finales.

El bloqueo se lee correctamente en las cuatro vistas de revisión. Todavía **no** es un asset de calidad comercial: el generador sigue siendo una caja negra, la caldera sigue pareciendo un barril marrón y no hay UVs, PBR, bake, LOD ni colisiones de Godot. Esos trabajos corresponden a la siguiente fase.

---

## 2. Archivos y salvaguardas

- **Máster original:** `nexus/nivel_01/NEXUS_L1_V05.blend` — no se ha sobrescrito durante esta etapa; su mtime sigue siendo 2026-11-03 16:23. Git lo marca como modificado por cambios previos del proyecto, no por este piloto.
- **Copia de trabajo:** `nexus/nivel_01/FM_PILOT_MAINTENANCE_v01.blend`.
- **Escena:** `NEXUS_L1_V05`.
- **Colección del piloto:** `FM_PILOT_MAINTENANCE`.
- **Notas internas:** text block `FM_PILOT_STAGE2_NOTES`.
- No se ha borrado ningún objeto del máster. Los objetos antiguos que estorbaban se han ocultado de forma reversible (`hide_viewport`, `hide_render`, `hide_set`).
- No se ha tocado Godot ni se ha exportado ningún GLB en esta etapa.

---

## 3. Estado real de la sala

| Dato | Valor |
|---|---:|
| Superficie interior | 14 × 8 m |
| Altura libre | 4,73 m |
| Rango X | 6,14 – 19,86 m |
| Rango Y | -9,56 – -1,84 m |
| Suelo | z = -5,65 m |
| Techo | z = -0,92 m |
| Entrada norte | x = 12,08 – 13,92 m |
| Puerta de servicio oeste | 1,2 × 2,8 m, solo visual en este piloto |
| Muros | hormigón, UV0 en su mayoría |
| Suelo | `NEXUS_V05_MANTENIMIENTO_FLOOR`, 14 × 8 × 0,3 m |

La sala no se ha agrandado ni reducido. Se conserva la métrica de 14 × 8 × 5 m aprobada en la Etapa 1.

---

## 4. Bloqueo construido

### 4.1. Estructura industrial

Se añadieron **123 objetos** en `FM_PILOT_STRUCT`:

- **4 vigas transversales en I** a lo largo de Y, en x = 7,4 / 10,8 / 14,2 / 17,6 m, a z = -1,07 m.
- **3 vigas longitudinales** a lo largo de X, en y = -2,4 / -5,7 / -9,0 m, a z = -1,32 m.
- **13 pilastras de pared** con placa base y cuatro anclajes cada una:
  - Muro norte: x = 7,0 / 9,5 / 11,2 / 14,8 / 16,8 / 18,8 m.
  - Muro sur: x = 7,4 / 11,3 / 14,3 / 18,85 m.
  - Muro este: y = -2,4 / -6,6 m.
  - Muro oeste: y = -2,3 m.
- Zócalo metálico perimetral en muro sur y este.
- Placas de extremo en las vigas.
- La pilastra sureste se desplazó a x = 18,85 m para no chocar con el riser del colector.

La estructura no invade la circulación principal. Las vigas quedan por encima de la altura de paso y las pilastras están adosadas a los muros.

### 4.2. Bandejas portacables

**36 objetos** en `FM_PILOT_CABLE_TRAY`:

- Bandeja en muro norte, por encima de la puerta de entrada.
- Bandeja en muro este, con soportes y tramos.
- Soportes tipo mensula y uniones.
- Pendiente de detalle final: tapas, curvas, bajantes, sujetacables y etiquetado.

### 4.3. Soportes de tubería

**37 objetos** en `FM_PILOT_PIPE_SUPPORTS`:

- Soportes trapecio para los dos colectores principales.
- Varillas de suspensión desde techo hasta trapecio, corregidas para quedar conectadas físicamente.
- Placas de techo.
- Soportes de cabecera en el muro sur.
- Pendiente de detalle final: abrazaderas, amortiguadores, aislamiento y tornillería.

### 4.4. Generador

**Pad:** `PILOT_EQUIP_GeneratorPad`, 3,8 × 2,8 × 0,15 m, en (13, -7,6).

**Conjunto:** `PILOT_EQUIP_Gen_*`.

- Skid estructural 3,4 × 2,0 m, con cuatro patas y placas de anclaje.
- Cuerpo cerrado de 2,8 × 1,7 × 1,75 m.
- Radiador y shroud con ventilador de 6 palas y rejilla.
- Panel de control con pantalla y tres botones.
- Puerta de acceso con manilla.
- Depósito de combustible y tapón.
- Escape vertical con silenciador y sombrerete.
- Argollas de izado en las cuatro esquinas.
- Costuras de panel y louvres del radiador.
- Cinta de seguridad perimetral y cuatro bolardos.

**Huella total:** 3,4 × 2,0 × 1,89 m.
**Holguras:** ~5,1 m a cada lado; 4,7 m al frente; ~0,9 m al fondo.

### 4.5. Caldera

**Pad:** `PILOT_EQUIP_BoilerPad`, 2,6 × 2,4 × 0,15 m, en (17,3, -7,8).

**Conjunto:** `PILOT_EQUIP_Boiler_*`.

- Cuerpo cilíndrico de radio 0,82 m y 2,25 m de altura.
- Cúpula superior, faldón y base.
- Cuatro bandas de refuerzo.
- Chimenea con reducción y sombrerete.
- Quemador y puerta de registro.
- Brida de registro con 12 tornillos.
- Panel de manómetros con dos relojes.
- Placa de identificación.
- Tuberías de alimentación y vapor, risers y válvulas.
- Colector sur de tres líneas con uniones esféricas y bridas.

**Huella total:** 1,72 × 1,72 × 2,54 m.
**Holguras:** 1,70 m al muro este; ~0,9 m al fondo; 5,1 m al frente.
**Aislamiento:** la chimenea atraviesa el techo a z = -0,93 m. Es intencionado; en el modelo final necesitará un pasamuros y un flashing.

### 4.6. Tuberías principales

- Dos colectores longitudinales de 12 m en z = -2,2 m, y = -9,0 / -6,0 m.
- Flanges en x = 8 / 11 / 14 / 17 / 19 m.
- Clamps y soportes verticales en el muro este.
- Válvula de volante rojo.
- Colector sur de tres líneas con válvula, bridas y uniones esféricas.
- El colector se acortó para liberar la escalera oeste; el riser se movió a x = 7,6 m.
- Pendiente de detalle final: codos, juntas de expansión, soportes, aislamiento, identificación de fluido y sentido de flujo.

### 4.7. Marcas de suelo y seguridad

**7 objetos** en `FM_PILOT_MARKINGS`:

- Delimitación amarilla del pad del generador.
- Línea de seguridad y esquinas.
- Bolardos amarillos.
- Pendiente de detalle final: señalización de tensión, prohibición de paso, identificación de equipos y flechas de evacuación.

---

## 5. Objetos antiguos ocultos o reubicados

No se ha borrado nada.

- **44 objetos** antiguos de generador, caldera y tuberías, ocultos de forma reversible.
- **4 objetos** que intersectaban el nuevo bloqueo: `NEXUS_V05_B_MAINT_ALTA_PLATE`, `NEXUS_ASSET_L1R_MAINT_PANEL_box_02`, `NEXUS_V05_D_MAINT_GAUGE_PIPE`, `NEXUS_V05_E_MAINT_GAUGE_NECK`.
- **4 cintas de peligro antiguas** `NEXUS_V05_B_MAINT_HAZ_*`, sustituidas por la nueva cinta del generador.
- **Rótulo `NEXUS_V05_B_MAINT_ALTA_TEXT`**, oculto porque quedaba flotando sobre el nuevo generador.
- **Cajas `NEXUS_V05_B_MAINT_CRATE_0/1`** y sus bandas/tape, movidas fuera del pad de caldera.
- En total hay **73 objetos ocultos** en la sala; la ocultación es reversible y está documentada.

Los props que se conservan (extintor, carros, herramientas, armario, panel, lámpara enjaulada, barril, cilindros, escalera, botiquín, rejilla, cinta, manchas de aceite y puerta de servicio) siguen en la escena como base de trabajo.

---

## 6. Métricas del bloqueo

| Concepto | Valor |
|---|---:|
| Objetos totales en `FM_PILOT_MAINTENANCE` | 325 |
| Mallas del piloto | 321 |
| Mallas con UV | 0 |
| Materiales usados | 9 |
| Objetos en `FM_PILOT_STRUCT` | 123 |
| Objetos en `FM_PILOT_CABLE_TRAY` | 36 |
| Objetos en `FM_PILOT_PIPE_SUPPORTS` | 37 |
| Objetos en `FM_PILOT_EQUIP_BLOCKOUT` | 118 |
| Objetos en `FM_PILOT_MARKINGS` | 7 |
| Objetos en `FM_PILOT_RENDER` | 4 |
| Pasillo entre generador y caldera | 2,38 m |
| Holgura caldera–muro este | 1,70 m |
| Holgura generador–muro oeste | ~5,1 m |
| Acceso trasero generador/caldera | ~0,9 m |

**Lectura:** el bloqueo cumple la escala y la circulación, pero **no cumple todavía el estándar de producción** de UVs, PBR, topología, bake, LOD y colisiones. Es una base de distribución, no un asset final.

---

## 7. Correcciones aplicadas durante el bloqueo

- Equipos desplazados +0,40 m hacia la entrada para dejar acceso trasero.
- Pilastra sureste movida para liberar el riser del colector.
- Colector sur acortado y riser oeste reubicado para liberar la escalera.
- Cajas y cintas retiradas del pad de caldera.
- Cartel ALTA, panel de pared y piezas de manómetro ocultos por intersección.
- Rótulo ALTA TENSIÓN retirado del generador.
- Varillas de soporte conectadas al techo y a la trapeza.
- Se detectó una única intersección restante: la chimenea de la caldera atraviesa el techo. Es intencionada y se resolverá con pasamuros en el modelo final.

---

## 8. Revisión visual

Renders de la última revisión:

- `docs/fm_pilot_maintenance_stage2/01_entrance.png` — vista desde la entrada.
- `docs/fm_pilot_maintenance_stage2/02_generator_boiler.png` — generador y caldera desde el oeste.
- `docs/fm_pilot_maintenance_stage2/03_east.png` — vista desde el este.
- `docs/fm_pilot_maintenance_stage2/04_plan.png` — planta con techo oculto.
- `docs/fm_pilot_maintenance_stage2/contact.jpg` — hoja de contacto 2 × 2.

### Lo que funciona

- La sala ya se lee como una sala de máquinas industrial, no como una caja vacía.
- La estructura de techo, las pilastras, las bandejas y los soportes dan escala y profundidad.
- El generador tiene volumen, skid, radiador, panel, escape, argollas y delimitación de seguridad.
- La caldera tiene cuerpo, cúpula, bandas, registro, manómetros, chimenea y colector.
- La circulación principal y el acceso trasero son legibles en planta.

### Lo que todavía no está aprobado

- El generador sigue siendo una **caja negra boxy**; le faltan paneles con relieve, louvres en la cara frontal, tornillería, bisagras, placas y desgaste.
- La caldera sigue pareciendo un **barril marrón**; el material y la silueta necesitan el modelo final.
- Los soportes verticales antiguos se veían como varillas finas; se ocultaron reversiblemente el 2026-11-05 y se conservan los soportes de cabecera del muro sur. El modelado final debe sustituirlos por perfiles, abrazaderas y amortiguadores (ver §14).
- Quedan props antiguos blancos y manchas de aceite muy grandes que distraen.
- La iluminación de la sala no se ha tocado en esta etapa; sigue siendo la del nivel.
- No hay UVs, texturas, bake, LOD, colisiones ni integración en Godot.

---

## 9. Qué falta para convertir esto en el estándar del juego

### 9.1. Modelado final

- Generador: envolvente de paneles, puertas, bisagras, louvres, radiador, ventilador, escape, placa, etiquetas, tornillería y desgaste.
- Caldera: cuerpo con costuras, bridas, registro, quemador, tubuladuras, válvulas, aislamiento, placa y chimenea con pasamuros.
- Tuberías: codos, bridas, válvulas, soportes, juntas y aislamiento con lectura industrial.
- Estructura: biseles, placas, anclajes y uniones con calidad de kit.
- Bandejas: curvas, tapas, bajantes y sujetacables.
- Props conservados: auditoría PBR, escala, pivote y desgaste.

### 9.2. UV, materiales y bake

- UVs sin solapamientos, con margen y texel density coherente.
- PBR: albedo, normal, roughness, metallic, AO y emisión.
- Desgaste por bordes, cavidades, aceite, polvo y humedad.
- Bake de high a low donde aporte detalle.
- Presupuesto: 2K para generador/caldera; 1K para props medianos; 512 para pequeños.

### 9.3. Integración en Godot

- Export glTF con escala aplicada, Y-up y sin luces/cámaras.
- Importador nativo de Godot para el piloto, no `GLTFDocument` en runtime.
- Colisiones `COL_` por primitivas/convex hull, no AABB.
- LODs, sombras y materiales importados.
- Iluminación local y pruebas de rendimiento.

---

## 10. Criterios de aceptación del bloqueo

- [x] La sala conserva 14 × 8 × 5 m.
- [x] La circulación principal queda libre.
- [x] El generador y la caldera tienen posición, escala y holguras definidas.
- [x] La estructura industrial no invade el paso.
- [x] No se ha borrado ningún objeto del máster.
- [x] Los originales se han ocultado de forma reversible.
- [x] Existe una versión recuperable del archivo.
- [x] Hay renders de revisión desde cuatro ángulos.
- [ ] UVs, PBR, bake, LOD y colisiones: **pendientes**.
- [ ] Calidad visual comercial: **pendiente de modelado final**.
- [ ] Importación y pruebas en Godot: **pendientes**.

---

## 11. Decisión solicitada

Antes de invertir en el modelado final, necesito la aprobación del bloqueo y de la dirección visual:

1. **Generador:** envolvente industrial en verde/grafito oscuro con acentos naranja de seguridad, paneles de acero y etiquetas NEXUS.
2. **Caldera:** acero oscuro con aislamiento gris, bridas metálicas, volante rojo y placa de identificación.
3. **Tuberías:** acero oscuro y cobre envejecido, con bridas y válvulas rojas; aislamiento solo en los tramos de vapor.
4. **Estructura:** verde industrial oscuro, con tornillería y desgaste; bandejas galvanizadas.
5. **Suelo:** hormigón húmedo, aceite contenido y marcas amarillas desgastadas.

Si se aprueba, el siguiente paso es el **modelado final de generador, caldera y tuberías**, con UVs, PBR, bake, QA y exportación a Godot. No se tocarán otras habitaciones.

---

## 12. Limitaciones de esta etapa

- El bloqueo no es arte final.
- No se ha medido rendimiento porque no se ha exportado a Godot.
- No hay pruebas de colisión ni de navegación con el jugador.
- La iluminación de la sala sigue pendiente de la fase de look final.
- Los props antiguos conservados aún no tienen auditoría PBR completa.
- La puerta de servicio es visual, no funcional.
- La chimenea atraviesa el techo de forma intencionada; falta el pasamuros.

---

## 13. Auditoría por objeto

Se auditó la sala completa: **553 mallas** y **588 objetos** contando empties, luces, cámaras y textos. El resultado está en:

- `docs/FM_PILOT_MAINTENANCE_OBJECT_AUDIT.md` — informe.
- `docs/fm_pilot_maintenance_stage2/object_audit.csv` — métricas crudas.
- `docs/fm_pilot_maintenance_stage2/object_audit_status.csv` — estado por objeto.

Resumen: 301 objetos de bloqueo correctos con UV pendiente, 142 correctos, 51 ocultos reversibles, 19 props heredados con topología a revisar, 19 corregidos, 15 de arquitectura con UV pendiente, 3 decals y 3 contactos revisados. No hay objetos flotantes, materiales sin asignar, texturas rotas ni escalas negativas.

## 14. Revisión 2026-11-05

Revisión de la sala piloto tras la comprobación visual de la zona oeste y de la caldera.

- **Soportes:** se ocultaron reversiblemente 32 soportes obsoletos (`PILOT_SUPPORT_CeilingPlate_*`, `PILOT_SUPPORT_Hanger_*` y `PILOT_SUPPORT_Trapeze_*`, filas y=-9,0 y y=-6,0). Quedan visibles 4 `PILOT_SUPPORT_HeaderBracket_01..04`; el `HeaderBracket_00` se ocultó al recortar el extremo oeste. No se borró ningún objeto.
- **Conexión de vapor:** `SteamDrop` y `SteamNozzle` se movieron a x=17,85; el bajante se acortó a 0,40 m (z=-3,14..-2,74) y se sustituyó el tramo de tapa plana por el codo `PILOT_EQUIP_Boiler_SteamElbow` (arco de 90° de 17,85/-2,76 a 18,01/-2,60, con prolongación hasta 18,14) y la brida `PILOT_EQUIP_Boiler_SteamFlange` en 18,12. La brida de la cúpula se amplió a 0,30 × 0,30 × 0,10 m. El antiguo `SteamPipe_W` queda oculto.
- **Ventilador:** `NEXUS_V05_D_MAINT_FAN` sigue oculto porque intersectaba la columna este; queda pendiente reubicarlo o sustituirlo en el modelado final.
- **Colector sur:** tres líneas anidadas, todas centradas en x=14,0: 00 (superior, z=-2,55) de 9,6 a 18,4; 01 (media, z=-2,80, galvanizada) de 9,0 a 19,0; 02 (inferior, z=-3,05) de 8,4 a 19,6. Los extremos oeste giran 90° hacia el muro sur con `PILOT_EQUIP_PipeHeader_WallElbow_00..02` y bridas de pared en (9,78/9,18/8,58; -9,54); los tres risers oeste (`RiserW_*`) quedan ocultos. Los risers este (`RiserE_*`) quedaron ocultos y las tres líneas se prolongaron hasta el muro este con bridas (ver §15). Las seis tapas esféricas `HeaderJoint_*` y la brida `PipeHeader_Flange_00` están ocultas.
- **Cartel:** `NEXUS_V05_B_MAINT_MACHINE_PLATE` y `..._TEXT` se movieron a y=-5,90, fuera de la columna este; el texto usa `NEXUS_Rubber` para que sea legible.
- **Lámpara:** se ocultaron reversiblemente los cuatro objetos de `NEXUS_ASSET_V05_MAINT_CAGED_LIGHT_*` (malla, cordón, luz y raíz); la lámpara verde de cono se conserva.
- **Materiales:** `NEXUS_Red_Matte` y `NEXUS_Extinguisher_Red` tenían el color de viewport blanco (0,8); se corrigieron a rojo. La botella roja y el extintor ya se ven rojos.
- **Botellas:** siguen siendo props de bloqueo con cuerpo, tapa y válvula. Se añadió un colector de pared con tres salidas y dos latiguillos que conectan las botellas roja y verde; la salida central queda tapada como reserva (ver §15). El objeto gris de la imagen 4 es el extintor (cuerpo/manguera), no el colector de gas.
- **Nota de vigencia:** la §4.6 aún describe dos colectores longitudinales en y=-9,0/-6,0; la escena actual usa un solo colector de tres líneas en y=-9,3, con alturas z=-2,55/-2,80/-3,05 y longitudes anidadas. Se conserva el texto histórico y se anota aquí la diferencia.
- **Verificación:** renders `maint_fix6_west/boiler`, `maint_fix7_boiler/entrance/steam`, `maint_fix8_steam`, `fix10_sign/steam/lamp`, `fix11_sign/cylinders`, `fix12_cylinders` y `fix13_header_w/e` revisados visualmente. Sin UV/PBR/LOD ni pruebas en Godot en esta revisión.

## 15. Colector de gas, escape del generador y cierre este (2026-11-05)

- **Escape del generador:** `PILOT_EQUIP_Gen_Exhaust` se prolongó de z=-3,515 a z=-3,80 (2,635 m; centro -2,4825) para entrar en la tapa del radiador; se añadió `PILOT_EQUIP_Gen_ExhaustFlange` (radio 0,19; altura 0,04) en (14,20; -8,05; -3,73). Render `fix14_generator.png`.
- **Cierre este del colector:** las tres líneas se extendieron hasta x=19,82 (00 de 9,6 a 19,82; 01 de 9,0 a 19,82; 02 de 8,4 a 19,82); se ocultaron `PILOT_EQUIP_PipeHeader_RiserE_00/01/02`; se añadieron `PILOT_EQUIP_PipeHeader_EastFlange_00/01/02` en (19,82; -9,30; z) con radios 0,110/0,095/0,085 y `PILOT_SUPPORT_HeaderBracket_05` en (19,40; -9,44; -2,80). La U de la vista este ya no existe. Render `fix14_header_e.png`.
- **Colector de gas:** en la pared este, colección `FM_PILOT_EQUIP_BLOCKOUT`:
  - Panel `PILOT_EQUIP_GasManifold_Panel` en (19,77; -3,10; -3,95), 0,02×1,30×0,90, con cuatro tornillos.
  - Línea principal `..._Main` en (19,65; -2,55; -2,395), radio 0,028, altura 2,91; cabecera `..._Header` en (19,65; -3,175; -3,95), radio 0,032, longitud 1,05; codo `..._MainElbow` de 90° y tuercas `..._MainUnion`/`..._HeaderUnion` (radio 0,05; profundidad 0,06) que cierran la esquina; válvula principal con maneta roja, regulador y manómetro. Render `fix19_gas_elbow.png`.
  - Tres salidas con codo `..._Outlet_00/01/02` en y=-2,80/-3,10/-3,45; latiguillos `..._Pigtail_00_Hose2` y `..._Pigtail_02_Hose2` (radio 0,017, curvas Bézier, material `M_PILOT_GasHose`) a las botellas roja y verde; la salida central queda con `..._SpareCap` rojo.
  - Es un prop visual: no hay lógica, presión ni simulación de gas. Los latiguillos antiguos (`Pigtail_00`, `Pigtail_02`, `..._Hose`) quedan ocultos; no se borró nada.
- **Uniones oeste:** se añadieron las tuercas hexagonales `PILOT_EQUIP_PipeHeader_Union_00/01/02` en x=9,60/9,00/8,40, y=-9,30, z=-2,55/-2,80/-3,05 (profundidad 0,10; radios 0,105/0,095/0,085; materiales rust/galvanizado/rust). Cubren las tapas planas de la unión colector-codo y dejan los tres codos como conexiones continuas. Render `fix17_union_w.png`.
- **Pasamuros oeste:** se ocultaron las bridas sólidas `PILOT_EQUIP_PipeHeader_WallFlange_00/01/02`; se añadieron anillos `..._WallFlangeRing_00/01/02` (exterior 0,24/0,21/0,19; interior 0,078/0,063/0,053; y=-9,52..-9,56) y manguitos abiertos `..._WallStub_00/01/02` (radio 0,075/0,060/0,050; profundidad 0,10; y=-9,57). Se eliminaron las tapas de pared de los codos `WallElbow_00/01/02`; el tubo atraviesa el anillo y entra en el muro. Renders `fix18_wall/close` y `fix19_wall/close`.
- **Verificación:** renders `fix14_manifold/generator/header_e/entrance`, `fix15_manifold*`, `fix16_manifold*`, `fix17_union_w.png`, `fix18_gas_elbow`, `fix18_wall`, `fix18_wall_close`, `fix19_gas_elbow`, `fix19_wall` y `fix19_wall_close` revisados. Sin UV/PBR/LOD, sin colisiones y sin pruebas en Godot (excluidas por el usuario).
- **Pendiente:** modelado final del panel y soportes, UV/PBR/LOD, colisiones y lógica de gas si se aprueba; el resto de la sala sigue en bloqueo.

## 16. Pase de QA, UV y arte de la sala (2026-11-05)

Pase de revisión objeto por objeto de la sala de Mantenimiento. No se tocaron otras habitaciones ni se modificó la librería compartida `NEXUS_SHARED_ASSETS.blend`. El archivo se guardó con la cámara `PILOT_CAM_01_Entrance` y resolución 1280×720.

### 16.1. Estado de QA y UVs

- **Mallas visibles en la sala:** 528; **173.301 tris** (antes 190.637). Solo el volumen `FM_PILOT_ATMOSPHERE_FOG` queda sin UV por diseño.
- **Estructura:** 147 mallas (`PILOT_STRUCT_*`, `NEXUS_V05_MANTENIMIENTO_*` y el muro oeste de servicio) con UV Smart Project y QA `pass: true`, 0 errores. Se corrigieron normales invertidas, columnas y vigas huecas, anclajes, z-fights de base/placas y escalas.
- **Bandejas de cables:** 36 objetos `PILOT_TRAY_*`; se reconstruyeron los soportes verticales `E_Bracket_00..03`, se corrigió `E_Arm_03` y se aplicó UV. QA `pass: true`, 0 errores.
- **Conexiones de servicio:** 19 objetos `NEXUS_V05_SERVICE_CONN_MAINT_*`; se ajustaron rigidizadores, placa, dintel y umbral. QA `pass: true`, 0 errores.
- **Props, story, disaster y marcas:** 74 props visibles, 17 decals/señalizaciones y el suelo como contexto. Se ocultaron los duplicados `BOLT_3/4/5`, se corrigieron contactos, escalas de decals y el `BLOOD_17`; QA `pass: true`, 0 errores. Se revirtieron las UV añadidas por error a 77 objetos de otras salas.
- **Equipos:** caldera (40 mallas), generador (43), colector de tres líneas (23), colector de gas (35) y soportes (5 individuales) con UV y QA `pass: true`. Se reconstruyeron pernos y botones con cilindros limpios y se eliminaron tapas coplanares.
- **Detalles nuevos:** `PILOT_EQUIP_Gen_Details` + `PILOT_EQUIP_Gen_Label` con el cuerpo y la puerta del generador, `PILOT_EQUIP_Boiler_Rivets` con la caldera y sus bandas, y `PILOT_LIGHT_Maint_Fixture` con el techo: QA `pass: true`, 0 errores.
- **Carro de herramientas:** el asset enlazado original de 29.394 tris se ocultó y se sustituyó por una malla local limpia de **3.704 tris y 4 materiales** (`M_PILOT_Cart_Paint`, `M_PILOT_Cart_Steel`, `M_PILOT_Cart_Rubber`, `M_PILOT_Cart_Dark`), con UV y QA en espacio local `pass: true`. Hay dos instancias: la vertical en (10,2; -5,0; -5,65) y la volcada, apoyada sobre su espalda, con raíz en (16,8; -5,2; -5,28). Se conserva la malla antigua en el carro de la sala contigua, que no se tocó.
- **Herramientas del toolchest:** se ocultaron reversiblemente `NEXUS_ASSET_L1R_MAINT_TOOLCHEST_root`, `..._arrow_simple`, `..._arrow_double_bended.002`, `..._dble_arrow_circular-quarter` y `..._key-no_key`, que no tenían material o eran ayudas de 0 tris.
- **Nota de QA:** `qa_check.py` da falsos positivos de normales interiores y piezas flotantes en objetos pequeños situados lejos del origen (cancelación numérica del volumen firmado). La malla del carro pasa en el origen; en su posición de sala el mismo chequeo reporta errores que no existen en la geometría. Se documenta la limitación y se usa el pase en espacio local como referencia.
- **Assets enlazados:** los props de `NEXUS_SHARED_ASSETS.blend` (armario, herramientas, lámparas de pared, alarma, caja eléctrica, extintor, carro industrial, toolbox) no se pueden editar sin override de librería; su QA corresponde a la librería compartida. No se modificaron.

### 16.2. Pase de arte

- **Materiales procedurales:** se rehicieron `M_PILOT_Boiler_Rust`, `M_PILOT_Pipe_Rust`, `M_PILOT_Steel_Galvanized`, `M_PILOT_Steel_Structure`, `M_PILOT_Equipment_Dark`, `M_PILOT_Concrete_Pad`, `M_PILOT_Safety_Yellow` y `M_PILOT_Valve_Red` con ruido, variación de color, rugosidad y bump. Se añadieron `M_PILOT_Equipment_Door`, `M_PILOT_Oil`, `M_PILOT_Lamp_Tube` y `M_PILOT_Atmosphere_Fog`.
- **Aceite:** las manchas de la sala usan `M_PILOT_Oil`, marrón oscuro translúcido con ruido; ya no se leen como agujeros negros.
- **Generador:** puerta de acceso con material propio, bisagras, pernos, placa de datos, etiqueta de advertencia, conducto, cable y rótulo `GEN-04`.
- **Caldera:** 56 remaches abiertos alrededor de las cuatro bandas; se conservan el manway, los gauges, la placa y las conexiones de vapor.
- **Techo:** se añadió una luminaria industrial con dos tubos emisivos (`M_PILOT_Lamp_Tube`) alineada con la luz principal.
- **Iluminación:** se redujeron y recolorearon las luces de la sala (principal 240 W; rellenos 45/35 W; banco 90 W; lámparas 38 W; emergencia 30 W), se añadieron relleno frontal de 40 W, relleno este de 70 W y un spot de 180 W desde la luminaria. Se añadió un volumen de niebla local de densidad 0,008. Render en EEVEE con AgX Medium High Contrast.
- **Verificación visual:** renders `room_light_pass4_details.png`, `room_hero_oilfix.png`, `room_hero_cart_moved.png` y el definitivo `docs/fm_pilot_maintenance_art_pass.png` (cámara `PILOT_CAM_02_GenBoiler`). Se revisaron composición, materiales, fugas de luz y contactos.

### 16.3. Pendientes reales

- El generador y la caldera siguen siendo bloqueos con detalle añadido; falta el modelado final de sus envolventes, tuberías y cableado.
- Falta el pase completo de texturizado/bake (mapas de desgaste, suciedad, normales y ORM) y la revisión de LOD y colisiones.
- Los assets enlazados de la librería compartida no se auditaron ni modificaron en este archivo.
- No hay partículas de polvo/vapor ni simulación; la niebla es un volumen estático.
- No hay pruebas en Godot, navegación ni rendimiento medido en el juego. Esas pruebas siguen excluidas de esta fase.
- No se ha hecho commit; el `.blend` y la documentación siguen sin rastrear en Git.

## 17. Pase de terror, materialidad y QA final (2026-11-05)

Pase de arte y QA de la sala de Mantenimiento con criterio de terror: la luz ambiental debe ser prácticamente nula y la linterna la fuente principal. No se tocaron otras habitaciones, no se modificó la librería compartida y no se hicieron pruebas en Godot.

### 17.1. Iluminación de terror

- **Ajustes globales:** mundo a 0,02; exposición 1,15; AgX Medium High Contrast; EEVEE con niebla volumétrica a 0,0018, tile 2 y 128 muestras.
- **Luces principales apagadas:** `NEXUS_V05_MANTENIMIENTO_LIGHT`, `PILOT_LIGHT_Maint_Spot`, `PILOT_LIGHT_MAINT_EAST`, `PILOT_LIGHT_MAINT_FRONT`, `NEXUS_V05_E_MAINT_FILL` y `NEXUS_V05_F_MAINT_FILL` a 0 W. La tira fluorescente del techo `NEXUS_V05_MANTENIMIENTO_STRIP` usa `FM_MAT_Strip_Dead` (sin emisión); la lámpara blanca con rejilla y su bombilla siguen ocultas.
- **Luces prácticas supervivientes:** banco 3 W, lámparas A/B 2,5 W, emergencia roja 14 W, balizas 3 W, luz de servicio 3 W, relleno de puerta 9 W, relleno frío de banco 4,5 W y baliza roja este de 6 W con foco y carcasa visibles. La sala sin linterna queda casi negra, con rojos de emergencia y amarillos de señalización.
- **Linterna de revisión:** `PILOT_LOOK_FLASHLIGHT`, spot de 760 W, 29°, blend 0,30, color cálido, unido a `PILOT_CAM_ART_HORROR`. La cámara final está en (8,6; -2,6; -3,45) mirando a (15,2; -8,0; -3,72), lens 24. La linterna se puede ocultar para el render sin linterna; en Godot será la linterna del jugador.
- **Verificación:** `docs/fm_pilot_maintenance_horror_pass.png` (con linterna) y `docs/fm_pilot_maintenance_horror_noflash.png` (sin linterna). La segunda demuestra que la sala no depende de luz ambiental para verse.

### 17.2. Materiales

- **Shell:** `FM_MAT_Wall_Concrete`, `FM_MAT_Ceiling_Concrete` y `FM_MAT_Floor_Concrete` usan `dirty_concrete_*` y `concrete_floor_damaged_01_*` con coordenadas de objeto, color oscurecido y rugosidad/normal desde textura. `FM_MAT_Wainscot_Green` usa `green_metal_rust_*` en el zócalo y cladding.
- **Caldera:** `FM_MAT_Boiler_GreenRust` sobre cuerpo, cúpula y chimenea, con `green_metal_rust_*` a escala 2,2 y valor 0,44; las bandas pasan a `FM_MAT_Dark_Steel`. Se probaron variantes de óxido (`rusty_metal_05`) y pintura oxidada; se descartaron por el aspecto de camuflaje/lámina de cobre.
- **Tuberías:** `FM_MAT_Pipe_Rust` con `rusty_metal_03_*` para colector y líneas de vapor/alimentación.
- **Generador:** `FM_MAT_Genset_Paint` y `FM_MAT_Genset_Door` con `metal_panel_*`; `FM_MAT_Dark_Steel` para louvres, bisagras, marcos y detalles.
- **Carro:** `FM_MAT_Cart_Red_Simple`, rojo óxido oscuro procedural; se conservan `M_PILOT_Cart_Steel`, `M_PILOT_Cart_Rubber` y `M_PILOT_Cart_Dark`.
- **Cilindro verde:** `FM_MAT_Cylinder_Green`, verde oscuro apagado, para que no se lea como un panel neón.
- **Caja eléctrica verde de la pared oeste:** el asset enlazado `NEXUS_ASSET_L1R_MAINT_CABINET_box_02` se ocultó reversiblemente porque su pantalla verde dominaba la escena y no se podía reasignar sin override de librería.

### 17.3. Geometría y detalles añadidos

- **Generador:** puerta de servicio grande con marco, tres bisagras, maneta y pestillo; panel de louvres con 7 lamas inclinadas, marco y tornillos; caja de conexiones con conducto; placa de datos y etiqueta; bisel de 0,012 m en el cuerpo. Se ocultaron la puerta pequeña antigua, sus bisagras y sus detalles flotantes.
- **Caldera:** panel de gauges oscurecido; agujas y caras nuevas; purga inferior con válvula de volante rojo y tubo de conexión; se ocultaron las costuras verticales, la escotilla frontal, el tubo de nivel y la escalera que quedaban flotando o sin apoyo.
- **Pared este:** armario eléctrico con puerta, asa, piloto rojo, conductos y cajas de unión; pulsador rojo; baliza roja con lente y foco orientado. Añadido para romper el vacío oscuro de la pared derecha.
- **Suelo:** rejilla del desagüe con cinco barras y dos rollos de cable en el suelo.
- **Puerta oeste:** la hoja se cerró en el plano del muro (rotación Z 90°, centro 6,14; -4,10; -4,25) y se movieron sus rigidizadores; se ocultó el tope de suelo que quedaba dentro.
- **Materiales y QA:** todos los objetos nuevos recibieron Smart UV Project; el cuerpo del generador recibió bisel y se revalidó.

### 17.4. QA de los grupos nuevos

- **Generador:** 79 mallas visibles, QA `pass: true`, 0 errores, 32 warnings aceptados (n-gons en tapas, back-to-back ocultos, ground z). Se reconstruyeron pernos limpios y se corrigieron z-fights, islas flotantes y UVs.
- **Caldera:** 52 mallas visibles, QA `pass: true`, 0 errores, 28 warnings aceptados. Se resolvieron normales interiores, z-fights y piezas flotantes; las caras/agujas nuevas que no se pudieron estabilizar se ocultaron.
- **Pared este:** 14 mallas + muro, QA `pass: true`, 0 errores, 7 warnings. Se ajustaron asa, pulsador y baliza para que toquen sus soportes.
- **Suelo:** barras de desagüe + rollos de cable + suelo, QA `pass: true`, 0 errores, 3 warnings.
- **Puerta oeste:** hoja, rigidizadores, jambas y muro, QA `pass: true`, 0 errores, 4 warnings.
- **Warnings aceptados:** n-gons en tapas planas, caras back-to-back ocultas y `ground_z` por la cota de la sala. Los falsos positivos de volumen firmado en piezas pequeñas siguen documentados en §16.1.
- **Sin pruebas en Godot:** no se exportó, no se abrió el proyecto de Godot, no se midió rendimiento en juego y no se validaron colisiones/navegación. Esas pruebas quedan para la fase que Riyo apruebe.

### 17.5. Estado y pendientes

- El pase de arte/QA de la sala está cerrado y guardado en `nexus/nivel_01/FM_PILOT_MAINTENANCE_v01.blend`, cámara `PILOT_CAM_ART_HORROR`, 1280×720.
- El generador y la caldera siguen siendo envolventes de bloqueo con detalle añadido; no son modelos finales de producción. Falta bake PBR definitivo, LOD, colisiones, partículas de polvo/vapor y la integración en Godot.
- No se declara el asset como arte final AAA ni se inicia Godot sin aprobación explícita. No hay commit; el `.blend` y la documentación siguen sin rastrear en Git.

## 18. Corrección de cilindros, luminarias y detalle final (2026-11-05)

Continuación del pase de arte/QA de la sala de Mantenimiento. Se usaron las skills `blender-core`, `blender-hardsurface-modeling`, `blender-pbr-materials`, `blender-lighting-lookdev` y `blender-asset-qa`; `qa_check.py` se ejecutó como puerta obligatoria. No se tocaron otras habitaciones, no se abrió Godot y no se hizo commit.

### 18.1. Sombreado y cilindros

- Se aplicó `smooth_by_angle` de 30° a **555 mallas locales visibles** de la sala, con marcado de aristas duras por ángulo. Se omitieron mallas de librería y objetos con normales personalizadas. Esto eliminó el facetado de tuberías, caldera, cúpula, barril, lámparas y depósitos.
- `NEXUS_V05_D_MAINT_AIR_TANK`: reconstruido por revolución alrededor de Z con **64 lados**, perfil abombado, **1,0 × 1,0 × 2,19 m**, centro (18,8; -5,0; -4,55). Se añadieron tres bandas `PILOT_EQUIP_AirTank_Band_0..2`, base `PILOT_EQUIP_AirTank_Base`, porta de inspección `PILOT_EQUIP_AirTank_Manway` y ocho pernos. La porta y los pernos usan `M_PILOT_Steel_Galvanized`.
- `NEXUS_V05_B_MAINT_CYLINDER_0/1`: reconstruidos a **40 lados**, **0,44 × 0,44 × 1,20 m**, con hombro y cuello; materiales `NEXUS_Red_Matte` y `FM_MAT_Cylinder_Green`. Se ocultaron las tapas gigantes `..._TOP`, que producían un disco blanco sobre cada botella.
- `NEXUS_V05_B_MAINT_BARREL`: reconstruido a **40 lados**, **0,56 × 0,56 × 0,85 m**; cuerpo en `NEXUS_Rusted_Metal`, tapa oxidada y anillos en `FM_MAT_Dark_Steel`.
- `PILOT_EQUIP_Boiler_Flue` y `PILOT_EQUIP_Boiler_FlueReducer` usan `FM_MAT_Flue_Heat`, acero oscuro con calor y óxido, en lugar del verde inadecuado.

### 18.2. Luminarias de emergencia

- Se ocultaron reversiblemente las cajas antiguas `NEXUS_V05_D_MAINT_BEACON` y `NEXUS_V05_B_MAINT_EMERGENCY_HOUSING`.
- Se creó `FM_PILOT_EMERGENCY` con **30 objetos** (15 por luminaria): placa, carcasa, visera, lente, tornillos, prensaestopas, etiqueta y rejilla de protección.
  - `PILOT_EMERGENCY_Low_*` en la pared norte, **x=11,55; z=-4,20**, a la izquierda de la puerta.
  - `PILOT_EMERGENCY_High_*` sobre la puerta, **x=13,0; z=-1,95**, por debajo de la viga.
  - Lente final **0,15 × 0,09 × 0,179 m**, suavizada.
- Las luces existentes se movieron al frente de las lentes: `NEXUS_V05_D_MAINT_BEACON_LIGHT` a (11,55; -2,22; -4,20), 12 W rojo; `NEXUS_V05_B_MAINT_EMERGENCY` a (13,0; -2,22; -1,95), 10 W rojo.
- Las cruces de la etiqueta se descartaron por z-fighting, UV de área cero y falsos positivos de QA; la placa blanca queda limpia.
- QA de cada luminaria con su muro: `pass True`, 0 errores, 2 warnings aceptados.

### 18.3. Rótulos, materiales y charcos

- `PILOT_EQUIP_Gen_Stencil` (\"GEN-04\") es una malla de texto en la cara frontal del generador, en (11,95; -6,748; -3,86), material `M_PILOT_Safety_Yellow`, orientada para leerse desde la cámara.
- `PILOT_EQUIP_Boiler_Nameplate` es una placa oscura de 0,64 × 0,08 × 0,22 m en (17,30; -7,02; -3,78). El texto \"CALDERA 02\" y los 16 pernos de marco del generador se ocultaron reversiblemente por errores de QA; no se eliminan.
- Se sincronizaron los `diffuse_color` de **165 materiales** con el Base Color del Principled para que Workbench y la vista sólida no muestren materiales blancos falsos.
- `M_PILOT_Puddle`: superficie oscura, rugosidad 0,10, IOR 1,33 y coat 0,55. Dos charcos irregulares con desvanecimiento alfa radial: `PILOT_FLOOR_Puddle_0` (1,79 × 1,02 m) y `PILOT_FLOOR_Puddle_1` (1,21 × 0,72 m), a 1,5 mm sobre el suelo.

### 18.4. Iluminación y render final

- Los valores de §17.1 quedan actualizados: exposición **1,30**; `PILOT_LOOK_FLASHLIGHT` **1600 W**, `spot_size=0,72`, `spot_blend=0,65`; niebla `M_PILOT_Atmosphere_Fog` a **0,0006**; EEVEE **32 muestras**.
- Las luces principales de la sala siguen a 0 W. Las prácticas se mantienen en 2,5–14 W; la sala sin linterna queda casi negra.
- Renders finales: `docs/fm_pilot_maintenance_art_final.png` (con linterna) y `docs/fm_pilot_maintenance_art_final_noflash.png` (sin linterna).
- El render se programó con `bpy.app.timers.register` para evitar el bloqueo del socket MCP en renders largos.

### 18.5. QA y estado

- QA `pass True`, 0 errores: generador + stencil; caldera + placa; depósito + bandas + manway + pernos + suelo; luminaria baja + muro; luminaria alta + dintel; cilindros rojo/verde; barril; charcos + suelo.
- Warnings aceptados: n-gons en tapas planas, caras back-to-back ocultas y `ground_z` por la cota de la sala. Los falsos positivos de volumen firmado en piezas pequeñas siguen documentados en §16.1.
- El `.blend` se guardó en `nexus/nivel_01/FM_PILOT_MAINTENANCE_v01.blend`, cámara `PILOT_CAM_ART_HORROR`, 1280×720, EEVEE 32 muestras.
- Sigue siendo un pase de arte sobre envolventes de bloqueo: faltan modelado final de generador/caldera, bake PBR definitivo, LOD, colisiones, partículas de polvo/vapor y todas las pruebas en Godot. No se declara terminado para Godot ni se hace commit sin aprobación de Riyo.

# FRECUENCIA MUERTA — Mantenimiento
## Auditoría por objeto de la sala piloto

**Estado:** auditoría terminada; correcciones menores aplicadas.
**Fecha:** 2026-11-04.
**Ámbito:** sala de Mantenimiento / Sala de máquinas.
**Archivo auditado:** `nexus/nivel_01/FM_PILOT_MAINTENANCE_v01.blend`.

---

## 1. Alcance real

Se auditaron **553 mallas** dentro del volumen de la sala. Contando empties, luces, cámaras y textos, el volumen contiene **588 objetos**.

| Tipo | Cantidad |
|---|---:|
| Mallas | 553 |
| Empties | 19 |
| Luces | 9 |
| Cámaras | 4 |
| Textos | 3 |

No se auditó el resto del nivel. No se modificó ninguna otra habitación.

---

## 2. Método

Para cada malla se comprobó:

- Caja envolvente mundial, dimensiones, centro y cota mínima.
- Contacto físico con otros objetos y con el suelo.
- Escala, rotación, origen y distancia del origen a la geometría.
- UVs: número de mapas, área UV cero y UVs fuera de 0–1.
- Materiales: slots vacíos, caras con índice inválido, texturas faltantes, nodos y Principled BSDF.
- Topología: boundary edges, non-manifold, wire edges, caras degeneradas, aristas de longitud cero y vértices duplicados.
- Triángulos, caras y vértices.
- Estado de ocultación reversible.
- Pertenencia a colección y jerarquía.

El resultado completo está en:

- `docs/fm_pilot_maintenance_stage2/object_audit.csv` — métricas crudas.
- `docs/fm_pilot_maintenance_stage2/object_audit_status.csv` — estado por objeto y notas.

---

## 3. Resultado global

| Estado | Objetos |
|---|---:|
| Bloqueo correcto, UV pendiente de modelado final | 301 |
| Correcto | 142 |
| Oculto reversible | 51 |
| Topología heredada a revisar | 19 |
| Corregido en esta auditoría | 19 |
| Arquitectura correcta, UV pendiente | 15 |
| Decal sobre suelo correcto | 3 |
| Contacto revisado | 3 |
| **Total** | **553** |

### Lectura

- **301 objetos del bloqueo** tienen geometría limpia, materiales asignados y contacto correcto. Su única carencia es UV, que corresponde al modelado final.
- **142 objetos** están correctos y completos para su función actual.
- **51 objetos** son originales ocultos de forma reversible; no se han borrado.
- **19 props importados** arrastran topología heredada (boundary/non-manifold/duplicados). No son del bloqueo nuevo y deben limpiarse o sustituirse en la fase de modelado final.
- **19 objetos** se corrigieron durante esta auditoría.
- **15 objetos de arquitectura** son correctos pero sin UV final.
- **3 decals** de suelo no tienen contacto volumétrico, lo cual es correcto.
- **3 objetos** se revisaron por contacto: rejilla embebida, carro y extintor; los tres están apoyados en el suelo, no flotando.

---

## 4. Correcciones aplicadas

Se aplicaron **20 ajustes**; 19 quedaron marcados como `CORREGIDO` y la válvula antigua sigue oculta de forma reversible.

| Grupo | Objetos | Corrección |
|---|---|---|
| Tapas de bolardo | `PILOT_EQUIP_BollardCap_00..03` | Alineadas sobre su bolardo y asentadas a z = -4,73 |
| Uniones del colector oeste | `PILOT_EQUIP_HeaderJoint_0_0..02` | Desplazadas a x = 7,60 para tocar el extremo del colector |
| Bandeja este | `PILOT_TRAY_E_Arm_03` | Ajustada a y = -7,40 para tocar el fondo de la bandeja |
| Vivienda de emergencia | `NEXUS_V05_B_MAINT_EMERGENCY_HOUSING` | Adosada al muro norte |
| Baliza | `NEXUS_V05_D_MAINT_BEACON` | Adosada al muro norte |
| Escombros | `NEXUS_V05_MAINT_DEBRIS_0..5` | Elevados 0,13 m para quedar sobre la losa |
| Marca de peligro | `NEXUS_V05_MAINT_HAZARD` | Elevada 0,14 m para quedar sobre la losa |
| Armario de pared | `NEXUS_ASSET_L1R_MAINT_CABINET_ROOT` | Desplazado 0,06 m hasta el muro oeste |
| Icono de llave | `NEXUS_ASSET_L1R_MAINT_TOOLCHEST_key-no_key` | Asignado material de acero; antes no tenía ningún slot |
| Válvula antigua | `NEXUS_V05_B_MAINT_PIPE_VALVE` | Reubicada sobre la tubería vertical; sigue oculta |

---

## 5. Problemas que quedan y su motivo

### 5.1. UVs

**489 mallas no tienen UV.** La distribución es:

- 301 del bloqueo nuevo.
- 173 de arquitectura/props heredados.
- 15 de arquitectura del nivel.

No se han generado UVs de blockout porque el bloqueo se va a sustituir por el modelado final. Generar UVs ahora sería trabajo desechable y podría dar una falsa sensación de asset terminado. En la fase de modelado final cada asset tendrá:

- UVs sin solapamientos.
- Margen de 4–8 px.
- Texel density coherente.
- UV2 para estáticos si se necesita lightmap.

### 5.2. Topología heredada

**19 props importados** tienen avisos de topología. Los más relevantes:

| Objeto | Boundary | Non-manifold | Duplicados | Triángulos |
|---|---:|---:|---:|---:|
| `NEXUS_L1_DIS_CART_TIPPED_cart` | 2454 | 96 | 256 | 29.394 |
| `NEXUS_ASSET_V05_MAINT_CART_industrial_storage_cart` | 1064 | 0 | 1360 | 18.902 |
| `NEXUS_ASSET_V05_MAINT_CAGED_LIGHT_caged_hanging_light` | 765 | 48 | 0 | 22.893 |
| `NEXUS_ASSET_V05_MAINT_POWER_BOX_power_box_01_box` | 604 | 0 | 26 | 19.856 |
| `NEXUS_ASSET_V05_MAINT_BENCH_TOOLBOX_metal_toolbox` | 551 | 0 | 4 | 3.975 |
| `NEXUS_ASSET_L1R_MAINT_CABINET_box_02` | 938 | 0 | 8 | 6.268 |
| `NEXUS_ASSET_L1R_MAINT_WRENCH_wrench` | 328 | 0 | 1 | 3.244 |
| `NEXUS_ASSET_L1_MAINT_FIRE_ALARM_fire_alarm` | 465 | 0 | 0 | 2.353 |

No se han modificado estos assets de forma agresiva porque:

- Son props heredados que pueden compartirse con otras salas.
- Un `remove_doubles` o un relleno de huecos puede alterar UVs y sombreado.
- Varios boundary edges son aberturas intencionadas de chapa o carcasas.

Quedan marcados como `LEGACY_TOPO_REVISAR` para la fase de limpieza/retopo o sustitución.

### 5.3. Escalas y orígenes

- **0 escalas negativas.**
- **23 escalas no unitarias**, casi todas en decals de sangre/aceite/papel y en los tubos/varillas del piloto, donde el escalado es intencionado.
- **3 orígenes alejados** de la geometría: armario, panel y carro industrial. El armario se ha corregido; el panel está oculto; el carro conserva su origen de importación. No afecta a la colocación, pero debe corregirse antes de exportar.

### 5.4. Materiales y texturas

- **0 texturas faltantes.**
- **0 materiales con Principled BSDF ausente.**
- **0 materiales con metallic 1 / roughness 1** en la sala.
- **1 objeto sin material**, ya corregido: el icono de llave.
- No se han detectado nodos de imagen rotos.

### 5.5. Contacto y flotantes

Tras las correcciones no se ha detectado ningún prop flotante:

- Tapas de bolardo: apoyadas.
- Uniones y soportes: en contacto con tuberías/bandejas.
- Escombros y marcas: sobre la losa.
- Vivienda de emergencia y baliza: adosadas al muro.
- Rejilla: embebida en el suelo, correcto.
- Carro y extintor: apoyados en el suelo; el carro está 3,6 mm por debajo de la cota teórica, sin efecto visual.
- Decals de aceite/papel: sobre el suelo, sin volumen, correcto.

---

## 6. Comprobación visual

Últimas vistas tras la auditoría:

- `docs/fm_pilot_maintenance_stage2/05_audit_front.png`
- `docs/fm_pilot_maintenance_stage2/06_audit_plan.png`

Las tapas de los bolardos ya se leen como remate de los postes. Los escombros y la marca de peligro están sobre la losa. La distribución y las holguras se mantienen.

No se ha hecho una revisión visual final de materiales porque el modelo sigue en bloqueo. Esa revisión corresponde al modelado final.

---

## 7. Qué está completo y qué no

### Completo para esta etapa

- Inventario de los 553 objetos.
- Contacto y apoyos revisados.
- Material faltante corregido.
- Escalas negativas descartadas.
- Texturas faltantes descartadas.
- Topología del bloqueo nuevo limpia.
- Ajustes de alineación y apoyo aplicados.
- Estado por objeto documentado en CSV.

### Pendiente para el modelado final

- UVs de los 489 objetos.
- Limpieza/retopo de los 19 props heredados.
- Geometría final de generador, caldera y tuberías.
- Materiales PBR y texturas.
- Bake, LOD y colisiones.
- Exportación e integración en Godot.
- Revisión visual con iluminación final.

---

## 8. Conclusión

La sala no tiene objetos flotantes, materiales sin asignar, texturas rotas ni escalas negativas. El bloqueo nuevo es geométricamente limpio. Las carencias reales son las esperadas en esta fase: **UVs, topología heredada de props antiguos y modelado final de los equipos**.

La auditoría por objeto no invalida el bloqueo; confirma que la base es sólida y que los problemas restantes están identificados y acotados.

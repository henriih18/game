# FRECUENCIA MUERTA — Propuesta de conectividad del Nivel 1 V06

**Fecha:** 2026-11-16  
**Rama:** `frecuencia-muerta` · HEAD `287b101`  
**Estado:** **Fases 1 y 2 implementadas** el 2026-11-16. La red Alt está exportada e integrada y Seguridad tiene acceso principal para la IA de capa 1. Ver `docs/FM_ALTERNATE_ROUTES.md` para el estado final.  
**Objetivo:** convertir la espina actual del Nivel 1 en una red con bucles, atajos y verticalidad, sin rehacer las salas ya vestidas.

---

## 1. Resumen ejecutivo

El Nivel 1 V06 funciona como una espina de ~175 m con ramales. Las nueve salas blockout están vestidas y el MEP principal está corregido, pero la mayoría de los ramales termina en fondo de saco y el este y el oeste del mapa siguen mal conectados.

La investigación del máster ha encontrado algo que cambia el plan: **la red de pasajes alternativos ya está modelada en Blender**, en la colección `L1_ARCH_ALTERNATE`. Son **114 mallas y 6.144 tris** con túneles, galerías, escaleras y bucles que conectan Almacén↔Mantenimiento, Control↔Oficinas, Oficinas↔Seguridad, Vestuarios↔Almacén, Recepción↔corredor y StairsConnector↔corredor. Los huecos bajos de 1,25 m en los muros ya existen en los GLB blockout del juego. Sin embargo, **esa red no se exportó a ningún GLB del V06** (salvo 22 mallas de `SecurityCorridor` dentro de `security_access_sector.glb`).

Por tanto, la primera intervención recomendada no es construir túneles nuevos, sino **integrar selectivamente la red existente** como rutas de sigilo para el jugador, manteniéndolas fuera del alcance de la IA principal por altura. Después se corrige la navegación de la IA en el oeste y se estudia la verticalidad y la extracción dinámica en fases separadas.

---

## 2. Grafo actual

### 2.1 Salas y conectores principales

| Zona | Acceso principal | Otras conexiones | Problema |
|---|---|---|---|
| Recepción Z01 | Corredor oeste | Extracción | Polo oeste aislado del este |
| Seguridad Z03 | Corredor (pasillo de servicio 1,4 m) | Conector a Control | IA principal no puede entrar; solo capa 2 |
| Control Z04 | Conector Seguridad | Puerta E sellada | Depende de Seguridad; sin ruta directa al corredor |
| Vestuarios Z05 | Corredor (puerta S) | Puerta E a Aseo, servicio W sellado | Servicio W sin uso |
| Almacén Z06 | Corredor (puerta S) | ServiceLink a Z10, puerta E a E1, servicio W | Sin atajo directo a Mantenimiento |
| Mantenimiento Z07 | Corredor (puerta N) | Puerta E a E2 | Gran sala con un solo acceso |
| Oficinas Z08 | Corredor (conector S) | Puerta E a Aseo | Sin ruta oeste hacia Seguridad/Control |
| Aseo Z09 | AseoLink desde Oficinas | Puerta E a Vestuarios | Sin ventilación/agua propia hasta MEP |
| StairsMain Z11 | Corredor (conector) | Nivel -1.5 en meseta | Sin conexión inferior con el resto |
| E1 Z12a | Almacén | Nivel -4.5 | Salida de emergencia sin bucle |
| E2 Z12b | Mantenimiento | Nivel -4.5 | Salida de emergencia sin bucle |

### 2.2 Conectores existentes

- Acceso Seguridad↔Control: `SM_L1_Conn_AccessConnector_Floor`, x −96..−92, z −40..−36.
- Corredor↔Seguridad: `SM_L1_Conn_SecurityConnector_Floor`, x −92..−86, z −10..−4.
- Corredor↔Almacén: `WarehouseConnector`, x 70..74, z −8..−4.
- Corredor↔Mantenimiento: `MaintenanceConnector`, x 60..66, z 4..8.
- Corredor↔Oficinas: `OfficesConnector`, x −14..−6, z −30..−4.
- Oficinas↔Aseo: `AseoLink`, x 15..18, z −52..−46.
- Almacén↔Z10: `ServiceLink`, x 62..70, z −24..−18.
- Corredor↔StairsMain: `StairsConnector`, x −4..2, z 4..30.

### 2.3 Navegación real

`scripts/fm/fm_level1_v06.gd` define seis `NavigationLink3D` de capa 1: Aseo x15, Aseo x18, E1 x110, E2 x112, Vestuarios z−40 y Control z−40. El smoke comprueba esos seis enlaces.

Limitación documentada: **la capa 1 no puede atravesar el acceso de Seguridad**; solo la capa 2 (`nav_layer1_security_isolated`). Seguridad y Control quedan fuera del alcance del Vigilante principal.

---

## 3. Hallazgo: red `L1_ARCH_ALTERNATE`

### 3.1 Estado en el máster

- Colección: `L1_ARCH_ALTERNATE`.
- 114 mallas, 5.776 vértices, 6.144 tris.
- 7 materiales de blockout: `M_L1_Corridor_Floor`, `M_L1_Door_Frame`, `M_L1_Label_Annotation`, `M_L1_Stair_Concrete`, `M_L1_Wall_Blockout`, `M_L1_Wall_Corridor`, `M_L1_Zone_MainStairs`.
- Todas con `hide_render=True`.
- Incluye 93 mallas de ruta, 20 mallas de muro que ya están en los GLB blockout y 1 anotación (`ANNOT_L1_MaintCorridor`).
- **No está en ningún GLB del V06**, salvo `SM_L1_Alt_SecurityCorridor_*` (22 mallas) dentro de `security_access_sector.glb`.

### 3.2 Aperturas ya presentes en el juego

Los huecos bajos de 1,25 m no hay que cortarlos: ya existen en los GLB blockout.

| Muro | Hueco | GLB que lo contiene |
|---|---|---|
| Corredor muro S, x20..21 | z1,25..4,2 | `corridor_sector.glb` (`Wall_S_7`) |
| StairsConnector muro E, z19..20 | z1,25..4,2 | `blockout_stairs_main.glb` (`Wall_E_1`) |
| Mantenimiento muro W, z19..20 | z1,25..6,0 | `blockout_maintenance.glb` (`Wall_W_1`) |
| Almacén muro S, x104,5..105,5 | z1,25..6,0 | `blockout_warehouse.glb` |
| Mantenimiento muro N, x104,5..105,5 | z1,25..6,0 | `blockout_maintenance.glb` |
| Control muro N, x−94,5..−93,5 | z0..1,25 | `blockout_control.glb` |
| Oficinas muro W, z−66..−65 | z0..1,25 | `blockout_offices.glb` |
| Oficinas muro W, z−31,5..−30,5 | z0..1,25 | `blockout_offices.glb` |
| Aseo/Vestuarios: no aplica a rutas Alt | — | — |

### 3.3 Rutas disponibles

Coordenadas en Godot (`z = −y` de Blender). Altura interior aproximada; la AABB incluye el espesor de techo.

| Ruta | Prefijo de mallas | Recorrido | Altura | Uso propuesto |
|---|---|---|---|---|
| EastGallery | `SM_L1_Alt_EastGallery_Tunnel_*` (4) | Almacén↔Mantenimiento, x104,25..105,75, z−8..8 | 1,25 m | Anillo este directo |
| MaintCorridor | `SM_L1_Alt_MaintCorridor_*` (9) | StairsConnector↔corredor (ramal x20)↔Mantenimiento oeste, x2..56, z18,75..20,25 | 1,25 m | Atajo sur y acceso alternativo a Mantenimiento |
| NorthConnector + NorthGallery | `SM_L1_Alt_NorthConnector_*` (4), `SM_L1_Alt_NorthGallery_*` (6) | Control norte↔Oficinas oeste, x−96..−30, z−66,25..−60,15 | 1,25 m | Anillo oeste Control↔Oficinas |
| OfficesCrawl | `SM_L1_Alt_OfficesCrawl_*` (9) | Oficinas oeste↔SecurityCorridor, x−40,25..−30,15, z−31,75..−11,8 | 1,25 m | Conexión Oficinas↔Seguridad |
| ReceptionStair | `SM_L1_Alt_ReceptionStair_*` (10) | Recepción este↔corredor, x−70..−12, z31,25..32,75, link x−37,75..−36,25 | 1,25 m | Bucle Recepción↔corredor |
| SecurityCorridor | `SM_L1_Alt_SecurityCorridor_*` (11) | Seguridad↔corredor, x−71..−36,6, z−11,8..−4 | 2,20 m | Ruta de capa 2 ya exportada |
| ServiceLoop | `SM_L1_Alt_ServiceLoop_*` (8) | Vestuarios servicio↔Almacén oeste, x57,25..70, z−40..−35,25 | 1,25 m | Bucle Vestuarios↔Almacén |
| NWStair | `SM_L1_Alt_NWStair_*` (36) | Control puerta E↔nivel −4,5, x−77..−67, z−60..−40 | completa | Reserva para fase de verticalidad |

### 3.4 Gálibo del jugador

`scripts/fm/fm_player.gd`:

- Altura de pie: 1,70 m.
- Altura agachado: **1,20 m**.
- Ojo agachado: 1,08 m.
- Velocidad agachado: 1,7 m/s.
- Step height: 0,20 m.

Los túneles de 1,25 m dejan 5 cm sobre la cabeza del jugador agachado. La IA principal (2,20 m) no puede entrar. Es una ruta de sigilo y escape para jugadores, no un corredor universal.

---

## 4. Propuesta

### Opción A — Integrar la red Alt selectivamente (recomendada)

Exportar las **93 mallas de ruta** (excluyendo las 20 mallas de muro ya presentes en blockout y la anotación) como un GLB nuevo y una escena propia. Añadirla al nivel como geometría no-sector, con colisión de capa 1 y sin tocar los 15 sectores actuales.

Ventajas:

- Aprovecha trabajo ya modelado; 6.144 tris es un coste despreciable.
- Crea bucles reales: este (Almacén↔Mantenimiento), oeste (Control↔Oficinas↔Seguridad↔corredor), sur (Recepción↔corredor), servicio (Vestuarios↔Almacén).
- Los túneles son solo para el jugador agachado; la IA principal conserva su red y no se rompe el navmesh.
- No requiere cortar muros: las aperturas ya existen en los GLB.
- Se puede hacer por fases y revertir fácilmente.

Riesgos:

- Geometría antigua de blockout con posibles huecos, solapes o cotas irregulares; requiere QA de gálibo y recorrido.
- Visualmente son pasillos de blockout; en esta fase se iluminan y señalizan, no se visten como arte final.
- El HUD seguirá mostrando la sala superior; se puede añadir un contexto de "conducto de servicio" más adelante.
- Si se hornea navmesh dentro, la IA principal no debe recibir rutas por ahí; validar con `NavigationAgent3D` y altura de agente.

### Opción B — Corregir la navegación de la IA en el oeste (complementaria)

Añadir un `NavigationLink3D` de capa 1 en la puerta S de Seguridad (x≈−89, z=−10) y verificar la ruta corredor↔Seguridad↔Control con el Vigilante principal. No requiere geometría nueva. Es la corrección más barata y debe ir junto a la opción A.

### Opción C — Verticalidad y mezzanine (fase posterior)

- Conectar la meseta inferior de NWStair (−4,5) con la meseta de StairsMain (−4,5) mediante un túnel de servicio nuevo.
- Estudiar una mezzanine en Almacén sobre la zona de staging, con escalera y barandilla, para dar verticalidad y una ruta de vigilancia.
- Requiere propuesta propia de arquitectura y presupuesto; no se implementa en la primera fase.

### Opción D — Extracción dinámica (fase de diseño, sin geometría)

Mantener la extracción en Recepción (nivel 1) y definir antes de implementar: activación, tiempo, riesgos, entrega de objetos completos y componentes, jugadores incapacitados, muerte y recompensas. No tocar la geometría de Recepción hasta aprobar las reglas.

---

## 5. Fases propuestas

### Fase 1 — Integración de rutas Alt (primera intervención)

**Objetivo:** que el jugador pueda recorrer la red de túneles y que la IA principal no los use.

Entregables:

1. `scripts/fm/fm_alt_routes_export_headless.py`: exporta las 93 mallas de ruta desde `L1_ARCH_ALTERNATE`, sin muros duplicados ni anotación, sin cámaras/luces, con AABB validada y reporte JSON.
2. `assets/models/fm/alternate_routes.glb`.
3. `scenes/fm/fm_alternate_routes.tscn`: raíz `AlternateRoutes`, GLB, luces de servicio de baja intensidad, balizas y carteles.
4. Instancia de la escena en `scenes/fm/level1_v06.tscn` como nodo **fuera de `Sectors`**, para no alterar la detección de sector ni los 15 sectores del smoke.
5. Extensión mínima de `scripts/fm/fm_level1_v06.gd` para construir colisión de capa 1 sobre `AlternateRoutes` y registrar el nodo.
6. Señalización física mínima: rejillas/hatch en las bocas, flechas de salida, carteles `SERVICIO`, `MANTENIMIENTO`, `SALIDA`, `CONDUCTO`.
7. Iluminación: tiras LED frías cada 6–8 m, balizas rojas en cruces y luz de emergencia en las bocas. Sin sombras.
8. Audio: reutilizar eventos de pasos metálicos y goteo; no crear sistema nuevo.
9. Tests:
   - `tests/fm_level1_v06_alt_routes_smoke.gd`: carga la escena, comprueba nodo, 93 mallas, AABB y colisión.
   - Recorrido automático agachado por EastGallery, NorthGallery, ServiceLoop y MaintCorridor; sin quedarse atascado.
   - Prueba de que el agente principal no encuentra ruta por un túnel de 1,25 m.
   - Smoke existente 403/0, gameplay 105/0, full 49/0, presets 194/0.
   - Perf: comparar 1280×720 antes/después; el coste esperado es <1 % por 6k tris y luces sin sombras.

**Criterios de aceptación:**

- El jugador agachado recorre cada túnel de boca a boca sin clipping ni bloqueos.
- No hay huecos visuales al vacío en las bocas.
- La IA principal no atraviesa ningún túnel de 1,25 m.
- Los 15 sectores, sus AABB y sus luces de emergencia siguen pasando el smoke.
- No se toca `fotos-referencia/`, `level1.tscn` ni escenas del slice.

**Estimación:** 1 checkpoint de trabajo, con backup previo del máster y del GLB.

### Fase 2 — Navegación de la IA en el oeste

- Añadir `NavigationLink3D` de capa 1 en la puerta S de Seguridad.
- Verificar ruta del Vigilante principal corredor→Seguridad→Control.
- Ajustar el navmesh solo si el bake no genera polígonos utilizables.
- Test de ruta y de que la IA no entra en los túneles Alt.

### Fase 3 — Verticalidad

- Túnel inferior NWStair↔StairsMain a −4,5.
- Mezzanine de Almacén.
- Propuesta y presupuesto aparte.

### Fase 4 — Extracción dinámica

- Diseño de reglas y pruebas; geometría solo después de aprobar.

---

## 6. Impacto técnico

### 6.1 Colisiones

- `FMGLBCollision` puede construir la colisión de las rutas con el mismo helper de los sectores.
- Las mallas de túnel no deben contener tokens de omisión; las rejillas, carteles, luces y decales sí (`GRILLE`, `SIGN`, `LIGHT`, `DECAL`, `CABLE`, `FLOOR_LINE`).
- Los techos de 1,25 m deben colisionar; el capsule agachado de 1,20 m debe pasar sin penetrar.
- Evitar cajas AABB gigantes: las rutas son series de tramos; no fusionar todo en una sola malla.

### 6.2 Navmesh

- La IA principal tiene altura 2,20 m; el bake debe excluir los túneles de 1,25 m.
- La capa 2 de Seguridad ya usa `SecurityCorridor`; no romper esa ruta.
- No añadir `NavigationLink3D` dentro de los túneles Alt en la Fase 1.
- Medir polígonos y tiempo de bake antes/después.

### 6.3 Iluminación

- Luces sin sombras, intensidad baja, rango corto.
- Balizas rojas en cruces y bocas.
- No usar la luz de emergencia de la sala como única fuente; el túnel debe leerse.

### 6.4 Audio

- Reutilizar eventos existentes de pasos, metal, goteo y ventilación.
- Añadir una identidad sonora de túnel solo si se reutiliza el sistema actual.
- El sonido de las compuertas debe alertar a criaturas según el sistema de propagación.

### 6.5 Rendimiento

- 93 mallas, 6.144 tris, materiales blockout y luces sin sombras: impacto esperado despreciable.
- El coste real viene de las luces y del audio, no de la geometría.
- Medir con el perf 1280×720 y comparar con la línea base 556,2 fps / 5.042.270 tris.

### 6.6 Tests existentes

- `tests/fm_level1_v06_smoke.gd` no debe cambiar sus 15 sectores; solo se añade una comprobación nueva de la escena Alt.
- `tests/fm_level1_v06_gameplay.tscn`, `fm_full_run.tscn`, `fm_graphics_presets_smoke.tscn` deben seguir pasando.
- Si se toca `level1_v06.tscn`, revisar el orden de nodos y el root.

---

## 7. Decisiones pendientes de aprobación

1. **¿Se integra la red Alt completa o solo el anillo este y el oeste?**  
   Recomendación: Fase 1 con EastGallery, NorthGallery, OfficesCrawl, SecurityCorridor, ServiceLoop, ReceptionStair y MaintCorridor. NWStair se reserva para verticalidad.

2. **¿La escena Alt va fuera de `Sectors` o se reparte entre escenas de sala?**  
   Recomendación: fuera de `Sectors`, como `AlternateRoutes`, para no contaminar la detección de sector ni las AABB de las 15 salas.

3. **¿Se permite tocar `level1_v06.tscn`?**  
   Es necesario para instanciar la escena Alt. No se tocará `level1.tscn` ni escenas del slice. Si no se autoriza, habría que repartir la geometría entre las escenas de sala, con más riesgo de AABB y colisión.

4. **¿La Fase 1 incluye arte de acabado o solo blockout iluminado y señalizado?**  
   Recomendación: blockout iluminado y señalizado; el arte final de túneles se pospone al pase visual global.

5. **¿Se corrige ya el NavigationLink de Seguridad?**  
   Recomendación: sí, en Fase 2 inmediata después de la Fase 1, porque es barato y desbloquea la IA en el oeste.

---

## 8. Archivos previstos

Nuevos:

- `scripts/fm/fm_alt_routes_export_headless.py`
- `assets/models/fm/alternate_routes.glb`
- `scenes/fm/fm_alternate_routes.tscn`
- `docs/fm_alternate_routes_export.json`
- `docs/FM_ALTERNATE_ROUTES_ART.md`
- `tests/fm_level1_v06_alt_routes_smoke.gd/.tscn`
- Posible `tests/fm_level1_v06_alt_routes_shot.gd/.tscn`

Modificados:

- `scenes/fm/level1_v06.tscn` (instancia de la escena Alt)
- `scripts/fm/fm_level1_v06.gd` (colisión de `AlternateRoutes`)
- `tests/fm_level1_v06_smoke.gd` (comprobación de la escena Alt)
- `AGENTS.md` (estado de la fase)

No se tocan:

- `fotos-referencia/`
- `scenes/fm/level1.tscn`
- escenas del slice
- GLB de las nueve salas, salvo que una prueba demuestre un defecto

---

## 9. Conclusión

La red Alt es la oportunidad más clara para convertir el Nivel 1 en un mapa con bucles sin rehacer arquitectura. Ya existe, encaja con los huecos de 1,25 m y ofrece exactamente los atajos que faltan. La propuesta recomendada es integrarla por fases, empezando por las rutas de sigilo y la navegación de la IA en el oeste, con QA de gálibo, colisión y rendimiento antes de añadir arte de acabado.

Sin commit hasta autorización.

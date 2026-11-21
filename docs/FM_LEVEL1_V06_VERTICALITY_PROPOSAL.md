# FRECUENCIA MUERTA — Propuesta de verticalidad NWStair / StairsMain

**Fecha:** 2026-11-16
**Rama:** `frecuencia-muerta` · HEAD `287b101`
**Estado:** propuesta de diseño. **No se ha modificado geometría, GLB ni el máster.**
**Documento base:** `docs/FM_LEVEL1_V06_CONNECTIVITY_PROPOSAL.md`, Opción C (verticalidad) y Fase 3.

---

## 1. Resumen ejecutivo

La meseta inferior de **NWStair** (nivel −4,5) es hoy un fondo de saco: se baja por la escalera de emergencia del oeste y no hay salida inferior. La meseta inferior de **StairsMain** (también −4,5) está cerrada por sus propios muros de fosa. La idea inicial de un túnel directo entre ambas parece un enlace pequeño, pero la medición del máster demuestra que no lo es.

Entre las dos mesetas no existe sótano ni galería: solo el `SM_L1_Bedrock` y el `SM_L1_Rock_Overburden` del bloque arquitectónico. La ruta ortogonal mínima ronda **70 m en X + 97 m en Z ≈ 167 m**, y un túnel habitable de 1,8 × 2,4 m a −4,5 sería, en la práctica, **un nivel inferior nuevo** bajo Recepción, Seguridad, Control, corredor y Oficinas. No es una corrección de conectividad menor y no debe construirse sin una fase propia de diseño, presupuesto y pruebas.

**Recomendación:** no ejecutar el túnel de 167 m en esta fase. Priorizar una intervención corta y reversible en NWStair (espolón + sala técnica) o, si se quiere verticalidad real, una **mezzanine en Almacén** con escalera y barandilla. El túnel inferior queda como **Opción D: nivel de servicio futuro**, solo si el diseño del juego necesita un sótano completo.

---

## 2. Estado actual

### 2.1 NWStair

- Ruta Alt integrada: `SM_L1_Alt_NWStair_*`.
- Extensión: x −77..−67 (Godot), z −60..−40.
- Escalera completa que desciende hasta la cota −4,5.
- Meseta inferior: x −73..−71, z −60..−52,7, cota −4,7..−4,5.
- Acceso superior desde la puerta E de Control (x −77, z −46..−42).
- La meseta inferior no tiene salida: es un callejón sin salida vertical.
- El muro norte de la meseta (y = 60 en Blender; z = −60 en Godot) no tiene muro bajo: se puede abrir sin demoler estructura existente.
- Iluminación actual: balizas ámbar de la escena Alt; sin sala de servicio propia.

### 2.2 StairsMain

- Sector Z11, meseta inferior x −4..0, z −44..−38,72, cota −4,7..−4,5.
- La fosa está cerrada por `Pit_W`, `Pit_E` y `Pit_S`; no hay puerta inferior.
- El acceso superior es el conector del corredor.
- Su meseta se usa para la prueba de caída/respawn de las escaleras, no como ruta.

### 2.3 Volumen intermedio

- No hay geometría de sótano entre ambas mesetas.
- Solo existen `SM_L1_Bedrock` (z −0,6..−0,2) y `SM_L1_Rock_Overburden` (z −1,25..1,25) como bloque de terreno.
- El volumen a −4,5 está vacío, pero atravesarlo implica construir un túnel nuevo de punta a punta, no conectar dos habitaciones existentes.

---

## 3. Opciones

### Opción A — Túnel inferior completo NWStair ↔ StairsMain

**Qué es:** un túnel de servicio a cota −4,5, de 1,8 m de ancho y 2,4 m de alto, con losa, drenaje, puertas cortafuego, iluminación de emergencia y ventilación, que une las dos mesetas.

**Ventajas:**

- Cierra el bucle inferior oeste-centro y da sentido a las dos mesetas.
- Permite una ruta de escape alternativa en caso de bloqueo del corredor.
- Aprovecha que el volumen inferior está vacío y que el suelo de las salas no se toca.

**Costes y riesgos:**

- Longitud estimada ≈167 m con desvíos; es un nivel inferior, no un pasillo.
- Hay que construir suelo, techo, muros, puertas, escaleras de conexión, drenaje, ventilación, luces y colisión en toda la longitud.
- Un túnel de 167 m sin habitaciones intermedias es un pasillo largo y repetitivo, justo lo contrario de la variedad espacial que pide el diseño.
- Permite a los jugadores evitar Recepción, Seguridad, Control y parte de Oficinas; puede vaciar de tensión la mitad oeste del mapa.
- Añade un sector/navmesh nuevo, más luces, más colisión y más coste de mantenimiento.
- Requiere una fase de level design propia y posiblemente salas técnicas intermedias, no solo un tubo.

**Veredicto:** **no recomendada ahora.** Si se hace, debe ser un nivel de servicio completo con 2–3 salas intermedias, no un atajo largo.

### Opción B — Espolón corto y sala técnica en NWStair (recomendada si se quiere cerrar el fondo de saco)

**Qué es:** abrir el muro norte de la meseta de NWStair (z = −60) y construir una sala técnica de unos **6 × 8 m** a cota −4,5, con 2,6 m de altura. La sala contiene bombas, cuadros eléctricos, tuberías, un banco de trabajo y una puerta de servicio. No conecta con StairsMain.

**Ventajas:**

- Da una recompensa y un propósito a la meseta inferior sin construir 167 m.
- Es una intervención pequeña, reversible y fácil de probar.
- Añade una habitación de identidad técnica coherente con Mantenimiento y el MEP existente.
- Se puede cerrar con una puerta de seguridad y convertir en un pequeño checkpoint/almacén de herramientas.
- No rompe la estructura de las nueve salas ni el flujo principal.

**Costes:**

- Geometría nueva de una habitación, puerta, escalón, luces, props, colisión y navmesh.
- Hay que decidir si es un sector nuevo (cambia el recuento de 15) o un nodo fuera de `Sectors` como las rutas Alt.
- No resuelve la conexión con StairsMain; solo elimina el fondo de saco de NWStair.

**Veredicto:** **recomendada como primer paso** si el objetivo es que NWStair deje de ser un callejón sin salida.

### Opción C — Mezzanine en Almacén

**Qué es:** una plataforma elevada de unos **10 × 6 m** sobre la zona de staging (x 92..102, z −33..−27), a +3,2 m, con escalera de un tramo, barandilla, columnas y una oficina de supervisor. Debajo se conserva el staging.

**Ventajas:**

- Aporta verticalidad real dentro de una sala ya vestida y muy transitada.
- Crea una ruta de vigilancia y un punto de observación para el Vigilante y el jugador.
- No requiere un nivel inferior ni un túnel largo.
- Reutiliza la identidad industrial del Almacén y los materiales existentes.
- Se puede probar con navmesh y colisión de forma aislada.

**Costes:**

- Geometría nueva, escalera, barandilla, colisión, luces y props.
- Hay que validar gálibo, navmesh, líneas de visión y que no tape la extracción ni el staging.
- Puede afectar al rendimiento si se añaden muchas luces; usar sin sombras y presupuesto medido.

**Veredicto:** **mejor relación valor/coste** para verticalidad, pero es una intervención de Almacén, no de NWStair/StairsMain.

### Opción D — Nivel de servicio futuro

**Qué es:** un sótano de servicio completo que conecte NWStair, StairsMain, E1/E2 y posiblemente el aparcamiento o la sala de máquinas, con 3–5 salas intermedias.

**Ventajas:**

- Da coherencia a todas las mesetas inferiores y a las salidas de emergencia.
- Permite una segunda capa de exploración y extracción.
- Es la única forma de que el túnel de 167 m tenga sentido.

**Costes:**

- Es un nivel nuevo: arquitectura, iluminación, audio, navegación, criaturas, objetos, pruebas y rendimiento.
- Requiere una fase de diseño completa y probablemente un capítulo propio del plan.

**Veredicto:** **fase futura**, no una corrección de esta semana.

---

## 4. Recomendación

1. **No construir el túnel de 167 m ahora.** La evidencia geométrica dice que es un nivel inferior nuevo, no un enlace menor.
2. **Aprobar la Opción B** (espolón + sala técnica de 6 × 8 m en NWStair) como intervención corta para cerrar el fondo de saco y dar uso a la meseta.
3. **Estudiar la Opción C** (mezzanine de Almacén) como siguiente mejora de verticalidad, en una fase separada y con presupuesto propio.
4. **Dejar la Opción D** documentada como nivel de servicio futuro, solo si el diseño del juego necesita un sótano completo.

---

## 5. Impacto técnico de la Opción B (si se aprueba)

### 5.1 Colisiones

- Suelo, techo, muros y puerta deben colisionar; las rejillas, carteles, luces, cables y decales llevan tokens de omisión (`GRILLE`, `SIGN`, `LIGHT`, `CABLE`, `DECAL`).
- La puerta de la sala debe ser un objeto interactivo o una compuerta reutilizada, no una caja estática.
- Evitar una única caja AABB gigante; construir la sala por tramos.

### 5.2 Navmesh

- La sala está a −4,5 y tiene 2,6 m de altura: cabe el perfil principal (radio 0,45 / altura 2,20).
- Hay que decidir si se hornea en `NavigationMain` (capa 1) o en una región propia.
- La conexión con la meseta de NWStair necesita un `NavigationLink3D` o un vano de altura completa.
- La IA principal podría entrar; si se quiere que sea solo del jugador, reducir la altura libre o añadir una puerta que la IA no cruce.

### 5.3 Iluminación

- 2–3 luminarias industriales frías sin sombras, una baliza de emergencia y una luz cálida de mesa.
- No usar la luz de la escalera como única fuente; la sala debe leerse.
- Medir el coste de luces en el perf.

### 5.4 Audio

- Reutilizar pasos metálicos, goteo, zumbido eléctrico y ventilación existentes.
- La puerta debe generar ruido y alertar a criaturas según el sistema actual.
- No crear un sistema de audio nuevo para una sola sala.

### 5.5 Rendimiento

- Geometría pequeña (una sala), pero con luces y props.
- Presupuesto orientativo: <8k tris, 4–6 luces sin sombras, 1 puerta, 1–2 props grandes.
- Medir con `tests/fm_level1_v06_perf.tscn` antes/después.

### 5.6 Pruebas

- Smoke: nuevo nodo/sector, AABB, colisión, suelo, puerta y luces.
- Gameplay: recorrido de la meseta a la sala, puerta, interacción y vuelta.
- Full run: no debe romper la extracción ni el respawn de las escaleras.
- Perf 1280×720: comparar con la línea base actual (411/108/49/194; perf ~447 fps).

---

## 6. Decisiones pendientes de aprobación

1. **¿Se aprueba la Opción B (sala técnica de 6 × 8 m en NWStair)?**
2. **¿La sala es un sector nuevo o un nodo fuera de `Sectors`?**
   - Recomendación: nodo fuera de `Sectors` como `NWStairService`, para no cambiar los 15 sectores del smoke; si se quiere HUD de sector propio, entonces sí sector nuevo y actualizar el test.
3. **¿La puerta es interactiva o una compuerta de seguridad existente?**
4. **¿Se estudia la mezzanine de Almacén en la misma fase o después?**
   - Recomendación: después, para no mezclar dos intervenciones.
5. **¿Se autoriza tocar `scenes/fm/level1_v06.tscn` para instanciar la nueva escena?**
   - Es necesario si la sala va fuera de `Sectors`. No se tocará `level1.tscn` ni escenas del slice.

---

## 7. Archivos previstos (solo si se aprueba la Opción B)

Nuevos:

- `scripts/fm/fm_nwstair_service_build.py`
- `scripts/fm/fm_nwstair_service_export_headless.py`
- `assets/models/fm/nwstair_service.glb`
- `scenes/fm/fm_nwstair_service.tscn`
- `tests/fm_level1_v06_nwstair_service_smoke.gd/.tscn`
- `docs/FM_NWSTAIR_SERVICE.md`
- `docs/fm_nwstair_service_export.json`

Modificados:

- `scenes/fm/level1_v06.tscn` (instancia de la escena)
- `scripts/fm/fm_level1_v06.gd` (colisión, luces y registro)
- `tests/fm_level1_v06_smoke.gd` (comprobaciones nuevas)
- `AGENTS.md`

No se tocan:

- `fotos-referencia/`
- `scenes/fm/level1.tscn`
- escenas del slice
- GLB de las nueve salas, salvo que una prueba demuestre un defecto

---

## 8. Conclusión

NWStair y StairsMain comparten cota, pero no comparten espacio. Un túnel entre ambas es un nivel inferior de 167 m, no un atajo. La intervención proporcionada es una **sala técnica corta en NWStair**; la verticalidad de mayor valor es la **mezzanine de Almacén**; el túnel completo queda como nivel de servicio futuro. Sin geometría nueva hasta que el usuario apruebe la opción y el alcance.

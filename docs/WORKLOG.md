# FRECUENCIA MUERTA — Registro de continuidad

Registro cronológico de sesiones para que Codex, OpenCode u otro agente pueda retomar el trabajo desde los archivos del proyecto. Las entradas previas no se eliminan ni se reescriben; cada sesión agrega una entrada al final.

## 2026-11-01 — Codex — Auditoría global y sistema de continuidad

- **Fecha y hora:** 2026-11-01 12:30 COT (17:30 UTC).
- **Agente:** Codex.
- **Fase de producción:** Fase 1, protección y preparación; auditoría de base para Fase 2. El sistema documental de continuidad se implementa en esta sesión.
- **Zona/departamento:** Instalación completa NEXUS (L1–L5, núcleo vertical y exterior).
- **Objetivo:** establecer registro independiente del historial de chat, contrastar el estado real de Blender/Git y continuar la producción sin perder el trabajo previo.
- **Archivos creados:** `docs/WORKLOG.md`, `docs/CURRENT_STATE.md`.
- **Archivos modificados:** ninguno preexistente.
- **Objetos/colecciones creados o modificados en Blender:** ninguno en esta sesión.
- **Cambios arquitectónicos:** ninguno. Se identifican como pendientes de verificación las escaleras de la torre, las hojas del ascensor y las conexiones de acceso/logística.
- **Materiales, texturas e iluminación:** ninguno incorporado ni modificado.
- **Referencias consultadas:** `AGENTS.md`, `docs/fm_nexus_nivel2.md`, `blender_concept/README.md`, `fotos-referencia/` y `fotos-referencia/modelos-referencia.png` (según auditoría visual registrada en el diagnóstico previo).
- **Blender/MCP:** conexión comprobada con Blender 5.2.3 LTS, addon/protocolo actualizado. Escena `Scene`: 7.079 objetos, 44 colecciones, 51 materiales, 29 cámaras y 291 luces; sistema métrico, unidad 1 m, EEVEE. El archivo activo reportado por Blender es `/home/riyo/Vídeos/FM_NEXUS_V05_level1_v90.blend` y `bpy.data.is_dirty` es `True`.
- **Archivo .blend guardado en esta sesión:** ninguno todavía. El v90 original del proyecto se conserva intacto; la copia `FM_NEXUS_V05_level1_v90_live_recovery_20261101.blend` también existe. El tamaño de v90 observado en disco es 3.073.074 bytes y el de la copia de recuperación 3.056.681 bytes. La documentación anterior de Nivel 2 informa un tamaño distinto para v90; usar los datos observados y verificar tras crear el nuevo punto de trabajo.
- **Estado de Git observado:** rama `frecuencia-muerta`, HEAD `0db132a69a9d53c24386dc308e4a9f6f64e9aa04` (`Arte del pasillo integrado en el vertical slice`). Hay numerosos archivos y recursos sin seguimiento, incluidos `.blend`, scripts y `fotos-referencia/`; no se eliminó ni modificó ninguno de ellos. Al crear los dos registros, estos se agregan como nuevos archivos.
- **Problemas encontrados:** no existían `docs/WORKLOG.md` ni `docs/CURRENT_STATE.md`. La escena viva tiene cambios sin guardar. El registro previo de Nivel 2 no coincide con el tamaño actual en disco de v90. La torre no tiene tramos activos de escalera entre sus rellanos; hay geometría histórica oculta que requiere evaluación antes de reutilizarse. Las hojas de ascensor están elevadas sobre los pisos aproximadamente 0,64–1,06 m. Varias puertas inferiores tienen 3,0 m de altura, igual al máximo oficial del Vigilante, por lo que requieren comprobación de gálibo.
- **Soluciones aplicadas:** creado el protocolo de continuidad en estos archivos; se registran hallazgos como pendientes y no como trabajo terminado. Se preservan archivos existentes y no se realizan cambios de geometría en esta sesión.
- **Último bloque completado:** lectura de instrucciones y documentación disponible; comprobación de Git y conexión MCP; inventario cuantitativo de la escena activa y registro del estado sucio de v90.
- **Operaciones pendientes:** (1) guardar el estado vivo actual como nueva versión incremental de trabajo `FM_NEXUS_V05_level1_v91.blend` dentro del proyecto, sin sobrescribir v90 ni la recuperación; (2) verificar tamaño, ruta activa y estado guardado; (3) actualizar ambos registros con el resultado; (4) completar el grafo de circulación de Fase 2 antes de corregir arquitectura; (5) evaluar el exterior y las conexiones de la torre.
- **Versión de Blender:** 5.2.3 LTS, EEVEE.
- **Versión de trabajo guardada:** todavía no hay una versión incremental guardada por Codex en esta sesión. Base viva para preservar: v90 activo y modificado sin guardar.

## 2026-11-01 — Codex — Punto de preservación incremental v91

- **Fecha y hora:** 2026-11-01 12:31 COT (17:31 UTC).
- **Agente:** Codex.
- **Fase de producción:** Fase 1, protección y preparación.
- **Zona/departamento:** Instalación NEXUS completa; operación de archivo, sin cambio de geometría.
- **Objetivo:** preservar en una nueva versión el estado vivo que Blender reportaba como modificado sin guardar, antes de modelar.
- **Archivo creado:** `FM_NEXUS_V05_level1_v91.blend` (3.056.566 bytes).
- **Objetos/colecciones creados o modificados:** ninguno; los 7.079 objetos y 44 colecciones se conservaron.
- **Cambios arquitectónicos, materiales, texturas e iluminación:** ninguno.
- **Operación Blender:** `bpy.ops.wm.save_as_mainfile` terminó con `{'FINISHED'}`. Verificación posterior: Blender apunta a `/home/riyo/Documentos/game/FM_NEXUS_V05_level1_v91.blend`, `bpy.data.is_dirty=False`; 7.079 objetos, 44 colecciones y 51 materiales.
- **Preservación:** v90 (3.073.074 bytes) y `FM_NEXUS_V05_level1_v90_live_recovery_20261101.blend` (3.056.681 bytes) conservan tamaños y marcas de tiempo observados antes de guardar v91; no se sobrescribieron.
- **Problemas/soluciones:** la primera lectura inmediatamente después del guardado aún indicó `is_dirty=True`; una consulta MCP posterior confirmó `False`. El archivo está presente y tiene tamaño no nulo. Se conserva el dato intermedio para que no parezca una discrepancia sin explicar.
- **Pendiente:** inspección visual y dimensional de la versión v91; completar el grafo de circulación Fase 2; después abordar continuidad vertical y arquitectura según dependencias.
- **Estado de Git:** rama `frecuencia-muerta`, HEAD `0db132a69a9d53c24386dc308e4a9f6f64e9aa04`; v91 y ambos registros aparecen como archivos nuevos sin seguimiento, junto con recursos previos. No se limpió ni descartó nada.
- **Versión de Blender:** 5.2.3 LTS.
- **Versión incremental guardada:** `/home/riyo/Documentos/game/FM_NEXUS_V05_level1_v91.blend`.

## Nota de corrección documental — 2026-11-01 12:32 COT

Durante la creación inicial, el contenido destinado a `CURRENT_STATE.md` quedó como texto literal al final de este archivo por un error de formato. Se detectó y retiró antes de continuar; la entrada inicial de la sesión se conservó. `CURRENT_STATE.md` se crea por separado y ambos archivos se verificarán al terminar el bloque.

## 2026-11-01 — Codex — Grafo preliminar de circulación en v91

- **Fecha y hora:** 2026-11-01 12:34 COT (17:34 UTC).
- **Agente:** Codex.
- **Fase de producción:** Fase 2, plano maestro y circulación (auditoría en curso).
- **Zona/departamento:** L1–L5 y núcleo vertical; lectura de geometría, sin modelado.
- **Objetivo:** distinguir arquitectura activa de versiones históricas y registrar las conexiones existentes y los bloqueos visibles antes de cambiar arquitectura.
- **Objetos/colecciones creados o modificados:** ninguno. Se consultaron las plantas actuales, los objetos de puertas, corredores, anillos, conectores y torre. Las vistas MCP fueron de inspección y no cambiaron la escena.
- **Archivos:** se actualizan `docs/CURRENT_STATE.md` y se agrega esta entrada a `docs/WORKLOG.md`. No se modificaron scripts ni documentación de diseño existente.
- **Hallazgos de circulación:** L1 tiene seis ramas hacia el corredor principal y un enlace oriental `NEXUS_LINK_L1` a la torre; el extremo oeste sigue cerrado con `NEXUS_V05_CORR_END_-22`, y no se verificó una salida de superficie. L2 tiene corredor longitudinal, cruces este/oeste y enlace al núcleo; existen puentes de piso `NEXUS_FIX_GAP_*` hacia varias salas. L3–L5 tienen anillos, puertas de salas y patas conectoras al núcleo. El conjunto es una red espacialmente conectada en varias áreas, pero aún falta el recorrido completo por umbrales y las salidas de emergencia no están certificadas.
- **Bloqueo concreto en L2:** `NEXUS_FIX_GAP_BIO_FLOOR` conecta espacialmente la puerta de biología con la zona de esclusa, pero `NEXUS_V04_AIRLOCK_WALL_W` ocupa todo el paño en esa intersección (malla caja de 8 vértices/6 caras, sin vano); la ruta está bloqueada por geometría. No se modificó. Es el primer conflicto arquitectónico a resolver tras cerrar el grafo.
- **Colecciones históricas:** `CORRIDOR_L-1_*` a `CORRIDOR_L-5_*` están en `02_CIRCULATION` y ocultas en viewport/render; no representan las rutas activas. Se conservarán. Las bandas `NEXUS_V04_CORR_*` del Nivel 2 están visibles; columnas de corredor aparecen ocultas individualmente y no se confunden con paredes de cierre.
- **Núcleo vertical:** la torre tiene links y rellanos por nivel, hueco de ascensor de 3×3 m con cabina estática en L1 y una escalera de mano continua en el hueco de escalera de 3×3 m. No hay vuelos de escalera convencionales activos. Los tramos antiguos ocultos N2–N3/N3–N4 no se aceptan aún: dimensiones y gálibos requieren inspección. Las hojas de ascensor siguen elevadas sobre los pisos.
- **Visualización:** inspección superior wireframe de L1–L5 y vista lateral/3⁄4 de la torre mediante Blender MCP. Las vistas confirman plantas apiladas, pero no sustituyen todavía una comprobación de recorrido transitable.
- **Errores de herramienta y resultado:** dos consultas iniciales `get_scene_info` fallaron (campos no válidos y uso de colección como nombre de objeto); una consulta Python falló por sintaxis de `sorted(generator, key=...)`. Se corrigieron las consultas; no hubo cambios parciales en Blender.
- **Materiales, texturas e iluminación:** ninguno incorporado o cambiado.
- **Cambios arquitectónicos:** ninguno en este bloque.
- **Versión de Blender:** 5.2.3 LTS.
- **Estado de guardado:** archivo activo `/home/riyo/Documentos/game/FM_NEXUS_V05_level1_v91.blend`, limpio según última consulta MCP; no se guardó una nueva versión porque no hubo cambios de geometría.
- **Estado de Git:** rama `frecuencia-muerta`, HEAD `0db132a69a9d53c24386dc308e4a9f6f64e9aa04`; `v91`, `WORKLOG.md` y `CURRENT_STATE.md` siguen sin seguimiento. Se mantienen los demás elementos sin seguimiento observados.
- **Siguiente paso:** terminar tabla de adyacencia por umbral y clasificación de rutas de emergencia; después diseñar vuelos y descansillos de escalera del núcleo con cotas reales, reutilizando material oculto solo si supera medidas/clearance. Resolver el bloqueo de Biología con versión incremental respaldada y verificación visual/QA.

## 2026-11-01 — Codex — Corrección de cotas y normales de puertas del ascensor (v92–v93)

- **Fecha y hora:** 2026-11-01 12:38 COT (17:38 UTC).
- **Agente:** Codex.
- **Fase de producción:** Fase 3, núcleo vertical y accesos (corrección incremental; núcleo aún incompleto).
- **Zona/departamento:** torre vertical, rellanos de L1–L5.
- **Objetivo:** corregir la altura de las hojas existentes del ascensor para que coincidan con el nivel de sus pisos; reparar normales y verificar el guardado incremental.
- **Archivo base:** `/home/riyo/Documentos/game/FM_NEXUS_V05_level1_v91.blend`.
- **Archivos nuevos:** `FM_NEXUS_V05_level1_v92.blend` (checkpoint tras alineación) y `FM_NEXUS_V05_level1_v93.blend` (estado actual, tras corregir normales). v90, su recuperación y v91 se conservaron.
- **Objetos modificados:** únicamente `NEXUS_VTOWER_ELEV_LEAF_L1/R1` hasta `NEXUS_VTOWER_ELEV_LEAF_L5/R5` (10 hojas preexistentes). Ningún objeto o colección creado o eliminado.
- **Cambios arquitectónicos:** se ajustó la cota inferior de cada hoja a la cota de su rellano: L1 −5,8 m; L2 −13,8 m; L3 −22,8 m; L4 −32,8 m; L5 −43,8 m. No se alteraron dimensiones, marcos, hueco, cabina, torre, escaleras ni conexiones.
- **Geometría/QA:** se recalcularon normales hacia afuera en las diez mallas. Blender Asset QA (`render`) confirma cero caras degeneradas, aristas no-manifold, aristas límite, vértices duplicados e islas con normales interiores. La herramienta todavía devuelve `pass=False` por nueve avisos de pieza flotante/detached: cada hoja se evalúa aislada del marco y esa regla no entiende que son hojas móviles separadas; el encaje debe revisarse en contexto. Advierte también que las mallas carecen de UV; conservado por ahora porque usan material uniforme y no se asignaron texturas. La comprobación genérica de suelo z=0 no aplica a elementos situados bajo tierra.
- **Verificación Blender MCP:** las diez cotas inferiores coinciden con la cota de piso correspondiente; `bpy.data.filepath` apunta a v93 y `bpy.data.is_dirty=False`. Se consultaron vistas de las hojas y marco L1; la lectura visual todavía no certifica todos los gálibos/encajes de puertas en los cinco niveles.
- **Materiales, texturas e iluminación:** sin cambios.
- **Problemas/soluciones:** el primer intento de localizar hojas con nombres supuestos falló antes de modificar Blender; el inventario reveló la nomenclatura real `..._LEAF_L1/R1`, etc. QA halló diez mallas cerradas con normales interiores; se corrigieron solo esas mallas. Sin cambios parciales por la consulta fallida.
- **Pendientes:** (1) revisar visualmente los cinco rellanos junto con paredes, cabina y puertas; (2) inspeccionar vuelos/descansillos históricos ocultos y diseñar continuidad de escaleras convencionales conforme a cotas de 8–11 m; (3) terminar el grafo de conexiones y evacuación; (4) resolver el bloqueo de Biología L2 (`NEXUS_V04_AIRLOCK_WALL_W`) una vez fijada la circulación.
- **Estado de Git:** rama `frecuencia-muerta`, HEAD `0db132a69a9d53c24386dc308e4a9f6f64e9aa04`; v92, v93 y ambos registros sin seguimiento. Persisten los numerosos recursos previos sin seguimiento; ninguno fue eliminado ni limpiado.
- **Versión de Blender:** 5.2.3 LTS.
- **Versión incremental guardada:** `/home/riyo/Documentos/game/FM_NEXUS_V05_level1_v93.blend` (estado limpio verificado en MCP).
- **Siguiente paso exacto:** usar v93 como base; inspeccionar un rellano completo y medir el espacio libre real de la torre junto a la escalera de mano y la cabina. Medir `STAIR_N2_N3_*` y `STAIR_N3_N4_*` ocultos para decidir reutilización sin mover ni eliminar piezas históricas.

### Inspección no destructiva de escaleras históricas — 2026-11-01 12:39 COT

- Se consultaron los objetos `STAIR_N2_N3_*` y `STAIR_N3_N4_*` en `02_CIRCULATION`; siguen ocultos en viewport y render, sin cambios.
- El primer conjunto contiene 22 peldaños, huella aproximada 0,66 × 1,50 m, diferencia vertical aproximada 8,6 m y recorrido horizontal de 13,1 m. El segundo contiene 24 peldaños, huella aproximada 0,68 × 1,40 m, diferencia vertical aproximada 9,6 m y recorrido horizontal de 14,6 m. Los incrementos verticales entre peldaños son aproximadamente 0,41 m; por ello no se consideran escaleras transitables por una persona y no se deben activar/reutilizar sin rediseño. Barandillas y postes también permanecen ocultos.
- La geometría queda lejos del enlace de torre activo en planta (coordenadas de los tramos históricos alrededor de X −21…−8 o X 7…22; enlace de torre alrededor de X 26–29); no se ha demostrado que conecten físicamente el núcleo vertical.
- No hubo edición ni guardado nuevo de Blender. Base válida sigue siendo v93, con `is_dirty=False`. Inspección de caja y nombres solamente; no se cambió visibilidad ni selección deliberadamente.
- **Siguiente paso ajustado:** medir el volumen libre de la torre y ubicar puertas, hueco, ladder y cabina por nivel; a la vez determinar si hay ubicación arquitectónica para un tramo accesible sin invadir el espacio de ascensor ni alterar rutas existentes. No dar por reutilizables los tramos ocultos.

## 2026-11-01 — Codex — Gálibos del núcleo y estudio de emplazamiento de escalera (v94–v97)

- **Fecha y hora:** 2026-11-01 12:45 COT (17:45 UTC).
- **Agente:** Codex.
- **Fase de producción:** Fase 3, núcleo vertical y accesos; auditoría y corrección local. El diseño de la nueva escalera convencional queda en propuesta previa a ejecución.
- **Zona/departamento:** torre vertical L1–L5 y volumen adyacente al este.
- **Objetivo:** medir las puertas del núcleo contra la altura oficial máxima del Vigilante; corregir el gálibo conservando los objetos existentes; medir el espacio libre cercano para proponer continuidad de escalera convencional.
- **Archivo base:** `/home/riyo/Documentos/game/FM_NEXUS_V05_level1_v93.blend`.
- **Versiones guardadas:** v94 es checkpoint de v93, sin geometría cambiada; v95 amplía hojas existentes; v96 ajusta dinteles; v97 es el estado activo después de corregir normales. No se sobrescribieron v90 ni su copia de recuperación; tampoco v91–v96.
- **Objetos modificados en Blender:** 15 hojas existentes: `NEXUS_VTOWER_ELEV_LEAF_L1/R1`…`L5/R5` y `NEXUS_VTOWER_STAIR_LEAF_1`…`_5`, llevadas de 2,20 a 3,12 m de altura. Se mantuvo la cota inferior; la puerta de ascensor coincide con el piso y la hoja abatible conserva el margen existente de 0,05 m. También se ajustaron seis dinteles existentes de L3–L5: `NEXUS_VTOWER_STAIR_DOOR_L{3,4,5}_TOP` y `NEXUS_VTOWER_ELEV_DOOR_L{3,4,5}_TOP`, de 0,40 a 0,20 m de grosor vertical, conservando sus bordes superiores. El vano libre medido en esos niveles queda en 3,28 m, 0,28 m sobre la altura oficial máxima de 3,0 m. En L1–L2 el vano ya supera 3,12 m. No se crearon ni eliminaron objetos o colecciones.
- **Cambios arquitectónicos:** solo gálibo de hojas y seis dinteles de los accesos verticales; anchos, umbrales, jambas, muros, vestíbulos, cabina, torre y conexiones horizontales no cambiaron. El cambio toma 3,12 m de la altura ya usada/documentada para las puertas estándar de L2.
- **Estudio espacial:** el volumen candidato al este de la torre, X=30,2–33,4 m, Y=10,9–15,1 m (3,2×4,2 m en planta), Z=−44,1…−1,36 m, no intersecta ninguna caja envolvente de geometría de escena consultada, incluida la oculta. Es una zona potencial para una torre de escaleras cerrada, conectada con puertas desde los vestíbulos de L1–L5 a través del muro este actual. Es solo un emplazamiento candidato: no se construyó, no se cortó el muro y aún deben verificarse los vuelos, descansillos, gálibos, estructura y el espacio de llegada a cada nivel.
- **Geometría histórica:** la escalera de mano enjaulada `NEXUS_VTOWER_LADDER_*` sí es continua por L1–L5, con 127 peldaños, jaula y descansos; sigue siendo una conexión técnica/alternativa, no una escalera convencional. Los vuelos históricos de `02_CIRCULATION` siguen ocultos: 0,41 m aprox. de contrahuella y sin conexión demostrada con el núcleo; no se reutilizaron.
- **Materiales/texturas/iluminación:** ninguno nuevo ni cambiado. Se conservaron materiales de hojas y marcos.
- **QA y revisión visual:** revisión de una puerta de L3 en contexto mostró la jaula de la escalera de mano detrás de la puerta y confirmó que aún no hay vuelos convencionales. Tras recalcular normales en cinco hojas de escalera y seis dinteles ajustados, la pasada Asset QA (`render`) registra cero normales interiores, caras degeneradas, aristas no-manifold y vértices duplicados entre los 21 objetos analizados. `pass=False` persiste por 20 detecciones de parte flotante/separada, porque las hojas y dinteles son objetos modulares independientes y la pasada no incluye todas las jambas/muros circundantes; requiere revisión de conjunto. También persisten 21 avisos de UV ausente en objetos de material uniforme sin textura. No se declara QA del núcleo terminado.
- **Errores/herramientas:** un primer `look` usó el nombre inexistente `NEXUS_VTOWER_LINK_L3`; falló sin cambiar la escena y se sustituyó por `NEXUS_LINK_L3_FLOOR`. La primera impresión de `Object.dimensions` inmediatamente tras editar mallas leyó valores en caché; se refrescó `view_layer` y la consulta posterior confirmó 3,12 m, cotas inferiores y claros reales. No quedó discrepancia sin resolver en v97.
- **Verificación de guardado:** MCP confirma `/home/riyo/Documentos/game/FM_NEXUS_V05_level1_v97.blend`, `bpy.data.is_dirty=False`, 7.079 objetos y 44 colecciones. Las 15 hojas miden 3,12 m. Los bordes superiores de los seis dinteles se mantienen en las cotas de techo originales.
- **Estado de Git:** rama `frecuencia-muerta`, HEAD `0db132a69a9d53c24386dc308e4a9f6f64e9aa04`; v94–v97 y ambos registros son archivos sin seguimiento. Otros recursos preexistentes sin seguimiento permanecen intactos.
- **Versión de Blender:** 5.2.3 LTS.
- **Siguiente paso exacto:** presentar para revisión el emplazamiento candidato al este (caja libre medida 3,2×4,2 m) como torre de escaleras cerrada; definir cortes/puertas en pared este y vuelos/descansillos para las separaciones L1–L2 8 m, L2–L3 9 m, L3–L4 10 m, L4–L5 11 m. `AGENTS.md` §47.10 exige presentar esta propuesta antes de iniciar un cambio estructural. Después de revisión, si se autoriza, crear respaldo incremental nuevo desde v97 y solo entonces modelar.

### Checkpoint de continuidad del estado vivo — 2026-11-01 12:46 COT

- Durante el cierre MCP informó `bpy.data.is_dirty=True` y objeto activo/seleccionado `NEXUS_V05_CONTROL_ACCESO_CEILING`, distintos del estado activo observado antes. No se pudo atribuir el cambio a una operación de geometría concreta. Las dimensiones verificadas de puertas y dinteles seguían correctas y la escena mantenía 7.079 objetos/44 colecciones.
- Se guardó el estado vivo como `/home/riyo/Documentos/game/FM_NEXUS_V05_level1_v98.blend` para conservarlo sin sobrescribir v97. La operación devolvió `FINISHED`; una consulta MCP separada confirmó v98 como ruta activa, `is_dirty=False`, 7.079 objetos y 44 colecciones.
- v98 mide 3.181.543 bytes. v90 (3.073.074 bytes), la recuperación (3.056.681 bytes) y v97 (3.181.517 bytes) conservaron tamaño y marcas de tiempo observados; no fueron sobrescritos.
- Estado Git: v97, v98, WORKLOG y CURRENT_STATE permanecen sin seguimiento; no se limpiaron cambios preexistentes.
- La escena queda en estado listo para revisión de la propuesta. No se modeló la extensión de escalera.

### Refinamiento de propuesta de escalera — 2026-11-01 12:48 COT

- Se comprobó una caja mayor, también sin intersecciones con cajas envolventes de geometría visible u oculta: X=30,2–33,8 m, Y=9,8–15,2 m, Z=−44,1…−1,36 m (3,6×5,4 m en planta). Alinearía su pared oeste con el muro este existente de la torre; la unión requiere aberturas coordinadas y aún no está construida.
- Esquema preliminar de ajuste (solo propuesta): huella objetivo 3,6×5,4 m; dos vuelos paralelos de 1,4 m de ancho separados por un hueco central de 0,4 m, estructura lateral de 0,2 m; huella de peldaño 0,27 m y descansillo de 1,1 m. El vuelo más largo tendría 14 contrahuellas/13 huellas = 3,78 m; vuelo + descansillo + muros de 0,2 m en ambos extremos suma 5,28 m, dentro de la caja medida con 0,12 m de margen. Revisar tolerancias y estructura en blockout antes de aceptar estas dimensiones.
- Distribución paramétrica para mantener cantidad par de vuelos por tramo y llegar a cada puerta con orientación compatible: L1–L2, 8 m, 44 contrahuellas en 4 vuelos de 11 (0,182 m por contrahuella); L2–L3, 9 m, 54 en 4 vuelos (13, 14, 13, 14; aprox. 0,167 m); L3–L4, 10 m, 60 en 4 vuelos de 15 (0,167 m); L4–L5, 11 m, 66 en 6 vuelos de 11 (0,167 m). Todas estas cifras son una hipótesis de blockout derivada de las cotas medidas, no un diseño constructivo aprobado. Verificar headroom de 3,12 m para el Vigilante, ancho útil para la silueta de las criaturas, zonas de cruce, descansillos y colisiones.
- Acceso propuesto por cada nivel desde el vestíbulo de la torre a través de una nueva puerta de 1,72×3,12 m en el muro este existente; esa anchura/altura toma como referencia las puertas interiores documentadas de L2. Debe comprobarse el espacio de maniobra y el dintel, sin bloquear el ascensor, la escalera de mano ni el vestíbulo.
- No se modificó Blender ni los archivos `.blend`. Esta propuesta responde al requisito de `AGENTS.md` §47.10: revisión previa antes del cambio estructural. Base actual para continuar es v98.

## 2026-11-01 — Codex — Prototipo de escalera este y validación de gálibo (v99–v100)

- **Fecha y hora:** 2026-11-01 13:20 COT (18:20 UTC).
- **Agente:** Codex.
- **Fase de producción:** Fase 3, núcleo vertical y accesos; blockout de escalera convencional en validación.
- **Zona/departamento:** anexo este de `NEXUS_VTOWER`, accesos L1–L5.
- **Objetivo:** materializar en una versión incremental la propuesta autorizada de escalera este, medir vanos/circulación y verificar el gálibo de criaturas sin tocar v90 ni la recuperación.
- **Archivo base:** `/home/riyo/Documentos/game/FM_NEXUS_V05_level1_v98.blend`. Al conectar MCP se encontró `bpy.data.is_dirty=True`, a pesar del cierre limpio documentado anteriormente. Para no perder ningún estado vivo, se guardó como checkpoint nuevo v99 antes de modelar; v98 y las versiones anteriores no se sobrescribieron.
- **Colecciones/objetos creados:** colección `NEXUS_VTOWER_EAST_STAIR` anidada en `NEXUS_VTOWER`, con 83 mallas: tres paredes de recinto, 18 vuelos, 19 descansillos, 18 conjuntos de barandilla y 25 piezas de cinco marcos/hojas abiertas. Colección hija `NEXUS_VTOWER_EAST_STAIR_CUTTERS` con cinco cortadores para puertas L1–L5.
- **Objeto existente modificado:** `NEXUS_VTOWER_WALL_E` conserva malla base (8 vértices/6 caras), material y bisel. Se añadió el modificador no destructivo `NEXUS_EAST_STAIR_DOOR_CUTS` antes del bisel, diferencia booleana exacta por colección. Cinco rayos MCP atraviesan los nuevos vanos; rayos cercanos siguen chocando con el muro intacto. No se aplicó ni eliminó el objeto/malla base.
- **Dimensiones/decisiones de blockout:** caja modelada X=30,14–36,52 m; Y=10,7–14,3 m; Z=−44,1…−1,36 m. Se mantuvieron cotas de nivel L1 −5,8; L2 −13,8; L3 −22,8; L4 −32,8; L5 −43,8 m, hojas/vanos de 1,72×3,12 m, huella nominal 0,27 m, ancho útil de vuelo 1,38 m y contrahuellas entre 0,167–0,182 m. Para alinear endpoints hubo que usar recorridos de planta comunes por tramo: 2,70; 3,51; 3,78; 2,70 m; en el tramo L2–L3 un vuelo de 13 contrahuellas queda con huella 0,2925 m. Esta es geometría provisional.
- **Materiales/texturas/iluminación:** se reutilizaron `NEXUS_Concrete`, `NEXUS_Steel`, `NEXUS_Painted_Metal` y `NEXUS_Dark_Metal`. No se crearon materiales, texturas ni luces. Se añadió UV atlas provisional por cara a las mallas para poder revisar QA; no sustituye UV final para texturizado.
- **Comprobación visual y QA:** se inspeccionaron vistas MCP three-quarter, top y front/xray del conjunto y de vuelos L4–L5. `blender-asset-qa` sobre 83 mallas dio finalmente `pass=True`: 4.684 triángulos; 0 z-fighting; 0 mallas con bordes no-manifold/boundary; 0 normales inconsistentes; 0 piezas flotantes; 83 mallas con UV. Quedan avisos de dos n-gons planos de cierre en cada vuelo y contactos de caras modulares (paredes de recinto y marcos), intencionales en blockout; QA los lista como caras ocultas back-to-back. No se declaró tránsito completo.
- **Problema detectado que bloquea aceptación:** los vuelos que se repiten en la misma franja XY se superponen verticalmente. El espacio calculado entre tramos es 1,84 m (L1–L2), 2,09 m (L2–L3), 2,34 m (L3–L4) y 1,673 m (L4–L5). El documento `docs/fm_nexus_nivel2.md` fija al Vigilante en 2,5–3,0 m; AGENTS/estado ya usa 3,12 m de gálibo de diseño. Por tanto v100 es un prototipo NO transitable/NO aprobado para criaturas y no debe detallarse como solución terminada.
- **Alternativas auditadas, solo por caja envolvente:** (A) cuatro franjas de escalera separadas para no solapar planta, caja candidata X=30,14–36,52, Y=8,8–15,7 m; (B) dos franjas con dos vuelos largos por desnivel, caja X=30,14–41,0, Y=10,7–14,3 m. Ambas cajas dieron cero colisiones AABB contra objetos anteriores a este prototipo, incluidos ocultos; esto no demuestra accesibilidad, gálibo en descansillos, ruta hasta las puertas, ni aprobación de mayor huella. No se construyeron estas alternativas.
- **Referencia de criatura consultada:** `fotos-referencia/modelos-referencia.png` muestra siluetas en escala comparativa y documenta altura aproximada del Vigilante 2,5–3,0 m; no proporciona ancho de paso numérico. El ancho útil de 1,38 m del prototipo requiere contrastarse con una envolvente/modelo de criatura y métricas reales de personaje antes de considerarse suficiente.
- **Errores de operación y resolución:** una consulta de ray cast intentó leer la malla evaluada después de `to_mesh_clear()` y lanzó `ReferenceError`; fue una lectura fallida sin cambios de escena, corregida guardando las métricas antes de liberar la malla. El primer generador de plataformas falló con `NameError` antes de crear el primer objeto; no hubo estado parcial. La primera pasada QA sí encontró railes con cotas Z repetidas y huellas/descansillos con superficies solapadas; se reconstruyeron únicamente los objetos de escalera creados en este bloque, se alinearon los recorridos, se corrigieron UVs y se repitió QA hasta `pass=True`. Ningún error de la herramienta dejó cambios parciales sin identificar.
- **Archivo guardado y verificado:** `/home/riyo/Documentos/game/FM_NEXUS_V05_level1_v100.blend`, 3.104.844 bytes. MCP confirmó ruta activa, `is_dirty=False`, 7.167 objetos, 46 colecciones, 83 objetos en colección principal y 5 cortadores en colección hija. v99 (3.181.404 bytes) es el checkpoint previo al modelo.
- **Preservación/Git:** v90 original (`3.073.074 bytes`) y copia recovery (`3.056.681 bytes`) no fueron sobrescritos. Los estados v98/v99 siguen conservados. Los archivos de Blender y docs siguen sin seguimiento; no se limpiaron recursos existentes ni se hizo commit.
- **Fase/material/iluminación:** ningún cambio de materiales existentes fuera de asignar los ya enumerados; sin texturas ni luces.
- **Siguiente paso exacto:** revisar con el usuario el replanteo que resuelve ≥3,12 m de gálibo. Preferencia técnica a evaluar: opción A, cuatro carriles alternados dentro de la caja auditada de 6,38×6,90 m, con descansillos parciales entre carriles; opción B: dos vuelos de mayor recorrido que extienden el anexo hasta X=41 m. No reemplazar ni modificar v100 hasta definir/autorizar la huella y validar las conexiones de descansillo con un prototipo geométrico. Después guardar v101 antes de cualquier cambio de escala y continuar con el recorrido del núcleo.
## 2026-11-01 — Codex — Validación y guardado del replanteo de escalera de cuatro franjas (v102)

- **Fecha y hora:** 2026-11-01 13:26 COT (18:26 UTC).
- **Agente:** Codex.
- **Fase de producción:** Fase 3, núcleo vertical y accesos; blockout revisado, circulación completa aún no certificada.
- **Zona/departamento:** torre este y conexiones verticales L1–L5.
- **Objetivo:** continuar desde el replanteo de cuatro franjas ya construido, revisar QA automatizado y visual, guardar una versión incremental nueva y dejar un siguiente paso reproducible.
- **Archivo base/checkpoint:** v101 `/home/riyo/Documentos/game/FM_NEXUS_V05_level1_v101.blend`; preservado sin sobrescribir.
- **Colecciones/objetos nuevos del bloque previo conservados:** `NEXUS_VTOWER_EAST_STAIR_4LANE`, con 58 mallas directas: tres paredes, 18 vuelos, 19 descansillos y 18 conjuntos de barandilla. Se comprobó la existencia de la colección en la escena viva. Los 25 componentes de puertas/marcos reutilizados siguen siendo los existentes; el modificador de colección `NEXUS_EAST_STAIR_DOOR_CUTS` y los cinco cortadores ocultos se conservan. El prototipo anterior `NEXUS_VTOWER_EAST_STAIR` permanece oculto individualmente y no se eliminó.
- **Objetos modificados durante este bloque:** se reconstruyeron únicamente los 18 objetos de vuelo de la nueva colección a partir de perfiles locales deduplicados, corrigiendo vértices/arestas degenerados y UVs de área cero detectados por QA. Los tres muros se ocultaron temporalmente solo para inspección visual y se restituyeron a su estado visible anterior. No se modificaron objetos originales de la instalación ni puertas existentes.
- **Cambios arquitectónicos:** se conserva el replanteo de cuatro franjas ya autorizado: huella global X=30,14–36,52 m, Y=8,8–15,7 m, Z=−44,1…−1,36 m; cuatro carriles de 1,38 m separados por 0,32 m. Los descansillos alternan el recorrido entre carriles. Se volvió a comprobar por rayos MCP que los cinco vanos del muro este dejan paso y el paño adyacente permanece cerrado. La prueba AABB contra geometría previa al prototipo reportó cero colisiones. El ancho útil continúa pendiente de comparar con la envolvente real de criaturas/controlador.
- **Materiales, texturas e iluminación:** sin cambios; se conservan los materiales Nexus existentes. No se añadieron texturas ni luces.
- **Problemas encontrados y soluciones:** la revisión anterior había detectado en cada vuelo dos vértices duplicados, una cara degenerada, dos aristas de longitud cero y una cara UV de área cero. Se corrigió el origen del error (deduplicación mezclaba coordenadas X de mundo con distancia local), reconstruyendo solo los vuelos de la colección nueva. QA repetido `game`: `pass=True`, sin errores, z-fighting ni flotantes; 4.384 tris evaluados en 58 mallas. Se aceptan provisionalmente, por ser blockout arquitectónico, dos n-gons planos de cierre por vuelo y nueve pares de caras ocultas coincidentes entre descansos/muros; revisar/optimizar si la geometría se conserva en versión final. El QA marca además Z mínima −44,1 m como aviso genérico de asset (el bloque pertenece a una instalación subterránea, no a un prop en z=0). La revisión MCP en material y wireframe permitió ver la secuencia de vuelos y las plataformas; no detectó obstrucción visual del nuevo recorrido. Dos llamadas iniciales `look` usaron nombres de objetivo inexistentes (nombre de colección en vez de objeto y un nombre de plataforma sin sufijo `_CROSS`); no hicieron cambios. Se consultaron los nombres reales y se repitió la inspección con éxito.
- **Operaciones pendientes:** medir ancho de la silueta en la imagen oficial si es posible; extraer métricas de colisión del controlador de jugador y cotejar 1,38 m, holguras/barandillas y maniobra de 19 plataformas; comprobar paso puerta a puerta desde vestíbulos L1–L5; validar rutas de emergencia y revisar grafo de circulación. No añadir detalle estético hasta cerrar métricas. Después continuar con el bloqueo del puente de Biología L2. No integrar en Godot.
- **Versión de Blender guardada:** Blender 5.2.3 LTS.
- **Archivo guardado:** `/home/riyo/Documentos/game/FM_NEXUS_V05_level1_v102.blend` (3.132.820 bytes). MCP confirmó ruta activa, `is_dirty=False`, archivo existente, 7.225 objetos y 47 colecciones. v101 y versiones anteriores permanecen intactas.
- **Estado de Git:** rama `frecuencia-muerta`, HEAD `0db132a69a9d53c24386dc308e4a9f6f64e9aa04` según la auditoría previa de esta sesión; `FM_NEXUS_V05_level1_v101.blend`, `FM_NEXUS_V05_level1_v102.blend`, `WORKLOG.md` y `CURRENT_STATE.md` sin seguimiento. Muchos recursos ya sin seguimiento siguen intactos; no se limpió el árbol ni se hizo commit.
- **Siguiente paso exacto:** usar v102 como base sin modificar hasta medir ancho útil de carriles y descansillos frente a las criaturas/personaje; registrar métricas y comprobar continuidad entre cada puerta y el corredor de su nivel. Si requiere cambios, crear un nuevo checkpoint incremental, sin sobrescribir v102.

## 2026-11-01 — Codex — Métricas de colisión para validar el ancho de escalera

- **Fecha y hora:** 2026-11-01 13:28 COT (18:28 UTC).
- **Agente:** Codex.
- **Fase de producción:** Fase 3, auditoría dimensional del núcleo vertical; inspección de solo lectura.
- **Zona/departamento:** escalera este de cuatro franjas, referencias de criaturas y controladores de jugador/entidad.
- **Objetivo:** determinar si existen métricas numéricas de ancho aplicables al blockout v102, sin editar Blender ni archivos de juego.
- **Archivos/objetos creados o modificados:** ninguno. Inspeccionados `fotos-referencia/modelos-referencia.png`, `scripts/fm/fm_player.gd`, `scripts/fm/fm_watcher.gd` y `scripts/fm/fm_creature_models.gd`; Blender v102 no se modificó y permanece guardado/limpio.
- **Hallazgos geométricos:** la escalera tiene carril nominal de 1,38 m; en un vuelo representativo el objeto de peldaños mide 1,38 m de ancho y el conjunto de barandillas ocupa una caja de 1,33 m. Este dato de caja no determina por sí mismo el claro libre interior entre pasamanos/postes. El rellano portal L1 tiene 6,52 m de ancho total, aunque sus zonas transitables se deben revisar junto a las divisiones de carril.
- **Métricas de colisión del proyecto:** `FMPlayer` crea una cápsula de radio 0,38 m (diámetro 0,76 m), altura 1,70 m. `FMWatcher` crea una cápsula de radio 0,40 m (diámetro 0,80 m), altura 2,35 m. El carril nominal es más ancho que ambos diámetros, pero falta medir el ancho interior entre barandillas y comprobar la maniobra real en descansillos.
- **Referencias:** `modelos-referencia.png` indica alturas aproximadas para las cuatro criaturas (Vigilante 2,5–3,0 m; las otras alrededor de 2,0–2,5 m) y muestra siluetas comparativas con jugador, pero no da anchos medidos. No se estima ni se inventa una anchura corporal a partir de la imagen. En el código inspeccionado solo se encontró cápsula activa del Vigilante; no se confirma aquí colisión jugable de las demás criaturas.
- **Problemas/limitaciones:** una cápsula de navegación puede ser más estrecha que extremidades del modelo visual; no se valida esa holgura con datos actuales. La altura de colisión de FMWatcher (2,35 m) también es inferior a su altura conceptual máxima (~3,0 m), aunque el gálibo arquitectónico establecido es 3,12 m. No se cambió el código.
- **Materiales, texturas e iluminación:** sin cambios.
- **Estado de Blender guardado:** sigue activo `/home/riyo/Documentos/game/FM_NEXUS_V05_level1_v102.blend`; última verificación previa: 3.132.820 bytes, `is_dirty=False`, 7.225 objetos y 47 colecciones.
- **Estado de Git:** sin cambios respecto a la auditoría anterior; documentos y versiones incrementales permanecen sin seguimiento. No se modificó ningún archivo de Godot ni se hizo commit.
- **Siguiente paso exacto:** en Blender, medir claros interiores de barandilla y radios/anchos de giro de descansillos para compararlos con las cápsulas Ø0,76/Ø0,80 m; luego verificar conexión sin obstrucciones desde cada puerta L1–L5. La envolvente visual de criaturas sigue sin medida oficial, por lo que no se debe declarar compatibilidad total hasta obtener sus dimensiones o decidir una métrica de colisión autorizada.

## 2026-11-01 — Codex — Medición de claros y plataformas de cuatro franjas

- **Fecha y hora:** 2026-11-01 13:29 COT (18:29 UTC).
- **Agente:** Codex.
- **Fase de producción:** Fase 3, verificación dimensional en curso; solo lectura.
- **Zona/departamento:** vuelos y descansillos de la torre este.
- **Objetivo:** resolver la medición estática de claros de barandilla/plataforma y cotejarla con cápsulas de colisión ya existentes.
- **Archivos/objetos creados o modificados:** ninguno. Lectura de las 18 mallas `*_RAILS`, los 19 objetos `*_LANDING_*`, `scripts/fm/fm_player.gd`, `scripts/fm/fm_watcher.gd` y referencia oficial; Blender permanece sin dirty y no se editó Godot.
- **Resultados:** el claro interior entre las dos barandillas es 1,21 m en los 18 vuelos. Frente a cápsulas diametrales Ø0,76 m (jugador) y Ø0,80 m (Vigilante), deja margen estático de 0,225 m y 0,205 m por lado, respectivamente, si están centradas. Los 14 descansos de transferencia miden 1,10–1,11 × 3,10 m; cinco plataformas portal 1,30 × 6,52 m; descanso transversal L4–L5 1,10 × 6,52 m. Sus cajas son mayores que ambas cápsulas, pero no demuestran por sí solas una ruta suave en giros ni colisiones sin enganches.
- **Referencias y límite:** `modelos-referencia.png` da alturas aproximadas, no anchuras. No inferir un ancho oficial de la ilustración; los modelos visuales podrían sobresalir de las cápsulas. La revisión de código solo confirmó cápsula de juego para jugador y Vigilante.
- **Problemas/errores:** la primera lectura de cajas en Blender falló porque no se importó `mathutils.Vector`; fue una operación de lectura sin cambios y se repitió correctamente. Ninguna modificación parcial.
- **Materiales, texturas e iluminación:** sin cambios.
- **Versión Blender:** 5.2.3 LTS; base viva v102, `/home/riyo/Documentos/game/FM_NEXUS_V05_level1_v102.blend`, 3.132.820 bytes, `is_dirty=False` verificado en el bloque anterior.
- **Estado de Git:** sin cambios; registros y versiones Blender permanecen sin seguimiento junto a recursos previos, todos preservados.
- **Siguiente paso exacto:** recorrer de forma geométrica las transiciones entre cada vuelo, descanso y umbral L1–L5 con las cápsulas Ø0,76/Ø0,80 m; detectar bordes, huecos o colisiones en giros. Si la trayectoria pasa, continuar con grafo de conexiones horizontales y rutas de emergencia. El ancho visual de criaturas todavía no está acotado.

## 2026-11-01 — Codex — Auditoría de continuidad entre los tramos verticales L1–L5

- **Fecha y hora:** 2026-11-01 13:30 COT (18:30 UTC).
- **Agente:** Codex.
- **Fase de producción:** Fase 3, verificación geométrica del blockout vertical; solo lectura.
- **Zona/departamento:** escalera este de cuatro franjas, portales L1–L5.
- **Objetivo:** comprobar la continuidad espacial de cada secuencia portal-vuelos-descansillos sin editar objetos ni archivo.
- **Objetos/archivos creados o modificados:** ninguno. Se leyeron bounds, vértices y superficies de los 18 vuelos y 19 descansillos de `NEXUS_VTOWER_EAST_STAIR_4LANE`. El archivo v102 permanece activo y sin cambios.
- **Cambios arquitectónicos:** ninguno.
- **Verificación:** se comprobó una ruta completa entre portales consecutivos en cada tramo: L1–L2 (4 vuelos), L2–L3 (4), L3–L4 (4) y L4–L5 (6). En los 36 empalmes consecutivos, la intersección de cajas XY es positiva: mínimo 0,01 m longitudinal × 1,38 m transversal. Las entradas desde descansos a vuelos quedan a nivel; las salidas de vuelo hacia descanso tienen descenso de una contrahuella, entre 0,167 y 0,182 m. No hay salto de transición mayor a una contrahuella ni huecos de caja entre superficies adyacentes. Esto es una comprobación de geometría/bounds, no una simulación de CharacterBody ni evaluación de extremidades de criaturas.
- **Materiales, texturas e iluminación:** sin cambios.
- **Problemas encontrados y soluciones:** ninguno en esta comprobación.
- **Operaciones pendientes:** revisar circulación horizontal completa y rutas alternativas/emergencia en cada nivel; registrar el bloqueo existente de Biología L2. Después comprobar el encuentro físico de cada corredor con los cinco portales de escalera. La dimensión visual de las criaturas no está acotada por sus referencias.
- **Versión Blender guardada:** 5.2.3 LTS, v102 ya guardado previamente en `/home/riyo/Documentos/game/FM_NEXUS_V05_level1_v102.blend` (3.132.820 bytes; 7.225 objetos; 47 colecciones; `is_dirty=False`). No se volvió a guardar porque no hubo cambios en Blender.
- **Estado de Git:** sin cambios; documentos y blends permanecen sin seguimiento, no se hizo commit ni limpieza.
- **Siguiente paso exacto:** auditar el grafo horizontal por nivel desde puertas de departamento hasta corredor principal, ramales y portal de núcleo, clasificando rutas bloqueadas/alternativas/emergencia. No mover ni abrir puertas hasta documentar cada conflicto y revisar el diseño.

## 2026-11-01 — Codex — Umbrales del núcleo y primera auditoría horizontal L1 (v103–v104)

- **Fecha y hora:** 2026-11-01 13:34 COT (18:34 UTC).
- **Agente:** Codex.
- **Fase de producción:** Fases 2–3, continuidad de circulaciones y núcleo vertical.
- **Zona/departamento:** cinco puertas entre vestíbulos L1–L5 y anexo este; auditoría inicial de corredor L1.
- **Objetivo:** comprobar la unión de suelos con los cinco vanos de la nueva escalera, corregir el hueco verificado y empezar auditoría de acceso horizontal.
- **Archivo base/checkpoint:** v103 `/home/riyo/Documentos/game/FM_NEXUS_V05_level1_v103.blend`, guardado desde v102 antes de cualquier geometría de umbral; sin sobrescribir versiones anteriores.
- **Objetos y colección creados:** cinco piezas `NEXUS_VTOWER_EAST_STAIR_4L_THRESHOLD_L1`…`L5`, enlazadas directamente en `NEXUS_VTOWER_EAST_STAIR_4LANE`. Cada una de 0,28×1,68×0,12 m, asignada a `NEXUS_Concrete`, UVs en atlas sin solape. v104 tiene 7.230 objetos, 47 colecciones; la colección de cuatro franjas tiene 63 objetos directos.
- **Objetos existentes modificados:** ninguno. No se alteraron losas, paredes, hojas/jambas, modificador Boolean ni cortadores. Los vértices superiores de cada umbral nuevo se elevaron solo 6 mm respecto a la cota nominal para separar una cara inferior coplanar de `NEXUS_VTOWER_WALL_E`. Los laterales de extremo no tienen tapas porque se empalman contra las losas y plataformas preexistentes. Visibilidad de `NEXUS_VTOWER_WALL_E` y los tres muros nuevos se cambió temporalmente para inspección y se restauró al estado anterior.
- **Cambios arquitectónicos:** se rellenó el espacio de 0,28 m correspondiente al espesor de muro entre cara de losa y plataforma en L1–L5. El vano mantiene 1,68 m entre jambas interiores. La superficie resultante crea una junta/umbral de 6 mm; no se cambió el diseño de puerta ni la abertura. En L1 se inspeccionó también el corredor principal: `NEXUS_V05_CORR_FLOOR` mide 44×3,4 m; `NEXUS_LINK_L1_FLOOR` se prolonga hasta el vestíbulo; rayos a altura de cuerpo pasan del link al núcleo y del núcleo hacia la puerta del anexo. Las seis hojas departamentales (recepción, seguridad, control de acceso, vestuarios, almacén y mantenimiento) están cerradas en la escena y reciben el rayo. No se alteraron porque su operación pertenece a la revisión de puertas/interacción.
- **Verificación:** rayos verticales desde cada nivel impactan su umbral a z de piso +0,006 m. Rayos horizontales a z+0,05 m atraviesan los cinco vanos; no detectan obstrucción. QA contextual de los cinco umbrales, cinco plataformas portal y `NEXUS_VTOWER_WALL_E`: cero z-fighting y cero piezas flotantes asociados a los umbrales; el resultado del grupo da `pass=False` por `NEXUS_VTOWER_WALL_E` preexistente sin UV. Hay avisos de n-gons del muro y caras de contacto ocultas muro/plataforma. Revisión visual MCP muestra suelo del núcleo y escalera por el vano. v104 guardado: 3.135.816 bytes; una consulta MCP posterior confirmó ruta activa v104, `is_dirty=False`, 7.230 objetos, 47 colecciones.
- **Problemas/errores:** QA inicial de umbrales aislados indicó flotantes porque la comprobación no incluía geometría vecina; UVs inicialmente apiladas al 100 % se cambiaron a celdas separadas; se incluyeron plataformas/walls de contexto para revisar contacto. La cara inferior coplanar del muro produjo z-fighting en L3; se repitió la consulta y se determinó que el booleano del muro mantiene superficie en la cota del piso, así que el top del umbral se subió 6 mm. QA contextual final no encuentra z-fighting. Una lectura de bounds falló primero por no importar `Vector` y se repitió sin cambios. Una primera prueba de rayos horizontales se originó dentro de la losa; se repitió a +1 m (para medir paso) y +0,05 m (para medir el vano). En un sondeo contextual se detectaron UV ausentes/normales interiores en `NEXUS_VTOWER_L{1..5}_SLAB_S`, objetos preexistentes que no se modificaron.
- **Materiales, texturas e iluminación:** se reutilizó `NEXUS_Concrete`; no se crearon texturas ni luces.
- **Operaciones pendientes:** terminar el grafo L1, documentar si las seis hojas cerradas deben abrirse/interactuar en el juego; continuar con L2–L5, rutas alternativas y emergencias. Mantener el bloqueo de Biología L2 sin intervenir hasta decidir su conexión. Revisar después los problemas QA existentes de muro/losas como trabajo separado y justificado.
- **Versión de Blender:** Blender 5.2.3 LTS.
- **Archivo guardado:** `/home/riyo/Documentos/game/FM_NEXUS_V05_level1_v104.blend`, 3.135.816 bytes, ruta activa y limpia (`is_dirty=False`). v103 (3.132.716 bytes), v102 y anteriores permanecen intactos.
- **Estado de Git:** rama/HEAD no cambiaron según la revisión previa; v103, v104 y los dos documentos continúan sin seguimiento, igual que recursos históricos sin seguimiento. No se hizo commit, reset, limpieza ni modificación de Godot.
- **Siguiente paso exacto:** completar auditoría de L1 desde el corredor de 44 m por las seis puertas y el enlace a núcleo, clasificando hoja cerrada/operable y salidas; después iniciar L2 con la conexión ya documentada de Biología bloqueada. No mover ni abrir puertas hasta analizar su mecanismo y el diseño de circulación.

## 2026-11-01 — Codex — Cierre de comprobación de circulación horizontal L1

- **Fecha y hora:** 2026-11-01 13:37 COT (18:37 UTC).
- **Agente:** Codex.
- **Fase de producción:** Fase 2, auditoría de circulación horizontal; solo lectura.
- **Zona/departamento:** corredor L1, seis departamentos, conector este, vestíbulo de torre y salida oeste.
- **Objetivo:** aclarar si las puertas departamentales de L1 conectan a vanos libres y confirmar los extremos del corredor.
- **Objetos/archivos creados o modificados:** ninguno. Las seis hojas `NEXUS_V05_{RECEPCION,SEGURIDAD,CONTROL_ACCESO,VESTUARIOS,ALMACEN,MANTENIMIENTO}_DOOR_LEAF` se ocultaron temporalmente por inspección y cada estado `hide_get()` se restauró a `False`. v104 continúa activo y limpio.
- **Hallazgos:** corredor `NEXUS_V05_CORR_FLOOR` de 44×3,4 m. Un rayo hacia el extremo oeste impacta `NEXUS_V05_CORR_END_-22` a x≈−21,86 m: no es salida al exterior. Seis rayos por departamento chocan con sus hojas en posición actual. Al ocultar solo esas hojas, los rayos atraviesan los seis vanos y no golpean pared; el de mantenimiento alcanza el panel `NEXUS_V05_MAINT_PANEL` a 6,825 m del origen, dentro del recinto. La llegada al conector este/vestíbulo y desde el vestíbulo a la puerta del anexo se atraviesa a altura de cuerpo en rayos de ambos segmentos.
- **Estado arquitectónico/funcional:** los seis umbrales existen y la pared tiene hueco; las hojas se encuentran físicamente cerradas en Blender y no se probó que se abran/animen. No clasificar las habitaciones como transitables durante gameplay hasta confirmar mecanismo/estado de puerta. No se movieron hojas.
- **Problemas/errores:** primer raycast de corredor había comenzado dentro del volumen de la losa, por lo que devolvió el piso; se repitió a altura de cuerpo (z del piso +1 m). En esta comprobación temporal, cinco rayos no golpearon objeto dentro de 7 m tras ocultar las hojas; el de mantenimiento golpeó panel ya situado dentro del cuarto. Todas las hojas se restauraron visibles al terminar. Sin estado parcial.
- **Materiales, texturas e iluminación:** sin cambios.
- **Versión Blender guardada:** Blender 5.2.3 LTS; v104 `/home/riyo/Documentos/game/FM_NEXUS_V05_level1_v104.blend`, 3.135.816 bytes, `is_dirty=False`, 7.230 objetos/47 colecciones.
- **Estado de Git:** sin cambios; v103/v104 y ambos docs siguen sin seguimiento, no se hizo commit ni limpieza.
- **Siguiente paso exacto:** auditar L2 desde el corredor y cruces a cada departamento, anotando puertas, rutas alternativas, salida y el bloqueo de Biología en el muro oeste de esclusa. No abrir ese paso ni mover otras puertas hasta dibujar el grafo y confirmar el vano requerido.

## 2026-11-01 — Codex — Auditoría espacial de corredores y accesos de L2

- **Fecha y hora:** 2026-11-01 13:40 COT (18:40 UTC).
- **Agente:** Codex.
- **Fase de producción:** Fase 2, circulación del nivel L2; inspección no destructiva.
- **Zona/departamento:** corredores oeste, principal y este; Nave, Biología, Química, Análisis, Servidores, Archivo científico, Esclusa y conector al núcleo.
- **Objetivo:** comprobar la organización de pasillos, accesos a habitaciones y conexión al núcleo, y reconfirmar el bloqueo de Biología sin alterar su diseño.
- **Archivos/objetos creados o modificados:** ninguno. Se leyeron bounds de `NEXUS_V04_CORR_{WEST,MAIN,EAST}_FLOOR`, siete suelos de recinto, `NEXUS_LINK_L2_*`, hojas de puertas y puentes `NEXUS_FIX_GAP_*`. Se ocultaron temporalmente hojas de puertas y `NEXUS_STORY_L2B_AIR_APRON` para rayos; todos sus estados visibles originales se restauraron. La escena continúa en v104, `is_dirty=False`.
- **Hallazgos de circulación:** corredores oeste/main/este se encuentran en una T; el corredor este continúa por `NEXUS_LINK_L2_FLOOR` al umbral de torre. Rayos a altura de cuerpo desde corredor este hacia el conector a y=11 y 12,5 no encontraron obstáculo. Química, Nave, Análisis, Archivo y Esclusa tienen vanos que permiten rayo tras apartar la hoja: algunos rayos llegan hasta objetos dentro de cada habitación (panel de mantenimiento/monitor de química/estantería de archivo). Los rayos de servidor y esclusa también cruzan hacia su lado del umbral cuando se alinean; las hojas permanecen físicamente cerradas. La red de pasillos con puertas de un acceso se comporta como T/ramas; no se identificó un loop de circulación alternativo.
- **Bloqueo de Biología:** tras ocultar solo para la prueba la hoja de puerta, hoja de esclusa y `AIR_APRON`, el rayo desde Bio a la esclusa choca con el paño sólido `NEXUS_V04_AIRLOCK_WALL_W` en x=−2,14 m. `NEXUS_FIX_GAP_BIO_FLOOR` lleva el suelo hasta la pared, pero no crea un vano; el bloqueo permanece sin cambios.
- **Defecto nuevo de continuidad en Servidores:** el piso del corredor principal termina en x=1,70 m y `NEXUS_FIX_GAP_SRV_FLOOR` empieza en x=2,00 m; un rayo vertical confirma que no hay suelo en el tramo de 0,30 m (p. ej., y=−9,5). La pared este de la esclusa ocupa x≈1,86–2,14 y termina en y=−10; para entrar por la puerta de servidor desde el norte, la cápsula Ø0,80 m dispone de una banda geométrica estimada de centros de ~0,06 m en el cuello, sin incluir margen del motor. Se clasifica como paso no certificado, no corregido. Requiere estudiar una ruta/umbral y la relación con la pared de esclusa.
- **Materiales, texturas e iluminación:** sin cambios.
- **Problemas/errores de inspección:** un primer rayo Bio→Esclusa detectó `NEXUS_STORY_L2B_AIR_APRON` cerca del punto de inicio; al ocultar temporalmente ese accesorio y las hojas, el muro oeste quedó identificado como obstáculo de fondo. Un primer rayo a servidor atravesó el marco de esclusa; se cambió el punto de partida a y=−9,5, donde la hoja oculta permite el rayo, y se midió por separado el suelo ausente. La prueba temporal no cambió la escena y todos los estados se restauraron.
- **Estado de Blender guardado:** v104 `/home/riyo/Documentos/game/FM_NEXUS_V05_level1_v104.blend`, 3.135.816 bytes; consulta final MCP: activo, `is_dirty=False`, 7.230 objetos, 47 colecciones. No se creó nueva versión porque no hubo cambios.
- **Estado de Git:** v104 y ambos registros continúan sin seguimiento junto a recursos preexistentes sin seguimiento. HEAD no se modificó; no hubo commit, reset ni limpieza.
- **Siguiente paso exacto:** pasar a auditoría no destructiva de L3 por cada puerta y circuito; continuar luego con L4, L5 y exterior. Antes de alterar L2, presentar una solución arquitectónica comprobable para el estrechamiento de Servidores y el acceso Bio–Esclusa; no cortar paredes ni mover puertas hasta resolver el recorrido completo y el efecto sobre la contención.

## 2026-11-01 — Codex — Auditoría geométrica de circulación L3

- **Fecha y hora:** 2026-11-01 13:43 COT (18:43 UTC).
- **Agente:** Codex.
- **Fase de producción:** Fase 2, circulación y continuidad por planta; auditoría no destructiva.
- **Zona/departamento:** L3, anillo médico, enfermería, quirófano, aislamiento A/B, cámaras frigoríficas, habitaciones médicas, morgue y enlace a torre.
- **Objetivo:** comprobar la continuidad lineal del anillo, el paso a la torre, la alineación de siete vanos y el contacto de suelo en ambos lados.
- **Objetos/colecciones/archivos creados o modificados:** ninguno en Blender. Se consultaron pisos, siete hojas `NEXUS_LDOOR_*_LEAF`, siete umbrales `NEXUS_LRING_L3_THRESH_*` y objetos del anillo. Las hojas fueron ocultadas temporalmente para rayos y se restauraron a `hide_get()=False` (visibles); se actualizaron sus estados de vista tras la restauración. No se movieron objetos ni se tocó geometría, materiales o luces. Se actualizó `docs/CURRENT_STATE.md`.
- **Hallazgos de circulación:** rayos horizontales a z=−20,5 m recorren sin impacto los cuatro segmentos cardinales del anillo y el link al núcleo. Con las siete hojas ocultas temporalmente, rayos desde el lado del anillo atraviesan los vanos en las siete habitaciones. Rayos verticales en puntos de corredor y cuarto encuentran sus pisos contiguos en z=−22,65 m. Esto confirma línea de paso y presencia de suelo en muestras puntuales, no navegación de cápsula, giros ni funcionamiento de puertas.
- **Hallazgo arquitectónico pendiente:** los siete umbrales existentes tienen tope z=−22,76 m, 0,11 m bajo las losas contiguas. Rayos verticales a los centros alcanzan la losa de corredor a z=−22,65 m antes que el umbral, por lo que los umbrales quedan tapados/empotrados. No se elevaron; revisar visualmente y resolver cotas y contacto antes de editar.
- **Cambios arquitectónicos, materiales, texturas e iluminación:** ninguno.
- **Problemas/errores de inspección:** la primera lista de nombres de pisos cardinales usó sufijos E/W/N/S en orden incorrecto; se consultaron los nombres reales `NEXUS_LRING_L3_FLOOR_{E,W,N,S}`. El primer ensayo horizontal partió dentro del bloque central y tocó separadores; se repitió desde las franjas perimetrales correctas. La primera llamada a `ray_cast` desempaquetó cinco valores, pero Blender 5.2 devolvió seis; hubo error antes de completar las pruebas y un bloque `finally` restauró estados. Los ensayos repetidos dieron los hallazgos anteriores.
- **Estado de Blender y guardado:** archivo vivo v104 `/home/riyo/Documentos/game/FM_NEXUS_V05_level1_v104.blend`, Blender 5.2.3, 7.230 objetos/47 colecciones. MCP informa `bpy.data.is_dirty=True`, aunque esta auditoría no hizo cambios geométricos; la bandera ya estaba en true en la primera lectura de esta sesión. Las visibilidades temporales quedaron restauradas. No se guardó para evitar sobrescribir v104 sin saber el origen de la bandera; v104 continúa como última versión guardada conocida, 3.135.816 bytes según el registro anterior. No se creó una nueva versión.
- **Estado de Git:** HEAD y rama sin intervención; `docs/CURRENT_STATE.md` y `docs/WORKLOG.md` son archivos sin seguimiento, al igual que v104 y muchos recursos preexistentes. No se hizo commit, reset ni limpieza.
- **Siguiente paso exacto:** iniciar auditoría no destructiva de L4 (habitaciones y puertas de seguridad/contención, anillo, link vertical y rutas secundarias), usando rayos desde el corredor perimetral y muestras de suelo; después auditar L5 y superficie. No corregir los umbrales L3 hasta revisar su contacto visual y cotas.

## 2026-11-01 — Codex — Auditoría geométrica de circulación L4

- **Fecha y hora:** 2026-11-01 13:44 COT (18:44 UTC).
- **Agente:** Codex.
- **Fase de producción:** Fase 2, circulación y continuidad por planta; auditoría no destructiva.
- **Zona/departamento:** L4, anillo, armería, búnker de seguridad, contención primaria/secundaria, control de contención, laboratorio restringido y enlace a torre.
- **Objetivo:** verificar anillo perimetral, link al núcleo, vanos departamentales y cotas de piso/umbrales.
- **Objetos/colecciones/archivos creados o modificados:** ninguno en Blender. Se consultaron objetos del anillo, puertas, umbrales, pisos y `CORRIDOR_L-4_00..05_*`. La geometría antigua `CORRIDOR_L-4_00..05_*` está oculta en `02_CIRCULATION` y se dejó intacta. Las seis hojas activas de departamentos y las dos hojas de puerta central se ocultaron temporalmente para los rayos y se restauraron a visibles (`hide_get()=False`). No se tocaron geometrías, colecciones, materiales, texturas ni luces. Se actualizaron los registros de continuidad.
- **Hallazgos de circulación:** rayos horizontales a z=−30,5 m recorren los cuatro segmentos cardinales y el link a torre sin impactos. Las seis rutas de departamento atraviesan los vanos al ocultar las hojas; el rayo de contención secundaria alcanza `NEXUS_LROOM_CONTENCION_SECUNDARIA_CYL_0` a x≈12,555 m, dentro del cuarto. La puerta doble norte del bloque central ofrece línea de paso en el rayo probado. Estos son rayos puntuales; no certifican cápsulas, giros ni funcionamiento de puertas.
- **Hallazgo de umbrales:** los seis `NEXUS_LRING_L4_THRESH_*` tienen tope z≈−32,76/−32,80 m. Las losas de anillo y habitaciones llegan a z=−32,65 m; rayos verticales a los centros impactan primero las losas. Los umbrales se encuentran cubiertos/empotrados alrededor de 0,11–0,15 m; no se elevaron. Revisar visualmente contacto/cotas antes de un cambio.
- **Estructura histórica:** los seis corredores `CORRIDOR_L-4_00..05_*` están ocultos; no se reactivaron ni reorganizaron. La circulación visible comprobada es el anillo `NEXUS_LRING_L4_*` y el enlace este.
- **Cambios arquitectónicos, materiales, texturas e iluminación:** ninguno.
- **Problemas/errores de inspección:** la primera medición vertical comenzó por encima del techo y reportó techo; se repitió desde dentro del volumen libre a z=−30 m. Algunos puntos verticales interiores de habitación encontraron bancos, consola o utilería narrativa antes del piso; esos impactos no se interpretaron como discontinuidad, y los bounds de los pisos comparten la cota de losa. En la aproximación a contención secundaria, la utilería está en la línea central del rayo después del vano; requiere evaluación con cápsula/ruta, sin moverla en esta auditoría.
- **Estado de Blender y guardado:** sesión viva v104 `/home/riyo/Documentos/game/FM_NEXUS_V05_level1_v104.blend`, Blender 5.2.3, 7.230 objetos/47 colecciones. `bpy.data.is_dirty=True` persistió en las lecturas; hojas restauradas. No se guardó ni se creó versión nueva para no sobrescribir v104 mientras se desconoce el origen de la bandera. v104, 3.135.816 bytes según el registro anterior, es la última versión guardada conocida.
- **Estado de Git:** HEAD/branch no se modificaron; documentos y v104 continúan sin seguimiento. Sin commit, reset ni limpieza.
- **Siguiente paso exacto:** iniciar auditoría no destructiva de L5 (anillo, puertas, pisos, habitaciones, bombas, generadores, refrigeración, túnel/extracción y link a torre); luego auditar superficie/exterior. Mantener pendientes de corrección los umbrales enterrados L3/L4 y los bloqueos de L2.

## 2026-11-01 — Codex — Auditoría geométrica de circulación L5

- **Fecha y hora:** 2026-11-01 13:45 COT (18:45 UTC).
- **Agente:** Codex.
- **Fase de producción:** Fase 2, circulación y continuidad por planta; auditoría no destructiva.
- **Zona/departamento:** L5, archivo secreto, bombeo/inundación, extracción profunda, generadores, refrigeración, túnel profundo, anillo y link de torre.
- **Objetivo:** comprobar rutas del anillo, seis puertas de recinto, puntos de suelo y conexión hacia la torre.
- **Objetos/colecciones/archivos creados o modificados:** ninguno en Blender. Se consultaron floors, umbrales, link, hojas de puerta y `CORRIDOR_L-5_00..05_FLOOR`; las hojas se ocultaron temporalmente y se restauraron visibles. Los corredores históricos permanecen ocultos y sin alterar. Se actualizaron `docs/CURRENT_STATE.md` y este registro.
- **Hallazgos de circulación:** rayos a z=−41,5 m pasan por los cuatro tramos del anillo y el link a torre. Con hojas ocultas, los rayos atraviesan las seis entradas; los de extracción y túnel alcanzan respectivamente `NEXUS_POLISH_L5_WINCH_MOTOR` (x≈−7,5, y=−10,65) y `NEXUS_LROOM_TUNEL_PROFUNDO_FRAME_1_POST_1` (x=4,5, y≈−9,56) ya dentro de sus recintos. Las muestras verticales de los umbrales impactan las losas del anillo a z=−43,65 m. No equivale a navegación de cápsula.
- **Hallazgo de umbrales:** los seis `NEXUS_LRING_L5_THRESH_*` tienen tope z≈−43,76/−43,80 m frente a losas en z=−43,65 m; quedan cubiertos/empotrados 0,11–0,15 m. No se corrigieron.
- **Geometría histórica:** los pisos `CORRIDOR_L-5_00..05_FLOOR` están ocultos; se conservaron intactos. Circulación visible bajo prueba: `NEXUS_LRING_L5_*` y `NEXUS_LINK_L5_*`.
- **Cambios arquitectónicos, materiales, texturas e iluminación:** ninguno.
- **Problemas/errores de inspección:** ninguna llamada fallida en esta etapa. Rayos a extracción/túnel contactan utilería narrativa después de entrar; se registra como necesidad de revisar gálibo y giro con cápsula, sin declarar obstrucción completa ni mover objetos.
- **Estado de Blender y guardado:** v104 activo en `/home/riyo/Documentos/game/FM_NEXUS_V05_level1_v104.blend`, Blender 5.2.3, 7.230 objetos/47 colecciones; `is_dirty=True`. Hojas restauradas visibles. No se guardó ni creó incremento. v104 (3.135.816 bytes, según registro previo) es la última versión guardada conocida.
- **Estado de Git:** HEAD/branch no se modificaron; docs y v104 permanecen sin seguimiento. Sin commit, reset ni limpieza.
- **Siguiente paso exacto:** auditar superficie/exterior con vistas y bounds; verificar si existe parcela, perímetro, acceso peatonal/vehicular, recepción de suministros y conexión real al extremo oeste de L1. No construir hasta confirmar que no hay geometría existente oculta o histórica que cumpla esa función.

## 2026-11-01 — Codex — Auditoría de superficie y checkpoint v105

- **Fecha y hora:** 2026-11-01 13:47 COT (18:47 UTC).
- **Agente:** Codex.
- **Fase de producción:** Fase 1, protección y auditoría global previa a la propuesta exterior.
- **Zona/departamento:** superficie, torre este y cap oeste de L1; referencias visuales del proyecto.
- **Objetivo:** comprobar si ya existe geometría de superficie que deba conservarse y localizar conexiones reales hacia L1 antes de proponer/modelar el exterior.
- **Objetos/colecciones/archivos creados o modificados:** no se modificó geometría de Blender. Inventario solo lectura de 47 colecciones, meshes visibles con bounds sobre z=−2 m, cap oeste y módulos históricos de recepción/seguridad. `RECEPCION_NEXUS_*` y `SEGURIDAD_PERIMETRAL_*` permanecen ocultos y en su ubicación de L1. Se creó el checkpoint incremental `/home/riyo/Documentos/game/FM_NEXUS_V05_level1_v105.blend` desde el estado vivo; v104 y anteriores no se sobrescribieron. Se actualizó `docs/CURRENT_STATE.md`.
- **Hallazgos:** no existe colección exterior ni parcela, perímetro, garita, acceso peatonal/vehicular, andén o calle de servicio activa. Recuento corregido: 144 meshes visibles tienen bound superior sobre z=−2 m; todos pertenecen a colecciones `V05_*`/`NEXUS_VTOWER*` (estructura, utilería, luces o torre). Solo `NEXUS_V05_RECEPCION_CEILING` llega a z=+0,32 m; no hay terreno ni paso al exterior confirmado. El corredor principal termina en `NEXUS_V05_CORR_END_-22`, cap en x≈−22 m. Los módulos históricos de recepción/seguridad son recintos L1 a z≈−6…−2 m, no una entrada exterior. El techo de la torre cierra parte del volumen superior; no se verificó continuidad al exterior.
- **Referencias:** listado y hoja de contacto de los 17 PNG en `fotos-referencia/` revisados; se abrió en tamaño original `modelos-referencia.png` y `Imagen pegada.png`. La hoja de criaturas indica alturas aproximadas: Imitador 2,2–2,5 m; Vigilante 2,5–3,0 m; Coleccionista 2,0–2,5 m; Sombra 2,0–2,5 m; no presenta cotas de anchura. `Imagen pegada.png` presenta un acceso industrial interior/catwalk húmedo con tuberías, luz fría, bruma y señales cálidas; no define una parcela exterior. Las referencias no muestran claramente el exterior privado de NEXUS. Imágenes fuente intactas; la hoja de contacto temporal se escribió solo en `/tmp/fm_reference_contact.png`.
- **Materiales, texturas, iluminación y cambios arquitectónicos:** ninguno.
- **Problemas/errores:** MCP informó `bpy.data.is_dirty=True` desde la primera lectura de esta sesión, pese a que el log previo indicaba v104 limpio. Para preservar el estado vivo se guardó una nueva versión v105 sin sobrescribir v104. El operador devolvió `FINISHED`; v105 tiene 3.135.995 bytes. La lectura inmediata siguió mostrando `is_dirty=True`, pero la consulta de verificación final devolvió `is_dirty=False` sin otro guardado. La causa de la transición no está determinada; no se detectaron cambios geométricos de auditoría. El primer filtro de bounds excluía algunos objetos que tocaban el intervalo de techo; se amplió a `max_z > −2 m` y el conteo verificado resultó 144. Conteo de escena final: 7.230 objetos/47 colecciones.
- **Estado de Git:** sin commit, reset ni limpieza; docs y v105 siguen sin seguimiento junto con numerosos recursos existentes.
- **Siguiente paso exacto:** preparar y documentar el plano de la superficie y su conexión funcional a L1, evaluando cómo sustituir el cap o crear un nuevo acceso sin eliminarlo, y dimensionando edificios/rutas según funciones, niveles existentes y métricas oficiales. Consultar el plan aprobado y la regla AGENTS.md §47.10 antes de cambiar arquitectura. No iniciar geometría exterior hasta tener un plano/cotas revisables; no sobrescribir v90, recuperación, v104 ni v105.



## 2026-11-01 13:58 COT — Codex — Auditoría integral y plan arquitectónico NEXUS

- **Fase:** auditoría integral, propuesta arquitectónica y estándar dimensional; modelado aún no autorizado.
- **Zona:** toda la instalación; Acceso V05 y bandas V04/L3/L4/L5, núcleo vertical y referencias visuales.
- **Objetivo:** inventariar habitaciones y huellas, evaluar conexiones/funciones, fijar criterios dimensionales y preparar secuencia de producción sin alterar Blender.
- **Archivos creados:** docs/NEXUS_ARCHITECTURAL_AUDIT.md y docs/NEXUS_DIMENSIONAL_STANDARD.md.
- **Archivos actualizados:** docs/CURRENT_STATE.md y este registro; se actualizó el estado vigente para reflejar el alcance actual (inicio dentro de NEXUS, sin exterior) y la discrepancia sobre el número de bandas.
- **Blender MCP:** addon conectado y compatible; Blender 5.2.3 LTS. Archivo vivo /home/riyo/Documentos/game/FM_NEXUS_V05_level1_v105.blend; Scene, 7.230 objetos, 47 colecciones, 51 materiales, 29 cámaras, 291 luces, EEVEE, escala 1.0. Consulta de bounds de floors, colecciones y cámaras generales. No se cambiaron objetos, colecciones, geometrías, materiales, luces, cámaras, selección ni visibilidad intencionalmente.
- **Cambios arquitectónicos:** ninguno. La auditoría recomienda conservar la zonificación gruesa y no trasladar habitaciones hasta demostrar necesidad. Propone llegada interior en recepción, controles escalonados, suministro interno segregado y circuitos funcionales de laboratorio, medicina, contención e infraestructura.
- **Materiales/texturas/iluminación:** ninguno incorporado. Referencias revisadas como guía de lenguaje visual; originales intactos.
- **Hallazgos principales:** cinco cotas ocupadas observadas (V05, V04, L3, L4, L5); el alcance “Acceso + L1–L5” implicaría seis bandas y requiere decisión. Se enumeran huellas AABB y problemas de Bio–Airlock, Servidores, umbrales L3–L5, núcleo/evacuación y gálibos en los documentos. Las huellas no son claras libres ni pruebas de navegación.
- **Referencias oficiales:** modelos-referencia.png muestra alturas aproximadas: Imitador 2,2–2,5 m; Vigilante 2,5–3,0 m; Coleccionista y Sombra 2,0–2,5 m. No muestra anchos. Hoja de contacto revisada para las 17 PNG; no se modificó fotos-referencia.
- **Problemas/errores:** la consulta MCP de get_scene_info con campos no válidos falló sin cambios; la llamada corregida funcionó. MCP informó bpy.data.is_dirty=True tras una consulta de solo lectura; causa no conocida. No se guardó el archivo. La escena viva apunta a v105, no al v98 solicitado como referencia histórica. v90 y recuperación no se tocaron.
- **Estado de Git:** rama frecuencia-muerta, HEAD 0db132a. Los docs y archivos Blender ya estaban sin seguimiento; se preservan. No commit, reset ni limpieza.
- **Versión Blender guardada:** última versión en disco v105, 3.135.995 bytes (2026-11-01 13:46); ninguna versión nueva guardada por esta auditoría. No sobrescribir v90, recuperación, v98, v104 o v105.
- **Pendiente:** aprobación de la auditoría/estándar; resolver designación y cantidad de bandas; localizar/confirmar oficina y aseos activos; diagnosticar is_dirty antes de cualquier guardado; luego plan de acceso detallado y modificaciones incrementales solo tras aprobación explícita.
- **Siguiente tarea exacta:** revisar los dos documentos de auditoría, confirmar si son cinco bandas totales incluyendo Acceso o seis incluyendo un quinto subnivel, y confirmar el programa de oficina/aseos en Acceso. No iniciar modelado hasta aprobación.


### Ampliación de inventario de escena — 2026-11-01 14:02 COT

- **Fase/zona:** auditoría integral, Acceso V05 y escena completa.
- **Objetivo:** precisar oficina/aseo y documentar cámaras, luces y familias de materiales sin alterar Blender.
- **Consulta realizada:** lista acotada de objetos OFFICE/REST, clases/cantidades de luces, materiales node-based y cámaras; lectura final de ruta y dirty flag.
- **Hallazgo/corrección documental:** oficina NEXUS_V05_OFFICE está activa, con muros, techo, puerta acristalada, escritorio, silla, archivador, monitor, HVAC y señal. Aseo NEXUS_V05_REST existe como compartimento interior parcial de esa zona, con puerta, lavamanos, inodoro, partición, secador y barra. No tienen objeto de piso *_FLOOR independiente; claro neto/accesibilidad aún no están medidos. La edición inicial de auditoría que decía “no localizados” queda corregida; no se borra la entrada previa del log.
- **Escena visual:** 51 materiales con node tree; 29 cámaras, cámara activa NEXUS_V05_CAM_Corridor; 291 luces (230 AREA, 60 POINT, 1 SPOT), 217 visibles y 74 ocultas según hide_get. Varias cámaras V03 y 28 luces V03 están ocultas/históricas. Las luces muestran lenguaje frío, emergencia roja y trabajo cálido; aún no se revisó exposición renderizada de todos los niveles.
- **Archivos actualizados:** docs/NEXUS_ARCHITECTURAL_AUDIT.md, docs/NEXUS_DIMENSIONAL_STANDARD.md, docs/CURRENT_STATE.md. No se reescribieron entradas históricas.
- **Estado Blender:** v105 activo; is_dirty=True sigue reportado por lectura. Ningún cambio en escena ni guardado.
- **Siguiente paso exacto:** revisión y aprobación de auditoría/estándar y decisión sobre número de bandas; modelado sigue en espera.


## 2026-11-01 14:15 COT — Codex — Continuidad de organización arquitectónica NEXUS

- **Fase:** organización arquitectónica integral; fase V05, revisión previa a intervención.
- **Zona:** V05 y enlace NEXUS_LINK_L1; alcance general V05/V04/L3/L4/L5.
- **Objetivo:** retomar desde el checkpoint vivo, aplicar el alcance de cinco bandas confirmado por el usuario y preparar una intervención V05 mínima sin perder datos.
- **Archivos/objetos creados:** no se crearon objetos de Blender. El checkpoint ya existente `FM_NEXUS_V05_level1_v106.blend` se verificó en disco (3.136.030 bytes, 2026-11-01 14:11) y como `bpy.data.filepath` de la instancia MCP. No se sobrescribieron v90, recuperación, v105 ni v105.blend1.
- **Archivos actualizados:** `docs/CURRENT_STATE.md`, `docs/NEXUS_DIMENSIONAL_STANDARD.md` y `docs/NEXUS_ARCHITECTURAL_AUDIT.md`; esta entrada conserva el historial anterior. Se anotó el alcance aprobado de cinco bandas y el comienzo autorizado de la producción en V05.
- **Estado Blender/MCP:** Blender 5.2.3 LTS; addon MCP 1.8, protocolo 15, conectado; escena `Scene`, 7.230 objetos y 47 colecciones. `bpy.data.is_dirty=True` continúa tras el guardado exitoso que produjo v106. La inspección comparativa anterior no halló diferencias geométricas principales entre v105/v106; el origen del dirty flag no está completamente confirmado. La selección activa varía en consultas MCP, por lo que no se toma como evidencia de cambio arquitectónico.
- **Hallazgos arquitectónicos:** el corredor V05 mide 44×3,4 m por bounds de piso y conecta con `NEXUS_LINK_L1` en el extremo este. Recepción, seguridad y control de acceso son salas contiguas con puertas al mismo corredor; no existe un umbral físico de control que segregue el tránsito al núcleo. La geometría de sala y puertas queda preservada. El enlace al núcleo forma un giro desde el corredor longitudinal hacia el norte; sus cotas y puertas requieren revisión visual completa.
- **Cambios arquitectónicos:** ninguno todavía. No se modificaron mallas, materiales, luces, cámaras ni colecciones.
- **Referencias:** AGENTS.md y documentación de continuidad revisados; el estándar dimensional marca las huellas como AABB, no como claros. No se modificaron referencias de `fotos-referencia/`.
- **Problemas y solución:** una actualización documental intentada con contexto obsoleto no aplicó; no alteró archivos. Se aplicaron cambios puntuales sobre textos coincidentes. La escena se mantiene sin cambios geométricos.
- **Estado de Git:** sin commits, resets ni limpieza. Documentación, versiones Blender y scripts no seguidos permanecen preservados.
- **Versión Blender:** v106 es el checkpoint activo; no hubo un nuevo guardado en este bloque.
- **Pendiente:** inspección MCP en contexto de la transición V05→link y de los elementos del puesto de control; verificar paso, jerarquía de umbrales, ruta de servicio y evacuación. Resolver el origen de `is_dirty=True` antes del próximo guardado. Después realizar únicamente el bloque mínimo V05, crear un nuevo incremento y validar visualmente.
- **Siguiente paso exacto:** vista MCP orientada al corredor V05, las puertas existentes de seguridad/control y el enlace `NEXUS_LINK_L1`, seguida de medición de claros y revisión de interferencias; aún no añadir geometría a ciegas.


## 2026-11-01 14:19 COT — Codex — Umbral de acceso restringido V05

- **Fase:** organización arquitectónica, V05 (primer bloque de producción).
- **Zona/departamento:** enlace entre el corredor de acceso V05 y el núcleo vertical, NEXUS_LINK_L1.
- **Objetivo:** hacer legible la transición hacia circulación restringida sin mover habitaciones ni estrechar de forma importante el paso existente.
- **Escena base:** /home/riyo/Documentos/game/FM_NEXUS_V05_level1_v106.blend, comprobada como activa antes de editar. v106 se conserva intacta; v105, v90 y la recuperación también quedan intactas.
- **Objetos/colecciones creados:** ocho objetos bajo la colección existente NEXUS_VTOWER: NEXUS_LINK_L1_RESTRICTED_GATE_HOUSING, ROLLER, GUIDE_W, GUIDE_E, SIGN_PLATE, SIGN_TEXT, SIGN_BRACKET_L y SIGN_BRACKET_R.
- **Objetos/colecciones modificados:** ninguno de los preexistentes. Mallas nuevas asignadas a materiales existentes NEXUS_Painted_Metal, NEXUS_Steel y NEXUS_SignPlate; texto usa NEXUS_SignText. Sin materiales, texturas, luces ni cámaras nuevas.
- **Cambio arquitectónico:** umbral de cierre enrollable representado en posición recogida, en el giro de entrada al enlace norte. La señal naranja “ACCESO RESTRINGIDO” identifica el cambio de zona. No se modeló hoja/paño desplegado, interacción ni puerta operable. Claro abierto estimado: 2,96 m de ancho por 3,59 m de alto, calculado contra los límites de piso/techo existentes; no certifica paso de criaturas porque su anchura no está acotada.
- **Comprobación visual:** vistas MCP del texto/placa y del conjunto en contexto; la placa se ve legible en vista frontal cercana. La vista de todo el enlace queda parcialmente oscurecida por las superficies de techo/muros; revisar la lectura desde el recorrido completo al finalizar V05.
- **QA de mallas:** Blender Asset QA, perfil game, eps=0,005, tol=0,01: pass=True, cero errores. Siete mallas, 164 triángulos; UVMap presente en cada una, UVs fuera de rango 0 %, caras UV de área cero 0; sin z-fighting, partes flotantes ni normales invertidas. Avisos aceptados: rodillo encerrado dentro de su carcasa (componente interno intencional), juntas cara a cara entre carcasa y guías (sin z-fighting), y z inferior −5,65 m correspondiente a la elevación real de la planta.
- **Problema y solución:** primera QA señaló UV ausentes y placa flotante. Se añadieron UVs, se trianguló el cierre del rodillo y se incorporaron dos soportes con solape físico; la reejecución pasó.
- **Estado is_dirty:** v106 reportó True al cargar. Prueba controlada mostró False al iniciar Blender limpio y True inmediatamente después de abrir v106, incluso con --factory-startup; por tanto ese True se vincula al ciclo de carga y no demuestra por sí solo una edición no guardada. Guardado de v107 devolvió FINISHED; la verificación posterior de MCP confirmó filepath v107 y is_dirty=False.
- **Versión guardada:** /home/riyo/Documentos/game/FM_NEXUS_V05_level1_v107.blend, 3.145.011 bytes, 7.238 objetos/47 colecciones. v106 permanece como checkpoint preintervención. No se sobrescribieron históricos.
- **Estado de Git:** sin commit, reset, limpieza ni eliminación. v106/v107 y documentos continúan sin seguimiento según el estado actual.
- **Pendientes:** verificar la ruta de servicio del almacén y su relación con mantenimiento; medir circulación y claros de NEXUS_V05_OFFICE/REST; comprobar desde el corredor la secuencia y visibilidad de recepción, seguridad, control y umbral; después revisar el núcleo vertical. No declarar V05 terminado aún.
- **Siguiente paso exacto:** inspeccionar con MCP los objetos de la puerta de servicio del almacén y sus conexiones físicas con mantenimiento/corredor; registrar medidas y decidir si existe ruta segregada sin alterar la geometría existente.


## 2026-11-01 19:52 COT — OpenCode — Assets locales y corrección de contactos V05

- **Fase:** organización arquitectónica, V05; integración de la biblioteca local `assets/` y revisión del servicio almacén–mantenimiento.
- **Zona/departamento:** almacén y mantenimiento de V05.
- **Objetivo:** continuar desde v107, revisar los recursos locales y usar modelos adecuados para mejorar la lectura de las salas sin alterar la arquitectura.
- **Escena base:** `FM_NEXUS_V05_level1_v107.blend`, conservado intacto. Se creó `v108`, pero resultó defectuoso por la deformación de la puerta del cuadro eléctrico al evaluar su modificador Armature sin la armadura; no debe usarse.
- **Assets incorporados:** ocho modelos Poly Haven en 26 objetos bajo la colección `NEXUS_ASSET_V05`; carro industrial, caja plástica, caja de cartón, barril, caja de herramientas, luminaria de jaula, cuadro eléctrico y extintor. Se documentó el inventario en `docs/NEXUS_ASSET_INVENTORY.md`.
- **Correcciones:** la caja de cartón se movió de (2,95,−1,98), donde atravesaba la pared norte, a (2,95,−8,20); el cuadro eléctrico se ajustó a y −9,55, a 1 cm de la pared sur. Se eliminaron las cámaras temporales de revisión.
- **Versiones:** `FM_NEXUS_V05_level1_v109.blend` (6.565.572 bytes) conserva la primera integración; `FM_NEXUS_V05_level1_v110.blend` (6.566.128 bytes, 7.270 objetos, 48 colecciones, 72 materiales, 29 cámaras, 292 luces, 26 assets) es el checkpoint activo. Cámara activa `NEXUS_V05_CAM_Corridor`; verificación MCP: `is_dirty=False`, sin objetos `TMP_`.
- **Revisión visual:** almacén y mantenimiento renderizados con `look`; los assets se integran sin dominar la escena. La puerta de carga este se confirmó decorativa: no hay vano real y el muro macizo está detrás de las lamas.
- **Propuesta:** se documentó `docs/NEXUS_V05_SERVICE_CONNECTOR_PROPOSAL.md`: paso de 1,60 m en el almacén, pasillo de 1,72 m con piso y techo nuevos, y paso de 1,20 m a mantenimiento; método no destructivo con muros segmentados y mallas originales ocultas. No se ha cortado ningún muro ni añadido geometría estructural.
- **Pendiente:** aprobar la propuesta del conector, ejecutarla en v111 y validar con rayos/cápsula; después medir oficina/aseo.
- **Estado de Git:** sin commit, reset ni limpieza. v109, v110, los scripts y los documentos quedan sin seguimiento, igual que los recursos preexistentes.

## 2026-11-01 20:35 COT — OpenCode — Conector de servicio almacén–mantenimiento V05

- **Fase:** organización arquitectónica, V05; ejecución del conector de servicio aprobado.
- **Zona/departamento:** almacén, franja de servicio y mantenimiento de V05.
- **Objetivo:** convertir la franja sin piso entre almacén y mantenimiento en un paso de servicio real, protegido y no destructivo, sin alterar la fachada de la puerta de carga.
- **Aprobación:** el usuario aprobó la propuesta de vanos de 1,60 m en almacén y 1,20 m en mantenimiento.
- **Método no destructivo:** se ocultaron en `NEXUS_V05_SERVICE_CONN_HIST` (10 objetos) los muros originales este/oeste, el tirador y las siete lamas de la puerta de carga. Se conservaron visibles el marco y la fachada. Se construyeron muros segmentados de reemplazo, piso, techo, cierre sur, umbrales y marcos en `NEXUS_V05_SERVICE_CONN`.
- **Geometría:** vano almacén y −6,60..−5,00; vano mantenimiento y −4,70..−3,50; altura libre 2,80 m (z −5,65..−2,85). Pasillo x 4,0..6,0, y −9,7..−1,7. Ancho libre ≈1,68 m entre zócalos; vanos entre jambas 1,46 m y 1,06 m.
- **Mobiliario:** banco/pegboard/herramientas desplazados −0,25 m en Y (y −8,55..−4,75); armario y LEDs +0,15 m en Y (y −3,45..−2,35); botiquín reubicado en (6,17,−5,95,−4,52), sobre el banco. Quedan 5 cm de holgura respecto a los vanos.
- **Acabado:** zócalos metálicos verde oscuro partidos alrededor de los vanos, franjas de peligro, carteles “MUELLE”, “MANTENIMIENTO”, “SERVICIO // MUELLE”, “ALMACEN // SERVICIO”, flechas interiores, bandeja de cables, drenaje, luminarias de servicio y cámara de revisión.
- **Auditoría:** rayos bajos a z −5,55 desde almacén al pasillo, pasillo a mantenimiento y diagonal almacén–mantenimiento: CLEAR. Verticales en cuatro puntos impactan `NEXUS_V05_SERVICE_CONN_FLOOR` a z −5,65. El límite superior real es la bandeja de cables a z −1,797.
- **Corrección:** los zócalos continuos iniciales cruzaban los vanos y creaban un bordillo de 0,18 m. Se sustituyeron por cuatro tramos `TRIM_W_S`, `TRIM_W_N`, `TRIM_E_S` y `TRIM_E_N`, sin obstáculo en los pasos.
- **Gálibo:** jugador Ø0,76 m y Vigilante Ø0,80 m caben por los vanos. El Vigilante de 3,0 m no pasa por altura; es una restricción intencional, no un defecto de escala.
- **Versiones:** v111 (conector base, 6.562.952 bytes, 7.376 objetos), v112 (pulido intermedio, 6.582.834 bytes, 7.408 objetos), v113 (pulido con luces finales, 6.585.166 bytes, 7.408 objetos) y **v114** (zócalos corregidos, **6.461.329 bytes, 7.410 objetos, 50 colecciones, 140 objetos de conector, 10 históricos, 26 assets**). v110, v109 y v107 se conservan; v108 no debe usarse.
- **Estado de Blender:** v114 activo, cámara `NEXUS_V05_CAM_Corridor`, `is_dirty=False`, sin objetos `TMP_`. `bpy.data.cameras` conserva tres datablocks huérfanos de cámaras temporales, sin objetos en escena; no se purgaron.
- **Revisión visual:** el pasillo se lee como espacio de servicio oscuro con zócalo verde, carteles y flechas; las puertas laterales y la fachada de carga son reconocibles. El ruido del techo en los renders es EEVEE, no geometría.
- **Limitaciones:** las puertas son geometría estática sin interacción; no se ha probado con cápsula en Godot; el arte sigue siendo provisional; no se exportó a Godot.
- **Documentación:** `docs/CURRENT_STATE.md` apunta a v114; `docs/NEXUS_V05_SERVICE_CONNECTOR_PROPOSAL.md` está marcado como ejecutado y auditado; este registro recoge el proceso. `docs/fm_nexus_nivel2.md` conserva el tamaño antiguo de v90 y queda pendiente de una revisión documental posterior.
- **Estado de Git:** sin commit, reset ni limpieza. Los .blend, scripts y documentos nuevos siguen sin seguimiento.
- **Siguiente paso exacto:** medir el claro, giro y ventilación de `NEXUS_V05_OFFICE/REST`; después revisar desde el corredor la secuencia recepción–seguridad–control–umbral restringido. No iniciar V04 hasta cerrar V05.

## 2026-11-01 21:30 COT — OpenCode — Pase de assets del Nivel 1 (V05)

- **Fase:** organización arquitectónica, V05; integración de la biblioteca local `assets/` en el Nivel 1.
- **Zona/departamento:** recepción, oficina, aseo, vestuarios, seguridad, control de acceso, almacén, mantenimiento, corredor y accesorios.
- **Objetivo:** reemplazar props blocky por modelos locales adecuados, sin alterar la arquitectura ni otros niveles, y revisar la biblioteca ampliada por el usuario.
- **Biblioteca revisada:** 1.147 archivos; 138 modelos repartidos en infraestructura, laboratorio, mobiliario, objetos narrativos, puertas/ventanas, rocas/escombros y vegetación. Se midieron 68 candidatos con Blender headless antes de elegir. No se modificaron los archivos originales.
- **Primera pasada (v115–v117):** 19 modelos en 40 instancias, 40 roots, 90 mallas y 130 objetos en `NEXUS_ASSET_L1`. Se ocultaron los originales blocky con `hide_render`, `hide_viewport` y `replaced_by`, sin borrarlos. Se colocaron sillas, carrito de café, relojes, grapadora, portapapeles, portátil, señales de suelo mojado, cubo, guantes, sombrero, bolsa, barriles, cajas, contenedores, carro de herramientas, alarmas y lámparas de pared. La corrección de la vegetación del aseo quedó incluida.
- **Segunda pasada (v118):** tres copias adicionales de `metal_office_desk_2k` para dos mesas de seguridad y una de control; se ocultaron `SEC_DESK*` y `ACC_CONSOLE*`; monitores elevados 0,078 m; objetos de consola bajados 0,012 m; sillas de control alineadas a x 12,25 y 13,75.
- **Cámaras:** recepción `(-8,30, 3,20, -4,25)` → `(-14,20, 8,20, -4,35)`, lens 20; aseo `(-7,95, 4,32, -4,05)` → `(-4,95, 2,65, -4,35)`, lens 18; corredor `(-20,50, 0,00, -4,15)` → `(0,00, 0,00, -4,15)`, lens 20.
- **Mediciones de oficina/aseo:** oficina ≈10,9 m², radio libre ≈0,73 m; aseo ≈10,3 m², radio libre ≈1,05 m; puertas de 0,90 m y 2,08 m. El jugador de Ø0,76 m cabe; la oficina es justa. El aseo no tiene extracción/HVAC.
- **Auditoría:** 0 solapes AABB > 0,015 m³ en los 37 roots iniciales; 0 solapes > 0,01 m³ en las 27 mallas nuevas de escritorio. Se corrigieron contactos de grapadora, sombrero, caja del palé, contenedor del almacén y señales. La auditoría global final (40 roots contra 1.229 mallas de V05_PROPS, V05_STORY, NEXUS_ASSET_V05 y NEXUS_V05_SERVICE_CONN) dio **0 solapes > 0,01 m³**; los apoyos revisados coinciden con suelo, palé, banco o pared, sin flotantes.
- **Renders:** recepción, oficina, seguridad, control, vestuarios, almacén, mantenimiento, corredor y aseo. Composición legible; el aseo queda condicionado por su tabique de privacidad. No se detectaron penetraciones nuevas.
- **Rendimiento:** v118 tiene 7.534 objetos, 51 colecciones, 133 materiales, 30 cámaras y 295 luces. Triángulos visibles: 673.792. Es alto para la GTX 1650 Ti; hace falta LOD/optimización antes de exportar. La medición intermedia de 506.468 quedó descartada por no contar todas las instancias compartidas.
- **Versiones:** v115 (10.443.910 B, primera pasada), v116 (10.500.697 B, cámaras/contactos), v117 (10.562.758 B, contenedor del almacén) y **v118 (10.584.412 B, versión activa)**. v114 y anteriores se conservan; v108 sigue defectuoso.
- **Estado de Blender:** cámara activa guardada `NEXUS_V05_CAM_Corridor`; `is_dirty=False`; sin objetos `TMP_`. Las cámaras de los renders posteriores cambiaron solo en memoria.
- **Scripts:** `blender_concept/assets_level1.py` (OUT v117) y `blender_concept/assets_level1_desks.py` (OUT v118); ambos compilan con `python3 -m py_compile`. No reejecutar sin subir `OUT` y revisar duplicados.
- **Documentación:** `docs/CURRENT_STATE.md` y `docs/NEXUS_ASSET_INVENTORY.md` actualizados a v118; este registro recoge el proceso.
- **Limitaciones:** el mostrador de recepción, la mesa de centro, el banco, las taquillas y las estanterías industriales siguen siendo blocky; las puertas son estáticas; no hay extracción en el aseo; el arte es provisional; no se exportó a Godot.
- **Estado de Git:** sin commit, reset ni limpieza. Los .blend, scripts y documentos siguen sin seguimiento.
- **Siguiente paso exacto:** medir el coste de los 673.792 triángulos y decidir LOD/optimización; después revisar la secuencia recepción–seguridad–control–umbral y el núcleo vertical.

## 2026-11-01 22:55 COT — OpenCode — Pase de abandono, texturas y HDRI del Nivel 1 (V05)

- **Fase:** organización arquitectónica, V05; abandono, desorden, materiales y ambiente del Nivel 1.
- **Zona/departamento:** recepción, oficina, aseo, seguridad, control de acceso, vestuarios, almacén, mantenimiento, corredor, conector y link L1.
- **Objetivo:** continuar desde v118 aplicando la petición del usuario: tener en cuenta las alturas de las criaturas y la jugabilidad, mostrar un complejo abandonado tras un desastre, evitar assets de épocas pasadas y usar texturas/HDRI locales. Sin tocar otros niveles.
- **Mediciones de escala:** las puertas principales de V05 (1,62×3,12 m, paso libre ≈3,07 m) permiten el paso de todas las criaturas, incluido el Vigilante de 3,0 m. Las puertas de oficina/aseo (0,90×2,08 m) excluyen a las criaturas de 2,2–2,5 m; solo una de 2,0 m pasaría justo. El conector de servicio mantiene 2,80 m de altura y excluye intencionalmente al Vigilante. Queda como propuesta pendiente subir las puertas de oficina/aseo a ≈2,60 m, sin ejecutarla todavía.
- **Suelos y mundo:** `NEXUS_V05_MAT_Floor_Worn` con `worn_concrete_floor_2k`, mapeo Object X/Y escala 0.30, HueSaturation saturación 0.35 y valor 0.16, normal map 0.75. Aplicado a recepción, corredor, seguridad, control, vestuarios, almacén, mantenimiento, conector y link L1. HDRI `abandoned_workshop_2k` en `World`, fuerza 0.02, conservando `Principled Volume`; AgX con exposición 1.5.
- **Materiales nuevos:** `NEXUS_L1_MAT_Blood`, `NEXUS_L1_MAT_Blood_Dark` y `NEXUS_L1_MAT_Mirror` (asignado al espejo del aseo). Los muros del corredor se mantuvieron con `NEXUS_Concrete`; la geometría antigua `CORRIDOR_L-1_*` de `02_CIRCULATION` sigue oculta y no se tocó.
- **Retirada de época pasada:** se ocultaron la cafetera exprés `CoffeeCart_01`, el portátil clásico y el cubo `cleaner_tin`; se marcaron con `replaced_by`. Se creó una estación de café moderna duplicando el escritorio metálico, con cafetera, pantalla, surtidor, bandeja, vasos y papelera.
- **Pase de desastre:** script `blender_concept/level1_abandoned_pass.py`, prefijo `NEXUS_L1_DIS_`, colección `NEXUS_L1_DISASTER`, `FLOOR=-5.65`. Añade 226 objetos: papeles, sangre, agua, aceite, escombros, cristales, sillas caídas en recepción/seguridad/control/corredor/oficina, barril y carro volcados, cajas derramadas, bolsas, señales caídas, monitores rotos, papelera, huellas, cable, panel, tubería, extractor del aseo y mancha de sangre sobre el escritorio de oficina.
- **Correcciones de contacto:** silla de seguridad reubicada en (5,0, 4,4) para que aparezca en la cámara y no quede bajo el escritorio; monitor de recepción girado y apoyado plano en el suelo; papelera de recepción movida a (-9,1, 4,0) para no rozar la pata del banco; extractor del aseo pegado a la pared este; huella de mano y sangre de oficina en pared y escritorio. La silla de recepción y el monitor siguen formando parte de un grupo de desorden; el monitor comparte volumen con el borde de la silla caída, sin penetración visible relevante.
- **Auditoría:** 0 objetos de desastre bajo el suelo. 34 objetos elevados, todos ensamblajes intencionales (sobre escritorio, pared, techo, cristal o cable). No se detectaron objetos fuera del perímetro útil: los cuatro situados en x≈23–24 están sobre `NEXUS_LINK_L1_FLOOR` (x 22–25), no en el vacío. Los objetos de desastre no bloquean las puertas principales; la silla del corredor deja paso a ambos lados.
- **Renders revisados:** recepción (suelo texturizado, silla caída, papeles, sangre, estación de café), oficina (escritorio, silla caída, huella y sangre), seguridad (escritorios, monitores, silla caída visible a la derecha), además de los renders previos de control, vestuarios, almacén, mantenimiento, aseo, corredor y conector. El ruido moteado del techo es EEVEE, no geometría.
- **Rendimiento:** v124 tiene 7.760 objetos, 52 colecciones, 137 materiales, 30 cámaras, 295 luces y **750.632 triángulos visibles**. Es alto para la GTX 1650 Ti; hace falta LOD/optimización antes de exportar.
- **Versiones:** v119 (10.655.250 B, 160 objetos de desastre), v120 (incremento intermedio), v121 (10.706.490 B, 221 objetos), v122/v123 (incrementos del mismo pase) y **v124 (10.702.915 B, versión activa, 226 objetos)**. v118 y anteriores se conservan; v108 sigue siendo defectuoso.
- **Estado de Blender:** v124 guardado con cámara `NEXUS_V05_CAM_Corridor`, sin objetos `TMP_`; la recarga headless confirma 7.760 objetos, 226 de desastre y cámara Corridor. `is_dirty=False` al guardar.
- **Scripts:** `level1_abandoned_pass.py` apunta a v124 y compila; `assets_level1.py` (v117) y `assets_level1_desks.py` (v118) se conservan. No reejecutar sin subir `OUT` y revisar duplicados.
- **Limitaciones:** el arte sigue siendo blocky/provisional; las puertas son geometría estática; el aseo tiene extractor visual pero no HVAC funcional; no se ha probado con cápsula en Godot; no se exportó a Godot.
- **Documentación:** `docs/CURRENT_STATE.md` y `docs/NEXUS_ASSET_INVENTORY.md` se actualizan a v124; este registro recoge el proceso. `docs/fm_nexus_nivel2.md` sigue con el tamaño antiguo de v90 y queda pendiente de revisión documental.
- **Estado de Git:** sin commit, reset ni limpieza. Los .blend, scripts y documentos siguen sin seguimiento.
- **Siguiente paso exacto:** decidir LOD/optimización para los 750.632 triángulos, revisar la secuencia recepción–seguridad–control–umbral y el núcleo vertical, y preparar la propuesta de puertas de oficina/aseo a ≈2,60 m sin ejecutarla.

## 2026-11-01 23:05 COT — OpenCode — Handoff del Nivel 1 para Codex

- **Objetivo de esta entrada:** dejar un punto de continuación inequívoco después del pase de abandono. No sustituye las entradas anteriores; las resume y marca el estado real que debe comprobar Codex antes de tocar nada.
- **Archivo activo:** `/home/riyo/Documentos/game/FM_NEXUS_V05_level1_v124.blend`.
- **Estado comprobado de v124:** 10.702.915 bytes; 7.760 objetos; 52 colecciones; 137 materiales; 30 cámaras; 295 luces; 226 objetos `NEXUS_L1_DIS_`; 130 objetos en `NEXUS_ASSET_L1`; 26 en `NEXUS_ASSET_V05`; 140 en `NEXUS_V05_SERVICE_CONN`; 10 históricos; cámara activa `NEXUS_V05_CAM_Corridor`; sin objetos `TMP_`; 750.632 triángulos visibles en 5.795 mallas.
- **Qué cambió respecto a v118:** se aplicó `NEXUS_V05_MAT_Floor_Worn` a 9 suelos; HDRI `abandoned_workshop_2k` a fuerza 0.02; materiales de sangre y espejo; se ocultaron tres props vintage; se creó una estación de café moderna; se añadieron 226 objetos de desastre (sillas, papeles, sangre, agua/aceite, escombros, cristales, barriles/carros/cajas volcados, monitores rotos, huellas, cable, panel, tubería, extractor y señalización); se corrigieron silla de seguridad, monitor de recepción y papelera.
- **Scripts y reproducibilidad:**
  - `blender_concept/level1_abandoned_pass.py`: OUT v124; compila. Reejecutar solo subiendo OUT a **v125**. El script limpia y recrea la colección `NEXUS_L1_DISASTER` y los objetos `NEXUS_L1_DIS_`; es la vía reproducible del pase de abandono.
  - `blender_concept/assets_level1.py`: OUT v117; primera pasada de assets del Nivel 1.
  - `blender_concept/assets_level1_desks.py`: OUT v118; escritorios de seguridad/control.
  - `blender_concept/assets_v05.py`: OUT v109; almacén/mantenimiento.
  - No reejecutar ningún script sobre v124 sin subir `OUT` y revisar que no se dupliquen colecciones, roots o mallas compartidas.
- **Qué está probado:** ejecución por MCP; guardado y recarga headless; renders de recepción, oficina y seguridad en v124; renders previos de control, vestuarios, almacén, mantenimiento, aseo, corredor y conector; auditoría AABB global de los 40 roots contra 1.229 mallas con 0 solapes > 0,01 m³; 0 objetos de desastre bajo el suelo; 34 elevados intencionales; 4 objetos sobre `NEXUS_LINK_L1_FLOOR`.
- **Limitaciones reales:** el arte sigue siendo blocky/provisional; las puertas son geometría estática; el aseo tiene extractor visual pero no HVAC funcional; no hay prueba con cápsula en Godot; no se exportó a Godot. El solape monitor/silla de recepción es ≈0,00228 m³ y no produce penetración visual relevante; la sangre del escritorio toca ligeramente el teléfono.
- **Orden de continuación recomendado:**
  1. **LOD/optimización:** medir el coste de los 750.632 triángulos y decidir LOD, decimación o reducción de instancias antes de exportar. Priorizar assets pesados: carro industrial, luminaria de jaula, cuadro eléctrico, cajas, escritorios y extintor. No borrar originales ni assets de la biblioteca.
  2. **Secuencia recepción–seguridad–control–umbral:** revisar desde el corredor la legibilidad del acceso restringido y el recorrido con cápsula/rayos. No iniciar V04 hasta cerrar esta revisión de V05.
  3. **Puertas de oficina/aseo:** propuesta pendiente de autorización para subirlas de 0,90×2,08 m a ≈2,60 m. Permitiría Imitador/Coleccionista/Sombra (2,0–2,5 m) y mantendría fuera al Vigilante (3,0 m). Requiere ajustar marco, dintel y muro; no ejecutar sin aprobación (AGENTS §47.10).
  4. **HVAC del aseo:** si se quiere pasar de extractor visual a sistema funcional, diseñarlo sin tocar la estructura aprobada.
  5. **Pendientes de otros niveles:** Bio–Airlock, discontinuidad de piso de Servidores y umbrales L3–L5. No tocarlos en esta fase.
- **Advertencias de entorno:** `bpy.ops.render.render` por MCP se cuelga; usar `tools["blender-mcp"].look` con `mode:"camera"`, `shading:"rendered"` y `max_size:640`. Los scripts largos por MCP pueden devolver `Communication error with Blender: No data received` aunque terminen; verificar en una segunda petición. `bpy.data.is_dirty` no es fiable al abrir un `.blend`. No usar v108 (defectuoso) ni sobrescribir v90.
- **Documentación:** `docs/CURRENT_STATE.md` y `docs/NEXUS_ASSET_INVENTORY.md` están actualizados a v124; `docs/WORKLOG.md` contiene esta entrada. `docs/fm_nexus_nivel2.md` sigue con el tamaño antiguo de v90 y queda pendiente de revisión documental.
- **Git:** sin commit, reset ni limpieza; los `.blend`, scripts y documentos siguen sin seguimiento.
- **Primera acción que debe hacer Codex:** abrir v124, confirmar los recuentos anteriores y decidir si empieza por LOD o por la revisión del corredor. No debe reconstruir ni reinterpretar el pase de abandono como arte final.

## 2026-11-02 14:26 COT — OpenCode — División modular del complejo NEXUS

- **Decisión del usuario:** conservar v125 como respaldo y dividir el trabajo en `nexus/nivel_01`, `nivel_02`, `nivel_03`, `nivel_04`, `nivel_05`, `nucleo`, `compartido` y `master`. Mantener assets comunes sin duplicarlos y editar cada nivel por separado.
- **Fuente intacta:** `/home/riyo/Documentos/game/FM_NEXUS_V05_level1_v125.blend`, 12.093.615 bytes; 7.828 objetos en escena y 7.849 datablocks de objeto. No se guardó ni sobrescribió durante esta tarea.
- **Script de generación:** `blender_concept/split_nexus_levels.py`; compila y se ejecutó con Blender 5.2.3 headless. Clasifica colecciones completas y objetos legacy por cotas, conserva históricos y cutters, crea archivos locales y enlaza el máster. Nivel 1 enlaza `NEXUS_SHARED_ASSETS` en vez de copiarlo.
- **Archivos generados:**
  - L1 `nexus/nivel_01/NEXUS_L1_V05.blend`: 2.154 objetos, 2.316.454 bytes.
  - L2 `nexus/nivel_02/NEXUS_L2_V04.blend`: 1.861 objetos, 1.029.129 bytes.
  - L3 `nexus/nivel_03/NEXUS_L3_MEDICAL.blend`: 620 objetos, 450.600 bytes.
  - L4 `nexus/nivel_04/NEXUS_L4_CONTAINMENT.blend`: 621 objetos, 455.950 bytes.
  - L5 `nexus/nivel_05/NEXUS_L5_INFRA.blend`: 817 objetos, 571.620 bytes.
  - Núcleo `nexus/nucleo/NEXUS_CORE.blend`: 500 objetos, 415.980 bytes.
  - Assets `nexus/compartido/NEXUS_SHARED_ASSETS.blend`: 224 objetos, 8.603.846 bytes.
  - Histórico `nexus/compartido/NEXUS_HISTORICAL.blend`: 1.255 objetos, 720.993 bytes.
  - Máster `nexus/master/NEXUS_MASTER.blend`: 7.828 objetos, 398.478 bytes.
- **Limpieza real de los archivos:** la primera generación conservaba colecciones/datablocks ajenos fuera de escena. Se corrigió el script para purgar recursivamente huérfanos solo en los archivos nuevos. Comprobación posterior: cada archivo tiene el mismo número de datablocks de objeto que objetos en su escena; L3 quedó en 620/620, no 620/7.827.
- **Bibliotecas:** el máster contiene ocho rutas relativas: cinco niveles, núcleo, histórico y assets compartidos. Nivel 1 tiene `//../compartido/NEXUS_SHARED_ASSETS.blend`. No falta ninguna biblioteca ni imagen por ruta.
- **Verificación:** `blender_concept/verify_nexus_split.py` comparó v125 con el máster: mismos 7.828 nombres, tipos, matrices y visibilidad; 761.932 triángulos en ambos; cámara `NEXUS_V05_CAM_Corridor`; cero objetos ausentes/extra y cero bibliotecas ausentes. Resultados en `nexus/verification.json`; inventario técnico en `nexus/manifest.json`.
- **Revisión visual:** render headless del corredor del máster completado a 640×360 y examinado. Conserva el desorden, los materiales y la iluminación de la fuente.
- **Defecto previo detectado:** las texturas `industrial_wall_lamp_glass_rough_1k.png` e `industrial_wall_lamp_glass_alpha_1k.png` dentro de `assets/Modelos 3D/.../industrial_wall_lamp_1k.blend/textures/` contienen JSON `internal_error/status 500` de 81 bytes, no PNG. Blender informa `unknown file-format` y fallo de textura GPU. No se modificaron los originales; reparación pendiente y separada de la división.
- **Documentación:** `nexus/README.md` explica apertura/edición; `docs/CURRENT_STATE.md` y `docs/NEXUS_ASSET_INVENTORY.md` apuntan a la estructura modular. Esta entrada no elimina ningún registro anterior.
- **Siguiente paso:** abrir el máster para revisar el complejo y editar cada nivel en su archivo. Continuar Nivel 1 con LOD/optimización y revisión de circulación; no reejecutar los scripts monolíticos antiguos sobre los archivos modulares sin adaptarlos. No exportar a Godot.

## 2026-11-02 20:36 COT — Codebuff — Recepción del Nivel 1: materiales, servicios, mostrador, luz y LOD

- **Decisión del usuario:** centrarse en la recepción del Nivel 1 hasta dejarla terminada, optimizada, con todo lo necesario y texturas.
- **Zona:** `NEXUS_V05_RECEPCION` (16×10×6 m), incluyendo el mostrador, el zócalo perimetral, el techo y los decals de desastre de la sala. No se tocaron otras salas ni se movieron muros, puertas o recintos.
- **Diagnóstico previo:** 428 objetos visibles y **116.785 triángulos** en el volumen de la recepción. El patrón punteado del techo se identificó como *shadow acne*: `NEXUS_V05_RECEPCION_LIGHT` (área 900 W, 3,0×0,4 m) estaba a 6 cm del techo con sombras activas; `NEXUS_V05_REC_FILL.001` aportaba 1.100 W con sombras desactivadas y aplanaba la sala.
- **Materiales nuevos (solo recepción):** `NEXUS_V05_MAT_Rec_Wall` (`worn_plaster_wall_2k`, escala 0,30, saturación 0,45, velo de suciedad por altura), `NEXUS_V05_MAT_Rec_Ceiling` (`dirty_concrete_2k`, 0,20), `NEXUS_V05_MAT_Rec_Floor` (`worn_concrete_floor_2k` + `dirt_2k` como suciedad), `NEXUS_V05_MAT_Rec_Wainscot` (`factory_wall_2k`, chapa verde corrugada) y `NEXUS_L1_MAT_Paper`. Todos usan Texture Coordinate Object y texturas PBR de `assets/texturas/`.
- **Decals corregidos:** `NEXUS_L1_MAT_Blood`, `NEXUS_L1_MAT_Blood_Dark` y `NEXUS_L1_MAT_Handprint` se reconstruyeron con `assets/art/fm/blood_splat.png` y `handprint.png` (alfa y UV planar por objeto). Los discos planos de color pasaron a manchas reales. 60 decals reprocesados; los papeles del volumen cambiaron de `NEXUS_OffWhite` (hormigón) a papel.
- **Geometría añadida (colección `NEXUS_V05_REC_PASS126`, 159 objetos, 3.916 triángulos):** conducto principal 15,3×1,25×0,72 con bridas y colgadores, ramal secundario, cuatro difusores, bandeja de cables con rastreles y mazos, banda de rociadores con bajantes y deflectores, tres bajantes verticales, seis downlights empotrados (dos fundidos), tres detectores de humo, carcasas de emergencia y rebordes. Mostrador reconstruido (tapa 4,36×1,32, frente verde con tres rejuntas, zócalo retranqueado, trasera, laterales, cajonera y bandeja de cables) y zócalos perimetrales partidos por la puerta. Los originales blocky se ocultaron con `replaced_by`.
- **Iluminación:** seis focos empotrados con sombra (cuatro activos 850 W, dos fundidos), práctico del mostrador, dos lámparas colgantes, dos rebotes suaves al techo, luz de rótulo y dos lámparas de emergencia rojas dentro de carcasa. La luz de techo bajó a 90 W sin sombra y el relleno a 120 W, lo que elimina el *shadow acne* y devuelve contraste.
- **Optimización (LOD1):** colección `NEXUS_V05_REC_LOD1` con 5 copias decimadas de objetos locales (3 sillas + bolsa + escritorio de café): **5.072→1.200**, 4.482→1.100, 4.186→1.100. Resultado medido: **116.785 → 98.701 triángulos visibles (−15,5 %)**.
- **Limitación importante:** los 18 assets enlazados de `NEXUS_SHARED_ASSETS` (73.089 triángulos: 5 sillas `SchoolChair_01`, 2 portapapeles de 6.176, 2 relojes de 3.380, escritorio, monitores, grapadora, lámpara de tubería) **no se pueden decimar ni ocultar por script**: viven dentro de la colección enlazada `NEXUS_ASSET_L1`, `hide_render`/`replaced_by` no persisten al guardar y `obj.make_local()` no los convierte. Se descartó decimarlos para no duplicar geometría visible. Optimizarlos requiere decisión aparte: editar `nexus/compartido/NEXUS_SHARED_ASSETS.blend` (afecta a todos los niveles) u obtener overrides de biblioteca.
- **Cámaras y renders:** `docs/fm_recepcion_v126.png` (cámara oficial `NEXUS_V05_CAM_Recepcion`) y `docs/fm_recepcion_v126_wide.png` (vista amplia desde la esquina noroeste).
- **Incidente de sesión:** la primera ejecución no se guardó porque el proceso de Blender se cerró; el `.blend` en disco seguía en 19:09. Los cuatro scripts (`blender_concept/reception_pass_v126_materials.py`, `_geometry.py`, `_lighting.py`, `_lod.py`) son idempotentes y reprodujeron el resultado exacto. Se guardó `nexus/nivel_01/NEXUS_L1_V05.blend` y el checkpoint `FM_NEXUS_L1_V05_recepcion_v126.blend` (2.475.500 bytes, 20:35:57).
- **Qué está probado:** recarga headless del checkpoint: 2.330 objetos, 112 materiales, `NEXUS_V05_REC_PASS126` con 159 objetos, `NEXUS_V05_REC_LOD1` con 5, materiales de muro/techo/suelo correctos en los objetos del recinto, mostrador nuevo presente, `NEXUS_V05_REC_DESK` oculto, 4 focos nuevos, lentes fundidas con `NEXUS_V05_MAT_LED_Dead`, 98.701 triángulos en el volumen y 0 bibliotecas ausentes. Auditoría de la geometría nueva: 0 objetos bajo el suelo, 0 por encima de la losa, sin objetos nuevos en el vano de la puerta.
- **Limitaciones:** el arte sigue siendo provisional y no se exportó a Godot. Los 18 assets enlazados quedan sin LOD. El techo está a 6 m (no se cambió la arquitectura). El relleno cálido hace que el muro de yeso se lea algo marrón en las vistas cercanas.
- **Siguiente paso exacto:** decidir si se optimiza `NEXUS_SHARED_ASSETS.blend` para todos los niveles; después aplicar el mismo pase (materiales + servicios + luz) a seguridad y control de acceso, y revisar la secuencia recepción–seguridad–control con cápsula.

## 2026-11-02 21:07 COT — Codebuff — Recepción v126b: solo luz de emergencia, paredes del recinto con textura y muebles con detalle

- **Instrucción del usuario:** hay paredes todavía sin textura, algunos objetos se ven simples/ficticios y, al ser un complejo abandonado, las únicas luces deben ser de emergencia.
- **Iluminación de emergencia (única):** se apagaron y ocultaron 14 luces practicables (`RECEPCION_LIGHT`, `REC_FILL.001`, `REC_SPOT_1..4`, `REC_PEND_LIGHT_0/1`, `REC_DESK_LAMP_LIGHT`, `REC_SIGN_WASH`, `REC_CEILING_BOUNCE_1/2`, `OFFICE_LIGHT`, `REST_LIGHT`) con marca `power_state = "sin corriente (complejo abandonado)"`. Se apagaron 12 lentes y difusores (colgantes, tira de techo, paneles de oficina/aseo, downlights y LED de detectores). Quedan **6 lámparas de emergencia rojas** (puerta, noroeste, muro norte, muro este, oficina y aseo) a 190–210 W las de sala y 25–30 W las interiores.
- **Señalización:** las placas pasan a `NEXUS_V05_MAT_Sign_Battery` sin emisión (antes eran superficies claras de 0,07 y AgX las saturaba a crema); los 13 textos de la sala usan `NEXUS_V05_MAT_Sign_Text` con emisión 0,22, de modo que se leen como rótulos alimentados por batería.
- **Paredes del recinto con textura:** 18 objetos (muros, particiones, parapetos y techo de oficina/aseo) dejan el hormigón genérico y usan `NEXUS_V05_MAT_Rec_Wall`, `NEXUS_V05_MAT_Rec_Ceiling` y `NEXUS_V05_MAT_Baseboard`.
- **Muebles menos ficticios:** bisel de 12 mm y 2 segmentos en 12 piezas de caja (bancos, sillones, respaldos, mesa de centro, jardineras, archivador); el banco pasa de 8 a 56 vértices. Materiales nuevos `NEXUS_V05_MAT_Upholstery`, `NEXUS_V05_MAT_Rec_Painted_Green` y `NEXUS_V05_MAT_Rec_Wood`. El bisel se aplica sobre malla de un solo usuario para no alterar muebles de otras salas.
- **Metales con textura PBR:** `NEXUS_V05_MAT_Galv`, `_Galv_Dark`, `_CableTray`, `_Conduit` y `_Pipe_Red` se reconstruyeron con `rusty_painted_metal_2k`, `rusty_metal_sheet_2k` y `green_metal_rust_2k` (proyección por coordenadas de objeto). Los conductos, bandejas y montantes dejan de verse como plástico liso.
- **Scripts:** `blender_concept/reception_pass_v126b_emergency.py`, `reception_pass_v126c_detail.py` y `reception_pass_v126d_metals.py`. Idempotentes.
- **Renders:** `docs/fm_recepcion_v126b.png` (cámara oficial) y `docs/fm_recepcion_v126b_wide.png`. Los `fm_recepcion_v126*.png` anteriores documentan el pase previo, todavía con luz general.
- **Verificación:** recarga headless del checkpoint `FM_NEXUS_L1_V05_recepcion_v126b.blend`: 2.329 objetos, 116 materiales, 0 focos practicables encendidos, las 6 emergencias activas, muro y partición de oficina con `NEXUS_V05_MAT_Rec_Wall`, conducto con texturas de imagen, banco biselado marcado, 5 LOD y **99.569 triángulos** en el volumen (+868 por los biseles).
- **Limitaciones:** la recepción queda muy oscura por diseño; la exploración dependerá de la linterna del jugador (Fase 3), que todavía no está integrada. Persisten los 18 assets enlazados sin LOD. Los muebles biselados siguen siendo geometría de caja: dejan de verse como primitivas, pero no son arte final.
- **Siguiente paso exacto:** aplicar el mismo criterio de luz de emergencia al corredor y a seguridad, y definir la linterna del jugador para que la recepción sea jugable sin luz general.

## 2026-11-03 11:08 — Recepción del Nivel 1: pase de mecánicas, luz y LOD (v127)

Auditoría previa de la sala contra el bucle de juego: la recepción estaba terminada
como escenario pero no como sala jugable. Tenía 0 objetos con física, 0 recuperables,
0 escondites, 0 fuentes de ruido y puertas estáticas.

**Añadido (todo geometría local, colección `NEXUS_V05_REC_PLAY`, 76 objetos):**

- Cinco objetos recuperables con metadatos para física, loot y carga:
  maletín (17 kg, 640), caja de muestras frágil (9 kg, 900), caja de equipo a dos
  jugadores (42 kg, 1.800), carpeta de documentos (0,6 kg, 220) y cartucho de datos
  (0,4 kg, 1.200). Todos con `weight_kg`, `loot_value`, `carry_hands`, `noise_kind`
  y `noise_radius_m`.
- Escondite: armario de conserjería con interior 0,96 × 0,93 × 2,09 m (el jugador mide
  0,76 m), una hoja abierta 28° y una cerrada, rejillas y etiqueta. Marcado con
  `hide_spot`, `hide_capacity` y medidas de interior.
- Puerta de acceso operable: la hoja, el vidrio y el manillar se colgaron de
  `NEXUS_V05_REC_DOOR_PIVOT` en la bisagra oeste. Probado a 45°: la hoja gira hacia
  el interior sin salirse del vano. Además se subió la hoja 70 mm, que estaba
  enterrada bajo el piso.
- Trampa sonora real en el recorrido de la puerta: 8 cristales de 5 mm con volumen,
  2 latas y una bandeja metálica, `trap_kind=sound`, radio 7 m.
- Luz: las 14 luces practicables siguen apagadas; las 6 de emergencia bajaron a
  85–95 W (salas) y 16–18 W (office/aseo) y se desaturó el rojo. Se añadió
  `NEXUS_V05_REC_SPILL_CORRIDOR` (140 W, 0,55/0,68/0,86) que simula la luz fría del
  pasillo entrando por la puerta de vidrio, y una emergencia más en el tramo este.
- Emisiones apagadas: pantallas (`NEXUS_Screen` 2,2 → 0), pulsadores (`NEXUS_Amber`
  2,8 → 0) y rótulos (`Sign_Text` 0,22 → 0,03). La lámpara de tubo del mostrador
  emitía a 82,4 con color blanco: se corrigió en la biblioteca compartida
  (`industrial_pipe_lamp` y `industrial_pipe_lamp_glass` → 0). Esa lámpara solo la
  usa la recepción.

**LOD:** se intentó primero un override de biblioteca; el operador de Blender
duplicó los 70 objetos enlazados en lugar de convertirlos, así que se descartó y no
queda ningún override en el archivo. La reducción se hizo en la biblioteca, sobre
mallas que no usan los niveles 2–5 ni el núcleo (verificado): sillas 5.072 → 2.028,
portapapeles 6.176 → 1.358, reloj 3.380 → 1.014, escritorio 4.186 → 2.092, carrito
de café 25.899 → 9.062, lámpara de tubo 7.606 → 3.422 y monitores 1.918 → 1.053.
Total **54.237 → 20.029 triángulos (−63 %)** en las mallas afectadas.

**Resultado medido:** recepción visible **100.628 → 74.280 triángulos** (−26 %)
incluyendo los 76 objetos nuevos.

**Archivos:** `blender_concept/reception_pass_v127_mechanics.py`,
`reception_pass_v127_light.py`, `nexus_shared_lod_pass.py`. Checkpoint
`nexus/nivel_01/NEXUS_L1_V05_recepcion_v127.blend` (junto al nivel, para que las rutas
relativas de la biblioteca sigan resolviendo). Renders `docs/fm_recepcion_v127.png` y
`docs/fm_recepcion_v127_entry.png`. Respaldos de biblioteca:
`NEXUS_SHARED_ASSETS_PRE_LAMPFIX.blend` y `NEXUS_SHARED_ASSETS_PRE_LOD.blend`.

**Limitaciones:** al decimar mallas compartidas, las mismas sillas y escritorios de
oficina y seguridad del Nivel 1 también quedan reducidos. El escondite y la puerta
son geometría preparada con pivote y metadatos, no un sistema interactivo: la
interacción se implementa al exportar a Godot. Sigue sin haber linterna en la
escena, así que la sala es muy oscura para explorar sin ella. Se detectó un reloj
local suelto en `Scene Collection` (copia manual, 3.380 triángulos) junto al reloj
enlazado del muro norte; no se tocó.

**Hallazgo colateral:** las copias de checkpoint guardadas en la raíz del proyecto
(`FM_NEXUS_L1_V05_recepcion_*.blend`) rompen la ruta relativa de la biblioteca
`//../compartido/NEXUS_SHARED_ASSETS.blend`: al abrirlas, Blender carga 2.166 objetos
en vez de 2.389 y pierde los assets enlazados. Comprobado con recarga headless. Los
checkpoints del Nivel 1 deben guardarse dentro de `nexus/nivel_01/` o con rutas
absolutas. Los checkpoints ya existentes en la raíz tienen el mismo problema.

---

## GUÍA DE CONTINUACIÓN — Recepción Nivel 1 (estado v127, 2026-11-03 11:08)

Esta sección es el punto de entrada para retomar el trabajo. Léela antes de tocar
la recepción.

### Dónde está el trabajo

| Qué | Dónde |
|---|---|
| Archivo de trabajo | `nexus/nivel_01/NEXUS_L1_V05.blend` |
| Checkpoint del pase | `nexus/nivel_01/NEXUS_L1_V05_recepcion_v127.blend` |
| Biblioteca compartida | `nexus/compartido/NEXUS_SHARED_ASSETS.blend` |
| Respaldos de biblioteca | `NEXUS_SHARED_ASSETS_PRE_LAMPFIX.blend`, `NEXUS_SHARED_ASSETS_PRE_LOD.blend` |
| Scripts del pase | `blender_concept/reception_pass_v127_mechanics.py`, `reception_pass_v127_light.py`, `nexus_shared_lod_pass.py` |
| Renders del estado | `docs/fm_recepcion_v127.png`, `docs/fm_recepcion_v127_entry.png` |

**Rutas relativas:** el archivo del nivel apunta a `//../compartido/NEXUS_SHARED_ASSETS.blend`.
Cualquier copia debe quedar dentro de `nexus/nivel_01/`. Una copia en la raíz del
proyecto pierde la biblioteca y abre con 2.166 objetos en vez de 2.389.

### Cómo debe abrirse y medirse

1. Abrir `nexus/master/NEXUS_MASTER.blend` para ver el conjunto (solo lectura).
2. Abrir `nexus/nivel_01/NEXUS_L1_V05.blend` para editar la recepción.
3. Medir con recarga headless, nunca fiándose del estado de la sesión viva:
   ```
   blender -b nexus/nivel_01/NEXUS_L1_V05.blend --python /tmp/verify.py
   ```
   El verify debe imprimir ~2.389 objetos, 76 objetos en `NEXUS_V05_REC_PLAY`,
   7 luces encendidas en la sala y ~74.280 triángulos visibles.

### Qué NO repetir

- **No volver a ejecutar `nexus_shared_lod_pass.py`.** Ya decimó la biblioteca.
  Si hiciera falta, restaurar antes `NEXUS_SHARED_ASSETS_PRE_LOD.blend`; ejecutarlo
  dos veces destruye la geometría.
- **No usar overrides de biblioteca sobre `NEXUS_ASSET_L1_REPLACE`.** El operador
  duplica los 70 objetos enlazados en lugar de convertirlos; el archivo quedó limpio
  de overrides y así debe mantenerse.
- **No reejecutar los scripts `reception_pass_v126*.py`**: son del pase anterior y
  volverían a crear servicios de techo y materiales ya existentes.
- Los scripts v127 son idempotentes: borran `NEXUS_V05_REC_PLAY` y reconstruyen.
  Reejecutarlos no duplica nada.

### Lo que ya está resuelto en la recepción

- 5 recuperables con `loot`, `loot_value`, `weight_kg`, `carry_hands`, `noise_radius_m`.
- Escondite `NEXUS_V05_REC_HIDE_CABINET_0` con interior 0,96 × 0,93 × 2,09 m.
- Puerta con pivote `NEXUS_V05_REC_DOOR_PIVOT` (bisagra oeste, giro interior 95°).
- Trampa sonora `NEXUS_V05_REC_TRAP_NOISE_0` (8 cristales, 2 latas, 1 bandeja).
- Solo emergencia: 6 lámparas originales + 1 nueva en el tramo este, más
  `NEXUS_V05_REC_SPILL_CORRIDOR` (luz fría del pasillo por la puerta de vidrio).
- Sin emisiones parásitas: pantallas, pulsadores y rótulos apagados; la lámpara de
  tubo corregida en la biblioteca.
- LOD aplicado en las mallas compartidas que solo usan las salas del Nivel 1.

### Lo que falta en la recepción

1. **Linterna.** La sala está pensada para recorrerse con linterna y todavía no
   existe en esta escena. Sin ella no es explorable. Es el bloqueador principal.
2. **Extracción.** No hay punto de extracción ni marcador de objetivo; el recorrido
   recepción → corredor → extracción no está definido.
3. **Puertas secundarias.** Oficina y aseo siguen con hojas estáticas y 2,08 m de
   alto (no pasan criaturas de 2,2–3,0 m). La propuesta de subirlas a ≈2,60 m sigue
   sin autorizar.
4. **Objetos narrativos interactivos.** No hay notas, paneles ni monitores que se
   puedan consultar; solo hay recuperables.
5. **Reloj suelto.** `NEXUS_ASSET_L1_REC_CLOCK_ROOT` (local, en `Scene Collection`,
   3.380 triángulos) convive con el reloj enlazado del muro norte. Decidir si se
   elimina o se integra en `NEXUS_V05_REC_PLAY`.
6. **Pase equivalente en seguridad y control de acceso.** Siguen sin recuperables,
   escondites, puertas operables ni trampas.

### Orden sugerido para seguir

1. Revisar los dos renders y corregir lo que aparezca fuera de sitio.
2. Integrar la linterna (o autorizarla) y volver a renderizar la recepción.
3. Definir el recorrido de extracción y su punto final.
4. Repetir el pase de mecánicas en seguridad y control, reutilizando
   `reception_pass_v127_mechanics.py` como plantilla (no copiarlo tal cual: cambian
   posiciones y nombres).
5. Abrir las puertas de oficina/aseo solo con autorización explícita.

### Metadatos para el exportador a Godot

Los objetos nuevos llevan propiedades personalizadas listas para leer:

- `loot`, `loot_class`, `loot_value`, `weight_kg`, `fragile`, `carry_hands`,
  `requires_two_players`, `noise_kind`, `noise_radius_m`, `physics`, `collider`.
- `hide_spot`, `hide_capacity`, `hide_type`, `interior_width_m`,
  `interior_depth_m`, `interior_height_m`, `cover`, `concealment`.
- `trap`, `trap_kind`, `noise_radius_m`, `triggers_on`, `breakable`.
- `interactive=door`, `door_type`, `door_state`, `open_angle_deg`, `hinge_side`,
  `swing_direction`, `requires_hands`.
- Cada root tiene `exported_name` con el identificador estable que debe usarse en el
  juego, para no depender del nombre del objeto en Blender.

## 2026-11-03 13:05 COT — OpenCode — Recepción v128–v130: linterna, extracción y enlace del máster

### Autorización y alcance

El usuario autorizó el plan de cierre de recepción con **“perfecto hagamos eso”**:
comparar el vivo contra v127, guardar checkpoint, integrar linterna, definir
extracción provisional, eliminar el reloj local suelto y no tocar las puertas de
oficina/aseo ni pasar todavía a seguridad.

### Diff y checkpoint v128

- `nexus/nivel_01/NEXUS_L1_V05.blend` tenía 2.377 objetos; v127 tenía 2.389.
- Faltaban 12 piezas de dos sillones blocky retirados:
  `NEXUS_V05_C_REC_LOUNGE_E_*` y `..._LOUNGE_W_*`.
- Ocho objetos tenían cambios manuales: `NEXUS_V05_OFFICE_DUCT` z −2,30→−2,48;
  `NEXUS_V05_RECEPCION_WALL_W` z −2,08→−2,84; `REC_LOOT_DOCS_0` y sus piezas
  movidas de x≈−12,95 a −12,61; asa del maletín z −5,278→−5,298.
- El render de control mostró la recepción coherente, sin huecos por los sillones.
  Se conservaron los cambios y se guardó
  `nexus/nivel_01/NEXUS_L1_V05_recepcion_v128.blend` (2.633.964 B, 2.377 objetos).

### v129 — linterna y extracción

Script: `blender_concept/reception_pass_v129_flashlight.py`.

- **Linterna:** asset `small_plastic_torch_2k` importado como
  `NEXUS_V05_REC_FLASHLIGHT_BODY`, root `NEXUS_V05_REC_FLASHLIGHT_RIG` en
  (−8,529, 3,669, −4,426). Spot de 1.000 W, 34°, sombra activa; spill de 7 W; lente
  emisiva. Metadatos: batería 78 %, consumo 1,2 %/min, alcance 18 m, recarga por
  pilas, `preview_only=True`, `attach_to=player_camera`.
- **Extracción provisional:** `NEXUS_V05_REC_EXTRACT_ZONE` en (−13,90, 2,78, −5,65),
  radio 0,75 m, activación 8 s, `required_players=1`, estado standby. Incluye aro
  naranja emisivo, consola de pared, pantalla teal, cartel
  “EXTRACCION // SALIDA” y luz naranja de 7 W.
- **Reloj:** se eliminó el reloj local suelto `NEXUS_ASSET_L1_REC_CLOCK*` de
  x < −18,5; se conservó el reloj enlazado de (−17,0, 11,472, −3,36).
- Resultado: `NEXUS_L1_V05_recepcion_v129.blend`, 2.869.557 B, 2.389 objetos,
  90 objetos en `NEXUS_V05_REC_PLAY`.
- Auditoría `blender_concept/audit_reception_v129.py`: 14 objetos nuevos, 0 fuera de
  la recepción, 0 bajo el suelo, 0 colisiones AABB > 0,0005 m³; sin relojes locales
  ni colecciones temporales del asset.
- Renders: recepción con linterna y detalle de extracción revisados a 640×360.

### v130 — las colecciones nuevas llegan al máster

Problema: `NEXUS_V05_REC_PASS126`, `NEXUS_V05_REC_LOD1` y `NEXUS_V05_REC_PLAY`
estaban en la raíz del archivo de L1, fuera de `NEXUS_L1_V05`, que es la única
colección que enlaza el máster. Por eso el máster seguía con 7.806 objetos y no
mostraba linterna ni extracción.

Solución no destructiva: `blender_concept/bind_l1_collections_v130.py` mueve las
tres colecciones bajo `NEXUS_L1_V05`, sin cambiar transformaciones ni borrar datos,
y guarda `NEXUS_L1_V05_recepcion_v130.blend` (2.869.245 B). Se copió sobre
`NEXUS_L1_V05.blend`.

Verificación:

- L1: **2.389 objetos**; `NEXUS_L1_V05` contiene las tres colecciones.
- Máster: **8.063 objetos** (7.806 + 257), linterna y extracción presentes.
- Comparación L1→máster: **0 objetos ausentes**, **0 diferencias** de tipo, matriz,
  `hide_render` o `hide_viewport` en los 2.389 objetos de L1.
- `nexus/manifest.json` regenerado con `blender_concept/refresh_nexus_manifest.py`.
- Render de recepción del máster a 640×360 (`/tmp/opencode/master_v130_reception.png`)
  revisado: linterna visible, haz cálido sobre el mostrador, desorden y emergencia
  coherentes.
- L1 actual: **570.777 triángulos visibles** en 1.885 objetos de malla; 50 luces
  visibles, 23 con sombra.

### Limitaciones y siguiente paso

- La linterna es una vista previa anclada a la cámara; no hay controlador de jugador
  ni código de batería/interacción.
- La extracción es una zona con metadatos y geometría; no hay lógica de activación.
- El máster enlaza niveles: hay que reabrirlo para recargar cambios.
- Siguiente: revisar circulación recepción → corredor → seguridad → control → umbral
  y núcleo con cápsula/recorrido, incluyendo obstáculos y retorno a extracción.
  Después proponer el pase de mecánicas de seguridad/control. No tocar las puertas
  de oficina/aseo (2,08 m) sin autorización.
- No se exportó a Godot; no se tocó `fotos-referencia/`; no se hicieron commits.

## 2026-11-03 13:35 COT — OpenCode — Circulación de recepción y accesos del Nivel 1 (v131–v133)

### Método y primera detección

Se sustituyó la comprobación por rayos por una rejilla de accesibilidad 2D con
cápsula conservadora: radio 0,38 m, altura 1,80 m, celda 0,05 m, obstáculos entre
suelo +0,16 m y suelo +1,80 m. Se excluyeron hojas/cristales/manillas/pivotes de
puerta, la linterna de vista previa y el aro de extracción. Salida:
`nexus/nivel_01/circulation_reachability.json`; script:
`blender_concept/audit_l1_pathgrid.py`.

La primera pasada encontró que el banco `NEXUS_V05_REC_BENCH2` cruzaba la entrada
de recepción: el hueco entre el muro y el banco era de 0,76 m, exactamente el
diámetro del jugador y sin margen práctico. El BFS solo alcanzaba hasta
`(-12, 2,05)`; la entrada y el interior no eran alcanzables. También se detectaron
el carro caído junto a la puerta de control y las dos señales del extremo oeste del
corredor.

### v131 — rechazada

`blender_concept/reception_fix_circulation_v131.py` rotaba el banco y lo llevaba a
la pared oeste. Se guardó `NEXUS_L1_V05_recepcion_v131.blend` (2.841.065 B), pero
solapaba con las tres sillas `NEXUS_ASSET_L1_REC_WAIT_CHAIR_0/1/2`. **No usar v131.**

### v132 — banco oculto de forma reversible

`blender_concept/reception_fix_circulation_v132.py` ocultó el banco duplicado y sus
cuatro patas, sin borrar datos:

- `NEXUS_V05_REC_BENCH2`
- `NEXUS_V05_D_REC_BENCH2_LEG_0_0`, `_0_1`, `_1_0`, `_1_1`

Cada objeto conserva `original_location`, `circulation_fix` y `replaced_by`. No
había objetos apoyados sobre el banco. Se conservan el banco de la pared oeste y
las tres sillas de espera. Resultado:
`NEXUS_L1_V05_recepcion_v132.blend` (2.873.000 B, 2.389 objetos).

### v133 — pasillo central legible

`blender_concept/reception_fix_circulation_v133.py`, partiendo de v132:

- Mesa de centro y sus cuatro patas: **−3,1 m en X**; el tablero queda en
  `(-15,1, 4,3, -5,27)`.
- Silla caída B: **+1,20 m en X**; la malla visible queda en
  `(-9,6, 4,4, -5,312)` y su bbox x −10,52..−9,4, y 3,5..4,61.
- Todos los objetos movidos guardan `original_location` y
  `circulation_fix="reception_v133_clear_aisle"`.

Solo queda un solape AABB con `NEXUS_V05_D_REC_RUG` de **0,0218 m³**, que es la
silla caída apoyada sobre la alfombra; se considera intencional. No hay solape con
la papelera. Resultado: `NEXUS_L1_V05_recepcion_v133.blend` (2.873.657 B, 2.389
objetos).

### Resultado de accesibilidad en v133

Alcanzables desde el corredor:

- entrada de recepción `(-12, 2,6)`;
- frente del mostrador `(-12, 6,6)`;
- ala oeste `(-16, 6,5)`;
- seguridad;
- vestuarios, almacén y mantenimiento justo dentro de su puerta;
- control justo dentro, control tras el arco/escritorio y enlace restringido.

Ruta al mostrador: `(-12,0) → (-11,6,0,6) → (-11,6,1,6) → (-11,35,2,35) →
(-11,35,3,35) → (-11,35,4,35) → (-11,8,4,9) → (-12,0,5,7) → (-12,0,6,6)`.

Limitaciones documentadas y no corregidas:

- `(13, 5,2)`, justo antes del arco de control, no es alcanzable en línea recta;
  se llega al otro lado por un rodeo occidental (≈x 9,9). Puede ser una secuencia
  de control intencional, pero necesita señalización/claridad de diseño.
- El extremo oeste **sí es alcanzable** por el carril sur (y ≈ −1,0): se llega a
  `(-15, -1)`, `(-17, -1)` y `(-20, -1)`, incluido el extintor. El carril norte a
  partir de x ≈ −14,6 queda bloqueado por la silla caída y las dos señales; decidir
  si se señaliza el desvío sur o se acepta como restricción narrativa.
- El interior completo de vestuarios, almacén y mantenimiento aún no se recorrió;
  solo se certificó el acceso desde el corredor.
- El núcleo vertical sigue pendiente de prueba con cápsula.

### Verificación visual e integración

Renders headless 640×360 revisados:

- `/tmp/opencode/v133_reception.png`: cámara existente, mesa desplazada, suelo más
  abierto, linterna y mostrador coherentes.
- `/tmp/opencode/v133_door_view.png`: vista baja desde la puerta; pasillo central
  legible, sillas y monitor roto como obstáculos laterales.
- `/tmp/opencode/v133_eye_entry.png`: altura de ojos desde la puerta; paso claro
  hasta el mostrador.

v133 se copió sobre `nexus/nivel_01/NEXUS_L1_V05.blend`. El máster se reabrió con
**8.063 objetos**, 8 bibliotecas relativas, 0 ausentes, sin `TMP_`, cámara
`NEXUS_V05_CAM_Corridor`; la mesa, la silla y el banco oculto se ven en su estado
nuevo. `blender_concept/refresh_nexus_manifest.py` actualizó `nexus/manifest.json`.

L1 medido: **2.389 objetos**, **1.880 mallas visibles**, **543.225 triángulos**,
**50 luces visibles**, **23 con sombra**, cámara `NEXUS_V05_CAM_Recepcion`, 0
bibliotecas ausentes. La reducción desde 570.777 viene de ocultar el banco y sus
patas.

### Documentación y siguiente paso

- Nuevo `docs/NEXUS_L1_CIRCULATION_AUDIT.md` con método, puertas, resultados y
  limitaciones.
- `docs/CURRENT_STATE.md` actualizado a v133 y 543.225 triángulos.
- `docs/NEXUS_ASSET_INVENTORY.md` actualizado con el pase de circulación.
- Siguiente: decidir señalización/reordenación del acceso al arco de control y el
  desvío sur del extremo oeste, recorrer el interior de vestuarios/almacén/mantenimiento
  y probar el núcleo vertical. Después, proponer el pase de mecánicas de seguridad/control.
- No se tocó `fotos-referencia/`; no se exportó a Godot; no se hicieron commits.
- Persisten las dos PNG inválidas de `industrial_wall_lamp_1k`; no se modificaron
  los originales.

---

## 2026-11-03 13:45 COT — OpenCode — Arco de control despejado (v134)

### Problema y corrección

La verificación v133 dejó un único acceso incómodo: `(13,0, 5,2)`, justo antes del
arco detector, no era alcanzable en línea recta. La causa no era el arco, sino dos
objetos bajos colocados en su vano: `NEXUS_V05_ACC_BARRIER_1` (x 12,82..13,18,
y 3,05..4,95, z −5,29..−5,21) y `NEXUS_V05_ACC_POST_1` (x 12,89..13,11,
y 2,89..3,11). Con el radio de cápsula de 0,38 m cerraban el paso útil del arco
(x 12,24..13,76) y obligaban a rodear todo el control por el oeste.

`blender_concept/control_checkpoint_fix_v134.py` oculta ambos objetos de forma
reversible (`hide_render=True`, `hide_viewport=True`) y guarda `original_location`,
`original_hide_render`, `original_hide_viewport`,
`circulation_fix="control_v134_clear_detector_lane"`, `hide_reason` y
`checkpoint_state` (`retracted`/`removed`). No se borró nada. La base es v133 y el
checkpoint es `nexus/nivel_01/NEXUS_L1_V05_control_v134.blend` (**2.874.332 B**,
2.389 objetos, cámara `NEXUS_V05_CAM_Recepcion`); se copió sobre
`nexus/nivel_01/NEXUS_L1_V05.blend`.

### Verificación

- BFS con cápsula de 0,38 m: **todos los objetivos alcanzables**, incluido el paso
  recto `(13, 5,2)` → `(13, 6,4)` → escritorio `(13, 7,0)`, además de recepción,
  mostrador, ala oeste, seguridad, vestuarios, almacén, mantenimiento, enlace
  restringido y extremo oeste por el carril sur. `OBSTACLES 956`,
  `COMPONENT 206082`.
- El auditor `blender_concept/audit_l1_pathgrid.py` quedó limpio con 15 objetivos
  estables; `nexus/nivel_01/circulation_reachability.json` actualizado.
- Máster: **8.063 objetos**, 8 bibliotecas relativas y 0 ausentes; los dos objetos
  retirados figuran con `hide_render=True` y el metadato del pase. `manifest.json`
  refrescado.
- L1: **2.389 objetos**, **1.878 mallas visibles**, **543.201 triángulos**,
  50 luces visibles y 23 con sombra.
- Render `/tmp/opencode/v134_control.png` (640×360, cámara Control): arco despejado
  y paso central visible; la sala sigue lavada por la exposición, sin cambios de
  iluminación. Persisten las dos PNG inválidas de `industrial_wall_lamp_1k`.

### Documentación y siguiente paso

- `docs/NEXUS_L1_CIRCULATION_AUDIT.md` marca el arco de control como resuelto en
  v134 y limita la limitación restante al carril norte del extremo oeste, que se
  acepta como restricción narrativa; el carril sur es transitable.
- `docs/CURRENT_STATE.md` actualizado a v134, 543.201 triángulos y checkpoint
  vigente; `docs/NEXUS_ASSET_INVENTORY.md` recoge la retirada reversible.
- Siguiente: probar el **núcleo vertical** con cápsula/recorrido y el retorno a la
  extracción; recorrer el interior completo de vestuarios, almacén y mantenimiento;
  después proponer (sin ejecutar) las mecánicas de seguridad/control.
- No se tocó `fotos-referencia/`; no se exportó a Godot; no se hicieron commits.

---

## 2026-11-03 13:50 COT — OpenCode — Auditoría del núcleo vertical este

### Objetivo y método

Se auditó la escalera `NEXUS_VTOWER_EAST_STAIR_4LANE` en el máster con
`blender_concept/audit_core_route.py`, sin modificar la torre. Se usaron dos
comprobaciones independientes:

1. rejilla 2D de 0,05 m con cápsula de 0,38 m desde el enlace L1 `(24,0)` hasta
   el portal `(30,12.5)`;
2. muestreo al 25/50/75 % de cada vuelo, con holgura lateral contra un BVH de la
   geometría visible y rayo vertical para altura libre.

La pared booleana `NEXUS_VTOWER_WALL_E` se representó como dos tramos sólidos
alrededor del hueco real de 1,64 m; usar su AABB habría cerrado falsamente el
portal.

### Resultado

- Acceso L1: **alcanzable**. Ruta:
  `(24,0) → (24,6,7,4) → (24,6,9,4) → (25,45,9,55) → (29,45,9,55) →
  (29,45,11,55) → (29,9,12,1) → (30,12,5)`.
- 18 vuelos, cuatro tramos. Recorridos de **2,72–3,80 m**; contrahuellas totales
  de 8–11 m por tramo.
- **Holgura lateral mínima 0,32 m** en la línea central, junto a los muros
  sur/norte de los vuelos 01 y 04.
- **Altura libre mínima 5,698 m** donde hay techo; L1–L2 queda abierto por
  arriba y el rayo no encuentra techo.
- Sin colisiones de cápsula en las muestras centrales.
- Resultado en `nexus/nucleo/core_route_audit.json` y
  `docs/NEXUS_CORE_ROUTE_AUDIT.md`.

### Limitaciones y siguiente paso

No es una simulación de `CharacterBody`: no mide peldaños reales, `floor_snap`,
giro fino en descansillos, criaturas de 3,0 m ni el retorno continuo completo.
La escalera es transitable en su línea central. El lobby oeste tiene luces de
área (`NEXUS_VTOWER_LOBBY_AREA_1..5`), pero el **recinto de la escalera este no
tiene fuentes propias** y el render de revisión `/tmp/opencode/core_stair.png`
sale negro. El siguiente paso es añadir luces de emergencia al recinto de la
escalera y revisar visualmente el portal L1, antes de probar los enlaces L2–L5 y
el retorno a la extracción. No se tocó `fotos-referencia/`; no se exportó a Godot.

---

## 2026-11-03 14:05 COT — OpenCode — Linterna fuera y extracción en la puerta

### Decisión del usuario

El usuario propuso que cada jugador reciba una linterna al ingresar y que el
punto de extracción sea la puerta de salida existente. Se aceptó: la linterna de
vista previa no debía quedarse como equipamiento fijo de la escena y la
extracción gana sentido narrativo en el acceso.

### Cambios

- Se eliminaron los cinco objetos `NEXUS_V05_REC_FLASHLIGHT_*` (`RIG`, `BODY`,
  `SPOT`, `SPILL`, `LENS`). La escena pasa de **2.389 a 2.384 objetos**. Se
  conserva el material `NEXUS_V05_MAT_Flashlight_Lens` para la futura linterna
  del jugador.
- `NEXUS_V05_REC_EXTRACT_ZONE` pasa de `(-13,90, 2,78, -5,65)` a
  **`(-12,0, 2,30, -5,65)`**, centrada en `NEXUS_V05_REC_DOOR_PIVOT`.
- Metadatos nuevos: `route_stage=reception_exit_door`,
  `exported_name=extraction_reception_exit_door`,
  `anchor=NEXUS_V05_REC_DOOR_PIVOT`, `doorway_width_m=1.60` y `layout_note`.
- La consola, pantalla, indicador, botón, cartel y luz conservan su posición
  física junto al marco oeste; se compensaron matrices al cambiar el padre.
- El anillo naranja queda centrado en la puerta a **z −5,628**, por encima del
  felpudo `NEXUS_V05_C_REC_MAT` (top ≈−5,634), con `surface_offset_m=0.022`.
  La alfombra grande `NEXUS_V05_D_REC_RUG` se movió durante la prueba y se
  revirtió a y=4,3 sin metadatos residuales.

### Verificación

- `NEXUS_L1_V05.blend` guardado en sitio: **2.577.575 bytes**, **2.384 objetos**,
  cámara `NEXUS_V05_CAM_Recepcion`, `NEXUS_V05_REC_PLAY` con **85 objetos**.
- No quedan objetos `NEXUS_V05_REC_FLASHLIGHT_*` ni objetos `TMP_`.
- Medición actual: **560.445 triángulos visibles**, **1.876 mallas**, **48 luces**
  visibles y **22 con sombra**.
- Máster recargado desde el enlace: **8.058 objetos**, sin linterna, con la zona
  de extracción en `(-12,0, 2,30, -5,65)`.
- Render `/tmp/opencode/extraction_at_door3.png`: anillo completo sobre el
  felpudo, consola junto al marco; legible. Persisten las dos PNG inválidas de
  `industrial_wall_lamp_1k`.

### Limitaciones y siguiente paso

La extracción sigue siendo geometría y metadatos sin lógica de activación; la
linterna será equipamiento del jugador al ingresar, no un objeto de la escena.
No se crearon más checkpoints de recepción por petición del usuario. Siguiente:
iluminar la escalera este y continuar la auditoría del núcleo vertical.

---

## 2026-11-03 14:35 COT — OpenCode — Sala de extracción en el extremo oeste del corredor (v135)

### Petición y decisión

El usuario propuso convertir el muro ciego con rótulo **SALIDA** que hay frente
al antiguo punto de extracción en una sala completa de extracción. Se
inspeccionó: no era una puerta, sino `NEXUS_V05_CORR_END_-22` con una placa
pequeña. Se aceptó abrir un vano real y construir detrás una sala de 6 × 6 m,
sin eliminar el rótulo ni el muro original. El usuario respondió **“si probemos
haber”**.

### Construcción

- Se abrió un vano de **1,60 × 3,07 m** en el extremo oeste del corredor. La
  sala ocupa x −28..−22, y −3..3, con suelo a −5,65 y techo a −1,72.
- Se construyeron suelo, techo, muros perimetrales, muro este segmentado,
  dintel, marco de acero, umbral y guía. La hoja corredera queda aparcada
  dentro de la sala, sin cerrar el paso.
- Compuerta industrial cerrada al oeste, con lamas de `NEXUS_Painted_Metal`,
  marco, franjas ámbar y rótulo **EXTRACCION // SALIDA**.
- Ducha de emergencia, desagüe central, tuberías, cuadro eléctrico, estantes,
  zócalos verdes, iluminación de área, luz de emergencia roja y luz de consola.
- La sala entera es la zona de extracción: `NEXUS_V05_REC_EXTRACT_ZONE` en
  `(-25, 0, -5,65)`, `zone_shape=room_box`, `zone_size_m=[5.6,5.6]`,
  activación 10 s. Se eliminaron `radius_m` y `doorway_width_m`.
- La consola se trasladó al muro norte, con pedestal, base, baliza y cartel.
  El aro antiguo de la puerta de recepción quedó oculto; no se borró.
- El muro original `NEXUS_V05_CORR_END_-22` se conserva oculto en
  `NEXUS_V05_EXTRACTION_HIST` con metadatos de reversibilidad. El rótulo
  **SALIDA** original se conserva visible sobre el nuevo vano.
- Se añadieron cuatro assets locales con metadatos `asset_source` y licencia
  pendiente de verificar: cajas de madera `wooden_crate_01_2k`, barril
  `barrel_03_2k`, armario auxiliar `utility_box_01_2k` y extintor
  `korean_fire_extinguisher_01_2k`.

### Verificación y render

- `nexus/nivel_01/NEXUS_L1_V05.blend` guardado **en sitio**, sin checkpoint
  nuevo: **3.155.052 bytes**, **2.493 objetos**, cámara guardada
  `NEXUS_V05_CAM_Recepcion`.
- `NEXUS_V05_EXTRACTION_ROOM`: **118 objetos**; de ellos **108** con prefijo
  `NEXUS_V05_EXTR_`. Sin objetos `TMP_`; sin colecciones residuales de los
  assets.
- L1 medido: **1.970 mallas visibles**, **598.391 triángulos**, **51 luces
  visibles**, **24 con sombra**. El máster recargado desde el enlace tiene
  **8.167 objetos**, 0 bibliotecas ausentes y 8 bibliotecas relativas.
- Rayos horizontales a z −5,0, −4,0 y −3,0 desde el corredor atraviesan el
  vano y terminan en la compuerta oeste, sin impactos intermedios. Los crates
  quedan separados de la pared sur (mín. y −2,833 frente a la cara −2,86) y
  apoyados en el suelo; la caja superior coincide con la cara superior de la
  inferior.
- La rejilla BFS ampliada a x −29..25 confirma alcanzables
  `extraction_room_center (-25,0)`, `extraction_console_front (-25.3,1.8)` y
  `extraction_shutter_front (-27,0)`; la ruta al centro usa 17 puntos y pasa
  por el carril sur del corredor.
- Renders guardados: `docs/fm_extraccion_v135_room.png` (vista interior) y
  `docs/fm_extraccion_v135_door.png` (desde la sala hacia el corredor). Se
  revisó también la aproximación desde el corredor: el vano se lee abierto y
  la sala queda iluminada.
- Script reproducible: `blender_concept/build_extraction_room_v135.py`;
  compila con `python3 -m py_compile`. No reejecutar sin revisar que reconstruye
  la sala y guarda en sitio.

### Limitaciones y siguiente paso

La compuerta y la hoja corredera son geometría estática, sin interacción. La
zona de extracción tiene metadatos, pero no lógica jugable. La sala es funcional
y legible, aunque todavía puede recibir una segunda pasada de detalle
narrativo. Persisten las dos PNG inválidas de `industrial_wall_lamp_1k`; no se
modificaron los assets originales. Siguiente: iluminar el recinto de la escalera
este y revisar visualmente el portal L1 y un tramo de escalera. No se exportó a
Godot ni se tocó `fotos-referencia/`.

---

## 2026-11-03 15:05 COT — OpenCode — Extracción en el ascensor SALIDA de recepción (v136)

### Corrección del usuario

El usuario vio la sala oeste y aclaró:

> “ya veo la sala de extraccion, pero ahi no era la ubicacion, la que yo decia
> es dentro de recepcion, ahi hay un letrero que dice SALIDA junto con un reloj
> ahi era donde queria que quedara”

Se localizó el rótulo: `NEXUS_V05_C_REC_ELEV_SIGN_TEXT_TEXT` dice **SALIDA** y
está sobre el ascensor de la pared norte de recepción. El reloj
`NEXUS_ASSET_L1_REC_CLOCK_ROOT` está montado sobre la misma puerta. No hay un
cuarto detrás del muro norte; es un ascensor. El usuario eligió:
**“Extracción en el ascensor y borrar sala oeste”**.

### Reversión y nueva extracción

- `blender_concept/fix_extraction_elevator_v136.py` elimina los **118 objetos**
  de la sala oeste y las colecciones `NEXUS_V05_EXTRACTION_ROOM` y
  `NEXUS_V05_EXTRACTION_HIST`.
- `NEXUS_V05_CORR_END_-22` vuelve a `V05_STRUCT`, visible y sin metadatos de
  sala. Los rótulos SALIDA del fondo del corredor se ocultan de forma
  reversible; el extremo oeste vuelve a ser una pared ciega.
- La extracción nueva está en `NEXUS_V05_REC_PLAY`: `NEXUS_V05_REC_EXTRACT_ZONE`
  en **(-17.5, 10.7, -5.65)**, `zone_shape="elevator_lobby"`,
  `zone_size_m=[2.10,1.50]`, activación 10 s, anclada al marco del ascensor.
- Se añadieron aro rectangular naranja de 2,10 × 1,50 m, texto de suelo
  **EXTRACCION**, consola mural a la derecha del ascensor con pantalla teal,
  indicador, botón, placa y texto, y una luz naranja de 8 W.
- El texto del cartel de consola se giró a vertical (`rot X = 90°`); antes
  quedaba horizontal y se veía como una línea brillante.
- La estación de café `NEXUS_L1_DIS_BREAK_*` se desplazó **−1.8 m en Y**
  (12 objetos no parentados) para despejar el frente del ascensor. Tiene
  metadatos `original_location` y `layout_fix="elevator_extraction_clear"`.
- Cámara permanente `NEXUS_V05_CAM_ExtractionElevator`, loc
  **(-17.50, 7.90, -4.22)**, target **(-17.05, 11.45, -4.45)**, lens **15**.
  El encuadre muestra el ascensor, SALIDA, el reloj, la consola, el aro y el
  texto completo.

### Verificación

- `nexus/nivel_01/NEXUS_L1_V05.blend` guardado **en sitio**: **2.389 objetos**,
  **2.559.900 bytes**, cámara guardada `NEXUS_V05_CAM_Recepcion`, sin `TMP_`.
- `NEXUS_V05_REC_PLAY`: **89 objetos**; **13** con prefijo
  `NEXUS_V05_REC_EXTRACT`. `NEXUS_V05_EXTR_` = 0; no quedan colecciones de la
  sala oeste.
- L1 medido: **1.878 mallas visibles**, **559.841 triángulos**, **48 luces
  visibles**, **22 con sombra**. El máster recargado tiene **8.063 objetos** y
  8 bibliotecas relativas sin ausencias.
- BFS con cápsula 0,38 m: alcanzables `extraction_elevator_center`,
  `extraction_elevator_zone_north`, `extraction_console_front` y
  `extraction_lobby_approach`, además de recepción, mostrador, seguridad,
  control recto, vestuarios, almacén, mantenimiento, enlace restringido y
  corredor oeste.
- Cámara de revisión final `NEXUS_V05_CAM_ExtractionElevator`:
  `(-17.50, 7.90, -4.22)`, target `(-17.05, 11.45, -4.45)`, lens 15. El cartel
  `NEXUS_V05_REC_EXTRACT_SIGN_TEXT` se giró a X=90° para que **EXTRACCION** se
  lea vertical sobre la consola; antes quedaba horizontal y parecía una línea.
- Render de revisión: `docs/fm_extraccion_ascensor_v136.png` (imagen anterior,
  lens 16 y cartel horizontal; no refleja el encuadre final porque los intentos
  de render headless reiniciaron el servidor). Los renders
  `docs/fm_extraccion_v135_room.png` y `docs/fm_extraccion_v135_door.png` se
  conservan como registro de la propuesta rechazada.
- `nexus/manifest.json` actualizado a L1 2.389 objetos / 2.559.900 B y MASTER
  8.063 / 398.478 B.

### Limitaciones y siguiente paso

El ascensor es geometría estática y no se abre; la extracción no tiene lógica
jugable, solo metadatos y marcadores visuales. Persisten las dos PNG inválidas
de `industrial_wall_lamp_1k`; no se tocaron los assets originales. Siguiente:
iluminar la escalera este y revisar el núcleo vertical, como estaba previsto.
No se exportó a Godot ni se tocó `fotos-referencia/`.

---

## 2026-11-03 15:42 COT — OpenCode — Cabina de ascensor en la extracción de recepción (v137)

### Petición

El usuario validó la ubicación de la extracción y pidió: **“me gustaria que fuera
como una simulacion de ascensor si me entiendes?”**. Eligió la opción de una
**cabina real detrás del muro**, con puertas animadas, en lugar de una simple
fachada.

### Construcción

- Se creó `blender_concept/build_elevator_simulation_v137.py` (497 líneas), con
  guard de `__main__`; se ejecutó pasando un namespace con `__name__="__main__"`.
- El muro, marco, zócalo y remate originales se conservaron ocultos en
  `NEXUS_V05_ELEVATOR_HIST` (4 objetos). Se duplicaron y se les aplicó un
  Boolean Difference para abrir un hueco de **1,88 × 2,625 m**:
  `NEXUS_V05_ELEV_SIM_WALL_N`, `..._FRAME_CUT`, `..._WAINSCOT_CUT` y
  `..._TRIM_CUT`.
- Se construyó una cabina transitable de **1,88 × 1,80 × 2,55 m** con suelo y
  techo, paredes metálicas, espejo ahumado local, pasamanos, luz de techo de
  45 W, rejilla, umbral, portal, jambas, bolsillos laterales y panel interior.
- Se animaron las hojas existentes `NEXUS_V05_C_REC_ELEV_L/R` en X:
  cerradas en frames **1 y 130**, abiertas en **45 y 105**. La escena queda
  en **1–160**. Los faldones y juntas se parentaron a cada hoja.
- El reloj se movió fuera del recorrido de la puerta, a
  **(-16.20, 11.515, -2.85)**. El llamador se adelantó a y 11.42/11.47.
- Se añadió el trigger de cabina `NEXUS_V05_REC_EXTRACT_CAB_TRIGGER` en
  **(-17.5, 12.55, -5.65)**, hijo de `NEXUS_V05_REC_EXTRACT_ZONE`, y la
  secuencia `NEXUS_V05_ELEVATOR_SEQUENCE` con los frames de apertura/cierre y
  `requires_player_inside=True`.
- El cartel de consola se desplazó **+0.20 m en X** para que no lo cortara el
  bolsillo derecho del ascensor.

### Verificación

- Archivo vivo: `nexus/nivel_01/NEXUS_L1_V05.blend`, **2.440 objetos**,
  **2.553.392 bytes**, frame 1, cámara guardada
  `NEXUS_V05_CAM_ExtractionElevator`, sin `TMP_`.
- **1.921 mallas visibles**, **560.493 triángulos**, **63 luces totales / 49
  visibles / 22 con sombra**. `NEXUS_V05_ELEVATOR` 50 objetos;
  `NEXUS_V05_ELEVATOR_HIST` 4; `NEXUS_V05_REC_PLAY` 90.
- Rayos a frame 45: el hueco deja pasar la mirada y llega al espejo de la
  cabina en y 13.62; los bolsillos laterales quedan cerrados.
- BFS con cápsula de 0,38 m: `elevator_car_center (-17.5,12.5)` y
  `elevator_car_back (-17.5,13.2)` alcanzables con **21 waypoints**; el resto
  de objetivos del Nivel 1 sigue alcanzable.
- Máster: **8.114 objetos**, 8 bibliotecas relativas sin ausencias.
  `nexus/manifest.json`: L1 2.440 objetos / 2.553.392 B; MASTER 8.114.
- Render de revisión con `look`: frame 1 cerrado y frame 45 abierto; cabina,
  espejo, pasamanos, SALIDA, reloj, consola y aro legibles.

### Limitaciones

- Las puertas y la cabina son datos de Blender: la animación no tiene
  controlador de juego ni lógica exportada. El trigger y la secuencia son
  metadatos; la extracción sigue sin implementación jugable.
- Los renders headless de este archivo reiniciaron el servidor; no reintentar.
  `docs/fm_extraccion_ascensor_v136.png` sigue siendo una imagen de v136 sin
  cabina; el render v137 se revisó en la sesión viva y no se guardó en docs.
- Persisten las dos PNG inválidas de `industrial_wall_lamp_1k`; no se tocaron
  los assets originales.

### Siguiente paso

Iluminar la escalera este del núcleo y revisar el portal L1 y el tramo; después
los portales L2–L5 y el retorno continuo a la extracción. No se exportó a
Godot ni se tocó `fotos-referencia/`. No se hicieron commits.

## 2026-11-03 16:05 COT — OpenCode — Reglas de extracción para hasta 8 jugadores (v138)

### Petición

El usuario pidió procesar la extracción recordando que el juego será online de
hasta **7 u 8 jugadores**. Se aplicó solo la definición y los metadatos; no se
cambió la geometría.

### Definición

- La zona de extracción pasa a ser la **recepción completa de 16 × 10 m**,
  centro `(-12.0, 6.7, -5.65)`, no el lobby de 2,10 × 1,50 m ni la cabina.
- Capacidad **1–8 jugadores**; la cabina es la salida visual y el aro naranja
  el marcador de salida.
- Activación: todos los jugadores conectados y vivos dentro de la recepción
  durante **2,0 s**. Secuencia total **8,7 s**: apertura 1,5 s, puertas
  abiertas 2,5 s, cierre 1,0 s y viaje visual 1,3 s.
- Extracción parcial: quien esté fuera al completar queda atrás; los abatidos
  dentro cuentan como presentes; desconectados y muertos se ignoran.
- El botín cuenta si está dentro de la recepción o lo lleva un jugador
  extraído. Recompensa única, sin duplicar objeto completo y componentes.

### Metadatos

- Nuevo empty `NEXUS_V05_REC_EXTRACT_RECEPTION_TRIGGER` en
  `(-12.0, 6.7, -5.65)`, hijo de `NEXUS_V05_REC_EXTRACT_ZONE`, con
  `zone_shape='reception_room'`, `zone_size_m=[16,10]`, `max_players=8`.
- `NEXUS_V05_ELEVATOR_SEQUENCE` queda con
  `requires_player_inside_reception=True` y `requires_cab_occupancy=False`.
- Los cinco recuperables reciben `rarity`, `size_class`, `volume_approx_l`,
  `condition`, `effects`, `disassemblable=False`, `delivery_zone` y
  `metadata_version='v138'`.

### Verificación

- Archivo vivo: `nexus/nivel_01/NEXUS_L1_V05.blend`, **2.441 objetos**,
  **2.569.121 bytes**, **1.921 mallas visibles**, **560.493 triángulos**,
  49 luces visibles y 22 con sombra. Cámara guardada
  `NEXUS_V05_CAM_ExtractionElevator`; sin `TMP_`.
- `NEXUS_V05_REC_PLAY` **91**; `NEXUS_V05_ELEVATOR` 50;
  `NEXUS_V05_ELEVATOR_HIST` 4. Solo existe un trigger de recepción.
- Máster: **8.115 objetos**, 8 bibliotecas relativas. El incremento es el empty
  del trigger.
- Script: `blender_concept/apply_extraction_rules_v138.py`, compila y guarda en
  sitio. Procedimiento: `docs/NEXUS_L1_EXTRACTION_PROCEDURE.md`.

### Limitaciones

- Son metadatos y geometría: no hay lógica de juego, inventario, transporte,
  entrega ni desmontaje implementados.
- No se ha probado una partida de 8 jugadores ni la sincronización de red.
- No se exportó a Godot. No se tocó `fotos-referencia/`. No se hicieron commits.

### Siguiente paso

Actualizar el manifiesto y el resto de documentación a v138; después continuar
con la iluminación de la escalera este del núcleo y la revisión de portales.

## 2026-11-03 17:25 COT — OpenCode — Recepción NEXUS jugable en Godot local

### Petición

El usuario pidió: **“necesito que la recepcion este completamente terminado con lo que exige el agents.md, graficos, fisicas detalles osea todo”**. Se acordó cerrar la recepción primero en Blender y luego implementarla en Godot local para 1 jugador, con arquitectura preparada para hasta 8; la sincronización completa de 8 queda fuera de este pase.

### Escena y arte

- `scenes/fm/reception_slice.tscn` + `scripts/fm/reception_slice.gd`.
- `assets/models/fm/reception_nexus.glb`: 13.446.520 B, 640 meshes, 69 imágenes WebP, 86 materiales, 2 animaciones, 14 luces. El importador no crea `.import`, pero `GLTFDocument` carga la escena en runtime (`APPEND_ERR 0`).
- La escena añade luces de recepción ajustadas, entorno, colisiones de suelo/perímetro, mostrador, mobiliario principal y cabina; 5 loot, escondite, trampa, extracción, jugador y HUD.

### Jugador, linterna y audio

- `FMPlayer` recibió gravedad; el spawn es `(-12.0, -5.60, -2.85)` y el jugador queda en `y≈-5.65`, `floor=true`.
- Se exportó `assets/models/fm/flashlight_nexus.glb` (1.272.372 B) desde `small_plastic_torch_2k` y se añadió un viewmodel de primera persona con relleno local, sin sombras. La luz de la linterna existente conserva batería y cono.
- `reception_slice.gd` detiene la música del menú y reproduce `assets/audio/ambience/ambience.wav` en bucle 3D; los pasos y la trampa siguen usando el autoload `Audio`.

### Extracción y puertas

- `FMReceptionExtraction` valida la recepción completa (16 × 10 m), 1–8 jugadores, activación 2,0 s y extracción parcial. Para activar exige todos los jugadores vivos dentro y al menos un objeto recuperado en el radio de entrega de 2,4 m.
- Secuencia total 8,7 s: 2,0 s de activación + 6,7 s de secuencia (apertura 1,5 / espera 2,5 / cierre 1,0 / viaje 1,3 / confirmación 0,4). Las puertas se abren, se cierran antes de completar y el resultado se muestra al final.
- El viewmodel de linterna y la secuencia de puertas se probaron en la escena; no son lógica de red.

### Menú y pruebas

- `scenes/menu.tscn` incluye `ReceptionButton` (“RECEPCIÓN NEXUS · NIVEL 1”); `scripts/menu.gd` usa `--reception` y carga la escena.
- `tests/fm_reception_smoke.tscn` pasa **PASS**: jugador en suelo, movimiento 1,70 m, escondite, trampa, rechazo de la caja de 42 kg, recogida, drop/repick, cierre y reapertura de puertas, extracción `RECEPTION_WON delivered=1 value=4760`.
- `godot --headless --path . --quit-after 60 scenes/menu.tscn` y la variante `-- --reception` terminan con **EXIT 0**.
- Captura de revisión 1280×720 en `/tmp/opencode/reception_godot.png`.

### Limitaciones

- Escena local de 1 jugador; la API acepta hasta 8, pero no hay red ni 8 cápsulas simultáneas.
- No hay inventario general, desmontaje, criaturas ni percepción sonora en recepción.
- El GLB se carga en runtime; no se ha generado un build final.
- Persisten las dos PNG inválidas de `industrial_wall_lamp_1k`; no se tocaron los assets originales.
- No se tocó `fotos-referencia/`; no se hicieron commits.

### Siguiente paso

Probar la recepción en ventana real y revisar el viewmodel de linterna, el audio ambiental y la secuencia de cierre del ascensor. Después continuar con la iluminación de la escalera este del núcleo y la revisión de portales; mantener pendientes Bio–Airlock, discontinuidad de Servidores y umbrales L3–L5.

## 2026-11-03 18:30 COT — OpenCode — Recepción: colisiones de props y pase visual

El usuario reportó que podía atravesar paredes y objetos y que la recepción seguía pareciendo un juego antiguo. Se trabajó solo en la recepción local de Godot, sin tocar Blender ni otros niveles.

### Cambios aplicados

- `scripts/fm/reception_slice.gd`:
  - Se añadieron colliders AABB a sillas de oficina y recepción, silla caída de oficina y corredor, papeleras, bolsa de basura, monitor caído, panel caído, cubo de limpieza, inodoro y tanque.
  - `_add_glb_aabb_collider()` reutiliza la jerarquía del GLB y crea un `StaticBody3D` por prop. Los objetos pequeños/decorativos siguen sin collider para no disparar el coste.
  - Iluminación corregida a la regla de dirección artística: **solo luces de emergencia visibles y la linterna del jugador**. Se eliminaron key/fill/downlights, los seis lentes de techo y la tira cian del mostrador. Ambiente 0.06, exposición AgX 1.15, SSAO 1.55, niebla volumétrica 0.010.
  - Se añadieron cinco luminarias de emergencia locales (ámbar/rojo) con lente emisiva visible, flicker sutil y rangos cortos; las luces generales del GLB quedaron apagadas y ocultas.
  - Se sustituyeron los dos monitores CRT del mostrador por pantallas planas con cuerpo metálico, marco, pie y pantalla emisiva teal.
  - Se añadió barrera de cristal con postes metálicos, lector de tarjetas con LED, pasacables y decals de suciedad en las paredes.
  - Se añadió una señal de emergencia **SALIDA** iluminada sobre el ascensor y se reforzó la señalización de extracción.
  - Los charcos grandes del GLB se ocultan y se sustituyen por decals de `blood_splat.png` sobre el suelo, con menor tamaño y sin sombra.
  - Se añadieron props físicos locales: tres latas, un portapapeles y una caja de cartón como `RigidBody3D`, con colisión y masa.
- `scripts/fm/fm_player.gd`:
  - El viewmodel de linterna usa materiales metálicos oscuros, lente emisiva y una posición más discreta en la esquina inferior derecha. **Dependencia compartida:** este ajuste afecta al jugador usado por la vertical slice; se documenta porque el sistema de jugador es compartido.
- `tests/fm_reception_smoke.gd`:
  - Nuevo `TEST_PROPS` con rayos contra la papelera y la jardinera.
  - Nuevo `TEST_LIGHTS` que verifica que no hay luces generales encendidas.
  - Nuevo `TEST_DEBRIS` que comprueba que una lata física cae y se asienta en el suelo.
  - `tests/fm_reception_shot.gd` fija la orientación de la cámara para capturas deterministas.

### Verificación

- `tests/fm_reception_smoke.tscn`: **EXIT 0**, `FM_RECEPTION_TEST: PASS`.
- `TEST_WALLS true`; `TEST_PROPS true bin=COL_NEXUS_L1_DIS_BIN_REC planter=COL_NEXUS_V05_REC_PLANTER_1`.
- `TEST_LIGHTS true general=0 emergency=15 flashlight=3`.
- `TEST_DEBRIS true y=-5.6006`.
- Pasan movimiento 1,70 m, escondite, trampa, rechazo de la caja de 42 kg, recogida, drop/repick, puertas y extracción `RECEPTION_WON delivered=1 value=4760`.
- Captura real determinista 1280×720 revisada: la recepción es oscura, con charcos de emergencia ámbar/rojos, haz de linterna, cartel SALIDA verde, monitores planos y barrera de cristal; sin luces generales.

### Limitaciones

- El arte continúa siendo una vertical slice: el mobiliario del GLB, las plantas y parte de los props siguen siendo simples; no hay brazos ni guantes modelados.
- Los props pequeños (papeles, vasos, cables) no tienen collider individual.
- La red de 8 jugadores, el inventario general, el desmontaje y las criaturas siguen pendientes.
- En ese momento solo la recepción estaba implementada como escena jugable en Godot; el resto del Nivel 1 seguía en Blender.
- Persisten las dos PNG inválidas de `industrial_wall_lamp_1k`; no se tocaron los assets originales.
- No se tocó `fotos-referencia/`; no se hicieron commits.

## 2026-11-03 19:40 COT — OpenCode — Nivel 1 completo jugable en Godot

Se amplió el trabajo de la recepción a **todo el Nivel 1**. El usuario pidió explícitamente no dejar una recepción bonita mientras el resto siguiera siendo un prototipo.

### Exportación y escena

- `blender_concept/export_level1_glb.py` exporta el nivel completo desde `nexus/nivel_01/NEXUS_L1_V05.blend` sin modificar el `.blend`.
- `assets/models/fm/level1_nexus.glb`: **42.507.928 bytes**, **1.940 objetos**, **530.249 triángulos**, WebP calidad 70, sin luces ni cámaras.
- Se omitieron las hojas de las puertas principales para dejar los vanos transitables; los marcos permanecen.
- `scenes/fm/level1.tscn` + `scripts/fm/level1.gd` cargan el GLB en runtime.
- Se añadió `COL_EastShutter` y el rótulo **ACCESO AL NÚCLEO // BLOQUEADO** para cerrar el extremo este, porque el núcleo es un sistema compartido fuera del alcance.

### Espacios incluidos

Recepción, oficina/aseo, corredor, seguridad, control, vestuarios, almacén, mantenimiento, conector de servicio, ascensor y compuerta este. La prueba de salas cubre **10/10**.

### Iluminación y materiales

- Solo emergencia visible y linterna: **20 luces de emergencia**, **0 generales**, 3 luces de linterna.
- Se apagaron emisivos de tiras, lámparas, tubos, paneles y trajes; se conservaron pantallas, letreros y lentes de emergencia.
- Se reemplazaron los monitores CRT de recepción, seguridad, control y oficina por pantallas planas.
- Se añadieron barrera de cristal, lector, sangre como decals y suciedad en paredes de recepción.
- Se mantuvo la oscuridad fuera de recepción; las salas tienen una o dos luces de emergencia y dependen de la linterna.

### Jugabilidad y físicas

- **515 colliders** estáticos generados desde el GLB.
- 5 loot distribuidos: seguridad, vestuarios, almacén, oficina y control.
- 3 escondites: armario de recepción, taquilla de vestuarios y estantería del almacén.
- 2 trampas de ruido: corredor y almacén.
- 9 props físicos con `RigidBody3D` (latas, portapapeles, cajas) que emiten ruido al golpearse.
- Vigilante patrullando el corredor; investiga ruidos y puede perseguir.
- Extracción con puertas animadas, HUD y audio ambiental.

### Pruebas

`tests/fm_level1_smoke.tscn`:

```text
TEST_PLAYER floor=true
TEST_LOOT 5
TEST_ROOMS 10/10
TEST_DOORS 6/6
TEST_EAST true hit=COL_EastShutter
TEST_LIGHTS true general=0 emergency=20 flashlight=3
TEST_WATCHER true patrol=6
TEST_NOISE true state=2
TEST_MOVE true
TEST_EXTRACTION true state=1 delivered=1
FM_LEVEL1_TEST: PASS
```

`tests/fm_level1_perf.tscn` a 1280×720:

```text
LEVEL1_PERF fps=272.0 draws=346 primitives=78632 objects=8122
```

Medición local de la máquina de desarrollo; no es una garantía para la GTX 1650 Ti.

### Capturas revisadas

`/tmp/opencode/level1_recepcion.png`, `corredor`, `seguridad`, `control`, `vestuarios`, `almacen`, `mantenimiento`, `oficina`, `aseo` y `level1_godot.png`.

### Limitaciones

- Las puertas principales están abiertas y son estáticas; no hay interacción de abrir/cerrar.
- Solo hay un Vigilante; Imitador, Coleccionista y Sombra no están implementados en esta escena.
- No hay red de 8 jugadores, inventario general, desmontaje ni guardado.
- El arte sigue siendo una vertical slice; algunos props del GLB son simples.
- La oficina y el aseo son espacios pequeños y su composición de cámara es mejorable.
- Persisten las dos PNG inválidas de `industrial_wall_lamp_1k`; no se tocaron los assets originales.
- No se modificaron menús, otros niveles ni sistemas de red. No se hicieron commits.

### Siguiente paso

Revisar arte y composición de todas las salas, implementar puertas interactivas locales, sonidos de pasos por superficie y otra criatura local sin tocar sistemas compartidos. Después medir en la GTX 1650 Ti y aplicar LOD/oclusión.

## 2026-11-03 20:35 COT — OpenCode — Fase 2 del Nivel 1: puertas, contenedores y recorrido continuo

El usuario pidió llevar el Nivel 1 completo desde la vertical slice a un estado de producción: calidad visual, puertas funcionales, interacciones con armarios/cajones/taquillas, más físicas y ruido, audio por sala, optimización, recorrido continuo y pruebas. Se trabajó solo en el Nivel 1 de Godot, sin tocar Blender, menús, red, guardado ni IA compartida.

### Implementado

- `scripts/fm/fm_level1_door.gd`: puertas locales de doble cara con panel, ventana teal, manilla, patada, bisagras, franja de peligro, colisión, tween de 95° y ruido. Se colocaron 6: recepción, seguridad, control, almacén, vestuarios y mantenimiento. Las hojas estaban excluidas del GLB; ahora se crean y controlan localmente.
- `scripts/fm/fm_level1_drawer.gd`: 8 cajones deslizantes (3 oficina, 3 seguridad, 2 mostrador), con ruido y sonido.
- `scripts/fm/fm_level1_locker.gd`: 4 taquillas abatibles en vestuarios, con rejillas, manilla y etiqueta NEXUS.
- `scripts/fm/fm_level1_alarm.gd`: 3 paneles de alarma remota en el corredor; generan ruido a 20 m en almacén, seguridad o mantenimiento, con recarga de 15 s.
- `scripts/fm/level1.gd`: llamadas a los nuevos sistemas, 12 props físicos adicionales, ambientes 3D por sala, lámparas locales y 4 charcos húmedos.
- `tests/fm_level1_smoke.gd`: pruebas de puertas cerradas/abiertas, cajón, taquilla y alarma.
- `tests/fm_level1_walk.gd/.tscn`: recorrido continuo por waypoints con el controlador real.
- `tests/fm_level1_rooms_shot.gd`: encuadres corregidos de control, mantenimiento, oficina y aseo, más vista de puerta cerrada.

### Pruebas

- `tests/fm_level1_smoke.tscn`: **PASS**; `TEST_DOORS_CLOSED 6/6`, `TEST_DOORS_OPEN 6/6`, `TEST_DRAWER true`, `TEST_LOCKER true`, `TEST_ALARM true`, `TEST_LIGHTS general=0 emergency=30`, `TEST_EAST true`, `TEST_EXTRACTION true`.
- `tests/fm_level1_walk.tscn`: **PASS**, `WALK_RESULT reached=33/33`, salida de recepción, todas las salas y retorno a la extracción sin teletransportes.
- `tests/fm_level1_perf.tscn`: **265 FPS, 582 draw calls, 124.892 primitivas, 8.629 objetos** a 1280×720 en la máquina de desarrollo. No es una medición de la GTX 1650 Ti.

### Capturas

- `docs/fm_level1_phase2_rooms.png`
- `docs/fm_level1_phase2_door.png`
- `docs/fm_level1_phase2_reception.png`
- `docs/fm_level1_phase2_corridor.png`

### Limitaciones

- Un solo Vigilante; Imitador, Coleccionista y Sombra siguen fuera de alcance.
- Sin red de 8 jugadores, inventario general, desmontaje, guardado ni build final.
- Sin pasos por material: el jugador compartido usa un único `step.wav`.
- Varios props del GLB siguen siendo simples; no se reconstruyó el arte.
- El recorrido se hizo con las puertas abiertas por código; la apertura manual se prueba en el smoke test, no en una partida humana completa.
- No se probó en la GTX 1650 Ti.
- Persisten las dos PNG inválidas de `industrial_wall_lamp_1k`; no se tocaron los assets originales.
- No se hicieron commits.

### Siguiente paso

Revisión artística de detalle por sala, pasos por material, prueba en la GTX 1650 Ti y LOD/oclusión. Mantener fuera de alcance el núcleo, menús, red y sistemas compartidos.

---

## 2026-11-03 21:20 COT — OpenCode — Fase 3 del Nivel 1: atmósfera, postprocesado y decals

Se cerró la Fase 3 local del Nivel 1 en Godot, sin tocar otros niveles, menús, red ni sistemas compartidos.

- **Postprocesado:** `assets/shaders/fm_postprocess.gdshader` con aberración 0.00045, contraste 1.02, saturación 1.0, grano 0.022 y viñeta 0.26, bajo el HUD.
- **Entorno:** ambiente 0.075, exposición 1.16, contraste 1.08, saturación 1.0, SSAO 1.6, glow 0.5, niebla volumétrica 0.010 y SSR 32 pasos.
- **Atmósfera:** tiras teal de guiado en el corredor, polvo (160 partículas) y vapor en mantenimiento (42).
- **Decals:** 22 decals con `blood_splat`, `blood_trail`, `puddle`, `grunge_decal`, `grime_decal` y `glass_crack`, sin colisión, alfa 0.24–0.55 y distance fade 14/6 m, repartidos por todas las salas.
- **Pruebas:** smoke **PASS** (`LEVEL1_READY loot=5 colliders=515`); walk **PASS** (`WALK_RESULT reached=33/33`, final `(-17.23691,-5.64919,-9.919388)`); perf **186 FPS, 1037 draws, 187.620 primitivas, 8.768 objetos** a 1280×720 en desarrollo.
- **Capturas:** recepción y corredor legibles; atmósfera roja, escombros, charcos y señalización. Salas oscuras pero transitables.
- **Limitaciones:** un Vigilante; sin red/inventario/desmontaje/guardado; arte de vertical slice; sin build final ni GTX 1650 Ti; dos PNG inválidas de `industrial_wall_lamp_1k`; no se hicieron commits.
- **Siguiente paso:** medir y optimizar el coste de los decals/draw calls, probar en GTX 1650 Ti y continuar el detalle artístico localizado.

---

## 2026-11-03 22:40 COT — OpenCode — Fase 3A: recepción y corredor

Intervención artística limitada a la recepción NEXUS y el corredor principal. No se modificó el `.blend` ni el GLB; el pase es runtime en Godot.

- **Módulo:** `scripts/fm/fm_level1_art_pass.gd`, llamado desde `scripts/fm/level1.gd` después de `_setup_postprocess()` y antes de `level_ready`.
- **Entorno:** HDRI `abandoned_workshop_2k`, ambiente 0.22, exposición 1.34, SSIL, SSR 40 pasos, SSAO 1.25, glow 0.32, niebla volumétrica 0.012, dos reflection probes.
- **Luces:** 17 luces `ART_` (recepción y corredor), emergencias reducidas al 52 %; solo la clave de recepción mantiene sombra dinámica.
- **Materiales:** 31 overrides PBR; texturas 2K de hormigón, yeso, pared de fábrica, metal oxidado, pintura verde, madera y paneles; suelo `concrete_floor_01` gris con clearcoat; 10 PNG de normal/roughness generados en `assets/art/fm/generated/` desde EXR locales.
- **Geometría:** costillas y remates del mostrador, banda de listones, luminaria lineal, mampara pequeña, paneles y servicios de techo; en corredor, bandeja de cables, tuberías, conducto, columnas con colliders, vigas, marcos de puertas, paneles, tornillería, luminarias y tiras frías.
- **Capturas:** `docs/fm_level1_phase3a_before_after.png`, `_reception`, `_counter`, `_logo`, `_corridor`, `_corridor_detail`.
- **Pruebas:** smoke **PASS** (`general=0 art=17 emergency=30 flashlight=3`); walk **PASS 33/33**; perf **110 FPS, 796 draws, 221.484 primitivas, 8655 objetos** a 1280×720 en desarrollo. Antes: 186 FPS, 1037 draws, 187.620 primitivas, 8768 objetos.
- **Luminancia:** recepción 0.056→0.124; corredor 0.048→0.139.
- **Limitaciones:** no se alcanzó el estándar comercial final; cristal del mostrador y conducto claro existente siguen dominando; faltan LOD real/occlusion y prueba en GTX 1650 Ti; viewmodel de linterna pendiente; licencias de assets sin confirmar.
- **Siguiente:** revisar capturas y aprobar/rechazar la base antes de extenderla al resto de habitaciones.

---

## 2026-11-03 23:20 COT — OpenCode — Fase 3A.1: kit de Blender para recepción y corredor

Se continuó la Fase 3A con geometría y materiales fuente en Blender, limitado a recepción y corredor.

- **Fuente:** `blender_concept/build_art3a1_kit.py`, `blender_concept/ART3A1_kit.blend`.
- **GLB:** `assets/models/fm/art3a1/level1_art3a1_kit.glb` (~3,9 MB, 274 objetos fusionados en 8 mallas por material).
- **Contenido:** mostrador/cristal de recepción, dos conductos de 10 m con bridas/rejillas/soportes y módulos de pared con costillas, rejillas, cajas y tornillería.
- **Integración:** `fm_level1_art_pass.gd` carga el kit con `GLTFDocument`, conserva luces/HDRI/probes y retira del runtime el mostrador/ducto/paneles procedurales duplicados. Se añadió `NEXUS_V05_MAT_Sign_Battery` oscuro, que corrigió el panel claro de recepción.
- **Capturas:** `docs/fm_level1_phase3a1_before_after.png` y derivadas `_reception`, `_counter`, `_logo`, `_corridor`, `_corridor_detail`, `_corridor_back`. Regeneradas después del último cambio del kit.
- **Pruebas:** smoke **PASS** (`ART3A1_KIT loaded`, `TEST_LIGHTS general=0 art=17`); walk **PASS 33/33**; perf **108 FPS / 814 draws / 406.748 primitivas / 8.683 objetos** a 1280×720 en desarrollo. Fase 3A: 110 FPS / 796 draws / 221.484 primitivas / 8.655 objetos.
- **Documento:** `docs/NEXUS_L1_PHASE3A1_ART.md`.

### Volumen claro del corredor: causa identificada y mitigada

El bloque claro de la zona alta del corredor se atribuyó a dos fuentes, no a una sola:

1. Los cuatro `NEXUS_V05_OFFICE_PARAPET_0..3` (material `NEXUS_V05_MAT_Rec_Ceiling`) del GLB original. Ahora se ocultan todos en `_load_kit()` con `find_children("*OFFICE_PARAPET*", "", true, false)`.
2. El propio conducto del kit, demasiado bajo y con material claro. En `build_art3a1_kit.py` se elevó **+0.23 m en Y y +0.20 m en Z de Blender**, se redujo de 0,55×0,38 a **0,48×0,32** y se le dio `ART3A1_DuctPaint` (0,045 / 0,085 / 0,070, metallic 0,12, rough 0,72).

Además se añadieron bulkheads simétricos en **z ±1,52** y revestimiento de servicio en **z ±1,40** sobre el acceso. En la última captura revisada el bloque claro ya no domina la esquina superior izquierda, pero **la confirmación visual final es del usuario**.

### Handoff para el siguiente modelo

**Estado:** Fase 3A.1 integrada y probada; recepción y corredor son las únicas zonas tocadas. Todo sin commit.

**Qué falta, en orden:**

1. **Refinar los módulos de pared del kit** (x ±8,7): en primer plano se ven demasiado grandes, planos y repetitivos. Reducir ancho/alto, añadir profundidad real (marco hacia fuera, panel hundido, costillas), variar la composición entre módulos y revisar que no tapen puertas ni señalización. Tocar `blender_concept/build_art3a1_kit.py` y reconstruir el GLB; no editar el GLB a mano.
2. **Revisar el conducto en vista cercana**: comprobar que las rejillas miren al pasillo y que las bridas/soportes no floten tras el desplazamiento.
3. **Confirmar el volumen claro** con una captura nueva desde el spawn mirando al acceso; si reaparece, hacer raycast y comparar contra `NEXUS_V05_RECEPCION_WALL_S_B` y los parapetos antes de añadir más cajas.
4. **Medir de nuevo** smoke/walk/perf y actualizar cifras.
5. **Detenerse** para aprobación del usuario antes de tocar otras salas.

**Comandos:**

```bash
# Reconstruir el kit desde Blender
/opt/blender/blender --background --factory-startup \
  --python blender_concept/build_art3a1_kit.py --python-exit-code 1

# Carga de la escena
godot --headless --path . --quit-after 5 scenes/fm/level1.tscn

# Pruebas
godot --headless --path . tests/fm_level1_smoke.tscn
godot --headless --path . tests/fm_level1_walk.tscn
godot --path . --audio-driver Dummy tests/fm_level1_perf.tscn

# Capturas (requiere sesión gráfica)
DISPLAY=:0 godot --path . --audio-driver Dummy tests/fm_level1_art_shots.tscn
```

**Mapeo de coordenadas Blender → Godot del kit:** `Godot = (bx, bz, -by)`. Ejemplo: el conducto se autoría en Blender `y=1.38, z=-2.00` y aparece en Godot en `y=-2.00, z=-1.38`. Tenerlo en cuenta al mover piezas del kit.

**Archivos que no se tocaron en esta fase:** `nexus/nivel_01/NEXUS_L1_V05.blend` (mtime 16:23) y `assets/models/fm/level1_nexus.glb` (mtime 19:29), ambos anteriores al trabajo de 3A.1. El kit es un GLB aparte. Nota: `git status` marca el `.blend` como modificado por trabajo de fases previas, no por 3A.1.

**Limitaciones reales:** el kit añade ~185k primitivas y 18 draw calls (108 FPS vs 110 de la Fase 3A en desarrollo); no hay LOD ni occlusion culling; no se probó en la GTX 1650 Ti ni en build final; el viewmodel de linterna sigue pendiente; los módulos de pared necesitan la segunda iteración descrita arriba.

---

## 2026-11-04 00:45 COT — OpenCode — Fase 3A.2: Nivel 1 completo

Se completó la pasada integral del Nivel 1 (10 zonas funcionales), conservando el GLB original y la lógica de juego.

- **Auditoría:** `docs/NEXUS_L1_MISSION_AUDIT.md` con inventario de recepción, corredor, seguridad, control, vestuarios, almacén, mantenimiento, oficina, aseo y conector/ascensor; medidas, contenido, iluminación, colisiones, problemas y estado.
- **Blender:** `blender_concept/build_level1_dressing.py` → `LEVEL1_DRESSING.blend` (1.327 objetos de origen, 10 mallas) → `assets/models/fm/art3a2/level1_dressing.glb` (~12,9 MB). Incluye vigas, costillas, zócalos, cajas de servicio, conductos, lámparas de jaula, dinteles, directorio, consola, racks, listones y rejillas.
- **Props:** `blender_concept/export_props.py` exportó 15 GLB a `assets/models/fm/props/` con texturas a 1K; 34 instancias en el nivel (plantas, archivadores, estanterías, cámaras, alarmas, botiquines, taburetes, barriles, cajas, microscopio y radio).
- **Integración:** `fm_level1_art_pass.gd` carga ambos kits, oculta parapetos y tiras de sala, corrige linteles/`_ABOVE_`, generador, espejos y pantallas, atenúa luces fuera de recepción y añade 17 colliders nuevos.
- **Correcciones:** volumen claro del corredor, paneles blancos flotantes, módulos de pared, mostrador/cristal, panel NEXUS, lámpara de vestuarios, plantas low-poly, salas vacías, espejos blancos y caída de FPS por texturas de props (36 → 108 FPS (medición previa a los rellenos fríos; 103–107 final)).
- **Capturas:** 34 vistas con y sin linterna en `/tmp/opencode/final_*.png`; copias y hoja de contacto en `docs/fm_level1_art3a2_*.png`; comparativa `docs/fm_level1_art3a2_before_after.png`.
- **Pruebas:** smoke **PASS** (`TEST_LIGHTS general=0 art=23 emergency=30 flashlight=3`, `FM_LEVEL1_TEST: PASS`); walk **PASS 33/33** (`final=(-17.2377,-5.649179,-9.92019)`); detalle **PASS 5/5** (14 `PropCollider`); perf **103–107 FPS / 1.255 draws / 886.246 primitivas / 9.089 objetos** a 1280×720 en desarrollo.
- **Limitaciones:** props de biblioteca simples, pantallas placeholder, sin LOD/occlusion, sin prueba en GTX 1650 Ti ni build final, warnings de RIDs al cerrar por GLB runtime. Se aprueba como vertical slice industrial estilizado, no como arte final AAA.
- **Documento maestro:** `docs/NEXUS_L1_MISSION_REPORT.md`.

---

## 2026-11-04 10:56 COT — OpenCode — Fase 3A.3: sistema de puertas del Nivel 1

Se rediseñaron y expandieron las seis puertas del Nivel 1 con geometría de Blender y lógica data-driven, preservando el arte aprobado de 3A.2 y sin tocar el GLB jugable ni el `.blend` original.

- **Auditoría previa:** las seis puertas eran idénticas, procedurales, sin cerraduras, alerta, energía, cooperación, audio 3D ni red. El GLB solo aportaba jambas y dinteles; no había hojas estáticas duplicadas.
- **Kit:** `blender_concept/build_level1_doors.py` → `blender_concept/LEVEL1_DOORS.blend` (589 objetos) → `assets/models/fm/doors/level1_doors.glb` (~5,3 MB, 116 mallas fusionadas). Jerarquía `DOOR_KIT_<ID>` con `Frame`, `LeafA`, `LeafB`, `Status`, `Sensor`, `Keypad`, `Manual`.
- **Diseño:** recepción automática de doble hoja de cristal con sensor; seguridad blindada con teclado `0451` y pista rotulada; control de doble hoja secuencial (A y B en 7 s); almacén corredera pesada para 2 operadores, con liberación en solitario manteniendo E 4 s; vestuarios ligera con panel esmerilado; mantenimiento con rejilla pequeña y liberación manual roja.
- **Lógica:** `scripts/fm/fm_level1_door.gd` reescrito (carga única del GLB, pivotes, colisión por hoja, audio 3D, estados, teclado, alerta, energía, cooperación, `get_network_state`/`apply_network_state`). `scripts/fm/level1.gd` configura las puertas, añade `set_red_alert`, `get_door_states`, `apply_door_states` y `F9` de desarrollo. Se ocultó el decal `NEXUS_V05_D_CORR_WALLSTAIN_0`.
- **Pruebas:** smoke **PASS** (`TEST_DOORS_CLOSED 6/6`, `TEST_DOORS_OPEN 6/6`, `TEST_LIGHTS general=0 art=23 emergency=30 flashlight=3`); walk **PASS 33/33**; `tests/fm_level1_doors.tscn` **PASS** (`DOOR_TEST_FAILS 0`); 14 capturas con `tests/fm_level1_door_shots.tscn`.
- **Rendimiento:** 99–101 FPS / 1.281 draws / 906.482 primitivas / 9.603 objetos a 1280×720, frente a 103 FPS / 1.255 / 886.246 / 9.089 de 3A.2. Coste ~4 FPS, +26 draws y +20k primitivas. El test de rendimiento desactiva al Vigilante para evitar que el overlay de detección distorsione la medición.
- **Documentación:** `docs/NEXUS_L1_DOOR_AUDIT.md`; `docs/fm_level1_doors_contact_sheet.png`, `docs/fm_level1_doors_before_after.png` y `docs/fm_level1_door_*.png`.
- **Limitaciones:** `level1.gd` sigue offline; no hay RPCs de puertas ni prueba con dos clientes reales, solo serialización y late join simulado. La alerta roja no está enlazada a las alarmas existentes. Código `0451` fijo de demo. Sin LOD/occlusion ni prueba en GTX 1650 Ti. El panel esmerilado de vestuarios sigue muy claro por la luz de la sala.
- **Siguiente paso:** conectar el estado de puertas al futuro transporte host-autoritativo, enlazar alerta y alarmas, sustituir el código fijo por tarjetas/documentos, añadir LOD y medir en GTX 1650 Ti.

---

## 2026-11-04 17:12 COT — OpenCode — Corrección integral del Nivel 1 (P0–P3)

Se ejecutó la fase de corrección de `docs/FM_LEVEL1_FULL_TECHNICAL_AUDIT.md` sobre las doce zonas del Nivel 1. Informe completo: `docs/FM_LEVEL1_CORRECTION_REPORT.md`.

- **P0 cerrado:** CR-01 extracción con botín transportado (deduplicado por instancia), CR-02 hojas del ascensor con `AnimatableBody3D` sincronizados y CR-03 triplanar métrico en arquitectura. Prueba específica `/tmp/opencode/final_p0.gd` **PASS** (`P0_ELEV_SYNC true -> false`, `P0_CARRY_INSIDE count=1`, `P0_CARRY_OUTSIDE count=0`).
- **Materiales:** pared `concrete_wall_*` en lugar de `worn_plaster_wall`; normales/roughness originales de metal verde/oxidado convertidas desde EXR; mipmaps y compresión S3TC (147 albedos); sin clearcoat global de suelo; silla/escritorio sin override; `DOOR_Rust` con normal/roughness; agua, esquirlas, espejos y pantallas corregidos; doble cristal del mostrador eliminado; `NEXUS_V05_MAT_Pipe_Red` corregido; charcos unificados.
- **Iluminación/geometría:** rellenos fríos, 30 luminarias de emergencia con carcasa y suspensión (6 con sombra), pantallas de interfaz, muro de 6 monitores de Seguridad, generador `industrial_generator.glb` (26.419 tris) y caldera con 42 remaches, volante y placa.
- **Físicas:** damping y `PhysicsMaterial` en props y botín; 511 colliders; sin tocar el sistema general de puertas.
- **Pruebas:** smoke **PASS** (`TEST_LIGHTS true general=0 art=24 emergency=30 flashlight=3`, `TEST_EXTRACTION true delivered=1`); walk **PASS 33/33**; puertas **PASS** (`DOOR_TEST_FAILS 0`); materiales 371 únicos, 20 triplanares, **0 sin mipmaps**.
- **Rendimiento:** 59–78 FPS / 817 draws / 704.584 primitivas / ~10.000 objetos a 1280×720 (mediciones inestables). Ventana 1920×1080: 28–35 FPS (viewport lógico 1280×720 con stretch). VRAM ~3,7 GB/4 GB. No se recuperó el baseline de 99–101 FPS; faltan LOD, occlusion y perfiles.
- **Capturas:** 34 vistas nuevas en `/tmp/opencode/final_*.png`; principales en `docs/fm_level1_correction_*.png` y comparativa `docs/fm_level1_correction_before_after.png`.
- **Pendientes:** AL-09 sombras de contacto, AL-13 conector, AL-15 identidad de puertas, AL-19 cuerpos estáticos de puertas, AL-20 LOD/occlusion, ME-15 topología, ME-16 física completa, BA-04 RIDs, export/build y multijugador real. No se hicieron commits.

---

## 2026-11-04 — Implementación P0–P3 y corrección de puertas del Nivel 1

Se pasó de la auditoría a la implementación directa sobre los sistemas existentes. Informe detallado: `docs/FM_LEVEL1_CORRECTION_REPORT.md`, sección 16.

- **Puertas (P0 obligatorio):** causa confirmada en `fm_player.gd::_has_line_of_sight`: el rayo impactaba el collider de la propia puerta. Se excluyen el jugador y los colliders del candidato. Las 6 puertas se probaron con interacción real; la pesada de almacén completa hold de 4,00017 s, abre, deja pasar una esfera de 0,28 m y vuelve a bloquear al cerrar. `tests/fm_level1_doors.tscn` PASS (`DOOR_TEST_FAILS 0`); smoke puertas 6/6 cerradas y abiertas.
- **Iluminación (P0):** ambiente 0.035, sky 0.45, exposición 1.05; eliminados 8 `ART_Corridor*` y 7 `ART_RoomFill_*`; 14 emergencias de 0.15–0.374 con una sombra; 9 luces de recepción. Capturas finales 24 en `docs/fm_level1_p2_lights/`. Fuera de recepción, luminancia off ≤2.47 salvo ascensor 13.29 (señalización/extraction).
- **P1 visual/funcional:** viewmodel de linterna corregido; espejos con roughness 0.22/0.38; SALIDA duplicada eliminada; dos pantallas de control nuevas y legibles; props PBR corregidos (8 materiales); sombras de contacto en muebles grandes; monitor de suelo que bloqueaba oficina retirado; walk ampliado a **44/44 PASS** con oficina y aseo.
- **Rendimiento (P2):** 1920×1080 **56 FPS**, 770 draws, 1.630.128 primitivas, 9.901 objetos, VRAM 3232 MiB; 1280×720 **107 FPS**, 1124 draws. Se corrigió el error `detect_alpha()` sobre imágenes comprimidas. Sin LOD/occlusion ni perfiles; no se cumplen <500 draws ni <5.000 objetos.
- **Build (P3):** cargas de imagen migradas a `res://`; no hay `export_presets.cfg` ni plantillas de exportación instaladas, por lo que no se generó build. GLB/HDR/PNG runtime deben incluirse en el preset.
- **Pruebas:** smoke PASS (`TEST_ROOMS 10/10` con el defecto conocido de rayos en oficina/aseo; suelos validados aparte), doors PASS, walk 44/44, escondites 3/3 y linterna drenaje/recarga PASS.
- **Limitaciones:** conector verificado por sonda desde almacén, no en recorrido completo; acceso desde mantenimiento bloqueado por hoja estática; Vigilante completo y dos clientes reales sin probar; deuda visual de cajas, caldera, estanterías y placa del corredor. No se hicieron commits.

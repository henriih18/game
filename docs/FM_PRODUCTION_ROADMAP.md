# FRECUENCIA MUERTA — Hoja de ruta de producción

Estado: **propuesta para aprobación**. No autoriza todavía a reconstruir habitaciones, crear criaturas ni modificar masivamente el nivel.

Documentos relacionados:

- `AGENTS.md` — identidad, visión y reglas del juego.
- `docs/FM_PRODUCTION_PIPELINE.md` — flujo Blender → Godot, herramientas y controles.
- `docs/FM_QUALITY_STANDARD.md` — criterios objetivos de aprobación.
- `docs/FM_LEVEL1_FULL_AUDIT.md` — estado real y deuda del Nivel 1.
- `docs/FM_TOOLS_AND_SKILLS_AUDIT.md` — capacidades y limitaciones de las herramientas.

---

## 1. Objetivo de la fase

Pasar de un nivel que funciona a un **pipeline de producción repetible**, capaz de producir una habitación con calidad comercial y, después, replicar el proceso sin reconstruir todo el juego.

La unidad de avance no es “terminar el Nivel 1”. La unidad es:

> **Una habitación piloto aprobada con evidencia visual, funcional y de rendimiento.**

Solo después se autoriza ampliar el alcance.

---

## 2. Principios de ejecución

1. **Calidad antes que cantidad.** Una sala excelente vale más que doce salas prototipo.
2. **Una sola fuente de verdad.** `AGENTS.md` manda sobre cualquier atajo técnico.
3. **Nada se declara terminado sin evidencia.** Capturas, métricas, pruebas y QA.
4. **El asset nace en Blender, no en un script de Godot.** Los scripts automatizan, no sustituyen modelado, UV, textura, rig o animación.
5. **El importador nativo de Godot es la vía principal.** Los GLB nuevos se importan como recursos, no se cargan con `GLTFDocument` en runtime.
6. **No se toca una sala sin baseline.** Antes de modificarla se captura y se mide.
7. **Los cambios son reversibles.** Ramas/versiones de `.blend`, presets y escenas; nunca sobrescribir referencias.
8. **Licencias primero.** Ningún asset externo entra en una build sin procedencia y licencia documentadas.
9. **El multijugador no se asume.** Lo que no se haya probado con dos clientes no está sincronizado.
10. **La oscuridad es diseño, no ausencia de luz.** Fuera de recepción, la linterna es la herramienta principal de lectura.

---

## 3. Línea base actual

| Área | Estado comprobado |
|---|---|
| Motor | Godot 4.7.2, Forward+, 1280×720 lógico |
| Nivel | 12 zonas; `level1.tscn` + `level1.gd` + `fm_level1_art_pass.gd` |
| Carga | GLB en runtime con `GLTFDocument`; sin `.import` de GLB |
| Puertas | 6/6 abren/cierran; puerta pesada verificada; walk 44/44 |
| Iluminación | P0 aplicado; fuera de recepción oscuro; recepción/extracción excepción |
| Rendimiento | 1080p 56 FPS, 770 draws, 1,63 M primitivas, VRAM ~3,23 GB; 720p 107 FPS |
| Optimización | Sin LOD, sin occlusion, sin perfiles de calidad |
| Assets | 539 `.blend`; máster con 2.217 mallas; 1.675 sin UV; 222 assets Poly Haven sin licencia verificada |
| Criaturas | Geometría procedural en Godot; sin rig, sin animaciones |
| Audio | 14 WAV heredados de otro proyecto; sin buses ni diseño sonoro propio |
| Build | Sin `export_presets.cfg`; plantillas de exportación ausentes |
| Multijugador | Sin prueba de dos clientes reales |

Esta línea base es la referencia. Cualquier mejora debe demostrarse contra ella.

---

## 4. Fases

### FASE 0 — Aprobación y preparación (sin producir contenido)

**Objetivo:** cerrar las decisiones que condicionan todo el pipeline.

Entregables:

- Aprobación de `FM_PRODUCTION_PIPELINE.md`.
- Aprobación de `FM_QUALITY_STANDARD.md`.
- Aprobación de esta hoja de ruta.
- Aprobación de la sala piloto: **Mantenimiento / Sala de máquinas**.
- Autorización expresa para instalar plantillas de exportación de Godot si faltan.
- Política de licencias: solo assets con licencia verificada; los 222 Poly Haven se revisan antes de distribución.
- Baseline del piloto: capturas off/on, medición de FPS/VRAM/draws, inventario de objetos y colliders.
- Prueba de importación nativa de un GLB pequeño en Godot, sin tocar el nivel jugable.

Criterios de salida:

- Documentos aprobados.
- Baseline archivado.
- Importación nativa validada en una escena de prueba.
- Ninguna sala modificada todavía.

Riesgo principal: empezar a modelar sin haber aprobado escala, presupuesto y criterios.

---

### FASE 1 — Habitación piloto: Mantenimiento

**Objetivo:** demostrar el pipeline completo en una sola sala.

#### 1.1. Diagnóstico y brief

- Levantar el estado actual de la sala: geometría, generador, caldera, tuberías, bancada, tablero, luces, colliders, audio y objetos interactivos.
- Capturas de referencia del estado actual y de la dirección artística.
- Brief de la sala: función, historia, materiales, paleta, iluminación, sonidos, riesgos y objetos.
- Lista de assets nuevos/reutilizados y presupuesto de triángulos/texturas.

#### 1.2. Bloqueo y escala

- Verificar la escala contra `AGENTS.md`: jugador, puertas, pasillos, criaturas.
- Revisar accesos, espacio de maniobra y colisiones.
- Corregir solo lo necesario; no reorganizar la instalación completa.

#### 1.3. Producción Blender

- Arquitectura: limpieza de la sala, biseles, paneles, uniones y desgaste.
- Generador industrial fijo: geometría propia, no el EN2500 portátil.
- Caldera: cuerpo, bridas, remaches, válvulas, placa y etiqueta integrada.
- Tuberías, soportes, válvulas, bancada, tablero y extintor.
- Props narrativos: herramientas, trapos, latas, documentación y residuos.
- Retopología y UV de los assets nuevos.
- Materiales PBR y texturizado: metal oxidado, pintura, goma, hormigón, agua.
- Baking de normales/AO/ORM cuando haya high-poly.
- Colisiones: proxies nombrados `COL_`, convex hull o primitivas.
- LOD0/LOD1/LOD2 para los assets grandes.
- QA de Blender: topología, normales, escala aplicada, UV, materiales y colisiones.
- Export glTF con `export_apply`, Y-up, sin cámaras/luces, incluyendo extras.

#### 1.4. Integración Godot

- Importación nativa del GLB, con presets y nombres correctos.
- Materiales y texturas importados; sin rutas absolutas.
- Colisiones y masas; objetos apoyados y estables.
- Iluminación local de terror: fuente visible, emergencia débil, sin rellenos.
- Audio: maquinaria, vapor, crujidos, pasos metálicos y reverberación.
- Interacción por mirada + distancia + línea de visión.
- Prueba de linterna, sombras y lectura en oscuridad.
- Medición de FPS/VRAM/draws con la sala y con el nivel.

#### 1.5. Puerta de aprobación del piloto

El piloto se aprueba solo si cumple:

- Criterios de `FM_QUALITY_STANDARD.md`.
- Capturas off/on y comparación con baseline.
- 1080p ≥45 FPS y 720p ≥55 FPS en la sala.
- Sin objetos flotantes, z-fighting, normales invertidas ni colisiones incoherentes.
- Sin luces sin fuente visible.
- Audio posicional y ambiental audible y coherente.
- Interacción completa: mirar, acercarse, abrir/accionar, feedback.
- Documentación de activos, licencias y decisiones.

Si falla, se corrige antes de replicar el pipeline.

---

### FASE 2 — Replicación controlada del pipeline

**Objetivo:** aplicar lo aprendido sin reconstruir las doce salas a la vez.

Orden recomendado, por dependencia y valor:

1. **Almacén** — props, cajas, estanterías, oscuridad y física.
2. **Oficina y aseo** — salas pequeñas, narrativa ambiental, espejos, materiales.
3. **Recepción y extracción** — zona héroe, iluminación funcional, mostrador, carteles.
4. **Corredor principal** — kit modular, ritmo de luces, puertas y señalización.
5. **Seguridad y control** — pantallas, monitores, mobiliario técnico.
6. **Vestuarios** — taquillas, señalización, humedad.
7. **Conector de servicio** — estrechez, tuberías, trampas, accesos.
8. **Ascensor** — puertas, señalización, espejo, transición.

Regla: cada sala se termina y aprueba antes de pasar a la siguiente. No se abre un frente nuevo para “avanzar más rápido”.

Criterios de salida por sala:

- Baseline y capturas finales.
- Assets con UV/PBR/LOD/colisión.
- Iluminación conforme a la regla de oscuridad.
- Audio y navegación.
- Pruebas de puertas, props, interacción y rendimiento.
- Sin regresiones en las salas ya aprobadas.

---

### FASE 3 — Criaturas y personajes

**Objetivo:** sustituir las cápsulas procedurales por criaturas con diseño, rig y animación.

Orden:

1. **El Vigilante** — prueba de escala grande, rig, animación de acecho/persecución y congelación al ser observado.
2. **El Imitador** — requiere voces, radio y engaño; depende del sistema de audio/comunicación.
3. **El Coleccionista** — requiere objetos, inventario y robo; depende de sistemas de loot.
4. **La Sombra** — requiere oscuridad, aparición y aislamiento; depende de iluminación y sigilo.

Por criatura:

- Modelo esculpido y de alta resolución.
- Retopología, UV y texturas PBR.
- Rig validado y pesos.
- Animaciones: idle, patrol, investigate, chase, attack, stun, death.
- LODs y colisión.
- IA propia, percepción y sonidos.
- Prueba en una sala aprobada y después en el nivel.

Criterios de salida:

- Silueta reconocible y fiel a `modelos-referencia.png`.
- Sin T-pose, sin deslizamiento, sin pies flotando.
- Comportamiento distinguible de las otras criaturas.
- Rendimiento dentro del presupuesto.

---

### FASE 4 — Sistemas de gameplay

**Objetivo:** consolidar los sistemas que sostienen la experiencia.

Orden:

1. Interacción por mirada/LOS y feedback.
2. Inventario, peso/volumen, carry/drop y desmontaje.
3. Escondites y detección.
4. Extracción en recepción y entrega de botín.
5. Resistencia, heridas, estrés y auxilio.
6. Herramientas de supervivencia y baterías.
7. Eventos dinámicos y trampas ambientales.

Cada sistema debe tener:

- Prueba funcional reproducible.
- Prueba de regresión.
- Integración con audio, criaturas y UI.
- Estado de red definido antes de implementar multijugador.

---

### FASE 5 — Audio y comunicación

**Objetivo:** pasar de SFX heredados a identidad sonora propia.

- Buses: Master, Music, SFX, Ambience, UI, Voice, Radio.
- Audio 3D, atenuación, oclusión y reverberación por sala.
- Pasos por material, maquinaria, vapor, crujidos y goteo.
- Identidad sonora de cada criatura.
- Radio, interferencia y comunicación por proximidad.
- Voces del Imitador con consentimiento y privacidad.
- Mezcla, loudness y pruebas en auriculares/altavoces.

Criterio de salida: una escena de persecución comprensible solo por audio.

---

### FASE 6 — Multijugador y persistencia

**Objetivo:** sincronizar lo que ya funciona en local.

- Autoridad del servidor.
- Sincronización de jugadores, puertas, objetos, criaturas y extracción.
- Reconexión y gestión de desconexiones.
- Prueba real de dos clientes, no simulada.
- Soak test de 10 minutos.
- Persistencia de misión e inventario.

No se declara sincronizado nada que solo se haya probado en una instancia.

---

### FASE 7 — Build, optimización y producción

**Objetivo:** convertir el proyecto en un juego distribuible.

- Instalar/verificar plantillas de exportación (con autorización).
- Crear `export_presets.cfg` Linux/Windows.
- Incluir GLB/HDR/PNG o migrar a recursos importados.
- Exportar release y probar en carpeta limpia.
- Perfiles Bajo/Medio/Alto/Ultra y render scale.
- LOD, occlusion, batching y presupuestos.
- Pruebas de arranque, carga de nivel, texturas, linterna, extracción.
- Build de demostración y checklist de release.

Criterio de salida: build que arranca en una máquina limpia y completa el nivel sin errores de recursos.

---

### FASE 8 — Contenido y lanzamiento

Solo después de que pipeline, piloto, sistemas y build estén aprobados:

- Completar las salas restantes con el pipeline validado.
- Contenido de las cuatro criaturas.
- Misiones, contratos y progresión.
- Base de operaciones y tienda.
- Pruebas de estrés, accesibilidad, localización y licencias.
- Demo, marketing y lanzamiento.

---

## 5. Dependencias críticas

| Dependencia | Bloquea | Estado |
|---|---|---|
| Aprobación de documentos | Toda producción | Pendiente |
| Plantillas de exportación | Build P3 | Bloqueado |
| Importador nativo validado | Pipeline de assets | Pendiente de prueba |
| Licencias de assets | Distribución | 222 sin verificar |
| Rig y animaciones | Criaturas y jugador remoto | No existe |
| Audio propio y buses | Terror, radio, Imitador | No existe |
| Prueba de dos clientes | Multijugador | No realizada |
| Baseline del piloto | Aprobación del piloto | Pendiente |

---

## 6. Riesgos y mitigaciones

| Riesgo | Impacto | Mitigación |
|---|---|---|
| Reconstruir demasiado pronto | Retrabajo y pérdida de lo que funciona | Piloto cerrado y aprobado antes de ampliar |
| 539 `.blend` y versiones duplicadas | Confusión de fuente de verdad | Un máster por sala, versionado y manifiesto |
| Carga runtime de GLB | Sin LOD/import settings | Migrar assets nuevos al importador nativo |
| Assets sin UV/topología | Texturas pobres y artefactos | QA bloqueante en Blender |
| Criaturas procedurales | No hay terror creíble | Sculpt/retopo/rig/animación antes de IA compleja |
| Audio heredado | No hay identidad sonora | Buses y diseño sonoro propio |
| Falta de plantillas | No hay build | Autorización para instalar templates |
| Multijugador tardío | Rehacer sistemas | Definir estado de red desde el diseño |
| Licencias | Riesgo legal | Registro y verificación antes de distribuir |

---

## 7. Prioridad inmediata

1. Aprobar pipeline, estándar y roadmap.
2. Aprobar **Mantenimiento** como piloto.
3. Autorizar la prueba de importación nativa y, si falta, la instalación de plantillas de exportación.
4. Ejecutar el baseline del piloto.
5. Empezar el brief y el bloqueo de Mantenimiento.

No se debe empezar por modelar props sueltos ni por rehacer el corredor. El primer entregable es el **piloto aprobado**, no una colección de assets sin integración.

---

## 8. Criterio de éxito de esta hoja de ruta

La hoja de ruta funciona si, al terminarla:

- Existe una habitación piloto que parece parte de un juego comercial.
- El pipeline se puede repetir en otra sala sin improvisar.
- Cada asset tiene procedencia, licencia, UV, PBR, colisión y LOD.
- El rendimiento se mide, no se estima.
- El audio y las criaturas dejan de ser placeholders.
- El proyecto puede generar una build verificable.
- Las decisiones están documentadas y aprobadas.

Si alguna de estas condiciones falla, no se pasa a la siguiente fase.

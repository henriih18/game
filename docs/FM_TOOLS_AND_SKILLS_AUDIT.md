# FRECUENCIA MUERTA — Auditoría de herramientas, skills y flujo Blender → Godot

**Fecha:** 2026-11-04  
**Alcance:** inspección exclusiva de herramientas, skills, MCP, extensiones de Blender y pipeline de assets.  
**Restricciones respetadas:** no se modificó ningún archivo del proyecto, no se instaló ni desinstaló nada, no se crearon modelos ni escenas, no se usaron subagentes. El único archivo creado es este informe.  
**Método:** lectura de `SKILL.md`, inspección de configuración de OpenCode, comprobación de procesos/puertos, ejecución de Blender 5.2.3 en modo headless sobre los `.blend` clave, inventario de assets y revisión de scripts de construcción/exportación.

> Este documento distingue explícitamente entre **capacidad comprobada**, **capacidad teórica** (documentada pero no ejecutada en esta auditoría) y **capacidad no disponible**.

---

## 1. Skills disponibles y utilidad real

### 1.1 Dónde están y cómo se cargan

Las skills del catálogo están en:

`/home/riyo/.agents/skills/<id>/SKILL.md`

Hay **45 archivos `SKILL.md`**. No están dentro del proyecto: `/home/riyo/Documentos/game/.agents` solo contiene `mcp.json`. La carpeta `/home/riyo/.config/opencode/skills` está vacía y `/home/riyo/.config/opencode/SKILL.md` es un documento de rol de auditoría, no una skill del catálogo.

Esto es importante: una skill instalada **no se ejecuta automáticamente**. Solo aporta instrucciones y, en algunos casos, scripts `bpy` que hay que invocar de forma deliberada.

### 1.2 Skills relevantes para FRECUENCIA MUERTA

| Skill | Instalada | Qué ofrece realmente | Dónde debería intervenir | ¿Se está usando? |
|---|---:|---|---|---|
| `blender-core` | Sí | Puerta de entrada a Blender 5.2+: MCP en vivo o CLI headless, context overrides, búsqueda de nodos por tipo, cambios de API 5.x, verificación. Scripts `env_report.py`, `run_in_blender.py`, `_bpyx.py`. | Toda tarea de Blender. | **No de forma sistemática.** |
| `blender-hardsurface-modeling` | Sí | Blockout→detalle, stacks no destructivos (Mirror, Boolean Exact/Manifold, Bevel, Weighted Normal, Smooth by Angle), mid-poly/subdiv/high-to-low, normales, presupuestos de segmentos. | Arquitectura, puertas, maquinaria, props metálicos. | **No.** El nivel se construye con scripts propios. |
| `blender-pbr-materials` | Sí | Reglas metal/roughness, Principled BSDF 5.2, espacios de color, albedo/F0 medidos, ORM, normales DirectX/OpenGL, alpha, displacement, AgX/Khronos PBR Neutral, reglas de export. | Materiales de arquitectura, metal oxidado, cristales, pantallas, agua. | **Parcial.** Se aplican overrides en Godot, no el flujo PBR de la skill. |
| `blender-lighting-lookdev` | Sí | 3 puntos, producto, HDRI, sol/sky, interiores, light linking, unidades físicas, focales, DOF, ciclorama, turntables. | Lookdev de salas y presentación de assets. | **No.** La iluminación se resuelve en Godot por script. |
| `blender-asset-qa` | Sí | Puerta obligatoria tras modelar/editar: z-fighting, piezas flotantes, normales, non-manifold, degenerados, duplicados, n-gons, escala, UV, pesos, materiales; renders multiángulo. Scripts `qa_check.py`, `review_shots.py`. | Cualquier malla antes de exportar. | **No.** Es la ausencia más grave del pipeline. |
| `blender-export-pipelines` | Sí | Presets para Roblox, Unity, Unreal, Godot/web, USD; escala/ejes, smoothing, tangentes, leaf bones, clips, batch, verificación posterior. Script `export_asset.py`. | Exportación GLB a Godot. | **No.** Se usan scripts `export_level1_glb.py` y `export_props.py` propios. |
| `blender-game-optimization` | Sí | Presupuestos por plataforma, LODs, decimación, limpieza, draw calls, instancing, vertex splits, proxies de colisión, memoria de texturas. Scripts `make_lods.py`, `mesh_stats.py`. | Optimización de nivel, props y criaturas. | **No.** No hay LODs ni presupuestos aplicados. |
| `blender-rendering` | Sí | Cycles/EEVEE/Workbench, presets, GPU, muestreo, denoise, color management, pases, compositor 5.0, batch. | Renders de referencia/QA. | **No.** |
| `blender-scene-setup` | Sí | Unidades/escala real, colecciones, naming `SM_/SK_/T_/M_`, orígenes, linking/appending, overrides, asset libraries, collection exporters, limpieza. Script `scene_audit.py`. | Organización del `.blend` maestro. | **No.** El máster tiene 19 colecciones y 539 `.blend` versionados sin política visible. |
| `godot-3d-essentials` | Sí | Node3D, cámara, luces, WorldEnvironment, materiales, GridMap. | Escenas 3D. | Uso parcial, conocimiento aplicado sin invocar la skill. |
| `godot-physics` | Sí | RigidBody/StaticBody/Area/CharacterBody, capas/máscaras, señales, raycasts, Jolt 3D. | Colisiones, escondites, objetos físicos. | Uso parcial; las colisiones del nivel son AABB manuales. |
| `godot-animation` | Sí | AnimationPlayer, AnimationTree, blend spaces, Tween. | Puertas, criaturas, personajes. | **No hay pipeline de animación.** |
| `godot-audio` | Sí | AudioStreamPlayer 2D/3D, buses, mezcla, dB/linear, sync. | Audio ambiental, pasos, criaturas, radio. | **No hay buses ni diseño sonoro real.** |
| `godot-shaders` | Sí | Shaders `canvas_item` y `spatial`, uniforms, TIME/UV, screen texture. | Efectos de terror, pantallas, distorsión. | Uso puntual, no sistemático. |
| `level-design` | Sí | Blockout→jugable, métricas, pacing, gating, critical path, encounter design. | Distribución y ritmo del Nivel 1. | **No** como proceso formal. |
| `game-ai` | Sí | FSM, behavior trees, steering, A*. | Vigilante y futuras criaturas. | Parcial; la IA existe, pero no se validó el ciclo completo. |
| `ai-behavior-trees-utility-ai` | Sí | Runtime BT/Blackboard/Utility AI, curvas, híbridos. | Criaturas con decisiones complejas. | **No.** |
| `performance-optimization` | Sí | Medir con profiler, frame budget, CPU/GPU, pooling, draw calls, allocaciones. | Optimización del nivel. | Parcial: se midió FPS/VRAM, pero no con profiler ni RenderDoc. |
| `physics-tuning` | Sí | Timestep fijo, interpolación, masa/gravedad/drag, CCD, jitter, capas. | Objetos, puertas, escondites. | **No** de forma sistemática. |
| `procedural-gen` | Sí | RNG determinista, ruido, habitaciones/corredores, loot. | Variabilidad de partidas. | **No.** |
| `sound-effects` | Sí | Generación de SFX con ElevenLabs; requiere `ELEVENLABS_API_KEY`. | SFX, ambientes, criaturas. | **No.** No hay clave configurada. |
| `systematic-debugging` | Sí | Metodología de reproducción, hipótesis, evidencia, regresión. | Bugs como puertas/colisiones. | Uso conceptual, no formal. |
| `verification-before-completion` | Sí | Exigir evidencia antes de declarar terminado. | Todas las fases. | Uso parcial. |
| `writing-plans` | Sí | Planificación multi-paso antes de tocar código. | Fases grandes. | Uso parcial. |
| `context7-mcp` | Sí | Consultar documentación actualizada de librerías. | APIs de Godot 4.7. | **No se usó de forma sistemática.** |

### 1.3 Skills que `blender-core` promete pero NO están instaladas

`blender-core` enruta a más de 20 skills especializadas. **No existen** en el catálogo, entre otras:

`blender-sculpting`, `blender-retopology-uv`, `blender-texturing`, `blender-texture-baking`, `blender-geometry-nodes`, `blender-character-rigging`, `blender-facial-shapekeys`, `blender-animation`, `blender-clothing`, `blender-hair-grooming`, `blender-stylized-npr`, `blender-environment-kits`, `blender-simulation`, `blender-addon-development`, `blender-pipeline-automation`, `blender-workflow-recipes`.

Consecuencia: el agente tiene guías para **hard-surface, PBR, iluminación, QA, exportación, optimización y escenas**, pero **no** tiene una guía instalada específica de escultura, retopología/UV, texturizado/baking, rigging o animación de personajes. Eso no significa que Blender no pueda hacerlo: significa que la capacidad existe en Blender, pero no está cubierta por una skill del catálogo.

### 1.4 Valor real de las skills

Las skills de Blender son **procedimientos y scripts**, no plugins que añadan capacidades al Blender instalado. Su valor está en:

- Obligar a un orden de trabajo (blockout → detalle → UV → materiales → QA → LOD → export).
- Evitar errores conocidos de Blender 5.x.
- Aportar scripts de verificación y exportación.
- Definir presupuestos y criterios de aceptación.

Sin invocarlas, el proyecto pierde exactamente eso: **proceso, QA y presupuestos**.

---

## 2. Extensiones de Blender instaladas

### 2.1 Versión y ejecutable

- Blender instalado: **5.2.3 LTS**.
- Ejecutable real: **`/opt/blender/blender`**.
- Copia adicional: `/home/riyo/Documentos/blender-5.2.3-linux-x64/blender`.
- **`blender` no está en PATH**; por eso `blender --version` falla. Se puede invocar por ruta absoluta o añadir un enlace simbólico (no se hizo).

### 2.2 Extensiones presentes

En `~/.config/blender/5.2/extensions/blender_org/` están instaladas 14 extensiones:

`material_utilities`, `archimesh`, `measureit`, `texture_wrangler`, `topopot_retopo_tool`, `ucupaint`, `mio3_uv`, `EdgeFlow`, `PlaceHelper`, `extra_mesh_objects`, `auto_mirror`, `bool_tool`, `Modifier_List_Fork`, `looptools`.

### 2.3 ¿Están habilitadas?

**No.** La comprobación de `bpy.context.preferences.addons` solo muestra los addons integrados y `blender_mcp`:

`bl_pkg`, `blender_mcp`, `cycles`, `io_anim_bvh`, `io_curve_svg`, `io_mesh_uv_layout`, `io_scene_fbx`, `io_scene_gltf2`, `pose_library`.

Los `strings` de `userpref.blend` no contienen los nombres de las 14 extensiones. Por tanto están **instaladas pero inactivas**: no aportan nada al flujo actual.

### 2.4 Valor real de las extensiones si se activan

No se recomienda activarlas todas. Las que sí tienen una necesidad concreta:

- **Ucupaint**: texturizado por capas dentro de Blender; útil para desgaste, suciedad y variación sin salir a otra aplicación.
- **Texture Wrangler**: empaquetado de canales ORM y limpieza de sets PBR.
- **Mio3 UV**: operaciones UV y empaquetado; útil para reducir coste de UV y mejorar texel density.
- **TopoPot Retopo**: retopología manual; necesario si se quiere pasar de blockout a malla de producción.
- **MeasureIt**: verificación de dimensiones reales (puertas, pasillos, criaturas).
- **Archimesh**: apoyo para arquitectura modular; útil, pero puede fomentar más blockout si no se acompaña de detalle.
- **Bool Tool / Modifier List Fork / Looptools / EdgeFlow**: apoyo de modelado hard-surface.
- **Auto Mirror**: simetría; útil para props y criaturas.
- **Extra Mesh Objects / PlaceHelper**: utilidades menores; no prioritarias.

**Conclusión:** hay capacidad instalada suficiente para texturizar, hacer UV y retopología básica, pero está desactivada. Activar Ucupaint, Texture Wrangler, Mio3 UV, TopoPot y MeasureIt es una mejora real y no requiere instalar nada nuevo.

---

## 3. Estado de Blender MCP y Context7 MCP

### 3.1 Blender MCP

**Estado actual: DESCONECTADO.**

- El servidor MCP `blender-mcp` está corriendo por `uvx` (`/home/riyo/.local/bin/uv tool uvx blender-mcp` y su proceso Python).
- El puerto **9876 no está escuchando**.
- No hay una UI de Blender abierta.
- `get_addon_status` devuelve:
  `Could not connect to Blender. Make sure the Blender addon is running.`
- El addon `blender_mcp` está **instalado y habilitado** en Blender 5.2.3 (`~/.config/blender/5.2/scripts/addons/blender_mcp.py`).

**Conclusión:** no falta instalar nada. Falta abrir Blender y arrancar el addon/servidor. Mientras no se haga, el agente no puede usar `look`, `get_scene_info` ni `execute_blender_code`.

### 3.2 Herramientas reales de Blender MCP

El catálogo expone **9 herramientas**:

1. `get_addon_status` — estado del addon.
2. `get_scene_info` — objetos, tamaño, salud topológica/rigs, settings.
3. `look` — imagen del viewport/cámara/ángulos/frames, shading.
4. `execute_blender_code` — ejecuta `bpy`/`bmesh`/`mathutils` en vivo.
5. `search_assets` — Poly Haven (CC0), Sketchfab, Poly Pizza.
6. `import_asset` — descarga e importa un asset, con `target_size`.
7. `generate_3d` — genera **un** objeto texturizado por llamada; puede costar dinero; proveedores Tripo/Hunyuan3D/Hyper3D/Meshy.
8. `record_trajectory_feedback` — feedback de trayectoria.
9. `disable_telemetry` — telemetría.

**Capacidades comprobadas si Blender está abierto:** inspeccionar escena, leer/escribir geometría con `bpy`, crear/modificar materiales y luces, renderizar vistas, importar assets, ejecutar scripts de las skills.

**Capacidades no disponibles ahora:** todo lo anterior, porque no hay conexión.

**Advertencia sobre `generate_3d`:** genera un objeto, no una escena, y puede consumir crédito. No es una solución para arquitectura modular ni para criaturas coherentes; no se usó.

### 3.3 Context7 MCP

**Estado: FUNCIONA.**

`resolve-library-id` devolvió documentación real de Godot:

- `/godotengine/godot-docs` — 47.270 snippets, reputación alta, rama 4.7.
- `/websites/godotengine_en` — 56.745 snippets, 4.7.
- `/godotengine/godot` — 3.421 snippets, rama 4.7.

Es útil para verificar APIs de Godot 4.7 (física, animación, audio, shaders, importación). **No se ha usado de forma sistemática** en el proyecto; se ha dependido de conocimiento previo y de prueba/error.

---

## 4. Capacidades disponibles y limitaciones

### 4.1 Capacidades comprobadas

- **Godot 4.7.2** en `/home/riyo/.local/bin/godot`; Forward+, 1280×720, escenas y tests funcionando.
- **Blender 5.2.3 headless** por `/opt/blender/blender -b`; se inspeccionaron los `.blend` maestros.
- **Blender MCP** con 9 herramientas, listo para conectar cuando se abra Blender.
- **Context7** para documentación de Godot.
- **ImageMagick** (`magick`/`convert`), **ffmpeg**, **python3**.
- **Blender addons**: `blender_mcp` habilitado; 14 extensiones instaladas (inactivas).
- **Skills**: 45 `SKILL.md`; guías y scripts de Blender/Godot/IA/diseño/rendimiento/audio.

### 4.2 Capacidades teóricas (documentadas, no ejecutadas en esta auditoría)

- Modelado hard-surface con Bevel/Boolean/Mirror/Weighted Normal.
- PBR con Principled BSDF 5.2, ORM, normales, alpha, displacement.
- QA topológico con `qa_check.py` y hojas de revisión con `review_shots.py`.
- Exportación con `export_asset.py` a Godot/web.
- LODs con `make_lods.py`; estadísticas con `mesh_stats.py`.
- Rigging/animación en Blender: **Blender puede hacerlo**, pero **no hay skill instalada** que lo guíe.
- Escultura/retopología/UV/baking: **Blender puede hacerlo**, pero **no hay skill instalada** específica.

### 4.3 Capacidades no disponibles

- **Blender MCP en vivo ahora mismo**: sin UI/puerto 9876.
- **Build/export de Godot**: no hay `export_presets.cfg`; `~/.local/share/godot/export_templates` está vacío. No se puede generar un release Linux/Windows sin plantillas.
- **Dos clientes reales**: no se ha probado multijugador.
- **RenderDoc / gltf-transform / gltfpack / toktx / MeshLab / Krita / GIMP / SoX**: no instalados.
- **ElevenLabs**: sin `ELEVENLABS_API_KEY`; la skill `sound-effects` no puede generar audio.
- **DAW / middleware de audio**: no hay; solo WAV + Godot AudioStreamPlayer.

### 4.4 Limitaciones del entorno

- `blender` no está en PATH: fricción para scripts y para el usuario.
- `rg` no está instalado: las búsquedas usan `grep -R`.
- El proyecto tiene **539 `.blend`** y backups; el control de versiones de assets es difuso.
- Los GLB se cargan en runtime, no por el importador de Godot (ver sección 7).
- Los assets externos tienen licencias sin resolver (ver sección 8).

---

## 5. Skills que no se están aprovechando

### 5.1 Las más críticas

1. **`blender-asset-qa`** — no se ha ejecutado nunca sobre el nivel. Es la causa directa de que se hayan exportado 739 mallas texturizadas sin UV, 25.010 boundary edges y 8.124 non-manifold sin detectarlos.
2. **`blender-export-pipelines`** — no se usa `export_asset.py`; los scripts propios exportan sin QA, sin LOD y sin verificación posterior.
3. **`blender-game-optimization`** — no se han generado LODs ni se han aplicado presupuestos; el nivel tiene 2.217 mallas y 588.313 tris en Blender, y 647.397 tris instanciados en el GLB.
4. **`blender-scene-setup`** — no hay una política de naming/escala/colecciones aplicada al máster; hay 1.675 mallas sin UV y 203 con escala no unitaria.
5. **`blender-pbr-materials`** — los materiales se corrigen en Godot con overrides, no se authorizan correctamente en Blender; esto produce el aspecto plano/yeso.
6. **`blender-lighting-lookdev`** — la iluminación se resuelve con luces y scripts en Godot; no hay lookdev previo en Blender.
7. **`godot-animation` / `godot-audio` / `godot-physics`** — no se usan como proceso; no hay rigs, buses ni validación de colisiones más allá de AABB.

### 5.2 Skills que sí se han usado de forma conceptual

- `systematic-debugging`: se aplicó al bug de puertas (reproducción, hipótesis, fix, regresión).
- `verification-before-completion`: se aplicó parcialmente (smoke, doors, walk, perf).
- `performance-optimization`: se midió FPS/VRAM, pero sin profiler ni RenderDoc.
- `godot-3d-essentials`, `godot-physics`: conocimiento aplicado, no invocación formal.

### 5.3 Por qué no se aprovecharon

- El proyecto ya tenía scripts propios (`build_level1.py`, `export_level1_glb.py`, etc.) y se siguió esa inercia.
- Las skills no se cargan automáticamente; hay que invocarlas.
- La auditoría anterior se centró en el nivel ya construido, no en el pipeline que lo produjo.
- No había una puerta de QA obligatoria antes de exportar.

---

## 6. Herramientas adicionales realmente necesarias

No se recomienda instalar por acumular. Prioridad por necesidad concreta:

### 6.1 Necesarias ahora (sin instalar nada nuevo)

1. **Abrir Blender 5.2.3 y arrancar `blender_mcp`** — desbloquea `look`, `get_scene_info`, `execute_blender_code`.
2. **Activar Ucupaint, Texture Wrangler, Mio3 UV, TopoPot y MeasureIt** — ya están instaladas; cubren texturizado por capas, ORM, UV, retopología y medición.
3. **Usar `blender-asset-qa` antes de cada export** — no requiere instalar; requiere ejecutar `qa_check.py` y `review_shots.py`.
4. **Usar `blender-export-pipelines` para el próximo GLB** — validar escala, ejes, smoothing, tangentes y presupuesto.
5. **Añadir `blender` al PATH** (enlace simbólico o alias) — comodidad, no capacidad nueva.
6. **Usar Context7 para APIs de Godot 4.7** — ya funciona.

### 6.2 Necesarias para calidad profesional (evaluar, no instalar aún)

1. **Pipeline de UV/retopología/baking**: la mayor carencia técnica. Blender puede hacerlo, pero no hay skill instalada. Antes de instalar nada, usar Mio3 UV + TopoPot + Ucupaint y definir un estándar de UV/bake.
2. **Rigging y animación**: no hay skill instalada ni pipeline. Para el Vigilante y los personajes hace falta un plan de armature, pesos y clips. Blender puede; falta método.
3. **RenderDoc**: útil para perfilar GPU de verdad. Godot Profiler primero; RenderDoc solo si el profiler no basta.
4. **gltfpack / gltf-transform**: útiles si se mantiene la carga runtime de GLB; permiten compresión de malla y análisis. No sustituyen el importador de Godot.
5. **Krita/GIMP**: no imprescindibles; Ucupaint/Blender + ImageMagick cubren gran parte. No instalar por defecto.
6. **DAW/SoX**: no prioritario; Godot buses + WAV bastan para el vertical slice.
7. **ElevenLabs**: solo si se decide usar voces sintéticas; requiere clave y política de consentimiento. No es necesario para el primer pase.

### 6.3 Lo que NO hace falta

- No hace falta otro motor.
- No hace falta un paquete de assets masivo.
- No hace falta instalar todas las extensiones de Blender.
- No hace falta `generate_3d` para arquitectura; sería incoherente y caro.

---

## 7. Flujo de trabajo recomendado para Blender y Godot

### 7.1 Regla principal: separar autoría, export e importación

El error estructural actual es cargar el GLB en runtime con `GLTFDocument.append_from_file()` y tratar Godot como si fuera un visor. Eso evita el importador de Godot y, con él:

- Generación automática de LODs.
- Hints de colisión `-col` / `-colonly`.
- UV2 para lightmaps.
- Ajustes de compresión de texturas.
- Reimportación y validación.

**Flujo recomendado:**

1. **Blender (autoría)**
   - Un `.blend` maestro por instalación, con colecciones y naming.
   - Unidades métricas, escala 1.0, orígenes en el suelo.
   - Blockout → detalle hard-surface → UV → materiales PBR → QA.
   - Mallas de colisión separadas con sufijo `-col`/`-colonly`.
   - LODs `LOD0/LOD1/LOD2` cuando el asset lo justifique.
   - Exportar GLB con `export_asset.py` o preset Godot validado.

2. **Godot (importación)**
   - Importar el GLB como recurso (`res://...glb` con `.import`), no cargarlo a mano.
   - Configurar LODs, compresión, tangentes, sombras y colisiones en el importador.
   - Usar la escena importada como base; los overrides de material/luz van en escena o script, no en el asset.
   - Si se necesita carga dinámica, usar `PackedScene`/`ResourceLoader`, no `GLTFDocument` en producción.

3. **QA**
   - `blender-asset-qa` antes de exportar.
   - `mesh_stats.py` para triángulos/draw calls.
   - `review_shots.py` para hojas multiángulo.
   - En Godot: smoke, walk, doors, capturas off/on, perfilado.

4. **Optimización**
   - Presupuesto por zona: triángulos, materiales, texturas, luces, draws.
   - LODs y occlusion culling.
   - Texturas 1K/2K con ORM empaquetado; no 2K en props pequeños.
   - Instancing para módulos repetidos.
   - Colisiones proxy, no AABB de cada mesh.

5. **Audio**
   - Buses (`Master`, `SFX`, `Ambience`, `Voice`, `UI`) en `default_bus_layout.tres`.
   - AudioStreamPlayer3D para fuentes posicionales; límites de voces.
   - Samples reales o síntesis documentada; no reutilizar audio de otro proyecto sin intención.

6. **Animación**
   - Armature + pesos + clips en Blender; exportar clips separados.
   - AnimationTree en Godot para estados; no animar por código salvo puertas/props.

### 7.2 Qué conservar del flujo actual

- Los scripts de construcción (`build_level1.py`, `build_level1_doors.py`, etc.) son útiles para blockout y para generar variantes.
- `level1_doors.glb` es el mejor asset del lote: topología limpia, 116 mallas, sin non-manifold, animación por script en Godot.
- El pase artístico de Godot puede conservarse para luces, materiales y detalles, pero no debe sustituir la autoría del asset.

### 7.3 Qué cambiar primero

1. Exportar el nivel por el importador de Godot, no por `GLTFDocument`.
2. Pasar `blender-asset-qa` al máster y corregir UV/escala/non-manifold antes de volver a exportar.
3. Activar las extensiones de texturizado/UV/retopo ya instaladas.
4. Definir presupuestos y LODs antes de añadir más contenido.
5. Resolver licencias de los 222 objetos marcados como Poly Haven.

---

## 8. Diagnóstico: por qué el flujo actual produce calidad de prototipo

### 8.1 Evidencia objetiva del máster

Inspección headless de `nexus/nivel_01/NEXUS_L1_V05.blend` (Blender 5.2.3):

- **2.445 objetos**: 2.217 mallas, 106 empties, 43 fuentes, 67 luces, 12 cámaras.
- **2.142 mallas de datos**, 128 materiales, 232 imágenes, 19 colecciones, 1 biblioteca enlazada.
- **316.006 vértices, 353.040 polígonos, 588.313 triángulos**.
- **1.675 mallas sin UV**.
- **203 objetos con escala no unitaria**.
- **296 objetos ocultos**.
- Modificadores: **1.185 Bevel**, 74 Weighted Normal, 4 Subsurf, 16 Geometry Nodes, 18 Triangulate.
- Muestra de 1.200 mallas: **5.583 boundary edges, 192 non-manifold, 512 vértices duplicados**.
- **222 objetos** con `asset_license = "Poly Haven - verificar licencia antes de distribuir"`.
- 230 imágenes externas; muchas a 2K.

### 8.2 Comparación con los assets authored

- `LEVEL1_DRESSING.blend`: 1.327 mallas, 21.516 tris, **0 sin UV**, **0 escala mala**, 1.235 Bevel + Weighted Normal, **0 non-manifold**.
- `LEVEL1_DOORS.blend`: 116 mallas, 51.820 tris, **0 sin UV**, **0 escala mala**, **0 non-manifold**, sin modificadores.
- `ART3A1_kit.blend`: 274 mallas, 4.632 tris, **0 sin UV**, **0 escala mala**, **0 non-manifold**.
- `FM_CORRIDOR_FINAL_v14.blend`: 5.724 mallas, 106.711 tris, **5.503 sin UV**, 3.341 Bevel, 225 materiales, 661 boundary en muestra de 1.200.

**Lectura:** cuando el equipo authora un asset concreto (puertas, kit, dressing), la topología es limpia. El problema está en el **ensamblaje del nivel maestro**: se mezclan assets externos, se duplican, se escalan y se exportan sin QA.

### 8.3 El GLB confirma lo mismo

Auditoría previa de `level1_nexus.glb`:

- 2.035 nodos, 1.905 mallas, 137 materiales.
- **647.397 triángulos instanciados**.
- **25.010 boundary edges, 8.124 non-manifold, 192 inconsistentes, 78 degenerados, 5.197 duplicados**.
- **739 mallas texturizadas sin UV**.
- **46.242 triángulos con área UV cero**.

Esto explica directamente:

- Materiales que se ven planos o “de yeso”.
- Reflejos y normales incorrectos.
- Z-fighting y artefactos.
- Dificultad para aplicar desgaste, suciedad y variación.
- Que los overrides de material en Godot no arreglen el problema de fondo.

### 8.4 La carga runtime impide que Godot ayude

`level1.gd:187-189` y `fm_level1_art_pass.gd:764/808/873/989` cargan GLB con `GLTFDocument.append_from_file()`. No hay `.import` para ningún GLB; solo 103 `.import` en todo el proyecto (iconos, audio e imágenes).

Consecuencias:

- No se generan LODs automáticos.
- No se aplican hints de colisión.
- No se genera UV2.
- No se comprimen texturas con el importador.
- No hay reimportación ni validación.
- Las colisiones se generan a mano por AABB (`_setup_collisions`), lo que produce cajas sobredimensionadas, paredes invisibles y props flotantes.

**Este es el punto de mayor impacto técnico del informe.** No es solo “faltan LODs”: es que el pipeline evita el sistema de importación de Godot y luego se compensa con scripts.

### 8.5 Assets externos y licencias

- 1.147 archivos de biblioteca, 138 modelos (4,0 GB), 557 MB de texturas, 78 MB de HDRI.
- Nombres tipo Poly Haven, pero **no hay archivos de licencia/readme**.
- 222 objetos tienen una propiedad `asset_license` que dice “verificar licencia antes de distribuir”.

No se puede declarar el nivel listo para distribución mientras esto siga así. La licencia Poly Haven CC0 es compatible, pero hay que **verificar cada asset** y documentar la fuente; la propiedad autoafirmada no es prueba suficiente.

### 8.6 Audio y criaturas

- `tools/generate_audio.py` es un sintetizador procedural heredado; su docstring dice “Robo Caotico”, no FRECUENCIA MUERTA.
- No hay `default_bus_layout.tres` ni buses.
- No hay `AnimationPlayer`, `AnimationTree`, `Skeleton3D` ni armature en `scripts/fm`/`scenes/fm`.
- `fm_creature_models.gd` construye al Vigilante y al Imitador con `CapsuleMesh`, `SphereMesh`, `BoxMesh` y `ArrayMesh`; no hay rig, huesos ni clips.

Esto explica que las criaturas y el audio se perciban como prototipo, aunque la IA y la lógica funcionen.

### 8.7 Síntesis causal

La calidad de prototipo no viene de una sola causa. Viene de la combinación de:

1. **Geometría de blockout procedural** con detalle añadido, no modelado de producción.
2. **Falta de UV/retopología/baking** en el máster.
3. **Escalas y orígenes inconsistentes** en 203 objetos.
4. **Exportación sin QA ni LOD**.
5. **Carga runtime que evita el importador de Godot**.
6. **Colisiones AABB manuales** en lugar de proxies.
7. **Materiales corregidos en Godot**, no authorados en Blender.
8. **Assets externos sin licencias resueltas**.
9. **Audio heredado y criaturas sin rig**.
10. **Skills y extensiones instaladas pero no utilizadas**.

La buena noticia: los assets authored (puertas, kit, dressing) demuestran que el equipo **sí puede producir mallas limpias**. El problema es el proceso de ensamblaje y exportación, no la capacidad artística absoluta.

---

## 9. Conclusión y prioridades

### Capacidades comprobadas

- Blender 5.2.3 headless y MCP listo para conectar.
- Godot 4.7.2, tests y nivel funcionando.
- Context7 operativo.
- 45 skills instaladas; 14 extensiones de Blender instaladas.
- Pipeline de scripts propio que genera geometría y exporta GLB.

### Capacidades no disponibles ahora

- Blender MCP en vivo (sin UI/puerto).
- Build de Godot (sin plantillas).
- Rigging/animación de personajes.
- Audio profesional.
- Perfilado GPU con RenderDoc.

### Prioridad inmediata

1. **Abrir Blender y conectar MCP.**
2. **Ejecutar `blender-asset-qa` sobre `NEXUS_L1_V05.blend`** y corregir UV, escala, non-manifold y duplicados.
3. **Migrar la carga de GLB al importador de Godot**; generar LODs y colisiones por import.
4. **Activar Ucupaint, Texture Wrangler, Mio3 UV, TopoPot y MeasureIt.**
5. **Definir presupuestos y LODs** antes de ampliar el nivel.
6. **Resolver licencias** de los 222 objetos marcados.
7. **Crear el pipeline de rigging/animación y audio** antes de invertir en criaturas definitivas.

### Veredicto

FRECUENCIA MUERTA tiene **herramientas suficientes para producir calidad profesional**, pero **no está usando el proceso que esas herramientas exigen**. El déficit principal no es de software: es de **QA, autoría de UV/materiales, importación correcta y pipeline de personajes/audio**. Mientras el nivel se siga cargando en runtime y se exporte sin QA, añadir más assets o luces solo producirá más contenido con la misma calidad de prototipo.

# FRECUENCIA MUERTA — Pipeline de producción Blender → Godot

**Estado:** propuesta para aprobación. No autoriza todavía a reconstruir habitaciones ni a modificar assets de forma masiva.
**Fecha:** 2026-11-04
**Motor:** Godot 4.7.2 · **DCC:** Blender 5.2.3 LTS
**Referencia principal:** `AGENTS.md`

---

## 1. Propósito

Definir un flujo de producción repetible para que los escenarios, props, personajes y criaturas de FRECUENCIA MUERTA dejen de ser prototipos y alcancen calidad comercial dentro del hardware objetivo (GTX 1650 Ti 4 GB, 32 GB RAM, i5).

Este documento describe **cómo se produce un asset**, no qué habitación se reconstruye primero. La primera aplicación será una sola habitación piloto: **Mantenimiento / Sala de máquinas**.

Principios:

1. El arte se produce en Blender. Los scripts automatizan, validan o ensamblan; **no sustituyen** el modelado orgánico, la retopología, el UV, el texturizado ni el rigging.
2. Ningún asset entra en Godot sin pasar por el importador nativo y por el control de calidad.
3. Ninguna decisión visual contradice `AGENTS.md`, las referencias de `fotos-referencia/` ni los diseños aprobados de las cuatro criaturas.
4. La oscuridad, el sonido y la tensión son requisitos de diseño, no efectos opcionales.
5. No se introducen armas, combate directo ni sistemas para matar criaturas.

---

## 2. Jerarquía de referencia

Cuando haya conflicto, se resuelve en este orden:

1. `AGENTS.md`: identidad, visión, reglas y dirección artística.
2. Documentos de diseño de sistemas y características.
3. `docs/FM_QUALITY_STANDARD.md`: criterios objetivos de aprobación.
4. `docs/FM_PRODUCTION_ROADMAP.md`: orden y dependencias.
5. Auditorías y estados técnicos (`docs/FM_LEVEL1_FULL_AUDIT.md`, `docs/CURRENT_STATE.md`).

Si dos documentos se contradicen, **no se decide por conveniencia**: se documenta el conflicto y se solicita aprobación.

---

## 3. Diagnóstico del pipeline actual

El proyecto ya tiene un Nivel 1 jugable, pero su cadena de producción no es la de un juego comercial:

- **539 archivos `.blend`**, con decenas de versiones y backups. El máster del nivel es `nexus/nivel_01/NEXUS_L1_V05.blend` (2.445 objetos, 2.217 mallas, 19 colecciones, librería `NEXUS_SHARED_ASSETS.blend`).
- El GLB del nivel (`assets/models/fm/level1_nexus.glb`, 42,5 MB) se carga en **runtime** con `GLTFDocument.append_from_file()`, no con el importador de Godot. Por eso no se aprovechan LODs automáticos, import hints de colisión, UV2 ni compresión del importador.
- El máster contiene **1.675 mallas sin UV**, **203 objetos con escala no unitaria**, **296 objetos ocultos** y, en una muestra de 1.200 mallas, **5.583 boundary edges** y **192 non-manifold**.
- El GLB principal reporta **647.397 triángulos instanciados**, **25.010 boundary edges**, **8.124 non-manifold**, **739 mallas texturizadas sin UV** y **46.242 triángulos con área UV cero**.
- **222 objetos** llevan la propiedad `asset_license` con el texto “Poly Haven - verificar licencia antes de distribuir”. No hay archivos de licencia por asset.
- No hay rigs, esqueletos ni animaciones de personajes/criaturas. Las criaturas actuales son mallas procedurales en Godot.
- El audio existente es un sintetizador WAV heredado de otro proyecto (“Robo Caotico”); no hay buses, mezcla ni diseño sonoro propio.
- No hay `export_presets.cfg`, build validada ni plantillas de exportación instaladas.

La consecuencia es directa: el nivel puede funcionar, pero la calidad visual y la mantenibilidad siguen siendo de prototipo. El pipeline debe corregir la causa, no solo retocar el resultado.

---

## 4. Herramientas y skills

### Blender

- Ejecutable: `/opt/blender/blender` (5.2.3 LTS). No está en `PATH`; usar ruta absoluta.
- MCP de Blender conectado en `127.0.0.1:9876` cuando la UI está abierta y el addon inicia el servidor.
- Addons activos relevantes: Blender MCP, glTF, Cycles, UV Layout, FBX, Ucupaint, Mio3 UV, TopoPot, LoopTools, EdgeFlow, Bool Tool, MeasureIt, Texture Wrangler, Material Utilities, Auto Mirror y Modifier List.
- Skills de referencia: `blender-core`, `blender-sculpting`, `blender-hardsurface-modeling`, `blender-retopology-uv`, `blender-pbr-materials`, `blender-texturing`, `blender-texture-baking`, `blender-lighting-lookdev`, `blender-character-rigging`, `blender-animation`, `blender-asset-qa`, `blender-pipeline-automation`, `blender-export-pipelines`, `blender-game-optimization`, `blender-scene-setup`.

### Godot

- Godot 4.7.2, renderer Forward+.
- Skills de referencia: `godot-3d-essentials`, `godot-gdscript`, `godot-nodes-scenes`, `godot-physics`, `godot-animation`, `godot-audio`, `godot-shaders`, `godot-ui-control`, `godot-multiplayer`, `scenario-godot-3d-world`, `scenario-godot-architecture`, `scenario-godot-gameplay`, `scenario-godot-rendering-lighting`, `scenario-godot-performance-export`, `scenario-godot-pipeline-automation`, `scenario-godot-expert`, `game-ai`, `ai-behavior-trees-utility-ai`, `level-design`, `performance-optimization`, `physics-tuning`, `procedural-gen`.

### Context7

Usar Context7 para verificar APIs de Godot 4.7 antes de implementar sistemas nuevos. No sustituye las pruebas reales.

---

## 5. Convenciones obligatorias

### Unidades y escala

- 1 unidad de Blender = 1 metro. `unit_settings.system = METRIC`, `scale_length = 1.0`.
- Aplicar escala y rotación antes de exportar (`Ctrl+A`). El origen de un prop va en la base, centrado; el de una puerta, en su bisagra; el de una criatura, entre los pies.
- Forward del personaje: `-Y` en Blender, `-Z` en Godot. Validar visualmente tras importar.
- Alturas de criaturas (referencia oficial `fotos-referencia/modelos-referencia.png`):
  - El Imitador: **2,2–2,5 m**.
  - El Vigilante: **2,5–3,0 m**.
  - El Coleccionista: **2,0–2,5 m**.
  - La Sombra: **2,0–2,5 m**.
- Métricas de jugador y arquitectura existentes:
  - Cápsula de jugador: radio **0,38 m**, altura **1,70 m** (verificar en `fm_player.gd` antes de cambiarla).
  - Puerta estándar del nivel: **1,58 × 3,00 m** (`_add_door`).
  - Pasillo principal: **3,4 m** de ancho; altura libre **3,0 m**.
  - Recepción: **16 × 10 m**; seguridad: **10 × 8 m**.
  - No reducir una habitación por debajo del espacio de giro, ocultación, combate-evasión ni transporte de objetos.

### Nombres

- `SM_` malla estática, `SK_` malla esquelética, `T_` textura, `M_` material, `COL_`/`UCX_` colisión, `LOD0/1/2` niveles de detalle.
- Formato: `FM_<ZONA>_<TIPO>_<NOMBRE>_<VARIANTE>`.
- Ejemplos: `FM_L1_MAINT_SM_Generator_01`, `FM_L1_MAINT_SM_Boiler_01`, `FM_L1_MAINT_M_Pipe_Red`, `FM_L1_MAINT_COL_Generator_01`, `FM_L1_MAINT_LOD1_Boiler_01`.
- No usar nombres genéricos (`Cube.001`, `Material.023`) en assets finales.

### Estructura de fuente y export

- Fuente: un `.blend` maestro por asset o por kit, dentro de `nexus/` o `blender_concept/`, no decenas de versiones sueltas.
- Export: `assets/models/fm/<zona>/<asset>.glb` + `<asset>.json` (manifiesto) + licencia.
- El manifiesto incluye: fuente `.blend`, autor, licencia, triángulos, materiales, texturas, LODs, colisiones, animaciones y fecha.
- Los assets externos (Poly Haven, Sketchfab, etc.) deben tener licencia comprobada y documentada antes de entrar en el build. Sin licencia, no se aprueba.

---

## 6. Pipeline Blender — producción de assets

### 6.1. Brief y referencias

Antes de modelar:

1. Definir función, dimensiones, materiales, nivel de desgaste y contexto narrativo.
2. Reunir referencias visuales reales (no solo imágenes generadas).
3. Comprobar que el asset no existe ya en el proyecto.
4. Definir presupuesto de triángulos, materiales y texturas.
5. Definir si necesita LOD, colisión, rig, animación o física.

### 6.2. Blockout y métricas

- Construir la silueta y el volumen con medidas reales.
- Verificar escala contra el jugador y, si aplica, contra la criatura.
- Para arquitectura: grid modular, puertas, techos, circulación, cobertura, escondites y navegación.
- No añadir detalle fino antes de aprobar proporciones y función.

### 6.3. Modelado

- **Hard-surface:** blockout → detalle → biseles → weighted normal/smooth by angle. Evitar aristas vivas sin intención.
- **Orgánico:** escultura base → detalle → retopología. No sustituir criaturas por cápsulas, esferas o cajas ensambladas.
- **Arquitectura:** módulos reutilizables, uniones coherentes, sin geometría oculta innecesaria.
- Respetar la silueta y los rasgos de las referencias de criaturas.

### 6.4. Retopología y UV

- Retopología orientada a deformación (personajes/criaturas) o a geometría estática (props/arquitectura).
- UVs sin solapamientos salvo simetría declarada; margen de 4–8 px; densidad de texel coherente.
- UV2/lightmap para geometría estática que use `LightmapGI`.
- Verificar que no hay caras con área UV cero.

### 6.5. Materiales PBR

- Un material = un conjunto coherente de superficies; evitar decenas de materiales por prop.
- Albedo en sRGB; normal, roughness, metallic y AO en lineal.
- Empaquetar ORM cuando el motor lo aproveche.
- Respetar valores medidos: metal/roughness, no “todo metallic 1.0”.
- No usar emisión para simular iluminación de sala; las luces van en Godot.

### 6.6. Texturizado y baking

- Desgaste, suciedad, óxido, rayones y humedad deben tener una causa física y narrativa.
- Usar máscaras de curvatura/AO para bordes y cavidades; no ruido aleatorio uniforme.
- Baking high→low para normales, AO, curvatura, ID y thickness cuando aporte.
- Resolución objetivo: 1K/2K; 4K solo para un hero asset aprobado.
- Revisar seams, skewing, waviness y márgenes.

### 6.7. Rigging y animación

- Un solo armature por personaje/criatura, con naming claro y pesos ≤4 influencias por vértice.
- Validar deformación en poses extremas (agacharse, correr, girar, recibir daño, ser auxiliado).
- Animaciones: idle, walk, run, crouch, jump, interact, carry, hide, hit, incapacitated, death; criaturas según diseño.
- Root motion solo si el sistema de locomoción lo usa; documentarlo.
- Exportar clips por nombre y con loop correcto.

### 6.8. QA en Blender

Antes de exportar:

- `blender-asset-qa` / `qa_check.py` sobre el asset.
- Normales consistentes, sin caras invertidas, non-manifold, degeneradas, duplicados, n-gons problemáticos.
- Escala aplicada, origen correcto, UVs presentes, materiales asignados.
- Sin objetos ocultos, cámaras, luces ni helpers dentro del export.
- Revisión multiángulo renderizada.

### 6.9. Exportación

Preset base para Godot:

- glTF 2.0 binario (`.glb`).
- `export_apply=True`, `export_yup=True`, `export_animations=True` cuando aplique.
- Sin cámaras ni luces.
- Texturas en PNG/WebP; normales/ORM sin pérdida agresiva.
- LODs como mallas separadas o configuración de importación; no confiar en LODs automáticos si el asset se carga en runtime.
- Colisión: `-col`/`-colonly` o `UCX_` documentado; para el pipeline nuevo, preferir el importador nativo de Godot.
- Manifiesto JSON y licencia junto al GLB.

---

## 7. Pipeline Godot — integración

### 7.1. Importación

- Usar el **importador nativo** de Godot para assets nuevos: `.glb` con `.import`, presets de importación y LODs.
- No usar `GLTFDocument.append_from_file()` para assets finales nuevos. El camino runtime queda solo para el Nivel 1 heredado mientras se migra.
- Configurar:
  - Escala y ejes.
  - Generación de LODs y `visibility_range`.
  - Colisiones (`-col`, `-colonly`, trimesh/convex).
  - Materiales y texturas.
  - Animaciones y `AnimationLibrary`.
  - Sombras y mallas de sombra.
- Verificar el asset en una escena aislada antes de integrarlo.

### 7.2. Materiales

- Los materiales base viven en el asset o en recursos `.tres` reutilizables.
- Los overrides en runtime solo para efectos (emisión, daño, interactabilidad), no para corregir un PBR mal hecho.
- Evitar duplicar materiales por instancia.

### 7.3. Colisiones y físicas

- Colisión coherente con la geometría; no AABB sobredimensionadas por rotación.
- Objetos decorativos sin física completa; objetos interactivos con `RigidBody3D`/`StaticBody3D` según función.
- Masas, fricción y damping documentados.
- Puertas, ascensor, objetos transportables y extracción con pruebas dedicadas.
- Nada flota: el punto de apoyo debe coincidir con el suelo o con la superficie de apoyo.

### 7.4. Iluminación y atmósfera

- La recepción es la única zona con iluminación ambiental relativamente funcional.
- Fuera de recepción: oscuridad legible con linterna, emergencias débiles y localizadas, fuentes visibles.
- Sin rellenos artificiales ni luz residual de cámara/ojos.
- Sombras selectivas, niebla volumétrica, partículas y postprocesado medidos por rendimiento.
- La iluminación se autora en Godot; Blender solo para lookdev/previsualización.

### 7.5. Audio

- Buses: Master, Music, Ambience, SFX, Voice, Radio, UI.
- Audio 3D posicional, atenuación, reverb zones, oclusión y Doppler cuando corresponda.
- Sonidos de pasos por material, objetos, puertas, maquinaria, criaturas, radio e interferencias.
- Silencios intencionados; no música constante ni sonidos aleatorios sin diseño.
- Los assets de audio deben tener fuente/licencia y no reutilizar el sintetizador de otro proyecto sin revisión.

### 7.6. Navegación e IA

- `NavigationRegion3D` horneado por zona; `NavigationAgent3D` para criaturas.
- Evitación, links, obstáculos dinámicos y costes por tipo de criatura.
- Validar que cada criatura cabe, gira y persigue sin bloqueos accidentales.
- La IA no detecta globalmente: usa visión, sonido, distancia, iluminación y escondites.

### 7.7. Pruebas y rendimiento

- Prueba aislada del asset.
- Prueba de sala (visual + colisión + navegación + audio).
- Prueba de nivel (recorrido, puertas, extracción).
- Perfilado en 1280×720 y 1920×1080, VSync off, GTX 1650 Ti.
- Capturas off/on de linterna y comparación de luminancia.
- Regresión: smoke, doors, walk, perf; añadir pruebas específicas de la sala piloto.

---

## 8. Clases de asset y puertas de aprobación

| Clase | Ejemplos | Presupuesto orientativo | Puerta |
|---|---|---|---|
| Arquitectura modular | pared, suelo, techo, viga | 2k–20k tris por módulo | Blockout + métricas + UV |
| Hero prop | generador, caldera, consola | 25k–80k tris | QA + PBR + LOD + colisión |
| Prop secundario | caja, silla, extintor, tubería | 5k–25k tris | QA + PBR |
| Prop pequeño | lata, papel, herramienta | 500–5.000 tris | QA + PBR |
| Personaje | trabajador | 60k–100k tris LOD0 | Rig + animación + QA |
| Criatura | Imitador/Vigilante/Coleccionista/Sombra | 80k–150k tris LOD0 | Sculpt + retopo + rig + anim + QA |

Puertas obligatorias:

1. **Brief aprobado** (función, dimensiones, referencias, licencia).
2. **Blockout aprobado** (escala, proporciones, circulación).
3. **Arte aprobado** (topología, UV, PBR, texturas, QA).
4. **Integración aprobada** (import, colisión, LOD, audio, luz).
5. **Rendimiento aprobado** (presupuesto y perfil).

Ninguna puerta se salta por “luego lo arreglamos”.

---

## 9. Versiones, backups y licencias

- Un `.blend` maestro por asset/kit; las versiones antiguas se archivan, no se acumulan en la raíz.
- Cada export tiene manifiesto y licencia.
- No se borran archivos existentes sin autorización; la limpieza se hace con inventario y backup.
- Los 222 assets Poly Haven deben revisarse antes de distribuir. Mientras no se verifiquen, se consideran **no aprobados para release**.
- El repositorio conserva fuente, export, manifiesto y capturas de QA.

---

## 10. Habitación piloto: Mantenimiento / Sala de máquinas

### Por qué

- Es una sala autónoma, de tamaño medio, con identidad industrial clara.
- Combina arquitectura, tuberías, generador, caldera, bancada, puerta, iluminación de emergencia, vapor, audio y interacción.
- Es uno de los puntos visualmente más débiles del nivel actual: generador portátil EN2500, caldera cilíndrica lisa, remaches invisibles, etiqueta flotante y vapor ausente.
- No es la recepción ni la extracción, por lo que se puede trabajar sin poner en riesgo el flujo principal.
- Permite medir antes/después con capturas y pruebas concretas.

### Alcance

- Conservar la arquitectura y el recorrido existentes; no reconstruir el nivel.
- Producir en Blender: generador industrial fijo, caldera, tuberías, bancada, pequeñas piezas y desgaste.
- Materiales PBR, UVs, baking y LODs.
- Colisiones coherentes y objetos apoyados.
- Iluminación de terror con fuentes visibles y emergencia localizada.
- Audio ambiental/posicional: zumbido, vapor, metal, pasos.
- Interacción mediante mirada, distancia y línea de visión.
- Capturas off/on y perfilado.

### Fuera de alcance

- Las otras 11 zonas.
- Criaturas completas y multijugador.
- Cambios masivos de arquitectura.
- Sustituir el arte por primitivas procedurales.

### Criterios de aceptación

- La sala se ve coherente con las referencias y con el resto del nivel.
- No hay objetos flotando, z-fighting, UVs rotas ni materiales planos.
- La oscuridad cumple la regla (off ≤5 de luminancia media fuera de recepción; on legible).
- Las colisiones permiten caminar, agacharse, ocultarse y manipular.
- El audio tiene fuente y espacialización; no es ruido aleatorio.
- 1080p ≥60 FPS en la sala piloto, sin degradar el nivel; VRAM y draws dentro de presupuesto.
- Smoke/doors/walk/perf siguen pasando.

---

## 11. Riesgos y controles

| Riesgo | Control |
|---|---|
| El GLB runtime impide LOD/import | Migrar assets nuevos al importador; mantener runtime solo para el nivel heredado |
| Máster con 1.675 mallas sin UV | QA bloqueante; no exportar sin UV |
| Assets externos sin licencia | Manifiesto + licencia antes de aprobar |
| 539 `.blend` y versiones duplicadas | Un maestro por asset; archivo de versiones |
| MCP de Blender se desconecta | Guardar con frecuencia; verificar puerto 9876; no depender de una sola sesión |
| Sin plantillas de exportación | Aprobar descarga/instalación antes de P3; no declarar build |
| Audio heredado de otro juego | Rehacer buses y assets con diseño propio |
| Rendimiento 1080p justo | Perfilar antes/después; presupuesto por sala |

---

## 12. Definition of Done de un asset

Un asset está terminado cuando:

1. Tiene brief, referencias y licencia.
2. Escala/origen/nombres correctos.
3. Topología, normales y UVs validados.
4. Materiales PBR y texturas aprobadas.
5. LODs y colisión (si aplica).
6. Rig/animaciones (si aplica) validados.
7. QA de Blender y revisión visual.
8. Importado en Godot con preset, sin overrides correctivos.
9. Probado en sala y en rendimiento.
10. Manifiesto y capturas archivados.

---

## 13. Aprobaciones necesarias antes de producir

1. Aprobar este pipeline y el estándar de calidad.
2. Aprobar **Mantenimiento** como habitación piloto y su alcance.
3. Aprobar la migración de assets nuevos al importador nativo de Godot.
4. Aprobar el presupuesto de rendimiento de la sala piloto.
5. Aprobar la política de licencias y la revisión de los 222 assets Poly Haven.
6. Aprobar el orden de producción de criaturas (propuesta: Vigilante primero, por su IA y presencia en el vertical slice).

Hasta que estas aprobaciones existan, no se reconstruyen habitaciones ni se modifican assets de forma masiva.

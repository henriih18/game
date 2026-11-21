# FRECUENCIA MUERTA — ESTÁNDAR DE CALIDAD

**Estado:** aprobado como estándar de realismo adaptativo (2026-11-06). Desarrolla y complementa `AGENTS.md`; no lo sustituye.
**Ámbito:** Nivel 1 y futuros assets de producción.
**Referencias:** `AGENTS.md`, `docs/FM_LEVEL1_FULL_AUDIT.md`, `docs/FM_TOOLS_AND_SKILLS_AUDIT.md`, `docs/FM_PRODUCTION_PIPELINE.md`.

---

## 1. Principio rector

Un asset no se aprueba por “verse bien en una captura”. Se aprueba cuando cumple criterios medibles, funciona dentro de Godot y no degrada el rendimiento, la legibilidad ni la experiencia de terror.

La calidad de FRECUENCIA MUERTA es **industrial, húmeda, deteriorada y creíble**, con oscuridad intencional y luz física. No es terror genérico, ni estética de prototipo, ni iluminación de relleno para que “se vea todo”.

---

## 2. Severidades y puertas de aprobación

| Nivel           | Definición                                                                                           | Consecuencia                                  |
| --------------- | ---------------------------------------------------------------------------------------------------- | --------------------------------------------- |
| **BLOQUEANTE**  | Impide jugar, exportar, atravesar una puerta, completar la extracción o provoca errores de recursos. | No se aprueba la fase.                        |
| **MAYOR**       | Se ve o se juega mal de forma evidente; rompe la identidad visual, la física o el terror.            | Se corrige antes del cierre de la fase.       |
| **MENOR**       | Detalle pulible que no impide jugar ni exportar.                                                     | Se registra y se corrige antes de la entrega. |
| **OBSERVACIÓN** | Mejora deseable o deuda futura.                                                                      | No bloquea, pero debe tener seguimiento.      |

Cada entrega debe incluir evidencia: capturas, mediciones, logs de test y lista de defectos. “Funciona” sin prueba no es un criterio válido.

---

## 3. Escala, unidades y convenciones

- Unidad de trabajo: **1 unidad = 1 metro**.
- Escala aplicada en Blender: `(1,1,1)` antes de exportar. Cero escalas no unitarias en assets nuevos.
- Origen: base del objeto, bisagra de puerta, punto de apoyo o pies del personaje. No dejar orígenes arbitrarios.
- Ejes: Blender Z-up; exportación glTF Y-up. Godot Forward+.
- Nombres:
  - `SM_` malla estática, `SK_` skeletal mesh, `T_` textura, `M_` material, `COL_` colisión, `LOD0/1/2`, `SM_*_DOOR`, `SM_*_PROP`.
- Jerarquía: una colección por sala/sistema; una raíz por asset; sin objetos sueltos sin padre.
- Métricas humanas:
  - Cápsula del jugador: radio **0,38 m**, altura **1,70 m**.
  - Puertas: **1,58 × 3,00 m**.
  - Pasillo principal: **3,4 m** de ancho, **3,0 m** de altura libre.
  - Recepción: **16 × 10 m**; seguridad: **10 × 8 m**.
  - Criaturas: Imitador **2,2–2,5 m**; Vigilante **2,5–3,0 m**; Coleccionista **2,0–2,5 m**; Sombra **2,0–2,5 m**.

---

## 4. Arquitectura y escenarios

### 4.1 Geometría

- Cero non-manifold no intencionales en mallas de arquitectura y props.
- Cero caras degeneradas, cero vértices duplicados en la malla final.
- Normales consistentes; smoothing por ángulo y Weighted Normal donde corresponda.
- Biseles visibles en aristas duras; no aristas “de cuchillo” sin intención.
- Módulos reutilizables con pivotes en grid; juntas y encuentros sin huecos visibles.
- Techo, suelo y paredes deben cerrar visualmente; no dejar “cajas” sin remate.

### 4.2 Escala y función

- Cada habitación debe poder explicar su función por su composición, mobiliario y circulación.
- No reducir una sala a la mínima caja que contiene sus objetos.
- Validar con cápsula del jugador y, cuando corresponda, con el volumen de la criatura.
- Dejar espacio de maniobra para girar, agacharse, transportar objetos y usar escondites.
- Los objetos deben apoyarse en el suelo o en superficies; tolerancia visual **≤ 2 mm**. Nada flota.

### 4.3 UV y texel density

- **0 mallas texturizadas sin UV**.
- **0 triángulos con área UV cero**.
- UVs sin solapamiento salvo espejado intencional; margen de **4–8 px** a 1024.
- Texel density orientativa:
  - Superficies hero: **512 px/m**.
  - Props medios: **256–512 px/m**.
  - Props pequeños: **128–256 px/m**.
- UV2/lightmap solo para geometría estática que lo requiera; documentar si se usa.

### 4.4 Colisiones

- La colisión corresponde a la forma real, no al AABB de una malla rotada.
- Preferir primitivas: caja, cápsula, esfera, convex hull; máximo **1–3 shapes** por prop.
- Puertas, ascensor, escaleras y rampas requieren prueba de paso con cápsula real.
- No usar colliders invisibles sobredimensionados que bloqueen pasillos o vanos.
- Los objetos físicos deben tener masa y fricción coherentes; no masas por defecto sin revisar.

---

## 5. Props y objetos

- Geometría trabajada: biseles, uniones, tornillos, paneles, ranuras, desgaste; no cajas lisas como resultado final.
- PBR correcto: metal/roughness medidos; evitar `metallic=1.0, roughness=1.0` por defecto.
- Pivote y escala coherentes; el objeto se puede colocar en escena sin ajustes manuales.
- LOD cuando el prop se repita o tenga protagonismo; LOD0/LOD1/LOD2 documentados.
- Colisión y física probadas: recoger, soltar, transportar, empujar, bloquear.
- Sonido asociado si el objeto es interactivo o recuperable.
- Los objetos recuperables deben respetar peso, volumen y reglas de transporte; no todos son “recogibles”.

### Presupuesto orientativo de props

| Tipo                              | Triángulos LOD0 | Materiales | Texturas  |
| --------------------------------- | --------------: | ---------: | --------- |
| Pequeño (lata, documento)         |       500–5.000 |        1–2 | 512–1024  |
| Medio (caja, radio, herramienta)  |    5.000–20.000 |        2–4 | 1024      |
| Hero (generador, caldera, equipo) |   20.000–40.000 |        3–6 | 1024–2048 |
| Criatura LOD0                     |  60.000–120.000 |        3–6 | 2048      |

Los límites son objetivos iniciales; se validan con medición y se ajustan con aprobación.

---

## 6. Materiales y texturas

- PBR metálico/roughness. Nada de materiales “yeso” o plástico plano por defecto.
- Albedo/base color en **sRGB**; normal, roughness, metallic, AO y ORM en **Non-Color/Linear**.
- Normales en **OpenGL** para Godot; documentar si un asset viene en DirectX.
- Empaquetado ORM cuando el pipeline lo requiera; no duplicar mapas innecesarios.
- Resoluciones máximas: **2048** para hero, **1024** para props, **512** para pequeños.
- Mipmaps activos; compresión S3TC/BC para albedo opaco; normales y ORM con compresión controlada.
- Cero texturas faltantes, cero rutas absolutas, cero recursos fuera del proyecto.
- Desgaste intencionado: bordes, cavidades, humedad, polvo, arañazos; no ruido aleatorio uniforme.
- Los materiales deben verse coherentes bajo la iluminación real del nivel, no solo en el visor de Blender.

---

## 7. Iluminación y atmósfera

### 7.1 Regla de oscuridad

- **La recepción es la única zona con iluminación ambiental relativamente funcional.**
- Fuera de recepción, sin linterna la media de luminancia debe ser **≤ 5** y el p95 **≤ 15** en captura representativa.
- Con linterna, la sala debe ser legible: paredes, suelo, obstáculos, puertas y objetos interactivos.
- La oscuridad no puede ocultar una muerte inevitable ni un objetivo sin pista visual.

### 7.2 Fuentes y sombras

- Toda luz debe tener una fuente física visible y coherente (luminaria, emergencia, pantalla, ventana, linterna).
- Prohibidos los rellenos ambientales sin fuente, los charcos de luz sin luminaria y la iluminación uniforme de pasillos.
- Sombras selectivas: linterna + 1–2 luces principales por sala; no 30 sombras simultáneas.
- Luces de emergencia: energía runtime **0.15–0.35**, rango **2,5–4,5 m**, localizadas y justificadas.
- Emisivos y bloom moderados; los carteles no deben quemarse a blanco.
- Volumétrica, niebla y partículas al servicio de la profundidad, no para tapar geometría pobre.

### 7.3 Criterios de captura

- 12 zonas × off/on, misma cámara y exposición.
- Medir luminancia media y p95; adjuntar tabla.
- Revisar fugas de luz, sombras incorrectas, materiales quemados y artefactos de espejo.
- Captura “bonita” no equivale a sala correcta: validar también colisiones, navegación y audio.

---

## 8. Física y colisiones

- Ningún objeto flota; los props deben asentarse en **≤ 2 s**.
- Colisiones coherentes con la geometría; no cajas invisibles que bloqueen pasos.
- Masas y fricciones revisadas por tipo: caja de cartón, metal, cadáver, puerta, generador.
- CCD en objetos rápidos o pequeños; no atravesar paredes.
- Puertas: abren, cierran, bloquean el paso cerradas y lo permiten abiertas; probar 6/6.
- Ascensor: hojas sincronizadas, colisión correcta, sin penetraciones.
- Objetos transportados: agarre estable, sin vibración, sin teletransporte, sin pérdida de colisión.
- Pruebas con cápsula real y, cuando exista, con dos jugadores.

---

## 9. Personajes y criaturas

### 9.1 Identidad

- Respetar `fotos-referencia/modelos-referencia.png`: silueta, anatomía, proporciones, materiales y rasgos de las cuatro criaturas.
- No sustituir criaturas por cápsulas, esferas o cajas ensambladas por script.
- Cada criatura debe ser reconocible en baja iluminación por silueta, sonido y comportamiento.

### 9.2 Malla y materiales

- Topología de deformación limpia; quads/tris, sin n-gons problemáticos.
- UVs completas, sin estiramientos; texel density coherente.
- Piel, tejido, metal, goma y fluidos con materiales diferenciados.
- LOD0/LOD1/LOD2 y colisión/cápsula documentados.
- Sin interpenetraciones visibles en poses de animación.

### 9.3 Rig y animación

- Esqueleto con naming consistente, roll correcto, colecciones de huesos y controles.
- Pesos sin artefactos; probar hombro, cadera, rodilla, cuello y mandíbula.
- Animaciones mínimas: idle, patrol/walk, investigate, chase/run, attack, hit/stun, death/despawn.
- Root motion cuando corresponda; sin deslizamiento de pies > 5 cm.
- Transiciones < 0,2 s y loops sin pop.
- No entregar T-pose en juego.

### 9.4 IA y percepción

- Cada criatura tiene sentidos y estados propios; no una IA universal.
- Vigilante: se detiene al ser observado, se mueve al perder contacto visual, investiga ruido y flanquea.
- Imitador: engaña con voces/sonidos, separa al equipo; no es un perseguidor genérico.
- Coleccionista: busca objetos, roba, reacciona a ruido y prioriza portadores.
- Sombra: usa oscuridad, aislamiento y apariciones; no debe ser injusta.
- Probar navegación, escondites, dos jugadores y situaciones de captura.

---

## 10. Animación

- 30/60 fps según clip; loop perfecto en idle/walk/run.
- Sin congelaciones, pops, T-pose ni cambios de escala.
- Animaciones de puertas, ascensor, objetos y criaturas integradas en Godot.
- AnimationTree/state machine para criaturas y jugador remoto.
- Pruebas en runtime, no solo en Blender.

---

## 11. Audio

- Buses mínimos: `Master`, `Music`, `SFX`, `Ambience`, `UI`, `Voice`, `Radio`.
- Audio 3D posicional con atenuación, distancia y oclusión cuando sea viable.
- Reverberación por espacio: pasillo metálico, laboratorio, sala de máquinas, recepción.
- Sonidos de pasos por material; correr, caminar y agacharse con niveles distintos.
- Criaturas con identidad sonora reconocible; no sonidos aleatorios.
- Radio: interferencia, estática, pérdida de señal y engaños del Imitador con pistas coherentes.
- Sin clipping; niveles medidos. Silencios intencionados.
- No usar audio heredado de otro proyecto como sustituto del diseño final.

---

## 12. Gameplay e interacción

- Movimiento FPS consistente: caminar, correr, saltar, agacharse, fatiga.
- Linterna real: encendido/apagado, batería, recarga, sin luz residual desde cámara.
- Interacción por mirada, distancia y línea de visión; sin atravesar puertas.
- Feedback visual y sonoro en cada interacción.
- Inventario/carry: peso, volumen, manos ocupadas, drop, entrega.
- Escondites: entrar, salir, cámara, colisión, detección.
- Extracción en recepción: activación, entrega, secuencia, cancelación y resultados.
- No armas, no combate, no matar criaturas.

---

## 13. Rendimiento

Objetivos de producción (medidos en GTX 1650 Ti 4 GB, Forward+, VSync off):

| Métrica          | Objetivo |
| ---------------- | -------: |
| 1280×720         | ≥ 55 FPS |
| 1920×1080        | ≥ 45 FPS |
| VRAM             | < 3,2 GB |
| Draw calls       |    < 500 |
| Objetos          |  < 5.000 |
| Frame time 1080p |  ≤ 22 ms |

- Perfilar antes de optimizar; no atribuir caídas a la iluminación sin evidencia.
- LOD y occlusion culling en salas y props repetidos.
- Presets Low/Medium/High/Ultra y render scale.
- Sin stutter por compilación de shaders; precargar y calentar.
- Medir con criaturas, partículas, audio y dos jugadores antes de declarar rendimiento final.

---

## 14. Multijugador

- Autoridad del servidor sobre puertas, criaturas, botín y extracción.
- Sincronización de jugadores, objetos y estados; reconexión.
- Prueba real con **dos clientes**, no solo simulación de late join.
- Sin divergencias de estado, duplicación de objetos ni teletransportes.
- Soak test de 10 minutos con criaturas y objetos.

---

## 15. Build y producción

- Assets nuevos por el **importador nativo** de Godot; evitar `GLTFDocument` en runtime para assets de producción.
- `export_presets.cfg` y plantillas de exportación instaladas.
- Build Linux y Windows probada en carpeta limpia.
- Sin recursos faltantes, rutas absolutas ni dependencias del editor.
- El nivel arranca, completa las 12 zonas y extrae sin errores.
- Documentar licencias y procedencia de todos los assets externos.

---

## 16. Evidencia y Definition of Done

Un asset/sala se considera terminado cuando:

1. Cumple los criterios de su categoría.
2. Tiene capturas off/on y métricas.
3. Tiene pruebas funcionales y de colisión.
4. Tiene QA de topología/UV/materiales.
5. No introduce regresiones en smoke/doors/walk/perf.
6. Está documentado y versionado.
7. Ha pasado la puerta de aprobación correspondiente.

Sin evidencia, el estado es **“en progreso”**, no “terminado”.

---

## 17. Aplicación al piloto: Mantenimiento

La sala de máquinas debe cumplir todo lo anterior y además:

- Generador y caldera con geometría creíble, no primitivas lisas.
- Tuberías, válvulas, bancada, tablero y extintores con PBR y desgaste.
- Objetos apoyados; cero flotación.
- Iluminación local de trabajo + emergencia; oscuridad legible con linterna.
- Audio de maquinaria, vapor, crujidos y pasos metálicos.
- Interacción con generador/panel y un objeto recuperable.
- Colisiones coherentes y paso del jugador.
- 1080p ≥ 45 FPS en la sala y sin fugas de luz.

---

## 18. Excepciones

Cualquier excepción a este estándar debe documentarse con:

- Motivo técnico o artístico.
- Alcance.
- Riesgo.
- Aprobación explícita.
- Fecha de revisión.

No se aceptan excepciones verbales ni “temporalmente” sin registro.

---

## 19. Reglas de realismo adaptativo para Blender

Cada vez que se modele un objeto, primero se **identifica su categoría** y se aplica el tipo de detalle y material adecuado. **Nunca se usa un estilo único para todo.**

### 19.1. Análisis de categoría (elegir una)

**A) Hard surface / mecánico / sci-fi** (robots, armas, naves, máquinas)

- Detalles: panel lines (inset + extrude), pernos/tornillos en uniones, rejillas de ventilación, cortes booleanos.
- Bordes: bevel pronunciado (Segments: 3–4) para capturar luz en metales.

**B) Orgánico / natural** (rocas, madera, plantas, comida)

- Detalles: **nunca** paneles ni pernos. Usar Displace o Multires con texturas de ruido para irregularidad natural.
- Bordes: irregulares, asimétricos, sin simetría perfecta.

**C) Objetos cotidianos / mobiliario** (tazas, sillas, mesas, electrodomésticos)

- Detalles: uniones realistas (por ejemplo, patas de mesa que se unen suavemente), costuras si es tela, bordes ligeramente desgastados.
- Bordes: bevel sutil (Segments: 2–3) para suavizar aristas; nada de cortes mecánicos agresivos.

**D) Arquitectura / estructuras** (edificios, muros, habitaciones)

- Detalles: marcos de ventanas, zócalos, ladrillos o textura de concreto, desgaste en esquinas inferiores.

**E) Estado de conservación: ABANDONO / VIEJO / POST-APOCALÍPTICO**
Aplicar a **cualquier objeto** cuyo contexto sea "abandonado", "viejo", "deteriorado", "post-apocalíptico" o "en desuso". Esta regla **se superpone** a la categoría principal (A, B, C o D).

**REGLA GLOBAL DEL PROYECTO:** Dado que el contexto general es un complejo abandonado, **TODOS** los objetos se modelarán por defecto en estado deteriorado, viejo o sucio.
**Solo** se modelará un objeto como "nuevo", "limpio" o "reparado" si el usuario lo especifica **explícitamente** en el prompt (ej: "esta computadora fue reparada recientemente").

**Geometría (degradación física visible):**

- Deformaciones sutiles en superficies planas (usar `Displace` con ruido suave o mover vértices manualmente).
- Paneles sueltos, ligeramente desencajados o inclinados.
- Cables colgando (usar curvas Bezier con física o geometría extruida).
- Escombros alrededor: fragmentos de concreto, vidrios rotos, papeles arrugados, latas aplastadas.
- Bordes astillados o rotos (usar operaciones `Boolean` negativas aleatorias en aristas).
- Objetos caídos o inclinados (ningún objeto abandonado está perfectamente alineado).
- Vegetación invasiva: musgo, enredaderas o hierba creciendo en grietas (instancias de partículas o geometría simple).

**Materiales (capas de degradación obligatorias):**

- Óxido en metales expuestos.
- Suciedad acumulada (grime) en esquinas inferiores y grietas.
- Pintura descascarada o descolorida.
- Manchas de humedad y moho (zonas verdes/negras).
- Amarillamiento en plásticos y papeles.
- Polvo acumulado en superficies horizontales superiores.
- marcas de desgaste humano (opcional, según contexto).

### 19.2. Materiales (PBR y Procedurales)

Nunca se usa un material plano. Adaptar los nodos al material y contexto.

**A) Texturas PBR del usuario (MÉTODO PREFERIDO):**
Si el usuario proporciona texturas en `//assets/textures/`, configurar los nodos así:

1. `Image Texture` (Color/Albedo) → `Base Color` del Principled BSDF.
2. `Image Texture` (Roughness) → **`image.colorspace_settings.name = 'Non-Color'`** → `Roughness`.
3. `Image Texture` (Normal) → **`image.colorspace_settings.name = 'Non-Color'`** → `Normal Map` → `Normal`.

- Usar rutas relativas: `//assets/textures/[nombre].jpg`.
- Si hay mapa de desplazamiento: conectarlo a un nodo `Displacement` con subdivisión adaptativa.

**B) Materiales procedurales para ABANDONO (ESTADO POR DEFECTO):**
Aplicar cuando el objeto no tiene textura PBR disponible.

- **Metal oxidado:** `Mix Color` para mezclar el color base con tonos marrones/naranjas oscuros, usando `Noise Texture` (Scale: 15–30) como Factor. Conectar esa misma Noise a `Roughness` (0.7–0.9) y a un nodo `Bump` (Strength: 0.1–0.2).
- **Concreto deteriorado:** `Noise Texture` (Scale: 5–10) → `ColorRamp` (oscurecer valores bajos) → `Base Color` para manchas de humedad. `Ambient Occlusion` → `ColorRamp` (invertir) → mezclar con el color base para oscurecer grietas.
- **Madera podrida:** `Wave Texture` o `Musgrave Texture` alargada en un eje → `ColorRamp` (tonos marrones oscuros/grises) → `Base Color`. `Roughness` alta (0.7–0.9).
- **Plástico/vidrio envejecido:** Amarillamiento (mezclar con amarillo pálido, Factor: 0.3–0.5). `Roughness` aumentada (0.4–0.6).
- **Tela desgastada:** `Bump` sutil (Strength: 0.01–0.02) con Noise a escala alta + manchas con `Mix Color` y Noise de escala baja.

**C) Materiales procedurales para objetos NUEVOS (SOLO si se pide explícitamente):**
Aplicar únicamente cuando el usuario especifique "nuevo", "limpio", "reparado" o "prístino".

- **Metal/plástico limpio:** Noise Texture (Scale: 80–150) → ColorRamp → Roughness (micro-arañazos sutiles).
- **Madera nueva:** Noise o Musgrave Texture (Scale: 10–20, alargado en un eje) → ColorRamp → Base Color y Roughness.
- **Tela/cuero nuevo:** Bump muy sutil (Strength: 0.01–0.02) con Noise a escala alta para simular tejido.

**D) Capa universal de suciedad (OBLIGATORIA para todos los objetos abandonados):**

- Añadir un nodo `Ambient Occlusion` → `ColorRamp` (invertido: negro en zonas expuestas, marrón oscuro en grietas) → mezclar con `Base Color` usando `Mix Color` (Factor: 0.3–0.5).
- Esto simula polvo y mugre acumulada en rincones de forma automática y realista.
- Aplicar SIEMPRE a menos que el objeto sea explícitamente "nuevo/reparado".

### 19.3. Reglas universales (todos los objetos)

- **Escala real:** dimensiones del mundo real (metros/centímetros).
- **Bordes reales:** **siempre** aplicar un modificador Bevel (mínimo 2 segmentos). En el mundo real no existen aristas de 0 mm.
- **Topología:** mantener quads limpios. Ejecutar `bpy.ops.mesh.remove_doubles()` y recalcular normales al final.
- **Iluminación:** eliminar la luz por defecto. Usar 2–3 Area Lights grandes para sombras suaves y realistas.
- **Cámara:** distancia focal 50 mm (estándar) u 85 mm (retrato/producto). Activar Depth of Field si es un objeto pequeño.
- **Render:** motor CYCLES, mínimo 128 samples, con Denoise activado.

### 19.4. Flujo de trabajo

1. Identificar la categoría del objeto solicitado.
2. Crear el blockout con escala real.
3. Añadir los detalles específicos de esa categoría (no mezclar categorías).
4. Aplicar el material procedural contextual.
5. Configurar luces, cámara y renderizar.

> **Nota de proyecto:** este estándar sustituye al estándar anterior basado en los casilleros Z10. El pase de casilleros queda como **ejemplo de aplicación**, no como norma única. Cualquier excepción debe documentarse y aprobarse; no se aceptan excepciones verbales.

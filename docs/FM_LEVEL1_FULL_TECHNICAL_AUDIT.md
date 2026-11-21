# FRECUENCIA MUERTA — Auditoría técnica y artística integral del Nivel 1

**Fecha:** 2026-11-04 (COT)  
**Ámbito:** Nivel 1 completo y sus 12 zonas.  
**Escena auditada:** `scenes/fm/level1.tscn`  
**Modo:** auditoría independiente de solo lectura. No se modificó ningún modelo, material, textura, escena, script ni configuración. El único archivo creado es este informe.  
**Motor:** Godot 4.7.2 stable. Renderer Forward+.  
**Fuentes de evidencia:** inspección directa de archivos, parseo de los GLB, pruebas runtime no destructivas, capturas actuales en `/tmp/opencode/`, documentación de las fases 3A.1–3A.3, y los artefactos de cinco auditorías paralelas.

---

## 0. Método, alcance y limitaciones

### 0.1. Método

1. Lectura de `AGENTS.md`, `docs/WORKLOG.md`, `docs/NEXUS_L1_MISSION_REPORT.md`, `docs/NEXUS_L1_MISSION_AUDIT.md`, `docs/NEXUS_L1_DOOR_AUDIT.md` y `docs/NEXUS_L1_EXTRACTION_PROCEDURE.md`.
2. Inspección de la escena, scripts y recursos reales del Nivel 1.
3. Parseo técnico de los GLB: nodos, mallas, triángulos, topología, UV, materiales, texturas y bounding boxes.
4. Pruebas runtime no destructivas: smoke, walk, puertas, físicas, luces, extracción y capturas por zona.
5. Contraste de las capturas con la dirección artística oficial: terror industrial cinematográfico, base fría cian/gris, acentos ámbar/rojos, oscuridad jugable y materiales PBR creíbles.
6. Revisión independiente por áreas: geometría/Blender, materiales PBR, físicas/colisiones, Godot/rendimiento e iluminación/arte.

### 0.2. Evidencias principales

- `assets/models/fm/level1_nexus.glb` — arquitectura y contenido original (41 MB).
- `assets/models/fm/art3a1/level1_art3a1_kit.glb` — kit de arquitectura 3A.1 (3,9 MB).
- `assets/models/fm/art3a2/level1_dressing.glb` — dressing 3A.2 (13 MB).
- `assets/models/fm/doors/level1_doors.glb` — kit de seis puertas 3A.3 (5,1 MB).
- `scripts/fm/level1.gd`, `scripts/fm/fm_level1_art_pass.gd`, `scripts/fm/fm_level1_door.gd`.
- `docs/fm_level1_art3a2_contact_sheet.png`, `docs/fm_level1_doors_contact_sheet.png`.
- Capturas actuales: `/tmp/opencode/final_*.png`, `/tmp/opencode/tour_*.png`, `/tmp/opencode/extra_*.png`, `/tmp/opencode/audit_*.png`.
- Evidencia de geometría: `/tmp/opencode/fm_l1_audit/glb_key_findings.txt`.
- Evidencia de materiales: `/tmp/opencode/fm_level1_readonly_audit/audit_materials.txt`.
- Evidencia de físicas: `/tmp/opencode/audit_level1_physics_v2.log` y `/tmp/opencode/audit_level1_physics.log`.

### 0.3. Limitaciones

- Tres auditorías auxiliares (geometría/Blender, Godot/rendimiento y físicas) no devolvieron su mensaje final por límite de uso de la herramienta. Sus scripts, logs y JSON sí se conservaron y se usaron como evidencia. Las conclusiones que dependían solo de su criterio se marcan como **NO VERIFICADO**.
- No se ejecutó una prueba con dos clientes ni una validación multijugador real. El propio `level1.gd` es offline.
- No se midió memoria de GPU, tiempo de carga exacto ni frame time con captura GPU. La medición de FPS disponible es de la fase 3A.3, no de esta auditoría.
- No se revisaron todas las orientaciones de todas las habitaciones. Las que faltan se indican.
- El encargo indica que las puertas no están implementadas funcionalmente. **El estado real del proyecto es que la fase 3A.3 sí las implementó.** Esta auditoría evalúa su estado actual, sus modelos y sus colisiones, pero no las modifica.
- Las etiquetas “APROBADA” de la documentación anterior no se aceptan como prueba de calidad final. Se contrastaron con archivos y capturas actuales.

---

## 1. Resumen ejecutivo

El Nivel 1 **no es un prototipo vacío**: existe una arquitectura completa, un pase artístico con más de 40 overrides, iluminación por zona, seis puertas con mecánicas, objetos físicos, loot, escondites, extracción, un Vigilante y pruebas funcionales que pasan. La recepción y el corredor tienen una composición y una profundidad que deben conservarse.

Sin embargo, **el nivel no alcanza el estándar de calidad final de FRECUENCIA MUERTA** y no debe declararse terminado. Los problemas más graves son:

1. **La extracción no cumple el procedimiento aprobado.** El contador solo acepta botín a ≤2,4 m del centro de extracción; no cuenta el objeto transportado por un jugador presente, aunque el documento lo exige. Un jugador puede llegar con el objeto en las manos y no poder extraer.
2. **Los colliders del ascensor no acompañan la animación de las hojas.** La puerta se abre visualmente, pero la colisión permanece cerrada.
3. **La arquitectura principal no tiene UV utilizables ni triplanar.** El pase artístico aplica texturas, pero sobre superficies sin coordenadas válidas. Esto invalida buena parte del trabajo PBR en suelos y paredes.
4. **El sistema de materiales tiene fugas sistémicas:** los overrides se saltan materiales duplicados, 21 texturas runtime no tienen mipmaps, el clearcoat húmedo se aplica a todos los suelos y varias normales/roughness son casi planas.
5. **Hay elementos visualmente provisionales en zonas protagonistas:** monitores cian planos, generador/caldera simples, cajas de almacén uniformes, lentes de emergencia que son cajas emisivas flotantes, vapor con aspecto de grumos y suelos con patrones que no leen como desgaste industrial.
6. **La física no está diseñada por objeto:** las hojas de puerta son `StaticBody3D`, los RigidBody no tienen damping ni material físico, y la generación automática de colliders AABB incluye decals como `WALLSTAIN`, con riesgo de bloqueos invisibles.
7. **La escalabilidad es frágil:** ~647.000 triángulos instanciados, 1.281 draw calls, 9.603 objetos y props pequeños de hasta 69.806 triángulos, sin LOD ni occlusion culling.

**Veredicto:** base jugable y visualmente reconocible, pero con deuda técnica y artística alta. Recepción y corredor son el estándar a preservar; seguridad, control, almacén, mantenimiento, oficina, aseo, conector, ascensor y extracción necesitan correcciones de material, iluminación, geometría y físicas antes de considerarse terminados.

### 1.1. Conteo de defectos

| Severidad | Cantidad |
|---|---:|
| CRÍTICO | 3 |
| ALTO | 22 |
| MEDIO | 16 |
| BAJO | 5 |
| **Total** | **46** |

---

## 2. Estado real del Nivel 1

### 2.1. Lo que existe y funciona

- Escena `scenes/fm/level1.tscn` con un `Node3D` raíz y `scripts/fm/level1.gd`.
- Carga runtime de cuatro GLB principales y props independientes.
- Jugador en primera persona con linterna, batería y movimiento.
- Seis puertas con tipos diferenciados: corredera automática, blindada con teclado, doble hoja secuencial, corredera pesada cooperativa, batiente ligera y batiente de mantenimiento.
- Loot físico, escondites, trampas de ruido, alarma, cajones, taquillas, extracción y Vigilante.
- Pase artístico con ~40 overrides PBR y luces cinematográficas.
- Pruebas existentes: smoke, walk, puertas, detalle, físicas y capturas.

### 2.2. Pruebas ejecutadas o verificadas

| Prueba | Resultado | Evidencia |
|---|---|---|
| Smoke | **PASS** | `TEST_LIGHTS true general=0 art=23 emergency=30 flashlight=3`; alarma, compuerta este, Vigilante, ruido, movimiento y extracción verdaderos |
| Walk | **PASS 33/33** | `WALK_RESULT reached=33/33 final=(-17.23759, -5.64919, -9.920031)` |
| Puertas | **PASS** según fase 3A.3 | `DOOR_TEST_FAILS 0`; seis cerradas/abiertas; teclado, cooperación, alerta, energía y serialización |
| Físicas runtime | Ejecutada | 572 `StaticBody3D`, 23 `RigidBody3D`, 6 `Area3D`, 2 `CharacterBody3D` |
| Rendimiento 3A.3 | Registrado | 99–101 FPS a 1280×720, 1.281 draws, 906.482 primitivas, 9.603 objetos |
| Rendimiento en esta auditoría | **NO VERIFICADO** | El log headless devolvió `fps=145 draws=0 primitives=0 objects=9854`; no es comparable con una medición con render real |

### 2.3. Advertencias de cierre

Al salir en modo headless aparecen errores de RIDs y recursos retenidos:

```text
ERROR: 32 RID allocations ... DummyMaterial
ERROR: 5 RID allocations ... DummyShader
ERROR: 157 RID allocations ... DummyMesh
ERROR: 53 RID allocations ... DummyTexture
ERROR: 157 RID allocations ... RendererSceneCull Instance
```

No impiden el funcionamiento de la partida, pero deben investigarse antes de una entrega porque indican que la carga runtime de GLB no libera todo lo que crea.

### 2.4. Estado documental

`docs/NEXUS_L1_MISSION_AUDIT.md` declara las zonas como “APROBADA” y, sin embargo, en el mismo documento reconoce props simples, pantallas placeholder, aseo sin azulejo, mantenimiento con generador plano y ausencia de LOD/occlusion. Esa contradicción es un defecto de documentación: una sala puede estar “vestida” y no estar terminada. El presente informe sustituye esa lectura complaciente por una evaluación de calidad real.

---

## 3. Evaluación individual de las 12 zonas

### 3.1. Recepción NEXUS

**Medidas:** 16 × 10 m, techo 5,7 m.  
**Fortalezas:** composición amplia y legible; mostrador con fascia verde, tapa de madera y mampara; directorio y panel corporativo; ascensor SALIDA; profundidad y contraste correctos; buena base para el estándar visual.  
**Defectos:** doble cristal de mostrador solapado con materiales distintos; directorio ilegible; pantalla/aro de extracción negro; dos rótulos SALIDA apilados; lente de emergencia como caja naranja flotante; sobreexposición especular en cristales y marcos; suelo con clearcoat global.  
**Veredicto:** la mejor zona del nivel, pero **no terminada**. Preservar composición y mobiliario; corregir materiales, señalización y extracción.

### 3.2. Corredor principal

**Medidas:** 44 × 3,4 m, techo 3,93 m.  
**Fortalezas:** longitud, ritmo de vigas, bandejas, tuberías, puertas y señalización; la profundidad funciona con y sin linterna; es el eje visual del nivel.  
**Defectos:** tramos largos de pared repetitivos; reflejos puntuales que parecen luces incrustadas; decals de suelo con bordes duros; bloom de señales que borra contenido; puertas con glare blanco; sin LOD/occlusion; acumulación de props físicos y colliders.  
**Veredicto:** conservar la composición y la arquitectura; corregir materiales, señalización y optimización.

### 3.3. Seguridad

**Medidas:** 10 × 8 m, techo 3,93 m.  
**Fortalezas:** mesa de monitores, rack, cámara, reloj y mobiliario; la sala ya no está vacía.  
**Defectos:** monitores cian planos con símbolos idénticos; pared trasera con grandes superficies oscuras; comparte lenguaje visual con Control; la puerta “blindada” no lee como blindada; `COL_297_NEXUS_V05_D_CORR_WALLSTAIN_0` (decal oculto) conserva `StaticBody` y se solapa con la apertura de la puerta; falta de narrativa de vigilancia.  
**Veredicto:** funcional, pero visualmente provisional. Necesita contenido de pantallas, identidad propia y limpieza de colisiones.

### 3.4. Control de acceso

**Medidas:** 8 × 8 m, techo 3,93 m.  
**Fortalezas:** consola, dos monitores, teclado, rack y señalización RAYOS X; la puerta doble secuencial tiene presencia.  
**Defectos:** consola es un bloqueo sin detalle funcional; monitores placeholder; el carro `COL_096_NEXUS_L1_DIS_CART_CORR_cart` interfiere con la apertura; exceso de superficie técnica lisa; misma utilería que Seguridad.  
**Veredicto:** blockout vestido, no sala terminada.

### 3.5. Vestuarios

**Medidas:** 10 × 8 m, techo 3,73 m.  
**Fortalezas:** taquillas, bancos, espejos y puerta ligera; la distribución se entiende.  
**Defectos:** taquillas idénticas y repetitivas; bancos como bloques; grandes paños laterales sin variación; panel esmerilado de la puerta opaco (`DOOR_Frost`, alpha 1,0, roughness 0,86) y demasiado claro por la luz de la sala; espejos oscuros sin reflexión local; dominancia ámbar; `COL_255_NEXUS_V05_B_VEST_VENT` interfiere con la apertura; decals de suelo planos.  
**Veredicto:** correcto como bloqueo, insuficiente como vestuario final.

### 3.6. Almacén

**Medidas:** 12 × 8 m, techo 3,93 m.  
**Fortalezas:** estanterías, carga, polipasto y puerta pesada; la función logística se reconoce.  
**Defectos:** cajas uniformes sin fibra, etiquetas, pliegues ni desgaste de aristas; la puerta pesada no se distingue lo suficiente; contorno naranja de suelo grueso y emisivo; sombras del dressing 3A.2 desactivadas, lo que hace flotar props; carros de almacén con 18.902 triángulos y 3.839 aristas non-manifold cada uno.  
**Veredicto:** la sala necesita reconstrucción de props y ajuste de luz/sombra, no solo retoques.

### 3.7. Mantenimiento

**Medidas:** 14 × 8 m, techo 4,73 m.  
**Fortalezas:** generador, caldera, banco de trabajo, herramientas, tuberías y vapor; la escala industrial es adecuada.  
**Defectos:** generador con gran disco y caja frontal de pocas conexiones; caldera naranja lisa con indicador quemado; banco y tablero casi vacíos; vapor como grumos blancos opacos; contorno de suelo naranja provisional; lámpara enjaulada de 22.893 triángulos y 48 non-manifold; sombras desactivadas en dressing.  
**Veredicto:** la zona con mayor brecha entre intención y resultado. Requiere reconstrucción de maquinaria y efectos.

### 3.8. Oficina

**Medidas:** 3,9 × 5,8 m, techo 2,85 m.  
**Fortalezas:** escritorio, estantería, silla, monitor y archivo; la escala es íntima y correcta.  
**Defectos:** pared posterior casi vacía; baldas desocupadas y sin soportes; tablón gris con líneas que parece placeholder; monitor cian simple; reloj plano; dominancia ámbar; falta de narrativa administrativa; silla/escritorio con overrides degradados.  
**Veredicto:** infra-decorada e incompleta. No es una oficina terminada.

### 3.9. Aseo

**Medidas:** ~4 × 3 m, techo 2,85 m.  
**Fortalezas:** volumen pequeño y claustrofóbico; espejo, botiquín, tabique y puerta.  
**Defectos:** en las orientaciones revisadas no se distingue con claridad lavabo ni inodoro; espejo casi negro; texto del botiquín aparentemente invertido; estantes son tablas sin soportes; pared lisa sin azulejo; jabón como bloque blanco; dominancia ámbar.  
**Veredicto:** no cumple la función sanitaria legible. Necesita reconstrucción de dressing y materiales.

### 3.10. Conector de servicio

**Fortalezas:** estrechez claustrofóbica y transición funcional; la proporción puede conservarse.  
**Defectos:** suelo beige/marrón con patrón tipo camuflaje, no humedad ni desgaste industrial; persiste sin linterna; decals y transiciones duras; iluminación ámbar; poca señalización de servicio.  
**Veredicto:** el problema es el acabado, no la idea espacial. Recuperable con material y luz.

### 3.11. Ascensor

**Fortalezas:** cabina legible, marco, reloj, foco, hoja metálica y código cromático de salida.  
**Defectos:** hojas oscuras casi lisas; control lateral diminuto; sin indicador de piso legible; dos rótulos SALIDA de distinto tamaño; pantalla/aro de extracción negro; **los colliders no siguen la animación**; la revisión interior no fue concluyente.  
**Veredicto:** visualmente aceptable a distancia, funcionalmente bloqueado. Es un defecto crítico.

### 3.12. Extracción

**Fortalezas:** trigger de recepción de 15,8 × 2,6 × 9,8 m; secuencia, temporizadores, entrega y pruebas; código cromático verde/ámbar/cian; el flujo se entiende.  
**Defectos:** el contador de entrega solo mira posición física del loot; no cuenta el objeto transportado por un jugador; pantalla y aro negros; dos SALIDA; lentes de emergencia flotantes; el procedimiento documento/código no coincide.  
**Veredicto:** la secuencia existe, pero la regla de entrega está mal implementada. Es el bloqueador funcional más importante del nivel.

---

## 4. Auditoría de Blender y geometría

### 4.1. Métricas verificadas

| GLB | Nodos | Mallas | Materiales | Triángulos instanciados | Topología |
|---|---:|---:|---:|---:|---|
| `level1_nexus.glb` | 2.035 | 1.905 | 137 | **647.397** | 25.010 boundary, 8.124 non-manifold, 192 inconsistentes, 78 degenerados, 5.197 duplicados |
| `level1_art3a1_kit.glb` | 8 | 8 | 8 | 23.992 | Limpio |
| `level1_dressing.glb` | 10 | 10 | — | 140.076 | 162 non-manifold, 108 duplicados en `DRESS_GreenPaint` |
| `level1_doors.glb` | 146 | 116 | 16 | 51.820 | Sin non-manifold ni degenerados |

### 4.2. Hallazgos

**G-01. La arquitectura original tiene topología sucia y UV inservibles.**  
`level1_nexus.glb` contiene 25.010 aristas de borde, 8.124 aristas non-manifold, 192 aristas inconsistentes, 78 triángulos degenerados y 5.197 duplicados. Además, 739 mallas texturizadas no tienen UV y 46.242 triángulos tienen área UV cero. No todo es visible —textos y señales usan materiales sólidos—, pero el conjunto indica que el GLB original no fue construido con un estándar de producción.

**G-02. Hay primitivas disfrazadas de objetos terminados.**  
Los monitores son cajas planas con un color emisivo y tres líneas; los generadores son cajas con un disco; las cajas de almacén son cubos uniformes; las lentes de emergencia son `BoxMesh` emisivos sin carcasa; los bancos de vestuario son bloques. La crítica no es que usen primitivas, sino que **no hay detalle funcional que las convierta en el objeto que representan**.

**G-03. Carros y props con coste y topología desproporcionados.**  
`NEXUS_ASSET_V05_MAINT_CART_industrial_storage_cart` y `V05_STORE_CART`: 18.902 triángulos cada uno, 3.839 non-manifold, 2.590 duplicados y 96 inconsistentes. Los carros de herramientas y de desastre alcanzan 29.394 triángulos y 96 non-manifold. La lámpara enjaulada `V05_MAINT_CAGED_LIGHT` tiene 22.893 triángulos y 48 non-manifold. Son objetos de primer plano, pero su presupuesto es de asset hero y su topología no está limpia.

**G-04. Props pequeños con presupuesto excesivo.**  
`potted_plant.glb` 69.806 triángulos; `chemistry.glb` 41.958 y 50 nodos; `radio.glb` 42.350; `power_box.glb` 21.272. Sin LOD, cada instancia repetida multiplica el coste. La planta y la radio no justifican ese presupuesto a la distancia de juego.

**G-05. El kit de puertas está bien construido a nivel de malla.**  
`level1_doors.glb` no tiene non-manifold ni degenerados; la jerarquía `DOOR_KIT_<ID>` con `Frame`, `LeafA`, `LeafB`, `Status`, `Sensor`, `Keypad`, `Manual` y `LabelAnchor_<ID>` es reutilizable. Es el mejor trabajo geométrico de las fases recientes y debe preservarse.

**G-06. El dressing 3A.2 tiene geometría duplicada.**  
`DRESS_GreenPaint` concentra 108 triángulos duplicados y el GLB suma 162 non-manifold. Puede producir z-fighting y sombreado inconsistente en vigas, paneles y listones.

**G-07. No hay una política de bevels y suavizado uniforme.**  
La arquitectura mezcla aristas vivas, biseles mínimos y superficies sin suavizado. En primeros planos, los cantos de paneles y marcos se ven duros; en otros, el smoothing oculta la construcción. No se verificó el modificador o el angle de suavizado en el `.blend` fuente, pero el resultado exportado es inconsistente.

**G-08. Las proporciones generales son creíbles.**  
El bounding box del nivel es 46,3 × 6,27 × 23,6 m; el corredor de 3,4 m de ancho, las puertas de ~3 m de alto y la recepción de 5,7 m de techo son coherentes con la escala de los personajes y las criaturas. **Esto debe preservarse.**

### 4.3. Qué preservar

- Jerarquía y mallas del kit de puertas.
- Kit 3A.1: topología limpia y escala correcta.
- Arquitectura de recepción y corredor.
- Proporciones de pasillos, puertas y salas.
- Componentes modulares reutilizables (vigas, costillas, zócalos, rejillas, dinteles).

### 4.4. Qué reconstruir o sustituir

- Monitores, pantallas y terminales.
- Generador, caldera y cuadros de mantenimiento.
- Cajas, carros y estanterías de almacén.
- Lentes de emergencia.
- Props pequeños de alto polígono sin LOD (planta, radio, chemistry, power box).
- Geometría non-manifold de carros y dressing.

---

## 5. Auditoría de materiales y texturas

### 5.1. Base PBR

El proyecto tiene una base correcta: 40 overrides, texturas 2K, normal maps, roughness maps, metallic, clearcoat y reflection probes en recepción y corredor. El problema es que **la base no se aplica de forma consistente**.

### 5.2. Defectos sistémicos

**M-01. Arquitectura sin UV ni triplanar.**  
`level1_nexus.glb` no tiene `uv0` utilizable en buena parte de su arquitectura; varios materiales usan `texCoord:-1`. El override `fm_level1_art_pass.gd:289-307` asigna texturas, pero no genera coordenadas. Afecta suelos y paredes de recepción, corredor, almacén, control, mantenimiento, seguridad y vestuarios. Es la causa principal del aspecto liso de superficies que deberían tener hormigón, pintura o metal con variación.

**M-02. Los overrides se saltan materiales duplicados.**  
`fm_level1_art_pass.gd:428-442` usa `seen[key]` y procesa solo el primer material con cada nombre, aunque Godot haya creado recursos distintos. Evidencia: `NEXUS_Steel` tiene tres recursos; uno recibe textura 2048/metallic 0,88/roughness 0,55 y dos conservan 1024/metallic 1/roughness 1. `SchoolChair_01.002` tiene 9 usos corregidos y 6 sin corregir; `metal_office_desk.002`, 36 y 9. También ocurre en `NEXUS_Painted_Metal`, `NEXUS_Concrete`, `NEXUS_OffWhite`, `NEXUS_Clinical`, `Rec_Wall` y `Rec_Wainscot`.

**M-03. Las 21 texturas runtime no tienen mipmaps.**  
`fm_level1_art_pass.gd:42-50` carga las imágenes con `Image.load()` y crea `ImageTexture` sin generar mipmaps. Los siete sets (floor, wall, wainscot, steel, painted, wood, concrete_panel) devuelven `mipmaps=false` en albedo, normal y roughness, todos a 2048×2048. El filtrado anisotrópico configurado no los genera. Consecuencia: aliasing y especular inestable a distancia.

**M-04. Clearcoat húmedo global en todos los suelos.**  
`fm_level1_art_pass.gd:135-138,341-344` aplica clearcoat 0,38 y clearcoat roughness 0,10 a `ART_floor`, `NEXUS_V05_MAT_Floor_Worn` y `NEXUS_V05_MAT_Rec_Floor`. No hay máscara por charcos. El hormigón queda barnizado y refleja fuera de las zonas húmedas.

**M-05. Normales y roughness casi planas.**  
La normal de pintura verde tiene inclinación media 0,7° y p95 1,6°; su roughness media es 0,504 con desviación 0,010. La normal de acero oxidado tiene 0,5° y 1,0°; el metallic es uniforme 0,80–0,88 sin máscara que separe acero desnudo de óxido. El resultado es metal/pintura sin microdesgaste, con un brillo uniforme que parece plástico.

**M-06. Overrides que degradan mapas correctos.**  
`fm_level1_art_pass.gd:420-423` sustituye la silla original (roughness media 0,297 y máscara metallic 0/1) por metallic 0,05 y un set genérico de chapa. El escritorio original tenía roughness 0,269 y metallic variable; el override impone 0,35 uniforme. Se pierde la separación entre plástico, pintura y estructura metálica.

**M-07. `DOOR_Rust` sin normal ni roughness.**  
La puerta de Almacén usa metallic 0,35 y roughness 1,0 sin mapas; `blender_concept/build_level1_doors.py:92-94` pasa `None, None`. Existen `rusty_painted_metal_nor_gl_2k.exr` y `rusty_painted_metal_rough_2k.exr`, pero no están conectados.

**M-08. Cristales y agua opacos.**  
`NEXUS_V05_MAT_Shard` (8 fragmentos `REC_TRAP_NOISE_0_SHARD_*`, transmisión glTF 0,85) y `NEXUS_Water` (6 `NEXUS_L1_DIS_WATER_*` y `NEXUS_V05_SERVICE_CONN_DAMP_PATCH`, transmisión 0,75) terminan en runtime con alpha 1,0 y `transparency=0`. El pase artístico no los corrige. Los cristales no leen como cristal y el agua no lee como agua.

**M-09. Doble cristal de mostrador.**  
`level1.gd:662-676` y `build_art3a1_kit.py:196-203` colocan `Level1CounterGlass` y `ART3A1_DESK_GLASS` en la misma línea visual. El primero tiene metallic 0,18 y alpha 0,14; el segundo metallic 0 y alpha 0,15. Ninguno usa la configuración de refracción de `ART_glass`. Se acumulan transparencias y reflejos.

**M-10. Metales de puertas sin microdesgaste.**  
`DOOR_Brush` metallic 0,92/roughness 0,30; `DOOR_DarkSteel` metallic 0,82/roughness 0,44, 23 usos; `DOOR_Blue` metallic 0,55/roughness 0,42. Ninguno tiene texturas ni máscara de pintura. El kit se ve limpio y uniforme, no usado.

**M-11. Cristales de lámparas con metallic casi 1.**  
`industrial_pipe_lamp_glass` metallic medio 0,897 y alpha 0,20; `korean_fire_extinguisher_01_glass.001` metallic 0,988 y alpha 0,30. Los vidrios de lámparas y extintores se comportan como metal pulido.

**M-12. Panel esmerilado de Vestuarios opaco.**  
`DOOR_Frost`, especialmente `VESTUARIOS_LeafA_FrostPanel`, tiene alpha 1,0, roughness 0,86 y sin transmisión. La pieza cubre la ventana y no deja pasar luz.

**M-13. Espejos oscuros sin reflexión local.**  
`NEXUS_L1_MAT_Mirror` y `NEXUS_Mirror_Soft` tienen albedo (0,020, 0,030, 0,040), metallic 0,70 y roughness 0,18. Solo hay reflection probes en recepción y corredor; aseo y vestuario no tienen entorno de reflexión. El resultado es un rectángulo negro con un hotspot.

**M-14. Escala UV y offsets sin política métrica.**  
`_copy_pbr()` cambia escala pero no offset. `Rec_Floor` queda en escala 3,0/offset 0,74; `Floor_Worn` 3,0/0,70; `NEXUS_Steel` 2,0/0,15. Tuberías y bandejas de 42 m comparten material y UV de primitivas con tornillería. Los kits aplican `smart_project` por objeto antes de fusionar, sin densidad mundial uniforme.

**M-15. `NEXUS_V05_MAT_Pipe_Red` sin override.**  
`NEXUS_V05_REC_CS_RISER_0`, `NEXUS_V05_REC_CS_SPRINK_PIPE` y cinco `SPRINK_DROP` conservan metallic 0,55, roughness 1,0, sin UV y con texturas `green_metal_rust`. Una tubería roja usa un set verde.

**M-16. Pantallas emisivas uniformes sin textura.**  
`Level1FlatMonitor_*_SCREEN`, `ART3A2_Screen` y `NEXUS_Screen` solo tienen color/emisión uniforme. Ninguno asigna `assets/art/fm/screen_scan.png`. Son rectángulos cian, no interfaces.

**M-17. Dos sistemas de charcos incompatibles.**  
`assets/art/fm/floor_wet.tres` usa metallic 0,12 y roughness efectiva ~0,613; `ART_wet_floor` usa metallic 0, roughness 0,10, clearcoat 1,0 y clearcoat roughness 0,035. El mismo tipo de superficie tiene dos respuestas distintas.

**M-18. Texturas de props etiquetadas 2K/4K pero embebidas a 1024.**  
`radio.glb`, `microscope.glb`, `drawer.glb` y `barrel.glb` incluyen imágenes con nombres `diff_4k`/`diff_2k` a 1024×1024. No es un defecto grave por sí solo, pero limita el primer plano y revela falta de control del pipeline.

### 5.3. Qué preservar

- Sets 2K de hormigón, madera, pintura verde y acero cuando estén bien conectados.
- Overrides de recepción y corredor que sí funcionan.
- Materiales del kit de puertas con herrajes, placas de desgaste y óxido.
- Código cromático verde/ámbar/cian.
- Reflection probes existentes en recepción y corredor.

### 5.4. Qué reconstruir

- UV/triplanar de toda la arquitectura.
- Sistema de overrides para que no se salte duplicados.
- Normales y roughness de pintura/óxido.
- Cristales, agua, espejos y paneles esmerilados.
- Clearcoat de suelos.
- Pantallas y terminales.
- Materiales de props externos con metallic 1/roughness 1.

---

## 6. Auditoría de iluminación y ambientación

### 6.1. Lo que funciona

- La oscuridad periférica de recepción, corredor, seguridad, vestuarios, almacén y conector es **intencionada y jugable**: las rutas y referencias principales siguen siendo reconocibles sin linterna.
- La composición de recepción y la profundidad del corredor son sólidas.
- La linterna tiene potencia suficiente y el contraste con las luces fijas funciona.
- La niebla volumétrica y el color grading están integrados, no son un efecto añadido sin criterio.

### 6.2. Defectos

**L-01. Monitores y pantallas provisionales.**  
Seguridad, control y extracción comparten rectángulos cian con tres líneas. No hay interfaces, texto, gráficos ni variación. Evidencia: `final_sec_desk.png`, `final_ctl_console.png`, `extra_extract_oblique.png`.

**L-02. Cajas de almacén sin lectura PBR.**  
Cubos uniformes, sin fibra, etiquetas, pliegues ni desgaste de aristas. En primer plano parecen bloques de color. Evidencia: `final_store_shelves.png`, `tour_storage_deep.png`.

**L-03. Dressing 3A.2 sin sombras de contacto.**  
`fm_level1_art_pass.gd:625-630` asigna `SHADOW_CASTING_SETTING_OFF` a todos los meshes de `ART3A2_Dressing`. Cajas y props parecen superpuestos al escenario. Evidencia: `final_store_entry.png`.

**L-04. Generador y caldera sin lectura de maquinaria.**  
Gran disco, caja frontal con pocas conexiones; el disco pierde volumen sin linterna. La caldera naranja es lisa y el indicador está quemado. Evidencia: `final_maint_gen.png`, `final_dark_maintenance.png`, `final_maint_boiler.png`.

**L-05. Sobreexposición especular en puertas, marcos y cristales.**  
Franjas blancas que borran juntas y detalle; intervienen linterna, luces fijas y materiales. Evidencia: `final_ctl_entry.png`, `tour_rec_deep.png`, `extra_elevator_inside.png`, `docs/fm_level1_door_control_closed.png`.

**L-06. Suelo del conector con escala y contraste incorrectos.**  
Patrón beige/marrón tipo camuflaje, no humedad ni desgaste industrial; persiste sin linterna. Evidencia: `extra_connector_south.png`, `extra_connector_north.png`, `extra_connector_dark.png`.

**L-07. Directorio de recepción ilegible.**  
Las seis placas aparecen vacías o sin texto distinguible; las tiras emisivas concentran la exposición. Evidencia: `final_rec_directory.png`.

**L-08. Dominancia ámbar/marrón.**  
Oficina, aseo, vestuarios y conector pierden la base fría cian/gris incluso en superficies bien iluminadas. No es solo oscuridad. Evidencia: `final_office.png`, `final_aseo.png`, `final_vest_lockers.png`, `extra_connector_south.png`.

**L-09. Oficina infra-decorada.**  
Pared posterior casi vacía, baldas desocupadas y escasa narrativa administrativa. Evidencia: `tour_office_deep.png`, `final_office.png`.

**L-10. Aseo sin función sanitaria legible.**  
No se distingue lavabo o inodoro con claridad; predominan espejo, botiquín, tabique y paredes vacías. Evidencia: `final_aseo.png`, `extra_aseo_reverse.png`.

**L-11. Seguridad y control comparten demasiada utilería.**  
Radio/micrófono repetidos, pantallas equivalentes y grandes superficies técnicas lisas. Evidencia: `final_sec_back.png`, `final_ctl_back.png`, `final_sec_rack.png`.

**L-12. Vapor de mantenimiento artificial.**  
Grumos blancos, opacos y redondeados que rompen el realismo con y sin linterna. Evidencia: `final_maint_entry.png`, `extra_maint_reverse.png`, `docs/fm_level1_door_mantenimiento_open.png`.

**L-13. Caldera y panel de herramientas por debajo del resto.**  
Caldera naranja lisa, indicador quemado y tablero casi vacío. Evidencia: `final_maint_boiler.png`, `final_maint_bench.png`.

**L-14. Decals de suelo planos y de bordes duros.**  
Elipses negras que parecen agujeros en mantenimiento y charcos cian que parecen recortes en corredor/vestuarios. Evidencia: `extra_maint_reverse.png`, `final_corr_mid.png`, `tour_lockers_deep.png`.

**L-15. Reflejos puntuales que parecen luces incrustadas.**  
El mismo punto azul permanece con y sin linterna, por lo que no es solo el haz del jugador. Evidencia: `final_corr_mid.png`, `final_dark_corridor.png`, `tour_storage_deep.png`, `tour_rec_west.png`.

**L-16. Vestuarios repetitivos.**  
Taquillas idénticas, bancos como bloques y grandes paños laterales sin variación. Evidencia: `final_vest_lockers.png`, `final_vest_bench.png`, `tour_lockers_deep.png`.

**L-17. Ascensor con poco detalle operativo.**  
Hoja oscura casi lisa, control lateral diminuto y ausencia de indicador de piso legible. Evidencia: `extra_elevator.png`, `extra_elevator_close.png`.

**L-18. Jerarquía redundante en ascensor/extracción.**  
Dos rótulos SALIDA apilados compiten con EXTRACCION, el marco luminoso y el terminal. Evidencia: `extra_elevator.png`, `extra_extract_oblique.png`.

**L-19. Lentes de emergencia como bloques emisivos.**  
`level1.gd:_add_emergency_fixture()` crea un `BoxMesh` unshaded con emisión 2,4 sin carcasa ni difusor. En `audit_elevator_close.png` se ve un rectángulo naranja flotante. Hay ~30 instancias.

**L-20. Bloom de señalización.**  
`SEGURIDAD` y carteles suspendidos se convierten en cajas blancas sin contenido legible. Evidencia: `final_corr_mid.png`, `final_corr_detail.png`.

### 6.3. Oscuridad intencionada

No se clasifica como defecto la oscuridad periférica de recepción, corredor, seguridad, vestuarios, almacén o conector. Las rutas y referencias principales permanecen reconocibles sin linterna. El problema no es la falta de luz, sino la calidad de las fuentes, los materiales y la composición.

### 6.4. NO VERIFICADO

- Cabina completa del ascensor: `extra_elevator_inside.png` está dominada por una superficie verde y un foco blanco.
- Oficina, aseo, control y terminal de extracción sin linterna: faltan pares dedicados.
- Todas las orientaciones de mantenimiento: `tour_maintenance_deep.png` quedó obstruido.
- Intersecciones reales de luces: los 32 resultados `NEAR` de `tests/fm_level1_lightaudit.tscn` son candidatos por AABB ampliada, no intersecciones confirmadas.

---

## 7. Auditoría de físicas y colisiones

### 7.1. Conteo runtime

| Tipo | Cantidad |
|---|---:|
| `StaticBody3D` | 572 |
| `RigidBody3D` | 23 |
| `Area3D` | 6 |
| `CharacterBody3D` | 2 |

### 7.2. Hallazgos

**F-01. Colisiones autogeneradas por AABB sin filtro suficiente.**  
`level1.gd:196-221` crea un `StaticBody3D` por cada `MeshInstance3D` que supere ciertos umbrales. `_skip_collider()` filtra `BLOOD`, `PAPER`, `DECAL`, `SIGN`, `LIGHT`, etc., pero **no filtra `WALLSTAIN`**. Por eso `COL_297_NEXUS_V05_D_CORR_WALLSTAIN_0` existe, aunque el decal se oculta en `_setup_doors()`. Un decal oculto con colisión es un bloqueo invisible potencial y se solapa con la apertura de la puerta de Seguridad.

**F-02. Las hojas de puerta son `StaticBody3D`.**  
`fm_level1_door.gd` crea `DoorCollider_*` como `StaticBody3D` (`type=StaticBody3D`, `sync=n/a`), aunque las hojas se mueven con tween. No hay `AnimatableBody3D` ni sincronización física. Es un riesgo de contactos, empuje y futura sincronización multijugador.

**F-03. Interferencias de apertura.**  
- Control: `COL_096_NEXUS_L1_DIS_CART_CORR_cart`.
- Seguridad: `COL_297_NEXUS_V05_D_CORR_WALLSTAIN_0`.
- Vestuarios: `COL_255_NEXUS_V05_B_VEST_VENT`.

Algunas entradas de overlap son suelo o el propio collider de la puerta y no deben inflarse como defectos. Las tres anteriores son interferencias reales o candidatas que deben revisarse.

**F-04. RigidBody sin damping ni material físico.**  
Los props físicos tienen masas plausibles (latas 0,24 kg; portapapeles 0,42; cartones 1,15), CCD activado, pero damping lineal y angular 0 y `physics_material_override=null`. No hay fricción ni rebote específicos por material. Todos se comportan con la misma física genérica.

**F-05. Loot con `freeze=true` inicial.**  
Las masas son 17/9/42/0,6/0,4 kg, capa 4/máscara 1, CCD activo y freeze inicial. No se marca como defecto sin una prueba de juego que demuestre que el freeze impide recogerlos o moverlos; el sistema de loot puede activarlos al interactuar.

**F-06. Colisiones de puertas y marcos.**  
Las hojas de Almacén tienen colliders de 0,802 × 2,94 × 0,18 m y el marco 0,09 × 3,14 × 0,24 m. El vano se abre correctamente en la prueba, pero las hojas son estáticas y los marcos pueden bloquear el paso si el jugador se aproxima en diagonal. No se verificó el barrido completo de todas las puertas con cápsula de jugador.

**F-07. Falsos positivos del log.**  
`MISSING_SOURCE_COL` es un artefacto de emparejamiento por nombres del script de auditoría, no evidencia de ausencia real de collider. No debe usarse como defecto.

### 7.3. Qué preservar

- Colisiones de arquitectura grande, suelo y paredes.
- Colisiones de mobiliario y props que ya funcionan.
- CCD de props y loot.
- Trigger de extracción y áreas de interacción.
- Pruebas de walk 33/33 y smoke.

### 7.4. Qué corregir

- Filtrar decals y manchas en `_skip_collider()`; eliminar el `StaticBody` de `WALLSTAIN`.
- Convertir hojas de puerta a `AnimatableBody3D` o sincronizar su collider con la animación.
- Revisar las tres interferencias de apertura.
- Añadir damping y materiales físicos por tipo de prop.
- Consolidar colliders estáticos para reducir las 572 bodies.

---

## 8. Auditoría de Godot

### 8.1. Organización

`scenes/fm/level1.tscn` es una escena mínima: un `Node3D` raíz con `scripts/fm/level1.gd`. La mayor parte del nivel se construye en runtime:

- Carga de `level1_nexus.glb` con `GLTFDocument`.
- Carga del kit 3A.1, dressing 3A.2 y puertas 3A.3.
- Instanciación de props.
- Generación de colliders.
- Pase artístico y luces.
- Wayfinding, emergency lights, extracción y HUD.

Esto facilita la iteración, pero concentra demasiada responsabilidad en un script y hace que la escena no sea inspeccionable en el editor.

### 8.2. Hallazgos

**GD-01. Script monolítico y referencias por nombre.**  
`level1.gd` supera las 1.300 líneas y usa `find_child("NEXUS_V05_...")` para encontrar nodos. Los nombres con sufijos `_003` de Godot obligan a búsquedas tolerantes. Es frágil ante renombrados, reexportaciones o cambios de jerarquía.

**GD-02. Carga runtime de GLB de 41 MB.**  
El GLB principal se carga en cada arranque, sin importación previa ni caché de escena. Esto aumenta el tiempo de carga y la memoria, y dificulta el control de import settings. No se midió el tiempo exacto: **NO VERIFICADO**.

**GD-03. Duplicación de sistemas de luz.**  
`_setup_emergency_lights()` y `_add_cinematic_lights()` crean luces y fixtures por separado; `_add_emergency_fixture()` construye lentes emisivas sin carcasa. No hay un sistema único de luminarias. Esto explica la inconsistencia entre lámparas enjauladas y cajas naranjas.

**GD-04. Sin LOD ni occlusion culling.**  
`_apply_distance_culling()` solo aplica `visibility_range_end=18` a props pequeños (papel, sangre, decals, latas, botellas, etc.). No hay LODs, `OccluderInstance3D` ni `visibility_range` para arquitectura o props grandes. La única optimización es distancia para basura.

**GD-05. Advertencias de cierre.**  
Los RIDs y recursos retenidos al salir indican que la carga runtime no libera todo. No rompen la partida, pero deben corregirse antes de producción.

**GD-06. Estado multijugador.**  
`level1.gd` es offline; las puertas serializan estado, pero no hay RPC real ni prueba con dos clientes. Cualquier afirmación de sincronización es **NO VERIFICADA**.

**GD-07. Señales y grupos.**  
El nivel usa grupos (`fm_extraction`) y señales de extracción, pero no se verificó el grafo completo de señales ni la duplicación de conexiones. **NO VERIFICADO**.

### 8.3. Qué preservar

- Sistema de carga runtime, mientras se planifica su migración.
- Pruebas smoke/walk/doors.
- API de puertas (`setup`, `set_open`, `interact`, `can_interact`, `get_interaction_prompt`).
- Serialización de estado de puertas, aunque no haya RPC.
- Separación entre lógica de nivel y scripts de props.

### 8.4. Qué corregir

- Reducir `level1.gd` y extraer sistemas (colliders, luces, wayfinding, extracción).
- Sustituir referencias por nombre por referencias exportadas o grupos.
- Unificar el sistema de luminarias.
- Añadir LOD/occlusion y presupuestos por zona.
- Liberar recursos al salir.

---

## 9. Auditoría de integración Blender-Godot

### 9.1. Lo correcto

- Los GLB se exportan con jerarquía y nombres legibles.
- El kit de puertas conserva `LabelAnchor_<ID>` y permite que Godot añada sufijos sin romper la búsqueda.
- Los materiales de los kits 3A.1 y 3A.3 llegan con texturas y metadatos.
- La escala general es coherente.

### 9.2. Problemas

**BG-01. El GLB principal no tiene UV exportables para PBR.**  
El problema nace en Blender: la arquitectura no se desenvuelve ni se prepara para triplanar. Godot recibe mallas sin coordenadas y el pase artístico no puede compensarlo.

**BG-02. Los materiales duplicados de Blender llegan como recursos separados.**  
Godot crea múltiples recursos con el mismo nombre; el pase artístico los trata como uno solo. La integración debe consolidar materiales por nombre y parámetros antes de aplicar overrides.

**BG-03. Los nombres con sufijos `_003` son una dependencia frágil.**  
La búsqueda tolerante funciona, pero no hay un contrato de nombres entre Blender y Godot. Cualquier reexportación puede cambiar el orden y los sufijos.

**BG-04. No se verificaron los import presets.**  
El nivel carga GLB en runtime, por lo que los ajustes de importación del editor no aplican. No se verificó la configuración de compresión, tangentes, mipmaps ni espacio de color. **NO VERIFICADO**.

**BG-05. La topología del GLB principal no está limpia.**  
Los 25.010 boundary edges y 8.124 non-manifold no son un problema de exportación aislado: vienen de la fuente. Deben corregirse en Blender antes de reexportar.

### 9.3. Qué preservar

- Pipeline de kits 3A.1 y 3A.3.
- Nombres estables de puertas y anclas.
- Escala y orientación.
- Materiales del kit de puertas.

### 9.4. Qué corregir

- UV/triplanar en la fuente.
- Consolidación de materiales duplicados.
- Contrato de nombres y validación post-export.
- Limpieza topológica.
- Documentar import settings y reproducibilidad.

---

## 10. Auditoría de rendimiento

### 10.1. Baseline registrado

Medición de la fase 3A.3 a 1280×720:

| Métrica | Valor |
|---|---:|
| FPS | 99–101 |
| Draw calls | 1.281 |
| Primitivas | 906.482 |
| Objetos | 9.603 |

La medición de esta auditoría en headless devolvió `fps=145 draws=0 primitives=0 objects=9854`; no es comparable porque el renderer dummy no dibuja. **NO VERIFICADO** con render real en esta sesión.

### 10.2. Hallazgos

**P-01. 647.397 triángulos instanciados en el GLB principal.**  
Es un nivel grande para una GTX 1650 Ti si se suma iluminación dinámica, sombras, niebla volumétrica, físicas y props. La cifra no es catastrófica por sí sola, pero no hay margen para añadir criaturas y multijugador sin optimizar.

**P-02. Sin LOD ni occlusion culling.**  
Toda la geometría se renderiza según distancia de cámara, sin LODs ni oclusión. En un nivel con pasillos y salas cerradas, la occlusión es especialmente rentable.

**P-03. Props pequeños con coste de asset hero.**  
Planta 69.806 tris, radio 42.350, chemistry 41.958, power box 21.272, carros 18.902–29.394, lámpara enjaulada 22.893. Instanciados varias veces, multiplican draws y primitivas.

**P-04. 1.281 draw calls.**  
La cifra es alta para un nivel de pasillo. La causa probable es la cantidad de materiales y mallas separadas, no solo los objetos. La consolidación de materiales y el merging de mallas estáticas reducirían draws.

**P-05. 572 StaticBody3D.**  
La generación AABB por mesh crea cientos de cuerpos. La física está sobredimensionada para objetos decorativos y decals. Conviene consolidar colliders por zona y excluir geometría no bloqueante.

**P-06. Texturas 2K sin mipmaps.**  
21 texturas runtime a 2048×2048 sin mipmaps aumentan el coste de muestreo y el aliasing. La memoria no se midió: **NO VERIFICADO**.

**P-07. Carga runtime de 41 MB + 13 MB + 5 MB + 3,9 MB.**  
Aumenta el tiempo de arranque y la memoria. No se midió el tiempo de carga. **NO VERIFICADO**.

**P-08. No hay perfiles gráficos aplicados al nivel.**  
El proyecto define perfiles bajo/medio/alto/ultra, pero el Nivel 1 no tiene un presupuesto por zona ni una prueba con esos perfiles. **NO VERIFICADO**.

### 10.3. Qué preservar

- La calidad visual de recepción y corredor.
- La iluminación cinematográfica.
- Los materiales 2K donde aportan.
- La niebla volumétrica, mientras se controle su coste.

### 10.4. Qué optimizar

- LODs para props y arquitectura repetida.
- Occlusion culling por sala/pasillo.
- Consolidación de materiales y mallas estáticas.
- Sustitución de props de alto polígono.
- Reducción de colliders decorativos.
- Mipmaps y compresión de texturas.
- Presupuestos por zona y pruebas con perfiles.

---

## 11. Defectos clasificados por severidad

> Cada defecto incluye identificador, archivo/ruta, objeto afectado, descripción, evidencia, consecuencia, solución, prioridad y dependencias. Las rutas son las del proyecto. Las líneas corresponden al estado actual.

### 11.1. CRÍTICO

#### CR-01 — La extracción no cuenta el botín transportado por un jugador presente

- **Archivo:** `scripts/fm/level1.gd:1322-1327`; `scripts/fm/fm_reception_extraction.gd`; `docs/NEXUS_L1_EXTRACTION_PROCEDURE.md:27,32,69`.
- **Objeto:** contador de entrega y activación de extracción.
- **Descripción:** `get_delivered_loot_count()` solo cuenta objetos cuyo `global_position` está a ≤2,4 m de `EXTRACTION_CENTER`. El procedimiento aprobado también acepta un objeto transportado por un jugador presente.
- **Evidencia:** el documento dice “o transportado por un jugador presente” (línea 27) y contempla “el objeto transportado por un jugador que se extrae” (línea 69). El código no consulta `player.carried_item` ni la posición del jugador.
- **Por qué está mal:** contradice una regla aprobada y rompe el flujo de extracción con botín en manos lejos del ascensor.
- **Consecuencia:** el jugador puede llegar a recepción con el objeto y no activar/completar la extracción; pérdida de partida o bloqueo.
- **Solución recomendada:** contar también `player.carried_item` cuando el jugador esté dentro del área de extracción; añadir prueba de extracción con objeto en manos en el extremo de recepción.
- **Prioridad:** P0.
- **Dependencias:** ninguna para corregir; afecta a pruebas de extracción y HUD.

#### CR-02 — Los colliders del ascensor no siguen la animación de las hojas

- **Archivo:** `scripts/fm/level1.gd:1039-1055`; `_setup_collisions()` en `level1.gd:196-221`.
- **Objeto:** `NEXUS_V05_C_REC_ELEV_L`, `NEXUS_V05_C_REC_ELEV_R`, `COL_266_NEXUS_V05_C_REC_ELEV_L`.
- **Descripción:** `animate_elevator_doors()` mueve visualmente las hojas, pero los `StaticBody3D` generados por AABB permanecen en la posición cerrada.
- **Evidencia:** `/tmp/opencode/audit_extraction_shots.gd`: antes de abrir, el rayo golpea `COL_266_NEXUS_V05_C_REC_ELEV_L`; tras `animate_elevator_doors(true)` y 1,8 s, el rayo sigue golpeando el mismo collider. `ELEV_RAY_CLOSED` y `ELEV_RAY_OPEN` devuelven el mismo nombre.
- **Por qué está mal:** la física no representa el estado visual; el jugador no puede entrar/salir cuando la puerta parece abierta.
- **Consecuencia:** bloqueo de la extracción y de la cabina; experiencia incoherente.
- **Solución recomendada:** usar `AnimatableBody3D` para cada hoja o mover el collider junto con la hoja; probar entrada/salida con cápsula.
- **Prioridad:** P0.
- **Dependencias:** CR-01; pruebas de extracción.

#### CR-03 — La arquitectura principal no tiene UV utilizables ni triplanar

- **Archivo:** `assets/models/fm/level1_nexus.glb`; `scripts/fm/fm_level1_art_pass.gd:289-307`.
- **Objeto:** suelos y paredes de recepción, corredor, almacén, control, mantenimiento, seguridad y vestuarios; materiales `NEXUS_Concrete`, `NEXUS_Concrete_Dark`, `NEXUS_V05_MAT_Rec_Wall`, `NEXUS_V05_CORR_FLOOR`, `NEXUS_V05_RECEPCION_FLOOR`.
- **Descripción:** el GLB no tiene `uv0` utilizable en grandes superficies y varios materiales usan `texCoord:-1`. El override asigna texturas, pero no genera coordenadas.
- **Evidencia:** parseo del GLB: `uv0=false`, `uv1_triplanar=false`; materiales con `texCoord:-1`. El pase artístico solo copia parámetros.
- **Por qué está mal:** el PBR no puede escalar ni variar correctamente; el hormigón/pintura/metal se ven lisos y plásticos.
- **Consecuencia:** afecta a la credibilidad visual de todo el nivel y a la lectura de materiales bajo la linterna.
- **Solución recomendada:** generar UVs métricas en Blender o aplicar triplanar en Godot para arquitectura; validar texel density.
- **Prioridad:** P0/P1.
- **Dependencias:** M-02, M-03, M-14; reexportación del GLB.

### 11.2. ALTO

#### AL-01 — Overrides omitidos en materiales duplicados

- **Archivo:** `scripts/fm/fm_level1_art_pass.gd:428-442`.
- **Objeto:** `NEXUS_Steel`, `SchoolChair_01.002`, `metal_office_desk.002`, `NEXUS_Painted_Metal`, `NEXUS_Concrete`, `NEXUS_OffWhite`, `NEXUS_Clinical`, `NEXUS_V05_MAT_Rec_Wall`, `NEXUS_V05_MAT_Rec_Wainscot`.
- **Descripción:** `seen[key]` procesa solo el primer material con cada nombre, aunque existan recursos distintos.
- **Evidencia:** `NEXUS_Steel` tiene tres recursos; uno recibe 2048/metallic 0,88/roughness 0,55 y dos conservan 1024/metallic 1/roughness 1. Silla: 9 usos corregidos, 6 sin corregir; escritorio: 36 y 9.
- **Por qué está mal:** objetos idénticos tienen materiales distintos; la corrección artística es parcial.
- **Consecuencia:** inconsistencias visibles y difícil depuración.
- **Solución:** aplicar overrides por recurso/material, no por nombre; validar conteos.
- **Prioridad:** P1.
- **Dependencias:** CR-03.

#### AL-02 — Las 21 texturas runtime no tienen mipmaps

- **Archivo:** `scripts/fm/fm_level1_art_pass.gd:42-50`.
- **Objeto:** sets floor, wall, wainscot, steel, painted, wood, concrete_panel.
- **Descripción:** `Image.load()` + `ImageTexture.create_from_image()` sin generar mipmaps.
- **Evidencia:** runtime `mipmaps=false` en albedo, normal y roughness; 2048×2048.
- **Por qué está mal:** aliasing y especular inestable a distancia; el anisotrópico no compensa.
- **Consecuencia:** ruido visual y shimmering en corredores y suelos.
- **Solución:** `image.generate_mipmaps()` antes de crear la textura o usar importación con mipmaps.
- **Prioridad:** P1.
- **Dependencias:** M-03.

#### AL-03 — Clearcoat húmedo global en todos los suelos

- **Archivo:** `scripts/fm/fm_level1_art_pass.gd:135-138,341-344`.
- **Objeto:** `ART_floor`, `NEXUS_V05_MAT_Floor_Worn`, `NEXUS_V05_MAT_Rec_Floor`.
- **Descripción:** clearcoat 0,38 y clearcoat roughness 0,10 sin máscara localizada.
- **Evidencia:** valores en código; reflejos fuera de charcos en capturas.
- **Por qué está mal:** el hormigón parece barnizado/plástico.
- **Consecuencia:** pérdida de credibilidad y compatibilidad con la dirección artística.
- **Solución:** clearcoat solo en zonas húmedas mediante máscara/vertex paint; roughness variable.
- **Prioridad:** P1.
- **Dependencias:** M-17.

#### AL-04 — Normales planas y metallic uniforme en pintura y óxido

- **Archivo:** `assets/art/fm/generated/gen_green_metal_rust_normal.png`, `gen_rusty_metal_sheet_normal.png`, `gen_rusty_metal_sheet_rough.png`.
- **Objeto:** `ART3A1_GreenPaint`, `DOOR_Green`, `ART_painted`, `ART_rack`, `ART3A1_Steel`, `DOOR_Steel`, `NEXUS_Steel`, `ART_detail_steel`, `NEXUS_V05_MAT_Galv`.
- **Descripción:** inclinación normal media 0,7°/p95 1,6° en verde y 0,5°/1,0° en óxido; roughness 0,504 ±0,010; metallic 0,80–0,88 uniforme.
- **Evidencia:** estadísticas de mapas; comparación con la normal antigua de Galv (13°/26°).
- **Por qué está mal:** no hay microdesgaste ni separación acero/óxido; el material parece plástico.
- **Consecuencia:** superficies industrialmente falsas en primeros planos.
- **Solución:** normales con detalle real, máscara metallic y roughness por zonas; conservar la normal antigua de Galv si es mejor.
- **Prioridad:** P1.
- **Dependencias:** CR-03, AL-01.

#### AL-05 — Overrides que degradan sillas y escritorios

- **Archivo:** `scripts/fm/fm_level1_art_pass.gd:420-423`.
- **Objeto:** `SchoolChair_01.002`, `metal_office_desk.002`.
- **Descripción:** se sustituyen mapas originales correctos por un set genérico.
- **Evidencia:** silla original roughness 0,297 y máscara metallic 0/1; override metallic 0,05. Escritorio original 0,269 y metallic variable; override 0,35.
- **Por qué está mal:** se pierde la identidad de plástico/pintura/metal.
- **Consecuencia:** mobiliario de oficina con aspecto uniforme.
- **Solución:** no sobrescribir estos materiales o crear sets específicos.
- **Prioridad:** P1.
- **Dependencias:** AL-01.

#### AL-06 — `DOOR_Rust` sin normal ni roughness

- **Archivo:** `assets/models/fm/doors/level1_doors.glb`; `blender_concept/build_level1_doors.py:92-94`.
- **Objeto:** puerta de Almacén.
- **Descripción:** metallic 0,35, roughness 1,0, sin mapas; el constructor pasa `None, None`.
- **Evidencia:** materiales del GLB; mapas existentes no conectados.
- **Por qué está mal:** la puerta de almacén no tiene el desgaste que sí tienen otras puertas.
- **Consecuencia:** inconsistencia dentro del mismo kit.
- **Solución:** conectar `rusty_painted_metal_nor_gl_2k.exr` y `rusty_painted_metal_rough_2k.exr`.
- **Prioridad:** P1.
- **Dependencias:** kit de puertas.

#### AL-07 — Cristales y agua opacos en runtime

- **Archivo:** `assets/models/fm/level1_nexus.glb`.
- **Objeto:** `NEXUS_V05_MAT_Shard` (8 fragmentos), `NEXUS_Water` (6 water + damp patch).
- **Descripción:** transmisión glTF 0,85/0,75, pero runtime alpha 1,0 y `transparency=0`.
- **Evidencia:** valores runtime; el pase artístico no los corrige.
- **Por qué está mal:** los cristales y el agua no leen como tales.
- **Consecuencia:** pérdida de realismo en trampas de ruido y zonas húmedas.
- **Solución:** materials con alpha/transmisión correctos y sorting; probar con y sin linterna.
- **Prioridad:** P1.
- **Dependencias:** AL-09.

#### AL-08 — Doble cristal de mostrador solapado

- **Archivo:** `scripts/fm/level1.gd:662-676`; `blender_concept/build_art3a1_kit.py:196-203`.
- **Objeto:** `Level1CounterGlass`, `ART3A1_DESK_GLASS`.
- **Descripción:** dos cristales en la misma línea visual con materiales distintos.
- **Evidencia:** metallic 0,18/alpha 0,14 vs metallic 0/alpha 0,15; ninguno usa `ART_glass`.
- **Por qué está mal:** transparencias acumuladas y aspecto lechoso.
- **Consecuencia:** el mostrador de recepción pierde claridad.
- **Solución:** eliminar uno o unificar material; una sola superficie de cristal.
- **Prioridad:** P1.
- **Dependencias:** recepción.

#### AL-09 — Dressing 3A.2 sin sombras de contacto

- **Archivo:** `scripts/fm/fm_level1_art_pass.gd:625-630`.
- **Objeto:** todos los meshes de `ART3A2_Dressing`.
- **Descripción:** `SHADOW_CASTING_SETTING_OFF` global.
- **Evidencia:** código y capturas de almacén.
- **Por qué está mal:** los props no se integran en el escenario; parecen superpuestos.
- **Consecuencia:** pérdida de profundidad y realismo en todas las salas vestidas.
- **Solución:** activar sombras solo en props grandes/sólidos; desactivar en emisivos y finos.
- **Prioridad:** P1.
- **Dependencias:** rendimiento/sombras.

#### AL-10 — Monitores y pantallas placeholder

- **Archivo:** `scripts/fm/level1.gd:615-644`; `fm_level1_art_pass.gd:406-409`; `blender_concept/build_level1_dressing.py:88`.
- **Objeto:** `Level1FlatMonitor_*_SCREEN`, `ART3A2_Screen`, `NEXUS_Screen`.
- **Descripción:** emisión uniforme y tres líneas; ninguna usa `screen_scan.png`.
- **Evidencia:** `final_sec_desk.png`, `final_ctl_console.png`, `extra_extract_oblique.png`.
- **Por qué está mal:** las pantallas son el foco visual de seguridad/control y parecen placeholders.
- **Consecuencia:** salas técnicas poco creíbles.
- **Solución:** interfaz procedural o texturas de pantalla con contenido, variación y scanlines; varias capas.
- **Prioridad:** P2.
- **Dependencias:** M-16.

#### AL-11 — Generador y caldera sin lectura de maquinaria

- **Archivo:** `assets/models/fm/level1_nexus.glb`; `level1_dressing.glb`.
- **Objeto:** generador, caldera, panel de herramientas.
- **Descripción:** caja con disco, caldera lisa, pocas conexiones y tablero vacío.
- **Evidencia:** `final_maint_gen.png`, `final_dark_maintenance.png`, `final_maint_boiler.png`.
- **Por qué está mal:** mantenimiento es una zona industrial y la maquinaria no tiene detalle funcional.
- **Consecuencia:** la sala parece un blockout vestido.
- **Solución:** reconstruir generador/caldera con tuberías, bridas, cables, placas, indicadores y desgaste.
- **Prioridad:** P2.
- **Dependencias:** geometría/Blender.

#### AL-12 — Sobreexposición especular en puertas, marcos y cristales

- **Archivo:** materiales del kit de puertas; luces del pase artístico; linterna.
- **Objeto:** puertas, marcos, cristales de recepción/vestuario.
- **Descripción:** franjas blancas que borran juntas y detalle.
- **Evidencia:** `final_ctl_entry.png`, `tour_rec_deep.png`, `extra_elevator_inside.png`, `docs/fm_level1_door_control_closed.png`.
- **Por qué está mal:** la lectura de materiales y herrajes se pierde.
- **Consecuencia:** el jugador no distingue mecanismos ni acabados.
- **Solución:** reducir roughness especular/energía de luces cercanas, ajustar clearcoat y exposición; probar con linterna.
- **Prioridad:** P2.
- **Dependencias:** AL-04, AL-06.

#### AL-13 — Suelo del conector con patrón incorrecto

- **Archivo:** material del conector en `level1_nexus.glb`; override de suelo.
- **Objeto:** suelo del conector de servicio.
- **Descripción:** patrón beige/marrón tipo camuflaje, no humedad/desgaste.
- **Evidencia:** `extra_connector_south.png`, `extra_connector_north.png`, `extra_connector_dark.png`.
- **Por qué está mal:** rompe la lectura industrial y la coherencia con el resto.
- **Consecuencia:** transición visualmente falsa.
- **Solución:** material de hormigón/metal desgastado con juntas, manchas y humedad localizada.
- **Prioridad:** P2.
- **Dependencias:** CR-03.

#### AL-14 — Dominancia ámbar/marrón en salas

- **Archivo:** `scripts/fm/level1.gd:_setup_emergency_lights()`.
- **Objeto:** oficina, aseo, mantenimiento, almacén, vestuarios.
- **Descripción:** luces cálidas de energía alta: oficina `(1.0,0.60,0.30)` 0,9; aseo `(1.0,0.58,0.28)` 0,8; mantenimiento `(1.0,0.48,0.18)` 1,45; almacén `(1.0,0.56,0.25)` 1,55; vestuarios `(1.0,0.46,0.20)` 1,35.
- **Evidencia:** capturas `final_office.png`, `final_aseo.png`, `final_vest_lockers.png`, `extra_connector_south.png`.
- **Por qué está mal:** la base fría cian/gris se pierde; el ámbar debería ser acento, no dominante.
- **Consecuencia:** las salas parecen marrones y genéricas.
- **Solución:** reducir energía/cambio de color, reforzar relleno frío y usar ámbar solo en emergencia/acento.
- **Prioridad:** P2.
- **Dependencias:** L-08.

#### AL-15 — Puertas con identidad y legibilidad insuficientes

- **Archivo:** `assets/models/fm/doors/level1_doors.glb`; `scripts/fm/fm_level1_door.gd`.
- **Objeto:** SEGURIDAD, ALMACEN, VESTUARIOS, RECEPCION.
- **Descripción:** Seguridad no lee blindada (panel esmerilado grande); Almacén no se distingue como pesada; Vestuarios demasiado claro; Recepción con glare; keypad/mecanismos poco legibles.
- **Evidencia:** `docs/fm_level1_doors_contact_sheet.png` y capturas `door_*.png`.
- **Por qué está mal:** el jugador debe reconocer el tipo de puerta y su mecanismo a distancia.
- **Consecuencia:** confusión de interacción y pérdida de lenguaje visual.
- **Solución:** acentuar masa, bisagras, refuerzos, ventanas, colores y señalización; mejorar materiales.
- **Prioridad:** P2.
- **Dependencias:** AL-06, AL-12.

#### AL-16 — Lentes de emergencia como cajas flotantes

- **Archivo:** `scripts/fm/level1.gd:860-921`.
- **Objeto:** ~30 fixtures de emergencia.
- **Descripción:** `BoxMesh` unshaded emisión 2,4 sin carcasa ni difusor.
- **Evidencia:** `audit_elevator_close.png`, `final_vest_lockers.png`.
- **Por qué está mal:** son primitivas usadas como luminarias terminadas.
- **Consecuencia:** lecturas de “bloque naranja” en paredes.
- **Solución:** carcasa, rejilla, difusor, soporte y luz coherente; reutilizar lámpara enjaulada.
- **Prioridad:** P2.
- **Dependencias:** GD-03.

#### AL-17 — Dos rótulos SALIDA apilados

- **Archivo:** `scripts/fm/level1.gd:741` y `_setup_wayfinding()` `923`.
- **Objeto:** ascensor/extracción.
- **Descripción:** dos rótulos SALIDA de distinto tamaño compiten con EXTRACCION.
- **Evidencia:** `extra_elevator.png`, `extra_extract_oblique.png`.
- **Por qué está mal:** jerarquía de señalización confusa.
- **Consecuencia:** el jugador no sabe cuál es el objetivo.
- **Solución:** un solo rótulo principal y un secundario de capacidad/instrucción.
- **Prioridad:** P2.
- **Dependencias:** wayfinding.

#### AL-18 — Decal `WALLSTAIN` con StaticBody y solape de puerta

- **Archivo:** `scripts/fm/level1.gd:181-221`; `_setup_doors()` 223-226.
- **Objeto:** `NEXUS_V05_D_CORR_WALLSTAIN_0`, `COL_297_...`.
- **Descripción:** el decal se oculta, pero su collider AABB permanece; se solapa con la apertura de Seguridad.
- **Evidencia:** `COL_297_NEXUS_V05_D_CORR_WALLSTAIN_0` en el log de físicas; `DOOR_OPEN_OVERLAP SEGURIDAD`.
- **Por qué está mal:** bloqueo invisible y física incoherente.
- **Consecuencia:** la puerta puede golpear un collider de una mancha invisible.
- **Solución:** añadir `WALLSTAIN`, `BLOOD`, `GRIME`, `OIL`, `SPILL`, `HAND` al filtro; eliminar colliders de decals.
- **Prioridad:** P0.
- **Dependencias:** CR-02.

#### AL-19 — Hojas de puerta con `StaticBody3D`

- **Archivo:** `scripts/fm/fm_level1_door.gd`.
- **Objeto:** `DoorCollider_*` de las seis puertas.
- **Descripción:** cuerpo estático para una hoja animada.
- **Evidencia:** `DOOR_COL ... type=StaticBody3D sync=n/a`.
- **Por qué está mal:** la física no acompaña el movimiento; contactos y empuje incorrectos.
- **Consecuencia:** atascos, solapamientos y problemas futuros de red.
- **Solución:** `AnimatableBody3D` por hoja o actualización del collider en `_physics_process`.
- **Prioridad:** P1.
- **Dependencias:** AL-18, CR-02.

#### AL-20 — Sin LOD/occlusion y props de alto polígono

- **Archivo:** `scripts/fm/fm_level1_art_pass.gd:1025-1037`; GLB de props.
- **Objeto:** planta, radio, chemistry, power box, carros, lámpara enjaulada.
- **Descripción:** solo culling por distancia a 18 m para basura; no LOD ni occlusion. Props de 18k–70k tris.
- **Evidencia:** métricas de geometría y código.
- **Por qué está mal:** el coste no escala con criaturas, multijugador ni más zonas.
- **Consecuencia:** caída de FPS y memoria en equipos modestos.
- **Solución:** LODs, occluders, instancing y presupuestos por prop.
- **Prioridad:** P3.
- **Dependencias:** P-01–P-05.

#### AL-21 — Pantalla y aro de extracción negros

- **Archivo:** `level1_nexus.glb`; materiales `NEXUS_V05_MAT_ExtractGlow`, `NEXUS_V05_MAT_ExtractScreen`.
- **Objeto:** terminal/aro de extracción.
- **Descripción:** albedo negro, metallic 1, roughness 1, sin emisión ni textura.
- **Evidencia:** `audit_materials.txt`.
- **Por qué está mal:** el punto de extracción debería ser el foco visual y está apagado.
- **Consecuencia:** el objetivo no se lee.
- **Solución:** material emisivo con máscara, textura de interfaz y luz local.
- **Prioridad:** P1.
- **Dependencias:** AL-10, AL-17.

#### AL-22 — Cajas de almacén sin lectura PBR

- **Archivo:** `level1_nexus.glb`; materiales `wooden_crate_02.002`, `industrial_pastic_container.002`.
- **Objeto:** cajas y contenedores de almacén.
- **Descripción:** cubos uniformes sin fibra, etiquetas, pliegues ni desgaste; materiales externos con metallic 1/roughness 1.
- **Evidencia:** `final_store_shelves.png`, `tour_storage_deep.png`; `audit_materials.txt`.
- **Por qué está mal:** el almacén es una sala de primer plano y las cajas parecen bloques.
- **Consecuencia:** pérdida de realismo y de narrativa logística.
- **Solución:** materiales de madera/cartón/plástico correctos, etiquetas, variación y aristas desgastadas.
- **Prioridad:** P2.
- **Dependencias:** AL-01, AL-09.

### 11.3. MEDIO

#### ME-01 — Directorio de recepción ilegible

- **Archivo:** geometría de recepción y `Label3D`/overrides.
- **Objeto:** seis placas del directorio.
- **Descripción:** placas vacías o sin texto distinguible; tiras emisivas concentran exposición.
- **Evidencia:** `final_rec_directory.png`.
- **Consecuencia:** pierde función narrativa y orientación.
- **Solución:** texto legible, contraste, iluminación local y jerarquía.
- **Prioridad:** P2.
- **Dependencias:** AL-20 (bloom).

#### ME-02 — Oficina infra-decorada

- **Archivo:** `level1_nexus.glb`; dressing.
- **Objeto:** oficina.
- **Descripción:** pared posterior vacía, baldas sin soportes, tablón placeholder, monitor simple, reloj plano.
- **Evidencia:** `tour_office_deep.png`, `final_office.png`.
- **Consecuencia:** habitación incompleta.
- **Solución:** documentación, carpetas, cajas, cables, silla secundaria, tablón con contenido, reloj con volumen.
- **Prioridad:** P2.
- **Dependencias:** AL-14, AL-05.

#### ME-03 — Aseo sin función sanitaria legible

- **Archivo:** `level1_nexus.glb`; dressing.
- **Objeto:** aseo.
- **Descripción:** no se distingue lavabo/inodoro; espejo negro, botiquín invertido, estantes sin soportes, sin azulejo, jabón bloque.
- **Evidencia:** `final_aseo.png`, `extra_aseo_reverse.png`.
- **Consecuencia:** no parece un aseo.
- **Solución:** reconstruir sanitarios, azulejo, espejo, jabonera y botiquín; corregir texto.
- **Prioridad:** P2.
- **Dependencias:** M-13, AL-14.

#### ME-04 — Seguridad y control comparten lenguaje visual

- **Archivo:** dressing y props.
- **Objeto:** seguridad, control.
- **Descripción:** radio/micrófono, pantallas y superficies equivalentes.
- **Evidencia:** `final_sec_back.png`, `final_ctl_back.png`, `final_sec_rack.png`.
- **Consecuencia:** salas intercambiables.
- **Solución:** diferenciar funciones: vigilancia vs control de acceso; utilería y composición propias.
- **Prioridad:** P2.
- **Dependencias:** AL-10.

#### ME-05 — Vapor de mantenimiento artificial

- **Archivo:** partículas/efectos de mantenimiento.
- **Objeto:** vapor.
- **Descripción:** grumos blancos opacos.
- **Evidencia:** `final_maint_entry.png`, `extra_maint_reverse.png`.
- **Consecuencia:** rompe el realismo.
- **Solución:** partículas finas, transparencia, disipación y luz volumétrica.
- **Prioridad:** P2.
- **Dependencias:** AL-11.

#### ME-06 — Decals de suelo planos y de bordes duros

- **Archivo:** materiales/decal de suelo.
- **Objeto:** charcos, manchas, elipses.
- **Descripción:** bordes duros; parecen recortes.
- **Evidencia:** `extra_maint_reverse.png`, `final_corr_mid.png`, `tour_lockers_deep.png`.
- **Consecuencia:** superficies falsas.
- **Solución:** decals con alpha suave, variación y orientación; integrar con humedad.
- **Prioridad:** P2.
- **Dependencias:** AL-03.

#### ME-07 — Reflejos puntuales que parecen luces incrustadas

- **Archivo:** materiales de suelo; luces.
- **Objeto:** corredor, almacén, recepción.
- **Descripción:** punto azul persistente con y sin linterna.
- **Evidencia:** `final_corr_mid.png`, `final_dark_corridor.png`, `tour_storage_deep.png`.
- **Consecuencia:** confusión visual.
- **Solución:** ajustar roughness/clearcoat y la fuente especular; revisar reflection probes.
- **Prioridad:** P2.
- **Dependencias:** AL-03, M-13.

#### ME-08 — Vestuarios repetitivos

- **Archivo:** `level1_nexus.glb`; dressing.
- **Objeto:** taquillas, bancos.
- **Descripción:** taquillas idénticas, bancos bloques, paños laterales sin variación.
- **Evidencia:** `final_vest_lockers.png`, `final_vest_bench.png`.
- **Consecuencia:** sala genérica.
- **Solución:** variación de taquillas, soportes, ropa, carteles, suciedad y luces.
- **Prioridad:** P2.
- **Dependencias:** AL-09.

#### ME-09 — Ascensor con poco detalle operativo

- **Archivo:** `level1_nexus.glb`.
- **Objeto:** ascensor.
- **Descripción:** hoja lisa, control diminuto, sin indicador de piso.
- **Evidencia:** `extra_elevator.png`, `extra_elevator_close.png`.
- **Consecuencia:** la salida no se lee como máquina.
- **Solución:** indicador, botonera, juntas, desgaste y luz de cabina.
- **Prioridad:** P2.
- **Dependencias:** CR-02.

#### ME-10 — Espejos oscuros sin reflexión local

- **Archivo:** `fm_level1_art_pass.gd:418-419,508-523`.
- **Objeto:** `NEXUS_L1_MAT_Mirror`, `NEXUS_Mirror_Soft`.
- **Descripción:** albedo casi negro, metallic 0,70, roughness 0,18; sin probes en aseo/vestuario.
- **Evidencia:** `audit_materials.txt`; capturas.
- **Consecuencia:** rectángulo negro con hotspot.
- **Solución:** material de espejo real o SSR/probe local; aclarar albedo.
- **Prioridad:** P2.
- **Dependencias:** ME-03, ME-08.

#### ME-11 — Escala UV y offsets sin política métrica

- **Archivo:** `fm_level1_art_pass.gd:289-307,874-935`; scripts de Blender.
- **Objeto:** suelos, acero, tuberías.
- **Descripción:** escala sin offset; tuberías de 42 m comparten UV de primitivas.
- **Evidencia:** valores `Rec_Floor` 3,0/0,74; `Floor_Worn` 3,0/0,70; `NEXUS_Steel` 2,0/0,15.
- **Consecuencia:** texturas estiradas o repetidas.
- **Solución:** texel density mundial y offsets por pieza; triplanar.
- **Prioridad:** P1/P2.
- **Dependencias:** CR-03.

#### ME-12 — Tubería roja con set verde

- **Archivo:** `level1_nexus.glb`; `fm_level1_art_pass.gd:336-425`.
- **Objeto:** `NEXUS_V05_REC_CS_RISER_0`, `SPRINK_PIPE`, `SPRINK_DROP`.
- **Descripción:** sin override; metallic 0,55, roughness 1,0, texturas green_metal_rust.
- **Evidencia:** `audit_materials.txt`.
- **Consecuencia:** incoherencia de señalización industrial.
- **Solución:** material rojo con desgaste y normal.
- **Prioridad:** P2.
- **Dependencias:** AL-04.

#### ME-13 — Pantallas emisivas uniformes

- **Archivo:** `level1.gd:615-644`; `fm_level1_art_pass.gd:406-409`; `build_level1_dressing.py:88`.
- **Objeto:** monitores.
- **Descripción:** solo color/emisión; sin textura.
- **Evidencia:** código; capturas.
- **Consecuencia:** interfaces falsas.
- **Solución:** textura de pantalla, scanlines y contenido variable.
- **Prioridad:** P2.
- **Dependencias:** AL-10.

#### ME-14 — Dos sistemas de charcos incompatibles

- **Archivo:** `assets/art/fm/floor_wet.tres`; `level1.gd:792-812`; `fm_level1_art_pass.gd:148-152,1003-1021`.
- **Objeto:** charcos.
- **Descripción:** metallic/roughness distintos para el mismo tipo de superficie.
- **Evidencia:** valores.
- **Consecuencia:** respuesta visual inconsistente.
- **Solución:** un solo sistema y parámetros por zona.
- **Prioridad:** P2.
- **Dependencias:** AL-03.

#### ME-15 — Topología non-manifold y duplicados

- **Archivo:** `level1_nexus.glb`, `level1_dressing.glb`.
- **Objeto:** arquitectura, carros, `DRESS_GreenPaint`.
- **Descripción:** 25.010 boundary, 8.124 non-manifold, 5.197 duplicados; dressing 162/108.
- **Evidencia:** métricas.
- **Consecuencia:** shading, z-fighting, riesgo de exportación.
- **Solución:** limpiar en Blender antes de reexportar; no solo en Godot.
- **Prioridad:** P2/P3.
- **Dependencias:** CR-03, AL-20.

#### ME-16 — RigidBody sin damping ni material físico

- **Archivo:** `scripts/fm/level1.gd:397-555`.
- **Objeto:** latas, portapapeles, cartones.
- **Descripción:** damping 0, `physics_material_override=null`.
- **Evidencia:** `RIGID ... damp=0.0/0.0 ... pm=<null>`.
- **Consecuencia:** rebotes y deslizamientos genéricos.
- **Solución:** damping, fricción y rebote por material; masas revisadas.
- **Prioridad:** P2.
- **Dependencias:** AL-19.

### 11.4. BAJO

#### BA-01 — Texturas de props 1024 etiquetadas como 2K/4K

- **Archivo:** `radio.glb`, `microscope.glb`, `drawer.glb`, `barrel.glb`.
- **Descripción:** nombres `diff_4k`/`diff_2k`, resolución real 1024.
- **Consecuencia:** límite de detalle en primer plano.
- **Solución:** corregir pipeline de exportación o renombrar.
- **Prioridad:** P3.
- **Dependencias:** AL-22.

#### BA-02 — Bloom de señalización del corredor

- **Archivo:** materiales emisivos y luces.
- **Objeto:** carteles `SEGURIDAD`, señales suspendidas.
- **Descripción:** bloom intenso; contenido ilegible.
- **Evidencia:** `final_corr_mid.png`, `final_corr_detail.png`.
- **Solución:** reducir emisión, añadir máscara y contraste.
- **Prioridad:** P2.
- **Dependencias:** AL-20.

#### BA-03 — Luminarias naranjas como bloques emisivos

- **Archivo:** `level1.gd` fixtures.
- **Objeto:** luces de emergencia.
- **Descripción:** sin carcasa/difusor; se leen como bloques.
- **Evidencia:** `final_vest_lockers.png`, `extra_elevator.png`.
- **Solución:** carcasa y difusor; unificar con lámparas enjauladas.
- **Prioridad:** P2.
- **Dependencias:** AL-16.

#### BA-04 — Advertencias de RIDs/recursos al salir

- **Archivo:** carga runtime de GLB.
- **Descripción:** recursos retenidos al cerrar.
- **Evidencia:** logs de smoke/walk.
- **Consecuencia:** posible fuga en sesiones largas.
- **Solución:** liberar documentos/escenas y auditar referencias.
- **Prioridad:** P3.
- **Dependencias:** GD-02.

#### BA-05 — Inconsistencias documentales

- **Archivo:** `docs/NEXUS_L1_MISSION_AUDIT.md`.
- **Descripción:** fila duplicada “Oficina/aseo” y etiquetas APROBADA que contradicen pendientes reconocidos.
- **Consecuencia:** estado del proyecto poco fiable.
- **Solución:** actualizar el estado real y separar “vestido” de “terminado”.
- **Prioridad:** P0 documental.
- **Dependencias:** este informe.

---

## 12. Requisitos originales incumplidos

| Requisito de FRECUENCIA MUERTA | Estado | Evidencia |
|---|---|---|
| Sin armas ni combate | **Cumple** | No hay sistemas de armas en el Nivel 1 |
| No reconstruir desde cero | **Cumple** | Se conservó la base y los GLB |
| Escenarios con detalle, no solo primitivas | **Incumple parcialmente** | Monitores, generador, cajas, lentes, bancos |
| Materiales PBR convincentes | **Incumple** | Sin UV, normales planas, metallic 1, clearcoat global, glass opaco |
| Iluminación cinematográfica con base fría | **Incumple parcialmente** | Dominancia ámbar en oficina/aseo/vestuarios/conector |
| Habitaciones completas y con función | **Incumple** | Oficina, aseo, almacén y mantenimiento |
| Físicas coherentes por objeto | **Incumple parcialmente** | Puertas StaticBody, damping 0, decal con collider |
| Puertas implementadas y probadas | **Cumple** (estado real 3A.3) | Tests PASS; quedan defectos visuales/físicos |
| Extracción según procedimiento | **Incumple** | CR-01 |
| LOD y occlusion culling | **Incumple** | No hay LOD/occluders |
| Perfiles bajo/medio/alto/ultra aplicados | **NO VERIFICADO** | No hay prueba del nivel con perfiles |
| Rendimiento medido en condiciones reproducibles | **Parcial** | Baseline 3A.3; esta auditoría no midió con render real |
| Multijugador sincronizado | **NO VERIFICADO** | `level1.gd` offline; sin RPC real |
| Audio y comunicación | **NO VERIFICADO** | Fuera del alcance de las evidencias recogidas |
| Documentación actualizada | **Incumple parcialmente** | Etiquetas APROBADA contradictorias |

---

## 13. Elementos que deben preservarse

1. **Recepción:** composición, mostrador, panel corporativo, directorio como intención, ascensor y escala.
2. **Corredor:** longitud, ritmo de vigas, bandejas, tuberías, puertas y profundidad.
3. **Kit 3A.1:** topología limpia, escala y modularidad.
4. **Kit de puertas 3A.3:** jerarquía, mallas, herrajes, teclados y anclas; es el mejor activo geométrico reciente.
5. **Pruebas:** smoke, walk 33/33, puertas y extracción; deben seguir siendo la red de seguridad.
6. **Sistema de loot, escondites, trampas y Vigilante:** funcionan y son la base de la vertical slice.
7. **Código cromático** verde/ámbar/cian y la lectura de la extracción.
8. **Iluminación de recepción/corredor** y la oscuridad intencionada.
9. **Materiales 2K** que ya están bien conectados.
10. **Estrechez del conector** como decisión de diseño; corregir acabado, no proporción.
11. **Documentación de puertas y extracción** como contrato funcional, corrigiendo la discrepancia de CR-01.

---

## 14. Elementos que necesitan reconstrucción o sustitución

| Elemento | Acción | Motivo |
|---|---|---|
| UV/triplanar de arquitectura | Reconstrucción técnica | PBR inválido en suelos/paredes |
| Monitores y terminales | Sustitución | Placeholders cian |
| Generador, caldera, panel de herramientas | Reconstrucción | Maquinaria sin detalle funcional |
| Cajas, contenedores, carros de almacén | Reconstrucción/sustitución | Primitivas y alto polígono |
| Lentes de emergencia | Sustitución | Cajas flotantes |
| Planta, radio, chemistry, power box | Sustitución/LOD | 21k–70k tris sin LOD |
| Espejos, cristales, agua, panel esmerilado | Reconstrucción de material | Opacos/negros |
| Suelo del conector | Sustitución de material | Patrón tipo camuflaje |
| Lámpara enjaulada | Optimización/reconstrucción | 22.893 tris, 48 non-manifold |
| Dressing con sombras off | Corrección de configuración | Props flotantes |
| Colliders de decals y puertas | Reconstrucción de física | Bloqueos y desincronización |
| Oficina/aseo/vestuarios | Repoblado y reconstrucción parcial | Habitaciones incompletas |
| Señalización SALIDA | Reorganización | Duplicidad |
| Contador de extracción | Corrección de código | CR-01 |

---

## 15. Plan de corrección priorizado

> **No ejecutar sin autorización.** El orden está pensado para no romper la base jugable y para que cada paso tenga pruebas de aceptación.

### P0 — Bloqueadores funcionales y de integridad (1–2 días)

1. **CR-01:** contar el objeto transportado por un jugador dentro del área de extracción. Prueba: llegar con loot en manos al extremo de recepción y completar.
2. **CR-02:** sincronizar colliders de ascensor con la animación. Prueba: rayo y cápsula antes/después de abrir; entrar y salir.
3. **AL-18:** filtrar decals/manchas y eliminar el `StaticBody` de `WALLSTAIN`. Prueba: puerta de Seguridad sin solape; walk 33/33.
4. **BA-05:** actualizar la documentación de estado para que no contradiga la realidad.
5. **CR-03 (inicio):** definir la estrategia de UV/triplanar antes de tocar materiales.

**Criterio de aceptación:** extracción con loot transportado, ascensor transitable, puertas sin solapes invisibles, walk y smoke PASS.

### P1 — Materiales y PBR (3–5 días)

1. Resolver UV/triplanar de arquitectura y texel density.
2. Corregir AL-01 (overrides por recurso), AL-02 (mipmaps), AL-03 (clearcoat), AL-04 (normales/roughness), AL-05 (silla/escritorio), AL-06 (DOOR_Rust).
3. Corregir AL-07 (cristales/agua), AL-08 (doble cristal), AL-21 (pantalla de extracción), ME-10 (espejos), ME-11 (escala UV), ME-12 (tubería roja), ME-14 (charcos).
4. Validación A/B con luz neutra y linterna.

**Criterio de aceptación:** mismos objetos, materiales coherentes; sin plástico, sin metallic 1 indiscriminado, sin texturas estiradas; capturas comparativas.

### P2 — Iluminación, salas y señalización (3–5 días)

1. Reequilibrar AL-14 (ámbar) y AL-12 (especular).
2. Sustituir AL-16 (lentes) y corregir AL-17 (SALIDA).
3. Reconstruir AL-10/AL-11/AL-22 y ME-01–ME-09.
4. Corregir AL-09 (sombras), AL-13 (conector), ME-05 (vapor), ME-06 (decals), ME-07 (reflejos), BA-02.
5. Revisión por zona con y sin linterna.

**Criterio de aceptación:** cada una de las 12 zonas tiene identidad, función legible, materiales creíbles y ninguna sala “vacía” o provisional.

### P3 — Geometría, física y rendimiento (3–5 días)

1. Limpiar topología de carros, dressing y arquitectura; reducir duplicados/non-manifold.
2. LODs para props y arquitectura repetida; occluders; consolidación de materiales/mallas.
3. Reducir `StaticBody3D` decorativos; damping/material físico (ME-16); revisar `AnimatableBody3D` (AL-19).
4. Medir con perfiles bajo/medio/alto/ultra; documentar memoria y carga.
5. Corregir BA-01/BA-04.

**Criterio de aceptación:** presupuesto por zona, FPS estables en GTX 1650 Ti y margen para criaturas/multijugador; sin pérdida de calidad artística injustificada.

### P4 — Verificación final (2 días)

1. Smoke, walk, doors, detail, extracción y capturas de las 12 zonas.
2. Prueba de extracción con loot transportado y con loot en el suelo.
3. Prueba de ascensor con cápsula.
4. Prueba de puertas con barrido diagonal.
5. Medición de rendimiento reproducible.
6. Actualización de `docs/WORKLOG.md`, `docs/CURRENT_STATE.md` y este informe.

---

## 16. Riesgos y dependencias

### 16.1. Riesgos técnicos

- **Regenerar UV/triplanar** puede cambiar por completo la lectura visual y requerir reajustar todos los overrides.
- **Cambiar colliders** puede romper el walk 33/33 y las puertas; debe hacerse con pruebas después de cada bloque.
- **Convertir hojas a `AnimatableBody3D`** puede alterar el empuje y la interacción; probar con cápsula y con las seis puertas.
- **Eliminar el doble cristal** puede cambiar la composición de recepción; hacer captura A/B.
- **Activar sombras del dressing** puede costar FPS; activar solo props grandes y medir.
- **Reexportar el GLB principal** puede cambiar nombres y sufijos; validar el contrato de nombres.
- **Tocar materiales compartidos** puede afectar a otras zonas fuera del Nivel 1; aislar por recurso.
- **Reducir polígonos** puede introducir siluetas pobres; usar LOD, no decimación indiscriminada.

### 16.2. Dependencias

- CR-01 depende de la lógica de extracción y del HUD.
- CR-02 y AL-19 dependen de la física de puertas y del sistema de interacción.
- CR-03, AL-01 y AL-04 dependen de la reexportación de Blender.
- AL-09 y AL-20 dependen del presupuesto de sombras y rendimiento.
- AL-14 depende de la jerarquía de luces y de la dirección artística.
- ME-03 y ME-08 dependen de la reconstrucción de dressing y de materiales.
- P3 depende de P1/P2 para no medir sobre una base falsa.

### 16.3. Regla de trabajo

Cada corrección debe:

1. Limitarse a un defecto o grupo coherente.
2. Ejecutar smoke + walk + puertas.
3. Guardar captura antes/después.
4. Actualizar la documentación.
5. No tocar otros niveles.
6. No introducir armas, combate ni sistemas de fases futuras.

---

## 17. Conclusión

El Nivel 1 tiene una **base real y aprovechable**: arquitectura completa, puertas, loot, extracción, iluminación y pruebas. No debe reconstruirse desde cero.

Pero la calidad actual **no es la calidad final**. Los tres bloqueadores críticos —extracción, colliders del ascensor y UV de la arquitectura— deben resolverse antes de seguir ampliando contenido. Después, la prioridad es materializar el PBR, eliminar los placeholders de las salas y reducir el coste geométrico/físico.

La recepción y el corredor demuestran que el equipo puede alcanzar el estándar; el resto del nivel todavía no lo alcanza. Este informe debe usarse como lista de trabajo, no como certificado de terminación.

---

## Anexo A — Comandos y evidencias reproducibles

```bash
# Smoke
godot --headless --path . tests/fm_level1_smoke.tscn

# Walk
godot --headless --path . tests/fm_level1_walk.tscn

# Puertas
godot --headless --path . tests/fm_level1_doors.tscn

# Capturas por zona
DISPLAY=:0 godot --path . --audio-driver Dummy tests/fm_level1_final_shots.tscn

# Extracción/ascensor (solo lectura, script externo)
DISPLAY=:0 godot --path . --audio-driver Dummy --script /tmp/opencode/audit_extraction_shots.gd
```

### Evidencias clave

- `WALK_RESULT reached=33/33` — `/tmp/opencode/audit_walk.log`.
- `TEST_LIGHTS true general=0 art=23 emergency=30 flashlight=3` — `/tmp/opencode/audit_smoke.log`.
- `ELEV_RAY_CLOSED COL_266...` y `ELEV_RAY_OPEN COL_266...` — `/tmp/opencode/extraction_audit2.log`.
- `DOOR_OPEN_OVERLAP SEGURIDAD COL_297_NEXUS_V05_D_CORR_WALLSTAIN_0` — `/tmp/opencode/audit_level1_physics_v2.log`.
- `BODY_COUNTS { "StaticBody3D": 572, "RigidBody3D": 23, "Area3D": 6, "CharacterBody3D": 2 }` — mismo log.
- `RIGID ... damp=0.0/0.0 ... pm=<Object#null>` — `/tmp/opencode/audit_level1_physics.log`.
- `uv0=false`, `uv1_triplanar=false`, `texCoord:-1` — parseo de `level1_nexus.glb`; `audit_materials.txt`.
- `mipmaps=false` en siete sets 2K — runtime de materiales.
- 647.397 triángulos instanciados, 25.010 boundary, 8.124 non-manifold — `glb_key_findings.txt`.

## Anexo B — NO VERIFICADO

- Sincronización multijugador real, RPCs y reconexión.
- Tiempo de carga y memoria de GPU.
- Rendimiento con render real en esta sesión; solo se cita el baseline 3A.3.
- Perfiles gráficos bajo/medio/alto/ultra aplicados al nivel.
- Import presets de GLB y espacio de color final.
- Intersecciones reales de todas las luces (los `NEAR` son candidatos por AABB).
- Cabina completa del ascensor y algunas orientaciones de oficina/aseo/control/mantenimiento.
- Audio del nivel y comunicación por proximidad/radio.
- Grafo completo de señales y grupos.
- Comportamiento de loot con `freeze=true` en una partida real.
- Calidad de refracción/SSR y sorting de transparencias en GPU.

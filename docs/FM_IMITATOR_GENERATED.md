# FRECUENCIA MUERTA — El Imitador generado (2026-11-17)

## 1. Origen

Modelo generado por el usuario:

- `Modelos-criaturas/Imitador/mesh-optimizer-1794962660769.glb`
- GLB original **intacto**; no se ha modificado.
- Copia de seguridad del original en `docs/backups/FM_IMITATOR_GENERATED_2026-11-17/imitator_source_original.glb`.

Referencia oficial: `fotos-referencia/modelos-referencia.png`.
El Imitador es una criatura emaciada de 2,2–2,5 m, piel pálida gris-marrón,
brazos largos con garras, piernas flexionadas, cabeza alargada y una boca
vertical enorme. Debe resultar reconocible incluso con poca luz.

## 2. Trabajo realizado

### Limpieza y escala

- Eliminado un panel plano grande detrás de la cintura (3.213 vértices).
- Eliminadas una isla flotante de 108 vértices, aristas degeneradas y caras
  con winding inconsistente.
- Escalado a **1,12** para una altura de **2,23 m**; transforms aplicados y
  pies apoyados en `z = 0`.
- Malla final: **36.637 vértices, 73.150 polígonos**.

### Proporciones

- Torso estrechado (`x × 0,87`, `y × 0,93`, falloff suave) para leer como
  criatura emaciada.
- Muslos ligeramente estrechados (`x × 0,94`).
- Cabeza, brazos y garras conservados; la boca natural del modelo generado se
  mantiene como cavidad vertical.
- Se probaron bocas, ojos y dientes postizos; flotaban o tapaban la cara y se
  eliminaron. **No añadir geometría facial sin un anclaje fiable.**

### Materiales y texturas

- `M_Gen_ImitadorSkin`: textura `assets/art/fm/imitador/T_Imitador_Skin_PaleRose.png`
  (512×512, base gris-marrón ≈138,124,114 con moteado y venas), normal
  `assets/art/fm/flesh_normal.png` a fuerza 0,80, roughness **0,66**.
- `M_Gen_Bone`: dientes y puntas claras.
- `M_Gen_Claw`: garras oscuras (3.474 caras).
- `M_Gen_Maw`: interior de la boca rojo oscuro (858 caras).
- `M_Gen_Muscle`, `M_Gen_Dark`, `M_Gen_Eye`: apoyo de regiones internas.
- UV Smart Project aplicado; smooth shading por ángulo de 38°.

### Acabado

- Eliminado el aspecto plástico bajando specular y subiendo roughness.
- La piel rojiza se descartó por alejarse de la referencia; la versión final es
  pálida gris-marrón.
- La boca conserva su volumen y dientes originales; el interior está oscurecido.

## 3. Archivos

- Copia de trabajo: `nexus/nivel_01/FM_IMITATOR_GENERATED_WORK.blend`.
- GLB final: `assets/models/fm/imitator_generated_v3.glb`
  - **2.743.352 bytes**
  - 1 mesh / 1 nodo
  - 4 materiales: `M_Gen_ImitadorSkin`, `M_Gen_Bone`, `M_Gen_Maw`, `M_Gen_Claw`
  - 2 imágenes
  - **73.256 tris**
  - 0 cámaras, 0 luces, 0 animaciones
  - MD5 `fcbce5006dfff0c5cd7afca8ce9bd0b4`
- Renders: `/tmp/opencode/imi_pale_{front,threeq,head}.png`.
- Backup: `docs/backups/FM_IMITATOR_GENERATED_2026-11-17/` con blend, GLB,
  original, renders y texturas.

## 4. QA

`blender-asset-qa` (`qa_check`, profile `game`, eps 0,002, tol 0,08,
`no_modifiers=True`):

**PASS True, 0 errores, 2 warnings.**

Los warnings son menores y aceptados. No hay islas flotantes, caras invertidas
ni geometría degenerada pendiente.

## 5. Limitaciones

- Sigue siendo un modelo generado por IA: topología ruidosa, fusiones
  orgánicas irreales (hombro/cuello) y algunos tendones colgantes.
- La cara es asimétrica y la boca está desplazada; no se ha reconstruido la
  anatomía facial.
- La piel es una textura plana con normal genérica; no hay bake de alta a baja
  ni poros/escurrimientos propios de la referencia.
- No está integrado en `fm_creature_models.gd`, escenas ni IA.
- No es un modelo final AAA; es una base válida y claramente mejor que las
  versiones procedurales v1–v4.

## 6. Skills usadas

- `blender-core`: API 5.2, data API, verificación.
- `blender-sculpting`: criterio de remesh/suavizado y anatomía.
- `blender-retopology-uv`: UV Smart Project y criterio de densidad.
- `blender-texturing`: capas de piel, textura y desgaste.
- `blender-pbr-materials`: roughness/specular, color spaces y normales.
- `blender-lighting-lookdev`: cámara y luces de revisión.
- `blender-asset-qa`: QA final de malla.

No se usaron `blender-animation`, `blender-character-rigging` ni
`blender-export-pipelines` como flujo completo: el modelo es estático y el
export se hizo con el exportador glTF de Blender.

## 7. Siguiente paso

1. Revisar los renders con el usuario y decidir si esta base sirve para el
   Imitador del nivel.
2. Si se integra: añadir `build_imitator`/carga del GLB en la escena, colisión
   de cápsula, punto de spawn y prueba de comportamiento.
3. Si se exige más realismo: retopología manual, bake normal/AO y escultura
   facial; no seguir añadiendo piezas postizas a ciegas.
4. Sin commit hasta autorización.

## 8. Pase de acercado a la referencia (2026-11-17)

Se aplicó un pase sobre `Imitator_Generated` para acercarlo a
`fotos-referencia/modelos-referencia.png`:

- **Textura nueva:** `T_Imitador_Skin_Ref_BC.png` (1024×1024, marrón rojizo
  oscuro con moteado, parches y vetas) y `T_Imitador_Skin_Ref_R.png`
  (rugosidad variable), generadas con `fm_imitator_texture_gen.py`.
- **Material:** `M_Gen_ImitadorSkin` con la nueva BC, roughness map,
  `flesh_normal.png`, roughness 0,66, specular 0,34 y subsurface 0,045.
- **Silueta:** torso inclinado 8° adicionales, cráneo estrechado un 15 % en X
  y alargado un 12 % en Z, cuello 10 % más fino, abdomen hundido 2,2 cm y
  crestas de costillas sutiles.
- **Boca:** se restauró la asignación original de materiales (858 caras de
  `M_Gen_Maw`) tras un intento de oscurecido que teñía 4.991 caras.
  La abertura frontal se abrió y se añadieron 12 dientes finos en dos filas
  dentro de la cavidad, unidos a la malla principal.
- **Limpieza:** se eliminaron tendones/varillas degeneradas en la zona de la
  mano izquierda (x≈−1,12) y se recalculan normales. QA final:
  **PASS, 0 errores, 4 warnings**.
- **Malla final:** 36.520 vértices, 72.115 polígonos. GLB
  `assets/models/fm/imitator_generated_v4.glb`: **3.501.284 bytes**, 1 mesh,
  1 nodo, 4 materiales, 3 imágenes, **72.971 tris**, 0 cámaras/luces.

Renders de este pase: `/tmp/opencode/imi_ref_full.png` y
`/tmp/opencode/imi_ref_head.png`. El resultado se lee como criatura
encorvada, rojiza, con brazos largos, garras y boca vertical dentada; sigue
siendo estilizado y con topología ruidosa, no un acabado AAA.

Backup: `docs/backups/FM_IMITATOR_REFERENCE_after_2026-11-17/` con blend,
GLB v4, renders, scripts y texturas.

## 9. Limpieza de boca y estado final v5 (2026-11-17)

Después del pase de referencia se intentó mejorar la cabeza. Los intentos de
cuencas oculares con esferas, una cabeza nueva completa y parches de material
no funcionaron: la cabeza nueva dejaba visible la cúpula antigua y los parches
producían una mancha negra única. Todos esos cambios se revirtieron.

Se conservó una única limpieza útil: **se eliminaron los 12 dientes unidos**
que, tras el `join`, se leían como un peine flotante fuera de la boca. La
cavidad bucal queda como una abertura vertical oscura y rasgada, sin dientes
postizos. La geometría se redujo a **36.435 vértices y 72.031 polígonos**.

- **GLB final:** `assets/models/fm/imitator_generated_v5.glb` =
  **3.491.352 bytes**, 1 mesh, 1 nodo, 4 materiales, 3 imágenes,
  **72.851 tris**, 0 cámaras, 0 animaciones, 0 luces.
  MD5 `f8f4bff49f72aee9780eda2f374d11f7`.
- **QA:** `blender-asset-qa` profile game, eps 0,002, tol 0,08,
  `no_modifiers=True` → **PASS, 0 errores, 3 warnings**.
- **Blend:** `nexus/nivel_01/FM_IMITATOR_GENERATED_WORK.blend`
  (md5 `7ae8180fb5377b2b07213406cc124a35`).
- **Renders:** `/tmp/opencode/imi_ref_full.png` y
  `/tmp/opencode/imi_ref_head.png`.
- **Backup:** `docs/backups/FM_IMITATOR_MOUTH_CLEAN_2026-11-17/`.

Estado visual: la silueta general (2,23 m, encorvada, brazos largos, garras,
piel rojiza) se acerca a la referencia, pero el cráneo sigue siendo una
cúpula lisa y la boca está bajo la frente, no en una cara vertical. Es un WIP
estilizado. Para el cráneo de `modelos-referencia.png` hace falta escultura y
retopología manual real, no más parches por script.

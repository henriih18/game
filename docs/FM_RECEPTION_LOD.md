# FM — Recepción: LOD global

## Alcance

Primera pasada de LOD para los clústeres hero de Recepción:

- `L1_RECEPTION_R6_HERO`
- `L1_RECEPTION_R7_HERO`
- `L1_RECEPTION_R8_HERO`
- `L1_RECEPTION_R9_HERO`
- `L1_RECEPTION_R12_HERO`
- `L1_RECEPTION_R13_HERO`

Solo se procesan mallas de **≥ 2.000 tris**. Los LOD se guardan ocultos en la colección `L1_RECEPTION_LOD`; no sustituyen todavía a LOD0 en el sector exportado.

## Resultado

- Fuentes procesadas: **39**.
- Triángulos de origen: **316.676**.
- LOD1 (ratio 0,45): **142.470 tris**.
- LOD2 (ratio 0,15): **47.466 tris**.
- Fallos QA: **0**.
- `qa_pass=true`.

QA: `docs/fm_reception_lod_qa.json`.
Backup: `docs/backups/FM_LEVEL1_V06_ARCH_before_reception_lod.blend`.
Script: `scripts/fm/fm_reception_lod.py`.

## Método

- Duplicado de objeto + malla independiente.
- `Decimate` COLLAPSE con triangulación.
- Limpieza de doubles, degenerados y normales.
- LOD1 suave; LOD2 flat.
- LOD1/LOD2 ocultos en viewport y render; son activos de biblioteca, no geometría del nivel.
- Metadatos `fm_class=LOD`, `fm_source`, `fm_lod`, `fm_generation=VERIFIED_RECEPTION_LOD`.

## Excluidos del LOD

Se conservan en LOD0 porque la decimación los volvía non-manifold (shells abiertos):

- `REC06_EQUIPMENT_HERO`
- `REC07_SECURITY_DESK_HERO`
- `REC09_SPRINKLER_RUN`
- `REC09_TRAY_N`
- `REC09_TRAY_W`

No se falseó el QA: el script los registra en `skipped` y el resto pasa.

## Limitaciones

- El sector `reception_sector.glb` sigue exportando **LOD0**: 326 objetos, 379.562 tris. Los LOD existen en Blender, pero todavía no hay conmutación por distancia en Godot ni export con LODs.
- Los draw calls no bajan por generar LODs; hace falta instancing/fusión por material y configuración de visibilidad.
- Los cinco objetos excluidos mantienen su coste completo.
- No hay LOD de colisiones ni proxies de jugador para R13.
- La reducción de tris no garantiza reducción de draw calls: hay 308 mallas únicas.

## Export y validación Godot

- GLB de prueba: `assets/models/fm/reception_lod_test.glb`.
- Tamaño: **61.932.496 bytes**.
- Contenido: **122 objetos / 108 mallas únicas / 548.890 tris**.
- Desglose: **44 LOD0 + 39 LOD1 + 39 LOD2**.
- Los LOD de R12 llevan sufijo `.001`; por eso una comprobación ingenua por sufijo parecía contar solo 36.
- Escena: `scenes/fm/fm_reception_lod_validate.tscn`.
- Script: `scripts/fm/fm_reception_lod_godot_validate_node.gd`.
- Resultado: **`RECEPTION_LOD_GODOT_OK`**.
- `meshes=122 unique=108 lod0=44 lod1=39 lod2=39`.
- AABB: `pos=(-110.1595,-0.014,8.000004)`, `size=(40.319,5.21,32.02999)`.
- Sin strays.

Esta validación comprueba que el GLB contiene todos los niveles y que caben en el volumen de Recepción. No conmuta LODs ni mide draw calls todavía; todos los niveles están visibles en el test.

## Conmutación de LOD

- Escena: `scenes/fm/fm_reception_lod_switch_test.tscn`.
- Script: `scripts/fm/fm_reception_lod_switch_test.gd`.
- Agrupa LOD0/LOD1/LOD2 por nombre base, tolerando sufijos `.001` de R12.
- Cámara de prueba en `(-90, 1.7, 20)`.
- Selección por distancia: ≤10 m LOD0, ≤20 m LOD1, >20 m LOD2.
- Muestra un solo nivel por grupo.
- Resultado: **`RECEPTION_LOD_SWITCH_OK`**.
  - `groups=44`
  - `visible=44`
  - `lod0=20`, `lod1=16`, `lod2=8`
  - `missing_lod0=0`
  - `multi_visible=0`

Con esto, la conmutación reduce los 122 meshes del GLB a **44 visibles** en la posición de prueba: un mesh por grupo.

## Medición de draw calls

- Comando: `DISPLAY=:0 /home/riyo/.local/bin/godot --path . --resolution 640x360 scenes/fm/fm_reception_lod_switch_test.tscn`.
- Renderer: **Forward+**, GTX 1650 Ti.
- Cámara: `(-90, 1.7, 20)`.
- Con LODs conmutados:
  - `draw_calls=94`
  - `objects=102`
  - `primitives=61.688`
- Baseline con solo LOD0 visible:
  - `draw_calls=94`
  - `objects=102`
  - `primitives=63.298`

### Conclusión

La conmutación de LOD reduce primitivas solo un **2,5 %** en esta cámara, y **no reduce los draw calls**. La razón es que:

- 20 de los 44 grupos ya están en LOD0 por cercanía.
- Cada mesh tiene varias superficies/materiales, así que un objeto puede generar más de un draw call.
- El cuello de botella principal no es el conteo de triángulos, sino el número de superficies/materiales y la falta de fusión de arquitectura estática.

Los LODs siguen siendo útiles para vistas lejanas y para el coste de vértices, pero **no son la solución principal a los 94 draw calls**.

## Merge por material

- Escena: `scenes/fm/fm_reception_merge_test.tscn`.
- Script: `scripts/fm/fm_reception_merge_test.gd`.
- Carga `reception_lod_test.glb`, oculta LOD1/LOD2, agrupa las superficies LOD0 por material y las fusiona con `SurfaceTool`.
- Resultado en Forward+ / GTX 1650 Ti, 640×360, cámara `(-90,1.7,20)`:
  - `materials=45`
  - `merged=45`
  - `draw_calls=28`
  - `objects=28`
  - `primitives=319.784`
  - **`RECEPTION_MERGE_OK`**

### Interpretación

La fusión por material reduce los draw calls de **94 a 28**, casi un 70 %. Es la prueba de que el cuello de botella son las superficies/materiales y no solo los triángulos.

El coste es que el merge dibuja **todos los LOD0** sin culling ni conmutación, por eso las primitivas suben a 319.784. En producción hay que combinar:

- merge de arquitectura estática por material,
- LOD/culling para props,
- separación de objetos interactivos para no perdigonar su lógica.

## Siguiente

1. Decidir la estrategia de fusión/instancing en producción conservando interactividad.
2. Medir de nuevo contra 94 draw calls y 28 draw calls del prototipo.
3. Continuar con Z10 feeds/S-10..S-15 y la capa de texturas/narrativa.

Sin commit.

# FRECUENCIA MUERTA — Z10: PASE DE ABANDONO E ILUMINACIÓN PRÁCTICA

## 1. Alcance

Pase de abandono y luz práctica sobre el conector Z10 (`x 40..62`,
`y 8..30`, altura 4,2 m), sin tocar la arquitectura ni los servicios
P0b.4. Se añaden tres colecciones:

- `L1_Z10_ABANDON`: debris, papeles, cables, techo caído, charcos,
  polvo, conos y el work light de trípode.
- `L1_Z10_LIGHTING`: luminarias de techo y luces prácticas.
- `L1_Z10_ATMOSPHERE`: volumen de niebla local, solo render.

Script: `scripts/fm/fm_z10_abandon.py`.
QA: `docs/fm_z10_abandon_qa.json`.
Backup: `docs/backups/FM_LEVEL1_V06_ARCH_before_z10_abandon.blend`.

## 2. Inventario verificado

- **45 objetos**, **38 mallas**, **7 luces**, **57.372 tris nuevos**.
- BBox: `[40,0, 8,0, -0,0002]` a `[62,0, 30,0, 4,2]`.
- `outside_room`: vacío.
- `portal_conflicts`: sur/este/norte vacíos.
- El `.blend` se guardó después del pase.

## 3. Iluminación práctica

| Luz | Tipo | Potencia | Posición / objetivo |
|---|---|---:|---|
| `LIGHT_Z10_Point_01..03` | POINT | 55 W | techo, `z 3,64`; `(47,14)`, `(57,14)`, `(52,25)` |
| `LIGHT_Z10_SouthSpill` | POINT | 35 W | `(42,5, 9,2, 2,6)`, azulada |
| `LIGHT_Z10_WorkSpot` | SPOT | 260 W | cabeza del trípode, cálida, ángulo 45° |
| `LIGHT_Z10_WorkFill` | POINT | 45 W | cabeza del trípode, cálida |
| `LIGHT_Z10_Emergency_E` | POINT | 10 W | `(61,5, 22,0, 3,0)`, roja |

- Tres luminarias de techo `SM_SH_LUMINAIRE_1500_ON_LOD1` centradas a
  `z 3,826` para que el cuerpo quede bajo el techo de `z 3,99`.
- `VOL_Z10_Fog`: volumen local de `22 × 22 × 4,2 m`, densidad 0,010,
  visible solo en render. La niebla de mundo existente se mantiene.
- El work light `PROP_Z10_WorkLight` se movió a `(56,2, 9,6)`, apunta al
  oeste por el pasillo sur (`target (44,0, 9,6, 1,4)`) para no chocar con
  el transformador. Se eliminaron duplicados `.001`–`.004` y se vinculó a
  `L1_Z10_ABANDON`; el floor snap lo apoya en el suelo.
- `PROP_Z10_WorkLamp`, la lámpara del workbench, es otro objeto y no se
  toca.

## 4. Renders de revisión

Script: `scripts/fm/fm_z10_abandon_render.py`.

- `docs/fm_z10_abandon_wide.png`: vista desde el noroeste hacia el
  sureste; columnas, conducto, suelo húmedo, estanterías, carro, cables,
  luces de emergencia y niebla. El work light queda fuera del encuadre.
- `docs/fm_z10_abandon_worklight.png`: close-up del trípode, cabeza,
  cable, palés, bidones y panel inclinado. Es la vista que mejor lee el
  work light.
- `docs/fm_z10_abandon_ceiling.png`: conducto, rejilla, luminaria,
  emergencia roja, cable colgante, techo caído y cono. El techo sigue
  dominante y oscuro.

Los renders usan las luces prácticas de la escena, sin las luces de
estudio `STUDIO_Z10_Key/Fill`. Para poder revisar el volumen se añaden
dos rebotes temporales de **140 W** y **80 W** y se sube la exposición a
**1,15**; esos rebotes no forman parte del juego y no se guardan.

## 5. Limitaciones

- El conjunto sigue siendo muy oscuro, sobre todo el techo y el fondo
  del pasillo. Es intencionado para terror, pero conviene validarlo en
  Godot con el jugador y la linterna antes de fijar valores.
- El haz del work light incide en el muro sur en la vista de close-up;
  el objetivo es atmosférico, no una prueba fotométrica.
- El debris reutiliza mallas hero de Security; no se ha creado geometría
  nueva para todos los escombros.
- No se ha exportado el GLB completo de la sala Z10 (shell, props,
  servicios, abandono y luces) ni se ha validado en Godot. La validación
  actual cubre los servicios P0b.4 y este pase en Blender/QA.
- No se han construido patinillos de Recepción/Seguridad; siguen
  pendientes por decisión del usuario.

## 6. Siguiente

1. Exportar el GLB completo de Z10 con shell, props, servicios P0b.4,
   abandono y luces prácticas; validar escala, colliders, draw calls y
   paso de cápsula en Godot 4.7.2.
2. Completar el resto de servicios de Z10: cuerpo de risers A/B,
   ramales/feeds de sprinkler y cruces S-10..S-15.
3. Aplicar el mismo pase de abandono/iluminación a Recepción y Seguridad.
4. Texturas/bake y objetos narrativos como capa final.

Sin commit.

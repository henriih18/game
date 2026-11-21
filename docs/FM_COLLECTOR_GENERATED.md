# El Coleccionista — modelo generado, limpieza y materiales

Fecha: 2026-11-17
Rama: `frecuencia-muerta` · HEAD `287b101` · sin commit

## 1. Origen

El usuario generó una criatura con un optimizador externo y la dejó en:

`Modelos-criaturas/Coleccionista/mesh-optimizer-1794961262932.glb`

Ese archivo **no se ha modificado**. El trabajo se hizo sobre una copia
abierta en Blender y guardada como:

- `nexus/nivel_01/FM_COLLECTOR_GENERATED_WORK.blend`

## 2. Estado inicial

- 1 malla (`geometry_0`), 39.953 vértices, 79.993 polígonos.
- Dimensiones: 1,562 × 1,882 × 2,002 m.
- Centrada en el origen; pies en z ≈ −1,009.
- Sin materiales ni texturas visibles.
- 27 islas: una principal de 36.280 vértices (cuerpo, cabeza, mochila y
  equipo fundidos) y 26 islas pequeñas (correas, cajas, colgantes, garras y
  varillas).
- Silueta: criatura jorobada de ~2 m, brazos largos, garras, máscara/skull,
  mochila y colgantes. Base claramente más coherente que las versiones
  procedurales v1–v4, con topología ruidosa.

## 3. Trabajo realizado

1. **Limpieza**
   - Merge by distance (0,0002).
   - Eliminación de vértices sueltos.
   - Recálculo de normales.
   - Eliminación del slot de material sin uso.
2. **Puesta a escala**
   - Modelo subido para que los pies queden en z = 0.
3. **UVs**
   - Smart UV Project (ángulo 66°, margen 0,02).
4. **Materiales PBR**
   - `M_Gen_Skin` — `assets/art/fm/collector/T_Collector_Skin_Dark.png` +
     `assets/art/fm/flesh_normal.png`.
   - `M_Gen_Canvas` — `T_Collector_Cloth_Dark.png` + `T_Collector_Cloth_N.png`.
   - `M_Gen_Leather` — `T_Collector_Leather_Dark.png` +
     `T_Collector_Leather_N.png`.
   - `M_Gen_Steel` — (0,045 · 0,050 · 0,055), roughness 0,78, metallic 0,15.
   - `M_Gen_Brass`, `M_Gen_Bone`, `M_Gen_Dark`, `M_Gen_Lens` emisivo.
   - Asignación por regiones espaciales: piel al cuerpo; canvas a la zona de
     mochila; acero a la máscara; hueso a puntas de pies/dedos; latón y lentes
     en la máscara.
5. **Detalle**
   - Respirador/filtro añadido a la máscara.
   - Se probaron gafas nuevas, pero quedaban duplicadas sobre la frente; se
     eliminaron los islotes sobrantes (916 vértices). Se conservan los dos
     ojos dorados originales.
6. **Renders de revisión**
   - `/tmp/opencode/gen6_threeq.png`
   - `/tmp/opencode/gen6_front.png`
   - Cámara 55 mm, Key/Fill/Rim, EEVEE 640×640, AgX.

## 4. Archivo exportado

`assets/models/fm/collector_generated_v1.glb`

| Dato | Valor |
|---|---:|
| Tamaño | 10.367.068 bytes |
| Meshes / nodos | 1 / 1 |
| Materiales | 7 |
| Imágenes | 6 |
| Triángulos | 80.313 |
| Cámaras | 0 |
| Animaciones | 0 |

Nodo: `Collector_Generated`. Exportado con `export_yup`, `export_apply`,
selección activa y sin cámaras ni luces.

## 5. QA

`blender-asset-qa` (`profile=game`, `eps=0.002`, `tol=0.08`,
`no_modifiers=True`) devuelve **6 hallazgos**:

- 10 aristas con winding inconsistente.
- 5 piezas flotantes/detached:
  - 255 vértices en `[-0.151, 0.883, 0.703]`
  - 121 vértices en `[0.022, 0.454, 0.522]`
  - 402 vértices en `[0.273, 0.628, 0.784]`
  - 131 vértices en `[0.364, 0.210, 0.696]`
  - 119 vértices en `[0.742, 0.315, 1.418]`

Las cinco piezas flotantes son correas, bolsas y colgantes del equipo; se
**aceptan como intencionales** porque forman parte de la silueta de saqueador.
Las 10 aristas de winding y 9 aristas non-manifold se consideran deuda técnica
menor: no afectan a la silueta ni al render, pero deben corregirse si el modelo
se usa en producción o se anima.

## 6. Limitaciones

- La topología sigue siendo ruidosa y no es apta para deformación o rigging
  fino.
- La mochila y el cuerpo están fundidos en una sola isla; no se pueden separar
  por piezas sin retopología.
- La máscara es la original con ojos dorados; el respirador/filtro es un
  añadido.
- El modelo es una base estilizada, no el acabado realista final de
  `fotos-referencia/modelos-referencia.png`.
- No se ha integrado en `fm_creature_models.gd` ni en ninguna escena.

## 7. Backups

`docs/backups/FM_COLLECTOR_GENERATED_2026-11-17/`:

- `FM_COLLECTOR_GENERATED_WORK.blend`
- `collector_generated_v1.glb`
- `collector_source_original.glb` (copia intacta del GLB del usuario)
- `gen6_threeq.png`, `gen6_front.png`
- `T_Collector_Skin_Dark.png`, `T_Collector_Cloth_Dark.png`,
  `T_Collector_Leather_Dark.png`

## 8. Siguiente paso

- Revisar el modelo y los renders con el usuario.
- Si se aprueba la base: QA de winding/non-manifold, posible retopología
  parcial, integración como `Coleccionista` y prueba de comportamiento de robo.
- Si no: mantenerlo como base de referencia y no bloquear el resto del
  desarrollo.

Sin commit.

## Pasada de proporción y limpieza v2 (2026-11-17)

- Se corrigieron proporciones por regiones: torso estrechado (x 0.88, y 0.95), mochila reducida (x 0.86, y/z 0.88/0.94) y cabeza/máscara agrandada un 5,5 %.
- Se eliminaron dos islas sueltas (bolsa colgante de 121 verts y varilla exterior de 119 verts).
- `M_Gen_Steel` pasó a mate (metallic 0, rough 0.82) para evitar el aspecto cromado de la máscara.
- Resultado: 39.881 verts, 79.612 polys, 1,56 × 1,94 × 2,00 m.
- Export: `assets/models/fm/collector_generated_v2.glb`, 1 malla, 7 materiales, 0 cámaras/luces, ~79,6k tris.
- Renders: `/tmp/opencode/gen_final2_front.png` y `gen_final2_threeq.png`.
- QA: 4 errores menores (10 aristas con winding inconsistente, 3 pares de z-fighting y 2 piezas flotantes de equipo aceptadas como intencionales). No se considera final ni realista.

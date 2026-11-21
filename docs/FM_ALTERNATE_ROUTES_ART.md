# FRECUENCIA MUERTA — Arte de las rutas alternativas del Nivel 1 V06

**Fecha:** 2026-11-16  
**Rama:** `frecuencia-muerta` · HEAD `287b101`  
**Estado:** pase visual de las rutas Alt implementado, validado e integrado. Sin commit.  
**Documento base:** `docs/FM_ALTERNATE_ROUTES.md`

---

## 1. Alcance

Las rutas alternativas tenían geometría de servicio oscurecida, pero seguían
pareciendo un blockout: sin señalización, sin conducciones visibles y sin
lenguaje de instalación. Este pase añade una capa de arte ligera y funcional
para que el jugador reconozca cada túnel, se oriente dentro de la red y lea
las salidas sin convertir los pasillos de 1,25 m en espacios ornamentados.

No se ha modificado la arquitectura, el navmesh ni los accesos. Todos los
objetos decorativos llevan tokens de omisión de colisión (`SIGN`, `CABLE`,
`HAZ`, `FLOOR_LINE`, `DIS_WATER`, `LIGHT`, `TRIM`), por lo que el número de
colliders de la red sigue siendo **86**.

---

## 2. Composición

La colección `L1_ART_ALT_ROUTES` contiene **20 objetos** y **38.632 triángulos
reales** (55.690 según el contador interno del script). Materiales planos
`M_ALT_*`: pintura verde-gris, panel metálico, texto claro, galvanizado,
amarillo de seguridad, goma, emisivo verde, emergencia roja y agua.

| Elemento | Objeto | Contenido |
|---|---|---|
| Conducciones | `ALT_Conduits_CABLE` | Dos tubos por ruta con abrazaderas, a z≈1,28 (NWStair a z≈2,55) |
| Señalización | `ALT_SignPlates_SIGN` + 13 textos | Placas de 0,95×0,24 m con soporte embutido y texto en relieve |
| Franjas de peligro | `ALT_Hazard_HAZ` | 8 franjas amarillas en las bocas principales |
| Líneas de guiado | `ALT_FloorLines_FLOOR_LINE` | Líneas en MaintCorridor, NorthGallery y ReceptionStair |
| Charcos | `ALT_Puddles_DIS_WATER` | 4 charcos de agua sucia |
| Balizas | `ALT_Beacons_LIGHT` | 7 balizas emisivas verdes con soporte al techo |

### 2.1 Señalización

Trece carteles: `GALERÍA ESTE` (×2), `PASILLO TÉCNICO` (×2), `GALERÍA NORTE`
(×2), `CONDUCTO DE SERVICIO`, `ACCESO RECEPCIÓN` (×2), `ENLACE VESTUARIOS`
(×2), `ESCALERA NOROESTE` y `PASILLO DE SEGURIDAD`.

Los carteles se montaron sobre los paramentos interiores reales, no sobre el
eje de las bocas. La posición y la normal se corrigieron con raycast contra la
arquitectura; varias placas estaban inicialmente dentro del espesor del muro.
Se verificaron las trece lecturas en Godot: texto legible, sin espejo y sin
quedar oculto por el muro.

---

## 3. Archivos

**Nuevos**
- `scripts/fm/fm_alt_routes_art_build.py`
- `scripts/fm/fm_alt_routes_art_export_headless.py`
- `assets/models/fm/alternate_routes_art.glb`
- `docs/fm_alternate_routes_art_export.json`
- `docs/FM_ALTERNATE_ROUTES_ART.md`

**Modificados**
- `scenes/fm/fm_alternate_routes.tscn`: `AlternateRoutesDressing` cuelga de
  `AlternateRoutesSector` e instancia `alternate_routes_art.glb`.
- `scripts/fm/fm_level1_v06.gd`: `get_alternate_routes_mesh_count()` cuenta
  solo las mallas base `SM_L1_Alt_*`; el arte no altera el check de 86.
- `docs/FM_ALTERNATE_ROUTES.md`, `docs/FM_LEVEL1_V06_CLOSURE.md`, `AGENTS.md`.

---

## 4. Datos técnicos

| Dato | Valor |
|---|---:|
| Objetos de arte | 20 |
| Triángulos GLB | 38.632 |
| Tamaño GLB | 1.545.912 bytes |
| Mallas / nodos | 20 / 20 |
| Materiales | 7 |
| Imágenes | 0 |
| Cámaras / luces | 0 / 0 |
| AABB Blender | min (−95,65, −32,557, 0,001) · max (105,69, 66,19, 2,597) |
| AABB dentro de bounds | Sí |

`alternate_routes_art.glb` no incluye cámaras ni luces; la iluminación vive en
`fm_alternate_routes.tscn` (27 OmniLight3D sin sombras).

---

## 5. QA

`blender-asset-qa` sobre **134 objetos** (114 mallas de `L1_ARCH_ALTERNATE` +
20 de `L1_ART_ALT_ROUTES`), perfil `render`, `eps=0.002`, `tol=0.08`,
`no_modifiers=True`, `max_tris=300000`:

**PASS · 0 errores · 181 warnings aceptados**

Los warnings son UVs solapadas o de área cero en textos generados por fuente,
duplicados de vértices de la conversión de texto y winding de cilindros. No hay
z-fighting ni piezas flotantes.

Incidencias corregidas durante la QA:
- Carteles dentro del espesor del muro (8 placas): recolocadas sobre la cara
  interior real con raycast y normales corregidas donde apuntaban hacia fuera.
- Soportes de cartel coplanares con el paramento: embutidos 1 cm.
- Franjas, charcos y balizas flotantes en bocas sin suelo/techo: eliminadas o
  dotadas de soporte.
- `ALT_Puddles_PUDDLE` renombrado a `ALT_Puddles_DIS_WATER` para que
  `FMGLBCollision` lo omita y no cree una losa de colisión de 169×98 m.
- Balizas sin soporte: se añadió `ALT_BeaconStems_TRIM` embutido en techo y
  baliza.

---

## 6. Pruebas

| Prueba | Resultado |
|---|---:|
| `fm_level1_v06_smoke` | **407 PASS / 0 FAIL** |
| `fm_level1_v06_alt_routes_smoke` | **73 PASS / 0 FAIL** |
| `fm_level1_v06_gameplay` | **105 PASS / 0 FAIL** |
| `fm_full_run` | **49 PASS / 0 FAIL** |
| `fm_graphics_presets_smoke` | **194 PASS / 0 FAIL** |
| Perf 1280×720 | **PASS** |

Perf final: 7.559 frames en 13,01 s, **581,0 fps** medios, mínimo **160,7**,
p1 **236,5**, p99 **4,23 ms**, 0 frames sobre 33,3 ms.

Escena: **4.101.232 tris**, 4.245 mallas, 774 materiales, **185 luces**,
**1.523 colliders**, 0 huérfanos, 1.090,6 MB de texturas.

---

## 7. Capturas

- 13 close-ups de carteles en `/tmp/opencode/altart_close_*.png`.
- Contacto de los 13 carteles: `/tmp/opencode/altart_all_signs.png`.
- 12 vistas de rutas: `/tmp/opencode/conn_godot_*.png` y
  `/tmp/opencode/conn_godot_contact_altart.png`.

Los túneles siguen siendo pasillos de servicio, ahora con conducciones,
señalización y balizas legibles. La iluminación local es tenue y deliberada.

---

## 8. Limitaciones

- Los materiales del arte son planos, sin texturas: el detalle viene de la
  geometría, la señalización y la iluminación. Un pase de texturas queda para
  la optimización/arte global.
- La señalización genera muchos triángulos de texto y warnings de UV; es
  aceptable para carteles estáticos, pero conviene vigilar el coste si se
  añaden más.
- No hay props pesados dentro de los túneles: el espacio de 1,25 m debe quedar
  libre para la cápsula agachada y la lectura de las rutas.
- La IA de Seguridad y la verticalidad NWStair/StairsMain siguen pendientes.
- Sin commit hasta autorización del usuario.

---

## 9. Backups

- Pre-art: `docs/backups/FM_CONNECTIVITY_after_2026-11-16/` (máster md5
  `4ce04b69c59b7d7dd683c84cdfc493ed`).
- Post-art: `docs/backups/FM_ALT_ROUTES_ART_after_2026-11-16/` con el máster
  (`md5 dab0b763afb1ebe55eefeb791a4b6a2a`) y `alternate_routes_art.glb`
  (`md5 340fa1840802b2154ba31c8b42a58c2a`).
- Reporte de export: `docs/fm_alternate_routes_art_export.json`.

---

## 10. Skills usadas

`blender-core`, `blender-hardsurface-modeling`, `blender-pbr-materials`,
`blender-texturing`, `blender-lighting-lookdev`, `blender-asset-qa`,
`blender-scene-setup`, `blender-game-optimization`,
`blender-export-pipelines`, `level-design`, `scenario-godot-3d-world` y
`writing-plans`.

No se usaron `blender-rendering` ni `blender-texture-baking`: las capturas se
hicieron en Godot y los materiales son planos reutilizables.

---

## 11. Siguiente fase

1. Ajuste de IA y encuentros en Seguridad tras abrir el acceso principal.
2. Verticalidad: conexión inferior NWStair ↔ StairsMain y posible mezzanine en
   Almacén.
3. Pase visual global (niebla, color grading, transiciones) y optimización
   medida de texturas/materiales/LOD.
4. Extracción dinámica, solo después de definir sus reglas.
5. Commit cuando el usuario lo autorice.

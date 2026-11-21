# FRECUENCIA MUERTA — Rutas alternativas y conectividad del Nivel 1 V06

**Fecha:** 2026-11-16  
**Rama:** `frecuencia-muerta` · HEAD `287b101`  
**Estado:** Fase 1 (rutas Alt), Fase 2 (navegación de Seguridad) y pase visual de las rutas implementados y verificados. Sin commit.  
**Documento de origen:** `docs/FM_LEVEL1_V06_CONNECTIVITY_PROPOSAL.md`

---

## 1. Alcance

El Nivel 1 V06 tenía una espina principal de ~175 m con ramales, pero la red de pasajes alternativos ya modelada en el máster no se había exportado al juego. Esta fase integra esa red como rutas de servicio y sigilo para el jugador, y abre el acceso principal de Seguridad para que la IA de capa 1 pueda recorrer el oeste del mapa.

No se ha construido arquitectura nueva. Se reutilizan los huecos de 1,25 m que ya existían en los blockout y la colección `L1_ARCH_ALTERNATE` del máster.

---

## 2. Rutas integradas

| Ruta | Conexión | Altura | Uso previsto |
|---|---|---:|---|
| EastGallery | Almacén ↔ Mantenimiento | 1,25 m | Bucle este, sigilo agachado |
| MaintCorridor | StairsConnector ↔ corredor ↔ Mantenimiento | 1,25 m | Atajo sur y acceso de servicio |
| NorthConnector + NorthGallery | Control ↔ Oficinas | 1,25 m | Bucle oeste alto |
| OfficesCrawl | Oficinas ↔ SecurityCorridor | 1,25 m | Acceso de mantenimiento al oeste |
| ReceptionStair | Recepción ↔ corredor | 1,25 m | Atajo oeste |
| SecurityCorridor | Seguridad ↔ corredor | 2,20 m | Ruta de servicio de capa 2 (ya existente) |
| ServiceLoop | Vestuarios ↔ Almacén | 1,25 m | Bucle de servicio del personal |
| NWStair | Control ↔ nivel −4,5 | Completa | Reservada para verticalidad futura |

El jugador agachado mide 1,20 m y los túneles 1,25 m; la cápsula de prueba pasa. La IA principal mide 2,20 m y no entra en los túneles, por lo que estas rutas son una ventaja de sigilo y escape para los jugadores.

---

## 3. Implementación

### 3.1 Exportación

- `scripts/fm/fm_alt_routes_export_headless.py` exporta la colección `L1_ARCH_ALTERNATE` sin duplicar mallas ya presentes en otros GLB y sin la anotación `ANNOT_L1_MaintCorridor`.
- Resultado: `assets/models/fm/alternate_routes.glb`, **86 mallas**, **1.032 tris**, **104.816 bytes**, 6 materiales, 0 imágenes, 0 cámaras y 0 luces.
- Los materiales blockout se oscurecieron en la sesión headless (suelo húmedo verdoso, muro verde-gris, hormigón oscuro, marco metálico) sin guardar el `.blend`.
- `scripts/fm/fm_security_connector_export_headless.py` exporta el conector principal de Seguridad: suelo y dos muros, **3 mallas**, **36 tris**, **5.016 bytes**.

### 3.2 Escenas y colisiones

- `scenes/fm/fm_alternate_routes.tscn`: raíz `AlternateRoutes`, `AlternateRoutesSector`, `AlternateRoutesArt` (geometría base) y `AlternateRoutesDressing` (arte, `alternate_routes_art.glb`), con **27 luces** de servicio sin sombras.
- `scenes/fm/level1_v06.tscn`: `AlternateRoutes` se instancia **fuera de `Sectors`**, por lo que los 15 sectores y sus pruebas no cambian.
- `scenes/fm/fm_security_art.tscn`: `SecurityConnectorArt` cuelga de `SecuritySector`; se añadió una losa de techo simple porque el techo original del máster está roto.
- `scripts/fm/fm_level1_v06.gd`: `ALT_ROUTES_BOUNDS`, `_setup_alternate_routes()` y `Collision_AlternateRoutes`. Se generaron **86 colliders** para las rutas.
- `SECURITY_BOUNDS` se amplió hasta Godot z = −4,0 para incluir el conector principal.

### 3.3 Navegación

Se añadieron dos `NavigationLink3D` de capa 1 en Seguridad:

- `NavLink_SecurityConnector` en el vano sur (z ≈ −4).
- `NavLink_Security_N` en la puerta norte (z ≈ −36).

La barrera de cinta de la puerta sur se retrajo en el export de `security_sector.glb` (se conservan postes y carcasas), dejando libre el vano de 4,6 m. La compuerta de servicio de capa 2 sigue siendo un atajo, no la única entrada.

---

## 4. Archivos

**Nuevos**
- `assets/models/fm/alternate_routes.glb`
- `assets/models/fm/alternate_routes_art.glb`
- `assets/models/fm/security_connector.glb`
- `scenes/fm/fm_alternate_routes.tscn`
- `scripts/fm/fm_alt_routes_export_headless.py`
- `scripts/fm/fm_alt_routes_art_build.py`
- `scripts/fm/fm_alt_routes_art_export_headless.py`
- `scripts/fm/fm_security_connector_export_headless.py`
- `tests/fm_level1_v06_alt_routes_smoke.gd`
- `tests/fm_level1_v06_alt_routes_smoke.tscn`
- `tests/fm_level1_v06_connectivity_shots.gd`
- `tests/fm_level1_v06_connectivity_shots.tscn`
- `docs/fm_alternate_routes_export.json`
- `docs/fm_alternate_routes_art_export.json`
- `docs/fm_security_connector_export.json`
- `docs/FM_ALTERNATE_ROUTES.md`
- `docs/FM_ALTERNATE_ROUTES_ART.md`

**Modificados**
- `scenes/fm/level1_v06.tscn`
- `scenes/fm/fm_security_art.tscn`
- `scripts/fm/fm_level1_v06.gd`
- `scripts/fm/fm_security_sector_export_headless.py`
- `scripts/fm/fm_security_sector_godot_validate_node.gd`
- `tests/fm_level1_v06_smoke.gd`
- `assets/models/fm/security_sector.glb`
- `docs/FM_P0B6_SHELL.md`
- `AGENTS.md`

---

## 5. Pruebas

| Prueba | Resultado |
|---|---:|
| `fm_level1_v06_smoke` | **407 PASS / 0 FAIL** |
| `fm_level1_v06_alt_routes_smoke` | **73 PASS / 0 FAIL** |
| `fm_level1_v06_gameplay` | **105 PASS / 0 FAIL** |
| `fm_full_run` | **49 PASS / 0 FAIL** |
| `fm_graphics_presets_smoke` | **194 PASS / 0 FAIL** |
| Perf 1280×720 | **PASS** |

Perf: 7.559 frames en 13,01 s, **581,0 fps** medios, mínimo **160,7**, p1 **236,5**, p99 **4,23 ms**, 0 frames sobre 33,3 ms.

Escena: **4.101.232 tris**, 4.245 mallas, 774 materiales, **185 luces**, **1.523 colliders**, navmesh principal 1.986 polígonos y servicio 8, 0 huérfanos, 1.090,6 MB de texturas.

La prueba física recorre cada ruta con una cápsula agachada de radio 0,34 / altura 1,16, comprueba que la cápsula de pie/IA queda bloqueada en los túneles de 1,25 m y verifica que hay suelo real bajo cada punto.

---

## 6. Capturas

12 vistas en `/tmp/opencode/conn_godot_*.png` y contacto `/tmp/opencode/conn_godot_contact_altart.png`:

`security_connector`, `security_south_door`, `east_gallery_warehouse`, `east_gallery_maintenance`, `maint_branch`, `maint_tunnel`, `north_gallery_control`, `north_gallery_offices`, `offices_crawl`, `reception_stair`, `service_loop`, `nw_stair`.

Además, 13 close-ups de carteles en `/tmp/opencode/altart_close_*.png` y contacto `/tmp/opencode/altart_all_signs.png`; los trece textos se leen sin espejo. Los túneles se ven oscuros y de servicio, con conducciones, señalización, franjas y balizas; el detalle artístico se documenta en `docs/FM_ALTERNATE_ROUTES_ART.md`.

---

## 7. Limitaciones

- Las rutas tienen arte ligero (conducciones, 13 carteles, franjas, líneas, charcos y balizas), pero no props pesados ni texturas propias: el detalle viene de geometría y señalización.
- La señalización aporta muchos triángulos de texto y warnings de UV aceptados; vigilar el coste si se añaden más carteles.
- `security_sector.glb` pasó de 32,7 MB a 46,4 MB porque el export anterior solo empaquetaba 7 imágenes y el nuevo incluye los sets PBR de los props (27 imágenes, 12 compartidas a 1K). Es un coste de memoria de texturas ya visible en el perfil.
- La seguridad tiene ahora dos accesos principales (conector sur y puerta norte) además del hatch de servicio; falta ajustar la presión de IA y los encuentros en esa zona.
- NWStair sigue siendo un fondo de saco vertical; su conexión inferior se estudiará en la fase de verticalidad.
- No hay test automático de la retracción visual de la barrera; se validó por smoke, sonda y captura.

---

## 8. Backups

- Pre-conectividad: `docs/backups/FM_CONNECTIVITY_before_2026-11-16/`
- Pre-reexport de Seguridad: `docs/backups/FM_SECURITY_CONNECTOR_before_2026-11-16/security_sector.glb` (md5 `a8a5fd407718e345141f911aab882fc8`)
- Post-conectividad: `docs/backups/FM_CONNECTIVITY_after_2026-11-16/`
  - `FM_LEVEL1_V06_ARCH_after_connectivity.blend` md5 `4ce04b69c59b7d7dd683c84cdfc493ed`
  - `alternate_routes.glb` md5 `ae7cf959593930f8e78549d6927514cc`
  - `security_connector.glb` md5 `6107298e2d032d85b78aa62bbb491299`
  - `security_sector.glb` md5 `97ed28b41ba25e8376d40e081fb7c92b`
- Post-arte de rutas: `docs/backups/FM_ALT_ROUTES_ART_after_2026-11-16/`
  - máster md5 `dab0b763afb1ebe55eefeb791a4b6a2a`
  - `alternate_routes_art.glb` md5 `340fa1840802b2154ba31c8b42a58c2a`

El máster Blender no se guardó con la retirada de la cinta: el cambio vive en
`fm_security_sector_export_headless.py` y en el GLB reexportado. Cualquier
reexport futuro a través de ese script mantiene la barrera retraída.

---

## 9. Skills usadas

- `level-design`: grafo de rutas, reachability y métricas del jugador.
- `scenario-godot-3d-world`: colisión, navmesh, pruebas de cápsula y capturas.
- `writing-plans`: propuesta formal y fases.
- Blender: `blender-core`, `blender-asset-qa`, `blender-export-pipelines`, `blender-game-optimization`, `blender-hardsurface-modeling`, `blender-pbr-materials`, `blender-lighting-lookdev`, `blender-scene-setup`, `blender-texturing`.

No se usaron `blender-rendering` ni `blender-texture-baking`: las capturas se hicieron en Godot y los materiales se reutilizaron/oscurecieron en el export.

---

## 10. Siguiente fase

1. Ajuste de IA y encounters en Seguridad tras abrir el acceso principal.
2. Verticalidad: conexión inferior NWStair ↔ StairsMain y posible mezzanine en Almacén.
3. Pase visual global (niebla, color grading y transiciones) y optimización medida de texturas/materiales/LOD.
4. Extracción dinámica, solo después de definir sus reglas.
5. Commit cuando el usuario lo autorice.

# FRECUENCIA MUERTA — P0b.6 cierre de cáscara Recepción/Seguridad

Fecha: 2026-11-10. Estado: **cerrado en lo auditado y exportado**, con una deuda explícita: patinillos (decisión del usuario); S-24 (drenajes y accesos) queda diferido.

## 1. Objetivo y método

Auditoría de solo lectura de Recepción y Seguridad antes de modelar, para comprobar el estado real frente a `docs/FM_QUALITY_SERVICES_AUDIT.md`. Se revisaron colecciones, mallas, bboxes, materiales, los documentos R9/R13 y P0A, y renders de auditoría. Después se aplicaron solo los cierres mínimos que no dependen de los patinillos.

**Hallazgo principal:** la auditoría de servicios está desactualizada. Recepción R9 ya tiene HVAC, sprinkler y bandejas hero; Seguridad P0A ya tiene HVAC, sprinkler y bandejas. No se reconstruyó nada de eso.

## 2. Estado real frente a la auditoría

| ID | Auditoría | Estado comprobado | Acción P0b.6 |
|---|---|---|---|
| S-01 | HVAC de Recepción termina en el aire | **Resuelto en R9**: `REC09_HVAC_MAIN` 16.844 tris, x−110..−70, sleeves E/O y fire dampers E/O, 7 rejillas, soportes. | Ninguna. |
| S-02 | Bandejas N/O cortadas | **Resuelto en R9**: bandejas N y O con cables, soportes y sleeves en muros. | Ninguna. |
| S-03 | Sprinkler de Recepción sin cabezas | **Resuelto en R9**: `REC09_SPRINKLER_RUN` x−110..−70, cabezas, sleeves y soportes. | Ninguna. |
| S-04 | HVAC sin rejillas | **Resuelto en R9**: 7 rejillas (4 en principal, 3 en ramales). | Ninguna. |
| S-05 | HVAC de Seguridad termina en el aire | **Resuelto en P0A**: `SEC_P0A_HVAC_RUN` 26 m, y10..36, sleeves y fire dampers S/N, 4 rejillas, soportes. | Ninguna. |
| S-06 | 3 rejillas de muro sin conducto | **Abierto**: `R21B_SERV_VentS/E/W`, 364 tris cada una, sobre muros macizos sin abertura ni plénum. | **Retiradas** a `L1_SECURITY_RETIRED_P0B6`; no se inventó una red de retorno. |
| S-07 | Bandejas de Seguridad cortadas | **Resuelto en P0A**: bandeja O 18,5 m y central 12 m, cables, soportes y endcaps; sin risers. | Ninguna; risers quedan con S-18. |
| S-08 | Sprinkler de Seguridad insuficiente | **Resuelto en P0A**: 23,6 m, 6 cabezas, soportes y caps; sigue siendo un solo ramal. | Ninguna; es cierre visual, no cálculo hidráulico. |
| S-09 | Bandeja CCTV sin conexión | **Abierto**: `R21A_CCTV_CableTray` en y35,5; la bandeja central P0A termina en y24,6 (hueco ≈10,8 m). | **`P0B6_CCTV_TRAY_LINK`**: 10,3 m + 2,3 m + 0,6 m + bajada de 0,55 m, con soportes y cables. |
| S-21 | Línea de orientación no llega a extracción | **Abierto**: `DET_REC02_Way_CenterToExtraction` terminaba en y−33; el deck empieza en y−35. | **Extendida** 2 m hasta y−35,0; el hueco queda cerrado. |
| S-22 | Cruces de muro sin sleeve/firestop | Recepción y Seguridad tienen sleeves y fire dampers en sus cruces principales; las únicas rejillas sin conducto eran S-06. | Retiradas S-06; sin nuevos cruces. |
| S-24 | Sin fire dampers, drains ni accesos | Fire dampers **sí existen** en Recepción y Seguridad; test drains y paneles de acceso sistemáticos siguen sin modelar. | Diferido; documentado. |
| S-18 | Sin patinillos verticales | Sigue pendiente por decisión del usuario; los conductos terminan en sleeves/fire dampers, sin shaft físico. | **No construir** sin nueva aprobación. |
| S-23/S-25 | Alturas no coordinadas / sin drains | Sin cambios en este pase. | Prioridad baja. |
| S-19 | Duplicados ocultos/legacy | Sin cambios. | Prioridad baja. |

## 3. Geometría nueva y modificada

| Objeto | Tris | Verts | BBox |
|---|---:|---:|---|
| `P0B6_CCTV_TRAY_LINK` | 4.472 | 2.432 | `(−87,108, 24,600, 3,690)..(−84,305, 35,553, 4,690)` |
| `DET_REC02_Way_CenterToExtraction` | 12 | 8 | `(−94,040, −35,000, 0,004)..(−93,960, −16,000, 0,010)` |

- La bandeja nueva es de 0,42 × 0,10 m, con raíles galvanizados, travesaños de acero, 3 cables por tramo y 5 soportes tipo trapecio; empalma con la bandeja central P0A en y24,6 y baja hasta la bandeja del rack de CCTV en y35,5.
- La línea se extendió moviendo sus 4 vértices del extremo sur de y−33 a y−35; conserva material `M_REC01_Wayfinding` y UV (sin textura, el estiramiento no afecta).
- Se retiraron 3 rejillas (`R21B_SERV_VentS/E/W`, 1.092 tris) a `L1_SECURITY_RETIRED_P0B6`. No se borraron.

QA: `docs/fm_p0b6_shell_qa.json`, `qa_pass: true`; 0 non-manifold, 0 degenerate, UV presente. Backup: `docs/backups/FM_LEVEL1_V06_ARCH_before_p0b6_shell.blend`.

## 4. Renders de revisión

- `docs/fm_p0b6_cctv_link.png`: bandeja galvanizada, giro y bajada hasta el rack de CCTV; los cables caen sobre los monitores. Sin clipping evidente. **Aprobado.**
- `docs/fm_p0b6_reception_line.png`: la línea verde llega al deck/hazard; el hueco de 2 m está cerrado. **Aprobado como verificación técnica.**
- `docs/fm_p0b6_security_services.png`: vista amplia con HVAC, rejillas, sprinkler, bandejas y el checkpoint; la sala sigue siendo blockout/checkpoint-only. **Aprobado como contexto técnico.**

## 5. Exportación y Godot

- **Recepción:** `assets/models/fm/reception_sector.glb` reexportado en headless con `scripts/fm/fm_reception_sector_export_headless.py`. Se añadió `L1_RECEPTION_R13_HERO`, que el exporter omitía: los lockers y carteles R13 ya están en el GLB.
  - **292 objetos / 274 mallas únicas / 403.610 tris / 36.235.496 bytes (~36,24 MB)**; aabb `(−110,25, −40,15, −0,20)..(−69,84, −3,81, 5,40)`; `strays: []`.
  - Godot tras `--import`: `RECEPTION_SECTOR meshes=292 unique=274 aabb_pos=(−110,25, −0,20, 3,812608) size=(40,4095, 5,6, 36,33739) strays=[]` → **`RECEPTION_SECTOR_GODOT_OK`**.
  - Validador actualizado de 326/308 (estado pre-R13) a **292/274**.
- **Seguridad:** `assets/models/fm/security_sector.glb` generado en headless con `scripts/fm/fm_security_sector_export_headless.py`: **534 objetos / 521 mallas únicas / 972.890 tris / 32.756.828 bytes (32,76 MB)**; aabb `(−105,15, 9,73, −1,219)..(−70,85, 36,27, 4,90)`; `strays: []`. Excluye la R2 legacy oculta, `LIB_*` y las colecciones retiradas; incluye R21A/B/C/D, P0A, R2_HERO, R1, P0B6 y la cáscara.
  - Godot tras `--import`: `SECURITY_SECTOR meshes=534 unique=521 aabb_pos=(−105,15, −1,218732, −36,27) size=(34,3, 6,118732, 26,54) strays=[]` → **`SECURITY_SECTOR_GODOT_OK`**.
  - Validador nuevo: `scenes/fm/fm_security_sector_validate.tscn` + `scripts/fm/fm_security_sector_godot_validate_node.gd` (530/517 desde la retirada de la cinta de la barrera sur, AABB y strays).
  - Durante la preparación se detectaron 4 duplicados del tramo corto de la bandeja; se corrigió `fm_p0b6_shell_close.py` y se reejecutó: `L1_P0B6_SHELL` queda con **1 objeto / 4.472 tris**.
- **Nivel completo:** no hay export V06; `scenes/fm/level1.tscn` sigue cargando el GLB V05. No se debe afirmar validación de nivel completo.
- `z10_sector.glb` no se toca: Recepción/Seguridad están fuera de su región.

## 6. Limitaciones

- Sin texturas, bake ni desgaste fino; Recepción mantiene el fondo blockout y Seguridad sigue checkpoint-only.
- Sin LOD ni colisiones; el export de Seguridad ya existe y está validado en Godot.
- Patinillos pendientes por decisión del usuario; el retorno de aire y la conexión física de conductos quedan diferidos con ellos.
- Los test drains y paneles de acceso de S-24 no se han modelado.
- No se auditó en este pase el resto de habitaciones (escaleras, laboratorio, vestíbulos) salvo el corredor, que ya tiene servicios P0B.

## 7. Siguiente

1. Pase hero de arte en Z10: PBR, bake, desgaste, suciedad, narrativa ambiental e iluminación; medir en la GTX 1650 Ti.
2. Vertical slice jugable: FPS, linterna con batería, objeto físico, escondite, Vigilante, ruido/detección y extracción en Recepción.
3. LOD, colisiones y optimización de los sectores ya exportados, empezando por Seguridad (534 objetos / 972.890 tris); después, extensión de arte, biblioteca instanciada y multijugador.

**Sin commit.** No se ha modificado `fotos-referencia/`.

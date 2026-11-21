# FRECUENCIA MUERTA — Seguridad P0a: portales adaptados

Fecha: 2026-11-09
Archivo: `nexus/nivel_01/FM_LEVEL1_V06_ARCH.blend`
Escena: `NEXUS_L1_V06_ARCH`
Colección: `L1_SECURITY_P0A_HERO`
Commit: no

## 1. Alcance

Segundo lote de sustitución P0a en Seguridad: los dos vanos de acceso.

- Vano sur: `x −92,0..−86,0`, `y = 10,0`; claro **6,0 × 3,04 m**.
- Vano norte: `x −96,0..−92,0`, `y = 36,0`; claro **4,0 × 2,44 m**.
- No se modificaron muros, dinteles ni la altura libre de la arquitectura.

## 2. Restricción y solución

Los portales de la biblioteca (`SM_SH_PORTAL_4000/6000/8000`) miden **3,265 m** de alto total y **2,88 m** de claro. No caben en los vanos de Seguridad (3,04 m y 2,44 m).

Solución: **variantes adaptadas** con el mismo lenguaje visual P0a:

- Postes que envuelven las jambas existentes con 10 mm de solape.
- Paneles embutidos, bandas, remaches, placas de anclaje, pernos y sellos.
- Dintel de 0,24 m, franja naranja, cap y umbral.
- Sin hoja de puerta: son portales abiertos, como los vanos originales.

## 3. Objetos nuevos

| Objeto | Tris | Vértices | Polys | Dimensiones | BBox |
|---|---:|---:|---:|---|---|
| `SEC_P0A_PORTAL_S` | 5.844 | 3.056 | 3.150 | 6,6 × 0,54 × 3,295 m | `[-92,3, 9,73, 0,0]..[-85,7, 10,27, 3,295]` |
| `SEC_P0A_PORTAL_N` | 5.844 | 3.056 | 3.150 | 4,6 × 0,54 × 2,695 m | `[-96,3, 35,73, 0,0]..[-91,7, 36,27, 2,695]` |

Total del lote: **11.688 tris**.

## 4. Jambas y dinteles antiguos

Los seis objetos de 12 tris de `L1_ARCH_ZONES` se conservan:

- `SM_L1_Zone03_Security_Door_S_L/R/T`.
- `SM_L1_Zone03_Security_Door_N_L/R/T`.

Quedan detrás de los postes y dinteles nuevos, cubiertos con 10 mm de solape. No se movieron ni se ocultaron; la arquitectura permanece intacta y el QA los registra en `old_trim_kept`.

## 5. QA

`docs/fm_security_p0a_portals_qa.json`:

- 2 objetos nuevos en `L1_SECURITY_P0A_HERO`.
- **0 non-manifold**, **0 degenerados**, UV presente en ambos.
- `old_trim_kept`: 6 objetos.
- `.blend` guardado.
- Backup: `docs/backups/FM_LEVEL1_V06_ARCH_before_security_p0a_portals.blend`.

## 6. Renders

- `docs/fm_security_p0a_portal_south_out.png`: vista desde el corredor; marco negro, paneles verticales, dintel con franja naranja y el checkpoint de Seguridad al fondo. Es la toma principal del lote.
- `docs/fm_security_p0a_portal_south_in.png`: vista desde el interior de Seguridad; marco, emergencia roja superior, lector y checkpoint. El fondo claro es el muro del corredor/vestíbulo, no una hoja.
- `docs/fm_security_p0a_portal_north_in.png`: vista desde el interior hacia el vano norte; marco y dintel legibles. El espacio exterior al norte aún está vacío/sin desarrollar, por eso el fondo es una pared clara.
- `docs/fm_security_p0a_portal_detail_s.png`: dintel, franja naranja, techo y cartel `SEGURIDAD`; verifica la unión con el marco.

Script: `scripts/fm/fm_security_p0a_portals_render.py`; no guarda `.blend`.

## 7. Limitaciones

- Son **portales abiertos**, no puertas con hoja; no hay mecánica de apertura ni control de acceso integrado.
- No se han instalado lectores nuevos; el lector existente se conserva.
- El espacio exterior al norte sigue sin desarrollar.
- Sin texturas/bake, sin LOD y sin integración de colisiones/export a Godot.
- Los paneles verticales son oscuros y lisos a esta distancia; el detalle de remaches se lee solo de cerca.

## 8. Siguiente

1. Lote 3: HVAC, bandejas y sprinklers antiguos de Seguridad → módulos P0a/P0b.
2. Recepción hero: bancas, taquillas, servicios y desgaste.
3. LOD de grupos pesados y export por colección.
4. Texturas/bake y narrativa al final.

Sin commit.

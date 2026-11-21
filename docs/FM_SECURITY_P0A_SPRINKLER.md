# SEGURIDAD — P0a SPRINKLER DN80

## Alcance
Sustitución del sprinkler antiguo `R21B_SERV_Sprinkler` (996 tris) por un tramo hero continuo construido a partir de los maestros P0b, dentro de la colección `L1_SECURITY_P0A_HERO`. No se tocó la arquitectura ni el checkpoint.

## Objetos construidos

| Objeto | Tris | Verts | Descripción |
|---|---:|---:|---|
| `SEC_P0A_SPRINKLER_RUN` | 5.580 | 2.832 | Tubo DN80 de 23,6 m, x=-90,7, y11,2..34,8, z4,38; rotado +90° Z; extremos cerrados con `holes_fill`. |
| `SEC_P0A_SPRINKLER_HEADS` | 10.320 | — | 6 cabezas upright en y12/16/20/24/28/32, z4,43..4,535. |
| `SEC_P0A_SPRINKLER_SUPPORTS` | 2.952 | — | 6 soportes con varilla, cleat y placa a z4,795. |
| `SEC_P0A_SPRINKLER_CAPS` | 1.000 | — | Tapas de extremo en y11,2 y y34,8. |
| **Total** | **19.852** | | |

- Materiales reutilizados: `M_SH_Sprinkler_Red` y `M_SH_Steel_Dark`.
- El objeto antiguo se retiró a `L1_SECURITY_RETIRED_P0A` (oculto, sin borrar).
- Backup: `docs/backups/FM_LEVEL1_V06_ARCH_before_security_p0a_services.blend`.

## QA
`docs/fm_security_p0a_sprinkler_qa.json`:

- 0 caras non-manifold.
- 0 caras degeneradas.
- UV presente en los cuatro objetos.
- `qa_pass=true`.

## Renders de revisión
Script `scripts/fm/fm_security_p0a_sprinkler_render.py` (CYCLES 1280×720, 64 spp, denoise; no guarda `.blend`).

- `docs/fm_security_p0a_sprinkler_wide.png`: línea roja continua sobre la nave, soportes y cabezas; se lee el conjunto con el checkpoint y el ops center.
- `docs/fm_security_p0a_sprinkler_line.png`: vista longitudinal del tubo, acoplamientos, soportes y cabezas; aparece un cable vertical existente de la sala, no forma parte del lote.
- `docs/fm_security_p0a_sprinkler_heads.png`: detalle de tubo, acoplamientos y cabezas upright; las cabezas se leen pequeñas a esta distancia.

## Limitaciones
- Las cabezas son upright y de tamaño real; en tomas amplias se leen como puntos pequeños.
- El tramo termina en tapas dentro de la sala. La conexión a una red vertical/patinillo sigue pendiente por decisión del usuario.
- No hay texturas/bake, colisiones específicas ni LOD para este lote.
- La iluminación del render es de revisión, no la iluminación final.

## Siguiente
1. HVAC de Seguridad: sustituir `R21B_SERV_HVACDuct` por tramo hero con bridas, soportes y difusores.
2. Bandejas oeste y central: sustituir por tramos hero con soportes y cables.
3. Revisar las tres rejillas `R21B_SERV_VentS/E/W` y conectarlas al HVAC.
4. Después: Recepción hero, desgaste, LOD/export y Godot.

Sin commit.

# SEGURIDAD — P0a HVAC 800×600

## Alcance
Sustitución del ducto antiguo `R21B_SERV_HVACDuct` (3.620 tris, tramo que terminaba en el aire) por un tramo hero continuo de 26 m entre los muros sur y norte de Seguridad, con pasamuros, compuertas cortafuego, soportes y difusores.

No se modificó la arquitectura. La colección es `L1_SECURITY_P0A_HERO`.

## Objetos construidos

| Objeto | Tris | Descripción |
|---|---:|---|
| `SEC_P0A_HVAC_RUN` | 10.912 | Tramo de 26 m cortado de `P0B_HVAC_RUN_800x600`; x=-97,2, y10..36, centro z3,55; rotado 90° Z; extremos cerrados. |
| `SEC_P0A_HVAC_SUPPORTS` | 7.392 | 6 soportes con varilla, placa de techo, travesaño, cleat y pernos. |
| `SEC_P0A_HVAC_SLEEVE_S` | 3.308 | Pasamuros rectangular en el muro sur, y=10. |
| `SEC_P0A_HVAC_SLEEVE_N` | 3.308 | Pasamuros rectangular en el muro norte, y=36. |
| `SEC_P0A_HVAC_FIREDAMPER_S` | 7.888 | Compuerta cortafuego en el extremo sur, y=10,55. |
| `SEC_P0A_HVAC_FIREDAMPER_N` | 7.888 | Compuerta cortafuego en el extremo norte, y=35,45. |
| `SEC_P0A_HVAC_GRILLE_14/20/26/32` | 3.820 c/u | 4 difusores de doble deflexión bajo el ducto, a z3,25. |
| **Total** | **55.976** | 10 objetos, 28.724 vértices. |

## Continuidad
- El ducto recorre el lado oeste de Seguridad, paralelo al eje Y, a la misma cota que la columna principal del corredor (`z=3,55`).
- Entra por el muro sur con sleeve y fire damper, y sale por el muro norte con sleeve y fire damper.
- Los difusores se reparten a y=14/20/26/32.
- El objeto antiguo se retiró a `L1_SECURITY_RETIRED_P0A`; no se borró.

## QA
`docs/fm_security_p0a_hvac_qa.json`:

- 10 objetos.
- 0 caras non-manifold.
- 0 caras degeneradas.
- UV presente en todos.
- `qa_pass=true`.
- AABB `[-97.69, 9.846, 3.091]..[-96.71, 36.153, 4.686]`.

Backup: `docs/backups/FM_LEVEL1_V06_ARCH_before_security_p0a_hvac.blend`.

## Renders
Script `scripts/fm/fm_security_p0a_hvac_render.py` (CYCLES 1280×720, 64 spp, denoise; no guarda `.blend`).

- `docs/fm_security_p0a_hvac_wide.png`: ducto continuo sobre la nave, con difusores, soportes, sprinkler rojo, checkpoint y ops center.
- `docs/fm_security_p0a_hvac_line.png`: vista longitudinal del tramo, bridas, difusores y soportes; al fondo se lee el muro norte.
- `docs/fm_security_p0a_hvac_detail.png`: detalle de brida, difusor y soporte de techo.
- `docs/fm_security_p0a_hvac_sleeve.png`: pasamuros sur con compuerta cortafuego; la pared se lee poco en el recorte, pero se verifica la penetración.

## Limitaciones
- El ducto termina en los muros con sleeve/fire damper; **no hay conexión física al ramal del corredor** ni patinillo vertical. El usuario dejó los patinillos pendientes.
- El metal nuevo está limpio y brillante; falta el pase de desgaste/pátina.
- Las rejillas de pared `R21B_SERV_VentS/E/W` siguen sin conectar a este ducto.
- No hay texturas/bake, LOD ni colisión específica para este lote.
- La iluminación de los renders es de revisión, no la final.

## Siguiente
1. Sustituir las bandejas oeste y central por tramos hero con soportes y cables.
2. Revisar y conectar las tres rejillas de pared al HVAC.
3. Documentar el lote y continuar con Recepción hero/desgaste.

Sin commit.

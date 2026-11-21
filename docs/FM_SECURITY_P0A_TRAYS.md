# SEGURIDAD — P0a BANDEJAS DE CABLES

## Alcance
Sustitución de las dos bandejas antiguas de baja densidad por bandejas hero continuas, con soportes, cables y tapas:

- `R21B_SERV_WestCableTray` (1.540 tris, 18,5 m).
- `R21B_SERV_CentreCableTray` (1.924 tris, 12 m).

La bandeja del CCTV (`R21A_CCTV_CableTray`, 2.616 tris) **no se sustituyó**: pertenece al conjunto hero del ops center y ya tiene un nivel de detalle aceptable.

No se modificó la arquitectura. Colección: `L1_SECURITY_P0A_HERO`.

## Objetos construidos

| Objeto | Tris | Descripción |
|---|---:|---|
| `SEC_P0A_TRAY_WEST_18M5` | 4.432 | Bandeja de 18,5 m en el muro oeste, x≈−104,72, y13..31,5, z3,55. Cortada de `P0B_TRAY_RUN_400`. |
| `SEC_P0A_TRAY_CENTRE_12M` | 2.898 | Bandeja de 12 m suspendida, x≈−84,55, y12,6..24,6, z4,30. Cortada de `P0B_TRAY_RUN_400`. |
| `SEC_P0A_TRAY_SUPPORTS_WEST` | 4.592 | 7 soportes de pared con placa, brazo y pernos. |
| `SEC_P0A_TRAY_SUPPORTS_CENTRE` | 4.940 | 5 soportes de techo con dos varillas, travesaño y pernos. |
| `SEC_P0A_TRAY_CABLES_WEST` | 2.244 | 3 cables (negro, gris, naranja) y bridas cada 1,5 m. |
| `SEC_P0A_TRAY_CABLES_CENTRE` | 1.716 | 3 cables y bridas cada 1,5 m. |
| `SEC_P0A_TRAY_ENDCAPS` | 432 | Tapas de extremo de ambas bandejas. |
| **Total** | **21.254** | 7 objetos. |

## QA
`docs/fm_security_p0a_trays_qa.json`:

- 7 objetos, 21.254 tris.
- 0 caras degeneradas.
- UV `MapaUV` presente.
- `inside=true`.
- `retired_visible=[]`.
- Bandeja oeste: bbox `[-104.93, 12.97, 3.494]..[-104.51, 31.5, 3.6]`.
- Bandeja central: bbox `[-84.765, 12.57, 4.244]..[-84.345, 24.6, 4.35]`.

Backup: `docs/backups/FM_LEVEL1_V06_ARCH_before_security_trays.blend`.

## Renders
Script `scripts/fm/fm_security_p0a_trays_render.py` (CYCLES 1280×720, 64 spp, denoise; no guarda `.blend`).

- `docs/fm_security_p0a_tray_wide.png`: vista de la nave con la bandeja central suspendida y la bandeja oeste sobre el muro.
- `docs/fm_security_p0a_tray_west.png`: bandeja oeste, peldaños, soportes y emergencia roja.
- `docs/fm_security_p0a_tray_centre.png`: bandeja central con cable naranja, varillas y techo; incluye un panel colgante existente del caos.
- `docs/fm_security_p0a_tray_detail.png`: detalle de peldaños, soporte y tapa de empalme.

## Limitaciones
- Los cables se leen poco desde abajo; están dentro del canal, no en la parte superior visible.
- Los soportes son funcionales y limpios, pero más simples que los del ducto hero.
- La vista central incluye un panel colgante y cables existentes del caos, que no pertenecen a este lote.
- El metal nuevo está limpio; falta desgaste/pátina.
- No hay LOD, texturas/bake ni colisión específica.
- Las rejillas `R21B_SERV_VentS/E/W` siguen sin conectar al HVAC.

## Siguiente
1. Conectar o retirar las tres rejillas de pared.
2. Revisar el conjunto completo de Seguridad y medir el coste acumulado.
3. Pasar a Recepción hero (bancas/taquillas), desgaste y luego LOD/export.

Sin commit.

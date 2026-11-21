# FRECUENCIA MUERTA — Seguridad P0a: luminarias y emergencias

Fecha: 2026-11-09
Archivo: `nexus/nivel_01/FM_LEVEL1_V06_ARCH.blend`
Escena: `NEXUS_L1_V06_ARCH`
Colección: `L1_SECURITY_P0A_HERO`
Commit: no

## 1. Alcance

Primer lote de sustitución P0a en Seguridad:

- 7 luminarias de techo antiguas de 60 tris + 7 paneles de 12 tris.
- 3 emergencias de pared antiguas de 0,3 × 0,267 × 0,22 m.
- Sustitución por los maestros de la biblioteca compartida, sin remodelar la arquitectura.
- No se tocaron el checkpoint hero, el ops center, las puertas ni los servicios.

## 2. Objetos nuevos

### Luminarias de techo

- 7 instancias de `SM_SH_LUMINAIRE_1500_OFF`, malla compartida.
- **9.228 tris por instancia**; 64.596 tris en total.
- Posiciones: `(-101.5, 13)`, `(-88, 13)`, `(-74.5, 13)`, `(-101.5, 31)`, `(-88, 31)`, `(-74.5, 31)`, `(-88, 21)`.
- Origen a `z = 4.42`; el cuerpo cuelga hasta `z = 4.392` y el techo queda en `z = 4.72`.
- Se usó la variante **OFF** para mantener el aspecto apagado/abandonado; la sala sigue iluminada por la iluminación de revisión y las luces prácticas existentes.

### Emergencias de pared

- 3 instancias de `SM_SH_EMERGENCY_WALL_E`, malla compartida.
- **9.712 tris por instancia**; 29.136 tris en total.
- `SEC_P0A_EMERG_S`: pared sur, `(-94.6, 10.0, 3.16)`, rotación 0°.
- `SEC_P0A_EMERG_W1`: pared oeste, `x = -105.0`, `y = 14.6`, `z = 3.16`, rotación −90° Z.
- `SEC_P0A_EMERG_W2`: pared oeste, `x = -105.0`, `y = 27.6`, `z = 3.16`, rotación −90° Z.
- W2 conserva la luz práctica existente `R21B_LIGHT_Emergency_1`.
- Se añadieron dos luces rojas de 8 W sin sombra: `SEC_P0A_LIGHT_EMERG_S` y `SEC_P0A_LIGHT_EMERG_W1`.

## 3. Retirados

17 objetos viejos movidos a `L1_SECURITY_RETIRED_P0A` (oculta, sin borrar):

- `KIT_SEC01_CeilingLightHousing_0..6`.
- `DET_SEC01_CeilingLightPanel_0..6`.
- `R21B_SERV_EmergencyS`, `R21B_SERV_EmergencyW1`, `R21B_SERV_EmergencyW2`.

Ninguno queda visible en la escena.

## 4. QA

`docs/fm_security_p0a_lights_qa.json`:

- 10 objetos nuevos.
- 2 luces nuevas.
- 17 objetos retirados; `retired_visible: []`.
- `all_inside: true`.
- `all_mesh_shared: true`.
- Mallas compartidas: luminarias con 8 usuarios de malla; emergencias con 5.
- Colección `L1_SECURITY_P0A_HERO` con 12 objetos (10 mallas + 2 luces).

## 5. Renders

- `docs/fm_security_p0a_lights_wide.png`: vista amplia de Seguridad con las nuevas tiras de techo, emergencias rojas y el checkpoint/ops center al fondo.
- `docs/fm_security_p0a_lights_ceiling.png`: vista de techo corregida; se leen las luminarias suspendidas, el sprinkler rojo y los cables. La sala sigue siendo de revisión, no beauty.
- `docs/fm_security_p0a_lights_emergency.png`: close-up de la emergencia nueva; el panel y el halo rojo se leen, pero la toma está sobreexpuesta y sin contexto de pared.

Script: `scripts/fm/fm_security_p0a_lights_render.py`; no guarda `.blend`.

## 6. Limitaciones

- El techo conserva el sprinkler rojo, cables colgantes y el panel cuadrado de emergencia existente; no forman parte de este lote.
- Las luminarias nuevas son geometría hero, pero sin texturas/bake finales.
- La iluminación de la sala sigue siendo la de revisión; no se ha hecho el pase de luz final.
- No hay LOD para las 7 luminarias; son mallas compartidas, pero 64.596 tris en la sala.
- El close-up de emergencia está sobreexpuesto; se puede repetir con menos clave si se necesita una imagen de presentación.

## 7. Siguiente

1. Lote 2: puertas y portales antiguos de Seguridad → maestros `SM_SH_DOOR_*` / `SM_SH_PORTAL_*`.
2. Lote 3: HVAC, bandejas y sprinklers antiguos → módulos P0a/P0b.
3. Después: Recepción hero (bancas, taquillas, servicios, desgaste).
4. LOD de grupos pesados y export por colección.
5. Texturas/bake y narrativa al final.

Sin commit.

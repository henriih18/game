# SEGURIDAD — P0a SERVICIOS (CIERRE DE LOTE)

## Alcance
Sustitución de los servicios antiguos de Seguridad por maestros de la biblioteca compartida y módulos P0a/P0b, sin modificar la arquitectura y sin tocar el checkpoint hero ni el centro de operaciones.

Colección: `L1_SECURITY_P0A_HERO`.
Objetos retirados: `L1_SECURITY_RETIRED_P0A` (ocultos, no borrados).

## Lotes cerrados

### 1. Luces y emergencias
- 7 `SEC_P0A_LUMINAIRE_00..06` (9.228 tris c/u, malla compartida).
- 3 `SEC_P0A_EMERG_S/W1/W2` (9.712 tris c/u).
- 2 point lights rojas de emergencia.
- Doc: `docs/FM_SECURITY_P0A_LIGHTS.md`.

### 2. Portales
- `SEC_P0A_PORTAL_S` 5.844 tris (6,6×0,54×3,295 m).
- `SEC_P0A_PORTAL_N` 5.844 tris (4,6×0,54×2,695 m).
- Variantes adaptadas a los vanos; las jambas/dinteles viejos quedan cubiertos.
- Doc: `docs/FM_SECURITY_P0A_PORTALS.md`.

### 3. Sprinkler DN80
- `SEC_P0A_SPRINKLER_RUN` 5.580 tris (23,6 m).
- `SEC_P0A_SPRINKLER_HEADS` 10.320 tris (6 cabezas).
- `SEC_P0A_SPRINKLER_SUPPORTS` 2.952 tris.
- `SEC_P0A_SPRINKLER_CAPS` 1.000 tris.
- Total 19.852 tris.
- Doc: `docs/FM_SECURITY_P0A_SPRINKLER.md`.

### 4. HVAC 800×600
- `SEC_P0A_HVAC_RUN` 10.912 tris (26 m).
- `SEC_P0A_HVAC_SUPPORTS` 7.392 tris.
- Sleeves S/N 3.308 c/u; fire dampers S/N 7.888 c/u.
- 4 difusores 3.820 c/u.
- Total 55.976 tris.
- Doc: `docs/FM_SECURITY_P0A_HVAC.md`.

### 5. Bandejas
- `SEC_P0A_TRAY_WEST_18M5` 4.432 tris.
- `SEC_P0A_TRAY_CENTRE_12M` 2.898 tris.
- Soportes west/centre 4.592/4.940 tris.
- Cables west/centre 2.244/1.716 tris.
- Endcaps 432 tris.
- Total 21.254 tris.
- Doc: `docs/FM_SECURITY_P0A_TRAYS.md`.

## Total del lote
- **Aproximadamente 202.500 tris** de servicios nuevos, repartidos en 29 objetos visibles.
- Mallas compartidas con la biblioteca en luces, portales, sprinkler, HVAC y bandejas.
- QA por lote: 0 caras non-manifold, 0 degeneradas y UV presente en todos los objetos construidos.
- No se eliminó ningún sistema aprobado.

## Renders de conjunto
Script `scripts/fm/fm_security_p0a_services_render.py` (CYCLES 1280×720, 64 spp, exposición 0,78; no guarda `.blend`).

- `docs/fm_security_p0a_services_east.png`: vista desde el este. Se leen el ducto, las bandejas, el sprinkler rojo, las luminarias y las emergencias sobre la nave; al fondo, el checkpoint y el ops center.
- `docs/fm_security_p0a_services_north.png`: vista desde el norte. Se leen el ops center, las taquillas, las bandejas y parte del ducto; la zona central queda oscura.

## Limitaciones
- Las tres rejillas de pared `R21B_SERV_VentS/E/W` siguen sin conectar; necesitan red de retorno o patinillo. **No se construyó ningún patinillo** porque el usuario lo dejó pendiente.
- El HVAC termina en sleeve/fire damper en los muros; no hay conexión física al ramal del corredor.
- El metal nuevo está limpio y brillante; falta el pase de desgaste/pátina.
- El suelo, los muros y parte del mobiliario de Seguridad siguen en calidad blockout.
- No hay texturas/bake, LOD, colisión específica ni export/validación Godot de este lote.
- La iluminación de los renders es de revisión, no la final.

## Siguiente
1. Decidir si se conectan las rejillas de pared o se documentan como deuda.
2. Pasar a Recepción hero: bancas, taquillas, servicios y desgaste.
3. LOD de los grupos pesados de la biblioteca y export por colección.

Sin commit.

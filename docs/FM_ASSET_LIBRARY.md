# FRECUENCIA MUERTA — Biblioteca compartida de assets hero

Fecha: 2026-11-09
Archivo principal: `nexus/nivel_01/FM_LEVEL1_V06_ARCH.blend`
Biblioteca standalone: `assets/blender/fm_shared_hero_library.blend`
Escena de biblioteca: `FM_ASSET_LIBRARY`
Colección raíz: `FM_LIBRARY`

## 1. Objetivo

Extraer de la escena jugable los maestros compartidos que estaban colocados en el corredor y conservar, en una biblioteca reutilizable, los objetos hero mejor modelados de Seguridad. La biblioteca permite reutilizar geometría mediante colecciones enlazadas o instancias, sin duplicar mallas ni contaminar el nivel con catálogos de prueba.

No se ha reconstruido nada ni se ha modificado la geometría de los originales.

## 2. Estado del nivel

- `L1_SHARED_HERO` ya **no está en la escena del nivel**. Se movió completo a `FM_ASSET_LIBRARY > LIB_CORRIDOR_HERO`.
- El nivel queda con **2.457 objetos**; la comprobación de objetos de `L1_SHARED_HERO` en el nivel devuelve **0**.
- Los maestros P0a conservan su geometría, LODs, colisiones y `P0_TEST_ASSEMBLY`.
- Las colecciones originales de Seguridad **no se movieron ni se borraron**. Las copias de biblioteca comparten malla con sus originales en el archivo principal.
- El corredor ya no muestra puertas, luminarias, ductos ni el test assembly como si fueran parte del nivel.

## 3. Estructura de la biblioteca

```
FM_ASSET_LIBRARY (escena)
└── FM_LIBRARY
    ├── LIB_CORRIDOR_HERO
    │   └── L1_SHARED_HERO
    │       ├── DOORS
    │       ├── DOORS_LOD
    │       ├── LIGHTING
    │       ├── LIGHTING_LOD
    │       ├── SERVICES
    │       ├── P0_COLLISION
    │       └── P0_TEST_ASSEMBLY
    └── LIB_SECURITY_HERO
        ├── LIB_SEC_CHECKPOINT
        ├── LIB_SEC_CHECKPOINT_DEBRIS
        ├── LIB_SEC_OPS
        ├── LIB_SEC_LOCKERS
        ├── LIB_SEC_HATCH
        ├── LIB_SEC_STORAGE
        ├── LIB_SEC_CART
        ├── LIB_SEC_FIXTURES
        ├── LIB_SEC_DEBRIS_R21C
        └── LIB_SEC_DEBRIS_R21D
```

## 4. Contenido y conteos

### Corredor — P0a

| Colección | Objetos | Mallas | Tris |
|---|---:|---:|---:|
| `LIB_CORRIDOR_HERO` / `L1_SHARED_HERO` | 230 | 147 | 853.164 |

Incluye puertas y portales, luminarias y emergencias, servicios HVAC/bandejas/sprinklers/conduit, sleeves/firestop, shaft access, LOD1/LOD2 y proxies de colisión `-col`.

### Seguridad — copias hero

| Grupo | Objetos | Mallas | Tris | Nota |
|---|---:|---:|---:|---|
| `LIB_SEC_CHECKPOINT` | 128 | 127 | 26.200 | Mostrador, monitor, teclado, lector, intercom, barrera, partición y señal |
| `LIB_SEC_CHECKPOINT_DEBRIS` | 32 | 31 | 13.412 | Cables, escombros, techo caído y charcos del checkpoint |
| `LIB_SEC_OPS` | 70 | 69 | 213.092 | Puestos, sillas, monitores, rack, CCTV, panel eléctrico y caos |
| `LIB_SEC_LOCKERS` | 3 | 2 | 181.984 | Dos bancos de taquillas; ~91k tris por banco |
| `LIB_SEC_HATCH` | 8 | 7 | 29.456 | Persiana, mostrador, señal, intercom y ventana |
| `LIB_SEC_STORAGE` | 3 | 2 | 56.958 | Estantería y panel de llaves |
| `LIB_SEC_CART` | 2 | 1 | 20.870 | Carro de herramientas |
| `LIB_SEC_FIXTURES` | 4 | 3 | 3.316 | Caja eléctrica, emergencia y hollín |
| `LIB_SEC_DEBRIS_R21C` | 13 | 12 | 27.856 | Sillas, CRT, cables, fragmentos, cristal y teja |
| `LIB_SEC_DEBRIS_R21D` | 46 | 45 | 55.510 | Sillas, palés, carrete, puertas, CRT, conos, techo, charcos y polvo |
| **Total Seguridad** | **309** | **299** | **628.654** | |

### Totales

- Biblioteca en el archivo principal: **539 objetos / 446 mallas / 1.481.818 tris**.
- Biblioteca standalone: **539 objetos / 446 mallas / 1.481.818 tris**; única escena `FM_ASSET_LIBRARY`.
- Las 10 mallas extra de objeto frente a malla son empties de grupo (`LIB_*_ROOT`), no geometría.

## 5. Uso y reutilización

### En Blender

1. Abrir `assets/blender/fm_shared_hero_library.blend` o el archivo principal y seleccionar `FM_ASSET_LIBRARY`.
2. Enlazar (`File > Link`) la colección `LIB_*` necesaria en la escena destino.
3. Colocar una **instancia de colección** o enlazar los objetos individuales.
4. No editar la malla desde la sala: modificar el maestro de biblioteca y dejar que las instancias se actualicen.
5. Para piezas repetidas, usar duplicados vinculados/instancias; no duplicar mallas.

### En Godot

- Exportar solo la colección necesaria a GLB; no exportar la biblioteca completa.
- Ocultar en runtime todo `MeshInstance3D` cuyo nombre termine en `-col`.
- Los proxies `-col` son geometría de colisión, no visual.

### Reglas

- No mover ni borrar los originales de Seguridad: la biblioteca ya tiene copias.
- No usar la biblioteca completa como una sala; son maestros.
- No colocar assets pesados sin LOD.
- No añadir armas ni combate: la biblioteca es de exploración, mobiliario, servicios y supervivencia.

## 6. Deuda y limitaciones

- **LOD pendiente** en los grupos pesados: lockers (181.984 tris), ops center (213.092), storage (56.958), cart (20.870) y puertas P0a (228.428). No colocar en masa hasta generar LOD1/LOD2.
- La biblioteca conserva la geometría, no texturas/bake finales. Los materiales son procedurales de trabajo.
- Falta el pase de **desgaste/pátina** en Recepción y en los props de Seguridad reutilizados; la geometría hero está limpia.
- El receptor de la barrera de Recepción queda parcialmente oculto por el mostrador en la vista de revisión; no es un defecto de biblioteca.
- La biblioteca standalone no incluye escena de nivel, luces de sala ni cámaras de revisión; solo los maestros y sus materiales.
- No hay export GLB de la biblioteca completa; se exportará por colección cuando se integre en una sala.

## 7. Validación

- Nivel sin objetos de `L1_SHARED_HERO`: **0**.
- Fuentes de Seguridad intactas:
  - `L1_SECURITY_R2_HERO`: 158 objetos / 158 mallas / 39.612 tris.
  - `L1_SECURITY_R21A_HERO`: 76 objetos / 69 mallas / 213.092 tris.
  - `L1_SECURITY_R21C_HERO_LOCKERS`: 2 / 2 / 181.984.
  - `L1_SECURITY_R21D_HERO_CHAOS`: 100 / 100 / 60.598.
- Standalone: solo `FM_ASSET_LIBRARY`, sin escenas de nivel/estudio.
- Reportes:
  - `docs/FM_ASSET_LIBRARY_STEP1.json`
  - `docs/FM_ASSET_LIBRARY_STEP2.json`
  - `docs/FM_ASSET_LIBRARY_QA_FINAL.json`
  - `docs/FM_ASSET_LIBRARY_FILE_REPORT.json`
  - `docs/FM_ASSET_LIBRARY_MAIN_REPORT.json`

## 8. Scripts

- `scripts/fm/fm_asset_library_step1.py`: mueve `L1_SHARED_HERO` a la escena de biblioteca.
- `scripts/fm/fm_asset_library_step2.py`: copia los grupos de Seguridad con malla compartida.
- `scripts/fm/fm_asset_library_cleanup.py`: limpia la copia standalone y purga huérfanos.
- `scripts/fm/fm_asset_library_report.py`: valida y escribe reportes.

## 9. Siguiente

1. Usar la biblioteca para sustituir los servicios antiguos de Seguridad por los maestros P0a. **Lote cerrado:** luces/emergencias, portales, sprinkler, HVAC y bandejas ya sustituidos. Ver el cierre en `docs/FM_SECURITY_P0A_SERVICES.md`, con detalle en `docs/FM_SECURITY_P0A_LIGHTS.md`, `docs/FM_SECURITY_P0A_PORTALS.md`, `docs/FM_SECURITY_P0A_SPRINKLER.md`, `docs/FM_SECURITY_P0A_HVAC.md` y `docs/FM_SECURITY_P0A_TRAYS.md`; quedan las tres rejillas de pared por conectar.
2. Generar LOD de los grupos pesados antes de poblar Recepción/Seguridad/Z10.
3. Pase de desgaste/pátina en Recepción y en los props reutilizados.
4. Exportar por colección a GLB y validar en Godot cuando se integre una sala.

Sin commit.

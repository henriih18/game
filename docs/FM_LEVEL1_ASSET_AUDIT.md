# FRECUENCIA MUERTA — Auditoría de assets reutilizables del Nivel 1

Fecha: 2026-11-05
Archivo auditado: `nexus/nivel_01/FM_PILOT_MAINTENANCE_v01.blend`
Escena: `NEXUS_L1_V05`
Baseline de comparación: `nexus/nivel_01/NEXUS_L1_V05_control_v134.blend`

## 1. Alcance y método

Auditoría de solo lectura del Nivel 1 para decidir qué objetos pueden convertirse en assets reutilizables en otros niveles. No se hicieron pruebas en Godot, no se tocó la librería compartida y no se hizo commit.

Se exportó un inventario JSON con nombre, tipo, colecciones, librería de origen, transformaciones, dimensiones, bbox, malla, vértices, polígonos, UVs, materiales, modificadores y flags de ocultación. Se comparó el archivo actual contra `NEXUS_L1_V05_control_v134.blend` para localizar objetos desplazados.

Archivos de apoyo:

- `docs/fm_level1_asset_families.csv`
- `docs/fm_level1_moved_objects.csv`
- `/tmp/opencode/audit_pilot.json`
- `/tmp/opencode/audit_control.json`

## 2. Estado global

| Métrica | Valor |
|---|---:|
| Objetos totales | 3.029 |
| Mallas totales | 2.786 |
| Mallas ocultas | 510 |
| Mallas visibles | 2.276 |
| Triángulos visibles | 283.731 |
| Mallas visibles enlazadas | 128 (200.175 tris) |
| Mallas visibles locales | 2.148 (83.556 tris) |
| Mallas locales visibles sin UV | 1.209 |

Lectura: el 70 % de los triángulos visibles ya viene de `NEXUS_SHARED_ASSETS.blend`; el resto es geometría local, en gran parte blockout de seis caras. No tiene sentido convertir cada malla en un asset.

## 3. Familias detectadas

| Familia | Prioridad | Estado | Mallas | Tris | Sin UV |
|---|---|---:|---|---:|---:|
| A. Assets enlazados de `NEXUS_SHARED_ASSETS` | P0 | Enlazado; no duplicar | 128 | 200.175 | 0 |
| B. Caldera / boiler kit | P1 | QA/UV aprobado | 48 | 1.963 | 0 |
| C. Generador / genset kit | P1 | QA/UV aprobado | 72 | 2.482 | 0 |
| D. Colector y tuberías | P1 | QA/UV aprobado | 23 | 1.752 | 0 |
| E. Colector de gas | P1 | QA/UV aprobado | 35 | 2.224 | 0 |
| F. Depósito de aire | P1 | QA/UV aprobado | 14 | 1.760 | 0 |
| G. Luminarias de emergencia | P1 | QA/UV aprobado | 28 | 1.752 | 0 |
| H. Bandejas de cables | P1 | QA/UV aprobado | 36 | 264 | 0 |
| I. Estructura modular | P1 | QA/UV aprobado | 130 | 4.509 | 0 |
| J. Equipamiento y soportes del piloto | P2 | QA/UV aprobado | 13 | 206 | 0 |
| K. Props interactivos de recepción | P2 | Blockout funcional | 65 | 1.994 | 65 |
| L. Ascensor / elevator kit | P3 | Blockout | 48 | 376 | 0 |
| M. Puerta y servicio de mantenimiento | P1 | QA/UV aprobado | 18 | 852 | 0 |
| N. Conexiones de servicio | P2 | Parcial | 109 | 4.399 | 4 |
| O. Props de mantenimiento | P2 | QA/UV aprobado | 68 | 1.678 | 0 |
| P. Set dressing de desastre | NO | Único / narrativo | 211 | 43.427 | 0 |
| Q. Set dressing de mantenimiento | NO | Único / narrativo | 7 | 42 | 0 |
| R. Props de gameplay de recepción | P2 | Blockout; sin UV | 65 | 1.994 | 65 |
| S. Props de almacén y taller | P3 | Blockout | 292 | 3.760 | 291 |
| T. Mobiliario y oficina | P3 | Blockout | 22 | 202 | 22 |
| U. Otros props locales | P3 | Blockout | 985 | 12.042 | 827 |

## 4. Qué se puede convertir en asset

### P0 — Reutilizar sin duplicar

Los 128 objetos visibles enlazados desde `NEXUS_SHARED_ASSETS.blend` ya son assets de biblioteca. No se deben re-exportar ni copiar al nivel. El trabajo pendiente es auditarlos:

- Revisar LOD y presupuesto de triángulos (hay piezas de 2.000–3.400 tris por objeto).
- Confirmar pivotes, escala y materiales.
- Añadir metadata y categoría si la librería aún no la tiene.
- Sustituir copias locales por instancias enlazadas cuando corresponda.

### P1 — Primer lote de assets locales del piloto

Conjunto formado por las familias B, C, D, E, F, G, H, I y M: **417 mallas, ~17.800 tris**, todas con UV y QA aprobado. Es el lote con mejor relación calidad/riesgo y el más reutilizable en laboratorios, minas, hospitales y complejos militares.

No se empaqueta malla por malla. Se empaqueta por familia:

- `KIT_Boiler` — cuerpo, cúpula, chimenea, puertas, bandas, válvulas, tuberías y remaches.
- `KIT_Genset` — cuerpo, skid, radiador, louvres, puerta de servicio, panel y escape.
- `KIT_PipeHeader` — tres líneas, codos, bridas, uniones oeste, pasamuros y soportes.
- `KIT_GasManifold` — panel, línea principal, válvula, manómetro, cabecera y pigtails.
- `KIT_AirReceiver` — depósito, bandas, base, manway y pernos.
- `KIT_EmergencyLight` — carcasa, lente, visera, rejilla y placa.
- `KIT_CableTray` — bandeja, brazos, brackets y tapas.
- `KIT_StructuralSteel` — columnas, vigas, anclajes y placas base.
- `KIT_MaintDoor` — hoja, jambas, rigidizadores, maneta, bisagras y umbral.

Cada kit debe salir con:

- Colección propia y jerarquía clara.
- Origen en el pivote/base correcto.
- Escala y rotación aplicadas.
- UVs y materiales PBR.
- LOD0/LOD1/LOD2 y colisión proxy.
- QA pasado con `qa_check.py`.
- Metadata: nombre, categoría, dimensiones, tris, materiales, variantes y estado.
- Miniatura y ficha de catálogo.

### P2 — Segundo lote

- **K/R. Props interactivos de recepción:** cajas de botín, maletín, muestras, escondite, trampa sonora, consola y botón de extracción. Son funcionales pero no tienen UV; necesitan UV/PBR y metadata de gameplay.
- **N. Conexiones de servicio:** puertas, jambas, señales, luminarias y conductos. Cuatro mallas sin UV; limpiar antes de extraer.
- **O. Props de mantenimiento:** banco, armario, taquilla, cajas, bidones y herramientas. Ya tienen QA/UV; se pueden empaquetar como kit de taller.
- **J. Soportes del piloto:** pequeños, pero útiles como variantes del kit de tuberías.

### P3 — No extraer todavía

- **L. Ascensor:** blockout de 376 tris; no tiene calidad suficiente para biblioteca final.
- **S, T, U:** almacén, oficina y props locales; la mayoría son cajas de seis caras sin UV. Se pueden usar como blockout, no como assets finales.
- **P, Q:** desastre y set dressing narrativo; son únicos de esta misión. No se convierten en assets.

## 5. Objetos movidos de su posición

La comparación contra el baseline detectó **138 objetos con desplazamiento mayor a 1 cm**. De ellos, **65 son visibles**; el resto son objetos ocultos u obsoletos.

### Corregido

- `NEXUS_V05_REC_EXTRACT_LIGHT` estaba en **(0, 0, 0)**. La consola, la pantalla, el botón, el indicador y el cartel de extracción se habían reubicado a recepción (y≈11,4), pero su luz se quedó en el origen. Se emparentó a `NEXUS_V05_REC_EXTRACT_CONSOLE` y quedó en **(-15,10; 11,325; -3,93)**, delante del conjunto. Guardado en el `.blend`.

### Verificar

- **Conjunto de extracción de recepción:** consola, pantalla, botón, indicador, cartel y zona se movieron entre **9,4 y 9,6 m** en Y, desde y≈1,95 hasta y≈11,4. Están en recepción, junto al ascensor. La reubicación parece intencional, pero conviene revisar que la consola no invada el hueco del ascensor ni quede fuera de la pared.
- **Área de descanso (`NEXUS_L1_DIS_BREAK_*`):** el conjunto completo se movió **1,8 m** en Y. Se movió en bloque, sin piezas sueltas; hay que confirmar si la nueva posición es la prevista.

### Cambios intencionales del pase de Mantenimiento

Aceite, baliza, carro volcado, cajas, puerta oeste, cartel, luces de emergencia, papeles, escombros, botiquín, hazard y señales se movieron durante el pase de arte/QA. No son errores y no se revierten.

### Objetos ocultos en el origen

Los rebuilds de caldera, generador y tuberías dejaron decenas de objetos antiguos ocultos con origen en (0,0,0). No son visibles, no se renderizan y no deben entrar en la biblioteca de assets. Se conservan como respaldo reversible.

El detalle completo está en `docs/fm_level1_moved_objects.csv`.

## 6. Formato de asset propuesto

Un asset no es una malla suelta. Debe ser una **colección empaquetada**:

```text
ASSET_Boiler_Industrial_A
├── Boiler_Body
├── Boiler_Dome
├── Boiler_Burner
├── Boiler_Pipes
├── Boiler_Valves
├── Boiler_Rivets
├── LOD1
├── LOD2
└── COLLISION
```

Con:

- Nombre de familia y variante.
- Pivote en la base y escala real.
- Materiales PBR con nombres estables.
- LODs y colisión proxy.
- QA aprobado.
- Metadata y miniatura.
- Estado: `WIP`, `blockout` o `aprobado`.

## 7. Siguiente paso

1. Aprobar el primer lote P1 (B, C, D, E, F, G, H, I, M) para extraerlo a una biblioteca de assets independiente.
2. Auditar los assets enlazados P0 y sustituir copias locales por instancias.
3. Corregir o confirmar la posición del conjunto de extracción y del área de descanso.
4. Dejar P2/P3 como inventario, sin extraerlos todavía.

Sin pruebas en Godot. Sin commit.

# NEXUS — archivos por nivel

Esta carpeta organiza el complejo sin alterar `FM_NEXUS_V05_level1_v125.blend`, que permanece como respaldo monolítico.

## Abrir el complejo

Abrir `master/NEXUS_MASTER.blend`. El máster enlaza los cinco niveles, el núcleo y el histórico; no contiene una segunda copia editable de toda la geometría.

## Editar

- `nivel_01/NEXUS_L1_V05.blend`: acceso y operaciones.
- `nivel_02/NEXUS_L2_V04.blend`: investigación y tecnología.
- `nivel_03/NEXUS_L3_MEDICAL.blend`: medicina.
- `nivel_04/NEXUS_L4_CONTAINMENT.blend`: seguridad y contención.
- `nivel_05/NEXUS_L5_INFRA.blend`: infraestructura profunda.
- `nucleo/NEXUS_CORE.blend`: torre, escaleras, ascensor y conexiones verticales.

Guardar el archivo del nivel modificado y volver a abrir el máster para recargar sus cambios.

## Recursos compartidos

- `compartido/NEXUS_SHARED_ASSETS.blend`: assets comunes y sus materiales. Nivel 1 los enlaza; editarlos aquí evita duplicar mallas y texturas.
- `compartido/NEXUS_HISTORICAL.blend`: geometría antigua, módulos ocultos y restos que no pertenecen a una banda activa. Se conserva para trazabilidad, no para reactivarlo indiscriminadamente.

No mover ni renombrar estas carpetas sin actualizar las rutas de las bibliotecas. No convertir los enlaces en copias locales salvo que exista una razón justificada.

## Reproducibilidad

`blender_concept/split_nexus_levels.py` genera esta estructura desde v125. No ejecutarlo sobre trabajos posteriores sin revisar antes sus rutas de salida: está diseñado para recrear los archivos generados, no para fusionar cambios nuevos.

`manifest.json` registra los recuentos, bibliotecas y comprobaciones de la generación.

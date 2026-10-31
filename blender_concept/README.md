# FRECUENCIA MUERTA — Reconstrucción del pasillo en Blender

Esta carpeta contiene una reconstrucción visual independiente del **pasillo existente**
del vertical slice de Godot. No se construyeron laboratorios, habitaciones nuevas ni
otras instalaciones.

## Archivos

| Archivo | Contenido |
|---|---|
| `FM_CORRIDOR_FINAL_v13.blend` | Escena final de Blender 5.2.3, motor EEVEE. |
| `build_corridor.py` | Script reproducible que genera la escena desde cero. |
| `renders/corridor_general.png` | Vista general del pasillo. |
| `renders/corridor_entrance.png` | Vista desde uno de los extremos. |
| `renders/corridor_security_door.png` | Puerta de seguridad, cartel y keypad. |
| `renders/corridor_detail.png` | Primer plano de tubería, abrazadera, rejilla y paneles. |
| `renders/corridor_cinematic.png` | Vista cinematográfica con niebla, luces y silueta. |
| `renders/contact_sheet.png` | Hoja de contacto de las cinco vistas. |

Los renders están a **1920 × 1080**, con 48 muestras EEVEE y gestión de color AgX.

## Elementos originales reconstruidos

- Corredor de **5,4 × 24 m** con suelo y techo, muros de hormigón y paneles metálicos.
- Costillas estructurales, vigas, zócalos, juntas, remaches y placas de anclaje.
- Ventanal de laboratorio oscuro con marco y vidrio tintado, sin construir el laboratorio.
- Puerta de seguridad doble con refuerzos, remaches, manijas, bisagras, franja hazard,
  barras roja y cian, keypad y cartel `SECTOR 04 / NEXUS // CONTENCIÓN`.
- Tuberías roja y oxidada, conductos, abrazaderas, bandeja de cables, cajas eléctricas,
  rejillas de ventilación y cámaras de seguridad.
- Fixtures cian de techo, luces de emergencia rojas, balizas de puerta, luces de trabajo y
  spots volumétricos.
- Señalización de pared: `BIO-LAB 04`, `ZONA CONTAMINADA`, `SALIDA DE EMERGENCIA`,
  `AUTORIZACIÓN NIVEL 3` y `RIESGO BIOLÓGICO`.
- Deterioro: panel de techo desprendido, cables colgando, óxido, escurrimientos, polvo,
  papeles, escombros, sangre y huellas.
- El Vigilante como silueta lejana de metaballs, con púas y boca vertical, situado a la
  izquierda de la puerta en la vista general y cinematográfica.

## Materiales y texturas

Se reutilizaron las texturas PBR del proyecto Godot (`assets/art/fm/`):

- Hormigón, metal pintado, suelo húmedo y óxido, con mapas de albedo, normal y roughness.
- Franjas hazard, sangre, rastro, huellas, suciedad, grieta de vidrio y charcos.
- Materiales emisivos para cian, rojo de emergencia, ámbar y verde biológico.
- Materiales procedurales para metales oscuros, goma, papel, hueso y agua.
- Las calcomanías usan UVs reales y blending dithered para conservar el alpha.

## Iluminación y atmósfera

- Key fría cenital, relleno azul, rebote de techo y contraluz de entrada.
- Fixtures cian en el techo y luces rojas de emergencia en las paredes.
- Spot frontal cálido sobre la puerta y luz azul de contraluz.
- Luz verde detrás del ventanal del laboratorio, sin crear la sala.
- Niebla volumétrica global, polvo y haces de luz.
- Exposición y contraste ajustados con AgX; no se usó Cycles porque no hay dispositivo
  GPU configurado en este Blender.

## Cámaras

| Cámara | Uso |
|---|---|
| `FM_Cam_General` | Vista general centrada. |
| `FM_Cam_Entrada` | Perspectiva desde el extremo de acceso. |
| `FM_Cam_Puerta` | Encuadre de la puerta y su cartel. |
| `FM_Cam_Detalle` | Primer plano de tubería, abrazadera y rejilla. |
| `FM_Cam_Cine` | Composición baja con niebla y silueta. |

## Limitaciones honestas

- Es una **reconstrucción visual**, no un nivel jugable: no tiene colisiones, navegación,
  interactividad ni red.
- La geometría es procedural y modular; no sustituye el arte final modelado a mano.
- El Vigilante es una **silueta provisional** de metaballs, no el modelo definitivo ni un
  rig animado; en la cámara de la puerta se oculta para no tapar el encuadre.
- Los carteles se generan con texto 3D; en una producción final convendría tipografía
  dedicada y texturas de señalización.
- La iluminación y los materiales están pensados para EEVEE; una versión con Cycles y
  texturas 4K requeriría otra pasada.
- No se modificó el proyecto Godot, `AGENTS.md` ni `fotos-referencia/`.

## Reproducir

Abrir `FM_CORRIDOR_FINAL_v13.blend` en Blender 5.2.3 o ejecutar `build_corridor.py`
desde Blender MCP. El script crea una escena nueva y guarda una variante sin sobrescribir
los `.blend` existentes.

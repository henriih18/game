# FRECUENCIA MUERTA — Checkpoint de Seguridad R2 (hero)

## Estado

Benchmark hard-surface jugable/visual construido en la colección **`L1_SECURITY_R2_HERO`**.
Archivo: `nexus/nivel_01/FM_LEVEL1_V06_ARCH.blend` (escena `NEXUS_L1_V06_ARCH`).
Ubicación: entrada de Seguridad 03, centrado en `x=-89`, `y≈12.6/13.9`, suelo `z=0`.

- 158 mallas, **69.520 tris** evaluados (sin LOD).
- El blockout antiguo `L1_SECURITY_R2` **no se ha borrado**: sus 25 mallas están ocultas en render y viewport. La luz de emergencia existente sigue activa.
- No se tocaron arquitectura, `L1_SECURITY_R1`, recepción, `L1_KIT_PILOT` ni las imágenes de `fotos-referencia/`.

## Contenido

- **Mostrador de pie**: tapa con bevel de 4 segmentos, esquina rota con interior de acero visto, cuerpo con tres paneles aplicados, largueros, tapas laterales, tornillos hexagonales, zócalo hundido, pasacables de goma, bandeja de cables, guías y cables.
- **Monitor muerto**: carcasa, bezel, pantalla negra recessed, cuello/base, bisagra, rejillas booleanas, tapa de servicio, VESA, botones y cable hasta el pasacables.
- **Teclado**: cuerpo en cuña, 60 teclas individuales con bevel, cable.
- **Lector de tarjetas**: pedestal cónico con base, collar, tapa, carcasa, marco, ranura, keypad de 12 teclas, LED rojo, barra de luz ámbar, cable, pasacables y registro de servicio.
- **Barrera**: dos postes (uno doblado), bases de goma y placa, collares, cabezales retráctiles con anillos, cinta roja con caída y torsión, hebilla/tensor y clip final.
- **Cartel SEGURIDAD**: placa texturizada `assets/art/fm/generated/rec_seguridad.png`, legible y no espejada, marco metálico y 4 separadores al panel trasero.
- **Caos no narrativo**: panel de techo caído con parrilla metálica, chapa doblada, pantalla secundaria rota, cables arrancados con hilos de cobre, agua, escombros de hormigón y restos metálicos. Sin sangre, cuerpos, documentos ni objetos personales.

Materiales PBR procedurales diferenciados (pintura, acero oscuro, acero desnudo, aluminio, goma, plástico, pantalla, hormigón, yeso, agua, cinta, cobre, LED). UVs en todas las mallas; el cartel usa UVs explícitas para conservar la orientación de la textura.

## QA

`blender-asset-qa/qa_check.py`, perfil `game`. Para evitar falsos positivos de precisión float32 en piezas pequeñas lejos del origen, la geometría se comprobó sobre una copia temporal desplazada al origen; incluye el suelo `SM_L1_Zone03_Security_Floor` para contacto.

- **PASS: 0 errores, 0 z-fighting, 0 piezas flotantes.**
- UV: 0 mallas sin UV, 0 caras UV de área cero.
- Warnings aceptados (53):
  - 26 × vértices duplicados en piezas unidas/curvas (no afectan render; mid-poly).
  - 20 × caras ocultas back-to-back en uniones atornilladas/solapadas intencionadas.
  - 6 × n-gons en tapas de cilindros y esquinas de bevel (caras planas, no deformables).
  - 1 × aviso de `ground_z` provocado por el desplazamiento temporal de la copia de QA.
  - 1 × solape UV del 9,6 % en el cable coiled del intercomunicador (aceptado).
- `qa_check` ejecutado en coordenadas reales puede marcar “inside-out” en tornillos diminutos por precisión numérica; no son errores de malla (desaparecen al trasladar al origen).

## Renders de revisión

Iluminación y suelo de revisión temporales; no se guardaron en el .blend.

- `docs/fm_security_checkpoint_hero_closeup.png` — 3/4 con lector, barrera, mostrador, monitor y cartel.
- `docs/fm_security_checkpoint_hero_desk_detail.png` — detalle de mostrador, monitor, teclado, intercom y esquina rota.
- `docs/fm_security_checkpoint_hero_reader_barrier.png` — lector, barrera y panel caído.
- `docs/fm_security_checkpoint_hero_front.png` — vista frontal.
- `docs/fm_security_checkpoint_hero_silhouette.png` — silueta 3/4.
- `docs/fm_security_checkpoint_hero_silhouette_side.png` — perfil lateral.

## Limitaciones

- Sin LOD, collision mesh, navegación ni pruebas de rendimiento con jugadores/criaturas.
- Materiales procedurales: para exportación a motor hace falta hornear sets PBR y revisar el coste de draw calls.
- El suelo original de Seguridad 03 es todavía el material de blockout; los renders usan un suelo neutro temporal.
- La iluminación guardada sigue siendo la de lookdev (luces de techo apagadas + emergencia roja). El checkpoint se ve oscuro si se abre sin luces de revisión.
- El daño del mostrador es una esquina rota + desgaste; no se ha deformado toda la chapa.
- El blockout R2 sigue en el archivo, oculto; se puede reactivar para comparar.

## Siguiente paso

Integrar el checkpoint como pieza definitiva de Seguridad 03: collider/oclusión, puntos de interacción, eventos sonoros (cajón, cables, barrera), LOD y bake de materiales; después sustituir el suelo y la iluminación de blockout por el look final de la zona.

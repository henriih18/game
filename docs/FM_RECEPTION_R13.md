# FM — Recepción R13: taquillas y señalización hero

## Alcance

Sustitución del banco de taquillas blockout y de los tres carteles planos de Recepción por un conjunto hero:

- `L1_RECEPTION_R13_HERO`
- `REC13_LOCKERS_HERO`
- `REC13_SIGN_LOCKERS`
- `REC13_SIGN_DECON`
- `REC13_SIGN_DESK`

No se modificó la arquitectura, el recorrido de extracción ni los clústeres R6/R7/R8/R9/R10/R11/R12. Sin commit.

## Taquillas

- Banco de **6 puertas**, 2,40 m de ancho × 0,48 m de fondo × 1,90 m de alto.
- Carcasa con laterales, techo, base, zócalo, divisiones y estantes.
- Puertas con rejillas de ventilación, portaetiquetas, tiradores, cerraduras de latón, tres bisagras y tornillos.
- Anclajes a muro y top trim metálico.
- `REC13_LOCKERS_HERO`: **21.488 tris / 11.000 verts**.
- 0 non-manifold, 0 degenerados, UV.

## Señalización

- `REC13_SIGN_LOCKERS`: 2,40 × 0,32 m, montado sobre el banco; **1.576 tris**.
- `REC13_SIGN_DECON`: 3,00 × 0,28 m, sobre la viga de decontaminación; **1.576 tris**.
- `REC13_SIGN_DESK`: 3,00 × 0,40 m, colgado bajo el soffit del mostrador; **1.352 tris**.
- Marcos metálicos, panel claro, franja verde, icono de barras, soportes/varillas y pernos.
- Total R13: **25.992 tris**.

## QA y archivos

- QA: `docs/fm_reception_r13_lockers_qa.json`; **qa_pass=true**.
- Backup: `docs/backups/FM_LEVEL1_V06_ARCH_before_reception_r13_lockers.blend`.
- Script: `scripts/fm/fm_rec13_lockers.py`.
- 38 objetos blockout retirados a `L1_RECEPTION_RETIRED`: 35 `PROP_REC02_Locker_*` y 3 `KIT_REC02_Sign_*`.

## Materiales

- `M_REC13_PaintedGreen`: base `srgb(42,60,50)`, roughness 0,56, `scale=10`, `bump=0.0002`, `micro=700`, `rough_var=0.03`. Se suavizó tras el primer close-up, que parecía piedra/hormigón.
- `M_REC13_SignPanel`: `srgb(178,184,168)`, roughness 0,55, `scale=40`, `bump=0.0003`, `micro=500`.
- `M_REC13_SteelDark`, `M_REC13_Steel`, `M_REC13_Label`, `M_REC13_Brass`, `M_REC13_Black`, `M_REC13_SignFrame`, `M_REC13_SignGreen`.

## Renders

Script: `scripts/fm/fm_rec13_render.py`.

- `docs/fm_rec13_lockers_wide.png`: banco completo, cartel `TAQUILLAS`, proporciones y anclajes.
- `docs/fm_rec13_lockers_threequarter.png`: seis puertas, rejillas, etiquetas, tiradores, cerraduras y bisagras.
- `docs/fm_rec13_lockers_door.png`: close-up de puertas; la pintura ya no parece piedra, el ruido es sutil.
- `docs/fm_rec13_sign_lockers.png`: cartel sobre el banco.
- `docs/fm_rec13_sign_desk.png`: cartel `RECEPCIÓN` visible desde el sur.
- `docs/fm_rec13_sign_decon.png`: cartel claro sobre la viga negra de decontaminación.

## Limitaciones

- El texto de los carteles proviene de rótulos/labels existentes superpuestos; no se modeló tipografía nueva. En la señal de decontaminación el panel es principalmente icónico (barras), no texto legible.
- Los carteles son de la capa de señalización base; la iluminación propia, el desgaste y la gráfica final pertenecen a la pasada de texturas/narrativa.
- El fondo de la sala sigue en blockout (muros claros, suelo azul).
- No hay LOD, colisiones propias ni export/Godot de R13.
- El close-up de puerta sigue mostrando una leve variación de pintura; es aceptable para la distancia de juego.

## Siguiente

1. LOD/optimización global de Recepción.
2. Colisiones/proxies de R13 si se van a usar en gameplay.
3. Z10 feeds/S-10..S-15.
4. Texturas/bake, desgaste fino y narrativa al final.

Sin commit.

# FRECUENCIA MUERTA — Centro de operaciones de Seguridad 03 (R2.1a, hero)

## Estado

Construido en la colección nueva **`L1_SECURITY_R21A_HERO`**.
Archivo: `nexus/nivel_01/FM_LEVEL1_V06_ARCH.blend` (escena `NEXUS_L1_V06_ARCH`).
Zona: centro/norte de Seguridad 03, aprovechando el muro norte y las columnas; el
checkpoint sur y las puertas quedan libres.

- **69 mallas, 207.602 tris evaluados, 107.654 vértices, 34 materiales.**
- 6 luces de práctica + 1 cámara guardada (`CAM_SECURITY_OPS_HERO`) en la colección.
- Extents reales: `x −90,72 … −71,12`, `y 25,75 … 35,88`, `z −0,02 … 4,78`.
- Subcolecciones: `L1_SECURITY_R21A_WORKSTATIONS`, `_CCTV`, `_RACK`, `_CHAOS`,
  `_FIXTURES`, `_LIGHTS`.

No se tocaron `L1_SECURITY_R2_HERO` (158 mallas, intacto), `L1_SECURITY_R1`, el shell,
recepción, Z10, `L1_ARCH_*` ni `fotos-referencia/`. El suelo de Seguridad 03 conserva su
material original `M_L1_Zone_Security.010` en el .blend guardado.

## Contenido

### Puestos de operador (3)

- Escritorios de 2,10 × 0,85 × 0,78 m con tapa de laminado biselada (4 segmentos), canto
  de goma, estructura de acero, paneles laterales con insets atornillados, panel trasero
  con rejilla, bandeja portacables, pasacables de goma y armazón de escritorio.
- 6 monitores de 27" con carcasa, bisel, pantalla hundida, rejillas, botones, VESA,
  cableado y UI emisiva tenue. Dos pantallas muertas utilizan material propio
  `M_HERO_Ops_ScreenDead`; una muestra el patrón de pantalla rota existente.
- Teclados de 60 teclas con keycaps biselados, ratones y alfombrillas.
- Radio transceptora con rejilla, LCD, mandos, antena, auricular y cable en espiral;
  teléfono/intercom con teclado y cable; consola PTZ con joystick y LCD.
- Torres de PC bajo dos escritorios.
- Sillas de operador con base de 5 patas, ruedas, pistón, mecanismo, asiento, respaldo,
  reposacabezas, brazos y palanca; dos erguidas y una **volcada** sobre el suelo.

### Muro CCTV

- Muro de 9 pantallas 3×3 sobre el muro norte, con estructura de raíles, anclajes,
  soportes, biseles, rejillas, pantallas vivas/muertas/rotas, UI, cables colgando y
  bandejas de cables con varillas y tuercas.
- Cartel físico `CENTRO DE VIGILANCIA` y placas de cámara (sin texto flotante).
- Bandeja superior de cableado que recorre el muro y baja hasta el rack.

### Rack de servidores / UPS

- Armario de 2,00 m con puerta perforada de lamas, bisagras, manilla, cerradura,
  laterales ventilados, patas, ventiladores superiores, panel trasero y entrada de cables.
- Interior con UPS, patch panel de 24 puertos, 11 unidades 1U/2U, raíles de montaje,
  LEDs, rejillas, etiquetas y una unidad extraída.
- Etiquetas de placa y cableado de parcheo; cables hacia la bandeja superior.
- Panel de distribución/breaker en el muro norte entre CCTV y rack, con filas de
  interruptores, LEDs, rejillas, conductos y etiqueta.

### Caos no narrativo

- Monitor caído con pantalla rota, base y cuello deformados, junto a la silla volcada.
- Panel de techo caído con rejilla, luminaria muerta y cables colgando hasta el techo.
- Escombros de hormigón, chapa oxidada, cristales, cables por el suelo, carrete de cable,
  charcos y acumulaciones de polvo.
- Sin cuerpos, sangre, documentos, notas, fotos ni objetos personales.

### Iluminación

- Prácticas finales escasas: dos emergencias rojas de pared y cuatro derrames fríos de
  monitor/CCTV de baja energía. La sala permanece oscura, coherente con el estándar del
  piloto (sin luz general; la recepción sigue siendo la única zona iluminada).
- Los renders de revisión usan luz temporal y un suelo neutro temporal; **no** se guardan
  en el .blend.

## Materiales

34 materiales PBR procedurales, entre ellos: laminado, pintura óleo, carcasa de silla,
tela, keycaps, pantallas (muerta/viva/scan/UI), LEDs fríos/ámbar, cable azul, goma,
aluminio, acero oscuro/desnudo/oxidado, galvanizado, hormigón, yeso, agua, polvo y
etiquetas. Bevels de 3–4 segmentos en formas principales, panel lines, tornillos,
remaches, Weighted Normal y UVs de proyección de caja.

## QA

`blender-asset-qa/scripts/qa_check.py` sobre `L1_SECURITY_R21A_HERO` + suelo de
Seguridad 03, en una **copia temporal con la geometría desplazada al origen** para evitar
falsos positivos de precisión float en piezas pequeñas lejanas.

Resultado formal (perfil **`render`**, `eps=0.0005`, `uv=True`):

- **PASS: 0 errores.**
- 0 z-fighting.
- 0 piezas flotantes/desconectadas.
- 0 mallas sin UV; 0 caras UV de área cero.
- 112 warnings, principalmente: 60 solapes UV de proyección de caja (materiales
  procedurales, no se hornea), 27 avisos de islas cerradas con volumen negativo (piezas
  diminutas; falso positivo del test de volumen firmado, sin artefacto visible), uniones
  back-to-back ocultas, 2 vértices duplicados, y avisos del suelo existente (sin UV y
  `ground_z`).

Perfil **`game`**, `eps=0.0005`: **0 z-fighting, 0 flotantes, 0 errores UV**; quedan 27
avisos/errores de “closed parts with normals pointing inward” en tornillos, LEDs y
pequeños cierres. El mismo test sobre coordenadas reales multiplica esos avisos, lo que
confirma su carácter numérico; los renders no muestran caras invertidas. No se declara
PASS en perfil game por esa métrica, y se documenta como limitación de QA.

## Renders

Iluminación y suelo temporales; el suelo del .blend guardado es el original.

- `docs/fm_security_ops_hero_closeup.png` — puesto A, monitores, teclado, PTZ, teléfono,
  radio, silla y contexto CCTV.
- `docs/fm_security_ops_hero_three_quarter.png` — vista 3/4 del centro: muro CCTV,
  tres puestos, sillas, rack, breaker, cableado y caos.
- `docs/fm_security_ops_hero_wide.png` — vista amplia de la sala con el checkpoint
  `SEGURIDAD` en primer plano y el centro de operaciones al fondo.

## Limitaciones

- Sin LOD, colliders de juego, navegación, sonido, interacción ni sincronización de red.
- Las pantallas son UI emisiva estática; no hay feeds de cámara animados.
- Materiales procedurales: para exportar a motor hay que hornear sets PBR y revisar
  draw calls.
- Teclados y sillas son mid-poly; el microdetalle es menor que el del checkpoint hero,
  aunque el conjunto mantiene el estándar visual.
- El suelo original de Seguridad 03 sigue siendo el material de blockout; los renders
  usan un suelo neutro temporal.
- No se han medido FPS con jugadores, criaturas, físicas o multijugador.
- El QA game queda condicionado por el test de volumen firmado en piezas diminutas.

## Siguiente paso

Integrar el centro como zona jugable: colliders/oclusión, puntos de interacción
(monitores, rack, breaker, radio de columna), eventos sonoros y de luz, LOD de los
monitores/rack, bake de materiales y pruebas de rendimiento con el jugador y El Vigilante.
Después, conectar la iluminación de emergencia y las pantallas a los eventos de la
instalación y a la sincronización multijugador.

## Skills y archivos

Skills aplicadas: `blender-core`, `blender-hardsurface-modeling`, `blender-pbr-materials`,
`blender-asset-qa`.

Scripts reproducibles:

- `nexus/nivel_01/scripts/fm_ops_lib.py`
- `nexus/nivel_01/scripts/fm_ops_workstations.py`
- `nexus/nivel_01/scripts/fm_ops_cctv.py`
- `nexus/nivel_01/scripts/fm_ops_rack.py`
- `nexus/nivel_01/scripts/fm_ops_chaos.py`
- `nexus/nivel_01/scripts/fm_ops_build.py`
- `nexus/nivel_01/scripts/fm_ops_render.py`

Sin commit.

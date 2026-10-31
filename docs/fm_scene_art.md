# FRECUENCIA MUERTA — Arte integrado del escenario

Estado: **corredor artístico integrado en el vertical slice jugable**. No es un
render aislado ni un nivel aparte: el jugador recorre ese corredor con la cámara en
primera persona, la linterna, el Vigilante, la puerta y la extracción.

## Capturas

| Vista | Archivo |
|---|---|
| Corredor jugable | `docs/fm_scene_corridor.png` |
| Laboratorio jugable | `docs/fm_scene_lab.png` |

## Qué se integró

- **Corredor**: arte reconstruido en Blender y exportado como
  `assets/models/fm/corridor_art.glb` (381 mallas, texturas embebidas).
- **Arquitectura**: paneles metálicos, hormigón, costillas, vigas, juntas,
  zócalos, techo técnico, bandejas de cables y tuberías.
- **Iluminación**: fixtures cian, luces de emergencia rojas, apliques tenues y
  niebla volumétrica. Las luces reales siguen siendo nodos de Godot; el GLB aporta
  las luminarias y materiales emisivos.
- **Deterioro**: óxido, escurrimientos, panel de techo desprendido, cables,
  escombros, papeles, sangre, huellas y charcos.
- **Puerta**: el GLB se recortó antes de la puerta para conservar la puerta
  interactiva de Godot (keypad, apertura, colisión y ruido).
- **Laboratorio**: sigue construido en Godot, con tanque de contención, Imitador,
  consola, camilla, batería, núcleo y luces propias.

## Cómo está montado

- `scripts/fm/vertical_slice.gd` crea un `CorridorBlockout` con las colisiones del
  corredor y lo oculta visualmente.
- El GLB se instancia como `CorridorArt` bajo `Level`.
- `corridor_shell.visible = false` oculta el blockout, pero **no desactiva** sus
  colisiones.
- `FMScenarioDressing.build(..., false)` omite el decorado procedural duplicado del
  corredor; conserva laboratorio, extracción y atmósfera.
- La lógica, la red host-autoritativa, la puerta, las baterías, la trampa, el
  núcleo, el Vigilante y la extracción no se reescribieron.

## Archivos

| Archivo | Uso |
|---|---|
| `assets/models/fm/corridor_art.glb` | Arte del corredor |
| `blender_concept/FM_CORRIDOR_FINAL_v14.blend` | Escena Blender recortada |
| `blender_concept/build_corridor.py` | Script reproducible |
| `scripts/fm/vertical_slice.gd` | Integración y juego |
| `scripts/fm/fm_scenario_dressing.gd` | Decorado restante |
| `docs/fm_scene_corridor.png` | Captura del corredor |
| `docs/fm_scene_lab.png` | Captura del laboratorio |

## Cómo probarlo

```bash
godot --path ~/Documentos/game -- --slice
```

También desde el menú: **ENTRAR A LA INSTALACIÓN**. Para la versión online, el host
usa **CREAR PARTIDA 3D (HOST)** y el cliente **UNIRSE 3D**.

## Verificación

- `bash tests/run_all.sh`: EXIT 0.
- Vertical slice: **26/26 PASS**.
- Juego 2D: **16/16 PASS**.
- Red 2D: **6/6 PASS**.
- Red 3D: **15/15 PASS**.
- Importación de Godot sin errores de script.

## Limitaciones honestas

- El arte del corredor es una reconstrucción procedural desde Blender, no un kit
  modular modelado a mano ni arte final de producción.
- El laboratorio, la puerta y la extracción conservan geometría procedural de
  Godot; el laboratorio está iluminado y es legible, pero no tiene el mismo nivel de
  detalle que el corredor.
- El GLB no incluye colisiones, navegación, interactividad ni red; esa capa sigue
  en Godot.
- Las criaturas siguen siendo bloqueos orgánicos procedurales.
- No se ha medido el rendimiento de la escena completa con 4 jugadores, IA y red.
- `fotos-referencia/` y `AGENTS.md` no se modificaron.

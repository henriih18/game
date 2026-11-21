# FRECUENCIA MUERTA — Oficinas / Administración (Z08)

Checkpoint de vestido de la sala `SM_L1_Zone08_Offices` del Nivel 1.
Fecha: 2026-11-15. Rama `frecuencia-muerta`, HEAD `287b101`. Sin commit.

## Alcance

Se ha vestido la sala de Oficinas / Administración con identidad corporativa
NEXUS: moqueta verde-teal, mamparas de vidrio, oficinas privadas, sala de
reuniones, archivo técnico, cafetería y un corredor administrativo de acceso.
No se han añadido armas ni sistemas de combate. El blockout y la navegación
existentes se conservan; la puerta sur y la puerta este quedan libres.

## Composición

- **Recepción / lobby**: mostrador con monitor, teléfono, papeles y sillas;
  zona de espera con asientos, mesa baja, alfombra, planta, reloj y directorio;
  ascensor decorativo y rótulo NEXUS.
- **Open office**: 12 puestos en tres filas, con escritorios, pedestales,
  monitores, teclados, teléfonos, lámparas y papeles; mamparas bajas de tela,
  archivadores, copiadora y plantas.
- **Cuatro oficinas privadas**: tabiques, frente de vidrio con puerta abierta,
  escritorio de 2,0 m, silla de dirección, dos sillas de invitado, credenza,
  archivador, alfombra, planta y rótulos GERENCIA / OPERACIONES / RRHH /
  DIRECCIÓN.
- **Sala de reuniones**: cerramiento de vidrio, mesa de 3,2 m con ocho sillas,
  pizarra blanca, pantalla, credenza, jarra y vasos, alfombra y planta.
- **Archivo / servidores**: cerramiento con puerta, estanterías de archivo,
  cajas, archivadores de cuatro cajones, cuatro racks de servidores, SAI,
  climatización y reloj; iluminación fría.
- **Cafetería**: encimera con fregadero, cafetera, microondas, nevera, fuente
  de agua y armarios; máquina expendedora, dos mesas redondas con sillas,
  reciclaje y fregona.
- **Corredor administrativo sur** (x −14..−6): alfombra corrida, panelado,
  bancos, plantas, seis luminarias lineales, tablón, plan de evacuación,
  extintor, reloj, cajas abandonadas y rastro sutil de sangre.
- **Techo y suelo**: bandejas de cables, conducto con difusores, rociadores,
  detectores, luminarias; zócalos, líneas de seguridad, flechas de evacuación,
  alfombras de zona, papeles y tazas.
- **Narrativa**: evacuación interrumpida, sillas desplazadas, papeles y tazas
  caídos, monitor apagado, cajas en el corredor y un rastro de sangre hacia el
  este. Horror ambiental sin violencia explícita.

## Archivos

| Archivo | Función |
|---|---|
| `scripts/fm/fm_offices_build.py` | Build idempotente de `L1_ART_OFFICES`. |
| `scripts/fm/fm_offices_export_headless.py` | Export GLB validado (262 objetos, sin luces/cámaras). |
| `assets/models/fm/offices_art.glb` | Arte exportado. |
| `scenes/fm/fm_blockout_offices_art.tscn` | Escena de sala: blockout + arte + 25 luces. |
| `tests/fm_level1_v06_offices_shots.gd/.tscn` | Capturas de revisión (11 vistas). |
| `docs/fm_offices_art_export.json` | Reporte del export. |
| `docs/backups/FM_LEVEL1_V06_ARCH_before_offices_art_2026-11-15.blend` | Backup previo. |
| `docs/backups/FM_LEVEL1_V06_ARCH_after_offices_art_2026-11-15.blend` | Backup de checkpoint. |
| `docs/backups/FM_OFFICES_ART_checkpoint_2026-11-15.glb` | Copia del GLB de checkpoint. |

## Datos técnicos

- Build Blender: **262 objetos**, 180.922 tris.
- GLB: **9.717.668 bytes**, **260 mallas / 262 nodos**, 32 materiales,
  16 imágenes, **178.810 tris**, 0 cámaras, 0 luces.
- AABB Blender: min (−29.941, 4.2, 0.0), max (14.805, 70.0, 4.5), dentro de
  `OFFICES_BOUNDS`.
- Escena Godot: **292 mallas**, **167 colliders**, **25 luces** (Emerg_Offices +
  24 luces de sala), todas sin sombras.
- El suelo, muros, columnas y techo proceden del blockout; el arte añade
  mobiliario, tabiques, vidrio y decoración.

## QA

`blender-asset-qa` sobre el subset de 283 objetos (262 de arte + 21 mallas del
shell Zone08 / columnas / conector, sin puertas ni techo, excluyendo solo
`SM_L1_Zone08_Offices_Wall_W_0a` por un defecto preexistente del shell):
**PASS, 0 errores**, 154 warnings aceptados (UVs de textos y papeles, winding
en cilindros). Se corrigieron z-fighting en sillas/alfombras, escritorios,
credenzas, marcos, cafetera, fregadero y bandejas; y flotantes en mesas,
archivadores, conducto y servicios de techo.

Durante el export se detectó que `OF_Bin_01` heredaba `hide_viewport=True` de
su prop de origen. Se corrigió `copy_prop()` en `fm_warehouse_build.py` para
forzar `hide_viewport=False`, lo que beneficia a futuras salas.

## Pruebas

| Prueba | Resultado |
|---|---|
| `fm_level1_v06_smoke` | **403 PASS / 0 FAIL** (Offices: 292 mallas, 167 colliders). |
| `fm_level1_v06_gameplay` | **105 PASS / 0 FAIL**. |
| `fm_full_run` | **49 PASS / 0 FAIL**. |
| `fm_graphics_presets_smoke` | **194 PASS / 0 FAIL**. |
| `fm_level1_v06_perf` (1280×720, ventana) | **PASS**: 232,0 fps promedio, mínimo 55,0, p1 79,7; 4,96 M tris, 127 luces, 1.428 draws máx., 886,9 MB texturas. |
| Capturas | 11 vistas en `/tmp/opencode/of_godot_*.png`. |

## Limitaciones conocidas

- La recepción y el fondo del open office quedan deliberadamente oscuros; la
  lectura mejora con la linterna. Es coherente con el tono de terror, pero se
  puede subir la exposición local si se desea una oficina más "funcional".
- La oficina privada se ve desde el vano y parte del escritorio queda en
  penumbra; se ha movido la luz al fondo para que escritorio y credenza se
  lean.
- La puerta este muestra el corredor de escaleras con poca información visual;
  el marco y la salida son reconocibles.
- Quedan pequeños paneles oscuros vistos de canto (backplates de señalización
  o ductos en penumbra) en algunas paredes; no afectan a la navegación.

## Skills utilizadas

`blender-core`, `blender-hardsurface-modeling`, `blender-pbr-materials`,
`blender-lighting-lookdev`, `blender-asset-qa`, `blender-texturing`,
`blender-scene-setup`, `blender-game-optimization`,
`blender-export-pipelines`. No se usaron `blender-rendering` ni
`blender-texture-baking`: las capturas se hicieron en Godot y los materiales
reutilizan sets PBR existentes.

## Siguiente sala

**Aseo de planta (Z09)**. Mantener el flujo: backup previo, diagnóstico del
shell, colección `L1_ART_RESTROOM`, QA hasta 0 errores, GLB validado, escena
ampliada in situ, smoke/pruebas/perf/capturas, documentación y checkpoint sin
commit.

# FRECUENCIA MUERTA — El Coleccionista (estado de trabajo)

Fecha: 2026-11-16 · Rama `frecuencia-muerta` · HEAD `287b101` · sin commit

## Estado

Modelo esculpido del Coleccionista generado en Blender con pipeline headless.
El cuerpo ya es una superficie continua (esqueleto + Skin + Subsurf + Remesh
VOXEL + Smooth + Displace), con bake de normal/AO y equipo de saqueador.

- `body_tris = 42.000`
- `total_tris = 59.544`
- GLB: `assets/models/fm/collector_creature.glb` (3,5 MB)
- .blend: `nexus/nivel_01/FM_COLLECTOR_SCULPT.blend` (2,9 MB)
- Render de revisión: `/tmp/opencode/collector_sculpt.png`
- Script: `scripts/fm/fm_collector_sculpt.py`
- Backup: `docs/backups/FM_COLLECTOR_SCULPT_2026-11-16/`
  (blend, GLB, script y render)

## Contenido actual

- Cuerpo orgánico continuo, joroba y brazos largos.
- Máscara de gas con goggles ámbar y respirador.
- Capucha, abrigo acampanado, mangas y pantalones oscuros.
- Guantes, botas, mochila/rollo, correas, cinturón, llaves y farol.
- Piel oscura, material PBR con normal horneado.

## Pendiente inmediato

1. Revisar el render final: el abrigo acampanado debe cubrir el torso y
   mejorar la silueta de saqueador.
2. Si convence, QA de malla/texturas (`blender-asset-qa`) y ajuste de
   proporciones finales.
3. Integrar el GLB esculpido en `scripts/fm/fm_creature_models.gd` /
   escena, sustituyendo el modelo procedural del Coleccionista.
4. Implementar `scripts/fm/fm_collector.gd`:
   - estados DORMANT / PATROL / INVESTIGATE / CHASE / STEAL / RETURN;
   - percepción y navegación reutilizando `FMWatcher`;
   - robo de `FMCarryItem` y punto de acopio;
   - prioridad a jugadores que transportan botín;
   - reacción a ruido.
5. Pruebas de comportamiento y documentación. Sin commit hasta autorización.

## Actualización 2026-11-17 (pase manual guardado)

Se aplicó y guardó un pase manual de escultura sobre el .blend:

- Joroba y desplazamiento del torso hacia delante, cintura estrechada y
  hombros ensanchados.
- Arrugas radiales y verticales en abrigo, capa, capucha y jirones.
- Ribete de capucha, filtro y tapa del filtro de la máscara.
- Cobertura de torso (`Collector_ChestWrap`, `Collector_ShoulderCloak`),
  guantes, punteras de bota y `Collector_Undersuit` duplicado del cuerpo a
  escala 1.018 con tela oscura.
- Piel oscurecida y cámara de revisión en 3/4.

Render más reciente: `/tmp/opencode/collector_manual3.png`.
El modelo está guardado, pero **sigue leyéndose como un traje acolchado** y
no alcanza el realismo de `fotos-referencia/modelos-referencia.png`. No se
considera terminado ni listo para integrar.

Siguiente decisión: sesión de escultura real en la GUI (brocha/arcilla,
retopología y bake) o pausar la criatura y avanzar en gameplay con un
placeholder. Sin commit.

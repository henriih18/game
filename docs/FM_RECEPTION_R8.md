# FM — Recepción R8: cola y barrera hero

Fecha: 2026-11-09
Colección: `L1_RECEPTION_R8_HERO`
Script: `scripts/fm/fm_rec08_queue.py`
Backup previo: `docs/backups/FM_LEVEL1_V06_ARCH_before_rec08.blend`

## Alcance

Sustituye la cola y la barrera blockout de `L1_RECEPTION_R2` por dos clústeres
hero reutilizables:

- **Cola en U**: 4 stanchions con base de disco, poste cónico, casetes
  retráctiles, discos laterales, tornillos, banda naranja y pomo de tensión.
  Las esquinas A/D llevan **dos casetes** a alturas distintas (0,90 y 0,84 m)
  para que las cintas no se crucen.
- **3 cintas** de 3 m / 3 m / 3 m con sección vertical de 50 mm, ligera
  catenaria y extremos retraídos dentro del casete.
- **Barrera retráctil** junto al puesto de seguridad: poste con base y casete
  en x=-86,25, cinta de 2 m y receptor de pie en x=-84,25.

## Conteos

| Objeto | Tris | Vértices |
|---|---:|---:|
| `REC08_STANCHION_A` | 13.820 | 7.376 |
| `REC08_STANCHION_B` | 10.972 | 5.864 |
| `REC08_STANCHION_C` | 10.972 | 5.864 |
| `REC08_STANCHION_D` | 13.820 | 7.376 |
| `REC08_BELT_A` | 228 | 116 |
| `REC08_BELT_B` | 228 | 116 |
| `REC08_BELT_C` | 228 | 116 |
| `REC08_BARRIER_POST` | 10.972 | 5.864 |
| `REC08_BARRIER_RECEIVER` | 4.564 | 2.440 |
| `REC08_BARRIER_BELT` | 228 | 116 |
| **Total** | **66.032** | **35.248** |

BBox: `[-89,1579, -13,6579, 0,0] .. [-84,1301, -9,5921, 0,971]`.

## QA

`docs/fm_rec08_queue_qa.json`: **10 objetos, 66.032 tris, 35.248 vértices**;
**0 non-manifold, 0 degenerados, UV presente** en los 10 objetos. Las 13 piezas
viejas (`PROP_REC02_Barrier_*`, `PROP_REC02_Belt_*`,
`PROP_REC02_Stanchion*`) quedan en `L1_RECEPTION_RETIRED`, ocultas.

## Renders

| Imagen | Contenido |
|---|---|
| `docs/fm_rec08_queue_wide.png` | Cola completa, cartel RECEPCIÓN, puerta y desk de seguridad; cintas negras y bases. |
| `docs/fm_rec08_queue_threequarter.png` | 3/4 desde el sureste: U completa, cintas, casetes y desk a la derecha. |
| `docs/fm_rec08_queue_stanchion.png` | Close-up del stanchion de esquina: dos casetes a distinta altura, discos, pomos y banda naranja. |
| `docs/fm_rec08_queue_barrier.png` | Barrera retráctil y receptor junto al desk de seguridad. |
| `docs/fm_rec08_queue_detail.png` | Detalle de casetes apilados y salida de cintas. |

Script de render: `scripts/fm/fm_rec08_render.py` (CYCLES 1280×720, 96 spp,
AgX Medium High Contrast, exposición 0,55; no guarda `.blend`).

## Correcciones

- La primera versión construía la cinta con sección horizontal y se leía como
  una varilla metálica; se pasó a sección vertical de 50 mm y material negro
  mate.
- Las cintas de las esquinas se cruzaban a la misma altura; ahora la cinta
  frontal va a 0,84 m y las laterales a 0,90 m.
- Se eliminaron las costuras claras y los clips visibles que parecían un asa
  metálica sobre el casete.
- La cámara de barrera estaba fuera de la sala (y=-7,9), contra el muro norte;
  se movió a y=-8,6.

## Limitaciones

- Sin texturas/bake: la cinta usa un bump procedural de tejido, no una tela
  textureada.
- Sin colisiones propias ni export GLB/Godot de este clúster.
- El fondo de Recepción sigue siendo blockout (suelo azul, muros y techo sin
  pase hero).
- El receptor de la barrera queda parcialmente oculto por el desk en la toma
  de contexto; la geometría existe y está completa.
- La sala sigue teniendo bancas, taquillas, mesas, reloj, cámaras y servicios
  pendientes.

## Siguiente

Bancas A/B, taquillas, mesas/espera y después servicios de Recepción. Sin
commit.

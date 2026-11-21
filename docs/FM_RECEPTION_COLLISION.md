# FM — Recepción: validación de colisión y cápsula

## Objetivo

Comprobar que el sector exportado de Recepción (`reception_sector.glb`) genera colisión estática suficiente para que una cápsula de jugador (radio 0,38 m, altura 1,70 m) se apoye en el suelo y recorra el pasillo central sin caer ni atravesar la arquitectura.

## Implementación

- `scripts/fm/fm_reception_collision_test.gd`
- `scenes/fm/fm_reception_collision_test.tscn`
- Depende de `scripts/fm/fm_glb_collision.gd` (`FMGLBCollision`).

El test:

1. Carga `res://assets/models/fm/reception_sector.glb`.
2. Construye colisión estática con `FMGLBCollision.build()` sobre el AABB del sector.
3. Espera **2 physics frames** para que las formas estén registradas en el `direct_space_state`.
4. Lanza un raycast de suelo en `(-94, 3, 20) → (-94, -1, 20)`.
5. Crea un `CharacterBody3D` con cápsula de 0,38 m de radio y 1,70 m de alto.
6. Lo coloca en `(-94, floor_y + 0.95, 9.5)` y lo desplaza 360 frames a 3 m/s hacia +Z con gravedad.
7. Valida que termine más allá de z=22, que no haya caído (`min_y > -0.5`) y que no se haya desviado más de 4 m en X.

## Corrección en `FMGLBCollision`

Antes, cualquier malla con `size.y < 0.10` se descartaba. Eso eliminaba la losa del suelo de Recepción, que es una superficie plana.

Ahora:

- Si `size.y < 0.10` y `max(size.x, size.z) >= 1.0`, se crea una caja fina con grosor mínimo de **0,04 m**.
- Las calcomanías, alfombras y líneas de suelo siguen filtrándose por token.

## Resultado

```text
RECEPTION_COLLISION_BUILD count=157 trimesh=6
RECEPTION_COLLISION_FLOOR y=0.020
RECEPTION_COLLISION_CAPSULE start=(-94.00,0.97,9.50) end=(-94.00,0.87,27.49)
travelled_z=17.99 min_y=0.87
RECEPTION_COLLISION_OK
```

- El raycast impacta el suelo real a **y = 0,020**.
- La cápsula recorre **17,99 m** por el pasillo central.
- Se mantiene a **y = 0,87** (centro de la cápsula), sin caer ni atravesar el suelo.
- No se desvía en X.

## Limitaciones

- Es una validación de **runtime**: la colisión se genera desde el GLB en el test, no está incluida como proxies `-col` en el GLB de producción.
- `FMGLBCollision` convierte superficies planas grandes en cajas finas; para suelos con desniveles, rampas o huecos reales habrá que usar proxies específicos.
- El test recorre solo el pasillo central; no valida escaleras, puertas secundarias, escondites ni props interactivos.
- Los prints `RECEPTION_COLLISION_BIGBOX` y `RECEPTION_COLLISION_RAY_*` son de diagnóstico y pueden quitarse cuando el test se estabilice.

## Siguiente

1. Documentar y cerrar la validación de colisión.
2. LOD/optimización global de Recepción.
3. Taquillas y señalización hero.
4. Z10 feeds/S-10..S-15; texturas/bake/narrativa al final.

Sin commit.

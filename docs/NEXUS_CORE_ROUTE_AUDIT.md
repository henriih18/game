# FRECUENCIA MUERTA — Auditoría del núcleo vertical este

Fecha: 2026-11-03.
Ámbito: `nexus/master/NEXUS_MASTER.blend`, torre `NEXUS_VTOWER` y escalera `NEXUS_VTOWER_EAST_STAIR_4LANE`.
Método: rejilla 2D para el acceso L1 y comprobación analítica de cápsula en los vuelos.
Script: `blender_concept/audit_core_route.py`.
Salida: `nexus/nucleo/core_route_audit.json`.

## Alcance y método

- Cápsula de jugador: radio **0,38 m**, altura **1,80 m**.
- Rejilla del acceso L1: celda **0,05 m**, desde el enlace `(24,0)` hasta el portal `(30,12.5)`.
- Se excluyen hojas, cristales, manillas y pivotes de puerta porque se asumen operables.
- Se excluyen escalones de ≤0,16 m.
- La pared este `NEXUS_VTOWER_WALL_E` es una malla booleana con cinco huecos; su AABB es maciza. Para la rejilla se sustituyó por dos tramos sólidos alrededor del portal L1 (y 9,00–11,66 y 13,34–17,00), dejando libre el hueco real de 1,64 m.
- En cada vuelo se muestreó el centro del carril al 25, 50 y 75 % del recorrido, con la cota de peldaño interpolada entre el descanso superior y el inferior.
- La holgura lateral usa un BVH de la geometría visible de la torre sin superficies pisables; la altura libre usa un rayo vertical desde 0,40 m sobre el peldaño.

## Resultado del acceso L1

El recorrido desde el enlace L1 hasta el portal de la escalera es **alcanzable**. Ruta de la rejilla:

`(24.0, 0.0) → (24.6, 7.4) → (24.6, 9.4) → (25.45, 9.55) → (29.45, 9.55) → (29.45, 11.55) → (29.9, 12.1) → (30.0, 12.5)`

El paso rodea el escombro del enlace por el este, cruza el umbral de 0,15 m entre la cota del enlace y la torre y llega al portal sin atravesar la pared. El vano libre del portal es de **1,64 m** entre jambas; las hojas están abiertas contra los laterales.

## Resultado de los vuelos

Se auditaron **18 vuelos** repartidos en cuatro tramos. Resultado global:

| Tramo | Vuelos | Recorrido por vuelo | Contrahuella total | Holgura lateral mínima | Altura libre mínima |
|---|---:|---:|---:|---:|---:|
| L1–L2 | 4 | 2,72 m | 2,00 m | 0,32 m | sin techo superior |
| L2–L3 | 4 | 3,53 m | 2,17–2,33 m | 0,32 m | 6,28 m |
| L3–L4 | 4 | 3,80 m | 2,50 m | 0,32 m | 7,20 m |
| L4–L5 | 6 | 2,72 m | 1,83 m | 0,32 m | 5,70 m |

- **Holgura lateral mínima: 0,32 m** en los vuelos 01 y 04 de cada tramo, junto a los muros sur/norte. El centro del carril queda a 0,70 m de la pared y la cápsula conserva 0,32 m.
- **Altura libre mínima: 5,698 m** en L4–L5. En L1–L2 el rayo no encuentra techo porque la escalera está abierta en la parte superior de ese tramo.
- Los cuatro vuelos de cada tramo tienen 2,00–2,50 m de desnivel individual, con una contrahuella total de 8–11 m; la secuencia de 18 vuelos cubre L1–L5.
- No se detectaron colisiones de la cápsula en la línea central ni techos por debajo de 3,12 m en los puntos medidos.

## Interpretación

La escalera de cuatro franjas es **geométricamente transitable** en su línea central para el jugador de 0,76 m de diámetro. El pasillo útil de 1,21 m entre barandillas deja 0,225 m por lado si el jugador va centrado; el muestreo conservador de 0,32 m corresponde a los tramos junto a los muros, no a las barandillas.

Esto **no** certifica todavía:

- el comportamiento de una `CharacterBody` real en Godot con peldaños, pendientes y `floor_snap_length`;
- el giro fino en los descansillos y el paso de criaturas de 3,0 m;
- la conexión horizontal de los portales L2–L5 con sus respectivos links, que se auditó por separado con rayos en pasadas anteriores;
- la iluminación del recinto de la escalera este: el lobby oeste tiene luces de área (`NEXUS_VTOWER_LOBBY_AREA_1..5`), pero la escalera no tiene fuentes propias y produce un render negro desde el portal.

## Retorno a la extracción

El retorno desde el núcleo al punto de extracción de recepción queda compuesto por:

1. bajada por la escalera este hasta el portal L1;
2. enlace L1 desde `(30,0, 12,5)` hasta el corredor principal;
3. corredor este-oeste hasta recepción;
4. entrada a recepción y zona de extracción en `(-13,90, 2,78)`.

Los tramos 2–4 ya están certificados en `docs/NEXUS_L1_CIRCULATION_AUDIT.md`. El tramo 1 es el que cubre esta auditoría. La combinación es coherente, pero no se ejecutó una simulación continua de ida y vuelta en un solo recorrido.

## Limitaciones

- La comprobación es analítica y conservadora; no simula físicas, escalones ni controlador.
- No se modificó la torre ni el máster; el archivo sigue igual.
- El render de revisión `/tmp/opencode/core_stair.png` sale negro por falta de iluminación en el núcleo; no es un fallo de geometría.
- Persisten las dos PNG inválidas de `industrial_wall_lamp_1k`; no se tocaron.

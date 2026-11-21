# FRECUENCIA MUERTA — Procedimiento de extracción del Nivel 1

**Estado:** prototipo local jugable en Godot 4.7; reglas de diseño v138.  
**Ámbito:** recepción del Nivel 1.  
**Implementación actual:** geometría y metadatos en Blender; escena local `reception_slice.tscn` en Godot para 1 jugador, preparada para hasta 8. La sincronización de red completa y el inventario general siguen pendientes.

## 1. Ubicación y volumen de extracción

- La extracción se realiza en la **recepción completa del Nivel 1**, de **16 × 10 m**.
- El ascensor **SALIDA**, junto al reloj, es la **salida visual**. Su cabina mide **1,88 × 1,80 × 2,55 m** y no es el volumen real de validación.
- El aro naranja, el texto de suelo y la consola marcan la salida, pero **no limitan la zona**. La validación usa el trigger de la recepción.
- El trigger de recepción está en `(-12.0, 6.7, -5.65)` y cubre los límites de la sala.

## 2. Jugadores y capacidad

- **Mínimo:** 1 jugador.
- **Máximo:** 8 jugadores, pensado para partidas online de 7 u 8.
- La capacidad de 8 se apoya en la superficie de la recepción. **No se ha simulado el movimiento simultáneo de 8 cápsulas**; la validación es geométrica y de metadatos.
- La cabina tiene capacidad visual para 2 personas. Los 8 jugadores no necesitan caber físicamente en ella: la extracción se valida en la recepción y la cabina representa la salida.

## 3. Activación

La secuencia puede activarse cuando:

1. Hay al menos un jugador conectado y vivo dentro de la recepción.
2. **Todos los jugadores conectados y vivos están dentro de la recepción.**
3. Hay al menos **un objeto recuperado dentro del radio de entrega** del ascensor (`2,4 m` desde `EXTRACTION_CENTER`), o transportado por un jugador presente.
4. La condición se mantiene durante **2,0 s** (`activation_time_s`).

Jugadores contemplados:

- **Abatido dentro de la recepción:** cuenta como presente.
- **Abatido fuera:** no cuenta para la activación y queda fuera.
- **Desconectado:** se ignora para la activación y la extracción.
- **Muerto:** se ignora para la activación y la extracción.

## 4. Secuencia

Duración total de referencia: **8,7 s**, incluida la activación.

| Fase | Duración | Notas |
|---|---:|---|
| Activación | 2,0 s | Todos los conectados vivos dentro |
| Apertura de puertas | 1,5 s | Frames 1–45 |
| Puertas abiertas | 2,5 s | Frames 45–105 |
| Cierre de puertas | 1,0 s | Frames 105–130 |
| Viaje visual | 1,3 s | Frames 130–160 |
| **Total** | **8,7 s** | `total_sequence_s` |

La animación de puertas es visual. Si el equipo se mueve durante la secuencia, la extracción no se cancela por ello: al completarse, solo se extrae quien siga dentro.

## 5. Condición de finalización

La extracción se completa cuando la secuencia termina y **al menos un jugador válido está dentro de la recepción**.

- **Jugadores dentro al completar:** extraídos.
- **Jugadores fuera al completar:** no extraídos; quedan atrás.
- **Jugadores abatidos dentro:** cuentan como presentes y se extraen.
- **Jugadores desconectados o muertos:** no se extraen.
- **Sin jugadores válidos dentro al completar:** la extracción no se completa.

La extracción es **parcial**: no se exige que los 8 jugadores lleguen para que el equipo asegure lo que tenga dentro.

## 6. Botín y entrega

Cuenta como recuperado:

- El objeto que está **físicamente dentro de la recepción** al completar.
- El objeto **transportado por un jugador que se extrae**.

No cuenta:

- El objeto que queda fuera de la recepción.
- El objeto abandonado por un jugador que no se extrae.
- El objeto cuya única copia quedó en una zona no válida.

Reglas de recompensa:

- Cada objeto cuenta **una sola vez** (`duplicate_reward_guard`).
- Un objeto completo y sus componentes son **excluyentes**: no se puede cobrar dos veces la misma recuperación.
- Los componentes futuros se contarán individualmente solo si llegan a la zona de entrega.
- El valor económico del botín se suma al resultado del equipo. **El reparto individual y la moneda final quedan pendientes de la fase de misión**; no se inventan aquí.

## 7. Riesgos durante la espera

- La recepción **no es una zona segura**. Las criaturas pueden entrar.
- La apertura de puertas, la luz de la cabina, la consola y el movimiento del equipo pueden generar ruido y atraer amenazas.
- La secuencia no concede invulnerabilidad.
- La tensión principal es decidir si el equipo espera a todos, abandona a alguien o se retira con parte del botín.

## 8. Casos límite

- **Un jugador sale durante la secuencia:** la secuencia continúa; ese jugador queda fuera y no se extrae.
- **Un jugador cae abatido dentro:** cuenta como presente; se extrae con el equipo.
- **Un jugador cae abatido fuera:** no cuenta; queda fuera.
- **Un jugador se desconecta:** se ignora; su loot solo cuenta si está físicamente dentro de la recepción.
- **Un jugador muere dentro:** se ignora como jugador, pero el loot que haya quedado en el suelo dentro de la recepción sí puede contar.
- **Todos los jugadores salen o mueren antes de completar:** no hay extracción.

## 9. Metadatos de referencia

- Zona: `NEXUS_V05_REC_EXTRACT_ZONE`, `zone_shape='reception_room'`, `zone_size_m=[16,10]`, `max_players=8`, `min_players=1`, `activation_time_s=2.0`, `total_sequence_s=8.7`.
- Trigger de recepción: `NEXUS_V05_REC_EXTRACT_RECEPTION_TRIGGER`.
- Trigger de cabina: `NEXUS_V05_REC_EXTRACT_CAB_TRIGGER`; es **visual**, `extraction_validation=False`.
- Secuencia: `NEXUS_V05_ELEVATOR_SEQUENCE`, `extraction_mode='team_reception_room'`, `requires_player_inside_reception=True`, `requires_cab_occupancy=False`.
- Objetos recuperables: `NEXUS_V05_REC_LOOT_CASE_0`, `_SAMPLE_0`, `_CRATE_0`, `_DOCS_0`, `_DRIVE_0`.

## 9.1. Implementación local en Godot

- Escena: `scenes/fm/reception_slice.tscn`; lógica: `scripts/fm/reception_slice.gd`, `scripts/fm/fm_reception_extraction.gd`, `scripts/fm/fm_reception_loot.gd`.
- Arte: `assets/models/fm/reception_nexus.glb` (13.446.520 B), cargado en runtime con `GLTFDocument`; 5 loot, escondite, trampa, puertas del ascensor y luces del GLB.
- Jugador: `scripts/fm/fm_player.gd`, con gravedad, linterna, batería, interacción y transporte de un objeto. El viewmodel usa `assets/models/fm/flashlight_nexus.glb` (1.272.372 B).
- Secuencia implementada: activación 2,0 s + apertura 1,5 s + espera 2,5 s + cierre 1,0 s + viaje 1,3 s + confirmación 0,4 s = **8,7 s**. Las puertas se abren, se cierran y después se muestra el resultado.
- Prueba: `tests/fm_reception_smoke.tscn` pasa **PASS**; cubre movimiento, escondite, trampa, rechazo del objeto de 42 kg, recogida, drop/repick, apertura/cierre de puertas y extracción.
- Límite actual: 1 jugador local. La API `all_alive_players_inside`, `get_active_player_count` y `max_players=8` está preparada, pero no hay sincronización de 8 ni prueba simultánea.

## 10. Limitaciones

- La sincronización de red para 8 jugadores no está implementada; la escena actual es local de 1 jugador.
- No existe inventario general, sistema de desmontaje ni efectos de fragilidad; el jugador transporta un objeto a la vez.
- No hay criaturas ni IA en la recepción; el ruido de pasos y trampas se registra, pero no hay un sistema de percepción que lo consuma en esta sala.
- La animación del ascensor es visual; la extracción no depende de que los 8 jugadores quepan en la cabina.
- Los tiempos y la capacidad son provisionales y deben validarse en playtest.
- El GLB se carga en runtime; no se ha generado un build final ni se ha exportado como entrega.

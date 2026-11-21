# FRECUENCIA MUERTA — Sistema de radio local

Fecha: 2026-11-17
Rama: `frecuencia-muerta` · HEAD `287b101` · sin commit

## 1. Alcance

Primera versión del sistema de comunicación por radio. Implementa la radio
individual del jugador, sin voz de red todavía:

- Push-to-talk (PTT).
- Canales de equipo, servicio y emergencia.
- Batería propia con drenaje distinto al transmitir y al escuchar.
- Interferencia y calidad de señal.
- Estática y pitidos generados por código, sin assets externos.
- Panel de estado en el HUD.
- API preparada para futuras transmisiones de compañeros y del Imitador.

La radio **no revela posiciones de compañeros** ni proporciona información
automática de navegación. La voz por proximidad y la radio en red quedan para
la fase multijugador.

## 2. Controles

| Acción | Tecla | Comportamiento |
|---|---|---|
| `radio` | **V** | Mantener pulsado para transmitir; soltar para terminar |
| `radio_channel` | **C** | Cambia al siguiente canal |

Las acciones están en `[input]` de `project.godot`. Se eligieron V y C porque
estaban libres y no colisionan con movimiento, linterna, inventario o pausa.

## 3. Canales

| Índice | Canal | Uso previsto |
|---|---|---|
| 0 | `EQUIPO` | Canal compartido inicial de los trabajadores |
| 1 | `SERVICIO` | Coordinación con sistemas y mantenimiento |
| 2 | `EMERGENCIA` | Canal reservado para incidencias graves |

El canal no otorga ventajas de información: solo cambia el contexto de
transmisión. En multijugador, los canales servirán para separar conversaciones
y para que el Imitador pueda inyectar mensajes falsos.

## 4. Batería y señal

- Batería máxima: **100**.
- Consumo transmitiendo: **0,85/s**.
- Consumo en escucha: **0,025/s**.
- Umbral de batería baja: **20**.
- Señal base: **0,92**.
- La interferencia resta hasta un 85 % de la señal.
- Con batería baja, la calidad se escala proporcionalmente.
- A batería 0 no se puede transmitir; el PTT emite un pitido de error.

La radio no debe convertirse en una obligación de gestión permanente. La
comunicación por proximidad seguirá funcionando cuando exista, aunque la
radio se quede sin batería.

## 5. Audio

Todo el audio se sintetiza en `FMRadio`:

- **Estática**: `AudioStreamWAV` de 1 s, 16 bits, 22.050 Hz, en bucle, con
  ruido y chasquidos esporádicos. El volumen sube cuando empeora la señal
  (de −30 dB a −12 dB).
- **Pitido**: `AudioStreamWAV` de 0,11 s a 880 Hz con envolvente de caída.
  Suena al iniciar y terminar la transmisión, al cambiar de canal y al
  intentar transmitir sin batería o sin señal.

No se añadieron archivos de audio nuevos ni dependencias.

## 6. HUD

Se añadió un panel debajo de la carga, en (1000,142), tamaño 256×52:

```
RADIO · EQUIPO
TRANSMITIENDO · BAT 84% · SEÑAL 92%
```

- El título muestra el canal y `TX` cuando se transmite.
- El estado muestra `TRANSMITIENDO`, `EN ESCUCHA`, `SEÑAL DÉBIL`,
  `SIN BATERÍA` o `RADIO APAGADA`.
- El color pasa a rojo sin batería, ámbar con batería o señal baja y verde
  al transmitir.
- El hint inferior incluye `V RADIO · C CANAL`.

## 7. API

`scripts/fm/fm_radio.gd` (`class_name FMRadio extends Node`).

Señales:

- `transmission_started(channel_name)`
- `transmission_ended(channel_name)`
- `channel_changed(index, channel_name)`
- `battery_changed(ratio)`
- `signal_changed(quality)`

Métodos:

- `cycle_channel()`
- `set_channel(index)`
- `set_interference(value)`
- `add_battery(amount)`
- `is_transmitting()`
- `get_channel_name()`
- `get_channel_index()`
- `get_battery()`
- `get_battery_ratio()`
- `get_signal_quality()`
- `get_status_text()`

Propiedades exportadas: `battery`, `channel_index`, `enabled`, `interference`.

## 8. Integración

- `scripts/fm/fm_level1_v06.gd`: nueva variable `radio: FMRadio`; se crea como
  hijo del `Player` en `_setup_player()`, después de la linterna y el grupo
  `fm_player`. En `_process()` se actualiza el HUD con `hud.set_radio(...)`.
- `scripts/fm/fm_hud.gd`: panel de radio y método
  `set_radio(channel_name, battery_ratio, signal_quality, transmitting,
  status_text)`.
- `project.godot`: acciones `radio` (V) y `radio_channel` (C).
- `tests/fm_level1_v06_radio_smoke.gd/.tscn`: test dedicado.

No se tocaron `scenes/fm/level1.tscn`, `fotos-referencia/` ni escenas del
slice. No se modificó ningún GLB ni el máster de Blender.

## 8.1. Suministros de batería

`scripts/fm/fm_radio_supply.gd` (`FMRadioSupply`) añade pilas recogibles y
cargadores de pared, reutilizando la interfaz `fm_interactable` del jugador.

- **7 estaciones de carga**: Z10, Control, Almacén, Mantenimiento, Oficinas,
  Escaleras principales y sala técnica NWStair. Recargan **+40 %** con un
  cooldown de **22 s** por estación.
- **8 pilas comunes**: Z10, Seguridad, Vestuarios, Almacén, Mantenimiento,
  Oficinas, Aseo y NWStair. Recargan **+30 %** y desaparecen al usarse.
- **2 pilas de alta capacidad**: Almacén y NWStair. Recargan **+70 %**.
- Total: **17 nodos** registrados en `fm_interactable` y `fm_radio_supply`.
- No añaden colisión, luces ni alteran el navmesh. No revelan posiciones de
  compañeros.
- La batería se limita a 100 % en `FMRadio.add_battery()`.

La integración vive en `_setup_radio_supplies()` de
`scripts/fm/fm_level1_v06.gd`, llamada tras `_setup_batteries()`.

## 9. Pruebas

| Prueba | Resultado |
|---|---|
| `tests/fm_level1_v06_radio_smoke.tscn` | **21 PASS / 0 FAIL** |
| `tests/fm_level1_v06_radio_supplies_smoke.tscn` | **30 PASS / 0 FAIL** |
| `tests/fm_level1_v06_smoke.tscn` | **412 PASS / 0 FAIL** |
| `tests/fm_level1_v06_gameplay.tscn` | **108 PASS / 0 FAIL** |
| `tests/fm_full_run.tscn` | **49 PASS / 0 FAIL** |
| `tests/fm_graphics_presets_smoke.tscn` | **194 PASS / 0 FAIL** |
| `tests/fm_level1_v06_perf.tscn` 1280×720 | **PASS** |

Perf final: **432,0 fps medios**, mínimo 154,3, p1 223,1, p99 4,48 ms, 0
frames sobre 16,7 ms.

El test de radio cubre: instancia y grupo, canal inicial, batería y señal,
audio sintetizado, ausencia de API de posición, etiqueta del HUD, PTT,
drenaje, cambio de canal, interferencia, recuperación de señal, batería baja
y recarga.

El test de suministros cubre: 17 nodos, grupos, prompts, carga de estación
(+40) con cooldown y bloqueo, pila común (+30) no repetible, pila de alta
capacidad (+70) y límite de batería a 100.

## 10. Limitaciones

- No hay voz de red ni reproducción de voz de compañeros.
- No hay captura de micrófono ni consentimiento de grabación todavía.
- Las pilas y cargadores son locales; su sincronización multijugador queda
  pendiente.
- La estática es local y no depende de la posición de otros jugadores.
- El Imitador todavía no inyecta transmisiones falsas.
- La integración multijugador requerirá autoridad del servidor y canales
  separados por equipo.

## 11. Siguiente fase

1. Sincronizar pilas, cargadores y estados de radio en multijugador.
2. Implementar voz por proximidad y radio en red (Opus, PTT, canales y
   consentimiento explícito).
3. Conectar el Imitador al sistema de radio para reproducir mensajes falsos
   con pistas auditivas coherentes.
4. Añadir pruebas de red con dos clientes y autoridad del servidor.

## 12. Skills usadas

- `godot-gdscript` — sintaxis, tipado y estructura de `FMRadio`.
- `godot-audio` — `AudioStreamWAV` sintetizado y reproductores.
- `godot-ui-control` — panel del HUD y jerarquía de `Control`.
- `godot-signals-groups` — señales de radio y grupo `fm_radio`.
- `scenario-godot-gameplay` — integración en el nivel y pruebas headless.
- `verification-before-completion` — batería de pruebas antes de documentar.

No se usaron skills de Blender: esta fase no creó geometría ni materiales.

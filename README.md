# Robo Caótico — Prototipo 0.8

Prototipo de robo cooperativo para Steam. La dirección elegida es **3D en primera persona y online**. El juego 2D sigue siendo la base jugable con red; la demo 3D elevada queda como referencia y la demo FP sirve para validar la cámara, la caja y el nivel antes de invertir en el multijugador 3D.

![Menú](docs/menu.png)

![Demo 3D en primera persona](docs/demo3d_fp.png)

![Demo 3D elevada](docs/demo3d.png)

![Gameplay 2D](docs/screenshot.png)

## Estado actual

### Prototipo 3D en primera persona (nuevo)

- Una sala 3D con techo, vigas, lámparas, servidores, escritorio, pilares y bóveda
- **Cámara en primera persona** a la altura de los ojos, mirada con mouse
- **Manos visibles** y caja sostenida delante del jugador
- **El mismo bucle**: 3 gemas + caja + extracción + temporizador + alarma
- **Cámaras de seguridad 3D** con cono de visión, detección por línea de vista y aviso rojo
- HUD con punto de mira, aviso de agarre/soltar, viñeta de peligro, partículas y sonidos
- **Importante**: es un prototipo **offline y de un solo jugador**. No es el modo local final ni tiene red todavía; sirve para decidir si la primera persona se siente bien.

### Juego 2D (base jugable)

- Arte flat vector estilo Among Us (personajes, caja, gemas, baldosas)
- **Multijugador en red**: partidas de 2 a 4 jugadores por IP directa (ENet/UDP)
- **Co-op local 2 jugadores**: P1 (violeta) y P2 (cian), usado como banco de pruebas
- Movimiento top-down con colisiones
- **Agarre cooperativo**: la caja se lleva entre uno (45% de velocidad) o entre dos (80%), y se ubica en el punto medio entre ambos
- **Ronda de 2 minutos** con cuenta regresiva
- **Cámaras de seguridad**: si te ven, la alarma sube; al 100% perdés. Sin nadie a la vista, baja sola
- **Sonido y música originales**, generados por código
- **Feedback visual**: partículas, viñeta roja, personajes animados, caja que se tambalea, zona de extracción que respira y HUD animado
- Pantalla de fin (victoria / derrota)
- **Mini-bucle**: juntar las 3 gemas y llevar la caja a EXTRACCIÓN antes de que se acabe el tiempo o salte la alarma
- El host manda: valida agarres, gemas, tiempos y entrega, y sincroniza todo a los clientes

### Demo 3D elevada (referencia)

- Una sala 3D construida por código, con servidores, escritorio, pilares, plantas y lámparas
- **El mismo bucle**: 3 gemas + caja cooperativa + extracción + temporizador + alarma
- **2 jugadores locales** con cámara elevada en perspectiva
- **Cámaras de seguridad 3D** con cono de visión y detección por línea de vista
- **Caja cooperativa** que se eleva entre los dos portadores
- HUD, viñeta de peligro, partículas 3D, sonidos y pantalla de fin
- **No tiene red**; se conserva como comparación visual y de jugabilidad

## Dirección del proyecto

- El juego final será **3D en primera persona y cooperativo online**, para 2 a 4 jugadores.
- **No habrá co-op local de dos ni pantalla dividida**. El botón "Prueba 2D local" es solo un banco de pruebas para iterar mecánicas sin red.
- El siguiente salto técnico es llevar el prototipo FP a online con ENet. Steam, lobbies y voz por proximidad vienen después.

## Cómo abrir el proyecto

```bash
godot --path ~/Documentos/game
```

O abrir Godot, **Import** y seleccionar esta carpeta. Dentro del editor, **F5** para jugar.

## Cómo jugar

En el menú:

- **Crear partida**: abre una sala 2D en el puerto UDP 7777.
- **Unirse**: escribí la IP del anfitrión y tocá Unirse.
- **Prueba 2D local**: banco de pruebas de 2 jugadores en la misma PC, en 2D.
- **Demo 3D**: demo 3D local con cámara elevada y 2 jugadores.
- **Demo 3D FPS**: prototipo en primera persona, offline y de un jugador.

Para probar el multijugador 2D en la misma PC, abrí **dos instancias** del juego: en una creá la partida y en la otra uníte a `127.0.0.1`.

Para jugar en LAN, el anfitrión pasa su IP local (por ejemplo con `hostname -I`) y el otro se une a esa IP. Para jugar por internet hay que abrir/redirigir el puerto **UDP 7777** en el router del anfitrión; todavía no hay lobbies de Steam ni NAT punch.

También se puede arrancar directo desde la terminal:

```bash
godot --path ~/Documentos/game -- --host
godot --path ~/Documentos/game -- --join=127.0.0.1
godot --path ~/Documentos/game -- --local
godot --path ~/Documentos/game -- --demo3d
godot --path ~/Documentos/game -- --demo3dfp
```

Las demos 3D también se pueden abrir directo:

```bash
godot --path ~/Documentos/game scenes/demo3d.tscn
godot --path ~/Documentos/game scenes/demo3d_fp.tscn
```

## Controles

| Acción | 2D / 3D elevada | 3D primera persona |
|---|---|---|
| Mover | WASD (P2: flechas) | WASD |
| Mirar | — | Mouse |
| Agarrar / soltar caja | E (P2: Enter) | E |
| Reiniciar al terminar | R | R |
| Volver al menú | Esc | Esc |
| Silenciar todo el audio | M | M |
| Desactivar balanceo de cámara | — | H |

En primera persona, si el mouse se libera, un clic lo vuelve a capturar. **M** silencia o reactiva el audio en cualquier momento.

## Estructura

```
scenes/        menu, main (2D), demo3d (3D elevada), demo3d_fp (3D FP),
               player, player2, player3d, gem, gem3d, crate, crate3d,
               extraction_zone, security_camera, security_camera3d
scripts/       GDScript de cada escena + player_fp3d.gd + audio.gd (autoload)
assets/art/    SVGs (personajes, caja, gema, sombra, baldosa, chispa)
assets/audio/  SFX y música en WAV (generados, sin samples externos)
assets/shaders/ viñeta de peligro + baldosas 3D
tools/         generate_audio.py (audio reproducible)
```

## Cómo regenerar el audio

El audio se puede reconstruir desde cero con Python 3 (solo biblioteca estándar):

```bash
cd ~/Documentos/game
python3 tools/generate_audio.py
godot --headless --path . --import
godot --headless --path . --import
```

La primera importación puede avisar que los WAV recién creados no tienen loader; la segunda pasada los deja listos. Los WAV se importan sin compresión (PCM) para que los loops de música no tengan artefactos.

## Verificación

- Test de integración del prototipo FP: **16/16 PASS** (cámara, aviso de agarre/soltar, caja delante, detección, alarma, gema, entrega y victoria)
- Test del juego 2D: **16/16 PASS**
- Test de red 2D: **6/6 PASS** (host + cliente en la misma PC)
- Smoke test de la demo 3D elevada: sin errores de script
- La demo FP arranca sin errores con `godot --headless --path . --quit-after 90 scenes/demo3d_fp.tscn`

## Limitaciones actuales

- El prototipo **3D FP es offline y de un solo jugador**; todavía no tiene red
- La demo **3D elevada es local de 2** y no tiene red
- El multijugador 2D funciona por IP directa (UDP 7777), sin lobbies de Steam
- 2 a 4 jugadores por partida en 2D
- Sin voz ni chat
- Si un jugador se desconecta, sale de la partida (no hay reconexión)
- El arte 3D y los personajes son procedurales: sirven para comparar, no son el acabado final
- El audio está generado por código: sirve para el prototipo, pero todavía no es una banda sonora profesional

## Siguiente paso

1. Probar la **Demo 3D FPS** desde el menú y validar cámara, manos, caja y cámaras.
2. Llevar el prototipo FP a **online 3D con ENet**: servidor autoritativo, 2 a 4 jugadores, sincronización de cuerpos, caja, gemas, alarma y temporizador.
3. Después: **lobbies de Steam**, voz por proximidad, modo traidor, más salas y página de Steam.

# Robo Caótico — Prototipo 0.6

Prototipo de robo cooperativo 2D (estilo R.E.P.O. / Among Us) para Steam.

![Menú](docs/menu.png)

![Gameplay](docs/screenshot.png)

## Estado actual

- Arte flat vector estilo Among Us (personajes, caja, gemas, baldosas)
- **Multijugador en red**: partidas de 2 a 4 jugadores por IP directa (ENet/UDP)
- **Co-op local 2 jugadores**: P1 (violeta) y P2 (cian)
- Movimiento top-down con colisiones
- **Agarre cooperativo**: la caja se lleva entre uno (45% de velocidad) o entre dos (80%), y se ubica en el punto medio entre ambos
- **Ronda de 2 minutos** con cuenta regresiva
- **Cámaras de seguridad**: si te ven, la alarma sube; al 100% perdés. Sin nadie a la vista, baja sola
- **Sonido y música originales**, generados por código (sin samples externos): loops de menú y de golpe, efectos de gemas, agarre, entrega, pasos, cámara, alarma y victoria/derrota
- **Feedback visual**: partículas al recoger gemas, viñeta roja que crece con la alarma, personajes que saltan al caminar, caja que se tambalea, zona de extracción que respira y HUD animado
- Pantalla de fin (victoria / derrota)
- **Mini-bucle**: juntar las 3 gemas y llevar la caja a EXTRACCIÓN antes de que se acabe el tiempo o salte la alarma
- El host manda: valida agarres, gemas, tiempos y entrega, y sincroniza todo a los clientes

## Cómo abrir el proyecto

```bash
godot --path ~/Documentos/game
```

O abrir Godot, **Import** y seleccionar esta carpeta. Dentro del editor, **F5** para jugar.

## Cómo jugar en red

En el menú:

- **Crear partida**: abre una sala en el puerto UDP 7777.
- **Unirse**: escribí la IP del anfitrión y tocá Unirse.
- **Jugar local**: 2 jugadores en la misma PC.

Para probar en la misma PC, abrí **dos instancias** del juego: en una creá la partida y en la otra uníte a `127.0.0.1`.

Para jugar en LAN, el anfitrión pasa su IP local (por ejemplo con `hostname -I`) y el otro se une a esa IP. Para jugar por internet hay que abrir/redirigir el puerto **UDP 7777** en el router del anfitrión; todavía no hay lobbies de Steam ni NAT punch.

También se puede arrancar directo desde la terminal (útil para pruebas):

```bash
godot --path ~/Documentos/game -- --host
godot --path ~/Documentos/game -- --join=127.0.0.1
godot --path ~/Documentos/game -- --local
```

## Controles

| Acción | Jugador 1 | Jugador 2 (local) |
|---|---|---|
| Mover | WASD | Flechas |
| Agarrar / soltar caja | E | Enter |
| Volver al menú (al terminar) | R | R |
| Silenciar todo el audio | M | M |

En red cada jugador usa **WASD + E**. **M** silencia o reactiva el audio del juego en cualquier momento.

## Estructura

```
scenes/        menu, main, player, player2, gem, crate, extraction_zone, security_camera
scripts/       GDScript de cada escena + audio.gd (autoload) + effects.gd
assets/art/    SVGs (personajes, caja, gema, sombra, baldosa, chispa)
assets/audio/  SFX y música en WAV (generados, sin samples externos)
assets/shaders/ viñeta de peligro
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

## Limitaciones actuales

- Sin lobbies de Steam: se juega por IP directa (UDP 7777)
- 2 a 4 jugadores por partida
- Sin voz ni chat
- Si un jugador se desconecta, sale de la partida (no hay reconexión)
- El audio está generado por código: sirve para el prototipo, pero todavía no es una banda sonora profesional

## Siguiente paso

- Lobbies de Steam con GodotSteam (y voz por proximidad)
- Modo traidor (tensión social)
- Más mapas, objetivos y variantes de robo
- Página de Steam y demo

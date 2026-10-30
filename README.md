# Robo Caótico — Prototipo 0.3

Prototipo de robo cooperativo 2D (estilo R.E.P.O. / Among Us) para Steam.

![Gameplay](docs/screenshot.png)

## Estado actual

- Arte flat vector estilo Among Us (dos personajes, caja, gemas, baldosas)
- **Co-op local 2 jugadores**: P1 (violeta) y P2 (cian)
- Movimiento top-down con colisiones
- **Agarre cooperativo**: la caja se lleva entre uno (45% de velocidad) o entre dos (80%), y se ubica en el punto medio entre ambos
- Si los portadores se separan demasiado, se sueltan (sin efecto goma)
- **Mini-bucle**: juntar las 3 gemas y llevar la caja a la zona de EXTRACCIÓN
- HUD con estado del botín

## Cómo abrir el proyecto

```bash
godot --path ~/Documentos/game
```

O abrir Godot, **Import** y seleccionar esta carpeta. Dentro del editor, **F5** para jugar.

## Controles

| Acción | Jugador 1 | Jugador 2 |
|---|---|---|
| Mover | WASD | Flechas |
| Agarrar / soltar caja | E | Enter |

## Estructura

```
scenes/        main, player, player2, gem, crate, extraction_zone
scripts/       GDScript de cada escena
assets/art/    SVGs (personajes, caja, gema, sombra, baldosa)
assets/audio/  (vacío por ahora)
```

## Siguiente paso

- Ronda con temporizador y alarma
- Agarre cooperativo con física (peso real, tambaleo)
- Multijugador en red (lobbies de Steam)

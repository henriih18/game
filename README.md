# Robo Caótico — Prototipo 0.4

Prototipo de robo cooperativo 2D (estilo R.E.P.O. / Among Us) para Steam.

![Gameplay](docs/screenshot.png)

## Estado actual

- Arte flat vector estilo Among Us (dos personajes, caja, gemas, baldosas)
- **Co-op local 2 jugadores**: P1 (violeta) y P2 (cian)
- Movimiento top-down con colisiones
- **Agarre cooperativo**: la caja se lleva entre uno (45% de velocidad) o entre dos (80%), y se ubica en el punto medio entre ambos
- **Ronda de 2 minutos** con cuenta regresiva
- **Cámaras de seguridad**: si te ven, la alarma sube; al 100% perdés. Sin nadie a la vista, baja sola
- Pantalla de fin (victoria / derrota) y **R para reintentar**
- **Mini-bucle**: juntar las 3 gemas y llevar la caja a EXTRACCIÓN antes de que se acabe el tiempo o salte la alarma

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
| Reintentar (al terminar) | R | R |

## Estructura

```
scenes/        main, player, player2, gem, crate, extraction_zone, security_camera
scripts/       GDScript de cada escena
assets/art/    SVGs (personajes, caja, gema, sombra, baldosa)
assets/audio/  (vacío por ahora)
```

## Siguiente paso

- Multijugador en red (lobbies de Steam)
- Sonido y música (mucho "juice" pendiente)
- Modo traidor (tensión social)

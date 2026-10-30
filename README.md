# Robo Caótico — Prototipo 0.5

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
```

## Controles

| Acción | Jugador 1 | Jugador 2 (local) |
|---|---|---|
| Mover | WASD | Flechas |
| Agarrar / soltar caja | E | Enter |
| Volver al menú (al terminar) | R | R |

En red cada jugador usa **WASD + E**.

## Estructura

```
scenes/        menu, main, player, player2, gem, crate, extraction_zone, security_camera
scripts/       GDScript de cada escena
assets/art/    SVGs (personajes, caja, gema, sombra, baldosa)
assets/audio/  (vacío por ahora)
```

## Limitaciones actuales

- Sin lobbies de Steam: se juega por IP directa (UDP 7777)
- 2 a 4 jugadores por partida
- Sin voz ni chat
- Si un jugador se desconecta, sale de la partida (no hay reconexión)

## Siguiente paso

- Lobbies de Steam con GodotSteam (y voz por proximidad)
- Sonido y música (mucho "juice" pendiente)
- Modo traidor (tensión social)

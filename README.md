# Robo Caótico — Prototipo 0.2

Prototipo de robo cooperativo 2D (estilo R.E.P.O. / Among Us) para Steam.

![Gameplay](docs/screenshot.png)

## Estado actual

- Arte flat vector estilo Among Us (personaje con antifaz, caja, gemas, baldosas)
- Movimiento top-down (WASD o flechas)
- Colisiones con paredes
- **Agarre**: E levanta/suelta la caja de botín (cargarla te frena)
- **Mini-bucle**: juntá las 3 gemas y llevá la caja a la zona de EXTRACCIÓN
- HUD con estado del botín

## Cómo abrir el proyecto

```bash
godot --path ~/Documentos/game
```

O abrir Godot, **Import** y seleccionar esta carpeta. Dentro del editor, **F5** para jugar.

## Controles

| Acción | Teclas |
|---|---|
| Mover | WASD / Flechas |
| Agarrar / soltar caja | E |

## Estructura

```
scenes/        main, player, gem, crate, extraction_zone
scripts/       GDScript de cada escena
assets/art/    SVGs (personaje, caja, gema, sombra, baldosa)
assets/audio/  (vacío por ahora)
```

## Siguiente paso

- Ronda con temporizador y alarma
- Multijugador local (2 jugadores, misma pantalla) → red
- Agarre cooperativo real: dos jugadores deben cargar la caja juntos

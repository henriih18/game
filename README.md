# Robo Caótico — Prototipo 0.1

Prototipo de robo cooperativo 2D (estilo R.E.P.O. / Among Us) para Steam.

## Estado actual

- Movimiento top-down (WASD o flechas)
- Colisiones con paredes
- 3 monedas para recoger y contador en pantalla

## Cómo abrir el proyecto

```bash
godot --path ~/Documentos/game
```

O abrir Godot, **Import** y seleccionar esta carpeta.

## Controles

| Acción | Teclas |
|---|---|
| Mover | WASD / Flechas |

## Estructura

```
scenes/    Escenas (main, player, coin)
scripts/   Código GDScript
assets/    Arte y audio (por ahora vacío)
```

## Siguiente paso

- Zona de agarre para arrastrar objetos entre dos jugadores (caos cooperativo)
- Ronda con temporizador y extracción
- Multijugador local → red

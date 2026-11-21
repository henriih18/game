# FRECUENCIA MUERTA — Primera pasada visual global (2026-11-16)

## 1. Alcance

Primera iteración del pase visual global sobre el `WorldEnvironment` del
Nivel 1 V06. El objetivo es ganar profundidad atmosférica y cohesión de
color sin tocar geometría, materiales de sala, iluminación local ni
jugabilidad.

Se aplicó sobre `scenes/fm/level1_v06.tscn`, en el subrecurso
`Environment_level1_v06`.

## 2. Cambios

| Parámetro | Antes | Después |
|---|---|---|
| `volumetric_fog_density` | 0.010 | 0.012 |
| `fog_enabled` | false | true |
| `fog_light_color` | — | (0.035, 0.055, 0.06) |
| `fog_light_energy` | — | 0.6 |
| `fog_density` | — | 0.0025 |
| `fog_aerial_perspective` | — | 0.15 |
| `fog_sky_affect` | — | 0.0 |
| `adjustment_enabled` | false | true |
| `adjustment_brightness` | — | 1.0 |
| `adjustment_contrast` | — | 1.06 |
| `adjustment_saturation` | — | 1.10 |

Se mantienen: fondo negro, ambiente (0.3, 0.32, 0.38) a 0.02, AgX con
exposición 0.8, SSR 48 pasos, SSAO radio 1.2 / intensidad 1.2, glow 0.2 y
bloom 0.01.

## 3. Intención

- La niebla de profundidad añade aire entre pasillos largos y salas sin
  lavar los negros; su color verde-azulado sigue la paleta oficial.
- El ajuste de contraste/saturación refuerza la lectura del cian, el ámbar
  de trabajo y el rojo de emergencia sin cambiar los materiales.
- La niebla volumétrica sube solo 0.002 para mantener el coste controlado
  y conservar la legibilidad de las zonas oscuras.

## 4. Verificación

- Smoke: **412 PASS / 0 FAIL**.
- Gameplay: **108/0**.
- Full run: **49/0**.
- Presets: **194/0**.
- Alt routes: **73/0**.
- Perf 1280×720 con ventana: **PASS**, fps_avg **474,0**, min **124,5**,
  p1 **180,8**, p99 **5,53 ms**, 0 frames por encima de 16,7 ms.
  Escena: 4.118.264 tris, 4.264 mallas, 775 materiales, 188 luces,
  1.529 colliders, nav 2.009 + 8 polígonos, 0 huérfanos.

Referencia previa a esta pasada: 482,9 fps medios. La diferencia (~1,8 %)
se considera aceptable y dentro del margen de la medición.

## 5. Capturas revisadas

- `wh_godot_aisle_center.png`: la niebla no lava la nave; la mezzanine y los
  racks mantienen contraste.
- `st_godot_connector.png`: el corredor del núcleo vertical gana
  profundidad hacia la escalera; el blockout gris sigue siendo la
  limitación principal, no la atmósfera.

## 6. Limitaciones

- El pase es deliberadamente conservador: no sustituye materiales de shell
  blockout ni añade transiciones por sector.
- Los pasillos y escaleras sin vestir siguen mostrando paredes grises de
  blockout. Su tratamiento requiere un pase de materiales por sala.
- La niebla de profundidad puede reducir algo el contraste en vistas muy
  largas; se ajustará con capturas comparativas si molesta en juego.

## 7. Siguiente paso

Continuar con la optimización medida: presupuesto de texturas (1.090 MB),
materiales y LOD, empezando por las fases con más draw calls
(`security_access`). Después, un pase de materiales de shell para las
zonas aún blockout. Commit solo con autorización.

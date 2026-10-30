# Pruebas

Pruebas básicas versionadas. No sustituyen una batería de integración completa.

## Vertical slice offline

```bash
godot --headless --path . tests/fm_slice_smoke.tscn
```

Comprueba: jugador, Vigilante, núcleo, extracción, escondites, HUD, linterna,
observación, recogida, esconderse/salir, victoria, puerta de seguridad, batería,
trampa sonora y audio ambiental. Resultado esperado: **26 PASS**.

## Juego 2D heredado

```bash
godot --headless --path . --script tests/test_main_2d.gd
```

Resultado esperado: **16 PASS**.

## Red 2D heredada

```bash
bash tests/run_net_check.sh
```

Levanta un host headless en el puerto 7777 y ejecuta un cliente. Resultado esperado:
**6 PASS**. El test usa `/tmp/opencode` para el log temporal.

## Red 3D host-autoritativa

```bash
bash tests/run_net_3d_check.sh
```

Levanta un host 3D headless (`--host3d --nettest`) y ejecuta un cliente real de la
escena `VerticalSlice` contra él. Comprueba conexión, roster de dos jugadores, spawns
separados, recarga de batería, apertura de puerta, recogida del núcleo, extracción
final y HUD del cliente. Resultado esperado: **15 PASS**. Los logs quedan en
`/tmp/opencode`.

## Nota

Los tests fuerzan la salida del árbol y pueden imprimir avisos de `ObjectDB` o recursos
todavía en uso. No indican un fallo de gameplay; se revisarán cuando exista una suite
de integración continua.

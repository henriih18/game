# FRECUENCIA MUERTA — Recepción R7: security desk hero

Fecha: 2026-11-09
Estado: **construido, QA PASS y validado visualmente**. Sin commit.

## Alcance

Primer pase hero del puesto de seguridad de Recepción, sustituto del blockout
`PROP_REC02_SecurityDesk_*`, `Monitor_Security_*` y `Chair_Security_*`.

Se conserva la huella del mostrador original (2,2 × 0,7 m) y se reconstruye
con:

- Mostrador de 2,2 × 0,7 m, tablero z 0,97–1,02, frente público al norte.
- Monitor empotrado en el tablero, con hueco de 0,12 × 0,12 m, base oculta en
  estante y pantalla sobre el top (z 1,04–1,40) mirando al operador (este).
- Hueco de rodillas en el lado este, con postes y raíles.
- Panel frontal con línea naranja, zócalo galvanizado, placa y badge hexagonal
  NEXUS (el texto se descartó por non-manifold).
- Panel de acceso y rejillas en el modesty sur.
- Armario cerrado con puerta y cerradura en el lado oeste.
- Bandeja de cables, regleta, estante, teclado de 70 teclas, ratón/alfombrilla,
  cargador de radio con dos radios, cuaderno, bolígrafo y taza.
- Monitor CCTV 3×3 con marco, rejilla, punto REC rojo, barra de tiempo y logo.
- Silla ergonómica reutilizada de REC06 (malla vinculada), rotada +90° Z.

## Colección y conteos

Colección: `L1_RECEPTION_R7_HERO`.

| Objeto | Tris | Vértices | Polígonos |
|---|---:|---:|---:|
| `REC07_SECURITY_DESK_HERO` | 6.968 | 3.616 | 3.524 |
| `REC07_SECURITY_EQUIPMENT_HERO` | 14.504 | 7.516 | 7.292 |
| `REC07_SECURITY_CHAIR_HERO` | 4.764 | 2.452 | 2.466 |
| **Total** | **26.236** | **13.584** | **13.282** |

- **0 non-manifold, 0 degenerados, UV presente** en las tres mallas.
- 16 piezas R2 antiguas retiradas a `L1_RECEPTION_RETIRED` (no borradas).
- BBox del desk: `[-85.12, -11.164, 0.0] .. [-82.88, -10.444, 1.0395]`.
- BBox del equipo: `[-84.93, -11.09, 0.87] .. [-82.83, -10.46, 1.4]`.
- BBox de la silla: `[-83.0362, -11.135, 0.015] .. [-82.4638, -10.465, 1.0575]`.

## Layout

- El público llega desde el norte (y = -10,5); el frente del desk mira al norte.
- El operador se sitúa al este, mirando al oeste.
- El monitor empotrado queda en x = -83,50; el teclado en x ≈ -82,98.
- La silla queda en (-82,75, -10,80), orientada al oeste.
- El lado oeste se cierra con armario; el este mantiene el hueco de rodillas.

## Correcciones aplicadas

1. **Colección:** `join_group` conservaba la colección del objeto activo
   (`Scene Collection`), por lo que el desk y el equipo no aparecían al
   renderizar solo R7. Se movieron a `L1_RECEPTION_R7_HERO` y se parcheó
   `fm_rec07_security_desk.py` para forzar el linkeo de las tres mallas.
2. **Silla hundida:** el cálculo de `add_chair` centraba también la Z del
   bbox, hundiendo la silla 0,52 m. Ahora se rota alrededor de un pivote
   vertical (z = 0) y conserva la altura original. BBox corregida:
   z 0,015–1,0575.
3. **Badge:** el texto del panel producía 3.092 aristas non-manifold; se
   sustituyó por el badge hexagonal y tres barras.

## Renders

Script: `scripts/fm/fm_rec07_security_render.py`.
Salidas (1280 × 720, Cycles, 96 spp, AgX Medium High Contrast, exposición 0,42):

- `docs/fm_rec07_security_front.png` — frente público limpio; toma histórica
  anterior a R8, con la cola blockout oculta solo en esa vista.
- `docs/fm_rec07_security_threequarter.png` — 3/4 desde el noreste; desk,
  silla, monitor, radios y contexto de Recepción.
- `docs/fm_rec07_security_workstation.png` — puesto del operador; pantalla
  CCTV, teclado, radios y hueco de rodillas.
- `docs/fm_rec07_security_detail.png` — detalle del tablero.
- `docs/fm_rec07_security_plaque.png` — detalle del badge/placa.

## Limitaciones

- El fondo de la sala sigue siendo blockout (suelo azul, muros lavados,
  mobiliario R2 de ~60 tris).
- La barrera/cola blockout de R2 fue sustituida por el clúster hero R8
  (`L1_RECEPTION_R8_HERO`, `docs/FM_RECEPTION_R8.md`).
- La pantalla del monitor es emisiva simple (rejilla CCTV), sin textura.
- Sin texturas/bake, sin GLB ni validación Godot de R7.
- La silla se ve correcta en frente y 3/4, pero en la toma de puesto solo se
  lee el respaldo; hace falta una cámara específica si se quiere documentar
  el asiento completo.

## Siguiente

1. Bancas A/B y taquillas a nivel hero.
2. Servicios de Recepción (HVAC, bandejas, sprinklers y continuidad).
3. Pase de conjunto de Recepción y export/Godot.

## Archivos

- Build: `scripts/fm/fm_rec07_security_desk.py`
- Render: `scripts/fm/fm_rec07_security_render.py`
- QA: `docs/fm_rec07_security_desk_qa.json`
- Backup: `docs/backups/FM_LEVEL1_V06_ARCH_before_rec07.blend`
- Escena: `nexus/nivel_01/FM_LEVEL1_V06_ARCH.blend`

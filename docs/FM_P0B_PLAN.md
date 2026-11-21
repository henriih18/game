# FRECUENCIA MUERTA — Plan P0b: servicios continuos

Estado: **P0b.1 ejecutado**; P0b.2 (patinillos) pendiente de aprobación de ubicación. Informe: `docs/FM_P0B.md`.
Fecha: 2026-11-09.

## 1. Objetivo

Convertir los servicios aislados de recepción, Seguridad y Z10 en una red continua,
coherente y con montaje real: mismos materiales y secciones, soportes, pasamuros,
sleeves y firestop. La red debe poder recorrerse con la mirada y no terminar en el aire.

## 2. Inventario verificado

### Corredor principal

- Volumen: x −100..74, y −4..4, altura útil 4,2 m.
- Techo: `SM_L1_Corridor_Main_Ceiling` en z ≈ 4,09 (colección `L1_ARCH_CEILINGS`,
  oculta en viewport y render para trabajar; no se modifica).
- Muros norte/sur completos, con vanos sobre las puertas a z 3,20..4,20.
- Sin ningún servicio actual (auditoría S-17).

### Z10

- Ducto existente `PROP_Z10_HVACDuct`: x 40,50..60,50, y 19,60..20,40, z 3,25..3,85.
- Bandeja oeste x ≈ 40,2..40,6, y 4,67..34,93, z 2,96..3,08.
- Conducto este x ≈ 61,7, z 3,12..3,19, con hueco de 6 m en la puerta (S-11).
- Sprinkler principal y ≈ 17, z 3,86..3,94; 5 cabezas.
- Airlock de entrada: x 40,14..46, y 4,07..8,07, techo z 3,99..4,19.
- Riser A/B: tubos verticales 0..4 m sin placa ni sleeve (S-15).

### Recepción

- HVAC `KIT_REC01_HVAC_Main`: x −108..−72, y −14,4..−13,6, z 4,20..4,80.
- Bandejas N y W a z ≈ 4,40; sprinkler a z 4,85..4,95 y 0 cabezas (S-03).
- **Conflicto:** el vestíbulo Recepción–Corredor tiene techo a z 3,20..3,36 y
  puertas de 3,04 m. No cabe un ducto de 0,60 m entre el corredor (techo 4,09)
  y la recepción (ducto a 4,20). El ramal no puede cruzar el vestíbulo sin
  obra o patinillo.

### Seguridad 03

- Ducto de ~19,86 m a z 3,84..4,71; termina en el aire (S-05).
- **Conflicto:** el pasillo de conexión mide 1,40 × 2,20 m con techo a 2,20..2,40.
  No cabe ningún servicio de 0,60 m a altura de techo. Tampoco existe patinillo
  vertical (S-18).

## 3. Rutas

### P0b.1 — columna vertebral del corredor + ramal Z10 (sin obra)

Factible y aprobado como siguiente paso técnico.

- **HVAC 800×600:** y = −2,00, centro z = 3,55 (fondo 3,25, alto 3,85),
  x −99,0..73,5. Tramos con brida cada 2,4 m, refuerzos, cleats y soportes
  trapecio cada 4,8 m anclados al techo (z 3,99). Tapones ciegos atornillados
  en ambos extremos para no dejar bocas abiertas.
- **Bandeja 400×100:** y = 0,20, centro z = 3,20, misma longitud; rungs cada
  0,30 m, soportes cada 3,0 m.
- **Sprinkler DN80:** y = 2,40, centro z = 3,90; cabezas cada 4,0 m con drop
  a z 3,20; soportes cada 4,0 m; tapones en extremos.
- **Ramal Z10:** tee en (43, −2, 3,55), tramo +Y hasta y = 20,0, tee final
  sobre el ducto de Z10 en (43, 20, 3,55). Sleeve rectangular 800×600 con
  firestop en el dintel del vano norte (y = 4,0) y en la entrada de Z10
  (y = 8,0). El ramal pasa por el airlock, que tiene 3,99 m libres.
- **Montaje:** herrajes y soportes normalizados; pernos hundidos 0,5 mm;
  sin caras coplanares; UV presente para bake futuro.

### P0b.2 — Recepción y Seguridad (requiere aprobación arquitectónica)

Dos alternativas, ninguna se ejecuta sin decisión:

1. **Patinillo técnico vertical** junto al vestíbulo de recepción y otro junto
   al pasillo de Seguridad, con puertas de registro, placa cortafuego y
   sleeves. Es la solución realista, pero añade arquitectura y colisiones.
2. **Falso techo técnico / cámara sobre el vestíbulo y el pasillo**, si la
   estructura existente lo permite. Requiere sección y comprobación de cotas;
   no se puede asumir.

Mientras no se apruebe, los ramales de recepción y Seguridad quedan fuera de
P0b.1 y se documentan como deuda, no como servicio terminado.

### P0b.3 — Z10, risers y correcciones

- Sustituir el ducto Z10 de 20 m por tramos hero y añadir difusores.
- Cerrar el hueco de 6 m del conducto este y los sleeves huérfanos (S-11/S-12).
- Bandeja oeste: sleeves en los muros que atraviesa (S-13).
- Sprinkler: completar cabezas y ramales (S-14).
- Risers A/B: placa de anclaje, sleeve y firestop (S-15).
- Corregir S-01, S-03, S-05..S-10, S-22 y S-24.

## 4. Criterios de aceptación P0b.1

- Un solo tramo continuo de HVAC, bandeja y sprinkler de x −99 a 73,5.
- Sin bocas abiertas: tapones ciegos en los cuatro extremos.
- Ramal Z10 conectado físicamente al ducto existente, con dos sleeves.
- Soportes cada ≤ 4,8 m (HVAC), ≤ 3,0 m (bandeja) y ≤ 4,0 m (sprinkler).
- 0 caras coplanares, 0 non-manifold, 0 degeneradas; UV presente.
- Presupuesto: ≤ 90.000 tris para toda la columna (geometría de tramo
  optimizada; los maestros hero de 10.392 tris se reservan para uniones y
  primeros planos).
- Render de validación y QA en `docs/fm_p0b_qa.json`.
- Sin commit.

## 5. Decisiones pendientes

1. ¿Se aprueba P0b.1 (corredor + Z10) tal como está descrito?
2. Para recepción y Seguridad: ¿patinillo técnico nuevo, cámara sobre el
   falso techo, u otra solución? Se necesita una decisión antes de tocar
   la arquitectura.

## 6. Archivos previstos

- `scripts/fm/fm_p0b_corridor.py` — construcción, QA y guardado.
- `scripts/fm/fm_p0b_render.py` — render de validación.
- `docs/fm_p0b_qa.json` — resultados.
- `docs/FM_P0B_PLAN.md` — este documento.

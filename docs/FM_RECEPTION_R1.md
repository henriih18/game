# FRECUENCIA MUERTA — Recepción R1

**Fecha:** 2026-11-08
**Archivo:** `nexus/nivel_01/FM_LEVEL1_V06_ARCH.blend`
**Escena:** `NEXUS_L1_V06_ARCH`
**Colección:** `L1_RECEPTION_R1`
**Estado:** R1 cerrada y validada; R2 pendiente

---

## 1. Alcance

R1 cierra la estructura y los servicios de la recepción subterránea. No añade
props, mobiliario, señalización con texto ni lógica de extracción. Es la base
física sobre la que se amoblará en R2.

La recepción es la única zona de extracción del Nivel 1, en Z = 0. El
procedimiento exacto de activación, entrega y cierre sigue pendiente y no se
inventó en esta etapa.

## 2. Estado de la escena

| Dato | Valor |
|---|---:|
| Objetos en `L1_RECEPTION_R1` | **138** |
| Mallas en `L1_RECEPTION_R1` | 133 |
| Luces en `L1_RECEPTION_R1` | 5 |
| Objetos totales de la escena | **1.497** |
| QA | **PASS, 0 errores / 191 warnings** |

Los 191 warnings se aceptan para R1:

- **133** por UV solapada al 100 % en losas, vigas y servicios: son cajas con
  materiales sólidos y UV proyectadas, sin bake previsto en R1.
- **20** por caras back-to-back internas ocultas.
- **1** por el punto más bajo del walkway en z = −0,005 (hundido 5 mm).
- **~37** advertencias por objeto, internas (back-to-back/enclosed).

No hay piezas flotantes ni normales invertidas.

## 3. Elementos construidos

### Techo y servicios

- Losa de 40,3 × 32,3 × 0,2 m en z = 5,3.
- Juntas de techo y vigas estructurales.
- Conducto HVAC de 36 × 0,8 × 0,6 m, con bridas y colgadores.
- Bandejas de cables en los muros oeste y norte, con soportes.
- Tubería de rociadores y colgadores.

### Iluminación

- Carcasas y difusores para `LIGHT_L1_Reception_A` y `_B`.
- Cuatro lámparas colgantes en los puntos Fill.
- Dos apliques de emergencia de techo reutilizados del Z10 y dos luces rojas.
- Luces del vestíbulo.

### Cerramientos y columnas

- Zócalo técnico de 1,2 m en muros N, S, W y E, con huecos.
- Remates superiores e inferiores.
- Seis envolventes de columnas con banda de peligro.
- No se conservaron los baseboards: eran redundantes con el zócalo y generaban
  solapes coplanares.

### Entrada y vestíbulo

- Cuatro montantes y riel superior.
- Dos paños de vidrio laterales.
- Fachada y placa de señal.
- Techo del vestíbulo y dos tiras emisivas.

### Extracción y descontaminación

- Pórtico de compuerta, cabecera, raíles, lamas, bandas de peligro y baliza.
- Plataforma de extracción de 12 × 5 m.
- Arco de descontaminación: dos postes, viga, rejilla y seis boquillas.
- Pasillo/tarima de 6 × 25 m con bordes de peligro.

## 4. Corrección de circulación

La compuerta, el arco de descontaminación y el walkway se desplazaron
**−4,0 m en X** para centrar el recorrido en **x ≈ −94**, entre las columnas
de x = −100 y x = −90.

| Elemento | Rango X |
|---|---:|
| Compuerta | −100 .. −88 |
| Arco de decontaminación | −96 .. −92 |
| Walkway | −97 .. −91 |
| Columnas laterales | −100 y −90 |

La columna de x = −90, y = −32 ya no queda en el eje de la compuerta ni tapa
la aproximación. No se movieron columnas ni muros.

## 5. Evidencia visual

Renders Workbench 1280×720, shading STUDIO, color MATERIAL, cavity BOTH:

- `docs/fm_recepcion_r1_wide_wb.png` — vista amplia desde el acceso.
- `docs/fm_recepcion_r1_entrance_wb.png` — entrada y vestíbulo.
- `docs/fm_recepcion_r1_extraction_wb.png` — compuerta y decontaminación.

Los renders EEVEE iniciales quedaron casi negros por falta de relleno y no se
usan como evidencia. La revisión de R1 es geométrica; la iluminación final se
ajustará en R3/R4.

## 6. Hallazgos y pendientes

1. **Compuerta:** se lee como pórtico abierto; las lamas no se ven desde el
   frente. Hay que decidir en R2 si debe mostrarse cerrada, semicerrada o
   abierta, sin implementar todavía la lógica de extracción.
2. **Señalización:** las placas están lisas. El texto y las UV finales
   corresponden a R2/R3.
3. **Sala vacía:** es lo esperado en R1. R2 añade mostrador, espera, taquillas,
   control de seguridad, monitores y barreras.
4. **Walkway:** hundido 5 mm; aceptado como warning. Se puede corregir en R2.
5. **Materiales:** se usaron materiales PBR existentes; las texturas finales y
   el desgaste corresponden a R3.
6. **Extracción:** el espacio físico está reservado, pero la activación,
   entrega y cierre no están definidos.

## 7. Próximo paso: R2

Añadir mobiliario y elementos funcionales:

- Mostrador de recepción y zona de espera.
- Taquillas y pertenencias.
- Control de seguridad con mesa, monitor y barrera.
- Monitores, cableado y señalización con texto.
- Arco de decontaminación con detalles funcionales.
- Revisión de la compuerta y de la aproximación al walkway.

Después:

- **R3:** desgaste, decals, suciedad, cables, extintores y ambientación.
- **R4:** exportación WebP, colisiones con `fm_glb_collision.gd`, prueba en
  Godot y rendimiento.

No se ha hecho commit.
